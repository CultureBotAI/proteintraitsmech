#!/usr/bin/env python3
"""InterPro match sidecar for the exemplar proteins (issue #7, phase 11).

Phase 10 gave Path 1 residue coordinates for *site* records (active/binding/
metal/PTM) via `fetch_residue_frame.py`, taking offline func-site edges from 394
to 768. It could not reach domain and family records — 34,781 `SEQ_DOMAIN` alone
— because a UniProt FT `DOMAIN` interval says only "a domain is here", not
*which* signature matched. That needs InterPro.

The aligner's existing `interpro` provider queries one URL per (signature,
protein) pair. Over the exemplar set phases 5-9 produced that is 104,176 calls,
and its 18,108 cached URLs cover only the old set. This crawls **per protein**
instead — `entry/all/protein/uniprot/{acc}/?page_size=200` returns every member-DB
match with coordinates in one request — and only for proteins that could actually
produce an edge (those hosting records of two or more distinct trait categories):

    104,176 pair-calls  →  63,718 for the useful subset  →  15,120 protein-calls

Output: `data/raw/align_cache/interpro_frame.json` (gitignored, regenerable)
  {"<ACC>": {"<PREFIX>:<SIG>": [[start, end], …], …}, …}

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
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "raw" / "align_cache" / "interpro_frame.json"
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


def fetch_protein(acc: str, tries: int = 3):
    """{CURIE: [[start, end], …]} of every member-DB match on this protein."""
    url = (f"https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/{acc}/"
           f"?page_size=200")
    out: dict = {}
    while url:
        data = None
        for i in range(tries):
            try:
                req = urllib.request.Request(
                    url, headers={"Accept": "application/json",
                                  "User-Agent": "ProteinTraitsMech-interpro-frame/1.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:          # no matches: a real, cacheable answer
                    return {}
                if i == tries - 1:
                    return None
                time.sleep(2.0 * (i + 1))
            except Exception:              # noqa: BLE001
                if i == tries - 1:
                    return None
                time.sleep(2.0 * (i + 1))
        if data is None:
            return None
        for e in data.get("results") or []:
            md = e.get("metadata") or {}
            prefix = DB_PREFIX.get(md.get("source_database"))
            sig = md.get("accession")
            if not (prefix and sig):
                continue
            # InterPro reports CATH-Gene3D as "G3DSA:1.10.510.10"; the corpus
            # (and build_swissprot_profiles.py) key on the bare CATH code, so a
            # lookup would never match without stripping it.
            if sig.startswith("G3DSA:"):
                sig = sig.split(":", 1)[1]
            spans = out.setdefault(f"{prefix}:{sig}", [])
            for pr in e.get("proteins") or []:
                for loc in pr.get("entry_protein_locations") or []:
                    for fr in loc.get("fragments") or []:
                        try:
                            s, en = int(fr["start"]), int(fr["end"])
                        except (KeyError, TypeError, ValueError):
                            continue
                        spans.append([min(s, en), max(s, en)])
        url = data.get("next")
    return {k: v for k, v in out.items() if v}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the sidecar")
    ap.add_argument("--limit", type=int, default=0, help="cap proteins fetched (debug)")
    ap.add_argument("--sleep", type=float, default=0.15, help="delay between calls")
    ap.add_argument("--workers", type=int, default=6,
                    help="concurrent requests. Serial is ~1.04s per protein, so "
                         "15,120 proteins is ~5h; 6 workers brings it under an "
                         "hour while staying near 5 req/s at EBI.")
    ap.add_argument("--allow-partial", action="store_true",
                    help="write even if some proteins failed after retries")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    outp = Path(args.out)
    have: dict = {}
    if outp.exists():
        try:
            have = json.loads(outp.read_text(encoding="utf-8"))
            print(f"resuming: {len(have):,} proteins already in {outp.name}",
                  file=sys.stderr)
        except ValueError:
            pass

    targets = target_proteins()
    todo = [a for a in targets if a not in have]
    if args.limit:
        todo = todo[:args.limit]
    print(f"target proteins: {len(targets):,} | already cached: "
          f"{len(targets)-len([a for a in targets if a not in have]):,} | to fetch: {len(todo):,}")
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
                have[acc] = got
            if n % 500 == 0:
                print(f"  {n:,}/{len(todo):,} fetched ({failed} failed)",
                      file=sys.stderr)
                outp.parent.mkdir(parents=True, exist_ok=True)
                outp.write_text(json.dumps(have, separators=(",", ":")),
                                encoding="utf-8")

    n_sig = sum(len(v) for v in have.values())
    print(f"proteins in sidecar: {len(have):,} | signature matches: {n_sig:,} | "
          f"failed: {failed:,}")
    if failed and not args.allow_partial:
        print("some proteins failed after retries — the sidecar was still "
              "checkpointed and the run is resumable; re-run to fill the gaps, "
              "or pass --allow-partial to accept it as final.", file=sys.stderr)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(have, separators=(",", ":")), encoding="utf-8")
    try:
        shown = outp.relative_to(REPO_ROOT)
    except ValueError:
        shown = outp
    print(f"WROTE {shown} ({outp.stat().st_size/1e6:.1f} MB)")
    return 1 if (failed and not args.allow_partial) else 0


if __name__ == "__main__":
    sys.exit(main())
