"""Tests for the LLM-abstract review pipeline (issue #92).

The two things worth testing here are the record edit and the reviewer-output parser.
The edit touches 2,746 curated files, so a formatting assumption that holds for most
of them and not a few is the failure mode that has bitten this repo repeatedly. The
parser handles output from a non-deterministic process, and its first real call
already returned a shape the first implementation could not read.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from review_llm_abstracts import (  # noqa: E402
    _parse_verdicts, folded, promoted_source, replace_scalar,
)

BATCH = [{"id": "PANTHER:PTHR1", "path": "p.yaml"}, {"id": "PANTHER:PTHR2", "path": "q.yaml"}]


def _v(i, verdict="PROMOTE"):
    return {"id": i, "verdict": verdict, "confidence": 0.9, "reason": "r", "concerns": []}


# ------------------------------------------------------------------ reviewer output

@pytest.mark.parametrize("raw,expect", [
    (json.dumps([_v("PANTHER:PTHR1")]), ["PROMOTE"]),
    ("```json\n" + json.dumps([_v("PANTHER:PTHR1", "FLAG")]) + "\n```", ["FLAG"]),
    ("```\n" + json.dumps([_v("PANTHER:PTHR1", "REJECT")]) + "\n```", ["REJECT"]),
    (json.dumps(_v("PANTHER:PTHR1")), ["PROMOTE"]),                       # bare object
    (json.dumps([_v("PANTHER:PTHR1")]) + "\n\nI reviewed 1 [see above].", ["PROMOTE"]),
])
def test_reviewer_output_shapes_are_read(raw, expect):
    assert [v["verdict"] for v in _parse_verdicts(raw, BATCH[:1], "m")] == expect


def test_two_arrays_are_both_read():
    """The shape the canary hit on its first and only call.

    Spanning first `[` to last `]` hands `[...]\\n[...]` to json.loads, which raises
    "Extra data" and throws away a whole batch of verdicts that were already paid for.
    """
    raw = json.dumps([_v("PANTHER:PTHR1")]) + "\n" + json.dumps([_v("PANTHER:PTHR2", "REJECT")])
    got = _parse_verdicts(raw, BATCH, "m")
    assert [(v["id"], v["verdict"]) for v in got] == [
        ("PANTHER:PTHR1", "PROMOTE"), ("PANTHER:PTHR2", "REJECT")]


def test_verdicts_for_unrequested_ids_are_discarded():
    """A verdict for an id not in the batch is a reviewer error, never a record edit."""
    raw = json.dumps([_v("PANTHER:PTHR1"), _v("PANTHER:NOT_IN_BATCH")])
    assert [v["id"] for v in _parse_verdicts(raw, BATCH[:1], "m")] == ["PANTHER:PTHR1"]


def test_unanswered_items_get_no_verdict_rather_than_a_default():
    """Silence must not become PROMOTE. An unanswered id is simply re-reviewed later."""
    assert _parse_verdicts(json.dumps([_v("PANTHER:PTHR1")]), BATCH, "m")[0]["id"] == "PANTHER:PTHR1"
    assert len(_parse_verdicts(json.dumps([_v("PANTHER:PTHR1")]), BATCH, "m")) == 1


@pytest.mark.parametrize("bad", ["MAYBE", "promote?", "", "APPROVE"])
def test_an_unrecognised_verdict_is_dropped(bad):
    assert _parse_verdicts(json.dumps([_v("PANTHER:PTHR1", bad)]), BATCH[:1], "m") == []


def test_lowercase_verdict_is_accepted():
    assert _parse_verdicts(json.dumps([_v("PANTHER:PTHR1", "promote")]),
                           BATCH[:1], "m")[0]["verdict"] == "PROMOTE"


def test_unparseable_output_raises_rather_than_returning_nothing():
    """A silent empty result would look like "reviewed, nothing to promote"."""
    with pytest.raises(ValueError):
        _parse_verdicts("I could not review these.", BATCH, "m")


# ----------------------------------------------------------------------- record edit

RECORD = """identifier: PANTHER:PTHR1
label: "A FAMILY"
definition: >-
  A FAMILY — a full-length protein family modelled by the PANTHER 19.0 profile HMM.
definition_source: "PANTHER 19.0 (composed from the family name)"
trait_axis: SEQUENCE
mapping_status: SEEDED
license: CC-BY 4.0
"""


def test_replace_scalar_replaces_the_whole_folded_block():
    """A folded scalar runs to the next top-level key.

    Replacing only the `key:` line strands the old continuation lines as orphans that
    no longer belong to any key - unparseable, and the caller's `out != text` guard
    would not notice because the text did change.
    """
    out = replace_scalar(RECORD, "definition", folded("definition", "New text here."))
    assert "New text here." in out
    assert "full-length protein family modelled" not in out
    assert out.count("definition:") == 1
    import yaml
    assert yaml.safe_load(out)["definition"] == "New text here."
    # every other key survives untouched
    before, after = yaml.safe_load(RECORD), yaml.safe_load(out)
    assert {k: v for k, v in before.items() if k != "definition"} == \
           {k: v for k, v in after.items() if k != "definition"}


def test_replace_scalar_on_a_single_line_value():
    out = replace_scalar(RECORD, "mapping_status", "mapping_status: PROPOSED\n")
    import yaml
    assert yaml.safe_load(out)["mapping_status"] == "PROPOSED"
    assert yaml.safe_load(out)["license"] == "CC-BY 4.0"


def test_replace_scalar_on_the_last_key_keeps_the_file_valid():
    out = replace_scalar(RECORD, "license", 'license: CC0-1.0\n')
    import yaml
    assert yaml.safe_load(out)["license"] == "CC0-1.0"


def test_replace_scalar_refuses_a_key_that_is_absent():
    """Better to fail loudly than to silently leave the record unchanged."""
    with pytest.raises(KeyError):
        replace_scalar(RECORD, "no_such_key", "no_such_key: x\n")


def test_replace_scalar_does_not_match_a_key_inside_prose():
    """`definition_source:` must not be found when looking for `definition:`."""
    out = replace_scalar(RECORD, "definition", folded("definition", "X."))
    assert 'definition_source: "PANTHER 19.0 (composed from the family name)"' in out


def test_folded_collapses_newlines_so_the_block_cannot_break_the_record():
    """An abstract containing a newline would otherwise emit a second, unindented line."""
    out = folded("definition", "one\ntwo   three\n\nfour")
    assert out == "definition: >-\n  one two three four\n"
    import yaml
    assert yaml.safe_load(out)["definition"] == "one two three four"


# ------------------------------------------------------------------------ provenance

def test_promoted_source_never_claims_curator_review():
    """The whole point of issue #92: an LLM review is not a curator review.

    If this string ever loses `not curator-reviewed`, machine-written text becomes
    indistinguishable from curated text in every downstream consumer.
    """
    src = promoted_source("InterPro:IPR000001", "claude-sonnet-5")
    assert "not curator-reviewed" in src
    assert "LLM-generated" in src
    assert "LLM-reviewed claude-sonnet-5" in src
    assert "InterPro:IPR000001 abstract" in src


def test_promoted_source_records_the_reviewing_model():
    """Which model reviewed it is part of the provenance, not a detail."""
    assert "LLM-reviewed some-future-model" in promoted_source("InterPro:IPR1", "some-future-model")


def test_promoted_source_without_an_interpro_entry_still_attributes():
    assert promoted_source(None, "m").startswith('definition_source: "InterPro abstract (')
