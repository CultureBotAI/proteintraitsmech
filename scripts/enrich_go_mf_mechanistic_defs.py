#!/usr/bin/env python3
"""Populate the MECHANISTIC definition layer for GO molecular-function records.

A GO molecular-function IS a molecular-level mechanism — a catalysed reaction, a
binding interaction, or a transport/transfer — so its main `definition` already
carries mechanistic content; it is just untyped. This composer extracts that core
and adds it as `definitions[{kind: MECHANISTIC}]`, so the mechanistic dimension of
the definition-only map and the browser can surface it (consistent with how
enrich_mechanistic_defs treats EC/Rhea/M-CSA).

MECHANISTIC covers molecular interactions and binding, not only catalysis
(mechanistic-layer-covers-interactions-not-just-reactions):
  • "Catalysis of the reaction: X = Y."        → "Catalyses: X = Y"
  • "Binding to X." / "Binds …" / "Combining…" → the binding interaction (verbatim)
  • "…transfer of X …" / "…transmembrane…"      → the transport/transfer (verbatim)
Records whose molecular function isn't a reaction/binding/transport (e.g. bare
"catalysis", "molecular adaptor activity") are skipped — no faithful mechanistic
core to lift.

Idempotent (skips records already carrying a MECHANISTIC layer); appends into any
existing `definitions:` list via deflib. Dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deflib import add_layer, def_body  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits" / "function" / "molecular_function"
SOURCE = "Gene Ontology"

_RXN = re.compile(r"^Catalysis of the reactions?:\s*(.+?)\.?\s*$", re.I)
_BIND = re.compile(r"^(Binding\b.*|Binds\b.*|Combining with\b.*|"
                   r"Interacting selectively(?: and non-covalently)?\b.*)$", re.I)
_TRANS = re.compile(r"(transfer of|transmembrane transfer|transport of|"
                    r"catalysis of the transfer)", re.I)


def mechanistic(body: str) -> str | None:
    """The MECHANISTIC core of a GO-MF definition, or None if not applicable."""
    if not body:
        return None
    m = _RXN.match(body)
    if m:
        return f"Catalyses: {m.group(1).strip()}"
    if _BIND.match(body):
        return body.rstrip(".") + "."
    if _TRANS.search(body):
        return body.rstrip(".") + "."
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    added = skipped = na = 0
    kinds = {"reaction": 0, "binding": 0, "transport": 0}
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8")
        if "kind: MECHANISTIC" in text:
            skipped += 1
            continue
        body = def_body(text)
        mtext = mechanistic(body)
        if not mtext:
            na += 1
            continue
        new, changed = add_layer(text, "MECHANISTIC", mtext, SOURCE)
        if not changed:
            skipped += 1
            continue
        kinds["reaction" if mtext.startswith("Catalyses:") else
              "transport" if _TRANS.search(body) and not _BIND.match(body)
              else "binding"] += 1
        added += 1
        if args.apply:
            p.write_text(new, encoding="utf-8")
    print(f"GO-MF MECHANISTIC: {'added' if args.apply else 'would add'} {added:,} "
          f"({kinds}); already had {skipped:,}; no mechanistic core {na:,}")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
