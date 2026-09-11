from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ngon_pilq_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_ngon_pilq_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


P = _load()


def _record(identifier: str = "ARO:3004835") -> dict:
    return {
        "identifier": identifier,
        "label": "Neisseria gonorrhoeae pilQ gene conferring resistance to beta-lactam",
        "definition": (
            "PilQ is an important gonococcal outer membrane component, member of "
            "secretin protein family, and involved in Type IV pilus formation."
        ),
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
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
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


def test_enrich_record_models_secretin_stability_not_pbp_affinity() -> None:
    enriched, changed = P.enrich_record(_record())

    assert changed
    assert enriched["mapping_status"] == "REVIEWED"
    graph = enriched["causal_graphs"][0]
    assert graph["graph_id"] == "resistance"
    assert "penicillin-binding-protein target mutation" in graph["description"]

    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["determinant"]["grounding"] == "ARO:3004835"
    assert by_node["mech0"]["grounding"] == "ARO:3000212"
    assert by_node["secretin"]["node_type"] == "STATE"
    assert by_node["influx"]["grounding"] == "GO:0042908"
    assert by_node["drug0"]["grounding"] == "ARO:0000032"
    assert by_node["drug1"]["grounding"] == "ARO:3000008"

    assert _edge_keys(graph) == {
        ("determinant", "RO:0000056", "mech0"),
        ("determinant", "RO:0002411", "secretin"),
        ("secretin", "RO:0002411", "influx"),
        ("influx", "RO:0002411", "resistance"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "ARO:2000001", "drug1"),
    }

    influx_edge = next(edge for edge in graph["edges"] if edge["object"] == "influx")
    assert any("enhances antibiotic entry" in e["snippet"] for e in influx_edge["evidence"])

    for edge in graph["edges"]:
        assert edge["description"]
        assert len({evidence["reference"] for evidence in edge["evidence"]}) > 1
        assert all(evidence["snippet"] for evidence in edge["evidence"])


def test_enrich_text_is_idempotent() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    out, changed = P.enrich_text(text)
    again, changed_again = P.enrich_text(out)

    assert changed
    assert not changed_again
    assert again == out
    assert "mapping_status: REVIEWED" in out
    assert "Curated Neisseria gonorrhoeae pilQ beta-lactam influx graph" in out


def test_rejects_wrong_identifier() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004835"):
        P.enrich_record(_record("ARO:3004836"))
