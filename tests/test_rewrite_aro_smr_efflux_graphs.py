from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_smr_efflux_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_smr_efflux_graphs", SCRIPT)
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


def _record(identifier: str = "ARO:3000768", with_drug: bool = False) -> dict:
    graph = {
        "graph_id": "resistance",
        "nodes": [
            _node("determinant", "PROTEIN", identifier),
            _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
            _node("antiport", "MOLECULAR_FUNCTION", "GO:0015297"),
            _node("resistance", "PHENOTYPE", "GO:0046677"),
        ],
        "edges": [],
    }
    if with_drug:
        graph["nodes"].append(_node("drug0", "CHEMICAL", "ARO:3005386"))
        graph["edges"].append(
            {
                "subject": "determinant",
                "predicate": "confers resistance to (drug class)",
                "predicate_id": "ARO:2000001",
                "object": "drug0",
                "description": "CARD asserts that this determinant confers resistance.",
                "evidence": [
                    {
                        "reference": identifier,
                        "snippet": (
                            "relationship: confers_resistance_to_drug_class "
                            "ARO:3005386 ! disinfecting agents and antiseptics"
                        ),
                        "notes": "Direct CARD drug-class assertion.",
                    }
                ],
            }
        )
    return {
        "identifier": identifier,
        "label": "test SMR",
        "definition": "test SMR definition",
        "causal_graphs": [graph],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_targets_are_exact_current_low_scoring_smr_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:0010003",
        "ARO:3000264",
        "ARO:3000768",
        "ARO:3003062",
        "ARO:3003836",
        "ARO:3004038",
        "ARO:3004039",
        "ARO:3004585",
        "ARO:3005098",
        "ARO:3007012",
        "ARO:3007014",
        "ARO:3007015",
    }


def test_rewrite_links_smr_antiport_to_export_and_resistance() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[2])

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "antiport"),
        ("antiport", "export"),
        ("export", "extruded_drug"),
        ("extruded_drug", "resistance"),
    }


def test_rewrite_preserves_direct_drug_class_assertions() -> None:
    out, changed = R.enrich_record(_record(with_drug=True), R.TARGETS[2])

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("determinant", "antiport"),
        ("antiport", "drug0"),
        ("antiport", "export"),
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
    once, changed = R.enrich_record(_record(), R.TARGETS[2])
    twice, changed_again = R.enrich_record(once, R.TARGETS[2])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS[2].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000768, found ARO:3000264"):
        R.enrich_record(_record("ARO:3000264"), R.TARGETS[2])


def test_drug_node_without_direct_drug_edge_is_refused() -> None:
    record = _record(with_drug=True)
    record["causal_graphs"][0]["edges"] = []

    with pytest.raises(ValueError, match=r"missing determinant→drug edge\(s\): drug0"):
        R.enrich_record(record, R.TARGETS[2])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
