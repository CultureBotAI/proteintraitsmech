"""The serine-hydrolysis note repair (#466).

4,664 records said `serine β-lactam hydrolysis` where the promoter has emitted
`serine beta-lactam hydrolysis` since #194 — a config string edited without a
`--repromote`. It was 4,664 of the 5,074 records #408's gate reported as drifted.

Two things need pinning, and only one of them is the rewrite:

  * the replacement must be EXACTLY what the promoter emits, which is why both read one
    constant rather than each carrying a copy of the sentence — two copies is how the
    drift happened;
  * the scope must be one sentence. 111 notes legitimately carry `β` in
    `Qnr/MfpA right-handed β-helix`, and the promoter's ARO configs quote literature
    containing β throughout. A blanket substitution corrupts all of it.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
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


R = _load("repair_beta_lactam_notes")
ARO = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _record(note: str) -> str:
    # the note is emitted as a plain scalar, exactly as it sits on disk -- but a note
    # containing ": " is not a legal plain scalar, so those are quoted the way PyYAML
    # would. Without this the "leave other notes alone" case failed as `unreadable`,
    # testing the fixture rather than the code.
    # width=10**6 so it never wraps: only the first line gets the indent below, so a
    # wrapped continuation would land at column 0 and make the fixture unparseable --
    # which is a bug in the fixture that reads as a bug in the code.
    scalar = yaml.safe_dump({"notes": note}, allow_unicode=True, width=10**6,
                            default_flow_style=False).strip()
    return ("identifier: ARO:1\ncurator: edison-causal-graphs\n"
            "causal_graphs:\n- graph_id: resistance\n  edges:\n"
            "  - subject: determinant\n    object: mech0\n    evidence:\n"
            "    - reference: ARO:3000187\n"
            f"      {scalar}\nlicense: CC0\n")


def test_the_replacement_is_the_promoters_own_string_not_a_copy():
    """The invariant, structural rather than asserted: `repair_beta_lactam_notes` imports
    `SERINE_HYDROLYSIS_NOTE` from the promoter. If the promoter's wording changes this
    writes the new wording or fails to import; it cannot quietly disagree, which is exactly
    what happened to produce 4,664 wrong notes."""
    import promote_family_drafts as P
    assert R.SERINE_HYDROLYSIS_NOTE is P.SERINE_HYDROLYSIS_NOTE
    assert "beta-lactam" in R.SERINE_HYDROLYSIS_NOTE
    assert "β" not in R.SERINE_HYDROLYSIS_NOTE


def test_the_drifted_note_is_rewritten_and_the_indent_survives():
    out, n, cannot = R.repair_record(_record(R.DRIFTED))
    assert (n, cannot) == (1, {})
    assert f"      notes: {R.SERINE_HYDROLYSIS_NOTE}\n" in out
    # nothing else moved
    assert out.replace(R.SERINE_HYDROLYSIS_NOTE, R.DRIFTED) == _record(R.DRIFTED)


def test_an_already_correct_note_is_left_alone():
    out, n, cannot = R.repair_record(_record(R.SERINE_HYDROLYSIS_NOTE))
    assert (out, n, cannot) == (None, 0, {})


@pytest.mark.parametrize("note", [
    "KB trait: the pentapeptide-repeat (Qnr/MfpA right-handed β-helix, Rfr) fold.",
    "Determinant → phenotype; GOB-family MBLs confer broad β-lactam resistance.",
    "The attack of Ser70 on the substrate β-lactam carbonyl results in a covalent complex.",
])
def test_other_notes_containing_beta_are_NOT_touched(note):
    """The trap. 111 notes carry β correctly, and the promoter's configs quote literature
    full of it. A `s/β/beta/` over notes would corrupt every one -- the finder/fixer
    failure of #462 in its most destructive form."""
    out, n, cannot = R.repair_record(_record(note))
    assert (out, n, cannot) == (None, 0, {})


def test_a_FOLDED_drifted_note_is_stranded_not_skipped():
    """The finder parses; the fixer is line-anchored. PyYAML folding a note across lines is
    invisible to the fixer and visible to the finder -- the case #364's raw-text prefilter
    missed on 28 records while its verification scan agreed with the miss, because both
    shared the blind spot."""
    folded = ("identifier: ARO:1\ncurator: edison-causal-graphs\n"
              "causal_graphs:\n- graph_id: resistance\n  edges:\n"
              "  - subject: determinant\n    object: mech0\n    evidence:\n"
              "    - reference: ARO:3000187\n"
              "      notes: >-\n"
              "        The active site carries out the serine β-lactam hydrolysis\n"
              "        mechanism.\n"
              "license: CC0\n")
    out, n, cannot = R.repair_record(folded)
    assert out is None and cannot == {"unrewritable": 1}, cannot


