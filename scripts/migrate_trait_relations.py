#!/usr/bin/env python3
"""Materialize Biolink-typed `trait_relations` on records whose parent edge is
really **membership**, not subclass — so the typed edge lives in the source
data for KG export (not only derived at docs-build time).

Adds, alongside the existing `parent_traits` (kept as the backward-compatible
biolink:subclass_of path), a `trait_relations` entry with
`predicate: biolink:member_of` for:
  Pfam family  → Pfam:CL…      (family is a member of a clan)
  COG          → COG_CATEGORY  (ortholog group ∈ functional category)
  PROSITE:PS   → PROSITE:PDOC  (signature ∈ documentation group)

Minimal-diff: the `trait_relations:` block is inserted textually right after
the record's `parent_traits:` block; the rest of the file is untouched.
Idempotent (skips records already carrying trait_relations). Dry-run unless
--apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"


def member_parents(identifier: str, parents: list[str]) -> list[str]:
    """Return the subset of parents that are member_of (not subclass) edges."""
    out = []
    for p in parents:
        if identifier.startswith("Pfam:") and p.startswith("Pfam:CL"):
            out.append(p)
        elif identifier.startswith("COG:") and p.startswith("proteintraitsmech:COG_CATEGORY_"):
            out.append(p)
        elif identifier.startswith("PROSITE:PS") and p.startswith("PROSITE:PDOC"):
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    touched = added = 0
    for path in TRAITS.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "parent_traits:" not in text or "trait_relations:" in text:
            continue
        lines = text.splitlines()
        ident = ""
        for ln in lines:
            if ln.startswith("identifier:"):
                ident = ln.split(":", 1)[1].strip()
                break
        # collect parent_traits block bounds + values
        try:
            start = next(i for i, l in enumerate(lines) if l.rstrip() == "parent_traits:")
        except StopIteration:
            continue
        end = start + 1
        parents = []
        indent = "  "
        while end < len(lines):
            m = re.match(r"(\s*)-\s*(\S+)\s*$", lines[end])
            if not m:
                break
            indent = m.group(1)          # match the file's list-item indent
            parents.append(m.group(2))
            end += 1
        mem = member_parents(ident, parents)
        if not mem:
            continue
        cont = indent + "  "             # continuation indent for mapping fields
        block = ["trait_relations:"]
        for p in mem:
            block += [f"{indent}- predicate: biolink:member_of",
                      f"{cont}object: {p}",
                      f"{cont}relation_source: derived"]
        new_lines = lines[:end] + block + lines[end:]
        touched += 1
        added += len(mem)
        if args.apply:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: {added} member_of "
          f"trait_relations across {touched} records.")
    if not args.apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
