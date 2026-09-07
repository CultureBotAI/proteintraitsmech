from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mate_efflux_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_mate_efflux_graphs", SCRIPT)
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


def _record(identifier: str = "ARO:3000112") -> dict:
    return {
        "identifier": identifier,
        "label": "test label",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
                    _node("extrusion", "MOLECULAR_FUNCTION"),
                    _node("cation_gradient", "STATE"),
                    _node("extruded", "STATE"),
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


def _node_ids(record: dict) -> set[str]:
    return {
        node["node_id"]
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_targets_are_exact_current_mate_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3000112",
        "ARO:3003551",
        "ARO:3003953",
        "ARO:3003965",
    }


def test_mate_graph_replaces_ungrounded_extrusion_function() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])
    nodes = _node_ids(out)

    assert changed
    assert "extrusion" not in nodes
    assert "export" in nodes
    assert "extruded_drug" in nodes
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("cation_gradient", "export"),
        ("determinant", "export"),
        ("export", "extruded_drug"),
        ("extruded_drug", "resistance"),
    }


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(_record(target.identifier), target)
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
    once, changed = R.enrich_record(_record(), R.TARGETS[0])
    twice, changed_again = R.enrich_record(once, R.TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000112, found ARO:3003551"):
        R.enrich_record(_record("ARO:3003551"), R.TARGETS[0])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "extrusion"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): extrusion"):
        R.enrich_record(record, R.TARGETS[0])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS[0].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
