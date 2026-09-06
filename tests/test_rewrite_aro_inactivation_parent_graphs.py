from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_inactivation_parent_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_inactivation_parent_graphs", SCRIPT)
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
        "evidence": [
            {
                "reference": "ARO:3000342",
                "snippet": "Enzymes that inactivate fosfomycin by chemical modification.",
            }
        ],
    }


def _record(identifier: str = "ARO:3000342") -> dict:
    return {
        "identifier": identifier,
        "definition": "definition",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "fosfomycin inactivation enzyme",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic inactivation",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001004",
                    },
                    {
                        "node_id": "modification",
                        "label": "enzymatic modification of fosfomycin",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "inactivated",
                        "label": "modified, inactive fosfomycin",
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
                    _edge("determinant", "mech0"),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge("determinant", "modification"),
                    _edge("modification", "inactivated"),
                ],
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_five():
    assert {target.filename for target in R.TARGETS.values()} == {
        "aminoglycoside-modifying-enzyme-aro3007380.yaml",
        "fosfomycin-inactivation-enzyme-aro3000342.yaml",
        "macrolide-inactivation-enzyme-aro3000201.yaml",
        "rifampin-inactivation-enzyme-aro3000576.yaml",
        "streptogramin-inactivation-enzyme-aro3000233.yaml",
    }


def test_enrichment_describes_edges_rewrites_nodes_and_adds_terminal_edge():
    target = R.TARGETS["ARO:3000342"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["modification"] == target.modification_node
    assert by_node["inactivated"] == target.inactivated_node
    assert len(by_pair) == len(R.EXPECTED_EDGES)
    assert ("inactivated", "resistance") in by_pair
    for edge in graph["edges"]:
        assert edge["description"] == R.EDGE_DESCRIPTIONS[(edge["subject"], edge["object"])]
        assert edge["evidence"] == [target.evidence]


def test_target_labels_are_drug_specific():
    for identifier, label in {
        "ARO:3007380": "chemically modified, inactive aminoglycoside antibiotic",
        "ARO:3000201": "chemically modified, inactive macrolide antibiotic",
        "ARO:3000576": "chemically modified, inactive rifampin antibiotic",
        "ARO:3000233": "chemically modified, inactive streptogramin antibiotic",
    }.items():
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
        assert by_node["inactivated"]["label"] == label


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3000342"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3000342, found ARO:3000201"):
        R.enrich_record(_record("ARO:3000201"), R.TARGETS["ARO:3000342"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("modification", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge modification -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000342"])


def test_duplicate_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("inactivated", "resistance"))
    record["causal_graphs"][0]["edges"].append(_edge("inactivated", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge inactivated -> resistance"):
        R.enrich_record(record, R.TARGETS["ARO:3000342"])


def test_missing_expected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): modification -> inactivated"):
        R.enrich_record(record, R.TARGETS["ARO:3000342"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3000342"]
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
    target = R.TARGETS["ARO:3000342"]
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
        assert ("inactivated", "resistance") in {
            (edge["subject"], edge["object"]) for edge in graph["edges"]
        }
        for edge in graph["edges"]:
            assert edge["description"]
            assert edge["evidence"] == [target.evidence]
