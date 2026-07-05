#!/usr/bin/env python3
"""Populate the `evidence` slot with per-entry literature citations from data we
ALREADY fetch but under-parse (record-sample-review-1 / evidence backfill #1).
Extends the PROSITE-citation approach (enrich_prosite_citations.py) to:

  InterPro  <publications> PUBMED dbkeys in interpro.xml.gz  → InterPro records
  NCBIfam   `pmids` column in hmm_PGAP.tsv                    → NCBIfam records
  CARD/ARO  PMID: dbxrefs in each aro.obo `def:` bracket      → ARO records
  COG       PubMed column (col 6) in cog-20.def.tab           → COG records

PMIDs are resolved to DOIs via NCBI eutils (shared cache data/raw/pmid2doi.json;
reused across sources). Each record gets an EvidenceItem list — `reference: DOI:…`
(PMID in notes) or `reference: PMID:…` when no DOI. In place; idempotent; dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
RAW = REPO_ROOT / "data" / "raw"
CACHE = RAW / "pmid2doi.json"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="
ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
PMID_RE = re.compile(r"\b\d{6,8}\b")


def resolve_dois(pmids: set[str]) -> dict[str, str]:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = sorted(p for p in pmids if p not in cache)
    for i in range(0, len(todo), 200):
        batch = todo[i:i + 200]
        try:
            with urllib.request.urlopen(ESUMMARY + ",".join(batch), timeout=30) as r:
                res = json.load(r)["result"]
            for uid in res.get("uids", []):
                cache[uid] = next((x["value"] for x in res[uid].get("articleids", [])
                                   if x["idtype"] == "doi"), "")
        except Exception as exc:  # noqa: BLE001
            print(f"  ! eutils batch failed: {exc}", file=sys.stderr)
            for p in batch:
                cache.setdefault(p, "")
        time.sleep(0.34)
        print(f"  resolved {min(i+200, len(todo)):,}/{len(todo):,}", end="\r")
    if todo:
        CACHE.write_text(json.dumps(cache))
        print()
    return cache


# ---------------------------------------------------------- per-source PMID maps
def map_interpro() -> dict[str, list[str]]:
    out = {}
    with gzip.open(RAW / "interpro" / "interpro.xml.gz", "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id", "")
            pubs = el.find("pub_list")
            if ipr and pubs is not None:
                pmids = [x.get("dbkey") for x in pubs.iter("db_xref")
                         if x.get("db") == "PUBMED" and x.get("dbkey")]
                if pmids:
                    out[f"InterPro:{ipr}"] = list(dict.fromkeys(pmids))
            el.clear()
    return out


def map_ncbifam() -> dict[str, list[str]]:
    out = {}
    lines = (RAW / "ncbifam" / "hmm_PGAP.tsv").read_text(encoding="utf-8", errors="replace").splitlines()
    h = {c: i for i, c in enumerate(lines[0].lstrip("#").split("\t"))}
    pi = h.get("pmids")
    for line in lines[1:]:
        c = line.split("\t")
        if pi is None or len(c) <= pi:
            continue
        pmids = [p for p in re.split(r"[;,\s]+", c[pi].strip()) if p.isdigit()]
        if not pmids:
            continue
        for a in (c[h["ncbi_accession"]].split(".")[0], c[h["source_identifier"]].split(".")[0]):
            if a:
                out[f"NCBIfam:{a}"] = list(dict.fromkeys(pmids))
    return out


def map_aro() -> dict[str, list[str]]:
    out = {}
    aro = None
    for line in (RAW / "aro" / "aro.obo").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("id: ARO:"):
            aro = line.split(": ", 1)[1].strip()
        elif line.startswith("def:") and aro:
            pmids = re.findall(r"PMID:(\d+)", line)
            if pmids:
                out[aro] = list(dict.fromkeys(pmids))
    return out


def map_cog() -> dict[str, list[str]]:
    out = {}
    for line in (RAW / "cog" / "cog-20.def.tab").read_text(encoding="utf-8", errors="replace").splitlines():
        c = line.split("\t")
        if len(c) > 5 and c[0].startswith("COG") and c[5].strip().isdigit():
            out[f"COG:{c[0]}"] = [c[5].strip()]
    return out


SOURCES = {
    "interpro": (["sequence/domain/interpro", "sequence/homologous_superfamily/interpro",
                  "sequence/repeat/interpro", "sequence/conservation/interpro",
                  "structure/active_site/interpro", "structure/binding_site/interpro",
                  "sequence/ptm_ontology/interpro"], map_interpro),
    "ncbifam": (["sequence/domain/ncbifam", "sequence/homologous_superfamily/ncbifam",
                 "sequence/repeat/ncbifam", "function/protein_family/ncbifam"], map_ncbifam),
    "aro": (["function/resistance/aro"], map_aro),
    "cog": (["function/ortholog_group/cog"], map_cog),
}


def evidence_block(pmids: list[str], pmid2doi: dict[str, str], source: str) -> str:
    lines = ["evidence:"]
    for p in pmids:
        doi = pmid2doi.get(p, "")
        if doi:
            lines += [f"- reference: DOI:{doi}", f"  notes: PMID:{p} ({source} citation)"]
        else:
            lines += [f"- reference: PMID:{p}", f"  notes: {source} citation"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sources", default="interpro,ncbifam,aro,cog")
    ap.add_argument("--max-refs", type=int, default=10)
    args = ap.parse_args()

    want = [s.strip() for s in args.sources.split(",") if s.strip()]
    maps = {}
    for s in want:
        print(f"building {s} PMID map…")
        maps[s] = SOURCES[s][1]()
        print(f"  {len(maps[s]):,} {s} entries with a PMID")
    allpmids = {p for m in maps.values() for v in m.values() for p in v}
    print(f"resolving {len(allpmids):,} unique PMIDs to DOIs (cached)…")
    pmid2doi = resolve_dois(allpmids)

    totals = {}
    for s in want:
        pmap = maps[s]
        touched = added = 0
        for sub in SOURCES[s][0]:
            base = TRAITS / sub
            for path in base.rglob("*.yaml") if base.exists() else []:
                text = path.read_text(encoding="utf-8", errors="replace")
                if re.search(r"^evidence:", text, re.M):
                    continue
                m = ID_RE.search(text)
                if not m or m.group(1) not in pmap:
                    continue
                pmids = pmap[m.group(1)][:args.max_refs]
                block = evidence_block(pmids, pmid2doi, s)
                if re.search(r"^license:", text, re.M):
                    new = re.sub(r"^license:", block + "license:", text, count=1, flags=re.M)
                else:
                    new = text.rstrip("\n") + "\n" + block
                touched += 1
                added += len(pmids)
                if args.apply:
                    path.write_text(new, encoding="utf-8")
        totals[s] = (touched, added)

    verb = "wrote" if args.apply else "would write"
    print(f"\n{verb} evidence:")
    for s, (t, a) in totals.items():
        print(f"  {s:10s} {t:>7,} records, {a:>8,} citations")
    if not args.apply:
        print("dry-run; pass --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
