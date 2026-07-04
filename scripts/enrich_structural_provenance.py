#!/usr/bin/env python3
"""Backfill provenance on structure-classification records (record-sample-review-1
S2 + S3): `structural_geometry_representations` on CATH/ECOD, and the per-record
`license` on SCOPe/ECOD/PROSITE-ProRule.

The reps come straight off each record's existing representative-domain xref — no
network, no compute (the analog of `build_structural_equivalence.py --enrich-ted`,
which does the same for TED AlphaFold reps):

  CATH:<pdb><chain><dom>  (e.g. CATH:5fokA02)  -> PDB:5fok, chain A
  ECOD:e<pdb><chain><dom> (e.g. ECOD:e2f2aB1)  -> PDB:2f2a, chain B

SCOPe seeded nodes carry no representative px/domain sid, so they get a license
only (no geometry rep). Licenses (schema: set `license` when the source is
tighter than the CC0-1.0 corpus default):
  SCOPe   -> CC-BY 4.0                    (download.yaml)
  ECOD    -> free for academic use (ECOD) (download.yaml: free / academic)
  PROSITE -> CC BY-NC-ND 4.0 (SIB)        (ProRule domain records; matches PROSITE)

Idempotent (skips a record that already has the slot); dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"

ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
LICENSE_RE = re.compile(r"^license:", re.M)
GEO_RE = re.compile(r"^structural_geometry_representations:", re.M)
CATH_DOM_RE = re.compile(r"\bCATH:(([0-9][0-9a-zA-Z]{3})([A-Za-z0-9])[0-9]{2})\b")
ECOD_DOM_RE = re.compile(r"\bECOD:(e([0-9][0-9a-zA-Z]{3})([A-Za-z]+)\d+)\b")

LICENSE = {
    "SCOP": "CC-BY 4.0",
    "ECOD": "free for academic use (ECOD)",
    "PROSITE": "CC BY-NC-ND 4.0 (SIB)",
}


def geo_block(source: str, domain: str, pdb: str, chain: str) -> str:
    return "\n".join([
        "structural_geometry_representations:",
        f"- structure_ref: PDB:{pdb}",
        f"  structure_source: {source}",
        f"  evidence_source: {source} representative domain {domain} (chain {chain})",
    ]) + "\n"


def enrich(text: str) -> tuple[str, list[str]]:
    """Return (new_text, [actions]). Adds geo rep (CATH/ECOD) and/or license."""
    mid = ID_RE.search(text)
    if not mid:
        return text, []
    prefix = mid.group(1).split(":", 1)[0]
    actions = []
    new = text

    # --- geometry representation (CATH / ECOD) ---
    if not GEO_RE.search(new):
        dom = None
        if prefix == "CATH":
            m = CATH_DOM_RE.search(new)
            if m:
                dom = ("CATH", m.group(1), m.group(2).lower(), m.group(3))
        elif prefix == "ECOD":
            m = ECOD_DOM_RE.search(new)
            if m:
                dom = ("ECOD", m.group(1), m.group(2).lower(), m.group(3))
        if dom:
            block = geo_block(*dom)
            if LICENSE_RE.search(new):
                new = LICENSE_RE.sub(block + "license:", new, count=1)
            else:
                new = new.rstrip("\n") + "\n" + block
            actions.append(f"geo:{dom[0]}")

    # --- license (SCOPe / ECOD / PROSITE) where missing ---
    if prefix in LICENSE and not LICENSE_RE.search(new):
        new = new.rstrip("\n") + "\n" + f"license: {LICENSE[prefix]}\n"
        actions.append(f"license:{prefix}")

    return new, actions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    roots = [TRAITS / "structure",
             TRAITS / "sequence" / "domain" / "prosite",
             TRAITS / "sequence" / "prorule"]
    tally = Counter()
    touched = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8", errors="replace")
            new, actions = enrich(text)
            if not actions:
                continue
            touched += 1
            for a in actions:
                tally[a] += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")

    verb = "enriched" if args.apply else "would enrich"
    print(f"{verb} {touched:,} records:")
    for a, n in sorted(tally.items()):
        print(f"  {a:22s} {n:>7,}")
    if not args.apply:
        print("Pass --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
