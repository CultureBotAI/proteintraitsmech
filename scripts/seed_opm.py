#!/usr/bin/env python3
"""Seed the OPM (Orientations of Proteins in Membranes) membrane-protein
CLASSIFICATION as chained CLASS records — types → classtypes → superfamilies.

OPM classifies membrane proteins into a small structural hierarchy. We seed the
classification *terms* (not the ~8,900 per-PDB `primary_structures`, which are
protein instances). Routing follows the axis-of-representation rule:
  • classtypes/superfamilies under the **Transmembrane** type → MIXED_TRANSMEMBRANE
    (axis SEQUENCE_STRUCTURE) — this greenfields the empty category;
  • the top types + non-transmembrane (Monotopic/peripheral, Peptides) tiers →
    STRUCT_CLASS (axis STRUCTURE).
Hierarchy: superfamily → classtype → type via `parent_traits`. Superfamilies
carry Pfam / TCDB cross-references.

Inputs (fetch via `just fetch-opm`, gitignored): the OPM REST backend JSON —
  data/raw/opm/types.json                  (/types)
  data/raw/opm/classtype_<id>.json         (/classtypes/<id>: name, type,
                                            nested superfamilies with pfam/tcdb)

Licence: CC-BY 3.0 (OPM) — stamped per record (confirm OPM's official reuse terms
before wider redistribution). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "opm"
TRAITS = REPO_ROOT / "data" / "traits"
LICENSE = "CC-BY 3.0 (OPM)"
SOURCE = "OPM (Orientations of Proteins in Membranes)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

# type name → (trait_axis, trait_category, subdir) for that type's tiers.
TM = ("SEQUENCE_STRUCTURE", "MIXED_TRANSMEMBRANE", "sequence_structure/transmembrane")
SC = ("STRUCTURE", "STRUCT_CLASS", "structure/class")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "opm"


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


def route(type_name: str):
    return TM if type_name == "Transmembrane" else SC


def build_yaml(ident, label, definition, axis, cat, parent, xrefs):
    lines = [f"identifier: {ident}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {SOURCE}", f"trait_axis: {axis}",
              f"trait_category: {cat}", "term_kind: CLASS", "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - {parent}"]
    if xrefs:
        lines += ["xrefs:"] + [f"  - {x}" for x in xrefs]
    lines.append(f"license: {yaml_escape(LICENSE)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not (RAW / "types.json").exists():
        print("missing data/raw/opm/*.json; run `just fetch-opm`", file=sys.stderr)
        return 2

    written = skipped = 0
    counts = {"types": 0, "classtypes": 0, "superfamilies": 0}

    def emit(subdir, fname, text):
        nonlocal written, skipped
        path = TRAITS / subdir / "opm" / fname
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    # 1) types → STRUCT_CLASS (top tier)
    types = json.loads((RAW / "types.json").read_text())["objects"]
    for t in types:
        d = (f"{t['name']} membrane proteins — a top-level OPM structural class "
             f"of membrane proteins.")
        emit("structure/class", f"opm-type-{slug(t['name'])}-{t['id']}.yaml",
             build_yaml(f"OPM:type-{t['id']}", f"{t['name']} membrane proteins",
                        d, *SC[:2], None, []))
        counts["types"] += 1

    # 2) classtypes + their nested superfamilies
    for cf in sorted(RAW.glob("classtype_*.json")):
        c = json.loads(cf.read_text())
        tname = c["type"]["name"]
        axis, cat, subdir = route(tname)
        cparent = f"OPM:type-{c['type']['id']}"
        cd = (f"{c['name']} — an OPM membrane-protein class within the {tname} "
              f"type.")
        emit(subdir, f"opm-class-{slug(c['name'])}-{c['id']}.yaml",
             build_yaml(f"OPM:class-{c['id']}", c["name"], cd, axis, cat, cparent, []))
        counts["classtypes"] += 1
        for sf in (c.get("superfamilies") or []):
            xr = []
            pf = (sf.get("pfam") or "").strip()
            if pf:
                xr.append(f"Pfam:{pf}")
            tc = (sf.get("tcdb") or "").strip()
            if tc:
                xr.append(f"TCDB:{tc}")
            sd = (f"{sf['name']} — an OPM membrane-protein superfamily in the "
                  f"{c['name']} class ({tname}).")
            emit(subdir, f"opm-sf-{slug(sf['name'])}-{sf['id']}.yaml",
                 build_yaml(f"OPM:superfamily-{sf['id']}", sf["name"], sd,
                            axis, cat, f"OPM:class-{c['id']}", xr))
            counts["superfamilies"] += 1

    total = sum(counts.values())
    print(f"OPM: {total} classification classes → {counts} "
          f"(Transmembrane→MIXED_TRANSMEMBRANE, else→STRUCT_CLASS)")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
