from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_paer_gyra_parc_graph.py"
TARGET = (
    REPO
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "pseudomonas-aeruginosa-gyra-and-parc-conferring-resistance-to-fluoroquinolones-aro3003702.yaml"
)


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_paer_gyra_parc_graph", SCRIPT)
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


def _record() -> dict:
    return {
        "identifier": "ARO:3003702",
        "label": "Pseudomonas aeruginosa gyrA and parC conferring resistance to fluoroquinolones",
        "evidence": [{"reference": "DOI:10.1128/AAC.45.8.2263-2268.2001"}],
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


def test_enrich_record_prunes_to_mutation_and_drug_core() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert _edge_keys(out) == set(R.CORE_EDGE_ORDER)
    assert {node["node_id"] for node in out["causal_graphs"][0]["nodes"]} == {
        "determinant",
        "mech0",
        "drug0",
        "resistance",
    }


def test_enrich_record_describes_and_multi_evidences_all_edges() -> None:
    out, _ = R.enrich_record(_record())

    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert not any(item["reference"] == "ARO:3000479" for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, TARGET)
    twice, changed_again = R.enrich_text(once, TARGET)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    record = _record()
    record["identifier"] = "ARO:3003703"

    with pytest.raises(ValueError, match="expected ARO:3003702"):
        R.enrich_record(record)


def test_unexpected_edge_set_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="unexpected Pseudomonas gyrA/parC edge set"):
        R.enrich_record(record)


@pytest.mark.skipif(not TARGET.is_file(), reason="Pseudomonas target record absent")
def test_shipped_record_rewrites_in_memory() -> None:
    record = yaml.safe_load(TARGET.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert _edge_keys(out) == set(R.CORE_EDGE_ORDER)
