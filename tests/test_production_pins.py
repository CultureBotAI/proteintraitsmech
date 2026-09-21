"""The plumbing for tests that read production grounding data (#713, #734)."""

from __future__ import annotations

import hashlib
import json
import re

OLD, NEW = "2026_02", "2099_01"          # a known-stale pin, and one that is not


def _registry(tmp_path, releases, name="protein_registry.jsonl"):
    path = tmp_path / name
    path.write_text("".join(json.dumps({"protein_id": f"UniProtKB:P{i:05d}",
                                        **({"uniprot_release": r} if r else {})}) + "\n"
                            for i, r in enumerate(releases)), encoding="utf-8")
    return path


def test_a_registry_on_the_pinned_release_is_ok(tmp_path, production_pins):
    assert production_pins.pin_verdict(_registry(tmp_path, [NEW, NEW]), release=NEW) == ("ok", "")


def test_an_empty_registry_satisfies_a_release_pin_as_the_stages_do(tmp_path, production_pins):
    assert production_pins.pin_verdict(_registry(tmp_path, []), release=NEW)[0] == "ok"


def test_a_known_stale_pin_is_an_expected_failure_naming_its_issue(tmp_path, production_pins):
    # main since #690: the stages pin 2026_02, the registry mixes it with 2026_03
    verdict, why = production_pins.pin_verdict(_registry(tmp_path, [OLD, "2026_03"]),
                                               release=OLD)
    assert verdict == "known_stale"
    assert "2026_03" in why and production_pins.KNOWN_STALE_PINS[OLD] in why


def test_any_other_mismatch_fails_so_the_next_stale_pin_is_seen(tmp_path, production_pins):
    # after a re-pin to NEW, a registry that moves again must go red, not quiet
    verdict, why = production_pins.pin_verdict(_registry(tmp_path, [NEW, "2099_02"]),
                                               release=NEW)
    assert verdict == "mismatch" and "not listed as known-stale" in why


def test_rows_without_a_release_are_a_mismatch_not_a_release_called_none(tmp_path, production_pins):
    verdict, why = production_pins.pin_verdict(_registry(tmp_path, [NEW, None]), release=NEW)
    assert verdict == "mismatch" and "carry no uniprot_release" in why and "None" not in why


def test_a_sha_pin_compares_the_exact_bytes(tmp_path, production_pins):
    path = _registry(tmp_path, [NEW])
    good = hashlib.sha256(path.read_bytes()).hexdigest()
    assert production_pins.pin_verdict(path, sha256=good)[0] == "ok"
    assert production_pins.pin_verdict(path, sha256="0" * 64)[0] == "mismatch"
    stale = next(p for p in production_pins.KNOWN_STALE_PINS if len(p) == 64)
    assert production_pins.pin_verdict(path, sha256=stale)[0] == "known_stale"


def test_one_unlisted_pin_is_enough_to_fail(tmp_path, production_pins):
    # a known-stale release pin must not excuse an unlisted sha pin beside it
    path = _registry(tmp_path, [OLD, "2026_03"])
    assert production_pins.pin_verdict(path, release=OLD, sha256="0" * 64)[0] == "mismatch"


def test_every_known_stale_pin_is_still_pinned_by_some_stage(production_pins):
    # re-pinning the last stage that uses a value must delete its entry here
    scripts = "\n".join(p.read_text(encoding="utf-8")
                        for p in (production_pins.REPO_ROOT / "scripts").glob("stage_*.py"))
    for pin, issue in production_pins.KNOWN_STALE_PINS.items():
        assert re.fullmatch(r"#\d+", issue)
        assert f'"{pin}"' in scripts, (
            f"no stage script pins {pin!r} any more — delete it from KNOWN_STALE_PINS")


def test_every_production_stage_test_checks_its_pin(production_pins):
    # a stage that pins the registry and reads the production one must say so
    root = production_pins.REPO_ROOT
    for script in sorted((root / "scripts").glob("stage_*.py")):
        if "EXPECTED_UNIPROT_RELEASE" not in script.read_text(encoding="utf-8"):
            continue
        test = root / "tests" / f"test_{script.stem}.py"
        assert "production_registry_pin(" in test.read_text(encoding="utf-8"), (
            f"{test.name} reads the production registry without checking {script.name}'s pin")


def test_the_checkout_note_is_silent_on_a_clean_tree_and_bounded_on_a_dirty_one(production_pins):
    assert production_pins.checkout_state_note(()) is None
    note = production_pins.checkout_state_note(
        tuple(f"data/grounding/f{i}.jsonl" for i in range(9)))
    assert note.startswith("9 tracked file(s)") and "f3.jsonl" in note and "f4.jsonl" not in note


def test_the_dirty_file_probe_reports_paths_under_data_grounding(production_pins):
    dirty = production_pins.dirty_grounding_files()
    assert isinstance(dirty, tuple) and all(p.startswith("data/grounding") for p in dirty)


def test_the_probe_is_silent_when_git_is_missing_hangs_or_fails(production_pins):
    import subprocess

    for error in (FileNotFoundError("git"), subprocess.TimeoutExpired("git", 60),
                  PermissionError("git")):
        def run(*args, _e=error, **kwargs):
            raise _e
        assert production_pins.probe_dirty_grounding_files(run) == ()


def test_the_probe_never_takes_the_index_lock(production_pins):
    # another session may be committing in this checkout while the suite runs
    seen = {}

    def run(cmd, **kwargs):
        seen["cmd"] = cmd
        return type("Done", (), {"stdout": ""})()

    assert production_pins.probe_dirty_grounding_files(run) == ()
    assert seen["cmd"][:3] == ["git", "--no-optional-locks", "status"]
    assert "-z" in seen["cmd"] and "--untracked-files=no" in seen["cmd"]


def test_porcelain_z_keeps_raw_paths_and_drops_a_renames_origin(production_pins):
    out = (" M data/grounding/occurrence_evidence.jsonl\0"
           "R  data/grounding/new name.jsonl\0data/grounding/old name.jsonl\0"
           "M  data/grounding/ż.jsonl\0")
    assert production_pins.parse_porcelain_z(out) == (
        "data/grounding/occurrence_evidence.jsonl", "data/grounding/new name.jsonl",
        "data/grounding/ż.jsonl")
    assert production_pins.parse_porcelain_z("") == ()
