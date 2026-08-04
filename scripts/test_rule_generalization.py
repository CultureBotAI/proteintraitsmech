#!/usr/bin/env python3
"""Held-out-organism test for the cross-axis trait rules (issue #7, phase 6).

Phases 3-4 mined rules like "this sequence signature essentially always encodes
this fold" from a matrix of 20,000 reviewed *human* proteins. That leaves an
obvious question unanswered: **are the rules biology, or are they an artefact of
one proteome?** A rule that only holds in human is a description of the human
gene set, not of the sequence→structure→function coupling the knowledge base
claims to capture.

This trains on one organism and tests on the others. For each rule A→B mined on
the training organism it recomputes confidence P(B|A) on each held-out organism,
counting a rule as:

  replicated   — held-out confidence >= --replication-conf
  contradicted — the antecedent occurs often enough to judge, but confidence
                 falls below threshold
  untestable   — fewer than --min-test-support carriers of A in that organism
                 (usually a lineage-specific trait, not a failure of the rule)

Reporting `untestable` separately matters: silently dropping those inflates the
replication rate, because the rules most likely to be organism-specific are
exactly the ones with no carriers elsewhere.

Read-only; prints a markdown report (optionally --out). Stdlib-only.

Usage:
  python3 scripts/test_rule_generalization.py --train 9606
  python3 scripts/test_rule_generalization.py --train 9606 --out research/x.md
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JSONL = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
INDEX = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"

SEQ_PREF = ("Pfam", "PROSITE", "SMART", "NCBIfam")
STRUCT_PREF = ("CATH",)
FUNC_PREF = ("GO", "EC")


def trait_set(r: dict) -> set:
    ts = set(r["traits"]) | set(r["go"]) | {f"EC:{e}" for e in r["ec"]}
    return {t for t in ts if t.split(":")[0] in (SEQ_PREF + STRUCT_PREF + FUNC_PREF)}


def counts(rows: list) -> tuple:
    """(support, co-occurrence, n) over a set of profiles."""
    supp: dict = collections.Counter()
    co: dict = collections.Counter()
    for r in rows:
        ts = r["_ts"]
        for t in ts:
            supp[t] += 1
        for a in ts:
            for b in ts:
                if a != b:
                    co[(a, b)] += 1
    return supp, co, len(rows)


def mine(supp: dict, co: dict, n: int, a_pref: tuple, b_pref: tuple,
         min_support: int, min_conf: float, min_lift: float) -> list:
    out = []
    for (a, b), c in co.items():
        if a.split(":")[0] not in a_pref or b.split(":")[0] not in b_pref:
            continue
        if supp[a] < min_support:
            continue
        conf = c / supp[a]
        lift = conf / (supp[b] / n) if supp[b] else 0.0
        if conf >= min_conf and lift >= min_lift:
            out.append((a, b, conf, lift, c))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", default="9606",
                    help="NCBI taxon id to mine the rules on (default 9606, human)")
    ap.add_argument("--min-support", type=int, default=30, help="on the training organism")
    ap.add_argument("--min-conf", type=float, default=0.95)
    ap.add_argument("--min-lift", type=float, default=5.0)
    ap.add_argument("--min-test-support", type=int, default=5,
                    help="carriers of A needed in a held-out organism to judge the rule")
    ap.add_argument("--replication-conf", type=float, default=0.90,
                    help="held-out confidence at which a rule counts as replicated")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--out")
    args = ap.parse_args()

    rows = [json.loads(ln) for ln in JSONL.open(encoding="utf-8")]
    for r in rows:
        r["_ts"] = trait_set(r)

    by_taxon: dict = collections.defaultdict(list)
    untaxoned = 0
    for r in rows:
        taxon = (r.get("taxon") or "").replace("NCBITaxon:", "")
        if not taxon:
            # would otherwise form an unnamed pseudo-organism and be reported as
            # a held-out result (issue #40)
            untaxoned += 1
            continue
        by_taxon[taxon].append(r)
    if untaxoned:
        print(f"warning: {untaxoned:,} profiles have no taxon and are excluded",
              file=sys.stderr)
    labels = {t: (rs[0].get("taxon_label") or t) for t, rs in by_taxon.items()}

    train_key = args.train.replace("NCBITaxon:", "")
    if train_key not in by_taxon:
        print(f"training taxon {args.train} not in the matrix. Present: "
              f"{', '.join(f'{k} ({labels[k]}, {len(v):,})' for k, v in by_taxon.items())}",
              file=sys.stderr)
        return 2
    if len(by_taxon) < 2:
        print("matrix has a single organism — rebuild it with "
              "`just build-profiles --organisms --limit 25000 --jsonl-only --apply`",
              file=sys.stderr)
        return 2

    tr_supp, tr_co, tr_n = counts(by_taxon[train_key])
    seq_fold = mine(tr_supp, tr_co, tr_n, SEQ_PREF, STRUCT_PREF,
                    args.min_support, args.min_conf, args.min_lift)
    trait_func = mine(tr_supp, tr_co, tr_n, STRUCT_PREF + SEQ_PREF, FUNC_PREF,
                      args.min_support, args.min_conf, args.min_lift)

    L = ["# Held-out-organism replication of the cross-axis rules",
         "",
         f"trained on **{labels[train_key]}** ({tr_n:,} proteins), "
         f"support≥{args.min_support}, conf≥{args.min_conf}, lift≥{args.min_lift}; "
         f"a rule replicates at held-out confidence ≥{args.replication_conf} given "
         f"≥{args.min_test_support} carriers of the antecedent.",
         ""]

    # counts() is the dominant cost — build each held-out organism's tables once
    # rather than once per rule family (issue #39)
    held_counts = {taxon: counts(rs) for taxon, rs in by_taxon.items()
                   if taxon != train_key}

    overall = {}
    for family, rules in (("seq-encodes-fold", seq_fold),
                          ("trait-implies-function", trait_func)):
        L += [f"## {family} — {len(rules):,} rules mined", "",
              "| held-out organism | testable | replicated | contradicted | untestable | median conf |",
              "|---|--:|--:|--:|--:|--:|"]
        for taxon, rs in sorted(by_taxon.items(), key=lambda kv: -len(kv[1])):
            if taxon == train_key:
                continue
            supp, co, n = held_counts[taxon]
            rep = con = unt = 0
            confs, failures = [], []
            for a, b, tr_conf, _lift, _c in rules:
                if supp[a] < args.min_test_support:
                    unt += 1
                    continue
                conf = co[(a, b)] / supp[a]
                confs.append(conf)
                if conf >= args.replication_conf:
                    rep += 1
                else:
                    con += 1
                    failures.append((conf, tr_conf, a, b, supp[a], labels[taxon]))
            testable = rep + con
            med = sorted(confs)[len(confs) // 2] if confs else float("nan")
            L.append(f"| {labels[taxon]} ({n:,}) | {testable:,} | {rep:,} "
                     f"({100*rep/testable:.0f}%) | {con:,} | {unt:,} | {med:.2f} |"
                     if testable else
                     f"| {labels[taxon]} ({n:,}) | 0 | — | — | {unt:,} | — |")
            overall.setdefault(family, []).append((labels[taxon], rep, testable, failures))
        L.append("")

    for family, per_org in overall.items():
        fails = [f for _org, _r, _t, fs in per_org for f in fs]
        if not fails:
            continue
        fails.sort()
        L += [f"### {family}: rules that do not hold outside the training organism",
              "",
              "_Naming the organism matters: a cellular-component rule tested in a "
              "bacterium is a category error, not a broken rule._",
              "", "| rule | held-out organism | train conf | held-out conf | carriers |",
              "|---|---|--:|--:|--:|"]
        for conf, tr_conf, a, b, s, org in fails[:args.top]:
            L.append(f"| {a} → {b} | {org} | {tr_conf:.2f} | {conf:.2f} | {s} |")
        L.append("")

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
