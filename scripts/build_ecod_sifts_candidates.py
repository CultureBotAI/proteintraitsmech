#!/usr/bin/env python3
"""Build fail-closed ECOD fold candidates from residue-level PDBe SIFTS XML.

ECOD coordinates are PDB author coordinates, not UniProt coordinates.  This
adapter therefore never copies ECOD ranges into a TraitOccurrence.  It retains
the exact ECOD domain row (including insertion codes), treats every position in
ECOD's ``seqid_range`` as defining (including SIFTS residues unobserved in the
structure), checks observed author coordinates against ``pdb_range``, and
requires one chain, one UniProt accession, one SIFTS mapping per defining
residue, and amino-acid agreement with a release-pinned ProteinReference.  Only
then does it emit UniProt positions.

The default discovery scope is ECOD's own ``manual_rep=True`` occurrences.  All
manual-representative alternatives are retained; no text ranking or first-hit
selection is performed.

Two commands are provided:

* ``fetch`` plans downloads from the official residue-level SIFTS XML archive.
  It is dry-run by default and writes only with ``--apply``.
* ``build`` requires a completed, canonical fetch manifest and production gzip,
  then emits candidate, compact mapping, GroundingEvidence, and blocked JSONL
  ledgers.  ``--offline-fixture-mode`` is an explicit test-only escape hatch
  whose rows production registry loaders reject.  It never edits trait records.

Resolver integration contract: ``ground_uniprot_examples.py`` must add a
``sifts-mapping`` provider which looks up ``mapping_id`` in ``--sifts-registry``,
uses ``load_mapping_registry`` to replay the exact ECOD file/line, canonical
manifest, and bound XML, projects the supplied TraitOccurrence and
GroundingEvidence without changing coordinates, and requires the usual
ProteinReference lookup.  Promotion policy remains the resolver's concern.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ECOD = REPO_ROOT / "data" / "raw" / "ecod.latest.domains.txt"
DEFAULT_TRAITS = REPO_ROOT / "data" / "traits" / "structure" / "fold" / "ecod"
DEFAULT_PROTEINS = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
GROUNDING_ROOT = REPO_ROOT / "data" / "grounding"
SIFTS_XML_ROOT = "https://ftp.ebi.ac.uk/pub/databases/msd/sifts/xml"
SIFTS_RIGHTS_URL = "http://pdbe.org/sifts"
ECOD_LICENSE = "free for academic use (ECOD)"
SCHEMA_VERSION = 1
PINNED_MANIFEST = "PINNED_MANIFEST"
OFFLINE_FIXTURE = "OFFLINE_FIXTURE"
MANIFEST_NAME = "manifest.json"

ECOD_COLUMNS = {
    "uid": 0,
    "domain_id": 1,
    "manual_rep": 2,
    "f_id": 3,
    "pdb": 4,
    "chain": 5,
    "pdb_range": 6,
    "seqid_range": 7,
}
NAMESPACE = "{http://www.ebi.ac.uk/pdbe/docs/sifts/eFamily.xsd}"
DC_NAMESPACE = "{http://purl.org/dc/elements/1.1/}"
RDF_NAMESPACE = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
NATIVE_RANGE_RE = re.compile(
    r"^(?P<chain>[^:,\s]+):(?P<start>-?[0-9]+)(?P<start_icode>[A-Za-z]?)"
    r"-(?P<end>-?[0-9]+)(?P<end_icode>[A-Za-z]?)$"
)
NATIVE_POSITION_RE = re.compile(r"^(?P<number>-?[0-9]+)(?P<icode>[A-Za-z]?)$")
TRAIT_ID_RE = re.compile(r"(?m)^identifier:\s*[\"']?(ECOD:F\.[^\s\"'#]+)")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SNAPSHOT_ID_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9])?$")

MANIFEST_FIELDS = frozenset(
    {
        "schema_version",
        "snapshot_mode",
        "snapshot_id",
        "source",
        "source_root",
        "rights_url",
        "ecod_source_path",
        "ecod_source_sha256",
        "ecod_release",
        "representatives_only",
        "requested_pdb_count",
        "requested_pdb_ids_sha256",
        "entries",
        "failures",
        "complete",
    }
)
MANIFEST_ENTRY_FIELDS = frozenset(
    {
        "pdb_id",
        "path",
        "sha256",
        "sifts_entry_date",
        "sifts_uniprot_release",
        "sifts_uniprot_version",
        "url",
    }
)
MAPPED_RESIDUE_FIELDS = frozenset(
    {
        "chain_id",
        "pdbe_sequence_position",
        "author_residue_number",
        "author_insertion_code",
        "pdb_amino_acid",
        "uniprot_position",
        "uniprot_amino_acid",
    }
)
MAPPING_FIELDS = frozenset(
    {
        "mapping_id",
        "schema_version",
        "trait_id",
        "ecod_domain_id",
        "ecod_uid",
        "ecod_release",
        "ecod_license",
        "ecod_source_path",
        "ecod_source_sha256",
        "ecod_line_number",
        "ecod_raw_line_sha256",
        "structure_id",
        "chain_id",
        "ecod_chain",
        "ecod_pdb_range",
        "ecod_seqid_range",
        "native_ranges",
        "protein_id",
        "sequence_sha256",
        "uniprot_release",
        "sifts_snapshot_mode",
        "sifts_snapshot_id",
        "sifts_manifest_path",
        "sifts_manifest_sha256",
        "sifts_manifest_entry",
        "sifts_manifest_entry_sha256",
        "sifts_entry_date",
        "sifts_uniprot_release",
        "sifts_uniprot_version",
        "sifts_xml_sha256",
        "sifts_source_url",
        "sifts_rights",
        "sifts_rights_url",
        "mapped_residues",
    }
)

AA3_TO_1 = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
    "SEC": "U",
    "PYL": "O",
}


class EcodSiftsError(ValueError):
    """An input cannot produce replayable ECOD/SIFTS evidence."""


@dataclass(frozen=True, order=True)
class NativePosition:
    number: int
    insertion_code: str = ""

    @classmethod
    def parse(cls, value: str) -> "NativePosition":
        match = NATIVE_POSITION_RE.fullmatch(value.strip())
        if match is None:
            raise EcodSiftsError(f"invalid PDB author residue number {value!r}")
        return cls(int(match.group("number")), match.group("icode").upper())

    def text(self) -> str:
        return f"{self.number}{self.insertion_code}"


@dataclass(frozen=True)
class NativeRange:
    chain: str
    start: NativePosition
    end: NativePosition

    def contains(self, chain: str, position: NativePosition) -> bool:
        return chain == self.chain and self.start <= position <= self.end

    def as_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain,
            "start": {
                "author_residue_number": self.start.number,
                "author_insertion_code": self.start.insertion_code,
            },
            "end": {
                "author_residue_number": self.end.number,
                "author_insertion_code": self.end.insertion_code,
            },
        }


@dataclass(frozen=True)
class EcodOccurrence:
    uid: str
    domain_id: str
    f_id: str
    pdb_id: str
    chain: str
    pdb_range: str
    seqid_range: str
    native_ranges: tuple[NativeRange, ...]
    seqid_ranges: tuple[NativeRange, ...]
    line_number: int
    raw_line_sha256: str

    @property
    def trait_id(self) -> str:
        return f"ECOD:F.{self.f_id}"


@dataclass(frozen=True)
class SiftsResidue:
    chain: str
    pdbe_position: int
    native: NativePosition | None
    pdb_amino_acid: str
    uniprot_accession: str | None
    uniprot_position: int | None
    uniprot_amino_acid: str | None
    ambiguous: bool = False


@dataclass(frozen=True)
class SiftsEntry:
    pdb_id: str
    entry_date: str
    uniprot_release: str
    uniprot_version: str
    xml_sha256: str
    rights: str
    rights_url: str
    residues: tuple[SiftsResidue, ...]


@dataclass(frozen=True)
class SiftsSnapshotBinding:
    """Content-addressed provenance for one XML inside a snapshot."""

    mode: str
    snapshot_id: str
    manifest_path: Path
    manifest_sha256: str
    manifest_entry: Mapping[str, Any]


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def mapping_entry_sha256(value: Mapping[str, Any]) -> str:
    """Digest the immutable mapping payload, excluding its content-address key."""
    return value_sha256({key: value[key] for key in value if key != "mapping_id"})


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise EcodSiftsError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _validate_snapshot_id(value: str) -> str:
    if SNAPSHOT_ID_RE.fullmatch(value) is None or Path(value).name != value:
        raise EcodSiftsError(
            "snapshot-id must be one safe 1-80 character path component "
            "(letters, digits, dot, underscore, or hyphen; alphanumeric ends)"
        )
    return value


def _nearest_existing_ancestor(path: Path) -> tuple[Path, tuple[str, ...]]:
    """Return the closest existing ancestor and its unresolved relative tail."""

    candidate = path.resolve()
    unresolved_reversed: list[str] = []
    while True:
        try:
            candidate.stat()
        except FileNotFoundError:
            parent = candidate.parent
            if parent == candidate:
                raise EcodSiftsError(f"cannot resolve an existing ancestor for path: {path}")
            unresolved_reversed.append(candidate.name)
            candidate = parent
        except OSError as exc:
            raise EcodSiftsError(f"cannot inspect path identity for {path}: {exc}") from exc
        else:
            return candidate, tuple(reversed(unresolved_reversed))


def _physical_path_key(path: Path) -> tuple[int, int, tuple[str, ...]]:
    """Identify an existing leaf or a case-insensitive prospective path."""

    ancestor, unresolved = _nearest_existing_ancestor(path)
    try:
        identity = ancestor.stat()
    except OSError as exc:
        raise EcodSiftsError(f"cannot inspect path identity for {path}: {exc}") from exc
    return (
        identity.st_dev,
        identity.st_ino,
        tuple(unicodedata.normalize("NFC", part).casefold() for part in unresolved),
    )


def _is_under(path: Path, parent: Path) -> bool:
    resolved_path = path.resolve()
    resolved_parent = parent.resolve()
    try:
        resolved_path.relative_to(resolved_parent)
    except ValueError:
        pass
    else:
        return True

    # ``Path.resolve()`` preserves a caller's component spelling on case-insensitive
    # macOS filesystems. Walk from the nearest existing ancestor and compare
    # physical identities so DATA/TRAITS cannot evade data/traits containment.
    candidate, _ = _nearest_existing_ancestor(resolved_path)
    while True:
        try:
            if candidate.samefile(resolved_parent):
                return True
        except OSError:
            return False
        parent_candidate = candidate.parent
        if parent_candidate == candidate:
            return False
        candidate = parent_candidate


def _reject_traits_target(path: Path, *, label: str) -> None:
    if _is_under(path, TRAITS_ROOT):
        raise EcodSiftsError(f"{label} must not be under data/traits: {path}")


def _reject_build_output_target(path: Path, *, selected_traits_root: Path) -> None:
    """Keep every staging output outside trait and durable-grounding stores."""

    protected_roots = (
        (TRAITS_ROOT, "data/traits"),
        (GROUNDING_ROOT, "data/grounding"),
        (selected_traits_root, "the selected --traits root"),
    )
    for root, label in protected_roots:
        if _is_under(path, root):
            raise EcodSiftsError(f"output path must not be under {label}: {path}")


def _bound_path(value: Any, *, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise EcodSiftsError(f"{label} must be a non-empty path")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()


def _require_iso_date(value: Any, *, label: str) -> str:
    if not isinstance(value, str):
        raise EcodSiftsError(f"{label} must be an ISO YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise EcodSiftsError(f"{label} must be an ISO YYYY-MM-DD date") from exc
    if parsed.isoformat() != value:
        raise EcodSiftsError(f"{label} must use exact ISO YYYY-MM-DD spelling")
    return value


def _validate_manifest_entry(row: Any, *, mode: str) -> dict[str, Any]:
    if not isinstance(row, dict) or set(row) != MANIFEST_ENTRY_FIELDS:
        raise EcodSiftsError("SIFTS manifest entry has invalid fields")
    pdb_id = row.get("pdb_id")
    if not isinstance(pdb_id, str) or re.fullmatch(r"[0-9][a-z0-9]{3}", pdb_id) is None:
        raise EcodSiftsError("SIFTS manifest entry has invalid pdb_id")
    expected_suffix = ".xml.gz" if mode == PINNED_MANIFEST else ".xml"
    expected_path = f"{pdb_id}{expected_suffix}"
    if row.get("path") != expected_path:
        raise EcodSiftsError(f"SIFTS manifest entry path must be exactly {expected_path!r}")
    if not isinstance(row.get("sha256"), str) or SHA256_RE.fullmatch(row["sha256"]) is None:
        raise EcodSiftsError("SIFTS manifest entry has invalid sha256")
    _require_iso_date(row.get("sifts_entry_date"), label="SIFTS entry date")
    release = row.get("sifts_uniprot_release")
    version = row.get("sifts_uniprot_version")
    if not isinstance(release, str) or re.fullmatch(r"[0-9]{4}_[0-9]{2}", release) is None:
        raise EcodSiftsError("SIFTS manifest entry has invalid UniProt release")
    if not isinstance(version, str) or _normalise_uniprot_release(version) != release:
        raise EcodSiftsError("SIFTS manifest entry UniProt release/version mismatch")
    if row.get("url") != f"{SIFTS_XML_ROOT}/{pdb_id}.xml.gz":
        raise EcodSiftsError("SIFTS manifest entry has non-canonical source URL")
    return row


def _validate_manifest_document(
    manifest: Any,
    *,
    expected_contract: Mapping[str, Any] | None = None,
    require_complete: bool = False,
) -> dict[str, Any]:
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS:
        raise EcodSiftsError("SIFTS manifest has invalid fields")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise EcodSiftsError("SIFTS manifest has unsupported schema_version")
    if manifest.get("snapshot_mode") != PINNED_MANIFEST:
        raise EcodSiftsError("SIFTS manifest is not a production pinned snapshot")
    snapshot_id = manifest.get("snapshot_id")
    if not isinstance(snapshot_id, str):
        raise EcodSiftsError("SIFTS manifest snapshot_id is missing")
    _validate_snapshot_id(snapshot_id)
    if manifest.get("source") != "PDBe SIFTS residue-level XML":
        raise EcodSiftsError("SIFTS manifest source mismatch")
    if manifest.get("source_root") != SIFTS_XML_ROOT:
        raise EcodSiftsError("SIFTS manifest source_root mismatch")
    if manifest.get("rights_url") != SIFTS_RIGHTS_URL:
        raise EcodSiftsError("SIFTS manifest rights_url mismatch")
    if not isinstance(manifest.get("ecod_source_path"), str) or not manifest["ecod_source_path"]:
        raise EcodSiftsError("SIFTS manifest ECOD source path is missing")
    if (
        not isinstance(manifest.get("ecod_source_sha256"), str)
        or SHA256_RE.fullmatch(manifest["ecod_source_sha256"]) is None
    ):
        raise EcodSiftsError("SIFTS manifest ECOD source digest is invalid")
    if not isinstance(manifest.get("ecod_release"), str) or not manifest["ecod_release"].startswith(
        "ECOD "
    ):
        raise EcodSiftsError("SIFTS manifest ECOD release is invalid")
    if type(manifest.get("representatives_only")) is not bool:
        raise EcodSiftsError("SIFTS manifest representatives_only must be boolean")
    count = manifest.get("requested_pdb_count")
    if type(count) is not int or count < 0:
        raise EcodSiftsError("SIFTS manifest requested_pdb_count is invalid")
    ids_digest = manifest.get("requested_pdb_ids_sha256")
    if not isinstance(ids_digest, str) or SHA256_RE.fullmatch(ids_digest) is None:
        raise EcodSiftsError("SIFTS manifest requested PDB digest is invalid")
    if type(manifest.get("complete")) is not bool:
        raise EcodSiftsError("SIFTS manifest complete must be boolean")
    entries_value = manifest.get("entries")
    failures_value = manifest.get("failures")
    if not isinstance(entries_value, list) or not isinstance(failures_value, list):
        raise EcodSiftsError("SIFTS manifest entries/failures must be lists")
    entries = [_validate_manifest_entry(item, mode=PINNED_MANIFEST) for item in entries_value]
    if entries != sorted(entries, key=lambda item: item["pdb_id"]):
        raise EcodSiftsError("SIFTS manifest entries are not deterministically sorted")
    entry_ids = [item["pdb_id"] for item in entries]
    if len(entry_ids) != len(set(entry_ids)):
        raise EcodSiftsError("SIFTS manifest contains duplicate PDB entries")
    failures: list[dict[str, str]] = []
    for item in failures_value:
        if (
            not isinstance(item, dict)
            or set(item) != {"pdb_id", "error"}
            or not isinstance(item.get("pdb_id"), str)
            or re.fullmatch(r"[0-9][a-z0-9]{3}", item["pdb_id"]) is None
            or not isinstance(item.get("error"), str)
            or not item["error"]
        ):
            raise EcodSiftsError("SIFTS manifest failure row is invalid")
        failures.append(item)
    if failures != sorted(failures, key=lambda item: (item["pdb_id"], item["error"])):
        raise EcodSiftsError("SIFTS manifest failures are not deterministically sorted")
    failure_ids = [item["pdb_id"] for item in failures]
    if len(failure_ids) != len(set(failure_ids)) or set(failure_ids) & set(entry_ids):
        raise EcodSiftsError("SIFTS manifest has duplicate or conflicting failures")
    if len(entries) > count:
        raise EcodSiftsError("SIFTS manifest contains more entries than requested")
    if manifest["complete"]:
        if failures or len(entries) != count:
            raise EcodSiftsError("completed SIFTS manifest is not complete")
        if ids_digest != value_sha256(entry_ids):
            raise EcodSiftsError("completed SIFTS manifest requested PDB digest mismatch")
    if require_complete and not manifest["complete"]:
        raise EcodSiftsError("SIFTS manifest is incomplete")
    if expected_contract is not None:
        for key, expected in expected_contract.items():
            if manifest.get(key) != expected:
                raise EcodSiftsError(
                    f"SIFTS snapshot contract mismatch for {key}: "
                    f"{manifest.get(key)!r} != {expected!r}"
                )
    return manifest


def _fixture_manifest_sha(snapshot_id: str, entry: Mapping[str, Any]) -> str:
    return value_sha256(
        {
            "schema_version": SCHEMA_VERSION,
            "snapshot_mode": OFFLINE_FIXTURE,
            "snapshot_id": snapshot_id,
            "entry": entry,
        }
    )


def _load_canonical_manifest(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw)
    except OSError as exc:
        raise EcodSiftsError(f"cannot read SIFTS manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EcodSiftsError(f"invalid SIFTS manifest JSON {path}: {exc}") from exc
    canonical = (canonical_json(manifest) + "\n").encode("utf-8")
    if raw != canonical:
        raise EcodSiftsError(f"SIFTS manifest is not canonical JSON: {path}")
    return manifest, hashlib.sha256(raw).hexdigest()


def _validate_mapping_row(
    row: dict[str, Any],
    *,
    allow_offline_fixtures: bool,
    ecod_cache: dict[Path, tuple[str, list[str], str]],
    manifest_cache: dict[Path, tuple[str, dict[str, Any]]],
    sifts_cache: dict[Path, SiftsEntry],
) -> None:
    if set(row) != MAPPING_FIELDS:
        missing = sorted(MAPPING_FIELDS - set(row))
        extra = sorted(set(row) - MAPPING_FIELDS)
        raise EcodSiftsError(f"mapping fields mismatch; missing={missing}, extra={extra}")
    if row["schema_version"] != SCHEMA_VERSION:
        raise EcodSiftsError("unsupported mapping schema_version")
    mapping_id = row["mapping_id"]
    expected_mapping_id = f"ecod-sifts:{mapping_entry_sha256(row)}"
    if mapping_id != expected_mapping_id:
        raise EcodSiftsError("mapping_id digest mismatch")
    required_text = (
        "trait_id",
        "ecod_domain_id",
        "ecod_uid",
        "ecod_release",
        "ecod_source_path",
        "structure_id",
        "chain_id",
        "ecod_chain",
        "ecod_pdb_range",
        "ecod_seqid_range",
        "protein_id",
        "uniprot_release",
        "sifts_snapshot_id",
        "sifts_manifest_path",
        "sifts_rights",
    )
    if any(not isinstance(row[field], str) or not row[field] for field in required_text):
        raise EcodSiftsError("mapping has a missing required text field")
    if not row["trait_id"].startswith("ECOD:F."):
        raise EcodSiftsError("mapping trait_id is not an ECOD F identifier")
    if re.fullmatch(r"UniProtKB:[A-Z0-9]{6,10}(?:-[0-9]+)?", row["protein_id"]) is None:
        raise EcodSiftsError("mapping protein_id is not a UniProtKB accession")
    if row["ecod_license"] != ECOD_LICENSE:
        raise EcodSiftsError("mapping ECOD license mismatch")
    if type(row["ecod_line_number"]) is not int or row["ecod_line_number"] < 1:
        raise EcodSiftsError("mapping ECOD line number is invalid")
    for field in (
        "ecod_source_sha256",
        "ecod_raw_line_sha256",
        "sequence_sha256",
        "sifts_manifest_sha256",
        "sifts_manifest_entry_sha256",
        "sifts_xml_sha256",
    ):
        if not isinstance(row[field], str) or SHA256_RE.fullmatch(row[field]) is None:
            raise EcodSiftsError(f"mapping {field} is not a SHA-256 digest")
    if re.fullmatch(r"[0-9]{4}_[0-9]{2}", row["uniprot_release"]) is None:
        raise EcodSiftsError("mapping UniProt release is invalid")
    _validate_snapshot_id(row["sifts_snapshot_id"])
    mode = row["sifts_snapshot_mode"]
    if mode not in {PINNED_MANIFEST, OFFLINE_FIXTURE}:
        raise EcodSiftsError("mapping SIFTS snapshot mode is invalid")
    if mode == OFFLINE_FIXTURE and not allow_offline_fixtures:
        raise EcodSiftsError(
            "OFFLINE_FIXTURE mapping rejected; pass allow_offline_fixtures=True only in tests"
        )
    manifest_entry = _validate_manifest_entry(row["sifts_manifest_entry"], mode=mode)
    if value_sha256(manifest_entry) != row["sifts_manifest_entry_sha256"]:
        raise EcodSiftsError("SIFTS manifest entry digest mismatch")
    pdb_id = manifest_entry["pdb_id"]
    if row["structure_id"] != f"PDB:{pdb_id}":
        raise EcodSiftsError("mapping structure/PDB mismatch")
    if row["sifts_xml_sha256"] != manifest_entry["sha256"]:
        raise EcodSiftsError("mapping XML/manifest digest mismatch")
    duplicated_entry_fields = {
        "sifts_entry_date": "sifts_entry_date",
        "sifts_uniprot_release": "sifts_uniprot_release",
        "sifts_uniprot_version": "sifts_uniprot_version",
        "sifts_source_url": "url",
    }
    for mapping_field, entry_field in duplicated_entry_fields.items():
        if row[mapping_field] != manifest_entry[entry_field]:
            raise EcodSiftsError(f"mapping/manifest mismatch for {mapping_field}")
    _require_iso_date(row["sifts_entry_date"], label="mapping SIFTS entry date")
    if _normalise_uniprot_release(row["sifts_uniprot_version"]) != row["sifts_uniprot_release"]:
        raise EcodSiftsError("mapping SIFTS release/version mismatch")
    if row["uniprot_release"] != row["sifts_uniprot_release"]:
        raise EcodSiftsError("mapping registry/SIFTS UniProt release mismatch")
    if row["sifts_rights_url"] != SIFTS_RIGHTS_URL:
        raise EcodSiftsError("mapping SIFTS rights URL mismatch")

    manifest_path = _bound_path(row["sifts_manifest_path"], label="SIFTS manifest path")
    _reject_traits_target(manifest_path, label="SIFTS manifest path")
    if mode == PINNED_MANIFEST:
        if (
            manifest_path.name != MANIFEST_NAME
            or manifest_path.parent.name != row["sifts_snapshot_id"]
        ):
            raise EcodSiftsError("SIFTS manifest path/snapshot_id mismatch")
        cached_manifest = manifest_cache.get(manifest_path)
        if cached_manifest is None:
            manifest, manifest_sha = _load_canonical_manifest(manifest_path)
            _validate_manifest_document(manifest, require_complete=True)
            cached_manifest = manifest_sha, manifest
            manifest_cache[manifest_path] = cached_manifest
        manifest_sha, manifest = cached_manifest
        if manifest_sha != row["sifts_manifest_sha256"]:
            raise EcodSiftsError("SIFTS manifest digest mismatch")
        if manifest["snapshot_id"] != row["sifts_snapshot_id"]:
            raise EcodSiftsError("SIFTS manifest snapshot_id mismatch")
        if manifest_entry not in manifest["entries"]:
            raise EcodSiftsError("SIFTS manifest does not contain the bound entry")
        manifest_ecod_fields = {
            "ecod_source_path": "ecod_source_path",
            "ecod_source_sha256": "ecod_source_sha256",
            "ecod_release": "ecod_release",
        }
        for mapping_field, manifest_field in manifest_ecod_fields.items():
            if row[mapping_field] != manifest[manifest_field]:
                raise EcodSiftsError(f"mapping/manifest ECOD mismatch for {mapping_field}")
    elif row["sifts_manifest_sha256"] != _fixture_manifest_sha(
        row["sifts_snapshot_id"], manifest_entry
    ):
        raise EcodSiftsError("offline fixture manifest projection digest mismatch")
    xml_path = manifest_path.parent / manifest_entry["path"]
    _reject_traits_target(xml_path, label="SIFTS XML path")
    cached_sifts = sifts_cache.get(xml_path)
    if cached_sifts is None:
        cached_sifts = _validate_xml_against_manifest(
            xml_path,
            manifest_entry,
            allow_plain_xml=mode == OFFLINE_FIXTURE,
        )
        sifts_cache[xml_path] = cached_sifts
    elif _manifest_entry(cached_sifts, path=xml_path) != manifest_entry:
        raise EcodSiftsError("cached SIFTS XML/manifest entry mismatch")
    if row["sifts_rights"] != cached_sifts.rights:
        raise EcodSiftsError("mapping/SIFTS XML rights statement mismatch")

    source_path = _bound_path(row["ecod_source_path"], label="ECOD source path")
    _reject_traits_target(source_path, label="ECOD source path")
    cached_ecod = ecod_cache.get(source_path)
    if cached_ecod is None:
        try:
            source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            raise EcodSiftsError(f"cannot replay ECOD source {source_path}: {exc}") from exc
        cached_ecod = file_sha256(source_path), source_lines, ecod_release(source_path)
        ecod_cache[source_path] = cached_ecod
    source_sha, source_lines, source_release = cached_ecod
    if source_sha != row["ecod_source_sha256"]:
        raise EcodSiftsError("ECOD source file digest mismatch")
    if source_release != row["ecod_release"]:
        raise EcodSiftsError("ECOD source release mismatch")
    line_index = row["ecod_line_number"] - 1
    if line_index >= len(source_lines):
        raise EcodSiftsError("ECOD source line number is out of bounds")
    source_line = source_lines[line_index]
    if hashlib.sha256(source_line.encode("utf-8")).hexdigest() != row["ecod_raw_line_sha256"]:
        raise EcodSiftsError("ECOD source line digest mismatch")
    source_parts = source_line.split("\t")
    if len(source_parts) <= max(ECOD_COLUMNS.values()):
        raise EcodSiftsError("bound ECOD source line is truncated")
    source_expectations = {
        "ecod_uid": source_parts[ECOD_COLUMNS["uid"]],
        "ecod_domain_id": source_parts[ECOD_COLUMNS["domain_id"]],
        "trait_id": f"ECOD:F.{source_parts[ECOD_COLUMNS['f_id']]}",
        "structure_id": f"PDB:{source_parts[ECOD_COLUMNS['pdb']].lower()}",
        "ecod_chain": source_parts[ECOD_COLUMNS["chain"]],
        "ecod_pdb_range": source_parts[ECOD_COLUMNS["pdb_range"]],
        "ecod_seqid_range": source_parts[ECOD_COLUMNS["seqid_range"]],
    }
    for field, expected in source_expectations.items():
        if row[field] != expected:
            raise EcodSiftsError(f"mapping/ECOD source mismatch for {field}")
    if mode == PINNED_MANIFEST and manifest["representatives_only"]:
        if source_parts[ECOD_COLUMNS["manual_rep"]] != "True":
            raise EcodSiftsError("mapping ECOD row is not a manual representative")

    try:
        native_ranges = parse_native_ranges(row["ecod_pdb_range"])
        seqid_ranges = parse_native_ranges(row["ecod_seqid_range"])
    except EcodSiftsError as exc:
        raise EcodSiftsError(f"mapping ECOD range is invalid: {exc}") from exc
    if row["native_ranges"] != [item.as_dict() for item in native_ranges]:
        raise EcodSiftsError("mapping native range projection mismatch")
    if any(item.start.insertion_code or item.end.insertion_code for item in seqid_ranges):
        raise EcodSiftsError("mapping seqid range contains insertion code")
    if any(item.start.number < 1 or item.end.number < 1 for item in seqid_ranges):
        raise EcodSiftsError("mapping seqid range must use positive PDBe positions")
    if {item.chain for item in native_ranges} != {row["chain_id"]}:
        raise EcodSiftsError("mapping native range chain mismatch")
    if {item.chain for item in seqid_ranges} != {row["chain_id"]}:
        raise EcodSiftsError("mapping seqid range chain mismatch")
    if row["ecod_chain"] != row["chain_id"]:
        raise EcodSiftsError("mapping ECOD/selected chain mismatch")
    expected_pdbe = {
        (item.chain, position)
        for item in seqid_ranges
        for position in range(item.start.number, item.end.number + 1)
    }
    expected_count = sum(item.end.number - item.start.number + 1 for item in seqid_ranges)
    if len(expected_pdbe) != expected_count:
        raise EcodSiftsError("mapping has overlapping ECOD seqid ranges")
    mapped = row["mapped_residues"]
    if not isinstance(mapped, list) or not mapped:
        raise EcodSiftsError("mapping mapped_residues must be non-empty")
    if any(not isinstance(item, dict) or set(item) != MAPPED_RESIDUE_FIELDS for item in mapped):
        raise EcodSiftsError("mapped residue has invalid fields")
    actual_pdbe: set[tuple[str, int]] = set()
    uniprot_positions: set[int] = set()
    accepted_amino_acids = set(AA3_TO_1.values())
    for residue in mapped:
        chain = residue["chain_id"]
        pdbe_position = residue["pdbe_sequence_position"]
        uniprot_position = residue["uniprot_position"]
        if chain != row["chain_id"] or type(pdbe_position) is not int or pdbe_position < 1:
            raise EcodSiftsError("mapped residue has invalid chain/PDBe position")
        if type(uniprot_position) is not int or uniprot_position < 1:
            raise EcodSiftsError("mapped residue has invalid UniProt position")
        actual_pdbe.add((chain, pdbe_position))
        if uniprot_position in uniprot_positions:
            raise EcodSiftsError("mapping reuses a UniProt position")
        uniprot_positions.add(uniprot_position)
        pdb_aa = residue["pdb_amino_acid"]
        uniprot_aa = residue["uniprot_amino_acid"]
        if (
            not isinstance(pdb_aa, str)
            or not isinstance(uniprot_aa, str)
            or pdb_aa not in accepted_amino_acids
            or uniprot_aa not in accepted_amino_acids
        ):
            raise EcodSiftsError("mapped residue has unsupported amino acid")
        if pdb_aa != uniprot_aa:
            raise EcodSiftsError("mapped residue PDB/UniProt amino-acid mismatch")
        author_number = residue["author_residue_number"]
        insertion_code = residue["author_insertion_code"]
        if author_number is None or insertion_code is None:
            if author_number is not None or insertion_code is not None:
                raise EcodSiftsError("mapped residue has partial author coordinates")
        else:
            if (
                type(author_number) is not int
                or not isinstance(insertion_code, str)
                or re.fullmatch(r"[A-Z]?", insertion_code) is None
            ):
                raise EcodSiftsError("mapped residue author coordinates are invalid")
            position = NativePosition(author_number, insertion_code)
            if not any(item.contains(chain, position) for item in native_ranges):
                raise EcodSiftsError("mapped author residue lies outside ECOD range")
    residue_order = [(item["chain_id"], item["pdbe_sequence_position"]) for item in mapped]
    if residue_order != sorted(residue_order):
        raise EcodSiftsError("mapping residues are not deterministically sorted")
    if actual_pdbe != expected_pdbe or len(mapped) != len(expected_pdbe):
        raise EcodSiftsError("mapping does not cover every ECOD defining residue exactly once")
    xml_residues: dict[tuple[str, int], list[SiftsResidue]] = {}
    for residue in cached_sifts.residues:
        xml_residues.setdefault((residue.chain, residue.pdbe_position), []).append(residue)
    accession = row["protein_id"].split(":", 1)[1]
    for residue in mapped:
        key = residue["chain_id"], residue["pdbe_sequence_position"]
        source_residues = xml_residues.get(key, [])
        if len(source_residues) != 1:
            raise EcodSiftsError(
                "mapping residue does not have exactly one SIFTS XML source residue"
            )
        source_residue = source_residues[0]
        source_author_number = (
            source_residue.native.number if source_residue.native is not None else None
        )
        source_insertion_code = (
            source_residue.native.insertion_code if source_residue.native is not None else None
        )
        expected_projection = {
            "author_residue_number": source_author_number,
            "author_insertion_code": source_insertion_code,
            "pdb_amino_acid": source_residue.pdb_amino_acid,
            "uniprot_position": source_residue.uniprot_position,
            "uniprot_amino_acid": source_residue.uniprot_amino_acid,
        }
        if source_residue.ambiguous or source_residue.uniprot_accession != accession:
            raise EcodSiftsError("mapping protein does not match SIFTS XML accession")
        if any(residue[field] != expected for field, expected in expected_projection.items()):
            raise EcodSiftsError("mapped residue projection does not match SIFTS XML")


def load_mapping_registry(
    path: Path, *, allow_offline_fixtures: bool = False
) -> dict[str, dict[str, Any]]:
    """Load mappings and replay their durable ECOD/manifest provenance.

    Production callers fail closed on ``OFFLINE_FIXTURE`` rows.  Tests must opt
    into those rows explicitly with ``allow_offline_fixtures=True``.
    """
    if not path.is_file():
        raise EcodSiftsError(f"SIFTS mapping registry does not exist: {path}")
    registry: dict[str, dict[str, Any]] = {}
    ecod_cache: dict[Path, tuple[str, list[str], str]] = {}
    manifest_cache: dict[Path, tuple[str, dict[str, Any]]] = {}
    sifts_cache: dict[Path, SiftsEntry] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise EcodSiftsError(f"{path}:{line_number}: invalid mapping JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise EcodSiftsError(f"{path}:{line_number}: mapping row is not an object")
            try:
                _validate_mapping_row(
                    row,
                    allow_offline_fixtures=allow_offline_fixtures,
                    ecod_cache=ecod_cache,
                    manifest_cache=manifest_cache,
                    sifts_cache=sifts_cache,
                )
            except EcodSiftsError as exc:
                raise EcodSiftsError(f"{path}:{line_number}: {exc}") from exc
            mapping_id = row["mapping_id"]
            if mapping_id in registry:
                raise EcodSiftsError(f"{path}:{line_number}: duplicate mapping_id {mapping_id}")
            registry[str(mapping_id)] = row
    return registry


def parse_native_ranges(value: str) -> tuple[NativeRange, ...]:
    """Parse ECOD author ranges without discarding insertion codes."""
    ranges: list[NativeRange] = []
    for raw_part in value.split(","):
        part = raw_part.strip()
        match = NATIVE_RANGE_RE.fullmatch(part)
        if match is None:
            raise EcodSiftsError(f"invalid ECOD pdb_range component {part!r}")
        start = NativePosition(int(match.group("start")), match.group("start_icode").upper())
        end = NativePosition(int(match.group("end")), match.group("end_icode").upper())
        if start > end:
            raise EcodSiftsError(f"reversed ECOD pdb_range component {part!r}")
        ranges.append(NativeRange(match.group("chain"), start, end))
    if not ranges:
        raise EcodSiftsError("ECOD pdb_range is empty")
    return tuple(ranges)


def ecod_release(path: Path) -> str:
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("# Version:"):
                version = line.split(":", 1)[1].strip()
                if not version:
                    break
                return f"ECOD {version}"
            if not line.startswith("#"):
                break
    raise EcodSiftsError(f"{path}: missing ECOD version header")


def iter_ecod_occurrences(
    path: Path,
    *,
    representatives_only: bool = True,
    parse_blocked: list[dict[str, Any]] | None = None,
) -> Iterator[EcodOccurrence]:
    """Stream valid ECOD F-level source occurrences in file order."""
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, 1):
            if raw.startswith("#") or raw.startswith("uid\t") or not raw.strip():
                continue
            parts = raw.rstrip("\n").split("\t")
            if len(parts) <= max(ECOD_COLUMNS.values()):
                raise EcodSiftsError(f"{path}:{line_number}: truncated ECOD row")
            if representatives_only and parts[ECOD_COLUMNS["manual_rep"]] != "True":
                continue
            pdb_id = parts[ECOD_COLUMNS["pdb"]].lower()
            if re.fullmatch(r"[0-9][a-z0-9]{3}", pdb_id) is None:
                detail = f"{path}:{line_number}: invalid PDB identifier {pdb_id!r}"
                if parse_blocked is None:
                    raise EcodSiftsError(detail)
                parse_blocked.append(
                    {
                        "trait_id": f"ECOD:F.{parts[ECOD_COLUMNS['f_id']]}",
                        "ecod_domain_id": parts[ECOD_COLUMNS["domain_id"]],
                        "structure_id": "",
                        "chain_id": parts[ECOD_COLUMNS["chain"]],
                        "ecod_pdb_range": parts[ECOD_COLUMNS["pdb_range"]],
                        "reason": "INVALID_ECOD_PDB_ID",
                        "detail": detail,
                    }
                )
                continue
            raw_line = raw.rstrip("\n")
            try:
                native_ranges = parse_native_ranges(parts[ECOD_COLUMNS["pdb_range"]])
                seqid_ranges = parse_native_ranges(parts[ECOD_COLUMNS["seqid_range"]])
                if any(
                    item.start.insertion_code or item.end.insertion_code for item in seqid_ranges
                ):
                    raise EcodSiftsError("ECOD seqid_range contains an insertion code")
                if any(item.start.number < 1 or item.end.number < 1 for item in seqid_ranges):
                    raise EcodSiftsError("ECOD seqid_range contains a non-positive PDBe position")
            except EcodSiftsError as exc:
                if parse_blocked is None:
                    raise
                parse_blocked.append(
                    {
                        "trait_id": f"ECOD:F.{parts[ECOD_COLUMNS['f_id']]}",
                        "ecod_domain_id": parts[ECOD_COLUMNS["domain_id"]],
                        "structure_id": f"PDB:{pdb_id}",
                        "chain_id": parts[ECOD_COLUMNS["chain"]],
                        "ecod_pdb_range": parts[ECOD_COLUMNS["pdb_range"]],
                        "reason": "INVALID_ECOD_PDB_RANGE",
                        "detail": str(exc),
                    }
                )
                continue
            yield EcodOccurrence(
                uid=parts[ECOD_COLUMNS["uid"]],
                domain_id=parts[ECOD_COLUMNS["domain_id"]],
                f_id=parts[ECOD_COLUMNS["f_id"]],
                pdb_id=pdb_id,
                chain=parts[ECOD_COLUMNS["chain"]],
                pdb_range=parts[ECOD_COLUMNS["pdb_range"]],
                seqid_range=parts[ECOD_COLUMNS["seqid_range"]],
                native_ranges=native_ranges,
                seqid_ranges=seqid_ranges,
                line_number=line_number,
                raw_line_sha256=hashlib.sha256(raw_line.encode("utf-8")).hexdigest(),
            )


def _open_xml(path: Path, *, allow_plain_xml: bool) -> bytes:
    try:
        raw = path.read_bytes()
    except (OSError, gzip.BadGzipFile) as exc:
        raise EcodSiftsError(f"cannot read SIFTS XML {path}: {exc}") from exc
    if path.name.endswith(".xml.gz"):
        try:
            return gzip.decompress(raw)
        except (OSError, gzip.BadGzipFile) as exc:
            raise EcodSiftsError(f"invalid gzip SIFTS XML {path}: {exc}") from exc
    if allow_plain_xml and path.name.endswith(".xml"):
        return raw
    raise EcodSiftsError(
        f"production SIFTS input must be an .xml.gz file: {path}; "
        "plain XML is allowed only in explicit offline fixture mode"
    )


def _normal_space(value: str | None) -> str:
    return " ".join((value or "").split())


def _normalise_uniprot_release(value: str) -> str:
    """Translate SIFTS' YYYY.NN spelling to the registry's YYYY_NN spelling."""
    match = re.fullmatch(r"([0-9]{4})[._]([0-9]{2})", value)
    if match is None:
        raise EcodSiftsError(f"invalid SIFTS UniProt version {value!r}")
    return f"{match.group(1)}_{match.group(2)}"


def load_sifts_xml(path: Path, *, allow_plain_xml: bool = False) -> SiftsEntry:
    """Load an exact residue-level mapping, requiring production gzip by default."""
    try:
        raw_file = path.read_bytes()
    except OSError as exc:
        raise EcodSiftsError(f"cannot read SIFTS XML {path}: {exc}") from exc
    xml_bytes = _open_xml(path, allow_plain_xml=allow_plain_xml)
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise EcodSiftsError(f"invalid SIFTS XML {path}: {exc}") from exc
    if root.tag != f"{NAMESPACE}entry":
        raise EcodSiftsError(f"{path}: SIFTS root element/namespace mismatch")
    if root.get("dbSource") != "PDBe" or root.get("dbCoordSys") != "PDBe":
        raise EcodSiftsError(f"{path}: SIFTS root source/coordinate system mismatch")
    pdb_id = str(root.get("dbAccessionId") or "").lower()
    if re.fullmatch(r"[0-9][a-z0-9]{3}", pdb_id) is None:
        raise EcodSiftsError(f"{path}: SIFTS root lacks a valid PDB accession")
    entry_date = _require_iso_date(root.get("date"), label=f"{path}: SIFTS entry date")
    uniprot_versions = {
        str(node.get("dbVersion"))
        for node in root.findall(f".//{NAMESPACE}listDB/{NAMESPACE}db")
        if node.get("dbSource") == "UniProt" and node.get("dbVersion")
    }
    if len(uniprot_versions) != 1:
        raise EcodSiftsError(
            f"{path}: expected one SIFTS UniProt release, found {sorted(uniprot_versions)}"
        )
    rights_node = root.find(f".//{DC_NAMESPACE}rights")
    rights = _normal_space(rights_node.text if rights_node is not None else None)
    rights_url = (
        str(rights_node.get(f"{RDF_NAMESPACE}resource") or "") if rights_node is not None else ""
    )
    if not rights:
        raise EcodSiftsError(f"{path}: SIFTS rights statement is missing")
    if rights_url != SIFTS_RIGHTS_URL:
        raise EcodSiftsError(f"{path}: SIFTS rights URL mismatch: {rights_url!r}")
    residues: list[SiftsResidue] = []
    for residue in root.findall(f".//{NAMESPACE}residue"):
        if residue.get("dbSource") != "PDBe" or residue.get("dbCoordSys") != "PDBe":
            raise EcodSiftsError(f"{path}: residue source/coordinate system mismatch")
        pdbe_position_text = str(residue.get("dbResNum") or "")
        if not pdbe_position_text.isdigit():
            raise EcodSiftsError(f"{path}: invalid PDBe sequence position {pdbe_position_text!r}")
        pdbe_position = int(pdbe_position_text)
        pdb_refs = [
            ref for ref in residue.findall(f"{NAMESPACE}crossRefDb") if ref.get("dbSource") == "PDB"
        ]
        if not pdb_refs:
            continue
        for ref in pdb_refs:
            if (
                ref.get("dbCoordSys") != "PDBresnum"
                or str(ref.get("dbAccessionId") or "").lower() != pdb_id
                or not ref.get("dbChainId")
            ):
                raise EcodSiftsError(f"{path}: invalid PDB residue cross-reference")
        uniprot_refs = [
            ref
            for ref in residue.findall(f"{NAMESPACE}crossRefDb")
            if ref.get("dbSource") == "UniProt"
        ]
        if any(ref.get("dbCoordSys") != "UniProt" for ref in uniprot_refs):
            raise EcodSiftsError(f"{path}: invalid UniProt coordinate system")
        mappings = {
            (
                str(ref.get("dbAccessionId") or ""),
                str(ref.get("dbResNum") or ""),
                str(ref.get("dbResName") or "").upper(),
            )
            for ref in uniprot_refs
        }
        for pdb_ref in pdb_refs:
            chain = str(pdb_ref.get("dbChainId") or "")
            native_text = str(pdb_ref.get("dbResNum") or "")
            native = None if native_text == "null" else NativePosition.parse(native_text)
            pdb_name = str(pdb_ref.get("dbResName") or "").upper()
            pdb_aa = AA3_TO_1.get(pdb_name, "")
            if len(mappings) == 1:
                accession, position_text, uniprot_aa = next(iter(mappings))
                position = int(position_text) if position_text.isdigit() else None
                residues.append(
                    SiftsResidue(
                        chain,
                        pdbe_position,
                        native,
                        pdb_aa,
                        accession or None,
                        position,
                        uniprot_aa or None,
                    )
                )
            else:
                residues.append(
                    SiftsResidue(
                        chain,
                        pdbe_position,
                        native,
                        pdb_aa,
                        None,
                        None,
                        None,
                        bool(mappings),
                    )
                )
    uniprot_version = next(iter(uniprot_versions))
    return SiftsEntry(
        pdb_id=pdb_id,
        entry_date=entry_date,
        uniprot_release=_normalise_uniprot_release(uniprot_version),
        uniprot_version=uniprot_version,
        xml_sha256=hashlib.sha256(raw_file).hexdigest(),
        rights=rights,
        rights_url=rights_url,
        residues=tuple(residues),
    )


def load_trait_index(path: Path) -> dict[str, Path]:
    if not path.is_dir():
        raise EcodSiftsError(f"ECOD trait directory does not exist: {path}")
    index: dict[str, Path] = {}
    for record_path in sorted(path.rglob("*.yaml")):
        match = TRAIT_ID_RE.search(record_path.read_text(encoding="utf-8", errors="replace"))
        if match is None:
            continue
        trait_id = match.group(1)
        if trait_id in index:
            raise EcodSiftsError(f"duplicate ECOD trait identifier {trait_id}")
        index[trait_id] = record_path
    return index


def load_protein_registry(path: Path) -> dict[str, dict[str, Any]]:
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from validate_uniprot_grounding import load_registry  # noqa: PLC0415

    registry, findings = load_registry(path)
    if findings:
        detail = "; ".join(f"{item.code}: {item.message}" for item in findings[:5])
        raise EcodSiftsError(f"invalid ProteinReference registry: {detail}")
    return registry


def _xml_path(directory: Path, pdb_id: str, *, allow_plain_xml: bool = False) -> Path | None:
    suffixes = (".xml",) if allow_plain_xml else (".xml.gz",)
    for suffix in suffixes:
        path = directory / f"{pdb_id}{suffix}"
        if path.is_file():
            return path
    return None


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _compress_positions(positions: Sequence[int]) -> list[dict[str, int]]:
    intervals: list[dict[str, int]] = []
    for position in sorted(set(positions)):
        if intervals and position == intervals[-1]["end"] + 1:
            intervals[-1]["end"] = position
        else:
            intervals.append({"start": position, "end": position})
    return intervals


def _candidate_id(row: Mapping[str, Any]) -> str:
    identity = {
        "trait_id": row.get("trait_id"),
        "protein_id": row.get("protein_id"),
        "source_trait_id": row.get("source_trait_id"),
        "mapping_method": row.get("mapping_method"),
        "evidence_source": row.get("evidence_source"),
        "source_release": row.get("source_release"),
        "sequence_release": row.get("sequence_release"),
        "sequence_sha256": row.get("sequence_sha256"),
        "scope": row.get("scope"),
        "coordinate_frame": row.get("coordinate_frame"),
        "intervals": row.get("intervals", []),
        "residue_positions": row.get("residue_positions", []),
        "structure_id": row.get("structure_id"),
        "chain_id": row.get("chain_id"),
        "ecod_domain_id": row.get("ecod_domain_id"),
        "sifts_mapping_id": row.get("sifts_mapping_id"),
    }
    return "ug-" + value_sha256(identity)


def _mapping_payload(
    occurrence: EcodOccurrence,
    entry: SiftsEntry,
    reference: Mapping[str, Any],
    selected: Sequence[SiftsResidue],
    release: str,
    *,
    ecod_source_path: Path,
    ecod_source_sha256: str,
    snapshot_binding: SiftsSnapshotBinding,
) -> dict[str, Any]:
    manifest_entry = dict(snapshot_binding.manifest_entry)
    return {
        "schema_version": SCHEMA_VERSION,
        "trait_id": occurrence.trait_id,
        "ecod_domain_id": occurrence.domain_id,
        "ecod_uid": occurrence.uid,
        "ecod_release": release,
        "ecod_license": ECOD_LICENSE,
        "ecod_source_path": _display_path(ecod_source_path),
        "ecod_source_sha256": ecod_source_sha256,
        "ecod_line_number": occurrence.line_number,
        "ecod_raw_line_sha256": occurrence.raw_line_sha256,
        "structure_id": f"PDB:{occurrence.pdb_id}",
        "chain_id": selected[0].chain,
        "ecod_chain": occurrence.chain,
        "ecod_pdb_range": occurrence.pdb_range,
        "ecod_seqid_range": occurrence.seqid_range,
        "native_ranges": [item.as_dict() for item in occurrence.native_ranges],
        "protein_id": reference["protein_id"],
        "sequence_sha256": reference["sequence_sha256"],
        "uniprot_release": reference["uniprot_release"],
        "sifts_snapshot_mode": snapshot_binding.mode,
        "sifts_snapshot_id": snapshot_binding.snapshot_id,
        "sifts_manifest_path": _display_path(snapshot_binding.manifest_path),
        "sifts_manifest_sha256": snapshot_binding.manifest_sha256,
        "sifts_manifest_entry": manifest_entry,
        "sifts_manifest_entry_sha256": value_sha256(manifest_entry),
        "sifts_entry_date": entry.entry_date,
        "sifts_uniprot_release": entry.uniprot_release,
        "sifts_uniprot_version": entry.uniprot_version,
        "sifts_xml_sha256": entry.xml_sha256,
        "sifts_source_url": f"{SIFTS_XML_ROOT}/{occurrence.pdb_id}.xml.gz",
        "sifts_rights": entry.rights,
        "sifts_rights_url": entry.rights_url,
        "mapped_residues": [
            {
                "chain_id": item.chain,
                "pdbe_sequence_position": item.pdbe_position,
                "author_residue_number": (item.native.number if item.native is not None else None),
                "author_insertion_code": (
                    item.native.insertion_code if item.native is not None else None
                ),
                "pdb_amino_acid": item.pdb_amino_acid,
                "uniprot_position": item.uniprot_position,
                "uniprot_amino_acid": item.uniprot_amino_acid,
            }
            for item in selected
        ],
    }


def map_occurrence(
    occurrence: EcodOccurrence,
    entry: SiftsEntry,
    registry: Mapping[str, Mapping[str, Any]],
    *,
    ecod_source_release: str,
    ecod_source_path: Path,
    ecod_source_sha256: str,
    snapshot_binding: SiftsSnapshotBinding,
    mapping_registry_path: Path,
    record_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return candidate, compact provider row, and GroundingEvidence."""
    range_chains = {item.chain for item in occurrence.native_ranges}
    if len(range_chains) != 1:
        raise EcodSiftsError("MULTI_CHAIN_ECOD_DOMAIN")
    chain = next(iter(range_chains))
    if occurrence.chain != chain:
        raise EcodSiftsError(
            f"ECOD_CHAIN_RANGE_MISMATCH: chain={occurrence.chain!r}, range_chain={chain!r}"
        )
    if entry.pdb_id != occurrence.pdb_id:
        raise EcodSiftsError("SIFTS_PDB_ID_MISMATCH")
    manifest_entry = _validate_manifest_entry(
        dict(snapshot_binding.manifest_entry), mode=snapshot_binding.mode
    )
    expected_manifest_values = {
        "pdb_id": entry.pdb_id,
        "sha256": entry.xml_sha256,
        "sifts_entry_date": entry.entry_date,
        "sifts_uniprot_release": entry.uniprot_release,
        "sifts_uniprot_version": entry.uniprot_version,
    }
    for field, expected in expected_manifest_values.items():
        if manifest_entry[field] != expected:
            raise EcodSiftsError(f"SIFTS_MANIFEST_ENTRY_MISMATCH:{field}")
    seqid_chains = {item.chain for item in occurrence.seqid_ranges}
    if seqid_chains != {chain}:
        raise EcodSiftsError(
            f"ECOD_PDB_SEQID_CHAIN_MISMATCH:pdb={sorted(range_chains)},seqid={sorted(seqid_chains)}"
        )
    expected_seqids = {
        (item.chain, position)
        for item in occurrence.seqid_ranges
        for position in range(item.start.number, item.end.number + 1)
    }
    selected_by_seqid: dict[tuple[str, int], SiftsResidue] = {}
    for residue in entry.residues:
        key = residue.chain, residue.pdbe_position
        if key not in expected_seqids:
            continue
        if key in selected_by_seqid:
            raise EcodSiftsError(f"AMBIGUOUS_SIFTS_PDBe_POSITION:{key}")
        selected_by_seqid[key] = residue
    missing_seqids = sorted(expected_seqids - set(selected_by_seqid))
    if missing_seqids:
        raise EcodSiftsError(f"INCOMPLETE_SIFTS_SEQUENCE_COVERAGE:missing={missing_seqids[:5]}")
    selected = sorted(selected_by_seqid.values(), key=lambda item: (item.chain, item.pdbe_position))
    if not selected:
        raise EcodSiftsError("ECOD_SEQID_RANGE_EMPTY")
    for item in selected:
        if item.native is not None and not any(
            native_range.contains(item.chain, item.native)
            for native_range in occurrence.native_ranges
        ):
            raise EcodSiftsError(f"SIFTS_AUTHOR_RESIDUE_OUTSIDE_ECOD_RANGE:{item.native.text()}")
    if any(item.ambiguous for item in selected):
        raise EcodSiftsError("AMBIGUOUS_SIFTS_RESIDUE_MAPPING")
    if any(item.uniprot_accession is None or item.uniprot_position is None for item in selected):
        raise EcodSiftsError("INCOMPLETE_SIFTS_RESIDUE_MAPPING")
    accessions = {str(item.uniprot_accession) for item in selected}
    if len(accessions) != 1:
        raise EcodSiftsError(f"CHIMERIC_SIFTS_MAPPING:{sorted(accessions)}")
    protein_id = f"UniProtKB:{next(iter(accessions))}"
    reference = registry.get(protein_id)
    if reference is None:
        raise EcodSiftsError(f"PROTEIN_REFERENCE_NOT_FOUND:{protein_id}")
    if reference.get("uniprot_release") != entry.uniprot_release:
        raise EcodSiftsError(
            "UNIPROT_RELEASE_MISMATCH:"
            f"registry={reference.get('uniprot_release')},sifts={entry.uniprot_release}"
        )
    sequence = reference.get("sequence")
    if not isinstance(sequence, str) or not sequence:
        raise EcodSiftsError("PROTEIN_REFERENCE_SEQUENCE_MISSING")
    mapped_positions = [int(item.uniprot_position or 0) for item in selected]
    if len(mapped_positions) != len(set(mapped_positions)):
        raise EcodSiftsError("NON_UNIQUE_UNIPROT_RESIDUE_MAPPING")
    for item in selected:
        if not item.pdb_amino_acid or not item.uniprot_amino_acid:
            native = item.native.text() if item.native is not None else "unobserved"
            raise EcodSiftsError(f"UNSUPPORTED_RESIDUE:{native}")
        position = int(item.uniprot_position or 0)
        if not 1 <= position <= len(sequence):
            raise EcodSiftsError(f"UNIPROT_POSITION_OUT_OF_BOUNDS:{position}")
        observed = sequence[position - 1]
        if item.pdb_amino_acid != item.uniprot_amino_acid:
            raise EcodSiftsError(
                "PDB_UNIPROT_RESIDUE_MISMATCH:"
                f"{item.native.text() if item.native is not None else 'unobserved'}:"
                f"{item.pdb_amino_acid}!={item.uniprot_amino_acid}"
            )
        if item.uniprot_amino_acid != observed:
            raise EcodSiftsError(
                f"REGISTRY_RESIDUE_MISMATCH:{position}:{item.uniprot_amino_acid}!={observed}"
            )
    payload = _mapping_payload(
        occurrence,
        entry,
        reference,
        selected,
        ecod_source_release,
        ecod_source_path=ecod_source_path,
        ecod_source_sha256=ecod_source_sha256,
        snapshot_binding=snapshot_binding,
    )
    entry_digest = mapping_entry_sha256(payload)
    mapping = {"mapping_id": f"ecod-sifts:{entry_digest}", **payload}
    positions = sorted(mapped_positions)
    occurrence_value: dict[str, Any] = {
        "trait_id": occurrence.trait_id,
        "protein_id": protein_id,
        "scope": "LOCALIZED",
        "coordinate_frame": (
            "UNIPROT_ISOFORM" if "-" in protein_id.split(":", 1)[1] else "UNIPROT_CANONICAL"
        ),
        "residue_positions": positions,
        "expected_residues": "".join(sequence[position - 1] for position in positions),
        "source_trait_id": occurrence.trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "ECOD via PDBe SIFTS",
        "source_release": ecod_source_release,
        "sequence_sha256": reference["sequence_sha256"],
        "structure_id": f"PDB:{occurrence.pdb_id}",
        "chain_id": chain,
        "mapping_completeness": "COMPLETE",
        "source_residue_count": len(selected),
        "mapped_residue_count": len(selected),
        "qualification_status": "LOCATION_VERIFIED",
    }
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from validate_uniprot_grounding import (  # noqa: PLC0415
        build_grounding_evidence,
        validate_grounding_evidence,
    )

    provider_release = f"SIFTS {entry.entry_date}; UniProt {entry.uniprot_release}"
    evidence = build_grounding_evidence(
        occurrence_value,
        provider_kind="SIFTS",
        provider_source=_display_path(mapping_registry_path),
        provider_release=provider_release,
        provider_entry_sha256=entry_digest,
    )
    evidence_findings = validate_grounding_evidence(evidence, path=mapping_registry_path, line=0)
    # The adapter may stage the complete, replayable projection, but ECOD/SIFTS
    # evidence is deliberately candidate-only until the central validator can
    # verify its acquisition receipts.  No other semantic finding is admissible.
    expected_receipt_lock = ["ecod_provider_receipt_required"]
    if [item.code for item in evidence_findings] != expected_receipt_lock:
        raise EcodSiftsError(
            "GROUNDING_EVIDENCE_INVALID:" + ",".join(item.code for item in evidence_findings)
        )
    occurrence_value["source_evidence_id"] = evidence["evidence_id"]
    intervals = _compress_positions(positions)
    candidate: dict[str, Any] = {
        "trait_id": occurrence.trait_id,
        "record_path": _display_path(record_path),
        "source_namespace": "ECOD",
        "trait_axis": "STRUCTURE",
        "trait_category": "STRUCT_FOLD",
        "protein_id": protein_id,
        "protein_label": reference["protein_label"],
        "taxon_id": reference["taxon_id"],
        "taxon_label": reference["taxon_label"],
        "sequence_length": reference["sequence_length"],
        "sequence_sha256": reference["sequence_sha256"],
        "sequence_release": reference["uniprot_release"],
        "reviewed": reference["reviewed"],
        "scope": "LOCALIZED",
        "coordinate_frame": occurrence_value["coordinate_frame"],
        "intervals": intervals,
        "residue_positions": positions,
        "expected_residues": occurrence_value["expected_residues"],
        "source_trait_id": occurrence.trait_id,
        "mapping_method": "SIFTS_RESIDUE_MAPPING",
        "evidence_source": "ECOD via PDBe SIFTS",
        "source_release": ecod_source_release,
        "evidence_tier": "B",
        "mapping_completeness": "COMPLETE",
        "source_residue_count": len(selected),
        "mapped_residue_count": len(selected),
        "structure_id": f"PDB:{occurrence.pdb_id}",
        "chain_id": chain,
        "ecod_domain_id": occurrence.domain_id,
        "ecod_pdb_range": occurrence.pdb_range,
        "ecod_native_ranges": [item.as_dict() for item in occurrence.native_ranges],
        "sifts_mapping_id": mapping["mapping_id"],
        "sifts_release": provider_release,
        "candidate_status": "LOCATION_VERIFIED",
        "qualification_status": "CANDIDATE_PROTEIN",
        "reasons": [],
        "provider_evidence": [
            {
                "kind": "sifts_mapping",
                "path": _display_path(mapping_registry_path),
                "key": mapping["mapping_id"],
                "source": "PDBe SIFTS",
                "release": provider_release,
                "entry_sha256": entry_digest,
                "trait_id": occurrence.trait_id,
            }
        ],
        "trait_occurrence": occurrence_value,
        "grounding_evidence": evidence,
    }
    candidate["candidate_id"] = _candidate_id(candidate)
    return candidate, mapping, evidence


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def _manifest_entry(entry: SiftsEntry, *, path: Path) -> dict[str, Any]:
    return {
        "pdb_id": entry.pdb_id,
        "path": path.name,
        "sha256": entry.xml_sha256,
        "sifts_entry_date": entry.entry_date,
        "sifts_uniprot_release": entry.uniprot_release,
        "sifts_uniprot_version": entry.uniprot_version,
        "url": f"{SIFTS_XML_ROOT}/{entry.pdb_id}.xml.gz",
    }


