#!/usr/bin/env python3
"""Round 2 of edison-trait-definitions: recompose CDD ortholog-group (KOG) defs.

CDD's FUNC_ORTHOLOG_GROUP records carry a NAME, not a definition —
  "KOG0227, Splicing factor 3a, subunit 2 [RNA processing and modification]"
— the KOG accession, the group name, and a bracketed COG-style functional
category. This turns each into a real definition in one consistent pattern,
composed from that same content (no new fetch, no LLM):

  "<name> (<KOG id>) — a eukaryotic orthologous group of proteins (KOG) in NCBI
   CDD; functional category: <category>."

method: SOURCED. Idempotent (detected via definition_source); dry-run unless
--apply. Stdlib-only.

Follow-up: seed_cdd.py should adopt the same composition for KOG records.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
SOURCE = "NCBI CDD (KOG; composed from name and functional category)"

# current def:  "<ACC>, <name> [<functional category>]"
_PARSE = re.compile(r"^(\w+\d+),\s*(.+?)\s*\[(.+)\]\s*$")
DEF_RE = re.compile(r"(?m)^definition:[ \t]*>-\n(?:[ \t]+.*\n)+?definition_source:.*$")


def def_body(text: str) -> str:
    m = re.search(r"(?m)^definition:[ \t]*>-\n((?:[ \t]+.*\n)+?)definition_source:", text)
    return " ".join(m.group(1).split()) if m else ""


def compose(cur: str) -> str | None:
    m = _PARSE.match(cur)
    if not m:
        return None
    acc, name, cat = m.group(1), m.group(2).strip().rstrip(","), m.group(3).strip()
    s = f"{name} ({acc}) — a eukaryotic orthologous group of proteins (KOG) in NCBI CDD"
    if cat and cat.lower() not in ("function unknown",):
        s += f"; functional category: {cat}"
    return s + "."


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    files = []
    for d in TRAITS.glob("function/*/cdd"):
        files += sorted(d.glob("*.yaml"))

    done = skip = miss = 0
    for p in files:
        text = p.read_text(encoding="utf-8")
        if "trait_category: FUNC_ORTHOLOG_GROUP" not in text:
            continue
        if SOURCE in text:
            skip += 1
            continue
        new_def = compose(def_body(text))
        if not new_def:
            miss += 1
            continue
        block = f"definition: >-\n  {new_def}\ndefinition_source: {SOURCE}"
        new, n = DEF_RE.subn(lambda _m: block, text, count=1)
        if not n:
            miss += 1
            continue
        done += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"CDD ortholog definitions: {'recomposed' if args.apply else 'would recompose'} {done:,} "
          f"| already done {skip:,} | unparsed {miss:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
