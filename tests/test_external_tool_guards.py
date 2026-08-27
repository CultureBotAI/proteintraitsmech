"""Tracked scripts may not hard-require an external binary the project never declares.

`rg` is not in `pyproject.toml`, is not installed by any workflow in
`.github/workflows/`, and is absent from the GitHub runner.  A script that shells
out to a bare ``["rg", ...]`` therefore works on a developer laptop with Homebrew
and fails everywhere else -- which is how #571 reached CI as fifteen failures in a
single module, after a full-suite run had passed locally.

The rule is not "do not use ripgrep".  `corpus_stats.py` uses it happily and falls
back to a Python path when it is missing.  The rule is that the dependency must be
*discovered*, via `shutil.which`, rather than assumed.

Scope is deliberately `git ls-files`: uncommitted work in progress is not yet a
promise this repository makes, and scanning the working tree would fail for anyone
mid-branch on unrelated code.  A script enters scope the moment it is committed,
which is exactly when a reviewer can act on it.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# Binaries that are not declared dependencies of this project.  A tracked script
# may call them, but only after checking they exist.
UNDECLARED_BINARIES = frozenset({"rg"})


def _tracked_scripts() -> list[Path]:
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--", "scripts/*.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return [REPO_ROOT / name for name in listing.stdout.decode().split("\0") if name]


def _command_vector_heads(tree: ast.AST) -> set[str]:
    """Names of binaries invoked as a literal first element of a command list.

    ``["rg", "--files"]`` is an assumed dependency.  ``[executable, "--files"]``,
    where ``executable`` came from ``shutil.which``, is a discovered one, and a
    bare ``shutil.which("rg")`` is the discovery itself -- neither is a literal
    list head, so neither is reported.
    """

    heads: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
            continue
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            heads.add(first.value)
    return heads


def _guards(tree: ast.AST, binary: str) -> bool:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "which"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == binary
        ):
            return True
    return False


def test_there_are_tracked_scripts_to_check() -> None:
    """Guard the guard: a listing that matches nothing passes every test below."""
    assert len(_tracked_scripts()) > 50


@pytest.mark.parametrize("path", _tracked_scripts(), ids=lambda p: p.name)
def test_tracked_scripts_discover_undeclared_binaries(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for binary in sorted(UNDECLARED_BINARIES & _command_vector_heads(tree)):
        assert _guards(tree, binary), (
            f"{path.relative_to(REPO_ROOT)} invokes {binary!r} as a literal command head "
            f"without a shutil.which({binary!r}) check. {binary} is not a declared "
            f"dependency and CI does not install it (#571); discover it and fall back, "
            f"as scripts/corpus_stats.py does."
        )