def _validate_xml_against_manifest(
    path: Path,
    manifest_entry: Mapping[str, Any],
    *,
    allow_plain_xml: bool = False,
) -> SiftsEntry:
    entry = load_sifts_xml(path, allow_plain_xml=allow_plain_xml)
    actual = _manifest_entry(entry, path=path)
    if actual != dict(manifest_entry):
        raise EcodSiftsError(f"SIFTS XML does not match immutable manifest entry: {path}")
    return entry


def _offline_fixture_binding(path: Path, entry: SiftsEntry) -> SiftsSnapshotBinding:
    snapshot_id = "offline-fixture"
    manifest_entry = _manifest_entry(entry, path=path)
    _validate_manifest_entry(manifest_entry, mode=OFFLINE_FIXTURE)
    return SiftsSnapshotBinding(
        mode=OFFLINE_FIXTURE,
        snapshot_id=snapshot_id,
        manifest_path=path.parent / MANIFEST_NAME,
        manifest_sha256=_fixture_manifest_sha(snapshot_id, manifest_entry),
        manifest_entry=manifest_entry,
    )


def _snapshot_contract(
    *,
    snapshot_id: str,
    ecod_path: Path,
    release: str,
    representatives_only: bool,
    pdb_ids: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_mode": PINNED_MANIFEST,
        "snapshot_id": snapshot_id,
        "source": "PDBe SIFTS residue-level XML",
        "source_root": SIFTS_XML_ROOT,
        "rights_url": SIFTS_RIGHTS_URL,
        "ecod_source_path": _display_path(ecod_path),
        "ecod_source_sha256": file_sha256(ecod_path),
        "ecod_release": release,
        "representatives_only": representatives_only,
        "requested_pdb_count": len(pdb_ids),
        "requested_pdb_ids_sha256": value_sha256(list(pdb_ids)),
    }


