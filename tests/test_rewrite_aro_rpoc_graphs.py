from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rpoc_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rpoc_graphs", SCRIPT)
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
                "reference": "ARO:3003289",
                "snippet": "Mutations in rpoC gene confers antibiotic resistance.",
            }
        ],
    }


def _record(identifier: str = "ARO:3003290") -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": "rpoC",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
        {
            "node_id": "transcription",
            "label": "transcription",
            "node_type": "BIOLOGICAL_PROCESS",
        },
        {
            "node_id": "active_center",
            "label": "RNA polymerase active center and template/transcript binding sites",
            "node_type": "PROTEIN",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    edges = [
        _edge("determinant", "mech0", "participates in", "RO:0000056"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
        _edge("determinant", "active_center", "part of", "BFO:0000050"),
        _edge("active_center", "transcription", "part of", "BFO:0000050"),
    ]

    if target.drug_relation_reference is not None:
        nodes.insert(
            2,
            {
                "node_id": "drug0",
                "label": target.drug_relation_label,
                "node_type": "CHEMICAL",
                "grounding": target.drug_relation_object,
            },
        )
        edges.append(_edge("determinant", "drug0", "confers resistance to", "ARO:2000001"))

    return {
        "identifier": identifier,
        "label": "rpoC",
        "definition": "Mutations in rpoC gene confers antibiotic resistance.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": nodes,
                "edges": edges,
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


def test_target_set_matches_exact_hidden_no_ignore_rpoc_subtree() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3003289",
        "ARO:3003290",
        "ARO:3003291",
        "ARO:3004681",
        "ARO:3004725",
        "ARO:3004994",
        "ARO:3004995",
    }


def test_root_is_reduced_to_mutation_route() -> None:
    target = R.TARGETS["ARO:3003289"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == ["determinant", "mech0", "resistance"]
    assert _edge_keys(out) == R._canonical_edges(target)


def test_drug_specific_records_keep_only_drug_class_edge() -> None:
    target = R.TARGETS["ARO:3003290"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == ["determinant", "mech0", "drug0", "resistance"]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert "active_center" not in yaml.safe_dump(out)
    assert "transcription" not in yaml.safe_dump(out)


def test_leaf_records_use_inherited_parent_evidence() -> None:
    target = R.TARGETS["ARO:3004681"]
    out, changed = R.enrich_record(_record(target.identifier), target)
    text = yaml.safe_dump(out)

    assert changed
    assert "ARO:3004725" in text
    assert "glycopeptide antibiotic" in text


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3003290"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003290, found ARO:3003291"):
        R.enrich_record(_record("ARO:3003291"), R.TARGETS["ARO:3003290"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3003290"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3003290"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3003290"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
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
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out
