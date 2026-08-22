"""The writer-safety audit (#492, for #484 item 4).

`record_io.write_record` is the choke point that makes `merge_on_reseed` reachable, and
#455 measured what that protects: a `--force` re-seed shortened 27,784 definitions when
one rule inside it failed to fire. This audit answers "does every writer of a trait record
go through it, or is it a declared exception?".

The tests that matter are the ones proving the audit CATCHES something, because during
development its detector cleared a known writer four times, each for a different reason:
a three-hop loop chain, an expression receiver, a root name it did not guess, and a root
IMPORTED from a sibling module. An audit that clears real writers is worse than none.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_writers.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_writers", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A = _load()


def test_the_repo_passes_today():
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=REPO)
    assert out.returncode == 0, out.stdout[-1200:]
    assert "OK: every writer of a trait record" in out.stdout


def test_the_registry_is_READ_from_the_guard_test_not_copied():
    """Two lists of the same thing is how slugify reached 31 copies (#110). A script added
    to one and not the other would otherwise pass both checks."""
    editors = A.registered_editors()
    assert "enrich_pfam_definitions" in editors
    guard = (REPO / "tests" / "test_inplace_editor_guards.py").read_text(encoding="utf-8")
    for name in editors:
        assert f'"{name}"' in guard


def test_no_script_is_in_BOTH_registries():
    assert not (set(A.BYPASS) & A.registered_editors())


def test_every_bypass_entry_carries_a_reason():
    """"It has always been in the list" is how an allow-list stops being a decision."""
    for name, reason in A.BYPASS.items():
        assert reason and len(reason) > 12, name


# --- the detector, against the four shapes that fooled it -------------------------------

import ast  # noqa: E402


def _writes(src: str) -> bool:
    return A.writes_trait_records(ast.parse(src))


def test_it_sees_the_direct_loop():
    assert _writes('TRAITS = ROOT / "data" / "traits"\n'
                   'for p in TRAITS.rglob("*.yaml"):\n    p.write_text("x")\n')


def test_it_sees_a_THREE_HOP_chain():
    """`paths = sorted(...)` then `for i, path in enumerate(paths)` then
    `path.write_text`. A single-pass detector binds only `paths` and clears the script."""
    assert _writes('TRAITS = ROOT / "data" / "traits"\n'
                   'paths = sorted(TRAITS.rglob("*.yaml"))\n'
                   'for i, path in enumerate(paths):\n    path.write_text("x")\n')


def test_it_sees_an_EXPRESSION_receiver():
    """`(TRAITS / dst / p.name).write_text(...)` -- the receiver is derived from the loop
    variable, not the variable. migrate_axis_split_fixes writes every record that way."""
    # the receiver must NOT mention the loop variable, or the loop-variable rule catches
    # it and this test proves nothing. The first version wrote `(TRAITS / "x" / p.name)`,
    # whose dump contains `id='p'` -- so deleting the rule under test left it green.
    assert _writes('TRAITS = ROOT / "data" / "traits"\n'
                   'for p in TRAITS.rglob("*.yaml"):\n'
                   '    (TRAITS / "x" / "fixed.yaml").write_text("y")\n')


def test_it_does_NOT_fire_on_a_script_that_only_reads():
    """Every audit names a traits root. Naming one is not writing to one."""
    assert not _writes('TRAITS = ROOT / "data" / "traits"\n'
                       'REPORT = ROOT / "reports" / "x.tsv"\n'
                       'for p in TRAITS.rglob("*.yaml"):\n'
                       '    pass\n'
                       'REPORT.write_text("done")\n')


def test_it_does_NOT_fire_on_a_script_with_no_traits_root():
    assert not _writes('RAW = ROOT / "data" / "raw"\n'
                       'for p in RAW.rglob("*.json"):\n    p.write_text("x")\n')


def test_an_UNDECLARED_writer_is_caught(tmp_path):
    """The whole point. A new script that writes records by an undeclared route must fail
    the audit rather than pass silently -- which is how #455 and #148 happened."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "sneaky_writer.py").write_text(
        'from pathlib import Path\n'
        'TRAITS = Path("data") / "traits"\n'
        'for p in TRAITS.rglob("*.yaml"):\n'
        '    p.write_text("clobbered")\n', encoding="utf-8")
    mod = _load()
    mod.SCRIPTS = scripts
    assert mod.writes_trait_records(
        ast.parse((scripts / "sneaky_writer.py").read_text(encoding="utf-8"))), (
        "the audit would not see a new in-place writer")
    assert "sneaky_writer" not in mod.BYPASS and "sneaky_writer" not in mod.registered_editors()


