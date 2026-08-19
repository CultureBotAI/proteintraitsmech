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
  * Our own generated notes, EXCLUDING this drift, run 17,236 ASCII to 112 Greek. 111 of
    those are `Qnr/MfpA right-handed β-helix`, where the Greek is simply right. The 112th
    is worth naming rather than rounding away, because it is a β-LACTAM note this repair
    deliberately leaves alone: `Determinant → phenotype; GOB-family MBLs confer broad
    β-lactam resistance.` It is a different sentence, written by a different config, and
    changing it is a separate curation decision nobody has made.

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


def _walk_notes(node):
    """Every `notes` value anywhere in the document, at any depth.

    TOTAL BY CONSTRUCTION: anything that is not a dict or a list is ignored rather than
    descended into. That is what makes a malformed-but-parseable record safe -- the first
    version did `doc.get("causal_graphs")` and indexed whatever came back, so
    `causal_graphs: just a string` raised AttributeError out of `main()` and aborted an
    `--apply` sweep mid-way with records already written and no summary. The guard is this
    function's shape, not the `except` below it, which is why the except is unreachable.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "notes" and isinstance(value, str):
                yield value
            else:
                yield from _walk_notes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_notes(item)


def find_notes(text: str) -> int:
    """How many notes on this record ARE the drifted sentence -- found by PARSING.

    Independent of `FIX`, and broader in BOTH directions, which took a review to get right.

    Broader in PARSING: a note PyYAML folds across lines is invisible to a line-anchored
    regex and visible here. That much was in the first version.

    Broader in SCOPE, which was not. The first version walked `causal_graphs -> edges ->
    evidence` while `FIX` matches any `notes:` line in the file -- and `evidence` is ALSO a
    top-level slot on ProteinTraitRecord, carried by 78,667 records holding 170,577 notes,
    3,243 of them under this script's own default path. So the "finder" was narrower than
    the fixer over a 170k-note surface, in a script whose entire premise is the opposite,
    and it failed in both directions at once:

      * a drifted note under top-level `evidence:` gave `want == 0`, so the record was
        SILENTLY SKIPPED -- the exact outcome the docstring promises cannot happen;
      * a record with one under each gave `want=1, can=2`, and `can < want` let the sweep
        rewrite a note the finder had never seen or vetted.

    And `test_no_drifted_note_remains_in_the_corpus` calls this function, so the corpus
    certification inherited the blind spot -- #462 and #364's shape, reproduced inside the
    fix for it. Walking every `notes` key at any depth is the only version that is
    genuinely a superset of a whole-file regex.
    """
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return -1                       # unreadable; the caller strands it
    except Exception:                   # pragma: no cover - not reachable on this corpus
        return -1
    try:
        return sum(1 for note in _walk_notes(doc) if _collapse(note) == DRIFTED)
    except Exception:                   # pragma: no cover - `_walk_notes` is total
        # Belt and braces only. If this ever fires, a record shaped in some way the walk
        # cannot follow is UNREADABLE rather than clean -- never silently 0.
        return -1


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
    if can != want:
        # BOTH directions are a refusal. `can < want` is the finder seeing a note the
        # rewrite cannot address -- folded, or on a line shape this does not match.
        # `can > want` is the rewrite seeing one the finder did not, which after the scope
        # fix should be impossible: the finder walks every `notes` key at any depth and the
        # fixer matches a subset of those lines. Impossible is not the same as unchecked,
        # and the version of this script that shipped to review had exactly that hole.
        cause = "unrewritable" if can < want else "unvetted"
        return None, 0, {cause: abs(want - can)}
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
        print("  unvetted      the rewrite matches more notes than the finder saw")
        print("  unreadable    the record does not parse, or is shaped so the walk cannot "
              "follow it")
        return 1
    if not args.apply and not limited:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
