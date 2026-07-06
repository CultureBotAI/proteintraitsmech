#!/usr/bin/env python3
"""Compose STRUCTURAL definitions for CATH records from the CATH hierarchy names.

CATH classifies a domain by Class → Architecture → Topology → Homologous
superfamily, and cath-names.txt gives each node a name. The names ARE the
structural description: Class "Mainly Alpha", Architecture "Orthogonal Bundle",
Topology/H names. For a CATH record at any level we compose its ancestors' names
into a "structural elements + how they are arranged" definition, e.g.

    CATH:1.20.81 → "Mainly alpha; orthogonal bundle architecture;
                    Receptor-associated Protein topology."

Added as a definitions[{kind: STRUCTURAL, method: SOURCED, source: CATH}] entry;
the existing `definition` string stays as the general fallback. Only applied where
the record has real ancestor names to compose (≥ architecture level).

Input: data/raw/cath/cath-names.txt  (just fetch-cath)
Idempotent (skips records already carrying a STRUCTURAL definition); dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NAMES = REPO_ROOT / "data" / "raw" / "cath" / "cath-names.txt"
TRAITS = REPO_ROOT / "data" / "traits"

LEVEL = {1: "class", 2: "architecture", 3: "topology", 4: "homologous superfamily"}


def load_names() -> dict[str, str]:
    """CATH node id (e.g. '1', '1.20', '1.20.81') → name."""
    out: dict[str, str] = {}
    for line in NAMES.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        # format (whitespace-delimited): <node_id>  <rep_domain>  :<name>
        parts = line.split(None, 2)
        if len(parts) >= 3:
            name = parts[2].lstrip(":").strip()
            if name:
                out[parts[0].strip()] = name
    return out


def compose(node_id: str, names: dict[str, str]) -> str:
    """Ancestor names → a structural sentence; deepest level named by its role."""
    nums = node_id.split(".")
    phrases = []
    for depth in range(1, len(nums) + 1):
        nid = ".".join(nums[:depth])
        nm = names.get(nid)
        if not nm:
            continue
        role = LEVEL.get(depth, "group")
        if depth == 1:                       # Class — leads the sentence
            phrases.append(nm.lower())
        elif depth in (2, 3):                # architecture / topology
            phrases.append(f"{nm.lower()} {role}")
        else:                                # H superfamily — keep original case
            phrases.append(f"{nm} {role}")
    return "; ".join(phrases)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not NAMES.exists():
        print("missing data/raw/cath/cath-names.txt; run `just fetch-cath`", file=sys.stderr)
        return 2

    names = load_names()
    added = skipped = thin = 0
    for p in TRAITS.rglob("*.yaml"):
        if "/cath/" not in str(p):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*CATH:([\d.]+)", text)
        if not m:
            continue
        node_id = m.group(1)
        if re.search(r"kind:\s*STRUCTURAL", text):
            skipped += 1
            continue
        desc = compose(node_id, names)
        if not desc or "." not in node_id:   # need ≥ architecture level to be structural
            thin += 1
            continue
        block = ("definitions:\n"
                 "  - kind: STRUCTURAL\n"
                 f"    text: >-\n      {desc}.\n"
                 '    source: "CATH (cath-names hierarchy)"\n'
                 "    method: SOURCED\n")
        new = re.sub(r"(?m)^(license:.*)$", block + r"\1", text, count=1) \
            if re.search(r"(?m)^license:", text) else text.rstrip("\n") + "\n" + block
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"CATH STRUCTURAL definitions: {'added' if args.apply else 'would add'} {added} "
          f"| already had {skipped} | too shallow (class-only) {thin}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
