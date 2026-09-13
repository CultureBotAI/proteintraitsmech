from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_dhfr_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_dhfr_graphs", SCRIPT)
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
                "reference": "ARO:3000381",
                "snippet": R.TARGET_REPLACEMENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3003425") -> dict:
    return {
        "identifier": identifier,
        "label": "antibiotic resistant dihydrofolate reductase",
        "definition": R.DHFR_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "antibiotic resistant dihydrofolate reductase",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic target replacement",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001002",
                    },
                    {
                        "node_id": "shared_function",
                        "label": "the function shared with the drug's target",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "structural_difference",
                        "label": "structural difference from the sensitive target",
                        "node_type": "STATE",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
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
                        "shared_function",
                        "enables (the same function as the drug's target)",
                        "RO:0002327",
                    ),
                    _edge(
                        "determinant",
                        "structural_difference",
                        "has quality (structurally unlike the sensitive target)",
                        "RO:0000086",
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


def test_target_set_matches_exact_hidden_no_ignore_dhfr_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {"ARO:3003425"}
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-dihydrofolate-reductase-aro3003425.yaml",
    }


def test_dhfr_record_grounds_shared_function_and_adds_structural_edge() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3003425"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "shared_function",
        "structural_difference",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys()
    shared_function = out["causal_graphs"][0]["nodes"][2]
    assert shared_function == R.SHARED_FUNCTION_NODE


def test_all_non_state_nodes_are_grounded() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3003425"])

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3003425"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3003425"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    record = _record()
    record["identifier"] = "ARO:unexpected"

    with pytest.raises(ValueError, match="expected ARO:3003425, found ARO:unexpected"):
        R.enrich_record(record, R.TARGETS["ARO:3003425"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("structural_difference", "mech0"))

    with pytest.raises(ValueError, match="unexpected edge structural_difference -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3003425"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGETS["ARO:3003425"])


def test_missing_core_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing core edge"):
        R.enrich_record(record, R.TARGETS["ARO:3003425"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3003425"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / R.TARGETS["ARO:3003425"].filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, R.TARGETS["ARO:3003425"])

    assert changed or out == record
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "shared_function",
        "structural_difference",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys()
