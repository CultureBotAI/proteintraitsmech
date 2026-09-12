from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_bci_bic_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_bci_bic_graphs", SCRIPT)
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
                "reference": "ARO:3004752",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:0000020 ! carbapenem"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:3004752",
                "snippet": "BIC is a class A beta-lactamase conferring resistance to carbapenem.",
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


def _record(identifier: str = "ARO:3004752") -> dict:
    return {
        "identifier": identifier,
        "label": "BIC Beta-lactamase",
        "definition": "BIC is a class A beta-lactamase conferring resistance to carbapenem.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000187"),
                    _node("drug0", "CHEMICAL", "ARO:0000020"),
                    _node("active_site", "MOTIF", "PROSITE:PS00146"),
                    _node("fold", "DOMAIN", "CATH:3.40.710.10"),
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
                        "active_site",
                        "determinant",
                        "part of (active site of the protein)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of (adopts fold)",
                        "RO:0002350",
                    ),
                    _edge(
                        "active_site",
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_is_the_exact_bci_bic_class_a_slice() -> None:
    assert len(R.TARGETS) == 10
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3002877",
        "ARO:3004748",
        "ARO:3004749",
        "ARO:3004750",
        "ARO:3004751",
        "ARO:3004752",
        "ARO:3004753",
        "ARO:3007100",
        "ARO:3007101",
        "ARO:3008080",
    }
    assert {target.kind for target in R.TARGETS} == {R.beta.GraphKind.CLASS_A}


@pytest.mark.parametrize("target", R.TARGETS)
def test_records_reuse_canonical_class_a_graph(target: R.beta.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "active_site",
        "fold",
        "resistance",
    ]
    assert _edge_keys(out) == {
        *R.beta._core_edge_keys("active_site"),
        ("determinant", "ARO:2000001", "drug0"),
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.beta.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.beta.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002877, found ARO:3004752"):
        R.enrich_record(_record("ARO:3004752"), R.TARGET_BY_ID["ARO:3002877"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3004752"]
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
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not R.ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", R.TARGETS)
def test_shipped_targets_are_enriched_in_memory(target: R.beta.Target) -> None:
    path = R.ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, target)

    assert changed or out == record
