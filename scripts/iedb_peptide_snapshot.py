"""Immutable native IEDB facts for an exact-peptide grounding provider.

This module has no writer. Consumers must supply a reviewed,
fixed snapshot byte checksum, independent of candidate or evidence input.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import PurePosixPath

from iedb_peptide_source import (
    SOURCE_URL, ExportPins, IedbSourceError, NativeRow, PeptideLocation,
    VerifiedExport, locate_existing_peptide, value_sha256,
)

LICENSE = "CC-BY-4.0"
SEMANTIC_FIELDS = (
    "identifier", "label", "definition", "definition_source", "trait_axis",
    "trait_category", "term_kind", "sequence_pattern", "license",
)
FACT_FIELDS = {
    "fact_sha256", "record_path", "record_semantics", "protein_reference",
    "native_row", "source_pins",
}
SNAPSHOT_FIELDS = {
    "schema_version", "source_url", "license", "source_release", "source_pins",
    "fetch_receipt_text", "source_records_scanned", "facts", "snapshot_id",
}


def _receipt(text: str, pins: ExportPins) -> dict:
    if not isinstance(text, str) or hashlib.sha256(text.encode()).hexdigest() != pins.receipt_sha256:
        raise IedbSourceError("capsule fetch receipt bytes differ from the acquired receipt")
    receipt = json.loads(text)
    fields = {
        "bytes", "content_type", "destination", "fetched_at", "requested_url",
        "resolved_url", "sha256",
    }
    if (not isinstance(receipt, dict) or set(receipt) != fields
            or receipt["requested_url"] != SOURCE_URL or receipt["resolved_url"] != SOURCE_URL
            or receipt["sha256"] != pins.archive_sha256
            or type(receipt["bytes"]) is not int or receipt["bytes"] <= 0):
        raise IedbSourceError("capsule requires the official IEDB acquisition receipt")
    if any(not isinstance(receipt[k], str) or not receipt[k].strip()
           for k in ("content_type", "destination", "fetched_at")):
        raise IedbSourceError("capsule acquisition metadata is incomplete")
    try:
        stamp = datetime.fromisoformat(receipt["fetched_at"])
        if stamp.tzinfo is None:
            raise ValueError("timestamp lacks timezone")
    except ValueError as exc:
        raise IedbSourceError("capsule acquisition timestamp is invalid") from exc
    return receipt


def record_semantics(record: dict) -> dict:
    result = {name: record.get(name) for name in SEMANTIC_FIELDS}
    if any(not isinstance(value, str) or not value.strip() for value in result.values()):
        raise IedbSourceError("source fact requires complete trait meaning and license fields")
    return result


def _native(row: dict) -> NativeRow:
    if not isinstance(row, dict) or set(row) != {"data_record_index", "values"}:
        raise IedbSourceError("invalid capsule native-row projection")
    if not isinstance(row["values"], list):
        raise IedbSourceError("capsule native row must preserve the complete column list")
    native = NativeRow(row["data_record_index"], tuple(row["values"]))
    # urllib's URL parser can discard controls; native identifiers must survive
    # without that normalization before the existing exact-ID parser sees them.
    for index in (0, 10, 12):
        if any(ord(char) <= 32 or ord(char) == 127 for char in native.values[index]):
            raise IedbSourceError("native identifier contains whitespace or control characters")
    return native


def validate_fact(fact: dict, pins: ExportPins) -> PeptideLocation:
    if not isinstance(fact, dict) or set(fact) != FACT_FIELDS:
        raise IedbSourceError("invalid IEDB source-fact fields")
    if fact["source_pins"] != asdict(pins):
        raise IedbSourceError("source fact belongs to another native export")
    payload = {key: value for key, value in fact.items() if key != "fact_sha256"}
    if fact["fact_sha256"] != value_sha256(payload):
        raise IedbSourceError("source fact digest mismatch")
    path = fact["record_path"]
    if (not isinstance(path, str) or PurePosixPath(path).is_absolute()
            or ".." in PurePosixPath(path).parts
            or str(PurePosixPath(path)) != path or not path.startswith("data/traits/")
            or PurePosixPath(path).suffix not in {".yaml", ".yml"}):
        raise IedbSourceError("source-fact record path must be canonical and repo-relative")
    semantics = fact["record_semantics"]
    if not isinstance(semantics, dict) or set(semantics) != set(SEMANTIC_FIELDS):
        raise IedbSourceError("source fact has an incomplete trait-meaning projection")
    if record_semantics(semantics) != semantics:
        raise IedbSourceError("source fact trait meaning changed")
    reference = fact["protein_reference"]
    native = _native(fact["native_row"])
    record = {**semantics, "canonical_examples": [
        {"protein_id": reference.get("protein_id") if isinstance(reference, dict) else None}
    ]}
    return locate_existing_peptide(record, reference, (native,))


def build_snapshot(
    export: VerifiedExport, fetch_receipt_text: str,
    records: dict[str, dict], references: dict[str, dict],
) -> tuple[dict, dict]:
    """Capture successful source facts after complete native-export verification."""
    receipt = _receipt(fetch_receipt_text, export.pins)
    if receipt["fetched_at"] != export.fetched_at:
        raise IedbSourceError("verified export and acquisition receipt timestamps differ")
    facts, blocked = [], Counter()
    identities = set()
    for path, record in sorted(records.items()):
        semantics = record_semantics(record)
        trait_id = record["identifier"]
        if trait_id in identities:
            raise IedbSourceError("the same IEDB trait occurs in multiple selected records")
        identities.add(trait_id)
        native_rows = export.rows.get(trait_id, ())
        for example in record.get("canonical_examples") or []:
            protein_id = example.get("protein_id")
            reference = references.get(protein_id)
            if reference is None:
                blocked["missing acquired ProteinReference"] += 1
                continue
            try:
                # This check binds the actual existing record before constructing
                # the smaller immutable meaning projection used by future replay.
                locate_existing_peptide(record, reference, native_rows)
                if len(native_rows) != 1:
                    raise IedbSourceError("exactly one native source row is required")
                native = native_rows[0]
                fact = {
                    "record_path": path, "record_semantics": semantics,
                    "protein_reference": reference,
                    "native_row": {"data_record_index": native.data_record_index,
                                   "values": list(native.values)},
                    "source_pins": asdict(export.pins),
                }
                fact["fact_sha256"] = value_sha256(fact)
                validate_fact(fact, export.pins)
            except IedbSourceError as exc:
                blocked[str(exc)] += 1
                continue
            facts.append(fact)
    if not facts:
        raise IedbSourceError("no uniquely localized source facts were captured")
    snapshot = {
        "schema_version": 1, "source_url": SOURCE_URL, "license": LICENSE,
        "source_release": export.source_release, "source_pins": asdict(export.pins),
        "fetch_receipt_text": fetch_receipt_text,
        "source_records_scanned": export.data_records_scanned,
        "facts": sorted(facts, key=lambda fact: fact["fact_sha256"]),
    }
    snapshot["snapshot_id"] = "iedb-peptide-snapshot:" + value_sha256(snapshot)
    return snapshot, dict(blocked)


def snapshot_bytes(snapshot: dict) -> bytes:
    return (json.dumps(snapshot, sort_keys=True, ensure_ascii=True, indent=2) + "\n").encode()


@dataclass(frozen=True)
class VerifiedSnapshot:
    snapshot_id: str
    source_release: str
    facts: dict[str, dict]
    locations: dict[str, PeptideLocation]


def verify_snapshot(raw: bytes, expected_sha256: str, expected_pins: ExportPins) -> VerifiedSnapshot:
    """Verify a separately reviewed byte pin before accepting any embedded claims."""
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise IedbSourceError("snapshot differs from the independently reviewed byte checksum")
    snapshot = json.loads(raw)
    if not isinstance(snapshot, dict) or set(snapshot) != SNAPSHOT_FIELDS:
        raise IedbSourceError("invalid IEDB snapshot fields")
    if (type(snapshot["schema_version"]) is not int or snapshot["schema_version"] != 1
            or snapshot["source_url"] != SOURCE_URL or snapshot["license"] != LICENSE
            or snapshot["source_pins"] != asdict(expected_pins)
            or snapshot["source_release"] != f"epitope_full_v3; sha256:{expected_pins.csv_sha256}"):
        raise IedbSourceError("snapshot source, release, license or schema mismatch")
    _receipt(snapshot["fetch_receipt_text"], expected_pins)
    payload = {key: value for key, value in snapshot.items() if key != "snapshot_id"}
    if snapshot["snapshot_id"] != "iedb-peptide-snapshot:" + value_sha256(payload):
        raise IedbSourceError("snapshot content digest mismatch")
    scanned = snapshot["source_records_scanned"]
    if type(scanned) is not int or scanned < 1:
        raise IedbSourceError("snapshot lacks the complete native row count")
    if not isinstance(snapshot["facts"], list) or not snapshot["facts"]:
        raise IedbSourceError("snapshot contains no source facts")
    facts, locations, identities = {}, {}, set()
    for fact in snapshot["facts"]:
        location = validate_fact(fact, expected_pins)
        key = fact["fact_sha256"]
        identity = (location.trait_id, location.protein_id)
        if key in facts or identity in identities:
            raise IedbSourceError("duplicate source fact or trait/protein identity")
        if location.native_data_record_index > scanned:
            raise IedbSourceError("native row index exceeds the scanned export")
        facts[key], locations[key] = fact, location
        identities.add(identity)
    return VerifiedSnapshot(snapshot["snapshot_id"], snapshot["source_release"], facts, locations)
