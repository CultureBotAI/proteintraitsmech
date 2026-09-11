from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_triclosan_gyra_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_triclosan_gyra_graphs", SCRIPT)
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
        "evidence": [
            {
                "reference": "ARO:3000479",
                "snippet": "aminocoumarin-only snippet",
            }
        ],
    }


def _record(identifier: str = "ARO:3004333") -> dict:
    return {
        "identifier": identifier,
        "label": "triclosan resistant gyrA",
        "definition": (
            "Point mutations in gyrA have been shown to decrease susceptibility "
            "to triclosan through an indirect pathway."
        ),
        "evidence": [{"reference": "DOI:10.1093/jac/dkx201", "notes": "PMID:29091182"}],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0"},
                    {"node_id": "drug0"},
                    {"node_id": "binding_loss"},
                    {"node_id": "dna_synth"},
                    {"node_id": "resistance"},
                ],
                "edges": [_edge(*key) for key in R.EXPECTED_EDGE_KEYS],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_targets_are_exact_current_score83_triclosan_gyra_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004333",
        "ARO:3004335",
        "ARO:3004334",
    }


def test_enrich_record_prunes_to_mutation_and_drug_core() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert _edge_keys(out) == set(R.CORE_EDGE_ORDER)
    assert {node["node_id"] for node in out["causal_graphs"][0]["nodes"]} == {
        "determinant",
        "mech0",
        "drug0",
        "resistance",
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, _ = R.enrich_record(_record(), R.TARGETS[0])

    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert not any(item["reference"] == "ARO:3000479" for item in edge["evidence"])


def test_child_edges_include_child_definition() -> None:
    child = _record("ARO:3004335")

    out, changed = R.enrich_record(child, R.TARGETS[1])

    assert changed
    assert any(
        item["reference"] == "ARO:3004335"
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
    with pytest.raises(ValueError, match="expected ARO:3004333, found ARO:3004335"):
        R.enrich_record(_record("ARO:3004335"), R.TARGETS[0])


def test_unexpected_edge_set_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="unexpected triclosan gyrA edge set"):
        R.enrich_record(record, R.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert _edge_keys(out) == set(R.CORE_EDGE_ORDER)
