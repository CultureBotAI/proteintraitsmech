from __future__ import annotations

import importlib.util
import pathlib
import sys
from collections import Counter

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cat_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_cat_graphs", SCRIPT)
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


def _record(identifier: str = "ARO:3000122", two_drugs: bool = False) -> dict:
    nodes = [
        _node("determinant", "PROTEIN", identifier),
        _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
        _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000106"),
        _node("drug0", "CHEMICAL", "ARO:3000387"),
        _node("domain", "DOMAIN", "Pfam:PF00302"),
        _node("fold", "DOMAIN", "CATH:3.30.559"),
        _node("resistance", "PHENOTYPE", "GO:0046677"),
    ]
    drug_edges = [
        _edge(
            "determinant",
            "drug0",
            "confers resistance to (drug class)",
            "ARO:2000001",
        )
    ]
    if two_drugs:
        nodes.append(_node("drug1", "CHEMICAL", "ARO:0000000"))
        drug_edges.append(
            _edge(
                "determinant",
                "drug1",
                "confers resistance to (drug class)",
                "ARO:2000001",
            )
        )

    return {
        "identifier": identifier,
        "label": "chloramphenicol acetyltransferase (CAT)",
        "definition": "Inactivates chloramphenicol by addition of an acyl group.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": nodes,
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
                    _edge("domain", "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("domain", "mech1", "enables", "RO:0002327"),
                    *drug_edges,
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


def test_target_set_is_the_exact_cat_set() -> None:
    assert R.TARGETS == (
        R.Target(
            "ARO:3004451",
            "agrobacterium-fabrum-chloramphenicol-acetyltransferase-aro3004451.yaml",
        ),
        R.Target(
            "ARO:3004452",
            "alkalihalobacillus-clausii-chloramphenicol-acetyltransferase-aro3004452.yaml",
        ),
        R.Target("ARO:3002672", "bacillus-pumilus-cat86-aro3002672.yaml"),
        R.Target(
            "ARO:3004454",
            "campylobacter-coli-chloramphenicol-acetyltransferase-aro3004454.yaml",
        ),
        R.Target("ARO:3002670", "cat-aro3002670.yaml"),
        R.Target("ARO:3002683", "cata1-aro3002683.yaml"),
        R.Target("ARO:3004657", "cata4-aro3004657.yaml"),
        R.Target("ARO:3004658", "cata8-aro3004658.yaml"),
        R.Target("ARO:3003110", "catb10-aro3003110.yaml"),
        R.Target("ARO:3004660", "catb11-aro3004660.yaml"),
        R.Target("ARO:3002675", "catb2-aro3002675.yaml"),
        R.Target("ARO:3002676", "catb3-aro3002676.yaml"),
        R.Target("ARO:3002680", "catb8-aro3002680.yaml"),
        R.Target("ARO:3002681", "catb9-aro3002681.yaml"),
        R.Target("ARO:3002682", "catd-aro3002682.yaml"),
        R.Target("ARO:3002684", "catii-aro3002684.yaml"),
        R.Target("ARO:3004656", "catii-from-escherichia-coli-k-12-aro3004656.yaml"),
        R.Target("ARO:3002685", "catiii-aro3002685.yaml"),
        R.Target("ARO:3002686", "catp-aro3002686.yaml"),
        R.Target("ARO:3002687", "catq-aro3002687.yaml"),
        R.Target("ARO:3002688", "cats-aro3002688.yaml"),
        R.Target("ARO:3003983", "catu-aro3003983.yaml"),
        R.Target("ARO:3004357", "catv-aro3004357.yaml"),
        R.Target("ARO:3000122", "chloramphenicol-acetyltransferase-cat-aro3000122.yaml"),
        R.Target("ARO:3002674", "clostridium-butyricum-catb-aro3002674.yaml"),
        R.Target(
            "ARO:3004458",
            "enterococcus-faecalis-chloramphenicol-acetyltransferase-aro3004458.yaml",
        ),
        R.Target(
            "ARO:3004456",
            "enterococcus-faecium-chloramphenicol-acetyltransferase-aro3004456.yaml",
        ),
        R.Target("ARO:3002671", "limosilactobacillus-reuteri-cat-tc-aro3002671.yaml"),
        R.Target("ARO:3002689", "plasmid-encoded-cat-pp-cat-aro3002689.yaml"),
        R.Target("ARO:3002678", "pseudomonas-aeruginosa-catb6-aro3002678.yaml"),
        R.Target("ARO:3002679", "pseudomonas-aeruginosa-catb7-aro3002679.yaml"),
        R.Target(
            "ARO:3004457",
            "staphylococcus-intermedius-chloramphenicol-acetyltransferase-aro3004457.yaml",
        ),
        R.Target(
            "ARO:3004455",
            "streptococcus-suis-chloramphenicol-acetyltransferase-aro3004455.yaml",
        ),
        R.Target(
            "ARO:3004460",
            "vibrio-anguillarum-chloramphenicol-acetyltransferase-aro3004460.yaml",
        ),
    )


def test_records_gain_described_cat_acetyl_coa_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3000122"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "domain",
        "fold",
        "acetyl_coa",
        "modified",
        "resistance",
    ]
    assert _edge_keys(out) == R.BASE_EDGE_KEYS | R.CAT_ROUTE_EDGE_KEYS | {
        ("determinant", "ARO:2000001", "drug0"),
    }


def test_existing_direct_drug_edges_are_preserved() -> None:
    out, changed = R.enrich_record(
        _record("ARO:3002675", two_drugs=True),
        R.TARGET_BY_ID["ARO:3002675"],
    )

    assert changed
    assert [node["node_id"] for node in out["causal_graphs"][0]["nodes"][3:5]] == [
        "drug0",
        "drug1",
    ]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("determinant", "ARO:2000001", "drug1") in _edge_keys(out)
    assert ("mech1", "RO:0002233", "drug1") in _edge_keys(out)
    assert ("modified", "RO:0002212", "drug1") in _edge_keys(out)
    assert Counter(_edge_keys(out)).total() == len(out["causal_graphs"][0]["edges"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_nodes_are_grounded_or_described_states(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding") or (
            node["node_type"] == "STATE" and node.get("description")
        )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3000122"])
    twice, changed_again = R.enrich_record(once, R.TARGET_BY_ID["ARO:3000122"])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002683, found ARO:3000122"):
        R.enrich_record(_record("ARO:3000122"), R.TARGET_BY_ID["ARO:3002683"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "determinant",
            "drug0",
            "confers resistance to (drug class)",
            "ARO:2000001",
        )
    )

    with pytest.raises(ValueError, match="duplicate edge determinant -> drug0"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000122"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000122"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(
        text,
        pathlib.Path("chloramphenicol-acetyltransferase-cat-aro3000122.yaml"),
    )
    twice, changed_again = R.enrich_text(
        once,
        pathlib.Path("chloramphenicol-acetyltransferase-cat-aro3000122.yaml"),
    )

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
