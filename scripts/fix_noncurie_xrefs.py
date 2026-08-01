#!/usr/bin/env python3
"""Drop `xrefs:` entries that are not CURIEs — issue #90.

  python3 scripts/fix_noncurie_xrefs.py            # dry run, lists every offender
  python3 scripts/fix_noncurie_xrefs.py --apply

28 records fail closed-mode validation because an `xrefs` value does not match the
schema's `^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$`:

  * 27 DOIs across `function/{pathway,localization,molecular_function}/go`. A DOI
    always contains `/`, so **no DOI can ever be a valid xref** — this is a category
    error, not 27 malformed strings.
  * 1 literal placeholder `CATH:???????` in `structure/homologous_superfamily/cath`.

WHY DROPPING IS THE RIGHT FIX, NOT MOVING TO `evidence`
-------------------------------------------------------
`seed_obo.py` already discards DOI xrefs at parse time (`if prefix == "DOI" or "/"
in local: return None`), so these 28 predate that filter. Re-seeding today would
produce records without them, and this migration simply brings the data to what the
seeder already emits.

Moving them to `evidence` was considered and rejected: the **current** `go.obo`
release contains zero `xref: DOI:` lines, so there is no citation to preserve — the
DOIs came from an older release. Writing them into `evidence` would reintroduce data
the source no longer carries, and would leave the seeder and the corpus disagreeing.

Idempotent; dry-run unless --apply. Stdlib-only. Rewrites only the offending lines,
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    n_files = n_dropped = 0
    emptied = []
    for f in sorted(TRAITS.rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if "xrefs:" not in text:
            continue
        lines = text.splitlines(keepends=True)
        bad = offenders(lines)
        if not bad:
            continue
        rel = f.relative_to(REPO_ROOT)
        for i in bad:
            print(f"  {rel}\n      drop {lines[i].strip()}")
        kept = [ln for i, ln in enumerate(lines) if i not in set(bad)]
        # An xrefs: key whose every item was invalid must go too, or it becomes an
        # empty mapping value and stops parsing as a list.
        xi = next((i for i, ln in enumerate(kept) if ln.startswith("xrefs:")), None)
        if xi is not None and not _ITEM.match(kept[xi + 1] if xi + 1 < len(kept) else ""):
            kept.pop(xi)
            emptied.append(str(rel))
        n_files += 1
        n_dropped += len(bad)
        if args.apply:
            f.write_text("".join(kept), encoding="utf-8")

    print(f"\n  {n_dropped} non-CURIE xref(s) in {n_files} record(s)", file=sys.stderr)
    if emptied:
        print(f"  {len(emptied)} record(s) lost their whole xrefs list:", file=sys.stderr)
        for e in emptied:
            print(f"      {e}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
