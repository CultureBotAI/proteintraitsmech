#!/usr/bin/env python3
"""Populate the MECHANISTIC definition layer for the enzyme / active-site sources.

The audit (research/definition-state-review.md) found the MECHANISTIC layer empty
(0), even though the mechanistic content is real — it just lives unlabelled in the
main `definition` of:
  • EC   — "Catalysed reaction: …"  → MECHANISTIC = the catalysed reaction
  • Rhea — the reaction equation (the label) → MECHANISTIC = the reaction
  • M-CSA — a mechanism description → MECHANISTIC = that description

Labelling it as `definitions[{kind: MECHANISTIC}]` makes it a distinguishable
layer (browser detail, and the mechanistic dimension of the definition-only map).

Idempotent (skips records already carrying a MECHANISTIC definition); dry-run
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


def def_body(text: str) -> str:
    m = (re.search(r"(?m)^definition:[ \t]*>-\s*\n((?:[ \t]+.*\n)+)", text)
         or re.search(r"(?m)^definition:[ \t]+(?![>|]\s*$)(.+)$", text))
    return " ".join(m.group(1).split()) if m else ""


def label_of(text: str) -> str:
    m = re.search(r'(?m)^label:[ \t]+"?(.+?)"?\s*$', text)
    return m.group(1).strip() if m else ""


def mechanistic_text(prefix: str, text: str) -> tuple[str, str] | None:
    """(text, source) for the MECHANISTIC layer, or None."""
    body = def_body(text)
    if prefix == "EC":
        m = re.search(r"Catalysed reaction:\s*(.+?)\.?\s*$", body)
        rxn = m.group(1).strip() if m else ""
        return (f"Catalyses: {rxn}", "ExPASy ENZYME") if rxn else None
    if prefix == "RHEA":
        rxn = label_of(text)
        return (f"Catalyses the reaction: {rxn}", "Rhea") if rxn else None
    if prefix == "MCSA":
        return (body, "M-CSA") if body else None
    return None


def yfold(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    counts = {"EC": 0, "RHEA": 0, "MCSA": 0}
    skipped = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"(?m)^identifier:\s*(EC|RHEA|MCSA):", text)
        if not m:
            continue
        if "kind: MECHANISTIC" in text:
            skipped += 1
            continue
        got = mechanistic_text(m.group(1), text)
        if not got:
            continue
        mtext, source = got
        # deflib.add_layer appends into any existing `definitions:` list — never a
        # second block (a duplicate mapping key that silently drops a co-present
        # layer, e.g. the EC GENERAL layer, on load).
        new, changed = add_layer(text, "MECHANISTIC", mtext, source)
        if not changed:
            skipped += 1
            continue
        counts[m.group(1)] += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")

    total = sum(counts.values())
    print(f"MECHANISTIC definitions: {'added' if args.apply else 'would add'} {total:,} "
          f"({counts}); already had {skipped:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
