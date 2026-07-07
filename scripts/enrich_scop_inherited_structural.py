#!/usr/bin/env python3
"""Give SCOP superfamily/family/domain (sf/fa/dm) records a STRUCTURAL definition
inherited from their fold.

enrich_scop_structural_defs.py added STRUCTURAL definitions only to SCOP **fold
(cf)** nodes, from SCOPe's dir.com comments. The ~21k sf/fa/dm nodes below them
still lack one — and their own dir.com comments are curatorial ("mapped to Pfam…"),
not structural. But every SCOP node's sccs encodes its fold: `c.55.2.0` → fold
`c.55`. So we inherit the fold's structural description, clearly labelled, the same
pattern used for RepeatsDB rep inheritance.

    SCOP:238316 (sccs c.55.2.0) → STRUCTURAL "<fold c.55 description>
                                  (inherited from fold c.55)."

Inputs (data/raw/scope/, from `just fetch-scope`):
  dir.des.scope.2.08-stable.txt   sunid → level, sccs
  dir.com.scope.2.08-stable.txt   sunid → comment

Idempotent (skips records already carrying a STRUCTURAL definition); dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCOPE = REPO_ROOT / "data" / "raw" / "scope"
DES = SCOPE / "dir.des.scope.2.08-stable.txt"
COM = SCOPE / "dir.com.scope.2.08-stable.txt"
TRAITS = REPO_ROOT / "data" / "traits"


def load_fold_desc() -> dict[str, str]:
    """fold sccs (2-part, e.g. 'c.55') → its structural description (dir.com)."""
    sunid_sccs, sunid_level = {}, {}
    for line in DES.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) >= 3:
            sunid_level[p[0]] = p[1]
            sunid_sccs[p[0]] = p[2]
    com = collections.defaultdict(list)
    for line in COM.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(\d+)\s*!\s*(.+)$", line)
        if m:
            com[m.group(1)].append(m.group(2).strip())
    out = {}
    for sunid, lvl in sunid_level.items():
        if lvl == "cf" and sunid in com:                 # fold node with a comment
            out[sunid_sccs[sunid]] = "; ".join(com[sunid])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not COM.exists():
        print("missing data/raw/scope/dir.com.scope.2.08-stable.txt", file=sys.stderr)
        return 2

    fold_desc = load_fold_desc()
    print(f"{len(fold_desc):,} folds carry a structural description")
    added = skipped = no_fold = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        if not re.search(r"(?m)^identifier:\s*SCOP:", text):
            continue
        if "kind: STRUCTURAL" in text:                   # cf nodes already have theirs
            skipped += 1
            continue
        m = re.search(r"SCOP:([a-z]\.[\d.]+)", text)     # the sccs xref
        if not m:
            continue
        fold = ".".join(m.group(1).split(".")[:2])       # class.fold
        desc = fold_desc.get(fold)
        if not desc:
            no_fold += 1
            continue
        block = ("definitions:\n"
                 "  - kind: STRUCTURAL\n"
                 f"    text: >-\n      {desc} (inherited from fold {fold}).\n"
                 '    source: "SCOPe 2.08 dir.com (inherited from fold)"\n'
                 "    method: SOURCED\n")
        new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1) \
            if re.search(r"(?m)^license:", text) else text.rstrip("\n") + "\n" + block
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"SCOP inherited STRUCTURAL: {'added' if args.apply else 'would add'} {added:,} "
          f"| already had {skipped:,} | fold has no description {no_fold:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
