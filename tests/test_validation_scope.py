"""Regression tests for the PR validation-scope decision (#515).

#515 was a *disagreement* between two lists: `mech_shared.yaml` triggered the
workflow but was absent from the scope regex, so the run started, selected
changed-mode, found no trait files, skipped both gates, and reported green. The
first version of these tests pinned that one path and derived everything else
from the set under test, so it could not have caught the same bug at any other
path (#536).

Everything below is therefore derived from the workflow YAML by parsing it, and
compared against the helper **bidirectionally**. A path may not trigger the
workflow without forcing full validation, and may not force full validation
without triggering the workflow.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "validation_scope.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate-strict.yaml"

# The one trigger that is deliberately NOT a full-validation input: a record
# change is validated by validating that record.
RECORD_TRIGGER = "data/traits/**"


def _load():
    spec = importlib.util.spec_from_file_location("validation_scope", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCOPE = _load()


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _triggers() -> dict[str, set[str]]:
    """Trigger path sets per event. PyYAML reads a bare `on:` key as True."""
    document = _workflow()
    on = document.get("on", document.get(True))
    assert on, "workflow declares no triggers"
    return {
        event: set(spec["paths"])
        for event, spec in on.items()
        if isinstance(spec, dict) and "paths" in spec
    }


def _steps() -> list[dict]:
    jobs = _workflow()["jobs"]
    assert len(jobs) == 1, "this test assumes one job; update it if that changes"
    return next(iter(jobs.values()))["steps"]


def _step(name_fragment: str) -> dict:
    matches = [s for s in _steps() if name_fragment in s.get("name", "")]
    assert len(matches) == 1, f"expected exactly one step matching {name_fragment!r}"
    return matches[0]


# --- the helper's decision ------------------------------------------------


def test_mech_shared_alone_forces_full_validation():
    """The exact #515 regression, pinned by name and not derived from the set."""
    assert SCOPE.choose_scope(["src/proteintraitsmech/schema/mech_shared.yaml"]) == ("full", [])


def test_record_only_changes_are_sorted_and_scoped():
    mode, paths = SCOPE.choose_scope(
        ["data/traits/structure/fold/z.yaml", "README.md", "data/traits/sequence/a.yml"]
    )
    assert mode == "changed"
    assert paths == ["data/traits/sequence/a.yml", "data/traits/structure/fold/z.yaml"]


def test_record_suffixes_are_matched_case_insensitively():
    """A `.YAML` record must not be silently dropped from changed-mode (#536)."""
    mode, paths = SCOPE.choose_scope(["data/traits/structure/fold/Z.YAML"])
    assert mode == "changed"
    assert paths == ["data/traits/structure/fold/Z.YAML"]


def test_docs_only_change_runs_no_record_validation():
    assert SCOPE.choose_scope(["README.md", "docs/x.md"]) == ("changed", [])


def test_outputs_are_complete_and_replace_the_changed_file(tmp_path):
    output = tmp_path / "out"
    output.write_text("pre=existing\n", encoding="utf-8")
    changed = tmp_path / "changed.txt"
    changed.write_text("stale/path.yaml\n", encoding="utf-8")
    SCOPE.write_outputs(
        "changed", ["data/traits/a.yaml"], github_output=output, changed_traits=changed
    )
    assert output.read_text(encoding="utf-8") == "pre=existing\nmode=changed\nchanged_count=1\n"
    assert changed.read_text(encoding="utf-8") == "data/traits/a.yaml\n"


# --- the two lists must agree, in both directions -------------------------


def _full_validation_triggers() -> set[str]:
    """Every full-validation input in the spelling the workflow uses.

    Exact paths appear verbatim; a directory prefix appears as ``<prefix>**``,
    because a workflow `paths:` entry has to be a glob and `choose_scope` has to
    match real repository-relative paths. Holding the two spellings to each other
    here is what stops one from drifting without the other (#606).
    """
    return set(SCOPE.FULL_VALIDATION_PATHS) | {
        prefix + SCOPE.TRIGGER_GLOB_SUFFIX for prefix in SCOPE.FULL_VALIDATION_PREFIXES
    }


@pytest.mark.parametrize("event", sorted(_triggers()))
def test_every_trigger_other_than_records_forces_full_validation(event):
    """The #515 direction: a path may not start this workflow and then be ignored.

    Derived from the workflow, compared against the helper. Deleting a path from
    FULL_VALIDATION_PATHS while it still triggers the workflow fails here.
    """
    ignored = _triggers()[event] - {RECORD_TRIGGER} - _full_validation_triggers()
    assert not ignored, f"{event} triggers on {sorted(ignored)} but scope selection ignores them"


@pytest.mark.parametrize("event", sorted(_triggers()))
def test_every_full_validation_path_triggers_the_workflow(event):
    """The converse: a full-validation input that never starts the run is dead."""
    unreachable = _full_validation_triggers() - _triggers()[event]
    assert not unreachable, f"{event} does not trigger for {sorted(unreachable)}"


@pytest.mark.parametrize("event", sorted(_triggers()))
def test_record_changes_still_trigger_the_workflow(event):
    """Without this trigger no record PR runs at all, and every test still passed (#536)."""
    assert RECORD_TRIGGER in _triggers()[event]


# --- the workflow must actually run what these tests reason about ---------


