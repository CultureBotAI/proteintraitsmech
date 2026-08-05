"""The prose gate's checks, and the abbreviation rule that makes them usable (#149).

The gate exists because a defect sat in 1,707 records while passing closed-mode
`linkml-validate` and `audit-text`: `compose_definition` emitted sentences beginning
with a lowercase "and". Nothing in the repo had an opinion about whether a definition
reads as English.

A gate that cries wolf gets switched off, so the abbreviation handling is tested as
carefully as the defect detection. The first version of `sentence_starts_lowercase`
used a lookahead for the abbreviation -- testing the word AFTER the period, the wrong
side entirely -- and reported 80 hits on the PANTHER tree of which 78 were false
("i.e. having", "subsp. japonica", "et al. has", "Synechocystis sp. carboxysome").
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from audit_prose_quality import (  # noqa: E402
    CHECKS, definition_of, is_composed, sentence_starts_lowercase,
)


# --- the defect this gate was written for ------------------------------------------

@pytest.mark.parametrize("text", [
    "Modelled by the PANTHER 19.0 profile HMM PTHR36562. and localise to nucleus.",
    "A family of kinases. participate in metabolic process.",
    "Bound to the membrane. it is a mitochondrial protein.",
    "A tandem of Ig-like domains. represents the C-terminal region.",
])
def test_a_real_lowercase_sentence_start_is_caught(text):
    assert sentence_starts_lowercase(text)


# --- the false positives that would have made it unusable --------------------------

@pytest.mark.parametrize("text", [
    "Isoforms of these flavoproteins (i.e. having a non-covalent bond) differ.",
    "STLP5 from Oryza sativa subsp. japonica is localised to the Golgi.",
    "Related to the Synechocystis sp. carboxysome structural protein.",
    "Phosphorylation of keto- and aldohexoses (e.g. glucose and mannose).",
    "Analysis applied by Lambrecht et al. has divided the Rid family.",
    "Narcissus aff. pseudonarcissus MK-2014 encodes the reductase.",
    "Isolated from E. coli and characterised in vitro.",       # single-letter initial
    "See Fig. 2 and the accompanying discussion.",
    "Roughly 40 kDa, approx. 350 residues in length.",
])
def test_an_abbreviation_is_not_a_sentence_boundary(text):
    assert not sentence_starts_lowercase(text), text


def test_the_check_looks_behind_the_period_not_ahead():
    """Pins the actual bug. Both strings have a lowercase word after a period; only
    the second is a real boundary. A lookahead cannot tell them apart, because the
    thing that distinguishes them is entirely on the left."""
    assert not sentence_starts_lowercase("shown in Fig. above")
    assert sentence_starts_lowercase("shown in the figure. above all it binds")


# --- the other checks ---------------------------------------------------------------

def test_dangling_colon_period():
    """`clean_abstract` strips an inline <db_xref/> and can leave the colon behind:
    two PANTHER records end "...the following relevant reference:."."""
    assert CHECKS["dangling colon-period"].search("Please see the reference:.")
    assert not CHECKS["dangling colon-period"].search("Catalyses: A + B = C.")


def test_empty_clause():
    assert CHECKS["empty clause"].search("PANTHER protein class: . Members bind.")
    assert not CHECKS["empty clause"].search("PANTHER protein class: hydrolase.")


def test_double_space():
    assert CHECKS["double space"].search("a family  of kinases")
    assert not CHECKS["double space"].search("a family of kinases")


# --- classification, which decides pass vs report -----------------------------------

def test_a_composed_definition_is_ours():
    assert is_composed('definition_source: "PANTHER 19.0 (composed from the family '
                       'name and its GO / protein-class annotations)"')


def test_a_source_abstract_is_not_ours():
    """The whole reason the gate does not simply fail on every hit: rewriting a
    curator-written upstream abstract is a curation decision, not a gate's call."""
    assert not is_composed('definition_source: "InterPro:IPR013921 abstract '
                           '(PANTHER PTHR12465 is a member signature)"')


def test_a_record_with_no_definition_source_is_not_ours():
    assert not is_composed("identifier: X:1\nlabel: A\n")


# --- definition extraction -----------------------------------------------------------

def test_folded_definition_is_collapsed():
    assert definition_of("definition: >-\n  one two\n  three\nlabel: x\n") \
        == "one two three"


def test_inline_definition_is_read():
    assert definition_of('definition: "a short one"\n') == "a short one"


def test_missing_definition_returns_none():
    assert definition_of("identifier: X:1\n") is None


# --- source text quoted inside composed text ----------------------------------------

def test_a_boundary_inside_a_quoted_source_label_is_not_ours():
    """The one composed failure on the first full corpus run. NCBIfam names a domain
    "Chloroflexota. gingipain-like propeptide domain"; the composer embeds that name
    unchanged. Blaming the composer would mean rewriting a source's label, and leaving
    the gate red would mean the gate gets switched off."""
    label = "Chloroflexota. gingipain-like propeptide domain"
    defn = f"{label} — a protein domain modelled by the NCBIfam HMM NF057917."
    assert sentence_starts_lowercase(defn)               # without the exemption
    assert not sentence_starts_lowercase(defn, label)    # with it


def test_the_exemption_does_not_hide_our_own_defect():
    """A composed clause outside the label must still fail even when the label
    happens to contain a period of its own."""
    label = "Chloroflexota. gingipain-like propeptide domain"
    defn = f"{label} — modelled by HMM NF057917. and localise to nucleus."
    assert sentence_starts_lowercase(defn, label)
