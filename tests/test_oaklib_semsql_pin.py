"""The oaklib pin must keep `sqlite:obo:` off the retired semantic-sql S3 bucket (#646).

INCATools/semantic-sql removed public read from the raw S3 bucket
(semantic-sql#112). oaklib below 0.7.2 resolves `sqlite:obo:` selectors against
it; 0.7.2 moved the default to the CDN. This repo stayed on 0.6.23 — the last
pre-CDN release — long enough for the bucket to start answering 403, at which
point the eight adapters in conf/id_label_targets.yaml and every
`sqlite:obo:{onto}` in scripts/ground_categories.py were aimed at nothing on a
cache miss.

The reversion is invisible until it is catastrophic. With `~/.data/oaklib/`
warm, every lookup still succeeds on 0.6.23, so no test, gate or error message
distinguishes a correct pin from a reverted one — right up until a cache miss.
That includes the id↔label gate, which downloads through this path.

These assert the floor, not the installed version: CI resolves from the lock,
and a developer may legitimately be ahead.

Ported from MediaIngredientMech's guard of the same name.
"""

from __future__ import annotations

import re

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 0.7.2 introduced the CDN default, but declares `requires_python <3.14` while
# this project declares an unbounded `>=3.10`. 0.7.3 widened it to <3.15, so it
# is the lowest release installable across the range we claim to support.
#
# This constant is deliberately the DECLARED FLOOR, not the release that first
# carried the CDN. A constant set to 0.7.2 here would still accept a pyproject
# lowered to 0.7.2 and quietly undo the alignment.
MIN_OAKLIB = (0, 7, 3)

S3_HOST = "s3.amazonaws.com"


def _spec() -> str:
    data = tomllib.loads((REPO / "pyproject.toml").read_text())
    return next(d for d in data["project"]["dependencies"] if d.startswith("oaklib"))


def _floor(spec: str) -> tuple[int, ...] | None:
    """The `>=` bound in a requirement, or None if it carries none.

    Accepts two-, three-, or more-component bounds and pads to three (#648). A
    three-component-only pattern reads an ordinary `oaklib>=1.0` as "no lower
    bound" and fails pointing at the wrong problem.
    """
    match = re.search(r">=\s*(\d+(?:\.\d+)*)", spec)
    if not match:
        return None
    parts = tuple(int(p) for p in match.group(1).split("."))
    return parts + (0,) * (3 - len(parts))


def _is_retired_host(url: str) -> bool:
    """Whether a resolved URL base points at the bucket semantic-sql retired.

    Extracted so the judgement is exercised by a unit test rather than only by
    whichever oaklib happens to be installed. In a correctly pinned environment
    the assertion in test_the_resolved_default_is_not_the_retired_bucket can never
    fail, so deleting it was invisible until this predicate existed.
    """
    return S3_HOST in url


def _resolved_default() -> str:
    """The URL base oaklib will actually use, or an assertion naming why there is none.

    Pre-0.7.2 oaklib does not hold this constant at a different value -- it does not
    define it at all, so a bare import raises ImportError and reports nothing about
    the retired bucket (#648). Verified against 0.6.23:

        ImportError: cannot import name 'SEMSQL_SQLITE_URL_BASE' from 'oaklib.constants'
    """
    try:
        from oaklib.constants import SEMSQL_SQLITE_URL_BASE
    except ImportError as exc:
        raise AssertionError(
            f"oaklib exposes no SEMSQL_SQLITE_URL_BASE ({exc}). Releases before 0.7.2 "
            "hardcode the retired bbop-sqlite S3 bucket instead, so this is what a "
            "reverted pin looks like. If upstream renamed the constant, point this "
            "guard at the new name rather than deleting it."
        ) from exc
    return SEMSQL_SQLITE_URL_BASE


def test_the_pin_floor_keeps_the_cdn_default():
    spec = _spec()
    floor = _floor(spec)
    assert floor is not None, (
        f"no lower bound in {spec!r} — below 0.7.2, `sqlite:obo:` resolves against "
        "the raw S3 bucket semantic-sql retired"
    )
    assert floor >= MIN_OAKLIB, (
        f"{spec!r} is below {'.'.join(map(str, MIN_OAKLIB))}; 0.7.2 carries the CDN "
        "default but is not installable on 3.14, which requires-python allows"
    )


