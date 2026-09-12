from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_beta_glucan_synthase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_beta_glucan_synthase_graphs", SCRIPT)
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
                "reference": "ARO:3007548",
                "snippet": "Mutations in FKS2 confer resistance to echinocandin antibiotic micafungin.",
            }
        ],
    }


def _record(identifier: str = "ARO:3007548") -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": "beta-1,3-D-glucan synthase",
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

    if target.drug_relation_reference is not None:
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

    if target.include_cell_wall:
        nodes.extend(
            [
                {
                    "node_id": "glucan_synthesis",
                    "label": "beta-1,3-glucan synthase activity",
                    "node_type": "MOLECULAR_FUNCTION",
                },
                {
                    "node_id": "cell_wall",
                    "label": "fungal cell wall production",
                    "node_type": "BIOLOGICAL_PROCESS",
                },
            ]
        )
        edges.extend(
            [
                _edge("determinant", "glucan_synthesis", "enables", "RO:0002327"),
                _edge("glucan_synthesis", "cell_wall", "part of", "BFO:0000050"),
            ]
        )

    return {
        "identifier": identifier,
        "label": "beta-1,3-D-glucan synthase",
        "definition": (
            "Fungal beta-1,3-D-glucan synthases include mutations to confer "
            "resistance to antifungal drug compounds."
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


def test_target_set_matches_exact_hidden_no_ignore_beta_glucan_synthase_chain() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3007545",
        "ARO:3007546",
        "ARO:3007548",
    }


def test_antifungal_parent_is_grounded_without_a_drug_node() -> None:
    target = R.TARGETS["ARO:3007545"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "glucan_synthase_activity",
        "beta_glucan_biosynthesis",
        "resistance",
    ]
    assert _edge_keys(out) == R._output_expected_edges(target)
    assert out["causal_graphs"][0]["graph_id"] == "resistance"


def test_echinocandin_parent_keeps_drug_class_edge() -> None:
    target = R.TARGETS["ARO:3007546"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert "drug0" in _node_ids(out)
    assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)


def test_fks2_child_gets_fungal_cell_wall_node() -> None:
    target = R.TARGETS["ARO:3007548"]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert "node_id: glucan_synthesis" not in yaml.safe_dump(out)
    assert "node_id: cell_wall" not in yaml.safe_dump(out)
    assert "fungal_cell_wall_biogenesis" in _node_ids(out)
    assert ("beta_glucan_biosynthesis", "BFO:0000050", "fungal_cell_wall_biogenesis") in _edge_keys(
        out
    )


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3007548"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007548, found ARO:3007546"):
        R.enrich_record(_record("ARO:3007546"), R.TARGETS["ARO:3007548"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3007548"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3007548"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_promotes_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3007548"]
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
