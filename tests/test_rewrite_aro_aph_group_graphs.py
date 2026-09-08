from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_aph_group_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_aph_group_graphs", SCRIPT)
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
                "reference": "PMID:9200607",
                "snippet": R.APH_STRUCTURE_EVIDENCE["snippet"],
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


def _record(identifier: str = "ARO:3000128") -> dict:
    return {
        "identifier": identifier,
        "label": "APH(2'')",
        "definition": (
            "A category of aminoglycoside O-phosphotransferase enzymes that "
            "inactivate aminoglycoside antibiotics by phosphorylation."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000105"),
                    _node("drug0", "CHEMICAL", "ARO:0000016"),
                    _node("domain", "DOMAIN", "Pfam:PF01636"),
                    _node("fold", "DOMAIN", "CATH:3.90.1200"),
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


def test_target_set_is_the_exact_aph_group_set() -> None:
    assert len(R.TARGETS) == 56
    assert R.TARGETS[0] == R.Target("ARO:3000128", "aph-2-aro3000128.yaml")
    assert R.TARGETS[-1] == R.Target("ARO:3003918", "apma-aro3003918.yaml")
    assert {target.filename for target in R.TARGETS} == {
        "aph-2-aro3000128.yaml",
        "aph-2-ie-aro3002634.yaml",
        "aph-2-if-aro3004191.yaml",
        "aph-2-ig-aro3002669.yaml",
        "aph-2-iia-aro3002635.yaml",
        "aph-2-iiia-aro3002636.yaml",
        "aph-2-iva-aro3002637.yaml",
        "aph-3-aro3000126.yaml",
        "aph-3-aro3000127.yaml",
        "aph-3-i-aro3007406.yaml",
        "aph-3-i-aro3007414.yaml",
        "aph-3-ia-aro3002638.yaml",
        "aph-3-ia-aro3002641.yaml",
        "aph-3-ib-aro3002639.yaml",
        "aph-3-ib-aro3002642.yaml",
        "aph-3-ic-aro3002640.yaml",
        "aph-3-ii-aro3007408.yaml",
        "aph-3-iia-aro3002644.yaml",
        "aph-3-iib-aro3002645.yaml",
        "aph-3-iic-aro3002646.yaml",
        "aph-3-iii-aro3007409.yaml",
        "aph-3-iiia-aro3002647.yaml",
        "aph-3-iv-aro3007410.yaml",
        "aph-3-iva-aro3002648.yaml",
        "aph-3-ixa-aro3004087.yaml",
        "aph-3-v-aro3007411.yaml",
        "aph-3-va-aro3002649.yaml",
        "aph-3-vb-aro3002650.yaml",
        "aph-3-vc-aro3002651.yaml",
        "aph-3-vi-aro3007412.yaml",
        "aph-3-via-aro3002652.yaml",
        "aph-3-vib-aro3002653.yaml",
        "aph-3-vii-aro3007413.yaml",
        "aph-3-viia-aro3002654.yaml",
        "aph-3-viiia-aro3004680.yaml",
        "aph-3-viiib-aro3004086.yaml",
        "aph-4-aro3000155.yaml",
        "aph-4-i-aro3007418.yaml",
        "aph-4-ia-aro3002655.yaml",
        "aph-4-ib-aro3002656.yaml",
        "aph-6-aro3000151.yaml",
        "aph-6-i-aro3007415.yaml",
        "aph-6-ia-aro3002657.yaml",
        "aph-6-ib-aro3002658.yaml",
        "aph-6-ic-aro3002659.yaml",
        "aph-6-id-aro3002660.yaml",
        "aph-7-aro3000154.yaml",
        "aph-7-i-aro3007417.yaml",
        "aph-7-ia-aro3002661.yaml",
        "aph-9-aro3000153.yaml",
        "aph-9-i-aro3007416.yaml",
        "aph-9-ia-aro3002662.yaml",
        "aph-9-ib-aro3002663.yaml",
        "aph-9-ic-aro3007539.yaml",
        "apha15-aro3004675.yaml",
        "apma-aro3003918.yaml",
    }


def test_aph_records_gain_phosphotransferase_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3000128"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "transfer",
        "phosphorylated",
        "domain",
        "fold",
        "resistance",
    ]
    assert _edge_keys(out) == {
        *R.CORE_EDGE_KEYS,
        *R.CANONICAL_EDGE_KEYS,
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
    target = R.TARGET_BY_ID["ARO:3000128"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002634, found ARO:3000128"):
        R.enrich_record(_record("ARO:3000128"), R.TARGET_BY_ID["ARO:3002634"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000128"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing drug edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3000128"])


def test_enrich_text_adds_history_once_and_avoids_yaml_anchors() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, pathlib.Path("aph-2-aro3000128.yaml"))
    twice, changed_again = R.enrich_text(once, pathlib.Path("aph-2-aro3000128.yaml"))

    assert changed
    assert not changed_again
    assert once == twice
    assert R.HISTORY_CURATOR in once
    assert "&id" not in once
    assert "*id" not in once
