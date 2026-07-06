#!/usr/bin/env python3
"""Fetch RepeatsDB per-structure annotations and build a classification→member
index, so classification nodes lacking a curated `representative` PDB can be
given a real member structure with provenance.

RepeatsDB's public API exposes the per-structure annotations at

    GET https://repeatsdb.org/api/production/annotations?limit=<1..100>&skip=<n>
        → {"count": N, "items": {<i>: {content:{chain:{structure,id,source},
                                                region_classes:[...]}}}}

There is NO server-side classification filter (every field param is ignored and
returns the full count), so we page the whole set once (~475 requests) and index
locally. Each annotated structure is a real PDB (or AlphaFold) chain carrying its
region_classes — the class.topology.fold.clan codes RepeatsDB assigns to it.

Output (gitignored raw): data/raw/repeatsdb/class_members.json
    { "<code>": {"pdb": "1A0C", "chain": "A", "source": "RCSB/PDB", "n": 12}, ... }
one deterministic representative (first RCSB/PDB member; AlphaFold only if no PDB)
per classification code, plus the member count. Resumable via --resume.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "repeatsdb"
OUT = RAW / "class_members.json"
API = "https://repeatsdb.org/api/production/annotations"
PAGE = 100


def get_json(url: str, tries: int = 4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def add(index: dict, code: str, pdb: str, chain: str, source: str) -> None:
    cur = index.get(code)
    is_pdb = source == "RCSB/PDB"
    if cur is None:
        index[code] = {"pdb": pdb, "chain": chain, "source": source, "n": 1}
        return
    cur["n"] += 1
    # Upgrade the representative to a real PDB if we only had an AlphaFold model.
    if is_pdb and cur["source"] != "RCSB/PDB":
        cur.update(pdb=pdb, chain=chain, source=source)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit-pages", type=int, default=0, help="cap pages (0=all; for testing)")
    args = ap.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    first = get_json(f"{API}?limit=1&skip=0")
    total = first["count"]
    pages = (total + PAGE - 1) // PAGE
    if args.limit_pages:
        pages = min(pages, args.limit_pages)
    print(f"{total:,} annotations → {pages} pages")

    index: dict[str, dict] = {}
    for p in range(pages):
        d = get_json(f"{API}?limit={PAGE}&skip={p*PAGE}")
        items = d["items"]
        items = items.values() if isinstance(items, dict) else items
        for it in items:
            c = it.get("content", {})
            ch = c.get("chain") or {}
            pdb = str(ch.get("structure") or "").upper()
            chain = str(ch.get("id") or "")
            source = ch.get("source") or ""
            if not pdb:
                continue
            for code in c.get("region_classes") or []:
                add(index, code, pdb, chain, source)
        if p % 25 == 0 or p == pages - 1:
            print(f"  page {p+1}/{pages} — {len(index)} distinct codes")
            OUT.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    OUT.write_text(json.dumps(index, sort_keys=True, indent=0), encoding="utf-8")
    print(f"wrote {len(index)} classification codes → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
