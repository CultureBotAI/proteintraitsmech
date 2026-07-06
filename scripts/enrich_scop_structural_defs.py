#!/usr/bin/env python3
"""Add STRUCTURAL definitions to SCOP fold records from SCOPe's comment file.

Phase 1a of the layered-definitions work. SCOP fold (cf-level) nodes carry a
canonical structural description in SCOPe's dir.com file, e.g.

    48370 ! multihelical; 2 (curved) layers: alpha/alpha; right-handed superhelix

which is exactly the "structural elements + how they are arranged" layer we want.
This adds it as a `definitions` entry {kind: STRUCTURAL, method: SOURCED} on each
SCOP STRUCT_FOLD record whose sunid is a **fold (cf)** node with a comment. The
existing `definition` string is left as the general fallback.

Family (fa) level comments are curatorial notes ("not a true family", "mapped to
Pfam …"), not structural — those are skipped.

Inputs (data/raw/scope/, from `just fetch-scope`):
  dir.des.scope.2.08-stable.txt   sunid → node level
  dir.com.scope.2.08-stable.txt   sunid → comment(s)

Idempotent (skips records that already carry a STRUCTURAL definition); dry-run
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
FOLD_DIR = REPO_ROOT / "data" / "traits" / "structure" / "fold" / "scope"

SOURCE = "SCOPe 2.08 (dir.com structural comment)"


def load_levels() -> dict[str, str]:
    lv = {}
    for line in DES.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) >= 2:
            lv[p[0]] = p[1]
    return lv


def load_comments() -> dict[str, str]:
    com = collections.defaultdict(list)
    for line in COM.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^(\d+)\s*!\s*(.+)$", line)
        if m:
            com[m.group(1)].append(m.group(2).strip())
    return {sid: "; ".join(parts) for sid, parts in com.items()}


def folded(text: str, indent: str) -> str:
    text = " ".join(text.split())
    return f"{indent}  text: >-\n{indent}    {text}\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not COM.exists():
        print("missing data/raw/scope/dir.com.scope.2.08-stable.txt", file=sys.stderr)
        return 2

    level = load_levels()
    comments = load_comments()
    added = skipped = no_com = 0

    for p in sorted(FOLD_DIR.glob("*.yaml")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^identifier:\s*SCOP:(\d+)", text, re.M)
        if not m:
            continue
        sid = m.group(1)
        if level.get(sid) != "cf":          # structural comments live on fold nodes
            continue
        if sid not in comments:
            no_com += 1
            continue
        if re.search(r"kind:\s*STRUCTURAL", text):
            skipped += 1
            continue
        ind = "  "  # SCOP records use 2-space list items
        block = ("definitions:\n"
                 f"{ind}- kind: STRUCTURAL\n"
                 + folded(comments[sid], ind)
                 + f'{ind}  source: "{SOURCE}"\n'
                 + f"{ind}  method: SOURCED\n")
        new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1) \
            if re.search(r"^license:", text, re.M) else text.rstrip("\n") + "\n" + block
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"SCOP fold STRUCTURAL definitions: {'added' if args.apply else 'would add'} {added} "
          f"| already had {skipped} | fold nodes w/o comment {no_com}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
