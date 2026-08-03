"""Tests for scripts/record_io.py — issue #96, the repo's first test module.

Each test here corresponds to a defect that actually shipped, or to the code path
that a defect hid in. The comments name which, so a future reader can tell these
apart from speculative coverage.

Run with `just test` (or `uv run pytest tests/`).
"""

from __future__ import annotations

import re
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

        # And the id it WRITES must be the same expression it CHECKS. Comparing the
        # checked id against a constant is not enough: mutating the written id to
        # f"{GRAPH_ID}_mcsa{mid + 1}" left the check untouched and passed, because
        # the written value resolved to no plain literal and the assertion accepted
        # "no literals found".
        written = _re.search(r'"graph_id":\s*(f?["\'][^"\']*["\']|f["\'][^"\']*["\'])', src)
        wexpr = _re.search(r'"graph_id":\s*([^,\n]+)', src)
        assert wexpr, f"{name}: no graph_id written"
        wexpr = wexpr.group(1).strip().rstrip(",")
        cexpr = arg
        assert wexpr == cexpr, (
            f"{name} writes graph_id={wexpr} but checks has_graph(..., {cexpr}) — "
            f"these must be the same expression or the builder loses idempotence")
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
    `/` turned the whole string into a bogus evidence reference. 299 lines across 162 GO terms carry
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


def test_trailing_newline_guard_on_the_key_PRESENT_path():
    """The earlier newline test only covered `evidence` ABSENT, so removing the
    guard on the key-present branch left the suite green. Missed input below: the
    payload has no trailing newline and the section already exists, which fuses
    `PMID:1license: CC0`."""
    text = "identifier: X:1\nevidence:\n- reference: PMID:0\nlicense: CC0\n"
    out = append_to_section(text, "evidence", "evidence:\n- reference: PMID:1")
    rec = yaml.safe_load(out)
    assert [e["reference"] for e in rec["evidence"]] == ["PMID:0", "PMID:1"]
    assert rec["license"] == "CC0"


@pytest.mark.parametrize("module", ["seed_obo", "seed_psi_mod"])
def test_both_obo_parsers_strip_descriptions(module):
    """THE TWIN. `seed_psi_mod.py` has its own parse_xref and did NOT receive the
    description-stripping fix, so `RESID:AA0001 "standard description"` was silently
    dropped there while working in seed_obo.py. That is the sixth fix-one-forget-the-
    twin in this cycle; both now share scripts/obo_syntax.py. Parametrised over both
    modules so a future divergence fails here."""
    import importlib
    m = importlib.import_module(module)
    assert m.parse_xref('RESID:AA0001 "standard description"') == "RESID:AA0001"
    assert m.parse_xref("RESID:AA0001") == "RESID:AA0001"


@pytest.mark.parametrize("raw,want", [
    ('Reactome:R-HSA-1 "activation A/B! now"', "Reactome:R-HSA-1"),
    ('Reactome:R-HSA-1 "activation! A/B"', "Reactome:R-HSA-1"),
    ("EC:1.1.1.1 ! a genuine trailing comment", "EC:1.1.1.1"),
])
def test_bang_inside_a_description_is_not_a_comment(raw, want):
    """OBO's `! comment` marker is ordinary text inside a quoted description.
    Splitting on the first `!` truncated the description and left an unbalanced
    quote — which then still contained a `/` and was misclassified as a citation,
    recreating the exact corruption the description-stripping was added to remove.
    The `!` handling lived in TWO places (strip_comment and the _XREF_RE pattern);
    fixing only the first left the bug live."""
    import seed_obo
    assert seed_obo.parse_xref(raw) == want


@pytest.mark.parametrize("module", ["seed_obo", "seed_psi_mod"])
def test_bang_handling_is_shared_by_both_parsers(module):
    """The `!` tests previously covered seed_obo only, so reverting seed_psi_mod to a
    naive split stayed green — uncovered behaviour, not an inert mutation."""
    import importlib
    m = importlib.import_module(module)
    assert m.parse_xref('RESID:AA0001 "activation! A/B"') == "RESID:AA0001"
    assert m.parse_xref("RESID:AA0001 ! trailing comment") == "RESID:AA0001"


