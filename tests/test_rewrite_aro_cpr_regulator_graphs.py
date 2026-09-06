from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_cpr_regulator_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_cpr_regulator_graphs",
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


def _record(identifier: str = "ARO:3005063") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "cpr determinant",
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


def test_target_filenames_are_exactly_the_expected_two():
    assert {target.filename for target in R.TARGETS.values()} == {
        "cprr-aro3005063.yaml",
        "cprs-aro3005064.yaml",
    }


def test_cpr_replaces_efflux_pump_scaffold_with_arn_induction():
    target = R.TARGETS["ARO:3005063"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert "pump" not in by_node
    assert "activation" not in by_node
    assert by_node["mech0"] == R.MECHANISM_NODE
    assert by_node["sensing"] == R.SENSING_NODE
    assert by_node["arn_operon"] == R.ARN_OPERON_NODE
    assert by_pair[("sensing", "determinant")]["predicate_id"] == "RO:0002411"
    assert by_pair[("determinant", "arn_operon")]["predicate_id"] == "RO:0002213"
    assert _actual_edge_pairs(out) == target.expected_edges


def test_cprs_edges_include_cprs_cprrs_and_arn_evidence():
    out, changed = R.enrich_record(_record("ARO:3005064"), R.TARGETS["ARO:3005064"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3005064" in references
        assert "ARO:3000553" not in references
        if edge["object"] in {"arn_operon", "mech0", "resistance"}:
            assert "ARO:3005065" in references


def test_archetype_evidence_is_replaced_with_exact_evidence():
    out, changed = R.enrich_record(_record(), R.TARGETS["ARO:3005063"])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3000553" not in references
        assert "ARO:3005063" in references
        assert len(edge["evidence"]) > 1


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3005063"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3005064, found ARO:3005063"):
        R.enrich_record(_record(), R.TARGETS["ARO:3005064"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("activation", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge activation -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3005063"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "mech0"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> mech0"):
        R.enrich_record(record, R.TARGETS["ARO:3005063"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3005063"]
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
    target = R.TARGETS["ARO:3005063"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    determinant_arn = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("determinant", "arn_operon")
    )
    arn_mechanism = next(
        edge
        for edge in edges
        if (edge["subject"], edge["object"]) == ("arn_operon", "mech0")
    )
    arn_mechanism["evidence"] = determinant_arn["evidence"]
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
