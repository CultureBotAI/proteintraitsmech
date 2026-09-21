#!/usr/bin/env python3
"""Taxon and domain of life for the embedded example proteins (issue #712).

The sequence map wanted to colour by domain of life, as the protein map does,
and could not: 2,686 of the 12,705 canonical-example proteins carry no
`taxon_id`, and the protein map's lookup only knows ten proteomes. UniProt
answers both at once — `organism_id` and the full lineage for an exact
accession, isoforms and unreviewed entries included — so this asks it, in
bounded batches, and keeps the answer in a gitignored, release-stamped sidecar.

It is a *label* source for a map, not a grounding input: nothing here is
written to a trait record or to `data/grounding`, and no example gains a
`taxon_id` from it. (Backfilling taxon ids onto records belongs to the
release-pinned grounding workflow.)

Dry-run by default: prints the request plan and touches neither the network
nor the disk. `--apply` fetches. Every response must carry the same
`x-uniprot-release`; a cache made under another release is refused rather
than mixed (`--refresh` starts over). Progress is written after every batch,
so an interrupted run resumes with what it already has.

Output (data/raw/uniprot_lineage/, gitignored):
  lineage.jsonl        one row per accession asked for:
                       {accession, taxon_id, organism, domain, entry_type,
                        uniprot_release}; `domain` is Eukaryota, Bacteria,
                       Archaea, Viruses or Unresolved
  lineage.fetch.json   endpoint, fields, release, UTC time, counts, the
                       accessions UniProt did not return, sha256 of the rows

  just fetch-uniprot-lineage                    # plan only
  just fetch-uniprot-lineage --apply --limit 25 # canary
  just fetch-uniprot-lineage --apply
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROTEINS = REPO_ROOT / "data" / "embeddings" / "esm2" / "proteins.jsonl"
OUT = REPO_ROOT / "data" / "raw" / "uniprot_lineage"

ENDPOINT = "https://rest.uniprot.org/uniprotkb/accessions"
FIELDS = "accession,organism_id,organism_name,lineage"
USER_AGENT = "ProteinTraitsMech-UniProt-lineage/1.0"
RELEASE_HEADER = "x-uniprot-release"
DOMAINS = ("Eukaryota", "Bacteria", "Archaea")
UNRESOLVED = "Unresolved"
ACCESSION = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})(-[0-9]+)?$")


class LineageError(RuntimeError):
    pass


# ------------------------------------------------------------------- pure logic


def bare(accession: str) -> str:
    """'UniProtKB:P12345-2' → 'P12345-2'."""
    return accession.split(":", 1)[-1]


def domain_of(entry: dict) -> str:
    """Domain of life from one UniProt JSON entry's lineage.

    UniProt labels the top cellular rank `domain` (older releases said
    `superkingdom`); viruses have no such rank and are recognised by name.
    """
    lineage = entry.get("lineages") or []
    for node in lineage:
        if node.get("rank") in ("domain", "superkingdom") and \
                node.get("scientificName") in DOMAINS:
            return node["scientificName"]
    if any(node.get("scientificName") == "Viruses" for node in lineage):
        return "Viruses"
    return UNRESOLVED


def row_from_entry(asked: str, entry: dict, release: str) -> dict:
    organism = entry.get("organism") or {}
    taxon = organism.get("taxonId")
    return {
        "accession": f"UniProtKB:{asked}",
        "taxon_id": f"NCBITaxon:{taxon}" if taxon else None,
        "organism": organism.get("scientificName"),
        "domain": domain_of(entry),
        "entry_type": entry.get("entryType"),
        "uniprot_release": release,
    }


def match_results(asked: list[str], results: list[dict], release: str) -> tuple[list[dict], list[str]]:
    """Rows for the accessions UniProt returned, and the ones it did not.

    Matched by primary accession, then by secondary accession for entries that
    were merged or demerged since the example was recorded. An isoform that
    comes back only as its canonical entry inherits that entry's organism.
    """
    by_primary = {e.get("primaryAccession"): e for e in results}
    by_secondary = {s: e for e in results for s in e.get("secondaryAccessions") or []}
    rows, missing = [], []
    for acc in asked:
        entry = by_primary.get(acc) or by_secondary.get(acc) \
            or by_primary.get(acc.split("-")[0]) or by_secondary.get(acc.split("-")[0])
        if entry is None:
            missing.append(acc)
        else:
            rows.append(row_from_entry(acc, entry, release))
    return rows, missing


def batches(items: list[str], size: int) -> list[list[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def request_url(accessions: list[str]) -> str:
    return ENDPOINT + "?" + urllib.parse.urlencode({
        "accessions": ",".join(accessions), "fields": FIELDS, "format": "json",
        "size": str(len(accessions))})


def load_accessions(path: Path) -> list[str]:
    """Sorted, de-duplicated bare accessions from proteins.jsonl (or any JSONL
    with an `accession` key); anything that is not UniProt accession syntax is
    an error rather than a request."""
    accs = set()
    with path.open(encoding="utf-8") as handle:
        for n, line in enumerate(handle, 1):
            if not line.strip():
                continue
            acc = bare(json.loads(line)["accession"])
            if not ACCESSION.match(acc):
                raise LineageError(f"{path}:{n}: {acc!r} is not a UniProtKB accession")
            accs.add(acc)
    return sorted(accs)


def load_cache(out: Path) -> tuple[dict[str, dict], str | None]:
    """Rows already fetched, keyed by bare accession, and their release."""
    path = out / "lineage.jsonl"
    if not path.exists():
        return {}, None
    rows = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[bare(row["accession"])] = row
    releases = {r.get("uniprot_release") for r in rows.values()}
    if len(releases) > 1:
        raise LineageError(f"{path} mixes UniProt releases {sorted(map(str, releases))}; "
                           f"re-run with --refresh")
    return rows, (releases.pop() if releases else None)


def load_not_returned(out: Path) -> list[str]:
    """Accessions an earlier run asked for and UniProt did not return."""
    path = out / "lineage.fetch.json"
    try:
        return list(json.loads(path.read_text(encoding="utf-8")).get("not_returned") or [])
    except (OSError, ValueError):
        return []


def write_outputs(out: Path, rows: dict[str, dict], missing: list[str], release: str | None,
                  release_date: str | None) -> None:
    """Rows and receipt. The receipt always describes the whole cache — never the
    `--limit` of the run that happened to write it — so a canary after a full run
    cannot shrink it or forget which accessions UniProt did not return."""
    out.mkdir(parents=True, exist_ok=True)
    missing = sorted(set(missing) - set(rows))
    body = "".join(json.dumps(rows[a], sort_keys=True) + "\n" for a in sorted(rows))
    tmp = out / "lineage.jsonl.part"
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, out / "lineage.jsonl")
    domains: dict[str, int] = {}
    for row in rows.values():
        domains[row["domain"]] = domains.get(row["domain"], 0) + 1
    receipt = {
        "endpoint": ENDPOINT, "fields": FIELDS, "uniprot_release": release,
        "uniprot_release_date": release_date,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "accessions_asked": len(rows) + len(missing), "rows": len(rows),
        "rows_without_taxon": sum(1 for r in rows.values() if not r["taxon_id"]),
        "domains": dict(sorted(domains.items())),
        "not_returned": missing,
        "lineage_jsonl_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "license": "CC BY 4.0 (UniProt Consortium)",
    }
    tmp = out / "lineage.fetch.json.part"
    tmp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, out / "lineage.fetch.json")   # the receipt is installed last


# --------------------------------------------------------------------- network


def fetch_batch(accessions: list[str], retries: int = 4) -> tuple[list[dict], str, str | None]:
    """One batch → (entries, release, release date), following pagination."""
    url: str | None = request_url(accessions)
    entries: list[dict] = []
    release = date = None
    while url:
        for attempt in range(retries):
            try:
                req = urllib.request.Request(
                    url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    got = resp.headers.get(RELEASE_HEADER)
                    date = resp.headers.get("x-uniprot-release-date") or date
                    link = resp.headers.get("Link") or ""
                    payload = json.load(resp)
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                    http.client.HTTPException, ConnectionError) as e:
                # a dropped connection mid-body is none of the first three
                status = getattr(e, "code", None)
                if status is not None and status < 500 and status != 429:
                    raise LineageError(f"UniProt refused the request ({status}): {url}") from e
                if attempt == retries - 1:
                    raise LineageError(f"UniProt request failed after {retries} tries: {e}") from e
                time.sleep(2 ** attempt)
        if not got:
            raise LineageError(f"response carried no {RELEASE_HEADER} header: {url}")
        if release is not None and got != release:
            raise LineageError(f"release changed mid-batch: {release} → {got}")
        release = got
        entries.extend(payload.get("results") or [])
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = nxt.group(1) if nxt else None
    return entries, str(release), date


# ------------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--accessions-from", default=str(PROTEINS),
                    help="JSONL with an `accession` key per row")
    ap.add_argument("--out-dir", default=str(OUT))
    ap.add_argument("--batch", type=int, default=100, help="accessions per request (≤ 500)")
    ap.add_argument("--limit", type=int, default=0, help="only the first N accessions; canary")
    ap.add_argument("--expect-release", help="abort unless UniProt is on this release")
    ap.add_argument("--refresh", action="store_true",
                    help="ignore the cache and fetch every accession again")
    ap.add_argument("--sleep", type=float, default=0.34, help="seconds between requests")
    ap.add_argument("--apply", action="store_true", help="fetch; default is a dry-run plan")
    args = ap.parse_args()
    if not 1 <= args.batch <= 500:
        ap.error("--batch must be between 1 and 500")

    src, out = Path(args.accessions_from), Path(args.out_dir)
    if not src.exists():
        print(f"missing {src} — run `just embed-sequences` first.", file=sys.stderr)
        return 2
    try:
        wanted = load_accessions(src)
        if args.limit:
            wanted = wanted[:args.limit]
        cached, cached_release = ({}, None) if args.refresh else load_cache(out)
    except LineageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.expect_release and cached_release and cached_release != args.expect_release:
        print(f"error: cached rows are from UniProt {cached_release}, not --expect-release "
              f"{args.expect_release}; re-run with --refresh", file=sys.stderr)
        return 1
    todo = [a for a in wanted if a not in cached]
    plan = {"endpoint": ENDPOINT, "fields": FIELDS, "accessions": len(wanted),
            "cached": len(wanted) - len(todo), "cached_release": cached_release,
            "to_fetch": len(todo), "requests": len(batches(todo, args.batch)),
            "out_dir": str(out), "apply": args.apply}
    print(json.dumps(plan, indent=2))
    if not args.apply:
        print("dry run — nothing fetched, nothing written. Re-run with --apply.",
              file=sys.stderr)
        return 0

    rows = dict(cached)
    release, release_date = cached_release, None
    # what earlier runs could not get stays on the receipt unless this run gets it
    missing: list[str] = [] if args.refresh else load_not_returned(out)
    if not todo:
        print(f"nothing to fetch: all {len(wanted):,} accessions are cached (UniProt "
              f"{cached_release}); outputs left untouched", file=sys.stderr)
        return 0
    try:
        for n, batch in enumerate(batches(todo, args.batch), 1):
            entries, got, date = fetch_batch(batch)
            release_date = date or release_date
            if args.expect_release and got != args.expect_release:
                raise LineageError(f"UniProt is on {got}, not --expect-release "
                                   f"{args.expect_release}")
            if release is not None and got != release:
                raise LineageError(
                    f"rows so far are from UniProt {release} and the service is now on "
                    f"{got}; re-run with --refresh to start over on one release")
            release = got
            new_rows, not_returned = match_results(batch, entries, got)
            rows.update({bare(r["accession"]): r for r in new_rows})
            missing.extend(not_returned)
            write_outputs(out, rows, missing, release, release_date)
            print(f"  batch {n}: {len(new_rows)}/{len(batch)} returned · {len(rows):,} rows "
                  f"· UniProt {got}", file=sys.stderr)
            time.sleep(args.sleep)
    except LineageError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    missing = sorted(set(missing) - set(rows))
    print(f"{len(rows):,} rows in {out / 'lineage.jsonl'} (UniProt {release}); "
          f"{len(missing)} accession(s) not returned", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
