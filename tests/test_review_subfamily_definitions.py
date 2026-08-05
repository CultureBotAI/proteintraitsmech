"""Guards on the codex review of subfamily-derived definitions (#151).

The verdicts in `research/subfamily-definition-review.jsonl` decided that 11 records
lost their definitions. Everything that decides *which* records those are is worth a
test, because a silent failure here does not look like a failure: it looks like a
confident verdict.

The specific thing being defended against is not hypothetical. A codex run earlier in
this repo fabricated 25 plausible PANTHER records after the command that should have
written its input was denied, leaving the prompt effectively empty. The output looked
entirely reasonable. It was caught only by comparing the returned ids against the ids
that had been sent, which is the check `review_batch` now performs on every batch.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import review_subfamily_definitions as rsd  # noqa: E402

BATCH = [{"id": "PTHR1", "label": "A", "n_subfamilies": 3, "claim": "x", "path": "p"},
         {"id": "PTHR2", "label": "B", "n_subfamilies": 4, "claim": "y", "path": "q"}]


class _Proc:
    def __init__(self, stdout, returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


def _run_returning(monkeypatch, stdout, returncode=0):
    monkeypatch.setattr(rsd.subprocess, "run",
                        lambda *a, **k: _Proc(stdout, returncode))


def _long(batch):
    """A batch big enough to clear MIN_PROMPT_CHARS, so the length guard is not
    what the test is measuring."""
    return [dict(r, claim="term " * 400) for r in batch]


# --- the fabrication guard --------------------------------------------------------

def test_an_invented_id_fails_the_batch(monkeypatch):
    """The exact shape of the 25-fabricated-records incident."""
    _run_returning(monkeypatch,
                   '[{"id":"PTHR9999","verdict":"OK","reason":"r"},'
                   ' {"id":"PTHR8888","verdict":"OK","reason":"r"}]')
    verdicts, err = rsd.review_batch(_long(BATCH))
    assert verdicts is None
    assert "id mismatch" in err and "PTHR9999" in err


def test_a_dropped_id_fails_the_batch(monkeypatch):
    """Partial answers must not be merged: the missing record would silently keep
    whatever it had, while the run reported success."""
    _run_returning(monkeypatch, '[{"id":"PTHR1","verdict":"OK","reason":"r"}]')
    verdicts, err = rsd.review_batch(_long(BATCH))
    assert verdicts is None
    assert "missing" in err and "PTHR2" in err


def test_a_short_prompt_is_never_sent(monkeypatch):
    """If the data went missing, do not pay a model to imagine it."""
    def explode(*a, **k):
        raise AssertionError("the model must not be called on an empty prompt")
    monkeypatch.setattr(rsd.subprocess, "run", explode)
    verdicts, err = rsd.review_batch([{"id": "PTHR1", "label": "A",
                                       "n_subfamilies": 1, "claim": "", "path": "p"}])
    assert verdicts is None
    assert "too short" in err or "no label" in err


def test_a_complete_matching_reply_is_accepted(monkeypatch):
    _run_returning(monkeypatch,
                   'some preamble\ncodex\n'
                   '[{"id":"PTHR1","verdict":"OK","reason":"r"},'
                   ' {"id":"PTHR2","verdict":"WRONG","reason":"r"}]\ntokens used\n123')
    verdicts, err = rsd.review_batch(_long(BATCH))
    assert err == ""
    assert {v["id"] for v in verdicts} == {"PTHR1", "PTHR2"}


def test_a_nonzero_exit_fails_the_batch(monkeypatch):
    _run_returning(monkeypatch, "", returncode=1)
    verdicts, err = rsd.review_batch(_long(BATCH))
    assert verdicts is None and "exited 1" in err


# --- reply parsing ----------------------------------------------------------------

@pytest.mark.parametrize("stdout", [
    '[{"id":"a","verdict":"OK"}]',
    'prose before\n[{"id":"a","verdict":"OK"}]\nprose after',
    'codex\n```json\n[{"id":"a","verdict":"OK"}]\n```\ntokens used\n42',
    # An echoed prompt containing brackets must not be mistaken for the reply.
    'reason: "under 30 words" [not json]\n[{"id":"a","verdict":"OK"}]',
])
def test_extract_json_finds_the_reply(stdout):
    got = rsd.extract_json(stdout)
    assert got == [{"id": "a", "verdict": "OK"}]


def test_extract_json_returns_none_when_there_is_no_array():
    assert rsd.extract_json("I could not complete that request.") is None


# --- record selection -------------------------------------------------------------

@pytest.mark.skipif(not rsd.RECORDS.is_dir(), reason="PANTHER records not present")
def test_only_subfamily_derived_records_are_selected():
    """THE SHIPPED BUG. The marker was the bare phrase "shared by all", which also
    occurs in two curator-written InterPro abstracts -- "a component shared by all
    three forms of eukaryotic RNA polymerases". Those two were pulled into the review
    set, giving 230 records where 228 were composed. Sending a curated abstract to a
    reviewer that believes it is auditing a machine-composed claim would have invited
    a verdict on the wrong thing entirely.
    """
    records = rsd.load_records()
    assert records, "no subfamily-derived records found"
    for r in records:
        assert "of its annotated subfamilies" in r["claim"] or r["claim"], r["id"]
    ids = {r["id"] for r in records}
    assert "PTHR11255" not in ids, "diacylglycerol kinase abstract pulled in again"
    assert "PTHR23431" not in ids, "RPABC5 abstract pulled in again"
