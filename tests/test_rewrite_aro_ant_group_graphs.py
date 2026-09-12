from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ant_group_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_ant_group_graphs", SCRIPT)
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
                "reference": "PMID:25564464",
                "snippet": R.aad.ANT_REACTION_EVIDENCE["snippet"],
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


def _record(identifier: str = "ARO:3004276") -> dict:
    return {
        "identifier": identifier,
        "label": "ANT(2'')",
        "definition": (
            "A category of aminoglycoside O-nucleotidyltransferase enzymes "
            "that inactivate aminoglycoside antibiotics."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000107"),
                    _node("drug0", "CHEMICAL", "ARO:0000016"),
                    _node("domain", "DOMAIN", "Pfam:PF01909"),
                    _node("fold", "DOMAIN", "CATH:3.30.460"),
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
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge("domain", "determinant", "part of", "BFO:0000050"),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge("domain", "mech1", "enables", "RO:0002327"),
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


def test_target_set_is_the_exact_ant_group_set() -> None:
    assert R.TARGETS == (
        R.Target("ARO:3004276", "ant-2-aro3004276.yaml"),
        R.Target("ARO:3007405", "ant-2-i-aro3007405.yaml"),
        R.Target("ARO:3000230", "ant-2-ia-aro3000230.yaml"),
        R.Target("ARO:3004275", "ant-3-aro3004275.yaml"),
        R.Target("ARO:3007407", "ant-3-i-aro3007407.yaml"),
        R.Target("ARO:3000232", "ant-3-ia-aro3000232.yaml"),
        R.Target("ARO:3005062", "ant-3-ib-aro3005062.yaml"),
        R.Target("ARO:3004089", "ant-3-iia-aro3004089.yaml"),
        R.Target("ARO:3004090", "ant-3-iib-aro3004090.yaml"),
        R.Target("ARO:3004091", "ant-3-iic-aro3004091.yaml"),
        R.Target("ARO:3000229", "ant-4-aro3000229.yaml"),
        R.Target("ARO:3007403", "ant-4-i-aro3007403.yaml"),
        R.Target("ARO:3002623", "ant-4-ia-aro3002623.yaml"),
        R.Target("ARO:3003905", "ant-4-ib-aro3003905.yaml"),
        R.Target("ARO:3007404", "ant-4-ii-aro3007404.yaml"),
        R.Target("ARO:3002624", "ant-4-iia-aro3002624.yaml"),
        R.Target("ARO:3002625", "ant-4-iib-aro3002625.yaml"),
        R.Target("ARO:3000225", "ant-6-aro3000225.yaml"),
        R.Target("ARO:3007399", "ant-6-i-aro3007399.yaml"),
        R.Target("ARO:3002626", "ant-6-ia-aro3002626.yaml"),
        R.Target("ARO:3002629", "ant-6-ib-aro3002629.yaml"),
        R.Target("ARO:3000228", "ant-9-aro3000228.yaml"),
        R.Target("ARO:3007400", "ant-9-i-aro3007400.yaml"),
        R.Target("ARO:3002630", "ant-9-ia-aro3002630.yaml"),
        R.Target("ARO:3007401", "ant-9-ib-aro3007401.yaml"),
        R.Target("ARO:3007515", "ant-9-ic-aro3007515.yaml"),
    )
    assert "ARO:3002598" not in R.TARGET_BY_ID


def test_ant_group_records_gain_aad_adenylylation_path() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3004276"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "transfer",
        "atp",
        "adenylylated",
        "domain",
        "fold",
        "resistance",
    ]
    assert _edge_keys(out) == {
        *R.aad.CORE_EDGE_KEYS,
        *R.aad.CANONICAL_EDGE_KEYS,
        ("transfer", "RO:0002233", "drug0"),
        ("determinant", "ARO:2000001", "drug0"),
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
def test_all_output_nodes_are_grounded_or_described_states(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding") or (
            node["node_type"] == "STATE" and node.get("description")
        )


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3004276"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007405, found ARO:3004276"):
        R.enrich_record(_record("ARO:3004276"), R.TARGET_BY_ID["ARO:3007405"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3004276"])


def test_enrich_text_adds_ant_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("ant-2-aro3004276.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("ant-2-aro3004276.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_EVENT["action"] in once
    assert "Completed AAD" not in once
    assert "&id" not in once
    assert "*id" not in once
