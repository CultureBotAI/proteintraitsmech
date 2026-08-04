"""The same runtime harness, across all five causal-graph builders (#141).

`test_builder_runtime.py` proved the pattern on `build_metalpdb`. This generalises it, so
every builder's skip-on-unreadable path (#104) is asserted by *running the loop*, not by
reading the source. The distinction is not academic: on `build_metalpdb` this caught
`break`-instead-of-`continue`, which every source-level check passes.

Two loop shapes, discovered rather than assumed:

* **glob-driven** — `build_ec`, `build_biolip`, `build_rhea`, `build_metalpdb` all iterate
  `sorted(ROOT.glob("*.yaml"))`, so pointing their records constant at a temp directory is
  enough;
* **cache-driven** — `build_mcsa` iterates `sorted(cache)` from an M-CSA JSONL and looks
  records up through `record_files()`. Its records constant still needs patching, but the
  loop only reaches a record if the cache mentions it, so the cache must be stubbed to
  name the fixtures.

Every heavy input is stubbed. None is read before the skip happens, so nothing is lost by
not loading a multi-gigabyte XML or an RDF dump to test a `continue`.

**The stubs are deliberately minimal, and only valid for the skip path.** The Rhea one
returns an object with `.reactions` alone, while the builders also call
`participants_of`, `lr_child`, `reactive_parts` and `.sides` further down. These tests
never reach that code — every fixture record either already has the graph or fails to
parse — so the stub is sufficient here and would NOT be sufficient for a test that
exercises graph construction. Anyone extending this file to cover the build path needs a
fuller fake, not a wider `BUILDERS` table.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"

RECORD = """identifier: {ident}
label: "record {n}"
definition: >-
  a record
definition_source: test
trait_axis: {axis}
trait_category: {category}
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: {graph_id}
    nodes: []
    edges: []
license: CC0
"""

MALFORMED = """identifier: {ident}
label: "broken"
definition: >-
  a record
