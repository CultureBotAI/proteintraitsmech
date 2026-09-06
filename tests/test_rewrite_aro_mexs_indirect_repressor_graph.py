from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mexs_indirect_repressor_graph.py"
TARGET = REPO / "data" / "traits" / "function" / "resistance" / "aro" / "mexs-aro3000813.yaml"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_mexs_indirect_repressor_graph",
        SCRIPT,
    )
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
        "description": "old description",
        "evidence": [
            {
                "reference": "ARO:3000553",
                "snippet": "AdeR archetype evidence",
            }
        ],
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "MexS",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic efflux",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "pump",
                        "label": "the efflux pump this determinant activates",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": "activation",
                        "label": "activation of efflux pump expression",
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
                    _edge(
                        "determinant",
                        "activation",
                        "enables (activates pump transcription)",
                        "RO:0002327",
                    ),
                    _edge(
                        "activation",
                        "pump",
                        "positively regulates (raises pump expression)",
                        "RO:0002213",
                    ),
                ],
            }
        ],
    }


def _actual_edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_enrichment_adds_the_mexs_to_mext_to_mexef_path():
    out, changed = R.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    assert list(by_node) == list(R.NODE_ORDER)
    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES
    assert ("determinant", "activation") not in _actual_edge_pairs(out)


def test_edges_get_exact_target_activator_pump_and_go_evidence():
    out, changed = R.enrich_record(_record())

    assert changed
    by_pair = {
        (edge["subject"], edge["object"]): edge
        for edge in out["causal_graphs"][0]["edges"]
    }

    all_references = {
        item["reference"]
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    }
    assert "ARO:3000553" not in all_references
    assert "ARO:3000813" in all_references
    assert "ARO:3000814" in all_references
    assert "ARO:3000798" in all_references

    suppression_refs = {
        item["reference"]
        for item in by_pair[("determinant", "suppression")]["evidence"]
    }
    assert "GO:0044092" in suppression_refs
    activation_refs = {
        item["reference"]
        for item in by_pair[("activation", "pump")]["evidence"]
    }
    assert "GO:0045893" in activation_refs


def test_enrich_record_is_idempotent():
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000813, found ARO:3000814"):
        R.enrich_record(_record("ARO:3000814"))


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump -> unmodeled"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("activation", "pump", "positively regulates", "RO:0002213")
    )

    with pytest.raises(ValueError, match="duplicate edge activation -> pump"):
        R.enrich_record(record)


def test_missing_legacy_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop(4)

    with pytest.raises(ValueError, match="missing edge\\(s\\): activation -> pump"):
        R.enrich_record(record)


def test_missing_canonical_edges_are_refused():
    out, changed = R.enrich_record(_record())
    assert changed
    out["causal_graphs"][0]["edges"].pop(5)

    with pytest.raises(ValueError, match="missing edge\\(s\\): determinant -> suppression"):
        R.enrich_record(out)


def test_enrich_text_adds_history_once():
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, TARGET)
    twice, changed_again = R.enrich_text(once, TARGET)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count("codex-causal-graph-quality") == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    enriched, changed = R.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_efflux = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("determinant", "mech0")
    )
    efflux_resistance = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("mech0", "resistance")
    )
    efflux_resistance["evidence"] = determinant_efflux["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, TARGET)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


@pytest.mark.skipif(not TARGET.is_file(), reason="MexS record absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges():
    record = yaml.safe_load(TARGET.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record))
    assert changed or out == record

    graph = next(graph for graph in out["causal_graphs"] if graph["graph_id"] == "resistance")
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES
    for edge in graph["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
