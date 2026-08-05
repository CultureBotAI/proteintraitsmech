#!/usr/bin/env python3
"""Fetch InterPro member-database signature lists from the EBI API (#162).

WHY AN API AND NOT A BULK FILE
------------------------------
InterPro's FTP carries no per-member-database file -- `names.dat` and
`short_names.dat` are InterPro entries only. The member signatures appear in
`interpro.xml.gz` inside `<member_list>`, but two things are missing there:

  * **SUPERFAMILY has no name at all.** 0 of 1,649 SSF `db_xref` elements carry a
    non-empty `name=` attribute. The API gives
    "Lesion bypass DNA polymerase (Y-family), little finger domain".
  * the names that ARE present are cryptic short forms -- SMART's `SM00002` is
    `KR` in the XML and "Myelin proteolipid protein (PLP or lipophilin)" in the API.

The API also lists signatures InterPro has not integrated, which the XML cannot
mention at all (SFLD 303 vs 163, SSF 2,019 vs 1,649).

Going to the member databases' own sites was the alternative and is not viable:
SUPERFAMILY's hosts (supfam.org, supfam.mrc-lmb.cam.ac.uk) all time out, and
SMART's and HAMAP's licences restrict redistribution in ways EBI's do not.

Writes one JSONL per database to data/raw/interpro_members/<db>.jsonl, one
signature per line, so the seeder never needs the network.

    python3 scripts/fetch_interpro_members.py --db pirsf
    python3 scripts/fetch_interpro_members.py --all
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw" / "interpro_members"
API = "https://www.ebi.ac.uk/interpro/api/entry/{db}/?page_size={n}"

# Files EBI hosts for a member database that the API does not expose. SFLD's
# superfamily/group/family hierarchy is the case that matters: the API reports
# `hierarchy: null` for every SFLD accession at all three levels, so without this
# a subgroup literally named "I" (SFLDG01162) arrives with nothing to say which
# superfamily it is subgroup I *of*.
EXTRA_FILES = {
    "sfld": ["https://ftp.ebi.ac.uk/pub/databases/interpro/databases/sfld/4/"
             "sfld_hierarchy_flat.txt"],
}

# The six UniProt "Family and domain databases" that PTM has no records for.
# Keys are InterPro's own `source_database` spelling, which is also the API path.
DATABASES = ("pirsf", "prints", "ssf", "sfld", "smart", "hamap")

PAGE_SIZE = 200
RETRIES = 4
USER_AGENT = "ProteinTraitsMech/1.0 (+https://github.com/CultureBotAI/proteintraitsmech)"


def get(url: str) -> dict:
    """One API page, with backoff. A partial fetch must fail loudly, not truncate."""
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as fh:
                return json.loads(fh.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt < RETRIES - 1:
                time.sleep(2 ** attempt)
    raise SystemExit(f"giving up on {url}: {last}")


def fetch_db(db: str, apply: bool) -> int:
    url = API.format(db=db, n=PAGE_SIZE)
    rows: list[dict] = []
    expected = None
    page = 0
    while url:
        data = get(url)
        if expected is None:
            expected = data.get("count")
        for r in data.get("results", []):
            m = r.get("metadata") or {}
            if not m.get("accession"):
                continue
            rows.append({"accession": m["accession"], "name": m.get("name") or "",
                         "type": m.get("type") or "", "integrated": m.get("integrated"),
                         "source_database": m.get("source_database") or db})
        url = data.get("next")
        page += 1
        print(f"    {db}: page {page}, {len(rows):,}/{expected:,}", file=sys.stderr)

    # The API reports its own total; a short read means a dropped page, and a
    # silently short release would seed a silently incomplete source.
    if expected is not None and len(rows) != expected:
        raise SystemExit(f"{db}: got {len(rows)} signatures, API reported {expected} "
                         f"-- refusing to write a partial release")

    if apply:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for extra in EXTRA_FILES.get(db, []):
            name = extra.rsplit("/", 1)[-1]
            req = urllib.request.Request(extra, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=90) as fh:
                (OUT_DIR / name).write_bytes(fh.read())
            print(f"  {db}: fetched {name}")
        out = OUT_DIR / f"{db}.jsonl"
        out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                       encoding="utf-8")
        print(f"  {db}: wrote {len(rows):,} → {out.relative_to(REPO_ROOT)}")
    else:
        print(f"  {db}: {len(rows):,} signatures (dry run)")
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", action="append", choices=DATABASES,
                    help="fetch one database (repeatable)")
    ap.add_argument("--all", action="store_true", help="fetch every database")
    ap.add_argument("--apply", action="store_true", help="write files")
    args = ap.parse_args()

    dbs = tuple(args.db) if args.db else (DATABASES if args.all else ())
    if not dbs:
        ap.error("pass --db <name> or --all")

    total = 0
    for db in dbs:
        total += fetch_db(db, args.apply)
    print(f"total: {total:,} signatures across {len(dbs)} database(s)")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
