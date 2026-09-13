from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_host_nutrient_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_host_nutrient_graphs", SCRIPT)
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


def _record(identifier: str = "ARO:3007425", *, with_drug: bool = False) -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:3007424"),
    ]
    if with_drug:
        nodes.append(_node("drug0", "CHEMICAL", "ARO:3000282"))
    nodes.extend(
        [
            _node("uptake", "MOLECULAR_FUNCTION"),
            _node("bypassed", "STATE"),
            _node("resistance", "PHENOTYPE", "GO:0046677"),
        ]
    )

    return {
        "identifier": identifier,
        "label": "test host nutrient uptake determinant",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": [],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_targets_are_exact_current_host_nutrient_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3007425",
        "ARO:3007426",
        "ARO:3007427",
    }


def test_generic_rewrite_links_host_nutrient_uptake_to_resistance() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "uptake"),
        ("determinant", "uptake"),
        ("uptake", "bypassed"),
        ("bypassed", "resistance"),
        ("determinant", "resistance"),
    }


def test_sulfonamide_targets_keep_drug_class_edge() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3007426", with_drug=True),
        R.TARGET_BY_ID["ARO:3007426"],
    )

    assert changed
    assert ("determinant", "drug0") in _edge_pairs(out)
    assert any(node["node_id"] == "drug0" for node in out["causal_graphs"][0]["nodes"])


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(
            _record(target.identifier, with_drug=target.has_sulfonamide_relation),
            target,
        )
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
    once, changed = R.enrich_record(_record(), R.TARGETS[0])
    twice, changed_again = R.enrich_record(once, R.TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


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


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007425, found ARO:3007426"):
        R.enrich_record(_record("ARO:3007426"), R.TARGETS[0])


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "bypassed"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): bypassed"):
        R.enrich_record(record, R.TARGETS[0])


def test_missing_drug_node_is_refused_for_sulfonamide_target() -> None:
    with pytest.raises(ValueError, match="missing node\\(s\\): drug0"):
        R.enrich_record(_record("ARO:3007426"), R.TARGET_BY_ID["ARO:3007426"])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
