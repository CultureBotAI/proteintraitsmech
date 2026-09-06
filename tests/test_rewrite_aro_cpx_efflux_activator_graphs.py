from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cpx_efflux_activator_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cpx_efflux_activator_graphs",
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


def _record(identifier: str = "ARO:3000524") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "cpx determinant",
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
        "cpxa-aro3000830.yaml",
        "cpxar-aro3000524.yaml",
        "cpxr-aro3000831.yaml",
        "pseudomonas-aeruginosa-cpxr-aro3004054.yaml",
    }


def test_cpxar_targets_split_legacy_pump_into_acrd_and_mdtabc():
    target = R.TARGETS["ARO:3000524"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert "pump" not in by_node
    assert by_node["acrd_pump"] == R.ACRD_NODE
    assert by_node["mdtabc_pump"] == R.MDTABC_TOLC_NODE
    assert by_node["activation"] == R.ACTIVATION_NODE
    assert _actual_edge_pairs(out) == target.expected_edges
    assert by_pair[("activation", "acrd_pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("activation", "mdtabc_pump")]["predicate_id"] == "RO:0002213"
    assert by_pair[("acrd_pump", "mech0")]["predicate_id"] == "RO:0002327"
    assert by_pair[("mdtabc_pump", "mech0")]["predicate_id"] == "RO:0002327"


def test_cpxr_targets_split_legacy_pump_into_acrd_and_mexab():
    target = R.TARGETS["ARO:3000831"]

    out, changed = R.enrich_record(_record("ARO:3000831"), target)

    assert changed
    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}

    assert "pump" not in by_node
    assert by_node["acrd_pump"] == R.ACRD_NODE
    assert by_node["mexab_pump"] == R.MEXAB_OPRM_NODE
    assert _actual_edge_pairs(out) == target.expected_edges


def test_pseudomonas_cpxr_targets_mexab_oprm():
    target = R.TARGETS["ARO:3004054"]

    out, changed = R.enrich_record(_record("ARO:3004054"), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["mexab_pump"] == R.MEXAB_OPRM_NODE
    assert "acrd_pump" not in by_node
    assert "mdtabc_pump" not in by_node
    assert by_pair[("activation", "mexab_pump")]["predicate_id"] == "RO:0002213"
    assert _actual_edge_pairs(out) == target.expected_edges


def test_cpxa_edges_include_cpxa_cpxar_and_pump_evidence():
    out, changed = R.enrich_record(_record("ARO:3000830"), R.TARGETS["ARO:3000830"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000830" in references
        assert "ARO:3000553" not in references
        if edge["object"] in {"acrd_pump", "mdtabc_pump"}:
            assert "ARO:3000524" in references
            assert "GO:0045893" in references


def test_archetype_evidence_is_replaced_with_exact_evidence():
    out, changed = R.enrich_record(_record("ARO:3004054"), R.TARGETS["ARO:3004054"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
        assert "ARO:3004054" in references
        assert len(edge["evidence"]) > 1


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000831"]

    once, changed = R.enrich_record(_record("ARO:3000831"), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000524, found ARO:3000831"):
        R.enrich_record(_record("ARO:3000831"), R.TARGETS["ARO:3000524"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("activation", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge activation -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000524"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "mech0"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3000524"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000524"]
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
    target = R.TARGETS["ARO:3000524"]
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
