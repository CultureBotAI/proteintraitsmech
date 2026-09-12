from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_target_protection_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_target_protection_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(
    subject: str,
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3000185",
                "snippet": R.TARGET_PROTEIN_EVIDENCE["snippet"],
            }
        ],
    }


def _node(node_id: str, node_type: str, grounding: str) -> dict:
    return {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
        "grounding": grounding,
    }


def _record(identifier: str = "ARO:3000185") -> dict:
    return {
        "identifier": identifier,
        "label": "antibiotic target protection protein",
        "definition": R.TARGET_PROTEIN_EVIDENCE["snippet"],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001003"),
                    {
                        "node_id": "target",
                        "label": "the antibiotic's target",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": "blocked_binding",
                        "label": "antibiotic prevented from binding its target",
                        "node_type": "STATE",
                    },
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "target",
                        "molecularly interacts with (binds the antibiotic target)",
                        "RO:0002436",
                    ),
                    _edge(
                        "determinant",
                        "blocked_binding",
                        "causally upstream of (prevents antibiotic binding)",
                        "RO:0002411",
                    ),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_is_only_the_abstract_target_protection_parent() -> None:
    assert R.TARGETS == (
        R.Target(
            "ARO:3000185",
            "antibiotic-target-protection-protein-aro3000185.yaml",
        ),
    )


def test_parent_gains_two_state_target_protection_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "target_binding",
        "blocked_binding",
        "resistance",
    ]
    assert _edge_keys(out) == R.OUTPUT_EDGE_KEYS
    assert "target" not in _node_ids(out)


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_all_output_nodes_are_grounded_or_described_states() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding") or (
            node["node_type"] == "STATE" and node.get("description")
        )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGET)
    twice, changed_again = R.enrich_record(once, R.TARGET)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000185, found ARO:3000186"):
        R.enrich_record(_record("ARO:3000186"), R.TARGET)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET)


def test_missing_core_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("object") != "mech0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGET)


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("target", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge target -> resistance"):
        R.enrich_record(record, R.TARGET)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = R.enrich_record(_record(), R.TARGET)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, R.ARO_DIR / R.TARGET.filename)
    again, changed_again = R.enrich_text(out, R.ARO_DIR / R.TARGET.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not R.ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory() -> None:
    path = R.ARO_DIR / R.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, R.TARGET)

    assert changed or out == record
