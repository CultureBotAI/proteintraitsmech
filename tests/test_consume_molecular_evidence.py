"""A reviewed reference cannot silently drift to new bytes, sequences or annotations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from consume_molecular_evidence import main, resolve

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
    assert result["mechanisms"] == []  # NTCP graphs do not transfer to A4.


@pytest.fixture(params=[
    ("ntcp-r252h-surface-availability",
     ("ntcp-r252h-surface-depletion-2015", "ntcp-r252h-uptake-reduction-2015"),
     {"position": 252, "residue": "R", "substituted_residue": "H"}),
    ("ntcp-s267f-substrate-selectivity",
     ("ntcp-s267f-taurocholate-reduction-2021", "ntcp-s267f-estrone-sulfate-increase-2021"),
     {"position": 267, "residue": "S", "substituted_residue": "F"}),
], ids=["R252H", "S267F"])
def residue_inputs(inputs, request):
    raw, original = inputs
    case, support_names, substitution = request.param
    bundle = json.loads(raw)
    protein = next(p for p in bundle["protein_references"] if p["protein_id"] == "UniProtKB:Q14973")
    consumer_request = deepcopy(original)
    consumer_request.update(
        protein_id=protein["protein_id"], sequence_sha256=protein["sequence_sha256"],
        assertion_id="slc10-explanation:" + case,
        fixture="PRODUCTION_RESIDUE_CONSUMER_TEST_NOT_UPSTREAM_ADOPTION",
    )
    support_ids = {"slc10-assay:" + name for name in support_names}
    return raw, consumer_request, bundle, support_ids, substitution


def test_production_residue_claim_resolves_with_exact_experimental_support(residue_inputs):
    raw, request, bundle, support_ids, substitution = residue_inputs
    before = deepcopy(request)
    result = resolve(raw, request)
    assert request == before
    assert result["annotation_action"] == "NONE"
    claim = next(e for e in bundle["explanations"] if e["assertion_id"] == request["assertion_id"])
    assert result["claim"] == claim
    assert claim["assessment"] == "SUPPORTED" and claim["review_status"] == "PROPOSED"
    assert claim["limitations"] and claim["unresolved_questions"]
    assert {row["assertion_id"] for row in result["basis"]} == support_ids
    observations = {row["assertion_id"]: row for row in bundle["functional_observations"]}
    for row in result["basis"]:
        assert row == observations[row["assertion_id"]]  # including source snippets and assay limits
        assert row["protein_id"] == request["protein_id"]
        assert row["sequence_sha256"] == request["sequence_sha256"]
        assert row["evidence_origin"] == "EXPERIMENTAL_ASSAY"
        assert row["review_status"] == "PROPOSED"
        assert row["sequence_substitutions"] == [substitution]
        assert row["evidence"] and row["limitations"]
    assert result["argument_edges"] == [
        {"explanation_id": claim["assertion_id"], "relation": "SUPPORTS", "assertion_id": ref}
        for ref in sorted(support_ids)
    ]
    assert result["context"] == result["context_edges"] == []
    assert "upstream_review" not in result
    assert len(result["mechanisms"]) == 1
    mechanism = result["mechanisms"][0]
    original = next(m for m in bundle["mechanisms"] if claim["assertion_id"] in m["assertion_refs"])
    assert {key: mechanism[key] for key in original} == original
    assert {a["assertion_id"] for a in mechanism["assertions"]} == support_ids | {claim["assertion_id"]}
    assert mechanism["argument_edges"] == result["argument_edges"]


@pytest.mark.parametrize("field,value,match", [
    ("protein_id", "UniProtKB:Q96EP9", "claim/protein/sequence mismatch"),
    ("sequence_sha256", "0" * 64, "claim/protein/sequence mismatch"),
    ("usage", "ASSIGN_GO", "cannot authorize annotations"),
])
def test_production_residue_claim_rejects_scope_drift_and_annotation_requests(residue_inputs, field, value, match):
    raw, original, _, _, _ = residue_inputs
    request = deepcopy(original)
    request[field] = value
    with pytest.raises(ValueError, match=match):
        resolve(raw, request)


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


def nest_comparison_arguments(raw, request):
    """Put the original comparison arguments behind a same-protein subclaim."""
    bundle = json.loads(raw)
    claim = next(e for e in bundle["explanations"] if e["assertion_id"] == request["assertion_id"])
    nested = deepcopy(claim)
    nested["assertion_id"] += "-nested"
    nested["assessment"] = "SUPPORTED"
    comparisons = nested.pop("challenging_assertions")
    nested["supporting_assertions"] = comparisons
    # Exercise context collection from a non-root explanation as well.
    nested["context_assertions"] = [claim["context_assertions"].pop()]
    claim["challenging_assertions"] = [nested["assertion_id"]]
    bundle["explanations"].append(nested)
    return bundle, claim, nested, comparisons


def encode_bundle(bundle, request):
    raw = json.dumps(bundle).encode()
    request["bundle_sha256"] = hashlib.sha256(raw).hexdigest()
    return raw


def test_nested_argument_closure_preserves_edge_polarity_and_context(upstream_inputs):
    raw, request, review = upstream_inputs
    bundle, claim, nested, comparisons = nest_comparison_arguments(raw, request)
    result = resolve(encode_bundle(bundle, request), request, encode_review(request, review))
    assert {r["assertion_id"] for r in result["basis"]} == {*comparisons, nested["assertion_id"]}
    assert {r["outcome"] for r in result["context"]} == {"DETECTED", "NOT_DETECTED"}
    assert {tuple(e.values()) for e in result["argument_edges"]} == {
        (claim["assertion_id"], "CHALLENGES", nested["assertion_id"]),
        *((nested["assertion_id"], "SUPPORTS", ref) for ref in comparisons),
    }
    assert {e["explanation_id"] for e in result["context_edges"]} == {
        claim["assertion_id"], nested["assertion_id"]}
    assert len(result["upstream_review"]["checked_claims"]) == 7
    assert result["annotation_action"] == "NONE"


def test_shared_argument_dag_deduplicates_objects_not_edges(inputs):
    raw, original = inputs
    request = deepcopy(original)
    bundle, claim, nested, comparisons = nest_comparison_arguments(raw, request)
    second = deepcopy(nested)
    second["assertion_id"] += "-shared"
    bundle["explanations"].append(second)
    claim["challenging_assertions"].append(second["assertion_id"])
    result = resolve(encode_bundle(bundle, request), request)
    assert len(result["basis"]) == 4  # two wrappers, two shared terminal comparisons
    assert len(result["argument_edges"]) == 6
    assert len(result["context"]) == 2
    assert len(result["context_edges"]) == 3
    assert {r["assertion_id"] for r in result["basis"]} == {
        *comparisons, nested["assertion_id"], second["assertion_id"]}


def test_nested_context_cannot_supply_upstream_argument_evidence(upstream_inputs):
    raw, request, review = upstream_inputs
    bundle, _, nested, _ = nest_comparison_arguments(raw, request)
    nested["context_assertions"].append(nested["supporting_assertions"].pop())
    with pytest.raises(ValueError, match="matching PTM comparison evidence"):
        resolve(encode_bundle(bundle, request), request, encode_review(request, review))


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


@pytest.fixture(params=["s267f", "r252h"])
def query_inputs(inputs, request):
    raw, _ = inputs
    path = ROOT / f"data/molecular/slc10/residue-query-{request.param}.json"
    return raw, json.loads(path.read_text())


def test_residue_query_preserves_complete_mechanism_and_evidence(query_inputs):
    raw, request = query_inputs
    before = deepcopy(request)
    result = resolve(raw, request)
    assert request == before
    assert result["request"] == request
    assert result["annotation_action"] == "NONE"
    assert result["retrieval_status"] == "MATCHED_CURATED_MECHANISMS"
    assert "claim" not in result  # Retrieval itself is not a new biological claim.
    assert len(result["mechanisms"]) == 1
    mechanism = result["mechanisms"][0]
    bundle = json.loads(raw)
    original = next(m for m in bundle["mechanisms"] if m["mechanism_id"] == mechanism["mechanism_id"])
    assert {key: mechanism[key] for key in original} == original
    assert mechanism["matched_residue_bindings"] == original["residue_bindings"]
    assertions = {a["assertion_id"]: a for field in ("explanations", "functional_observations") for a in bundle[field]}
    assert mechanism["assertions"] == [assertions[key] for key in sorted(original["assertion_refs"])]
    assert {a["evidence_origin"] for a in mechanism["assertions"]} == {"EXPERIMENTAL_ASSAY", "CURATOR_INTERPRETATION"}
    assert all(a["review_status"] == "PROPOSED" for a in mechanism["assertions"])
    assert all(e["evidence"][0]["snippet"] for e in mechanism["graph"]["edges"])
    assert any(a.get("unresolved_questions") for a in mechanism["assertions"])
    assert result["sources"] == bundle["sources"]


@pytest.mark.parametrize("query,expected", [
    ({"position": 257, "residue": "E"}, "slc10-mechanism:ntcp-sodium-coordination"),
    ({"position": 257, "residue": "E", "substituted_residue": "A"}, "slc10-mechanism:ntcp-e257a-uptake-reduction"),
    ({"position": 267, "residue": "S"}, None),
    ({"position": 267, "residue": "S", "substituted_residue": "A"}, None),
])
def test_residue_query_is_exact_not_a_variant_wildcard(inputs, query, expected):
    raw, _ = inputs
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    request["residue_query"] = query
    result = resolve(raw, request)
    assert [m["mechanism_id"] for m in result["mechanisms"]] == ([expected] if expected else [])
    assert result["retrieval_status"] == ("MATCHED_CURATED_MECHANISMS" if expected else "NO_CURATED_MECHANISM")
    assert "not absence of a biological effect" in result["retrieval_limitations"]
    if expected and "substituted_residue" not in query:
        mechanism = result["mechanisms"][0]
        assert {b["position"] for b in mechanism["residue_bindings"]} == {257, 261}
        assert [b["position"] for b in mechanism["matched_residue_bindings"]] == [257]
        assert "necessity or sufficiency" in result["retrieval_limitations"]


@pytest.mark.parametrize("protein_id,position,residue", [
    ("UniProtKB:Q96EP9", 335, "E"),  # Retained A4 correspondence is not target mechanism evidence.
    ("UniProtKB:Q0GE19", 1, "M"),
])
def test_residue_query_does_not_transfer_ntcp_graphs(inputs, protein_id, position, residue):
    raw, _ = inputs
    bundle = json.loads(raw)
    protein = next(p for p in bundle["protein_references"] if p["protein_id"] == protein_id)
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    request.update(protein_id=protein_id, sequence_sha256=protein["sequence_sha256"],
                   residue_query={"position": position, "residue": residue})
    result = resolve(raw, request)
    assert result["mechanisms"] == []
    assert result["retrieval_status"] == "NO_CURATED_MECHANISM"
    assert result["annotation_action"] == "NONE"


@pytest.mark.parametrize("query", [
    None, [], {}, {"position": 267}, {"position": 267, "residue": "S", "extra": "value"},
    {"position": True, "residue": "M"}, {"position": 267.0, "residue": "S"},
    {"position": "267", "residue": "S"}, {"position": 0, "residue": "S"},
    {"position": 10000, "residue": "S"}, {"position": 267, "residue": "F"},
    {"position": 267, "residue": ["S"]},
    *[{"position": 267, "residue": "S", "substituted_residue": alt}
      for alt in (None, "S", "f", "FF", "*", 5, ["F"])],
])
def test_invalid_residue_query_refused(inputs, query):
    raw, _ = inputs
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    request["residue_query"] = query
    with pytest.raises(ValueError, match="query"):
        resolve(raw, request)


@pytest.mark.parametrize("field,value,match", [
    ("bundle_id", "different", "identity/version"),
    ("bundle_version", "2", "identity/version"),
    ("bundle_sha256", "0" * 64, "checksum"),
    ("sequence_sha256", "0" * 64, "protein/sequence mismatch"),
    ("protein_id", "UniProtKB:P00000", "protein/sequence mismatch"),
    ("usage", "ASSIGN_GO", "cannot authorize annotations"),
    ("assertion_id", "slc10-explanation:a4-residue-loss", "unknown or missing fields"),
    ("upstream_review", {}, "unknown or missing fields"),
])
def test_residue_request_pin_and_mode_boundaries(inputs, field, value, match):
    raw, _ = inputs
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    request[field] = value
    with pytest.raises(ValueError, match=match):
        resolve(raw, request)


def test_partial_multi_mutant_query_does_not_claim_single_mutant_effect(inputs):
    raw, _ = inputs
    bundle = json.loads(raw)
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    mechanism = next(m for m in bundle["mechanisms"] if m["mechanism_id"].endswith("s267f-substrate-selectivity"))
    additional = {"position": 252, "residue": "R", "substituted_residue": "H"}
    mechanism["residue_bindings"].append({**mechanism["residue_bindings"][0], **additional})
    for observation in bundle["functional_observations"]:
        if observation["assertion_id"] in mechanism["assertion_refs"]:
            observation["sequence_substitutions"].append(additional)
    result = resolve(encode_bundle(bundle, request), request)
    assert result["retrieval_status"] == "NO_CURATED_MECHANISM"


def test_mechanism_response_preserves_nested_arguments_and_context(inputs):
    raw, _ = inputs
    bundle = json.loads(raw)
    request = json.loads((ROOT / "data/molecular/slc10/residue-query-s267f.json").read_text())
    claim = next(e for e in bundle["explanations"] if e["assertion_id"].endswith("s267f-substrate-selectivity"))
    nested = deepcopy(claim)
    nested["assertion_id"] += "-synthetic-nested"
    nested["assessment"] = "CHALLENGED"
    supports = nested.pop("supporting_assertions")
    nested["challenging_assertions"] = supports[:1]
    nested["context_assertions"] = supports[1:]
    claim["supporting_assertions"] = [nested["assertion_id"]]
    bundle["explanations"].append(nested)
    result = resolve(encode_bundle(bundle, request), request)
    mechanism = result["mechanisms"][0]
    assert {a["assertion_id"] for a in mechanism["assertions"]} == {*supports, claim["assertion_id"], nested["assertion_id"]}
    assert {tuple(e.values()) for e in mechanism["argument_edges"]} == {
        (claim["assertion_id"], "SUPPORTS", nested["assertion_id"]),
        (nested["assertion_id"], "CHALLENGES", supports[0]),
    }
    assert mechanism["context_edges"] == [{"explanation_id": nested["assertion_id"], "assertion_id": supports[1]}]


def test_shared_support_does_not_implicitly_link_a_mechanism(residue_inputs):
    raw, request, bundle, _, _ = residue_inputs
    for mechanism in bundle["mechanisms"]:
        if request["assertion_id"] in mechanism["assertion_refs"]:
            mechanism["assertion_refs"].remove(request["assertion_id"])
    result = resolve(encode_bundle(bundle, request), request)
    assert result["basis"]
    assert result["mechanisms"] == []


def test_query_cli_prints_read_only_result(capsys):
    directory = ROOT / "data/molecular/slc10"
    assert main(["--bundle", str(directory / "pilot.json"),
                 "--request", str(directory / "residue-query-s267f.json")]) == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert not captured.err
    assert result["retrieval_status"] == "MATCHED_CURATED_MECHANISMS"
    assert result["annotation_action"] == "NONE"
    assert result["mechanisms"][0]["mechanism_id"].endswith("s267f-substrate-selectivity")
