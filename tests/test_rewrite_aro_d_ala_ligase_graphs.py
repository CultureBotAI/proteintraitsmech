from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_d_ala_ligase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_d_ala_ligase_graphs", SCRIPT)
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
                "reference": "ARO:test",
                "snippet": "Test Van ligase evidence.",
            }
        ],
    }


def _node(
    node_id: str,
    node_type: str,
    grounding: str | None = None,
) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding is not None:
        node["grounding"] = grounding
    return node


def _record(identifier: str = "ARO:3002978") -> dict:
    return {
        "identifier": identifier,
        "label": "test Van ligase",
        "definition": "Test Van ligase definition.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000213"),
                    _node("drug0", "CHEMICAL", "ARO:3000081"),
                    _node("domain", "DOMAIN", "Pfam:PF07478"),
                    _node("fold", "DOMAIN", "CATH:3.30.470"),
                    _node("precursor_ser", "STATE"),
                    _node("dala_dser", "CHEMICAL"),
                    _node("ligase_activity", "MOLECULAR_FUNCTION", "EC:6.3.2.35"),
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
                    _edge("domain", "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("domain", "mech0", "enables", "RO:0002327"),
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


def test_target_set_is_the_exact_low_score_d_ala_ligase_slice() -> None:
    assert R.TARGETS == (
        R.Target(
            "ARO:3002978",
            "d-ala-d-lac-ligase-aro3002978.yaml",
            "peptidoglycan precursor ending in D-Ala-D-Lac",
            "dlac",
        ),
        R.Target(
            "ARO:3002979",
            "d-ala-d-ser-ligase-aro3002979.yaml",
            "peptidoglycan precursor ending in D-Ala-D-Ser",
            "dser",
        ),
    )


def test_d_lac_graph_keeps_grounded_domain_and_fold() -> None:
    target = R.TARGET_BY_ID["ARO:3002978"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    nodes = _nodes_by_id(out)
    assert "dala_dser" not in nodes
    assert nodes["domain"] == R.DLAC_DOMAIN_NODE
    assert nodes["fold"] == R.ATP_GRASP_FOLD_NODE
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("alt_precursor", "RO:0002411", "low_affinity"),
        ("low_affinity", "RO:0002411", "resistance"),
        ("domain", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("domain", "RO:0002327", "alt_precursor"),
    }


def test_d_ser_graph_keeps_ec_ligase_activity_and_drops_ungrounded_dipeptide() -> None:
    target = R.TARGET_BY_ID["ARO:3002979"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    nodes = _nodes_by_id(out)
    assert "dala_dser" not in nodes
    assert nodes["ligase_activity"] == R.DSER_LIGASE_ACTIVITY_NODE
    assert _edge_keys(out) == {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("alt_precursor", "RO:0002411", "low_affinity"),
        ("low_affinity", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "ligase_activity"),
        ("ligase_activity", "RO:0002411", "alt_precursor"),
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002978, found ARO:3002979"):
        R.enrich_record(_record("ARO:3002979"), R.TARGET_BY_ID["ARO:3002978"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002978"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3002978"]
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
