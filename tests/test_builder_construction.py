"""The causal-graph builders' CONSTRUCTION path, not just their skip path (#144).

`test_builder_runtime_all.py` drives all five builders' main loops, but every
fixture there either already has the graph or fails to parse, so the loop always
takes an early `continue`. Everything after `if seen: continue` — assembling the
graph, splicing it in, the two refusal paths, the `mapping_status` flip and the
write — has never been executed by a test. Six builders write 40,115 graphs.

#99 named three mutations the suite tolerated, and **two of them are defects that
already shipped once each and were fixed**:

  * comparing the FINAL text rather than the graph splice, so a refused graph
    looked like success and wrote a history entry claiming a graph that was not
    there (found in #131's review);
  * moving the `written`/`nodes`/`edges` increments before the splices, so
    refused records were counted as written.

Both live entirely in the construction path. This file covers `build_metalpdb`,
which #144 names as one of the two cheapest starting points; the other builders
follow the same shape and are tracked separately.

WHY A FULLER FAKE, NOT ANOTHER ROW IN `BUILDERS`
------------------------------------------------
The existing harness says so explicitly: its stubs are "deliberately minimal, and
only valid for the skip path". Reaching `build()` means supplying what it
actually reads — a CHEBI metal on `chemical_participants`, a PDB code in a
`canonical_examples` note, and a site whose nuclearity, periodic name and
protein ligands all match. Anything less returns `None` and skips, which would
look like a passing test while testing nothing.
"""

from __future__ import annotations

import importlib
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

BUILDER = "build_metalpdb_causal_graphs"

# A record the builder will actually build from: STRUCT_METAL_SITE, a CHEBI
# metal, and an exemplar whose note carries a PDB code PDBRE can find.
RECORD = """identifier: MetalPDB:ZN_MONONUCLEAR_TEST
label: "mononuclear zinc site"
definition: >-
  a test metal site
definition_source: MetalPDB
trait_axis: STRUCTURE
trait_category: STRUCT_METAL_SITE
term_kind: CLASS
mapping_status: SEEDED
chemical_participants:
  - name: Zinc
    chebi: CHEBI:29105
canonical_examples:
  - protein_id: UniProtKB:P00001
    note: "MetalPDB entry PDB 1abc, site A"
license: CC-BY 4.0
"""

# One MetalPDB site matching that record: mononuclear zinc, two histidines with
# residue numbers, which is what `build` requires to emit residue nodes.
SITE = {
    "site_name": "ZN_1",
    "nuclearity": "mononuclear",
    "symbol": "Zn",
    "periodic_name": "Zinc",
    "coordination_number": "4",
    "geometry": "tetrahedral",
    "ligands": [
        {"residue_name": "HIS", "residue_pdb_number": "94", "chain_letter": "A",
         "donor": "NE2", "distance": "2.1"},
        {"residue_name": "HIS", "residue_pdb_number": "96", "chain_letter": "A",
         "donor": "ND1", "distance": "2.0"},
        # a water ligand: real chemistry, deliberately NOT a protein trait node
        {"residue_name": "HOH", "residue_pdb_number": "201", "chain_letter": "A",
         "donor": "O", "distance": "2.2"},
    ],
}
SITES = {"1abc": [SITE]}


def test_the_fake_site_matches_what_load_sites_produces():
    """A fake that drifts from the real parser tests nothing. `symbol` was
    missing from the first draft and the builder raised KeyError -- which was the
    fixture being wrong, not the code. Pinned to the keys `load_sites` writes so
    the next omission fails here with a clear message instead of a KeyError deep
    in graph assembly.
    """
    import ast
    src = (REPO / "scripts" / f"{BUILDER}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "load_sites")
    # the dict literal appended per site is the one with a "ligands" key
    site_keys = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Dict):
            keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            if "ligands" in keys:
                site_keys = keys
    assert site_keys, "could not find load_sites' site dict"
    assert site_keys <= set(SITE), f"fake site is missing {site_keys - set(SITE)}"


