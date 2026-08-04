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

# The corpus already records each GO term's aspect as its trait_category, so the
# function edges can be split without a second GO parse. Phase 6's held-out test
# showed the aspects do not deserve equal trust — molecular-function rules
# replicate across organisms, localisation rules largely do not.
KIND_BY_CATEGORY = {
    "FUNC_MOLECULAR_FUNCTION": "trait-implies-molecular-function",
    "FUNC_ENZYMATIC_ACTIVITY": "trait-implies-enzymatic-activity",
    "FUNC_PATHWAY": "trait-implies-biological-process",
    "FUNC_LOCALIZATION": "trait-implies-localization",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-support", type=int, default=30, help="min proteins carrying A")
    ap.add_argument("--min-conf", type=float, default=0.9)
    ap.add_argument("--min-lift", type=float, default=3.0)
    ap.add_argument("--min-balanced-conf", type=float, default=0.0,
                    help="drop rules whose organism-balanced confidence (each "
                         "proteome one vote) falls below this. 0.0 = report the "
                         "balanced figure but gate on raw confidence only.")
    ap.add_argument("--min-organism-support", type=int, default=5,
                    help="carriers of the antecedent needed for an organism to "
                         "vote in the balanced confidence")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--out")
    ap.add_argument("--emit-overlay",
                    help="write the passing cross-axis rules as a data/equivalence TSV "
                         "(biolink:related_to; both endpoints are corpus trait records)")
    args = ap.parse_args()

    idx = json.loads(INDEX.read_text(encoding="utf-8"))     # {trait: [axis, cat]}

    def axis(t):
        return (idx.get(t) or ["", ""])[0]

    def cat(t):
        return (idx.get(t) or ["", ""])[1]

    rows = [json.loads(ln) for ln in JSONL.open(encoding="utf-8")]
    N = len(rows)
    # Provenance stamped onto every emitted edge. Derived from the matrix rather
    # than hardcoded — these rules were human-only through phase 5 and the
    # relation_source has to say which proteomes actually support them.
    orgs = collections.Counter(r.get("taxon_label") or "?" for r in rows)
    matrix_src = "Swiss-Prot(" + ",".join(
        o.split(" (")[0] for o, _ in orgs.most_common()) + ")"
    supp = collections.Counter()
    co = collections.Counter()
    org_of = {}
    for i, r in enumerate(rows):
        # A protein's trait set: its signature traits plus its GO / EC as trait
        # CURIEs. Endpoints must be *corpus records* — r["traits"] is already
        # index-filtered by the profile builder but r["go"] / r["ec"] are raw
        # UniProt annotations, so without `t in idx` a GO term the knowledge base
        # has no record for could become an overlay endpoint and dangle.
        ts = set(r["traits"]) | set(r["go"]) | {f"EC:{e}" for e in r["ec"]}
        ts = {t for t in ts
              if t.split(":")[0] in (SEQ_PREF + STRUCT_PREF + FUNC_PREF) and t in idx}
        r["_ts"] = ts
        org_of[i] = r.get("taxon_label") or "?"
        for t in ts:
            supp[t] += 1
        for a, b in itertools.permutations(ts, 2):
            co[(a, b)] += 1

    def candidates(a_pref, b_pref):
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
        return out

    seq_struct = candidates(SEQ_PREF, STRUCT_PREF)
    struct_func = candidates(STRUCT_PREF + SEQ_PREF, FUNC_PREF)

    # --- organism-balanced confidence -------------------------------------
    # Raw confidence is dominated by whichever proteomes are largest: this
    # matrix is 76% vertebrate by protein count, so a rule that holds in human
    # and mouse and fails everywhere else still clears threshold. Balanced
    # confidence averages the per-organism confidences over the organisms where
    # the antecedent is actually testable, giving each proteome one vote.
    # Counted only for candidate rules — a full per-organism co-occurrence table
    # would be several GB.
    cand_pairs = {(a, b) for _c, _l, _n, a, b in seq_struct + struct_func}
    by_ante: dict = collections.defaultdict(set)
    for a, b in cand_pairs:
        by_ante[a].add(b)
    o_supp: dict = collections.defaultdict(collections.Counter)
    o_co: dict = collections.defaultdict(collections.Counter)
    for i, r in enumerate(rows):
        tax, ts = org_of[i], r["_ts"]
        if tax == "?":
            continue                    # untaxoned rows must not vote (issue #43)
        for a in ts & by_ante.keys():
            o_supp[tax][a] += 1
            for b in by_ante[a]:
                if b in ts:
                    o_co[tax][(a, b)] += 1
    organisms = sorted({t for t in org_of.values() if t != "?"})
    untaxoned = sum(1 for t in org_of.values() if t == "?")
    if untaxoned:
        print(f"warning: {untaxoned:,} profiles have no organism and are excluded "
              f"from the balanced confidence", file=sys.stderr)
    # a floor of 0 would admit organisms with no carriers at all and divide by
    # zero (issue #42)
    vote_floor = max(1, args.min_organism_support)

    def balanced(a, b):
        """(mean per-organism confidence, n organisms it was testable in)."""
        confs = [o_co[t][(a, b)] / o_supp[t][a] for t in organisms
                 if o_supp[t][a] >= vote_floor]
        return (sum(confs) / len(confs), len(confs)) if confs else (0.0, 0)

    unjudged = 0

    def keep(cands):
        nonlocal unjudged
        out = []
        for conf, lift, c, a, b in cands:
            cb, k = balanced(a, b)
            if not k:
                # no proteome carries the antecedent often enough to vote. Keep
                # the rule — an unjudgeable rule has not failed — but count it,
                # so a run with a gate set cannot quietly report rules the gate
                # never actually examined.
                unjudged += 1
            elif cb < args.min_balanced_conf:
                continue
            out.append((conf, lift, c, a, b, cb, k))
        out.sort(reverse=True)
        return out

    dropped = len(seq_struct) + len(struct_func)
    seq_struct, struct_func = keep(seq_struct), keep(struct_func)
    dropped -= len(seq_struct) + len(struct_func)

    L = [f"matrix: {matrix_src}",
         f"proteins: {N:,} | trait pairs evaluated: {len(co):,} | "
         f"thresholds: support≥{args.min_support}, conf≥{args.min_conf}, lift≥{args.min_lift}\n",
         f"organism-balanced: conf≥{args.min_balanced_conf} averaged over organisms "
         f"with ≥{vote_floor} carriers of the antecedent "
         f"({dropped:,} rules dropped; {unjudged:,} kept unjudged — no proteome "
         f"carried the antecedent often enough to vote)\n",
         f"## Sequence signature → structure fold ({len(seq_struct):,} rules)",
         "_\"this sequence feature encodes this fold\" — P(fold | signature)_\n",
         "| sequence signature | → structure fold | conf | balanced | orgs | lift | n |",
         "|---|---|--:|--:|--:|--:|--:|"]
    for conf, lift, c, a, b, cb, k in seq_struct[:args.top]:
        L.append(f"| {a} | {b} | {conf:.2f} | {cb:.2f} | {k} | {lift:.0f}× | {c} |")
    L += [f"\n## Sequence / structure trait → function ({len(struct_func):,} rules)",
          "", "By GO aspect — the held-out-organism test (phase 6) showed these do "
          "not all deserve the same trust:", "",
          "| aspect | rules |", "|---|--:|"]
    aspects = collections.Counter(KIND_BY_CATEGORY.get(cat(b), "other")
                                  for *_x, b, _cb, _k in struct_func)
    for k_, v_ in aspects.most_common():
        L.append(f"| {k_} | {v_:,} |")
    L += ["", "| trait | → function (GO/EC) | conf | balanced | orgs | lift | n |",
          "|---|---|--:|--:|--:|--:|--:|"]
    for conf, lift, c, a, b, cb, k in struct_func[:args.top]:
        L.append(f"| {a} ({axis(a).lower()}) | {b} | {conf:.2f} | {cb:.2f} | {k} "
                 f"| {lift:.0f}× | {c} |")
    # summary: how often a sequence signature perfectly predicts a fold
    perfect = sum(1 for conf, *_ in seq_struct if conf >= 0.99)
    L.insert(1, f"**{len(seq_struct):,} sequence→fold rules ≥{args.min_conf} confidence; "
             f"{perfect:,} at ≥0.99 (a signature that essentially always encodes one fold).**\n")

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)

    if args.emit_overlay:
        # Materialise the passing cross-axis rules as a relate-only equivalence
        # overlay. Both endpoints are corpus trait records (they came from the
        # trait index); cross-axis → biolink:related_to, never a merge. The
        # empirical confidence / lift / support live in relation_source.
        seen, edges = set(), []
        unmapped: dict = collections.Counter()
        for kind, rr in (("seq-encodes-fold", seq_struct), (None, struct_func)):
            for conf, lift, c, a, b, cb, k in rr:
                if (a, b) in seen:
                    continue
                seen.add((a, b))
                # Function edges are split by GO aspect: phase 6 showed
                # molecular-function edges replicate across organisms in a way
                # cellular-component edges do not, so a consumer has to be able
                # to tell them apart without re-deriving the aspect.
                if kind:
                    this = kind
                else:
                    this = KIND_BY_CATEGORY.get(cat(b))
                    if this is None:
                        # falling back to the undifferentiated kind is exactly
                        # what this split exists to remove — say so rather than
                        # silently reintroducing it
                        unmapped[cat(b) or "(no category)"] += 1
                        this = "trait-implies-function"
                src = (f"{this}|conf={conf:.2f}|balanced={cb:.2f}|organisms={k}"
                       f"|lift={lift:.0f}x|n={c}|{matrix_src}")
                edges.append((a, "biolink:related_to", b, src))
        edges.sort()
        outp = Path(args.emit_overlay)
        outp.parent.mkdir(parents=True, exist_ok=True)
        with outp.open("w", encoding="utf-8") as fh:
            fh.write("subject\tpredicate\tobject\trelation_source\n")
            for e in edges:
                fh.write("\t".join(e) + "\n")
        if unmapped:
            print(f"warning: {sum(unmapped.values()):,} function edges fell back to "
                  f"the undifferentiated `trait-implies-function` kind — add these "
                  f"categories to KIND_BY_CATEGORY: "
                  f"{', '.join(f'{k} ({v})' for k, v in unmapped.most_common())}",
                  file=sys.stderr)
        try:                       # --emit-overlay may point anywhere on disk
            shown = outp.relative_to(REPO_ROOT)
        except ValueError:
            shown = outp
        print(f"\nwrote {len(edges):,} cross-axis co-occurrence edges → {shown}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
