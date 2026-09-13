from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_bae_arl_efflux_activator_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_bae_arl_efflux_activator_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _edge(subject: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "causally upstream of",
        "predicate_id": "RO:0002411",
        "object": object_,
        "description": "old description",
        "evidence": [
            {
                "reference": "ARO:3000553",
                "snippet": "AdeR archetype evidence",
            }
        ],
    }


def _record(identifier: str = "ARO:3000838", bae: bool = False) -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "efflux activator",
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
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "activation"),
                    _edge("activation", "pump"),
                ],
            }
        ],
    }


def _actual_edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_filenames_are_exactly_the_expected_four():
    assert {target.filename for target in R.TARGETS.values()} == {
        "arlr-aro3000838.yaml",
        "arlrs-aro3000547.yaml",
        "baer-aro3000828.yaml",
        "baes-aro3000829.yaml",
    }


def test_arl_targets_ground_nora_and_positive_regulation():
    target = R.TARGETS["ARO:3000838"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["pump"] == R.NORA_NODE
    assert by_node["activation"] == R.NORA_ACTIVATION_NODE
    assert _actual_edge_pairs(out) == target.expected_edges
    assert by_pair[("activation", "pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("pump", "mech0")]["predicate_id"] == "RO:0002327"


def test_bae_targets_split_legacy_pump_into_mdtabc_and_acrd():
    target = R.TARGETS["ARO:3000828"]

    out, changed = R.enrich_record(_record("ARO:3000828", bae=True), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert "pump" not in by_node
    assert by_node["mdtabc_pump"] == R.MDTABC_TOLC_NODE
    assert by_node["acrd_pump"] == R.ACRD_NODE
    assert by_node["activation"] == R.BAE_ACTIVATION_NODE
    assert _actual_edge_pairs(out) == target.expected_edges
    assert by_pair[("activation", "mdtabc_pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("activation", "acrd_pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("mdtabc_pump", "mech0")]["predicate_id"] == "RO:0002327"
    assert by_pair[("acrd_pump", "mech0")]["predicate_id"] == "RO:0002327"


def test_baes_edges_include_baes_baer_and_pump_evidence():
    out, changed = R.enrich_record(_record("ARO:3000829", bae=True), R.TARGETS["ARO:3000829"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000829" in references
        assert "ARO:3000553" not in references
        if edge["object"] in {"mdtabc_pump", "acrd_pump"}:
            assert "ARO:3000828" in references
            assert "GO:0045893" in references


def test_archetype_evidence_is_replaced_with_exact_evidence():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3000838"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
        assert "ARO:3000838" in references
        assert len(edge["evidence"]) > 1


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000828"]

    once, changed = R.enrich_record(_record("ARO:3000828", bae=True), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000828, found ARO:3000838"):
        R.enrich_record(_record(), R.TARGETS["ARO:3000828"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("activation", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge activation -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000838"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "mech0"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3000838"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000838"]
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
    target = R.TARGETS["ARO:3000838"]
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
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


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
        assert _actual_edge_pairs(out) == target.expected_edges
        for edge in graph["edges"]:
            references = {item["reference"] for item in edge["evidence"]}
            assert edge["description"]
            assert len(edge["evidence"]) > 1
            assert "ARO:3000553" not in references
