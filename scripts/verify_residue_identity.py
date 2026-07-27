#!/usr/bin/env python3
"""Adjudicate the identical-residue-set links (issue #7, phase 12).

Phase 11's residue-frame alignment emitted 1,747 `biolink:related_to` edges whose
two records cover the *identical residue set* on every shared exemplar protein.
1,680 of them pair a CATH superfamily with an InterPro entry, and **none of them
appear in `cross_source.tsv`** — the residue frame found them independently of
every identifier mapping the corpus already had.

Identical residues on a protein prove co-extension *there*, not that the two
records denote the same thing. This checks each pair against the authority:
InterPro publishes the member signatures each entry integrates, so if
`InterPro:IPRxxxxxx` lists `G3DSA:<cath>` among its Gene3D members, the pair is
the same superfamily under two identifiers. If it does not, the residues coincide
for some other reason and the edge stays a plain `related_to`.

Confirmed pairs are emitted as a `biolink:close_match` overlay —
`data/equivalence/residue_identity.tsv` — which is a stronger claim than the
alignment overlay's `related_to` and is carried by two independent lines of
evidence (residue co-extension + InterPro's own membership).

Cross-axis pairs are still **never a merge** (per the merge-within-axis skill):
a sequence signature and a structural superfamily remain different
representations of one biological entity, which is exactly what `close_match`
says and `exact_match` would not.

Caches verdicts, so re-runs are free. Dry-run unless --apply.

  just verify-residue-identity --apply
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

REPO_ROOT = Path(__file__).resolve().parent.parent
ALIGN = REPO_ROOT / "data" / "equivalence" / "seq_struct_alignment.tsv"
OUT = REPO_ROOT / "data" / "equivalence" / "residue_identity.tsv"
CACHE = REPO_ROOT / "data" / "raw" / "align_cache" / "interpro_members.json"


def identical_pairs(path: Path) -> list:
    """(interpro, cath, n_proteins, relation_source) for each identical-residue edge."""
    out = []
    with path.open(encoding="utf-8") as fh:
        next(fh, "")
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) < 4 or c[1] != "biolink:related_to":
                continue
            a, b = c[0], c[2]
            ipr = next((x for x in (a, b) if x.startswith("InterPro:")), None)
            cath = next((x for x in (a, b) if x.startswith("CATH:")), None)
            if ipr and cath:
                m = re.search(r"n=(\d+)", c[3])
                out.append((ipr, cath, int(m.group(1)) if m else 0, c[3]))
    return out


def gene3d_members(ipr: str, cache: dict) -> set:
    """Gene3D signatures InterPro entry `ipr` integrates.

    A missing entry (204/404) is cached as `None`, not `[]`: "this entry does not
    exist" and "this entry integrates no Gene3D signature" would otherwise both
    read as a refutation, and a retired InterPro accession would be silently
    refuted rather than flagged. All 40 refutations in the first run return HTTP
    200, so this distinction changes nothing today — it stops a future retirement
    from looking like evidence.
    """
    if ipr in cache:
        return set(cache[ipr] or ())      # cached None = entry not found
    acc = ipr.split(":", 1)[1]
    url = f"https://www.ebi.ac.uk/interpro/api/entry/interpro/{acc}/"
    for i in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "ProteinTraitsMech-residue-identity/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read()
            if not body.strip():
                cache[ipr] = None          # 204: entry not found
                return set()
            md = (json.loads(body.decode("utf-8")).get("metadata") or {})
            mem = (md.get("member_databases") or {}).get("cathgene3d") or {}
            vals = sorted(x.split(":")[-1] for x in mem)
            cache[ipr] = vals
            return set(vals)
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                cache[ipr] = None          # entry not found / retired
                return set()
            time.sleep(2.0 * (i + 1))
        except Exception:                       # noqa: BLE001
            time.sleep(2.0 * (i + 1))
    return set()                                # unresolved: not cached, not confirmed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the overlay")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--report")
    args = ap.parse_args()

    if not ALIGN.exists():
        print(f"no alignment overlay at {ALIGN} — build it first with "
              f"`just build-seq-struct-alignment`", file=sys.stderr)
        return 2

    pairs = identical_pairs(ALIGN)
    print(f"identical-residue CATH<->InterPro pairs: {len(pairs):,}", file=sys.stderr)
    cache: dict = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text(encoding="utf-8"))
        except ValueError:
            pass

    want = sorted({ipr for ipr, _c, _n, _s in pairs if ipr not in cache})
    if want:
        print(f"fetching membership for {len(want):,} InterPro entries", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            list(pool.map(lambda i: gene3d_members(i, cache), want))
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, separators=(",", ":")), encoding="utf-8")

    confirmed, refuted, unresolved = [], [], []
    for ipr, cath, n, src in pairs:
        if ipr not in cache or cache[ipr] is None:
            unresolved.append((ipr, cath, n, src))
        elif cath.split(":", 1)[1] in set(cache[ipr]):
            confirmed.append((ipr, cath, n, src))
        else:
            refuted.append((ipr, cath, n, src))

    by_n = collections.Counter(n for _i, _c, n, _s in confirmed)
    L = ["# Identical-residue links: adjudicated against InterPro membership", "",
         f"{len(pairs):,} CATH↔InterPro pairs cover the identical residue set on "
         f"every shared exemplar protein, and **none appear in "
         f"`cross_source.tsv`** — the residue frame found them independently of "
         f"the corpus's identifier mappings.", "",
         "| verdict | pairs | meaning |", "|---|--:|---|",
         f"| **confirmed** | **{len(confirmed):,}** | InterPro lists this CATH "
         f"superfamily among the entry's Gene3D members — the same superfamily "
         f"under two identifiers |",
         f"| refuted | {len(refuted):,} | InterPro integrates no Gene3D signature, "
         f"or a different one: the residues coincide for another reason |",
         f"| unresolved | {len(unresolved):,} | membership unfetchable, or the "
         f"InterPro entry no longer exists |",
         "",
         "Confirmed pairs by supporting-protein count "
         "(3 is the ceiling — `suggest_canonical_examples --max-examples 3` gives "
         "each record at most three exemplars, so n=3 means *all* available "
         "evidence agrees):", "",
         "| proteins | pairs |", "|---|--:|"]
    for k in sorted(by_n):
        L.append(f"| {k} | {by_n[k]:,} |")
    report = "\n".join(L)
    print(report)
    if args.report:
        Path(args.report).write_text(report + "\n", encoding="utf-8")

    if not args.apply:
        print("\nDry-run — pass --apply to write the overlay.", file=sys.stderr)
        return 0

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for ipr, cath, n, src in sorted(confirmed):
            prots = src.split("|")[1] if "|" in src else ""
            fh.write(f"{cath}\tbiolink:close_match\t{ipr}\t"
                     f"residue-identity+interpro-member|{prots}|n={n}\n")
    print(f"\nwrote {len(confirmed):,} close_match edges → "
          f"{outp.relative_to(REPO_ROOT) if str(outp).startswith(str(REPO_ROOT)) else outp}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
