from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mph_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_mph_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


M = _load()


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
                "reference": M.PARENT_IDENTIFIER,
                "snippet": M.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(target: object | None = None, identifier: str | None = None) -> dict:
    if target is None:
        target = M.TARGETS["ARO:3000316"]
    if identifier is None:
        identifier = target.identifier
    return {
        "identifier": identifier,
        "label": "mphA",
        "definition": M.PARENT_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "mphA",
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
                        "label": "phosphorylation of antibiotic conferring resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000105",
                    },
                    {
                        "node_id": "drug0",
                        "label": "macrolide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:0000000",
                    },
                    {
                        "node_id": "kinase",
                        "label": "macrolide phosphotransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "pocket",
                        "label": "expanded hydrophobic antibiotic binding pocket",
                        "node_type": "STATE",
                    },
                    {
                        "node_id": "phospho_drug",
                        "label": "phosphorylated (inactive) macrolide",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
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
                    _edge(
                        "determinant",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "kinase",
                        "enables (macrolide phosphorylation)",
                        "RO:0002327",
                    ),
                    _edge(
                        "pocket",
                        "determinant",
                        "part of (the substrate-binding site)",
                        "BFO:0000050",
                    ),
                    _edge("kinase", "phospho_drug", "has output", "RO:0002234"),
                    _edge(
                        "phospho_drug",
                        "drug0",
                        "negatively regulates (the phosphorylated drug is inactive)",
                        "RO:0002212",
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


def test_targets_match_exact_mph_records() -> None:
    assert set(M.TARGETS) == {
        "ARO:3000333",
        "ARO:3000316",
        "ARO:3000318",
        "ARO:3000319",
        "ARO:3003741",
        "ARO:3003071",
        "ARO:3003742",
        "ARO:3004539",
        "ARO:3003991",
        "ARO:3004544",
        "ARO:3004541",
        "ARO:3003072",
        "ARO:3003767",
        "ARO:3004542",
        "ARO:3004543",
        "ARO:3003839",
    }


def test_mph_records_rewrite_to_grounded_phosphorylation_route() -> None:
    out, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "phospho_drug",
        "resistance",
    ]
    assert _edge_keys(out) == M.EXPECTED_EDGE_KEYS


def test_redundant_kinase_and_pocket_side_branch_are_removed() -> None:
    out, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])

    assert changed
    assert "kinase" not in _node_ids(out)
    assert "pocket" not in _node_ids(out)
    assert M.REMOVED_EDGE_KEYS.isdisjoint(_edge_keys(out))
    assert ("mech1", "RO:0002234", "phospho_drug") in _edge_keys(out)


def test_phosphorylated_macrolide_becomes_described_state() -> None:
    out, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])

    assert changed
    phospho_drug = out["causal_graphs"][0]["nodes"][4]
    assert phospho_drug["node_id"] == "phospho_drug"
    assert phospho_drug["node_type"] == "STATE"
    assert phospho_drug["description"]


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_drug_relation_evidence_distinguishes_parent_from_children() -> None:
    parent = M._drug_relation_evidence(M.TARGETS["ARO:3000333"])
    child = M._drug_relation_evidence(M.TARGETS["ARO:3000316"])

    assert "asserted directly" in parent["notes"]
    assert "inherited by ARO:3000316" in child["notes"]


def test_enrich_record_is_idempotent() -> None:
    once, changed = M.enrich_record(_record(), M.TARGETS["ARO:3000316"])
    twice, changed_again = M.enrich_record(once, M.TARGETS["ARO:3000316"])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000316, found ARO:3000317"):
        M.enrich_record(_record(identifier="ARO:3000317"), M.TARGETS["ARO:3000316"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("phospho_drug", "mech1"))

    with pytest.raises(ValueError, match="unexpected edge phospho_drug -> mech1"):
        M.enrich_record(record, M.TARGETS["ARO:3000316"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech1", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech1 -> resistance"):
        M.enrich_record(record, M.TARGETS["ARO:3000316"])


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        M.enrich_record(record, M.TARGETS["ARO:3000316"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = M.TARGETS["ARO:3000316"]
    enriched, changed = M.enrich_record(_record(target), target)
    assert changed

    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = M.enrich_text(text, ARO_DIR / target.filename, target)
    again, changed_again = M.enrich_text(out, ARO_DIR / target.filename, target)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(M.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", list(M.TARGETS.values()))
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: object,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = M.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == M.EXPECTED_EDGE_KEYS
