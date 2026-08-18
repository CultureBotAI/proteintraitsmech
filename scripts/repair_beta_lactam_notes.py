#!/usr/bin/env python3
r"""Restore the ASCII spelling in the serine-hydrolysis note on 4,664 records (#466).

`promote_family_drafts` emits, and has emitted since #194:

    The active site carries out the serine beta-lactam hydrolysis mechanism.

4,664 records on disk say `serine β-lactam hydrolysis`. A config string was edited without
a `--repromote`, so the corpus and its generator disagree — found by #408's reproduction
gate once it stopped excluding multi-config records (#465). It is 4,664 of the 5,074
records that gate reports as drifted: 92% of #408 in one sentence.

WHY ASCII AND NOT β, WHICH IS THE CURATION CALL
------------------------------------------------
Measured, because "which spelling is right" reads like a style preference and is not:

  * `aro.obo`, the release these notes describe, uses `beta-lactam` **11,293** times and
    `β-lactam` **twice**.
  * The promoter emits ASCII at all four sites that mention the mechanism.
  * Our own generated notes, EXCLUDING this drift, run 17,236 ASCII to 112 Greek — and the
    112 are `Qnr/MfpA right-handed β-helix`, a different string where the Greek is right.

β looked like the majority only because the drift itself is 4,664 records.

And the field decides nothing about quotation fidelity either way: this is a `notes:`, not
a `snippet:`. Snippets must be verbatim in the source they cite and are gated by
`audit_snippets`; notes are our own prose about it. The promoter's configs are full of β
inside quoted literature snippets, and NONE of that is in scope here — which is exactly why
this matches one exact sentence rather than substituting β globally. A blanket rewrite
would corrupt 111 β-helix notes and every quoted abstract in the ARO configs.

ONE WRITER FOR THE STRING
-------------------------
The replacement is imported from `promote_family_drafts.SERINE_HYDROLYSIS_NOTE`, which was
an inline default until this change. Two copies of one sentence is how the drift happened;
a repair carrying a third copy would only set up the next one. If the promoter's wording
changes, this script writes the new wording or fails to import — it cannot silently
disagree.

FINDER AND FIXER ARE DIFFERENT, AND THE FINDER IS THE BROADER ONE (#462)
-------------------------------------------------------------------------
The fixer is a line-anchored regex: the note is a single-line scalar in all 4,664 records,
so a line rewrite preserves formatting exactly and avoids the re-dump churn the sibling
repairs accept.

The finder PARSES the record and compares the collapsed note text, so it sees a note PyYAML
has folded across lines — the case a raw-text pattern cannot see, and the one that made
#364's prefilter skip 28 records while the verification scan agreed with the miss because
it shared the prefilter.

Measured before relying on it: raw and parsed agree today at 4,664 notes in 4,664 records,
0 folded. So the fixer is sufficient NOW, and a folded note appearing later is reported as
stranded instead of silently skipped.

Dry-run by default; `--apply` writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from promote_family_drafts import SERINE_HYDROLYSIS_NOTE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

# The drifted text, as the only thing this script recognises. Written out rather than
# derived from SERINE_HYDROLYSIS_NOTE by a β/beta substitution: deriving it would make the
# script rewrite whatever the promoter later says with the Greek letter swapped, which is a
# licence to touch sentences nobody has looked at.
DRIFTED = "The active site carries out the serine β-lactam hydrolysis mechanism."

# THE FIXER. Line-anchored, and it keeps the record's own indentation.
FIX = re.compile(r"^(?P<indent>[ \t]*)notes:[ \t]*" + re.escape(DRIFTED) + r"[ \t]*$", re.M)

# Cheap gate before parsing 7,452 records; deliberately weaker than either pattern, so it
# can only ever admit more than it should. `β-lactam hydrolysis` and not the whole sentence,
# because a prefilter that repeats the fixer's precision is the #364 defect.
PREFILTER = "lactam hydrolysis"


def _collapse(text: str) -> str:
    return " ".join((text or "").split())


def find_notes(text: str) -> int:
    """How many notes on this record ARE the drifted sentence -- found by PARSING.

    Independent of `FIX`, and broader: a note PyYAML folds across lines is invisible to a
    line-anchored regex and visible here. `repair_self_referential_notes` learned this the
    expensive way -- one pattern serving as both finder and fixer reported 11 unfixable
    notes as "nothing to do".
    """
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return -1                       # unreadable; the caller strands it
    return sum(1 for graph in doc.get("causal_graphs") or []
               for edge in graph.get("edges") or []
               for ev in edge.get("evidence") or []
               if _collapse(ev.get("notes")) == DRIFTED)


def repair_record(text: str) -> tuple[str | None, int, dict[str, int]]:
    """(new text or None, notes rewritten, {cause: count} for what it could NOT do).

    The cause map rather than a count, following #462's third round: `main` must not have
    to enumerate the reasons it knows about, or the one it does not know about is computed
    and dropped.
    """
    want = find_notes(text)
    if want < 0:
        return None, 0, {"unreadable": 1}
    can = len(FIX.findall(text))
    if not want:
        return None, 0, {}
    if can < want:
        # The finder saw a note the rewrite cannot address -- folded, or on a line shape
        # this does not match. Reported, never skipped.
        return None, 0, {"unrewritable": want - can}
    out = FIX.sub(lambda m: f"{m.group('indent')}notes: {SERINE_HYDROLYSIS_NOTE}", text)
    return out, can, {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write; default is a dry run")
    ap.add_argument("--path", default=str(ARO_DIR))
    ap.add_argument("--limit", type=int, default=0, help="stop after N records (the canary)")
    ap.add_argument("--show", type=int, default=10)
    args = ap.parse_args()

    paths = sorted(Path(args.path).rglob("*.yaml"))
    if not paths:
        print(f"FAIL: no records under {args.path}")
        return 1

    repaired = notes = examined = 0
    stranded: list[tuple[str, dict[str, int]]] = []
    limited = False
    for i, path in enumerate(paths):
        text = path.read_text(encoding="utf-8")
        if PREFILTER not in text:
            continue
        examined += 1
        out, n, cannot = repair_record(text)
        if cannot:
            stranded.append((path.name, cannot))
            detail = ", ".join(f"{k} {c}" for c, k in sorted(cannot.items()))
            print(f"  STRANDED {path.name}: {detail}")
        if out is None:
            continue
        repaired += 1
        notes += n
        if repaired <= args.show:
            print(f"  {'wrote' if args.apply else 'would write'}  {path.name}  ({n} note(s))")
        if args.apply:
            path.write_text(out, encoding="utf-8")
        if args.limit and repaired >= args.limit:
            print(f"\n--limit {args.limit} reached; {len(paths) - i - 1:,} record(s) NOT "
                  f"examined. The counts below are not a survey, and the stranded check "
                  f"covers only what was scanned.")
            limited = True
            break

    print(f"\nrecords examined: {examined:,}")
    print(f"records repaired: {repaired:,}   notes rewritten: {notes:,}")
    if not examined and not limited:
        # #418/#432/#469: a sweep that read nothing must not exit with the code that means
        # "clean".
        print(f"FAIL: no record under {args.path} mentions {PREFILTER!r}; this examined "
              f"nothing and cannot certify anything.")
        return 1
    if stranded:
        print(f"\nFAIL: {len(stranded):,} record(s) carry the drifted note in a form this "
              f"cannot rewrite. They are unexamined, not clean.")
        print("  unrewritable  the note is folded or otherwise not a single-line scalar")
        print("  unreadable    the record does not parse at all")
        return 1
    if not args.apply and not limited:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
