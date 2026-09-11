from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_absence_parent_graph.py"
TARGET = (
    REPO
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "gene-conferring-resistance-via-absence-aro3003768.yaml"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_absence_parent_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record(identifier: str = "ARO:3003768") -> dict:
    return {
        "identifier": identifier,
        "label": "gene conferring resistance via absence",
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0"},
                    {"node_id": "absence"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    {
                        "subject": subject,
                        "predicate": "seeded predicate",
                        "predicate_id": predicate_id,
                        "object": object_,
                        "evidence": [{"reference": "ARO:3003764"}],
                    }
                    for subject, predicate_id, object_ in R.EDGE_ORDER
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_enrich_record_completes_existing_five_edge_graph() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _edge_keys(out) == R.EDGE_KEYS
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert {item["reference"] for item in edge["evidence"]} == {
            "ARO:3003764",
            "ARO:3003768",
        }


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text)
    twice, changed_again = R.enrich_text(once)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003768, found ARO:3003764"):
        R.enrich_record(_record("ARO:3003764"))


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:2]

    with pytest.raises(ValueError, match="unexpected edge set"):
        R.enrich_record(record)


@pytest.mark.skipif(not TARGET.is_file(), reason="ARO:3003768 record absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    record = yaml.safe_load(TARGET.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert _edge_keys(out) == R.EDGE_KEYS
