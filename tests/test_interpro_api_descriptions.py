"""The InterPro API's description format is not the release's abstract format (#445).

209 of the release's 54,190 entries ship no `<abstract>`, while the API has a
curator-written description for every one — 811 to 5,326 characters. That gap left 45 Pfam
records and 60 InterPro records defining themselves by their own name: `IPR006076` read
`"FAD dependent oxidoreductase"`, 28 characters, against 848 in the API.

The two formats share nothing but intent. The release ships XML elements
(`<db_xref db=... dbkey=.../>`); the API ships HTML with square-bracket markers
(`[[cite:PUB00012956], [cite:PUB00079463]]`, `[ec:1.2.4.1]`, `[interpro:IPR000001]`).
Every test here pins a way the first version of the cleaner got that wrong and shipped
damaged prose — the failure mode #448 exists for.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from interpro_text import clean_api_description  # noqa: E402
from record_scope import records_in_source_directories  # noqa: E402

MISSING = REPO / "data" / "raw" / "interpro" / "missing_abstracts.json"


def _blocks(text):
    return [{"text": text, "llm": False, "checked": False}]


def test_a_citation_GROUP_leaves_no_comma_run():
    """Citations arrive as a bracketed LIST. Matching each `[cite:X]` on its own leaves the
    separators, which turned one real ferrochelatase sentence into
    "...at the C terminus,,,,,,,,,,,." -- damage written BY the fix for damage.
    """
    raw = ("<p>a dimerization motif at the C terminus [[cite:PUB00012956], "
           "[cite:PUB00079463], [cite:PUB00079464]]. In eukaryotic cells it binds.</p>")
    got = clean_api_description(_blocks(raw))
    assert got == ("a dimerization motif at the C terminus. In eukaryotic cells it binds.")
    assert ",," not in got and " ," not in got


def test_italics_get_a_space_and_sup_sub_do_not():
    """InterPro writes `of<i>Bacillus subtilis</i>and` with NO spaces around the tags, so
    stripping tags to nothing yields "ofBacillus subtilisand" -- which the first version
    shipped. But `NAD<sup>+</sup>` must close up, or the chemistry breaks. Both, in one
    string, because a fix for either alone is wrong.
    """
    raw = ("<p>structure of<i>Bacillus subtilis</i>and human, with "
           "NAD<sup>+</sup>+ H<sub>2</sub>O.</p>")
    got = clean_api_description(_blocks(raw))
    assert "of Bacillus subtilis and human" in got, got
    assert "NAD++ H2O" in got, got


def test_accession_markers_survive_and_chemistry_brackets_are_untouched():
    """`[interpro:]`, `[ec:]` and `[cazy:]` ARE the content -- 64 of them across the 209 --
    and a bracket sweep deletes them. `[2Fe-2S]` and `[Fe<sup>4+</sup>=O]` are chemistry
    and must come through unchanged.
    """
    raw = ("<p>pyruvate dehydrogenase ([ec:1.2.4.1]) relates to [interpro:IPR000001] and "
           "[cazy:GH25]; each subunit contains one [2Fe-2S] cluster and a "
           "[Fe<sup>4+</sup>=O] intermediate.</p>")
    got = clean_api_description(_blocks(raw))
    assert "EC:1.2.4.1" in got and "InterPro:IPR000001" in got and "CAZy:GH25" in got
    assert "[2Fe-2S]" in got, got
    assert "[Fe4+=O]" in got, got
    # an UNKNOWN marker is left alone rather than guessed at or deleted
    assert "[wibble:123]" in clean_api_description(_blocks("<p>x [wibble:123] y</p>"))


def test_list_items_do_not_run_together():
    raw = "<p>related:</p><ul><li>alpha chain</li><li>beta chain</li></ul>"
    got = clean_api_description(_blocks(raw))
    assert "alpha chain; beta chain" in got, got
    assert "chainbeta" not in got


def test_empty_and_missing_input():
    assert clean_api_description([]) == ""
    assert clean_api_description(_blocks("")) == ""
    assert clean_api_description([{"llm": False}]) == ""


@pytest.mark.skipif(not MISSING.exists(),
                    reason="data/raw/interpro/missing_abstracts.json absent; run "
                           "`just fetch-interpro-missing-abstracts`")
def test_no_markup_survives_into_any_of_the_real_descriptions():
    """The whole artefact, swept for every shape that has bitten this corpus before.

    A unit test on hand-written input proves the cleaner handles what I thought of; this
    proves it handles what InterPro actually wrote.
    """
    data = json.loads(MISSING.read_text(encoding="utf-8"))
    assert len(data) >= 200, f"only {len(data)} entries; the artefact looks truncated"
    problems = []
    for acc, rec in data.items():
        text = clean_api_description(rec["description"])
        if not text:
            continue
        for pattern, name in ((r"<[^>]+>", "html tag"), (r"\[\[|\]\]", "double bracket"),
                              (r"\[(?:cite|interpro|ec|cazy):", "marker survived"),
                              (r"&\w+;", "html entity"), (r",\s*,", "comma run"),
                              (r"\s[,.;]", "space before punctuation"),
                              (r"\s{2,}", "double space")):
            m = re.search(pattern, text)
            if m:
                problems.append(f"{acc}: {name} at {text[max(0, m.start()-40):m.start()+40]!r}")
                break
    assert problems == [], "\n".join(problems[:8])


@pytest.mark.skipif(not MISSING.exists(), reason="artefact absent")
def test_the_artefact_records_the_llm_flags_it_must_not_decide():
    """#92: a machine-written description promoted under `definition_source: InterPro`
    launders its provenance. The fetch script records the flags and refuses to judge; the
    enrichers refuse to promote a flagged one. None of the 209 is flagged today, and that
    is a fact about this release, not a property of the pipeline."""
    data = json.loads(MISSING.read_text(encoding="utf-8"))
    for acc, rec in data.items():
        for block in rec["description"]:
            assert "llm" in block and "checked" in block, f"{acc} lost its provenance flags"
        assert "is_llm" in rec and "is_reviewed_llm" in rec, acc


def test_records_sourced_from_the_api_say_so_and_not_abstract():
    """A record whose text came from the API but cites "IPR011598 abstract" claims to quote
    a release that does not contain it -- #344's defect in a new place, and #344 cost 407
    records their definition. Both enrichers must say `description (InterPro API; ...)`.

    Also asserts the #344 gate SEES them: its regex matched only "abstract", so all 45
    became invisible to it the moment they were written.

    NO SKIP GUARD, deliberately. This reads `data/traits` only -- all committed -- and the
    first version was gated on `missing_abstracts.json`, which is gitignored. It therefore
    skipped on every CI run, silently, while guarding 105 committed records (#454 review).
    """
    import audit_pfam_interpro as A
    n_api = 0
    # The two writers that emit this exact provenance marker write only InterPro- and
    # Pfam-source directories.  Scoping by those writer-owned directories avoids reading
    # every unrelated record; it is safe here because this check is about that marker,
    # not about arbitrary CURIE prefixes.
    paths = records_in_source_directories(
        REPO / "data" / "traits", {"interpro", "pfam"}
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "InterPro API; this entry ships no abstract" not in text:
            continue
        n_api += 1
        src = re.search(r"^definition_source: (.+)$", text, re.M).group(1)
        assert " abstract (" not in src, f"{path.name} claims to quote an absent abstract"
        assert "description (InterPro API" in src, src
        if "/pfam/" in str(path):
            assert A.DEF_SRC.search(text), f"{path.name} is invisible to audit-pfam-interpro"
    assert n_api >= 100, f"only {n_api} records carry the API provenance"


# ---------------------------------------------------------------------------------------
# Review follow-ups (#454 review): the cap deleted the only entry-specific sentence, and
# three damage shapes reached 105 committed records before anyone read one end to end.
# ---------------------------------------------------------------------------------------

def test_the_cap_anchors_on_the_DEFINING_paragraph_wherever_it_sits():
    """Two wrong versions of this shipped before the right one, both by assuming a position.

      * head-truncation kept the front, and for entries whose defining sentence is LAST --
        "This entry represents an active site found in a number of peroxidases." -- deleted
        the only part naming the trait. IPR019794 (an active site) and IPR019793 (a
        haem-binding site) came out BYTE-IDENTICAL.
      * keeping the last paragraph instead broke the opposite shape, and worse: InterPro
        often ENDS with a member catalogue. IPR011598's defining text is paragraph 0 and its
        last paragraph is 3,426 characters of myc-family members, so `bhlh-hif1a` -- label
        "Hypoxia-inducible factor 1-alpha bHLH domain" -- was given a myc catalogue
        mentioning neither HIF1A nor bHLH.

    All three real positions are covered here: defining paragraph first, in the middle, and
    last. A fixture that only exercised one is how the second version passed.
    """
    filler = "general background. " * 120                       # ~2,400 chars

    # LAST -- the IPR019794 shape
    last = [{"text": f"<p>{filler}</p><p>This entry represents the active site.</p>"}]
    got = clean_api_description(last, cap=1800)
    assert got.endswith("This entry represents the active site."), got[-60:]

    # FIRST, with a huge catalogue after it -- the IPR011598 shape that regressed
    first = [{"text": f"<p>This domain is found in eukaryotes and does a thing.</p>"
                      f"<p>Proteins containing it include:</p><p>{filler}</p>"}]
    got = clean_api_description(first, cap=1800)
    assert got.startswith("This domain is found in eukaryotes"), got[:60]

    # MIDDLE -- the IPR002515 shape
    mid = [{"text": f"<p>{filler}</p><p>This entry represents the CCHHC zinc finger.</p>"
                    f"<p>{filler}</p>"}]
    got = clean_api_description(mid, cap=1800)
    assert "This entry represents the CCHHC zinc finger." in got, got[-90:]

    for blocks in (last, first, mid):
        out = clean_api_description(blocks, cap=1800)
        assert len(out) <= 1800, len(out)
        assert "…" in out, "the elision is not marked"

    # two entries sharing a preamble stay distinguishable
    other = [{"text": f"<p>{filler}</p><p>This entry represents something else.</p>"}]
    assert clean_api_description(other, cap=1800) != clean_api_description(last, cap=1800)
    # uncapped is untouched
    assert clean_api_description(last) == clean_api_description(last, cap=None)


def test_the_cap_is_never_exceeded_by_a_defining_paragraph_near_its_size():
    """`budget = cap - len(anchor) - 3` went NEGATIVE for an anchor of cap-1 or cap-2
    characters, and `head[:-2]` slices from the END -- returning nearly the whole preamble
    and blowing the cap by thousands of characters. No entry lands in that window today;
    the next InterPro release is not obliged to be so kind.
    """
    for anchor_len in (97, 98, 99, 100, 101):
        anchor = "This entry represents " + "x" * (anchor_len - 22)
        blocks = [{"text": f"<p>{'preamble ' * 60}</p><p>{anchor}</p>"}]
        out = clean_api_description(blocks, cap=100)
        assert len(out) <= 100, f"anchor {anchor_len}: produced {len(out)} against cap 100"


def test_an_elision_never_cuts_mid_word():
    """25 of the 105 definitions elided mid-word before this -- `...as ortholo`,
    `...translocate t`, `...degradation of lignin. In M`."""
    blocks = [{"text": "<p>" + "alpha bravo charlie delta echo " * 40 + "</p>"
                       "<p>This entry represents the thing.</p>"}]
    got = clean_api_description(blocks, cap=400)
    head = got.split(" … ")[0]
    assert head.endswith(("alpha", "bravo", "charlie", "delta", "echo")), repr(head[-25:])


def test_a_list_item_that_already_ends_in_a_stop_does_not_gain_a_semicolon():
    """`</li>` became "; " unconditionally, and InterPro's items mostly end in a full stop,
    so 125 `".;"` sequences reached 32 records -- against 9 in the entire 429k-record
    corpus before this PR."""
    ends_in_stop = [{"text": "<ul><li>alcohol dehydrogenases.</li>"
                             "<li>Insect-type reductases.</li></ul>", "llm": False}]
    got = clean_api_description(ends_in_stop)
    assert ".;" not in got, got
    assert "dehydrogenases. Insect-type" in got, got
    # ...but an item WITHOUT punctuation still gets its separator, or the list runs together
    no_stop = [{"text": "<ul><li>alpha chain</li><li>beta chain</li></ul>", "llm": False}]
    assert "alpha chain; beta chain" in clean_api_description(no_stop)


def test_a_leading_synonym_list_is_dropped_not_concatenated():
    """`Synonym(s): Penicillinase, Cephalosporinase` is metadata InterPro renders above the
    prose. Merged into a definition it reads as one, and 9 entries opened with it --
    `imp-dehydrogenase` with two stacked."""
    blocks = [{"text": "<p>Synonym(s): Protohaem ferro-lyase, Iron chelatase, etc. "
                       "<p>Ferrochelatase is the terminal enzyme of the pathway.</p>",
               "llm": False}]
    got = clean_api_description(blocks)
    assert got.startswith("Ferrochelatase is the terminal enzyme"), got
    assert "Synonym" not in got


def test_an_unclosed_paragraph_still_separates_two_sentences():
    """InterPro opens a second `<p>` without closing the first in 5 of the 209. Splitting on
    the closing tag alone fused the sentences with no punctuation between them."""
    got = clean_api_description([{"text": "<p>First sentence ends here.<p>Second begins.",
                                  "llm": False}])
    assert "here. Second" in got, got


def test_sup_and_sub_close_up_for_chemistry_but_not_before_a_word():
    """22 of the 61 occurrences are followed by a capital continuing a formula
    (`H<sub>2</sub>O`); 18 by a lowercase letter starting a word
    (`H<sub>2</sub>O<sub>2</sub>to give`, `Mn<sup>2+</sup>serves`). Opposite treatments.

    The first version got this backwards for the commonest case, because `re.I` on the
    whole pattern made the lookahead's `[a-z]` match capitals too -- so `H<sub>2</sub>O`
    became "H2 O". The flag is scoped to the tag now.
    """
    got = clean_api_description([{"text": "<p>NAD<sup>+</sup>+ H<sub>2</sub>O and "
                                          "H<sub>2</sub>O<sub>2</sub>to give "
                                          "Mn<sup>2+</sup>serves.</p>", "llm": False}])
    assert "H2O and" in got, got
    assert "H2O2 to give" in got, got
    assert "Mn2+ serves" in got, got


def test_no_dot_semicolon_or_weld_reaches_any_of_the_209():
    """The corpus-wide sweep the earlier version of this file should have included. Every
    shape below reached committed records once."""
    if not MISSING.exists():
        pytest.skip("artefact absent; run `just fetch-interpro-missing-abstracts`")
    data = json.loads(MISSING.read_text(encoding="utf-8"))
    problems = []
    for acc, rec in data.items():
        text = clean_api_description(rec["description"], cap=1800)
        if not text:
            continue
        for pattern, name in ((r"\.\s*;", "dot-semicolon"),
                              (r"^\s*Synonym\(s\)", "synonym opener"),
                              (r"\b[A-Z][a-z]?\d\+?[a-z]{2,}\b", "formula welded to a word"),
                              (r"\.\s*[A-Z][a-z]+\s+\.", "stranded fragment")):
            m = re.search(pattern, text)
            if m:
                problems.append(f"{acc}: {name} at {text[max(0, m.start()-40):m.start()+45]!r}")
                break
    assert problems == [], "\n".join(problems[:8])
