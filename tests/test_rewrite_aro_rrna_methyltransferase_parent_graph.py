from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rrna_methyltransferase_parent_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_rrna_methyltransferase_parent_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


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
                "reference": "ARO:3000164",
                "snippet": "Catalyzes methylation of rRNA.",
            }
        ],
    }


def _record(identifier: str = "ARO:3000164") -> dict:
    return {
        "identifier": identifier,
        "definition": "Catalyzes methylation of rRNA.",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "rRNA methyltransferase conferring antibiotic resistance",
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
                        "node_id": "mech1",
                        "label": "ribosomal alteration conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000211",
                    },
                    {
                        "node_id": "methyltransferase",
                        "label": "16S rRNA methyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "decoding_site",
                        "label": "16S rRNA decoding site (aminoglycoside binding site)",
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
                    _edge("determinant", "mech1", "participates in", "RO:0000056"),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "methyltransferase", "enables", "RO:0002327"),
                    _edge("methyltransferase", "methylated"),
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


def _actual_edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filename_is_generic_rrna_methyltransferase_parent():
    assert R.FILENAME == "rrna-methyltransferase-conferring-antibiotic-resistance-aro3000164.yaml"
    assert R.IDENTIFIER == "ARO:3000164"


def test_enrichment_generalizes_and_grounds_activity_and_rrna_nodes():
    out, changed = R.enrich_record(_record())

    assert changed
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node
    assert by_node["decoding_site"]["label"] == "rRNA antibiotic-binding site"
    assert "16S" not in by_node["methyltransferase"]["label"]


def test_enrichment_adds_methylated_site_to_resistance_edge():
    out, changed = R.enrich_record(_record())

    assert changed
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES


def test_all_edges_get_descriptions_and_multiple_evidence_items():
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert "ARO:3000164" in references
        assert len(references) > 1


def test_methyltransferase_edges_get_go_evidence():
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        if (edge["subject"], edge["object"]) in {
            ("determinant", "methyltransferase"),
            ("methyltransferase", "methylated"),
        }:
            references = {item["reference"] for item in edge["evidence"]}
            assert "GO:0008649" in references


def test_enrich_record_is_idempotent():
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000164, found ARO:3000857"):
        R.enrich_record(_record("ARO:3000857"))


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("methylated", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge methylated -> unmodeled"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("methylated", "decoding_site", "negatively regulates", "RO:0002212")
    )

    with pytest.raises(ValueError, match="duplicate edge methylated -> decoding_site"):
        R.enrich_record(record)


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop(7)

    with pytest.raises(ValueError, match="missing edge\\(s\\): methylated -> decoding_site"):
        R.enrich_record(record)


def test_enrich_text_adds_history_once():
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / R.FILENAME)
    twice, changed_again = R.enrich_text(once, ARO_DIR / R.FILENAME)

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
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("mech0", "resistance")
    )
    efflux_resistance["evidence"] = determinant_efflux["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / R.FILENAME)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_record_enriches_in_memory_without_unexpected_edges():
    path = ARO_DIR / R.FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    graph = next(graph for graph in out["causal_graphs"] if graph["graph_id"] == "resistance")
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert "ARO:3000164" in references
        assert len(references) > 1