def test_a_two_component_floor_is_read_as_a_floor():
    """`oaklib>=1.0` is an ordinary bump, not an absent bound (#648)."""
    assert _floor("oaklib>=1.0") == (1, 0, 0)
    assert _floor("oaklib>=0.7.3") == (0, 7, 3)
    assert _floor("oaklib>=0.7.3,<0.8") == (0, 7, 3)
    assert _floor("oaklib") is None
    assert _floor("oaklib>=1.0") >= MIN_OAKLIB
    assert _floor("oaklib>=0.6") < MIN_OAKLIB


def test_the_lockfile_agrees_with_the_floor():
    """A floor the lock does not satisfy is a floor in name only."""
    lock = (REPO / "uv.lock").read_text()
    match = re.search(r'name = "oaklib"\nversion = "(\d+)\.(\d+)\.(\d+)"', lock)
    assert match, "oaklib absent from uv.lock"
    assert tuple(int(g) for g in match.groups()) >= MIN_OAKLIB


def test_the_resolved_default_is_not_the_retired_bucket():
    """Pin the property, not a proxy for it.

    The two tests above track a version number, which is what we can control but
    not what we care about. This reads the constant oaklib will actually use, so a
    release that keeps the version but changes the default is still caught.

    It is not resilient to a rename: the constant is absent on pre-0.7.2 oaklib
    and a rename looks identical from here. _resolved_default turns both into an
    assertion that says so, rather than the bare ImportError this raised (#648).
    """
    resolved = _resolved_default()

    assert not _is_retired_host(resolved), (
        f"oaklib resolves sqlite:obo: against {resolved}, the raw S3 "
        "bucket INCATools/semantic-sql retired (semantic-sql#112)"
    )
    assert resolved.startswith("https://"), resolved


def test_the_retired_host_is_recognised_whatever_is_installed():
    """The judgement itself, independent of the resolved value.

    With a correct pin the live assertion is unfalsifiable, so this is what holds
    it honest: the retired bucket must read as retired and the CDN must not.
    """
    assert _is_retired_host("https://s3.amazonaws.com/bbop-sqlite/{prefix}.db.gz")
    assert _is_retired_host("http://s3.amazonaws.com/bbop-sqlite/go.db.gz")
    assert not _is_retired_host("https://semanticsql.berkeleybop.io")
    assert not _is_retired_host("https://semanticsql.berkeleybop.io/go.db.gz")


def test_a_missing_constant_reports_the_reverted_pin_not_an_import_error(monkeypatch):
    """Pre-0.7.2 oaklib has no such constant, and a rename looks identical (#648).

    Simulated rather than waited for: the guard must turn both into an assertion
    that names the retired bucket, never a bare ImportError or -- worse -- a
    silently substituted default that reports success.
    """
    import sys
    import types

    monkeypatch.setitem(sys.modules, "oaklib.constants", types.ModuleType("oaklib.constants"))
    with pytest.raises(AssertionError, match="no SEMSQL_SQLITE_URL_BASE"):
        _resolved_default()


def test_the_setuptools_bound_survives(monkeypatch):
    """oaklib imports eutils, which imports pkg_resources; setuptools 82 removed it.

    Nothing else in pyproject.toml bounds setuptools, so without this bound a
    relock can take it to 82 and every `import oaklib` dies. That failure is loud
    once it happens -- but the bound going missing is silent until someone
    relocks, which is exactly the gap this closes.
    """
    data = tomllib.loads((REPO / "pyproject.toml").read_text())
    spec = next((d for d in data["project"]["dependencies"] if d.startswith("setuptools")), None)
    assert spec, "no setuptools bound; a relock can take it to 82 and break `import oaklib`"
    match = re.search(r"<\s*(\d+)", spec)
    assert match and int(match.group(1)) <= 82, (
        f"{spec!r} does not keep setuptools below 82, which removed pkg_resources"
    )
