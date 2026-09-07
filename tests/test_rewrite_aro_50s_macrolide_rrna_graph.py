from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_50s_macrolide_rrna_graph.py"
ARO_PATH = (
    REPO
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "50s-rrna-with-mutation-conferring-resistance-to-macrolide-antibiotics-aro3005001.yaml"
)


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_50s_macrolide_rrna_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _record(identifier: str = "ARO:3005001") -> dict:
    return {
        "identifier": identifier,
        "label": "50S rRNA with mutation conferring resistance to macrolide antibiotics",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "NUCLEIC_ACID", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:0000000"),
                    _node("ribosome", "CELLULAR_LOCALIZATION", "GO:0005840"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_rewrite_keeps_broad_ribosome_and_macrolide_edge() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("determinant", "ribosome"),
        ("drug0", "ribosome"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["ribosome"] == R.RIBOSOME_NODE
    assert "binding_site" not in by_node


def test_all_nodes_are_grounded_and_all_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_PATH)
    twice, changed_again = R.enrich_text(once, ARO_PATH)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3005001, found ARO:3005003"):
        R.enrich_record(_record("ARO:3005003"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "ribosome"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): ribosome"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_PATH.is_file(), reason="50S macrolide rRNA record absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    record = yaml.safe_load(ARO_PATH.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
