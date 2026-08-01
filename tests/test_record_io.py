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
    "  graph_id: reaction_chemistry",
    "- graph_id: reaction_chemistry",
    "  - graph_id: reaction_chemistry",
    "    graph_id:   reaction_chemistry   ",
])
def test_has_graph_tolerates_indentation_and_list_dash(line):
    """REGRESSION. `graph_id` is the first key of a list item, so PyYAML emits it as
    `- graph_id: …`. A first attempt at this fix anchored on `^\\s*graph_id:`, which
    matches none of the real records — turning "skip what is done" into "append a
    duplicate every run". This case is the one that failed."""
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
    today — the helper returns the text unchanged, and every caller already treats
    "unchanged" as "could not splice, skip". Found by adversarially fuzzing record
    shapes rather than by any failure in the corpus."""
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
