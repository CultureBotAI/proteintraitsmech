from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_aad_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_aad_graphs", SCRIPT)
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
                "snippet": R.ANT_REACTION_EVIDENCE["snippet"],
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


def _record(identifier: str = "ARO:3002628", two_drugs: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "aad(6)",
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
            "label": "nucleotidylation of antibiotic conferring resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000107",
        },
        _drug_node("drug0", "aminoglycoside antibiotic", "ARO:0000016"),
        {
            "node_id": "domain",
            "label": "nucleotidyltransferase domain",
            "node_type": "DOMAIN",
            "grounding": "Pfam:PF01909",
        },
        {
            "node_id": "fold",
            "label": "DNA-polymerase-β-like nucleotidyltransferase fold",
            "node_type": "DOMAIN",
            "grounding": "CATH:3.30.460",
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
        nodes.append(_drug_node("drug1", "streptomycin", "ARO:3000433"))
        drug_edges.append(
            _edge(
                "determinant",
                "drug1",
                "confers resistance to (drug)",
                "ARO:2000001",
            )
        )

    return {
        "identifier": identifier,
        "label": "aad(6)",
        "definition": "AAD test record.",
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
                        "domain",
                        "determinant",
                        "part of (catalytic domain of the protein)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of (adopts fold)",
                        "RO:0002350",
                    ),
                    _edge(
                        "domain",
                        "mech1",
                        "enables (antibiotic nucleotidylation)",
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


def test_target_set_is_the_exact_rank_77_aad_set() -> None:
    assert len(R.TARGETS) == 28
    assert R.TARGETS[0] == R.Target("ARO:3002628", "aad-6-aro3002628.yaml")
    assert R.TARGETS[-1] == R.Target("ARO:3004683", "aads-aro3004683.yaml")
    assert "ARO:3000218" not in R.TARGET_BY_ID


def test_aad_records_gain_atp_dependent_adenylylation_path() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3002628"])

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
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "transfer"),
        ("transfer", "RO:0002233", "atp"),
        ("transfer", "RO:0002233", "drug0"),
        ("transfer", "RO:0002411", "adenylylated"),
        ("adenylylated", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("domain", "BFO:0000050", "determinant"),
        ("determinant", "RO:0002350", "fold"),
        ("domain", "RO:0002327", "transfer"),
    }


def test_multiple_existing_drug_edges_are_preserved() -> None:
    out, changed = R.enrich_record(
        _record(two_drugs=True),
        R.TARGET_BY_ID["ARO:3002628"],
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
    assert ("transfer", "RO:0002233", "drug0") in _edge_keys(out)
    assert ("transfer", "RO:0002233", "drug1") in _edge_keys(out)


def test_legacy_domain_to_mechanism_shortcut_is_removed() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3002628"])

    assert changed
    assert ("domain", "RO:0002327", "mech1") not in _edge_keys(out)
    assert ("domain", "RO:0002327", "transfer") in _edge_keys(out)
    assert "ATP" in yaml.safe_dump(out)


def test_all_output_groundable_nodes_are_grounded() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3002628"])

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3002628"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])
        assert len(
            {(item["reference"], item["snippet"]) for item in edge["evidence"]}
        ) == len(edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGET_BY_ID["ARO:3002628"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002601, found ARO:3002628"):
        R.enrich_record(_record("ARO:3002628"), R.TARGET_BY_ID["ARO:3002601"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002628"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002628"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3002628"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("aad-6-aro3002628.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("aad-6-aro3002628.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
