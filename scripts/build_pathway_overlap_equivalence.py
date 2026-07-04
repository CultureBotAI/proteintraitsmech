#!/usr/bin/env python3
"""Pathway equivalence overlay for FUNC_PATHWAY (SEED ↔ Reactome).

Pathways have no single shared identifier across sources, so equivalence is
decided by TWO parallel signals (cross-source-comparison-review-1 §4 gap + the
GO-BP grounding path):

  A. GO biological-process anchor  — two FUNC_PATHWAY records that carry the same
     specific GO-BP CURIE denote the same process → biolink:close_match.
     (Reactome GO-BP is authoritative via ContentService; SEED via exact
     name→GO-BP match. A broad GO-BP shared by many pathways is generic, not
     identity, so groups larger than --max-group are skipped.)

  B. Constituent EC-set Jaccard    — two pathways whose enzyme (EC) sets overlap
     substantially share machinery → biolink:overlaps; only a near-identical
     EC set AND an agreeing label token is promoted to close_match. (A pathway
     sharing a few enzymes with another is NOT the same pathway — hence
     `overlaps`, not `close_match`.)

Both signals require the records to be GROUNDED first (GO-BP and/or EC
mapped_xrefs). SEED subsystems carry EC today; Reactome EC is not populated, so
signal B only fires once Reactome carries EC — the code is ready for it.

Only same-category (FUNC_PATHWAY) + cross-source pairs are emitted.
Output: data/equivalence/pathway.tsv  (subject, predicate, object, relation_source)
Stdlib-only.

  python3 scripts/build_pathway_overlap_equivalence.py
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PATHWAY = REPO_ROOT / "data" / "traits" / "function" / "pathway"
OUT = REPO_ROOT / "data" / "equivalence" / "pathway.tsv"

ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
LABEL_RE = re.compile(r'^label:\s*"?(.*?)"?\s*$', re.M)
GO_RE = re.compile(r"\bGO:\d{7}\b")
EC_RE = re.compile(r"\bEC:\d+\.\d+\.\d+\.\d+\b")   # EC leaf only
_STOP = {"the", "and", "of", "in", "to", "a", "an", "by", "with", "for", "from",
         "pathway", "metabolism", "biosynthesis", "process", "cluster", "system"}


def source_of(curie: str) -> str:
    pre, _, rest = curie.partition(":")
    return "SEED" if pre == "proteintraitsmech" and rest.startswith("SEED_") else pre


def mapped_region(text: str) -> str:
    """The xrefs + mapped_xrefs blocks only (identity/grounding anchors), never
    parent_traits / trait_relations."""
    keep = []
    for block in ("xrefs", "mapped_xrefs"):
        mb = re.search(rf"^{block}:\s*\n((?:\s+[-\w].*\n?)+)", text, re.M)
        if mb:
            keep.append(mb.group(1))
    return "\n".join(keep)


def label_tokens(label: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", label.lower()) if len(w) > 3 and w not in _STOP}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-group", type=int, default=25,
                    help="skip a GO-BP anchor shared by more than this many pathways (generic process)")
    ap.add_argument("--min-jaccard", type=float, default=0.30,
                    help="min EC-set Jaccard for an `overlaps` edge")
    ap.add_argument("--close-jaccard", type=float, default=0.80,
                    help="EC-set Jaccard at/above this + shared label token → close_match")
    args = ap.parse_args()

    recs = {}   # id -> {"src","label","go","ec"}
    for path in PATHWAY.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        mid = ID_RE.search(text)
        if not mid or "trait_category: FUNC_PATHWAY" not in text:
            continue
        ident = mid.group(1)
        region = mapped_region(text)
        ml = LABEL_RE.search(text)
        recs[ident] = {
            "src": source_of(ident),
            "label": ml.group(1) if ml else "",
            "go": set(GO_RE.findall(region)),
            "ec": set(EC_RE.findall(region)),
        }

    edges = {}   # frozenset({s,o}) -> (s, predicate, o, relation_source) ; best predicate wins

    def offer(a: str, b: str, predicate: str, rel: str, strength: int):
        key = frozenset((a, b))
        prev = edges.get(key)
        if prev is None or strength > prev[0]:
            s, o = sorted((a, b))
            edges[key] = (strength, s, predicate, o, rel)

    STRENGTH = {"biolink:overlaps": 1, "biolink:close_match": 2}

    # --- Signal A: GO-BP anchor ---
    by_go: dict[str, list[str]] = defaultdict(list)
    for ident, r in recs.items():
        for g in r["go"]:
            by_go[g].append(ident)
    a_skipped = 0
    for go, members in by_go.items():
        if len(members) < 2:
            continue
        if len(members) > args.max_group:
            a_skipped += 1
            continue
        for x, y in combinations(members, 2):
            if recs[x]["src"] != recs[y]["src"]:
                offer(x, y, "biolink:close_match", f"go-bp-{go}", STRENGTH["biolink:close_match"])

    # --- Signal B: EC-set Jaccard (cross-source) ---
    by_ec: dict[str, set[str]] = defaultdict(set)
    for ident, r in recs.items():
        for e in r["ec"]:
            by_ec[e].add(ident)
    candidate_pairs = set()
    for members in by_ec.values():
        for x, y in combinations(sorted(members), 2):
            if recs[x]["src"] != recs[y]["src"]:
                candidate_pairs.add((x, y))
    for x, y in candidate_pairs:
        ex, ey = recs[x]["ec"], recs[y]["ec"]
        inter = ex & ey
        union = ex | ey
        if not union:
            continue
        jac = len(inter) / len(union)
        if jac < args.min_jaccard:
            continue
        if jac >= args.close_jaccard and (label_tokens(recs[x]["label"]) & label_tokens(recs[y]["label"])):
            offer(x, y, "biolink:close_match", f"ec-jaccard-{jac:.2f}", STRENGTH["biolink:close_match"])
        else:
            offer(x, y, "biolink:overlaps", f"ec-jaccard-{jac:.2f}", STRENGTH["biolink:overlaps"])

    rows = sorted((s, p, o, rel) for (_st, s, p, o, rel) in edges.values())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, p, o, rel in rows:
            fh.write(f"{s}\t{p}\t{o}\t{rel}\n")

    n_go = sum(1 for r in rows if r[3].startswith("go-bp-"))
    n_ec = len(rows) - n_go
    grounded_go = sum(1 for r in recs.values() if r["go"])
    print(f"scanned {len(recs):,} FUNC_PATHWAY records "
          f"({grounded_go:,} carry a GO-BP anchor); wrote {len(rows):,} cross-source edges "
          f"→ {OUT.relative_to(REPO_ROOT)}  [GO-BP {n_go}, EC-Jaccard {n_ec}]"
          + (f"; {a_skipped} generic GO-BP groups skipped" if a_skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
