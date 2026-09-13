from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_target_modifying_parent_graph.py"
ARO_FILE = (
    REPO
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "antibiotic-target-modifying-enzyme-aro3000519.yaml"
)


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_target_modifying_parent_graph", SCRIPT)
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
                "reference": "PMID:40643688",
                "snippet": "Aminoglycoside-resistance methyltransferases modify 16S rRNA.",
            }
        ],
    }


def _record(identifier: str = R.IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "antibiotic target modifying enzyme",
        "definition": "Enzymes that confer resistance by modifying antibiotic targets.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "description": "old graph",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "antibiotic target modifying enzyme",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic target alteration",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001001",
                    },
                    {
                        "node_id": "methyltransferase",
                        "label": "16S rRNA methyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "decoding_site",
                        "label": "16S rRNA decoding site",
                        "node_type": "NUCLEIC_ACID",
                    },
                    {
                        "node_id": "methylated",
                        "label": "methylated decoding site",
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
                    _edge("determinant", "mech0", "participates in", "RO:0000056"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "methyltransferase",
                        "enables (16S rRNA methylation)",
                        "RO:0002327",
                    ),
                    _edge(
                        "methyltransferase",
                        "methylated",
                        "causally upstream of (methylates the site)",
                    ),
                    _edge(
                        "methylated",
                        "decoding_site",
                        "negatively regulates",
                        "RO:0002212",
                    ),
                ],
            }
        ],
    }


def _by_node(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_parent_is_reduced_to_grounded_target_alteration_route() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    nodes = _by_node(out)
    assert nodes == {
        "determinant": {
            "node_id": "determinant",
            "label": "antibiotic target modifying enzyme",
            "node_type": "PROTEIN",
            "grounding": R.IDENTIFIER,
        },
        "mech0": R.MECHANISM_NODE,
        "resistance": R.RESISTANCE_NODE,
    }
    assert _edge_keys(out) == R.CANONICAL_EDGES
    assert out["causal_graphs"][0]["description"] == R.GRAPH_DESCRIPTION


def test_edges_get_descriptions_multi_reference_evidence_and_no_16s_nodes() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    text = yaml.safe_dump(out, sort_keys=False)
    assert "node_id: methyltransferase" not in text
    assert "node_id: decoding_site" not in text
    assert "node_id: methylated" not in text
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert all(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000519, found ARO:3000164"):
        R.enrich_record(_record("ARO:3000164"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("methylated", "resistance", "causally upstream of")
    )

    with pytest.raises(ValueError, match="unexpected edge methylated -> resistance"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "methyltransferase",
            "methylated",
            "causally upstream of (methylates the site)",
        )
    )

    with pytest.raises(ValueError, match="duplicate edge methyltransferase -> methylated"):
        R.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = R.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, pathlib.Path(R.FILENAME))

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    record = yaml.safe_load(ARO_FILE.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record))
    assert changed or out == record
