#!/usr/bin/env python3
"""Move non-CURIE citation `xrefs` into `evidence`; drop the rest — issue #90.

  python3 scripts/fix_noncurie_xrefs.py            # dry run, lists every change
  python3 scripts/fix_noncurie_xrefs.py --apply

28 records fail closed-mode validation because an `xrefs` value does not match the
schema's `^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$`:

  * 27 DOIs across `function/{pathway,localization,molecular_function}/go`. A DOI
    always contains `/`, so **no DOI can ever be a valid xref** — a category error,
    not 27 malformed strings. These are **moved to `evidence`**, whose `reference`
    range accepts a DOI.
  * 1 literal placeholder `CATH:???????`, which is a data bug and is **dropped**.

WHY MOVED AND NOT DROPPED — A CORRECTION
-----------------------------------------
An earlier version of this script dropped the DOIs, arguing that the current
`go.obo` carries none and that `seed_obo.py` already discards them, so nothing was
lost and a re-seed would not recreate them. **Both halves of that were wrong.**

`seed_obo.py` discards DOIs found on `xref:` lines, but these came from the `def:`
source brackets, which `normalise_source()` passed straight through into `xrefs`
with no CURIE check. And the current release does still carry them — 35 DOI
definition sources, including the one on GO:0072324:

    def: "Ascus cytoplasm that is not packaged into ascospores." [DOI:10.1016/S0953-7562(96)80057-8, GOC:mcc]

So a re-seed would have recreated every one of these failures, and dropping them
discarded live provenance that GO still asserts. `seed_obo.py` now routes citation
def-sources (DOI/PMID) to `evidence` instead of `xrefs`, and this migration brings
existing records to the same shape.

Idempotent; dry-run unless --apply. Stdlib-only. Rewrites only the lines it must,
leaving the rest of each hand-formatted record untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")
CITATION = re.compile(r"^(DOI|PMID):", re.I)
_ITEM = re.compile(r"^  - (.+?)\s*$")
_TOP_KEY = re.compile(r"^[A-Za-z_]")


def offenders(lines: list[str]) -> list[int]:
    """Indices of `xrefs:` list items whose value is not a CURIE."""
    out, inx = [], False
    for i, ln in enumerate(lines):
        if ln.startswith("xrefs:"):
            inx = True
            continue
        if not inx:
            continue
        m = _ITEM.match(ln)
        if not m:
            if ln.strip() and _TOP_KEY.match(ln):
                inx = False
            continue
        if not CURIE.match(m.group(1).strip().strip("\"'")):
            out.append(i)
    return out


def evidence_block(citations: list[str]) -> list[str]:
    out = ["evidence:\n"]
    for c in citations:
        out.append(f"  - reference: {c}\n")
        out.append("    notes: GO definition source (moved from xrefs; a DOI is not "
                   "a CURIE)\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    n_files = n_moved = n_dropped = 0
    for f in sorted(TRAITS.rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if "xrefs:" not in text:
            continue
        lines = text.splitlines(keepends=True)
        bad = offenders(lines)
        if not bad:
            continue
        rel = f.relative_to(REPO_ROOT)
        bad_set = set(bad)
        citations, dropped = [], []
        for i in bad:
            v = _ITEM.match(lines[i]).group(1).strip().strip("\"'")
            (citations if CITATION.match(v) else dropped).append(v)
        for c in citations:
            print(f"  {rel}\n      move to evidence: {c}")
        for d in dropped:
            print(f"  {rel}\n      drop:             {d}")

        kept = [ln for i, ln in enumerate(lines) if i not in bad_set]
        # An xrefs: key whose every item was invalid must go too, or it is left as an
        # empty mapping value and stops parsing as a list.
        xi = next((i for i, ln in enumerate(kept) if ln.startswith("xrefs:")), None)
        if xi is not None and not _ITEM.match(kept[xi + 1] if xi + 1 < len(kept) else ""):
            kept.pop(xi)

        if citations:
            # `evidence` belongs before `license:`, the record's last key by
            # convention; merge into an existing block if the record already has one.
            ei = next((i for i, ln in enumerate(kept) if ln.startswith("evidence:")), None)
            if ei is not None:
                end = ei + 1
                while end < len(kept) and not _TOP_KEY.match(kept[end]):
                    end += 1
                kept = kept[:end] + evidence_block(citations)[1:] + kept[end:]
            else:
                lic = next((i for i, ln in enumerate(kept)
                            if ln.startswith("license:")), len(kept))
                kept = kept[:lic] + evidence_block(citations) + kept[lic:]

        n_files += 1
        n_moved += len(citations)
        n_dropped += len(dropped)
        if args.apply:
            f.write_text("".join(kept), encoding="utf-8")

    print(f"\n  {n_moved} citation(s) moved to evidence, {n_dropped} dropped, "
          f"across {n_files} record(s)", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
