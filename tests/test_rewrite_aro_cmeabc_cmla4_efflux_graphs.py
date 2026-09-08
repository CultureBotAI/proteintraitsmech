from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cmeabc_cmla4_efflux_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cmeabc_cmla4_efflux_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


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
                "reference": "ARO:test",
                "snippet": "relationship: confers_resistance_to_drug_class ARO:test ! test drug",
            }
        ],
    }


def _record(
    identifier: str = "ARO:3000773",
) -> dict:
    return {
        "identifier": identifier,
        "label": "test efflux pump",
        "definition": "test efflux pump definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0010000"),
                    _node("drug0", "CHEMICAL", "ARO:0000001"),
                    _node("domain", "DOMAIN", "Pfam:PF00873"),
                    _node("fold", "DOMAIN", "CATH:3.30.70.1430"),
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
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
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


def test_target_set_is_the_exact_cmeabc_cmla4_efflux_slice() -> None:
    assert R.TARGETS == (
        R.efflux.Target("ARO:3000773", "cmeabc-aro3000773.yaml", R.efflux.GraphKind.RND),
        R.efflux.Target("ARO:3002694", "cmla4-aro3002694.yaml", R.efflux.GraphKind.MFS),
    )


@pytest.mark.parametrize(
    ("target", "domain", "fold"),
    [
        (R.TARGET_BY_ID["ARO:3000773"], "Pfam:PF00873", "CATH:3.30.70.1430"),
        (R.TARGET_BY_ID["ARO:3002694"], "Pfam:PF07690", "CATH:1.20.1250.20"),
    ],
)
def test_records_keep_drug_edge_and_gain_family_domain_fold(
    target: R.efflux.Target,
    domain: str,
    fold: str,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    nodes = _nodes_by_id(out)
    assert nodes["drug0"]["grounding"] == "ARO:0000001"
    assert nodes["domain"]["grounding"] == domain
    assert nodes["fold"]["grounding"] == fold
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("domain", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("domain", "RO:0002327", "mech0"),
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(
    target: R.efflux.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.efflux.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000773, found ARO:3002694"):
        R.enrich_record(_record("ARO:3002694"), R.TARGET_BY_ID["ARO:3000773"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3000773"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
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
