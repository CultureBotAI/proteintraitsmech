from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fluoroquinolone_parent_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_fluoroquinolone_parent_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


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
                "snippet": R.TARGET_EVIDENCE["snippet"],
            }
        ],
    }


def _record() -> dict:
    return {
        "identifier": R.IDENTIFIER,
        "label": "fluoroquinolone resistant DNA topoisomerase",
        "definition": R.TARGET_EVIDENCE["snippet"],
        "mapping_status": "SEEDED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "fluoroquinolone resistant DNA topoisomerase",
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
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_parent_adds_fluoroquinolone_inhibition_state() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "inhibition",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    drug = next(
        node
        for node in out["causal_graphs"][0]["nodes"]
        if node["node_id"] == "drug0"
    )
    assert drug["grounding"] == "ARO:0000001"


def test_all_output_edges_are_multi_evidenced_and_described() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge.get("description")
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    record = _record()
    record["identifier"] = "ARO:3000864"

    with pytest.raises(ValueError, match="expected ARO:3000452, found ARO:3000864"):
        R.enrich_record(record)


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("inhibition", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge inhibition -> resistance"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record)


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing initial edge"):
        R.enrich_record(record)


def test_partial_canonical_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge(
            "drug0",
            "inhibition",
            "causally upstream of (inhibits target topoisomerases)",
            "RO:0002411",
        )
    )

    with pytest.raises(ValueError, match="partial canonical edge"):
        R.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = R.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / R.FILENAME)
    again, changed_again = R.enrich_text(out, ARO_DIR / R.FILENAME)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(
    not (ARO_DIR / R.FILENAME).is_file(),
    reason="fluoroquinolone parent absent",
)
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / R.FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record)

    assert changed or out == record
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
