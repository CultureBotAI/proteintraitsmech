from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_petn_transferase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_petn_transferase_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:old",
                "snippet": "stale evidence",
            }
        ],
    }


def _record(identifier: str = "ARO:3004112", *, child: bool = False) -> dict:
    nodes = [
        {
            "node_id": "determinant",
            "label": "phosphoethanolamine transferase conferring colistin resistance",
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "charge alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3003588",
        },
        {
            "node_id": "petn_transfer",
            "label": "phosphoethanolamine transferase activity",
            "node_type": "MOLECULAR_FUNCTION",
        },
        {
            "node_id": "lipid_a",
            "label": "lipid A of the outer membrane",
            "node_type": "CHEMICAL",
        },
        {
            "node_id": "charge",
            "label": "reduced net negative surface charge",
            "node_type": "STATE",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    if child:
        nodes.insert(
            2,
            {
                "node_id": "drug0",
                "label": "peptide antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3000053",
            },
        )

    edges = [
        _edge("determinant", "mech0"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
        _edge("determinant", "petn_transfer"),
        _edge("petn_transfer", "lipid_a"),
        _edge("lipid_a", "charge"),
    ]
    if child:
        edges.insert(3, _edge("determinant", "drug0"))
        edges.append(_edge("charge", "drug0"))

    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": nodes,
                "edges": edges,
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_seven():
    assert {target.filename for target in R.TARGETS.values()} == {
        "phosphoethanolamine-transferase-conferring-colistin-resistance-aro3004112.yaml",
        "pmr-phosphoethanolamine-transferase-aro3004269.yaml",
        "intrinsic-colistin-resistant-phosphoethanolamine-transferase-aro3004465.yaml",
        "icr-mc-aro3004466.yaml",
        "icr-mo-aro3004569.yaml",
        "epta-aro3003576.yaml",
        "eptb-aro3005047.yaml",
    }


def test_parent_enrichment_grounds_nodes_describes_edges_and_adds_terminal_edge():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3004112"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["petn_transfer"] == R.SHARED_NODE_UPDATES["petn_transfer"]
    assert by_node["lipid_a"] == R.SHARED_NODE_UPDATES["lipid_a"]
    assert by_node["charge"] == R.SHARED_NODE_UPDATES["charge"]
    assert by_node["lipid_a"]["grounding"] == "CHEBI:58540"
    assert "grounding" not in by_node["charge"]
    assert len(by_pair) == len(R.PARENT_EDGES)
    assert ("charge", "resistance") in by_pair
    for edge in graph["edges"]:
        assert edge["description"]
    assert by_pair[("determinant", "petn_transfer")]["evidence"] == [
        R.PETN_GROUP_EVIDENCE,
        R.GO_PETN_TRANSFER_EVIDENCE,
    ]
    assert by_pair[("petn_transfer", "lipid_a")]["evidence"] == [
        R.PMR_PETN_EVIDENCE,
        R.GO_PETN_TRANSFER_EVIDENCE,
    ]
    assert by_pair[("charge", "resistance")]["evidence"] == [
        R.CHARGE_ALTERATION_EVIDENCE,
        R.PMR_PETN_EVIDENCE,
    ]


def test_child_targets_allow_drug_class_and_charge_to_drug_edges():
    target = R.TARGETS["ARO:3004269"]
    out, changed = R.enrich_record(_record("ARO:3004269", child=True), target)

    assert changed
    by_pair = {
        (edge["subject"], edge["object"]): edge
        for edge in out["causal_graphs"][0]["edges"]
    }
    assert len(by_pair) == len(R.CHILD_EDGES)
    assert by_pair[("determinant", "drug0")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("determinant", "drug0")]
    )
    assert by_pair[("charge", "drug0")]["description"] == (
        R.ALL_EDGE_DESCRIPTIONS[("charge", "drug0")]
    )
    assert ("charge", "resistance") in by_pair


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3004112"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3004112, found ARO:3004269"):
        R.enrich_record(_record("ARO:3004269", child=True), R.TARGETS["ARO:3004112"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("charge", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge charge -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3004112"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): lipid_a -> charge"):
        R.enrich_record(record, R.TARGETS["ARO:3004112"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3004112"]
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count(R.HISTORY_ACTION) == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    target = R.TARGETS["ARO:3004112"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    det_petn = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("determinant", "petn_transfer")
    )
    petn_lipid = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("petn_transfer", "lipid_a")
    )
    petn_lipid["evidence"] = det_petn["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-05T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_enriched_in_memory_without_unexpected_edges():
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        out, changed = R.enrich_record(copy.deepcopy(record), target)
        assert changed or out == record
        for graph in out["causal_graphs"]:
            if graph["graph_id"] != "resistance":
                continue
            assert ("charge", "resistance") in {
                (edge["subject"], edge["object"]) for edge in graph["edges"]
            }
            for edge in graph["edges"]:
                assert edge["description"]
