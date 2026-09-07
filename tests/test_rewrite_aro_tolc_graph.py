from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_tolc_graph.py"
ARO_PATH = REPO / "data" / "traits" / "function" / "resistance" / "aro" / "tolc-aro3000237.yaml"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_tolc_graph", SCRIPT)
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


def _record(identifier: str = "ARO:3000237") -> dict:
    return {
        "identifier": identifier,
        "label": "TolC",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
                    _node("transporter", "STATE"),
                    _node("export", "BIOLOGICAL_PROCESS", "GO:1990961"),
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


def test_rewrite_links_tolc_to_tripartite_export_complex() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "transporter"),
        ("transporter", "export"),
        ("export", "resistance"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["transporter"] == R.PUMP_NODE
    assert "MFS" not in graph["description"]


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
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
    with pytest.raises(ValueError, match="expected ARO:3000237, found ARO:3003063"):
        R.enrich_record(_record("ARO:3003063"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "transporter"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): transporter"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_PATH.is_file(), reason="TolC record absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    record = yaml.safe_load(ARO_PATH.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
