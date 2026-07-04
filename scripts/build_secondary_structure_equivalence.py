#!/usr/bin/env python3
"""Secondary-structure equivalence (research/cross-source-comparison-review-1.md §4).

The 2D analogue of the Phase-1/2/3 equivalence overlays: compare STRUCT_SECONDARY
entries in *secondary-structure* space using the `secondary_structure_
representations` slot (normalised SS-element topology string, e.g. `E-turn-E`,
`H-turn-H`, or a DSSP/STRIDE state string). Two entries whose SS grammar matches
are the same 2° trait.

Operators (Biolink-typed, conservative):
  * identical normalised topology_string (or ss_string) across DIFFERENT sources
    → biolink:close_match
  * one topology is a proper specialization of another (equal after stripping a
    parenthetical qualifier, e.g. `H-loop(Ca)-H` ⊂ `H-loop-H`) → the more
    specific → biolink:narrow_match the general
Parent/child pairs already linked via `parent_traits` are skipped (no redundant
edges). Same-source pairs are withheld by default (the current 2° taxonomy is a
single curated source, so cross-source edges appear only once DSSP/STRIDE/PDBsum
-derived SS records are seeded); `--allow-same-source` surfaces them for review.

Output overlay: data/equivalence/secondary_structure.tsv (same 4-col schema;
loaded into the browser `eq` field by build_docs_index). Stdlib-only.

  just build-secondary-structure-equivalence
  python3 scripts/build_secondary_structure_equivalence.py --allow-same-source
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "equivalence" / "secondary_structure.tsv"
MARKER = "secondary_structure_representations:"
QUAL = re.compile(r"\([^)]*\)")   # parenthetical qualifier, e.g. (Ca), (kink)


def source_of(curie: str) -> str:
    return curie.split(":", 1)[0]


def norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).lower()


def parse_record(text: str) -> dict | None:
    mid = re.search(r"^identifier:\s*(\S+)", text, re.M)
    if not mid:
        return None
    lbl = re.search(r"^label:\s*(.+)$", text, re.M)
    parents = re.findall(r"^-\s*(\S+)", text, re.M)  # loose; only used for skip
    topos = [norm(m) for m in re.findall(r"^\s*topology_string:\s*\"?([^\"\n]+)\"?", text, re.M)]
    sss = [norm(m) for m in re.findall(r"^\s*ss_string:\s*(\S+)", text, re.M)]
    return {"id": mid.group(1), "label": (lbl.group(1).strip() if lbl else mid.group(1)),
            "topos": set(t for t in topos if t), "ss": set(sss),
            "parents": set(parents)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-same-source", action="store_true",
                    help="also emit edges between same-source records (exploration)")
    args = ap.parse_args()

    # Fast: grep for the marker, parse only matching files.
    try:
        files = subprocess.run(["grep", "-rl", MARKER, str(TRAITS)],
                               capture_output=True, text=True).stdout.split()
    except FileNotFoundError:
        files = [str(p) for p in TRAITS.rglob("*.yaml") if MARKER in p.read_text()]
    recs = [r for r in (parse_record(Path(f).read_text(encoding="utf-8")) for f in files) if r]
    recs = [r for r in recs if r["topos"] or r["ss"]]
    print(f"{len(recs)} records with a secondary-structure representation")

    edges = []          # (subj, pred, obj, relsrc)
    withheld_same = 0
    for a, b in combinations(recs, 2):
        # skip hierarchy-linked pairs (already related via parent_traits)
        if a["id"] in b["parents"] or b["id"] in a["parents"]:
            continue
        same_src = source_of(a["id"]) == source_of(b["id"])
        exact = bool((a["topos"] & b["topos"]) or (a["ss"] & b["ss"]))
        # Exact match = equivalence/dedup — same-source pairs are usually just
        # siblings, so guard them (the whole 2° taxonomy is one source today).
        if exact:
            if same_src and not args.allow_same_source:
                withheld_same += 1
            else:
                edges.append((a["id"], "biolink:close_match", b["id"], "ss-topology-exact"))
            continue
        # Specialization (equal after stripping a qualifier, e.g. H(kink) ⊂ H) is
        # a genuine refinement relation, not dedup — emit regardless of source.
        for ta in a["topos"]:
            for tb in b["topos"]:
                if ta == tb:
                    continue
                if QUAL.sub("", ta) == tb:      # a is more specific
                    edges.append((a["id"], "biolink:narrow_match", b["id"], "ss-topology-specialization"))
                elif QUAL.sub("", tb) == ta:    # b is more specific
                    edges.append((b["id"], "biolink:narrow_match", a["id"], "ss-topology-specialization"))

    seen, uniq = set(), []
    for s, p, o, rs in sorted(edges):
        k = tuple(sorted((s, o)))
        if k in seen:
            continue
        seen.add(k)
        uniq.append((s, p, o, rs))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, p, o, rs in uniq:
            fh.write(f"{s}\t{p}\t{o}\t{rs}\n")
    print(f"wrote {len(uniq):,} SS-equivalence edges → {OUT.relative_to(REPO_ROOT)}")
    if withheld_same and not args.allow_same_source:
        print(f"  ({withheld_same} same-source topology matches withheld — the 2° "
              f"taxonomy is one curated source; pass --allow-same-source to include, "
              f"or seed DSSP/STRIDE-derived SS records for real cross-source edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
