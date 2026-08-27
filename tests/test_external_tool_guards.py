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

# Callees that execute a string as a command line.  The string form is only a
# dependency when one of these runs it: `shutil.which("rg")` is also a call with
# the bare string "rg", and it is the discovery, not the assumption.
_STRING_COMMAND_CALLEES = frozenset(
    {"system", "popen", "run", "call", "check_call", "check_output"}
)


def _callee_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _tracked_scripts() -> list[Path]:
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--", "scripts/*.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return [REPO_ROOT / name for name in listing.stdout.decode().split("\0") if name]


def _assumed_binaries(tree: ast.AST) -> set[str]:
    """Undeclared binaries invoked by name instead of being discovered.

    Two shapes are reported, both examined only in call arguments so that prose in
    a docstring can never trip the gate:

    * a literal first element of a command list or tuple -- ``["rg", "--files"]``;
    * a literal string command whose first token is the binary, counted only when
      the callee actually executes a command line -- ``subprocess.run(...,
      shell=True)``, ``os.system("rg ...")``.  Without that restriction
      ``shutil.which("rg")`` would be flagged as the very thing it prevents.

    A *discovered* dependency has a variable at the head, holding what
    ``shutil.which`` returned, so it is never a literal and is never reported.
    That is why both current users pass without a special case:

        scripts/corpus_stats.py               [rg, "--no-heading", ...]
        scripts/stage_rhea_uniprot_grounding  [executable, "--null", ...]

    Deliberately absolute: there is no "but it calls shutil.which somewhere" escape
    hatch.  A file-scoped escape hatch was the first version of this gate, and a
    dead ``shutil.which("rg")`` in an uncalled function was enough to excuse a bare
    ``["rg", ...]`` (#577) -- a check reporting OK because of something it had not
    actually verified, which is the exact shape this gate exists to catch.

    Known limit (#578): indirection through a constant -- ``CMD = "rg"`` and then
    ``[CMD, ...]`` -- needs dataflow analysis and is not detected.  Stated rather
    than half-solved, so nobody reads this gate as more complete than it is.
    """

    found: set[str] = set()
    for node in ast.walk(tree):
        # A command list is very often built as a local first --
        #     command = ["rg", "--null", ...]
        #     subprocess.run(command, ...)
        # -- which is exactly how all eight scripts in #571 are written, so this
        # branch must look at every list, not only at call arguments.
        if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
            head = node.elts[0]
            if isinstance(head, ast.Constant) and head.value in UNDECLARED_BINARIES:
                found.add(head.value)
            continue
        # The string form is only a dependency when something executes it.  A bare
        # string is not enough: shutil.which("rg") is also a call carrying "rg".
        if isinstance(node, ast.Call) and _callee_name(node) in _STRING_COMMAND_CALLEES:
            for argument in node.args:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    tokens = argument.value.split()
                    if tokens and tokens[0] in UNDECLARED_BINARIES:
                        found.add(tokens[0])
    return found


def test_there_are_tracked_scripts_to_check() -> None:
    """Guard the guard: a listing that matches nothing passes every test below."""
    assert len(_tracked_scripts()) > 50


@pytest.mark.parametrize("path", _tracked_scripts(), ids=lambda p: p.name)
def test_tracked_scripts_discover_undeclared_binaries(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assumed = sorted(_assumed_binaries(tree))
    assert not assumed, (
        f"{path.relative_to(REPO_ROOT)} names {', '.join(repr(b) for b in assumed)} directly as a "
        f"command. Those binaries are not declared dependencies and CI does not install them "
        f"(#571). Discover them with shutil.which and fall back, as scripts/corpus_stats.py "
        f"does, so the command head is a variable rather than a literal."
    )
