#!/usr/bin/env python3
"""Phase-2 Tier-2 region-overlap verification (research/entry-merge-methods-round1.md).

Phase 2 (build_member_overlap.py) finds signature pairs that match nearly the
same UniProtKB proteins — but for LOCALIZED features (domains/sites/motifs) that
is not enough: two *distinct* domains that co-occur in the same proteins score a
high Jaccard without being the same trait (e.g. a nuclear receptor's DNA-binding
zinc finger PF00105 vs its ligand-binding domain IPR000536, J≈0.94). Tier 2
resolves this by checking WHERE each signature matches on the shared proteins:
if they annotate the *same region* they are the same trait; if disjoint regions
(DBD at 558-626 vs LBD at 669-900) they merely co-occur → reject.

Method: for each member-overlap candidate, take the shared Swiss-Prot proteins
(from the Phase-2 member cache), sample up to --sample of them, and pull each
protein's InterPro match coordinates for both signatures. Per protein compute
reciprocal residue overlap `min(|A∩B|/|A|, |A∩B|/|B|)`; a protein "agrees" when
that is ≥ --min-overlap. If the agreeing fraction ≥ --min-frac the pair is
CONFIRMED same-region → written as a real biolink:close_match browser edge in
data/equivalence/member_overlap.tsv. Otherwise REJECTED (co-occurring, distinct).

Input:  data/analysis/member_overlap_candidates.yaml (Phase 2)
        data/raw/uniprot_members/*.txt                (Phase 2 member cache)
Cache:  data/raw/interpro_matches/<acc>.json          (per-protein, reused)
Output: data/equivalence/member_overlap.tsv           (CONFIRMED close_match edges)
        data/analysis/member_overlap_candidates.yaml  (annotated with tier2 verdict)

  python3 scripts/verify_region_overlap.py                 # verify all candidates
  python3 scripts/verify_region_overlap.py --sample 40
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
CAND = REPO_ROOT / "data" / "analysis" / "member_overlap_candidates.yaml"
MEMBERS = REPO_ROOT / "data" / "raw" / "uniprot_members"
MATCHES = REPO_ROOT / "data" / "raw" / "interpro_matches"
OUT = REPO_ROOT / "data" / "equivalence" / "member_overlap.tsv"
API = "https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/{acc}/?page_size=200"


def api_accession(curie: str) -> str | None:
    """Our CURIE -> the accession InterPro's API reports for that signature."""
    pfx, _, acc = curie.partition(":")
    if pfx in ("Pfam", "InterPro", "PROSITE", "SMART", "NCBIfam"):
        return acc.upper()
    if pfx == "CATH":                 # exposed as Gene3D in InterPro
        return f"G3DSA:{acc}"
    return None


def members(curie: str) -> set:
    f = MEMBERS / (re.sub(r"[^A-Za-z0-9._-]", "_", curie) + ".txt")
    return set(f.read_text().split()) if f.exists() else set()


def fetch_matches(acc: str, pause: float) -> dict | None:
    """{signature_accession(upper): set(residue positions)} for one protein."""
    cache = MATCHES / f"{acc}.json"
    if cache.exists():
        raw = json.loads(cache.read_text())
    else:
        url = API.format(acc=acc)
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "proteintraitsmech-merge/1.0",
                                  "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    doc = json.load(resp)
                raw = {}
                for r in doc.get("results", []):
                    a = (r.get("metadata") or {}).get("accession", "").upper()
                    frags = []
                    for prot in r.get("proteins", []):
                        for loc in prot.get("entry_protein_locations", []):
                            for fr in loc.get("fragments", []):
                                frags.append([fr["start"], fr["end"]])
                    if a and frags:
                        raw[a] = frags
                MATCHES.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(raw))
                time.sleep(pause)
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    print(f"  ! match fetch failed {acc}: {exc}", file=sys.stderr)
                    return None
                time.sleep(2 * (attempt + 1))
    return {a: {p for s, e in frs for p in range(s, e + 1)} for a, frs in raw.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=30,
                    help="shared proteins to check per candidate")
    ap.add_argument("--min-overlap", type=float, default=0.80,
                    help="reciprocal residue overlap for a protein to 'agree'")
    ap.add_argument("--min-frac", type=float, default=0.50,
                    help="fraction of sampled proteins that must agree to CONFIRM")
    ap.add_argument("--pause", type=float, default=0.15)
    args = ap.parse_args()

    import yaml
    if not CAND.exists():
        print(f"no candidates at {CAND}; run build_member_overlap.py first", file=sys.stderr)
        return 2
    doc = yaml.safe_load(CAND.read_text())
    cands = doc.get("candidates") or []
    print(f"{len(cands)} candidates to verify")

    confirmed = []
    for c in cands:
        subj, obj = c["subject"], c["object"]
        aa, ab = api_accession(subj), api_accession(obj)
        if not aa or not ab:
            c["tier2"] = "skipped (unmapped accession)"
            continue
        shared = sorted(members(subj) & members(obj))[:args.sample]
        if not shared:
            c["tier2"] = "skipped (no cached shared members)"
            continue
        agree = evaluated = 0
        for acc in shared:
            m = fetch_matches(acc, args.pause)
            if not m or aa not in m or ab not in m:
                continue
            A, B = m[aa], m[ab]
            if not A or not B:
                continue
            inter = len(A & B)
            recip = min(inter / len(A), inter / len(B))
            evaluated += 1
            if recip >= args.min_overlap:
                agree += 1
        frac = agree / evaluated if evaluated else 0.0
        c["tier2_evaluated"] = evaluated
        c["tier2_agree_frac"] = round(frac, 3)
        if evaluated and frac >= args.min_frac:
            c["tier2"] = "CONFIRMED same-region"
            confirmed.append(c)
        else:
            c["tier2"] = ("REJECTED co-occurring (disjoint regions)"
                          if evaluated else "inconclusive (no dual matches)")
        print(f"  {subj} vs {obj}: {c['tier2']} "
              f"(agree {agree}/{evaluated})")

    # Persist verdicts back onto the candidates file.
    doc["counts"] = doc.get("counts", {})
    doc["counts"]["tier2_confirmed"] = len(confirmed)
    CAND.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

    # Confirmed pairs become real browser equivalence edges.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for c in confirmed:
            fh.write(f"{c['subject']}\t{c['predicate']}\t{c['object']}\t"
                     f"{c['relation_source']}-tier2\n")
    print(f"\nCONFIRMED {len(confirmed)}/{len(cands)} → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
