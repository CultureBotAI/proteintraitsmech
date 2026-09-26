"""Boundary tests for complete native source sets, without production writes."""

import copy
import importlib
import os
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(Path(__file__).parent), str(ROOT / "scripts"), str(ROOT / "tests")]
provider = importlib.import_module("interpro_native_grounding")
source = importlib.import_module("interpro_native_snapshot")
validator = importlib.import_module("validate_uniprot_grounding")
from interpro_native_groups import NativeCaptureError  # noqa: E402
from test_interpro_native_snapshot import inputs as inputs  # noqa: E402


@pytest.fixture
def installed(inputs, tmp_path, monkeypatch):
    snapshot = source.build_snapshot(*inputs)
    raw = source.snapshot_bytes(snapshot)
    pin = source.sha(raw)
    name = provider.SOURCE_DIRECTORY + pin + ".json"
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "SOURCES", {name: (pin, tuple(sorted(inputs[1].items())))})
    path = provider.source_path(name)
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    provider._load.cache_clear()
    yield name, inputs[2], inputs[3]
    provider._load.cache_clear()


def resolve(installed, trait="InterPro:IPR000055"):
    name, records, _ = installed
    path, record = next((p, r) for p, r in records.items() if r["identifier"] == trait)
    reference = copy.deepcopy(record["canonical_examples"][0])
    fact, occurrences, evidence = provider.resolve_occurrences(record, reference, path, name)
    return name, path, record, reference, fact, occurrences, evidence


def qualified(occurrences, evidence):
    return [{**copy.deepcopy(o), "source_evidence_id": e["evidence_id"],
             "qualification_status": "QUALIFIED"} for o, e in zip(occurrences, evidence, strict=True)]


def test_independent_native_matches_remain_two_separate_occurrences(installed):
    name, _, record, reference, fact, occurrences, evidence = resolve(installed)
    assert [o["intervals"] for o in occurrences] == [[{"start": 7, "end": 190}],
                                                   [{"start": 348, "end": 403}]]
    assert len({e["evidence_id"] for e in evidence}) == 2
    assert all("qualification_status" not in o for o in occurrences)
    assert all(e["provider_kind"] == "INTERPRO" and e["provider_source"] == name for e in evidence)
    assert all(e["provider_entry_sha256"] != fact["location_set_sha256"] for e in evidence)
    assert all(not provider.record_errors(record, reference, e) for e in evidence)
    claims = qualified(occurrences, evidence)
    assert not provider.complete_set_errors(record, reference, claims,
                                            {e["evidence_id"]: e for e in evidence})
    provider.assert_source_unchanged(name)


def test_discontinuous_location_remains_one_occurrence_with_two_fragments(installed):
    _, _, record, reference, _, occurrences, evidence = resolve(installed, "SUPERFAMILY:SSF56519")
    assert len(occurrences) == len(evidence) == 1
    assert occurrences[0]["intervals"] == [{"start": 59, "end": 121}, {"start": 212, "end": 341}]
    assert not provider.record_errors(record, reference, evidence[0])


@pytest.mark.parametrize("mutation", ["omit", "duplicate", "flatten", "change", "extra_legacy"])
def test_complete_set_gate_rejects_lost_or_conflicting_locations(installed, mutation):
    _, _, record, reference, _, occurrences, evidence = resolve(installed)
    claims = qualified(occurrences, evidence)
    evidence_by_id = {e["evidence_id"]: e for e in evidence}
    if mutation == "omit":
        claims.pop()
    elif mutation == "duplicate":
        claims.append(copy.deepcopy(claims[0]))
    elif mutation == "flatten":
        claims[0]["intervals"] += claims.pop()["intervals"]
    elif mutation == "change":
        claims[0]["intervals"][0]["start"] += 1
    elif mutation == "extra_legacy":
        claims.append({**copy.deepcopy(claims[0]), "source_evidence_id": "ug-evidence:" + "f" * 64})
    assert provider.complete_set_errors(record, reference, claims, evidence_by_id)


