#!/usr/bin/env python3
"""Materialize Biolink-typed `trait_relations` on records whose parent edge is
really **membership**, not subclass — so the typed edge lives in the source
data for KG export (not only derived at docs-build time).

Adds, alongside the existing `parent_traits` (kept as the backward-compatible
biolink:subclass_of path), a typed `trait_relations` entry for parent edges that
are really **membership** or **partonomy**, not subclass:
  biolink:member_of
    Pfam family  → Pfam:CL…      (family is a member of a clan)
    COG          → COG_CATEGORY  (ortholog group ∈ functional category)
    PROSITE:PS   → PROSITE:PDOC  (signature ∈ documentation group)
    CDD domain   → CDD:cl…       (conserved domain ∈ superfamily)
  biolink:part_of
    Reactome     → Reactome      (sub-pathway/reaction is part of its pathway;
                                  Reactome's hierarchy is event partonomy)

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


def typed_parents(identifier: str, parents: list[str]) -> list[tuple[str, str]]:
    """Return (predicate, parent) for parent edges that are NOT subclass —
    membership or partonomy — so they can be typed. Subclass edges stay implicit
    in parent_traits."""
    out = []
    for p in parents:
        if identifier.startswith("Pfam:") and p.startswith("Pfam:CL"):
            out.append(("biolink:member_of", p))
        elif identifier.startswith("COG:") and p.startswith("proteintraitsmech:COG_CATEGORY_"):
            out.append(("biolink:member_of", p))
        elif identifier.startswith("PROSITE:PS") and p.startswith("PROSITE:PDOC"):
            out.append(("biolink:member_of", p))
        elif identifier.startswith("CDD:") and p.startswith("CDD:cl"):
            out.append(("biolink:member_of", p))
        elif identifier.startswith("Reactome:") and p.startswith("Reactome:"):
            out.append(("biolink:part_of", p))
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
        typed = typed_parents(ident, parents)
        if not typed:
            continue
        cont = indent + "  "             # continuation indent for mapping fields
        block = ["trait_relations:"]
        for predicate, p in typed:
            block += [f"{indent}- predicate: {predicate}",
                      f"{cont}object: {p}",
                      f"{cont}relation_source: derived"]
        new_lines = lines[:end] + block + lines[end:]
        touched += 1
        added += len(typed)
        if args.apply:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: {added} typed "
          f"trait_relations across {touched} records.")
    if not args.apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
