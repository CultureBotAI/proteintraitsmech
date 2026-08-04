#!/usr/bin/env python3
"""Report text-encoding damage across the corpus, by source and by kind.

A data gate in the style of `audit_causal_graphs.py`, not a unit test: it walks all
424k records, so it belongs behind `just audit-text` rather than in `just test`, which
the justfile is explicit does not touch `data/traits`.

THREE KINDS, WHICH NEED DIFFERENT ANSWERS
------------------------------------------
* **mojibake** (`â€`, `Ã¼`) — UTF-8 read as cp1252. A pure byte round trip, so it is
  REVERSIBLE: `yaml_emit.repair_mojibake` undoes it, and #123 did.
* **C1 controls** (U+0080–U+009F) — usually the tail of the same damage.
* **U+FFFD** — the replacement character. **Not reversible.** The original bytes are
  already gone by the time the text reaches us, so there is nothing to decode back; the
  only routes are inferring the character or getting a better source.

Reporting them separately matters because the first two are a bug to fix and the third
is a fact to decide about (#139).
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TRAITS = REPO / "data" / "traits"

KINDS = {
    "mojibake": re.compile("\u00e2\u20ac|\u00c3\u00a2|\u00c3\u00bc|\u00c3\u00a9"),
    "C1 control": re.compile("[\u0080-\u009f]"),
    "U+FFFD (lossy)": re.compile("\ufffd"),
}
_SRC = re.compile(r"^identifier:\s*([A-Za-z0-9_]+):", re.M)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default=str(TRAITS),
                    help="scope to a subdirectory (default: all of data/traits)")
    ap.add_argument("--list", action="store_true", help="print every affected record")
    args = ap.parse_args()

    root = pathlib.Path(args.path)
    by_kind: dict[str, collections.Counter] = {k: collections.Counter() for k in KINDS}
    hits: list[tuple[str, str, pathlib.Path]] = []
    scanned = 0

    for p in root.rglob("*.yaml"):
        scanned += 1
        text = p.read_text(encoding="utf-8")
        if text.isascii():          # the overwhelming majority; skip the regexes
            continue
        src = (_SRC.search(text) or [0, "?"])[1]
        for kind, pat in KINDS.items():
            if pat.search(text):
                by_kind[kind][src] += 1
                hits.append((kind, src, p))

    print(f"text-quality audit: {scanned:,} records scanned")
    total = 0
    for kind, counts in by_kind.items():
        n = sum(counts.values())
        total += n
        detail = "  ".join(f"{s}={c}" for s, c in counts.most_common(5)) or "none"
        print(f"  {kind:<18}{n:>6}   {detail}")
    if args.list:
        for kind, src, p in sorted(hits):
            print(f"    {kind:<18}{src:<16}{p.relative_to(REPO)}")

    # Reversible damage is a defect and should be zero; U+FFFD is a recorded fact (#139).
    reversible = sum(by_kind["mojibake"].values()) + sum(by_kind["C1 control"].values())
    if reversible:
        print(f"\n  {reversible} record(s) carry REVERSIBLE damage — repair_mojibake "
              f"should fix these", file=sys.stderr)
        return 1
    print("\n  no reversible damage", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
