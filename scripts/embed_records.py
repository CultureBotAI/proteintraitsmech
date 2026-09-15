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
  meta.json         model/revision, dimension, count and complete embedding identity
  checkpoint.npz    atomic resumable vectors + identity (legacy caches are not resumed)

  just embed                       # whole corpus
  python3 scripts/embed_records.py --limit 5000 --model BAAI/bge-large-en-v1.5
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

from embedding_documents import build_document, human_cat as human_cat

from embedding_checkpoint import (
    CheckpointError, corpus_identity, load_checkpoint, save_checkpoint,
)

DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"
DEFAULT_REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARDS = REPO_ROOT / "docs" / "data"
DETAIL = SHARDS / "detail"
OUT = REPO_ROOT / "data" / "embeddings"


def load_corpus(mode: str = "full") -> tuple[list[str], list[str]]:
    """Return (ids, documents) in a stable order from the shards + sidecars.

    mode="full": label · category · definition · layered-definition texts ·
      sequence_pattern · a few semantic groundings (see the embedding-field-audit
      skill for the include/exclude rationale).
    mode="definition": ONLY the definition + layered-definition texts — powers the
      definition-only corpus map."""
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
    n_fallback = 0
    for r in sorted(recs, key=lambda r: r["id"]):
        rid = r["id"]
        doc, fallback = build_document(r, detail.get(rid, {}), mode)
        n_fallback += int(fallback)
        ids.append(rid)
        docs.append(doc)
    if mode == "definition" and n_fallback:
        print(f"  note: {n_fallback:,} records had no definition → label fallback",
              file=sys.stderr)
    return ids, docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--revision", help="exact model commit; required for custom --model")
    ap.add_argument("--max-seq-length", type=int, default=512)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--device", default=None, help="mps|cpu|cuda (auto if unset)")
    ap.add_argument("--fresh", action="store_true", help="ignore any checkpoint")
    ap.add_argument("--text-mode", choices=["full", "definition"], default="full",
                    help="full = label+category+definition+layers+pattern+groundings; "
                         "definition = only the definition + layered-definition texts")
    args = ap.parse_args()
    revision = args.revision or (DEFAULT_REVISION if args.model == DEFAULT_MODEL else None)
    if not revision or not re.fullmatch(r"[0-9a-f]{40}", revision):
        ap.error("--revision must be an exact 40-character lowercase model commit")
    if args.max_seq_length <= 0 or args.batch <= 0 or args.limit < 0:
        ap.error("--max-seq-length and --batch must be positive; --limit must be nonnegative")
    out = OUT if args.text_mode == "full" else OUT / args.text_mode

    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer

    device = args.device or ("mps" if torch.backends.mps.is_available()
                             else "cuda" if torch.cuda.is_available() else "cpu")
    ids, docs = load_corpus(args.text_mode)
    if args.limit:
        ids, docs = ids[:args.limit], docs[:args.limit]
    print(f"{len(ids):,} records → embedding ({args.text_mode}) with {args.model} "
          f"on {device} → {out.relative_to(REPO_ROOT)}")

    identity = corpus_identity(
        ids, docs, name=args.model, revision=revision, text_mode=args.text_mode,
        max_seq_length=args.max_seq_length, normalized=True, dtype="float16",
    )
    model = SentenceTransformer(args.model, revision=revision, device=device)
    model.max_seq_length = args.max_seq_length
    dim = model.get_sentence_embedding_dimension()
    out.mkdir(parents=True, exist_ok=True)
    vpath = out / "vectors.f16.npy"
    import time

    # One atomic NPZ binds the prefix to ALL documents and encoder settings.
    # Legacy .npy/.corpus_fingerprint pairs cannot prove that identity (#700).
    checkpoint = out / "checkpoint.npz"
    parts, start = [], 0
    if not args.fresh:
        try:
            previous = load_checkpoint(checkpoint, identity, dim)
        except CheckpointError as exc:
            print(f"checkpoint rejected: {exc}; starting fresh", file=sys.stderr)
        else:
            if previous is not None:
                parts, start = [previous], len(previous)
                print(f"resuming verified checkpoint: {start:,} already embedded")
            elif vpath.exists():
                print("legacy vectors have no verified checkpoint identity; starting fresh",
                      file=sys.stderr)

    chunk = max(args.batch * 20, 5000)
    t0 = time.time()
    for ci, s in enumerate(range(start, len(docs), chunk), 1):
        part = model.encode(docs[s:s + chunk], batch_size=args.batch,
                            normalize_embeddings=True, show_progress_bar=False,
                            convert_to_numpy=True).astype(np.float16)
        if part.shape != (len(docs[s:s + chunk]), dim):
            raise CheckpointError("encoder returned an unexpected vector shape")
        parts.append(part)
        if device == "mps":
            torch.mps.empty_cache()   # MPS stalls without freeing between chunks
        done = min(s + chunk, len(docs))
        rate = (done - start) / max(time.time() - t0, 1e-6)
        print(f"  {done:,}/{len(docs):,}  ({rate:.0f} docs/s, "
              f"eta {(len(docs)-done)/max(rate,1e-6)/60:.1f} min)", flush=True)
        save_checkpoint(checkpoint, np.vstack(parts), identity)
    vecs = np.vstack(parts)

    out.mkdir(parents=True, exist_ok=True)
    # These legacy consumer exports are not a multi-file transaction. The complete
    # checkpoint remains available to retry export after an interruption.
    np.save(out / "vectors.f16.npy", vecs)
    (out / "ids.json").write_text(json.dumps(ids))
    (out / "meta.json").write_text(json.dumps(
        {"model": args.model, "dim": int(vecs.shape[1]), "count": len(ids),
         "normalized": True, "dtype": "float16", "text_mode": args.text_mode,
         "revision": revision, "max_seq_length": args.max_seq_length,
         "embedding_identity": identity}, indent=2))
    print(f"wrote {vecs.shape} → {(out / 'vectors.f16.npy').relative_to(REPO_ROOT)} "
          f"({vecs.nbytes/1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
