#!/usr/bin/env python3
"""Backfill structural_geometry_representations on RepeatsDB classification nodes
that lack a curated `representative` PDB but have a descendant that carries one.

Context: seed_repeatsdb.py attaches a PDB xref (and, via enrich_structural_
provenance.py, a structural_geometry_representations block) only when a node's
`representative` field is populated in classification.json. 35 of 122 nodes have
an empty representative. For the subset whose *descendant* nodes DO have a curated
representative, we inherit the nearest descendant's PDB — a genuine member of the
node's classification group — clearly labelled as inherited. The remaining nodes
(no representative anywhere in their subtree) are left as an explicit gap:
RepeatsDB assigns them no representative, and its bulk classification export lists
no member structures, so a rep cannot be derived without fabricating curation.

Idempotent (skips nodes that already have a geometry rep); dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLASS_JSON = REPO_ROOT / "data" / "raw" / "repeatsdb" / "classification.json"
RDB_DIR = REPO_ROOT / "data" / "traits" / "sequence_structure" / "structural_repeat" / "repeatsdb"


def to_pdb(token: str) -> str:
    """'4ionA' → 'PDB:4ION' (drop chain suffix)."""
    token = (token or "").strip()
    return f"PDB:{token[:4].upper()}" if len(token) >= 4 and token[:4].isalnum() else ""


def nearest_descendant_rep(rid: str, reps: dict[str, str]) -> tuple[str, str] | None:
    """Nearest descendant (shortest id) of `rid` that carries a representative."""
    cands = sorted((c for c in reps if c.startswith(rid + ".") and reps[c]),
                   key=lambda c: (c.count("."), c))
    return (cands[0], reps[cands[0]]) if cands else None


def find_file(rid: str) -> Path | None:
    needle = f"identifier: RepeatsDB:{rid}\n"
    for p in RDB_DIR.glob("*.yaml"):
        if needle in p.read_text(encoding="utf-8"):
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    data = json.loads(CLASS_JSON.read_text(encoding="utf-8"))
    reps = {rid: (node.get("representative") or "").strip() for rid, node in data.items()}
    missing = [rid for rid, r in reps.items() if not r]

    inherited = gap = 0
    for rid in sorted(missing):
        path = find_file(rid)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8")
        if "structural_geometry_representations" in text:
            continue
        dr = nearest_descendant_rep(rid, reps)
        pdb = to_pdb(dr[1]) if dr else ""
        if not pdb:
            gap += 1
            continue
        block = (
            "structural_geometry_representations:\n"
            f"- structure_ref: {pdb}\n"
            "  structure_source: RepeatsDB\n"
            f"  evidence_source: RepeatsDB representative inherited from member subclass "
            f"{dr[0]} (node has no curated representative)\n"
        )
        # Insert before the trailing `license:` line to keep field order tidy.
        if re.search(r"^license:", text, re.M):
            new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1)
        else:
            new = text.rstrip("\n") + "\n" + block
        inherited += 1
        print(f"  {rid:12s} ← {dr[0]}  ({pdb})   {path.name}")
        if args.apply:
            path.write_text(new, encoding="utf-8")

    print(f"\nInherited reps: {inherited} | no rep in subtree (documented gap): {gap}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
