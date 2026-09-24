#!/usr/bin/env python3
"""InterPro match sidecar for the exemplar proteins (issue #7, phase 11).

Phase 10 gave Path 1 residue coordinates for *site* records (active/binding/
metal/PTM) via `fetch_residue_frame.py`, taking offline func-site edges from 394
to 768. It could not reach domain and family records — 34,781 `SEQ_DOMAIN` alone
— because a UniProt FT `DOMAIN` interval says only "a domain is here", not
*which* signature matched. That needs InterPro.

The aligner's existing `interpro` provider queries one URL per (signature,
protein) pair. Crawling **per protein** instead through
`entry/all/protein/uniprot/{acc}/?page_size=200` returns every member-DB match
with coordinates in one request. The target set is further bounded to proteins
that could actually produce an edge: those hosting records of two or more
distinct trait categories.

Output: `data/raw/align_cache/interpro_frame.json` (gitignored, regenerable)
  {"<ACC>": {"<PREFIX>:<SIG>": [[start, end], …], …}, …}
and `data/raw/align_cache/interpro_grouped_locations.json`
  {"<ACC>": {"<PREFIX>:<SIG>": [[[start, end], …], …]}, …}

Signature accessions are mapped back to the corpus's CURIE prefixes, so a lookup
is keyed exactly as a record's `identifier`.

Resumable: an existing sidecar is loaded and only missing proteins are fetched,
so an interrupted crawl costs nothing. Refuses to write a partial result unless
--allow-partial (the lesson of #53). Stdlib-only.

  just fetch-interpro-frame --apply
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sidecar  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "raw" / "align_cache" / "interpro_frame.json"
GROUPED_OUT = (
    REPO_ROOT / "data" / "raw" / "align_cache" / "interpro_grouped_locations.json"
)
RESIDUE_FRAME = REPO_ROOT / "data" / "raw" / "align_cache" / "residue_frame.json"

# InterPro `source_database` → the corpus CURIE prefix. Inverse of the aligner's
# MEMBERDB; "profile" is how InterPro labels PROSITE profiles (as opposed to
# patterns), and both live under the PROSITE prefix here.
DB_PREFIX = {
    "interpro": "InterPro", "pfam": "Pfam", "smart": "SMART", "cdd": "CDD",
    "prints": "PRINTS", "panther": "PANTHER", "ncbifam": "NCBIfam",
    "pirsf": "PIRSF", "hamap": "HAMAP", "sfld": "SFLD", "prosite": "PROSITE",
    "profile": "PROSITE", "cathgene3d": "CATH", "ssf": "SUPERFAMILY",
}
MEMBERDB_PREFIXES = set(DB_PREFIX.values())

# categories fetch_residue_frame.py can already localize — a member-DB record can
# pair with one of these, so they count toward "two distinct categories"
FRAME_CATS = {
    "SEQ_COMPOSITION", "SEQ_MOTIF", "STRUCT_ACTIVE_SITE", "STRUCT_BINDING_SITE",
    "STRUCT_METAL_SITE", "STRUCT_DISULFIDE", "SEQ_SIGNAL_PEPTIDE",
    "SEQ_TRANSIT_PEPTIDE", "SEQ_PROPEPTIDE", "SEQ_MODIFIED_RESIDUE",
    "SEQ_LIPIDATION_SITE", "SEQ_GLYCOSYLATION_SITE", "SEQ_CROSSLINK_SITE",
}

_IDENT = re.compile(r"(?m)^identifier:\s*(\S+)")
_CAT = re.compile(r"(?m)^trait_category:\s*(\S+)")
# `\s*` not `\s+`: fetch_uniprot_examples.py writes its blocks through
# PyYAML, which emits list items at column 0 ("- protein_id:"). Requiring
# leading whitespace silently skipped 27,325 records — every UNIPROTKB_API
# exemplar block in the corpus.
_PID = re.compile(r"(?m)^\s*-\s+protein_id:\s*(\S+)")


def target_proteins() -> list:
    """Exemplar proteins that host records of ≥2 distinct trait categories.

    A residue-frame edge needs two *comparable* records localized on one protein;
    a protein carrying only one category can never supply that pair, so fetching
    it would be pure cost. This is what turns a 38,357-protein crawl into 15,120.
    """
    prot_cats: dict = collections.defaultdict(set)
    prot_member: dict = collections.defaultdict(set)
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        i = text.find("\ncanonical_examples:")
        if i < 0:
            continue
        mi, mc = _IDENT.search(text), _CAT.search(text)
        if not (mi and mc):
            continue
        ident, cat = mi.group(1), mc.group(1)
        for pid in set(_PID.findall(text[i:])):
            acc = pid.split(":")[-1]
            # every record counts toward "which categories live on this protein".
            # A first cut gated this on residue-frame membership, which silently
            # excluded proteins whose partner record localizes via `stored`
            # (inline sequence / features) — 430 of the protein mentions in the
            # committed overlay, and so 230 of its edges, were unreachable.
            prot_cats[acc].add(cat)
            if ident.split(":")[0] in MEMBERDB_PREFIXES:
                prot_member[acc].add(cat)
    return sorted(a for a in prot_member
                  if len(prot_cats.get(a, set())) > 1)


def _curie(metadata: dict) -> str | None:
    prefix = DB_PREFIX.get(metadata.get("source_database"))
    sig = metadata.get("accession")
    if not prefix or not isinstance(sig, str) or not sig:
        return None
    # InterPro reports CATH-Gene3D as "G3DSA:1.10.510.10"; the corpus
    # (and build_swissprot_profiles.py) key on the bare CATH code, so a
    # lookup would never match without stripping it.
    if sig.startswith("G3DSA:"):
        sig = sig.split(":", 1)[1]
    return f"{prefix}:{sig}"


def extract_entry_matches(
    results: list[dict],
) -> tuple[dict[str, list[list[int]]], dict[str, list[list[list[int]]]]]:
    """Return flat and per-entry_protein_location InterPro matches.

    The compact frame preserves the legacy flattened lookup used by existing
    queues.  The grouped frame keeps every InterPro ``entry_protein_location`` as
    one independent hit, including any discontinuous fragments within that hit.
    """
    flat: dict[str, list[list[int]]] = {}
    grouped: dict[str, list[list[list[int]]]] = {}
    for entry in results:
        curie = _curie(entry.get("metadata") or {})
        if curie is None:
            continue
        for protein in entry.get("proteins") or []:
            for location in protein.get("entry_protein_locations") or []:
                fragments: list[list[int]] = []
                for fragment in location.get("fragments") or []:
                    try:
                        start, end = int(fragment["start"]), int(fragment["end"])
                    except (KeyError, TypeError, ValueError):
                        continue
                    fragments.append([min(start, end), max(start, end)])
                if not fragments:
                    continue
                flat.setdefault(curie, []).extend(fragments)
                grouped.setdefault(curie, []).append(fragments)
    return (
        {key: value for key, value in flat.items() if value},
        {key: value for key, value in grouped.items() if value},
    )


def fetch_protein(
    acc: str, tries: int = 3
) -> tuple[dict[str, list[list[int]]], dict[str, list[list[list[int]]]]] | None:
    """Return flat and grouped member-DB matches on this protein."""
    url = (f"https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/{acc}/"
           f"?page_size=200")
    flat: dict[str, list[list[int]]] = {}
    grouped: dict[str, list[list[list[int]]]] = {}
    while url:
        data = None
        for i in range(tries):
            try:
                req = urllib.request.Request(
                    url, headers={"Accept": "application/json",
                                  "User-Agent": "ProteinTraitsMech-interpro-frame/1.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    body = r.read()
                    if r.status == 204 or not body.strip():
                        # InterPro answers 204 No Content — NOT 404 — for a
                        # protein with no member-DB matches. That is a real,
                        # cacheable answer; letting json.loads() choke on the
                        # empty body instead cost three retries and ~6s and then
                        # reported a false failure (issue #56).
                        return {}, {}
                    data = json.loads(body.decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code in (204, 404):   # no matches: a real, cacheable answer
                    return {}, {}
                if i == tries - 1:
                    return None
                time.sleep(2.0 * (i + 1))
            except Exception:              # noqa: BLE001
                if i == tries - 1:
                    return None
                time.sleep(2.0 * (i + 1))
        if data is None:
            return None
        page_flat, page_grouped = extract_entry_matches(data.get("results") or [])
        for curie, intervals in page_flat.items():
            flat.setdefault(curie, []).extend(intervals)
        for curie, locations in page_grouped.items():
            grouped.setdefault(curie, []).extend(locations)
        url = data.get("next")
    return (
        {key: value for key, value in flat.items() if value},
        {key: value for key, value in grouped.items() if value},
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sidecar")
    ap.add_argument("--limit", type=int, default=0, help="cap proteins fetched (debug)")
    ap.add_argument("--sleep", type=float, default=0.15, help="delay between calls")
    ap.add_argument("--workers", type=int, default=6,
                    help="concurrent requests. One InterPro crawl costs one or "
                         "more calls per target protein; the default stays near "
                         "5 req/s at EBI.")
    ap.add_argument("--allow-stale", action="store_true",
                    help="resume from a sidecar built against a different release")
    ap.add_argument("--allow-partial", action="store_true",
                    help="write even if some proteins failed after retries")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--grouped-out", default=str(GROUPED_OUT))
    args = ap.parse_args()

    outp = Path(args.out)
    grouped_outp = Path(args.grouped_out)
    release = sidecar.interpro_release()
    have, meta = sidecar.read(outp, "proteins")
    if have:
        if not sidecar.check_release(meta, release, outp, args.allow_stale):
            return 2
        print(f"resuming: {len(have):,} proteins already in {outp.name} "
              f"(release {meta.get('release')})", file=sys.stderr)
    grouped_have, grouped_meta = sidecar.read(grouped_outp, "proteins")
    if grouped_have:
        if not sidecar.check_release(grouped_meta, release, grouped_outp, args.allow_stale):
            return 2
        print(f"resuming: {len(grouped_have):,} proteins already in "
              f"{grouped_outp.name} (release {grouped_meta.get('release')})",
              file=sys.stderr)

    targets = target_proteins()
    todo = [a for a in targets if a not in have or a not in grouped_have]
    if args.limit:
        todo = todo[:args.limit]
    already_cached = sum(1 for a in targets if a in have and a in grouped_have)
    print(f"target proteins: {len(targets):,} | already cached: "
          f"{already_cached:,} | to fetch: {len(todo):,}")
    if not args.apply:
        print("Dry-run — pass --apply to fetch and write.")
        return 0

    failed = 0

    def _one(acc):
        time.sleep(args.sleep)          # spreads the workers' request rate
        return acc, fetch_protein(acc)

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for n, (acc, got) in enumerate(pool.map(_one, todo), 1):
            if got is None:
                failed += 1
            else:
                flat, grouped = got
                have[acc] = flat
                grouped_have[acc] = grouped
            if n % 500 == 0:
                print(f"  {n:,}/{len(todo):,} fetched ({failed} failed)",
                      file=sys.stderr)
                outp.parent.mkdir(parents=True, exist_ok=True)
                outp.write_text(json.dumps(
                    sidecar.wrap("proteins", have, "InterPro", release),
                    separators=(",", ":")), encoding="utf-8")
                grouped_outp.parent.mkdir(parents=True, exist_ok=True)
                grouped_outp.write_text(json.dumps(
                    sidecar.wrap("proteins", grouped_have, "InterPro", release),
                    separators=(",", ":")), encoding="utf-8")

    n_sig = sum(len(v) for v in have.values())
    n_grouped_sig = sum(len(v) for v in grouped_have.values())
    print(f"proteins in sidecar: {len(have):,} | signature matches: {n_sig:,} | "
          f"grouped signature matches: {n_grouped_sig:,} | failed: {failed:,}")
    if failed and not args.allow_partial:
        print("some proteins failed after retries — the sidecar was still "
              "checkpointed and the run is resumable; re-run to fill the gaps, "
              "or pass --allow-partial to accept it as final.", file=sys.stderr)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(sidecar.wrap("proteins", have, "InterPro", release),
                               separators=(",", ":")), encoding="utf-8")
    grouped_outp.parent.mkdir(parents=True, exist_ok=True)
    grouped_outp.write_text(json.dumps(
        sidecar.wrap("proteins", grouped_have, "InterPro", release),
        separators=(",", ":")), encoding="utf-8")
    try:
        shown = outp.relative_to(REPO_ROOT)
    except ValueError:
        shown = outp
    print(f"WROTE {shown} ({outp.stat().st_size/1e6:.1f} MB)")
    try:
        shown_grouped = grouped_outp.relative_to(REPO_ROOT)
    except ValueError:
        shown_grouped = grouped_outp
    print(f"WROTE {shown_grouped} ({grouped_outp.stat().st_size/1e6:.1f} MB)")
    return 1 if (failed and not args.allow_partial) else 0


if __name__ == "__main__":
    sys.exit(main())
