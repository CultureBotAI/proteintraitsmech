from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_eis_graphs.py"
ARO = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_eis_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


E = _load()


def _record(identifier: str = "ARO:3004961") -> dict:
    return {
        "identifier": identifier,
        "label": "antibiotic resistant eis",
        "definition": "Mutations in the eis gene that can contribute to antibiotic resistance.",
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "old",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    {
                        "subject": "determinant",
                        "predicate": "causally upstream of",
                        "predicate_id": "RO:0002411",
                        "object": "resistance",
                        "evidence": [{"reference": identifier, "snippet": "old"}],
                    }
                ],
            }
        ],
    }


def _edge_keys(graph: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"]) for edge in graph["edges"]
    }


def test_targets_are_exact_eis_records() -> None:
    assert [(target.identifier, target.filename) for target in E.TARGETS] == [
        ("ARO:3004961", "antibiotic-resistant-eis-aro3004961.yaml"),
        ("ARO:3004962", "kanamycin-resistant-eis-aro3004962.yaml"),
        (
            "ARO:3004963",
            "mycobacterium-tuberculosis-eis-mutations-confer-resistance-to-kanamycin-aro3004963.yaml",
        ),
    ]


def test_enrich_record_builds_eis_acetylation_chain() -> None:
    enriched, changed = E.enrich_record(_record(), E.TARGET_BY_ID["ARO:3004961"])

    assert changed
    assert enriched["mapping_status"] == "REVIEWED"
    graph = enriched["causal_graphs"][0]
    assert graph["graph_id"] == "resistance"
    assert graph["title"] == "antibiotic resistant eis → Eis-mediated kanamycin acetylation"

    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["determinant"]["grounding"] == "ARO:3004961"
    assert by_node["mech0"]["grounding"] == "ARO:3000212"
    assert by_node["overexpression"]["node_type"] == "STATE"
    assert by_node["acetylation"]["grounding"] == "GO:0016407"
    assert by_node["acetyl_coa"]["grounding"] == "CHEBI:15351"
    assert by_node["drug0"]["grounding"] == "ARO:0000016"
    assert by_node["acetylated"]["node_type"] == "STATE"

    assert _edge_keys(graph) == {
        ("determinant", "RO:0000056", "mech0"),
        ("determinant", "RO:0002411", "overexpression"),
        ("overexpression", "RO:0002411", "acetylation"),
        ("acetylation", "RO:0002233", "acetyl_coa"),
        ("acetylation", "RO:0002233", "drug0"),
        ("acetylation", "RO:0002411", "acetylated"),
        ("acetylated", "RO:0002411", "resistance"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }

    for edge in graph["edges"]:
        assert edge["description"]
        assert len({evidence["reference"] for evidence in edge["evidence"]}) > 1
        assert all(evidence["snippet"] for evidence in edge["evidence"])


def test_kanamycin_targets_get_direct_drug_class_edge() -> None:
    parent, _ = E.enrich_record(_record("ARO:3004961"), E.TARGET_BY_ID["ARO:3004961"])
    kanamycin_parent, _ = E.enrich_record(
        _record("ARO:3004962"), E.TARGET_BY_ID["ARO:3004962"]
    )
    mtub_child, _ = E.enrich_record(_record("ARO:3004963"), E.TARGET_BY_ID["ARO:3004963"])

    assert ("determinant", "ARO:2000001", "drug0") not in _edge_keys(
        parent["causal_graphs"][0]
    )
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(
        kanamycin_parent["causal_graphs"][0]
    )
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(
        mtub_child["causal_graphs"][0]
    )


def test_enrich_text_is_idempotent() -> None:
    target = E.TARGET_BY_ID["ARO:3004961"]
    text = yaml.safe_dump(_record(), sort_keys=False)

    out, changed = E.enrich_text(text, ARO / target.filename)
    again, changed_again = E.enrich_text(out, ARO / target.filename)

    assert changed
    assert not changed_again
    assert again == out
    assert "mapping_status: REVIEWED" in out
    assert "Curated Eis kanamycin acetylation graphs" in out


def test_rejects_wrong_file_for_identifier() -> None:
    with pytest.raises(ValueError, match="target ARO:3004961 must be in"):
        E.enrich_text(yaml.safe_dump(_record(), sort_keys=False), ARO / "wrong.yaml")
