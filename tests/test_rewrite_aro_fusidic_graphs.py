from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fusidic_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fusidic_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _record(identifier: str = "ARO:3003025") -> dict:
    return {
        "identifier": identifier,
        "label": "test fusidic acid inactivation enzyme",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3004140"),
                    _node("drug0", "CHEMICAL", "ARO:3007153"),
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


def test_targets_are_exact_fusidic_acid_records() -> None:
    assert {target.identifier for target in F.TARGETS} == {
        "ARO:3003025",
        "ARO:3003026",
    }


def test_rewrite_links_lactone_derivative_to_resistance() -> None:
    target = F.TARGET_BY_ID["ARO:3003025"]

    out, changed = F.enrich_record(_record(), target)
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "mech1"),
        ("mech1", "resistance"),
        ("determinant", "drug0"),
        ("mech1", "drug0"),
        ("mech1", "modified"),
        ("modified", "resistance"),
        ("determinant", "resistance"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["mech1"] == F.LACTONIZATION_NODE
    assert by_node["modified"] == F.MODIFIED_NODE
    assert "transfer" not in by_node


def test_fush_gets_specific_published_evidence() -> None:
    target = F.TARGET_BY_ID["ARO:3003026"]

    out, changed = F.enrich_record(_record("ARO:3003026"), target)

    assert changed
    assert any(
        evidence["reference"] == "DOI:10.1099/00221287-143-3-867"
        for edge in out["causal_graphs"][0]["edges"]
        for evidence in edge["evidence"]
    )


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in F.TARGETS:
        out, changed = F.enrich_record(_record(target.identifier), target)
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
    target = F.TARGET_BY_ID["ARO:3003025"]

    once, changed = F.enrich_record(_record(), target)
    twice, changed_again = F.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    target = F.TARGET_BY_ID["ARO:3003025"]
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / target.filename

    once, changed = F.enrich_text(text, path)
    twice, changed_again = F.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(F.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    target = F.TARGET_BY_ID["ARO:3003025"]

    with pytest.raises(ValueError, match="expected ARO:3003025, found ARO:3003026"):
        F.enrich_record(_record("ARO:3003026"), target)


def test_missing_required_node_is_refused() -> None:
    target = F.TARGET_BY_ID["ARO:3003025"]
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "mech1"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): mech1"):
        F.enrich_record(record, target)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in F.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = F.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
