from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_lipid_a_acyltransferase_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_lipid_a_acyltransferase_graph",
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
                "snippet": R.LIPID_A_ACYLTRANSFERASE_DEFINITION,
            }
        ],
    }


def _record() -> dict:
    return {
        "identifier": R.IDENTIFIER,
        "label": "lipid A acyltransferase",
        "definition": R.LIPID_A_ACYLTRANSFERASE_DEFINITION,
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
                        "label": "lipid A acyltransferase",
                        "node_type": "PROTEIN",
                        "grounding": R.IDENTIFIER,
                    },
                    {
                        "node_id": "mech0",
                        "label": "charge alteration conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3003588",
                    },
                    {
                        "node_id": "drug0",
                        "label": "peptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000053",
                    },
                    {
                        "node_id": "aminoacylation",
                        "label": "aminoacylation of lipopolysaccharide",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "charge",
                        "label": "reduced net negative surface charge",
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
                        "drug0",
                        "confers resistance to",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "aminoacylation",
                        "enables (aminoacylates LPS)",
                        "RO:0002327",
                    ),
                    _edge(
                        "aminoacylation",
                        "charge",
                        "causally upstream of (decreases negative charge)",
                    ),
                    _edge(
                        "charge",
                        "drug0",
                        "negatively regulates (impedes drug binding)",
                        "RO:0002212",
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


def test_target_is_exact_lipid_a_acyltransferase_parent() -> None:
    assert R.IDENTIFIER == "ARO:3004363"
    assert R.FILENAME == "lipid-a-acyltransferase-aro3004363.yaml"


def test_lipid_a_acyltransferase_replaces_ungrounded_aminoacylation() -> None:
    out, changed = R.enrich_record(_record())
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "drug0",
        "aminoacylated_lps",
        "charge",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "aminoacylation" not in nodes
    assert nodes["aminoacylated_lps"]["node_type"] == "STATE"


def test_lipid_a_acyltransferase_connects_charge_to_resistance() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert ("charge", "RO:0002411", "resistance") in _edge_keys(out)
    assert ("charge", "RO:0002212", "drug0") in _edge_keys(out)


def test_all_non_state_nodes_are_grounded_and_edges_are_described() -> None:
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
    record["identifier"] = "ARO:3004364"

    with pytest.raises(ValueError, match="expected ARO:3004363, found ARO:3004364"):
        R.enrich_record(record)


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("aminoacylation", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge aminoacylation -> unmodeled"):
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
