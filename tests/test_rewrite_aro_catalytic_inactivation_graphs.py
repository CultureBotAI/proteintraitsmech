from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_catalytic_inactivation_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_catalytic_inactivation_graphs",
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


def _record(identifier: str = "ARO:3000121", catalytic_node_id: str = "domain") -> dict:
    return {
        "identifier": identifier,
        "label": "test label",
        "definition": "test definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:specific"),
                    _node(catalytic_node_id, "DOMAIN", "Pfam:test"),
                    _node("fold", "DOMAIN", "CATH:test"),
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


def test_targets_are_exact_catalytic_parent_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3005459",
        "ARO:3000121",
        "ARO:3000218",
        "ARO:3000114",
        "ARO:3000078",
        "ARO:3000096",
        "ARO:3000004",
        "ARO:3000568",
        "ARO:3000570",
        "ARO:3000571",
        "ARO:3000076",
    }


def test_aminoglycoside_graph_keeps_domain_and_specific_mechanism() -> None:
    target = R.TARGET_BY_ID["ARO:3000121"]
    out, changed = R.enrich_record(_record("ARO:3000121"), target)
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["domain"]["grounding"] == "InterPro:IPR000182"
    assert by_node["mech1"]["grounding"] == "ARO:3000106"


def test_serine_beta_lactamase_graph_keeps_active_site() -> None:
    target = R.TARGET_BY_ID["ARO:3000078"]
    out, changed = R.enrich_record(_record("ARO:3000078", "active_site"), target)
    nodes = _node_ids(out)
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert "active_site" in nodes
    assert "domain" not in nodes
    assert by_node["active_site"]["grounding"] == "PROSITE:PS00146"


def test_metallo_beta_lactamase_graph_keeps_mbl_domain() -> None:
    target = R.TARGET_BY_ID["ARO:3000004"]
    out, changed = R.enrich_record(_record("ARO:3000004"), target)
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    assert changed
    assert by_node["domain"]["grounding"] == "Pfam:PF00753"
    assert by_node["mech1"]["grounding"] == "ARO:3000203"


def test_every_graph_has_expected_eight_edges() -> None:
    for target in R.TARGETS:
        catalytic_node_id = target.catalytic_node_id
        out, changed = R.enrich_record(
            _record(target.identifier, catalytic_node_id),
            target,
        )

        assert changed
        assert _edge_pairs(out) == {
            ("determinant", "mech0"),
            ("mech0", "resistance"),
            ("determinant", "mech1"),
            ("mech1", "resistance"),
            ("determinant", "resistance"),
            (catalytic_node_id, "determinant"),
            ("determinant", "fold"),
            (catalytic_node_id, "mech1"),
        }


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    for target in R.TARGETS:
        out, changed = R.enrich_record(
            _record(target.identifier, target.catalytic_node_id),
            target,
        )
        graph = out["causal_graphs"][0]

        assert changed
        assert all(node.get("grounding") for node in graph["nodes"])
        for edge in graph["edges"]:
            references = {item["reference"] for item in edge["evidence"]}
            assert edge["description"]
            assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3000121"]

    once, changed = R.enrich_record(_record("ARO:3000121"), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000121, found ARO:3000114"):
        R.enrich_record(_record("ARO:3000114"), R.TARGET_BY_ID["ARO:3000121"])


def test_missing_required_node_is_refused() -> None:
    record = _record("ARO:3000121")
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "domain"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): domain"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000121"])


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record("ARO:3000121"), sort_keys=False)
    path = ARO_DIR / R.TARGET_BY_ID["ARO:3000121"].filename

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
