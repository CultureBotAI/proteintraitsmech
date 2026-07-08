#!/usr/bin/env python3
"""Inherit a STRUCTURAL definition layer onto SEQUENCE records from the fold they
map to.

STRUCTURAL (molecular structure) has wide relevance beyond the structure axis: a
sequence domain/family/repeat that cross-references a structural classification
(CATH / SCOP / ECOD / TED / Gene3D / SUPERFAMILY) adopts that fold, so the fold's
structural description applies to it. This composer copies the mapped fold
record's STRUCTURAL layer onto the sequence record, with explicit provenance
("Adopts the fold of <fold-id>: …", source = "mapped fold <fold-id>"), so the
structural dimension of the definition-only map and the browser cover sequence
traits too.

Only records with a fold xref that resolves to a structure record carrying a
STRUCTURAL layer are enriched (~5% of SEQ_DOMAIN today — broader coverage needs
Pfam→CATH-style mappings that aren't in the corpus yet). Among multiple matching
folds the most descriptive (longest STRUCTURAL text) is chosen, deterministic
tie-break by id.

Idempotent (skips records already carrying a STRUCTURAL layer); appends into any
existing `definitions:` list via deflib. Dry-run unless --apply. Stdlib-only.
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
SEQ_DIR = TRAITS / "sequence"
STRUCT_DIR = TRAITS / "structure"

SEQ_CATS = {"SEQ_DOMAIN", "SEQ_FAMILY", "SEQ_HOMOLOGOUS_SUPERFAMILY",
            "SEQ_MOTIF", "SEQ_REPEAT", "SEQ_DISORDER"}
FOLD_PREFIXES = ("CATH:", "SCOP:", "SCOP2:", "ECOD:", "TED:", "Gene3D:",
                 "SUPERFAMILY:")
_IDENT = re.compile(r"(?m)^identifier:\s*(\S+)")
_CAT = re.compile(r"(?m)^trait_category:\s*(\S+)")
_REF = re.compile(r'(?m)^\s*-\s*([A-Za-z0-9]+:[^\s"]+)')
_STRUCT_LAYER = re.compile(
    r"(?ms)^\s*-\s*kind:\s*STRUCTURAL\s*\n\s*text:\s*>-\s*\n((?:\s+.*\n)+?)\s*source:")


def structural_text(text: str) -> str:
    m = _STRUCT_LAYER.search(text)
    return " ".join(m.group(1).split()) if m else ""


def build_fold_map() -> dict[str, str]:
    """fold identifier → its STRUCTURAL layer text."""
    out: dict[str, str] = {}
    for p in STRUCT_DIR.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8")
        i = _IDENT.search(t)
        if not i:
            continue
        st = structural_text(t)
        if st:
            out[i.group(1)] = st
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    fold = build_fold_map()
    print(f"structure records with STRUCTURAL text: {len(fold):,}", file=sys.stderr)

    added = skipped = 0
    by_cat: dict[str, int] = {}
    for p in SEQ_DIR.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        cm = _CAT.search(text)
        if not cm or cm.group(1) not in SEQ_CATS:
            continue
        if "kind: STRUCTURAL" in text:
            skipped += 1
            continue
        matches = [(f, fold[f]) for f in _REF.findall(text)
                   if f.startswith(FOLD_PREFIXES) and f in fold]
        if not matches:
            continue
        # most descriptive fold (longest text), deterministic tie-break by id
        fid, ftext = max(matches, key=lambda kv: (len(kv[1]), kv[0]))
        layer = f"Adopts the fold of {fid}: {ftext}"
        new, changed = add_layer(text, "STRUCTURAL", layer, f"mapped fold {fid}")
        if not changed:
            skipped += 1
            continue
        by_cat[cm.group(1)] = by_cat.get(cm.group(1), 0) + 1
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")
    print(f"SEQ STRUCTURAL (inherited): {'added' if args.apply else 'would add'} "
          f"{added:,} ({dict(sorted(by_cat.items()))}); skipped {skipped:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
