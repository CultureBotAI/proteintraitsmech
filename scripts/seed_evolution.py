#!/usr/bin/env python3
"""Seed evolutionary / pangenome traits (EVOLUTION axis).

A protein's conservation and distribution across taxa is a trait dimension
orthogonal to its own sequence / structure / function: whether it is conserved,
clade-specific, or variable, and — in comparative genomics — which pangenome
partition it belongs to (core / soft-core / shell / cloud / persistent /
singleton). These are class-level assertions ("this protein is a core-genome
protein"), grounded downstream by an NCBITaxon xref when scoped to a clade.

Emits one curator-minted record per term under `data/traits/evolution/`:

  conservation/  EVO_CONSERVED, EVO_CLADE_SPECIFIC, EVO_VARIABLE
  pangenome/     EVO_PANGENOME_{CORE,SOFTCORE,SHELL,CLOUD,PERSISTENT,SINGLETON}

"conserved at taxon rank (id)" is not enumerated — it is an EVO_CONSERVED (or
EVO_CLADE_SPECIFIC) record carrying an `NCBITaxon:` xref for the clade; the
generic terms below are the parents such scoped records attach to.

`mapping_status: SEEDED`; curator-minted `proteintraitsmech:EVO_*` identifiers;
license CC0-1.0. Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "traits" / "evolution"
DEFINITION_SOURCE = "ProteinTraitsMech curated evolutionary/pangenome taxonomy"
LICENSE = "CC0-1.0"

# (category, subdir, label, definition, [synonyms])
TERMS: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
    ("EVO_CONSERVED", "conservation", "conserved protein",
     "A protein that is evolutionarily conserved — orthologues are retained "
     "across multiple taxa. When scoped to a clade, the record carries an "
     "NCBITaxon xref (conserved at that taxon rank).",
     ("conserved", "evolutionarily conserved", "orthologously conserved")),
    ("EVO_CLADE_SPECIFIC", "conservation", "clade-specific protein",
     "A lineage- or clade-specific (taxonomically restricted) protein, present "
     "only within a particular taxon; the NCBITaxon xref gives the clade.",
     ("lineage-specific protein", "taxonomically restricted gene", "orphan gene", "TRG")),
    ("EVO_VARIABLE", "conservation", "variable protein",
     "A variable / hypervariable / fast-evolving protein or region with low "
     "cross-taxon conservation.",
     ("hypervariable protein", "fast-evolving protein", "variable region")),
    ("EVO_PANGENOME_CORE", "pangenome", "core-genome protein",
     "A core-genome protein — present in (nearly) all genomes of a "
     "species/clade pangenome.",
     ("core gene", "core genome protein")),
    ("EVO_PANGENOME_SOFTCORE", "pangenome", "soft-core protein",
     "A soft-core protein — present in most (e.g. >= 95%) genomes of the "
     "pangenome.",
     ("soft-core gene", "softcore protein")),
    ("EVO_PANGENOME_SHELL", "pangenome", "shell protein",
     "A shell / accessory (dispensable) protein — present in a subset of "
     "genomes of the pangenome.",
     ("shell gene", "accessory protein", "dispensable gene")),
    ("EVO_PANGENOME_CLOUD", "pangenome", "cloud protein",
     "A cloud protein — present in only a few genomes of the pangenome (rare "
     "accessory).",
     ("cloud gene", "rare accessory protein")),
    ("EVO_PANGENOME_PERSISTENT", "pangenome", "persistent-genome protein",
     "A persistent-genome protein — the near-core partition in the PPanGGOLiN "
     "pangenome model.",
     ("persistent gene", "persistent genome protein")),
    ("EVO_PANGENOME_SINGLETON", "pangenome", "singleton protein",
     "A singleton / strain-specific protein — present in a single genome of the "
     "pangenome.",
     ("strain-specific protein", "unique gene", "singleton gene")),
)


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    text = " ".join(text.split())
    return [">-", f"  {text}"]


def record(cat: str, label: str, definition: str, synonyms: tuple[str, ...]) -> str:
    lines = [f"identifier: proteintraitsmech:{cat}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append(f"definition_source: {yaml_escape(DEFINITION_SOURCE)}")
    lines.append("trait_axis: EVOLUTION")
    lines.append(f"trait_category: {cat}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if synonyms:
        lines.append("synonyms:")
        for s in synonyms:
            lines.append(f"  - synonym_text: {yaml_escape(s)}")
            lines.append("    synonym_type: EXACT_SYNONYM")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    written = skipped = 0
    for cat, subdir, label, definition, syns in TERMS:
        path = OUT_DIR / subdir / f"{label.replace(' ', '-')}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(record(cat, label, definition, syns), encoding="utf-8")
            written += 1

    print(f"{len(TERMS)} EVOLUTION records.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → {OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(TERMS) - skipped}; {skipped} exist. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