# --- the ENFORCEMENT path, which nothing covered -----------------------------------------

def test_main_EXITS_1_on_an_undeclared_writer(tmp_path, monkeypatch):
    """Four mutations survived the first version of this file because no test ever ran
    `main()` on a failing tree: deleting `return 1`, and disabling the stale-BYPASS, the
    registry-overlap and the examined-nothing guards all stayed green.

    `test_an_UNDECLARED_writer_is_caught` looked end-to-end and was not -- it called
    `writes_trait_records` on a synthetic source and asserted registry membership
    separately, and its `mod.SCRIPTS = scripts` line was assigned and never read.
    """
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "sneaky_writer.py").write_text(
        'from pathlib import Path\n'
        'TRAITS = Path("data") / "traits"\n'
        'for p in TRAITS.rglob("*.yaml"):\n'
        '    p.write_text("clobbered")\n', encoding="utf-8")
    mod = _load()
    monkeypatch.setattr(mod, "SCRIPTS", scripts)
    monkeypatch.setattr(sys, "argv", ["audit_writers.py"])
    assert mod.main() == 1


def test_main_EXITS_1_on_a_stale_bypass_entry(tmp_path, monkeypatch):
    """An allow-list that outlives what it allows silently covers a future script that
    reuses the name."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "harmless.py").write_text("x = 1\n", encoding="utf-8")
    mod = _load()
    monkeypatch.setattr(mod, "SCRIPTS", scripts)
    monkeypatch.setattr(mod, "BYPASS", {"gone_away": "a reason long enough to pass"})
    monkeypatch.setattr(sys, "argv", ["audit_writers.py"])
    assert mod.main() == 1


def test_main_EXITS_1_WHEN_IT_EXAMINED_NOTHING(tmp_path, monkeypatch):
    """#418/#432/#469. The guard whose own comment cites those issues was itself
    uncertified — deleting it left every test green."""
    empty = tmp_path / "scripts"
    empty.mkdir()
    mod = _load()
    monkeypatch.setattr(mod, "SCRIPTS", empty)
    monkeypatch.setattr(mod, "BYPASS", {})
    monkeypatch.setattr(sys, "argv", ["audit_writers.py"])
    assert mod.main() == 1


def test_a_declared_bypass_may_not_name_a_plain_seeder(tmp_path, monkeypatch):
    """BYPASS means "writes records WITHOUT write_record". Subtracting `seeders` from the
    stale check meant `BYPASS["seed_prosite"] = "..."` kept the audit green while asserting
    something false about that script."""
    mod = _load()
    monkeypatch.setattr(sys, "argv", ["audit_writers.py"])
    monkeypatch.setitem(mod.BYPASS, "seed_prosite", "a reason long enough to pass the check")
    assert mod.main() == 1


def test_registered_editor_without_validated_write_fails(tmp_path, monkeypatch):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "unsafe_editor.py").write_text(
        'from pathlib import Path\n'
        'TRAITS = Path("data") / "traits"\n'
        'for p in TRAITS.rglob("*.yaml"):\n'
        '    p.write_text("unsafe")\n',
        encoding="utf-8",
    )
    guard = tmp_path / "guard.py"
    guard.write_text('EDITORS = [\n    "unsafe_editor",\n]\n', encoding="utf-8")
    mod = _load()
    monkeypatch.setattr(mod, "SCRIPTS", scripts)
    monkeypatch.setattr(mod, "GUARD_TEST", guard)
    monkeypatch.setattr(mod, "BYPASS", {})
    monkeypatch.setattr(sys, "argv", ["audit_writers.py"])

    assert mod.main() == 1
