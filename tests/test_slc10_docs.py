"""The committed pilot and its published export are checked independently of raw downloads."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_slc10_docs import ROOT, exports
from validate_molecular_evidence import validate_bundle


@pytest.fixture(scope="module")
def pilot():
    return json.loads((ROOT / "data/molecular/slc10/pilot.json").read_text())


def test_committed_pilot_is_closed_schema_and_semantically_valid(pilot):
    assert validate_bundle(pilot) == []
    assert len(pilot["protein_references"]) == 7
    assert len(pilot["model_comparisons"]) == 3
    assert len(pilot["mechanisms"]) == 7
    assert len(pilot["functional_observations"]) == 16
    assert len(pilot["explanations"]) == 5
    assert "Pfam:PF13593" in pilot["trait_refs"]
    assert "Q0GE19: PANTHER:PTHR18640, Pfam:PF13593" in pilot["scope_note"]


def test_pilot_retains_distinct_ligands_states_and_self_control(pilot):
    sites = pilot["sites"]
    assert len([s for s in sites if s["structure_id"] == "PDB:7ZYI" and s["ligand_id"] == "PDBCCD:CHO"]) == 2
    assert len({s["structure_state"] for s in sites}) == 3
    model = next(m for m in pilot["model_comparisons"] if m["protein_id"] == "UniProtKB:Q14973")
    f128 = next(p for p in model["pairs"] if p["anchor_position"] == 128)
    assert (f128["target_position"], f128["target_residue"]) == (128, "F")
    for comparison in pilot["comparisons"]:
        if comparison["protein_id"] == "UniProtKB:Q14973":
            assert all(r["anchor_position"] == r["target_position"] and r["status"] == "IDENTICAL" for r in comparison["residues"])


def test_production_contact_carbon_is_not_sodium_oxygen_coordination(pilot):
    # 9QZQ E257 side-chain carbon proximity must not be confused with a ligand oxygen.
    site = next(s for s in pilot["sites"] if s["assertion_id"] == "slc10-site:9QZQ-F-402-NA-4.5A")
    contacts = [c for c in site["contacts"] if c["protein_position"] == 257 and c["atom_role"] == "SIDECHAIN"]
    assert contacts and all(c["protein_atom"]["element"] == "C" for c in contacts)
    assert [s["cutoff_angstrom"] for s in site["cutoff_sensitivity"]] == [4, 4.5, 5]
    middle = site["cutoff_sensitivity"][1]
    assert middle["atom_pair_count"] == len(site["contacts"])
    assert 257 not in middle["sidechain_heteroatom_positions"]


def test_sodium_mechanism_points_to_the_original_coordination_figure(pilot):
    mechanism = next(m for m in pilot["mechanisms"] if m["mechanism_id"] == "slc10-mechanism:ntcp-sodium-coordination")
    citation = next(e for e in mechanism["graph"]["edges"][0]["evidence"]
                    if e["reference"] == "https://doi.org/10.1038/s41422-022-00680-4")
    assert citation["notes"] == (
        "Original substrate-bound structure; Figure 1i, Supplementary Figure S7, and sodium-site discussion."
    )


def test_experimental_and_interpretive_statuses_are_not_collapsed(pilot):
    assertions = {a["assertion_id"]: a for a in pilot["functional_observations"]}
    assert assertions["slc10-assay:mouse-pres1-binding-2013"]["outcome"] == "DETECTED"
    assert assertions["slc10-assay:mouse-viral-infection-2013"]["outcome"] == "NOT_DETECTED"
    assert assertions["slc10-assessment:a7-assay-identity-unresolved"]["outcome"] == "NOT_ASSESSED"
    assert assertions["slc10-assay:a4-thrombin-associated-uptake-2013"]["activity"] != "Taurocholate uptake"
    assert all(s["review_status"] == "PROPOSED" for s in pilot["sites"])
    mutant = assertions["slc10-assay:ntcp-e257a-uptake-reduction-2014"]
    assert mutant["outcome"] == "DETECTED" and mutant["activity"].startswith("Reduction")
    assert mutant["sequence_substitutions"] == [{"position": 257, "residue": "E", "substituted_residue": "A"}]
    assert "not complete absence" in mutant["limitations"]
    mechanism = next(m for m in pilot["mechanisms"] if m["mechanism_id"] == "slc10-mechanism:ntcp-e257a-uptake-reduction")
    assert mechanism["residue_bindings"][0]["substituted_residue"] == "A"


def test_export_preserves_exact_payload_and_checksum():
    raw = (ROOT / "data/molecular/slc10/pilot.json").read_bytes()
    result = exports(raw)
    manifest = json.loads(result["slc10-pilot-manifest.json"])
    assert result[manifest["file"]] == raw
    assert manifest["sha256"] == hashlib.sha256(raw).hexdigest()
    assert manifest["bytes"] == len(raw)


def test_r252h_chain_preserves_measured_localization_and_interpreted_mediation(pilot):
    observations = {o["assertion_id"]: o for o in pilot["functional_observations"]}
    surface = observations["slc10-assay:ntcp-r252h-surface-depletion-2015"]
    uptake = observations["slc10-assay:ntcp-r252h-uptake-reduction-2015"]
    assert surface["outcome"] == "NOT_DETECTED"
    assert uptake["outcome"] == "DETECTED" and uptake["activity"].startswith("Reduction")
    assert surface["sequence_substitutions"] == uptake["sequence_substitutions"] == [
        {"position": 252, "residue": "R", "substituted_residue": "H"}
    ]
    assert "Residual transport" in uptake["limitations"]
    mechanism = next(m for m in pilot["mechanisms"]
                     if m["mechanism_id"] == "slc10-mechanism:ntcp-r252h-surface-availability")
    first, second = mechanism["graph"]["edges"]
    assert (first["subject"], first["object"]) == ("r252h", "surface_depleted")
    assert (second["subject"], second["object"]) == ("surface_depleted", "uptake")
    assert first["description"].startswith("EXPERIMENTAL RESULT")
    assert second["description"].startswith("AUTHOR INTERPRETATION")
    assert "not independently isolated" in second["description"]
    assert all(e["evidence"][0]["reference"] == "https://doi.org/10.1002/hep.27240"
               for e in (first, second))


def test_s267f_retains_substrate_specific_opposite_effects_without_invented_intermediate(pilot):
    mechanism = next(m for m in pilot["mechanisms"]
                     if m["mechanism_id"] == "slc10-mechanism:ntcp-s267f-substrate-selectivity")
    assert {n["node_type"] for n in mechanism["graph"]["nodes"]} == {"RESIDUE", "MOLECULAR_FUNCTION"}
    assert {(e["subject"], e["predicate_id"], e["object"]) for e in mechanism["graph"]["edges"]} == {
        ("s267f", "RO:0002212", "taurocholate_uptake"),
        ("s267f", "RO:0002213", "estrone_sulfate_uptake"),
    }
    observations = {o["assertion_id"]: o for o in pilot["functional_observations"]}
    estrone = observations["slc10-assay:ntcp-s267f-estrone-sulfate-increase-2021"]
    assert "before surface-expression correction" in estrone["conditions"]
    assert "Earlier studies" in estrone["limitations"]
    for ref in mechanism["assertion_refs"]:
        if ref in observations:
            assert observations[ref]["sequence_substitutions"] == [
                {"position": 267, "residue": "S", "substituted_residue": "F"}
            ]


@pytest.mark.parametrize("case", ["ntcp-r252h-surface-availability", "ntcp-s267f-substrate-selectivity"])
def test_supported_residue_explanations_remain_proposed_and_assay_backed(pilot, case):
    explanation = next(e for e in pilot["explanations"] if e["assertion_id"] == "slc10-explanation:" + case)
    assert explanation["assessment"] == "SUPPORTED"
    assert explanation["review_status"] == "PROPOSED"
    assert explanation["evidence_origin"] == "CURATOR_INTERPRETATION"
    assert len(explanation["supporting_assertions"]) == 2
    observations = {o["assertion_id"]: o for o in pilot["functional_observations"]}
    assert all(observations[ref]["evidence_origin"] == "EXPERIMENTAL_ASSAY"
               for ref in explanation["supporting_assertions"])
    assert explanation["unresolved_questions"]


def test_unresolved_case_preserves_assay_and_correspondence_gaps(pilot):
    explanation = next(e for e in pilot["explanations"] if e["assertion_id"] == "slc10-explanation:a7-site-divergence")
    assert explanation["assessment"] == "UNRESOLVED"
    assert not explanation.get("supporting_assertions") and not explanation.get("challenging_assertions")
    assert "slc10-assessment:a7-assay-identity-unresolved" in explanation["context_assertions"]
    assert "slc10-model:Q0GE19-v6-7ZYI" in explanation["context_assertions"]
    assert "no general lack" in explanation["limitations"]


@pytest.mark.parametrize("version", ["../escape", "1/../../other", "", 1])
def test_export_rejects_unexpected_version(version):
    with pytest.raises((ValueError, TypeError)):
        exports(json.dumps({"bundle_id": "ptm-molecular:slc10", "version": version}).encode())


def test_page_does_not_treat_untrusted_evidence_as_html():
    js = (ROOT / "docs/slc10.js").read_text()
    assert "innerHTML" not in js and "insertAdjacentHTML" not in js
    assert 'crypto.subtle.digest("SHA-256",raw)' in js
    assert 'receipt.sha256' in js
    assert "ligand occupancy inferred" in js


def test_build_and_deployment_include_export():
    workflow = (ROOT / ".github/workflows/pages.yml").read_text()
    assert '"data/molecular/slc10/pilot.json"' in workflow
    assert "python scripts/build_slc10_docs.py --check" in workflow
    assert 'href="slc10.html"' in (ROOT / "docs/index.html").read_text()
