#!/usr/bin/env python3
"""Build docs/data/chebi.json — a compact ChEBI lookup for the browser.

The corpus stores chemistry as `chemical_participants` (ChEBI id + role) on
FUNCTION traits; molecular formula / InChIKey / canonical name are NOT copied
per-record (bloat + scale). This script resolves them once, for only the
ChEBI ids the corpus actually references, into a single small sidecar the
browser lazy-loads:

  {"CHEBI:29033": {"name": "iron(2+)", "formula": "Fe", "inchikey": "..."}}

Inputs (fetch via `just fetch-chebi`, gitignored) from ChEBI flat_files:
  data/raw/chebi/compounds.tsv.gz      id ↔ chebi_accession, name
  data/raw/chebi/chemical_data.tsv.gz  compound_id → formula
  data/raw/chebi/structures.tsv.gz     compound_id → standard_inchi_key, smiles

Unlike the other build step this sidecar needs the (large) ChEBI dumps, so it
is a separate script and its output docs/data/chebi.json is committed (small),
rather than rebuilt in CI. Stdlib-only. Idempotent.
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
from pathlib import Path

# ChEBI's structures.tsv embeds multi-line, tab-containing molfiles in quoted
# fields, so a naive line/split parse corrupts every row after the first
# molfile. csv.reader with a large field-size limit parses it correctly.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
RAW = REPO_ROOT / "data" / "raw" / "chebi"
OUT = REPO_ROOT / "docs" / "data" / "chebi.json"


def referenced_chebi() -> set[str]:
    """Distinct CHEBI CURIEs used in any record's chemical_participants."""
    ids: set[str] = set()
    for p in TRAITS.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8", errors="replace")
        if "chebi: CHEBI:" not in t:
            continue
        for line in t.splitlines():
            s = line.strip().lstrip("- ").strip()
            if s.startswith("chebi: CHEBI:"):
                ids.add(s.split("chebi:", 1)[1].strip())
    return ids


def _cols(path: Path):
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        idx = {c: i for i, c in enumerate(header)}
        for row in reader:
            yield idx, row


def main() -> int:
    if not (RAW / "compounds.tsv.gz").exists():
        print("missing data/raw/chebi/*; run `just fetch-chebi`", file=sys.stderr)
        return 2
    want = referenced_chebi()
    print(f"{len(want)} ChEBI ids referenced by the corpus")
    if not want:
        OUT.write_text("{}\n")
        return 0

    # compounds: chebi_accession (CHEBI:n) → internal id + name, for wanted ids.
    internal_to_chebi: dict[str, str] = {}
    out: dict[str, dict] = {}
    for idx, row in _cols(RAW / "compounds.tsv.gz"):
        try:
            acc = row[idx["chebi_accession"]]
        except (IndexError, KeyError):
            continue
        if acc in want:
            internal = row[idx["id"]]
            name = row[idx["name"]] or row[idx.get("ascii_name", idx["name"])]
            out[acc] = {"name": name}
            internal_to_chebi[internal] = acc
    print(f"resolved {len(out)} in compounds")

    # chemical_data: compound_id → formula (first non-empty FORMULA wins).
    for idx, row in _cols(RAW / "chemical_data.tsv.gz"):
        cid = row[idx["compound_id"]] if idx.get("compound_id", -1) < len(row) else None
        if cid in internal_to_chebi:
            formula = row[idx["formula"]] if idx["formula"] < len(row) else ""
            if formula and "formula" not in out[internal_to_chebi[cid]]:
                out[internal_to_chebi[cid]]["formula"] = formula

    # structures: compound_id → InChIKey (+ SMILES).
    for idx, row in _cols(RAW / "structures.tsv.gz"):
        ci = idx.get("compound_id", -1)
        if ci < 0 or ci >= len(row):
            continue
        cid = row[ci]
        if cid not in internal_to_chebi:
            continue
        rec = out[internal_to_chebi[cid]]
        ik = idx.get("standard_inchi_key", -1)
        if 0 <= ik < len(row) and row[ik] and "inchikey" not in rec:
            rec["inchikey"] = row[ik]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":"), sort_keys=True) + "\n",
                   encoding="utf-8")
    n_form = sum(1 for v in out.values() if v.get("formula"))
    n_ik = sum(1 for v in out.values() if v.get("inchikey"))
    print(f"wrote {OUT.relative_to(REPO_ROOT)}: {len(out)} entries "
          f"({n_form} formula, {n_ik} InChIKey), {OUT.stat().st_size//1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
