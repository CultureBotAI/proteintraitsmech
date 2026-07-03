#!/usr/bin/env python3
"""Materialize Pfam **clan** records (public domain)
→ STRUCTURE / STRUCT_HOMOLOGOUS_SUPERFAMILY.

Pfam families carry `parent_traits: [Pfam:CL…]` (their clan), but the clans
themselves were never seeded — the single biggest source of dangling parents
in the corpus (~13.9k edges; see research/schema-hierarchy-review-1.md). This
seeds one record per clan so those parents resolve. A clan is a superfamily-
grouping of evolutionarily related families, so STRUCT_HOMOLOGOUS_SUPERFAMILY
is its natural home.

Input (from `just fetch-pfam`): data/raw/pfam/Pfam-A.clans.tsv.gz
  columns: pfamA_acc, clan_acc, clan_id, pfamA_id, pfamA_description
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "pfam" / "Pfam-A.clans.tsv.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "homologous_superfamily" / "pfam"
LICENSE = "public domain (Pfam / InterPro)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "clan"


def yaml_escape(text) -> str:
    text = str(text)
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def build_yaml(clan_acc, clan_id):
    label = clan_id or clan_acc
    definition = (f"{clan_id or clan_acc} — a Pfam clan ({clan_acc}); a "
                  f"superfamily grouping of evolutionarily related Pfam "
                  f"families sharing structure/function.")
    lines = [f"identifier: Pfam:{clan_acc}", f"label: {yaml_escape(label)}",
             f"definition: >-", f"  {definition}",
             "definition_source: Pfam (clan)", "trait_axis: STRUCTURE",
             "trait_category: STRUCT_HOMOLOGOUS_SUPERFAMILY",
             "term_kind: CLASS", "mapping_status: SEEDED",
             f"license: {LICENSE}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/pfam/Pfam-A.clans.tsv.gz; run `just fetch-pfam`",
              file=sys.stderr)
        return 2

    clans: dict[str, str] = {}
    with gzip.open(RAW, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) >= 3 and c[1].strip():
                clans[c[1].strip()] = c[2].strip()

    written = skipped = 0
    for clan_acc, clan_id in sorted(clans.items()):
        path = OUT_DIR / f"{slugify(clan_id)}-{clan_acc.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(clan_acc, clan_id), encoding="utf-8")
            written += 1

    print(f"{len(clans)} Pfam clans → STRUCT_HOMOLOGOUS_SUPERFAMILY.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(clans) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
