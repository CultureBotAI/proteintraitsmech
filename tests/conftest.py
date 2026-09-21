"""Shared test plumbing for checks that read production data from the checkout.

Most of the suite builds its inputs under ``tmp_path``. Six staging scripts have
an acceptance test that instead reads the real ``data/grounding`` registry and
ignored raw artifacts, so its outcome depends on the state of the checkout and
not only on the code. CI has no artifacts and skips them, which is how their
pins went stale unnoticed (#713, #734):

* each stage pins the ProteinReference registry it was reviewed against — a
  UniProt release, and for two of them an exact sha256. The committed registry
  left those pins behind in #690, and every stage has refused it since.

``production_registry_pin`` separates the two situations that look alike:

* the stage's pin is **listed in ``KNOWN_STALE_PINS``**: the stage cannot run
  against any current registry until someone re-pins or retires it, which is a
  tracked decision — the test is an expected failure naming the issue;
* the pin is **not** listed and the registry does not match it: that is news —
  a registry moved without its stages, or a batch is mid-install in this
  checkout — and the test fails, saying which.

Re-pinning a stage changes its pin value, so its entry stops applying by
itself; ``test_production_pins.py`` fails while an entry names a pin no stage
uses any more, so the table cannot outlive its reason.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# pin value → the issue tracking the decision to re-pin or retire the stage.
# Delete an entry in the same change that re-pins the last stage using it.
KNOWN_STALE_PINS = {
    "2026_02": "#734",
    "d587fad177207ca4f00d1dfb8649f4f9d2d21d01953d483f44a3a6e81acc729c": "#734",
}


def registry_releases(path: Path) -> tuple[set[str], int]:
    """(``uniprot_release`` values, rows that carry none) in a registry."""
    releases: set[str] = set()
    unlabelled = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            release = json.loads(line).get("uniprot_release")
            if release:
                releases.add(str(release))
            else:
                unlabelled += 1
    return releases, unlabelled


def pin_verdict(path: Path, *, release: str | None = None,
                sha256: str | None = None) -> tuple[str, str]:
    """``("ok" | "known_stale" | "mismatch", reason)`` for a stage's registry pins.

    An empty registry satisfies a release pin, as it does in the stages' own
    parsers. Rows without a release are a mismatch in their own right.
    """
    broken: list[tuple[str, str]] = []          # (pin value, what is wrong)
    if sha256 is not None:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sha256:
            broken.append((sha256, f"{path.name} is sha256 {actual[:12]}…, not the pinned "
                                   f"{sha256[:12]}…"))
    if release is not None:
        found, unlabelled = registry_releases(path)
        if unlabelled:
            broken.append((release, f"{unlabelled} row(s) of {path.name} carry no "
                                    f"uniprot_release"))
        elif found and found != {release}:
            broken.append((release, f"{path.name} carries UniProt release(s) "
                                    f"{sorted(found)}, not only the pinned {release!r}"))
    if not broken:
        return "ok", ""
    why = "; ".join(text for _, text in broken)
    issues = {KNOWN_STALE_PINS.get(pin) for pin, _ in broken}
    if None not in issues:
        return "known_stale", (f"{why}. The stage's pin is known to be stale and the stage "
                               f"cannot run until it is re-pinned or retired "
                               f"({', '.join(sorted(issues))})")
    return "mismatch", (f"{why}. This pin is not listed as known-stale: either the registry "
                        f"moved without re-pinning this stage, or a grounding batch is being "
                        f"installed in this checkout")


@pytest.fixture
def production_registry_pin():
    """``check(path, release=…, sha256=…)`` — see the module docstring."""

    def check(path: Path, *, release: str | None = None, sha256: str | None = None) -> None:
        verdict, why = pin_verdict(path, release=release, sha256=sha256)
        if verdict == "known_stale":
            pytest.xfail(why)
        if verdict == "mismatch":
            pytest.fail(why, pytrace=False)

    return check


def parse_porcelain_z(out: str) -> tuple[str, ...]:
    """Current paths from ``git status --porcelain -z`` output.

    ``-z`` gives raw, unquoted paths. A rename or copy entry is followed by a
    second NUL-terminated field holding the path it came from, which is dropped.
    """
    fields = out.split("\0")
    paths, i = [], 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if entry[0] in "RC" or entry[1] in "RC":
            i += 1
    return tuple(paths)


def _probe_dirty_grounding_files(run=subprocess.run) -> tuple[str, ...]:
    """Tracked files under data/grounding that differ from HEAD; () if git cannot say.

    ``--no-optional-locks`` matters here: plain ``git status`` may refresh the
    index and take ``index.lock``, and this runs in checkouts where another
    session may be committing at that moment.
    """
    try:
        out = run(["git", "--no-optional-locks", "status", "--porcelain", "-z",
                   "--untracked-files=no", "--", "data/grounding"],
                  cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        return ()
    return parse_porcelain_z(out)


@lru_cache(maxsize=1)
def _dirty_grounding_files() -> tuple[str, ...]:
    """The probe, once per session."""
    return _probe_dirty_grounding_files()


def checkout_state_note(dirty: tuple[str, ...]) -> str | None:
    """The note a failing production-data test gets when grounding data differs from HEAD."""
    if not dirty:
        return None
    shown = ", ".join(dirty[:4]) + (" …" if len(dirty) > 4 else "")
    return (f"{len(dirty)} tracked file(s) under data/grounding differ from HEAD in this "
            f"checkout ({shown}). If a grounding batch is being installed here, this test "
            f"describes the committed state and may fail until the batch and its pins are "
            f"committed together.")


@pytest.fixture
def production_pins():
    """The pure helpers, for tests of this plumbing (no ``import conftest`` needed)."""
    return SimpleNamespace(pin_verdict=pin_verdict, registry_releases=registry_releases,
                           checkout_state_note=checkout_state_note,
                           dirty_grounding_files=_dirty_grounding_files,
                           probe_dirty_grounding_files=_probe_dirty_grounding_files,
                           parse_porcelain_z=parse_porcelain_z,
                           KNOWN_STALE_PINS=KNOWN_STALE_PINS, REPO_ROOT=REPO_ROOT)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    # only tests that read the production registry; a tmp_path test gains nothing from it
    if report.when != "call" or not report.failed \
            or "production_registry_pin" not in getattr(item, "fixturenames", ()):
        return
    note = checkout_state_note(_dirty_grounding_files())
    if note:
        report.sections.append(("checkout state", note))
