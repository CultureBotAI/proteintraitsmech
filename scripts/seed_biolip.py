#!/usr/bin/env python3
"""Seed ligand-binding-site trait CLASSES from BioLiP2 → STRUCTURE /
STRUCT_BINDING_SITE.

BioLiP2 (Yang / Zhang group, https://zhanggroup.org/BioLiP/) is a
semi-manually curated database of biologically relevant ligand–protein
interactions. Each flat-file row is one *binding-site occurrence* — a
ligand L bound to a receptor chain in a specific PDB structure. Those
rows are INSTANCES, not reusable trait classes.

  ── MODELLING DECISION ─────────────────────────────────────────────
  This corpus catalogues protein-trait CLASSES, so raw per-PDB rows are
  NOT seeded 1:1. Instead we AGGREGATE the rows by their natural class
  key — the **ligand** (the PDB Chemical Component Dictionary id in
  column 5, e.g. ATP, HEM, ZN; plus BioLiP's polymer pseudo-ligands
  `rna`, `dna`, `peptide`). One STRUCT_BINDING_SITE record is emitted
  per distinct ligand — "ATP-binding site", "heme-binding site",
  "Zn-binding site", "RNA-binding site" — with the per-PDB occurrences
  summarised as `canonical_examples` (capped) and an occurrence /
  PDB-structure count folded into the definition.

  Grounding: chemical ligands are cross-referenced to the PDB Chemical
  Component Dictionary (`pdb.ligand:<CCD>`); the three polymer
  pseudo-ligands are grounded to ChEBI (RNA/DNA/peptide). No ChEBI id
  for small-molecule ligands is present in the source, so we do not
  invent one — the CCD id + ligand name (+ InChIKey in the definition)
  are the on-record identifiers.

  Per-row EC / GO terms describe the *receptor's* function and vary
  across the many unrelated proteins that share a ligand — they are NOT
  class-defining for a ligand-keyed binding-site class, so they are
  deliberately NOT aggregated onto the record (that would be noise).
  ────────────────────────────────────────────────────────────────────

Inputs (fetch via `just fetch-biolip`, gitignored under data/raw/biolip/):
  BioLiP_nr.txt   non-redundant annotation flat file, 21 tab-separated
                  columns (see readme.txt). Columns used:
                    01 PDB ID   02 receptor chain   03 resolution
                    05 ligand CCD id (class key)    06 ligand chain
                    08 binding-site residues (PDB numbering)
                    18 UniProt id(s)  (for canonical_examples)
  ligand.tsv      CCD id → formula / InChI / InChIKey / SMILES / name

⚠ LICENSE: BioLiP2 is free for academic use (Zhang Lab) with NO explicit
open license. The corpus is otherwise CC0-1.0, so every BioLiP record is
stamped with the BioLiP license and FLAGGED. See download.yaml.

Idempotent (skips existing files by path); dry-run unless --apply.
--force overwrites; --min-occurrences N drops ligands seen < N times;
--limit N caps records. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "biolip"
NR_FILE = RAW / "BioLiP_nr.txt"
LIGAND_FILE = RAW / "ligand.tsv"
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "binding_site" / "biolip"

DEFINITION_SOURCE = "BioLiP2 (Yang/Zhang group)"
LICENSE = ("BioLiP2 — free for academic use (Zhang Lab); "
           "no explicit open license (FLAGGED)")

EXAMPLE_CAP = 5

# BioLiP polymer pseudo-ligands → ChEBI groundings + display names.
POLYMER_LIGANDS = {
    "rna": ("CHEBI:33697", "RNA", "an RNA molecule"),
    "dna": ("CHEBI:16991", "DNA", "a DNA molecule"),
    "peptide": ("CHEBI:16670", "peptide", "a peptide"),
}

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_UNIPROT_RE = re.compile(r"^[A-Z0-9]+([-][0-9]+)?$")
_ID_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", (text or "").lower()).strip("-")[:70]) or "site"


def ident_token(ccd: str) -> str:
    """Sanitize a CCD id for use inside a proteintraitsmech: identifier."""
    return _ID_RE.sub("_", ccd).strip("_").upper() or "LIGAND"


def yaml_escape(text: str) -> str:
    if text is None or text == "":
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded(indent: str, text: str) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return [">-", f"{indent}  \"\""]
    return [">-", f"{indent}  {text}"]


def load_ligand_meta() -> dict[str, dict[str, str]]:
    """CCD id → {name, inchikey, formula} from ligand.tsv."""
    meta: dict[str, dict[str, str]] = {}
    if not LIGAND_FILE.exists():
        return meta
    for line in LIGAND_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 6:
            continue
        ccd = cols[0].strip()
        # name column may hold "NAME; synonym" — keep the first, cleanest.
        name = cols[5].split(";")[0].strip()
        meta[ccd] = {
            "name": name,
            "inchikey": cols[3].strip(),
            "formula": cols[1].strip(),
        }
    return meta


class Ligand:
    __slots__ = ("ccd", "occ", "pdb_ids", "examples", "_seen_prot")

    def __init__(self, ccd: str):
        self.ccd = ccd
        self.occ = 0
        self.pdb_ids: set[str] = set()
        self.examples: list[dict[str, str]] = []
        self._seen_prot: set[str] = set()

    def add_row(self, cols: list[str]) -> None:
        self.occ += 1
        pdb = cols[0].strip()
        self.pdb_ids.add(pdb)
        if len(self.examples) >= EXAMPLE_CAP:
            return
        raw_up = cols[17].strip() if len(cols) > 17 else ""
        acc = raw_up.split(",")[0].strip()
        if not acc or not _UNIPROT_RE.match(acc) or acc in self._seen_prot:
            return
        self._seen_prot.add(acc)
        chain = cols[1].strip()
        res = cols[2].strip()
        residues = " ".join(cols[7].split()) if len(cols) > 7 else ""
        if len(residues) > 200:
            residues = residues[:197] + "…"
        note = (f"BioLiP2 binding-site occurrence in PDB {pdb} chain {chain}"
                + (f" (resolution {res} Å)" if res and res != "-1.00" else "")
                + (f"; binding residues: {residues}" if residues else ""))
        self.examples.append({
            "protein_id": f"UniProtKB:{acc}",
            "protein_label": f"{pdb.upper()} chain {chain} (BioLiP receptor)",
            "note": note,
        })


def build_yaml(lig: Ligand, meta: dict[str, dict[str, str]]) -> str:
    ccd = lig.ccd
    n_pdb = len(lig.pdb_ids)
    polymer = POLYMER_LIGANDS.get(ccd)

    if polymer:
        chebi, display, phrase = polymer
        xref = chebi
        name = display
        inchikey = ""
    else:
        info = meta.get(ccd, {})
        name = info.get("name") or ccd
        inchikey = info.get("inchikey") or ""
        display = ccd
        phrase = f"the ligand {name} ({ccd})" if name and name != ccd else f"ligand {ccd}"
        xref = f"pdb.ligand:{ccd}"

    label = f"{display}-binding site"

    occ_txt = (f"{lig.occ} binding-site occurrence"
               f"{'s' if lig.occ != 1 else ''} across {n_pdb} PDB "
               f"structure{'s' if n_pdb != 1 else ''}")
    definition = (f"A structure-derived ligand-binding site at which "
                  f"{phrase} is bound to a receptor protein chain, defined "
                  f"from 3D protein–ligand complexes. BioLiP2 catalogues this "
                  f"binding site over {occ_txt}"
                  + (f"; ligand InChIKey {inchikey}." if inchikey else "."))

    lines: list[str] = [
        f"identifier: proteintraitsmech:BIOLIP_{ident_token(ccd)}",
        f"label: {yaml_escape(label)}",
    ]
    folded = yaml_folded("", definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(DEFINITION_SOURCE)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append("trait_category: STRUCT_BINDING_SITE")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    lines.append("xrefs:")
    lines.append(f"  - {xref}")

    if not polymer and name and name != ccd:
        lines.append("synonyms:")
        lines.append(f"  - synonym_text: {yaml_escape(f'{name}-binding site')}")
        lines.append("    synonym_type: EXACT_SYNONYM")
        lines.append("    source: BioLiP2")

    if lig.examples:
        lines.append("canonical_examples:")
        for ex in lig.examples:
            lines.append(f"  - protein_id: {ex['protein_id']}")
            lines.append(f"    protein_label: {yaml_escape(ex['protein_label'])}")
            lines.append(f"    note: {yaml_escape(ex['note'])}")
            lines.append("    source: CURATOR")

    lines.append(f"license: {yaml_escape(LICENSE)}")
    return "\n".join(lines) + "\n"


def target_path(lig: Ligand) -> Path:
    display = POLYMER_LIGANDS.get(lig.ccd, (None, lig.ccd))[1]
    return OUT_DIR / f"{slugify(display + '-binding-site')}-{lig.ccd.lower()}.yaml"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--min-occurrences", type=int, default=1,
                    help="skip ligands seen fewer than N times (default 1 = keep all)")
    ap.add_argument("--limit", type=int, default=0, help="cap records processed (0 = all)")
    ap.add_argument("--sample", type=int, default=0,
                    help="print the first N built YAMLs to stdout (review aid)")
    args = ap.parse_args()

    if not NR_FILE.exists():
        print(f"missing {NR_FILE.relative_to(REPO_ROOT)}; run `just fetch-biolip`",
              file=sys.stderr)
        return 2

    meta = load_ligand_meta()

    ligands: dict[str, Ligand] = {}
    n_rows = 0
    with NR_FILE.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 6:
                continue
            ccd = cols[4].strip()
            if not ccd:
                continue
            n_rows += 1
            ligands.setdefault(ccd, Ligand(ccd)).add_row(cols)

    kept = [lig for lig in ligands.values() if lig.occ >= args.min_occurrences]
    kept.sort(key=lambda l: (-l.occ, l.ccd))

    # occurrence-count distribution (bucketed)
    buckets = {"1": 0, "2-4": 0, "5-9": 0, "10-49": 0, "50-99": 0, "100+": 0}
    for lig in kept:
        c = lig.occ
        key = ("1" if c == 1 else "2-4" if c <= 4 else "5-9" if c <= 9
               else "10-49" if c <= 49 else "50-99" if c <= 99 else "100+")
        buckets[key] += 1

    written = skipped = planned = 0
    printed = 0
    for i, lig in enumerate(kept):
        if args.limit and i >= args.limit:
            break
        body = build_yaml(lig, meta)
        if args.sample and printed < args.sample:
            print(f"# ---- {target_path(lig).relative_to(REPO_ROOT)} ----")
            print(body)
            printed += 1
        path = target_path(lig)
        if path.exists() and not args.force:
            skipped += 1
            continue
        planned += 1
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
            written += 1

    print(f"\nParsed {n_rows} BioLiP_nr rows → {len(ligands)} distinct ligands "
          f"({len(kept)} kept at --min-occurrences={args.min_occurrences}).")
    print("Occurrence-count distribution (kept ligands):")
    for k in ("1", "2-4", "5-9", "10-49", "50-99", "100+"):
        print(f"  {k:>6} occ : {buckets[k]}")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {planned}; {skipped} already exist. "
              f"Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
