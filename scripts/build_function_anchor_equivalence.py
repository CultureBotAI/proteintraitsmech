#!/usr/bin/env python3
"""Function-axis equivalence overlay (cross-source-comparison-review-1 §4).

For the FUNCTION axis, cross-source equivalence is decided by shared *ontology
anchors*, not embedding similarity (review: "the operator must agree with the
category representation"). Two FUNCTION records of the **same trait_category**
that share a discriminating anchor CURIE denote the same function.

Anchors (from identifier + xrefs + mapped_xrefs only — never parent_traits):
  EC leaf   `EC:d.d.d.d`   (partial EC like `1.1.1.-` excluded — not a leaf)
  RHEA      `RHEA:n`
  ARO       `ARO:n`
  TCDB      `TCDB:x[.x…]`
  PSI-MI    `MI:n`
GO and ChEBI are deliberately excluded: broad GO terms are not identity, and a
shared ChEBI participant is `has_participant`, not equivalence.

Edge rule (per §1 category operators):
  * only pairs in the SAME trait_category are compared;
  * only CROSS-SOURCE pairs are emitted (same-source siblings are a within-source
    hierarchy, not a match);
  * predicate `biolink:close_match`; `relation_source = anchor-<CURIE>`.
When a member's identifier IS the anchor (the canonical record, e.g. the EC:x or
RHEA:x record) the group is emitted as a star to that canonical record (O(k));
otherwise cross-source pairs are emitted pairwise, and groups larger than
--max-group are skipped-with-log to avoid a quadratic blow-up on a popular anchor.

Output: data/equivalence/function.tsv  (subject, predicate, object, relation_source)
Stdlib-only.

  python3 scripts/build_function_anchor_equivalence.py
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FUNC = REPO_ROOT / "data" / "traits" / "function"
OUT = REPO_ROOT / "data" / "equivalence" / "function.tsv"

ANCHOR_RES = [
    re.compile(r"\bEC:\d+\.\d+\.\d+\.\d+\b"),   # EC leaf only
    re.compile(r"\bRHEA:\d+\b"),
    re.compile(r"\bARO:\d+\b"),
    re.compile(r"\bTCDB:[0-9]+(?:\.[0-9A-Za-z]+)*\b"),
    re.compile(r"\bMI:\d+\b"),
]
ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
CAT_RE = re.compile(r"^trait_category:\s*(\S+)", re.M)


def source_of(curie: str) -> str:
    """Coarse provenance key. proteintraitsmech:SEED_* / COG_CATEGORY_* etc. are
    split on the second token so different minted families don't all collapse."""
    pre, _, rest = curie.partition(":")
    if pre == "proteintraitsmech":
        return "pm:" + rest.split("_")[0]
    return pre


def anchor_region(text: str) -> str:
    """The identifier line + the xrefs and mapped_xrefs blocks — i.e. everything
    EXCEPT parent_traits / trait_relations, so a parent/hierarchy CURIE is never
    mistaken for an identity anchor."""
    keep = []
    m = ID_RE.search(text)
    if m:
        keep.append(m.group(0))
    for block in ("xrefs", "mapped_xrefs"):
        mb = re.search(rf"^{block}:\s*\n((?:\s+[-\w].*\n?)+)", text, re.M)
        if mb:
            keep.append(mb.group(1))
    return "\n".join(keep)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-group", type=int, default=40,
                    help="skip anchorless-canonical groups larger than this (quadratic guard)")
    args = ap.parse_args()

    # (category, anchor) -> {identifier: source}
    groups: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    n_records = 0
    for path in FUNC.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        mid, mcat = ID_RE.search(text), CAT_RE.search(text)
        if not mid or not mcat:
            continue
        ident, cat = mid.group(1), mcat.group(1)
        region = anchor_region(text)
        anchors = set()
        for rx in ANCHOR_RES:
            anchors.update(rx.findall(region))
        anchors.discard(ident)      # a record's own id isn't a self-anchor edge target here
        if not anchors:
            continue
        n_records += 1
        for a in anchors:
            groups[(cat, a)][ident] = source_of(ident)
        # also register the canonical record under its own identifier-anchor
        for rx in ANCHOR_RES:
            if rx.fullmatch(ident):
                groups[(cat, ident)][ident] = source_of(ident)

    edges = set()          # frozenset({s,o}) dedup guard
    edges_list: list[tuple[str, str, str]] = []
    skipped_big = 0
    for (cat, anchor), members in groups.items():
        if len(members) < 2:
            continue
        canonical = anchor if anchor in members else None
        ids = list(members)
        if canonical:
            for other in ids:
                if other == canonical:
                    continue
                if members[other] == members[canonical]:
                    continue                       # same source
                key = frozenset((other, canonical))
                if key not in edges:
                    edges.add(key)
                    edges_list.append((other, canonical, anchor))
        else:
            if len(ids) > args.max_group:
                skipped_big += 1
                continue
            for a, b in combinations(ids, 2):
                if members[a] == members[b]:
                    continue                       # same source
                key = frozenset((a, b))
                if key not in edges:
                    edges.add(key)
                    edges_list.append((a, b, anchor))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted((s, o, anc) for s, o, anc in edges_list)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, o, anc in rows:
            fh.write(f"{s}\tbiolink:close_match\t{o}\tanchor-{anc}\n")
    print(f"scanned {n_records:,} anchored FUNCTION records; "
          f"wrote {len(rows):,} cross-source close_match edges → {OUT.relative_to(REPO_ROOT)}"
          + (f" ({skipped_big} oversized groups skipped)" if skipped_big else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
