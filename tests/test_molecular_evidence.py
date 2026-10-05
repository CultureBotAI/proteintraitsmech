"""Offline adversarial tests for the molecular evidence interpretation boundary."""
from copy import deepcopy
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
import sys

import gemmi
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from molecular_evidence import (atoms_from_block, compare_site, correspondence, distance,
                                optimal_correspondences, read_snapshot, sha256)
from validate_molecular_evidence import validate_bundle


def atom(number, name, residue, x, chain="A", sequence_id="1"):
    return {"atom_id": str(number), "atom_name": name, "element": "O" if name == "O" else "C",
            "residue_name": residue, "auth_chain": chain, "label_chain": chain,
            "auth_seq_id": sequence_id, "occupancy": 1.0, "x": x, "y": 0.0, "z": 0.0}


@pytest.fixture
def bundle():
    # Explicitly synthetic coordinates and sequences: not a source snapshot.
    proteins = []
    for accession, sequence in (("Q14973", "ACD"), ("Q96EP9", "ASD")):
        proteins.append({"protein_id": f"UniProtKB:{accession}", "protein_label": "synthetic",
                         "taxon_id": "NCBITaxon:9606", "taxon_label": "Homo sapiens",
                         "sequence": sequence, "sequence_length": len(sequence),
                         "sequence_sha256": sha256(sequence), "reviewed": True,
                         "uniprot_release": "2026_03", "sequence_version": 1})
    first, second = atom(1, "O", "CYS", 0, sequence_id="2"), atom(2, "NA", "NA", 2.5, "I", "705")
    second["element"] = "NA"
    site = {"assertion_id": "test:site", "protein_id": proteins[0]["protein_id"],
            "sequence_sha256": proteins[0]["sequence_sha256"], "label": "synthetic site",
            "evidence_origin": "COMPUTED_CONTACTS", "review_status": "PROPOSED",
            "structure_id": "PDB:7ZYI", "structure_source": "7ZYI.cif", "mapping_source": "7zyi.xml.gz",
            "structure_state": "synthetic state", "model_number": 1,
            "assembly_scope": "DEPOSITED_ASYMMETRIC_UNIT",
            "conformer_policy": "INDEPENDENT_ATOM_PROXIMITIES_NO_JOINT_CONFORMER_ASSERTION",
            "ligand_id": "PDBCCD:NA", "ligand_instance": "I:I:705:NA", "distance_cutoff_angstrom": 4.5,
            "contacts": [{"protein_position": 2, "protein_residue": "C", "protein_atom": first,
                          "ligand_atom": second, "atom_role": "MAINCHAIN", "distance_angstrom": 2.5}],
            "evidence": [{"reference": "https://doi.org/10.2210/pdb7ZYI/pdb"}],
            "limitations": "Synthetic test; not biological evidence."}
    comparison = compare_site(site, proteins[0], proteins[1], {2: 2})
    return {"bundle_id": "test:synthetic", "version": "1", "trait_refs": ["Pfam:PF01758"],
            "scope_note": "Synthetic test panel; no biological membership claim.",
            "protein_references": proteins,
            "sources": [{"source_id": name, "reference": "https://example.org/fixture",
                         "source_version": "synthetic", "sha256": "a" * 64, "license": "CC0-1.0",
                         "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"}
                        for name in ("7ZYI.cif", "7zyi.xml.gz")],
            "sites": [site], "comparisons": [comparison]}


def test_valid_synthetic_bundle(bundle):
    assert validate_bundle(bundle) == []
    assert bundle["comparisons"][0]["residues"][0]["status"] == "CHANGED"
    # Backbone identity changes are recorded; never automatically called neutral.
    assert bundle["sites"][0]["contacts"][0]["atom_role"] == "MAINCHAIN"


@pytest.mark.parametrize("sequence", ["ACDEFGHIKLMNPQRSTVWY", "MFFFFGGGGAAAA", "A"])
def test_self_alignment_exact(sequence):
    assert correspondence(sequence, sequence) == {i: i for i in range(1, len(sequence) + 1)}


