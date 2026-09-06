from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mshc_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_mshc_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3004889": "antibiotic resistant mshC",
    "ARO:3004890": "ethionamide resistant mshC",
    "ARO:3004904": "isoniazid resistant mshC",
    "ARO:3004927": "Mycobacterium tuberculosis mshC mutations conferring resistance to isoniazid",
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
                "reference": "ARO:3004904",
                "snippet": "mshC catalyzes condensation of GlcN-Ins and L-cysteine.",
            }
        ],
    }


def _record(identifier: str = "ARO:3004904") -> dict:
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
                "label": target.drug_relation_label,
                "node_type": "CHEMICAL",
                "grounding": target.drug_relation_object,
            },
        )
        edges.append(_edge("determinant", "drug0", "confers resistance to", "ARO:2000001"))

    if target.identifier in {"ARO:3004904", "ARO:3004927"}:
        nodes.extend(
            [
                {
                    "node_id": "condensation",
                    "label": "ATP-dependent GlcN-Ins / L-cysteine ligase activity",
                    "node_type": "MOLECULAR_FUNCTION",
                },
                {
                    "node_id": "cys_glcn_ins",
                    "label": "L-Cys-GlcN-Ins",
                    "node_type": "CHEMICAL",
                },
            ]
        )
        edges.extend(
            [
                _edge("determinant", "condensation", "enables", "RO:0002327"),
                _edge("condensation", "cys_glcn_ins", "has output", "RO:0002234"),
            ]
        )

    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": (
            "Mutations that occur on the mshC gene resulting in resistance. "
            "It catalyzes the ATP-dependent condensation of GlcN-Ins and "
            "L-cysteine to form L-Cys-GlcN-Ins."
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


def test_target_set_matches_exact_hidden_no_ignore_mshc_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3004889",
        "ARO:3004890",
        "ARO:3004904",
        "ARO:3004927",
    }


def test_broad_parent_is_reduced_to_mutation_route() -> None:
    target = R.TARGETS["ARO:3004889"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == ["determinant", "mech0", "resistance"]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_drug_parent_without_existing_reaction_gets_mshc_reaction() -> None:
    target = R.TARGETS["ARO:3004890"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "mshc_ligase",
        "cys_glcn_ins",
        "mycothiol_biosynthesis",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys(target)


def test_isoniazid_records_replace_legacy_reaction_nodes() -> None:
    target = R.TARGETS["ARO:3004927"]

    out, changed = R.enrich_record(_record(target.identifier), target)
    text = yaml.safe_dump(out)

    assert changed
    assert "node_id: condensation" not in text
    assert "object: condensation" not in text
    assert "cys_glcn_ins" in text
    assert ("mshc_ligase", "RO:0002234", "cys_glcn_ins") in _edge_keys(out)


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
    target = R.TARGETS["ARO:3004904"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004904, found ARO:3004890"):
        R.enrich_record(_record("ARO:3004890"), R.TARGETS["ARO:3004904"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3004904"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3004904"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_promotes_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3004890"]
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
