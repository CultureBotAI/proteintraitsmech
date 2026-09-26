"""Replay independently pinned IEDB peptide facts on existing protein examples.

This source-specific provider does not write records or grant qualification.
The central resolver, semantic validator and reviewed promoter own those steps.
Only peptide identity/location is established, not immune activity in the parent.
"""

from __future__ import annotations

import copy
import hashlib
from functools import lru_cache
from pathlib import Path

from iedb_peptide_snapshot import record_semantics, verify_snapshot
from iedb_peptide_source import ExportPins, IedbSourceError, NativeRow, locate_existing_peptide
from validate_uniprot_grounding import ROOT, build_grounding_evidence

SOURCE = "IEDB"
PROVIDER_KIND = "iedb_peptide"
SOURCE_PATH = "data/grounding/iedb_peptide_source_snapshot.json"
# These reviewed byte pins are trusted code, never candidate/CLI/evidence input.
SOURCE_SHA256 = "fbd5f570a95705e2a44c7e547b6db1bd571dfa19383b4fd9a4d0d5d62e587470"
SOURCE_PINS = ExportPins(
    "af0882317565ff55897f4f0b6b00b3bd94a5f4f06620a6c5acda3a44838e00ba",
    "a1f25aff30c5b948d0d8374976c81a5c8813c6d7e6cb98f04457cd37bc1bca32",
    "f4e97aca28f2421406eae4d2cce3fe8b664c4c809ebed9517ad26405bdb721d1",
)
SOURCE_RELEASE = f"epitope_full_v3; sha256:{SOURCE_PINS.csv_sha256}"


def source_path() -> Path:
    return ROOT / SOURCE_PATH


def _state(path: Path) -> tuple[int, ...]:
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


@lru_cache(maxsize=2)
def _load(path: Path, state: tuple, sha256: str, pins: ExportPins):
    if path.is_symlink() or _state(path) != state:
        raise IedbSourceError("IEDB source snapshot changed before verification")
    raw = path.read_bytes()
    verified = verify_snapshot(raw, sha256, pins)
    if _state(path) != state:
        raise IedbSourceError("IEDB source snapshot changed during verification")
    by_identity = {(loc.trait_id, loc.protein_id): key
                   for key, loc in verified.locations.items()}
    return verified, by_identity


def _snapshot():
    path = source_path()
    if path.is_symlink():
        raise IedbSourceError("IEDB source snapshot must be a regular fixed-path file")
    return _load(path, _state(path), SOURCE_SHA256, SOURCE_PINS)


def assert_source_unchanged() -> None:
    """Rehash the complete input immediately before the central writer runs."""
    path = source_path()
    before = _state(path)
    if path.is_symlink():
        raise IedbSourceError("IEDB source snapshot must be a regular fixed-path file")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if digest != SOURCE_SHA256 or _state(path) != before:
        raise IedbSourceError("IEDB source snapshot changed before installation")


def _fact(fact_sha256: str):
    if not isinstance(fact_sha256, str):
        raise IedbSourceError("IEDB evidence requires an exact source-fact digest")
    verified, _ = _snapshot()
    if fact_sha256 not in verified.facts:
        raise IedbSourceError("IEDB source fact is absent from the reviewed snapshot")
    return verified.facts[fact_sha256], verified.locations[fact_sha256]


def source_facts(keys=None) -> dict:
    """Return defensive copies; callers cannot modify cached trusted facts."""
    verified, _ = _snapshot()
    selected = verified.facts if keys is None else {
        key: verified.facts[key] for key in keys if key in verified.facts
    }
    return copy.deepcopy(selected)


def find_fact(trait_id: str, protein_id: str, record_path: str) -> dict:
    verified, by_identity = _snapshot()
    key = by_identity.get((trait_id, protein_id))
    if key is None:
        raise IedbSourceError("no reviewed IEDB source fact for this exact trait/protein")
    fact = verified.facts[key]
    if record_path != fact["record_path"]:
        raise IedbSourceError("IEDB source-fact record path changed")
    return copy.deepcopy(fact)


def _occurrence(location) -> dict:
    return {
        "trait_id": location.trait_id, "source_trait_id": location.trait_id,
        "protein_id": location.protein_id, "scope": "LOCALIZED",
        "mapping_method": "PATTERN_MATCH", "coordinate_frame": location.coordinate_frame,
        "intervals": [{"start": location.start, "end": location.end}],
        "evidence_source": SOURCE, "source_release": SOURCE_RELEASE,
        "sequence_sha256": location.sequence_sha256,
    }


def _evidence(fact: dict, location) -> dict:
    return build_grounding_evidence(
        _occurrence(location), provider_kind="SOURCE_DATABASE", provider_source=SOURCE_PATH,
        provider_release=SOURCE_RELEASE, provider_entry_sha256=fact["fact_sha256"],
    )


def contract_errors(evidence: dict) -> list[tuple[str, str]]:
    """Require exactly the evidence projection of a trusted native source fact."""
    try:
        fact, location = _fact(evidence.get("provider_entry_sha256"))
        expected = _evidence(fact, location)
        if evidence != expected:
            changed = sorted(key for key in set(evidence) | set(expected)
                             if key not in evidence or key not in expected
                             or evidence[key] != expected[key])
            raise IedbSourceError("IEDB evidence differs from its native fact: " + ", ".join(changed))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("iedb_source_contract", str(exc))]
    return []


def _record_location(record: dict, reference: dict, fact: dict, expected):
    if record_semantics(record) != fact["record_semantics"]:
        raise IedbSourceError("IEDB record meaning differs from the reviewed source fact")
    if reference != fact["protein_reference"]:
        raise IedbSourceError("IEDB complete ProteinReference changed")
    row = fact["native_row"]
    location = locate_existing_peptide(
        record, reference, (NativeRow(row["data_record_index"], tuple(row["values"])),),
    )
    if location != expected:
        raise IedbSourceError("IEDB peptide location no longer reproduces the native fact")
    return location


def record_errors(record: dict, reference: dict, evidence: dict) -> list[tuple[str, str]]:
    errors = contract_errors(evidence)
    if errors:
        return errors
    try:
        fact, expected = _fact(evidence["provider_entry_sha256"])
        _record_location(record, reference, fact, expected)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("iedb_record_source_mismatch", str(exc))]
    return []


def resolve_occurrence(record: dict, reference: dict, record_path: str) -> tuple[dict, dict, dict]:
    """Recompute from the existing record/reference; accept no candidate coordinates."""
    fact = find_fact(record.get("identifier"), reference.get("protein_id"), record_path)
    _, expected = _fact(fact["fact_sha256"])
    location = _record_location(record, reference, fact, expected)
    return fact, _occurrence(location), _evidence(fact, location)
