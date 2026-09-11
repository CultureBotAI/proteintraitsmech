from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ahpc_overexpression_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_ahpc_overexpression_graph",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, predicate_id: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [{"reference": "ARO:3004921"}],
    }


def _record(identifier: str = "ARO:3004921") -> dict:
    return {
        "identifier": identifier,
        "label": "Mycobacterium tuberculosis ahpC mutations confer resistance to isoniazid",
        "definition": (
            "Mutations that occur in ahpC that result in ahpC overexpression thus "
            "conferring or contributing to resistance to isoniazid."
        ),
        "mapping_status": "SEEDED",
        "evidence": [
            {
                "reference": "DOI:10.1046/j.1365-2958.1996.449980.x",
                "notes": "PMID:8830260 (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0"},
                    {"node_id": "drug0"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    _edge("determinant", "RO:0000056", "mech0"),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0002411", "resistance"),
                    _edge("determinant", "ARO:2000001", "drug0"),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _parent_text(identifier: str) -> str:
    return f"""identifier: {identifier}
label: ahpC parent
definition: parent definition
mapping_status: SEEDED
causal_graphs:
- graph_id: resistance-draft
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
  edges: []
license: CC-BY 4.0
"""


def _history_actions(text: str) -> list[str]:
    return [
        event["action"]
        for event in yaml.safe_load(text)["curation_history"]
    ]


def test_targets_are_exact_ahpc_family() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004893",
        "ARO:3004894",
        "ARO:3004921",
    }


@pytest.mark.parametrize("target", R.PARENTS)
def test_parent_draft_graphs_are_removed(target: R.Target) -> None:
    out, changed = R.enrich_text(_parent_text(target.identifier), ARO_DIR / target.filename)

    assert changed
    assert "causal_graphs:" not in out
    assert target.action in _history_actions(out)


def test_enrich_record_adds_overexpression_route() -> None:
    out, changed = R.enrich_record(_record(), R.TARGET)

    graph = out["causal_graphs"][0]
    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert graph["graph_id"] == "resistance"
    assert _edge_keys(out) == set(R.FINAL_EDGE_ORDER)
    assert [node["node_id"] for node in graph["nodes"]] == [
        "determinant",
        "mech0",
        "drug0",
        "overexpression",
        "resistance",
    ]
    assert any(
        edge["subject"] == "overexpression" and edge["object"] == "resistance"
        for edge in graph["edges"]
    )
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_edges_carry_child_definition_and_source_citation() -> None:
    out, _ = R.enrich_record(_record(), R.TARGET)

    for edge in out["causal_graphs"][0]["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert "ARO:3004921" in references
        assert "DOI:10.1046/j.1365-2958.1996.449980.x" in references


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGET)
    twice, changed_again = R.enrich_record(once, R.TARGET)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET.filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert _history_actions(once).count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004921, found ARO:3004893"):
        R.enrich_record(_record("ARO:3004893"), R.TARGET)
    with pytest.raises(ValueError, match="expected ARO:3004893, found ARO:3004894"):
        R.enrich_text(
            _parent_text("ARO:3004894"),
            ARO_DIR / R.BROAD_PARENT.filename,
        )


def test_missing_drug_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:3]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, R.TARGET)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    for target in R.PARENTS:
        path = ARO_DIR / target.filename
        out, changed = R.enrich_text(path.read_text(encoding="utf-8"), path)
        assert changed or out == path.read_text(encoding="utf-8")
        assert target.action in _history_actions(out)

    path = ARO_DIR / R.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(copy.deepcopy(record), R.TARGET)

    assert changed or out == record
    assert _edge_keys(out) == set(R.FINAL_EDGE_ORDER)
