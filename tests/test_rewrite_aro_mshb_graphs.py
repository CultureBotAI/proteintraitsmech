from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mshb_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_mshb_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3004902": "antibiotic resistant mshB",
    "ARO:3004903": "isoniazid resistant mshB",
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
                "reference": "ARO:3004903",
                "snippet": "MshB deacetylates GlcNAc-Ins to produce GlcN-Ins.",
            }
        ],
    }


def _record(identifier: str = "ARO:3004903") -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": LABELS[identifier],
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
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    edges = [
        _edge("determinant", "mech0", "participates in", "RO:0000056"),
        _edge("mech0", "resistance"),
        _edge("determinant", "resistance"),
    ]

    if target.has_drug:
        nodes.insert(
            2,
            {
                "node_id": "drug0",
                "label": "isoniazid-like antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3007152",
            },
        )
        edges.append(_edge("determinant", "drug0", "confers resistance to", "ARO:2000001"))

    if target.has_reaction:
        nodes.extend(
            [
                {
                    "node_id": "deacetylation",
                    "label": "GlcNAc-Ins deacetylase activity",
                    "node_type": "MOLECULAR_FUNCTION",
                },
                {
                    "node_id": "mycothiol",
                    "label": "mycothiol synthesis",
                    "node_type": "BIOLOGICAL_PROCESS",
                },
            ]
        )
        edges.extend(
            [
                _edge("determinant", "deacetylation", "enables", "RO:0002327"),
                _edge("deacetylation", "mycothiol", "part of", "BFO:0000050"),
            ]
        )

    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": (
            "mshB is a deacetylase that is involved in the second step of "
            "mycothiol synthesis. GlcNAc-Ins is deacetylated by MshB to "
            "produce GlcN-Ins."
        ),
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": nodes,
                "edges": edges,
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


def test_target_set_matches_exact_hidden_no_ignore_mshb_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3004902",
        "ARO:3004903",
    }


def test_broad_parent_is_reduced_to_mutation_route() -> None:
    target = R.TARGETS["ARO:3004902"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == ["determinant", "mech0", "resistance"]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_isoniazid_child_gets_grounded_mshb_reaction() -> None:
    target = R.TARGETS["ARO:3004903"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "mshb_deacetylase",
        "glcn_ins",
        "mycothiol_biosynthesis",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_legacy_reaction_nodes_are_removed() -> None:
    target = R.TARGETS["ARO:3004903"]

    out, changed = R.enrich_record(_record(target.identifier), target)
    text = yaml.safe_dump(out)

    assert changed
    assert "node_id: deacetylation" not in text
    assert "object: deacetylation" not in text
    assert "node_id: mycothiol\n" not in text


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
    target = R.TARGETS["ARO:3004903"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004903, found ARO:3004902"):
        R.enrich_record(_record("ARO:3004902"), R.TARGETS["ARO:3004903"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3004903"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3004903"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_promotes_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3004903"]
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
    assert "mapping_status: REVIEWED" in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out
