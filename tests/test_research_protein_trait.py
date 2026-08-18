from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "research_protein_trait", REPO_ROOT / "scripts" / "research_protein_trait.py"
)
assert SPEC and SPEC.loader
rpt = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rpt
SPEC.loader.exec_module(rpt)


def _write_record(path: Path, identifier: str, label: str, trait_axis: str = "STRUCTURE") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"identifier: {identifier}\nlabel: {label}\ntrait_axis: {trait_axis}\n",
        encoding="utf-8",
    )
    return path


def test_resolve_record_by_unique_path_and_identifier(tmp_path):
    """Uses a small synthetic corpus rather than a live curated record, so this
    test stays fast (no full-corpus fallback scan) and does not pin the content
    of a record real curation might later edit."""
    traits_dir = tmp_path / "traits"
    path = _write_record(
        traits_dir / "structure" / "cavity" / "pocket.yaml",
        "proteintraitsmech:POCKET", "binding pocket",
    )
    assert rpt.resolve_record(str(path), traits_dir=traits_dir) == path.resolve()
    assert rpt.resolve_record("proteintraitsmech:POCKET", traits_dir=traits_dir) == path


def test_resolve_record_ambiguous_stem_raises(tmp_path):
    traits_dir = tmp_path / "traits"
    _write_record(traits_dir / "a" / "pocket.yaml", "proteintraitsmech:POCKET_A", "pocket a")
    _write_record(traits_dir / "b" / "pocket.yaml", "proteintraitsmech:POCKET_B", "pocket b")
    with pytest.raises(ValueError, match="Ambiguous"):
        rpt.resolve_record("pocket", traits_dir=traits_dir)


def test_resolve_record_not_found_raises(tmp_path):
    traits_dir = tmp_path / "traits"
    traits_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        rpt.resolve_record("proteintraitsmech:NOPE", traits_dir=traits_dir)


def test_resolve_record_by_unique_label(tmp_path):
    """The multi-word-label case: what the justfile quote() fix and the
    grep prefilter both exist to support."""
    traits_dir = tmp_path / "traits"
    path = _write_record(
        traits_dir / "structure" / "cavity" / "pocket.yaml",
        "proteintraitsmech:POCKET", "binding pocket",
    )
    assert rpt.resolve_record("binding pocket", traits_dir=traits_dir) == path


def test_grep_candidates_missing_grep_returns_none(monkeypatch, tmp_path):
    def _no_grep(*a, **k):
        raise FileNotFoundError("grep")

    monkeypatch.setattr(rpt.subprocess, "run", _no_grep)
    assert rpt._grep_candidates("x", tmp_path) is None


def test_grep_candidates_timeout_raises_instead_of_degrading(monkeypatch, tmp_path):
    """A grep timeout must not silently fall back to the full Python scan it
    was added to avoid — that fallback is slower than grep, not faster, so
    degrading into it on failure just trades one slow path for a much
    slower one (proteintraitsmech#487 review)."""
    def _timeout(*a, **k):
        raise rpt.subprocess.TimeoutExpired(cmd="grep", timeout=180)

    monkeypatch.setattr(rpt.subprocess, "run", _timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        rpt._grep_candidates("x", tmp_path)


def test_grep_candidates_bad_exit_code_raises(monkeypatch, tmp_path):
    class _Result:
        returncode = 2
        stdout = ""
        stderr = "grep: permission denied"

    monkeypatch.setattr(rpt.subprocess, "run", lambda *a, **k: _Result())
    with pytest.raises(RuntimeError, match="failed"):
        rpt._grep_candidates("x", tmp_path)


def test_template_vars_capture_protein_trait_context(tmp_path):
    path = _write_record(
        tmp_path / "structure" / "cavity" / "pocket.yaml",
        "proteintraitsmech:POCKET", "binding pocket",
    )
    variables = rpt.template_vars(rpt.load_record(path), path)
    assert variables["trait_identifier"] == "proteintraitsmech:POCKET"
    assert variables["trait_axis"] == "STRUCTURE"
    assert variables["record_path"].endswith("structure/cavity/pocket.yaml")


def test_build_command_uses_provider_and_citation_sidecar(tmp_path):
    command = rpt.build_command(
        "asta",
        REPO_ROOT / "templates" / "protein_trait_mechanism_research.md",
        tmp_path / "report.md",
        tmp_path / "report.md.citations.md",
        {"trait_label": "pocket"},
        ["--param", "top_k=10"],
    )
    assert command[:4] == [
        "deep-research-client",
        "research",
        "--template",
        "templates/protein_trait_mechanism_research.md",
    ]
    assert ["--provider", "asta"] == command[
        command.index("--provider") : command.index("--provider") + 2
    ]
    assert "--separate-citations" in command
    assert command[-2:] == ["--param", "top_k=10"]


def test_edison_alias_and_platform_key(monkeypatch):
    assert rpt.canonical_provider("Edison") == "falcon"
    monkeypatch.delenv("EDISON_API_KEY", raising=False)
    monkeypatch.setenv("EDISON_PLATFORM_API_KEY", "test-only")
    assert rpt.research_env()["EDISON_API_KEY"] == "test-only"


def test_claude_code_alias_and_space_normalization():
    assert rpt.canonical_provider("claude-code") == "claude_code"
    assert rpt.canonical_provider("Claude Code") == "claude_code"


def test_dry_run_defaults_true_and_apply_flips_it():
    """A bare `research-protein-trait <provider> <target>` must never fire a
    live, possibly billed provider call — --apply is required to opt in."""
    args = rpt.parse_args(["--provider", "falcon", "--target", "x.yaml"])
    assert args.dry_run is True

    args = rpt.parse_args(["--provider", "falcon", "--target", "x.yaml", "--apply"])
    assert args.dry_run is False

    args = rpt.parse_args(["--provider", "falcon", "--target", "x.yaml", "--dry-run"])
    assert args.dry_run is True


def test_main_dry_run_does_not_invoke_subprocess(monkeypatch, tmp_path, capsys):
    path = _write_record(
        tmp_path / "traits" / "pocket.yaml", "proteintraitsmech:POCKET", "binding pocket",
    )
    monkeypatch.setattr(rpt, "TRAITS_DIR", tmp_path / "traits")

    def _boom(*a, **k):
        raise AssertionError("subprocess.run must not be called in dry-run mode")

    monkeypatch.setattr(rpt.subprocess, "run", _boom)
    rc = rpt.main(["--provider", "falcon", "--target", str(path)])
    assert rc == 0
