from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_vat_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_vat_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


V = _load()


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
                "reference": V.PARENT_IDENTIFIER,
                "snippet": V.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(target: object | None = None, identifier: str | None = None) -> dict:
    if target is None:
        target = V.TARGETS["ARO:3002840"]
    if identifier is None:
        identifier = target.identifier
    return {
        "identifier": identifier,
        "label": "vatA",
        "definition": V.PARENT_EVIDENCE["snippet"],
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
                        "label": "vatA",
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
                        "label": "acylation of antibiotic conferring resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000106",
                    },
                    {
                        "node_id": "drug0",
                        "label": "streptogramin antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:0000026",
                    },
                    {
                        "node_id": "acetylation",
                        "label": "streptogramin A acetyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "acetyl_coa",
                        "label": "acetyl-CoA (the acetyl donor)",
                        "node_type": "CHEMICAL",
                        "grounding": "CHEBI:15351",
                    },
                    {
                        "node_id": "modified",
                        "label": "acetylated, inactive streptogramin A",
                        "node_type": "STATE",
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
                        "acetylation",
                        "enables (acetylates the drug)",
                        "RO:0002327",
                    ),
                    _edge(
                        "acetylation",
                        "acetyl_coa",
                        "has input (the acetyl donor)",
                        "RO:0002233",
                    ),
                    _edge(
                        "acetylation",
                        "drug0",
                        "has input (the drug)",
                        "RO:0002233",
                    ),
                    _edge(
                        "acetylation",
                        "modified",
                        "causally upstream of (inactivates the drug)",
                    ),
                    _edge(
                        "modified",
                        "drug0",
                        "negatively regulates (the acetylated drug is inactive)",
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


def test_targets_match_exact_vat_records() -> None:
    assert set(V.TARGETS) == {
        "ARO:3000453",
        "ARO:3002840",
        "ARO:3002841",
        "ARO:3002842",
        "ARO:3002843",
        "ARO:3002844",
        "ARO:3003744",
        "ARO:3002845",
        "ARO:3003987",
    }


def test_vat_records_rewrite_to_grounded_acylation_route() -> None:
    out, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "acetyl_coa",
        "modified",
        "resistance",
    ]
    assert _edge_keys(out) == V.EXPECTED_EDGE_KEYS


def test_redundant_acetylation_function_is_removed() -> None:
    out, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])

    assert changed
    assert "acetylation" not in _node_ids(out)
    assert V.REMOVED_EDGE_KEYS.isdisjoint(_edge_keys(out))
    assert ("mech1", "RO:0002233", "acetyl_coa") in _edge_keys(out)
    assert ("mech1", "RO:0002233", "drug0") in _edge_keys(out)
    assert ("mech1", "RO:0002411", "modified") in _edge_keys(out)


def test_old_graph_without_inactive_product_edge_is_accepted() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if (edge["subject"], edge["object"]) != ("modified", "drug0")
    ]

    out, changed = V.enrich_record(record, V.TARGETS["ARO:3002840"])

    assert changed
    assert _edge_keys(out) == V.EXPECTED_EDGE_KEYS


def test_modified_streptogramin_remains_described_state() -> None:
    out, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])

    assert changed
    modified = out["causal_graphs"][0]["nodes"][5]
    assert modified["node_id"] == "modified"
    assert modified["node_type"] == "STATE"
    assert modified["description"]


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_drug_relation_evidence_distinguishes_parent_from_children() -> None:
    parent = V._drug_relation_evidence(V.TARGETS["ARO:3000453"])
    child = V._drug_relation_evidence(V.TARGETS["ARO:3002840"])

    assert "asserted directly" in parent["notes"]
    assert "inherited by ARO:3002840" in child["notes"]


def test_enrich_record_is_idempotent() -> None:
    once, changed = V.enrich_record(_record(), V.TARGETS["ARO:3002840"])
    twice, changed_again = V.enrich_record(once, V.TARGETS["ARO:3002840"])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002840, found ARO:3002846"):
        V.enrich_record(_record(identifier="ARO:3002846"), V.TARGETS["ARO:3002840"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("modified", "mech1"))

    with pytest.raises(ValueError, match="unexpected edge modified -> mech1"):
        V.enrich_record(record, V.TARGETS["ARO:3002840"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech1", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech1 -> resistance"):
        V.enrich_record(record, V.TARGETS["ARO:3002840"])


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        V.enrich_record(record, V.TARGETS["ARO:3002840"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = V.TARGETS["ARO:3002840"]
    enriched, changed = V.enrich_record(_record(target), target)
    assert changed

    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = V.enrich_text(text, ARO_DIR / target.filename, target)
    again, changed_again = V.enrich_text(out, ARO_DIR / target.filename, target)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(V.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", list(V.TARGETS.values()))
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: object,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = V.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == V.EXPECTED_EDGE_KEYS
