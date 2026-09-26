"""Snapshot membership, complete native-source, and independently trusted pin tests."""

import copy
import hashlib
import importlib
import sys
from pathlib import Path

import pytest

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "pyproject.toml").is_file())
sys.path[:0] = [str(Path(__file__).parent), str(ROOT / "scripts")]
fixture = importlib.import_module("test_mcsa_native_source")
source = importlib.import_module("mcsa_native_source")
capsule = importlib.import_module("mcsa_native_snapshot")
RECORD_PATH = "data/traits/structure/active_site/mcsa/fixture.yaml"


def captured(tmp_path):
    path, pins = fixture.capture(tmp_path)
    native = source.read_verified_source(tmp_path, path, pins)
    record = fixture.record()
    record.update(mapping_status="REVIEWED", xrefs=["EC:1.2.3.4"], created_by="Fixture curator")
    references = {"UniProtKB:P12345": fixture.reference()}
    snapshot, blocked = capsule.build_snapshot(native, path.read_text(), {RECORD_PATH: record}, references)
    assert not blocked
    return snapshot, pins, native, record, references


def verified(snapshot, pins):
    raw = capsule.snapshot_bytes(snapshot)
    return capsule.verify_snapshot(raw, hashlib.sha256(raw).hexdigest(), pins)


def rehash(snapshot):
    for fact in snapshot["facts"]:
        fact["fact_sha256"] = source.value_sha256({k: v for k, v in fact.items() if k != "fact_sha256"})
    snapshot["snapshot_id"] = "mcsa-native-snapshot:" + source.value_sha256(
        {k: v for k, v in snapshot.items() if k != "snapshot_id"})


def test_snapshot_retains_all_native_entries_and_complete_record_reference_bindings(tmp_path):
    snapshot, pins, _, record, references = captured(tmp_path)
    before = copy.deepcopy(snapshot)
    result = verified(snapshot, pins)
    assert len(snapshot["native_entries"]) == 2 and len(result.facts) == 1
    fact = next(iter(result.facts.values()))
    assert fact["record_semantics"] == {k: v for k, v in record.items() if k != "canonical_examples"}
    assert fact["protein_reference"] == references["UniProtKB:P12345"]
    assert next(iter(result.locations.values())).residue_positions == (2, 4, 7)
    assert snapshot == before


def test_capture_does_not_share_mutable_inputs(tmp_path):
    snapshot, pins, native, record, references = captured(tmp_path)
    before = capsule.snapshot_bytes(snapshot)
    record["xrefs"].append("EC:9.9.9.9")
    references["UniProtKB:P12345"]["protein_label"] = "Changed"
    native.entries[1]["description"] = "Changed source"
    assert capsule.snapshot_bytes(snapshot) == before
    verified(snapshot, pins)


def test_forged_rehashed_snapshot_cannot_supply_its_own_trusted_byte_pin(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    expected = hashlib.sha256(capsule.snapshot_bytes(snapshot)).hexdigest()
    snapshot["facts"][0]["record_semantics"]["created_by"] = "Arbitrary replacement"
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="independently reviewed byte checksum"):
        capsule.verify_snapshot(capsule.snapshot_bytes(snapshot), expected, pins)


@pytest.mark.parametrize("target", ["selected_entry", "unselected_entry", "omit_entry", "duplicate_entry", "reorder"])
def test_complete_native_source_pin_protects_entries_outside_selected_facts(tmp_path, target):
    snapshot, pins, _, _, _ = captured(tmp_path)
    if target == "selected_entry":
        snapshot["native_entries"][0]["description"] = "Modified selected source"
    elif target == "unselected_entry":
        snapshot["native_entries"][1]["description"] = "Modified unselected source"
    elif target == "omit_entry":
        snapshot["native_entries"].pop()
    elif target == "duplicate_entry":
        snapshot["native_entries"].append(copy.deepcopy(snapshot["native_entries"][0]))
    else:
        snapshot["native_entries"].reverse()
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError):
        verified(snapshot, pins)


@pytest.mark.parametrize("field,value", [
    ("schema_version", True), ("source_url", "https://example.org/source"),
    ("license", "CC0"), ("attribution", "wrong source"), ("source_release", "unknown"),
])
def test_snapshot_requires_the_exact_source_and_license(tmp_path, field, value):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot[field] = value
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="source, release, license or schema"):
        verified(snapshot, pins)


@pytest.mark.parametrize("field,value", [
    ("native_entry_id", True), ("native_entry_id", 2), ("native_entry_id", 99),
    ("native_entry_sha256", "a" * 64), ("record_path", "../outside.yaml"),
    ("record_path", "/tmp/record.yaml"), ("record_path", "data/traits/../outside.yaml"),
])
def test_rehashed_fact_requires_exact_native_identity_and_valid_record_path(tmp_path, field, value):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot["facts"][0][field] = value
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError):
        verified(snapshot, pins)


def test_fact_cannot_qualify_a_partial_site_or_another_existing_protein(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    fact = snapshot["facts"][0]
    fact["protein_reference"] = fixture.reference(protein_id="UniProtKB:Q12345")
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="exact native reference"):
        verified(snapshot, pins)


def test_snapshot_replays_residues_against_the_embedded_reference(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot["facts"][0]["protein_reference"] = fixture.reference("MGGHCUY")
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="residue disagrees"):
        verified(snapshot, pins)


def test_embedded_acquisition_text_preserves_exact_reviewed_bytes(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot["acquisition_manifest_text"] += "\n"
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="acquisition bytes"):
        verified(snapshot, pins)


def test_duplicate_facts_and_empty_snapshots_are_not_accepted(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot["facts"].append(copy.deepcopy(snapshot["facts"][0]))
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="duplicate native source fact"):
        verified(snapshot, pins)
    snapshot["facts"] = []
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="no native site facts"):
        verified(snapshot, pins)


def test_unknown_fact_fields_and_unbound_examples_cannot_enter_record_meaning(tmp_path):
    snapshot, pins, _, _, _ = captured(tmp_path)
    snapshot["facts"][0]["record_semantics"]["canonical_examples"] = [{"protein_id": "UniProtKB:Q12345"}]
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="invalid record meaning"):
        verified(snapshot, pins)
    snapshot["facts"][0].pop("record_semantics")
    rehash(snapshot)
    with pytest.raises(source.McsaSourceError, match="source-fact fields"):
        verified(snapshot, pins)


def test_capture_reports_unsupported_examples_without_replacing_the_existing_list(tmp_path):
    path, pins = fixture.capture(tmp_path)
    native = source.read_verified_source(tmp_path, path, pins)
    record = fixture.record()
    record["canonical_examples"].append({"protein_id": "UniProtKB:Q12345"})
    before = copy.deepcopy(record)
    snapshot, blocked = capsule.build_snapshot(native, path.read_text(), {RECORD_PATH: record}, {
        "UniProtKB:P12345": fixture.reference(), "UniProtKB:Q12345": fixture.reference(protein_id="UniProtKB:Q12345")})
    assert len(snapshot["facts"]) == 1 and sum(blocked.values()) == 1
    assert record == before


def test_capture_cannot_create_facts_without_acquired_references(tmp_path):
    path, pins = fixture.capture(tmp_path)
    native = source.read_verified_source(tmp_path, path, pins)
    with pytest.raises(source.McsaSourceError, match="no complete native site facts"):
        capsule.build_snapshot(native, path.read_text(), {RECORD_PATH: fixture.record()}, {})
