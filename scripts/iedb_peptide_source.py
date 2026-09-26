"""Read a pinned IEDB export and locate peptides on existing example proteins.

These functions produce source facts and candidate locations. Qualification and
record installation belong to the reviewed grounding workflow. Native antigen
positions constrain a match only when that antigen is the exact parent protein.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from validate_uniprot_grounding import UNIPROT_RE, validate_protein_reference

SOURCE_URL = "https://www.iedb.org/downloader.php?file_name=doc/epitope_full_v3.zip"
CSV_MEMBER = "epitope_full_v3.csv"
GROUP_HEADER = ("Epitope ID",) + ("Epitope",) * 16 + ("Related Object",) * 15
COLUMN_HEADER = (
    "IEDB IRI", "Object Type", "Name", "Modified Residue(s)", "Modifications",
    "Starting Position", "Ending Position", "IRI", "Synonyms", "Source Molecule",
    "Source Molecule IRI", "Molecule Parent", "Molecule Parent IRI", "Source Organism",
    "Source Organism IRI", "Species", "Species IRI", "Epitope Relation", "Object Type",
    "Name", "Starting Position", "Ending Position", "IRI", "Synonyms", "Source Molecule",
    "Source Molecule IRI", "Molecule Parent", "Molecule Parent IRI", "Source Organism",
    "Source Organism IRI", "Species", "Species IRI",
)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_TRAIT_ID = re.compile(r"IEDB:([1-9][0-9]*)")
_PEPTIDE = re.compile(r"[ACDEFGHIKLMNPQRSTVWY]{5,50}")
_POSITION = re.compile(r"[1-9][0-9]*")


class IedbSourceError(ValueError):
    """A source, identity, sequence, or coordinate requirement failed."""


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def value_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class ExportPins:
    archive_sha256: str
    csv_sha256: str
    receipt_sha256: str

    def __post_init__(self):
        for value in (self.archive_sha256, self.csv_sha256, self.receipt_sha256):
            if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
                raise IedbSourceError("export pins must be complete SHA-256 digests")


@dataclass(frozen=True)
class NativeRow:
    data_record_index: int
    values: tuple[str, ...]

    def __post_init__(self):
        if type(self.data_record_index) is not int or self.data_record_index < 1:
            raise IedbSourceError("native row index must be a positive integer")
        if (not isinstance(self.values, tuple) or len(self.values) != len(COLUMN_HEADER)
                or any(not isinstance(value, str) for value in self.values)):
            raise IedbSourceError("native IEDB rows require exactly 32 text columns")

    @property
    def row_sha256(self) -> str:
        return value_sha256(self.values)


@dataclass(frozen=True)
class VerifiedExport:
    pins: ExportPins
    rows: dict[str, tuple[NativeRow, ...]]
    data_records_scanned: int
    fetched_at: str

    @property
    def source_release(self) -> str:
        return f"epitope_full_v3; sha256:{self.pins.csv_sha256}"


def _uri_identifier(value: str, *, hosts: set[str], prefix: str) -> str | None:
    # urlsplit strips some raw control characters; identifier agreement must not.
    if not isinstance(value, str) or any(ord(char) <= 32 or ord(char) == 127 for char in value):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if (parsed.scheme not in {"http", "https"} or parsed.netloc not in hosts
            or parsed.query or parsed.fragment or not parsed.path.startswith(prefix)):
        return None
    tail = parsed.path.removeprefix(prefix)
    return tail if tail and "/" not in tail else None


def uniprot_id(value: str) -> str | None:
    """Retain exact accessions, including isoform suffixes; never truncate an ID."""
    accession = _uri_identifier(
        value, hosts={"www.uniprot.org", "uniprot.org"}, prefix="/uniprot/"
    )
    protein_id = f"UniProtKB:{accession}" if accession else ""
    return protein_id if UNIPROT_RE.fullmatch(protein_id) else None


def _trait_id(value: str) -> str | None:
    identifier = _uri_identifier(
        value, hosts={"www.iedb.org", "iedb.org"}, prefix="/epitope/"
    )
    trait_id = f"IEDB:{identifier}" if identifier else ""
    return trait_id if _TRAIT_ID.fullmatch(trait_id) else None


def read_verified_export(
    archive_path: Path, receipt_path: Path, pins: ExportPins, wanted: set[str]
) -> VerifiedExport:
    """Replay the fetched archive, its complete CSV member, and exact native rows.

    Both complete member reads reach EOF, checking ZIP CRCs. The archive and
    receipt are checked again after reading to reject concurrent replacement.
    Duplicate epitope rows remain explicit for the localization gate to reject.
    """
    if any(not isinstance(item, str) or not _TRAIT_ID.fullmatch(item) for item in wanted):
        raise IedbSourceError("requested traits must be exact IEDB identifiers")
    if _sha256(receipt_path) != pins.receipt_sha256:
        raise IedbSourceError("fetch receipt checksum mismatch")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    required = {
        "bytes", "content_type", "destination", "fetched_at", "requested_url",
        "resolved_url", "sha256",
    }
    if not isinstance(receipt, dict) or set(receipt) != required:
        raise IedbSourceError("invalid fetch receipt fields")
    if (receipt["requested_url"] != SOURCE_URL or receipt["resolved_url"] != SOURCE_URL
            or receipt["sha256"] != pins.archive_sha256
            or type(receipt["bytes"]) is not int or receipt["bytes"] <= 0
            or receipt["bytes"] != archive_path.stat().st_size
            or not isinstance(receipt["destination"], str)
            or Path(receipt["destination"]).resolve() != archive_path.resolve()
            or not isinstance(receipt["content_type"], str)
            or not receipt["content_type"].strip()):
        raise IedbSourceError("fetch receipt does not bind the official IEDB archive")
    try:
        fetched_at = datetime.fromisoformat(receipt["fetched_at"])
        if fetched_at.tzinfo is None:
            raise ValueError("timestamp lacks a timezone")
    except (TypeError, ValueError) as exc:
        raise IedbSourceError("invalid fetch timestamp") from exc
    if _sha256(archive_path) != pins.archive_sha256:
        raise IedbSourceError("archive checksum mismatch")
    selected: dict[str, list[NativeRow]] = {}
    scanned = 0
    with zipfile.ZipFile(archive_path) as archive:
        members = [item for item in archive.infolist() if item.filename == CSV_MEMBER]
        if len(members) != 1 or members[0].is_dir():
            raise IedbSourceError("archive requires one exact epitope CSV member")
        digest = hashlib.sha256()
        with archive.open(members[0]) as member:
            while chunk := member.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != pins.csv_sha256:
            raise IedbSourceError("CSV member checksum mismatch")
        with archive.open(members[0]) as member:
            with io.TextIOWrapper(member, encoding="utf-8", newline="") as handle:
                rows = csv.reader(handle)
                if (tuple(next(rows, ())) != GROUP_HEADER
                        or tuple(next(rows, ())) != COLUMN_HEADER):
                    raise IedbSourceError("IEDB export headers changed")
                for scanned, row in enumerate(rows, start=1):
                    if len(row) != len(COLUMN_HEADER):
                        raise IedbSourceError(f"invalid column count at native row {scanned}")
                    trait_id = _trait_id(row[0])
                    if trait_id in wanted:
                        selected.setdefault(trait_id, []).append(NativeRow(scanned, tuple(row)))
    if _sha256(archive_path) != pins.archive_sha256 or _sha256(receipt_path) != pins.receipt_sha256:
        raise IedbSourceError("source inputs changed while replaying the export")
    return VerifiedExport(
        pins, {key: tuple(value) for key, value in selected.items()}, scanned,
        receipt["fetched_at"],
    )


@dataclass(frozen=True)
class PeptideLocation:
    trait_id: str
    protein_id: str
    peptide: str
    start: int
    end: int
    coordinate_frame: str
    sequence_sha256: str
    uniprot_release: str
    protein_reference_sha256: str
    native_row_sha256: str
    native_data_record_index: int


def locate_existing_peptide(
    record: dict, reference: dict, native_rows: tuple[NativeRow, ...]
) -> PeptideLocation:
    """Compute one unique literal match on the complete, exact existing carrier."""
    trait_id = record.get("identifier")
    peptide = record.get("sequence_pattern")
    if (not isinstance(trait_id, str) or not _TRAIT_ID.fullmatch(trait_id)
            or record.get("trait_axis") != "SEQUENCE"
            or record.get("trait_category") != "SEQ_EPITOPE"
            or record.get("term_kind") != "CLASS"
            or not isinstance(peptide, str) or not _PEPTIDE.fullmatch(peptide)):
        raise IedbSourceError("record is not an exact unmodified IEDB peptide class")
    findings = validate_protein_reference(reference, path=Path("<IEDB reference>"), line=0)
    if findings:
        raise IedbSourceError("invalid complete ProteinReference: " + findings[0].code)
    protein_id = reference["protein_id"]
    examples = record.get("canonical_examples") or []
    if not isinstance(examples, list) or sum(
        isinstance(example, dict) and example.get("protein_id") == protein_id
        for example in examples
    ) != 1:
        raise IedbSourceError("protein must occur exactly once in the existing examples")
    if len(native_rows) != 1:
        raise IedbSourceError("exactly one native epitope row is required")
    native = native_rows[0]
    row = native.values
    if (_trait_id(row[0]) != trait_id or row[1] != "Linear peptide" or row[2] != peptide
            or row[3].strip() or row[4].strip()):
        raise IedbSourceError("native epitope identity, type, peptide or modifications disagree")
    if uniprot_id(row[12]) != protein_id:
        raise IedbSourceError("native parent differs from the exact existing protein")
    sequence = reference["sequence"]
    start = sequence.find(peptide)
    if start < 0:
        raise IedbSourceError("peptide is absent from the complete acquired sequence")
    if sequence.find(peptide, start + 1) >= 0:
        raise IedbSourceError("peptide has multiple literal matches, including overlaps")
    interval = (start + 1, start + len(peptide))
    if uniprot_id(row[10]) == protein_id and (row[5] or row[6]):
        if (not _POSITION.fullmatch(row[5]) or not _POSITION.fullmatch(row[6])
                or (int(row[5]), int(row[6])) != interval):
            raise IedbSourceError("native coordinates on this exact protein disagree")
    return PeptideLocation(
        trait_id, protein_id, peptide, *interval,
        "UNIPROT_ISOFORM" if UNIPROT_RE.fullmatch(protein_id).group(2) else "UNIPROT_CANONICAL",
        reference["sequence_sha256"], reference["uniprot_release"], value_sha256(reference),
        native.row_sha256, native.data_record_index,
    )
