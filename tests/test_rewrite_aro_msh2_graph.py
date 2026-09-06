from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_msh2_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_msh2_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


M = _load()


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
                "reference": M.IDENTIFIER,
                "snippet": "MSH2 is a mismatch repair gene in fungi.",
            }
        ],
    }


def _record(identifier: str = M.IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "antifungal resistance-associated MSH2",
        "definition": (
            "MSH2 is a mismatch repair gene in fungi. Strains with alterations "
            "in this gene exhibit the resistance to Polyenes (Amphotericin B), "
            "Echinocandins (Caspofungin, Micafungin), and Azoles "
            "(Fluconazole, Voriconazole)."
        ),
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
                        "label": "antifungal resistance-associated MSH2",
                        "node_type": "PROTEIN",
                        "grounding": M.IDENTIFIER,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "mismatch_repair",
                        "label": "DNA mismatch repair",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "description": "Ungrounded: not looked up rather than guessed.",
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
                        "mismatch_repair",
                        "participates in (DNA mismatch repair)",
                        "RO:0000056",
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


def test_msh2_graph_grounds_mismatch_repair_without_hypermutation() -> None:
    out, changed = M.enrich_record(_record())

    assert changed
    assert _edge_keys(out) == M.EXPECTED_EDGE_KEYS
    graph = out["causal_graphs"][0]
    assert [node["node_id"] for node in graph["nodes"]] == [
        "determinant",
        "mech0",
        "mismatch_repair",
        "resistance",
    ]
    mismatch_repair = next(
        node for node in graph["nodes"] if node["node_id"] == "mismatch_repair"
    )
    assert mismatch_repair["grounding"] == "GO:0006298"
    assert "hypermutation" in graph["description"]
    assert "hypermutation" not in yaml.safe_dump(graph["edges"])


def test_all_output_nodes_are_grounded_and_edges_described() -> None:
    out, changed = M.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    assert all(node.get("grounding") for node in graph["nodes"])
    assert all(edge.get("description") for edge in graph["edges"])
    assert all(len({item["reference"] for item in edge["evidence"]}) > 1 for edge in graph["edges"])


def test_mutation_edges_inherit_broad_aro_mutation_evidence() -> None:
    out, changed = M.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"][:3]:
        assert "ARO:3000212" in {item["reference"] for item in edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    once, changed = M.enrich_record(_record())
    twice, changed_again = M.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3009134, found ARO:wrong"):
        M.enrich_record(_record("ARO:wrong"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mismatch_repair", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge mismatch_repair -> resistance"):
        M.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        M.enrich_record(record)


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "mismatch_repair"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        M.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = M.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = M.enrich_text(text, ARO_DIR / M.FILENAME)
    again, changed_again = M.enrich_text(out, ARO_DIR / M.FILENAME)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(M.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / M.FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = M.enrich_record(record)

    assert changed or out == record
    assert _edge_keys(out) == M.EXPECTED_EDGE_KEYS