@pytest.mark.parametrize("gaps", [(-10, -0.5), (-12, -1), (-1, -0.5)])
def test_optimal_path_dag_matches_exhaustive_biopython(gaps):
    from Bio import Align
    from Bio.Align import substitution_matrices
    aligner = Align.PairwiseAligner(mode="global", substitution_matrix=substitution_matrices.load("BLOSUM62"),
                                  open_gap_score=gaps[0], extend_gap_score=gaps[1])
    sequences = ["".join(s) for n in range(1, 4) for s in product("AC", repeat=n)]
    for anchor, target in product(sequences, repeat=2):
        expected = defaultdict(set)
        for alignment in aligner.align(anchor, target):
            for a, t in zip(*alignment.indices, strict=True):
                if a >= 0:
                    expected[int(a) + 1].add(int(t) + 1 if t >= 0 else None)
        assert optimal_correspondences(anchor, target, *gaps) == expected


def test_many_optimal_paths_preserve_stable_columns():
    anchor, target = "W" + "AC" * 12 + "Y", "W" + "AC" * 6 + "Y"
    partners = optimal_correspondences(anchor, target, -1, -1)
    assert partners[1] == {1} and partners[len(anchor)] == {len(target)}
    assert any(len(p) > 1 for p in partners.values())


@pytest.mark.parametrize("mutation,expected", [
    (lambda b: b["protein_references"][0].update(sequence="AAA"), "checksum"),
    (lambda b: b["protein_references"][0].update(sequence_length=4), "length"),
    (lambda b: b["sites"][0].update(sequence_sha256="f" * 64), "sequence"),
    (lambda b: b["sites"][0].update(mapping_source="missing"), "source"),
    (lambda b: b["sites"][0].update(evidence_origin="EXPERIMENTAL_ASSAY"), "COMPUTED_CONTACTS"),
    (lambda b: b["sites"][0].update(evidence=[]), "evidence"),
    (lambda b: b["sites"][0].update(required_for="GO:0008508"), "required_for"),
    (lambda b: b["sites"][0].update(distance_cutoff_angstrom=2.0), "cutoff"),
    (lambda b: b["sites"][0]["contacts"][0].update(protein_position=20), "residue"),
    (lambda b: b["sites"][0]["contacts"][0].update(protein_residue="S"), "residue"),
    (lambda b: b["sites"][0]["contacts"][0]["protein_atom"].update(residue_name="GLU"), "atom residue"),
    (lambda b: b["sites"][0]["contacts"][0].update(atom_role="SIDECHAIN"), "role"),
    (lambda b: b["sites"][0]["contacts"][0].update(distance_angstrom=2.4), "distance"),
    (lambda b: b["sites"][0]["contacts"][0]["ligand_atom"].update(auth_seq_id="706"), "ligand"),
    (lambda b: b["sites"][0]["contacts"][0]["ligand_atom"].update(element="H"), "heavy-atom"),
    (lambda b: b["sites"][0]["contacts"][0]["ligand_atom"].update(occupancy=0), "occupancy"),
    (lambda b: b["sites"][0]["contacts"].append(deepcopy(b["sites"][0]["contacts"][0])), "duplicate"),
    (lambda b: b["comparisons"][0].update(evidence_origin="EXPERIMENTAL_ASSAY"), "COMPUTED_COMPARISON"),
    (lambda b: b["comparisons"][0].update(site_ref="missing"), "site"),
    (lambda b: b["comparisons"][0].update(residues=[]), "cover"),
    (lambda b: b["comparisons"][0].update(qualification_status="QUALIFIED"), "qualification_status"),
    (lambda b: b["comparisons"][0]["residues"][0].update(status="IDENTICAL"), "identity"),
    (lambda b: b["comparisons"][0]["residues"][0].update(target_position=3), "target"),
    (lambda b: b["comparisons"][0]["residues"][0].update(status="UNRESOLVED"), "unresolved"),
])
def test_adversarial_mutations_fail(bundle, mutation, expected):
    mutation(bundle)
    errors = validate_bundle(bundle)
    assert errors and expected.lower() in " ".join(errors).lower()


