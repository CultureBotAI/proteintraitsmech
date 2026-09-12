from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_evga_efflux_activator_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_evga_efflux_activator_graph",
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
                "reference": "ARO:3000553",
                "snippet": "AdeR archetype evidence",
            }
        ],
    }


def _record(identifier: str = "ARO:3000832") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "evgA",
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
                        "enables (activates the pump operon)",
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


def test_target_filename_is_evga():
    assert R.FILENAME == "evga-aro3000832.yaml"
    assert R.IDENTIFIER == "ARO:3000832"


def test_enrichment_replaces_generic_pump_with_both_evgA_pumps():
    out, changed = R.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    assert by_node["emrky_tolc"] == R.EMRKY_TOLC.node
    assert by_node["mdtef_tolc"] == R.MDTEF_TOLC.node
    assert by_node["activation"] == R.ACTIVATION_NODE
    assert "pump" not in by_node


def test_enrichment_adds_activation_and_efflux_edges_for_both_pumps():
    out, changed = R.enrich_record(_record())

    assert changed
    assert _actual_edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "activation"),
        ("activation", "emrky_tolc"),
        ("activation", "mdtef_tolc"),
        ("emrky_tolc", "mech0"),
        ("mdtef_tolc", "mech0"),
    }


def test_stale_ader_evidence_is_replaced_with_exact_evidence():
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
        assert "ARO:3000832" in references
        assert len(references) > 1


def test_pump_specific_edges_get_their_pump_evidence():
    out, changed = R.enrich_record(_record())

    assert changed
    by_pair = {
        (edge["subject"], edge["object"]): edge
        for edge in out["causal_graphs"][0]["edges"]
    }
    for pump in R.PUMPS:
        activation_edge = by_pair[("activation", pump.node_id)]
        efflux_edge = by_pair[(pump.node_id, "mech0")]

        assert "GO:0045893" in {
            item["reference"] for item in activation_edge["evidence"]
        }
        assert pump.grounding in {
            item["reference"]
            for item in activation_edge["evidence"] + efflux_edge["evidence"]
        }


def test_enrich_record_is_idempotent():
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000832, found ARO:3000508"):
        R.enrich_record(_record("ARO:3000508"))


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("activation", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge activation -> unmodeled"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("activation", "pump", "positively regulates", "RO:0002213")
    )

    with pytest.raises(ValueError, match="duplicate edge activation -> pump"):
        R.enrich_record(record)


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop(4)

    with pytest.raises(ValueError, match="missing edge\\(s\\): activation -> pump"):
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
def test_shipped_evga_record_enriches_without_unexpected_edges():
    path = ARO_DIR / R.FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    graph = next(graph for graph in out["causal_graphs"] if graph["graph_id"] == "resistance")
    by_node = {node["node_id"]: node for node in graph["nodes"]}

    assert by_node["emrky_tolc"] == R.EMRKY_TOLC.node
    assert by_node["mdtef_tolc"] == R.MDTEF_TOLC.node
    assert by_node["activation"] == R.ACTIVATION_NODE
    assert _actual_edge_pairs(out) == set(R.EDGE_ORDER)
    for edge in graph["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
        assert R.IDENTIFIER in references
