"""Replay complete native InterPro location sets on existing protein examples.

This provider neither writes records nor qualifies occurrences. Source
registration pins captured bytes; definition, scope and license review still
belong to the central reviewed workflow.
"""

from __future__ import annotations

from collections import Counter
import copy
from functools import lru_cache
from pathlib import Path

from interpro_native_groups import digest, require
from interpro_native_snapshot import record_semantics, sha, verify_snapshot
from interpro_native_sources import SOURCES
from validate_uniprot_grounding import ROOT, build_grounding_evidence

SOURCE = "InterPro"
PROVIDER_KIND = "interpro_native"
SOURCE_DIRECTORY = "data/grounding/interpro_native/"
CANDIDATE_FIELDS = ("native_source", "native_location_set_sha256", "native_locations")


def is_native_source(value) -> bool:
    return isinstance(value, str) and value.startswith(SOURCE_DIRECTORY)


def source_path(source: str) -> Path:
    require(isinstance(source, str) and source in SOURCES,
            "native source is not independently registered")
    expected, _ = SOURCES[source]
    require(source == SOURCE_DIRECTORY + expected + ".json", "invalid registered native source path")
    path = ROOT / source
    require(path.resolve().is_relative_to(ROOT.resolve()), "native source escapes the repository")
    require(not any(part.is_symlink() for part in (path, *path.parents) if part != ROOT
                    and part.is_relative_to(ROOT)), "native source must not use symlinks")
    return path


def _state(path: Path) -> tuple[int, ...]:
    stat = path.stat()
    require(path.is_file(), "native source must be a regular file")
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def _location_fact(location_set, index: int) -> dict:
    result = {"location_set_sha256": location_set.set_sha256,
              "native_location_index": index,
              "native_location_sha256": location_set.locations[index]["native_location_sha256"]}
    result["fact_sha256"] = digest(result)
    return result


@lru_cache(maxsize=8)
def _load(path: Path, state: tuple, expected: str, pins: tuple):
    require(not path.is_symlink() and _state(path) == state, "native source changed before verification")
    verified = verify_snapshot(path.read_bytes(), expected, dict(pins))
    require(_state(path) == state, "native source changed during verification")
    identities = {(value.trait_id, value.protein_id): key for key, value in verified.sets.items()}
    facts = {}
    for key, location_set in verified.sets.items():
        for index in range(len(location_set.locations)):
            fact = _location_fact(location_set, index)
            require(fact["fact_sha256"] not in facts, "duplicate native location identity")
            facts[fact["fact_sha256"]] = fact, key, index
    return verified, identities, facts


def _snapshot(source: str):
    path = source_path(source)
    expected, pins = SOURCES[source]
    return _load(path, _state(path), expected, pins)


def assert_source_unchanged(source: str) -> None:
    """Rehash the complete immutable source immediately before installation."""
    path = source_path(source)
    before = _state(path)
    require(sha(path.read_bytes()) == SOURCES[source][0] and _state(path) == before,
            "native source changed before installation")


def _fact(source: str, key: str):
    require(isinstance(key, str), "native evidence requires an exact location digest")
    verified, _, facts = _snapshot(source)
    require(key in facts, "native location is absent from the registered source")
    fact, set_key, index = facts[key]
    return fact, verified.sets[set_key], index


def source_facts(source: str, keys=None) -> dict:
    """Return complete location-set facts without exposing cached mutable data."""
    verified, _, _ = _snapshot(source)
    selected = verified.facts if keys is None else {
        key: verified.facts[key] for key in keys if key in verified.facts}
    return copy.deepcopy(selected)


def find_fact(source: str, trait_id: str, protein_id: str, record_path: str) -> dict:
    verified, identities, _ = _snapshot(source)
    key = identities.get((trait_id, protein_id))
    require(key is not None, "no native source fact for this exact trait/protein")
    fact = verified.facts[key]
    require(record_path == fact["record_path"], "native source-fact record path changed")
    return copy.deepcopy(fact)


def _occurrence(location_set, index: int) -> dict:
    return {
        "trait_id": location_set.trait_id, "source_trait_id": location_set.trait_id,
        "protein_id": location_set.protein_id, "scope": "LOCALIZED",
        "mapping_method": "INTERPRO_MATCH", "coordinate_frame": (
            "UNIPROT_ISOFORM" if "-" in location_set.protein_id else "UNIPROT_CANONICAL"),
        "intervals": copy.deepcopy(location_set.locations[index]["intervals"]),
        "evidence_source": SOURCE, "source_release": location_set.source_release,
        "sequence_sha256": location_set.reference["sequence_sha256"],
    }


def _evidence(source: str, location_set, index: int) -> dict:
    return build_grounding_evidence(
        _occurrence(location_set, index), provider_kind="INTERPRO", provider_source=source,
        provider_release=location_set.source_release,
        provider_entry_sha256=_location_fact(location_set, index)["fact_sha256"],
    )


def contract_errors(evidence: dict) -> list[tuple[str, str]]:
    """Verify exact native occurrence evidence, including its complete-set identity."""
    try:
        source = evidence.get("provider_source")
        _, location_set, index = _fact(source, evidence.get("provider_entry_sha256"))
        require(evidence == _evidence(source, location_set, index),
                "native evidence differs from the complete source location")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("interpro_native_source_contract", str(exc))]
    return []


