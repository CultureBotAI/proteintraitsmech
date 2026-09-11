from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_bypass_parent_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_bypass_parent_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record_text(identifier: str = "ARO:3000012") -> str:
    return f"""identifier: {identifier}
label: broad bypass parent
definition: Broad bypass parent definition
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


def test_targets_are_exact_broad_parent_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3000012",
        "ARO:3002976",
    }


@pytest.mark.parametrize("target", R.TARGETS)
def test_draft_graphs_are_removed(target: R.Target) -> None:
    out, changed = R.enrich_text(
        _record_text(target.identifier),
        ARO_DIR / target.filename,
    )

    assert changed
    assert "causal_graphs:" not in out
    assert target.action in _history_actions(out)


def test_enrich_text_is_idempotent() -> None:
    path = ARO_DIR / R.BYPASS_PARENT.filename

    once, changed = R.enrich_text(_record_text(), path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert _history_actions(once).count(R.BYPASS_ACTION) == 1


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000012, found ARO:3002976"):
        R.enrich_text(
            _record_text("ARO:3002976"),
            ARO_DIR / R.BYPASS_PARENT.filename,
        )


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = R.enrich_text(before, path)

        assert changed or after == before
        assert "causal_graphs:" not in after
        assert target.action in _history_actions(after)
