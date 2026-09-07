from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ngon_mtrr_graph.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_ngon_mtrr_graph",
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
                "reference": "PMID:19166984",
                "snippet": "stale RND transporter evidence.",
            }
        ],
    }


def _record() -> dict:
    return {
        "identifier": R.IDENTIFIER,
        "label": "Neisseria gonorrhoeae mtrR with mutation conferring resistance",
        "definition": R.TARGET_EVIDENCE["snippet"],
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
                        "label": "Neisseria gonorrhoeae mtrR mutant",
                        "node_type": "PROTEIN",
                        "grounding": R.IDENTIFIER,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic efflux",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "domain",
                        "label": "RND transporter domain",
                        "node_type": "DOMAIN",
                        "grounding": "Pfam:PF00873",
                    },
                    {
                        "node_id": "fold",
                        "label": "AcrB pore-domain fold",
                        "node_type": "DOMAIN",
                        "grounding": "CATH:3.30.70.1430",
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
                        "domain",
                        "determinant",
                        "part of (domain of the protein)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "determinant",
                        "fold",
                        "member of (adopts fold)",
                        "RO:0002350",
                    ),
                    _edge(
                        "domain",
                        "mech0",
                        "enables (drug efflux)",
                        "RO:0002327",
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


def test_target_is_exact_neisseria_mtrr_mutant() -> None:
    assert R.IDENTIFIER == "ARO:3004851"
    assert (
        R.FILENAME
        == "neisseria-gonorrhoeae-mtrr-with-mutation-conferring-resistance-aro3004851.yaml"
    )


def test_ngon_mtrr_mutant_replaces_stale_rnd_side_nodes() -> None:
    out, changed = R.enrich_record(_record())
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "pump",
        "repression",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "domain" not in nodes
    assert "fold" not in nodes
    assert R.OBSOLETE_RND_EDGE_KEYS.isdisjoint(_edge_keys(out))


def test_ngon_mtrr_mutant_adds_mtrcde_derepression_route() -> None:
    out, changed = R.enrich_record(_record())
    nodes = _nodes_by_id(out)

    assert changed
    assert nodes["pump"]["grounding"] == "ARO:3000369"
    assert nodes["repression"]["grounding"] == "GO:0045892"
    assert ("determinant", "RO:0002212", "repression") in _edge_keys(out)
    assert ("repression", "RO:0002212", "pump") in _edge_keys(out)
    assert ("pump", "RO:0002327", "mech0") in _edge_keys(out)


def test_all_output_nodes_are_grounded_and_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    for edge in graph["edges"]:
        references = {
            evidence["reference"]
            for evidence in edge["evidence"]
            if evidence.get("reference")
        }
        assert edge.get("description")
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
    record["identifier"] = "ARO:3000817"

    with pytest.raises(ValueError, match="expected ARO:3004851, found ARO:3000817"):
        R.enrich_record(record)


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].pop(0)

    with pytest.raises(ValueError, match="missing edge\\(s\\): determinant -> mech0"):
        R.enrich_record(record)


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("domain", "fold"))

    with pytest.raises(ValueError, match="unexpected edge domain -> fold"):
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
