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
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from prints_snapshot import (
    EXPECTED_PRINTS_SNAPSHOT_ID,
    HIERARCHY_NAME,
    MANIFEST_NAME,
    PrintsSnapshotError,
    build_prints_manifest,
    dump_hierarchy_jsonl,
    dump_manifest,
    parse_hierarchy_source,
    require_expected_manifest_id,
    verify_prints_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw" / "interpro_members"
INTERPRO_XML = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
API = "https://www.ebi.ac.uk/interpro/api/entry/{db}/?page_size={n}"

# Files EBI hosts for a member database that the API does not expose. SFLD's
# superfamily/group/family hierarchy is the case that matters: the API reports
# `hierarchy: null` for every SFLD accession at all three levels, so without this
# a subgroup literally named "I" (SFLDG01162) arrives with nothing to say which
# superfamily it is subgroup I *of*.
EXTRA_FILES = {
    "sfld": ["https://ftp.ebi.ac.uk/pub/databases/interpro/databases/sfld/4/"
             "sfld_hierarchy_flat.txt"],
    # PRINTS needs two. The API's `name` for a fingerprint is its CODE, not a
    # name -- PR00001 comes back as "GLABLOOD", and the detail endpoint shows
    # why: {"name": null, "short": "GLABLOOD"}. There is no full name in the API
    # at all. The .kdat carries a real title ("Glassy blood signature") for all
    # 2,106, plus the motif count. The hierarchy file is the same story as SFLD.
    "prints": ["https://ftp.ebi.ac.uk/pub/databases/interpro/databases/prints/"
               "42.0/prints42_0.kdat",
               "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/prints/"
               "42.0/FingerPRINTShierarchy21Feb2012"],
}

# The six UniProt "Family and domain databases" that PTM has no records for.
# Keys are InterPro's own `source_database` spelling, which is also the API path.
DATABASES = ("pirsf", "prints", "ssf", "sfld", "smart", "hamap")

PAGE_SIZE = 200
RETRIES = 4
USER_AGENT = "ProteinTraitsMech/1.0 (+https://github.com/CultureBotAI/proteintraitsmech)"


def _api_jsonl(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def _install_prints_snapshot(rows: list[dict], extras: dict[str, bytes]) -> dict:
    """Stage, replay, and install a complete PRINTS snapshot; manifest last."""

    kdat_name = "prints42_0.kdat"
    raw_hierarchy_name = "FingerPRINTShierarchy21Feb2012"
    missing = sorted({kdat_name, raw_hierarchy_name} - set(extras))
    if missing:
        raise PrintsSnapshotError(f"downloaded PRINTS snapshot lacks {missing!r}")
    if not INTERPRO_XML.is_file():
        raise PrintsSnapshotError(
            f"local InterPro XML required by the PRINTS seeder is absent: {INTERPRO_XML}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".prints-snapshot-", dir=OUT_DIR) as tmp:
        stage = Path(tmp)
        api_path = stage / "prints.jsonl"
        kdat_path = stage / kdat_name
        raw_hierarchy_path = stage / raw_hierarchy_name
        hierarchy_path = stage / HIERARCHY_NAME
        manifest_path = stage / MANIFEST_NAME

        api_path.write_bytes(_api_jsonl(rows))
        kdat_path.write_bytes(extras[kdat_name])
        raw_hierarchy_path.write_bytes(extras[raw_hierarchy_name])
        hierarchy_rows = parse_hierarchy_source(extras[raw_hierarchy_name])
        hierarchy_path.write_bytes(dump_hierarchy_jsonl(hierarchy_rows))
        manifest = build_prints_manifest(
            api_path=api_path,
            kdat_path=kdat_path,
            hierarchy_path=hierarchy_path,
            interpro_xml_path=INTERPRO_XML,
        )
        # Do not install a newly fetched, self-consistent snapshot unless its
        # full four-artifact identity is the reviewed production identity.
        require_expected_manifest_id(
            manifest.get("manifest_id"), EXPECTED_PRINTS_SNAPSHOT_ID
        )
        manifest_path.write_bytes(dump_manifest(manifest))
        verify_prints_manifest(
            manifest_path,
            expected_manifest_id=EXPECTED_PRINTS_SNAPSHOT_ID,
            api_path=api_path,
            kdat_path=kdat_path,
            hierarchy_path=hierarchy_path,
            interpro_xml_path=INTERPRO_XML,
        )

        # A crash during replacement leaves either the old manifest or no new
        # manifest matching the files, so the seeder fails closed. Install the
        # new manifest only after every source artefact is in its final place.
        for source in (api_path, kdat_path, raw_hierarchy_path, hierarchy_path):
            source.replace(OUT_DIR / source.name)
        manifest_path.replace(OUT_DIR / MANIFEST_NAME)
    return manifest


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
        extras: dict[str, bytes] = {}
        for extra in EXTRA_FILES.get(db, []):
            name = extra.rsplit("/", 1)[-1]
            req = urllib.request.Request(extra, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=90) as fh:
                extras[name] = fh.read()
            print(f"  {db}: fetched {name}")
        if db == "prints":
            try:
                manifest = _install_prints_snapshot(rows, extras)
            except PrintsSnapshotError as error:
                raise SystemExit(f"prints: refusing incomplete snapshot: {error}") from error
            print(
                f"  prints: installed verified {manifest['manifest_id']} → "
                f"{(OUT_DIR / MANIFEST_NAME).relative_to(REPO_ROOT)}"
            )
        else:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            for name, payload in extras.items():
                (OUT_DIR / name).write_bytes(payload)
            out = OUT_DIR / f"{db}.jsonl"
            out.write_bytes(_api_jsonl(rows))
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
