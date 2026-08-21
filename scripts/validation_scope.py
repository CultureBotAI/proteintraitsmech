#!/usr/bin/env python3
"""Choose changed-file or full-corpus validation for a pull request.

Trait-only changes can be validated in isolation. Changes to the schema, validators,
their dependency declaration, or this workflow can affect records outside the diff and
must validate the whole corpus. Keeping that decision here makes it unit-testable; the
old workflow embedded an incomplete regular expression and silently skipped validation
for a ``mech_shared.yaml``-only change (#515).
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable


FULL_VALIDATION_PATHS = frozenset({
    ".github/workflows/validate-strict.yaml",
    "pyproject.toml",
    "scripts/audit_causal_graphs.py",
    "scripts/validate_strict.py",
    "scripts/validation_scope.py",
    "src/proteintraitsmech/schema/mech_shared.yaml",
    "src/proteintraitsmech/schema/proteintraitsmech.yaml",
})


def choose_scope(changed_paths: Iterable[str]) -> tuple[str, list[str]]:
    """Return ``(mode, changed trait YAMLs)`` for repository-relative paths."""
    changed = {path for path in changed_paths if path}
    if changed & FULL_VALIDATION_PATHS:
        return "full", []
    traits = sorted(
        path for path in changed
        if path.startswith("data/traits/") and Path(path).suffix in {".yaml", ".yml"}
    )
    return "changed", traits


def git_changed_paths(base: str, head: str) -> list[str]:
    """Return paths changed between two commits, failing loudly if Git cannot diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", base, head],
        check=True,
        capture_output=True,
    )
    return [part.decode("utf-8", errors="surrogateescape")
            for part in result.stdout.split(b"\0") if part]


def write_outputs(
    mode: str,
    traits: list[str],
    *,
    github_output: Path,
    changed_traits: Path,
) -> None:
    """Write the GitHub Actions outputs and the changed-record argument file."""
    changed_traits.write_text("".join(f"{path}\n" for path in traits), encoding="utf-8")
    with github_output.open("a", encoding="utf-8") as handle:
        handle.write(f"mode={mode}\n")
        handle.write(f"changed_count={len(traits)}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base commit")
    parser.add_argument("--head", required=True, help="head commit")
    parser.add_argument("--github-output", required=True, type=Path)
    parser.add_argument("--changed-traits", default="changed_traits.txt", type=Path)
    args = parser.parse_args()

    mode, traits = choose_scope(git_changed_paths(args.base, args.head))
    write_outputs(
        mode,
        traits,
        github_output=args.github_output,
        changed_traits=args.changed_traits,
    )
    if mode == "full":
        print("A schema, validator, dependency, or workflow change requires full validation.")
    else:
        print(f"{len(traits)} changed trait file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
