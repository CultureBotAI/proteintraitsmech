from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_mutant_efflux_regulator_parent_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_mutant_efflux_regulator_parent_graph",
        SCRIPT,
    )
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
                "reference": R.IDENTIFIER,
                "snippet": R.MUTANT_REGULATOR_EVIDENCE["snippet"],
            }
        ],
    }


def _record() -> dict:
    return {
        "identifier": R.IDENTIFIER,
        "label": "mutant efflux regulatory protein conferring antibiotic resistance",
        "definition": R.MUTANT_REGULATOR_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "mutant efflux regulatory protein",
                        "node_type": "PROTEIN",
                        "grounding": R.IDENTIFIER,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "pump_expression",
                        "label": "expression of efflux pump proteins",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "efflux_process",
                        "label": "antibiotic efflux",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge(
                        "determinant",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "determinant",
                        "pump_expression",
                        "positively regulates (mutation raises pump expression)",
                        "RO:0002213",
                    ),
                    _edge(
                        "pump_expression",
                        "efflux_process",
                        "causally upstream of (more pump, more efflux)",
                    ),
                    _edge(
                        "efflux_process",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _nodes_by_id(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def test_target_is_exact_mutant_efflux_regulator_parent() -> None:
    assert R.IDENTIFIER == "ARO:3000219"
    assert (
        R.FILENAME
        == "mutant-efflux-regulatory-protein-conferring-antibiotic-resistance-aro3000219.yaml"
    )


def test_mutant_efflux_regulator_parent_rewrites_pump_expression_to_state() -> None:
    out, changed = R.enrich_record(_record())
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "pump_expression",
        "efflux_process",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert nodes["pump_expression"]["node_type"] == "STATE"
    assert nodes["pump_expression"]["description"]


def test_positive_regulation_and_efflux_path_are_preserved() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert ("determinant", "RO:0002213", "pump_expression") in _edge_keys(out)
    assert ("pump_expression", "RO:0002411", "efflux_process") in _edge_keys(out)
    assert ("efflux_process", "RO:0002411", "resistance") in _edge_keys(out)


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_supported_by_multiple_references() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        references = {
            evidence["reference"]
            for evidence in edge["evidence"]
            if evidence.get("reference")
        }
        assert len(references) > 1
        assert R.IDENTIFIER in references


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    record = _record()
    record["identifier"] = "ARO:3000212"

    with pytest.raises(ValueError, match="expected ARO:3000219, found ARO:3000212"):
        R.enrich_record(record)


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): efflux_process -> resistance"):
        R.enrich_record(record)


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump_expression", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump_expression -> unmodeled"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record)


def test_enrich_text_appends_history_once_and_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / R.FILENAME
    text = yaml.safe_dump(_record(), sort_keys=False)

    out, changed = R.enrich_text(text, path)
    second, changed_again = R.enrich_text(out, path)

    assert changed
    assert not changed_again
    assert second == out
    assert out.count(R.HISTORY_ACTION) == 1
