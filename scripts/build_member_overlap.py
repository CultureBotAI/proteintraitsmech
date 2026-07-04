#!/usr/bin/env python3
"""Phase-2 member-set overlap (research/entry-merge-methods-round1.md, Tier 1).

For entries a source hasn't already integrated (i.e. NOT linked by the Phase-1
InterPro overlay), decide equivalence by comparing *which UniProtKB proteins
each signature matches* — the output of its detection recipe. Two signatures
that hit (almost) the same protein set are the same trait.

Member sets come for free from the UniProtKB members query the browser already
exposes (`xref:pfam-…`, `xref:interpro-…`, `xref:gene3d-…`, `xref:prosite-…`),
restricted to Swiss-Prot (`reviewed:true`) as the reference proteome. For each
candidate pair (same axis+category, different source, not already Phase-1
linked, sharing ≥1 member) we compute:

    Jaccard      J = |A∩B| / |A∪B|
    containment  C = |A∩B| / min(|A|,|B|)

scoring each pair (J≥--merge-j → MERGE candidate; --close-j≤J → close_match;
C≥--contain-c → narrow_match / containment).

IMPORTANT — localized-feature caveat. Most member-queryable sources here
(Pfam/InterPro/PROSITE/CATH) describe LOCALIZED features (a domain/site/motif
occupies a sub-region). Two *distinct* domains that co-occur in the same
proteins — e.g. a nuclear receptor's DNA-binding zinc finger (PF00105) and its
ligand-binding domain (IPR000536) — score a high Jaccard without being the same
trait. The research requires Tier-2 reciprocal REGION overlap before asserting
equivalence for localized categories, which this script does NOT compute. So:

  * Default output is a REVIEW file, data/analysis/member_overlap_candidates.yaml
    (every scored pair with metrics, labels, and a `verdict`). This is the
    honest primary product — a curator (or a future Tier-2 pass) promotes them.
  * Browser equivalence edges (data/equivalence/member_overlap.tsv, loaded into
    the `eq` field) are written ONLY with --emit-edges, and ONLY for
    NON-localized categories. Localized pairs are always withheld pending Tier-2.

This script NEVER edits records. Member lists are cached under
data/raw/uniprot_members/ (gitignored) so re-runs are cheap and incremental.
Full-scale is a long batched job; use --category / --limit to bound a run.
Blocking (shared-member inverted index) keeps comparison well under O(n²).

  python3 scripts/build_member_overlap.py --category STRUCT_DOMAIN --limit 300
  python3 scripts/build_member_overlap.py --emit-edges   # + non-localized edges
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARDS = REPO_ROOT / "docs" / "data"
EQ_DIR = REPO_ROOT / "data" / "equivalence"
CACHE = REPO_ROOT / "data" / "raw" / "uniprot_members"
ANALYSIS = REPO_ROOT / "data" / "analysis"
OUT = EQ_DIR / "member_overlap.tsv"
CAND = ANALYSIS / "member_overlap_candidates.yaml"

# CURIE prefix -> UniProtKB xref query fragment (mirrors browse.js MEMBER_QUERY;
# only prefixes UniProt actually indexes as a family/domain xref are members).
MEMBER_QUERY = {
    "Pfam":        lambda i: f"xref:pfam-{i}",
    "InterPro":    lambda i: f"xref:interpro-{i}",
    "CATH":        lambda i: f"xref:gene3d-{i}",
    "PROSITE":     lambda i: f"xref:prosite-{i}",
    "SMART":       lambda i: f"xref:smart-{i}",
    "HAMAP":       lambda i: f"xref:hamap-{i}",
    "PANTHER":     lambda i: f"xref:panther-{i}",
}
REST = "https://rest.uniprot.org/uniprotkb/search"


def prefix(curie: str) -> str:
    return curie.split(":", 1)[0] if ":" in curie else ""


def load_records() -> dict:
    recs = {}
    for f in glob.glob(str(SHARDS / "records.*.json")):
        for r in json.load(open(f)):
            recs[r["id"]] = r
    return recs


def load_phase1_pairs() -> set:
    """Directed (a,b) pairs already asserted by any existing overlay, so Phase 2
    only spends fetches on the *unlinked* gap."""
    pairs = set()
    for tsv in EQ_DIR.glob("*.tsv"):
        if tsv.name == OUT.name:
            continue
        for i, line in enumerate(tsv.read_text().splitlines()):
            if i == 0 or not line.strip():
                continue
            c = line.split("\t")
            if len(c) >= 3:
                pairs.add((c[0], c[2]))
                pairs.add((c[2], c[0]))
    return pairs


def fetch_members(curie: str, cap: int, reviewed: bool, pause: float) -> set | None:
    """Swiss-Prot accession set for a signature, cached. `cap` = max page size
    (single page — a screening set, not exhaustive). Returns None on failure."""
    pfx = prefix(curie)
    q = MEMBER_QUERY.get(pfx)
    if not q:
        return None
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", curie)
    cache_file = CACHE / f"{safe}.txt"
    if cache_file.exists():
        return set(cache_file.read_text().split())
    query = f"({q(curie.split(':', 1)[1])})"
    if reviewed:
        query += " AND reviewed:true"
    url = f"{REST}?{urllib.parse.urlencode({'query': query, 'format': 'list', 'size': cap})}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "proteintraitsmech-merge/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                accs = resp.read().decode().split()
            CACHE.mkdir(parents=True, exist_ok=True)
            cache_file.write_text("\n".join(accs))
            time.sleep(pause)
            return set(accs)
        except Exception as exc:  # noqa: BLE001 — network is best-effort
            if attempt == 2:
                print(f"  ! fetch failed {curie}: {exc}", file=sys.stderr)
                return None
            time.sleep(2 * (attempt + 1))
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", help="restrict to one trait_category")
    ap.add_argument("--axis", help="restrict to one trait_axis")
    ap.add_argument("--limit", type=int, default=0, help="max entries to fetch (0=all)")
    ap.add_argument("--cap", type=int, default=500, help="max members fetched per entry")
    ap.add_argument("--min-members", type=int, default=3,
                    help="skip entries with fewer than this many members")
    ap.add_argument("--merge-j", type=float, default=0.90)
    ap.add_argument("--close-j", type=float, default=0.50)
    ap.add_argument("--contain-c", type=float, default=0.90)
    ap.add_argument("--all-proteins", action="store_true",
                    help="fetch all UniProtKB, not just Swiss-Prot (larger, noisier)")
    ap.add_argument("--pause", type=float, default=0.2, help="seconds between fetches")
    ap.add_argument("--emit-edges", action="store_true",
                    help="also write non-localized pairs to the browser overlay "
                         "(localized pairs are always withheld pending Tier-2)")
    args = ap.parse_args()

    recs = load_records()
    if not recs:
        print("no records.*.json — run `just build-docs` first", file=sys.stderr)
        return 2
    linked = load_phase1_pairs()

    # Candidate entries: member-queryable source, matching axis/category filters.
    cand = [r for r in recs.values()
            if prefix(r["id"]) in MEMBER_QUERY
            and (not args.category or r.get("cat") == args.category)
            and (not args.axis or r.get("axis") == args.axis)]
    # Interleave by source so a --limit run samples across sources (cross-source
    # overlap is the whole point — one source alone yields no edges).
    cand.sort(key=lambda r: (r["id"]))
    by_src = defaultdict(list)
    for r in cand:
        by_src[r.get("src")].append(r)
    interleaved = []
    i = 0
    while any(i < len(v) for v in by_src.values()):
        for v in by_src.values():
            if i < len(v):
                interleaved.append(v[i])
        i += 1
    if args.limit:
        interleaved = interleaved[:args.limit]
    print(f"{len(interleaved):,} candidate entries "
          f"({len(by_src)} sources: {', '.join(sorted(by_src))})")

    # Fetch member sets.
    members: dict[str, set] = {}
    for n, r in enumerate(interleaved, 1):
        s = fetch_members(r["id"], args.cap, not args.all_proteins, args.pause)
        if s and len(s) >= args.min_members:
            members[r["id"]] = s
        if n % 50 == 0:
            print(f"  fetched {n}/{len(interleaved)} ({len(members)} usable)")
    print(f"{len(members):,} entries with ≥{args.min_members} members")

    # Blocking: inverted index protein -> entries; candidate pairs share ≥1.
    inv: dict[str, list] = defaultdict(list)
    for cid, s in members.items():
        for acc in s:
            inv[acc].append(cid)
    pairs: set = set()
    for cids in inv.values():
        if len(cids) < 2:
            continue
        for a, b in combinations(sorted(cids), 2):
            pairs.add((a, b))
    print(f"{len(pairs):,} candidate pairs (share ≥1 member)")

    # Categories whose entries are LOCALIZED features (a domain/site/motif/repeat
    # occupies a sub-region). For these, member-set overlap alone is NOT enough:
    # two *distinct* domains that co-occur in the same proteins (e.g. a nuclear
    # receptor's DNA-binding zinc finger and its ligand-binding domain) score a
    # high Jaccard without being the same trait. The research requires Tier-2
    # reciprocal REGION overlap before asserting equivalence for these — which is
    # not computed here — so localized pairs are emitted as review candidates
    # only, never as browser equivalence edges.
    LOCALIZED = {"STRUCT_DOMAIN", "STRUCT_HOMOLOGOUS_SUPERFAMILY", "SEQ_MOTIF",
                 "SEQ_REPEAT", "SEQ_CONSERVATION", "STRUCT_ACTIVE_SITE",
                 "STRUCT_BINDING_SITE", "STRUCT_METAL_SITE", "SEQ_PTM_SITE",
                 "STRUCT_TOPOLOGY", "STRUCT_FOLD"}

    scored = []         # every pair above a threshold, with metrics + verdict
    for a, b in pairs:
        ra, rb = recs[a], recs[b]
        if prefix(a) == prefix(b):
            continue                                   # same source — not cross
        if ra.get("axis") != rb.get("axis") or ra.get("cat") != rb.get("cat"):
            continue                                   # NEVER-guard
        if (a, b) in linked:
            continue                                   # already Phase-1 linked
        A, B = members[a], members[b]
        inter = len(A & B)
        if not inter:
            continue
        J = inter / len(A | B)
        C = inter / min(len(A), len(B))
        localized = ra.get("cat") in LOCALIZED
        if J >= args.merge_j:
            pred, metric = "biolink:close_match", f"j{J:.2f}"
            tier = "MERGE candidate — needs Tier-2 region check" if localized else "MERGE candidate"
        elif J >= args.close_j:
            pred, metric = "biolink:close_match", f"j{J:.2f}"
            tier = "close_match — needs Tier-2 region check" if localized else "close_match"
        elif C >= args.contain_c:
            pred, metric = "biolink:narrow_match", f"c{C:.2f}"
            tier = "narrow_match (containment) — needs Tier-2 region check" if localized else "narrow_match"
        else:
            continue
        # narrow_match points the smaller (more specific) set at the larger.
        subj, obj = (a, b)
        if pred == "biolink:narrow_match" and len(A) > len(B):
            subj, obj = b, a
        scored.append({
            "subject": subj, "object": obj, "predicate": pred,
            "subject_label": recs[subj].get("label"), "object_label": recs[obj].get("label"),
            "jaccard": round(J, 3), "containment": round(C, 3),
            "n_subject": len(members[subj]), "n_object": len(members[obj]), "shared": inter,
            "axis": ra.get("axis"), "category": ra.get("cat"),
            "localized": localized, "verdict": tier,
            "relation_source": f"uniprot-member-overlap-{metric}",
        })

    # De-dup undirected.
    seen, cands = set(), []
    for c in sorted(scored, key=lambda c: -c["jaccard"]):
        k = tuple(sorted((c["subject"], c["object"])))
        if k in seen:
            continue
        seen.add(k)
        cands.append(c)

    # Review candidates (ALWAYS): the honest primary output. A curator promotes
    # confirmed ones (or a future Tier-2 pass auto-clears the localized ones).
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    import yaml
    n_loc = sum(1 for c in cands if c["localized"])
    CAND.write_text(yaml.safe_dump(
        {"generated_by": "build_member_overlap.py (Phase 2 — member-set overlap)",
         "note": ("Member-set (Jaccard/containment) overlap candidates. Localized "
                  "categories (domains/sites/motifs/repeats) need Tier-2 reciprocal "
                  "REGION overlap before equivalence is asserted — co-occurring "
                  "distinct domains inflate Jaccard. Curator-review only; never "
                  "auto-applied. Browser edges are written only with --emit-edges."),
         "counts": {"total": len(cands), "localized_need_tier2": n_loc,
                    "non_localized": len(cands) - n_loc},
         "candidates": cands},
        sort_keys=False, allow_unicode=True))
    print(f"wrote {len(cands):,} review candidates ({n_loc} localized/need-Tier-2) "
          f"→ {CAND.relative_to(REPO_ROOT)}")

    # Browser overlay: only if explicitly asked, and only non-localized pairs
    # (localized ones are unverified without Tier-2, so never asserted).
    if args.emit_edges:
        emit = [c for c in cands if not c["localized"]]
        EQ_DIR.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8") as fh:
            fh.write("subject\tpredicate\tobject\trelation_source\n")
            for c in emit:
                fh.write(f"{c['subject']}\t{c['predicate']}\t{c['object']}\t{c['relation_source']}\n")
        print(f"wrote {len(emit):,} non-localized edges → {OUT.relative_to(REPO_ROOT)} "
              f"(--emit-edges; {n_loc} localized withheld pending Tier-2)")
    else:
        print("no browser edges written (all candidates localized / unverified; "
              "pass --emit-edges to write non-localized close_match edges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
