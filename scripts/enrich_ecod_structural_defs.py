#!/usr/bin/env python3
"""Compose STRUCTURAL definitions for ECOD records from the ECOD hierarchy names.

ECOD classifies a domain by Architecture → X (possible homology) → H (homology)
→ T (topology) → F (family). The domains file carries all five names per domain;
the group ids are the truncated 4-part `f_id` (X=1 component, H=2, T=3, F=4) plus
the architecture text. The names ARE the structural description — the architecture
("beta barrels", "a+b two layers") and X name give the structural elements and
arrangement, e.g.

    ECOD:F.1.1.1.3 → "beta barrels architecture; cradle loop barrel;
                      RIFT-related homology; acid protease topology; RVP family."

Added as a definitions[{kind: STRUCTURAL, method: SOURCED, source: ECOD}] entry.
ECOD is the single largest source (~45k records) and the biggest compute consumer
in the tool-value analysis, carried almost entirely by hierarchy — this gives it
real structural content. The `definition` string stays as the general fallback.

Input: data/raw/ecod.latest.domains.txt  (just fetch-ecod)
Idempotent (skips records already carrying a STRUCTURAL definition); dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS = REPO_ROOT / "data" / "raw" / "ecod.latest.domains.txt"
TRAITS = REPO_ROOT / "data" / "traits"

# 0-indexed columns (per seed_ecod.py)
C_FID, C_ARCH, C_X, C_H, C_T, C_F = 3, 8, 9, 10, 11, 12
_PLACEHOLDER = re.compile(r"^(NO_[A-Z]_NAME|)$")


def clean(name: str) -> str:
    name = (name or "").strip()
    return "" if _PLACEHOLDER.match(name) else name


def load_names() -> dict[str, tuple]:
    """group id (with level prefix, e.g. 'X.1', 'H.1.1', 'T.1.1.1', 'F.1.1.1.3',
    'A.beta barrels') → (arch, x, h, t, f) names known at that level."""
    out: dict[str, tuple] = {}
    with open(DOMAINS, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if len(c) <= C_F or not re.match(r"[\d.]+$", c[C_FID]):
                continue
            fid = c[C_FID]
            arch, xn, hn, tn, fn = (clean(c[i]) for i in (C_ARCH, C_X, C_H, C_T, C_F))
            p = fid.split(".")
            if arch:
                out.setdefault("A." + arch, (arch, "", "", "", ""))
            if len(p) >= 1:
                out["X." + p[0]] = (arch, xn, "", "", "")
            if len(p) >= 2:
                out["H." + ".".join(p[:2])] = (arch, xn, hn, "", "")
            if len(p) >= 3:
                out["T." + ".".join(p[:3])] = (arch, xn, hn, tn, "")
            if len(p) >= 4:
                out["F." + fid] = (arch, xn, hn, tn, fn)
    return out


def compose(level: str, names: tuple) -> str:
    arch, xn, hn, tn, fn = names
    parts = []
    if arch:
        parts.append(f"{arch} architecture")
    if xn and xn != arch:
        parts.append(xn)
    if level in ("H", "T", "F") and hn:
        parts.append(f"{hn} homology")
    if level in ("T", "F") and tn:
        parts.append(f"{tn} topology")
    if level == "F" and fn:
        parts.append(f"{fn} family")
    return "; ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not DOMAINS.exists():
        print("missing data/raw/ecod.latest.domains.txt; run `just fetch-ecod`", file=sys.stderr)
        return 2

    names = load_names()
    print(f"{len(names):,} ECOD groups indexed from the domains file")
    added = skipped = miss = 0
    # ECOD F-level lives in structure/fold/ecod/, but A/X/H/T sit directly in the
    # shared category folders (architecture / topology / homologous_superfamily),
    # so scan those and filter to ECOD by identifier.
    ecod_dirs = re.compile(r"/structure/(fold/ecod|homologous_superfamily|topology|architecture)/")
    for p in TRAITS.rglob("*.yaml"):
        if not ecod_dirs.search(str(p)):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*ECOD:([AXHTF])\.(.+)$", text)
        if not m:
            continue
        level, gid = m.group(1), m.group(2).strip()
        if re.search(r"kind:\s*STRUCTURAL", text):
            skipped += 1
            continue
        key = f"{level}.{gid}"
        nm = names.get(key)
        if not nm:
            miss += 1
            continue
        desc = compose(level, nm)
        if not desc:
            miss += 1
            continue
        block = ("definitions:\n"
                 "  - kind: STRUCTURAL\n"
                 f"    text: >-\n      {desc}.\n"
                 '    source: "ECOD (architecture/X/H/T/F hierarchy)"\n'
                 "    method: SOURCED\n")
        new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1) \
            if re.search(r"(?m)^license:", text) else text.rstrip("\n") + "\n" + block
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"ECOD STRUCTURAL definitions: {'added' if args.apply else 'would add'} {added:,} "
          f"| already had {skipped:,} | no name match {miss:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
