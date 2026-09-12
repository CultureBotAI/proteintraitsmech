from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_adc_leaf_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_adc_leaf_graphs", SCRIPT)
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
                "reference": "PMID:19136439",
                "snippet": R.AMPC_REACTION_EVIDENCE["snippet"],
            }
        ],
    }


def _drug_node(node_id: str, label: str, grounding: str) -> dict:
    return {
        "node_id": node_id,
        "label": label,
        "node_type": "CHEMICAL",
        "grounding": grounding,
    }


def _record(identifier: str = "ARO:3003847", two_drugs: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "ADC-1",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "antibiotic inactivation",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001004",
        },
        {
            "node_id": "mech1",
            "label": "hydrolysis of beta-lactam antibiotic by serine beta-lactamase",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000187",
        },
        _drug_node("drug0", "cephalosporin", "ARO:0000032"),
        {
            "node_id": "active_site",
            "label": "class C beta-lactamase active-site signature (Ser64 S-x-x-K)",
            "node_type": "MOTIF",
            "grounding": "PROSITE:PRU10102",
        },
        {
            "node_id": "fold",
            "label": "DD-peptidase/beta-lactamase superfamily fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.40.710.10",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
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
        nodes.append(_drug_node("drug1", "carbapenem", "ARO:0000020"))
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
        "label": "ADC-1",
        "definition": "ADC-1 is a beta-lactamase found in Acinetobacter baumannii.",
        "mapping_status": "REVIEWED",
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
                    *drug_edges,
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


def test_target_set_is_the_exact_adc_rank_77_set() -> None:
    assert len(R.TARGETS) == 329
    assert R.TARGETS[0] == R.Target("ARO:3003847", "adc-1-aro3003847.yaml")
    assert R.TARGETS[-1] == R.Target(
        "ARO:3005460",
        "adc-beta-lactamases-pending-classification-for-carbapenemase-activity-aro3005460.yaml",
    )
    assert "ARO:3005459" not in R.TARGET_BY_ID


def test_adc_records_keep_class_c_hydrolysis_shape() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3003847"])

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
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("active_site", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("active_site", "RO:0002327", "mech1"),
    }


def test_multiple_existing_drug_edges_are_preserved() -> None:
    out, changed = R.enrich_record(
        _record(two_drugs=True),
        R.TARGET_BY_ID["ARO:3003847"],
    )

    assert changed
    assert [node["node_id"] for node in out["causal_graphs"][0]["nodes"][:5]] == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "drug1",
    ]
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
    assert ("determinant", "ARO:2000001", "drug1") in _edge_keys(out)


def test_all_output_groundable_nodes_are_grounded() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3003847"])

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding")


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3003847"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])
        assert len(
            {(item["reference"], item["snippet"]) for item in edge["evidence"]}
        ) == len(edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3003847"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003855, found ARO:3003847"):
        R.enrich_record(_record("ARO:3003847"), R.TARGET_BY_ID["ARO:3003855"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3003847"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3003847"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3003847"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("adc-1-aro3003847.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("adc-1-aro3003847.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
