#!/usr/bin/env python3
"""Seed orthologous-group traits from NCBI COG 2020 (US Gov public domain)
→ FUNCTION / FUNC_ORTHOLOG_GROUP.

A COG (Cluster of Orthologous Genes) is a set of orthologues sharing a
conserved function across taxa — an entry-level functional-genomic trait
("belongs to orthologous group COGxxxx"). We seed:
  - the 26 COG **functional categories** (letters J, A, K, …) as parent
    nodes (proteintraitsmech:COG_CATEGORY_<L>), and
  - the ~4,877 individual **COGs** (COG:COGnnnn), each parented to its one
    or more functional categories.

Inputs (fetch via `just fetch-cog`, gitignored):
  data/raw/cog/cog-20.def.tab  "<COG>\\t<cats>\\t<name>\\t<gene>\\t<pathway>\\t…\\t<PDB>"
  data/raw/cog/fun-20.tab      "<letter>\\t<color>\\t<description>"

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "cog"
DEF = RAW / "cog-20.def.tab"
FUN = RAW / "fun-20.tab"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "ortholog_group" / "cog"
LICENSE = "US Government public domain"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "cog"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text): return [">-", f"  {' '.join((text or '').split())}"]


def read_lines(path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def build_category_yaml(letter, desc):
    definition = (f"{desc} — a COG functional category ({letter}); a broad "
                  f"functional class grouping clusters of orthologous genes.")
    lines = [f"identifier: proteintraitsmech:COG_CATEGORY_{letter}",
             f"label: {yaml_escape(desc)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: COG", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED", f"license: {LICENSE}"]
    return "\n".join(lines) + "\n"


def build_cog_yaml(cog, name, cats, gene, pathway):
    extra = f" Functional context: {pathway}." if pathway else ""
    definition = (f"{name} — a cluster of orthologous genes ({cog}); members "
                  f"are orthologues with a conserved function.{extra}")
    lines = [f"identifier: COG:{cog}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: COG", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if gene:
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(gene)}",
                  "    synonym_type: RELATED_SYNONYM",
                  "    source: COG"]
    if cats:
        lines += ["parent_traits:"]
        lines += [f"  - proteintraitsmech:COG_CATEGORY_{c}" for c in cats]
        # A COG is a MEMBER of its functional category (not a subclass).
        lines += ["trait_relations:"]
        for c in cats:
            lines += ["  - predicate: biolink:member_of",
                      f"    object: proteintraitsmech:COG_CATEGORY_{c}",
                      "    relation_source: COG functional category"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not DEF.exists():
        print("missing data/raw/cog/*; run `just fetch-cog`", file=sys.stderr)
        return 2

    categories: dict[str, str] = {}
    if FUN.exists():
        for line in read_lines(FUN):
            parts = line.split("\t")
            if len(parts) >= 3 and len(parts[0].strip()) == 1:
                categories[parts[0].strip()] = parts[2].strip()

    # (slug, builder-args-tuple, kind) planned records.
    plan: list[tuple[str, str]] = []  # (slug, yaml_text)
    for letter, desc in sorted(categories.items()):
        plan.append((f"category-{letter.lower()}",
                     build_category_yaml(letter, desc)))

    n_cogs = 0
    for line in read_lines(DEF):
        cols = line.split("\t")
        if len(cols) < 3 or not cols[0].startswith("COG"):
            continue
        cog = cols[0].strip()
        cats = [c for c in cols[1].strip() if c in categories]
        name = cols[2].strip()
        gene = cols[3].strip() if len(cols) > 3 else ""
        pathway = cols[4].strip() if len(cols) > 4 else ""
        if not name:
            continue
        n_cogs += 1
        plan.append((f"{slugify(name)}-{cog.lower()}",
                     build_cog_yaml(cog, name, cats, gene, pathway)))

    written = skipped = 0
    for slug, text in plan:
        path = OUT_DIR / f"{slug}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    print(f"{len(plan)} COG records "
          f"({len(categories)} functional categories, {n_cogs} COGs).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(plan) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
