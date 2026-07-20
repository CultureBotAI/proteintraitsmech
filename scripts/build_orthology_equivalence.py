#!/usr/bin/env python3
"""Cross-source orthology equivalence overlay (FUNCTION axis) — issue #20.

OrthoDB, OMA, COG and KOG all populate FUNC_ORTHOLOG_GROUP describing overlapping
orthology, but with disjoint identifier spaces (no shared ontology anchor). Per
the merge-within-axis skill these must be **related, never merged**. Orthologous
groups from different sources that carry the **same functional name** denote the
same conserved function, so this builder anchors on the normalized group name and
emits `biolink:close_match` edges (review candidates, not merges) to
`data/equivalence/orthology.tsv` — loaded bidirectionally by build_docs_index like
the other equivalence overlays.

Guards (mirroring the merge-traits generic-anchor cut):
  • cross-SOURCE only (same normalized name within one source is not an edge);
  • skip generic names shared by more than --anchor-cap records (default 8);
  • skip unknown-function / too-short names.

Read-only w.r.t. records; writes only the overlay TSV. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OG_DIR = REPO_ROOT / "data" / "traits" / "function" / "ortholog_group"
OUT = REPO_ROOT / "data" / "equivalence" / "orthology.tsv"

_NORM = re.compile(r"[^a-z0-9]+")
_NOFUNC = re.compile(r"hypothetical|uncharacteri[sz]ed|unknown function|"
                     r"^duf\d|domain of unknown|predicted protein", re.I)
# Minted level/category parent nodes are not orthologous groups.
_NODE = re.compile(r"_LEVEL_|_CATEGORY_")


def norm(label: str) -> str:
    return _NORM.sub(" ", (label or "").lower()).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anchor-cap", type=int, default=8,
                    help="skip names shared by more than this many records (generic)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # normalized name -> {(source, identifier)}
    by_name: dict[str, set] = defaultdict(set)
    scanned = 0
    for p in OG_DIR.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8", errors="replace")
        if "trait_category: FUNC_ORTHOLOG_GROUP" not in t:
            continue
        im = re.search(r"(?m)^identifier:\s*(\S+)", t)
        lm = re.search(r'(?m)^label:\s*"?(.+?)"?\s*$', t)
        if not im or not lm or _NODE.search(im.group(1)):
            continue
        nl = norm(lm.group(1))
        if len(nl) < 6 or _NOFUNC.search(lm.group(1)):
            continue
        scanned += 1
        by_name[nl].add((im.group(1).split(":", 1)[0], im.group(1)))

    edges: dict[tuple, str] = {}
    generic = 0
    for nl, recs in by_name.items():
        if len({s for s, _ in recs}) < 2:      # cross-source only
            continue
        if len(recs) > args.anchor_cap:         # generic name — skip
            generic += 1
            continue
        for (sa, a), (sb, b) in combinations(sorted(recs), 2):
            if sa == sb:
                continue
            key = tuple(sorted((a, b)))
            edges.setdefault(key, f"orthology-name:{nl[:60]}")

    rows = sorted((a, "biolink:close_match", b, src) for (a, b), src in edges.items())
    from collections import Counter
    pair_src = Counter(tuple(sorted((r[0].split(":")[0], r[2].split(":")[0]))) for r in rows)
    print(f"scanned {scanned:,} orthology records; "
          f"{len(rows):,} cross-source close_match edges over "
          f"{sum(1 for recs in by_name.values() if len({s for s,_ in recs})>=2):,} "
          f"shared names ({generic} generic names skipped)")
    for pair, n in pair_src.most_common():
        print(f"  {pair[0]} ↔ {pair[1]}: {n}")
    if args.dry_run:
        for r in rows[:6]:
            print("  ", *r)
        print("Dry-run — not written.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print(f"wrote {len(rows):,} edges → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
