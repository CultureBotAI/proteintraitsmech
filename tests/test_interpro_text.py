"""Cleaning InterPro abstracts without destroying their citations (#159).

Every seeder that read an InterPro abstract stripped inline `<db_xref/>`
elements along with the markup. The element is not decoration -- it is the
accession the sentence is about:

    This domain is usually find associated with <db_xref db="PFAM" dbkey="PF07730"/> .
    ->  This domain is usually find associated with .

16,699 inline db_xrefs across the release, of which 5,521 are EC numbers and
2,930 are UniProt accessions.

The tests that matter here are the ORDER of operations (substitute before
stripping, or the attributes are already gone) and the distinction between
`db_xref` and `cite` -- one is content, the other is an InterPro-internal
bibliography key that genuinely should go.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from interpro_text import (  # noqa: E402
    DB_PREFIX, clean_abstract, clean_abstract_element, render_xref,
)


# --- the bug ------------------------------------------------------------------------

def test_a_db_xref_is_substituted_not_deleted():
    """THE DEFECT. The accession is the content of the sentence."""
    raw = ('<p>This domain is usually find associated with '
           '<db_xref db="PFAM" dbkey="PF07730"/> .</p>')
    assert clean_abstract(raw) == (
        "This domain is usually find associated with Pfam:PF07730.")


@pytest.mark.parametrize("db,key,want", [
    ("PFAM", "PF07730", "Pfam:PF07730"),
    ("EC", "3.2.2.20", "EC:3.2.2.20"),
    ("SWISSPROT", "P00648", "UniProtKB:P00648"),
    ("INTERPRO", "IPR005398", "InterPro:IPR005398"),
    ("PDBE", "3NGK", "PDB:3NGK"),
    ("CAZY", "GH27", "CAZy:GH27"),
    ("NCBIFAM", "TIGR01564", "NCBIfam:TIGR01564"),
    ("PROSITEDOC", "PDOC00018", "PROSITE:PDOC00018"),
    ("SSF", "52171", "SUPERFAMILY:52171"),
])
def test_each_database_renders_with_its_corpus_prefix(db, key, want):
    assert render_xref(db, key) == want


def test_an_unknown_database_keeps_its_accession():
    """Losing the accession is the bug being fixed, so an unmapped db must not
    fall back to deletion. A slightly odd prefix is the lesser problem."""
    assert render_xref("NEWDB", "X123") == "NEWDB:X123"
    assert "NEWDB:X123" in clean_abstract('<p>see <db_xref db="NEWDB" dbkey="X123"/></p>')


def test_substitution_happens_before_the_generic_tag_strip():
    """Order is the whole bug. Strip tags first and the attributes are gone
    before anything can read them -- which is exactly what the old code did."""
    raw = '<p><i>x</i> <db_xref db="EC" dbkey="1.1.1.1"/> <b>y</b></p>'
    assert clean_abstract(raw) == "x EC:1.1.1.1 y"


# --- what should still be dropped ---------------------------------------------------

def test_a_cite_is_removed_with_its_brackets():
    """`cite idref` is an InterPro-internal publication key, meaningless outside
    their database. Unlike db_xref, deleting it is right."""
    raw = ('<p>Members form hexamers [<cite idref="PUB00019120"/>, '
           '<cite idref="PUB00019121"/>].</p>')
    assert clean_abstract(raw) == "Members form hexamers."


def test_brackets_left_empty_are_swept():
    for raw, want in [("<p>a ( ) b</p>", "a b"),
                      ("<p>a [ , ] b</p>", "a b"),
                      ("<p>a () b</p>", "a b")]:
        assert clean_abstract(raw) == want


def test_brackets_with_content_survive():
    """The sweep must not eat real parentheticals -- including one that now holds
    a substituted accession."""
    assert clean_abstract("<p>ATCase (a trimer) acts</p>") == "ATCase (a trimer) acts"
    assert clean_abstract('<p>x (<db_xref db="EC" dbkey="1.1.1.1"/>) y</p>') \
        == "x (EC:1.1.1.1) y"


def test_entities_are_unescaped_and_whitespace_collapsed():
    assert clean_abstract("<p>alpha &amp;  beta\n  gamma</p>") == "alpha & beta gamma"


def test_space_before_punctuation_is_closed_up():
    assert clean_abstract("<p>a word , and another .</p>") == "a word, and another."


# --- the element entry point --------------------------------------------------------

def test_the_element_path_substitutes_too():
    """seed_interpro parsed with ElementTree and used `itertext()`, which cannot
    see attributes -- so an empty <db_xref/> contributed nothing at all. That is
    why InterPro's own records showed no empty-paren tell while PANTHER's did:
    same deletion, different leftovers."""
    import xml.etree.ElementTree as ET
    el = ET.fromstring('<abstract><p>see <db_xref db="PFAM" dbkey="PF00001"/> '
                       'here</p></abstract>')
    assert clean_abstract_element(el) == "see Pfam:PF00001 here"


def test_a_missing_element_is_empty():
    assert clean_abstract_element(None) == ""


# --- the map ------------------------------------------------------------------------

def test_the_prefix_map_covers_every_database_seen_inline():
    """The twelve that actually occur inside abstracts in the current release."""
    for db in ("INTERPRO", "EC", "SWISSPROT", "PFAM", "PDBE", "CAZY", "NCBIFAM",
               "PROSITEDOC", "GENPROP", "PIRSF", "SSF", "PROSITE"):
        assert db in DB_PREFIX, db
