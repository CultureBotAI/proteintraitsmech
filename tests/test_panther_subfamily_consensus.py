"""The rule that lets a PANTHER family borrow its subfamilies' annotations (#150).

3,596 families are annotation-free in `PANTHER19.0_HMM_classifications`. Some of
them have annotated *subfamilies*, which the seeder otherwise ignores. Composing a
family definition from those rows asserts something the release does not state on
the family's own row, so the rule is deliberately strict, and these tests pin the
two restrictions that make it defensible:

  * at least `MIN_SUBFAMILIES` annotated subfamilies, so one outlier cannot speak
    for a whole family;
  * **intersection, not majority** — a term must be on EVERY annotated subfamily.

The second is the one worth guarding. Relaxing it to a majority is a one-word
change that would look harmless, roughly double the coverage, and quietly start
attributing a minority's annotations to the family.

The prose restriction is tested too: it must say "Subfamilies ...", never
"Members ...", because that difference is the whole claim.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from seed_panther import (  # noqa: E402
    MIN_SUBFAMILIES, compose_from_subfamilies, subfamily_consensus,
)


def row(pid, name="SUB", mf="", bp="", cc="", classes=""):
    return "\t".join([pid, name, mf, bp, cc, classes, ""])


GO_A = "catalytic activity#GO:0003824"
GO_B = "nuclease activity#GO:0004518"
CLS = "hydrolase#PC00121"


def test_a_single_annotated_subfamily_is_not_enough():
    out = subfamily_consensus([row("PTHR1:SF1", mf=GO_A)])
    assert out == {}, "one subfamily must not speak for the family"
    assert MIN_SUBFAMILIES == 2


def test_a_term_on_only_some_subfamilies_is_dropped():
    """Intersection, not majority. GO_A is on both; GO_B on one, so it goes."""
    out = subfamily_consensus([row("PTHR1:SF1", mf=f"{GO_A};{GO_B}"),
                               row("PTHR1:SF2", mf=GO_A)])
    agreed, n = out["PTHR1"]
    assert n == 2
    assert [go for _, go in agreed["mf"]] == ["GO:0003824"]


def test_no_consensus_at_all_yields_no_entry():
    out = subfamily_consensus([row("PTHR1:SF1", mf=GO_A), row("PTHR1:SF2", mf=GO_B)])
    assert "PTHR1" not in out


def test_unannotated_subfamilies_do_not_count_toward_the_minimum():
    """An empty subfamily row is absence of evidence, not disagreement."""
    out = subfamily_consensus([row("PTHR1:SF1", mf=GO_A), row("PTHR1:SF2"),
                               row("PTHR1:SF3")])
    assert "PTHR1" not in out, "one annotated subfamily plus two blanks is not two"


def test_family_rows_are_ignored():
    out = subfamily_consensus([row("PTHR1", mf=GO_A), row("PTHR1:SF1", mf=GO_A)])
    assert "PTHR1" not in out


def test_classes_intersect_too():
    out = subfamily_consensus([row("PTHR1:SF1", classes=CLS),
                               row("PTHR1:SF2", classes=CLS)])
    assert out["PTHR1"][0]["classes"] == ["hydrolase"]


def test_ordering_is_stable_across_runs():
    rows = [row("PTHR1:SF1", mf=f"{GO_B};{GO_A}"), row("PTHR1:SF2", mf=f"{GO_A};{GO_B}")]
    first = subfamily_consensus(rows)["PTHR1"][0]["mf"]
    assert first == subfamily_consensus(list(reversed(rows)))["PTHR1"][0]["mf"]


def test_prose_attributes_the_claim_to_subfamilies_not_members():
    agreed = {"mf": [("catalytic activity", "GO:0003824")], "bp": [], "cc": [],
              "classes": ["hydrolase"], "pathways": []}
    out = compose_from_subfamilies("PTHR1", "SOME FAMILY", agreed, 4)
    assert "Subfamilies are annotated with" in out
    assert "Members are annotated with" not in out, \
        "attributing subfamily annotations to members is the claim this must not make"
    assert "shared by all 4 of its annotated subfamilies" in out, \
        "the basis size must be visible to a reader, not just to the script"


@pytest.mark.parametrize("agreed", [
    {"mf": [("f", "GO:1")], "bp": [], "cc": [], "classes": [], "pathways": []},
    {"mf": [], "bp": [("p", "GO:2")], "cc": [], "classes": [], "pathways": []},
    {"mf": [], "bp": [], "cc": [("c", "GO:3")], "classes": [], "pathways": []},
    {"mf": [], "bp": [], "cc": [], "classes": ["k"], "pathways": []},
])
def test_no_sentence_starts_lowercase(agreed):
    """The same property #147 fixed on the family composer, for this one."""
    import re
    out = compose_from_subfamilies("PTHR1", "SOME FAMILY", agreed, 3)
    bad = re.search(r"\.\s+([a-z])", out)
    assert not bad, f"sentence starts lowercase ({bad.group(1)!r}) in: {out}"
