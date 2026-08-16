#!/usr/bin/env python3
r"""Rewrite the notes that call a record its own is_a ancestor (#364).

`promote_family_drafts._drug_assertion` walks `is_a` from the record upward, with the
RECORD ITSELF first, and wrote the same note whichever step matched:

    Asserted on ARO:3004574 (Acinetobacter baumannii AbaQ), an is_a ancestor of this
    record's ARO:3004574; inherited by this variant.

A term is not its own `is_a` ancestor — `aro.obo` gives ARO:3004574 `is_a ARO:0000031` and
nothing else — and the relation is asserted ON the record, not inherited by it. 184 such
notes were on disk across 162 records.

WHY THIS AND NOT `fix_resistance_drug_edges`. That script owns the corrected wording and
has written it for 593 records, but it only selects edges whose subject is `resistance` and
whose object starts with `drug`. These notes sit on `determinant -> drug0` edges, which it
never looks at — it reports nothing to do. Widening its selection would put 12,581
already-correct edges back in scope for no reason.

WHY NOT RE-PROMOTE. The promoter is fixed in the same commit, so re-promotion would also
produce the right note — but it rewrites the whole graph, and #408 measured that 449
promoter-owned records no longer reproduce from their config. Re-promoting to fix a note
would drag that unrelated drift into the same diff.

THE INVARIANT, and it is checked rather than asserted: the text this writes must be
byte-identical to what the repaired `_drug_assertion` now emits for the same term. One
writer's output, reproduced by the repairer, or the next promotion re-introduces a
difference.

Dry-run by default; `--apply` writes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

# The self-referential form, with the two ids captured so the equality is the CONDITION
# rather than an assumption. A note naming a genuine ancestor is left alone.
#
# `(?P<name>.*)` AND NOT `[^)]*`: 415 of aro.obo's 8,601 names contain a close-paren --
# "Outer Membrane Porin (Opr)", "16S rRNA methyltransferase (A1408)", "AAC(3)". Against
# `[^)]*` the name group stops at the inner paren, the fixed tail can no longer match, and
# `fullmatch` fails. That silently skipped 11 notes across 7 records while the tool printed
# "records repaired: 0" -- a miss indistinguishable from nothing to do, which is the #431
# lesson this file's docstring invokes and then reproduced.
#
# Greedy `.*` is safe because the tail is FIXED and anchored by fullmatch: the only way to
# satisfy it is for the name to end at the last `), an is_a ancestor of this record's`.
SELF_REF = re.compile(
    r"Asserted on (?P<a>ARO:\d+) \((?P<name>.*)\), an is_a ancestor of this record's "
    r"(?P<b>ARO:\d+); inherited by this variant\. "
    r"CARD/ARO release in data/raw/aro/aro\.obo\.")

# DETECTION, independent of the rewrite pattern. `repair_record` used `fix_note` for both,
# so a note the rewrite could not parse was reported as "no self-referential note" rather
# than as stranded -- and the corpus test used `fix_note` as its oracle too, so the gate
# was blind to exactly the notes that survived. One pattern must not be both the finder and
# the fixer.
LOOKS_SELF_REF = re.compile(
    r"Asserted on (ARO:\d+) \(.*\), an is_a ancestor of this record's (ARO:\d+);")


def looks_self_referential(note: str) -> bool:
    """True if this note calls a record its own ancestor, however it is worded."""
    m = LOOKS_SELF_REF.search(" ".join((note or "").split()))
    return bool(m and m.group(1) == m.group(2))


def corrected(term: str, name: str) -> str:
    """The direct-assertion note. Must match `_drug_assertion`'s branch byte for byte."""
    return (f"Asserted directly on {term} ({name}) in the CARD/ARO release in "
            f"data/raw/aro/aro.obo.")


def fix_note(note: str) -> str | None:
    """The corrected note, or None if this one is not self-referential."""
    m = SELF_REF.fullmatch(" ".join((note or "").split()))
    if not m or m.group("a") != m.group("b"):
        return None
    return corrected(m.group("a"), m.group("name"))


