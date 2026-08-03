"""Tests for scripts/record_io.py — issue #96, the repo's first test module.

Each test here corresponds to a defect that actually shipped, or to the code path
that a defect hid in. The comments name which, so a future reader can tell these
apart from speculative coverage.

Run with `just test` (or `uv run pytest tests/`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from record_io import append_to_section, has_graph, insert_before_license  # noqa: E402

GRAPH_BLOCK = yaml.safe_dump(
    {"causal_graphs": [{"graph_id": "g1", "nodes": [{"node_id": "n"}], "edges": []}]},
    sort_keys=False, allow_unicode=True, width=100)
HIST_BLOCK = yaml.safe_dump(
    {"curation_history": [{"timestamp": "t1", "curator": "c", "action": "first"}]},
    sort_keys=False, allow_unicode=True, width=100)

BARE = """identifier: RHEA:99999
label: "a + b = c"
definition: >-
  test record
trait_axis: FUNCTION
evidence:
- reference: PMID:1
license: CC-BY 4.0
"""

NO_LICENSE = """identifier: RHEA:99998
label: "d = e"
trait_axis: FUNCTION
"""


# --- append_to_section -------------------------------------------------------

def test_inserts_whole_block_when_key_absent():
    """THE SHIPPED DEFECT. The old splicer stripped `causal_graphs:` off the payload
    unconditionally and only restored it on one of three branches, so a record with
    no such key received a bare `- graph_id: …` sequence item directly under the
    top-level mapping. That is unparseable, and the caller's `out == text` guard did
    not catch it because the text had in fact changed."""
    out = append_to_section(BARE, "causal_graphs", GRAPH_BLOCK)
    rec = yaml.safe_load(out)                      # would raise before the fix
    assert [g["graph_id"] for g in rec["causal_graphs"]] == ["g1"]
    assert rec["license"] == "CC-BY 4.0"           # key inserted BEFORE license
    assert rec["identifier"] == "RHEA:99999"


def test_appends_to_existing_section_in_order():
    """`curation_history` events must read oldest-first. The old code spliced new
    items directly after the `key:` line, i.e. AHEAD of existing ones, while every
    event carried the same hardcoded timestamp — so ordering was the only signal of
    sequence and it was backwards."""
    once = append_to_section(BARE, "curation_history", HIST_BLOCK)
    second = yaml.safe_dump(
        {"curation_history": [{"timestamp": "t2", "curator": "c", "action": "second"}]},
        sort_keys=False, allow_unicode=True, width=100)
    twice = append_to_section(once, "curation_history", second)
    assert [h["action"] for h in yaml.safe_load(twice)["curation_history"]] == \
        ["first", "second"]


def test_appends_graph_without_disturbing_siblings():
    out = append_to_section(BARE, "causal_graphs", GRAPH_BLOCK)
    second = yaml.safe_dump(
        {"causal_graphs": [{"graph_id": "g2", "nodes": [{"node_id": "m"}], "edges": []}]},
        sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(out, "causal_graphs", second)
    rec = yaml.safe_load(out)
    assert [g["graph_id"] for g in rec["causal_graphs"]] == ["g1", "g2"]
    assert rec["evidence"] == [{"reference": "PMID:1"}]


def test_record_without_license_gets_block_appended():
    out = append_to_section(NO_LICENSE, "causal_graphs", GRAPH_BLOCK)
    assert yaml.safe_load(out)["causal_graphs"][0]["graph_id"] == "g1"


def test_backslash_in_payload_survives_verbatim():
    """LATENT, NEVER FIRED. The builders used `re.sub` with a *string* replacement,
    which interprets `\\g` and `\\1`. No Rhea or ENZYME release contains a backslash
    today — which is exactly why this would have surfaced as corruption long after
    whatever change introduced one."""
    payload = yaml.safe_dump(
        {"causal_graphs": [{"graph_id": "g", "nodes": [],
                            "edges": [{"description": r"C:\path and \g<1> and \1"}]}]},
        sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(BARE, "causal_graphs", payload)
    assert yaml.safe_load(out)["causal_graphs"][0]["edges"][0]["description"] == \
        r"C:\path and \g<1> and \1"


def test_empty_payload_is_a_noop():
    assert append_to_section(BARE, "causal_graphs", "causal_graphs:\n") == BARE


# --- has_graph ---------------------------------------------------------------

def test_has_graph_is_not_a_prefix_match():
    """THE SHIPPED DEFECT. `"..._mcsa45" in text` is true when the record actually
    holds `..._mcsa454`, so a genuinely new M-CSA entry was reported "already wired"
    and never written. Latent only because no such id pair exists in this release —
    RHEA:15017 carries 43, 44, 454 and 558, so one new entry numbered 45 triggers it."""
    text = "causal_graphs:\n- graph_id: catalytic_residues_mcsa454\n  nodes: []\n"
    assert has_graph(text, "catalytic_residues_mcsa454")
    assert not has_graph(text, "catalytic_residues_mcsa45")


def test_has_graph_is_specific_not_merely_any_graph():
    """THE SHIPPED DEFECT. Builders skipped on the bare substring `causal_graphs:`,
    so a record that gained ANY graph first was permanently locked out of its own."""
    text = "causal_graphs:\n- graph_id: catalytic_residues_mcsa1\n"
    assert not has_graph(text, "reaction_chemistry")
    assert has_graph(text, "catalytic_residues_mcsa1")


@pytest.mark.parametrize("line", [
    "- graph_id: reaction_chemistry",        # 39,645 records look exactly like this
    "  - graph_id: reaction_chemistry",      # 2 records do
    "- graph_id:   reaction_chemistry   ",
])
def test_has_graph_tolerates_the_indentation_records_actually_use(line):
    """REGRESSION. `graph_id` is the first key of a list item, so PyYAML emits it as
    `- graph_id: …`. A first attempt anchored on `^\\s*graph_id:`, which matches none
    of the real records — turning "skip what is done" into "append a duplicate every
    run".

    Measured across the corpus with a real multiline scan (line-based `grep` cannot
    do this and silently gave wrong counts): 39,645 `causal_graphs` sections put
    their items at column 0 and 2 at a two-space indent. None are deeper, and none
    omit the `- `. The item indent is therefore derived from the section itself."""
    assert has_graph(f"causal_graphs:\n{line}\n", "reaction_chemistry")


# --- insert_before_license ---------------------------------------------------

def test_insert_before_license_places_and_preserves_backslashes():
    out = insert_before_license(BARE, "extra:\n- value: 'a\\b'\n")
    rec = yaml.safe_load(out)
    assert rec["extra"] == [{"value": "a\\b"}]
    assert list(rec)[-1] == "license"


def test_insert_before_license_appends_when_absent():
    out = insert_before_license(NO_LICENSE, "extra:\n- value: 1\n")
    assert yaml.safe_load(out)["extra"] == [{"value": 1}]


# --- shapes no record uses today, but which would corrupt if they appeared -----

@pytest.mark.parametrize("inline", [
    "causal_graphs: []",
    "causal_graphs: [{graph_id: g1}]",
])
def test_inline_flow_value_is_refused_not_corrupted(inline):
    """LATENT. Appending block-style items under a key that carries an INLINE value
    produces unparseable YAML. No record is written this way, so this cannot fire
    today, and the helper returns the text unchanged.

    An earlier version of this docstring claimed "every caller already treats
    unchanged as could not splice, skip". That was false: review found the builders
    flipped mapping_status to REVIEWED and appended a history entry claiming a graph
    had been added, without noticing the refusal. The callers now check the graph
    splice on its own and skip. This test still only covers the helper's no-op — the
    caller behaviour is not exercised here, and saying so is the point."""
    text = f"identifier: X:1\n{inline}\nlicense: CC0\n"
    assert append_to_section(text, "causal_graphs", GRAPH_BLOCK) == text


@pytest.mark.parametrize("text,label", [
    ("identifier: X:1\nlicense: CC0", "no trailing newline"),
    ("identifier: X:1\ncausal_graphs:\n- graph_id: g1\n", "section is the last key"),
    ("identifier: X:1\r\ncausal_graphs:\r\n- graph_id: g1\r\nlicense: CC0\r\n", "CRLF"),
    ("identifier: X:1\ndefinition: >-\n  mentions causal_graphs: not a key\nlicense: CC0\n",
     "key name inside a folded scalar"),
    ("identifier: X:1\ncausal_graphs:\nlicense: CC0\n", "key present with null value"),
])
def test_awkward_but_valid_shapes_still_parse(text, label):
    """Shapes that are unusual but legal. The folded-scalar case matters: the key
    name appears in prose, indented, and must NOT be mistaken for the section.

    The payload uses a graph_id present in none of the inputs, so this cannot pass
    merely because the input already had one — the "section is the last key" case
    ships a `g1` and would satisfy a naive membership check for free.
    """
    payload = yaml.safe_dump({"causal_graphs": [{"graph_id": "appended"}]},
                             sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(text, "causal_graphs", payload)
    ids = [g["graph_id"] for g in yaml.safe_load(out)["causal_graphs"]]
    assert ids[-1] == "appended", f"{label}: appended item missing or misplaced"


# --- codex review findings ----------------------------------------------------

def test_has_graph_ignores_the_name_appearing_in_prose():
    """FALSE POSITIVE found by review. Searching the whole document matched the key
    name inside a folded scalar, so a record merely *describing* a graph counted as
    having one."""
    text = ('identifier: X:1\n'
            'definition: |-\n'
            '  graph_id: reaction_chemistry\n'
            'license: CC0\n')
    assert not has_graph(text, "reaction_chemistry")


@pytest.mark.parametrize("value", ['reaction_chemistry', '"reaction_chemistry"',
                                   "'reaction_chemistry'",
                                   'reaction_chemistry  # written by round 16'])
def test_has_graph_handles_quoting_and_comments(value):
    """FALSE NEGATIVES found by review. A quoted value or a trailing comment made the
    match fail, so a record that HAS the graph would be rewritten and duplicated."""
    text = f"identifier: X:1\ncausal_graphs:\n- graph_id: {value}\n  nodes: []\n"
    assert has_graph(text, "reaction_chemistry")


def test_append_at_eof_without_trailing_newline_does_not_concatenate():
    """Found by review. The earlier 'no trailing newline' fixture contained
    `license:`, so insertion happened before that line and the append-at-EOF path
    was never exercised. Without a guard the payload fuses onto the last value:
    `label: x` + `causal_graphs:` -> `label: xcausal_graphs:`."""
    text = "identifier: X:1\nlabel: x"          # no license, no trailing newline
    out = append_to_section(text, "causal_graphs", GRAPH_BLOCK)
    rec = yaml.safe_load(out)
    assert rec["label"] == "x"
    assert [g["graph_id"] for g in rec["causal_graphs"]] == ["g1"]


def test_second_builder_appends_rather_than_duplicating_the_key():
    """THE DATA-LOSS DEFECT found by review, which this branch introduced. Making the
    skip predicate specific let a record carrying another builder's graph proceed;
    inserting a fresh `causal_graphs:` then gave the record two top-level keys, and
    PyYAML keeps only the last — silently discarding the existing graph."""
    first = append_to_section("identifier: X:1\nlicense: CC0\n",
                              "causal_graphs", GRAPH_BLOCK)
    first = append_to_section(first, "curation_history", HIST_BLOCK)
    second = yaml.safe_dump(
        {"causal_graphs": [{"graph_id": "reaction_chemistry"}]},
        sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(first, "causal_graphs", second)
    assert out.count("\ncausal_graphs:") + out.startswith("causal_graphs:") == 1
    assert [g["graph_id"] for g in yaml.safe_load(out)["causal_graphs"]] == \
        ["g1", "reaction_chemistry"]


# --- second codex review ------------------------------------------------------

def test_append_into_existing_final_section_without_trailing_newline():
    """`license:` is optional, so a section can be the last thing in the file. If its
    final line has no newline, appending fused the two:
    `edges: []` + `- graph_id: g2` -> `edges: []- graph_id: g2`. The key-ABSENT
    branch was guarded; the key-PRESENT branch was not, and the earlier EOF test
    only covered the absent case."""
    text = ("identifier: X:1\n"
            "causal_graphs:\n"
            "- graph_id: g1\n"
            "  nodes: []\n"
            "  edges: []")            # no trailing newline, no license
    payload = yaml.safe_dump({"causal_graphs": [{"graph_id": "g2"}]},
                             sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(text, "causal_graphs", payload)
    assert [g["graph_id"] for g in yaml.safe_load(out)["causal_graphs"]] == ["g1", "g2"]


def test_has_graph_ignores_a_nested_scalar_inside_the_section():
    """A `description: |-` block INSIDE causal_graphs whose text reads
    `graph_id: reaction_chemistry` used to count as having that graph, because the
    match allowed arbitrary indentation. A builder would then permanently skip a
    graph the record does not have. The earlier prose test only covered prose
    OUTSIDE the section."""
    text = ("causal_graphs:\n"
            "- graph_id: other\n"
            "  description: |-\n"
            "    graph_id: reaction_chemistry\n"
            "  nodes: []\n")
    assert has_graph(text, "other")
    assert not has_graph(text, "reaction_chemistry")


def test_append_matches_the_existing_section_indentation():
    """LIVE CORRUPTION found by review. PyYAML emits list items at column 0, but two
    corpus records indent theirs by two spaces — `beta-lactamase-class-a-mcsa2` and
    `-class-b1-mcsa15`, which are also the only records carrying hand-written
    residue→substrate edges. Appending column-0 items into a two-space list produced
    unparseable YAML on exactly those two. Earlier tests named those records for
    has_graph but never tried appending to them."""
    text = ("identifier: X:1\n"
            "causal_graphs:\n"
            "  - graph_id: old\n"
            "    nodes: []\n"
            "license: CC0\n")
    payload = yaml.safe_dump({"causal_graphs": [{"graph_id": "new"}]},
                             sort_keys=False, allow_unicode=True, width=100)
    out = append_to_section(text, "causal_graphs", payload)
    rec = yaml.safe_load(out)                       # raised before the fix
    assert [g["graph_id"] for g in rec["causal_graphs"]] == ["old", "new"]
    assert rec["license"] == "CC0"


def test_append_matches_indentation_for_any_section_not_just_graphs():
    """The indentation bug was found on `causal_graphs`, where only 2 records are
    affected — but 6,182 records indent their `curation_history` items, so that is
    the far larger risk class. Verified exhaustively against all 6,182; this pins
    the behaviour so a future change to the indent detection cannot silently
    reintroduce it for one key while fixing the other."""
    text = ("identifier: X:1\n"
            "curation_history:\n"
            "  - timestamp: t1\n"
            "    action: first\n"
            "license: CC0\n")
    payload = yaml.safe_dump({"curation_history": [{"timestamp": "t2", "action": "second"}]},
                             sort_keys=False, allow_unicode=True, width=100)
    rec = yaml.safe_load(append_to_section(text, "curation_history", payload))
    assert [h["action"] for h in rec["curation_history"]] == ["first", "second"]
    assert rec["license"] == "CC0"


@pytest.mark.parametrize("indent", ["", "  "])
def test_migration_end_to_end_on_a_real_file(indent, tmp_path, monkeypatch):
    """Runs the ACTUAL migration over a real file and parses the result.

    The previous version of this test called `offenders()` and `evidence_block()`
    separately and asserted on each — it never spliced, never parsed, and never
    checked the offending xref was gone. It would have passed if the migration had
    stopped inserting evidence entirely, or inserted it in the wrong place. That is
    the third test in this file to have been written that way, so this one drives
    main() and asserts on the file that lands on disk."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fx", Path(__file__).resolve().parent.parent / "scripts" / "fix_noncurie_xrefs.py")
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)

    traits = tmp_path / "traits"
    (traits / "go").mkdir(parents=True)
    rec = traits / "go" / "probe.yaml"
    rec.write_text(
        f"identifier: GO:1\nlabel: \"probe\"\ntrait_axis: FUNCTION\n"
        f"xrefs:\n{indent}- DOI:10.1000/ex\n{indent}- GOC:a\nlicense: CC-BY 4.0\n",
        encoding="utf-8")
    monkeypatch.setattr(fx, "TRAITS", traits)
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["fix_noncurie_xrefs.py", "--apply"])
    fx.main()

    out = yaml.safe_load(rec.read_text(encoding="utf-8"))
    assert out["xrefs"] == ["GOC:a"], "the offending xref was not removed"
    assert out["evidence"][0]["reference"] == "DOI:10.1000/ex", "not relocated"
    assert out["label"] == "probe" and out["license"] == "CC-BY 4.0"
    # and the emitted indent matches the record's own style
    body = rec.read_text(encoding="utf-8")
    assert f"\nevidence:\n{indent}- reference:" in body