@pytest.fixture
def builder(tmp_path, monkeypatch):
    """The builder pointed at a temp corpus, with its heavy inputs stubbed.

    Only `wanted_codes` and `load_sites` are faked — everything from `build()`
    onward is the real code, which is the entire point of this file.
    """
    mod = importlib.import_module(BUILDER)
    root = tmp_path / "metalpdb"
    root.mkdir()
    monkeypatch.setattr(mod, "ROOT", root)
    monkeypatch.setattr(mod, "wanted_codes", lambda: ["1abc"])
    monkeypatch.setattr(mod, "load_sites", lambda codes: SITES)
    monkeypatch.setattr(sys, "argv", [BUILDER, "--apply"])
    return mod, root


def run(mod, capsys):
    assert mod.main() == 0
    return capsys.readouterr().err


# --- the construction path actually runs -------------------------------------------

def test_a_graph_is_built_and_written(builder, capsys):
    """The baseline the whole file rests on: reach `build()`, emit a graph, write
    it. If this ever starts skipping, every assertion below is vacuous."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    err = run(mod, capsys)
    assert "written" in err
    rec = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))
    graphs = rec["causal_graphs"]
    assert len(graphs) == 1 and graphs[0]["graph_id"] == "metal_coordination"
    assert graphs[0]["nodes"] and graphs[0]["edges"]


def test_every_edge_carries_evidence(builder, capsys):
    """The skill's non-negotiable, and closed-mode validation enforces it on the
    corpus — but only for records that reach the corpus. This asserts the builder
    never emits an evidence-less edge in the first place."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    rec = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))
    for edge in rec["causal_graphs"][0]["edges"]:
        assert edge.get("evidence"), f"edge {edge} has no evidence"
        assert all(e.get("reference") for e in edge["evidence"])


def test_non_protein_ligands_are_not_written_as_nodes(builder, capsys):
    """The water in the fixture is real chemistry and deliberately not a protein
    trait; the builder's docstring says so. A node for it would be a claim the
    record is not making."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    rec = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))
    labels = " ".join(str(n) for n in rec["causal_graphs"][0]["nodes"])
    assert "HOH" not in labels


def test_status_flips_and_history_is_recorded(builder, capsys):
    """Adding a graph is the curation act that makes a record REVIEWED, and the
    history is the audit trail for it."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    rec = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))
    assert rec["mapping_status"] == "REVIEWED"
    assert len(rec["curation_history"]) == 1
    assert "metal_coordination" in rec["curation_history"][0]["action"]


# --- the refusal paths, which are the reason #144 was filed -------------------------

def test_a_refused_graph_splice_writes_nothing(builder, capsys):
    """THE SHIPPED DEFECT (#131). `append_to_section` refuses a key carrying an
    inline value it cannot safely extend. Comparing the FINAL text rather than
    the graph splice made that refusal look like success — the record kept no
    graph but was flipped to REVIEWED and given a history entry claiming one.
    """
    mod, root = builder
    p = root / "r.yaml"
    p.write_text(RECORD.replace("license: CC-BY 4.0",
                                "causal_graphs: []\nlicense: CC-BY 4.0"),
                 encoding="utf-8")
    err = run(mod, capsys)
    assert "could not splice the graph" in err
    rec = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert rec["causal_graphs"] == [], "a graph was written despite the refusal"
    assert rec["mapping_status"] == "SEEDED", "status flipped on a refused splice"
    assert "curation_history" not in rec, "history claims a graph that is absent"


def test_a_refused_history_splice_writes_nothing(builder, capsys):
    """The second half. The graph splice succeeds, the history splice is refused,
    and writing anyway would flip mapping_status to REVIEWED with no audit trail
    of why — a curated record nobody can trace."""
    mod, root = builder
    p = root / "r.yaml"
    p.write_text(RECORD.replace("license: CC-BY 4.0",
                                "curation_history: []\nlicense: CC-BY 4.0"),
                 encoding="utf-8")
    err = run(mod, capsys)
    assert "could not splice the history" in err
    rec = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert "causal_graphs" not in rec, "graph written despite the history refusal"
    assert rec["mapping_status"] == "SEEDED"


def test_counters_do_not_count_a_refused_record_as_written(builder, capsys):
    """#99's third mutation: moving the `written`/`nodes`/`edges` increments back
    before the splices. A refused record would be reported as written, and the
    run's own summary would be the only evidence — wrong."""
    mod, root = builder
    (root / "ok.yaml").write_text(RECORD, encoding="utf-8")
    (root / "bad.yaml").write_text(
        RECORD.replace("MetalPDB:ZN_MONONUCLEAR_TEST", "MetalPDB:ZN_REFUSED")
              .replace("license: CC-BY 4.0", "causal_graphs: []\nlicense: CC-BY 4.0"),
        encoding="utf-8")
    err = run(mod, capsys)
    written = [ln for ln in err.splitlines() if ln.strip().startswith("written")]
    assert written, err
    assert written[0].split()[-1] == "1", f"refused record counted as written: {written}"