def _completed_snapshot_bindings(
    directory: Path,
    *,
    ecod_path: Path,
    release: str,
    representatives_only: bool,
) -> dict[str, SiftsSnapshotBinding]:
    _reject_traits_target(directory, label="SIFTS snapshot path")
    manifest_path = directory / MANIFEST_NAME
    manifest, manifest_sha = _load_canonical_manifest(manifest_path)
    snapshot_id = directory.resolve().name
    _validate_snapshot_id(snapshot_id)
    expected = {
        "snapshot_id": snapshot_id,
        "ecod_source_path": _display_path(ecod_path),
        "ecod_source_sha256": file_sha256(ecod_path),
        "ecod_release": release,
        "representatives_only": representatives_only,
    }
    _validate_manifest_document(manifest, expected_contract=expected, require_complete=True)
    bindings: dict[str, SiftsSnapshotBinding] = {}
    for manifest_entry in manifest["entries"]:
        path = directory / manifest_entry["path"]
        if not path.is_file():
            raise EcodSiftsError(f"SIFTS snapshot file is missing: {path}")
        pdb_id = manifest_entry["pdb_id"]
        bindings[pdb_id] = SiftsSnapshotBinding(
            mode=PINNED_MANIFEST,
            snapshot_id=snapshot_id,
            manifest_path=manifest_path,
            manifest_sha256=manifest_sha,
            manifest_entry=manifest_entry,
        )
    return bindings


