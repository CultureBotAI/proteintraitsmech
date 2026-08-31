"""Tests for the shared guarded ripgrep prefilter (#571, #573)."""

from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ripgrep_prefilter.py"


def _load():
    spec = importlib.util.spec_from_file_location("ripgrep_prefilter", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PREFILTER = _load()


def _corpus(tmp_path: pathlib.Path) -> pathlib.Path:
    root = tmp_path / "traits"
    (root / "a").mkdir(parents=True)
    (root / "a" / "hit.yaml").write_text("identifier: RHEA:10000\n", encoding="utf-8")
    (root / "a" / "miss.yaml").write_text("identifier: GO:1\n", encoding="utf-8")
    (root / "a" / "upper.YAML").write_text("identifier: RHEA:20000\n", encoding="utf-8")
    return root


def test_the_fallback_is_a_superset_of_ripgrep(tmp_path, monkeypatch):
    """Both paths must agree, and where they differ the fallback must be wider."""
    root = _corpus(tmp_path)
    if PREFILTER.shutil.which("rg") is None:
        pytest.skip("ripgrep absent here, so the fallback is already the only path")
    with_rg = set(PREFILTER.candidate_paths(root, ["RHEA:"], label="t"))
    monkeypatch.setenv("PATH", "")
    without_rg = set(PREFILTER.candidate_paths(root, ["RHEA:"], label="t"))
    assert with_rg <= without_rg
    assert with_rg


def test_both_paths_find_a_hit(tmp_path, monkeypatch):
    root = _corpus(tmp_path)
    assert any(p.name == "hit.yaml" for p in PREFILTER.candidate_paths(root, ["RHEA:"], label="t"))
    monkeypatch.setenv("PATH", "")
    assert any(p.name == "hit.yaml" for p in PREFILTER.candidate_paths(root, ["RHEA:"], label="t"))


def test_the_fallback_includes_uppercase_suffixes(tmp_path, monkeypatch):
    """A .YAML record silently dropped from the fallback is a hole ripgrep does not have."""
    root = _corpus(tmp_path)
    monkeypatch.setenv("PATH", "")
    names = {p.name for p in PREFILTER.candidate_paths(root, ["RHEA:"], label="t")}
    assert "upper.YAML" in names


def test_a_missing_root_fails_closed_in_the_fallback(tmp_path, monkeypatch):
    """os.walk reports an absent tree as an empty one; scanning nothing must not pass (#573)."""
    monkeypatch.setenv("PATH", "")
    with pytest.raises(PREFILTER.PrefilterError, match="not a directory"):
        PREFILTER.candidate_paths(tmp_path / "gone", ["RHEA:"], label="t")


def test_an_unreadable_subdirectory_fails_closed(tmp_path, monkeypatch):
    root = _corpus(tmp_path)
    os.chmod(root / "a", 0o000)
    try:
        if os.access(root / "a", os.R_OK):
            pytest.skip("running as a user that ignores directory permissions")
        monkeypatch.setenv("PATH", "")
        with pytest.raises(PREFILTER.PrefilterError, match="cannot scan"):
            PREFILTER.candidate_paths(root, ["RHEA:"], label="t")
    finally:
        os.chmod(root / "a", 0o700)


def test_extra_paths_are_always_included(tmp_path, monkeypatch):
    """Callers add their canonical route, which must survive either path."""
    root = _corpus(tmp_path)
    extra = root / "a" / "miss.yaml"
    monkeypatch.setenv("PATH", "")
    assert extra.resolve() in {
        p.resolve() for p in PREFILTER.candidate_paths(root, ["RHEA:"], label="t", extra=[extra])
    }


def test_no_patterns_is_refused(tmp_path):
    """An empty pattern list would make ripgrep match nothing and the fallback everything."""
    with pytest.raises(PREFILTER.PrefilterError, match="at least one pattern"):
        PREFILTER.candidate_paths(_corpus(tmp_path), [], label="t")


def test_the_helper_itself_passes_the_undeclared_binary_gate():
    """It names rg only through shutil.which, so it is not a literal command head (#571)."""
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'shutil.which("rg")' in source
    assert '\n        "rg",' not in source


def test_a_user_ripgrep_config_cannot_change_the_candidate_set(tmp_path, monkeypatch):
    """--no-config, because a developer's ~/.ripgreprc could empty the scan (#587).

    Without it, `--max-filesize=1` in a user config returned ZERO candidates from the
    real corpus while the stage reported success. The wide-root scan exists to catch
    identities hiding outside the canonical route, so an empty result silently removes
    exactly the protection it provides.

    `--iglob` in the command does override a config `--glob=!*.yaml`, so not every
    option exposes this; the assertion is on the flag, which covers all of them.
    """
    if PREFILTER.shutil.which("rg") is None:
        pytest.skip("ripgrep absent, so no config is read either way")
    root = _corpus(tmp_path)
    config = tmp_path / "ripgreprc"
    config.write_text("--max-filesize=1\n", encoding="utf-8")
    monkeypatch.setenv("RIPGREP_CONFIG_PATH", str(config))
    found = PREFILTER.candidate_paths(root, ["RHEA:"], label="t")
    assert any(p.name == "hit.yaml" for p in found), (
        "a user ripgrep config changed the candidate set; --no-config is missing"
    )


def test_the_command_passes_no_config():
    """Pin the flag itself, so removing it fails even where the probe above cannot run."""
    assert '"--no-config"' in SCRIPT.read_text(encoding="utf-8")
