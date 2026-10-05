"""A reviewed reference cannot silently drift to new bytes, sequences or annotations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from consume_molecular_evidence import resolve

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def inputs():
    directory = ROOT / "data/molecular/slc10"
    return (directory / "pilot.json").read_bytes(), json.loads((directory / "gene-review-fixture.json").read_text())


def test_fixture_resolves_without_an_annotation_action(inputs):
    result = resolve(*inputs)
    assert result["annotation_action"] == "NONE"
    assert result["claim"]["assessment"] == "CHALLENGED"
    assert result["claim"]["review_status"] == "PROPOSED"
    assert len(result["basis"]) == 2
    assert all(row["evidence_origin"] == "COMPUTED_COMPARISON" for row in result["basis"])
    assert {row["outcome"] for row in result["context"]} == {"DETECTED", "NOT_DETECTED"}
    assert all(row["evidence_origin"] == "EXPERIMENTAL_ASSAY" for row in result["context"])
    assert result["claim"]["limitations"] and result["claim"]["unresolved_questions"]


@pytest.mark.parametrize("field,value", [
    ("bundle_id", "different"), ("bundle_version", "2"), ("bundle_sha256", "0" * 64),
    ("protein_id", "UniProtKB:Q14973"), ("sequence_sha256", "0" * 64),
    ("assertion_id", "absent"), ("usage", "ASSIGN_GO"), ("unknown_field", "unexpected"),
])
def test_request_drift_rejected(inputs, field, value):
    raw, original = inputs
    request = deepcopy(original)
    request[field] = value
    with pytest.raises(ValueError):
        resolve(raw, request)


def test_even_whitespace_change_requires_new_export_pin(inputs):
    raw, request = inputs
    with pytest.raises(ValueError, match="checksum"):
        resolve(raw + b" ", request)


@pytest.fixture
def upstream_inputs(inputs):
    """Synthetic YAML in the inspected upstream shape, not copied review prose."""
    raw, _ = inputs
    request = json.loads((ROOT / "data/molecular/slc10/gene-review-integration.json").read_text())
    request["fixture"] = "SYNTHETIC_UPSTREAM_SCHEMA_TEST"
    request["upstream_review"].update(repository="example/review", commit="f" * 40)
    claims = [{"claim_type": "RETAINED", "site_ref": "PANTHER:PTHR10361#na_coordination",
               "anchor": {"accession": "UniProtKB:Q14973", "position": a, "residue": aa, "sequence_version": 1},
               "target": {"accession": "UniProtKB:Q96EP9", "position": t, "residue": aa}, "method": "STRUCTURE"}
              for a, t, aa in ((68, 146, "Q"), (105, 183, "S"), (106, 184, "N"), (119, 197, "S"),
                               (123, 201, "T"), (257, 335, "E"), (261, 339, "Q"))]
    review = {"id": "Q96EP9", "existing_annotations": [{} for _ in range(9)] + [{
        "term": {"id": "GO:0015721"}, "review": {"action": "REMOVE", "propagation_review": {"residue_claims": claims}}}]}
    return raw, request, review


def encode_review(request, review):
    raw = yaml.safe_dump(review).encode()
    request["upstream_review"]["sha256"] = hashlib.sha256(raw).hexdigest()
    return raw


def test_read_only_upstream_claim_integration(upstream_inputs):
    raw, request, review = upstream_inputs
    upstream_raw = encode_review(request, review)
    before = deepcopy(request), deepcopy(review)
    result = resolve(raw, request, upstream_raw)
    assert result["annotation_action"] == "NONE"
    checked = result["upstream_review"]
    assert checked["status"] == "MATCHED_RETAINED_IDENTITIES"
    assert len(checked["checked_claims"]) == 7
    e257 = checked["checked_claims"][5]
    assert e257["target"]["position"] == 335
    assert e257["comparison_assertions"] == ["slc10-comparison:7ZYI-J-706-NA-4.5A-Q96EP9"]
    assert "not experimental" in checked["limitations"]
    assert (request, review) == before


@pytest.mark.parametrize("mutation,match", [
    (lambda r: r.update(id="Q14973"), "protein mismatch"),
    (lambda r: r["existing_annotations"][9]["term"].update(id="GO:0008508"), "identity/action"),
    (lambda r: r["existing_annotations"][9]["review"].update(action="ACCEPT"), "identity/action"),
    (lambda r: r["existing_annotations"][9]["review"].update(propagation_review={}), "claim count"),
])
def test_upstream_review_scope_mismatch(upstream_inputs, mutation, match):
    raw, request, review = upstream_inputs
    mutation(review)
    with pytest.raises(ValueError, match=match):
        resolve(raw, request, encode_review(request, review))


@pytest.mark.parametrize("mutation,match", [
    (lambda c: c.update(claim_type="LOST"), "retained claims"),
    (lambda c: c.update(site_ref="other"), "pinned site"),
    (lambda c: c["anchor"].update(sequence_version=99), "pinned PTM sequence"),
    (lambda c: c["target"].update(residue="F"), "pinned PTM sequence"),
    (lambda c: c["target"].update(position=True), "pinned PTM sequence"),
    (lambda c: c["target"].update(position=1, residue="M"), "matching PTM comparison"),
])
def test_upstream_residue_claim_mismatch(upstream_inputs, mutation, match):
    raw, request, review = upstream_inputs
    mutation(review["existing_annotations"][9]["review"]["propagation_review"]["residue_claims"][0])
    with pytest.raises(ValueError, match=match):
        resolve(raw, request, encode_review(request, review))


def test_duplicate_upstream_claim_cannot_replace_a_missing_position(upstream_inputs):
    raw, request, review = upstream_inputs
    claims = review["existing_annotations"][9]["review"]["propagation_review"]["residue_claims"]
    claims[1] = deepcopy(claims[0])
    with pytest.raises(ValueError, match="duplicate"):
        resolve(raw, request, encode_review(request, review))


@pytest.mark.parametrize("field,value", [
    ("commit", "main"), ("path", "../unrelated.yaml"), ("sha256", "not-a-hash"),
    ("annotation_index", True), ("expected_claim_count", 0), ("unexpected", "field"),
])
def test_invalid_upstream_pin_rejected(upstream_inputs, field, value):
    raw, request, review = upstream_inputs
    upstream_raw = encode_review(request, review)
    request["upstream_review"][field] = value
    with pytest.raises(ValueError, match="upstream review pin"):
        resolve(raw, request, upstream_raw)


def test_upstream_bytes_must_match_and_be_explicitly_pinned(upstream_inputs):
    raw, request, review = upstream_inputs
    upstream_raw = encode_review(request, review)
    for value in (None, upstream_raw + b" "):
        with pytest.raises(ValueError, match="checksum"):
            resolve(raw, request, value)
    request.pop("upstream_review")
    with pytest.raises(ValueError, match="explicit source pin"):
        resolve(raw, request, upstream_raw)
