"""Verify captured M-CSA entries and replay their exact reference-protein sites.

This source reader has no writer and grants no qualification. It consumes native
UniProt residue numbering, never PDB chain offsets or homologue alignments.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from validate_uniprot_grounding import UNIPROT_RE, validate_protein_reference

SOURCE_URL = "https://www.ebi.ac.uk/thornton-srv/m-csa/api/entries/?format=json"
SOURCE_DIRECTORY = "data/raw/mcsa-native-review"
LICENSE = "CC-BY-4.0"
ATTRIBUTION = "M-CSA, Thornton group, EMBL-EBI"
DEFINITION_SOURCE = "M-CSA (Thornton lab, EBI; fetched via REST API)"
ENTRY_FIELDS = {
    "mcsa_id", "enzyme_name", "is_reference_uniprot_id", "reference_uniprot_id",
    "url", "description", "protein", "all_ecs", "residues", "reaction",
}
RESIDUE_FIELDS = {
    "function_location_abv", "main_annotation", "mcsa_id", "ptm",
    "residue_chains", "residue_sequences", "roles", "roles_summary",
}
SEQUENCE_FIELDS = {"code", "is_reference", "resid", "uniprot_id"}
RECEIPT_FIELDS = {
    "bytes", "content_type", "destination", "fetched_at", "requested_url", "resolved_url", "sha256",
}
PROOF_FIELDS = {"page", "path", "sha256", "receipt_sha256", "receipt_path", "bytes", "fetched_at"}
MANIFEST_FIELDS = {
    "added_native_entry_ids", "attribution", "canary_sha256", "changed_native_entry_ids",
    "complete_acquisitions_equal", "fetcher", "legacy_source_sha256", "license", "method",
    "missing_native_entry_ids", "new_requests", "normalized_bytes", "normalized_path",
    "normalized_sha256", "observed_at_utc", "pages_per_pass", "passes", "requested_urls",
    "scope", "total_entries", "unchanged_native_entries",
}
_SHA256 = re.compile(r"[0-9a-f]{64}")
_TRAIT_ID = re.compile(r"MCSA:([1-9][0-9]*)")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAG = re.compile(r"</?[a-zA-Z][^>]*>")
AMINO_ACIDS = dict(zip(
    "Ala Arg Asn Asp Cys Gln Glu Gly His Ile Leu Lys Met Phe Pro Ser Thr Trp Tyr Val Sec".split(),
    "ARNDCQEGHILKMFPSTWYVU",
))


class McsaSourceError(ValueError):
    """A native acquisition, identity, meaning, or residue requirement failed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise McsaSourceError(message)