def test_escaped_bang_is_data_not_a_comment_marker():
    """OBO defines `\\!` as a character escape. strip_comment protected backslash
    pairs only INSIDE quotes, so an escaped bang outside them was cut, leaving a
    dangling backslash in the identifier."""
    import seed_obo
    got = seed_obo.parse_xref(r"DOI:10.1/foo\!bar")
    assert got == ("evidence", "DOI:10.1/foo!bar", "xref")


def test_modifier_block_with_an_escaped_brace():
    """`[^{}]` stopped at an escaped brace, so the modifier block did not match and
    the whole xref was dropped."""
    import seed_obo
    assert seed_obo.parse_xref(r'GO:0001 {note="a\}b"}') == "GO:0001"


def test_has_graph_dash_only_sequence_item():
    """A sequence item may be a bare `-` with its mapping on following lines. The
    indent was derived only from `- ` + content, so this returned False for a graph
    the record really had — and the builder would append a duplicate."""
    text = ("causal_graphs:\n"
            "-\n"
            "    title: x\n"
            "    graph_id: reaction_chemistry\n"
            "    nodes: []\n")
    assert has_graph(text, "reaction_chemistry")
    assert not has_graph(text, "catalytic_residues")


# --- data-driven invariants, worth more than the hand-written edge cases --------

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def _obo_releases():
    """Every OBO release the seeders are configured to read, that is present.

    Derived from `seed_obo.SOURCES` rather than a hardcoded list: the first version
    of this test looked for `data/raw/ARO.obo` while the configured path is
    `data/raw/aro/aro.obo`, so ARO was silently never exercised — the test reported
    a pass over the releases it happened to name correctly.
    """
    import seed_obo
    found = [(src.obo_file, seed_obo) for src in seed_obo.SOURCES.values()]
    import seed_psi_mod
    found.append(("PSI-MOD.obo", seed_psi_mod))
    return [(f, m) for f, m in found if (RAW / f).exists()]


_OBO = _obo_releases()
# The schema's own CURIE pattern. A token that cannot satisfy it MUST be dropped,
# so only tokens that could satisfy it are eligible to be called wrongly-dropped:
# `Wikipedia:Meiosis#Leptotene`, `MetaCyc:DNA-LIGASE-NAD+-RXN` and `url:http\://…`
# are all correct drops, and an invariant that flagged them would be noise.
_CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


def _leading_id(raw):
    """The ID token of an xref line, found without reusing the parser's own logic.

    An OBO ID cannot contain an unescaped space, so the first space-delimited token
    is the ID. Deliberately a second, independent implementation: an invariant that
    asks the parser to check itself proves nothing.
    """
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and i + 1 < len(raw):
            out.append(raw[i:i + 2])
            i += 2
            continue
        if c.isspace():
            break
        out.append(c)
        i += 1
    return "".join(out)


@pytest.mark.skipif(not _OBO, reason="data/raw is gitignored; run after a fetch")
@pytest.mark.parametrize("filename,module", _OBO)
def test_no_obo_line_syntax_leaks_into_a_parsed_value(filename, module):
    """INVARIANT over every real xref line, rather than another guessed edge case.

    obo_syntax was revised four times, each for a shape the previous revision
    missed — quoted `!`, escaped `!`, escaped braces, a brace inside a quoted
    qualifier value. Enumerating a fifth by imagination is a losing game; this
    asserts what must always hold instead: a parsed identifier must never contain
    syntax belonging only to the OBO line format.
    """
    import seed_obo as _so
    leak = re.compile(r'["{}]|(?<!\\)!|\\$')
    offenders = []
    for line in (RAW / filename).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("xref: "):
            got = module.parse_xref(line[6:].strip())
            val = got[1] if isinstance(got, tuple) else got
            if val and leak.search(val):
                offenders.append((line[:90], val))
        elif line.startswith("def: "):
            for tok in _so.parse_def(line[5:])[1]:
                c = _so.normalise_source(tok.strip())
                if c and leak.search(c):
                    offenders.append((tok.strip(), c))
    assert not offenders, f"{filename}: OBO syntax leaked into {len(offenders)} values, e.g. {offenders[:3]}"


