"""`seed_panther.compose_definition` must produce grammatical prose for every
present/absent combination of its annotation clauses.

The bug this guards against shipped in 1,707 records. The clause leads were
"Members are annotated with the molecular function" / "and participate in" /
"and localise to", assembled into a list of `bits` that were joined with a space —
*after each bit already ended in a period*. The two "and" leads were written as if
they continued the molecular-function sentence, but nothing ever continued: every
record with a biological-process or cellular-component annotation got

    ... profile HMM PTHR36562. and localise to nucleus, ...

The composer now emits each clause as a standalone sentence, which is correct for
all eight MF/BP/CC combinations without any conditional grammar. These tests assert
the property (no sentence begins lowercase) rather than the exact wording, so a
future rewording is free to change the prose but not to reintroduce the defect.

`scripts/repair_panther_definitions.py` fixed the records already on disk.
"""

from __future__ import annotations

import itertools
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from seed_panther import compose_definition  # noqa: E402

PANTHER_DIR = REPO / "data" / "traits" / "sequence" / "family" / "panther"

MF = [("catalytic activity", "GO:0003824")]
BP = [("metabolic process", "GO:0008152")]
CC = [("nucleus", "GO:0005634")]

# A sentence boundary followed by a lowercase word. `sn-glycerol` and friends never
# follow a period, so this does not fire on the chemistry in family names.
LOWERCASE_AFTER_PERIOD = re.compile(r"\.\s+([a-z])")


def _ann(mf=(), bp=(), cc=(), classes=()):
    return {"mf": list(mf), "bp": list(bp), "cc": list(cc),
            "classes": list(classes), "pathways": []}


@pytest.mark.parametrize(
    "mf,bp,cc,classes",
    list(itertools.product([(), MF], [(), BP], [(), CC], [(), ["hydrolase"]])),
)
def test_no_sentence_starts_lowercase(mf, bp, cc, classes):
    """All 16 combinations of the four optional clauses read as prose."""
    out = compose_definition("PTHR00001", "SOME FAMILY", _ann(mf, bp, cc, classes))
    bad = LOWERCASE_AFTER_PERIOD.search(out)
    assert not bad, f"sentence starts lowercase ({bad.group(1)!r}) in: {out}"


@pytest.mark.parametrize("mf,bp,cc", [((), BP, ()), ((), (), CC), ((), BP, CC)])
def test_clauses_stand_alone_without_the_molecular_function_clause(mf, bp, cc):
    """The regression proper: BP/CC with no MF used to emit a dangling "and"."""
    out = compose_definition("PTHR00001", "SOME FAMILY", _ann(mf, bp, cc))
    assert ". and " not in out, out
    assert out.endswith("."), out


def test_every_clause_present_is_stated():
    out = compose_definition("PTHR00001", "SOME FAMILY",
                             _ann(MF, BP, CC, ["hydrolase"]))
    for expected in ("hydrolase", "catalytic activity", "metabolic process", "nucleus"):
        assert expected in out, f"{expected!r} dropped from: {out}"


@pytest.mark.skipif(not PANTHER_DIR.is_dir(), reason="PANTHER records not present")
def test_no_composed_record_still_carries_the_dangling_and():
    """The corpus itself, so a re-seed from an unfixed checkout cannot slip back in."""
    offenders = [p.name for p in PANTHER_DIR.rglob("*.yaml")
                 if ". and participate in" in (t := p.read_text(encoding="utf-8"))
                 or ". and localise to" in t]
    assert offenders == [], f"{len(offenders)} records still malformed: {offenders[:5]}"