def test_unresolved_does_not_assert_residue(bundle):
    comparison = compare_site(bundle["sites"][0], *bundle["protein_references"], {2: None})
    row = comparison["residues"][0]
    assert row["status"] == "UNRESOLVED"
    assert "target_position" not in row and "target_residue" not in row
    bundle["comparisons"] = [comparison]
    assert validate_bundle(bundle) == []


def test_nonfinite_geometry_rejected(bundle):
    bundle["sites"][0]["contacts"][0]["protein_atom"]["x"] = float("nan")
    assert validate_bundle(bundle)


def test_incomplete_snapshot_refused(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"kind": "SLC10_RESEARCH_SNAPSHOT",
                                                      "schema_version": 1, "artifacts": []}))
    with pytest.raises(ValueError, match="incomplete"):
        read_snapshot(tmp_path)


def test_atom_parser_preserves_author_label_insertion_altloc():
    block = gemmi.cif.Block("synthetic")
    block.set_mmcif_category("_atom_site.", {
        "group_PDB": ["ATOM"], "id": ["1"], "type_symbol": ["O"], "label_atom_id": ["O"],
        "label_alt_id": ["B"], "label_comp_id": ["GLU"], "label_asym_id": ["Z"],
        "label_seq_id": ["5"], "pdbx_PDB_ins_code": ["A"], "Cartn_x": ["1"],
        "Cartn_y": ["2"], "Cartn_z": ["3"], "occupancy": ["0.5"],
        "auth_seq_id": ["257"], "auth_asym_id": ["A"], "pdbx_PDB_model_num": ["1"],
    })
    atom = atoms_from_block(block)[0]
    assert atom["label_chain"] == "Z" and atom["auth_chain"] == "A"
    assert atom["label_seq_id"] == 5 and atom["auth_seq_id"] == "257"
    assert atom["insertion_code"] == "A" and atom["altloc"] == "B"
    assert atom["occupancy"] == 0.5
    assert distance(atom, atom) == 0


def test_computational_function_claim_rejected(bundle):
    observation = {k: bundle["sites"][0][k] for k in (
        "protein_id", "sequence_sha256", "review_status", "limitations", "evidence")}
    observation.update({"assertion_id": "test:activity", "evidence_origin": "COMPUTED_COMPARISON",
                        "activity": "transport", "substrate": "taurocholate", "outcome": "DETECTED",
                        "assay": "none", "conditions": "none", "construct": "reference",
                        "expression_localization_controls": "none", "source_locator": "none"})
    bundle["functional_observations"] = [observation]
    assert any("experimental assay" in e for e in validate_bundle(bundle))


@pytest.fixture
def mechanism_bundle(bundle):
    bundle["mechanisms"] = [{
        "mechanism_id": "test:mechanism", "review_status": "PROPOSED",
        "trait_ref": "Pfam:PF01758", "protein_ids": ["UniProtKB:Q14973"],
        "assertion_refs": ["test:site"], "limitations": "Synthetic, not biological evidence.",
        "residue_bindings": [{"node_id": "residue", "protein_id": "UniProtKB:Q14973",
                              "sequence_sha256": bundle["protein_references"][0]["sequence_sha256"],
                              "position": 2, "residue": "C"}],
        "graph": {"graph_id": "test_graph", "title": "Synthetic graph",
                  "nodes": [{"node_id": "residue", "label": "synthetic C2", "node_type": "RESIDUE",
                             "local": True, "description": "Synthetic residue, exact binding supplied."},
                            {"node_id": "sodium", "label": "sodium", "node_type": "LIGAND",
                             "grounding": "CHEBI:29101"}],
                  "edges": [{"subject": "residue", "object": "sodium", "predicate": "physically interacts with",
                             "predicate_id": "RO:0002436", "evidence": [{
                                 "reference": "https://example.org/synthetic",
                                 "snippet": "Synthetic test fixture, not a biological claim."}]}]}}]
    return bundle


def test_typed_mechanism_graph_validates(mechanism_bundle):
    assert validate_bundle(mechanism_bundle) == []