definition_source: test
trait_axis: {axis}
trait_category: {category}
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: [unclosed
license: CC0
"""

# module, records-dir constant, graph id it checks, and the functions whose heavy inputs
# must not load. `stub_loaders` maps name -> value the stub returns.
BUILDERS = [
    dict(mod="build_ec_causal_graphs", root="ROOT", graph_id="reaction_chemistry",
         ident="EC:1.1.1.{n}", axis="FUNCTION", category="FUNC_ENZYMATIC_ACTIVITY",
         stubs={"kb_identifiers": {}}, rhea=True),
    dict(mod="build_rhea_causal_graphs", root="ROOT", graph_id="reaction_chemistry",
         ident="RHEA:1000{n}", axis="FUNCTION", category="FUNC_ENZYMATIC_ACTIVITY",
         stubs={"kb_identifiers": {}}, rhea=True),
    dict(mod="build_biolip_causal_graphs", root="ROOT", graph_id="ligand_binding",
         ident="proteintraitsmech:BIOLIP_{n}", axis="STRUCTURE",
         category="STRUCT_BINDING_SITE",
         stubs={"biolip_index": {}, "ligand_table": {}, "chebi_by_inchikey": {}}),
    dict(mod="build_metalpdb_causal_graphs", root="ROOT", graph_id="metal_coordination",
         ident="proteintraitsmech:METALPDB_{n}", axis="STRUCTURE",
         category="STRUCT_METAL_SITE",
         stubs={"wanted_codes": [], "load_sites": {}}),
]


def _load(name):
    import importlib.util

    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    key = f"_ptm_rt_{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[key] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_three(tmp_path, cfg):
    """A good record, a malformed one, and another good one — in sort order."""
    common = dict(axis=cfg["axis"], category=cfg["category"], graph_id=cfg["graph_id"])
    (tmp_path / "aaa.yaml").write_text(
        RECORD.format(ident=cfg["ident"].format(n=1), n=1, **common), encoding="utf-8")
    (tmp_path / "mmm.yaml").write_text(
        MALFORMED.format(ident=cfg["ident"].format(n=2), axis=cfg["axis"],
                         category=cfg["category"]), encoding="utf-8")
    (tmp_path / "zzz.yaml").write_text(
        RECORD.format(ident=cfg["ident"].format(n=3), n=3, **common), encoding="utf-8")


def _arrange(cfg, tmp_path, monkeypatch):
    mod = _load(cfg["mod"])
    _write_three(tmp_path, cfg)
    monkeypatch.setattr(mod, cfg["root"], tmp_path)
    for fn_name, value in cfg["stubs"].items():
        monkeypatch.setattr(mod, fn_name, lambda *a, _v=value, **k: _v)
    if cfg.get("rhea"):
        # rhea_rdf.load() parses a 3M-line gzip; the skip happens long before it is used
        rhea = _load("rhea_rdf")
        monkeypatch.setattr(rhea, "load", lambda *a, **k: type("R", (), {"reactions": {}})())
        monkeypatch.setattr(mod, "rhea_rdf", rhea)
    monkeypatch.setattr(sys, "argv", [cfg["mod"] + ".py"])
    return mod


IDS = [c["mod"].replace("_causal_graphs", "") for c in BUILDERS]


@pytest.mark.parametrize("cfg", BUILDERS, ids=IDS)
def test_one_unreadable_record_does_not_abort_the_run(cfg, tmp_path, monkeypatch, capsys):
    """#104's whole point, asserted per builder on behaviour rather than source text."""
    mod = _arrange(cfg, tmp_path, monkeypatch)
    rc = mod.main()
    err = capsys.readouterr().err
    assert rc == 0, f"{cfg['mod']} aborted instead of skipping the bad record"
    assert "WARN unreadable" in err, f"{cfg['mod']}: the handler did not fire"
    assert "mmm.yaml" in err, f"{cfg['mod']}: the warning does not name the record"


@pytest.mark.parametrize("cfg", BUILDERS, ids=IDS)
def test_the_loop_continues_past_the_bad_record(cfg, tmp_path, monkeypatch, capsys):
    """`continue`, not `break`.

    The good records sort either side of the malformed one, so both being counted is
    what proves the loop resumed rather than stopping at the failure.
    """
    mod = _arrange(cfg, tmp_path, monkeypatch)
    mod.main()
    err = capsys.readouterr().err
    line = next((ln for ln in err.splitlines()
                 if "already" in ln and "graph" in ln), None)
    assert line is not None, f"{cfg['mod']}: no already-has-a-graph line in:\n{err}"
    assert line.split()[-1] == "2", f"{cfg['mod']}: expected both good records, got {line!r}"


@pytest.mark.parametrize("cfg", BUILDERS, ids=IDS)
def test_the_unreadable_record_is_left_untouched(cfg, tmp_path, monkeypatch):
    """A record the builder cannot read must not be rewritten on the way past."""
    mod = _arrange(cfg, tmp_path, monkeypatch)
    before = (tmp_path / "mmm.yaml").read_text(encoding="utf-8")
    mod.main()
    assert (tmp_path / "mmm.yaml").read_text(encoding="utf-8") == before


def test_every_causal_graph_builder_is_covered():
    """A new builder must not slip past this file unnoticed.

    Discovered from disk rather than hardcoded, for the same reason
    `test_each_builder_checks_its_own_graph_id` is: the first version of that test
    listed five builders and silently omitted a sixth.
    """
    on_disk = {p.stem for p in SCRIPTS.glob("build_*_causal_graphs.py")}
    covered = {c["mod"] for c in BUILDERS} | {"build_mcsa_causal_graphs"}
    assert on_disk == covered, f"uncovered builders: {sorted(on_disk - covered)}"


# --- build_mcsa: the cache-driven shape -------------------------------------------

MCSA_RECORD = """identifier: MCSA:{n}
label: "site {n}"
definition: >-
  a catalytic site
definition_source: M-CSA
trait_axis: STRUCTURE
trait_category: STRUCT_ACTIVE_SITE
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: catalysis
    nodes: []
    edges: []
license: CC0
"""

MCSA_MALFORMED = """identifier: MCSA:{n}
label: "broken"
definition: >-
  a catalytic site
definition_source: M-CSA
trait_axis: STRUCTURE
trait_category: STRUCT_ACTIVE_SITE
term_kind: CLASS
mapping_status: SEEDED
causal_graphs:
  - graph_id: [unclosed
license: CC0
"""


@pytest.fixture
def mcsa(tmp_path, monkeypatch):
    """`build_mcsa` iterates its M-CSA cache, not the records directory.

    So the cache has to name the fixture records or the loop never reaches them — the
    records constant alone is not enough, which is why this builder needs its own
    fixture rather than a row in BUILDERS.
    """
    mod = _load("build_mcsa_causal_graphs")
    (tmp_path / "aaa.yaml").write_text(MCSA_RECORD.format(n=1), encoding="utf-8")
    (tmp_path / "mmm.yaml").write_text(MCSA_MALFORMED.format(n=2), encoding="utf-8")
    (tmp_path / "zzz.yaml").write_text(MCSA_RECORD.format(n=3), encoding="utf-8")
    monkeypatch.setattr(mod, "MCSA_DIR", tmp_path)
    # INT keys, because record_files() does `out[int(m.group(1))]`. With strings every
    # id misses and the loop counts `no_record` instead of ever reaching has_graph —
    # which is what this harness surfaced the first time it ran.
    monkeypatch.setattr(mod, "load_cache", lambda: {1: {"mcsa_id": 1},
                                                    2: {"mcsa_id": 2},
                                                    3: {"mcsa_id": 3}})
    monkeypatch.setattr(mod, "kb_cath", lambda: set())
    monkeypatch.setattr(sys, "argv", ["build_mcsa_causal_graphs.py"])
    return mod, tmp_path


def test_mcsa_one_unreadable_record_does_not_abort_the_run(mcsa, capsys):
    mod, _ = mcsa
    rc = mod.main()
    err = capsys.readouterr().err
    assert rc == 0, "build_mcsa aborted instead of skipping the bad record"
    assert "WARN unreadable" in err, "the handler did not fire"
    assert "mmm.yaml" in err, "the warning does not name the record"


def test_mcsa_the_loop_continues_past_the_bad_record(mcsa, capsys):
    mod, _ = mcsa
    mod.main()
    err = capsys.readouterr().err
    line = next((ln for ln in err.splitlines() if "skip_has_graph" in ln), None)
    assert line is not None, f"no skip_has_graph line in:\n{err}"
    assert line.split()[-1] == "2", f"expected both good records counted, got {line!r}"


def test_mcsa_the_unreadable_record_is_left_untouched(mcsa):
    mod, tmp = mcsa
    before = (tmp / "mmm.yaml").read_text(encoding="utf-8")
    mod.main()
    assert (tmp / "mmm.yaml").read_text(encoding="utf-8") == before
