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

# Grounding CURIE prefixes whose domain carries meaning worth embedding; the rest
# (PDB/TED/ECOD/CATH/InterPro/Pfam/cd… accessions) are opaque → dropped from text.
SEMANTIC_PREFIXES = ("EC:", "GO:", "RHEA:", "Rhea:", "CHEBI:", "PR:", "MOD:",
                     "HP:", "MONDO:", "RO:", "GO_", "PATO:")


def human_cat(cat: str) -> str:
    """SEQ_PTM_SITE -> 'ptm site' etc. (drop the axis prefix, spell it out)."""
    parts = (cat or "").split("_")
    if parts and parts[0] in ("SEQ", "STRUCT", "MIXED", "FUNC", "EVO"):
        parts = parts[1:]
    return " ".join(parts).lower()


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
    for r in sorted(recs, key=lambda r: r["id"]):
        rid = r["id"]
        d = detail.get(rid, {})
        definition = str(d.get("def") or r.get("def") or "")
        # layered definitions [[kind, text, source], …] → their texts, kind-prefixed
        layered = [f"{(x[0] or '').lower()}: {x[1]}".strip(": ")
                   for x in (d.get("defs") or []) if x and len(x) > 1 and x[1]]
        if mode == "definition":
            body = [definition] + layered
            doc = ". ".join(p for p in body if p) or str(r.get("label") or rid)
        else:  # full
            # keep only SEMANTIC groundings — ~85% of raw xrefs are opaque
            # structural accessions (PDB/TED/ECOD/CATH/cd…) that are noise to a
            # text model (embedding-field-audit skill).
            sem = [x for x in (d.get("xr") or []) if str(x).startswith(SEMANTIC_PREFIXES)][:8]
            syn = d.get("syn") or []
            chem = r.get("chem") or []            # ChEBI *names* (semantic) not ids
            pat = d.get("pat")
            cat = human_cat(r.get("cat", ""))
            axis = (r.get("axis") or "").replace("_", " ").lower()
            parts = [str(r.get("label") or rid)]  # numeric label parses to int in the shard
            if cat:
                parts.append(f"{cat} ({axis} trait)")
            if definition:
                parts.append(definition)
            parts.extend(layered)                 # structural / mechanistic / general layers
            if syn:
                parts.append("also known as " + ", ".join(str(s) for s in syn))
            if pat:                               # sequence_pattern (regex/motif) is class-defining
                parts.append(f"pattern: {pat}")
            if chem:
                parts.append("chemistry: " + ", ".join(str(c) for c in chem[:8]))
            if sem:
                parts.append("groundings: " + ", ".join(str(x) for x in sem))
            doc = ". ".join(parts)
        ids.append(rid)
        docs.append(doc)
    return ids, docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="BAAI/bge-large-en-v1.5")
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--device", default=None, help="mps|cpu|cuda (auto if unset)")
    ap.add_argument("--fresh", action="store_true", help="ignore any checkpoint")
    ap.add_argument("--text-mode", choices=["full", "definition"], default="full",
                    help="full = label+category+definition+layers+pattern+groundings; "
                         "definition = only the definition + layered-definition texts")
    args = ap.parse_args()
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

    model = SentenceTransformer(args.model, device=device)
    dim = model.get_sentence_embedding_dimension()
    out.mkdir(parents=True, exist_ok=True)
    vpath = out / "vectors.f16.npy"
    import time

    # Resume: docs are in a stable id-sorted order, so a partial vectors file
    # covers the first R docs — pick up at R. (`--fresh` ignores it.)
    parts, start = [], 0
    if not args.fresh and vpath.exists():
        try:
            prev = np.load(vpath)
            if prev.ndim == 2 and 0 < prev.shape[0] < len(docs) and prev.shape[1] == dim:
                parts, start = [prev], prev.shape[0]
                print(f"resuming from checkpoint: {start:,} already embedded")
        except Exception:  # noqa: BLE001
            pass

    chunk = max(args.batch * 20, 5000)
    t0 = time.time()
    for ci, s in enumerate(range(start, len(docs), chunk), 1):
        part = model.encode(docs[s:s + chunk], batch_size=args.batch,
                            normalize_embeddings=True, show_progress_bar=False,
                            convert_to_numpy=True).astype(np.float16)
        parts.append(part)
        if device == "mps":
            torch.mps.empty_cache()   # MPS stalls without freeing between chunks
        done = min(s + chunk, len(docs))
        rate = (done - start) / max(time.time() - t0, 1e-6)
        print(f"  {done:,}/{len(docs):,}  ({rate:.0f} docs/s, "
              f"eta {(len(docs)-done)/max(rate,1e-6)/60:.1f} min)", flush=True)
        np.save(vpath, np.vstack(parts))   # checkpoint every chunk (resumable)
    vecs = np.vstack(parts)

    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "vectors.f16.npy", vecs)
    (out / "ids.json").write_text(json.dumps(ids))
    (out / "meta.json").write_text(json.dumps(
        {"model": args.model, "dim": int(vecs.shape[1]), "count": len(ids),
         "normalized": True, "dtype": "float16", "text_mode": args.text_mode}, indent=2))
    print(f"wrote {vecs.shape} → {(out / 'vectors.f16.npy').relative_to(REPO_ROOT)} "
          f"({vecs.nbytes/1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
