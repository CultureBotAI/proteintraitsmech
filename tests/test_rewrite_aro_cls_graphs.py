from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cls_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_cls_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3003272": "daptomycin resistant cls",
    "ARO:3003074": "Staphylococcus aureus cls conferring resistance to daptomycin",
    "ARO:3003092": "Enterococcus faecium cls conferring resistance to daptomycin",
    "ARO:3003760": "Enterococcus faecalis cls with mutation conferring resistance to daptomycin",
}


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
                "reference": "ARO:3003272",
                "snippet": "Cardiolipin synthetase mutations confer resistance to daptomycin.",
            }
        ],
    }


def _record(identifier: str = "ARO:3003272") -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": (
            "Cardiolipin synthetase catalyzes the formation of cardiolipin "
            "from two phosphatidylglycerol molecules. Current known mutations "
            "on the enzyme confer resistance to daptomycin."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "daptomycin resistant cls",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "drug0",
                        "label": "peptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000053",
                    },
                    {
                        "node_id": "cl_synthesis",
                        "label": "cardiolipin synthase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "cardiolipin",
                        "label": "cardiolipin",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "membrane_role",
                        "label": "membrane translocation and permeabilization",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    _edge("determinant", "mech0", "participates in", "RO:0000056"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "drug0", "confers resistance to", "ARO:2000001"),
                    _edge("determinant", "cl_synthesis", "enables", "RO:0002327"),
                    _edge("cl_synthesis", "cardiolipin", "has output", "RO:0002234"),
                    _edge("cardiolipin", "membrane_role", "participates in", "RO:0000056"),
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


def test_target_set_matches_exact_hidden_no_ignore_cls_subtree() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3003272",
        "ARO:3003074",
        "ARO:3003092",
        "ARO:3003760",
    }


def test_cls_graph_is_grounded_and_drops_membrane_side_path() -> None:
    target = R.TARGETS["ARO:3003272"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "cardiolipin_synthase_activity",
        "cardiolipin",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys()
    text = yaml.safe_dump(out)
    assert "membrane_role" not in text
    assert "cl_synthesis" not in text


def test_all_output_nodes_are_grounded() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        assert all(node.get("grounding") for node in out["causal_graphs"][0]["nodes"])


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])
            assert len(
                {(item["reference"], item["snippet"]) for item in edge["evidence"]}
            ) == len(edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3003272"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003272, found ARO:3003092"):
        R.enrich_record(_record("ARO:3003092"), R.TARGETS["ARO:3003272"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3003272"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3003272"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_canonical_output_is_accepted() -> None:
    target = R.TARGETS["ARO:3003272"]
    once, changed = R.enrich_record(_record(target.identifier), target)

    again, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert again == once


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3003272"]
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
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out
