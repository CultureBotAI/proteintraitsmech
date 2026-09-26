"""Tests for independently pinned IEDB source-fact custody."""

import copy
import hashlib
import importlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
capsule = importlib.import_module("iedb_peptide_snapshot")
source = importlib.import_module("iedb_peptide_source")


@pytest.fixture
def native_inputs():
    seq = "MACDEFGHIK"
    reference = {
        "protein_id": "UniProtKB:P12345", "protein_label": "Fixture antigen",
        "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
        "sequence": seq, "sequence_length": len(seq),
        "sequence_sha256": hashlib.sha256(seq.encode()).hexdigest(),
        "reviewed": True, "uniprot_release": "2026_03",
    }
    record = {
        "identifier": "IEDB:10", "label": "epitope ACDEF",
        "definition": "Linear peptide epitope ACDEF from fixture antigen.",
        "definition_source": "IEDB (epitope_full_v3)", "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_EPITOPE", "term_kind": "CLASS", "sequence_pattern": "ACDEF",
        "license": "CC-BY 4.0 (IEDB)",
        "canonical_examples": [{"protein_id": reference["protein_id"]}],
    }
    values = [""] * 32
    values[0], values[1], values[2] = "http://www.iedb.org/epitope/10", "Linear peptide", "ACDEF"
    values[5], values[6] = "200", "204"
    values[10], values[12] = (
        "http://www.uniprot.org/uniprot/Q12345", "http://www.uniprot.org/uniprot/P12345"
    )
    receipt = json.dumps({
        "bytes": 1000, "content_type": "application/zip", "destination": "source.zip",
        "fetched_at": "2026-09-16T22:39:43+00:00", "requested_url": source.SOURCE_URL,
        "resolved_url": source.SOURCE_URL, "sha256": "a" * 64,
    })
    pins = source.ExportPins("a" * 64, "b" * 64, hashlib.sha256(receipt.encode()).hexdigest())
    export = source.VerifiedExport(pins, {"IEDB:10": (source.NativeRow(3, tuple(values)),)},
                                   30, "2026-09-16T22:39:43+00:00")
    records = {"data/traits/sequence/epitope/iedb/fixture.yaml": record}
    return export, receipt, records, {reference["protein_id"]: reference}


def _repin(snapshot):
    """Only for structural tests; production callers must never trust input pins."""
    for fact in snapshot["facts"]:
        fact["fact_sha256"] = source.value_sha256(
            {k: v for k, v in fact.items() if k != "fact_sha256"}
        )
    snapshot["snapshot_id"] = "iedb-peptide-snapshot:" + source.value_sha256(
        {k: v for k, v in snapshot.items() if k != "snapshot_id"}
    )
    raw = capsule.snapshot_bytes(snapshot)
    return raw, hashlib.sha256(raw).hexdigest()


def test_capture_and_verify_preserve_native_rows_reference_and_trait_meaning(native_inputs):
    before = copy.deepcopy(native_inputs)
    snapshot, blocked = capsule.build_snapshot(*native_inputs)
    raw = capsule.snapshot_bytes(snapshot)
    verified = capsule.verify_snapshot(raw, hashlib.sha256(raw).hexdigest(), native_inputs[0].pins)
    assert not blocked
    assert len(verified.facts) == 1
    match = next(iter(verified.locations.values()))
    assert (match.start, match.end) == (2, 6)
    assert match.native_data_record_index == 3
    assert "qualification_status" not in snapshot["facts"][0]
    assert native_inputs == before


def test_even_consistently_rehashed_forgery_cannot_replace_reviewed_snapshot(native_inputs):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    expected = hashlib.sha256(capsule.snapshot_bytes(snapshot)).hexdigest()
    snapshot["facts"][0]["record_semantics"]["definition"] = "Forged trait meaning."
    changed, _ = _repin(snapshot)
    with pytest.raises(source.IedbSourceError, match="independently reviewed"):
        capsule.verify_snapshot(changed, expected, native_inputs[0].pins)


@pytest.mark.parametrize("kind", [
    "parent", "peptide", "modification", "index", "path", "unknown_fact_field", "reference",
])
def test_structural_contract_rejects_rehashed_invalid_facts(native_inputs, kind):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    fact = snapshot["facts"][0]
    if kind == "parent":
        fact["native_row"]["values"][12] = "http://www.uniprot.org/uniprot/Q12345"
    elif kind == "peptide":
        fact["record_semantics"]["sequence_pattern"] = "ACDEG"
    elif kind == "modification":
        fact["native_row"]["values"][3] = "3"
    elif kind == "index":
        fact["native_row"]["data_record_index"] = 31
    elif kind == "path":
        fact["record_path"] = "data/traits/../../unexpected.yaml"
    elif kind == "unknown_fact_field":
        fact["qualification_status"] = "QUALIFIED"
    else:
        fact["protein_reference"]["sequence_sha256"] = "c" * 64
    raw, pin = _repin(snapshot)
    with pytest.raises(source.IedbSourceError):
        capsule.verify_snapshot(raw, pin, native_inputs[0].pins)


@pytest.mark.parametrize("column", [0, 10, 12])
@pytest.mark.parametrize("control", ["\t", "\n", " ", "\x00", "\x7f"])
def test_uri_controls_cannot_be_normalized_into_an_exact_native_identifier(
    native_inputs, column, control
):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    values = snapshot["facts"][0]["native_row"]["values"]
    values[column] = control + values[column]
    raw, pin = _repin(snapshot)
    with pytest.raises(source.IedbSourceError, match="whitespace or control"):
        capsule.verify_snapshot(raw, pin, native_inputs[0].pins)


def test_duplicate_fact_identity_is_rejected(native_inputs):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    snapshot["facts"].append(copy.deepcopy(snapshot["facts"][0]))
    raw, pin = _repin(snapshot)
    with pytest.raises(source.IedbSourceError, match="duplicate"):
        capsule.verify_snapshot(raw, pin, native_inputs[0].pins)


def test_snapshot_cannot_claim_another_source_release(native_inputs):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    raw, pin = _repin(snapshot)
    other = replace(native_inputs[0].pins, csv_sha256="c" * 64)
    with pytest.raises(source.IedbSourceError, match="source, release"):
        capsule.verify_snapshot(raw, pin, other)


def test_fetch_receipt_is_bound_as_exact_acquired_bytes(native_inputs):
    snapshot, _ = capsule.build_snapshot(*native_inputs)
    snapshot["fetch_receipt_text"] += "\n"
    raw, pin = _repin(snapshot)
    with pytest.raises(source.IedbSourceError, match="fetch receipt bytes"):
        capsule.verify_snapshot(raw, pin, native_inputs[0].pins)


def test_capture_cannot_add_a_protein_absent_from_existing_examples(native_inputs):
    export, receipt, records, refs = native_inputs
    next(iter(records.values()))["canonical_examples"] = []
    with pytest.raises(source.IedbSourceError, match="no uniquely localized"):
        capsule.build_snapshot(export, receipt, records, refs)


def test_record_meaning_projection_ignores_occurrence_enrichment_but_binds_the_pattern(native_inputs):
    record = next(iter(native_inputs[2].values()))
    original = capsule.record_semantics(record)
    record["canonical_examples"][0]["trait_occurrences"] = [{"example": "placeholder"}]
    assert capsule.record_semantics(record) == original
    record["sequence_pattern"] = "ACDEG"
    assert capsule.record_semantics(record) != original
