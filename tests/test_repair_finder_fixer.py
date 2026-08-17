"""A repair script's finder must be broader than its fixer (#462).

THE SHAPE, which this repo has now produced four times in five PRs
------------------------------------------------------------------
One regex, or one predicate, is used as BOTH the finder and the fixer. When it cannot
parse a case, the record is reported as *"nothing to do"* rather than *"needs fixing,
cannot"* — and the stranded counter that exists to catch exactly that is computed with the
same predicate, so it never fires. Then the acceptance test uses that predicate as its
oracle too, and the gate agrees with the miss.

#461 is the worked example: `\\([^)]*\\)` against `Outer Membrane Porin (Opr)` stopped at
the inner paren, 11 notes across 7 records were skipped, and the tool printed
`records repaired: 0` — a miss indistinguishable from a clean corpus.

WHAT THESE TESTS ARE, AND WHY THEY LOOK ODD
--------------------------------------------
Every one of them **injects damage the fixer cannot handle** and asserts the script says
so. They are not testing the repairs — the repairs have their own tests, and all of these
scripts report 0 to do against the corpus today. They are testing the *reporting of
failure*, which is the only part that was never exercised, because on real data it never
fires.

That is the whole point. A guard nobody has watched fire is a guard nobody knows works, and
in this repo three of them did not.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- repair_misattributed_snippets: a reworded snippet -----------------------------------

SNIPPETS = _load("repair_misattributed_snippets")


def _record(reference: str, snippet: str, subject="determinant", obj="resistance") -> str:
    """A record shaped exactly as `promote_family_drafts._dump` emits one, so the
    re-dump guard passes and the near-match branch is what decides the outcome."""
    block = yaml.safe_dump(
        {"causal_graphs": [{"graph_id": "resistance",
                            "edges": [{"subject": subject, "object": obj,
                                       "evidence": [{"reference": reference,
                                                     "snippet": snippet}]}]}]},
        sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    return f"identifier: ARO:1\ncurator: edison-causal-graphs\n{block}license: CC0\n"


def _repair_entry():
    return next(r for r in SNIPPETS.REPAIRS if r["ref_from"] == "Pfam:PF04563")


def test_an_exact_snippet_is_repaired_normally():
    """The control. Without this, a test asserting STRANDED could pass on a script that
    strands everything."""
    rep = _repair_entry()
    out, reason, n = SNIPPETS.repair_record(_record(rep["ref_from"], rep["old"]))
    assert reason == "repaired" and n == 1, reason
    assert SNIPPETS._norm(rep["new"]) in SNIPPETS._norm(out)


def test_a_REWORDED_snippet_is_stranded_not_silently_skipped():
    """The defect. One word changed inside the quote -- which is what #423, #425 and #426
    were each about -- and the old code returned "no matching snippet", filing the record
    with the ones that need nothing."""
    rep = _repair_entry()
    drifted = rep["old"].replace("Prokaryotes contain", "Prokaryotic cells contain")
    assert drifted != rep["old"]
    out, reason, n = SNIPPETS.repair_record(_record(rep["ref_from"], drifted))
    assert out is None
    assert reason.startswith("STRANDED"), reason
    assert n == 1, "a stranded item must be COUNTED, not merely mentioned"


def test_an_unrelated_snippet_on_the_same_reference_is_left_alone():
    """The false-positive guard. `ref_from` alone is far too broad -- plenty of evidence
    legitimately cites these references with other text -- so the near-matcher must key on
    the TEXT resembling `old`, not on the reference."""
    out, reason, n = SNIPPETS.repair_record(
        _record("Pfam:PF04563", "An entirely unrelated sentence about zinc coordination."))
    assert (out, n) == (None, 0)
    assert "STRANDED" not in reason, reason


def test_an_ALREADY_REPAIRED_snippet_is_not_reported_every_run():
    """`new` resembles `old` by construction, so a naive similarity test would strand every
    record this script has already fixed -- turning the count into noise."""
    rep = _repair_entry()
    out, reason, n = SNIPPETS.repair_record(_record(rep["ref_from"], rep["new"]))
    assert (out, n) == (None, 0)
    assert "STRANDED" not in reason, reason


def test_on_edge_still_narrows_the_near_matcher():
    """Two carO entries share a (reference, snippet) pair and differ only by `on_edge`. The
    broad finder must respect that or it will strand the sibling edge."""
    caro = [r for r in SNIPPETS.REPAIRS if r["ref_from"] == "ARO:3003808"]
    assert len(caro) >= 2 and all(r.get("on_edge") for r in caro)
    rep = caro[0]
    drifted = rep["old"].replace("transmembrane", "trans-membrane")
    # on the edge the entry names -> recognised
    edge = {"subject": rep["on_edge"][0], "object": rep["on_edge"][1]}
    assert SNIPPETS._near_match(edge, {"reference": rep["ref_from"], "snippet": drifted})
    # on an edge no entry names -> not this repair's business
    other = {"subject": "determinant", "object": "not-an-edge-any-entry-names"}
    assert SNIPPETS._near_match(other, {"reference": rep["ref_from"],
                                        "snippet": drifted}) is None


def test_the_corpus_has_no_stranded_snippets_today():
    """The claim in the module comment, asserted rather than asserted-in-prose. If this
    breaks, a snippet drifted and the repair table no longer covers it."""
    aro = REPO / "data" / "traits" / "function" / "resistance" / "aro"
    if not aro.is_dir():
        pytest.skip("ARO records absent")
    stranded = []
    for path in sorted(aro.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if "curator: edison-causal-graphs" not in text:
            continue
        _, reason, _ = SNIPPETS.repair_record(text)
        if reason.startswith("STRANDED"):
            stranded.append((path.name, reason))
    assert not stranded, stranded[:5]


# --- repair_pfam_interpro_xrefs: an xref shape the rewrite cannot parse -------------------

XREFS = _load("repair_pfam_interpro_xrefs")

_PFAM = """identifier: Pfam:PF00001
mapped_xrefs:
- object: InterPro:IPR000001
  mapping_source: pfam2interpro
