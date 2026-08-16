"""A term is not its own `is_a` ancestor (#364).

`_drug_assertion` walks `is_a` from the record upward with the RECORD ITSELF first, and
wrote the same note whichever step matched:

    Asserted on ARO:3004574 (Acinetobacter baumannii AbaQ), an is_a ancestor of this
    record's ARO:3004574; inherited by this variant.

`aro.obo` gives ARO:3004574 `is_a ARO:0000031` and nothing else, and the relation is
asserted ON the record rather than inherited by it.

TWO WRITERS, ONE WORDING. `fix_resistance_drug_edges` has emitted the correct form for 593
records; this function never did, so the promoter re-created the defect on every run and
re-promoting a repaired record silently undid the repair. That is why #408 could not simply
re-promote its drifted records — 74 of them differ from their config for exactly this
reason, with the RECORD right and the CONFIG wrong.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import promote_family_drafts as promote  # noqa: E402
import repair_self_referential_notes as repair  # noqa: E402

ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _terms(direct: bool):
    """A two-term ontology where the drug relation sits on the record, or on its parent."""
    rel = "confers_resistance_to_drug_class ARO:0000020 ! carbapenem"
    return {
        "ARO:9000001": {"name": "the record", "is_a": ["ARO:9000002"],
                        "rel": [rel] if direct else []},
        "ARO:9000002": {"name": "the family", "is_a": [],
                        "rel": [] if direct else [rel]},
    }


def test_a_direct_assertion_does_not_claim_the_record_is_its_own_ancestor(monkeypatch):
    """The walk puts the record first, which is right -- a term that asserts the relation
    directly must not be described as inheriting it. Only the WORDING was wrong."""
    monkeypatch.setattr(promote.E, "ancestry",
                        lambda terms, i: {"ARO:9000002"} if i == "ARO:9000001" else set())
    anc, snippet, note = promote._drug_assertion(
        "ARO:9000001", "ARO:0000020", _terms(direct=True))
    assert anc == "ARO:9000001"
    assert note == ("Asserted directly on ARO:9000001 (the record) in the CARD/ARO "
                    "release in data/raw/aro/aro.obo.")
    assert "ancestor" not in note
    assert "relationship: confers_resistance_to_drug_class" in snippet


def test_a_genuinely_inherited_assertion_still_says_inherited(monkeypatch):
    """The other branch must be untouched, or the fix trades one wrong note for another.
    11,284 notes in the corpus name a real ancestor and are correct as they stand."""
    monkeypatch.setattr(promote.E, "ancestry",
                        lambda terms, i: {"ARO:9000002"} if i == "ARO:9000001" else set())
    anc, _snippet, note = promote._drug_assertion(
        "ARO:9000001", "ARO:0000020", _terms(direct=False))
    assert anc == "ARO:9000002"
    assert note == ("Asserted on ARO:9000002 (the family), an is_a ancestor of this "
                    "record's ARO:9000001; inherited by this variant. CARD/ARO release "
                    "in data/raw/aro/aro.obo.")


def test_the_record_is_preferred_over_an_ancestor_that_also_asserts_it(monkeypatch):
    """`[ident] + [...]` is the whole mechanism: without the record leading the walk there
    is no self-referential case to get wrong, and a test exercising only the inherited
    branch passes against the buggy code.

    Asserted as BEHAVIOUR -- when BOTH the record and its parent carry the relation, the
    record must win and the note must say "directly". The first version of this test
    grepped the source line instead, which passes if the function returns garbage and
    fails if anyone reflows the line.
    """
    both = _terms(direct=True)
    both["ARO:9000002"]["rel"] = ["confers_resistance_to_drug_class ARO:0000020 ! carbapenem"]
    monkeypatch.setattr(promote.E, "ancestry",
                        lambda terms, i: {"ARO:9000002"} if i == "ARO:9000001" else set())
    anc, _s, note = promote._drug_assertion("ARO:9000001", "ARO:0000020", both)
    assert anc == "ARO:9000001", "an ancestor won over the record's own assertion"
    assert note.startswith("Asserted directly on ARO:9000001")
    # and with ONLY the ancestor asserting it, the same call takes the other branch
    anc2, _s2, note2 = promote._drug_assertion(
        "ARO:9000001", "ARO:0000020", _terms(direct=False))
    assert anc2 == "ARO:9000002" and "an is_a ancestor" in note2


def test_the_three_writers_agree_on_the_direct_note(monkeypatch):
    """Three places now produce this sentence -- `_drug_assertion`, the repairer, and
    `fix_resistance_drug_edges`. They drifted once already: one was fixed and the other was
    not, and the corpus carried both forms for months.

    Compared as OUTPUT rather than as source fragments. The first version grepped three
    f-string literals out of the sibling, which cannot catch behavioural divergence -- and
    there is some: the sibling's missing-name fallback is `names.get(src, "")` (empty
    parens) where the promoter's is `terms[anc].get("name", anc)` (the id). Harmless today
    (0 nameless ARO terms) and exactly the kind of thing a source grep hides.
    """
    monkeypatch.setattr(promote.E, "ancestry", lambda terms, i: set())
    _anc, _s, promoted = promote._drug_assertion(
        "ARO:9000001", "ARO:0000020",
        {"ARO:9000001": {"name": "AAC(3)", "is_a": [],
                         "rel": ["confers_resistance_to_drug_class ARO:0000020 ! x"]}})
    repaired = repair.corrected("ARO:9000001", "AAC(3)")
    assert promoted == repaired, f"writers disagree:\n  {promoted}\n  {repaired}"
    # a name containing a close-paren is the case that broke the repairer's pattern
    assert "AAC(3)" in promoted
    assert repair.fix_note(
        "Asserted on ARO:9000001 (AAC(3)), an is_a ancestor of this record's ARO:9000001; "
        "inherited by this variant. CARD/ARO release in data/raw/aro/aro.obo.") == promoted


def test_fix_note_requires_the_two_ids_to_MATCH():
    """The equality is the condition, not an assumption: a note naming a genuine ancestor
    must be left exactly as it is."""
    self_ref = ("Asserted on ARO:3004574 (AbaQ), an is_a ancestor of this record's "
                "ARO:3004574; inherited by this variant. CARD/ARO release in "
                "data/raw/aro/aro.obo.")
    inherited = self_ref.replace("record's ARO:3004574", "record's ARO:9999999")
    assert repair.fix_note(self_ref) == (
        "Asserted directly on ARO:3004574 (AbaQ) in the CARD/ARO release in "
        "data/raw/aro/aro.obo.")
    assert repair.fix_note(inherited) is None
    assert repair.fix_note("something else entirely") is None
    assert repair.fix_note(None) is None
    # folded across lines by PyYAML -- the shape that made a raw-text count report 98
    # where the true figure was 173
    assert repair.fix_note(self_ref.replace(" an is_a", "\n        an is_a")) is not None


def test_no_self_referential_note_remains_in_the_corpus():
    """The data half. Parsed per note rather than grepped: the note is a folded scalar, so
    a single-line regex undercounts it (98 against a true 173) and a whole-file collapse
    overcounts it (197, matching across note boundaries)."""
    if not ARO_DIR.is_dir():
        pytest.skip("ARO records absent")
    bad = []
    for path in ARO_DIR.glob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        if "an is_a ancestor of this record" not in text:
            continue
        span = repair._graph_block(text)
        if span is None:
            continue
        block = "".join(text.splitlines(keepends=True)[span[0]:span[1]])
        for graph in (yaml.safe_load(block) or {}).get("causal_graphs") or []:
            for edge in graph.get("edges") or []:
                for ev in edge.get("evidence") or []:
                    # DETECTED independently of the rewrite pattern. The first version
                    # used `fix_note` as its oracle, so the gate was blind to exactly the
                    # notes that pattern could not parse -- 11 across 7 records, whose
                    # term names contain a close-paren -- and passed while they survived.
                    if repair.looks_self_referential(ev.get("notes")):
                        bad.append(f"{path.name}: {ev['notes'][:70]}")
    assert bad == [], f"{len(bad)} self-referential note(s) remain:\n" + "\n".join(bad[:5])


def test_the_corrected_form_is_actually_present_so_the_check_above_is_not_vacuous():
    """`assert bad == []` passes just as well if the notes vanished entirely."""
    if not ARO_DIR.is_dir():
        pytest.skip("ARO records absent")
    n = sum(len(re.findall(r"Asserted directly on ARO:\d+",
                           p.read_text(encoding="utf-8")))
            for p in ARO_DIR.glob("*.yaml"))
    assert n >= 700, f"only {n} corrected notes; the repair may have removed rather than fixed"


def test_a_close_paren_in_the_term_name_does_not_hide_the_note(monkeypatch):
    """#461 review, and the reason the first pass reported "records repaired: 0" while 11
    notes survived.

    415 of aro.obo's 8,601 names contain a close-paren -- "Outer Membrane Porin (Opr)",
    "16S rRNA methyltransferase (A1408)", "AAC(3)". Against `\\([^)]*\\)` the name group
    stops at the inner paren, the fixed tail cannot match, and `fullmatch` fails. Because
    detection and rewrite were the SAME pattern, the record was reported as needing nothing.
    """
    note = ("Asserted on ARO:3004278 (Outer Membrane Porin (Opr)), an is_a ancestor of "
            "this record's ARO:3004278; inherited by this variant. CARD/ARO release in "
            "data/raw/aro/aro.obo.")
    assert repair.looks_self_referential(note), "detection missed a paren-containing name"
    assert repair.fix_note(note) == (
        "Asserted directly on ARO:3004278 (Outer Membrane Porin (Opr)) in the CARD/ARO "
        "release in data/raw/aro/aro.obo.")
    # the nested parens survive intact rather than being truncated at the inner one
    assert "(Outer Membrane Porin (Opr))" in repair.fix_note(note)


def test_detection_is_not_the_rewrite_pattern(monkeypatch):
    """A note the rewrite cannot parse must be reported as STRANDED, never silently
    skipped. The two patterns are separate precisely so a miss is loud."""
    weird = ("Asserted on ARO:1 (a name), an is_a ancestor of this record's ARO:1; "
             "inherited by this variant. SOME OTHER TAIL.")
    assert repair.looks_self_referential(weird), "detection is too narrow"
    assert repair.fix_note(weird) is None, "the rewrite pattern is too loose"

    block = ("causal_graphs:\n- graph_id: resistance\n  edges:\n  - subject: determinant\n"
             "    object: drug0\n    evidence:\n    - reference: ARO:1\n"
             f"      notes: {weird}\n")
    out, reason, n = repair.repair_record(block)
    assert out is None and n == 1, (out is None, n)
    assert "cannot parse" in reason, reason


def test_a_note_naming_a_genuine_ancestor_is_never_detected():
    """The equality of the two ids is the whole condition. 11,284 notes name a real
    ancestor and must be left exactly as they are."""
    inherited = ("Asserted on ARO:3005394 (BSU beta-lactamase (class D)), an is_a ancestor "
                 "of this record's ARO:3006902; inherited by this variant. CARD/ARO "
                 "release in data/raw/aro/aro.obo.")
    assert not repair.looks_self_referential(inherited)
    assert repair.fix_note(inherited) is None
