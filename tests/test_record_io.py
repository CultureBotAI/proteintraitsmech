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
    "- graph_id: reaction_chemistry",        # 40,113 records look exactly like this
    "  - graph_id: reaction_chemistry",      # 2 records do
    "  graph_id: reaction_chemistry",
    "  graph_id:   reaction_chemistry   ",
])
def test_has_graph_tolerates_the_indentation_records_actually_use(line):
    """REGRESSION. `graph_id` is the first key of a list item, so PyYAML emits it as
    `- graph_id: …`. A first attempt anchored on `^\\s*graph_id:`, which matches none
    of the real records — turning "skip what is done" into "append a duplicate every
    run".

    Measured across the corpus: 40,113 graph_id lines sit at column 0 with `- `, and
    2 at a two-space indent. Nothing deeper, which is why anything deeper is treated
    as nested content rather than a graph key — see the spoofing test below."""
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
