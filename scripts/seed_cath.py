#!/usr/bin/env python3
"""Seed the CATH structural-classification hierarchy (CATH-Gene3D, CC-BY 4.0).

CATH classifies protein domains into a four-level hierarchy — Class (C) >
Architecture (A) > Topology (T) > Homologous superfamily (H) — encoded as a
dotted numeric code (`3.40.50.300`). We seed every node from cath-names.txt,
routed by code depth, with each node parented to the code one level up:

  C  (e.g. "3")        → STRUCT_CLASS
  A  (e.g. "3.40")     → STRUCT_ARCHITECTURE
  T  (e.g. "3.40.50")  → STRUCT_TOPOLOGY
  H  (e.g. "3.40.50.300") → STRUCT_HOMOLOGOUS_SUPERFAMILY

This is the authoritative upper hierarchy that the TED folds (CATH-derived) and
ECOD superfamilies relate to.

Input (fetch via `just fetch-cath`, gitignored):
  data/raw/cath/cath-names.txt   "<code>\\t<rep-domain>\\t:<name>"

Each record: identifier CATH:<code>, label (node name), parent CATH:<parent>,
STRUCTURE / STRUCT_*, mapping_status SEEDED. Idempotent; dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NAMES = REPO_ROOT / "data" / "raw" / "cath" / "cath-names.txt"
TRAITS_DIR = REPO_ROOT / "data" / "traits"
LICENSE = "CC-BY 4.0"

# depth (number of dotted fields) → (category, subdir, level label)
LEVELS = {
    1: ("STRUCT_CLASS",                 "structure/class/cath",                 "class"),
    2: ("STRUCT_ARCHITECTURE",          "structure/architecture/cath",          "architecture"),
    3: ("STRUCT_TOPOLOGY",              "structure/topology/cath",              "topology"),
    4: ("STRUCT_HOMOLOGOUS_SUPERFAMILY","structure/homologous_superfamily/cath","homologous superfamily"),
}
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:70]) or "cath"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    text = " ".join((text or "").split())
    return [">-", f"  {text}"]


def build_yaml(code: str, name: str, rep: str, category: str, level: str) -> str:
    parent = code.rsplit(".", 1)[0] if "." in code else ""
    # Unnamed nodes (CATH gives no textual name) are still real classification
    # classes — label them by their CATH id + level, keep the representative
    # domain as evidence, rather than dropping them.
    if name:
        label = name
        definition = f"CATH {level} {code}: {name}."
    else:
        label = f"CATH {level} {code}"
        definition = (f"CATH {level} {code} — an (unnamed) CATH classification "
                      f"node; representative domain {rep}.")
    lines = [f"identifier: CATH:{code}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append("definition_source: CATH")
    lines.append("trait_axis: STRUCTURE")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if parent:
        lines.append("parent_traits:")
        lines.append(f"  - CATH:{parent}")
    if rep:
        lines.append("xrefs:")
        lines.append(f"  - CATH:{rep}")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not NAMES.exists():
        print(f"missing {NAMES.relative_to(REPO_ROOT)}; run `just fetch-cath`", file=sys.stderr)
        return 2

    stats = {"written": 0, "skipped": 0, "by_cat": {}}
    for line in NAMES.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        # "<code>  <rep-domain>  :<name>" — whitespace-delimited; the name
        # follows a ':' and may itself contain spaces.
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        code = parts[0].strip()
        rep = parts[1].strip()
        name = parts[2].lstrip(":").strip()
        depth = code.count(".") + 1
        route = LEVELS.get(depth)
        if route is None:
            continue
        category, subdir, level = route
        stats["by_cat"][category] = stats["by_cat"].get(category, 0) + 1
        slug = slugify(name) if name else code.replace(".", "-")
        path = TRAITS_DIR / subdir / f"{slug}-{code.replace('.', '-')}.yaml"
        if path.exists() and not args.force:
            stats["skipped"] += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(code, name, rep, category, level), encoding="utf-8")
            stats["written"] += 1

    total = sum(stats["by_cat"].values())
    print("Per-category totals:")
    for c, n in sorted(stats["by_cat"].items(), key=lambda kv: -kv[1]):
        print(f"  {c:32s} {n:>5,}")
    print(f"  {'TOTAL':32s} {total:>5,}")
    if args.apply:
        print(f"Wrote {stats['written']:,}; skipped {stats['skipped']:,} existing.")
    else:
        print(f"Dry-run — would write {total - stats['skipped']:,}; {stats['skipped']:,} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
