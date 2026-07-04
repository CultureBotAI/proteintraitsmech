#!/usr/bin/env python3
"""Text-embed every ProteinTraitRecord into a dense vector (local model).

ProteinTraitsMech has no KG embeddings, so we build a purely *textual* vector
representation of each record with a local open-source embedding model — run
inside this environment on Apple-Silicon MPS, no external embeddings API (Claude
has none) and no per-record cost. The vectors power: semantic "related traits"
in the browser, Tier-5 semantic merge candidates, a UMAP corpus map, and a
portable vector-store export.

Default model: BAAI/bge-large-en-v1.5 (1024-dim, retrieval-tuned, 512-token
window — ample for a record's label+definition; symmetric, so no query
instruction is needed for record-to-record similarity). ~460 docs/s on an M1
Max → the full 277k corpus in ~10 min.

Each record is serialized to a compact document (label · human category · axis ·
definition · key groundings) read from the docs shards + detail sidecars (so we
don't re-parse 277k YAMLs — run `just build-docs` first).

Output (data/embeddings/, gitignored — large, rebuildable):
  vectors.f16.npy   float16 [N, dim], L2-normalized, row i ↔ ids[i]
  ids.json          the N record identifiers, in row order
  meta.json         {model, dim, count, normalized}

  just embed                       # whole corpus
  python3 scripts/embed_records.py --limit 5000 --model BAAI/bge-large-en-v1.5
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARDS = REPO_ROOT / "docs" / "data"
DETAIL = SHARDS / "detail"
OUT = REPO_ROOT / "data" / "embeddings"


def human_cat(cat: str) -> str:
    """SEQ_PTM_SITE -> 'ptm site' etc. (drop the axis prefix, spell it out)."""
    parts = (cat or "").split("_")
    if parts and parts[0] in ("SEQ", "STRUCT", "MIXED", "FUNC", "EVO"):
        parts = parts[1:]
    return " ".join(parts).lower()


def load_corpus() -> tuple[list[str], list[str]]:
    """Return (ids, documents) in a stable order from the shards + sidecars."""
    # id/label/cat/axis/src + detail-bucket pointer from the list shards
    recs = []
    for f in sorted(glob.glob(str(SHARDS / "records.*.json"))):
        recs.extend(json.load(open(f)))
    if not recs:
        print("no records.*.json — run `just build-docs` first", file=sys.stderr)
        sys.exit(2)
    # full definition + xrefs live in the per-bucket detail sidecars
    detail: dict = {}
    for f in glob.glob(str(DETAIL / "*.json")):
        detail.update(json.load(open(f)))

    ids, docs = [], []
    for r in sorted(recs, key=lambda r: r["id"]):
        rid = r["id"]
        d = detail.get(rid, {})
        definition = d.get("def") or r.get("def") or ""
        xr = d.get("xr") or []
        cat = human_cat(r.get("cat", ""))
        axis = (r.get("axis") or "").replace("_", " ").lower()
        parts = [r.get("label") or rid]
        if cat:
            parts.append(f"{cat} ({axis} trait)")
        if definition:
            parts.append(definition)
        if xr:
            parts.append("groundings: " + ", ".join(xr[:8]))
        ids.append(rid)
        docs.append(". ".join(parts))
    return ids, docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-large-en-v1.5")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--device", default=None, help="mps|cpu|cuda (auto if unset)")
    args = ap.parse_args()

    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer

    device = args.device or ("mps" if torch.backends.mps.is_available()
                             else "cuda" if torch.cuda.is_available() else "cpu")
    ids, docs = load_corpus()
    if args.limit:
        ids, docs = ids[:args.limit], docs[:args.limit]
    print(f"{len(ids):,} records → embedding with {args.model} on {device}")

    model = SentenceTransformer(args.model, device=device)
    # Chunked encode with PLAIN progress prints (no tqdm — it blocks when stderr
    # is a full background pipe) and periodic partial saves so a long run is
    # observable and crash-resilient.
    OUT.mkdir(parents=True, exist_ok=True)
    import time
    chunk = max(args.batch * 20, 5000)
    parts = []
    t0 = time.time()
    n_chunks = (len(docs) + chunk - 1) // chunk
    for ci, s in enumerate(range(0, len(docs), chunk), 1):
        part = model.encode(docs[s:s + chunk], batch_size=args.batch,
                            normalize_embeddings=True, show_progress_bar=False,
                            convert_to_numpy=True).astype(np.float16)
        parts.append(part)
        done = min(s + chunk, len(docs))
        rate = done / max(time.time() - t0, 1e-6)
        print(f"  {done:,}/{len(docs):,}  ({rate:.0f} docs/s, "
              f"eta {(len(docs)-done)/max(rate,1e-6)/60:.1f} min)", flush=True)
        if ci % 10 == 0 and ci != n_chunks:
            np.save(OUT / "vectors.f16.npy", np.vstack(parts))  # periodic checkpoint
    vecs = np.vstack(parts)

    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "vectors.f16.npy", vecs)
    (OUT / "ids.json").write_text(json.dumps(ids))
    (OUT / "meta.json").write_text(json.dumps(
        {"model": args.model, "dim": int(vecs.shape[1]), "count": len(ids),
         "normalized": True, "dtype": "float16"}, indent=2))
    print(f"wrote {vecs.shape} → {(OUT / 'vectors.f16.npy').relative_to(REPO_ROOT)} "
          f"({vecs.nbytes/1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
