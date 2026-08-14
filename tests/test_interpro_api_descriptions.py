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


@pytest.mark.skipif(not MISSING.exists(), reason="artefact absent")
def test_records_sourced_from_the_api_say_so_and_not_abstract():
    """A record whose text came from the API but cites "IPR011598 abstract" claims to quote
    a release that does not contain it -- #344's defect in a new place, and #344 cost 407
    records their definition. Both enrichers must say `description (InterPro API; ...)`.

    Also asserts the #344 gate SEES them: its regex matched only "abstract", so all 45
    became invisible to it the moment they were written.
    """
    import audit_pfam_interpro as A
    n_api = 0
    for path in (REPO / "data" / "traits").rglob("*.yaml"):
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