@pytest.mark.parametrize("field,value", [
    ("trait_id", "InterPro:IPR000056"), ("source_trait_id", "Pfam:PF01420"),
    ("protein_id", "UniProtKB:P05719-2"), ("mapping_method", "SIFTS_RESIDUE_MAPPING"),
    ("evidence_source", "Pfam"), ("provider_kind", "SOURCE_DATABASE"),
    ("source_release", "109.0"), ("provider_release", "109.0"),
    ("scope", "WHOLE_PROTEIN"), ("coordinate_frame", "UNIPROT_ISOFORM"),
    ("intervals", [{"start": 7, "end": 403}]),
    ("intervals", [{"start": 7, "end": 190}, {"start": 348, "end": 403}]),
    ("sequence_sha256", "c" * 64), ("provider_source", "/tmp/forged.json"),
    ("provider_entry_sha256", "d" * 64), ("provider_entry_sha256", []),
    ("residue_positions", [7, 190]), ("unexpected", True),
])
def test_rehashed_evidence_cannot_change_source_location(installed, field, value):
    _, _, record, reference, _, _, evidence = resolve(installed)
    changed = copy.deepcopy(evidence[0])
    changed[field] = value
    changed["evidence_id"] = validator.compute_evidence_id(changed)
    assert provider.contract_errors(changed)
    assert provider.record_errors(record, reference, changed)


@pytest.mark.parametrize("field", ["identifier", "definition", "label", "definition_source",
                                    "trait_axis", "trait_category", "license", "new_metadata"])
def test_all_record_meaning_is_bound(installed, field):
    _, _, record, reference, _, _, evidence = resolve(installed)
    record[field] = "changed"
    assert provider.record_errors(record, reference, evidence[0])


@pytest.mark.parametrize("field", ["sequence", "taxon_id", "uniprot_release", "protein_id",
                                    "protein_label", "sequence_version"])
def test_complete_reference_is_bound(installed, field):
    _, _, record, reference, _, _, evidence = resolve(installed)
    reference[field] = "changed"
    assert provider.record_errors(record, reference, evidence[0])


@pytest.mark.parametrize("mutation", ["remove", "duplicate", "sequence", "path"])
def test_existing_exact_example_and_record_path_are_required(installed, mutation):
    name, path, record, reference, _, _, _ = resolve(installed)
    if mutation == "remove":
        record["canonical_examples"] = []
    elif mutation == "duplicate":
        record["canonical_examples"] *= 2
    elif mutation == "sequence":
        record["canonical_examples"][0]["sequence"] = "WRONG"
    elif mutation == "path":
        path = path.replace("repeated", "other")
    with pytest.raises(NativeCaptureError):
        provider.resolve_occurrences(record, reference, path, name)


@pytest.mark.parametrize("mutation", ["rewrite", "replace", "remove", "symlink"])
def test_changed_source_invalidates_warm_cache(installed, mutation):
    name, _, record, reference, _, _, evidence = resolve(installed)
    path = provider.source_path(name)
    before = path.stat()
    if mutation == "rewrite":
        raw = path.read_bytes()
        altered = raw.replace(b"Synthetic native trait", b"Rewritten native trait")
        assert altered != raw and len(altered) == len(raw)
        path.write_bytes(altered)
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    elif mutation == "replace":
        replacement = path.with_suffix(".replacement")
        replacement.write_text("{}")
        replacement.replace(path)
    elif mutation == "remove":
        path.unlink()
    elif mutation == "symlink":
        target = path.with_suffix(".target")
        path.rename(target)
        path.symlink_to(target)
    assert provider.record_errors(record, reference, evidence[0])
    with pytest.raises((NativeCaptureError, OSError)):
        provider.assert_source_unchanged(name)


def test_returned_values_cannot_modify_cached_source(installed):
    name, path, record, reference, fact, occurrences, evidence = resolve(installed)
    original = copy.deepcopy((occurrences, evidence))
    occurrences[0]["intervals"][0]["start"] = 100
    fact["trait_id"] = "forged"
    facts = provider.source_facts(name)
    facts[next(iter(facts))]["capture_id"] = "forged"
    assert provider.resolve_occurrences(record, reference, path, name)[1:] == original
    assert provider.source_facts(name, ["f" * 64]) == {}
    assert provider._load.cache_info().misses == 1
