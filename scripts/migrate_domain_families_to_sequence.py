#!/usr/bin/env python3
"""One-time migration: sequence-signature domain/family records → SEQUENCE axis.

Decision (2026-07-04): the trait axis follows the *representation*. Pfam,
InterPro, CDD, NCBIfam and MEROPS classify proteins with profile HMMs / PSSMs /
patterns — their representation is in sequence space — so their domain / family /
homologous-superfamily records move off STRUCTURE onto SEQUENCE (new categories
SEQ_DOMAIN / SEQ_FAMILY / SEQ_HOMOLOGOUS_SUPERFAMILY). NCBIfam/TIGRFAM
whole-protein *functional* families (equivalog / subfamily / exception / paralog)
instead move to FUNCTION / FUNC_PROTEIN_FAMILY. Structure-derived classifications
(CATH / SCOPe / ECOD / TED) are untouched — they stay on STRUCTURE.

Each affected record has its `trait_axis` + `trait_category` rewritten and its
file moved to the matching axis/category directory. Idempotent, git-friendly
(rename + 2-line edit), dry-run by default. The seeders were updated in lockstep
so a future re-seed produces the same layout.

  python3 scripts/migrate_domain_families_to_sequence.py            # dry-run
  python3 scripts/migrate_domain_families_to_sequence.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"

PFAM_TYPE_RE = re.compile(r"Pfam ([a-z-]+) family")
NCBIFAM_TYPE_RE = re.compile(r"\([A-Za-z]+[0-9]+, ([a-z_]+)\)")
_NCBIFAM_FUNC = {"equivalog", "subfamily", "exception", "hypoth_equivalog", "paralog"}


def route_pfam_domain(text: str):
    m = PFAM_TYPE_RE.search(text)
    typ = m.group(1) if m else "domain"
    if typ == "family":
        return "SEQUENCE", "SEQ_FAMILY", "sequence/family/pfam"
    return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/pfam"


def route_ncbifam_domain(text: str):
    m = NCBIFAM_TYPE_RE.search(text)
    ft = (m.group(1) if m else "").lower()
    if ft.endswith("_domain") or ft in ("domain", "signature", ""):
        return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/ncbifam"
    if ft == "superfamily":
        return "SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily/ncbifam"
    if ft in _NCBIFAM_FUNC:
        return "FUNCTION", "FUNC_PROTEIN_FAMILY", "function/protein_family/ncbifam"
    return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/ncbifam"


def const(axis, cat, subdir):
    return lambda text: (axis, cat, subdir)


def route_structure_domain_flat(text: str):
    # structure/domain now holds only PROSITE ProRule domain profiles (flat
    # *.yaml → SEQ_DOMAIN) and the SCOPe subdir (structure-derived → keep).
    if re.search(r"^identifier:\s*SCOP:", text, re.M) or "SCOPe" in text:
        return None
    return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/prosite"


# (source directory under data/traits, per-record router)
RULES = [
    ("structure/domain/pfam", route_pfam_domain),
    ("structure/homologous_superfamily/pfam", const("SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily/pfam")),
    ("structure/domain/interpro", const("SEQUENCE", "SEQ_DOMAIN", "sequence/domain/interpro")),
    ("structure/homologous_superfamily/interpro", const("SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily/interpro")),
    ("structure/domain/cdd", const("SEQUENCE", "SEQ_DOMAIN", "sequence/domain/cdd")),
    ("structure/homologous_superfamily/cdd", const("SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily/cdd")),
    ("structure/domain/ncbifam", route_ncbifam_domain),
    ("structure/domain/merops", const("SEQUENCE", "SEQ_FAMILY", "sequence/family/merops")),
    ("structure/domain", route_structure_domain_flat),  # PROSITE ProRule (skips SCOPe subdir)
]

AXIS_LINE = re.compile(r"^trait_axis:\s*\S+\s*$", re.M)
CAT_LINE = re.compile(r"^trait_category:\s*\S+\s*$", re.M)


def rewrite(text: str, axis: str, category: str) -> str:
    text, n1 = AXIS_LINE.subn(f"trait_axis: {axis}", text, count=1)
    text, n2 = CAT_LINE.subn(f"trait_category: {category}", text, count=1)
    if n1 != 1 or n2 != 1:
        raise ValueError("trait_axis/trait_category line not found exactly once")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    moved = Counter()
    errors = []
    touched_dirs = set()
    for src_rel, router in RULES:
        src = TRAITS / src_rel
        if not src.exists():
            continue
        for path in src.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8")
            routed = router(text)
            if routed is None:
                continue
            axis, category, subdir = routed
            dest = TRAITS / subdir / path.name
            try:
                new_text = rewrite(text, axis, category)
            except ValueError as exc:
                errors.append(f"{path}: {exc}")
                continue
            moved[(src_rel, category)] += 1
            touched_dirs.add(src)
            if args.apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(new_text, encoding="utf-8")
                if dest != path:
                    path.unlink()

    total = sum(moved.values())
    print(f"{'migrated' if args.apply else 'would migrate'} {total:,} records:")
    for (src_rel, category), n in sorted(moved.items()):
        print(f"  {src_rel:44s} → {category:28s} {n:>6,}")
    if errors:
        print(f"\n{len(errors)} errors (skipped):", file=sys.stderr)
        for e in errors[:20]:
            print("  " + e, file=sys.stderr)

    # prune now-empty source dirs
    if args.apply:
        for d in sorted(touched_dirs, key=lambda p: len(p.parts), reverse=True):
            for sub in sorted(d.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if sub.is_dir() and not any(sub.iterdir()):
                    sub.rmdir()
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    if not args.apply:
        print("\nDry-run — pass --apply to move files.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
