#!/usr/bin/env python3
"""Route 2 — ground existing InterPro and Pfam records to CAZy families.

InterPro (public domain) cross-references CAZy families (db="CAZY" dbkey="GH27").
This adds those CAZy families as `mapped_xrefs` on:
  • InterPro records whose IPR entry carries the CAZy cross-ref (direct);
  • Pfam records whose InterPro mapping (their existing InterPro mapped_xref) has
    the CAZy cross-ref (one hop: Pfam → InterPro → CAZy).

The link is asserted by InterPro, not by the record's own source, so it is a
`mapped_xref` (with mapping_source), never a direct xref. Idempotent (skips a
record that already carries the CAZy family); dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INTERPRO_XML = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
TRAITS = REPO_ROOT / "data" / "traits"


def ipr2cazy() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    with gzip.open(INTERPRO_XML, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id")
            fams = sorted({x.get("dbkey") for x in el.iter("db_xref")
                           if x.get("db") == "CAZY" and x.get("dbkey")})
            if fams:
                out[ipr] = fams
            el.clear()
    return out


def append_mapped(text: str, fams: list[str], source: str) -> tuple[str, int]:
    """Add CAZy mapped_xrefs not already present. Returns (new_text, n_added)."""
    have = set(re.findall(r"object:\s*(CAZy:\S+)", text))
    add = [f for f in fams if f"CAZy:{f}" not in have]
    if not add:
        return text, 0
    # Match the file's existing list-item indentation (Pfam uses 0-space items,
    # InterPro 2-space) so we never mix indents within a block.
    mm = re.search(r"^mapped_xrefs:[ \t]*\n([ \t]*)-", text, re.M)
    gen = re.search(r"^([ \t]*)-[ \t]+object:", text, re.M)
    ind = mm.group(1) if mm else (gen.group(1) if gen else "")
    block = "".join(f"{ind}- object: CAZy:{f}\n"
                    f"{ind}  predicate: skos:relatedMatch\n"
                    f"{ind}  mapping_source: {source}\n" for f in add)
    if re.search(r"^mapped_xrefs:[ \t]*$", text, re.M):
        text = re.sub(r"(^mapped_xrefs:[ \t]*\n)", r"\1" + block, text, count=1, flags=re.M)
    else:  # insert a mapped_xrefs section before `license:` (or at end)
        sect = "mapped_xrefs:\n" + block
        text = re.sub(r"(?m)^(license:.*)$", sect + r"\1", text, count=1) \
            if re.search(r"^license:", text, re.M) else text.rstrip("\n") + "\n" + sect
    return text, len(add)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()
    if not INTERPRO_XML.exists():
        print("missing interpro.xml.gz; run `just fetch-interpro`", file=sys.stderr)
        return 2

    i2c = ipr2cazy()
    print(f"{len(i2c)} InterPro entries carry a CAZy cross-ref")
    stats = {"interpro": 0, "pfam": 0}

    # InterPro records: direct.
    for p in (TRAITS).rglob("*.yaml"):
        if "/interpro/" not in str(p) and "/pfam/" not in str(p):
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(r"^identifier:\s*(\S+)", text, re.M)
        if not m:
            continue
        ident = m.group(1)
        if ident.startswith("InterPro:"):
            fams = i2c.get(ident.split(":", 1)[1])
            src = "InterPro CAZY cross-reference"
            key = "interpro"
        elif ident.startswith("Pfam:"):
            # Pfam → its InterPro mapped_xref(s) → CAZy
            iprs = re.findall(r"object:\s*InterPro:(\S+)", text)
            fams = sorted({f for ip in iprs for f in i2c.get(ip, [])})
            src = "Pfam→InterPro→CAZY (InterPro cross-reference)"
            key = "pfam"
        else:
            continue
        if not fams:
            continue
        new, n = append_mapped(text, list(fams), src)
        if n and args.apply:
            p.write_text(new, encoding="utf-8")
        if n:
            stats[key] += 1

    print(f"{'Grounded' if args.apply else 'Would ground'}: "
          f"{stats['interpro']} InterPro records, {stats['pfam']} Pfam records")
    if not args.apply:
        print("Dry-run — re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
