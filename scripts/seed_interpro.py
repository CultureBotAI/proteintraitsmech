#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from InterPro entries.

InterPro is the integrative classification of protein families, domains and
sites (combining Pfam, PROSITE, SMART, PRINTS, PANTHER, PIRSF, SFLD, CDD, HAMAP,
NCBIfam, CATH-Gene3D, SUPERFAMILY). Public domain.

We seed the **entries** (not the multi-terabyte match files), and only the
entry types that localise to a sequence/structure element — each carries a real
definition (the InterPro abstract) and a type-specific parent/child hierarchy:

  Domain                 → SEQUENCE    / SEQ_DOMAIN
  Homologous_superfamily → SEQUENCE    / SEQ_HOMOLOGOUS_SUPERFAMILY
  Repeat                 → SEQUENCE    / SEQ_REPEAT
  Conserved_site         → SEQUENCE    / SEQ_CONSERVATION
  Active_site            → STRUCTURE   / STRUCT_ACTIVE_SITE
  Binding_site           → STRUCTURE   / STRUCT_BINDING_SITE
  PTM                    → SEQUENCE    / SEQ_PTM_SITE

An InterPro `Repeat` is a *sequence* signature (a repeated region detected by an
HMM); many correspond to structural repeats (Armadillo, LRR, WD40 solenoids) but
InterPro does not assert 3D periodicity per entry, so we default to the sequence
axis (SEQ_REPEAT) rather than the mixed MIXED_STRUCTURAL_REPEAT — the latter is
reserved for repeats with demonstrated structural periodicity (e.g. RepeatsDB).

GO groundings are added to `xrefs` from interpro2go when present.

`Family` (whole-protein homology groups) is **excluded by default** — it does
not localise to a sequence/structure element and has no matching trait_category.
Pass --include-families to emit them as SEQ_FAMILY anyway (not recommended).

Inputs (fetch with `just fetch-interpro`, gitignored):
  data/raw/interpro/interpro.xml.gz          — entries + abstracts + types
  data/raw/interpro/ParentChildTreeFile.txt  — parent/child hierarchy

Each record: identifier InterPro:IPRnnnnnn, label (entry name), definition
(abstract, whitespace-collapsed, capped), parent_traits (InterPro parent),
trait_axis/category per the table, term_kind CLASS, mapping_status SEEDED,
license public domain. Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "interpro"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

XML_GZ = RAW_DIR / "interpro.xml.gz"
TREE = RAW_DIR / "ParentChildTreeFile.txt"
INTERPRO2GO = RAW_DIR / "interpro2go"

LICENSE = "public domain"
DEF_CAP = 1800

# InterPro entry type → (axis, category, subdir).
TYPE_MAP: dict[str, tuple[str, str, str]] = {
    "Domain":                 ("SEQUENCE",           "SEQ_DOMAIN",                    "sequence/domain/interpro"),
    "Homologous_superfamily": ("SEQUENCE",           "SEQ_HOMOLOGOUS_SUPERFAMILY",    "sequence/homologous_superfamily/interpro"),
    "Repeat":                 ("SEQUENCE",           "SEQ_REPEAT",                    "sequence/repeat/interpro"),
    "Conserved_site":         ("SEQUENCE",           "SEQ_CONSERVATION",              "sequence/conservation/interpro"),
    "Active_site":            ("STRUCTURE",          "STRUCT_ACTIVE_SITE",            "structure/active_site/interpro"),
    "Binding_site":           ("STRUCTURE",          "STRUCT_BINDING_SITE",           "structure/binding_site/interpro"),
    "PTM":                    ("SEQUENCE",           "SEQ_PTM_SITE",                  "sequence/ptm_ontology/interpro"),
}

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_TREE_RE = re.compile(r"^(-*)(IPR\d+)::")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:70]) or "entry"


def parse_tree() -> dict[str, str]:
    """child IPR → parent IPR, from the dash-indented tree file."""
    parent_of: dict[str, str] = {}
    stack: list[str] = []  # stack[depth] = ipr at that depth
    for line in TREE.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _TREE_RE.match(line)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        ipr = m.group(2)
        del stack[depth:]
        if depth > 0 and len(stack) >= depth:
            parent_of[ipr] = stack[depth - 1]
        stack.append(ipr)
    return parent_of


_GO_RE = re.compile(r";\s*(GO:\d{7})\s*$")