@pytest.mark.parametrize("mutation,expected", [
    (lambda m: m.update(residue_bindings=[]), "sequence bindings"),
    (lambda m: m["residue_bindings"][0].update(position=99), "scoped sequence"),
    (lambda m: m["residue_bindings"][0].update(residue="S"), "scoped sequence"),
    (lambda m: m["residue_bindings"][0].update(sequence_sha256="f" * 64), "scoped sequence"),
    (lambda m: m["residue_bindings"][0].update(node_id="sodium"), "sequence bindings"),
    (lambda m: m["residue_bindings"].append(deepcopy(m["residue_bindings"][0])), "duplicate"),
    (lambda m: m.update(protein_ids=["UniProtKB:Q96EP9"]), "scope"),
    (lambda m: m.update(assertion_refs=["unknown"]), "resolve"),
    (lambda m: m.update(limitations=""), "limitations"),
    (lambda m: m["graph"]["edges"][0]["evidence"][0].pop("snippet"), "excerpt"),
    (lambda m: m["graph"]["edges"][0]["evidence"][0].update(reference="PMID:123"), "stable URL"),
    (lambda m: m["graph"]["edges"][0].update(object="absent"), "absent"),
])
def test_adversarial_mechanism_mutations(mechanism_bundle, mutation, expected):
    mutation(mechanism_bundle["mechanisms"][0])
    errors = validate_bundle(mechanism_bundle)
    assert errors and expected.lower() in " ".join(errors).lower()


@pytest.fixture
def model_bundle(bundle):
    from slc10_model_comparison import fit_pairs
    anchor, target = bundle["protein_references"]
    pairs = []
    for i, (x, y) in enumerate(((0, 0), (2, 0), (0, 2)), 1):
        first = atom(i, "CA", ["ALA", "CYS", "ASP"][i - 1], x, sequence_id=str(i))
        first.update(y=y, label_seq_id=i)
        second = deepcopy(first)
        second.update(x=x + 5, y=y - 2, residue_name=["ALA", "SER", "ASP"][i - 1])
        pairs.append({"anchor_position": i, "anchor_residue": anchor["sequence"][i - 1],
                      "target_position": i, "target_residue": target["sequence"][i - 1],
                      "status": "CHANGED" if i == 2 else "IDENTICAL", "mapping_note": "Synthetic",
                      "anchor_ca": first, "target_ca": second, "target_plddt": 90,
                      "used_in_fit": True, "geometry_note": "Synthetic"})
    fit = fit_pairs(pairs, minimum=3)
    bundle["model_comparisons"] = [{
        "assertion_id": "test:model", "protein_id": target["protein_id"],
        "sequence_sha256": target["sequence_sha256"], "evidence_origin": "COMPUTED_COMPARISON",
        "review_status": "PROPOSED", "evidence": [{"reference": "https://example.org/model"}],
        "limitations": "Synthetic; no biology.", "anchor_protein_id": anchor["protein_id"],
        "anchor_structure_source": "7ZYI.cif", "mapping_source": "7zyi.xml.gz", "model_source": "7ZYI.cif",
        "method": "Synthetic rigid transform", "confidence_threshold": 70, "pairs": pairs, **fit}]
    return bundle


def test_predicted_model_rigid_transform_validates(model_bundle):
    assert validate_bundle(model_bundle) == []
    model = model_bundle["model_comparisons"][0]
    assert model["fit_rmsd_angstrom"] < 1e-10
    assert model["translation"] == pytest.approx([-5, 2, 0])


@pytest.mark.parametrize("mutation,expected", [
    (lambda m: m.update(evidence_origin="EXPERIMENTAL_ASSAY"), "COMPUTED_COMPARISON"),
    (lambda m: m.update(model_source="missing"), "source"),
    (lambda m: m.update(anchor_protein_id="missing"), "anchor protein"),
    (lambda m: m.update(rotation=[1] * 9), "rigid transform"),
    (lambda m: m.update(rotation=[]), "complete transform"),
    (lambda m: m.update(translation=[0, 0, 0]), "displacement"),
    (lambda m: m.update(fit_rmsd_angstrom=3), "RMSD"),
    (lambda m: m.update(fit_residue_count=50), "count"),
    (lambda m: m["pairs"][0].update(status="UNRESOLVED"), "unresolved"),
    (lambda m: m["pairs"][0].update(target_position=9), "target residue"),
    (lambda m: m["pairs"][0].update(target_plddt=60), "confidence"),
    (lambda m: m["pairs"][0]["target_ca"].update(label_seq_id=3), "numbering"),
    (lambda m: m["pairs"][0]["target_ca"].update(atom_name="CB"), "CA identity"),
    (lambda m: m["pairs"][0].update(ca_displacement_angstrom=5), "displacement"),
    (lambda m: m.update(predicted_ligand="NA"), "predicted_ligand"),
])
def test_model_interpretation_boundary(model_bundle, mutation, expected):
    mutation(model_bundle["model_comparisons"][0])
    errors = validate_bundle(model_bundle)
    assert errors and expected.lower() in " ".join(errors).lower()


