"""End-to-end residue chemistry/context/trait boundaries and hostile mutations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from consume_molecular_evidence import resolve
from molecular_evidence import canonical
from residue_reasoning import validate_reasoning
from validate_molecular_evidence import validate_bundle

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bundle():
    return json.loads((ROOT / "data/molecular/slc10/pilot.json").read_text())


def request_for(case, bundle=None):
    request = json.loads((ROOT / f"data/molecular/slc10/residue-query-{case}.json").read_text())
    raw = (ROOT / "data/molecular/slc10/pilot.json").read_bytes() if bundle is None else canonical(bundle).encode()
    if bundle is not None:
        request["bundle_sha256"] = hashlib.sha256(raw).hexdigest()
    return raw, request


@pytest.mark.parametrize("case", ["s267f", "r252h"])
def test_complete_case_has_properties_exact_context_and_independent_measured_branches(case, bundle):
    raw, request = request_for(case)
    result = resolve(raw, request)
    assert result["annotation_action"] == "NONE"
    assert result["residue_context"]["residue_address"] == {
        "protein_id": request["protein_id"], "sequence_sha256": request["sequence_sha256"], **request["residue_query"]}
    mechanism = result["mechanisms"][0]
    entry = mechanism["residue_evidence"]["entries"][0]
    assert entry["chemistry"]["causal_inference"] == "NONE"
    assert len(entry["chemistry"]["differences"]) == 8
    ledger = entry["reasoning"][0]
    assert len(ledger["context_trait_links"]) == 2
    assert all(link["assessment"] == "UNRESOLVED" for link in ledger["context_trait_links"])
    assertions = {a["assertion_id"]: a for a in ledger["assertions"]}
    for link in ledger["context_trait_links"]:
        assay = assertions[link["observation_ref"]]
        assert assay["evidence_origin"] == "EXPERIMENTAL_ASSAY"
        assert assay["construct"] and assay["expression_localization_controls"] and assay["evidence"]
    contexts = result["residue_context"]["local_context"]
    if case == "s267f":
        simulation = next(c for c in contexts if c["evidence_origin"] == "PUBLISHED_SIMULATION")
        assert simulation["partner_id"] == "CHEBI:36257"
        assert simulation["evidence"][0]["reference"] == "https://doi.org/10.1016/j.bpj.2024.03.033"
        estrone = next(link for link in ledger["context_trait_links"] if "estrone" in link["observation_ref"])
        assert simulation["assertion_id"] not in estrone["context_refs"]
        deposited = next(l for l in ledger["property_context_links"] if "CHO" in l["context_ref"])
        assert "glycochenodeoxycholic acid" in deposited["limitations"]
    else:
        assert not any(c["evidence_origin"] == "PUBLISHED_SIMULATION" for c in contexts)
        assert {link["assessment"] for link in ledger["property_context_links"]} == {"REFERENCE_CONTEXT_ONLY"}
        assert any(assertions[link["observation_ref"]]["outcome"] == "NOT_DETECTED" for link in ledger["context_trait_links"])
    original = next(m for m in bundle["mechanisms"] if m["mechanism_id"] == mechanism["mechanism_id"])
    assert mechanism["graph"] == original["graph"]  # No edges manufactured from chemistry.


@pytest.mark.parametrize("alternate", [None, "A", "X"])
def test_no_matching_mechanism_still_returns_chemistry_without_borrowing_variant_evidence(alternate):
    raw, request = request_for("s267f")
    if alternate is None:
        request["residue_query"].pop("substituted_residue")
    else:
        request["residue_query"]["substituted_residue"] = alternate
    result = resolve(raw, request)
    assert result["mechanisms"] == []
    assert result["retrieval_status"] == "NO_CURATED_MECHANISM"
    assert result["residue_context"]["chemistry"]["reference"]["entry"]["one_letter"] == "S"
    assert not any(c["evidence_origin"] == "PUBLISHED_SIMULATION" for c in result["residue_context"]["local_context"])
    if alternate == "X":
        assert result["residue_context"]["chemistry"]["comparison_status"] == "UNSUPPORTED_RESIDUE"


def test_old_bundle_remains_usable_without_catalog(bundle):
    for key in ("amino_acid_catalog", "residue_reasoning", "residue_environments", "residue_simulations"):
        bundle.pop(key)
    result = resolve(*request_for("s267f", bundle))
    assert result["residue_context"]["status"] == "CATALOG_NOT_INCLUDED"
    assert result["mechanisms"][0]["residue_evidence"]["status"] == "CATALOG_NOT_INCLUDED"


@pytest.mark.parametrize("mutation,expected", [
    (lambda b: b.pop("amino_acid_catalog"), "requires a reviewed"),
    (lambda b: b["amino_acid_catalog"].pop("review"), "source-transcription review"),
    (lambda b: b["residue_reasoning"][0].update(catalog_sha256="0" * 64), "catalog pin"),
    (lambda b: b["residue_reasoning"][0]["residue_binding"].update(substituted_residue="A"), "exact mechanism binding"),
    (lambda b: b["residue_reasoning"][0]["residue_binding"].update(protein_id="UniProtKB:Q96EP9"), "exact mechanism binding"),
    (lambda b: b["residue_reasoning"][0]["property_context_links"][0].update(assessment="COMPUTATIONAL_HYPOTHESIS"), "evidence assessment"),
    (lambda b: b["residue_reasoning"][0]["property_context_links"][0].update(context_ref="unknown"), "context protein/sequence"),
    (lambda b: b["residue_reasoning"][0]["property_context_links"][0].update(context_ref="slc10-environment:7ZYI-A-252-4.5A"), "context residue/variant"),
    (lambda b: b["residue_simulations"][0].update(partner_id="CHEBI:28865"), "partner does not match"),
    (lambda b: b["residue_simulations"][0].update(evidence_origin="EXPERIMENTAL_ASSAY"), "published computation"),
    (lambda b: b["residue_simulations"][0].update(substituted_residue="A"), "context residue/variant"),
    (lambda b: b["residue_simulations"][0]["evidence"][0].pop("snippet"), "source excerpt"),
    (lambda b: b["residue_reasoning"][0]["context_trait_links"][0].update(observation_ref="slc10-assay:ntcp-r252h-uptake-reduction-2015"), "matching scoped"),
    (lambda b: b["residue_reasoning"][0]["context_trait_links"][0].update(assessment="SOURCE_PROPOSED_HYPOTHESIS"), "own exact source evidence"),
    (lambda b: b["residue_reasoning"][0]["context_trait_links"][0].update(context_refs=["unknown"]), "consequence contexts"),
    (lambda b: b["residue_environments"][0]["neighbors"][0].update(distance_angstrom=100), "distance/cutoff"),
    (lambda b: b["residue_environments"][0]["neighbors"][0]["partner_atom"].update(auth_chain="B"), "reference protein/chain"),
    (lambda b: b["residue_environments"][0].update(mapping_source="7ZYI.cif"), "identity/role"),
])
def test_semantic_mutations_fail_closed_even_when_outer_bundle_is_repinned(bundle, mutation, expected):
    mutation(bundle)
    assert any(expected in error for error in validate_reasoning(bundle))
    with pytest.raises(ValueError, match="invalid molecular bundle"):
        resolve(*request_for("s267f", bundle))


@pytest.mark.parametrize("field", ["property_context_links", "context_trait_links"])
def test_empty_ledgers_rejected(bundle, field):
    bundle["residue_reasoning"][0][field] = []
    assert validate_bundle(bundle)


def test_stale_request_cannot_consume_changed_catalog(bundle):
    raw, request = request_for("s267f")
    bundle["amino_acid_catalog"]["amino_acids"][0]["label"] += " changed"
    with pytest.raises(ValueError, match="export checksum"):
        resolve(canonical(bundle).encode(), request)


def test_taurocholate_simulation_cannot_be_attached_to_estrone_sulfate_branch(bundle):
    bundle["residue_reasoning"][0]["context_trait_links"][1]["context_refs"].append(
        "slc10-simulation:ntcp-s267f-taurocholate-2024")
    assert any("simulation/assay substrate mismatch" in e for e in validate_reasoning(bundle))


def test_simulation_requires_explicit_matching_assay_substrate(bundle):
    assay = next(a for a in bundle["functional_observations"] if a["assertion_id"].endswith("s267f-taurocholate-reduction-2021"))
    assay.pop("substrate_id")
    assert any("simulation/assay substrate mismatch" in e for e in validate_reasoning(bundle))


def test_single_variant_ledger_cannot_survive_compound_node_mutation(bundle):
    m = next(m for m in bundle["mechanisms"] if m["mechanism_id"].endswith("s267f-substrate-selectivity"))
    m["residue_bindings"].append({**m["residue_bindings"][0], "position": 252, "residue": "R", "substituted_residue": "H"})
    assert any("isolated single substitution" in e for e in validate_reasoning(bundle))


def test_input_objects_not_mutated(bundle):
    before = deepcopy(bundle)
    assert validate_reasoning(bundle) == []
    resolve(*request_for("s267f", bundle))
    assert bundle == before
