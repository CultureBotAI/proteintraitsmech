#!/usr/bin/env python3
"""Phase-1 cross-source equivalence overlay (research/entry-merge-methods-round1.md).

Emits biolink:close_match edges between entries that a source has ALREADY
integrated as equivalent — no compute, highest confidence. Round 1 uses the
InterPro member-DB integration: every member signature (Pfam / PROSITE / CDD /
NCBIfam / CATH-Gene3D / SMART / …) that InterPro folds into an entry is
close_match to that InterPro entry (and, transitively, to its co-members).

Output is a version-controlled OVERLAY (not written onto 70k records): a TSV
`data/equivalence/cross_source.tsv` (subject, predicate, object, source). This
is KG-export-ready and is loaded by build_docs_index to show an "Equivalent
entries" row in the browser — so it stays scalability-neutral.

Input:  data/raw/interpro/interpro.xml.gz  (member_list per InterPro entry)
        docs/data/records.*.json           (the set of ids actually in the corpus)
Idempotent; writes the TSV. Stdlib-only.
"""

from __future__ import annotations

import glob
import gzip
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
XML = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
SHARDS = REPO_ROOT / "docs" / "data"
OUT = REPO_ROOT / "data" / "equivalence" / "cross_source.tsv"


def member_curie(db: str, dbkey: str) -> str | None:
    """Map an InterPro member db_xref to our record CURIE (only the member DBs
    we actually seed)."""
    if db == "PFAM" and dbkey.startswith("PF"):
        return f"Pfam:{dbkey}"
    if db in ("PROSITE", "PROFILE") and dbkey.startswith("PS"):
        return f"PROSITE:{dbkey}"
    if db == "CDD" and dbkey.startswith(("cd", "sd")):
        return f"CDD:{dbkey}"
    if db == "NCBIFAM" and dbkey.startswith("NF"):
        return f"NCBIfam:{dbkey.split('.')[0]}"
    if db == "GENE3D":
        m = re.match(r"G3DSA:(\d+\.\d+\.\d+\.\d+)$", dbkey)
        if m:
            return f"CATH:{m.group(1)}"
    return None


def load_ids() -> set[str]:
    ids: set[str] = set()
    for f in glob.glob(str(SHARDS / "records.*.json")):
        for r in json.load(open(f)):
            ids.add(r["id"])
    return ids


def main() -> int:
    if not XML.exists():
        print("missing data/raw/interpro/interpro.xml.gz; run `just fetch-interpro`",
              file=sys.stderr)
        return 2
    ids = load_ids()
    if not ids:
        print("no records.*.json — run `just build-docs` first", file=sys.stderr)
        return 2
    print(f"{len(ids):,} record ids loaded")

    edges: list[tuple[str, str, str]] = []
    from_db: dict[str, int] = {}
    with gzip.open(XML, "rb") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = "InterPro:" + (el.get("id") or "")
            ml = el.find("member_list")
            if ipr in ids and ml is not None:
                for x in ml.findall("db_xref"):
                    cur = member_curie(x.get("db", ""), x.get("dbkey", ""))
                    if cur and cur in ids and cur != ipr:
                        edges.append((cur, ipr, x.get("db")))
                        from_db[x.get("db")] = from_db.get(x.get("db"), 0) + 1
            el.clear()

    # de-dup
    seen = set()
    uniq = []
    for s, o, db in edges:
        if (s, o) not in seen:
            seen.add((s, o))
            uniq.append((s, o, db))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, o, db in sorted(uniq):
            fh.write(f"{s}\tbiolink:close_match\t{o}\tinterpro:{db.lower()}\n")

    print(f"wrote {len(uniq):,} close_match edges → {OUT.relative_to(REPO_ROOT)}")
    print("  by member db:", {k: v for k, v in sorted(from_db.items(), key=lambda x: -x[1])})
    return 0


if __name__ == "__main__":
    sys.exit(main())
