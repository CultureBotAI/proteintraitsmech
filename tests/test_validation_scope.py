"""Regression tests for the PR validation-scope decision (#515)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validation_scope.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate-strict.yaml"


def _load():
    spec = importlib.util.spec_from_file_location("validation_scope", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCOPE = _load()


@pytest.mark.parametrize("path", sorted(SCOPE.FULL_VALIDATION_PATHS))
def test_every_declared_infrastructure_path_forces_full_validation(path):
    assert SCOPE.choose_scope([path]) == ("full", [])


def test_mech_shared_alone_forces_full_validation():
    assert SCOPE.choose_scope([
        "src/proteintraitsmech/schema/mech_shared.yaml",
    ]) == ("full", [])


def test_record_only_changes_are_sorted_and_scoped():
    mode, paths = SCOPE.choose_scope([
        "data/traits/structure/fold/z.yaml",
        "README.md",
        "data/traits/function/pathway/a.yml",
        "data/traits/function/pathway/a.yml",
    ])
    assert mode == "changed"
    assert paths == [
        "data/traits/function/pathway/a.yml",
        "data/traits/structure/fold/z.yaml",
    ]


def test_docs_only_change_runs_no_record_validation():
    assert SCOPE.choose_scope(["README.md"]) == ("changed", [])


def test_outputs_are_complete_and_replace_the_changed_file(tmp_path):
    github_output = tmp_path / "github-output"
    changed_traits = tmp_path / "changed.txt"
    changed_traits.write_text("stale\n", encoding="utf-8")

    SCOPE.write_outputs(
        "changed",
        ["data/traits/sequence/motif/example.yaml"],
        github_output=github_output,
        changed_traits=changed_traits,
    )

    assert github_output.read_text(encoding="utf-8") == "mode=changed\nchanged_count=1\n"
    assert changed_traits.read_text(encoding="utf-8") == (
        "data/traits/sequence/motif/example.yaml\n"
    )


def test_workflow_uses_the_tested_scope_and_runs_both_full_gates():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/validation_scope.py" in text
    assert text.count("if: steps.scope.outputs.mode == 'full'") == 2


def test_workflow_triggers_cover_every_full_validation_path():
    triggers = WORKFLOW.read_text(encoding="utf-8").split("permissions:", 1)[0]
    missing = SCOPE.FULL_VALIDATION_PATHS - {
        path for path in SCOPE.FULL_VALIDATION_PATHS if path in triggers
    }
    assert not missing, f"workflow does not trigger for full-validation inputs: {missing}"