# --- idempotence --------------------------------------------------------------------

def test_a_second_run_adds_nothing(builder, capsys):
    """`has_graph` is what makes a re-run safe. #99's first mutation — using a
    sibling builder's graph_id — would duplicate a graph into every record on the
    next run, and only a second run can catch it."""
    mod, root = builder
    p = root / "r.yaml"
    p.write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    first = p.read_text(encoding="utf-8")
    err = run(mod, capsys)
    assert "already has a graph" in err
    assert p.read_text(encoding="utf-8") == first


# --- review round 1: the graph's SHAPE, not just its presence -----------------------

def test_the_graph_has_exactly_the_expected_nodes_and_edges(builder, capsys):
    """Asserting only that nodes and edges are non-empty would pass on a graph
    with the wrong content. The fixture's site has three ligands, two of them
    protein, so the shape is fully determined: metal + site + 2 residues, and
    each residue coordinates the metal and is part of the site, plus the metal's
    own part-of edge."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    g = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))["causal_graphs"][0]
    assert [n["node_type"] for n in g["nodes"]] == \
        ["CHEMICAL", "MOTIF", "RESIDUE", "RESIDUE"]
    assert len(g["edges"]) == 5, [e["predicate"] for e in g["edges"]]
    assert {e["object"] for e in g["edges"]} == {"metal", "site"}


def test_the_metal_node_is_grounded_to_the_records_chebi(builder, capsys):
    """"Ground the node, cite the edge" — a CHEMICAL node with no CHEBI is a
    label, not a grounding."""
    mod, root = builder
    (root / "r.yaml").write_text(RECORD, encoding="utf-8")
    run(mod, capsys)
    g = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))["causal_graphs"][0]
    metal = next(n for n in g["nodes"] if n["node_id"] == "metal")
    assert metal["grounding"] == "CHEBI:29105"


SECOND_SITE = dict(SITE, site_name="ZN_2",
                   ligands=[{"residue_name": "HIS", "residue_pdb_number": "94",
                             "chain_letter": "A", "donor": "NE2", "distance": "2.1"}])


def test_the_same_residue_number_in_two_structures_stays_two_nodes(tmp_path,
                                                                   monkeypatch,
                                                                   capsys):
    """A documented invariant with a stated failure mode, and nothing tested it.

    The builder puts the PDB code in the residue node id, with the comment: "the
    same residue number in two exemplar structures is two different residues in
    two different proteins, and must not collapse into one node". Drop the code
    from the id and His94 of 1abc silently becomes His94 of 2xyz — one node
    carrying two proteins' evidence.
    """
    mod = importlib.import_module(BUILDER)
    root = tmp_path / "metalpdb"
    root.mkdir()
    monkeypatch.setattr(mod, "ROOT", root)
    monkeypatch.setattr(mod, "wanted_codes", lambda: ["1abc", "2xyz"])
    monkeypatch.setattr(mod, "load_sites",
                        lambda codes: {"1abc": [SITE], "2xyz": [SECOND_SITE]})
    monkeypatch.setattr(sys, "argv", [BUILDER, "--apply"])
    (root / "r.yaml").write_text(
        RECORD.replace('    note: "MetalPDB entry PDB 1abc, site A"',
                       '    note: "MetalPDB entry PDB 1abc, site A"\n'
                       '  - protein_id: UniProtKB:P00002\n'
                       '    note: "MetalPDB entry PDB 2xyz, site A"'),
        encoding="utf-8")
    run(mod, capsys)
    g = yaml.safe_load((root / "r.yaml").read_text(encoding="utf-8"))["causal_graphs"][0]
    residues = [n["node_id"] for n in g["nodes"] if n["node_type"] == "RESIDUE"]
    assert len(residues) == len(set(residues)), "residue node ids collide"
    assert any("1abc" in r for r in residues) and any("2xyz" in r for r in residues), \
        f"the PDB code is not in the residue node id: {residues}"
