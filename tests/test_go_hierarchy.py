"""GO `is_a` ancestry and the term ranking it feeds (#152).

Composed definitions show three GO terms per aspect. Before this, which three was
decided by list order — PANTHER's own, or CURIE sort order for the subfamily
consensus, where a set has no order and something deterministic was needed. Sorting
for determinism quietly became a decision about content: the three shown were the
three lowest GO ids, which tracks when a term was minted rather than how much it says.

These tests use a hand-written ontology rather than `data/raw/go-basic.obo`, so they
run in CI where that file is absent, and so a GO release cannot silently change what
they assert.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from go_hierarchy import GoRanker, ancestors_of, depth_of, parse_is_a  # noqa: E402

# root <- mid <- leaf, plus a sibling of mid, one obsolete term, and a Typedef stanza
# that must not be mistaken for a term.
MINI = """format-version: 1.2

[Term]
id: GO:0000001
name: root

[Term]
id: GO:0000002
name: mid
is_a: GO:0000001 ! root

[Term]
id: GO:0000003
name: leaf
is_a: GO:0000002 ! mid

[Term]
id: GO:0000004
name: sibling of mid
is_a: GO:0000001 ! root

[Term]
id: GO:0000009
name: obsolete thing
is_obsolete: true
replaced_by: GO:0000003

[Typedef]
id: part_of
name: part of
is_a: GO:0000001
"""


@pytest.fixture
def onto(tmp_path):
    p = tmp_path / "mini.obo"
    p.write_text(MINI, encoding="utf-8")
    return p


def test_obsolete_terms_are_skipped(onto):
    """An obsolete term must not become an ancestor of anything.

    Not hypothetical: PANTHER 19.0 annotates with 177 GO ids that current GO has
    obsoleted, across 226,659 annotation rows -- `GO:0044249` "cellular biosynthetic
    process" among them. They are kept in the list (dropping a term because the local
    ontology moved would lose data) but they carry no ancestry, so they rank last.
    """
    assert "GO:0000009" not in parse_is_a(onto)


def test_typedef_stanzas_are_not_parsed_as_terms(onto):
    """`[Typedef]` blocks carry `id:` and `is_a:` lines with the same syntax."""
    assert "part_of" not in parse_is_a(onto)


def test_ancestry_is_transitive(onto):
    anc = ancestors_of(parse_is_a(onto))
    assert anc["GO:0000003"] == frozenset({"GO:0000002", "GO:0000001"})
    assert anc["GO:0000001"] == frozenset()


def test_depth_increases_down_a_chain(onto):
    d = depth_of(ancestors_of(parse_is_a(onto)))
    assert d["GO:0000001"] < d["GO:0000002"] < d["GO:0000003"]


def test_a_cycle_does_not_hang_or_recurse(tmp_path):
    """A hand-edited or malformed release could contain one; the closure is built
    iteratively partly so this cannot blow the stack."""
    p = tmp_path / "cyc.obo"
    p.write_text("[Term]\nid: GO:1\nis_a: GO:2\n\n[Term]\nid: GO:2\nis_a: GO:1\n",
                 encoding="utf-8")
    anc = ancestors_of(parse_is_a(p))
    assert "GO:2" in anc["GO:1"] and "GO:1" in anc["GO:2"]


# --- ranking ----------------------------------------------------------------------

def test_an_ancestor_of_another_listed_term_is_dropped(onto):
    """THE POINT OF #152. "catalytic activity" says nothing beside "exonuclease
    activity", but it has the lower GO id and so used to win the slot."""
    r = GoRanker(onto)
    got = r.rank([("root", "GO:0000001"), ("leaf", "GO:0000003")])
    assert got == [("leaf", "GO:0000003")]


def test_siblings_are_both_kept(onto):
    """Pruning must remove redundancy, not breadth."""
    r = GoRanker(onto)
    got = {go for _, go in r.rank([("mid", "GO:0000002"), ("sib", "GO:0000004")])}
    assert got == {"GO:0000002", "GO:0000004"}


def test_most_specific_first(onto):
    r = GoRanker(onto)
    got = r.rank([("sib", "GO:0000004"), ("leaf", "GO:0000003")])
    assert [go for _, go in got] == ["GO:0000003", "GO:0000004"]


def test_order_is_stable_regardless_of_input_order(onto):
    """The property the old CURIE sort was protecting, and still required: the
    composed text must be byte-identical across runs."""
    r = GoRanker(onto)
    a = [("sib", "GO:0000004"), ("mid", "GO:0000002")]
    assert r.rank(a) == r.rank(list(reversed(a)))


