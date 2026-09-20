"""Shared test plumbing for checks that read production data from the checkout.

Most of the suite builds its inputs under ``tmp_path``. A handful of acceptance
tests instead read the real ``data/grounding`` registry and ignored raw
artifacts, so their outcome depends on the state of the checkout, not only on
the code. Two things made those failures hard to read (#713, #734):

* a staging script pins the ProteinReference registry it was reviewed against
  (a UniProt release, or an exact sha256). When the committed registry moves
  on, the stage refuses it and its acceptance test fails wherever the raw
  artifacts exist — and nowhere else, because CI has none and skips it;
* a batch installer rewriting ``data/grounding`` in the same checkout makes
  otherwise-correct pins fail until the batch is committed.

``production_registry_pin`` turns the first case into an *expected failure*
that names the pin and the tracking issue, and that stops applying by itself
once the pin matches again. The report hook labels the second case.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PIN_ISSUE = "#734"


def registry_releases(path: Path) -> set[str]:
    """Every ``uniprot_release`` value in a ProteinReference registry."""
    releases: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                releases.add(str(json.loads(line).get("uniprot_release")))
    return releases


def registry_pin_mismatch(path: Path, *, release: str | None = None,
                          sha256: str | None = None) -> str | None:
    """Why the registry at ``path`` is not the one a stage is pinned to, or None."""
    if sha256 is not None:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sha256:
            return (f"{path.name} is sha256 {actual[:12]}…, but the stage is pinned to "
                    f"{sha256[:12]}…")
    if release is not None:
        found = registry_releases(path)
        if found != {release}:
            return (f"{path.name} carries UniProt release(s) {sorted(found)}, but the "
                    f"stage is pinned to {release!r}")
    return None


@pytest.fixture
def production_registry_pin():
    """``check(path, release=…, sha256=…)``: xfail unless the production
    registry is the snapshot the stage under test is pinned to."""

    def check(path: Path, *, release: str | None = None, sha256: str | None = None) -> None:
        why = registry_pin_mismatch(path, release=release, sha256=sha256)
        if why:
            pytest.xfail(f"{why}; the stage cannot run against this registry until it is "
                         f"re-pinned or retired ({PIN_ISSUE})")

    return check


@lru_cache(maxsize=1)
def _dirty_grounding_files() -> tuple[str, ...]:
    """Tracked files under data/grounding that differ from HEAD (once per session)."""
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no", "--", "data/grounding"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return ()
    return tuple(line[3:] for line in out.splitlines() if line.strip())


def checkout_state_note(dirty: tuple[str, ...]) -> str | None:
    """The note a failing test gets when grounding data differs from HEAD."""
    if not dirty:
        return None
    shown = ", ".join(dirty[:4]) + (" …" if len(dirty) > 4 else "")
    return (f"{len(dirty)} tracked file(s) under data/grounding differ from HEAD in this "
            f"checkout ({shown}). If a grounding batch is being installed here, tests that "
            f"read production data describe the committed state and may fail until the "
            f"batch and its pins are committed together.")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    note = checkout_state_note(_dirty_grounding_files())
    if note:
        report.sections.append(("checkout state", note))
