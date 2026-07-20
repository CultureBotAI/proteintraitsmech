#!/usr/bin/env python3
"""Seed orthologous-group traits from OrthoDB v12 → FUNCTION / FUNC_ORTHOLOG_GROUP.

An OrthoDB orthologous group (OG) is a set of orthologues at a taxonomic level — a
reusable, class-level conserved-function trait, exactly like a COG (see seed_cog).
This is the round-4 EVOLUTION-gap flagship. OrthoDB has millions of OGs across all
NCBI levels, so we **scope by level** (`--level`, default the broad domain clades
Bacteria/Archaea/Eukaryota/Viruses → ~32k OGs). Each OG is a CLASS parented (via
`biolink:member_of`) to a minted per-level node, mirroring seed_cog's
COG-functional-category tier.

Inputs (fetch via `just fetch-orthodb`, gitignored):
  data/raw/orthodb/odb12v2_OGs.tab.gz     — <OG_id>\\t<level_taxid>\\t<OG_name>
  data/raw/orthodb/odb12v2_levels.tab.gz  — <level_taxid>\\t<name>\\t…

Licence: CC-BY 4.0 (OrthoDB). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "orthodb"
OGS = RAW / "odb12v2_OGs.tab.gz"
LEVELS = RAW / "odb12v2_levels.tab.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "ortholog_group" / "orthodb"
LICENSE = "CC-BY 4.0 (OrthoDB)"
DEFAULT_LEVELS = {"2", "2157", "2759", "10239"}   # Bacteria, Archaea, Eukaryota, Viruses
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "og"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}
            or re.fullmatch(r"-?\d+(?:\.\d+)?", text)):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def load_levels():
    out = {}
    if LEVELS.exists():
        with gzip.open(LEVELS, "rt", errors="replace") as fh:
            for line in fh:
                c = line.rstrip("\n").split("\t")
                if len(c) >= 2:
                    out[c[0]] = c[1]
    return out


def level_rid(taxid): return f"proteintraitsmech:ORTHODB_LEVEL_{taxid}"


def build_level(taxid, name):
    lines = [f"identifier: {level_rid(taxid)}",
             f"label: {yaml_escape(f'{name} orthologous groups (OrthoDB)')}"]
    f = folded(f"OrthoDB orthologous groups defined at the {name} "
               f"(NCBITaxon:{taxid}) taxonomic level.")
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: OrthoDB v12", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED", "xrefs:", f"  - NCBITaxon:{taxid}",
              f"license: {yaml_escape(LICENSE)}"]
    return "\n".join(lines) + "\n"


def build_og(og_id, name, taxid, level_name):
    label = name or og_id
    lines = [f"identifier: OrthoDB:{og_id}", f"label: {yaml_escape(label)}"]
    f = folded(f"{label} — an OrthoDB orthologous group at the {level_name} level.")
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: OrthoDB v12", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED",
              "parent_traits:", f"  - {level_rid(taxid)}",
              "trait_relations:", "  - predicate: biolink:member_of",
              f"    object: {level_rid(taxid)}", "    relation_source: OrthoDB level",
              f"license: {yaml_escape(LICENSE)}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--level", default=",".join(sorted(DEFAULT_LEVELS)),
                    help="comma list of NCBI level taxids to seed (default broad clades)")
    ap.add_argument("--limit", type=int, default=20000,
                    help="cap total OG records (the domain levels hold ~1.5M OGs; "
                         "this seeds a bounded, named representative slice). 0 = all.")
    args = ap.parse_args()
    if not OGS.exists():
        print("missing data/raw/orthodb/odb12v2_OGs.tab.gz; run `just fetch-orthodb`",
              file=sys.stderr)
        return 2
    levels = set(x.strip() for x in args.level.split(",") if x.strip())
    level_names = load_levels()
    written = skipped = ogs = unnamed = 0

    def emit(fname, text):
        nonlocal written, skipped
        path = OUT_DIR / fname
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    # per-level parent nodes
    for tx in sorted(levels):
        emit(f"orthodb-level-{tx}.yaml", build_level(tx, level_names.get(tx, tx)))

    with gzip.open(OGS, "rt", errors="replace") as fh:
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) < 2 or c[1] not in levels:
                continue
            og_id, taxid = c[0], c[1]
            name = (c[2] if len(c) > 2 else "").strip()
            # Prefer functionally-named OGs; skip unnamed / hypothetical.
            if not name or name.lower() in ("hypothetical protein", "uncharacterized protein"):
                unnamed += 1
                continue
            if args.limit and ogs >= args.limit:
                break
            ogs += 1
            emit(f"{slug(name)}-{slug(og_id)}.yaml",
                 build_og(og_id, name, taxid, level_names.get(taxid, taxid)))

    cap = f" (capped at --limit {args.limit}; skipped {unnamed:,} unnamed)" if args.limit else ""
    print(f"OrthoDB: {ogs} named OGs at levels {sorted(levels)} + {len(levels)} level "
          f"nodes → FUNC_ORTHOLOG_GROUP{cap}.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {ogs + len(levels) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