@pytest.mark.skipif(not _OBO, reason="data/raw is gitignored; run after a fetch")
@pytest.mark.parametrize("filename,module", _OBO)
def test_no_wellformed_xref_is_silently_dropped(filename, module):
    """The other half of the invariant: nothing well-formed may vanish.

    The leak check above only inspects truthy results, so a parser that returns
    None for a line it cannot handle passes it — which is exactly how the quoted
    `{note="a}b"}` qualifier survived a review round that ran the leak check and
    reported a clean pass. A silent drop loses an xref on the next reseed, which is
    quieter and worse than a malformed one.

    If the leading token is CURIE-shaped, the parser must return something.
    """
    dropped = []
    for line in (RAW / filename).read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("xref: "):
            continue
        raw = line[6:].strip()
        # unescaped independently of the parser, so this is a real second opinion
        token = re.sub(r"\\\\(.)", r"\\1", _leading_id(raw))
        if not _CURIE.match(token):
            continue                     # cannot satisfy the schema; dropping is correct
        if module.parse_xref(raw) is None:
            dropped.append(raw[:100])
    assert not dropped, f"{filename}: {len(dropped)} well-formed xrefs dropped, e.g. {dropped[:5]}"


# --- the four defects the thirteenth review found ------------------------------

@pytest.mark.parametrize("raw", [
    'GO:0001 {note="a}b"}',      # `}` inside a QuotedString qualifier value
    'GO:0001 {note="a{b"}',      # `{` likewise
    'GO:0001 {a="1", b="a}b"}',  # and with a preceding well-behaved qualifier
])
@pytest.mark.parametrize("mod", ["seed_obo", "seed_psi_mod"])
def test_brace_inside_a_quoted_qualifier_value_does_not_drop_the_xref(raw, mod):
    """OBO qualifier values are QuotedStrings; `{`/`}` inside them need no escape.

    Treating every unescaped `}` as structural made `_MODIFIERS` fail to match, and
    a failed match silently DROPPED the whole xref on reseed rather than producing a
    malformed one — the quiet failure mode. Both parsers, because five of this
    cycle's defects were a fix applied to one twin and not the other.
    """
    import importlib
    assert importlib.import_module(mod).parse_xref(raw) == "GO:0001"


def test_a_literal_scalar_containing_a_dash_cannot_spoof_has_graph():
    """The worst shape found all cycle: wrong in BOTH directions at once.

    A `description: |-` block whose text contains `- prose` made the old indent
    inference latch onto the dash inside the scalar, after which the scalar's own
    `graph_id:` text was read as an item key. The record reported True for a graph
    it does not have (builder skips it forever) and False for the one it does
    (builder appends a duplicate).
    """
    text = ("causal_graphs:\n-\n  graph_id: other\n  description: |-\n"
            "    - prose\n      graph_id: reaction_chemistry\n  nodes: []\n  edges: []\n")
    assert has_graph(text, "other") is True
    assert has_graph(text, "reaction_chemistry") is False


def test_flow_style_sequence_item_is_found():
    """`- {graph_id: x}` is valid YAML and matched no branch of the old scanner.

    Unlike an inline value on the key line, append_to_section does not refuse this
    layout, so a False here meant appending a second copy of a graph already present.
    """
    text = "causal_graphs:\n- {graph_id: reaction_chemistry, nodes: [], edges: []}\nlicense: CC0\n"
    assert has_graph(text, "reaction_chemistry") is True