def _validate_build_paths(args: argparse.Namespace) -> None:
    outputs = [args.candidates, args.mappings, args.evidence, args.blocked]
    output_keys = [_physical_path_key(path) for path in outputs]
    if len(set(output_keys)) != 4:
        raise EcodSiftsError(
            "--candidates, --mappings, --evidence, and --blocked must be four distinct paths"
        )
    _reject_traits_target(args.sifts_dir, label="SIFTS snapshot path")
    protected_inputs = {
        _physical_path_key(args.ecod),
        _physical_path_key(args.protein_registry),
    }
    for path in outputs:
        _reject_build_output_target(path, selected_traits_root=args.traits)
        resolved = path.resolve()
        if _physical_path_key(path) in protected_inputs:
            raise EcodSiftsError(f"output path aliases an input file: {path}")
        if _is_under(resolved, args.sifts_dir):
            raise EcodSiftsError(f"output path must not be inside SIFTS snapshot: {path}")


def build(args: argparse.Namespace) -> int:
    _validate_build_paths(args)
    release = ecod_release(args.ecod)
    ecod_sha256 = file_sha256(args.ecod)
    registry = load_protein_registry(args.protein_registry)
    traits = load_trait_index(args.traits)
    snapshot_bindings = (
        {}
        if args.offline_fixture_mode
        else _completed_snapshot_bindings(
            args.sifts_dir,
            ecod_path=args.ecod,
            release=release,
            representatives_only=not args.all_occurrences,
        )
    )
    sifts_cache: dict[str, SiftsEntry] = {}
    candidates: list[dict[str, Any]] = []
    mappings: dict[str, dict[str, Any]] = {}
    evidence: dict[str, dict[str, Any]] = {}
    blocked: list[dict[str, Any]] = []
    seen_candidate_ids: dict[str, str] = {}
    occurrences = iter_ecod_occurrences(
        args.ecod,
        representatives_only=not args.all_occurrences,
        parse_blocked=blocked,
    )
    for occurrence in occurrences:
        if args.limit is not None and len(candidates) + len(blocked) >= args.limit:
            break
        record_path = traits.get(occurrence.trait_id)
        if record_path is None:
            reason = "ECOD_TRAIT_RECORD_NOT_FOUND"
        else:
            if args.offline_fixture_mode:
                snapshot_binding = None
                xml_path = _xml_path(args.sifts_dir, occurrence.pdb_id, allow_plain_xml=True)
                missing_reason = "SIFTS_FIXTURE_XML_NOT_FOUND"
            else:
                snapshot_binding = snapshot_bindings.get(occurrence.pdb_id)
                xml_path = (
                    args.sifts_dir / snapshot_binding.manifest_entry["path"]
                    if snapshot_binding is not None
                    else None
                )
                missing_reason = "SIFTS_XML_NOT_IN_MANIFEST"
            if xml_path is None:
                reason = missing_reason
            else:
                try:
                    entry = sifts_cache.get(occurrence.pdb_id)
                    if entry is None:
                        if args.offline_fixture_mode:
                            entry = load_sifts_xml(xml_path, allow_plain_xml=True)
                            snapshot_binding = _offline_fixture_binding(xml_path, entry)
                        else:
                            if snapshot_binding is None:
                                raise EcodSiftsError("SIFTS_XML_NOT_IN_MANIFEST")
                            entry = _validate_xml_against_manifest(
                                xml_path, snapshot_binding.manifest_entry
                            )
                        sifts_cache[occurrence.pdb_id] = entry
                    elif args.offline_fixture_mode:
                        snapshot_binding = _offline_fixture_binding(xml_path, entry)
                    if snapshot_binding is None:
                        raise EcodSiftsError("SIFTS_SNAPSHOT_BINDING_MISSING")
                    candidate, mapping, grounding_evidence = map_occurrence(
                        occurrence,
                        entry,
                        registry,
                        ecod_source_release=release,
                        ecod_source_path=args.ecod,
                        ecod_source_sha256=ecod_sha256,
                        snapshot_binding=snapshot_binding,
                        mapping_registry_path=args.mappings,
                        record_path=record_path,
                    )
                except EcodSiftsError as exc:
                    reason = str(exc)
                else:
                    previous = seen_candidate_ids.get(candidate["candidate_id"])
                    if previous is not None and previous != mapping["mapping_id"]:
                        reason = "CANDIDATE_ID_COLLISION_DIFFERENT_MAPPING"
                    elif previous is None:
                        seen_candidate_ids[candidate["candidate_id"]] = mapping["mapping_id"]
                        candidates.append(candidate)
                        mappings[mapping["mapping_id"]] = mapping
                        evidence[grounding_evidence["evidence_id"]] = grounding_evidence
                        continue
                    else:
                        continue
        blocked.append(
            {
                "trait_id": occurrence.trait_id,
                "ecod_domain_id": occurrence.domain_id,
                "structure_id": f"PDB:{occurrence.pdb_id}",
                "chain_id": occurrence.chain,
                "ecod_pdb_range": occurrence.pdb_range,
                "reason": reason.split(":", 1)[0],
                "detail": reason,
            }
        )
    candidates.sort(key=lambda row: (row["trait_id"], row["candidate_id"]))
    mapping_rows = [mappings[key] for key in sorted(mappings)]
    evidence_rows = [evidence[key] for key in sorted(evidence)]
    blocked.sort(
        key=lambda row: (row["trait_id"], row["ecod_domain_id"], row["structure_id"], row["reason"])
    )
    _atomic_write(args.candidates, _jsonl(candidates))
    _atomic_write(args.mappings, _jsonl(mapping_rows))
    _atomic_write(args.evidence, _jsonl(evidence_rows))
    _atomic_write(args.blocked, _jsonl(blocked))
    reason_counts = Counter(row["reason"] for row in blocked)
    print(
        f"ECOD {release}: candidates={len(candidates):,}; "
        f"provider mappings={len(mapping_rows):,}; blocked={len(blocked):,}"
    )
    for reason, count in sorted(reason_counts.items()):
        print(f"  {reason}: {count:,}")
    return 0


