#!/usr/bin/env python3
"""Migrate the records mis-routed across axes, per research/axis-split-review-1.md.

Moves already-seeded records to the axis/category the corrected seeders now emit,
in place (re-seeding would drop enrichment). Three groups:

  1. NCBIfam PfamEq  (1,860): SEQUENCE/SEQ_DOMAIN → FUNCTION/FUNC_PROTEIN_FAMILY
     NCBIfam PfamAutoEq (1,203): SEQUENCE/SEQ_DOMAIN → SEQUENCE/SEQ_FAMILY
     — and RE-COMPOSE the definition for the new axis (family, not domain).
  2. CDD protein clusters PRK/PLN/PHA/PTZ/MTH/CHL (~10k): SEQUENCE/SEQ_DOMAIN →
     FUNCTION/FUNC_PROTEIN_FAMILY; drop the (now cross-axis) domain-superfamily
     parent. The CDD abstract definition is kept.
  3. InterPro Active_site/Binding_site (215): STRUCTURE/STRUCT_*_SITE →
     SEQUENCE/SEQ_*_SITE. Definition kept.

Idempotent (a file already in its target dir is skipped); dry-run unless --apply.
Stdlib-only (imports the NCBIfam composer).
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_ncbifam_definitions as NCB  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
CDD_FAMILY_PREFIXES = ("PRK", "PLN", "PHA", "PTZ", "MTH", "CHL")
# definition folded-block + its source line (MULTILINE only — never DOTALL)
DEF_RE = re.compile(r"(?m)^definition:[ \t]*>-\n(?:[ \t]+.*\n)+?definition_source:.*$")


def set_line(text: str, key: str, val: str) -> str:
    return re.sub(rf"(?m)^{key}:.*$", f"{key}: {val}", text, count=1)


def drop_parents(text: str) -> str:
    return re.sub(r"(?m)^parent_traits:\n(?:[ \t]+-.*\n)+", "", text, count=1)


def move(p: Path, new_dir: Path, apply: bool) -> None:
    if apply:
        new_dir.mkdir(parents=True, exist_ok=True)
        (new_dir / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        p.unlink()


def ncbifam_family_type() -> dict[str, str]:
    ft = {}
    with open(NCB.TSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            for col in ("#ncbi_accession", "source_identifier"):
                v = (row.get(col) or "").strip()
                if v:
                    ft[re.sub(r"\.\d+$", "", v)] = (row.get("family_type") or "").strip()
    return ft


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    n = {"ncbifam_pfameq": 0, "ncbifam_pfamautoeq": 0, "cdd_family": 0, "interpro_site": 0}

    # ---- 1. NCBIfam PfamEq / PfamAutoEq ----
    ftmap = ncbifam_family_type()
    meta, gon, ecn = NCB.load_meta(), NCB.load_go_names(), NCB.load_ec_names()
    srcdir = TRAITS / "sequence" / "domain" / "ncbifam"
    for p in sorted(srcdir.glob("*.yaml")) if srcdir.is_dir() else []:
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*NCBIfam:(\S+)", text)
        if not m:
            continue
        acc = m.group(1); ft = ftmap.get(acc, "")
        if ft == "PfamEq":
            axis, cat, dst, key = "FUNCTION", "FUNC_PROTEIN_FAMILY", "function/protein_family/ncbifam", "ncbifam_pfameq"
        elif ft == "PfamAutoEq":
            axis, cat, dst, key = "SEQUENCE", "SEQ_FAMILY", "sequence/family/ncbifam", "ncbifam_pfamautoeq"
        else:
            continue
        text = set_line(set_line(text, "trait_axis", axis), "trait_category", cat)
        if acc in meta:                                  # recompose def for the new axis
            new_def = NCB.compose(meta[acc], acc, axis, ecn, gon)
            text = DEF_RE.subn(lambda _m: f"definition: >-\n  {new_def}\ndefinition_source: {NCB.SOURCE}",
                               text, count=1)[0]
        if args.apply:
            (TRAITS / dst).mkdir(parents=True, exist_ok=True)
            (TRAITS / dst / p.name).write_text(text, encoding="utf-8"); p.unlink()
        n[key] += 1

    # ---- 2. CDD protein-cluster prefixes ----
    srcdir = TRAITS / "sequence" / "domain" / "cdd"
    for p in sorted(srcdir.glob("*.yaml")) if srcdir.is_dir() else []:
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*CDD:(\S+)", text)
        if not m or not any(m.group(1).startswith(pre) for pre in CDD_FAMILY_PREFIXES):
            continue
        text = drop_parents(set_line(set_line(text, "trait_axis", "FUNCTION"),
                                     "trait_category", "FUNC_PROTEIN_FAMILY"))
        if args.apply:
            d = TRAITS / "function" / "protein_family" / "cdd"; d.mkdir(parents=True, exist_ok=True)
            (d / p.name).write_text(text, encoding="utf-8"); p.unlink()
        n["cdd_family"] += 1

    # ---- 3. InterPro sites ----
    for sub, cat in (("active_site", "SEQ_ACTIVE_SITE"), ("binding_site", "SEQ_BINDING_SITE")):
        srcdir = TRAITS / "structure" / sub / "interpro"
        for p in sorted(srcdir.glob("*.yaml")) if srcdir.is_dir() else []:
            text = p.read_text(encoding="utf-8")
            text = set_line(set_line(text, "trait_axis", "SEQUENCE"), "trait_category", cat)
            if args.apply:
                d = TRAITS / "sequence" / sub / "interpro"; d.mkdir(parents=True, exist_ok=True)
                (d / p.name).write_text(text, encoding="utf-8"); p.unlink()
            n["interpro_site"] += 1

    print(f"{'migrated' if args.apply else 'would migrate'}: {n}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
