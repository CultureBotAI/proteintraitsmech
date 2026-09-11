from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_msha_activation_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_msha_activation_graphs", SCRIPT)
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
        "evidence": [{"reference": "ARO:3004900", "snippet": "activation"}],
    }


def _record(identifier: str = "ARO:3004901") -> dict:
    return {
        "identifier": identifier,
        "label": "isoniazid resistant mshA",
        "definition": "Resistance has been shown in the gene to isoniazid.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0"},
                    {"node_id": "drug0", "grounding": "ARO:3007152"},
                    {"node_id": "activation"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    _edge("determinant", "RO:0000056", "mech0"),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0002411", "resistance"),
                    _edge("determinant", "ARO:2000001", "drug0"),
                    _edge("determinant", "RO:0002212", "activation"),
                ],
            }
        ],
    }


def test_targets_are_exact_current_drug_specific_msha_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004901",
        "ARO:3005107",
        "ARO:3004925",
        "ARO:3005108",
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_thioamide_record_uses_thioamide_drug_class() -> None:
    record = _record("ARO:3005107")
    record["causal_graphs"][0]["nodes"][2]["grounding"] = "ARO:3007156"

    out, changed = R.enrich_record(record, R.TARGETS[1])

    assert changed
    assert any(
        item["reference"] == "ARO:3007156"
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    )


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
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004901, found ARO:3005107"):
        R.enrich_record(_record("ARO:3005107"), R.TARGETS[0])


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="unexpected edge set"):
        R.enrich_record(record, R.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        for edge in out["causal_graphs"][0]["edges"]:
            assert edge.get("description")
            assert len({item["reference"] for item in edge["evidence"]}) > 1
