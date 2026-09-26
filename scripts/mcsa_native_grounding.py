"""Replay fixed M-CSA native UniProt residue assertions on existing examples.

This provider neither writes records nor qualifies occurrences. Its complete
source byte pin is independent of candidate input, evidence and snapshot metadata.
"""

from __future__ import annotations

import copy
import hashlib
from functools import lru_cache
from pathlib import Path

from mcsa_native_snapshot import record_semantics, verify_snapshot
from mcsa_native_source import McsaSourceError, SourcePins, locate_existing_site
from validate_uniprot_grounding import ROOT, build_grounding_evidence

SOURCE = "M-CSA"
PROVIDER_KIND = "mcsa_native"
SOURCE_PATH = "data/grounding/mcsa_native_source_snapshot.json"
# Reviewed complete source bytes; never accepted from a candidate or CLI option.
SOURCE_SHA256 = "2b70efba815454fb5a4315e6e0c1773a7b12f37258571b86315a39b9dab7153e"
SOURCE_PINS = SourcePins(
    "22257d2e7525cbc01e330fe5354917d6118ff9f03937c9fe78e03a44c884b7b7",
    "d80963b916c2ed4508d25fb823b809f0bc0ce7a36e51ebdfe1beb836b3950e2a",
)
SOURCE_RELEASE = f"M-CSA entries API; sha256:{SOURCE_PINS.normalized_sha256}"


def source_path() -> Path:
    return ROOT / SOURCE_PATH


def _state(path: Path) -> tuple[int, ...]:
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


@lru_cache(maxsize=2)
def _load(path: Path, state: tuple, sha256: str, pins: SourcePins):
    if path.is_symlink() or _state(path) != state:
        raise McsaSourceError("M-CSA source snapshot changed before verification")
    verified = verify_snapshot(path.read_bytes(), sha256, pins)
    if _state(path) != state:
        raise McsaSourceError("M-CSA source snapshot changed during verification")
    by_identity = {(loc.trait_id, loc.protein_id): key
                   for key, loc in verified.locations.items()}
    return verified, by_identity


def _snapshot():
    path = source_path()
    if path.is_symlink():
        raise McsaSourceError("M-CSA source snapshot must be a regular fixed-path file")
    return _load(path, _state(path), SOURCE_SHA256, SOURCE_PINS)


def assert_source_unchanged() -> None:
    """Rehash the full source input before a central writer can install claims."""
    path = source_path()
    before = _state(path)
    if path.is_symlink():
        raise McsaSourceError("M-CSA source snapshot must be a regular fixed-path file")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    if digest != SOURCE_SHA256 or _state(path) != before:
        raise McsaSourceError("M-CSA source snapshot changed before installation")


def _fact(fact_sha256: str):
    if not isinstance(fact_sha256, str):
        raise McsaSourceError("M-CSA evidence requires an exact source-fact digest")
    verified, _ = _snapshot()
    if fact_sha256 not in verified.facts:
        raise McsaSourceError("M-CSA source fact is absent from the reviewed snapshot")
    return verified.facts[fact_sha256], verified.locations[fact_sha256]


def source_facts(keys=None) -> dict:
    """Return defensive copies of reviewed facts, optionally restricted by digest."""
    verified, _ = _snapshot()
    selected = verified.facts if keys is None else {
        key: verified.facts[key] for key in keys if key in verified.facts
    }
    return copy.deepcopy(selected)


def find_fact(trait_id: str, protein_id: str, record_path: str) -> dict:
    verified, by_identity = _snapshot()
    key = by_identity.get((trait_id, protein_id))
    if key is None:
        raise McsaSourceError("no reviewed M-CSA source fact for this exact trait/protein")
    fact = verified.facts[key]
    if record_path != fact["record_path"]:
        raise McsaSourceError("M-CSA source-fact record path changed")
    return copy.deepcopy(fact)


def _occurrence(location) -> dict:
    amino_acids = {row.position: row.amino_acid for row in location.native_residues}
    return {
        "trait_id": location.trait_id, "source_trait_id": location.trait_id,
        "protein_id": location.protein_id, "scope": "LOCALIZED",
        "mapping_method": "SOURCE_NATIVE_COORDINATES", "coordinate_frame": location.coordinate_frame,
        "residue_positions": list(location.residue_positions),
        "expected_residues": "".join(amino_acids[position] for position in location.residue_positions),
        "evidence_source": SOURCE, "source_release": SOURCE_RELEASE,
        "sequence_sha256": location.sequence_sha256,
    }


def _evidence(fact: dict, location) -> dict:
    return build_grounding_evidence(
        _occurrence(location), provider_kind="SOURCE_DATABASE", provider_source=SOURCE_PATH,
        provider_release=SOURCE_RELEASE, provider_entry_sha256=fact["fact_sha256"],
    )


def contract_errors(evidence: dict) -> list[tuple[str, str]]:
    """Require the complete, exact evidence projection of a trusted native fact."""
    try:
        fact, location = _fact(evidence.get("provider_entry_sha256"))
        expected = _evidence(fact, location)
        if evidence != expected:
            changed = sorted(key for key in set(evidence) | set(expected)
                             if key not in evidence or key not in expected
                             or evidence[key] != expected[key])
            raise McsaSourceError("M-CSA evidence differs from its native fact: " + ", ".join(changed))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("mcsa_native_source_contract", str(exc))]
    return []


def _record_location(record: dict, reference: dict, fact: dict, expected):
    if record_semantics(record) != fact["record_semantics"]:
        raise McsaSourceError("M-CSA record meaning differs from the reviewed source fact")
    if reference != fact["protein_reference"]:
        raise McsaSourceError("M-CSA complete ProteinReference changed")
    verified, _ = _snapshot()
    native = verified.native_entries[fact["native_entry_id"]]
    location = locate_existing_site(record, reference, native)
    if location != expected:
        raise McsaSourceError("M-CSA catalytic site no longer reproduces the native fact")
    return location


def record_errors(record: dict, reference: dict, evidence: dict) -> list[tuple[str, str]]:
    errors = contract_errors(evidence)
    if errors:
        return errors
    try:
        fact, expected = _fact(evidence["provider_entry_sha256"])
        _record_location(record, reference, fact, expected)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("mcsa_native_record_source_mismatch", str(exc))]
    return []


def resolve_occurrence(record: dict, reference: dict, record_path: str) -> tuple[dict, dict, dict]:
    """Replay source residues on the current exact record and full reference."""
    fact = find_fact(record.get("identifier"), reference.get("protein_id"), record_path)
    _, expected = _fact(fact["fact_sha256"])
    location = _record_location(record, reference, fact, expected)
    return fact, _occurrence(location), _evidence(fact, location)