def _wanted_pdb_ids(path: Path, *, all_occurrences: bool) -> list[str]:
    wanted: set[str] = set()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, 1):
            if raw.startswith("#") or raw.startswith("uid\t") or not raw.strip():
                continue
            parts = raw.rstrip("\n").split("\t")
            if len(parts) <= max(ECOD_COLUMNS.values()):
                raise EcodSiftsError(f"{path}:{line_number}: truncated ECOD row")
            if not all_occurrences and parts[ECOD_COLUMNS["manual_rep"]] != "True":
                continue
            pdb_id = parts[ECOD_COLUMNS["pdb"]].lower()
            if re.fullmatch(r"[0-9][a-z0-9]{3}", pdb_id) is None:
                if not pdb_id:
                    continue
                raise EcodSiftsError(f"{path}:{line_number}: invalid PDB identifier {pdb_id!r}")
            wanted.add(pdb_id)
    return sorted(wanted)


def _manifest_value(
    contract: Mapping[str, Any],
    entries: Mapping[str, Mapping[str, Any]],
    failures: Mapping[str, str],
) -> dict[str, Any]:
    complete = len(entries) == contract["requested_pdb_count"] and not failures
    return {
        **contract,
        "entries": [dict(entries[key]) for key in sorted(entries)],
        "failures": [{"pdb_id": key, "error": failures[key]} for key in sorted(failures)],
        "complete": complete,
    }


