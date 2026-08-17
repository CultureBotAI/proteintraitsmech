"""The cross-family config-fit sweep had no test file at all (#469).

It reported "accepted by NO config of any of their families: 0" and exited 0, and until
this branch it printed that same line having globbed a cwd-relative path that matched
nothing. Two indistinguishable zeros, no caller other than `just audit-fit`, and nothing
in CI -- so the clean answer was unfalsifiable.

Its sibling has exactly this canary (`test_refused_drafts_audit.py::test_the_scan_finds
_drafts_at_all`: "a scan that reads no files would also report 0 accepted"). This is that,
for this script.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_config_fit.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_config_fit", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_importing_it_does_no_work():
    """It ran the whole 7,211-record sweep at import time, which is what
    `test_every_seeder_is_importable` was tripping over -- and with the release present it
    ran that sweep inside the test suite instead of importing a module."""
    mod = _load()
    assert hasattr(mod, "main"), "the sweep must live in main(), not at module scope"


def test_every_path_it_reads_is_absolute():
    """The corpus glob was the literal 'data/traits/function/resistance/aro'. From any cwd
    but the repo root that matched nothing, printed 0, and exited 0 -- a sweep that
    examined nothing reporting a clean corpus, which is #418/#432's whole subject."""
    mod = _load()
    assert mod.E.ARO_DIR.is_absolute() and mod.E.OBO.is_absolute()
    src = SCRIPT.read_text(encoding="utf-8")
    assert "pathlib.Path('data/" not in src and 'pathlib.Path("data/' not in src, \
        "a cwd-relative corpus path is back"


def test_it_runs_from_a_foreign_cwd(tmp_path):
    """The regression test for the above, at the process level: same numbers from /tmp as
    from the repo root, not a silent 0."""
    if not (REPO / "data" / "raw" / "aro" / "aro.obo").exists():
        pytest.skip("data/raw/aro/aro.obo absent (gitignored); run just fetch-aro")
    out = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                         cwd=tmp_path)
    assert out.returncode == 0, out.stdout + out.stderr
    import re
    m = re.search(r"curated records under a known family: ([\d,]+)", out.stdout)
    assert m, out.stdout
    assert int(m.group(1).replace(",", "")) > 1_000, \
        f"scanned too few to be the corpus: {out.stdout!r}"


def test_it_refuses_a_tree_with_no_curated_records(tmp_path, monkeypatch):
    """The zero that matters. With nothing to examine it must not print a clean 0."""
    mod = _load()
    if not mod.E.OBO.exists():
        pytest.skip("data/raw/aro/aro.obo absent (gitignored); run just fetch-aro")
    empty = tmp_path / "aro"
    empty.mkdir()
    (empty / "x.yaml").write_text("identifier: ARO:1\n", encoding="utf-8")
    monkeypatch.setattr(mod.E, "ARO_DIR", empty)
    assert mod.main() == 1


def test_it_refuses_a_missing_release(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setattr(mod.E, "OBO", tmp_path / "absent.obo")
    assert mod.main() == 1