def parse_interpro2go() -> dict[str, list[str]]:
    """IPR accession → [GO CURIEs], from the interpro2go mapping file.
    Lines: 'InterPro:IPRnnnnnn name > GO:go_name ; GO:nnnnnnn'."""
    out: dict[str, list[str]] = {}
    if not INTERPRO2GO.exists():
        return out
    for line in INTERPRO2GO.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("!") or not line.startswith("InterPro:"):
            continue
        m = _GO_RE.search(line)
        if not m:
            continue
        ipr = line.split(None, 1)[0].split(":", 1)[1]
        out.setdefault(ipr, [])
        if m.group(1) not in out[ipr]:
            out[ipr].append(m.group(1))
    return out


def clean_abstract(el) -> str:
    if el is None:
        return ""
    text = " ".join("".join(el.itertext()).split())
    # Stripped <cite>/<dbxref> tags leave empty "[ ]" / "[ , ]" stubs — drop them.
    text = re.sub(r"\s*\[\s*(?:,\s*)*\]", "", text)
    text = " ".join(text.split())
    if len(text) > DEF_CAP:
        text = text[: DEF_CAP - 1].rstrip() + "…"
    return text


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
    return [">-", f"  {text}"] if text else [">-", '  ""']


def build_yaml(ipr: str, name: str, definition: str, axis: str, category: str,
               parent: str | None, go_xrefs: list[str]) -> str:
    lines = [f"identifier: InterPro:{ipr}", f"label: {yaml_escape(name)}"]
    f = folded(definition or name)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append("definition_source: InterPro")
    lines.append(f"trait_axis: {axis}")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if parent:
        lines.append("parent_traits:")
        lines.append(f"  - InterPro:{parent}")
    if go_xrefs:
        # GO here is asserted by the interpro2go mapping product, not by the
        # InterPro entry itself → mapped_xrefs with provenance, not xrefs.
        lines.append("mapped_xrefs:")
        for g in go_xrefs:
            lines.append(f"  - object: {g}")
            lines.append("    mapping_source: interpro2go")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def read_release() -> str:
    # interpro.xml starts with <release><dbinfo dbname="INTERPRO" version="..."/>
    with gzip.open(XML_GZ, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag == "dbinfo" and el.get("dbname", "").upper() == "INTERPRO":
                v = el.get("version") or el.get("entry_count") or ""
                return f"InterPro {v}".strip()
            if el.tag == "interpro":
                break
    return "InterPro"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--include-families", action="store_true",
                    help="also emit Family entries as SEQ_FAMILY (not recommended)")
    ap.add_argument("--limit", type=int, default=0, help="cap records (0 = all)")
    args = ap.parse_args()

    if not XML_GZ.exists() or not TREE.exists():
        print("missing data/raw/interpro/*; run `just fetch-interpro` first", file=sys.stderr)
        return 2

    type_map = dict(TYPE_MAP)
    if args.include_families:
        type_map["Family"] = ("SEQUENCE", "SEQ_FAMILY", "sequence/family/interpro")

    parent_of = parse_tree()
    ipr2go = parse_interpro2go()
    stats = {"written": 0, "skipped": 0, "planned": 0, "by_cat": {}, "with_go": 0}
    processed = 0

    with gzip.open(XML_GZ, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            typ = el.get("type", "")
            route = type_map.get(typ)
            if route is None:
                el.clear()
                continue
            if args.limit and processed >= args.limit:
                break
            axis, category, subdir = route
            ipr = el.get("id", "")
            name_el = el.find("name")
            name = (name_el.text or "").strip() if name_el is not None else el.get("short_name", ipr)
            definition = clean_abstract(el.find("abstract"))
            parent = parent_of.get(ipr)
            go_xrefs = ipr2go.get(ipr, [])
            if go_xrefs:
                stats["with_go"] += 1

            path = TRAITS_DIR / subdir / f"{slugify(name)}-{ipr.lower()}.yaml"
            stats["by_cat"][category] = stats["by_cat"].get(category, 0) + 1
            processed += 1
            el.clear()
            if path.exists() and not args.force:
                stats["skipped"] += 1
                continue
            stats["planned"] += 1
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    build_yaml(ipr, name, definition, axis, category, parent, go_xrefs),
                    encoding="utf-8")
                stats["written"] += 1

    print("Per-category totals (all in-scope entries):")
    for c, n in sorted(stats["by_cat"].items(), key=lambda kv: -kv[1]):
        print(f"  {c:34s} {n:>6,}")
    total = sum(stats["by_cat"].values())
    print(f"  {'TOTAL':34s} {total:>6,}")
    print(f"  ({stats['with_go']:,} carry GO xrefs from interpro2go)")
    if args.apply:
        print(f"\nWrote {stats['written']:,}; skipped {stats['skipped']:,} existing.")
    else:
        print(f"\nDry-run — would write {stats['planned']:,}; {stats['skipped']:,} exist. "
              f"Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
