#!/usr/bin/env python3
"""Seed metabolic/signalling pathway traits from Reactome (CC0).

Reactome is a curated pathway knowledgebase. Its pathways are curated for human
and projected to other species, so we seed the **Homo sapiens** set as the
species-agnostic reference (~2,900 pathways), parent-chained by the Reactome
pathway hierarchy → FUNCTION / FUNC_PATHWAY.

Inputs (fetch via `just fetch-reactome`, gitignored):
  data/raw/reactome/ReactomePathways.txt          "<id>\\t<name>\\t<species>"
  data/raw/reactome/ReactomePathwaysRelation.txt  "<parent>\\t<child>"

Each record: identifier Reactome:R-HSA-nnnnn, FUNCTION / FUNC_PATHWAY, parent
from the relation file. Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "reactome"
PATHWAYS = RAW / "ReactomePathways.txt"
RELATION = RAW / "ReactomePathwaysRelation.txt"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "pathway" / "reactome"
LICENSE = "CC0"
SPECIES = "Homo sapiens"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "pathway"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text): return [">-", f"  {' '.join((text or '').split())}"]


def build_yaml(rid, name, parent):
    definition = (f"{name} — a Reactome pathway; the protein participates in "
                  f"this metabolic/signalling pathway ({rid}).")
    lines = [f"identifier: Reactome:{rid}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: Reactome", "trait_axis: FUNCTION",
              "trait_category: FUNC_PATHWAY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - Reactome:{parent}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not PATHWAYS.exists():
        print("missing data/raw/reactome/*; run `just fetch-reactome`", file=sys.stderr)
        return 2

    parent_of = {}
    if RELATION.exists():
        for line in RELATION.read_text(encoding="utf-8", errors="replace").splitlines():
            p = line.split("\t")
            if len(p) == 2 and p[1].startswith("R-HSA-"):
                parent_of[p[1].strip()] = p[0].strip()

    written = skipped = 0
    total = 0
    for line in PATHWAYS.read_text(encoding="utf-8", errors="replace").splitlines():
        cols = line.split("\t")
        if len(cols) < 3 or cols[2].strip() != SPECIES:
            continue
        rid, name = cols[0].strip(), cols[1].strip()
        if not rid or not name:
            continue
        total += 1
        parent = parent_of.get(rid, "")
        path = OUT_DIR / f"{slugify(name)}-{rid.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(rid, name, parent), encoding="utf-8")
            written += 1

    print(f"{total} Homo sapiens Reactome pathways → FUNC_PATHWAY.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → {OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
