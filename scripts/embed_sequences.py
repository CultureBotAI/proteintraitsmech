#!/usr/bin/env python3
"""ESM-2 sequence embeddings for the canonical example proteins (issue #508).

The corpus map embeds record *text* and the protein map positions proteins by
the *traits* they carry. Neither reads the amino-acid sequence. This does: one
1,280-d vector per canonical-example protein, from a protein language model, so
`build_sequence_map.py` can lay proteins out by how similar they are *as
molecules* and `measure_sequence_map.py` can ask whether that recovers CATH
structure better than the annotation map does.

Model: facebook/esm2_t33_650M_UR50D at a pinned revision (MIT, ungated). The
vector is the final hidden layer, **residue mean excluding CLS, EOS and
padding** — Meta's own extraction code averages `token_representations[1:len-1]`
and warns against pooling the BOS token, which got no supervision.

Long sequences: ESM-2 takes at most 1,022 residues. 1,026 of the 12,705 example
proteins are longer (the longest is 34,350 aa). They are **never truncated**:
the sequence is cut into 1,022-residue windows with 256-residue overlap (stride
766), every residue's representation is averaged over the windows that saw it,
and the protein vector is the equal-weight mean over original positions. A
window boundary still hides contacts that span it, and a mean dilutes a small
domain inside a huge multidomain protein; both are stated limitations, and both
are smaller errors for a *similarity* map than truncating to the N-terminus.

Compute: FP32, on MPS when available (Apple Silicon), else CUDA, else CPU.
`PYTORCH_ENABLE_MPS_FALLBACK` should stay unset so an unsupported op fails
visibly instead of silently running on CPU. Vectors are cached by sequence
SHA-256 (`cache_*` in the output dir), so a re-run only embeds new sequences
and 116 accessions that share a sequence are embedded once.

Output (data/embeddings/esm2/, gitignored — rebuildable):
  ids.json           accession per row (UniProtKB:…)
  vectors.f16.npy    L2-normalised rows, same order as ids.json
  proteins.jsonl     per-row metadata the map builder needs (label, taxon,
                     length, families, exemplified records/axes)
  meta.json          {model, revision, dim, count, pooling, window, …}

  just embed-sequences --limit 5 --verify-cpu 5       # canary
  just embed-sequences                                # the full run (~1 h)
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "embeddings" / "esm2"

MODEL = "facebook/esm2_t33_650M_UR50D"
REVISION = "08e4846e537177426273712802403f7ba8261b6c"
MAX_RESIDUES = 1022     # ESM-2 positional limit, excluding CLS/EOS
OVERLAP = 256

# Acceptance rule for any device/dtype other than CPU FP32, from #508: the same
# sequence must come back with cosine >= 0.999, and no pairwise cosine between
# checked sequences may move by 0.01 or more.
SAME_SEQ_MIN_COS = 0.999
PAIRWISE_MAX_DELTA = 0.01


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------- input


def sequence_files() -> list[str]:
    """Record files that carry a canonical-example sequence.

    A grep prefilter first: parsing every record in the corpus with PyYAML takes
    over ten minutes, while only ~2% of records carry a sequence.
    """
    res = subprocess.run(["grep", "-rlE", r"^\s+sequence:", str(TRAITS)],
                         capture_output=True, text=True, check=False)
    return sorted(res.stdout.split())


def load_proteins(files: list[str]) -> list[dict]:
    """One row per accession, with the sequence and the metadata the map needs.

    Every accession in the corpus carries exactly one sequence (checked when
    this was written; a conflict is reported rather than silently resolved).
    """
    import yaml
    try:
        from yaml import CSafeLoader as Loader
    except ImportError:  # pragma: no cover - libyaml missing
        from yaml import SafeLoader as Loader

    rows: dict[str, dict] = {}
    conflicts = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            rec = yaml.load(fh, Loader=Loader)
        for ex in rec.get("canonical_examples") or []:
            seq = ex.get("sequence")
            if not seq:
                continue
            seq = seq.strip().upper()
            acc = ex["protein_id"]
            row = rows.get(acc)
            if row is None:
                row = rows[acc] = {
                    "accession": acc,
                    "label": ex.get("protein_label"),
                    "taxon_id": ex.get("taxon_id"),
                    "taxon_label": ex.get("taxon_label"),
                    "sequence": seq,
                    "families": set(),
                    "records": 0,
                    "axes": collections.Counter(),
                }
            elif row["sequence"] != seq:
                conflicts += 1
                continue
            row["label"] = row["label"] or ex.get("protein_label")
            row["taxon_id"] = row["taxon_id"] or ex.get("taxon_id")
            row["taxon_label"] = row["taxon_label"] or ex.get("taxon_label")
            row["families"].update(ex.get("family_classifications") or [])
            row["records"] += 1
            row["axes"][rec.get("trait_axis") or "?"] += 1
    if conflicts:
        print(f"warning: {conflicts} example(s) carry a sequence that disagrees with "
              f"another example of the same accession; first seen wins", file=sys.stderr)
    return sorted(rows.values(), key=lambda r: r["accession"])


# ----------------------------------------------------------------------- windowing


def windows(length: int, window: int = MAX_RESIDUES, overlap: int = OVERLAP) -> list[tuple[int, int]]:
    """[start, end) residue windows covering a sequence, with fixed overlap.

    A sequence within the limit is one window. Otherwise windows start every
    (window - overlap) residues until one reaches the end; the last window may
    be shorter than `window` but still overlaps its predecessor by `overlap`.
    A 34,350-residue sequence becomes 45 windows.
    """
    if length <= window:
        return [(0, length)]
    stride = window - overlap
    out = []
    start = 0
    while True:
        end = min(start + window, length)
        out.append((start, end))
        if end >= length:
            return out
        start += stride


# ----------------------------------------------------------------------- embedding


def pick_device(name: str):
    import torch

    if name != "auto":
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_model(model_name: str, revision: str, device, dtype_name: str):
    import torch
    from transformers import AutoTokenizer, EsmModel

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[dtype_name]
    tok = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = EsmModel.from_pretrained(model_name, revision=revision, dtype=dtype,
                                     add_pooling_layer=False)
    model.eval().to(device)
    return tok, model


class Embedder:
    """Batches windows across sequences by a token budget and pools per sequence."""

    def __init__(self, tok, model, device, max_tokens: int, max_batch: int):
        self.tok, self.model, self.device = tok, model, device
        self.max_tokens, self.max_batch = max_tokens, max_batch
        self.residues = 0
        self.windows = 0
        self.batches = 0

    def run(self, seqs: list[str], on_done) -> None:
        """Embed `seqs`; call on_done(i, vector) as each finishes, in any order."""
        import numpy as np
        import torch

        # longest first, so the first batch is the memory peak and fails early
        order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
        plan = [(i, s, e) for i in order for (s, e) in windows(len(seqs[i]))]
        remaining = {i: len(windows(len(seqs[i]))) for i in order}
        acc_sum: dict[int, np.ndarray] = {}
        acc_cnt: dict[int, np.ndarray] = {}

        pos = 0
        while pos < len(plan):
            batch = []
            width = 0
            while pos < len(plan) and len(batch) < self.max_batch:
                i, s, e = plan[pos]
                w = max(width, e - s + 2)
                if batch and w * (len(batch) + 1) > self.max_tokens:
                    break
                width = w
                batch.append(plan[pos])
                pos += 1
            texts = [seqs[i][s:e] for i, s, e in batch]
            enc = self.tok(texts, padding=True, return_tensors="pt")
            enc = {k: v.to(self.device) for k, v in enc.items()}
            with torch.inference_mode():
                hid = self.model(**enc).last_hidden_state
            hid = hid.float().cpu().numpy()
            self.batches += 1
            for row, (i, s, e) in enumerate(batch):
                n = e - s
                rep = hid[row, 1:n + 1]          # drop CLS at 0 and EOS/padding after
                if i not in acc_sum:
                    acc_sum[i] = np.zeros((len(seqs[i]), rep.shape[1]), dtype=np.float32)
                    acc_cnt[i] = np.zeros(len(seqs[i]), dtype=np.float32)
                acc_sum[i][s:e] += rep
                acc_cnt[i][s:e] += 1.0
                self.residues += n
                self.windows += 1
                remaining[i] -= 1
                if remaining[i] == 0:
                    per_res = acc_sum.pop(i) / acc_cnt.pop(i)[:, None]
                    on_done(i, per_res.mean(axis=0))


# --------------------------------------------------------------------------- cache


def sha(seq: str) -> str:
    return hashlib.sha256(seq.encode("ascii")).hexdigest()


def load_cache(out: Path):
    import numpy as np

    h, v = out / "cache_hashes.json", out / "cache_vectors.f32.npy"
    if h.exists() and v.exists():
        hashes = json.loads(h.read_text(encoding="utf-8"))
        vecs = np.load(v)
        if len(hashes) == vecs.shape[0]:
            return {k: vecs[i] for i, k in enumerate(hashes)}
        print(f"warning: cache in {rel(out)} is inconsistent; ignoring it", file=sys.stderr)
    return {}


def save_cache(out: Path, cache: dict) -> None:
    import numpy as np

    if not cache:
        return
    hashes = list(cache)
    vecs = np.stack([cache[k] for k in hashes]).astype(np.float32)
    # np.save appends ".npy" to any other suffix, so the temp name must end in it
    tmp_v = out / "cache_vectors.f32.tmp.npy"
    np.save(tmp_v, vecs)
    tmp_h = out / "cache_hashes.json.tmp"
    tmp_h.write_text(json.dumps(hashes), encoding="utf-8")
    # vectors first, hashes second: a crash between the two leaves the pair
    # inconsistent, which load_cache treats as no cache rather than a wrong one
    os.replace(tmp_v, out / "cache_vectors.f32.npy")
    os.replace(tmp_h, out / "cache_hashes.json")


# ---------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--revision", default=REVISION)
    ap.add_argument("--device", default="auto", help="auto | mps | cuda | cpu")
    ap.add_argument("--dtype", default="float32", choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--max-tokens", type=int, default=16384,
                    help="token budget per batch (rows × padded width)")
    ap.add_argument("--max-batch", type=int, default=64, help="max windows per batch")
    ap.add_argument("--limit", type=int, default=0, help="embed only the first N proteins")
    ap.add_argument("--accession", action="append", default=[],
                    help="restrict to these accessions (repeatable); for canaries")
    ap.add_argument("--verify-cpu", type=int, default=0, metavar="N",
                    help="re-embed N of the proteins on CPU FP32 and enforce the "
                         "agreement rule (cosine ≥ 0.999 same-sequence, pairwise "
                         "shift < 0.01)")
    ap.add_argument("--checkpoint-every", type=int, default=500,
                    help="write the cache every N newly embedded proteins")
    ap.add_argument("--out-dir", default=str(OUT))
    args = ap.parse_args()

    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK"):
        print("warning: PYTORCH_ENABLE_MPS_FALLBACK is set — an unsupported op would "
              "silently run on CPU; unset it so failures are visible.", file=sys.stderr)

    try:
        import numpy as np
        import torch
    except ImportError:
        print("needs torch + transformers + numpy — run with system python3.",
              file=sys.stderr)
        return 2

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    files = sequence_files()
    rows = load_proteins(files)
    if args.accession:
        want = set(args.accession)
        rows = [r for r in rows if r["accession"] in want]
        missing = want - {r["accession"] for r in rows}
        if missing:
            print(f"error: not in corpus: {sorted(missing)}", file=sys.stderr)
            return 2
    if args.limit:
        rows = rows[:args.limit]
    if not rows:
        print("no canonical-example sequences found", file=sys.stderr)
        return 1
    n_long = sum(len(r["sequence"]) > MAX_RESIDUES for r in rows)
    n_win = sum(len(windows(len(r["sequence"]))) for r in rows)
    uniq = {sha(r["sequence"]): r["sequence"] for r in rows}
    print(f"{len(rows):,} proteins from {len(files):,} record files in "
          f"{time.time() - t0:.0f}s; {len(uniq):,} unique sequences, {n_long:,} over "
          f"{MAX_RESIDUES} aa → {n_win:,} windows", file=sys.stderr)

    cache = load_cache(out)
    todo = [h for h in uniq if h not in cache]
    print(f"cache: {len(uniq) - len(todo):,} hit, {len(todo):,} to embed", file=sys.stderr)

    device = pick_device(args.device)
    tok = model = None
    if todo or args.verify_cpu:
        print(f"loading {args.model}@{args.revision[:8]} ({args.dtype}) on {device}",
              file=sys.stderr)
        tok, model = load_model(args.model, args.revision, device, args.dtype)

    if todo:
        emb = Embedder(tok, model, device, args.max_tokens, args.max_batch)
        seqs = [uniq[h] for h in todo]
        done = 0
        t1 = time.time()
        last_save = 0

        def on_done(i, vec):
            nonlocal done, last_save
            cache[todo[i]] = vec.astype(np.float32)
            done += 1
            if done - last_save >= args.checkpoint_every:
                save_cache(out, cache)
                last_save = done
                el = time.time() - t1
                print(f"  {done:,}/{len(todo):,} embedded · {emb.residues / el:,.0f} "
                      f"residues/s · {el / 60:.1f} min", file=sys.stderr)

        emb.run(seqs, on_done)
        save_cache(out, cache)
        el = time.time() - t1
        mem = ""
        if device.type == "mps":
            mem = f" · peak MPS {torch.mps.driver_allocated_memory() / 2**30:.1f} GB"
        print(f"embedded {done:,} sequences ({emb.windows:,} windows, "
              f"{emb.residues:,} residues, {emb.batches:,} batches) in {el / 60:.1f} min "
              f"· {emb.residues / max(el, 1e-9):,.0f} residues/s{mem}", file=sys.stderr)

    # assemble rows in accession order; duplicates of one sequence share a vector
    dim = next(iter(cache.values())).shape[0]
    raw = np.stack([cache[sha(r["sequence"])] for r in rows]).astype(np.float32)
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vecs = (raw / norms).astype(np.float16)

    if args.verify_cpu:
        n = min(args.verify_cpu, len(rows))
        # spread the check over the length range, including the longest
        idx = sorted(range(len(rows)), key=lambda i: len(rows[i]["sequence"]))
        pick = sorted({idx[int(k * (len(idx) - 1) / max(n - 1, 1))] for k in range(n)})
        if device.type == "cpu" and args.dtype == "float32":
            print("verify-cpu: already CPU FP32 — nothing to compare", file=sys.stderr)
        else:
            print(f"verify-cpu: re-embedding {len(pick)} proteins on CPU FP32 "
                  f"(lengths {[len(rows[i]['sequence']) for i in pick]})", file=sys.stderr)
            tok_c, model_c = load_model(args.model, args.revision, torch.device("cpu"), "float32")
            ref = {}
            Embedder(tok_c, model_c, torch.device("cpu"), args.max_tokens, args.max_batch).run(
                [rows[i]["sequence"] for i in pick], lambda j, v: ref.__setitem__(j, v))
            R = np.stack([ref[j] for j in range(len(pick))]).astype(np.float32)
            R /= np.linalg.norm(R, axis=1, keepdims=True)
            D = raw[pick] / np.linalg.norm(raw[pick], axis=1, keepdims=True)
            same = (R * D).sum(axis=1)
            shift = np.abs(R @ R.T - D @ D.T)
            np.fill_diagonal(shift, 0.0)
            print(f"verify-cpu: same-sequence cosine min {same.min():.5f} "
                  f"(rule ≥ {SAME_SEQ_MIN_COS}); max pairwise cosine shift "
                  f"{shift.max():.5f} (rule < {PAIRWISE_MAX_DELTA})", file=sys.stderr)
            if same.min() < SAME_SEQ_MIN_COS or shift.max() >= PAIRWISE_MAX_DELTA:
                print(f"verify-cpu: FAILED — {device}/{args.dtype} does not reproduce "
                      f"CPU FP32; do not ship these vectors", file=sys.stderr)
                return 1
            print("verify-cpu: passed", file=sys.stderr)

    ids = [r["accession"] for r in rows]
    (out / "ids.json").write_text(json.dumps(ids), encoding="utf-8")
    np.save(out / "vectors.f16.npy", vecs)
    with (out / "proteins.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({
                "accession": r["accession"], "label": r["label"],
                "taxon_id": r["taxon_id"], "taxon_label": r["taxon_label"],
                "length": len(r["sequence"]), "sequence_sha256": sha(r["sequence"]),
                "windows": len(windows(len(r["sequence"]))),
                "families": sorted(r["families"]), "records": r["records"],
                "axes": dict(r["axes"].most_common()),
            }) + "\n")
    (out / "meta.json").write_text(json.dumps({
        "model": args.model, "revision": args.revision, "dim": int(dim),
        "count": len(ids), "unique_sequences": len(uniq), "normalized": True,
        "dtype": "float16", "compute_dtype": args.dtype, "device": str(device),
        "pooling": "final-layer residue mean, excluding CLS/EOS/padding",
        "window": MAX_RESIDUES, "overlap": OVERLAP,
        "long_sequences": n_long, "windows": n_win,
        "source": "canonical_examples[].sequence over data/traits/",
    }, indent=2), encoding="utf-8")
    print(f"wrote {len(ids):,} × {dim} → {rel(out)}/ (ids.json, vectors.f16.npy, "
          f"proteins.jsonl, meta.json) in {(time.time() - t0) / 60:.1f} min", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