def test_scope_step_invokes_the_tested_helper():
    """`in text` was satisfied by the `on: paths` entries alone (#536)."""
    assert "scripts/validation_scope.py" in _step("Determine validation scope")["run"]


@pytest.mark.parametrize(
    ("step_name", "command", "expected_if"),
    [
        ("Strict validation (full corpus)", "scripts/validate_strict.py", "full"),
        ("Structural audit (full corpus)", "scripts/audit_causal_graphs.py", "full"),
        ("Strict validation (changed files)", "scripts/validate_strict.py", "changed"),
        ("Structural audit (changed files)", "scripts/audit_causal_graphs.py", "changed"),
    ],
)
def test_each_gate_runs_its_command_under_the_right_condition(step_name, command, expected_if):
    """Counting `if:` conditions did not notice a `run:` replaced by `echo skip` (#536)."""
    step = _step(step_name)
    assert command in step["run"], f"{step_name} does not run {command}"
    condition = step["if"]
    assert f"steps.scope.outputs.mode == '{expected_if}'" in condition
    if expected_if == "changed":
        assert "steps.scope.outputs.changed_count != '0'" in condition
        assert "changed_traits.txt" in step["run"]


def test_a_registry_change_alone_forces_full_validation():
    """The reason `data/grounding/` is a full-validation input at all (#606).

    A QUALIFIED canonical example is only valid while its registry row exists and
    agrees, so editing a registry can invalidate records no diff mentions. That is
    the same argument that puts the schema in FULL_VALIDATION_PATHS, and it is a
    prefix rather than an exact path because the registries are a directory.
    """
    mode, traits = SCOPE.choose_scope(["data/grounding/protein_registry.jsonl"])
    assert mode == "full"
    assert traits == []


def test_a_prefix_matches_only_beneath_itself():
    """`data/grounding-notes.md` is not beneath `data/grounding/`.

    A prefix test written against `data/grounding` without the separator would
    force a full corpus run for any path that merely starts with those letters.
    """
    mode, _ = SCOPE.choose_scope(["data/grounding-notes.md"])
    assert mode == "changed"


def test_the_workflow_runs_the_grounding_validator_in_both_modes():
    """`validate-all` is two halves and only the first was gated (#606).

    Asserting the script name, not the recipe: validate-strict.yaml invokes the
    scripts directly, so a test looking for `just validate-all` would pass while
    nothing ran -- and asserting mere presence in the file is satisfied by the
    `on: paths:` entries alone, which is how #536 slipped through.
    """
    steps = _steps()
    grounding = [
        step for step in steps if "scripts/validate_uniprot_grounding.py" in step.get("run", "")
    ]
    assert len(grounding) == 2, "expected a changed-files and a full-corpus grounding step"
    conditions = sorted(step.get("if", "") for step in grounding)
    assert any("mode == 'full'" in condition for condition in conditions)
    assert any("mode == 'changed'" in condition for condition in conditions)


def test_both_changed_file_steps_tolerate_a_deletion_only_list():
    """The two steps run on ONE file list, so they must agree about it (#616).

    `changed_traits.txt` can name only deleted records. `validate_strict.py` has
    tolerated that since #540; when the grounding validator joined it on the same
    list without the flag, a deletion-only PR failed the second step and passed
    the first. Asserting on both together is what keeps them symmetric, since the
    asymmetry is invisible when either step is read alone.
    """
    changed_steps = [
        step
        for step in _steps()
        if "changed_traits.txt" in step.get("run", "")
        and "validation_scope.py" not in step.get("run", "")
    ]
    assert len(changed_steps) >= 2, "expected at least the strict and grounding changed-file steps"
    for step in changed_steps:
        run = step["run"]
        if "validate_strict.py" in run or "validate_uniprot_grounding.py" in run:
            assert "--allow-missing" in run, (
                f"{step.get('name')!r} consumes the CI diff list without --allow-missing; "
                "a deletion-only change would fail it"
            )


def test_a_lockfile_bump_alone_forces_full_validation():
    """`pyproject.toml` pins a range; `uv.lock` pins what is installed (#537).

    The job runs `uv sync --extra dev`, which is lockfile-driven, so a
    `uv lock --upgrade` PR changes the validator itself while touching neither
    the schema nor a record. Without the lockfile in scope that PR never starts
    this workflow at all.
    """
    mode, traits = SCOPE.choose_scope(["uv.lock"])
    assert mode == "full"
    assert traits == []


def test_a_lockfile_bump_bundled_with_a_record_edit_still_forces_full():
    """The worse case, and the reason `changed` mode is not good enough here.

    Bundled with a record edit the workflow would otherwise select `changed` and
    validate only the diff -- under a validator nobody checked against the rest
    of the corpus, which is exactly the situation a full run exists for.
    """
    mode, traits = SCOPE.choose_scope(["uv.lock", "data/traits/sequence/a.yaml"])
    assert mode == "full"
    assert traits == []


def test_both_dependency_declarations_are_in_scope():
    """Neither file alone determines the installed validator.

    `pyproject.toml` was already here for #515's "validation dependencies"
    criterion; the lockfile is the half that says which version arrives. Listing
    them together keeps the pair visible, so removing one is a deliberate act.
    """
    assert {"pyproject.toml", "uv.lock"} <= set(SCOPE.FULL_VALIDATION_PATHS)