def test_graph_id_is_read_from_prose_nowhere_in_the_record():
    """A folded scalar outside the section must never register as a graph."""
    assert has_graph("definition: >-\n  compare graph_id: catalysis here\nlicense: CC0\n",
                     "catalysis") is False


@pytest.mark.parametrize("shape", [
    'causal_graphs:\n  - graph_id: "catalysis"\n',       # quoted
    "causal_graphs:\n  - graph_id: 'catalysis'\n",       # single-quoted
    "causal_graphs:\n  -\n    graph_id: catalysis\n",    # dash-only item
    "causal_graphs:\n  - title: t\n    graph_id: catalysis\n",   # not the first key
    "causal_graphs:\n- graph_id: catalysis  # trailing\n",       # trailing comment
])
def test_every_shape_the_scanner_needed_a_branch_for_still_works(shape):
    """Regression net for the six branches the parser replaced.

    Each of these cost a review round to find. They are cheap to keep and they are
    what proves the rewrite was a simplification rather than a trade.
    """
    assert has_graph(shape, "catalysis") is True
    assert has_graph(shape, "catalysi") is False      # no substring matching


def test_escaped_comma_survives_unescaping():
    """`\\,` is a spec-defined OBO escape; decoding it to anything else corrupts the id.

    Uncovered until the thirteenth review mutated `_ESCAPES[","]` and the suite
    stayed green. `UM-BBD_pathwayID:2\\,4-d` is a real line in go-basic.obo.
    """
    from obo_syntax import unescape
    assert unescape(r"2\,4-d") == "2,4-d"
    assert unescape(r"10.1002/(SICI)1520-6327(1997)35\:1") == "10.1002/(SICI)1520-6327(1997)35:1"


# --- payload indentation must not be added to the section's (found by a canary) -----

@pytest.mark.parametrize("section_indent", ["", "  ", "    "])
@pytest.mark.parametrize("payload_indent", ["", "  ", "    "])
def test_append_matches_the_section_regardless_of_how_the_payload_is_indented(
        section_indent, payload_indent):
    """The payload's own indentation must be normalised away, not added to.

    The re-indent was written when every caller passed `yaml.safe_dump` output, which
    is always at column 0, so "add the section's indent" and "set the section's indent"
    were indistinguishable. The first hand-written payload — indented the way the file
    itself looks, which is the natural way to write one — was double-indented to four
    spaces and the record stopped parsing.

    Caught by the canary on the very first `demote`, on a record that already carried a
    curation_history event. Every PANTHER record promoted in #111 had none, so the
    insert path was used and 15,489/15,489 validated; this was one record away.
    """
    record = (f"label: x\ncuration_history:\n{section_indent}- timestamp: \"t1\"\n"
              f"{section_indent}  curator: c\nlicense: CC0\n")
    payload = (f"curation_history:\n{payload_indent}- timestamp: \"t2\"\n"
               f"{payload_indent}  curator: c\n")
    out = append_to_section(record, "curation_history", payload)
    loaded = yaml.safe_load(out)
    assert [e["timestamp"] for e in loaded["curation_history"]] == ["t1", "t2"]
    assert loaded["license"] == "CC0"
    assert loaded["label"] == "x"


def test_append_preserves_deeper_continuation_lines_when_reindenting():
    """Normalising must shift the whole item, keeping keys nested under it nested."""
    record = 'label: x\ncuration_history:\n  - timestamp: "t1"\nlicense: CC0\n'
    payload = ('curation_history:\n    - timestamp: "t2"\n      curator: c\n'
               '      action: "did a thing"\n      llm_assisted: true\n')
    out = append_to_section(record, "curation_history", payload)
    second = yaml.safe_load(out)["curation_history"][1]
    assert second == {"timestamp": "t2", "curator": "c",
                      "action": "did a thing", "llm_assisted": True}