def test_insufficient_model_pairs_no_transform(model_bundle):
    from slc10_model_comparison import fit_pairs
    model = model_bundle["model_comparisons"][0]
    assert fit_pairs(model["pairs"], minimum=20) == {
        "fit_residue_count": 3, "minimum_fit_pairs": 20, "fit_status": "INSUFFICIENT_PAIRS"}


def test_self_consistent_but_nonoptimal_model_fit_is_rejected(model_bundle):
    import numpy as np
    from slc10_model_comparison import coords
    model = model_bundle["model_comparisons"][0]
    # A translation error can be hidden by rewriting every residual and RMSD.
    model["translation"][0] += 10
    rotation = np.array(model["rotation"]).reshape(3, 3)
    for pair in model["pairs"]:
        pair["ca_displacement_angstrom"] = float(np.linalg.norm(
            np.array(coords(pair["target_ca"])) @ rotation + model["translation"] - coords(pair["anchor_ca"])))
    model["fit_rmsd_angstrom"] = float(np.sqrt(np.mean([
        p["ca_displacement_angstrom"] ** 2 for p in model["pairs"] if p["used_in_fit"]])))
    assert any("least-squares" in error for error in validate_bundle(model_bundle))


def test_collinear_model_fit_is_rejected(model_bundle):
    model = model_bundle["model_comparisons"][0]
    model["pairs"][2]["anchor_ca"].update(x=4, y=0)
    model["pairs"][2]["target_ca"].update(x=9, y=-2)
    for pair in model["pairs"]:
        pair["ca_displacement_angstrom"] = 0
    model["fit_rmsd_angstrom"] = 0
    assert any("degenerate" in error for error in validate_bundle(model_bundle))


def test_cutoff_summary_is_recomputed_not_trusted(bundle):
    site = bundle["sites"][0]
    site["cutoff_sensitivity"] = [{"cutoff_angstrom": 2.5, "atom_pair_count": 1,
                                   "residue_positions": [2], "sidechain_heteroatom_positions": []}]
    assert validate_bundle(bundle) == []
    site["cutoff_sensitivity"][0]["sidechain_heteroatom_positions"] = [2]
    assert any("threshold summary disagrees" in e for e in validate_bundle(bundle))


def test_missing_selected_ligand_component_fails_closed(bundle, monkeypatch, tmp_path):
    from types import SimpleNamespace
    import molecular_evidence as module
    protein = bundle["protein_references"][0]
    first, ion = deepcopy(bundle["sites"][0]["contacts"][0]["protein_atom"]), deepcopy(bundle["sites"][0]["contacts"][0]["ligand_atom"])
    first["label_seq_id"] = 2
    # Valid synthetic protein mapping and one NA, but the expected CHO is absent.
    monkeypatch.setattr(module.gemmi.cif, "read_file", lambda path: SimpleNamespace(sole_block=lambda: SimpleNamespace(name="7ZYI")))
    monkeypatch.setattr(module, "load_sifts_xml", lambda path: SimpleNamespace(pdb_id="7ZYI", uniprot_release=protein["uniprot_release"]))
    monkeypatch.setattr(module, "source_residue_map", lambda *a: {("2", ""): (2, "C")})
    monkeypatch.setattr(module, "atoms_from_block", lambda block: [first, ion])
    with pytest.raises(ValueError, match="expected ligand"):
        module.extract_sites(tmp_path, "7ZYI", protein)
