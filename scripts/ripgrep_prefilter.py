"""One guarded ripgrep prefilter, shared by every corpus scan that uses one.

Nine scripts in this repository narrow a whole-corpus scan by asking ripgrep which
YAML records could possibly match, then parse only those. The pattern is sound --
every candidate is parsed downstream, so the prefilter only has to be a superset --
but it was written out nine times, and each copy re-derived two decisions that are
easy to get wrong:

* **ripgrep may be absent.** It is not a declared dependency and CI does not install
  it, so a bare ``["rg", ...]`` fails everywhere except a developer laptop (#571).
  Absence must fall back; an ``rg`` that is present and errors is still fatal.
* **the fallback must fail closed.** ``os.walk`` reports a missing or unreadable
  tree as an empty one, so a naive fallback scans nothing, finds nothing, and
  reports success -- which silently empties whatever the scan was protecting
  (#573).

Getting either wrong is invisible: the scan returns fewer candidates and everything
downstream agrees there was nothing to find. Written once, tested once, here.

The fallback is deliberately NOT a reimplementation of ripgrep's matching. Escape,
NUL and UTF-16 semantics reproduced in a second matcher are how two paths drift
apart silently, which is #539 in ``corpus_stats``. It returns every YAML under the
root instead: a strict superset, correct by construction, and slower.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

YAML_SUFFIXES = frozenset({".yaml", ".yml"})


class PrefilterError(RuntimeError):
    """Raised when the prefilter cannot produce a trustworthy candidate set."""


def ripgrep_paths(root: Path, patterns: Sequence[str], label: str) -> set[Path] | None:
    """Ripgrep's candidate set, or ``None`` when ripgrep is not installed."""
    executable = shutil.which("rg")
    if executable is None:
        return None
    command = [
        executable,
        "--no-config",
        "--null",
        "-l",
        "--text",
        "--hidden",
        "--no-ignore",
        "--iglob",
        "*.yaml",
        "--iglob",
        "*.yml",
    ]
    for pattern in patterns:
        command += ["-e", pattern]
    command += ["--", os.fspath(root)]
    try:
        completed = subprocess.run(command, check=False, capture_output=True)
    except OSError as exc:
        raise PrefilterError(f"cannot run ripgrep {label} prefilter: {exc}") from exc
    if completed.returncode not in {0, 1}:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise PrefilterError(f"{label} prefilter failed: {detail}")
    try:
        return {Path(raw.decode("utf-8")) for raw in completed.stdout.split(b"\0") if raw}
    except UnicodeDecodeError as exc:
        raise PrefilterError(f"ripgrep returned a non-UTF-8 {label} path: {exc}") from exc


def walked_paths(root: Path, label: str) -> set[Path]:
    """Every YAML under the root: a strict superset of what ripgrep would return."""
    if not root.is_dir():
        raise PrefilterError(f"cannot scan {label} root {root}: not a directory")

    def refuse(error: OSError) -> None:
        raise PrefilterError(f"cannot scan {label} root {root}: {error}") from error

    found: set[Path] = set()
    for directory, _subdirectories, filenames in os.walk(root, followlinks=False, onerror=refuse):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in YAML_SUFFIXES:
                found.add(Path(directory) / filename)
    return found


def candidate_paths(
    root: Path,
    patterns: Sequence[str],
    *,
    label: str,
    extra: Sequence[Path] = (),
) -> tuple[Path, ...]:
    """Records that could match ``patterns`` under ``root``, plus ``extra``, sorted.

    Over-inclusive on purpose. Callers parse every candidate, so a superset costs
    time and cannot change the result; a subset silently changes it.
    """
    if not patterns:
        raise PrefilterError(f"{label} prefilter needs at least one pattern")
    found = ripgrep_paths(root, patterns, label)
    if found is None:
        found = walked_paths(root, label)
    found.update(extra)
    return tuple(sorted(Path(os.path.abspath(os.fspath(path))) for path in found))
