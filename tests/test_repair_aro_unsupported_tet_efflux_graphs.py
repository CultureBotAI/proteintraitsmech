from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "repair_aro_unsupported_tet_efflux_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "repair_aro_unsupported_tet_efflux_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


REPAIR = _load()


def _record_text(target: REPAIR.Target) -> str:
    return f"""identifier: {target.identifier}
label: tet test
definition: unsupported efflux graph
mapping_status: REVIEWED
causal_graphs:
- graph_id: resistance
  title: wrong graph
  nodes:
  - node_id: determinant
    label: tet test
    node_type: PROTEIN
    grounding: {target.identifier}
  - node_id: resistance
    label: resistance
    node_type: PHENOTYPE
    grounding: GO:0046677
  edges:
  - subject: determinant
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: resistance
    evidence:
    - reference: PMID:38974671
curation_history:
  - timestamp: "2026-07-21T00:00:00Z"
    curator: edison-causal-graphs
    action: "Promoted auto-draft to curated causal_graphs with family verbatim snippets; SEEDED -> REVIEWED"
    llm_assisted: true
license: CC-BY 4.0
"""


def test_targets_are_exact_unsupported_efflux_records() -> None:
    assert {target.identifier for target in REPAIR.TARGETS} == {
        "ARO:3004650",
        "ARO:3004653",
    }


@pytest.mark.parametrize("target", REPAIR.TARGETS)
def test_repair_text_removes_graph_and_reverts_to_seeded(target: REPAIR.Target) -> None:
    out, changed = REPAIR.repair_text(_record_text(target), target)

    assert changed
    assert "causal_graphs:" not in out
    assert "mapping_status: SEEDED" in out
    assert target.history_action in out


@pytest.mark.parametrize("target", REPAIR.TARGETS)
def test_repair_text_adds_history_once(target: REPAIR.Target) -> None:
    once, changed = REPAIR.repair_text(_record_text(target), target)
    twice, changed_again = REPAIR.repair_text(once, target)

    assert changed
    assert not changed_again
    assert twice == once
    assert once.count(target.history_action) == 1


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004650, found ARO:3004653"):
        REPAIR.repair_text(_record_text(REPAIR.TARGETS[1]), REPAIR.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", REPAIR.TARGETS)
def test_shipped_records_are_repaired_in_memory(target: REPAIR.Target) -> None:
    text = target.path.read_text(encoding="utf-8")
    out, changed = REPAIR.repair_text(text, target, target.path)

    assert changed or out == text
    assert "causal_graphs:" not in out
    assert "mapping_status: SEEDED" in out