def test_has_graph_ignores_a_dashless_mapping():
    """`causal_graphs:` followed by a bare `graph_id:` with no `- ` parses as a
    MAPPING, not a list of graphs, so it is not a graph list at all — confirmed with
    yaml.safe_load, and zero corpus records are written that way. An earlier version
    of the test above asserted this form should match, which was wrong on both
    counts."""
    import yaml as _y
    text = "causal_graphs:\n  graph_id: reaction_chemistry\n"
    assert isinstance(_y.safe_load(text)["causal_graphs"], dict)   # not a list
    assert not has_graph(text, "reaction_chemistry")


# --- gaps codex named: mutations the suite would have tolerated -----------------

def test_obo_escape_is_actually_decoded():
    """MUTATION GAP. Making `_unescape_obo` return its input unchanged passed all 34
    tests: the migration fixture used a plain `DOI:10.1000/ex` and nothing exercised
    the escape. `EvidenceItem.reference` is unconstrained text, so validation would
    not have caught it either — GO:0016087 shipped a malformed DOI for exactly that
    reason."""
    import seed_obo
    assert seed_obo._unescape_obo(r"10.1002/(SICI)1520-6327(1997)35\:1") == \
        "10.1002/(SICI)1520-6327(1997)35:1"
    assert seed_obo.normalise_source(r"DOI:10.1/a\:b") == "DOI:10.1/a:b"
    # an escape OBO does not define must survive rather than lose its backslash
    assert seed_obo._unescape_obo(r"a\qb") == r"a\qb"


