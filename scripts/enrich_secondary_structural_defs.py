#!/usr/bin/env python3
"""Populate the STRUCTURAL definition layer for STRUCT_SECONDARY records.

STRUCTURAL covers any molecular-structure content, including the 3D
secondary-structure *arrangement* (structural-definitions scope). STRUCT_SECONDARY
records carry that arrangement as a `secondary_structure_representations[].
topology_string` (e.g. "H-loop(Ca)-H") but no typed STRUCTURAL layer. This lifts
the topology string into `definitions[{kind: STRUCTURAL}]` so it reads alongside
the fold-classification STRUCTURAL layers (SCOP/CATH/ECOD) and feeds the
structural dimension of the definition-only map.

Idempotent; appends into any existing `definitions:` list via deflib. Dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deflib import add_layer  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
SOURCE = "curated secondary-structure topology"

_TOPO = re.compile(r"(?m)^\s*topology_string:\s*(.+?)\s*$")


def structural_text(text: str) -> str | None:
    if "trait_category: STRUCT_SECONDARY" not in text:
        return None
    m = _TOPO.search(text)
    if not m:
        return None
    topo = m.group(1).strip().strip('"')
    return f"Secondary-structure arrangement (topology string): {topo}." if topo else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    added = skipped = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        if "trait_category: STRUCT_SECONDARY" not in text:
            continue
        stext = structural_text(text)
        if not stext:
            continue
        new, changed = add_layer(text, "STRUCTURAL", stext, SOURCE)
        if not changed:
            skipped += 1
            continue
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")
    print(f"STRUCT_SECONDARY STRUCTURAL: {'added' if args.apply else 'would add'} "
          f"{added:,}; skipped {skipped:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
