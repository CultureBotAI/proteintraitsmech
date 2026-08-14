#!/usr/bin/env python3
r"""Fetch the abstracts `interpro.xml.gz` omits but the InterPro API has (#445).

209 of the release's 54,190 entries carry no usable `<abstract>` element. That is a
PACKAGING gap, not a content gap: sampling 12 of them against
`https://www.ebi.ac.uk/interpro/api/entry/interpro/<acc>` returned 811-5,326 characters
each, every one curator-written (`is_llm: false`).

The cost of the gap is real. `enrich_pfam_definitions` falls back to the Pfam boilerplate
when the entry has no abstract, so 97 Pfam records carry
`"<name>. Pfam <type> family <id> (Pfam:<acc>)."` -- and 72 InterPro records carry little
more than their own name -- while InterPro has a full description. `hlh-pf00010` is 75
characters where the API has 4,982.

WHY A FETCH SCRIPT AND NOT AN INLINE CALL. Every other definition in this corpus is
derived from a release in `data/raw/`, so re-deriving it is offline and reproducible. A
script that reached out to a network service mid-enrichment would break that for these 97
and make the corpus depend on a service's current state. This writes a release-shaped
artefact next to the others; the enrichers read only that.

THE LLM FLAG IS LOAD-BEARING. InterPro serves machine-written descriptions alongside
curator-written ones, flagged `llm` and `checked`. #92 established that those must NOT be
promoted to `definition` under `definition_source: InterPro:... abstract` -- doing so
launders provenance so nobody downstream can tell a curator never saw the text. This
records the flags verbatim and refuses to decide; `enrich_pfam_definitions` promotes only
the unflagged ones.

Idempotent: re-running refetches and overwrites. Output is gitignored with the rest of
`data/raw/`.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from interpro_text import clean_abstract_element  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
XML_GZ = ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
OUT = ROOT / "data" / "raw" / "interpro" / "missing_abstracts.json"
API = "https://www.ebi.ac.uk/interpro/api/entry/interpro/{}"
MIN_ABSTRACT = 40           # the same threshold enrich_pfam_definitions uses


def entries_without_abstract(xml_gz: Path) -> list[str]:
    """InterPro accessions whose release entry has no usable abstract."""
    out = []
    with gzip.open(xml_gz, "rt", encoding="utf-8", errors="replace") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            if len(clean_abstract_element(el.find("abstract"))) < MIN_ABSTRACT:
                out.append(el.get("id", ""))
            el.clear()
    return [a for a in out if a]


def fetch(acc: str, timeout: int = 30) -> dict | None:
    """The entry's description blocks and their provenance flags, or None on 404."""
    try:
        with urllib.request.urlopen(API.format(acc), timeout=timeout) as resp:
            meta = json.load(resp)["metadata"]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    blocks = meta.get("description") or []
    return {
        "accession": acc,
        "name": (meta.get("name") or {}).get("name", ""),
        "type": meta.get("type", ""),
        # Verbatim, both flags, per block. Collapsing them to one boolean here would be
        # deciding the #92 question inside a fetch script.
        "description": [{"text": b.get("text", ""),
                         "llm": bool(b.get("llm")),
                         "checked": bool(b.get("checked"))} for b in blocks],
        "is_llm": bool(meta.get("is_llm")),
        "is_reviewed_llm": bool(meta.get("is_reviewed_llm")),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0,
                    help="fetch only N (the canary; run 1 first and read the output)")
    ap.add_argument("--sleep", type=float, default=0.35,
                    help="pause between calls; be a good citizen of a public API")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    if not XML_GZ.exists():
        print(f"missing {XML_GZ}; run `just fetch-interpro`", file=sys.stderr)
        return 2

    accs = entries_without_abstract(XML_GZ)
    print(f"{len(accs):,} InterPro entries have no usable abstract in the release")
    if args.limit:
        accs = accs[:args.limit]
        print(f"--limit {args.limit}: fetching {len(accs)}")

    got, missing, failed = {}, [], []
    for i, acc in enumerate(accs, 1):
        try:
            rec = fetch(acc)
        except Exception as exc:                       # network, timeout, 5xx
            failed.append((acc, f"{type(exc).__name__}: {exc}"))
            continue
        if rec is None:
            missing.append(acc)
        else:
            got[acc] = rec
        if i % 25 == 0:
            print(f"  {i}/{len(accs)}…")
        time.sleep(args.sleep)

    n_curated = sum(1 for r in got.values()
                    if r["description"] and not any(b["llm"] for b in r["description"]))
    n_llm = sum(1 for r in got.values() if any(b["llm"] for b in r["description"]))
    n_empty = sum(1 for r in got.values() if not r["description"])
    print(f"\nfetched {len(got):,}   404 {len(missing):,}   failed {len(failed):,}")
    print(f"  curator-written description: {n_curated:,}")
    print(f"  LLM-generated description:   {n_llm:,}  -- NOT promotable as InterPro prose (#92)")
    print(f"  no description at all:       {n_empty:,}")
    for acc, why in failed[:10]:
        print(f"  FAILED {acc}: {why}")

    if args.limit:
        # A partial fetch must not overwrite a complete one: the enrichers read this file
        # as "the abstracts the release is missing", and a canary run would silently
        # redefine that to "one of them".
        print(f"\n--limit set; NOT writing {args.out}. Re-run without it to write.")
        return 1 if failed else 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(got, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
