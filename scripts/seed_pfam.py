#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from Pfam-A families.

Pfam (now hosted at EMBL-EBI / InterPro, public domain) classifies protein
sequences into families and domains via HMMs. We seed every Pfam-A family,
routed by its family type, and cross-referenced to GO (pfam2go), InterPro
(pfam2interpro, derived from interpro.xml) and its Pfam clan:

  Domain / Family → STRUCTURE          / STRUCT_DOMAIN
  Repeat          → SEQUENCE           / SEQ_REPEAT
  Coiled-coil     → SEQUENCE_STRUCTURE / MIXED_COILED_COIL
  Disordered      → SEQUENCE           / SEQ_DISORDER
  Motif           → SEQUENCE           / SEQ_MOTIF

Pfam-B is NOT ingested: it was discontinued at Pfam 28.0 (2015) and is not in
the current release. Pfam ⊂ InterPro, so each record carries its InterPro entry
as an xref (the relationship is explicit rather than duplicated); `interpro2ec`
has no bulk file, so EC is not attached here.

Inputs (fetch via `just fetch-pfam`, gitignored):
  data/raw/pfam/Pfam-A.clans.tsv.gz   accession, clan, clan_name, id, description
  data/raw/pfam/pfam_types.tsv        accession -> family type (from Pfam-A.hmm.dat)
  data/raw/mappings/pfam2go           Pfam -> GO
  data/raw/mappings/pfam2interpro.tsv Pfam -> InterPro (derived from interpro.xml)

Each record: identifier Pfam:PFnnnnn, label (description), definition, parent
(Pfam clan), xrefs (GO + InterPro), synonym (short id), mapping_status SEEDED.
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw"
CLANS = RAW / "pfam" / "Pfam-A.clans.tsv.gz"
TYPES = RAW / "pfam" / "pfam_types.tsv"
PFAM2GO = RAW / "mappings" / "pfam2go"
PFAM2IPR = RAW / "mappings" / "pfam2interpro.tsv"
TRAITS_DIR = REPO_ROOT / "data" / "traits"
LICENSE = "public domain (Pfam / InterPro)"

TYPE_MAP: dict[str, tuple[str, str, str]] = {
    "Domain":      ("STRUCTURE",          "STRUCT_DOMAIN",     "structure/domain/pfam"),
    "Family":      ("STRUCTURE",          "STRUCT_DOMAIN",     "structure/domain/pfam"),
    "Repeat":      ("SEQUENCE",           "SEQ_REPEAT",        "sequence/repeat/pfam"),
    "Coiled-coil": ("SEQUENCE_STRUCTURE", "MIXED_COILED_COIL", "mixed/coiled_coil/pfam"),
    "Disordered":  ("SEQUENCE",           "SEQ_DISORDER",      "sequence/disorder/pfam"),
    "Motif":       ("SEQUENCE",           "SEQ_MOTIF",         "sequence/motif/pfam"),
}

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_GO_RE = re.compile(r"(GO:\d{7})")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:70]) or "pfam"


def load_types() -> dict[str, str]:
    out = {}
    for line in TYPES.read_text(encoding="utf-8", errors="replace").splitlines():
        if "\t" in line:
            ac, tp = line.split("\t", 1)
            out[ac.strip()] = tp.strip()
    return out


def load_pfam2go() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    if not PFAM2GO.exists():
        return out
    for line in PFAM2GO.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("Pfam:"):
            continue
        pf = line.split(None, 1)[0].split(":", 1)[1]
        for go in _GO_RE.findall(line.split(">", 1)[-1]):
            if go not in out[pf]:
                out[pf].append(go)
    return out


def load_pfam2ipr() -> dict[str, str]:
    out = {}
    if PFAM2IPR.exists():
        for line in PFAM2IPR.read_text(encoding="utf-8", errors="replace").splitlines():
            if "\t" in line:
                pf, ipr = line.split("\t", 1)
                out[pf.strip()] = ipr.strip()
    return out


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


def build_yaml(pf, pid, desc, clan, typ, axis, category, go, ipr) -> str:
    label = desc or pid
    definition = f"{desc or pid}. Pfam {typ.lower()} family {pid} (Pfam:{pf})."
    lines = [f"identifier: Pfam:{pf}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append("definition_source: Pfam")
    lines.append(f"trait_axis: {axis}")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    if clan:
        lines.append("parent_traits:")
        lines.append(f"  - Pfam:{clan}")
    # GO (pfam2go) and InterPro (pfam2interpro) are both mapping-product
    # assertions, not Pfam-direct → mapped_xrefs with provenance.
    mapped = [(g, "pfam2go") for g in go]
    if ipr:
        mapped.append((f"InterPro:{ipr}", "pfam2interpro"))
    if mapped:
        lines.append("mapped_xrefs:")
        for obj, src in mapped:
            lines.append(f"  - object: {obj}")
            lines.append(f"    mapping_source: {src}")
    if pid and pid != label:
        lines.append("synonyms:")
        lines.append(f"  - synonym_text: {yaml_escape(pid)}")
        lines.append("    synonym_type: EXACT_SYNONYM")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not CLANS.exists() or not TYPES.exists():
        print("missing data/raw/pfam/*; run `just fetch-pfam` first", file=sys.stderr)
        return 2

    types = load_types()
    p2go = load_pfam2go()
    p2ipr = load_pfam2ipr()
    stats = {"written": 0, "skipped": 0, "by_cat": defaultdict(int), "with_go": 0, "with_ipr": 0}

    with gzip.open(CLANS, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 5:
                continue
            pf, clan, _clan_name, pid, desc = cols[0], cols[1], cols[2], cols[3], cols[4]
            typ = types.get(pf, "Family")
            route = TYPE_MAP.get(typ, TYPE_MAP["Family"])
            axis, category, subdir = route
            clan = clan if clan.startswith("CL") else ""
            go = p2go.get(pf, [])
            ipr = p2ipr.get(pf, "")
            if go:
                stats["with_go"] += 1
            if ipr:
                stats["with_ipr"] += 1
            stats["by_cat"][category] += 1
            path = TRAITS_DIR / subdir / f"{slugify(pid or pf)}-{pf.lower()}.yaml"
            if path.exists() and not args.force:
                stats["skipped"] += 1
                continue
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(build_yaml(pf, pid, desc, clan, typ, axis, category, go, ipr),
                                encoding="utf-8")
                stats["written"] += 1

    total = sum(stats["by_cat"].values())
    print("Per-category totals:")
    for c, n in sorted(stats["by_cat"].items(), key=lambda kv: -kv[1]):
        print(f"  {c:28s} {n:>6,}")
    print(f"  {'TOTAL':28s} {total:>6,}  ({stats['with_go']:,} GO, {stats['with_ipr']:,} InterPro xrefs)")
    if args.apply:
        print(f"Wrote {stats['written']:,}; skipped {stats['skipped']:,} existing.")
    else:
        print(f"Dry-run — would write {total - stats['skipped']:,}; {stats['skipped']:,} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
