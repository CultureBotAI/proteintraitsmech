#!/usr/bin/env python3
"""Seed the secondary-structure (2°) trait taxonomy — elements, arrangements,
turns/bends, local motifs, and super-secondary motifs — under
data/traits/structure/secondary/ (STRUCT_SECONDARY).

Now that 2° and 3° structure share the STRUCTURE axis, the class-level 2°
taxonomy was near-empty (only 8 generic motifs) and had no *representation* to
compare across sources. This seeder materializes the taxonomy recommended in
research/cross-source-comparison-review-1.md and gives each record a
`secondary_structure_representations` block (DSSP/STRIDE state + normalised
SS-element topology string) — the comparable 2D representation.

Grounding: DSSP 8-state codes (H,G,I,E,B,T,S,P,C) live in the representation;
SO / LocalStructuralFeature xrefs ground the motif classes where available.
Idempotent (writes by path); dry-run by default, `--apply` to write, `--force`
to overwrite existing seeded records (e.g. to enrich the original 8).
Stdlib-only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "secondary"
PFX = "proteintraitsmech:"
LSF = "https://linkml.io/valuesets/elements/LocalStructuralFeature/"
DSSP = "DSSP (Kabsch & Sander 1983; mkdssp)"

# family → parent identifier suffix (roots have parent None)
ROOTS = {
    "SECONDARY_STRUCTURE_ELEMENT": "Elementary secondary-structure state assigned "
        "per residue (DSSP/STRIDE): helices, strands, bridges, turns, bends, coil.",
    "SECONDARY_STRUCTURE_ARRANGEMENT": "An arrangement of secondary-structure "
        "elements (e.g. a beta sheet: several strands hydrogen-bonded in a defined "
        "pairing topology).",
    "SUPER_SECONDARY_MOTIF": "A super-secondary (motif-level) grouping of a few "
        "secondary-structure elements with a characteristic topology, smaller than "
        "a domain.",
    # POLYPEPTIDE_STRUCTURAL_MOTIF already exists (parent for local motifs).
}

# each: (SUFFIX, label, definition, parent_suffix, alphabet, topology, xrefs)
TAXON = [
    # ---- elementary states (DSSP) ----
    ("ALPHA_HELIX", "alpha helix", "Right-handed alpha helix (DSSP H); ~3.6 residues per turn, i→i+4 hydrogen bonds.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "H", []),
    ("THREE_TEN_HELIX", "3-10 helix", "3_10 helix (DSSP G); tighter helix with i→i+3 hydrogen bonds.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "G", []),
    ("PI_HELIX", "pi helix", "Pi helix (DSSP I); wider helix with i→i+5 hydrogen bonds.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "I", []),
    ("PPII_HELIX", "polyproline II helix", "Left-handed polyproline II helix; extended 3-fold helix, not a standard DSSP core state.", "SECONDARY_STRUCTURE_ELEMENT", "TOPOLOGY", "P", []),
    ("BETA_STRAND", "beta strand", "Extended beta strand (DSSP E); participates in beta sheets via backbone hydrogen bonds.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "E", []),
    ("BETA_BRIDGE", "beta bridge", "Isolated beta bridge (DSSP B); a single residue pair in beta conformation.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "B", []),
    ("TURN", "turn", "Hydrogen-bonded turn (DSSP T); reverses chain direction over a few residues.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "T", []),
    ("BEND", "bend", "Bend (DSSP S); a region of high backbone curvature without regular hydrogen bonding.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_8", "S", []),
    ("LOOP_COIL", "loop / coil", "Irregular coil / loop (DSSP blank or 3-state C); residual state, not a regular element.", "SECONDARY_STRUCTURE_ELEMENT", "DSSP_3", "C", []),
    # ---- turn subtypes ----
    ("BETA_TURN", "beta turn", "Four-residue turn reversing the chain, often i→i+3 hydrogen bonded; the commonest turn.", "TURN", "TOPOLOGY", "turn", []),
    ("GAMMA_TURN", "gamma turn", "Three-residue turn with an i→i+2 hydrogen bond.", "TURN", "TOPOLOGY", "turn", []),
    ("ALPHA_TURN", "alpha turn", "Five-residue turn (i→i+4) linking secondary-structure elements.", "TURN", "TOPOLOGY", "turn", []),
    ("PI_TURN", "pi turn", "Six-residue turn (i→i+5).", "TURN", "TOPOLOGY", "turn", []),
    # ---- arrangements ----
    ("BETA_SHEET", "beta sheet", "Several beta strands hydrogen-bonded side by side (parallel, antiparallel, or mixed) forming a pleated sheet.", "SECONDARY_STRUCTURE_ARRANGEMENT", "TOPOLOGY", "E+", []),
    # ---- super-secondary motifs ----
    ("BETA_MEANDER", "beta meander", "Antiparallel beta sheet of sequence-adjacent strands connected by hairpin loops.", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "E-turn-E-turn-E", []),
    ("GREEK_KEY", "Greek key motif", "Four-stranded antiparallel beta motif with a characteristic connectivity (three adjacent strands plus a fourth folded back).", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "E-E-E-E(greek-key)", []),
    ("JELLY_ROLL", "jelly roll motif", "Eight-stranded beta-sandwich motif of two four-stranded sheets (a wrapped Greek-key elaboration).", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "beta-sandwich", []),
    ("BETA_ALPHA_BETA", "beta-alpha-beta motif", "Two parallel beta strands connected by an alpha helix packed against the sheet (the Rossmann building block).", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "E-H-E", []),
    ("HELIX_TURN_HELIX", "helix-turn-helix", "Two alpha helices joined by a short turn; a recurrent DNA-binding motif.", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "H-turn-H", []),
    ("HELIX_LOOP_HELIX", "helix-loop-helix", "Two alpha helices connected by a loop (distinct from coiled-coil bHLH usage); umbrella for EF-hand-like motifs.", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "H-loop-H", []),
    ("EF_HAND", "EF-hand", "Helix-loop-helix motif whose loop chelates a calcium ion; a super-secondary motif with a metal-binding role.", "HELIX_LOOP_HELIX", "TOPOLOGY", "H-loop(Ca)-H", []),
    ("HELIX_HAIRPIN_HELIX", "helix-hairpin-helix", "Two helices connected by a hairpin, a specialised helix-loop-helix (e.g. in DNA-repair proteins).", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "H-hairpin-H", []),
    ("ALPHA_ALPHA_CORNER", "alpha-alpha corner", "Two nearly antiparallel helices packed at a corner via a short connection.", "SUPER_SECONDARY_MOTIF", "TOPOLOGY", "H-H(corner)", []),
    # ---- local motifs (enrich existing 8; parent POLYPEPTIDE_STRUCTURAL_MOTIF) ----
    ("BETA_HAIRPIN", "beta hairpin", "Two adjacent antiparallel beta strands connected by a short loop or turn.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "E-turn-E", ["valuesets:LocalStructuralFeature", "SO:0001114"]),
    ("BETA_BULGE", "beta bulge", "A local disruption of beta-sheet hydrogen bonding inserting one or two residues into a strand.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "E(bulge)", ["SO:0001107", "valuesets:LocalStructuralFeature", "SO:0001114"]),
    ("HELIX_CAP", "helix cap", "N-cap / C-cap residues terminating an alpha helix with characteristic backbone/side-chain hydrogen bonds.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "Ncap|Ccap", ["valuesets:LocalStructuralFeature", "SO:0001114"]),
    ("KINK", "kink", "A local bend interrupting an alpha helix.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "H(kink)", ["valuesets:LocalStructuralFeature", "SO:0001114"]),
    ("ASX_MOTIF", "asx motif", "Asn/Asp side-chain-nucleated ~5-residue N-terminal-cap-like motif mimicking a helix cap.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "asx", ["SO:0001106", "valuesets:LocalStructuralFeature", "SO:0001114"]),
    ("NEST", "nest", "Three-residue anion-binding backbone concavity.", "POLYPEPTIDE_STRUCTURAL_MOTIF", "TOPOLOGY", "nest", ["SO:0001120", "valuesets:LocalStructuralFeature", "SO:0001114"]),
]


def slug(sfx: str) -> str:
    return sfx.lower().replace("_", "-")


def folded(text: str) -> str:
    return ">-\n  " + text


def emit(rec: dict) -> str:
    lines = [
        f"identifier: {rec['identifier']}",
        f"label: {rec['label']}",
        f"definition: {folded(rec['definition'])}",
        f"definition_source: {rec['definition_source']}",
        "trait_axis: STRUCTURE",
        "trait_category: STRUCT_SECONDARY",
        "term_kind: CLASS",
        "mapping_status: SEEDED",
    ]
    if rec.get("parent"):
        lines += ["parent_traits:", f"- {rec['parent']}"]
    if rec.get("xrefs"):
        lines.append("xrefs:")
        lines += [f"- {x}" for x in rec["xrefs"]]
    if rec.get("rep"):
        r = rec["rep"]
        lines.append("secondary_structure_representations:")
        lines.append(f"- method: {r['method']}")
        lines.append(f"  state_alphabet: {r['alphabet']}")
        if r.get("topology"):
            lines.append(f"  topology_string: {yaml_scalar(r['topology'])}")
        lines.append(f"  evidence_source: {r['evidence_source']}")
    return "\n".join(lines) + "\n"


def yaml_scalar(s: str) -> str:
    # quote topology strings that contain YAML-special chars
    if any(c in s for c in ":|>#&*!%@`{}[],") or s != s.strip():
        return '"' + s.replace('"', '\\"') + '"'
    return s


def build_records() -> list[dict]:
    recs = []
    for sfx, definition in ROOTS.items():
        recs.append({
            "identifier": PFX + sfx,
            "label": sfx.replace("_", " ").lower(),
            "definition": definition,
            "definition_source": "research/cross-source-comparison-review-1.md",
            "parent": None,
            "xrefs": ["valuesets:LocalStructuralFeature", "SO:0001114"],
            "rep": None,
            "path": OUT_DIR / f"{slug(sfx)}.yaml",
        })
    for sfx, label, definition, parent, alph, topo, xrefs in TAXON:
        recs.append({
            "identifier": PFX + sfx,
            "label": label,
            "definition": definition,
            "definition_source": (LSF if xrefs and "valuesets:LocalStructuralFeature" in xrefs else DSSP),
            "parent": PFX + parent if parent else None,
            "xrefs": xrefs,
            "rep": {"method": "curated", "alphabet": alph, "topology": topo,
                    "evidence_source": "research/cross-source-comparison-review-1.md"},
            "path": OUT_DIR / f"{slug(sfx)}.yaml",
        })
    return recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing seeded records")
    args = ap.parse_args()

    recs = build_records()
    created = enriched = skipped = 0
    for rec in recs:
        path = rec["path"]
        exists = path.exists()
        if exists and not args.force:
            skipped += 1
            continue
        if args.apply:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(emit(rec), encoding="utf-8")
        if exists:
            enriched += 1
        else:
            created += 1
        print(f"  {'ENRICH' if exists else 'CREATE'} {path.relative_to(REPO_ROOT)}")

    verb = "wrote" if args.apply else "would write"
    print(f"\n{verb} {created} new + {enriched} enriched, {skipped} skipped "
          f"({len(recs)} taxonomy records). "
          + ("" if args.apply else "Dry-run — pass --apply (and --force to enrich the 8)."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
