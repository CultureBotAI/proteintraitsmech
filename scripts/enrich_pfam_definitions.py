#!/usr/bin/env python3
"""Backfill rich Pfam definitions from InterPro abstracts (record-sample-review-1
S1 for Pfam). Pfam merged into InterPro, and the '#=GF CC' prose that Pfam-A.hmm.dat
lacks is now the InterPro entry ABSTRACT. pfam2interpro maps ~29.7k Pfam families
to an InterPro entry; interpro.xml.gz (already fetched) carries the abstracts.

For each Pfam record whose family maps to an InterPro entry with a non-trivial
abstract, replace the boilerplate definition ('<name>. Pfam <type> family …')
with that abstract. In place (preserves sequence_pattern / clan member_of /
mapped_xrefs / license). Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
PF2IPR = REPO_ROOT / "data" / "raw" / "mappings" / "pfam2interpro.tsv"
XML_GZ = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
ID_RE = re.compile(r"^identifier:\s*(Pfam:PF\d+)", re.M)
DEF_CAP = 1800


def clean_abstract(el) -> str:
    if el is None:
        return ""
    text = " ".join("".join(el.itertext()).split())
    text = re.sub(r"\s*\[\s*(?:,\s*)*\]", "", text)     # empty [ ] / [ , ] cite stubs
    text = " ".join(text.split())
    if len(text) > DEF_CAP:
        text = text[:DEF_CAP - 1].rstrip() + "…"
    return text


def load_pf2ipr() -> dict[str, str]:
    out = {}
    for line in PF2IPR.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].startswith("PF"):
            out[parts[0]] = parts[1].strip()
    return out


def load_ipr_abstracts(wanted: set[str]) -> dict[str, str]:
    out = {}
    with gzip.open(XML_GZ, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id", "")
            if ipr in wanted:
                ab = clean_abstract(el.find("abstract"))
                if len(ab) >= 40:                        # skip empty/near-empty
                    out[ipr] = ab
            el.clear()
    return out


def set_definition(text: str, new_def: str) -> str:
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("definition:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                j += 1
            block = ["definition: >-", "  " + " ".join(new_def.split())]
            return "\n".join(lines[:i] + block + lines[j:])
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for f in (PF2IPR, XML_GZ):
        if not f.exists():
            print(f"missing {f}; run `just fetch-pfam` / `just fetch-interpro`", file=sys.stderr)
            return 2

    pf2ipr = load_pf2ipr()
    pfam_dirs = [TRAITS / "sequence" / d / "pfam" for d in
                 ("domain", "family", "homologous_superfamily", "repeat", "disorder", "motif")]
    pfam_dirs.append(TRAITS / "mixed" / "coiled_coil" / "pfam")
    records = []
    for d in pfam_dirs:
        for path in d.rglob("*.yaml") if d.exists() else []:
            m = ID_RE.search(path.read_text(encoding="utf-8", errors="replace"))
            if m:
                records.append((path, m.group(1).split(":", 1)[1]))

    wanted = {pf2ipr[pf] for _, pf in records if pf in pf2ipr}
    print(f"{len(records):,} Pfam records; {len(wanted):,} distinct InterPro targets — reading abstracts…")
    abstracts = load_ipr_abstracts(wanted)
    print(f"{len(abstracts):,} InterPro entries have a usable abstract")

    updated = 0
    for path, pf in records:
        ab = abstracts.get(pf2ipr.get(pf, ""))
        if not ab:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new = set_definition(text, ab)
        if new != text:
            updated += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")

    verb = "updated" if args.apply else "would update"
    print(f"{verb} {updated:,} Pfam definitions from InterPro abstracts"
          + ("" if args.apply else "  (dry-run; pass --apply)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
