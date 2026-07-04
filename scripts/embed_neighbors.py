#!/usr/bin/env python3
"""Nearest-neighbor "related traits" + Tier-5 semantic merge candidates.

Consumes the record embeddings (scripts/embed_records.py) and computes, for
every record, its top-k most similar records by cosine similarity (vectors are
L2-normalized, so cosine = dot product). Two products:

1. Browser "Related traits (semantic)". Neighbors are written sharded the SAME
   way build_docs shards detail sidecars — md5(id) % 256 → docs/data/neighbors/
   NNN.json, keyed by id → [[neighbor_id, score], …]. These files are COMMITTED
   (the docs deploy has no embedding stack to recompute them); browse.js lazily
   loads the shard for the record on view, mirroring detail-sidecar loading.

2. Tier-5 semantic merge candidates (research/entry-merge-methods-round1.md).
   A record's high-similarity neighbor in a DIFFERENT source but the SAME
   (axis, category) is a label/definition-semantics merge candidate — Tier 5 is
   review-only (never auto-merged), so these go to
   data/analysis/semantic_merge_candidates.yaml for a curator.

The all-vs-all cosine runs on MPS/CUDA/CPU in query chunks. ~277k² is ~16 PFLOP
— a few minutes on an M1 Max in float16.

  just embed-neighbors                      # k=6 neighbors + Tier-5 @ 0.92
  python3 scripts/embed_neighbors.py --k 8 --tier5-sim 0.90
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EMB = REPO_ROOT / "data" / "embeddings"
SHARDS = REPO_ROOT / "docs" / "data"
NEIGH_DIR = SHARDS / "neighbors"
CAND = REPO_ROOT / "data" / "analysis" / "semantic_merge_candidates.yaml"
BUCKETS = 256


def bucket(rec_id: str) -> int:
    return int(hashlib.md5(rec_id.encode("utf-8")).hexdigest(), 16) % BUCKETS


def load_meta() -> dict:
    recs = {}
    for f in glob.glob(str(SHARDS / "records.*.json")):
        for r in json.load(open(f)):
            recs[r["id"]] = (r.get("axis"), r.get("cat"), r.get("src"),
                             r.get("label") or r["id"])
    return recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=6, help="neighbors stored per record")
    ap.add_argument("--tier5-sim", type=float, default=0.92,
                    help="min cosine for a cross-source Tier-5 merge candidate")
    ap.add_argument("--min-sim", type=float, default=0.60,
                    help="drop browser neighbors below this cosine")
    ap.add_argument("--chunk", type=int, default=4096)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    import numpy as np
    import torch

    ids = json.loads((EMB / "ids.json").read_text())
    vecs = np.load(EMB / "vectors.f16.npy")
    if args.limit:
        ids, vecs = ids[:args.limit], vecs[:args.limit]
    meta = load_meta()
    N = len(ids)
    print(f"{N:,} vectors, dim {vecs.shape[1]}")

    dev = ("mps" if torch.backends.mps.is_available()
           else "cuda" if torch.cuda.is_available() else "cpu")
    V = torch.from_numpy(vecs).to(dev).to(torch.float16)      # [N, d], normalized

    idx_of = {rid: i for i, rid in enumerate(ids)}
    neighbors: dict[str, list] = {}
    tier5: list = []
    seen_pair: set = set()
    kq = args.k + 1  # +1 to drop self

    for start in range(0, N, args.chunk):
        q = V[start:start + args.chunk]
        sims = q @ V.T                                        # [c, N] cosine
        vals, inds = torch.topk(sims, min(kq + 8, N), dim=1)  # a few extra for filtering
        vals = vals.float().cpu().numpy()
        inds = inds.cpu().numpy()
        for r in range(q.shape[0]):
            i = start + r
            rid = ids[i]
            ax_i, cat_i, src_i, _ = meta.get(rid, (None, None, None, rid))
            kept = []
            for j, s in zip(inds[r], vals[r]):
                if j == i:
                    continue
                nid = ids[j]
                if len(kept) < args.k and s >= args.min_sim:
                    kept.append([nid, round(float(s), 3)])
                # Tier-5: cross-source, same axis+category, high similarity
                if s >= args.tier5_sim:
                    ax_j, cat_j, src_j, _ = meta.get(nid, (None, None, None, nid))
                    if src_j != src_i and ax_j == ax_i and cat_j == cat_i:
                        key = tuple(sorted((rid, nid)))
                        if key not in seen_pair:
                            seen_pair.add(key)
                            tier5.append({
                                "a": rid, "b": nid, "similarity": round(float(s), 3),
                                "a_label": meta.get(rid, (None,)*4)[3],
                                "b_label": meta.get(nid, (None,)*4)[3],
                                "axis": ax_i, "category": cat_i,
                                "a_source": src_i, "b_source": src_j,
                            })
            if kept:
                neighbors[rid] = kept
        if (start // args.chunk) % 10 == 0:
            print(f"  {min(start + args.chunk, N):,}/{N:,}")

    # Browser neighbor shards (committed — the deploy can't recompute them).
    NEIGH_DIR.mkdir(parents=True, exist_ok=True)
    buckets: dict[int, dict] = defaultdict(dict)
    for rid, ns in neighbors.items():
        buckets[bucket(rid)][rid] = ns
    for b in range(BUCKETS):
        (NEIGH_DIR / f"{b:03d}.json").write_text(
            json.dumps(buckets.get(b, {}), separators=(",", ":")))
    total_bytes = sum((NEIGH_DIR / f"{b:03d}.json").stat().st_size for b in range(BUCKETS))
    print(f"wrote neighbors for {len(neighbors):,} records → {NEIGH_DIR.relative_to(REPO_ROOT)}/ "
          f"({total_bytes/1e6:.0f} MB in {BUCKETS} shards)")

    # Tier-5 review candidates.
    import yaml
    CAND.parent.mkdir(parents=True, exist_ok=True)
    tier5.sort(key=lambda c: -c["similarity"])
    CAND.write_text(yaml.safe_dump(
        {"generated_by": "embed_neighbors.py (Tier-5 label/definition semantics)",
         "note": ("Cross-source, same axis+category, embedding cosine ≥ threshold. "
                  "Tier 5 is REVIEW-ONLY — semantic similarity never auto-merges "
                  "(homonyms/near-labels abound). A curator promotes real ones."),
         "threshold": args.tier5_sim, "count": len(tier5), "candidates": tier5[:5000]},
        sort_keys=False, allow_unicode=True))
    print(f"wrote {len(tier5):,} Tier-5 candidates → {CAND.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
