#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs under data/traits/structure/ from the
LinkML valuesets `LocalStructuralFeature` enumeration.

Source:
  https://linkml.io/valuesets/elements/LocalStructuralFeature/

Behaviour:
  - Default: dry-run — print per-term action and per-category counts.
  - --apply: write YAMLs.
  - --force: overwrite existing YAMLs when applying (default preserves them).

Stdlib-only (no PyYAML dep) — YAML is templated as text so a fresh checkout
can seed before `just install`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "traits" / "structure"

SOURCE_ENUM = "valuesets:LocalStructuralFeature"
SOURCE_URL = "https://linkml.io/valuesets/elements/LocalStructuralFeature/"
DEFINITION_SOURCE = SOURCE_URL

PARENT_MOTIF = "proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF"

# Terms which are conceptually sub-motifs of POLYPEPTIDE_STRUCTURAL_MOTIF —
# small, recurring 3D structural elements that don't form a globular unit.
CHILD_MOTIFS = {
    "BETA_HAIRPIN",
    "BETA_BULGE",
    "ASX_MOTIF",
    "NEST",
    "COILED_COIL",
    "HELIX_CAP",
    "KINK",
    "ELBOW",
}

# One entry per permissible value on the source enum.
# subdir is the directory under data/traits/structure/ (kept short by dropping
# the redundant STRUCT_ prefix from the category enum value).
TERMS = [
    {
        "term": "POLYPEPTIDE_STRUCTURAL_MOTIF",
        "label": "polypeptide structural motif",
        "definition": "A recurring 3D structural element within the chain that does not form a stable globular unit.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001079",
    },
    {
        "term": "BETA_HAIRPIN",
        "label": "beta hairpin",
        "definition": "Two adjacent antiparallel beta strands connected by a short loop or turn.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "BETA_BULGE",
        "label": "beta bulge",
        "definition": "A local disruption of beta-sheet hydrogen bonding across three residues.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001107",
    },
    {
        "term": "ASX_MOTIF",
        "label": "asx motif",
        "definition": "A five-residue motif nucleated by an Asp/Asn side chain (Asx).",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001106",
    },
    {
        "term": "NEST",
        "label": "nest",
        "definition": "A motif of two consecutive residues forming an anion-binding concavity.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001120",
    },
    {
        "term": "COILED_COIL",
        "label": "coiled coil",
        "definition": "Two or more alpha helices wound together like strands of a rope.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": "SO:0001080",
    },
    {
        "term": "HELIX_CAP",
        "label": "helix cap",
        "definition": "N-cap or C-cap residue terminating an alpha helix.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "KINK",
        "label": "kink",
        "definition": "A localized bend interrupting the regular geometry of a helix.",
        "category": "STRUCT_SECONDARY",
        "subdir": "secondary",
        "so_xref": None,
    },
    {
        "term": "CATALYTIC_RESIDUE",
        "label": "catalytic residue",
        "definition": "An amino acid residue directly involved in enzyme catalysis (active site).",
        "category": "STRUCT_ACTIVE_SITE",
        "subdir": "active_site",
        "so_xref": "SO:0001104",
    },
    {
        "term": "PROTEIN_BINDING_SITE",
        "label": "protein binding site",
        "definition": "A site that interacts selectively and non-covalently with polypeptide molecules.",
        "category": "STRUCT_BINDING_SITE",
        "subdir": "binding_site",
        "so_xref": "SO:0000410",
    },
    {
        "term": "DISULFIDE_BOND",
        "label": "disulfide bond",
        "definition": "A covalent S-S bond between two cysteine residues.",
        "category": "STRUCT_DISULFIDE",
        "subdir": "disulfide",
        "so_xref": None,
    },
    {
        "term": "METAL_BINDING_SITE",
        "label": "metal binding site",
        "definition": "A local site coordinating one or more metal ions.",
        "category": "STRUCT_METAL_SITE",
        "subdir": "metal_site",
        "so_xref": None,
    },
    {
        "term": "POCKET",
        "label": "pocket",
        "definition": "A concave, solvent-accessible surface depression that can accommodate a ligand.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "CLEFT",
        "label": "cleft",
        "definition": "An elongated surface groove between structural elements or domains.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "CAVITY",
        "label": "cavity",
        "definition": "An enclosed, solvent-inaccessible internal void within the structure.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "TUNNEL",
        "label": "tunnel",
        "definition": "An elongated, often buried, passage through the structure connecting two regions.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "GROOVE",
        "label": "groove",
        "definition": "A surface channel, e.g. a nucleic-acid-binding groove.",
        "category": "STRUCT_CAVITY",
        "subdir": "cavity",
        "so_xref": None,
    },
    {
        "term": "ELBOW",
        "label": "elbow",
        "definition": "A localized bend or hinge between two structural elements or domains.",
        "category": "STRUCT_DYNAMICS",
        "subdir": "dynamics",
        "so_xref": None,
    },
    {
        "term": "INTERFACE",
        "label": "interface",
        "definition": "A surface patch mediating contact with another chain or molecule.",
        "category": "STRUCT_INTERFACE",
        "subdir": "interface",
        "so_xref": None,
    },
]


def slug_for(term: str) -> str:
    return term.lower().replace("_", "-")


def yaml_for(entry: dict) -> str:
    lines: list[str] = []
    lines.append(f"identifier: proteintraitsmech:{entry['term']}")
    lines.append(f"label: {entry['label']}")
    lines.append("definition: >-")
    lines.append(f"  {entry['definition']}")
    lines.append(f"definition_source: {DEFINITION_SOURCE}")
    lines.append("trait_axis: STRUCTURE")
    lines.append(f"trait_category: {entry['category']}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    if entry["term"] in CHILD_MOTIFS:
        lines.append("parent_traits:")
        lines.append(f"  - {PARENT_MOTIF}")

    xrefs: list[str] = []
    if entry.get("so_xref"):
        xrefs.append(entry["so_xref"])
    xrefs.append(SOURCE_ENUM)
    lines.append("xrefs:")
    for x in xrefs:
        lines.append(f"  - {x}")

    return "\n".join(lines) + "\n"


def target_path(entry: dict) -> Path:
    return DATA_DIR / entry["subdir"] / f"{slug_for(entry['term'])}.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files when applying")
    args = parser.parse_args()

    counts: dict[str, int] = {}
    written = 0
    skipped = 0
    would_overwrite = 0

    for entry in TERMS:
        path = target_path(entry)
        rel = path.relative_to(REPO_ROOT)
        counts[entry["category"]] = counts.get(entry["category"], 0) + 1

        if path.exists() and not args.force:
            action = "SKIP (exists)"
            skipped += 1
        elif path.exists() and args.force:
            action = "OVERWRITE" if args.apply else "would-overwrite"
            if args.apply:
                path.write_text(yaml_for(entry))
                written += 1
            else:
                would_overwrite += 1
        else:
            action = "WRITE" if args.apply else "would-write"
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(yaml_for(entry))
                written += 1

        print(f"  [{action:16s}] {rel}")

    print()
    print("Per-category totals:")
    for cat, n in sorted(counts.items()):
        print(f"  {cat:22s} {n}")
    print()
    if args.apply:
        print(f"Wrote {written} file(s); skipped {skipped} existing.")
    else:
        planned = len(TERMS) - skipped
        print(f"Dry-run — would write {planned} file(s); {skipped} already exist.")
        if would_overwrite:
            print(f"  (of which {would_overwrite} would be overwritten by --force)")
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