def test_unknown_terms_are_kept_but_rank_last(onto):
    """An id absent from the local ontology -- obsolete, or newer than the file --
    must not vanish. Losing a term because the checkout is stale is worse than
    showing it."""
    r = GoRanker(onto)
    got = r.rank([("gone", "GO:0009999"), ("leaf", "GO:0000003")])
    assert [go for _, go in got] == ["GO:0000003", "GO:0009999"]


def test_duplicate_ids_collapse(onto):
    r = GoRanker(onto)
    assert len(r.rank([("leaf", "GO:0000003"), ("leaf again", "GO:0000003")])) == 1


def test_an_empty_list_is_empty(onto):
    assert GoRanker(onto).rank([]) == []


# --- obsolete terms (#157) -----------------------------------------------------------

OBS = """format-version: 1.2

[Term]
id: GO:0000001
name: live parent

[Term]
id: GO:0000002
name: live child
is_a: GO:0000001 ! live parent

[Term]
id: GO:0000010
name: obsolete with a replacement
is_obsolete: true
replaced_by: GO:0000002

[Term]
id: GO:0000011
name: obsolete with only a suggestion
is_obsolete: true
consider: GO:0000002

[Term]
id: GO:0000012
name: obsolete with no successor
is_obsolete: true
"""


@pytest.fixture
def obs(tmp_path):
    p = tmp_path / "obs.obo"
    p.write_text(OBS, encoding="utf-8")
    return p


def test_replaced_by_is_followed_and_the_term_is_relabelled(obs):
    """GO's `replaced_by` is its own assertion that the new term IS the old one,
    so both the id AND the name move. Keeping PANTHER's old wording beside the
    new id would assert the replacement means what the withdrawn term meant."""
    r = GoRanker(obs)
    assert r.resolve([("obsolete with a replacement", "GO:0000010")]) == \
        [("live child", "GO:0000002")]


def test_a_consider_suggestion_is_never_applied(obs):
    """`consider` is explicitly a suggestion for a curator, not an equivalence.
    18 of PANTHER's 177 obsolete terms have only this. Applying it automatically
    would be inventing a mapping GO declined to make."""
    r = GoRanker(obs)
    assert r.resolve([("obsolete with only a suggestion", "GO:0000011")]) == []


def test_an_obsolete_term_with_no_successor_is_dropped(obs):
    """A class the ontology has withdrawn is not a fact about the protein.
    Stating its pre-obsoletion label republishes it as current -- which is what
    #157 is about (63 of the 177, 87,205 annotation rows)."""
    r = GoRanker(obs)
    assert r.resolve([("obsolete with no successor", "GO:0000012")]) == []


def test_live_terms_pass_through_untouched(obs):
    r = GoRanker(obs)
    assert r.resolve([("live child", "GO:0000002")]) == [("live child", "GO:0000002")]


def test_a_substituted_term_is_then_ranked_like_any_other(obs):
    """Resolution happens BEFORE pruning, so a replacement that turns out to be
    an ancestor of a term already in the list is dropped as redundant -- which is
    what happens in the corpus: GO:0044249 resolves to "biosynthetic process",
    an ancestor of "glycerophospholipid biosynthetic process", and goes."""
    r = GoRanker(obs)
    got = r.rank([("live child", "GO:0000002"),
                  ("obsolete with a replacement", "GO:0000010")])
    assert got == [("live child", "GO:0000002")], "the duplicate survived"


def test_resolve_obsolete_false_reproduces_the_old_behaviour(obs):
    """Load-bearing for the repair scripts: their safety gate compares a record
    against what the composer USED to produce, which is impossible if the old
    behaviour is unreachable."""
    r = GoRanker(obs, resolve_obsolete=False)
    terms = [("obsolete with no successor", "GO:0000012")]
    assert r.resolve(terms) == terms


def test_the_obsolete_index_is_not_empty_on_the_real_release():
    """A parser that silently matched nothing would make every test above pass
    while changing no records."""
    pytest.importorskip("pathlib")
    from go_hierarchy import GO_OBO, parse_obsolete
    if not GO_OBO.exists():
        pytest.skip("go-basic.obo not fetched")
    obsolete, replaced, names = parse_obsolete()
    assert len(obsolete) > 1000, len(obsolete)
    assert replaced, "no replaced_by parsed at all"
    assert all(v.startswith("GO:") for v in replaced.values())
