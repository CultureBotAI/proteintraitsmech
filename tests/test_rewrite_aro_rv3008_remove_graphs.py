from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rv3008_remove_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rv3008_remove_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record_text(identifier: str) -> str:
    return f"""identifier: {identifier}
label: Rv3008 test
definition: May contribute to resistance.
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


def test_targets_are_exact_rv3008_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {"ARO:3004988", "ARO:3004989"}


@pytest.mark.parametrize("target", R.TARGETS)
def test_draft_graphs_are_removed(target: R.Target) -> None:
    out, changed = R.remove_graph_text(_record_text(target.identifier), target)

    assert changed
    assert "causal_graphs:" not in out
    assert target.action in _history_actions(out)


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
    with pytest.raises(ValueError, match="expected ARO:3004988, found ARO:3004989"):
        R.remove_graph_text(_record_text(R.PYRAZINAMIDE_PARENT.identifier), R.BROAD_PARENT)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_records_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = R.enrich_text(text, target.path)

        assert changed or out == text
        assert target.action in _history_actions(out)