def test_an_unparseable_record_is_stranded_not_skipped():
    out, n, cannot = R.repair_record("identifier: ARO:1\ncausal_graphs: \"unbalanced\n")
    assert out is None and cannot == {"unreadable": 1}, cannot


def test_the_prefilter_is_weaker_than_both_patterns():
    """A prefilter that repeats the fixer's precision is the #364 defect: it decides the
    record needs nothing before anything looks at it."""
    assert R.PREFILTER in R.DRIFTED and R.PREFILTER in R.SERINE_HYDROLYSIS_NOTE
    assert len(R.PREFILTER) < len(R.DRIFTED) / 3


@pytest.mark.skipif(not ARO.is_dir(), reason="ARO records absent")
def test_no_drifted_note_remains_in_the_corpus():
    """Scanned with the BROAD pattern, not the rewrite -- a verification that shares the
    fixer's blind spot certifies nothing (#462)."""
    remaining, examined = [], 0
    for path in sorted(ARO.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        if R.PREFILTER not in text:
            continue
        examined += 1
        if R.find_notes(text):
            remaining.append(path.name)
    assert examined > 1_000, f"examined only {examined}; this cannot certify the corpus"
    assert not remaining, remaining[:5]


@pytest.mark.skipif(not ARO.is_dir(), reason="ARO records absent")
def test_the_beta_helix_notes_survived():
    """111 before the repair, 111 after. The count is the point: a rewrite that caught
    these would look identical in every other respect."""
    import re
    NOTE_BETA_HELIX = re.compile(r"^[ \t]*notes:.*β-helix", re.M)
    n = sum(len(NOTE_BETA_HELIX.findall(p.read_text(encoding="utf-8")))
            for p in (REPO / "data" / "traits").rglob("*.yaml"))
    # 111 NOTES, measured before the repair. Counted on notes rather than on every
    # occurrence of the string: β-helix appears 418 times corpus-wide, mostly in
    # definitions quoting upstream prose, and this repair never looks at those.
    assert n == 111, f"expected 111 β-helix notes, found {n}"


@pytest.mark.skipif(not ARO.is_dir(), reason="ARO records absent")
def test_a_rerun_is_a_no_op():
    """Idempotence, checked by running the real script rather than reasoning about it."""
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "repair_beta_lactam_notes.py")],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout[-800:]
    assert "records repaired: 0" in out.stdout, out.stdout[-800:]


def test_a_record_with_BOTH_notes_rewrites_only_the_drifted_one():
    """The mutation that survived the first version of this file, and the one that matters.

    `test_other_notes_containing_beta_are_NOT_touched` exercises records carrying ONLY a
    β note, where `find_notes` returns 0 and `repair_record` returns before `FIX` is ever
    applied -- so the breadth of the rewrite pattern is never tested at all. Widening `FIX`
    to `notes:.*β.*` passed every test in this file.

    On a record carrying both, that mutation rewrites both, and `Qnr/MfpA right-handed
    β-helix` becomes `beta-helix` on 111 records. This is the test that sees it.
    """
    keep = "KB trait: the pentapeptide-repeat (Qnr/MfpA right-handed β-helix, Rfr) fold."
    both = ("identifier: ARO:1\ncurator: edison-causal-graphs\n"
            "causal_graphs:\n- graph_id: resistance\n  edges:\n"
            "  - subject: determinant\n    object: mech0\n    evidence:\n"
            "    - reference: ARO:3000187\n"
            f"      notes: {R.DRIFTED}\n"
            "    - reference: ARO:3000001\n"
            f"      notes: '{keep}'\n"
            "license: CC0\n")
    out, n, cannot = R.repair_record(both)
    assert (n, cannot) == (1, {}), (n, cannot)
    assert R.SERINE_HYDROLYSIS_NOTE in out
    assert keep in out, "the β-helix note was rewritten -- the fixer is too broad"
    assert "beta-helix" not in out
