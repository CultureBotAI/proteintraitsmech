"""Unit tests for scripts/validate_strict.py.

Locks in:
- Closed-mode catches unknown top-level fields (the failure mode
  proteintraitsmech#485 is about: `validate-all` advertised closed-mode
  but batched open-mode `linkml-validate` CLI calls).
- Closed-mode also catches unknown nested fields (inside a nested
  attribute like `evolutionary_scope`), not just top-level ones.
- Missing required attributes surface as ERROR rows.
- The error classifier categorizes messages into known buckets.
- iter_yaml_files filters non-YAML and walks directories.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_strict import (  # noqa: E402
    classify,
    iter_yaml_files,
    main,
    validate_one,
)


# ---------------------------------------------------------------- classify


@pytest.mark.parametrize(
    "message, expected_category",
    [
        (
            "Additional properties are not allowed ('bogus_field' was unexpected) in /",
            "unexpected_field",
        ),
        # jsonschema switches to a plural verb and a key list for two or more, which
        # the singular-only pattern bucketed as "other" -- under-reporting the one
        # category closed mode exists to produce (#541).
        (
            "Additional properties are not allowed ('bogus_one', 'bogus_two' were unexpected) in /",
            "unexpected_field",
        ),
        (
            "Additional properties are not allowed ('a', 'b', 'c' were unexpected) in /x/0",
            "unexpected_field",
        ),
        ("'identifier' is a required property in /", "missing_required"),
        ("'foo' is not one of ['bar', 'baz']", "enum_mismatch"),
        (
            "'PTM_BAD' does not match '^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$'",
            "pattern_mismatch",
        ),
        ("Something totally weird happened", "other"),
    ],
)
def test_classify_buckets(message, expected_category):
    cat, _detail = classify(message)
    assert cat == expected_category


def test_classify_unexpected_field_extracts_name():
    _cat, detail = classify(
        "Additional properties are not allowed ('bogus_field' was unexpected) in /"
    )
    assert "bogus_field" in detail


# ---------------------------------------------------------------- validate_one


# Minimal valid ProteinTraitRecord that satisfies the closed-mode schema
# (identifier, label, trait_axis are the only required attributes).
_VALID_RECORD = """\
identifier: proteintraitsmech:TEST_RECORD
label: test trait
trait_axis: SEQUENCE
"""


def test_validate_one_clean_yaml_produces_no_errors(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_VALID_RECORD)
    errors = validate_one(p)
    assert errors == []


def test_validate_one_unknown_top_level_field_fails(tmp_path):
    """Closed-mode must flag an unknown top-level field. This is the
    proteintraitsmech#485 gate: the old batched-CLI validate-all let this
    pass silently."""
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "unexpected_field" in cats


def test_validate_one_unknown_nested_field_fails(tmp_path):
    """Closed-mode must also flag an unknown field nested inside a
    non-scalar attribute (evolutionary_scope), not just at the top level."""
    p = tmp_path / "bogus_nested.yaml"
    p.write_text(
        _VALID_RECORD
        + "evolutionary_scope:\n"
        + "  min_prevalence: 0.1\n"
        + "  max_prevalence: 0.9\n"
        + "  bogus_nested_field: oops\n"
    )
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "unexpected_field" in cats


def test_validate_one_missing_required_field_fails(tmp_path):
    """A ProteinTraitRecord without `identifier` must fail validation."""
    p = tmp_path / "missing.yaml"
    p.write_text("label: test trait\ntrait_axis: SEQUENCE\n")
    errors = validate_one(p)
    assert len(errors) >= 1
    cats = {e["category"] for e in errors}
    assert "missing_required" in cats


def test_validate_one_yaml_parse_error_surfaces_as_row(tmp_path):
    p = tmp_path / "broken.yaml"
    p.write_text("identifier: proteintraitsmech:TEST\n  not: aligned\n garbage:\n: bad\n")
    errors = validate_one(p)
    assert any(e["category"] == "yaml_parse_error" for e in errors)


# ---------------------------------------------------------------- iter_yaml_files


def test_iter_yaml_files_walks_directory_and_filters(tmp_path):
    (tmp_path / "a.yaml").write_text("x: 1\n")
    (tmp_path / "b.yml").write_text("x: 2\n")  # .yml — skipped by rglob('*.yaml')
    (tmp_path / "c.txt").write_text("nope")  # non-YAML — skipped
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.yaml").write_text("y: 3\n")

    out = iter_yaml_files([tmp_path])
    names = {p.name for p in out}
    # rglob('*.yaml') only picks .yaml (not .yml) when walking a directory
    assert "a.yaml" in names
    assert "d.yaml" in names
    assert "b.yml" not in names
    assert "c.txt" not in names


def test_iter_yaml_files_accepts_yml_file_passed_directly(tmp_path):
    """When a .yml file is passed *as a file argument* (not via dir walk),
    iter_yaml_files accepts it — only the directory rglob is .yaml-only."""
    yml = tmp_path / "explicit.yml"
    yml.write_text("x: 1\n")
    txt = tmp_path / "explicit.txt"
    txt.write_text("nope")

    out = iter_yaml_files([yml, txt])
    names = {p.name for p in out}
    assert "explicit.yml" in names
    assert "explicit.txt" not in names


# ---------------------------------------------------------------- main


def test_main_writes_tsv_header_and_returns_zero_when_clean(tmp_path):
    p = tmp_path / "ok.yaml"
    p.write_text(_VALID_RECORD)
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet"])
    assert rc == 0
    assert out.read_text().splitlines()[0] == "file\tcategory\tdetail\tpath\tmessage"


def test_main_returns_one_and_writes_error_row_on_failure(tmp_path):
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet"])
    assert rc == 1
    rows = out.read_text().splitlines()
    assert len(rows) == 2  # header + one ERROR row
    assert "unexpected_field" in rows[1]


def test_main_fail_on_never_still_returns_zero_on_failure(tmp_path):
    p = tmp_path / "bogus.yaml"
    p.write_text(_VALID_RECORD + "bogus_field: oops\n")
    out = tmp_path / "out.tsv"
    rc = main([str(p), "--out", str(out), "--workers", "1", "--quiet", "--fail-on", "never"])
    assert rc == 0


def test_main_returns_two_when_default_scope_has_no_files(tmp_path, monkeypatch):
    import validate_strict

    monkeypatch.setattr(validate_strict, "DEFAULT_ROOTS", [tmp_path / "does_not_exist"])
    assert main([]) == 2


def test_main_refuses_a_supplied_path_that_does_not_exist(tmp_path, capsys):
    """A mistyped path must not report success (#540).

    Returning 0 here made the hardened gate weaker on this axis than the open-mode
    CLI it replaced, which exits 2. `just validate <typo>` printed nothing alarming
    and exited 0, so a curator could reasonably report "validated, closed mode" for
    a file that was never opened.
    """
    missing = tmp_path / "gone.yaml"
    rc = main([str(missing), "--out", str(tmp_path / "out.tsv")])
    assert rc == 2
    assert "None of the supplied paths exist" in capsys.readouterr().err


def test_main_allows_missing_paths_only_when_asked(tmp_path):
    """The deletion-only CI diff stays valid, but opts in rather than being assumed.

    A PR that only deletes records supplies a file list where nothing exists; that
    is not an error for the CI caller (#488), and is an error for a human typing a
    path (#540). The difference is now explicit.
    """
    missing = tmp_path / "gone.yaml"
    rc = main(["--allow-missing", str(missing), "--out", str(tmp_path / "out.tsv")])
    assert rc == 0


# ---------------------------------------------------------------- just recipes


def _dry_run_just(*args: str) -> str:
    result = subprocess.run(
        ["just", "--dry-run", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout + result.stderr


def test_just_validate_delegates_to_the_closed_validator():
    command = _dry_run_just("validate", "record with spaces.yaml")
    assert "scripts/validate_strict.py" in command
    assert "--workers 1" in command
    assert "linkml-validate" not in command
    assert "'record with spaces.yaml'" in command


def test_just_validate_exits_non_zero_on_a_path_that_does_not_exist(tmp_path):
    """The assertion whose absence let #540 through.

    The recipe tests above inspect `just --dry-run` text, which proves what would be
    run but never that running it fails. This executes the recipe for real.
    """
    result = subprocess.run(
        ["just", "validate", str(tmp_path / "definitely-not-here.yaml")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, result.stdout + result.stderr


def test_ci_opts_in_to_missing_paths_so_deletion_only_prs_still_pass():
    """The workflow and the flag must stay together (#540).

    If the changed-files step stops passing --allow-missing, a deletion-only PR
    fails CI for a reason that has nothing to do with the records it deleted.
    """
    workflow = (REPO_ROOT / ".github" / "workflows" / "validate-strict.yaml").read_text(
        encoding="utf-8"
    )
    changed_invocation = [
        line
        for line in workflow.splitlines()
        if "validate_strict.py" in line and "${files[@]}" in line
    ]
    assert len(changed_invocation) == 1, changed_invocation
    assert "--allow-missing" in changed_invocation[0]


def test_reference_cli_is_explicitly_separate_from_the_gate():
    command = _dry_run_just("validate-reference", "record.yaml")
    assert "linkml-validate" in command
    assert "scripts/validate_strict.py" not in command
