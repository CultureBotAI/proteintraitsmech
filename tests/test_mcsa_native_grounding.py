"""Native catalytic-site source and record replay boundary regressions."""

import copy
import hashlib
import importlib
import os
import sys
from pathlib import Path

import pytest

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "pyproject.toml").is_file())
sys.path[:0] = [str(Path(__file__).parent), str(ROOT / "scripts")]
provider = importlib.import_module("mcsa_native_grounding")
capsule = importlib.import_module("mcsa_native_snapshot")
source = importlib.import_module("mcsa_native_source")
validator = importlib.import_module("validate_uniprot_grounding")
fixture = importlib.import_module("test_mcsa_native_snapshot")


@pytest.fixture
def installed_source(tmp_path, monkeypatch):
    snapshot, pins, native, record, references = fixture.captured(tmp_path)
    raw = capsule.snapshot_bytes(snapshot)
    monkeypatch.setattr(provider, "ROOT", tmp_path)
    monkeypatch.setattr(provider, "SOURCE_PINS", pins)
    monkeypatch.setattr(provider, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest())
    monkeypatch.setattr(provider, "SOURCE_RELEASE", native.source_release)
    path = provider.source_path()
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    provider._load.cache_clear()
    yield fixture.RECORD_PATH, record, references["UniProtKB:P12345"], snapshot
    provider._load.cache_clear()


def test_exact_native_site_uses_discontinuous_uniprot_positions(installed_source):
    path, record, reference, _ = installed_source
    before = copy.deepcopy((record, reference))
    fact, occurrence, evidence = provider.resolve_occurrence(record, reference, path)
    assert occurrence["residue_positions"] == [2, 4, 7]
    assert occurrence["expected_residues"] == "AHY"
    assert occurrence["mapping_method"] == "SOURCE_NATIVE_COORDINATES"
    assert occurrence["scope"] == "LOCALIZED"
    assert occurrence["trait_id"] == occurrence["source_trait_id"] == "MCSA:1"
    assert occurrence["protein_id"] == "UniProtKB:P12345"
    assert evidence["provider_kind"] == "SOURCE_DATABASE"
    assert evidence["provider_source"] == provider.SOURCE_PATH
    assert evidence["provider_entry_sha256"] == fact["fact_sha256"]
    assert not provider.contract_errors(evidence)
    assert not provider.record_errors(record, reference, evidence)
    assert not {"qualification_status", "intervals", "structure_id", "chain_id"} & occurrence.keys()
    assert (record, reference) == before
    provider.assert_source_unchanged()


@pytest.mark.parametrize("field,value", [
    ("trait_id", "MCSA:2"), ("source_trait_id", "MCSA:2"),
    ("trait_id", "M-CSA:1"), ("source_trait_id", "M-CSA:1"),
    ("protein_id", "UniProtKB:P12345-2"), ("mapping_method", "SIFTS_RESIDUE_MAPPING"),
    ("evidence_source", "MCSA"), ("provider_kind", "SIFTS"),
    ("source_release", "other-release"), ("provider_release", "other-release"),
    ("scope", "WHOLE_PROTEIN"), ("coordinate_frame", "UNIPROT_ISOFORM"),
    ("residue_positions", [2, 4]), ("residue_positions", [2, 4, 6, 7]),
    ("residue_positions", [4, 2, 7]), ("residue_positions", [102, 104, 107]),
    ("expected_residues", "AGY"), ("intervals", [{"start": 2, "end": 7}]),
    ("sequence_sha256", "c" * 64), ("provider_source", "/tmp/arbitrary-source.json"),
    ("provider_entry_sha256", "d" * 64), ("provider_entry_sha256", []),
    ("inheritance_path", ["MCSA:2", "MCSA:1"]), ("structure_id", "PDB:1abc"),
    ("chain_id", "A"), ("mapping_completeness", "COMPLETE"),
    ("source_residue_count", 3), ("mapped_residue_count", 3), ("unexpected", True),
])
def test_rehashing_cannot_change_native_identity_frame_or_complete_residue_set(
    installed_source, field, value
):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    evidence[field] = value
    evidence["evidence_id"] = validator.compute_evidence_id(evidence)
    assert provider.contract_errors(evidence)
    assert provider.record_errors(record, reference, evidence)


