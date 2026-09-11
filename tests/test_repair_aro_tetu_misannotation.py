from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "repair_aro_tetu_misannotation.py"
TARGET = (
    REPO
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "tet-u-aro3004650.yaml"
)


def _load():
    spec = importlib.util.spec_from_file_location("repair_aro_tetu_misannotation", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


REPAIR = _load()


def _record_text(identifier: str = "ARO:3004650") -> str:
    return f"""identifier: {identifier}
label: tet(U)
definition: negative control
mapping_status: REVIEWED
causal_graphs:
- graph_id: resistance
  title: wrong graph
  nodes:
  - node_id: determinant
    label: tet(U)
    node_type: PROTEIN
    grounding: ARO:3004650
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


def test_repair_text_removes_graph_and_reverts_to_seeded() -> None:
    out, changed = REPAIR.repair_text(_record_text())

    assert changed
    assert "causal_graphs:" not in out
    assert "mapping_status: SEEDED" in out
    assert REPAIR.HISTORY_ACTION in out


def test_repair_text_adds_history_once() -> None:
    once, changed = REPAIR.repair_text(_record_text())
    twice, changed_again = REPAIR.repair_text(once)

    assert changed
    assert not changed_again
    assert twice == once
    assert once.count(REPAIR.HISTORY_ACTION) == 1


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004650, found ARO:3004653"):
        REPAIR.repair_text(_record_text("ARO:3004653"))


@pytest.mark.skipif(not TARGET.is_file(), reason="tet(U) record absent")
def test_shipped_tetu_record_is_repaired_in_memory() -> None:
    text = TARGET.read_text(encoding="utf-8")
    out, changed = REPAIR.repair_text(text, TARGET)

    assert changed or out == text
    assert "causal_graphs:" not in out
    assert "mapping_status: SEEDED" in out