def value_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json(raw: bytes | str):
    try:
        return json.loads(raw, object_pairs_hook=_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise McsaSourceError("invalid source JSON") from exc


def _timestamp(value: object) -> None:
    try:
        _require(isinstance(value, str), "source timestamp must be text")
        parsed = datetime.fromisoformat(value)
        _require(parsed.utcoffset() is not None, "source timestamp lacks a timezone")
    except ValueError as exc:
        raise McsaSourceError("invalid source timestamp") from exc


def page_url(page: int) -> str:
    return SOURCE_URL if page == 1 else SOURCE_URL + f"&page={page}"


@dataclass(frozen=True)
class SourcePins:
    acquisition_sha256: str
    normalized_sha256: str

    def __post_init__(self):
        _require(all(isinstance(value, str) and _SHA256.fullmatch(value)
                     for value in (self.acquisition_sha256, self.normalized_sha256)),
                 "source pins must be complete SHA-256 digests")


@dataclass(frozen=True)
class VerifiedSource:
    pins: SourcePins
    entries: dict[int, dict]
    acquisition: dict

    @property
    def source_release(self) -> str:
        return f"M-CSA entries API; sha256:{self.pins.normalized_sha256}"


def _native_entry(entry: object) -> dict:
    _require(isinstance(entry, dict) and set(entry) == ENTRY_FIELDS, "native entry fields changed")
    identifier = entry["mcsa_id"]
    _require(type(identifier) is int and identifier > 0, "native entry ID must be a positive integer")
    _require(entry["url"] == f"www.ebi.ac.uk/thornton-srv/m-csa/entry/{identifier}/",
             "native entry URL does not match its ID")
    _require(isinstance(entry["residues"], list), "native entry lacks the full residue list")
    for residue in entry["residues"]:
        _require(isinstance(residue, dict) and set(residue) == RESIDUE_FIELDS,
                 "native residue fields changed")
        _require(type(residue["mcsa_id"]) is int and residue["mcsa_id"] == identifier,
                 "native residue belongs to another entry")
        rows = residue["residue_sequences"]
        _require(isinstance(rows, list), "native sequence mappings must be a list")
        for row in rows:
            _require(isinstance(row, dict) and set(row) == SEQUENCE_FIELDS,
                     "native sequence mapping fields changed")
    return entry


def read_verified_source(root: Path, acquisition_path: Path, pins: SourcePins) -> VerifiedSource:
    """Replay both complete API captures, every receipt, and normalized entries."""
    seen_files: dict[Path, str] = {}

    def read(path: Path, expected: str) -> bytes:
        _require(not path.is_symlink() and path.is_file(), "source must be a regular file")
        raw = path.read_bytes()
        _require(hashlib.sha256(raw).hexdigest() == expected, f"source checksum mismatch: {path}")
        previous = seen_files.setdefault(path, expected)
        _require(previous == expected, "inconsistent source byte pins")
        return raw

    def source_path(value: object) -> Path:
        _require(isinstance(value, str), "source path must be text")
        path = PurePosixPath(value)
        _require(not path.is_absolute() and ".." not in path.parts and str(path) == value
                 and value.startswith(SOURCE_DIRECTORY + "/"), "source path is outside the native capture")
        resolved = root / value
        _require(resolved.resolve().is_relative_to(root.resolve()), "source path escapes the repository")
        return resolved

    manifest = strict_json(read(acquisition_path, pins.acquisition_sha256))
    _require(isinstance(manifest, dict) and set(manifest) == MANIFEST_FIELDS,
             "native acquisition manifest fields changed")
    total = manifest["total_entries"]
    _require(type(total) is int and total > 0, "native source requires a complete entry count")
    pages = math.ceil(total / 100)
    _require(type(manifest["pages_per_pass"]) is int and manifest["pages_per_pass"] == pages
             and type(manifest["new_requests"]) is int and manifest["new_requests"] == pages * 2 - 1,
             "native source page counts disagree")
    _require(manifest["method"] == "GET" and manifest["fetcher"] == "scripts/fetch_source.py"
             and manifest["license"] == LICENSE and manifest["attribution"] == ATTRIBUTION,
             "native acquisition method or attribution changed")
    _require(manifest["complete_acquisitions_equal"] is True
             and manifest["requested_urls"] == [page_url(n) for n in range(1, pages + 1)],
             "native acquisition URL set or completeness changed")
    _require(manifest["normalized_sha256"] == pins.normalized_sha256
             and manifest["normalized_path"] == SOURCE_DIRECTORY + "/entries.jsonl",
             "normalized source identity changed")
    _timestamp(manifest["observed_at_utc"])
    _require(isinstance(manifest["passes"], list) and len(manifest["passes"]) == 2,
             "two complete native acquisitions are required")
    generations = []
    for generation, proofs in enumerate(manifest["passes"]):
        _require(isinstance(proofs, list) and len(proofs) == pages, "incomplete native source pass")
        entries = {}
        directory = SOURCE_DIRECTORY + ("/verification" if generation else "")
        for page, proof in enumerate(proofs, 1):
            _require(isinstance(proof, dict) and set(proof) == PROOF_FIELDS,
                     "native page proof fields changed")
            expected_path = f"{directory}/entries-page-{page:03}.json"
            _require(type(proof["page"]) is int and proof["page"] == page
                     and proof["path"] == expected_path
                     and proof["receipt_path"] == expected_path + ".fetch.json",
                     "native page order or identity changed")
            raw = read(source_path(proof["path"]), proof["sha256"])
            receipt = strict_json(read(source_path(proof["receipt_path"]), proof["receipt_sha256"]))
            _require(isinstance(receipt, dict) and set(receipt) == RECEIPT_FIELDS,
                     "native fetch receipt fields changed")
            _require(receipt["requested_url"] == receipt["resolved_url"] == page_url(page)
                     and receipt["destination"] == expected_path
                     and receipt["sha256"] == proof["sha256"], "receipt does not bind the official native page")
            _require(type(receipt["bytes"]) is int and type(proof["bytes"]) is int
                     and receipt["bytes"] == proof["bytes"] == len(raw), "native page byte count mismatch")
            _require(isinstance(receipt["content_type"], str)
                     and receipt["content_type"].split(";", 1)[0] == "application/json",
                     "native page content type changed")
            _timestamp(receipt["fetched_at"])
            _require(receipt["fetched_at"] == proof["fetched_at"], "native fetch timestamps disagree")
            document = strict_json(raw)
            _require(isinstance(document, dict) and set(document) == {"count", "next", "previous", "results"},
                     "native API pagination fields changed")
            _require(type(document["count"]) is int and document["count"] == total
                     and document["next"] == (page_url(page + 1) if page < pages else None)
                     and document["previous"] == (page_url(page - 1) if page > 1 else None),
                     "native API pagination is incomplete")
            rows = document["results"]
            _require(isinstance(rows, list) and len(rows) == min(100, total - (page - 1) * 100),
                     "native page has the wrong entry count")
            for row in rows:
                entry = _native_entry(row)
                _require(entry["mcsa_id"] not in entries, "duplicate native entry ID")
                entries[entry["mcsa_id"]] = entry
        _require(len(entries) == total, "native source pass is incomplete")
        generations.append(entries)
    _require(manifest["canary_sha256"] == manifest["passes"][0][0]["sha256"], "native canary pin changed")
    _require(generations[0] == generations[1], "complete native acquisitions disagree")
    normalized = read(source_path(manifest["normalized_path"]), pins.normalized_sha256)
    _require(type(manifest["normalized_bytes"]) is int and len(normalized) == manifest["normalized_bytes"],
             "normalized source byte count mismatch")
    rows = [strict_json(line) for line in normalized.splitlines()]
    _require(rows == [generations[0][key] for key in sorted(generations[0])],
             "normalized source differs from the complete native acquisition")
    for path, expected in seen_files.items():
        _require(not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                 "native source changed during verification")
    return VerifiedSource(pins, generations[0], manifest)


def native_definition(entry: dict) -> str:
    description = entry.get("description") or entry.get("enzyme_name")
    _require(isinstance(description, str) and bool(description.strip()), "native definition is absent")
    return " ".join(_HTML_TAG.sub("", _CONTROL.sub("", description)).split())


@dataclass(frozen=True)
class NativeResidue:
    source_residue_index: int
    position: int
    amino_acid: str
    native_mapping_sha256: str


@dataclass(frozen=True)
class SiteLocation:
    trait_id: str
    protein_id: str
    coordinate_frame: str
    residue_positions: tuple[int, ...]
    native_residues: tuple[NativeResidue, ...]
    sequence_sha256: str
    sequence_release: str
    protein_reference_sha256: str
    native_entry_sha256: str


def locate_existing_site(record: dict, reference: dict, entry: dict) -> SiteLocation:
    """Require the complete source site's exact native mappings on an existing protein."""
    findings = validate_protein_reference(reference, path=Path("MCSA-ProteinReference"), line=1)
    _require(not findings, "invalid or incomplete ProteinReference")
    _require(isinstance(record, dict), "trait record must be an object")
    entry = _native_entry(entry)
    trait_id = record.get("identifier")
    match = _TRAIT_ID.fullmatch(trait_id) if isinstance(trait_id, str) else None
    _require(match is not None and int(match.group(1)) == entry["mcsa_id"], "native trait identity differs")
    expected = {
        "label": entry["enzyme_name"], "definition": native_definition(entry),
        "definition_source": DEFINITION_SOURCE, "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_ACTIVE_SITE", "term_kind": "CLASS", "license": LICENSE,
    }
    _require(isinstance(entry["enzyme_name"], str) and bool(entry["enzyme_name"].strip()),
             "native enzyme name is absent")
    _require(all(record.get(key) == value for key, value in expected.items()),
             "record meaning or license differs from the native source")
    _require(not expected["definition"].rstrip().endswith((":", "e.g.", "i.e.")),
             "native definition appears incomplete")
    protein_id = reference["protein_id"]
    examples = record.get("canonical_examples")
    _require(isinstance(examples, list) and all(isinstance(row, dict) for row in examples)
             and sum(row.get("protein_id") == protein_id for row in examples) == 1,
             "site requires one exact protein in the existing examples")
    _require(entry["is_reference_uniprot_id"] is True, "native entry is not a reference entry")
    protein = entry["protein"]
    _require(isinstance(protein, dict) and set(protein) == {"sequences"}
             and isinstance(protein["sequences"], list), "native reference protein list is incomplete")
    identifiers = []
    for row in protein["sequences"]:
        _require(isinstance(row, dict) and set(row) == {"uniprot_id"}, "native protein identity fields changed")
        accession = row["uniprot_id"]
        _require(isinstance(accession, str) and UNIPROT_RE.fullmatch("UniProtKB:" + accession) is not None,
                 "native protein accession is invalid")
        identifiers.append(accession)
    _require(identifiers and len(set(identifiers)) == len(identifiers)
             and entry["reference_uniprot_id"] == ", ".join(identifiers),
             "native reference protein identities disagree")
    accession = protein_id.removeprefix("UniProtKB:")
    _require(accession in identifiers, "existing protein is not an exact native reference")
    _require(bool(entry["residues"]), "native source has no catalytic residues")
    residues = []
    for index, residue in enumerate(entry["residues"]):
        rows = residue["residue_sequences"]
        exact = [row for row in rows if row["uniprot_id"] == accession]
        _require(len(exact) == 1 and exact[0]["is_reference"] is True,
                 "complete unambiguous reference-only residue set is required")
        native = exact[0]
        position, code = native["resid"], native["code"]
        _require(type(position) is int and 1 <= position <= reference["sequence_length"],
                 "native UniProt residue position is out of bounds")
        _require(isinstance(code, str) and code in AMINO_ACIDS, "unsupported native residue code")
        amino_acid = AMINO_ACIDS[code]
        _require(reference["sequence"][position - 1] == amino_acid,
                 "native residue disagrees with the exact reference sequence")
        residues.append(NativeResidue(index, position, amino_acid, value_sha256(native)))
    return SiteLocation(
        trait_id, protein_id,
        "UNIPROT_ISOFORM" if UNIPROT_RE.fullmatch(protein_id).group(2) else "UNIPROT_CANONICAL",
        tuple(sorted({row.position for row in residues})), tuple(residues),
        reference["sequence_sha256"], reference["uniprot_release"], value_sha256(reference),
        value_sha256(entry),
    )