def _graph_block(text: str) -> tuple[int, int] | None:
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith("causal_graphs:")), None)
    if start is None:
        return None
    for i in range(start + 1, len(lines)):
        if lines[i][:1].strip() and not lines[i].startswith(("-", " ")):
            return start, i
    return start, len(lines)


def _dump(obj) -> str:
    """Byte-for-byte the promoter's emitter (`promote_family_drafts._dump`)."""
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100,
                          default_flow_style=False)


def _norm(text: str) -> str:
    return " ".join(text.split())


def repair_record(text: str) -> tuple[str | None, str, int]:
    """(new text or None, reason, notes fixed)."""
    span = _graph_block(text)
    if span is None:
        return None, "no causal_graphs block", 0
    lines = text.splitlines(keepends=True)
    block = "".join(lines[span[0]:span[1]])
    try:
        doc = yaml.safe_load(block)
    except Exception as exc:                                    # pragma: no cover
        return None, f"unparseable: {exc}", 0

    # Found with the INDEPENDENT pattern, rewritten with the strict one. A note this
    # detects and cannot rewrite is stranded and said so, rather than silently skipped.
    hits = [ev for g in doc.get("causal_graphs") or []
            for e in g.get("edges") or []
            for ev in e.get("evidence") or []
            if looks_self_referential(ev.get("notes"))]
    if not hits:
        return None, "no self-referential note", 0
    unfixable = [ev for ev in hits if not fix_note(ev.get("notes"))]
    if unfixable:
        return None, (f"{len(unfixable)} self-referential note(s) the rewrite pattern "
                      f"cannot parse"), len(unfixable)
    # Whitespace-collapsed, not byte-for-byte: the corpus holds blocks re-wrapped by an
    # earlier repair with a hand-rolled folder, and byte equality would refuse those --
    # the mistake #454's first version made, which stranded every record it was for.
    if _norm(_dump(doc)) != _norm(block):
        return None, f"re-dump would change content -- AND CARRIES {len(hits)} NOTE(S)", len(hits)

    for ev in hits:
        ev["notes"] = fix_note(ev["notes"])
    return ("".join(lines[:span[0]]) + _dump(doc) + "".join(lines[span[1]:]),
            "repaired", len(hits))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="stop after N records (canary)")
    ap.add_argument("--path", default=str(ARO_DIR))
    args = ap.parse_args()

    paths = sorted(Path(args.path).rglob("*.yaml"))
    fixed = notes = stranded = 0
    limited = False
    for i, path in enumerate(paths):
        text = path.read_text(encoding="utf-8")
        # NO SUBSTRING PREFILTER. There was one -- `"an is_a ancestor of this record" not
        # in text` -- and PyYAML folds that very phrase across a line break, so it was
        # absent from the raw text of 28 records that contained the note. They were skipped
        # before anything looked at them, and the verification scan used the SAME prefilter,
        # so both agreed on "0 remain" while 31 notes survived.
        #
        # That is the third form of one mistake in this file: `[^)]*` in the rewrite, the
        # rewrite doubling as the detector, and now the prefilter. All three are the same
        # error -- reasoning about folded YAML as flat text -- and all three were invisible
        # because the check shared the blind spot (#462). Parse every record; the walk is
        # 7.4k files and costs seconds.
        out, reason, n = repair_record(text)
        if out is None:
            if n:
                stranded += 1
                print(f"  STRANDED {path.name}: {reason}")
            continue
        fixed += 1
        notes += n
        print(f"  {'wrote' if args.apply else 'would write'}  {path.name}  ({n} note(s))")
        if args.apply:
            path.write_text(out, encoding="utf-8")
        if args.limit and fixed >= args.limit:
            print(f"\n--limit {args.limit} reached; {len(paths) - i - 1:,} record(s) not "
                  f"examined, so the counts below are not a survey.")
            limited = True
            break

    print(f"\nrecords repaired: {fixed:,}   notes rewritten: {notes:,}")
    if stranded:
        # A record that needs the fix and cannot take it must not be filed under the same
        # silence as one that needs nothing (#431's lesson).
        print(f"FAIL: {stranded:,} record(s) carry a self-referential note this cannot "
              f"rewrite. Fix by hand; `just audit-graphs` will not see them either.")
        return 1
    if not args.apply and not limited:
        print("\ndry run -- nothing written. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
