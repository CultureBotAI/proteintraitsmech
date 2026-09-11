from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_aminocoumarin_topoisomerase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_aminocoumarin_topoisomerase_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(
    subject: str,
    predicate_id: str,
    object_: str,
    reference: str = "ARO:3000370",
) -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": reference,
                "snippet": "Resistant DNA topoisomerase subunits prevent antibiotic binding.",
            }
        ],
    }


def _record(identifier: str = "ARO:3000479") -> dict:
    return {
        "identifier": identifier,
        "label": "aminocoumarin resistant gyrB",
        "evidence": [{"reference": "DOI:10.1128/test", "notes": "PMID:test"}],
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
                "edges": [
                    _edge("determinant", "RO:0000056", "mech0"),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0002411", "resistance"),
                    _edge("determinant", "ARO:2000001", "drug0", "ARO:3000479"),
                    _edge("determinant", "RO:0000086", "binding_loss"),
                    _edge("drug0", "RO:0002212", "dna_synth"),
                    _edge("binding_loss", "RO:0002411", "dna_synth"),
                ],
            }
        ],
    }


def test_targets_match_exact_current_score83_aminocoumarin_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3000479",
        "ARO:3000457",
        "ARO:3000480",
        "ARO:3003302",
        "ARO:3003303",
        "ARO:3003301",
        "ARO:3003314",
        "ARO:3003318",
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])
        assert any(item["reference"] == "DOI:10.1128/test" for item in edge["evidence"])


def test_enrich_record_keeps_edge_order_stable() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = list(reversed(record["causal_graphs"][0]["edges"]))

    out, changed = R.enrich_record(record, R.TARGETS[0])

    assert changed
    assert [
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in out["causal_graphs"][0]["edges"]
    ] == list(R.EDGE_ORDER)


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
    with pytest.raises(ValueError, match="expected ARO:3000479, found ARO:3000457"):
        R.enrich_record(_record("ARO:3000457"), R.TARGETS[0])


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGETS[0])


def test_record_without_source_evidence_is_refused() -> None:
    record = _record()
    record["evidence"] = []

    with pytest.raises(ValueError, match="missing record-level DOI evidence"):
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
