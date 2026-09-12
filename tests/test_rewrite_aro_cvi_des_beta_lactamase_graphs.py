from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cvi_des_beta_lactamase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cvi_des_beta_lactamase_graphs",
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
    if predicate_id == "ARO:2000001":
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:test ! test drug"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": "Test beta-lactamase definition.",
            }
        ]

    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence,
    }


def _node(node_id: str, node_type: str, grounding: str) -> dict:
    return {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
        "grounding": grounding,
    }


def _record(
    identifier: str = "ARO:3005403",
    kind: R.beta.GraphKind = R.beta.GraphKind.METALLO,
) -> dict:
    parts = R._parts(R.beta.Target(identifier, "test.yaml", kind))

    return {
        "identifier": identifier,
        "label": "test beta-lactamase",
        "definition": "Test beta-lactamase definition.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", parts.mech1_node["grounding"]),
                    _node("drug0", "CHEMICAL", "ARO:0000020"),
                    _node(
                        parts.catalytic_node_id,
                        parts.catalytic_node["node_type"],
                        parts.catalytic_node["grounding"],
                    ),
                    _node("fold", "DOMAIN", parts.fold_node["grounding"]),
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
                    _edge(
                        "determinant",
                        "mech1",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to",
                        "ARO:2000001",
                    ),
                    _edge(
                        parts.catalytic_node_id,
                        "determinant",
                        "part of",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of",
                        "RO:0002350",
                    ),
                    _edge(
                        parts.catalytic_node_id,
                        "mech1",
                        "enables (catalysis)",
                        "RO:0002327",
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


def _nodes_by_id(record: dict) -> dict[str, dict]:
    return {
        node["node_id"]: node
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_target_set_is_the_exact_cvi_des_beta_lactamase_slice() -> None:
    assert R.TARGETS == (
        R.beta.Target("ARO:3005403", "cvi-beta-lactamase-aro3005403.yaml", R.beta.GraphKind.METALLO),
        R.beta.Target("ARO:3006924", "cvi-1-aro3006924.yaml", R.beta.GraphKind.METALLO),
        R.beta.Target("ARO:3004779", "des-beta-lactamase-aro3004779.yaml", R.beta.GraphKind.CLASS_A),
        R.beta.Target("ARO:3004780", "des-1-aro3004780.yaml", R.beta.GraphKind.CLASS_A),
    )


@pytest.mark.parametrize("target", R.TARGETS)
def test_records_gain_canonical_graph_for_assigned_family(target: R.beta.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier, target.kind), target)

    assert changed

    parts = R._parts(target)
    nodes = _nodes_by_id(out)
    assert nodes[parts.catalytic_node_id] == parts.catalytic_node
    assert nodes["fold"] == parts.fold_node
    assert _edge_keys(out) == {
        *R.beta._core_edge_keys(parts.catalytic_node_id),
        ("determinant", "ARO:2000001", "drug0"),
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(
    target: R.beta.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier, target.kind), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.beta.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier, target.kind), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3005403, found ARO:3006924"):
        R.enrich_record(_record("ARO:3006924"), R.TARGET_BY_ID["ARO:3005403"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3005403"]
    enriched, changed = R.enrich_record(_record(target.identifier, target.kind), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, R.ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, R.ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert again == out
