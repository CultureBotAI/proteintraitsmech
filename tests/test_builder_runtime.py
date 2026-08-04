"""A builder's loop, actually run (#132).

Everything else asserting #104's skip-on-unreadable behaviour reads the SOURCE: that each
builder has an `except RecordError`, warns with a path, and does not widen to `Exception`.
None of that proves the handler runs. A builder could catch and then `raise`, or `break`
instead of `continue`, and every source-level check still passes.

This drives `build_metalpdb_causal_graphs.main()` over a temp directory containing a good
record, a malformed one, and another good one, and asserts on what actually happened.

`build_metalpdb` is the pattern because it is the smallest of the five causal-graph
builders at 301 lines — #132 suggested `build_mcsa`, which is 416 and additionally loads
an M-CSA cache. The rest are 334, 385 and 498.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _builder():
    import importlib.util

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    name = "_ptm_rt_metalpdb"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, SCRIPTS / "build_metalpdb_causal_graphs.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


GOOD = """identifier: proteintraitsmech:METALPDB_{n}
label: "site {n}"
definition: >-
  a metal site
definition_source: MetalPDB
trait_axis: STRUCTURE
trait_category: STRUCT_METAL_SITE
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: metal_coordination
    nodes: []
    edges: []
license: CC0
"""

# valid YAML everywhere except the causal_graphs section, which is what the builder reads
MALFORMED = """identifier: proteintraitsmech:METALPDB_BAD
label: "broken"
definition: >-
  a metal site
definition_source: MetalPDB
trait_axis: STRUCTURE
trait_category: STRUCT_METAL_SITE
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: [unclosed
license: CC0
"""


@pytest.fixture
def harness(tmp_path, monkeypatch):
    """A builder pointed at three records, with its heavy inputs stubbed out."""
    mod = _builder()
    (tmp_path / "aaa-good.yaml").write_text(GOOD.format(n=1), encoding="utf-8")
    (tmp_path / "mmm-bad.yaml").write_text(MALFORMED, encoding="utf-8")
    (tmp_path / "zzz-good.yaml").write_text(GOOD.format(n=2), encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    # the MetalPDB XML is ~GB and irrelevant here: the skip happens before it is used
    monkeypatch.setattr(mod, "wanted_codes", lambda: [])
    monkeypatch.setattr(mod, "load_sites", lambda codes: {})
    monkeypatch.setattr(sys, "argv", ["build_metalpdb_causal_graphs.py"])
    return mod, tmp_path


def test_one_unreadable_record_does_not_abort_the_run(harness, capsys):
    """The whole point of #104, asserted on behaviour rather than on source text."""
    mod, _ = harness
    rc = mod.main()
    err = capsys.readouterr().err
    assert rc == 0, "the run aborted instead of skipping the bad record"
    assert "WARN unreadable" in err, "the handler did not fire"
    assert "mmm-bad.yaml" in err, "the warning does not name the offending record"


def test_the_loop_continues_past_the_bad_record(harness, capsys):
    """`continue`, not `break`.

    The two good records sort either side of the malformed one, so the counter reaching
    2 proves the loop resumed rather than stopping at the failure.
    """
    mod, _ = harness
    mod.main()
    err = capsys.readouterr().err
    assert "already has a graph" in err
    line = next(ln for ln in err.splitlines() if "already has a graph" in ln)
    assert line.strip().endswith("2"), f"expected both good records counted, got {line!r}"


def test_the_skip_is_counted_exactly_once(harness, capsys):
    mod, _ = harness
    mod.main()
    err = capsys.readouterr().err
    line = next(ln for ln in err.splitlines() if "could not be read" in ln)
    assert line.strip().endswith("1"), f"expected exactly one skip, got {line!r}"


def test_the_unreadable_record_is_left_untouched(harness):
    """A record the builder cannot read must not be rewritten on the way past."""
    mod, tmp = harness
    before = (tmp / "mmm-bad.yaml").read_text(encoding="utf-8")
    mod.main()
    assert (tmp / "mmm-bad.yaml").read_text(encoding="utf-8") == before
