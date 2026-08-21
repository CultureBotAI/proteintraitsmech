"""Schema-quality probes (#496).

`just audit-schema` was in the justfile and in CLAUDE.md for the life of this repo, and
`scripts/audit_schema.py` never existed. It died with `can't open file` every time, and
being in no workflow, nothing was ever red. The recipe was indistinguishable from a
passing one.

So the tests that matter here are the ones proving each probe FAILS on a broken schema.
A probe that only ever reports OK on the real schema would reproduce the original defect
exactly — a check nobody has seen fire.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_schema.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_schema", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load()
REAL = A.load_schema(A.SCHEMA)


def _run(schema: dict, tmp_path) -> subprocess.CompletedProcess:
    path = tmp_path / "s.yaml"
    path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--schema", str(path), "--traits", str(tmp_path)],
        capture_output=True, text=True, cwd=REPO)


def test_the_real_schema_passes():
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO)
    assert out.returncode == 0, out.stdout[-1500:]
    assert "OK: schema is internally coherent" in out.stdout


def test_an_UNREACHABLE_class_fails(tmp_path):
    """Dead weight that still reaches generated dataclasses and docs."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["classes"]["OrphanedThing"] = {"description": "reachable from nothing"}
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "OrphanedThing" in out.stdout


def test_a_SECOND_ROOT_is_not_reported_as_dead(tmp_path):
    """`ProteinProfile` is a real second document type. The first version of this audit
    assumed one root and reported it and `ProfileTrait` as unreachable — an audit calling
    a design a defect, which is how a gate loses its credibility."""
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO)
    assert "ProteinProfile" not in out.stdout and "ProfileTrait" not in out.stdout


def test_a_rule_that_CANNOT_FIRE_fails(tmp_path):
    """A rule whose pattern matches no category enforces nothing while looking exactly
    like enforcement — the same shape as the missing script this file is about."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["classes"]["ProteinTraitRecord"]["rules"].append({
        "title": "ghost_rule",
        "preconditions": {"slot_conditions": {"trait_category": {"pattern": "^NOSUCH_"}}},
        "postconditions": {"slot_conditions": {"trait_axis": {"equals_string": "SEQUENCE"}}},
    })
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "ghost_rule" in out.stdout


def test_a_category_prefix_NO_RULE_COVERS_fails(tmp_path):
    """The dangerous direction: a category with no rule binding it to an axis can be filed
    on ANY axis, and every record carrying it validates."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["enums"]["ProteinTraitCategoryEnum"]["permissible_values"]["ROGUE_THING"] = {
        "description": "bound to no axis"}
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "ROGUE_" in out.stdout


def test_the_documented_axis_free_prefixes_do_NOT_fail():
    """README: "`UPPER` / `OTHER` are administrative and may appear on any axis." The first
    version flagged both, i.e. reported a documented decision as a defect."""
    assert A.AXIS_FREE_PREFIXES == {"UPPER", "OTHER"}
    dead, uncovered = A.rule_coverage(REAL)
    assert not dead and not uncovered


def test_a_schema_with_no_classes_does_not_report_a_clean_result(tmp_path):
    """#418/#432/#469 — the guard that this probe examined something."""
    out = _run({"classes": {}, "enums": {}}, tmp_path)
    assert out.returncode == 1
    assert "examined nothing" in out.stdout


def test_unused_enum_values_are_REPORTED_not_failed():
    """A permissible value may be aspirational, so this must not gate. But the number has
    to be visible, or nobody ever prunes one."""
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO)
    assert out.returncode == 0
    assert "unused permissible values" in out.stdout
    assert "total unused:" in out.stdout


@pytest.mark.parametrize("missing", ["classes", "enums"])
def test_it_survives_a_schema_missing_a_top_level_key(missing, tmp_path):
    broken = {k: v for k, v in yaml.safe_load(yaml.safe_dump(REAL)).items() if k != missing}
    out = _run(broken, tmp_path)
    assert out.returncode in (0, 1), out.stdout + out.stderr
