"""Source and record replay tests for the staged IEDB grounding provider."""

import copy
import hashlib
import importlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
provider = importlib.import_module("iedb_peptide_grounding")
capsule = importlib.import_module("iedb_peptide_snapshot")
source = importlib.import_module("iedb_peptide_source")
validator = importlib.import_module("validate_uniprot_grounding")
native_inputs = importlib.import_module("test_iedb_peptide_snapshot").native_inputs


@pytest.fixture
def installed_source(native_inputs, tmp_path, monkeypatch):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    raw = capsule.snapshot_bytes(snapshot)
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "SOURCE_PINS", native_inputs[0].pins)
    monkeypatch.setattr(provider, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest())
    monkeypatch.setattr(provider, "SOURCE_RELEASE", native_inputs[0].source_release)
    path = provider.source_path()
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    provider._load.cache_clear()
    record_path, record = next(iter(native_inputs[2].items()))
    reference = next(iter(native_inputs[3].values()))
    yield record_path, record, reference, snapshot
    provider._load.cache_clear()


def test_recomputed_occurrence_locates_this_peptide_on_the_existing_parent(installed_source):
    path, record, reference, _ = installed_source
    before = copy.deepcopy((record, reference))
    fact, occurrence, evidence = provider.resolve_occurrence(record, reference, path)
    assert occurrence["intervals"] == [{"start": 2, "end": 6}]
    assert occurrence["mapping_method"] == "PATTERN_MATCH"
    assert occurrence["scope"] == "LOCALIZED"
    assert occurrence["source_trait_id"] == record["identifier"]
    assert occurrence["protein_id"] == reference["protein_id"]
    assert evidence["provider_entry_sha256"] == fact["fact_sha256"]
    assert evidence["provider_source"] == provider.SOURCE_PATH
    assert evidence["provider_kind"] == "SOURCE_DATABASE"
    assert not provider.contract_errors(evidence)
    assert not provider.record_errors(record, reference, evidence)
    assert "qualification_status" not in occurrence
    assert (record, reference) == before
    provider.assert_source_unchanged()


@pytest.mark.parametrize(("field", "value"), [
    ("trait_id", "IEDB:11"), ("source_trait_id", "IEDB:11"),
    ("protein_id", "UniProtKB:P12345-2"), ("mapping_method", "SOURCE_NATIVE_COORDINATES"),
    ("evidence_source", "InterPro"), ("provider_kind", "INTERPRO"),
    ("source_release", "other-release"), ("provider_release", "other-release"),
    ("scope", "WHOLE_PROTEIN"), ("coordinate_frame", "UNIPROT_ISOFORM"),
    ("intervals", [{"start": 200, "end": 204}]),
    ("sequence_sha256", "c" * 64), ("provider_source", "/tmp/arbitrary-source.json"),
    ("provider_entry_sha256", "d" * 64), ("provider_entry_sha256", []),
    ("inheritance_path", ["IEDB:11", "IEDB:10"]), ("residue_positions", [2]),
    ("expected_residues", "ACDEF"), ("structure_id", "PDB:1abc"), ("chain_id", "A"),
    ("mapping_completeness", 1.0), ("source_residue_count", 5), ("mapped_residue_count", 5),
    ("unexpected", True),
])
def test_consistently_rehashed_evidence_cannot_change_any_native_claim(
    installed_source, field, value
):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    evidence[field] = value
    evidence["evidence_id"] = validator.compute_evidence_id(evidence)
    assert provider.contract_errors(evidence)
    assert provider.record_errors(record, reference, evidence)


@pytest.mark.parametrize("field", capsule.SEMANTIC_FIELDS)
def test_changed_record_meaning_rejects_existing_evidence(installed_source, field):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    changed = copy.deepcopy(record)
    changed[field] += " changed"
    assert provider.record_errors(changed, reference, evidence)


@pytest.mark.parametrize("field", [
    "protein_id", "protein_label", "taxon_id", "taxon_label", "sequence", "sequence_length",
    "sequence_sha256", "uniprot_release", "reviewed",
])
def test_entire_acquired_reference_is_bound(installed_source, field):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    changed = copy.deepcopy(reference)
    changed[field] = "changed"
    assert provider.record_errors(record, changed, evidence)


@pytest.mark.parametrize("examples", [[], [{"protein_id": "UniProtKB:Q12345"}], [
    {"protein_id": "UniProtKB:P12345"}, {"protein_id": "UniProtKB:P12345"},
]])
def test_removed_or_duplicated_existing_example_is_rejected(installed_source, examples):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    changed = copy.deepcopy(record)
    changed["canonical_examples"] = examples
    assert provider.record_errors(changed, reference, evidence)


def test_resolution_checks_the_exact_record_path(installed_source):
    path, record, reference, _ = installed_source
    with pytest.raises(source.IedbSourceError, match="record path changed"):
        provider.resolve_occurrence(record, reference, path.replace("fixture", "other"))


def test_snapshot_change_invalidates_cached_facts_even_if_mtime_is_restored(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    native_path = provider.source_path()
    before = native_path.stat()
    raw = native_path.read_bytes()
    changed = raw.replace(b"Fixture antigen", b"Forged! antigen")
    assert len(raw) == len(changed) and raw != changed
    native_path.write_bytes(changed)
    os.utime(native_path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert provider.contract_errors(evidence)
    with pytest.raises(source.IedbSourceError):
        provider.assert_source_unchanged()


def test_replacing_or_removing_the_source_invalidates_cached_facts(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    native_path = provider.source_path()
    alternative = native_path.with_suffix(".other")
    alternative.write_text("{}")
    alternative.replace(native_path)
    assert provider.contract_errors(evidence)
    native_path.unlink()
    assert provider.contract_errors(evidence)


def test_public_fact_reads_cannot_poison_the_cached_source(installed_source):
    path, record, reference, _ = installed_source
    fact, _, evidence = provider.resolve_occurrence(record, reference, path)
    fact["protein_reference"]["sequence"] = "FORGED"
    all_facts = provider.source_facts()
    next(iter(all_facts.values()))["record_semantics"]["definition"] = "FORGED"
    assert not provider.record_errors(record, reference, evidence)
    assert provider._load.cache_info().misses == 1


def test_adding_occurrence_metadata_preserves_the_meaning_binding(installed_source):
    path, record, reference, _ = installed_source
    _, occurrence, evidence = provider.resolve_occurrence(record, reference, path)
    record["canonical_examples"][0].update({
        "qualification_status": "QUALIFIED", "trait_occurrences": [occurrence],
    })
    assert not provider.record_errors(record, reference, evidence)
