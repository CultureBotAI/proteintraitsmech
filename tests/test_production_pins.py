"""The plumbing for tests that read production grounding data (#713, #734)."""

from __future__ import annotations

import hashlib
import json

import pytest

import conftest


def _registry(tmp_path, releases):
    path = tmp_path / "protein_registry.jsonl"
    path.write_text("".join(json.dumps({"protein_id": f"UniProtKB:P{i:05d}",
                                        "uniprot_release": r}) + "\n"
                            for i, r in enumerate(releases)), encoding="utf-8")
    return path


def test_a_registry_on_the_pinned_release_is_accepted(tmp_path):
    path = _registry(tmp_path, ["2026_02", "2026_02"])
    assert conftest.registry_pin_mismatch(path, release="2026_02") is None


def test_a_registry_that_has_moved_on_names_both_releases(tmp_path):
    # the state main has been in since #690: old and new rows side by side
    path = _registry(tmp_path, ["2026_02", "2026_03"])
    why = conftest.registry_pin_mismatch(path, release="2026_02")
    assert "2026_02" in why and "2026_03" in why and "pinned to" in why


def test_a_sha_pin_compares_the_exact_bytes(tmp_path):
    path = _registry(tmp_path, ["2026_02"])
    good = hashlib.sha256(path.read_bytes()).hexdigest()
    assert conftest.registry_pin_mismatch(path, sha256=good) is None
    assert "sha256" in conftest.registry_pin_mismatch(path, sha256="0" * 64)


def test_the_fixture_xfails_with_the_tracking_issue(tmp_path, production_registry_pin):
    production_registry_pin(_registry(tmp_path, ["2026_02"]), release="2026_02")  # no-op
    moved = _registry(tmp_path, ["2026_03"])
    with pytest.raises(pytest.xfail.Exception, match=conftest.PIN_ISSUE):
        production_registry_pin(moved, release="2026_02")


def test_the_checkout_note_is_silent_on_a_clean_tree_and_bounded_on_a_dirty_one():
    assert conftest.checkout_state_note(()) is None
    note = conftest.checkout_state_note(tuple(f"data/grounding/f{i}.jsonl" for i in range(9)))
    assert note.startswith("9 tracked file(s)") and "f3.jsonl" in note and "f4.jsonl" not in note


def test_the_dirty_file_probe_never_raises():
    assert isinstance(conftest._dirty_grounding_files(), tuple)
