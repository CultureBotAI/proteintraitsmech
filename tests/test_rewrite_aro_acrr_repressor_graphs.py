from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_acrr_repressor_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_acrr_repressor_graphs", SCRIPT)
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
        "evidence": [
            {
                "reference": "ARO:3000702",
                "snippet": (
                    "AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. "
                    "AcrR mutations result in high level antibiotic resistance."
                ),
            }
        ],
    }


def _record(identifier: str = "ARO:3000702") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "acrR",
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
                        "node_id": "mech1",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "pump",
                        "label": "the efflux pump this determinant represses",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": "repression",
                        "label": "repression of efflux pump expression",
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
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "mech1"),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "repression",
                        "enables (represses the pump operon)",
                        "RO:0002327",
                    ),
                    _edge(
                        "repression",
                        "pump",
                        "negatively regulates (holds pump expression down)",
                        "RO:0002212",
                    ),
                    _edge(
                        "determinant",
                        "repression",
                        "negatively regulates (mutation lifts the repression)",
                        "RO:0002212",
                    ),
                ],
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_four():
    assert {target.filename for target in R.TARGETS.values()} == {
        "acrr-aro3000702.yaml",
        "enterobacter-aerogenes-acrr-with-mutation-conferring-multidrug-antibiotic-resist-aro3003374.yaml",
        "escherichia-coli-acrab-tolc-with-acrr-mutation-conferring-resistance-to-ciproflo-aro3003807.yaml",
        "klebsiella-pneumoniae-acrr-with-mutation-conferring-multidrug-antibiotic-resista-aro3003373.yaml",
    }


def test_enrichment_grounds_shared_nodes_replaces_wildtype_edge_and_adds_pump_edge():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000702"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["pump"] == R.PUMP_NODE
    assert by_node["repression"] == R.REPRESSION_NODE
    assert len(by_pair) == len(R.EXPECTED_EDGES)
    assert ("pump", "mech0") in by_pair
    assert R.OBSOLETE_EDGE not in {
        (edge["subject"], edge["predicate_id"], edge["object"]) for edge in graph["edges"]
    }
    assert by_pair[("determinant", "repression")]["predicate_id"] == "RO:0002212"
    for edge in graph["edges"]:
        assert edge["description"] == R.EDGE_DESCRIPTIONS[(edge["subject"], edge["object"])]


def test_species_targets_get_their_direct_aro_definition():
    target = R.TARGETS["ARO:3003807"]

    out, changed = R.enrich_record(_record("ARO:3003807"), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3003807" in references


def test_efflux_edges_get_acrab_tolc_evidence():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000702"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        if (edge["subject"], edge["object"]) in {
            ("determinant", "mech0"),
            ("mech0", "resistance"),
            ("determinant", "resistance"),
            ("repression", "pump"),
            ("pump", "mech0"),
        }:
            references = {item["reference"] for item in edge["evidence"]}
            assert "ARO:3000384" in references


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000702"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000702, found ARO:3003373"):
        R.enrich_record(_record("ARO:3003373"), R.TARGETS["ARO:3000702"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000702"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("pump", "mech0", "enables (drug efflux)", "RO:0002327")
    )
    record["causal_graphs"][0]["edges"].append(
        _edge("pump", "mech0", "enables (drug efflux)", "RO:0002327")
    )

    with pytest.raises(ValueError, match="duplicate edge pump -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3000702"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop(6)

    with pytest.raises(ValueError, match="missing edge\\(s\\): repression -> pump"):
        R.enrich_record(record, R.TARGETS["ARO:3000702"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000702"]
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count("codex-causal-graph-quality") == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    target = R.TARGETS["ARO:3000702"]
    enriched, changed = R.enrich_record(_record(), target)
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
    text += "- timestamp: '2026-09-05T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += f"  action: {R.HISTORY_ACTION}\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_enriched_in_memory_without_unexpected_edges():
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        out, changed = R.enrich_record(copy.deepcopy(record), target)
        assert changed or out == record
        graph = next(
            graph for graph in out["causal_graphs"] if graph["graph_id"] == "resistance"
        )
        by_node = {node["node_id"]: node for node in graph["nodes"]}
        by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}
        assert by_node["pump"]["grounding"] == "ARO:3000384"
        assert by_node["repression"]["grounding"] == "GO:0045892"
        assert ("pump", "mech0") in by_pair
        assert ("determinant", "repression") in by_pair
        for edge in graph["edges"]:
            assert edge["description"]