def _record_location(record: dict, reference: dict, source: str, location_set):
    verified, _, _ = _snapshot(source)
    require(record_semantics(record) == verified.records[location_set.record_path],
            "record meaning differs from the native source snapshot")
    require(reference == location_set.reference, "complete native ProteinReference changed")
    examples = record.get("canonical_examples")
    require(isinstance(examples, list) and all(isinstance(e, dict) for e in examples),
            "existing example list required")
    matches = [e for e in examples if e.get("protein_id") == location_set.protein_id]
    require(len(matches) == 1, "exact native protein must already occur once on the record")
    for key in ("sequence", "sequence_sha256", "sequence_length", "taxon_id", "reviewed"):
        if matches[0].get(key) is not None:
            require(matches[0][key] == reference[key], f"existing example {key} differs from native reference")


def record_errors(record: dict, reference: dict, evidence: dict) -> list[tuple[str, str]]:
    errors = contract_errors(evidence)
    if errors:
        return errors
    try:
        source = evidence["provider_source"]
        _, location_set, _ = _fact(source, evidence["provider_entry_sha256"])
        _record_location(record, reference, source, location_set)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("interpro_native_record_source_mismatch", str(exc))]
    return []


def resolve_occurrences(record: dict, reference: dict, record_path: str,
                        source: str) -> tuple[dict, list[dict], list[dict]]:
    """Replay all native locations; no caller can select a source-set subset."""
    fact = find_fact(source, record.get("identifier"), reference.get("protein_id"), record_path)
    verified, _, _ = _snapshot(source)
    location_set = verified.sets[fact["location_set_sha256"]]
    _record_location(record, reference, source, location_set)
    indices = range(len(location_set.locations))
    return (fact, [_occurrence(location_set, i) for i in indices],
            [_evidence(source, location_set, i) for i in indices])


def project_set(source: str, key: str) -> tuple[dict, list[dict], list[dict]]:
    """Replay one complete source set for independently checked ledger projections."""
    require(isinstance(key, str), "native location-set identity must be text")
    verified, _, _ = _snapshot(source)
    require(key in verified.sets, "native location set is absent from the registered source")
    location_set = verified.sets[key]
    return (copy.deepcopy(verified.facts[key]),
            [_occurrence(location_set, i) for i in range(len(location_set.locations))],
            [_evidence(source, location_set, i) for i in range(len(location_set.locations))])


def candidate_fields(evidence: dict) -> dict:
    """Reconstruct the entire candidate identity from any verified set member."""
    require(not contract_errors(evidence), "native evidence cannot reconstruct its candidate")
    source = evidence["provider_source"]
    _, location_set, _ = _fact(source, evidence["provider_entry_sha256"])
    return {"native_source": source, "native_location_set_sha256": location_set.set_sha256,
            "native_locations": [copy.deepcopy(loc["intervals"]) for loc in location_set.locations]}


def complete_set_errors(record: dict, reference: dict, occurrences: list[dict],
                        evidence_by_id: dict) -> list[tuple[str, str]]:
    """Reject omitted, duplicated, altered or mixed registered native locations.

    The central validator must independently resolve every evidence ID and check
    ordinary occurrences. This function adds the native set-completeness gate.
    """
    try:
        actual, expected, identities = {}, {}, {}
        for occurrence in occurrences:
            evidence = evidence_by_id.get(occurrence.get("source_evidence_id"))
            if not isinstance(evidence, dict):
                continue  # Missing evidence is rejected by the central validator.
            source = evidence.get("provider_source")
            if not isinstance(source, str) or not source.startswith(SOURCE_DIRECTORY):
                continue
            require(not contract_errors(evidence), "native occurrence evidence is invalid")
            _, location_set, index = _fact(source, evidence["provider_entry_sha256"])
            _record_location(record, reference, source, location_set)
            require(build_grounding_evidence(
                occurrence, provider_kind="INTERPRO", provider_source=source,
                provider_release=location_set.source_release,
                provider_entry_sha256=_location_fact(location_set, index)["fact_sha256"],
            ) == evidence, "native occurrence differs from its exact evidence")
            key = source, location_set.set_sha256
            identity = location_set.trait_id, location_set.protein_id
            require(identities.setdefault(identity, key) == key,
                    "conflicting native location sets for one trait/protein")
            actual.setdefault(key, []).append(evidence["evidence_id"])
            expected[key] = [_evidence(source, location_set, i)["evidence_id"]
                             for i in range(len(location_set.locations))]
        require(all(Counter(ids) == Counter(expected[key]) for key, ids in actual.items()),
                "native occurrence list does not preserve its complete location set")
        for identity, key in identities.items():
            observed = [o.get("source_evidence_id") for o in occurrences
                        if (o.get("trait_id"), o.get("protein_id")) == identity]
            require(Counter(observed) == Counter(expected[key]),
                    "another occurrence conflicts with the complete native location set")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return [("interpro_native_incomplete_location_set", str(exc))]
    return []
