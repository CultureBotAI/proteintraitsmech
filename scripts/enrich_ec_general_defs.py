#!/usr/bin/env python3
"""Add a GENERAL definition layer to EC (enzyme) records from the EC nomenclature.

FUNCTION records read mechanistic — an EC record's `definition` is the catalysed
reaction ("… = … + ADP + H(+)"). This adds a plain "what kind of enzyme it is"
GENERAL layer composed from the EC class hierarchy (enzclass.txt), e.g.

    EC:2.7.1.157 → "A transferase; transferring phosphorus-containing groups;
                    phosphotransferases with an alcohol group as acceptor."

Added as definitions[{kind: GENERAL, method: SOURCED, source: EC nomenclature}];
the mechanistic `definition` string stays as-is.

Input: data/raw/ec/enzclass.txt  (just fetch-ec)
Idempotent (skips records already carrying a GENERAL definition); dry-run unless
--apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deflib import add_layer  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
ENZCLASS = REPO_ROOT / "data" / "raw" / "ec" / "enzclass.txt"
EC_DIR = REPO_ROOT / "data" / "traits" / "function" / "enzymatic_activity" / "ec"

CLASS_SINGULAR = {"1": "oxidoreductase", "2": "transferase", "3": "hydrolase",
                  "4": "lyase", "5": "isomerase", "6": "ligase", "7": "translocase"}
_LINE = re.compile(r"^\s*(\d+)\.\s*([\d-]+)\.\s*([\d-]+)\.-?\s+(.+?)\.?\s*$")


def load_class_names() -> dict[str, str]:
    """'2', '2.7', '2.7.1' → the nomenclature name at that level."""
    out: dict[str, str] = {}
    for line in ENZCLASS.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        c, sc, ssc, name = m.groups()
        key = ".".join(x for x in (c, sc, ssc) if x not in ("-", ""))
        out[key] = name.strip()
    return out


def compose(ec_id: str, names: dict[str, str]) -> str:
    parts = ec_id.split(".")
    c = parts[0]
    phrases = []
    cs = CLASS_SINGULAR.get(c)
    if cs:
        phrases.append(("an " if cs[0] in "aeiou" else "a ") + cs)
    for depth in (2, 3):                       # subclass, sub-subclass
        if len(parts) >= depth and parts[depth - 1] not in ("-", ""):
            nm = names.get(".".join(parts[:depth]))
            if nm:
                phrases.append(nm[0].lower() + nm[1:])
    return "; ".join(phrases)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not ENZCLASS.exists():
        print("missing data/raw/ec/enzclass.txt; run `just fetch-ec`", file=sys.stderr)
        return 2

    names = load_class_names()
    added = skipped = thin = 0
    for p in EC_DIR.glob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*EC:([\d.]+)", text)
        if not m:
            continue
        if re.search(r"kind:\s*GENERAL", text):
            skipped += 1
            continue
        desc = compose(m.group(1).rstrip("."), names)
        if not desc:
            thin += 1
            continue
        # deflib.add_layer appends into any existing `definitions:` list — never a
        # second block (which would be a duplicate mapping key, silently dropping
        # a co-present layer on load).
        new, changed = add_layer(text, "GENERAL", f"{desc[0].upper() + desc[1:]}.",
                                 "EC nomenclature (enzclass)")
        if not changed:
            skipped += 1
            continue
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    print(f"EC GENERAL definitions: {'added' if args.apply else 'would add'} {added:,} "
          f"| already had {skipped:,} | no class name {thin:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
