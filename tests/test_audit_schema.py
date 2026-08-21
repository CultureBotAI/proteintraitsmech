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
    traits = tmp_path / "traits"
    traits.mkdir(exist_ok=True)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--schema", str(path), "--traits", str(traits)],
        capture_output=True, text=True, cwd=REPO)


def test_the_real_schema_passes(tmp_path):
    """Schema structure does not require a second real-corpus enum-usage scan."""
    out = _run(REAL, tmp_path)
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
    out = _run(REAL, tmp_path)
    # returncode FIRST. Asserting only the absence of two substrings passes on empty
    # stdout, i.e. if the script crashes -- a test for "does not report X" that a crash
    # satisfies.
    assert out.returncode == 0, out.stdout[-800:] + out.stderr[-400:]
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


def test_the_documented_axis_free_categories_do_NOT_fail():
    """README: "`UPPER` / `OTHER` are administrative and may appear on any axis." The first
    version flagged both, i.e. reported a documented decision as a defect."""
    assert A.AXIS_FREE_CATEGORIES == {"UPPER", "OTHER"}
    dead, uncovered = A.rule_coverage(REAL)
    assert not dead and not uncovered


def test_a_schema_with_no_classes_does_not_report_a_clean_result(tmp_path):
    """#418/#432/#469 — the guard that this probe examined something."""
    out = _run({"classes": {}, "enums": {}}, tmp_path)
    assert out.returncode == 1
    assert "examined nothing" in out.stdout


def test_unused_enum_values_are_REPORTED_not_failed(tmp_path):
    """A permissible value may be aspirational, so this must not gate. But the number has
    to be visible, or nobody ever prunes one."""
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "one.yaml").write_text("trait_axis: SEQUENCE\n", encoding="utf-8")
    path = tmp_path / "s.yaml"
    path.write_text(yaml.safe_dump(REAL, sort_keys=False), encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--schema", str(path), "--traits", str(traits)],
        capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0
    assert "unused permissible values" in out.stdout
    assert "total unused:" in out.stdout


@pytest.mark.parametrize("missing", ["classes", "enums"])
def test_it_survives_a_schema_missing_a_top_level_key(missing, tmp_path):
    """`returncode in (0, 1)` accepted the crash this test is named for -- an uncaught
    exception also exits 1. It asserts NO TRACEBACK instead."""
    broken = {k: v for k, v in yaml.safe_load(yaml.safe_dump(REAL)).items() if k != missing}
    out = _run(broken, tmp_path)
    assert "Traceback" not in out.stderr, out.stderr[-600:]
    assert out.returncode in (0, 1), out.stdout + out.stderr


def test_a_malformed_class_does_not_crash_it(tmp_path):
    """`classes: {Broken: "a string"}` raised AttributeError and exited 1 -- which the old
    assertion accepted as success."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["classes"]["Broken"] = "a string, not a mapping"
    out = _run(broken, tmp_path)
    assert "Traceback" not in out.stderr, out.stderr[-600:]


def test_a_rule_binding_the_RIGHT_categories_to_the_WRONG_axis_fails(tmp_path):
    """The probe read only preconditions, so a rule could match every FUNC_* category and
    require EVOLUTION -- mis-axising the whole corpus -- while the audit reported
    "bound to an axis: yes". This is the invariant the PR body calls central."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    for rule in broken["classes"]["ProteinTraitRecord"]["rules"]:
        pre = (rule.get("preconditions") or {}).get("slot_conditions") or {}
        if (pre.get("trait_category") or {}).get("pattern", "").startswith("^FUNC"):
            rule["postconditions"]["slot_conditions"]["trait_axis"]["equals_string"] = "EVOLUTION"
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "asserts trait_axis" in out.stdout


def test_a_precondition_this_probe_cannot_EVALUATE_is_reported(tmp_path):
    """A rule keyed on `equals_string` was silently skipped, so a whole class of dead rule
    was unauditable -- and a LIVE one would have made the coverage check emit a false
    failure, since its categories never entered `covered`."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["classes"]["ProteinTraitRecord"]["rules"].append({
        "title": "opaque_rule",
        "preconditions": {"slot_conditions": {"trait_category": {"equals_string": "SEQ_DOMAIN"}}},
        "postconditions": {"slot_conditions": {"trait_axis": {"equals_string": "SEQUENCE"}}},
    })
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "cannot evaluate" in out.stdout


def test_a_ROOT_CLASS_the_schema_no_longer_declares_fails(tmp_path):
    """Additions were asked about; REMOVALS were silent, and that is the direction that
    turns an exemption into a lie."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    del broken["classes"]["ProteinProfile"]
    del broken["classes"]["ProfileTrait"]
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "ROOT_CLASSES names" in out.stdout


def test_an_AXIS_FREE_value_the_enum_no_longer_declares_fails(tmp_path):
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    del broken["enums"]["ProteinTraitCategoryEnum"]["permissible_values"]["UPPER"]
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "AXIS_FREE_CATEGORIES names" in out.stdout


def test_the_axis_free_exemption_is_EXACT_not_a_prefix(tmp_path):
    """Subtracting `c.split("_")[0]` exempted the whole `OTHER_*` namespace, so a genuinely
    unbound `OTHER_UNBOUND_THING` passed. `SEQ_OTHER` / `MIXED_OTHER` already exist, so
    that naming is not hypothetical."""
    broken = yaml.safe_load(yaml.safe_dump(REAL))
    broken["enums"]["ProteinTraitCategoryEnum"]["permissible_values"]["OTHER_UNBOUND_THING"] = {
        "description": "bound to no axis"}
    out = _run(broken, tmp_path)
    assert out.returncode == 1, out.stdout
    assert "OTHER_UNBOUND_THING" in out.stdout


def test_enum_usage_counts_LIST_ITEM_keys(tmp_path):
    r"""`- kind: STRUCTURAL` is how every definitions[] entry renders. Anchoring on
    `^\s*kind:` missed 156,386 uses and reported DefinitionKindEnum as 3-of-3 unused."""
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "one.yaml").write_text(
        "definitions:\n"
        "  - kind: GENERAL\n"
        "  - kind: MECHANISTIC\n"
        "  - kind: STRUCTURAL\n",
        encoding="utf-8",
    )
    usage = A.enum_usage(REAL, traits)
    kinds = usage.get("DefinitionKindEnum", {})
    assert set(kinds) >= {"GENERAL", "MECHANISTIC", "STRUCTURAL"}, dict(kinds)
    assert sum(kinds.values()) == 3, sum(kinds.values())