license: CC0
"""


def test_a_parseable_xref_is_repointed_normally():
    """The control again."""
    out, reason = XREFS.repair_text(_PFAM, "IPR999999")
    assert reason == "repaired" and "InterPro:IPR999999" in out


def test_an_xref_the_rewrite_cannot_parse_is_stranded():
    """The keys REORDERED -- `mapping_source` before `object` -- which is schema-legal, is
    not the shape any seeder emits today, and which `XREF` cannot match. The old code
    returned "no pfam2interpro InterPro xref": the same answer as a record that has none."""
    reordered = """identifier: Pfam:PF00001
mapped_xrefs:
- mapping_source: pfam2interpro
  object: InterPro:IPR000001
license: CC0
"""
    out, reason = XREFS.repair_text(reordered, "IPR999999")
    assert out is None
    assert reason.startswith("STRANDED"), reason


def test_a_record_with_genuinely_no_pfam2interpro_xref_is_not_stranded():
    """The distinction the whole change is about: 'none' and 'unreadable' must not give the
    same answer, and 'none' must stay quiet."""
    clean = """identifier: Pfam:PF00001
mapped_xrefs:
- object: GO:0005515
  mapping_source: pfam2go
license: CC0
"""
    out, reason = XREFS.repair_text(clean, "IPR999999")
    assert out is None and "STRANDED" not in reason, reason


def test_the_corpus_has_no_stranded_xrefs_today():
    traits = REPO / "data" / "traits"
    if not traits.is_dir():
        pytest.skip("records absent")
    bad = []
    for path in traits.rglob("*.yaml"):
        if "/pfam/" not in str(path):
            continue
        text = path.read_text(encoding="utf-8")
        if "pfam2interpro" not in text:
            continue
        if len(XREFS.LOOSE.findall(text)) > len(list(XREFS.XREF.finditer(text))):
            bad.append(path.name)
    assert not bad, bad[:5]


# --- repair_interpro_abstracts: a definition that wraps across lines ----------------------

ABSTRACTS = _load("repair_interpro_abstracts")


def test_the_multiline_detector_sees_a_wrapped_definition():
    """`_DEF` captures the first line of a folded scalar, so every comparison downstream is
    against a fragment and the record is skipped as "unchanged" -- a miss shaped exactly
    like nothing to do."""
    wrapped = ("identifier: InterPro:IPR000001\ndefinition: >-\n"
               "  first line of the abstract\n  second line of it\n"
               "definition_source: InterPro\nlicense: CC0\n")
    assert ABSTRACTS._DEF_MULTILINE.search(wrapped)
    # and the fragment `_DEF` would have compared with, which is the actual defect
    assert ABSTRACTS._DEF.search(wrapped).group(1) == "first line of the abstract"


def test_the_multiline_detector_leaves_a_one_line_definition_alone():
    """Every record in the corpus is this shape; a detector that fired here would strand
    all 68,900."""
    flat = ("identifier: InterPro:IPR000001\ndefinition: >-\n"
            "  the whole abstract on one line\n"
            "definition_source: InterPro\nlicense: CC0\n")
    assert ABSTRACTS._DEF_MULTILINE.search(flat) is None


def test_no_targeted_record_wraps_today():
    """The measured claim in the module comment. 0 of 68,900."""
    traits = REPO / "data" / "traits"
    if not traits.is_dir():
        pytest.skip("records absent")
    bad = []
    for path in traits.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        sm = ABSTRACTS._SRC.search(text)
        if not sm or "InterPro" not in sm.group(1):
            continue
        if ABSTRACTS._DEF_MULTILINE.search(text):
            bad.append(path.name)
    assert not bad, bad[:5]
