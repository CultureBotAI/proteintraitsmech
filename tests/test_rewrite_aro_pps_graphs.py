from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_pps_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_pps_graphs", SCRIPT)
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
                "reference": "ARO:3005002",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:3007155 ! pyrazine antibiotic"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:3005002",
                "snippet": R.PPS_PARENT_EVIDENCE["snippet"],
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


def _record(identifier: str = "ARO:3005002") -> dict:
    return {
        "identifier": identifier,
        "label": "antibiotic resistant polyketide synthase genes",
        "definition": R.PPS_PARENT_EVIDENCE["snippet"],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:3007155"),
                    {
                        "node_id": "pdim_synthesis",
                        "label": "phthiocerol dimycocerosate biosynthesis",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
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
                    _edge(
                        "determinant",
                        "pdim_synthesis",
                        "participates in (phthiocerol dimycocerosate biosynthesis)",
                        "RO:0000056",
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


def test_target_set_is_the_exact_pps_branch() -> None:
    assert len(R.TARGETS) == 9
    assert {target.filename for target in R.TARGETS} == {
        "antibiotic-resistant-polyketide-synthase-genes-aro3005002.yaml",
        "antibiotic-resistant-ppsa-aro3004972.yaml",
        "pyrazinamide-resistant-ppsa-aro3004973.yaml",
        "antibiotic-resistant-ppsc-aro3004883.yaml",
        "pyrazinamide-resistant-ppsc-aro3004884.yaml",
        (
            "mycobacterium-tuberculosis-ppsc-mutations-confer-resistance-to-"
            "pyrazinamide-aro3004975.yaml"
        ),
        "antibiotic-resistant-ppsd-aro3004885.yaml",
        "pyrazinamide-resistant-ppsd-aro3004886.yaml",
        (
            "mycobacterium-tuberculosis-ppsd-mutations-confer-resistance-to-"
            "pyrazinamide-aro3004976.yaml"
        ),
    }


def test_pps_records_gain_pdim_loss_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET_BY_ID["ARO:3005002"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "pdim_loss",
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
def test_all_output_nodes_are_grounded_or_described_states(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding") or (
            node["node_type"] == "STATE" and node.get("description")
        )


@pytest.mark.parametrize("target", R.TARGETS)
def test_enrich_record_is_idempotent(target: R.Target) -> None:
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004972, found ARO:3005002"):
        R.enrich_record(_record("ARO:3005002"), R.TARGET_BY_ID["ARO:3004972"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3005002"])


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge.get("predicate_id") != "ARO:2000001"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3005002"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pdim_synthesis", "drug0"))

    with pytest.raises(ValueError, match="unexpected edge pdim_synthesis -> drug0"):
        R.enrich_record(record, R.TARGET_BY_ID["ARO:3005002"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGET_BY_ID["ARO:3005002"]
    enriched, changed = R.enrich_record(_record(), target)
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
def test_shipped_targets_are_enriched_in_memory(target: R.Target) -> None:
    path = R.ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, target)

    assert changed or out == record