def test_has_graph_handles_indentation_deeper_than_the_corpus_uses():
    """MUTATION GAP. Replacing the derived indent with a hardcoded 0-2 spaces passed
    every test, because the suite only exercised column 0 and two spaces — the two
    styles the corpus happens to use. Production deliberately supports deeper, since
    a false negative there makes a builder append a graph the record already has."""
    text = ("causal_graphs:\n"
            "    - graph_id: reaction_chemistry\n"
            "      nodes: []\n")
    assert has_graph(text, "reaction_chemistry")


@pytest.mark.parametrize("shape,expect_refused", [
    ("evidence: []", True),                                  # inline: refuse
    ("evidence:\n- reference: PMID:1\n  notes: e", False),   # EOF, no newline: merge
])
def test_migration_merge_into_existing_evidence(shape, expect_refused):
    """MUTATION GAP. The migration test had no pre-existing `evidence`, so the entire
    merge branch could break without failing `just test` — and it did: hand-rolled
    splicing corrupted both of these shapes."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fx", Path(__file__).resolve().parent.parent / "scripts" / "fix_noncurie_xrefs.py")
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    text = f"identifier: GO:1\nxrefs:\n  - DOI:10.1000/ex\n{shape}"
    lines = text.splitlines(keepends=True)
    bad = fx.offenders(lines)
    kept = [ln for i, ln in enumerate(lines) if i not in set(bad)]
    xi = next((i for i, ln in enumerate(kept) if ln.startswith("xrefs:")), None)
    if xi is not None and not fx._ITEM.match(kept[xi + 1] if xi + 1 < len(kept) else ""):
        kept.pop(xi)
    has_ev = any(ln.startswith("evidence:") for ln in kept)
    payload = "".join(fx.evidence_block([("DOI:10.1000/ex", "def")], "GO",
                                        "" if has_ev else "  "))
    merged = fx.append_to_section("".join(kept), "evidence", payload)
    if expect_refused:
        assert merged == "".join(kept), "an inline value must be refused, not spliced"
    else:
        refs = [e["reference"] for e in yaml.safe_load(merged)["evidence"]]
        assert refs == ["PMID:1", "DOI:10.1000/ex"]


# --- mutations round 9 named as "highly plausible future edits" -----------------

def test_has_graph_finds_a_target_in_the_SECOND_graph():
    """MUTATION: `if value == want: return True` -> `return value == want`. Every
    prior test had one graph in the section, so the early return was never exercised
    and the mutation stayed green — while a builder would stop finding any graph but
    the first and start appending duplicates."""
    text = ("causal_graphs:\n"
            "- graph_id: reaction_chemistry\n  nodes: []\n"
            "- graph_id: catalytic_residues_mcsa1\n  nodes: []\n")
    assert has_graph(text, "reaction_chemistry")
    assert has_graph(text, "catalytic_residues_mcsa1")   # the mutation loses this


def test_append_writes_every_item_not_just_the_first():
    """MUTATION: truncate `items` at the second column-0 `- `. All prior payloads
    held exactly one item, so the mutation stayed green — while a migration
    relocating two citations would silently drop the second."""
    payload = yaml.safe_dump(
        {"causal_graphs": [{"graph_id": "a"}, {"graph_id": "b"}]},
        sort_keys=False, allow_unicode=True, width=100)
    # Key ABSENT: this path inserts `payload` whole.
    out = append_to_section("identifier: X:1\nlicense: CC0\n", "causal_graphs", payload)
    assert [g["graph_id"] for g in yaml.safe_load(out)["causal_graphs"]] == ["a", "b"]
    # Key PRESENT: this path splices `items`, and is the one the mutation hits —
    # the absent-key case above cannot catch it, which is why both are asserted.
    existing = "identifier: X:1\ncausal_graphs:\n- graph_id: z\n  nodes: []\nlicense: CC0\n"
    out2 = append_to_section(existing, "causal_graphs", payload)
    assert [g["graph_id"] for g in yaml.safe_load(out2)["causal_graphs"]] == ["z", "a", "b"]


def test_each_builder_checks_its_own_graph_id():
    """MUTATION: copy/paste a sibling's graph_id into a builder's has_graph call —
    e.g. BioLiP checking for `reaction_chemistry`. No builder is imported by any
    test, so every such regression stays green and the builder silently duplicates
    graphs on its next run."""
    import re as _re
    # DERIVED, not hardcoded. The first version of this test listed five builders
    # and silently omitted build_rhea_mcsa_residue_graphs.py despite its name, so a
    # copy/paste regression there stayed green. Discovering the set from disk means
    # a newly added builder is covered without anyone remembering to add it.
    scripts = Path(__file__).resolve().parent.parent / "scripts"
    builders = sorted(p.name for p in scripts.glob("build_*.py")
                      if "has_graph(" in p.read_text(encoding="utf-8"))
    assert len(builders) >= 6, f"expected every converted builder, found {builders}"
    expected = {"build_biolip_causal_graphs.py": "ligand_binding",
                "build_metalpdb_causal_graphs.py": "metal_coordination",
                "build_mcsa_causal_graphs.py": "catalysis",
                "build_rhea_causal_graphs.py": "reaction_chemistry",
                "build_ec_causal_graphs.py": "reaction_chemistry",
                "build_rhea_mcsa_residue_graphs.py": "catalytic_residues"}
    assert set(builders) == set(expected), (
        f"a builder calls has_graph but is not asserted here: "
        f"{set(builders) ^ set(expected)}")
    for name, want in expected.items():
        src = (scripts / name).read_text(encoding="utf-8")
        # Extract the literal text of the has_graph argument. No `want in src`
        # fallback: that made the assertion tautological, because the graph id also
        # appears elsewhere in the file (e.g. as GRAPH_ID), so it passed no matter
        # what has_graph was actually called with.
        arg = _re.search(r"has_graph\(\s*text\s*,\s*([^)]+)\)", src)
        assert arg, f"{name} does not call has_graph(text, ...)"
        arg = arg.group(1).strip()
        # either a literal "want", or an f-string built from a constant equal to want
        literal = _re.fullmatch(r'["\']([^"\']+)["\']', arg)
        if literal:
            got = literal.group(1)
        else:
            const = _re.search(r"\{(\w+)\}", arg)
            assert const, f"{name}: cannot resolve has_graph argument {arg!r}"
            val = _re.search(rf'^{const.group(1)}\s*=\s*["\']([^"\']+)["\']', src, _re.M)
            assert val, f"{name}: {const.group(1)} not a module constant"
            got = val.group(1)
        assert got == want, f"{name} checks has_graph(..., {got!r}), expected {want!r}"
        # and it must equal the graph_id it actually writes
        written = _re.findall(r'"graph_id":\s*["\']([^"\']+)["\']', src)
        assert not written or want in written, f"{name}: writes {written}, checks {want!r}"


# --- round 10 (post-merge review) ----------------------------------------------

def test_has_graph_when_graph_id_is_not_the_first_key():
    """MUTATION: reorder a builder's graph dict so `title` precedes `graph_id`.
    PyYAML preserves dict order, so the record gets `- title:` then `  graph_id:`.
    Requiring the sequence dash on the same line made has_graph miss it entirely,
    and the builder would append a duplicate on its next run. Every test fixture
    happened to put graph_id first, so the mutation stayed green."""
    text = ("causal_graphs:\n"
            "- title: Reaction chemistry\n"
            "  graph_id: reaction_chemistry\n"
            "  nodes: []\n")
    assert has_graph(text, "reaction_chemistry")
    assert not has_graph(text, "catalytic_residues")


@pytest.mark.parametrize("fn_name", ["append_to_section", "insert_before_license"])
def test_payload_without_trailing_newline_does_not_fuse(fn_name):
    """The helpers guarded the boundary BEFORE a payload but not after it, so a
    payload with no trailing newline fused into the next key:
    `- reference: PMID:1license: CC0`. Dropping a `+ "\\n"` in any caller — a
    plausible formatting refactor — would have activated this for every record
    that has a license."""
    import record_io
    fn = getattr(record_io, fn_name)
    args = (("identifier: X:1\nlicense: CC0\n", "evidence", "evidence:\n- reference: PMID:1")
            if fn_name == "append_to_section"
            else ("identifier: X:1\nlicense: CC0\n", "evidence:\n- reference: PMID:1"))
    rec = yaml.safe_load(fn(*args))
    assert rec["license"] == "CC0"
    assert rec["evidence"] == [{"reference": "PMID:1"}]


def test_obo_xref_description_is_stripped_not_misread():
    """LIVE-ON-NEXT-RESEED. OBO allows `xref: ID "description"`. The description was
    never stripped, so such an xref was DROPPED (the CURIE test failed on the space
    and quotes) — and once the slash rule was widened, any description containing a
    `/` turned the whole string into a bogus evidence reference. 302 GO terms carry
    that shape, mostly Reactome."""
    import seed_obo
    assert seed_obo.parse_xref('Reactome:R-HSA-69206 "G1/S Transition"') == "Reactome:R-HSA-69206"
    assert seed_obo.parse_xref('Reactome:R-HSA-1234 "Plain"') == "Reactome:R-HSA-1234"
    # a genuine slash-bearing identifier is still routed to evidence
    assert seed_obo.parse_xref("EC:1.2/3")[0] == "evidence"


@pytest.mark.parametrize("raw,want", [
    ('Reactome:R-HSA-1 "desc: with colon"', "Reactome:R-HSA-1"),
    (r'Reactome:R-HSA-2 "say \"hi\" now"', "Reactome:R-HSA-2"),
    ('GO:0001 "a" {is_inferred="true"}', "GO:0001"),
    ('Reactome:R-HSA-3  "extra spaces"  ', "Reactome:R-HSA-3"),
    ("EC:1.1.1.1", "EC:1.1.1.1"),
])
def test_obo_xref_spec_legal_suffixes(raw, want):
    """OBO 1.4 allows `<ID> "<description>" {<modifiers>}`; both suffixes are
    optional. Neither the escaped-quote nor the trailing-modifier form occurs in the
    current releases — they are handled because the spec allows them. A naive
    `"[^"]*"` leaves a fragment behind on an escaped quote, the CURIE test then
    fails, and the xref is silently dropped: the exact failure that stripping was
    added to fix, one shape further out."""
    import seed_obo
    assert seed_obo.parse_xref(raw) == want
