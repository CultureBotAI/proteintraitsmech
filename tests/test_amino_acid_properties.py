"""Reference chemistry must not become an inferred interaction or variant effect."""
from pathlib import Path
from copy import deepcopy
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import amino_acid_properties as chemistry
from build_amino_acid_properties import literal_table


@pytest.fixture
def catalog():
    return json.loads(chemistry.CATALOG.read_text())


def test_reviewed_catalog_and_all_twenty_residue_values(catalog):
    assert chemistry.validate_catalog(catalog) == []
    assert len(catalog["sources"]) == 22
    expected_heavy = dict(zip("ACDEFGHIKLMNPQRSTVWY", (1, 2, 4, 5, 7, 0, 6, 4, 5, 4, 4, 4, 3, 5, 7, 2, 3, 3, 10, 8)))
    expected_aromatic = {"F": 6, "H": 5, "W": 9, "Y": 6}
    for entry in catalog["amino_acids"]:
        aa = entry["one_letter"]
        props = {p["property_id"]: p for p in entry["properties"]}
        assert set(props) == set(chemistry.PROPERTY_IDS)
        assert props["SIDE_CHAIN_HEAVY_ATOM_COUNT"]["value"] == expected_heavy[aa]
        assert props["SIDE_CHAIN_AROMATIC_ATOM_COUNT"]["value"] == expected_aromatic.get(aa, 0)
        assert props["SIDE_CHAIN_HYDROXYL_COUNT"]["value"] == int(aa in "STY")
        assert props["BACKBONE_RING_CLOSURE"]["value"] == int(aa == "P")
        trait = next((chemistry.ROOT / "data/traits/sequence/ptm_ontology").glob(
            f"*-mod{entry['residue_trait_ref'].split(':')[1]}.yaml"))
        assert chemistry.digest(trait.read_bytes()) == entry["trait_record_sha256"]


@pytest.mark.parametrize("ref,alt,delta", [("S", "F", 3.6), ("R", "H", 1.3)])
def test_acceptance_property_contrasts_are_not_causal_claims(catalog, ref, alt, delta):
    before = deepcopy(catalog)
    contrast = chemistry.compare_residues(catalog, ref, alt)
    props = {p["property_id"]: p for p in contrast["differences"]}
    assert props["KYTE_DOOLITTLE_HYDROPATHY"]["delta_alternate_minus_reference"] == pytest.approx(delta)
    if ref == "S":
        assert "delta_alternate_minus_reference" not in props["SIDE_CHAIN_PKA"]
        assert props["SIDE_CHAIN_HYDROXYL_COUNT"]["delta_alternate_minus_reference"] == -1
    else:
        assert props["REFERENCE_SIDE_CHAIN_CHARGE_PH7"]["alternate"]["value"] == pytest.approx(0.08717418825458693)
    assert contrast["causal_inference"] == "NONE"
    assert len(contrast["sources"]) == 4
    assert contrast["review"]["llm_assisted"] is True
    contrast["reference"]["entry"]["label"] = "changed"
    assert catalog == before


@pytest.mark.parametrize("aa", list("UOBZJX") + ["SEP", "", "s"])
def test_nonstandard_residues_never_impute_parents(catalog, aa):
    result = chemistry.compare_residues(catalog, "S", aa)
    assert result["comparison_status"] == "UNSUPPORTED_RESIDUE"
    assert "differences" not in result


@pytest.mark.parametrize("mutation", [
    lambda c: c.pop("review"),
    lambda c: c["review"].update(content_sha256="0" * 64),
    lambda c: c["review"].update(reviewed_on="2026-02-31"),
    lambda c: c["amino_acids"].pop(),
    lambda c: c["amino_acids"].append(deepcopy(c["amino_acids"][0])),
    lambda c: c["amino_acids"][0].update(one_letter="X"),
    lambda c: c["amino_acids"][0].update(residue_chemical_ref="CHEBI:29999"),
    lambda c: c["amino_acids"][0]["bonds"][0].update(atom_1="missing"),
    lambda c: c["amino_acids"][0]["properties"][0].update(value=True),
    lambda c: c["amino_acids"][0]["properties"][0].update(value=float("nan")),
    lambda c: c["amino_acids"][0]["properties"][0].update(value=100),
    lambda c: c["amino_acids"][0]["properties"][0].update(source_id="invented"),
    lambda c: c["sources"][0].update(license="unknown"),
    lambda c: c["sources"][0].update(evidence=[]),
    lambda c: c.update(invented_field="value"),
])
def test_mutated_catalog_is_rejected(catalog, mutation):
    mutation(catalog)
    assert chemistry.validate_catalog(catalog)


@pytest.mark.parametrize("root", [None, [], "catalog", 42])
def test_wrong_root_is_rejected(root):
    assert chemistry.validate_catalog(root)


def test_parameter_parser_never_executes_downloaded_code():
    assert literal_table(b'raise RuntimeError("must not execute")\nkd={"S": -0.8}', "kd") == {"S": -0.8}
    with pytest.raises(ValueError):
        literal_table(b'kd=dict(S=-0.8)', "kd")
    with pytest.raises(ValueError):
        literal_table(b'kd={"S": True}', "kd")
    with pytest.raises(ValueError):
        literal_table(b'kd={"S": -0.8}\nkd={"S": 1}', "kd")


def chemical_graph(elements, bonds):
    atoms = [dict(atom_name=n, element=e, aromatic=False, backbone=False, leaving=False)
             for n, e in elements.items()]
    return atoms, [dict(atom_1=a, atom_2=b, bond_order=o) for a, b, o in bonds]


@pytest.mark.parametrize("nhydrogen", [2, 3])
def test_primary_amino_group_includes_neutral_and_protonated_reference(nhydrogen):
    atoms, bonds = chemical_graph({"NZ": "N", "CE": "C", **{f"HZ{i}": "H" for i in range(nhydrogen)}},
                                  [("NZ", "CE", "SING"), *[("NZ", f"HZ{i}", "SING") for i in range(nhydrogen)]])
    assert any(g["group_type"] == "PRIMARY_AMINO_GROUP" for g in chemistry.groups(atoms, bonds))


@pytest.mark.parametrize("partner_element", ["O", "N"])
def test_amide_and_guanidino_nitrogens_are_not_primary_amino_groups(partner_element):
    atoms, bonds = chemical_graph({"NX": "N", "CX": "C", "HX1": "H", "HX2": "H", "X": partner_element},
                                  [("NX", "CX", "SING"), ("NX", "HX1", "SING"),
                                   ("NX", "HX2", "SING"), ("CX", "X", "DOUB")])
    assert not any(g["group_type"].startswith("PRIMARY_AMIN") for g in chemistry.groups(atoms, bonds))