@pytest.mark.parametrize("field", [
    "identifier", "label", "definition", "definition_source", "trait_axis",
    "trait_category", "term_kind", "license", "mapping_status", "xrefs", "created_by",
])
def test_every_non_example_record_field_is_bound(installed_source, field):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    changed = copy.deepcopy(record)
    changed[field] = "changed"
    assert provider.record_errors(changed, reference, evidence)


def test_adding_unreviewed_record_metadata_requires_new_fact_review(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    record["new_metadata"] = "not reviewed"
    assert provider.record_errors(record, reference, evidence)


@pytest.mark.parametrize("field", [
    "protein_id", "protein_label", "taxon_id", "taxon_label", "sequence", "sequence_length",
    "sequence_sha256", "uniprot_release", "sequence_version", "reviewed",
])
def test_full_acquired_reference_is_bound(installed_source, field):
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
    record["canonical_examples"] = examples
    assert provider.record_errors(record, reference, evidence)


def test_resolution_requires_the_exact_record_path(installed_source):
    path, record, reference, _ = installed_source
    with pytest.raises(source.McsaSourceError, match="record path changed"):
        provider.resolve_occurrence(record, reference, path.replace("fixture", "other"))


def test_source_byte_change_invalidates_warm_cache_despite_restored_mtime(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    native_path = provider.source_path()
    before = native_path.stat()
    raw = native_path.read_bytes()
    changed = raw.replace(b"Fixture enzyme", b"Forged! enzyme")
    assert len(changed) == len(raw) and changed != raw
    native_path.write_bytes(changed)
    os.utime(native_path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert provider.contract_errors(evidence)
    with pytest.raises(source.McsaSourceError):
        provider.assert_source_unchanged()


def test_replaced_or_removed_source_invalidates_warm_cache(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    native_path = provider.source_path()
    replacement = native_path.with_suffix(".replacement")
    replacement.write_text("{}")
    replacement.replace(native_path)
    assert provider.contract_errors(evidence)
    native_path.unlink()
    assert provider.contract_errors(evidence)


def test_symlink_cannot_replace_the_fixed_source(installed_source):
    path, record, reference, _ = installed_source
    _, _, evidence = provider.resolve_occurrence(record, reference, path)
    native_path = provider.source_path()
    target = native_path.with_suffix(".target")
    native_path.rename(target)
    native_path.symlink_to(target)
    assert provider.contract_errors(evidence)
    with pytest.raises(source.McsaSourceError, match="regular fixed-path"):
        provider.assert_source_unchanged()


def test_returned_source_facts_cannot_poison_trusted_cached_objects(installed_source):
    path, record, reference, _ = installed_source
    fact, _, evidence = provider.resolve_occurrence(record, reference, path)
    key = fact["fact_sha256"]
    fact["protein_reference"]["sequence"] = "FORGED"
    provider.source_facts()[key]["record_semantics"]["definition"] = "FORGED"
    provider.source_facts([key])[key]["native_entry_id"] = 999
    assert provider.source_facts(["f" * 64]) == {}
    assert not provider.record_errors(record, reference, evidence)
    assert provider._load.cache_info().misses == 1


def test_qualification_metadata_keeps_the_existing_meaning_binding(installed_source):
    path, record, reference, _ = installed_source
    _, occurrence, evidence = provider.resolve_occurrence(record, reference, path)
    record["canonical_examples"][0].update({
        "qualification_status": "QUALIFIED", "trait_occurrences": [occurrence],
    })
    assert not provider.record_errors(record, reference, evidence)
