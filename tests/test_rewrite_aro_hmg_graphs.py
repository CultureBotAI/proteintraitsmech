from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"
SCRIPT = REPO / "scripts" / "rewrite_aro_hmg_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_hmg_graphs", SCRIPT)
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
                "reference": "ARO:3007668",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:3007499 ! triazole antibiotic"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:3007668",
                "snippet": R.HMG_PARENT_EVIDENCE["snippet"],
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


def _record(identifier: str = "ARO:3007668") -> dict:
    return {
        "identifier": identifier,
        "label": "HMG-CoA reductase-encoding genes",
        "definition": R.HMG_PARENT_EVIDENCE["snippet"],
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:3007499"),
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
                        "confers resistance to",
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_is_the_exact_hmg_reductase_branch() -> None:
    assert R.TARGETS == (
        R.Target("ARO:3007668", "hmg-coa-reductase-encoding-genes-aro3007668.yaml"),
        R.Target(
            "ARO:3007670",
            (
                "aspergillus-spp-hmg1-with-mutations-conferring-resistance-to-"
                "triazoles-antibioti-aro3007670.yaml"
            ),
        ),
    )


@pytest.mark.parametrize("target", R.TARGETS)
def test_records_gain_grounded_hmgcoa_activity(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert out["causal_graphs"][0]["graph_id"] == "resistance"
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "hmgcoa",
        "resistance",
    ]
    assert _edge_keys(out) == R.OUTPUT_EDGE_KEYS


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_edges_are_described_and_multi_evidenced(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


@pytest.mark.parametrize("target", R.TARGETS)
def test_all_output_nodes_are_grounded(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding")


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007670, found ARO:3007668"):
        R.enrich_record(_record("ARO:3007668"), R.TARGET_BY_ID["ARO:3007670"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3007668"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3007668"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("hmgcoa", "drug0"))

    with pytest.raises(ValueError, match="unexpected edge hmgcoa -> drug0"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3007668"])


def test_enrich_text_rewrites_yaml_aliases_promotes_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3007668"]
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
    assert "*id" not in out
    assert "mapping_status: REVIEWED" in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not R.ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", R.TARGETS)
def test_shipped_targets_are_enriched_in_memory(target: R.Target) -> None:
    path = R.ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, target)

    assert changed or out == record
