from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_axyz_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_axyz_graphs", SCRIPT)
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
        "description": "old description",
        "evidence": [
            {
                "reference": "ARO:3000219",
                "snippet": R.MUTANT_REGULATOR_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "AxyZ",
        "definition": R.AXYZ_DEFINITION,
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "AxyZ",
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
                        "node_id": "pump_expression",
                        "label": "expression of efflux pump proteins",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "description": "The regulated quantity. Ungrounded.",
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
                        "mech1",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech1", "resistance"),
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


def test_target_set_matches_exact_hidden_no_ignore_axyz_search() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {R.TARGET_IDENTIFIER}
    assert {target.filename for target in R.TARGETS.values()} == {R.TARGET_FILENAME}


def test_axyz_record_is_grounded_through_named_efflux_pump() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]
    out, changed = R.enrich_record(_record(), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "mech1",
        "pump",
        "pump_expression",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "efflux_process" not in nodes
    assert nodes["pump"]["grounding"] == "ARO:3004141"
    assert nodes["pump_expression"]["node_type"] == "STATE"
    assert "Ungrounded" not in nodes["pump_expression"]["description"]


def test_all_edges_are_described_and_supported_by_multiple_references() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]
    out, changed = R.enrich_record(_record(), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert len(references) > 1
        assert "ARO:3004141" in references or "ARO:3000212" in references
        assert "ARO:3000702" not in references


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.TARGET_IDENTIFIER]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004145, found ARO:3004141"):
        R.enrich_record(_record("ARO:3004141"), R.TARGETS[R.TARGET_IDENTIFIER])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump -> unmodeled"):
        R.enrich_record(record, R.TARGETS[R.TARGET_IDENTIFIER])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGETS[R.TARGET_IDENTIFIER])
