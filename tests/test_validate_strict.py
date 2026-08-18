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

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_strict import (  # noqa: E402
    classify,
    iter_yaml_files,
    validate_one,
)


# ---------------------------------------------------------------- classify


@pytest.mark.parametrize("message, expected_category", [
    ("Additional properties are not allowed ('bogus_field' was unexpected) in /",
     "unexpected_field"),
    ("'identifier' is a required property in /", "missing_required"),
    ("'foo' is not one of ['bar', 'baz']", "enum_mismatch"),
    ("'PTM_BAD' does not match '^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$'", "pattern_mismatch"),
    ("Something totally weird happened", "other"),
])
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
    (tmp_path / "b.yml").write_text("x: 2\n")        # .yml — skipped by rglob('*.yaml')
    (tmp_path / "c.txt").write_text("nope")          # non-YAML — skipped
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
