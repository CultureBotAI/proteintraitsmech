from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ddla_cycloserine_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_ddla_cycloserine_graphs",
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
                "reference": "ARO:3004939",
                "snippet": "ddlA catalyzes the ATP-driven ligation of two D-alanine.",
            }
        ],
    }


def _record(identifier: str = "ARO:3004939") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "cycloserine resistant ddlA",
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
                        "node_id": "drug0",
                        "label": "cycloserine-like antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007154",
                    },
                    {
                        "node_id": "ligation",
                        "label": "D-Ala-D-Ala ligase activity (ATP-driven)",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "dala",
                        "label": "D-alanine, the substrate cycloserine resembles",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "wall_growth",
                        "label": "cell wall growth",
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
                    _edge("determinant", "drug0", "confers resistance to", "ARO:2000001"),
                    _edge("determinant", "ligation", "enables", "RO:0002327"),
                    _edge("ligation", "dala", "has input", "RO:0002233"),
                    _edge("drug0", "dala", "molecularly similar to", "RO:0002158"),
                    _edge("drug0", "wall_growth", "negatively regulates", "RO:0002212"),
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
        "cycloserine-resistant-ddla-aro3004939.yaml",
        "mycobacterium-tuberculosis-ddla-mutations-confer-resistance-to-"
        "cycloserine-aro3004941.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_enrichment_grounds_ligation_substrate_and_cell_wall_nodes(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    by_node = {
        node["node_id"]: node
        for node in out["causal_graphs"][0]["nodes"]
    }

    for node_id, node in R.SHARED_NODE_UPDATES.items():
        assert by_node[node_id] == node


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_enrichment_adds_ligation_to_peptidoglycan_biosynthesis_edge(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _actual_edge_pairs(out) == R.EXPECTED_EDGES


@pytest.mark.parametrize("target", R.TARGETS.values())
def test_all_edges_get_descriptions_and_multiple_evidence_items(target):
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_child_edges_get_child_and_parent_aro_evidence():
    target = R.TARGETS["ARO:3004941"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        if (edge["subject"], edge["object"]) != ("ligation", "dala"):
            assert "ARO:3004941" in references
        if (edge["subject"], edge["object"]) in {
            ("determinant", "ligation"),
            ("drug0", "dala"),
            ("drug0", "wall_growth"),
            ("ligation", "wall_growth"),
        }:
            assert "ARO:3004939" in references


def test_ligation_edges_get_go_activity_evidence():
    target = R.TARGETS["ARO:3004939"]

    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        if (edge["subject"], edge["object"]) in {
            ("determinant", "ligation"),
            ("ligation", "dala"),
            ("ligation", "wall_growth"),
        }:
            references = {item["reference"] for item in edge["evidence"]}
            assert "GO:0008716" in references


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3004939"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3004939, found ARO:3004941"):
        R.enrich_record(_record("ARO:3004941"), R.TARGETS["ARO:3004939"])


def test_unexpected_edges_are_refused():
    target = R.TARGETS["ARO:3004939"]
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> unmodeled"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused():
    target = R.TARGETS["ARO:3004939"]
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("drug0", "dala", "molecularly similar to", "RO:0002158")
    )

    with pytest.raises(ValueError, match="duplicate edge drug0 -> dala"):
        R.enrich_record(record, target)


def test_missing_expected_edges_are_refused():
    target = R.TARGETS["ARO:3004939"]
    record = _record()
    record["causal_graphs"][0]["edges"].pop(7)

    with pytest.raises(ValueError, match="missing edge\\(s\\): drug0 -> wall_growth"):
        R.enrich_record(record, target)


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3004939"]
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
    target = R.TARGETS["ARO:3004939"]
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
    text += "- timestamp: '2026-09-06T00:00:00Z'\n"
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
        by_node = {node["node_id"]: node for node in graph["nodes"]}

        for node_id, node in R.SHARED_NODE_UPDATES.items():
            assert by_node[node_id] == node
        assert _actual_edge_pairs(out) == R.EXPECTED_EDGES
        for edge in graph["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
