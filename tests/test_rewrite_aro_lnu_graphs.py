from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_lnu_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_lnu_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


LNU = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _record(identifier: str = "ARO:3000221") -> dict:
    return {
        "identifier": identifier,
        "label": "test LNU",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000107"),
                    _node("drug0", "CHEMICAL", "ARO:0000017"),
                    _node("transfer", "MOLECULAR_FUNCTION"),
                    _node("modified", "STATE"),
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


def test_targets_are_exact_current_lnu_records() -> None:
    assert {target.identifier for target in LNU.TARGETS} == {
        "ARO:3000221",
        "ARO:3002879",
        "ARO:3002835",
        "ARO:3002836",
        "ARO:3002837",
        "ARO:3002838",
        "ARO:3003762",
        "ARO:3002839",
        "ARO:3004085",
        "ARO:3004600",
        "ARO:3004601",
    }


def test_lin_abc_f_record_is_not_rewritten_as_lnu() -> None:
    assert "ARO:3004651" not in LNU.TARGET_BY_ID


def test_rewrite_links_modified_lincosamide_to_resistance() -> None:
    out, changed = LNU.enrich_record(_record(), LNU.TARGETS[0])
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "mech1"),
        ("mech1", "resistance"),
        ("determinant", "transfer"),
        ("transfer", "atp"),
        ("transfer", "drug0"),
        ("transfer", "modified"),
        ("modified", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["transfer"] == LNU.TRANSFER_NODE
    assert by_node["atp"] == LNU.ATP_NODE
    assert by_node["modified"] == LNU.MODIFIED_NODE


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in LNU.TARGETS:
        out, changed = LNU.enrich_record(_record(target.identifier), target)
        graph = out["causal_graphs"][0]

        assert changed
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
            else:
                assert node.get("description")
        for edge in graph["edges"]:
            references = {item["reference"] for item in edge["evidence"]}
            assert edge["description"]
            assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = LNU.enrich_record(_record(), LNU.TARGETS[0])
    twice, changed_again = LNU.enrich_record(once, LNU.TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / LNU.TARGETS[0].filename

    once, changed = LNU.enrich_text(text, path)
    twice, changed_again = LNU.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(LNU.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000221, found ARO:3002835"):
        LNU.enrich_record(_record("ARO:3002835"), LNU.TARGETS[0])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "transfer"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): transfer"):
        LNU.enrich_record(record, LNU.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in LNU.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = LNU.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
