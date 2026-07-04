#!/usr/bin/env python3
"""2-D corpus map from the record embeddings → docs/data/corpus_map.json.

Projects the record vectors (scripts/embed_records.py) to 2-D so the browser can
render a "map of the corpus" scatter, colored by trait axis, one point per
record, clickable through to the record.

PRIMARY projection is **PaCMAP** (Pairwise Controlled Manifold Approximation
Projection — preserves both local and global structure better than UMAP/t-SNE
for high-dim embeddings). **UMAP and PCA are secondary options** (`--method umap`
/ `--method pca`).

Output: docs/data/corpus_map.json
  {"method": "pacmap"|"umap"|"pca", "axes": [...], "n_total": N, "n_shown": M,
   "explained": [ev0, ev1],                 # PCA only: variance ratio of PC1/PC2
   "points": [[x, y, axisIdx, "record_id"], …]}   # coords rounded, in [0,1]

  just embed-map                         # PaCMAP (primary)
  python3 scripts/embed_map.py --method umap --sample 20000   # secondary
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EMB = REPO_ROOT / "data" / "embeddings"
SHARDS = REPO_ROOT / "docs" / "data"
OUT = SHARDS / "corpus_map.json"


def pca_2d(x):
    """Top-2 principal components via eigdecomposition of the covariance
    (768x768 — trivial). Returns (coords[N,2], explained_variance_ratio[2])."""
    import numpy as np
    xc = x - x.mean(0)
    cov = (xc.T @ xc) / (len(xc) - 1)
    evals, evecs = np.linalg.eigh(cov)            # ascending
    order = evals.argsort()[::-1]
    pcs = evecs[:, order[:2]]
    coords = xc @ pcs
    ratio = (evals[order[:2]] / evals.sum()).tolist()
    return coords, ratio


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=["pacmap", "umap", "pca"], default="pacmap",
                    help="pacmap (primary) or umap/pca (secondary)")
    ap.add_argument("--sample", type=int, default=0,
                    help="stratified sample size; 0 = all (PCA) / method default")
    ap.add_argument("--neighbors", type=int, default=15, help="UMAP n_neighbors")
    ap.add_argument("--min-dist", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    import numpy as np

    ids = json.loads((EMB / "ids.json").read_text())
    vecs = np.load(EMB / "vectors.f16.npy").astype(np.float32)
    axis_of = {}
    for f in glob.glob(str(SHARDS / "records.*.json")):
        for r in json.load(open(f)):
            axis_of[r["id"]] = r.get("axis") or "OTHER"

    idx = np.arange(len(ids))
    # PCA runs over everything; PaCMAP/UMAP sample for speed unless --sample 0.
    default_sample = 0 if args.method == "pca" else 60000
    sample = args.sample if args.sample else default_sample
    if sample and sample < len(ids):
        by_axis = defaultdict(list)
        for i in idx:
            by_axis[axis_of.get(ids[i], "OTHER")].append(i)
        rng = np.random.default_rng(args.seed)
        take = []
        for members in by_axis.values():
            k = max(1, round(len(members) / len(ids) * sample))
            m = np.array(members)
            take.extend(rng.choice(m, size=min(k, len(m)), replace=False).tolist())
        idx = np.array(sorted(take))
    sub = vecs[idx]
    print(f"{args.method.upper()} on {len(idx):,} of {len(ids):,} vectors (dim {sub.shape[1]})")

    explained = None
    if args.method == "pca":
        xy, explained = pca_2d(sub)
    elif args.method == "umap":
        import umap
        xy = umap.UMAP(n_neighbors=args.neighbors, min_dist=args.min_dist,
                       metric="cosine", random_state=args.seed,
                       verbose=True).fit_transform(sub)
    else:  # pacmap (primary)
        import pacmap
        reducer = pacmap.PaCMAP(n_components=2, n_neighbors=args.neighbors,
                                random_state=args.seed, verbose=True)
        xy = reducer.fit_transform(sub, init="pca")

    lo, hi = xy.min(0), xy.max(0)
    xy = (xy - lo) / np.maximum(hi - lo, 1e-9)

    axes = sorted({axis_of.get(ids[i], "OTHER") for i in idx})
    ax_idx = {a: k for k, a in enumerate(axes)}
    points = [[round(float(xy[j, 0]), 4), round(float(xy[j, 1]), 4),
               ax_idx[axis_of.get(ids[i], "OTHER")], ids[i]]
              for j, i in enumerate(idx)]

    out = {"method": args.method, "axes": axes, "n_total": len(ids),
           "n_shown": len(points), "points": points}
    if explained:
        out["explained"] = [round(e, 4) for e in explained]
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"wrote {len(points):,} points → {OUT.relative_to(REPO_ROOT)} "
          f"({OUT.stat().st_size/1e6:.1f} MB)"
          + (f"; PC1/PC2 variance {explained}" if explained else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
