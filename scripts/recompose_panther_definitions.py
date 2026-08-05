#!/usr/bin/env python3
"""Re-rank the GO terms shown in composed PANTHER definitions (#152).

A composed definition shows at most three GO terms per aspect. Which three was
decided by list order: PANTHER's own for a family's row, and CURIE sort order for
the subfamily consensus, where a set has no order and something deterministic was
needed. Sorting for determinism quietly became a decision about content -- the three
shown were the three lowest GO ids, which tracks when a term was minted, not how much
it says. Across the 228 records in #154 the cap discarded 3,130 agreed-on terms
chosen that way.

`go_hierarchy.GoRanker` now drops terms that are `is_a` ancestors of another term in
the same list -- "catalytic activity" says nothing beside "exonuclease activity" --
and orders what remains most-specific-first. The seeder composes that way from now
on; this brings the records already written into line.

The effect is mostly to make the cap stop binding rather than to swap one term for
another: pruning removes redundant ancestors, so fewer categories have more than
three terms left to choose from.

Gated on exact match against the UNRANKED composition, so a record a curator has
touched no longer matches and is skipped. In-place edit, so it writes directly
rather than through write_record (#148). Dry-run by default.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from go_hierarchy import GO_OBO, GoRanker  # noqa: E402
from seed_panther import (  # noqa: E402
    _UNNAMED, OUT_DIR, RAW, compose_definition, compose_from_subfamilies,
    has_annotations, parse_annotations, subfamily_consensus,
)

_IDENT = re.compile(r"^identifier: PANTHER:(\S+)\s*$", re.M)
_LABEL = re.compile(r"^label:[ \t]*(.*)$", re.M)
_DEF = re.compile(r"^definition: >-\n  (.*)$", re.M)
_SRC = re.compile(r"^definition_source: (.*)$", re.M)

FAMILY_MARK = "(composed from the family name and its GO"
SUBFAMILY_MARK = "annotations shared by all of its annotated subfamilies"


def _record_label(text: str) -> str | None:
    m = _LABEL.search(text)
    if not m:
        return None
    raw = m.group(1).strip()
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return raw


def _collapse(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    for needed in (RAW, GO_OBO):
        if not needed.exists():
            print(f"missing {needed}", file=sys.stderr)
            return 2
    ranker = GoRanker()
    print(f"GO terms indexed: {len(ranker.parents):,}", file=sys.stderr)

    raw = {}
    for line in RAW.open(encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if p[0].strip() and ":SF" not in p[0]:
            raw[p[0].strip()] = p
    consensus = subfamily_consensus()

    changed = unchanged = skipped = already = 0
    terms_before = terms_after = 0
    for path in sorted(OUT_DIR.rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        m, sm, dm = _IDENT.search(text), _SRC.search(text), _DEF.search(text)
        if not (m and sm and dm):
            continue
        pid, src, current = m.group(1), sm.group(1), dm.group(1)
        is_family = FAMILY_MARK in src
        is_sub = SUBFAMILY_MARK in src
        if not (is_family or is_sub):
            continue                      # curated InterPro abstract; not ours
        parts = raw.get(pid)
        if parts is None:
            skipped += 1
            continue
        label = (parts[1] if len(parts) > 1 else "").strip()
        if label.upper() in _UNNAMED:
            label = _record_label(text) or label

        if is_sub:
            hit = consensus.get(pid)
            if hit is None:
                skipped += 1
                continue
            agreed, n_sub = hit
            old = _collapse(compose_from_subfamilies(pid, label, agreed, n_sub))
            new = _collapse(compose_from_subfamilies(pid, label, agreed, n_sub, ranker))
            counted = agreed
        else:
            ann = parse_annotations(parts)
            if not has_annotations(ann):
                continue                  # a name-only stub has no terms to rank
            old = _collapse(compose_definition(pid, label, ann))
            new = _collapse(compose_definition(pid, label, ann, ranker))
            counted = ann

        if old == new:
            unchanged += 1
            continue
        if old != current:
            # Distinguish "a previous run already did this" from "a curator changed
            # it". Both leave `old != current`, but lumping them together made a
            # re-run report 1,569 records as edited-since, which reads as damage.
            if new == current:
                already += 1
            else:
                skipped += 1
            continue
        for key in ("mf", "bp", "cc"):
            terms_before += min(3, len(counted[key]))
            terms_after += min(3, len(ranker.rank(counted[key])))
        if args.apply:
            path.write_text(text.replace(old, new), encoding="utf-8")
        changed += 1
        if args.limit and changed >= args.limit:
            break

    print(f"{'recomposed' if args.apply else 'would recompose'}: {changed:,}")
    print(f"  already identical after ranking: {unchanged:,}")
    if already:
        print(f"  already recomposed by a prior run: {already:,}")
    if skipped:
        print(f"  skipped (edited since, or no source row): {skipped:,}")
    print(f"  GO terms shown in changed records: {terms_before:,} -> {terms_after:,}")
    if args.limit and changed >= args.limit:
        print(f"  PARTIAL: stopped at --limit {args.limit}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
