from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_alr_cycloserine_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_alr_cycloserine_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, object_: str, predicate_id: str) -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3004946",
                "snippet": "Can confer resistance to cycloserine.",
                "notes": "Existing promoted evidence.",
            }
        ],
    }


def _record(identifier: str = "ARO:3004946") -> dict:
    return {
        "identifier": identifier,
        "label": "test Alr",
        "definition": "Provides D-alanine and can confer resistance to cycloserine.",
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {"node_id": "determinant", "label": "test Alr"},
                    {"node_id": "mech0"},
                    {"node_id": "drug0"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    _edge("determinant", "mech0", "RO:0000056"),
                    _edge("mech0", "resistance", "RO:0002411"),
                    _edge("determinant", "resistance", "RO:0002411"),
                    _edge("determinant", "drug0", "ARO:2000001"),
                ],
            }
        ],
    }


def test_targets_are_exact_current_cycloserine_alr_records() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3004946",
        "ARO:3004947",
    }


def test_enrich_record_adds_grounded_alr_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3004946"])

    assert changed
    graph = out["causal_graphs"][0]
    assert out["mapping_status"] == "REVIEWED"
    node_groundings = {node["grounding"] for node in graph["nodes"] if "grounding" in node}
    assert {
        "GO:0008784",
        "CHEBI:16977",
        "CHEBI:15570",
        "GO:0009252",
    } <= node_groundings
    assert {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in graph["edges"]
    } == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "alr_activity"),
        ("alr_activity", "RO:0002233", "l_alanine"),
        ("alr_activity", "RO:0002234", "d_alanine"),
        ("alr_activity", "BFO:0000050", "wall_synthesis"),
        ("drug0", "RO:0002212", "alr_activity"),
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, _ = R.enrich_record(_record(), R.TARGETS["ARO:3004946"])

    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_child_edges_include_mutant_alr_pmid() -> None:
    record = _record("ARO:3004947")

    out, changed = R.enrich_record(record, R.TARGETS["ARO:3004947"])

    assert changed
    assert any(
        item["reference"] == "PMID:28971867"
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGETS["ARO:3004946"])
    twice, changed_again = R.enrich_record(once, R.TARGETS["ARO:3004946"])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS["ARO:3004946"].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004946, found ARO:3004947"):
        R.enrich_record(_record("ARO:3004947"), R.TARGETS["ARO:3004946"])


def test_missing_core_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:2]

    with pytest.raises(ValueError, match="missing core edge"):
        R.enrich_record(record, R.TARGETS["ARO:3004946"])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        graph = out["causal_graphs"][0]
        assert graph["graph_id"] == "resistance"
        for edge in graph["edges"]:
            assert edge.get("description")
            assert len({item["reference"] for item in edge["evidence"]}) > 1
