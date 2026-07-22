#!/usr/bin/env python3
"""Trait → GO-function decision tree (issue #7, phase 2).

Trains interpretable decision trees that predict a protein's **GO molecular-
function** terms from the **signature traits** it carries (Pfam / InterPro / CATH /
PROSITE / SMART / CDD / NCBIfam) — the "predict function from the presence of
certain traits" baseline. Reads the protein×trait matrix `data/profiles/profiles.jsonl`
(from build_swissprot_profiles.py) and the corpus trait index (to tell which GO ids
are molecular-function).

For each of the top-K GO-MF targets it fits a shallow DecisionTreeClassifier
(interpretable), reports held-out precision/recall/F1, and prints the learned
if-present rules (which trait → which function). Also a multi-label summary.

Run with the interpreter that has scikit-learn (system python3 here, like the embed
scripts). Read-only; prints a report (optionally --out a markdown file).
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
SIG_PREFIXES = ("Pfam", "InterPro", "CATH", "PROSITE", "SMART", "CDD", "NCBIfam")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-features", type=int, default=400, help="top-N signature traits")
    ap.add_argument("--targets", type=int, default=25, help="top-K GO-MF terms to model")
    ap.add_argument("--min-pos", type=int, default=40, help="min proteins carrying a target GO")
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--out", help="write the markdown report here")
    args = ap.parse_args()

    try:
        import numpy as np
        from sklearn.tree import DecisionTreeClassifier, export_text
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import precision_recall_fscore_support
    except ImportError:
        print("needs scikit-learn + numpy — run with the interpreter that has them "
              "(system python3 here).", file=sys.stderr)
        return 2

    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    go_mf = {c for c, (ax, cat) in idx.items()
             if c.startswith("GO:") and cat == "FUNC_MOLECULAR_FUNCTION"}

    rows = [json.loads(l) for l in JSONL.open(encoding="utf-8")]
    # signature-trait feature vocab (most frequent) + GO-MF label vocab
    feat_ct, lab_ct = collections.Counter(), collections.Counter()
    for r in rows:
        sig = {t for t in r["traits"] if t.split(":")[0] in SIG_PREFIXES}
        r["_sig"] = sig
        r["_mf"] = set(r["go"]) & go_mf
        feat_ct.update(sig)
        lab_ct.update(r["_mf"])
    feats = [f for f, _ in feat_ct.most_common(args.max_features)]
    fpos = {f: i for i, f in enumerate(feats)}
    labels = [g for g, c in lab_ct.most_common() if c >= args.min_pos][:args.targets]
    if not labels:
        print("no GO-MF label meets --min-pos; lower it or scale the matrix.")
        return 1

    X = np.zeros((len(rows), len(feats)), dtype=np.int8)
    for i, r in enumerate(rows):
        for f in r["_sig"]:
            if f in fpos:
                X[i, fpos[f]] = 1
    Xtr, Xte, tr_i, te_i = train_test_split(X, np.arange(len(rows)), test_size=0.25, random_state=42)

    out = [f"proteins: {len(rows):,} | signature-trait features: {len(feats)} "
           f"(of {len(feat_ct):,}) | GO-MF targets: {len(labels)}\n",
           "| GO-MF target | pos | test P | R | F1 | top learned rule |",
           "|---|--:|--:|--:|--:|---|"]
    f1s = []
    for g in labels:
        y = np.array([1 if g in rows[i]["_mf"] else 0 for i in range(len(rows))])
        ytr, yte = y[tr_i], y[te_i]
        if ytr.sum() < 5 or yte.sum() < 2:
            continue
        clf = DecisionTreeClassifier(max_depth=args.max_depth, class_weight="balanced",
                                     random_state=42).fit(Xtr, ytr)
        pred = clf.predict(Xte)
        p, r_, f1, _ = precision_recall_fscore_support(yte, pred, average="binary", zero_division=0)
        f1s.append(f1)
        # top rule: the feature with the highest importance + its positive direction
        imp = clf.feature_importances_
        top = feats[int(imp.argmax())] if imp.max() > 0 else "(none)"
        out.append(f"| {g} | {int(y.sum())} | {p:.2f} | {r_:.2f} | {f1:.2f} | present({top}) → {g} |")
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0
    out.insert(1, f"macro-F1 over {len(f1s)} targets: **{macro_f1:.2f}**\n")

    # one worked example tree (the highest-support target) for the report
    g0 = labels[0]
    y0 = np.array([1 if g0 in rows[i]["_mf"] else 0 for i in range(len(rows))])
    clf0 = DecisionTreeClassifier(max_depth=3, class_weight="balanced", random_state=42).fit(X, y0)
    tree_txt = export_text(clf0, feature_names=feats, max_depth=3)
    out.append(f"\nExample decision tree for {g0} (depth 3):\n```\n{tree_txt.strip()}\n```")

    report = "\n".join(out)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
