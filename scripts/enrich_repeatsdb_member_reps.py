#!/usr/bin/env python3
"""Backfill structural_geometry_representations on RepeatsDB classification nodes
that have no curated `representative` (in classification.json) and no curated
representative anywhere in their subtree either — using a real MEMBER structure
drawn from RepeatsDB's per-structure annotations.

Data: data/raw/repeatsdb/class_members.json (built by
fetch_repeatsdb_annotations.py) maps each classification code to a representative
member — {pdb, chain, source, n} — taken from the structures RepeatsDB actually
annotates with that class.topology.fold.clan code.

For each still-repless node:
  • exact code match in the member index → use that structure;
  • else the most-populated descendant code (highest member count) → use its
    structure, noting the sub-classification it came from.
Provenance is explicit: evidence_source records the PDB chain, the region class it
was annotated with, and that it is a member (not a curated representative).

This is the third tier of representative quality, after (1) the node's own curated
representative and (2) a curated descendant's (enrich_repeatsdb_inherited_reps.py).
Idempotent (skips nodes that already carry a geometry rep); dry-run unless --apply.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "repeatsdb"
CLASS_JSON = RAW / "classification.json"
MEMBERS = RAW / "class_members.json"
RDB_DIR = REPO_ROOT / "data" / "traits" / "sequence_structure" / "structural_repeat" / "repeatsdb"


def find_file(rid: str) -> Path | None:
    needle = f"identifier: RepeatsDB:{rid}\n"
    for p in RDB_DIR.glob("*.yaml"):
        if needle in p.read_text(encoding="utf-8"):
            return p
    return None


def best_member(rid: str, members: dict) -> tuple[str, dict] | None:
    """Exact code match, else the most-populated descendant code."""
    if rid in members:
        return rid, members[rid]
    desc = [(c, m) for c, m in members.items() if c.startswith(rid + ".")]
    if not desc:
        return None
    code, m = max(desc, key=lambda cm: (cm[1].get("n", 0), cm[0]))
    return code, m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    if not MEMBERS.exists():
        print("missing data/raw/repeatsdb/class_members.json; run "
              "fetch_repeatsdb_annotations.py first", file=sys.stderr)
        return 2
    data = json.loads(CLASS_JSON.read_text(encoding="utf-8"))
    members = json.loads(MEMBERS.read_text(encoding="utf-8"))
    repless = [rid for rid, node in data.items()
               if not (node.get("representative") or "").strip()]

    filled = still_gap = 0
    for rid in sorted(repless):
        path = find_file(rid)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8")
        if "structural_geometry_representations" in text:  # already has one (own/inherited)
            continue
        hit = best_member(rid, members)
        if hit is None:
            still_gap += 1
            print(f"  {rid:12s} — no member structure in annotations (true gap)")
            continue
        code, m = hit
        pdb, chain, source = m["pdb"], m.get("chain", ""), m.get("source", "")
        ref = f"PDB:{pdb}" if source == "RCSB/PDB" else f"AlphaFoldDB:{pdb}"
        via = "" if code == rid else f", within {rid}"
        note = (f"RepeatsDB member structure {pdb} chain {chain} "
                f"(region classified {code}{via}; node has no curated representative)")
        block = (
            "structural_geometry_representations:\n"
            f"- structure_ref: {ref}\n"
            "  structure_source: RepeatsDB\n"
            f"  evidence_source: {note}\n"
        )
        new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1) \
            if re.search(r"^license:", text, re.M) else text.rstrip("\n") + "\n" + block
        filled += 1
        print(f"  {rid:12s} ← {code:10s} {ref} (chain {chain}, {m.get('n')} members)   {path.name}")
        if args.apply:
            path.write_text(new, encoding="utf-8")

    print(f"\nFilled from member structures: {filled} | true gaps (no member at all): {still_gap}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
