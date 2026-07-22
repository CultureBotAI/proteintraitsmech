#!/usr/bin/env python3
"""Cross-axis trait correlations (issue #7, phase 3).

Answers the issue's question — "do certain sequence features always encode certain
structural traits?" — plus the SEQUENCE/STRUCTURE → FUNCTION implications, from the
protein×trait matrix `data/profiles/profiles.jsonl`.

For every ordered trait pair (A → B) that co-occurs on the profiled proteins it
computes support(A), confidence P(B|A), and lift P(B|A)/P(B), then reports the
strongest **cross-axis** implications:
  • SEQUENCE signature → STRUCTURE fold  (a sequence feature that encodes a fold)
  • SEQUENCE / STRUCTURE trait → FUNCTION (GO/EC)  (structure/sequence → function)

Uses the corpus trait index for each trait's axis. Read-only; prints a markdown
report (optionally --out). Stdlib-only.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JSONL = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
INDEX = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"
# only signature/fold namespaces carry the SEQUENCE↔STRUCTURE encoding signal
SEQ_PREF = ("Pfam", "PROSITE", "SMART", "NCBIfam")          # sequence signatures
STRUCT_PREF = ("CATH",)                                      # structure folds
FUNC_PREF = ("GO", "EC")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-support", type=int, default=30, help="min proteins carrying A")
    ap.add_argument("--min-conf", type=float, default=0.9)
    ap.add_argument("--min-lift", type=float, default=3.0)
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--out")
    args = ap.parse_args()

    idx = json.loads(INDEX.read_text(encoding="utf-8"))     # {trait: [axis, cat]}

    def axis(t):
        return (idx.get(t) or ["", ""])[0]

    rows = [json.loads(l) for l in JSONL.open(encoding="utf-8")]
    N = len(rows)
    supp = collections.Counter()
    co = collections.Counter()
    for r in rows:
        # a protein's full trait set (signature traits + its GO/EC as trait CURIEs)
        ts = set(r["traits"]) | set(r["go"]) | {f"EC:{e}" for e in r["ec"]}
        ts = {t for t in ts if t.split(":")[0] in (SEQ_PREF + STRUCT_PREF + FUNC_PREF)}
        for t in ts:
            supp[t] += 1
        for a, b in itertools.permutations(ts, 2):
            co[(a, b)] += 1

    def rules(a_pref, b_pref):
        out = []
        for (a, b), c in co.items():
            if a.split(":")[0] not in a_pref or b.split(":")[0] not in b_pref:
                continue
            if supp[a] < args.min_support:
                continue
            conf = c / supp[a]
            lift = conf / (supp[b] / N) if supp[b] else 0
            if conf >= args.min_conf and lift >= args.min_lift:
                out.append((conf, lift, c, a, b))
        out.sort(reverse=True)
        return out

    seq_struct = rules(SEQ_PREF, STRUCT_PREF)
    struct_func = rules(STRUCT_PREF + SEQ_PREF, FUNC_PREF)

    L = [f"proteins: {N:,} | trait pairs evaluated: {len(co):,} | "
         f"thresholds: support≥{args.min_support}, conf≥{args.min_conf}, lift≥{args.min_lift}\n",
         f"## Sequence signature → structure fold ({len(seq_struct):,} rules)",
         "_\"this sequence feature encodes this fold\" — P(fold | signature)_\n",
         "| sequence signature | → structure fold | conf | lift | n |",
         "|---|---|--:|--:|--:|"]
    for conf, lift, c, a, b in seq_struct[:args.top]:
        L.append(f"| {a} | {b} | {conf:.2f} | {lift:.0f}× | {c} |")
    L += [f"\n## Sequence / structure trait → function ({len(struct_func):,} rules)",
          "| trait | → function (GO/EC) | conf | lift | n |", "|---|---|--:|--:|--:|"]
    for conf, lift, c, a, b in struct_func[:args.top]:
        L.append(f"| {a} ({axis(a).lower()}) | {b} | {conf:.2f} | {lift:.0f}× | {c} |")
    # summary: how often a sequence signature perfectly predicts a fold
    perfect = sum(1 for conf, *_ in seq_struct if conf >= 0.99)
    L.insert(1, f"**{len(seq_struct):,} sequence→fold rules ≥{args.min_conf} confidence; "
             f"{perfect:,} at ≥0.99 (a signature that essentially always encodes one fold).**\n")

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
