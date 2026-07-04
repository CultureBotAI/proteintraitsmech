#!/usr/bin/env python3
"""Materialize the residual ontology grouping-parent nodes that curated
whitelist records point to but that were never seeded — the last ~37 dangling
`parent_traits` edges after Pfam-clan + PROSITE-PDOC materialization
(schema-hierarchy-review-1 oddity #2 / adopt #3).

Each of these 10 CURIEs is the is_a boundary just above a curated PATO/METPO/
ARO/PSI-MI branch. We emit one grouping record per node with its real OBO label
+ definition, inheriting the (axis, category, dir, license, def-source) of its
children, as a top-level root (no parent_traits — its OBO is_a targets are above
the curated scope, so chaining would re-introduce danglers).

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"

# target CURIE -> (obo file, axis, category, subdir under data/traits)
# axis/category = plurality of the node's existing children (verified 2026-07-04).
TARGETS = {
    "ARO:1000001":  ("aro/aro.obo", "FUNCTION",  "FUNC_RESISTANCE",             "function/resistance/aro"),
    "METPO:1000059":("METPO.obo",   "FUNCTION",  "FUNC_ENVIRONMENTAL_RESPONSE", "function/environmental_response/metpo"),
    "MI:0000":      ("PSI-MI.obo",  "FUNCTION",  "FUNC_INTERACTION_PARTNER",    "function/interaction_partner/psi_mi"),
    "PATO:0000141": ("PATO.obo",    "STRUCTURE", "STRUCT_STABILITY",            "structure/stability/pato"),
    "PATO:0001018": ("PATO.obo",    "STRUCTURE", "STRUCT_DYNAMICS",             "structure/dynamics/pato"),
    "PATO:0001546": ("PATO.obo",    "STRUCTURE", "STRUCT_DYNAMICS",             "structure/dynamics/pato"),
    "PATO:0002182": ("PATO.obo",    "STRUCTURE", "STRUCT_SURFACE",              "structure/surface/pato"),
    "PATO:0002303": ("PATO.obo",    "STRUCTURE", "STRUCT_DYNAMICS",             "structure/dynamics/pato"),
    "PATO:0002305": ("PATO.obo",    "STRUCTURE", "STRUCT_DYNAMICS",             "structure/dynamics/pato"),
    "PATO:0045001": ("PATO.obo",    "STRUCTURE", "STRUCT_DYNAMICS",             "structure/dynamics/pato"),
}

RAW = REPO_ROOT / "data" / "raw"
SLUG = re.compile(r"[^a-z0-9]+")


def slugify(t: str) -> str:
    return (SLUG.sub("-", t.lower()).strip("-")[:70]) or "term"


def yaml_escape(text: str) -> str:
    if text is None or text == "":
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if any(c in unsafe for c in text) or text[0] in "-?" or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def parse_obo(path: Path, wanted: set[str]) -> dict[str, tuple[str, str]]:
    out = {}
    for st in path.read_text(encoding="utf-8").split("\n[Term]\n"):
        mid = re.search(r"^id:\s*(\S+)", st, re.M)
        if not mid or mid.group(1) not in wanted:
            continue
        name = re.search(r"^name:\s*(.+)", st, re.M)
        d = re.search(r'^def:\s*"([^"]*)"', st, re.M)
        out[mid.group(1)] = (name.group(1).strip() if name else mid.group(1),
                             d.group(1).strip() if d else "")
    return out


def child_stamp(subdir: str) -> tuple[str, str]:
    """Reuse an existing sibling's definition_source + license so the new
    grouping node matches the branch exactly."""
    d = TRAITS / subdir
    for p in d.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8")
        ds = re.search(r"^definition_source:\s*(.+)$", t, re.M)
        lic = re.search(r"^license:\s*(.+)$", t, re.M)
        if ds and lic:
            return ds.group(1).strip(), lic.group(1).strip()
    return '""', "CC-BY-4.0"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the YAMLs (default: dry-run)")
    args = ap.parse_args()

    by_file: dict[str, set[str]] = {}
    for curie, (obo, *_rest) in TARGETS.items():
        by_file.setdefault(obo, set()).add(curie)
    obo_terms = {}
    for obo, curies in by_file.items():
        obo_terms.update(parse_obo(RAW / obo, curies))

    written = skipped = 0
    for curie, (obo, axis, cat, subdir) in TARGETS.items():
        label, defn = obo_terms.get(curie, (curie, ""))
        defn = defn or f"{label}."
        ds, lic = child_stamp(subdir)
        lines = [f"identifier: {curie}", f"label: {yaml_escape(label)}",
                 "definition: >-", f"  {defn}",
                 f"definition_source: {ds}",
                 f"trait_axis: {axis}", f"trait_category: {cat}",
                 "term_kind: CLASS", "mapping_status: SEEDED",
                 f"license: {lic}"]
        path = TRAITS / subdir / f"{slugify(label)}-{curie.lower().replace(':', '')}.yaml"
        if path.exists():
            skipped += 1
            continue
        print(f"  {'+ ' if args.apply else '  '}{curie}  {label!r} → {axis}/{cat}  {path.relative_to(REPO_ROOT)}")
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            written += 1
    verb = "wrote" if args.apply else "would write"
    print(f"{verb} {len(TARGETS) - skipped} grouping-parent nodes ({skipped} already exist)."
          + ("" if args.apply else " Pass --apply."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
