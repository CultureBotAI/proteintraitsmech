#!/usr/bin/env python3
"""Rename NCBIfam record files to the seeder's current slug convention.

seed_ncbifam.py names a file `{slugify(label)}-{acc}.yaml`, and the label is now
the readable product_name (record-sample-review S5). But the ~38k on-disk records
were written under an earlier convention that slugified the terse HMM *model* name
(e.g. `lhat-lp-ac-tran-nf052528.yaml`), so the seeder no longer recognises them as
existing → a `--force` re-seed would create product-named duplicates instead of
overwriting. This renames each file to `{slugify(current label)}-{acc}.yaml`,
restoring idempotency. Filenames are cosmetic — records key by `identifier`, and
the accession stays in the name — so this is a pure rename (content unchanged).

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seed_ncbifam as S  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
NCBIFAM_DIRS = [
    "function/protein_family/ncbifam", "sequence/domain/ncbifam",
    "sequence/family/ncbifam", "sequence/repeat/ncbifam",
    "sequence/homologous_superfamily/ncbifam",
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="rename files (default: dry-run)")
    args = ap.parse_args()

    renamed = ok = collide = 0
    for sub in NCBIFAM_DIRS:
        d = REPO_ROOT / "data" / "traits" / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.yaml")):
            text = p.read_text(encoding="utf-8")
            acc = re.search(r"(?m)^identifier:\s*NCBIfam:(\S+)", text)
            lab = re.search(r'(?m)^label:\s*"?(.+?)"?\s*$', text)
            if not acc or not lab:
                continue
            target = f"{S.slugify(lab.group(1))}-{acc.group(1).lower()}.yaml"
            if p.name == target:
                ok += 1
                continue
            dst = d / target
            if dst.exists() and dst != p:            # unexpected slug collision
                collide += 1
                print(f"  COLLISION: {p.name} → {target} (exists)")
                continue
            renamed += 1
            if args.apply:
                p.rename(dst)

    print(f"NCBIfam filenames: {'renamed' if args.apply else 'would rename'} {renamed:,} "
          f"| already correct {ok:,} | collisions {collide}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
