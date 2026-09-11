from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rv0191_pyrazinamide_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rv0191_pyrazinamide_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _parent_text(identifier: str = "ARO:3004979") -> str:
    return f"""identifier: {identifier}
label: antibiotic resistant Rv0191
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


def _child_text(identifier: str = "ARO:3004980") -> str:
    return f"""identifier: {identifier}
label: pyrazinamide resistant Rv0191
definition: A probable conserved integral membrane protein that acts as an active efflux pump.
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


def test_targets_are_exact_rv0191_parent_and_pyrazinamide_child() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004979",
        "ARO:3004980",
    }


def test_parent_draft_graph_is_removed() -> None:
    out, changed = R.repair_parent_text(_parent_text())

    assert changed
    assert "causal_graphs:" not in out
    assert "mapping_status: SEEDED" in out
    assert R.PARENT_ACTION in out


def test_pyrazinamide_child_gets_efflux_graph() -> None:
    out, changed = R.curate_child_text(_child_text())
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
    assert R.CHILD_ACTION in out


def test_rewrites_are_idempotent() -> None:
    parent_once, parent_changed = R.repair_parent_text(_parent_text())
    parent_twice, parent_changed_again = R.repair_parent_text(parent_once)
    child_once, child_changed = R.curate_child_text(_child_text())
    child_twice, child_changed_again = R.curate_child_text(child_once)

    assert parent_changed
    assert child_changed
    assert not parent_changed_again
    assert not child_changed_again
    assert parent_twice == parent_once
    assert child_twice == child_once
    assert parent_once.count(R.PARENT_ACTION) == 1
    assert child_once.count(R.CHILD_ACTION) == 1


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004979, found ARO:3004980"):
        R.repair_parent_text(_child_text())
    with pytest.raises(ValueError, match="expected ARO:3004980, found ARO:3004979"):
        R.curate_child_text(_parent_text())


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_records_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = R.enrich_text(text, target.path)

        assert changed or out == text
        assert target.action in out
