#!/usr/bin/env python3
"""Seed epitope traits from the IEDB epitope export → SEQUENCE / SEQ_EPITOPE.

The IEDB epitope table (`epitope_full_v3.csv`) is one row per epitope (already
aggregated across assays), so each row is close to a reusable trait class. To keep
records class-native and groundable, we seed only **linear peptide** epitopes that
carry a **UniProt source-antigen** (`Molecule Parent IRI`) and a clean amino-acid
sequence, capped by `--limit` (the export holds ~2M epitopes). Each epitope class
carries its peptide as `sequence_pattern`, the antigen as an `xref` +
`canonical_example`. Discontinuous/conformational and modified epitopes are
skipped (not a linear-sequence class).

Input (fetch via `just fetch-iedb`, gitignored): the 1 GB
data/raw/iedb/epitope_full_v3.csv (two header rows; streamed, not loaded).
Columns (2nd header): 0 IEDB-IRI, 1 Object-Type, 2 Name(sequence), 4 Modifications,
11 Molecule-Parent, 12 Molecule-Parent-IRI(UniProt), 13 Source-Organism.

Licence: CC-BY 4.0 (IEDB). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV = REPO_ROOT / "data" / "raw" / "iedb" / "epitope_full_v3.csv"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "epitope" / "iedb"
LICENSE = "CC-BY 4.0 (IEDB)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_PEPTIDE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]{5,50}$")   # clean linear peptide
_UNIPROT = re.compile(r"uniprot\.org/uniprot/([A-NR-Z0-9][A-Z0-9.]+)")
_EPID = re.compile(r"/epitope/(\d+)")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "epitope"


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


def build_yaml(epid, seq, antigen, acc, organism):
    label = f"epitope {seq}"
    lines = [f"identifier: IEDB:{epid}", f"label: {yaml_escape(label)}"]
    d = (f"Linear peptide epitope {seq}"
         + (f" from {antigen}" if antigen else "")
         + (f" ({organism})" if organism else "") + ".")
    f = folded(d)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: IEDB (epitope_full_v3)", "trait_axis: SEQUENCE",
              "trait_category: SEQ_EPITOPE", "term_kind: CLASS",
              "mapping_status: SEEDED",
              f"sequence_pattern: {yaml_escape(seq)}"]
    if acc:
        lines += ["xrefs:", f"  - UniProtKB:{acc}",
                  "canonical_examples:", f"  - protein_id: UniProtKB:{acc}"]
        if antigen:
            lines.append(f"    protein_label: {yaml_escape(antigen)}")
        if organism:
            lines.append(f"    taxon_label: {yaml_escape(organism)}")
        lines += ["    note: IEDB source antigen for this epitope",
                  "    source: CURATOR"]
    lines.append(f"license: {yaml_escape(LICENSE)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=20000,
                    help="cap epitope records (export holds ~2M). 0 = all.")
    args = ap.parse_args()
    if not CSV.exists():
        print("missing data/raw/iedb/epitope_full_v3.csv; run `just fetch-iedb`",
              file=sys.stderr)
        return 2

    written = skipped = kept = scanned = 0
    with CSV.open(encoding="utf-8", errors="replace", newline="") as fh:
        r = csv.reader(fh)
        next(r, None); next(r, None)                     # 2 header rows
        for row in r:
            if args.limit and kept >= args.limit:
                break
            if len(row) < 14:
                continue
            scanned += 1
            if row[1] != "Linear peptide" or row[4].strip():  # linear, unmodified
                continue
            seq = row[2].strip().upper()
            if not _PEPTIDE.match(seq):
                continue
            um = _UNIPROT.search(row[12])
            if not um:                                    # require UniProt antigen
                continue
            acc = um.group(1).split(".")[0]
            em = _EPID.search(row[0])
            if not em:
                continue
            epid = em.group(1)
            kept += 1
            path = OUT_DIR / f"{slug(seq)}-iedb{epid}.yaml"
            if path.exists() and not args.force:
                skipped += 1
                continue
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    build_yaml(epid, seq, row[11].strip(), acc, row[13].strip()),
                    encoding="utf-8")
                written += 1

    print(f"IEDB: {kept} linear-peptide epitope classes (UniProt-grounded, capped "
          f"at {args.limit}; scanned {scanned:,} rows) → SEQ_EPITOPE.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {kept - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
