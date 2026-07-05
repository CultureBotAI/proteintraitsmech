#!/usr/bin/env python3
"""Populate the `evidence` slot on PROSITE PDOC family records with their
literature citations (record-sample-review-1 / evidence backfill).

Correcting an earlier assumption: prosite.doc reference blocks DO carry PubMed
IDs (`… PubMed=1551828`). This extracts them per PDOC, resolves each PMID to a
DOI via NCBI eutils esummary (cached to data/raw/pmid2doi.json so re-runs need no
network), and writes an EvidenceItem list onto each PROSITE:PDOC record
(sequence/family/prosite/): `reference: DOI:…` (PMID kept in notes), or
`reference: PMID:…` when no DOI exists. In place; idempotent; dry-run unless
--apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
DOC = REPO_ROOT / "data" / "raw" / "prosite.doc"
CACHE = REPO_ROOT / "data" / "raw" / "pmid2doi.json"
FAMILY_DIR = TRAITS / "sequence" / "family" / "prosite"
ID_RE = re.compile(r"^identifier:\s*(PROSITE:PDOC\d+)", re.M)
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="


def pdoc_pmids() -> dict[str, list[str]]:
    txt = DOC.read_text(encoding="utf-8", errors="replace")
    out = {}
    for b in re.split(r"^\{PDOC", txt, flags=re.M)[1:]:
        pid = "PDOC" + b[:8].split("}")[0]
        pmids = list(dict.fromkeys(re.findall(r"PubMed=(\d+)", b)))
        if pmids:
            out[pid] = pmids
    return out


def resolve_dois(pmids: set[str]) -> dict[str, str]:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = sorted(p for p in pmids if p not in cache)
    for i in range(0, len(todo), 200):
        batch = todo[i:i + 200]
        try:
            with urllib.request.urlopen(ESUMMARY + ",".join(batch), timeout=30) as r:
                res = json.load(r)["result"]
            for uid in res.get("uids", []):
                doi = next((x["value"] for x in res[uid].get("articleids", [])
                            if x["idtype"] == "doi"), "")
                cache[uid] = doi
        except Exception as exc:  # noqa: BLE001
            print(f"  ! eutils batch {i//200} failed: {exc}", file=sys.stderr)
            for p in batch:
                cache.setdefault(p, "")
        time.sleep(0.34)                      # NCBI: <=3 req/s without a key
        print(f"  resolved {min(i+200, len(todo)):,}/{len(todo):,}", end="\r")
    CACHE.write_text(json.dumps(cache))
    print()
    return cache


def evidence_block(pmids: list[str], pmid2doi: dict[str, str], indent: str) -> str:
    lines = ["evidence:"]
    for p in pmids:
        doi = pmid2doi.get(p, "")
        if doi:
            lines += [f"{indent}- reference: DOI:{doi}",
                      f"{indent}  notes: PMID:{p} (PROSITE PDOC reference)"]
        else:
            lines += [f"{indent}- reference: PMID:{p}",
                      f"{indent}  notes: PROSITE PDOC reference"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max-refs", type=int, default=12, help="cap citations per record")
    args = ap.parse_args()
    if not DOC.exists():
        print("missing data/raw/prosite.doc; run `just fetch-prosite`", file=sys.stderr)
        return 2

    pmap = pdoc_pmids()
    allpmids = {p for v in pmap.values() for p in v}
    print(f"{len(pmap):,} PDOCs with citations; {len(allpmids):,} unique PMIDs — resolving DOIs…")
    pmid2doi = resolve_dois(allpmids)
    n_doi = sum(1 for p in allpmids if pmid2doi.get(p))
    print(f"resolved {n_doi:,}/{len(allpmids):,} PMIDs to a DOI")

    touched = added = 0
    for path in FAMILY_DIR.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        m = ID_RE.search(text)
        if not m or "\nevidence:" in text or text.startswith("evidence:"):
            continue
        pmids = pmap.get(m.group(1).split(":", 1)[1], [])[:args.max_refs]
        if not pmids:
            continue
        block = evidence_block(pmids, pmid2doi, "")
        if re.search(r"^license:", text, re.M):
            new = re.sub(r"^license:", block + "license:", text, count=1, flags=re.M)
        else:
            new = text.rstrip("\n") + "\n" + block
        touched += 1
        added += len(pmids)
        if args.apply:
            path.write_text(new, encoding="utf-8")

    verb = "wrote" if args.apply else "would write"
    print(f"{verb} evidence on {touched:,} PDOC records ({added:,} citations)"
          + ("" if args.apply else "; dry-run, pass --apply"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
