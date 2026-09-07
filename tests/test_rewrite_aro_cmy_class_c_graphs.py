from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cmy_class_c_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cmy_class_c_graphs",
        SCRIPT,
    )
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


def _record(identifier: str = "ARO:3000085") -> dict:
    return {
        "identifier": identifier,
        "label": "test CMY family",
        "definition": "A test class C beta-lactamase grouping.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000187"),
                    _node("active_site", "MOTIF", "PROSITE:PRU10102"),
                    _node("fold", "DOMAIN", "CATH:3.40.710.10"),
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


def test_targets_are_exact_cmy_lat_mox_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3000085",
        "ARO:3000086",
        "ARO:3000087",
    }


def test_enrich_record_keeps_class_c_active_site_and_fold() -> None:
    target = R.TARGET_BY_ID["ARO:3000085"]

    out, changed = R.enrich_record(_record(), target)
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["active_site"]["grounding"] == "PROSITE:PRU10102"
    assert by_node["fold"]["grounding"] == "CATH:3.40.710.10"


def test_every_graph_has_expected_eight_edges() -> None:
    target = R.TARGET_BY_ID["ARO:3000085"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "mech1"),
        ("mech1", "resistance"),
        ("determinant", "resistance"),
        ("active_site", "determinant"),
        ("determinant", "fold"),
        ("active_site", "mech1"),
    }


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(_record(target.identifier), target)
        graph = out["causal_graphs"][0]

        assert changed
        assert all(node.get("grounding") for node in graph["nodes"])
        for edge in graph["edges"]:
            references = {item["reference"] for item in edge["evidence"]}
            assert edge["description"]
            assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3000085"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000085, found ARO:3000086"):
        R.enrich_record(_record("ARO:3000086"), R.TARGET_BY_ID["ARO:3000085"])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "fold"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): fold"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000085"])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3000085"), sort_keys=False)
    path = ARO_DIR / R.TARGET_BY_ID["ARO:3000085"].filename

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
