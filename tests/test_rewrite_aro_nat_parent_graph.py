from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_nat_parent_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_nat_parent_graph",
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
        "evidence": [{"reference": "ARO:3004909"}],
    }


def _record(identifier: str = "ARO:3004909") -> dict:
    return {
        "identifier": identifier,
        "label": "Antibiotic resistant nat",
        "definition": (
            "Mutations that occur in nat inactivate antibiotic functioning and "
            "contribute to antibiotic resistance."
        ),
        "mapping_status": "SEEDED",
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


def test_targets_are_exact_nat_parent() -> None:
    assert {target.identifier for target in R.TARGETS} == {"ARO:3004909"}


def test_enrich_record_completes_generic_mutation_graph() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET)

    graph = out["causal_graphs"][0]
    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert graph["graph_id"] == "resistance"
    assert _edge_keys(out) == R.EDGE_KEYS
    assert [node["node_id"] for node in graph["nodes"]] == [
        "determinant",
        "mech0",
        "resistance",
    ]
    assert all(edge.get("description") for edge in graph["edges"])
    assert all(
        {item["reference"] for item in edge["evidence"]} == {"ARO:3004909", "ARO:3000212"}
        for edge in graph["edges"]
    )
    assert all(node["node_id"] != "overexpression" for node in graph["nodes"])
    assert all(
        "overexpression" not in edge["predicate"].lower()
        and edge["object"] != "overexpression"
        for edge in graph["edges"]
    )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGET)
    twice, changed_again = R.enrich_record(once, R.TARGET)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET.filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004909, found ARO:3004930"):
        R.enrich_record(_record("ARO:3004930"), R.TARGET)


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:2]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGET)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    path = ARO_DIR / R.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record), R.TARGET)

    assert changed or out == record
    assert _edge_keys(out) == R.EDGE_KEYS
