from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rv1667_pyrazinamide_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rv1667_pyrazinamide_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record_text(identifier: str) -> str:
    return f"""identifier: {identifier}
label: Rv1667 test
definition: Mutations in Rv1667 can confer pyrazinamide resistance.
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


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _history_actions(text: str) -> list[str]:
    return [
        event["action"]
        for event in yaml.safe_load(text)["curation_history"]
    ]


def test_targets_are_exact_rv1667_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004982",
        "ARO:3004983",
        "ARO:3004984",
    }


@pytest.mark.parametrize("target", R.PARENTS)
def test_parent_draft_graphs_are_removed(target: R.Target) -> None:
    out, changed = R.repair_parent_text(_record_text(target.identifier), target)

    assert changed
    assert "causal_graphs:" not in out
    assert target.action in _history_actions(out)


def test_mtb_child_gets_efflux_graph() -> None:
    out, changed = R.curate_child_text(_record_text(R.CHILD.identifier))
    record = yaml.safe_load(out)
    graph = record["causal_graphs"][0]

    assert changed
    assert record["mapping_status"] == "REVIEWED"
    assert graph["graph_id"] == "resistance"
    assert {node["node_id"] for node in graph["nodes"]} == {
        "determinant",
        "mutation",
        "efflux",
        "drug0",
        "resistance",
    }
    assert _edge_pairs(record) == {
        ("determinant", "mutation"),
        ("determinant", "efflux"),
        ("efflux", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
    }
    for edge in graph["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
    assert R.CHILD.action in out


def test_rewrites_are_idempotent() -> None:
    for target in R.TARGETS:
        text = _record_text(target.identifier)
        once, changed = R.enrich_text(text, target.path)
        twice, changed_again = R.enrich_text(once, target.path)

        assert changed
        assert not changed_again
        assert twice == once
        assert _history_actions(once).count(target.action) == 1


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004982, found ARO:3004984"):
        R.repair_parent_text(_record_text(R.CHILD.identifier), R.ANTIBIOTIC_PARENT)
    with pytest.raises(ValueError, match="expected ARO:3004984, found ARO:3004982"):
        R.curate_child_text(_record_text(R.ANTIBIOTIC_PARENT.identifier))


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_records_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = R.enrich_text(text, target.path)

        assert changed or out == text
        assert target.action in _history_actions(out)
