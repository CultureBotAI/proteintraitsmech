from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fusb_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fusb_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load()


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
                "reference": F.PARENT_IDENTIFIER,
                "snippet": F.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(target: object | None = None, identifier: str | None = None) -> dict:
    if target is None:
        target = F.TARGETS["ARO:3003552"]
    if identifier is None:
        identifier = target.identifier
    return {
        "identifier": identifier,
        "label": "fusB",
        "definition": F.PARENT_EVIDENCE["snippet"],
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
                        "label": "fusB",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic target protection",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001003",
                    },
                    {
                        "node_id": "drug0",
                        "label": "fusidane antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007153",
                    },
                    {
                        "node_id": "efg",
                        "label": "elongation factor G (EF-G), the drug's target",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": "stalled",
                        "label": "stalled ribosome-EF-G-GDP complex",
                        "node_type": "STATE",
                    },
                    {
                        "node_id": "zinc_finger",
                        "label": "four-cysteine zinc finger domain of FusB-type proteins",
                        "node_type": "DOMAIN",
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
                        "zinc_finger",
                        "determinant",
                        "part of (the EF-G-binding domain)",
                        "BFO:0000050",
                    ),
                    _edge("drug0", "stalled"),
                    _edge(
                        "determinant",
                        "stalled",
                        "negatively regulates (dissociates the stalled complex)",
                        "RO:0002212",
                    ),
                    _edge(
                        "determinant",
                        "efg",
                        "molecularly interacts with (binds the target)",
                        "RO:0002436",
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


def test_targets_match_exact_fusb_type_records() -> None:
    assert set(F.TARGETS) == {
        "ARO:3005086",
        "ARO:3003552",
        "ARO:3003733",
        "ARO:3003731",
        "ARO:3004663",
    }
    assert {target.filename for target in F.TARGETS.values()} == {
        "target-protecting-fusb-type-protein-conferring-resistance-to-fusidic-acid-aro3005086.yaml",
        "fusb-aro3003552.yaml",
        "fusc-aro3003733.yaml",
        "fusd-aro3003731.yaml",
        "fusf-aro3004663.yaml",
    }


def test_fusb_type_records_rewrite_to_stalled_complex_route() -> None:
    out, changed = F.enrich_record(_record(), F.TARGETS["ARO:3003552"])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "stalled",
        "resistance",
    ]
    assert _edge_keys(out) == F.EXPECTED_EDGE_KEYS


def test_efg_and_zinc_finger_side_details_are_removed() -> None:
    out, changed = F.enrich_record(_record(), F.TARGETS["ARO:3003552"])

    assert changed
    assert "efg" not in _node_ids(out)
    assert "zinc_finger" not in _node_ids(out)
    assert F.REMOVED_SIDE_EDGE_KEYS.isdisjoint(_edge_keys(out))


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = F.enrich_record(_record(), F.TARGETS["ARO:3003552"])

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = F.enrich_record(_record(), F.TARGETS["ARO:3003552"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_drug_relation_evidence_distinguishes_parent_from_children() -> None:
    parent = F._drug_relation_evidence(F.TARGETS["ARO:3005086"])
    child = F._drug_relation_evidence(F.TARGETS["ARO:3003552"])

    assert "asserted directly" in parent["notes"]
    assert "inherited by ARO:3003552" in child["notes"]


def test_enrich_record_is_idempotent() -> None:
    once, changed = F.enrich_record(_record(), F.TARGETS["ARO:3003552"])
    twice, changed_again = F.enrich_record(once, F.TARGETS["ARO:3003552"])

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003552, found ARO:3003553"):
        F.enrich_record(_record(identifier="ARO:3003553"), F.TARGETS["ARO:3003552"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("stalled", "drug0"))

    with pytest.raises(ValueError, match="unexpected edge stalled -> drug0"):
        F.enrich_record(record, F.TARGETS["ARO:3003552"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        F.enrich_record(record, F.TARGETS["ARO:3003552"])


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        F.enrich_record(record, F.TARGETS["ARO:3003552"])


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = F.TARGETS["ARO:3003552"]
    enriched, changed = F.enrich_record(_record(target), target)
    assert changed

    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = F.enrich_text(text, ARO_DIR / target.filename, target)
    again, changed_again = F.enrich_text(out, ARO_DIR / target.filename, target)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(F.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", list(F.TARGETS.values()))
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: object,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = F.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == F.EXPECTED_EDGE_KEYS