def _write_manifest(
    path: Path,
    contract: Mapping[str, Any],
    entries: Mapping[str, Mapping[str, Any]],
    failures: Mapping[str, str],
) -> dict[str, Any]:
    manifest = _manifest_value(contract, entries, failures)
    _validate_manifest_document(manifest, expected_contract=contract)
    _atomic_write(path, canonical_json(manifest) + "\n")
    return manifest


def fetch(args: argparse.Namespace) -> int:
    snapshot_id = _validate_snapshot_id(args.snapshot_id)
    _reject_traits_target(args.snapshot_dir, label="SIFTS snapshot root")
    snapshot_dir = args.snapshot_dir / snapshot_id
    _reject_traits_target(snapshot_dir, label="SIFTS snapshot path")
    release = ecod_release(args.ecod)
    pdb_ids = _wanted_pdb_ids(args.ecod, all_occurrences=args.all_occurrences)
    if args.limit is not None:
        pdb_ids = pdb_ids[: args.limit]
    contract = _snapshot_contract(
        snapshot_id=snapshot_id,
        ecod_path=args.ecod,
        release=release,
        representatives_only=not args.all_occurrences,
        pdb_ids=pdb_ids,
    )
    print(f"{release}: plan {len(pdb_ids):,} residue-level SIFTS XML file(s) under {snapshot_dir}")
    if not args.apply:
        print("dry-run; no files written (pass --apply to fetch)")
        for pdb_id in pdb_ids[:5]:
            print(f"  {SIFTS_XML_ROOT}/{pdb_id}.xml.gz")
        return 0
    manifest_path = snapshot_dir / MANIFEST_NAME
    if snapshot_dir.exists() and not snapshot_dir.is_dir():
        raise EcodSiftsError(f"SIFTS snapshot path is not a directory: {snapshot_dir}")
    if manifest_path.is_file():
        manifest, _ = _load_canonical_manifest(manifest_path)
        _validate_manifest_document(manifest, expected_contract=contract)
    else:
        try:
            existing = list(snapshot_dir.iterdir()) if snapshot_dir.is_dir() else []
        except OSError as exc:
            raise EcodSiftsError(f"cannot inspect SIFTS snapshot {snapshot_dir}: {exc}") from exc
        if existing:
            raise EcodSiftsError(f"refusing unmanifested files in SIFTS snapshot: {snapshot_dir}")
        try:
            snapshot_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise EcodSiftsError(f"cannot create SIFTS snapshot {snapshot_dir}: {exc}") from exc
        manifest = _write_manifest(manifest_path, contract, {}, {})

    entries = {item["pdb_id"]: item for item in manifest["entries"]}
    failures = {item["pdb_id"]: item["error"] for item in manifest["failures"]}
    requested_ids = set(pdb_ids)
    unexpected_ids = (set(entries) | set(failures)) - requested_ids
    if unexpected_ids:
        raise EcodSiftsError(
            "SIFTS manifest contains PDB IDs outside its immutable request: "
            f"{sorted(unexpected_ids)}"
        )
    if manifest["complete"]:
        for pdb_id in pdb_ids:
            target = snapshot_dir / f"{pdb_id}.xml.gz"
            if not target.is_file():
                raise EcodSiftsError(f"completed SIFTS snapshot is missing bound file: {target}")
            _validate_xml_against_manifest(target, entries[pdb_id])
        print(f"fetched/verified={len(entries):,}; failures=0 (immutable snapshot)")
        return 0

    for number, pdb_id in enumerate(pdb_ids, 1):
        target = snapshot_dir / f"{pdb_id}.xml.gz"
        url = f"{SIFTS_XML_ROOT}/{pdb_id}.xml.gz"
        existing_entry = entries.get(pdb_id)
        if existing_entry is not None:
            if not target.is_file():
                raise EcodSiftsError(f"manifest-bound SIFTS file is missing: {target}")
            _validate_xml_against_manifest(target, existing_entry)
            failures.pop(pdb_id, None)
            _write_manifest(manifest_path, contract, entries, failures)
            continue
        if target.is_file():
            try:
                loaded = load_sifts_xml(target)
                if loaded.pdb_id != pdb_id:
                    raise EcodSiftsError(
                        f"existing file contains PDB {loaded.pdb_id}, expected {pdb_id}"
                    )
                entries[pdb_id] = _manifest_entry(loaded, path=target)
                failures.pop(pdb_id, None)
            except EcodSiftsError as exc:
                raise EcodSiftsError(f"unmanifested existing SIFTS file is invalid: {exc}") from exc
        else:
            descriptor = -1
            temporary: Path | None = None
            try:
                with urllib.request.urlopen(url, timeout=args.timeout) as response:
                    payload = response.read()
                descriptor, temporary_name = tempfile.mkstemp(
                    prefix=f".{pdb_id}.", suffix=".xml.gz", dir=snapshot_dir
                )
                temporary = Path(temporary_name)
                with os.fdopen(descriptor, "wb") as handle:
                    descriptor = -1
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                loaded = load_sifts_xml(temporary)
                if loaded.pdb_id != pdb_id:
                    raise EcodSiftsError(f"downloaded PDB {loaded.pdb_id} for requested {pdb_id}")
                os.replace(temporary, target)
                temporary = None
                entries[pdb_id] = _manifest_entry(loaded, path=target)
                failures.pop(pdb_id, None)
            except (OSError, urllib.error.URLError, EcodSiftsError) as exc:
                failures[pdb_id] = str(exc)
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        _write_manifest(manifest_path, contract, entries, failures)
        if number % 100 == 0:
            print(f"  checked {number:,}/{len(pdb_ids):,}")
    manifest = _write_manifest(manifest_path, contract, entries, failures)
    print(f"fetched/verified={len(entries):,}; failures={len(failures):,}")
    if manifest["complete"]:
        print(f"immutable manifest: {manifest_path}")
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    subparsers = ap.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="plan or fetch SIFTS XML")
    fetch_parser.add_argument("--ecod", type=Path, default=DEFAULT_ECOD)
    fetch_parser.add_argument(
        "--snapshot-dir", type=Path, default=REPO_ROOT / "data" / "raw" / "sifts-xml"
    )
    fetch_parser.add_argument("--snapshot-id", required=True)
    fetch_parser.add_argument("--all-occurrences", action="store_true")
    fetch_parser.add_argument("--limit", type=int)
    fetch_parser.add_argument("--timeout", type=float, default=60.0)
    fetch_parser.add_argument("--apply", action="store_true")
    fetch_parser.set_defaults(func=fetch)

    build_parser = subparsers.add_parser("build", help="build offline candidate ledgers")
    build_parser.add_argument("--ecod", type=Path, default=DEFAULT_ECOD)
    build_parser.add_argument("--traits", type=Path, default=DEFAULT_TRAITS)
    build_parser.add_argument("--sifts-dir", type=Path, required=True)
    build_parser.add_argument("--protein-registry", type=Path, default=DEFAULT_PROTEINS)
    build_parser.add_argument("--candidates", type=Path, required=True)
    build_parser.add_argument("--mappings", type=Path, required=True)
    build_parser.add_argument("--evidence", type=Path, required=True)
    build_parser.add_argument("--blocked", type=Path, required=True)
    build_parser.add_argument(
        "--offline-fixture-mode",
        action="store_true",
        help=(
            "allow uncompressed, unmanifested synthetic XML for tests; emitted "
            "mappings are marked OFFLINE_FIXTURE and rejected by production loaders"
        ),
    )
    build_parser.add_argument("--all-occurrences", action="store_true")
    build_parser.add_argument("--limit", type=int)
    build_parser.set_defaults(func=build)
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        print("error: --limit must be positive", file=sys.stderr)
        return 2
    try:
        return int(args.func(args))
    except EcodSiftsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
