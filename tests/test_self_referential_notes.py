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
    605 notes in the corpus name a real ancestor and are correct as they stand."""
    monkeypatch.setattr(promote.E, "ancestry",
                        lambda terms, i: {"ARO:9000002"} if i == "ARO:9000001" else set())
    anc, _snippet, note = promote._drug_assertion(
        "ARO:9000001", "ARO:0000020", _terms(direct=False))
    assert anc == "ARO:9000002"
    assert note == ("Asserted on ARO:9000002 (the family), an is_a ancestor of this "
                    "record's ARO:9000001; inherited by this variant. CARD/ARO release "
                    "in data/raw/aro/aro.obo.")


def test_the_walks_FIRST_element_is_what_makes_the_defect_reachable(monkeypatch):
    """`[ident] + [a for a in ancestry if a != ident]` is the whole mechanism: without the
    record leading the walk there is no self-referential case to get wrong. A test that
    only exercised the inherited branch would have passed against the buggy code."""
    seen = []

    def _spy(terms, i):
        seen.append(i)
        return {"ARO:9000002"}

    monkeypatch.setattr(promote.E, "ancestry", _spy)
    promote._drug_assertion("ARO:9000001", "ARO:0000020", _terms(direct=True))
    src = pathlib.Path(promote.__file__).read_text(encoding="utf-8")
    assert "for anc in [ident] + [a for a in E.ancestry(terms, ident) if a != ident]" in src


def test_the_two_writers_agree_on_both_note_forms():
    """`fix_resistance_drug_edges` and `_drug_assertion` both write this note. They drifted
    once already -- one was fixed and the other was not -- and the corpus carried both
    forms for months. Pinned against the sibling's source so a change to either fails."""
    sibling = (REPO / "scripts" / "fix_resistance_drug_edges.py").read_text(encoding="utf-8")
    assert 'f"Asserted directly on {src} ({names.get(src, \'\')}) in the "' in sibling
    assert 'f"CARD/ARO release in data/raw/aro/aro.obo.")' in sibling
    assert 'f"Asserted on {src} ({names.get(src, \'\')}), an is_a ancestor "' in sibling
    # and the repairer reproduces the direct form exactly
    assert repair.corrected("ARO:1", "a name") == (
        "Asserted directly on ARO:1 (a name) in the CARD/ARO release in "
        "data/raw/aro/aro.obo.")


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
                    if repair.fix_note(ev.get("notes")):
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
