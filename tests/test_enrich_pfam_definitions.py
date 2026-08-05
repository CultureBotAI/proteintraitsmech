"""Provenance on borrowed definitions (#173).

`enrich_pfam_definitions` replaces a Pfam record's definition with the abstract
of the InterPro entry Pfam maps to, and used to leave `definition_source: Pfam`.
The text's real origin was then unrecoverable from the record, and that cost real
time twice:

  * #171 could not identify which script wrote these definitions, because the
    source pointed at Pfam; `git log --follow` on one record was what found it.
  * `repair_interpro_abstracts` keys on the source naming an InterPro abstract,
    so it skipped every one of them -- which is why #170 shipped with 3,431
    records still carrying deleted cross-references.

After the fix that repair sees 15,531 Pfam records where it previously saw none.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from enrich_pfam_definitions import (  # noqa: E402
    borrowed_source, enrich_record, set_definition,
)

RECORD = """identifier: Pfam:PF04567
label: RNA polymerase Rpb2, domain 5
definition: >-
  the old boilerplate text
definition_source: Pfam
trait_axis: SEQUENCE
license: public domain (Pfam / InterPro)
"""


def test_the_source_names_the_entry_the_text_came_from():
    src = borrowed_source("IPR007647", "PF04567")
    assert "InterPro:IPR007647" in src
    assert "pfam2interpro" in src, "how the mapping was made must be stated"
    assert src.startswith('"') and src.endswith('"'), "must be a quoted scalar"


def test_definition_and_source_move_together():
    """A definition and a source that disagree is the whole defect, so the two
    are never written apart."""
    out = set_definition(RECORD, "the InterPro abstract",
                         borrowed_source("IPR007647", "PF04567"))
    assert "  the InterPro abstract\n" in out
    assert "definition_source: Pfam\n" not in out
    assert 'definition_source: "InterPro:IPR007647 abstract' in out


def test_the_rest_of_the_record_is_untouched():
    out = set_definition(RECORD, "new text", borrowed_source("IPR007647", "PF04567"))
    for line in ("identifier: Pfam:PF04567", "label: RNA polymerase Rpb2, domain 5",
                 "trait_axis: SEQUENCE", "license: public domain (Pfam / InterPro)"):
        assert line in out, line


def test_omitting_the_source_leaves_it_alone():
    """The old two-argument behaviour still works, so a caller that only wants
    to refresh text cannot silently relabel a record."""
    out = set_definition(RECORD, "new text")
    assert "definition_source: Pfam\n" in out


def test_a_record_with_no_definition_is_returned_unchanged():
    bare = "identifier: Pfam:PF00001\nlabel: x\n"
    assert set_definition(bare, "text", borrowed_source("IPR1", "PF00001")) == bare


def test_the_caller_passes_the_source_not_just_the_text():
    """MUTATION-DRIVEN. Tests that called `set_definition` directly could not
    catch the main loop dropping its third argument -- which IS the original
    defect. `enrich_record` exists so the wiring is covered, not just the
    splice."""
    out = enrich_record(RECORD, "IPR007647", "PF04567", "the InterPro abstract")
    assert "definition_source: Pfam\n" not in out, (
        "the caller dropped the source; the record would keep claiming Pfam "
        "while holding InterPro's prose")
    assert 'definition_source: "InterPro:IPR007647 abstract' in out
    assert "  the InterPro abstract\n" in out
