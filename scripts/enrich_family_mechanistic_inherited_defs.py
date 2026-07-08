#!/usr/bin/env python3
"""Inherit a MECHANISTIC definition layer onto protein-family / domain records
from the enzyme reaction they are annotated with.

A protein family or domain that carries a fully-specified EC number
(`EC:x.x.x.x`) has that catalysed reaction as its molecular-level mechanism. This
copies the reaction text from the corpus EC record's MECHANISTIC layer (populated
by enrich_mechanistic_defs) onto the family/domain record, with provenance
(source = "mapped enzyme <EC>"), so the mechanistic dimension covers families too
— not just the enzyme-activity records themselves.

Scope: FUNC_PROTEIN_FAMILY / FUNC_ORTHOLOG_GROUP / SEQ_FAMILY / SEQ_DOMAIN /
SEQ_HOMOLOGOUS_SUPERFAMILY records that (a) lack a MECHANISTIC layer and (b) carry
an EC xref resolving to a corpus EC record with a reaction. Among multiple ECs the
most descriptive reaction (longest text) is chosen, deterministic tie-break by EC.

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

CATS = {"FUNC_PROTEIN_FAMILY", "FUNC_ORTHOLOG_GROUP", "SEQ_FAMILY",
        "SEQ_DOMAIN", "SEQ_HOMOLOGOUS_SUPERFAMILY"}
_IDENT_EC = re.compile(r"(?m)^identifier:\s*(EC:\d+\.\d+\.\d+\.\d+)\s*$")
_CAT = re.compile(r"(?m)^trait_category:\s*(\S+)")
_EC_XREF = re.compile(r"(?m)^\s*-\s*(EC:\d+\.\d+\.\d+\.\d+)\s*$")
_MECH_LAYER = re.compile(
    r"(?ms)^\s*-\s*kind:\s*MECHANISTIC\s*\n\s*text:\s*>-\s*\n((?:\s+.*\n)+?)\s*source:")


def mech_text(text: str) -> str:
    m = _MECH_LAYER.search(text)
    return " ".join(m.group(1).split()) if m else ""


def build_ec_map() -> dict[str, str]:
    """EC identifier → its MECHANISTIC (reaction) text."""
    out: dict[str, str] = {}
    for p in TRAITS.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8")
        i = _IDENT_EC.search(t)
        if not i:
            continue
        mt = mech_text(t)
        if mt:
            out[i.group(1)] = mt
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    ec = build_ec_map()
    print(f"corpus EC records with MECHANISTIC text: {len(ec):,}", file=sys.stderr)

    added = skipped = 0
    by_cat: dict[str, int] = {}
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        cm = _CAT.search(text)
        if not cm or cm.group(1) not in CATS:
            continue
        if "kind: MECHANISTIC" in text:
            skipped += 1
            continue
        matches = [(e, ec[e]) for e in _EC_XREF.findall(text) if e in ec]
        if not matches:
            continue
        eid, etext = max(matches, key=lambda kv: (len(kv[1]), kv[0]))
        new, changed = add_layer(text, "MECHANISTIC", etext, f"mapped enzyme {eid}")
        if not changed:
            skipped += 1
            continue
        by_cat[cm.group(1)] = by_cat.get(cm.group(1), 0) + 1
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")
    print(f"family/domain MECHANISTIC (inherited): "
          f"{'added' if args.apply else 'would add'} {added:,} "
          f"({dict(sorted(by_cat.items()))}); skipped {skipped:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
