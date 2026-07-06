#!/usr/bin/env python3
"""Seed structural tandem-repeat traits from RepeatsDB (CC-BY 4.0)
→ SEQUENCE_STRUCTURE / MIXED_STRUCTURAL_REPEAT.

RepeatsDB classifies protein regions with **demonstrated 3D periodicity** in a
Class → Topology → Fold → Clan hierarchy (123 nodes). Unlike InterPro "Repeat"
signatures (routed to SEQ_REPEAT — periodicity asserted only in sequence),
RepeatsDB repeats have structural periodicity, so they populate the otherwise-
empty MIXED_STRUCTURAL_REPEAT category. We seed the **classification nodes**
(not the per-PDB annotations, which are structure instances).

Input (fetch via `just fetch-repeatsdb`, gitignored):
  data/raw/repeatsdb/classification.json
    {"3.1.1": {"id","name","description","representative": "2n3dA", ...}, ...}

Each record: identifier RepeatsDB:<id>, parent chained by dotted id, the
representative PDB chain as a direct xref. Idempotent; dry-run unless --apply.
Stdlib-only.

Representative coverage: 87/122 nodes carry a curated `representative` PDB (→ a
direct PDB xref, and a structural_geometry_representations block via
enrich_structural_provenance.py). Of the 35 with an empty representative,
enrich_repeatsdb_inherited_reps.py backfills 3 by inheriting a curated
descendant's PDB (a genuine member of the group). The remaining 32 have no
representative anywhere in their subtree, and RepeatsDB's bulk classification
export lists no member structures (only aggregate `statistics` counts) — its
public API exposes only /api/production/classification — so those are left as an
explicit gap rather than fabricated.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "repeatsdb" / "classification.json"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence_structure" / "structural_repeat" / "repeatsdb"
LICENSE = "CC-BY 4.0"
LEVELS = {0: "class", 1: "topology", 2: "fold", 3: "clan"}
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "repeat"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def build_yaml(rid, name, desc, parent, pdb):
    level = LEVELS.get(rid.count("."), "repeat")
    definition = (desc or f"{name} — a RepeatsDB structural tandem-repeat "
                  f"{level} ({rid}).")
    definition = f"{definition} A structural tandem repeat with demonstrated 3D periodicity."
    lines = [f"identifier: RepeatsDB:{rid}", f"label: {yaml_escape(name)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: RepeatsDB", "trait_axis: SEQUENCE_STRUCTURE",
              "trait_category: MIXED_STRUCTURAL_REPEAT", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - RepeatsDB:{parent}"]
    if pdb:
        lines += ["xrefs:", f"  - PDB:{pdb}"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/repeatsdb/classification.json; run `just fetch-repeatsdb`",
              file=sys.stderr)
        return 2

    data = json.loads(RAW.read_text(encoding="utf-8", errors="replace"))
    written = skipped = 0
    for rid, node in sorted(data.items(), key=lambda kv: (kv[0].count("."), kv[0])):
        if not rid or not isinstance(node, dict):
            continue  # skip the empty-id umbrella root ("Tandem Repeat proteins")
        name = (node.get("name") or "").strip() or f"RepeatsDB {rid}"
        desc = (node.get("description") or "").strip()
        parent = rid.rsplit(".", 1)[0] if "." in rid else ""
        rep = (node.get("representative") or "").strip()
        # representative is a "<pdbid><chain>" token, e.g. 2n3dA → PDB:2N3D
        pdb = rep[:4].upper() if len(rep) >= 4 and rep[:4].isalnum() else ""
        path = OUT_DIR / f"{slugify(name)}-{rid.replace('.', '-')}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(rid, name, desc, parent, pdb), encoding="utf-8")
            written += 1

    print(f"{len(data)} RepeatsDB classification nodes → MIXED_STRUCTURAL_REPEAT.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(data) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
