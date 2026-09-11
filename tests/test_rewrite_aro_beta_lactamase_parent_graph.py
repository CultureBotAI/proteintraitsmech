from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_beta_lactamase_parent_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_beta_lactamase_parent_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, predicate_id: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [{"reference": "ARO:3000001", "snippet": "seed"}],
    }


def _record(identifier: str = "ARO:3000001") -> dict:
    return {
        "identifier": identifier,
        "label": "beta-lactamase",
        "mapping_status": "SEEDED",
        "evidence": [
            {"reference": "DOI:10.1098/rstb.1980.0049", "notes": "PMID:6109327"}
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    _edge("determinant", "RO:0000056", "mech0"),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0002411", "resistance"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_enrich_record_rewrites_parent_to_ring_opening_path() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _edge_keys(out) == set(R.EDGE_ORDER)
    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert by_node["ring_opening"]["local"] is True
    assert by_node["inactive"]["local"] is True


def test_enrich_record_adds_multi_reference_evidence_to_every_edge() -> None:
    out, _ = R.enrich_record(_record())

    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET_FILE

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000001, found ARO:3000002"):
        R.enrich_record(_record("ARO:3000002"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("determinant", "RO:0002327", "unexpected")
    )

    with pytest.raises(ValueError, match="unexpected edge set"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    path = ARO_DIR / R.TARGET_FILE
    record = yaml.safe_load(path.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert _edge_keys(out) == set(R.EDGE_ORDER)
