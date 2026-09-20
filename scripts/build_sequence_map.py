#!/usr/bin/env python3
"""2-D sequence-similarity map of the canonical-example proteins (issue #508).

The third protein map. The **corpus map** (`embed_map.py`) places trait
*records* by their text; the **protein map** (`build_protein_map.py`) places
Swiss-Prot proteins by the corpus *traits* they carry. This one places the
canonical-example proteins by their ESM-2 **sequence** embedding
(`embed_sequences.py`), so nearby points are proteins that are similar as
molecules — with no annotation, taxonomy or signature feature in the input.
Annotations are colours, facets and validation labels here, never coordinates
(`research/protein-map-feature-space.md` measured why).

Layout, from #508: L2-normalise the 1,280-d mean embeddings → PCA(100) (PCA,
not TruncatedSVD — these vectors are dense) → L2-normalise the scores → PaCMAP,
Euclidean, 15 neighbours, PCA init, no internal PCA. UMAP and PCA are secondary
`--method` options, as on the other maps.

What the page shows. Colour is the **trait axis** the protein exemplifies
(most of its records' axis; the page's own axis palette, so no new hues). The
filter facet is **CATH class**, taken from the protein's own
`family_classifications` and from the Swiss-Prot profiles, because "does a
sequence map recover fold?" is the question this map exists for. The second
facet is **sequence length**, so the windowed >1,022-aa tail can be isolated.
Organism sits on the tooltip and in the CSV. Domain of life was the first
choice for colour and was dropped: 2,686 of these proteins carry no taxon id
(#712 tracks adding a taxonomy source).

CATH class is the *majority* class of a protein's CATH assignments. `--sample`
draws uniformly, and the payload says so (`sample_label`).

Output schema matches `build_protein_map.py`, so `docs/map.html` renders it
unchanged: docs/data/sequence_map.json.

  just sequence-map                       # PaCMAP (primary)
  python3 scripts/build_sequence_map.py --method umap
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_protein_map import CATH_CLASS, NO_FOLD, rel  # noqa: E402

EMB = REPO_ROOT / "data" / "embeddings" / "esm2"
PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
OUT = REPO_ROOT / "docs" / "data" / "sequence_map.json"

AXIS_ORDER = ("SEQUENCE", "STRUCTURE", "SEQUENCE_STRUCTURE", "FUNCTION", "EVOLUTION")

# Ordered, rendered in this order so the facet reads as a scale. The last bin is
# the one the embedding treats differently: those proteins were windowed.
LENGTH_BINS = ("≤ 200 aa", "201–500 aa", "501–1,022 aa", "> 1,022 aa (windowed)")


def length_bin(n: int) -> str:
    return (LENGTH_BINS[0] if n <= 200 else LENGTH_BINS[1] if n <= 500
            else LENGTH_BINS[2] if n <= 1022 else LENGTH_BINS[3])


def primary_axis(axes: dict[str, int]) -> str:
    """The axis most of a protein's exemplified records sit on; ties break in
    the schema's axis order so the label is deterministic."""
    known = {a: n for a, n in axes.items() if a in AXIS_ORDER}
    if not known:          # no axis, or only the "?" placeholder for a missing one
        return "SEQUENCE"
    top = max(known.values())
    return next(a for a in AXIS_ORDER if known.get(a) == top)


def cath_labels(proteins: list[dict], profiles: Path) -> dict[str, list[str]]:
    """accession → sorted CATH CURIEs, from the example's own family
    cross-references plus the Swiss-Prot profile where one exists."""
    labels: dict[str, set[str]] = {p["accession"]: set() for p in proteins}
    for p in proteins:
        labels[p["accession"]].update(f for f in p.get("families", ())
                                      if f.startswith("CATH:"))
    if profiles.exists():
        want = set(labels)
        with profiles.open(encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                acc = d["accession"]
                if acc in want:
                    labels[acc].update(t for t in d.get("traits", ()) if t.startswith("CATH:"))
    return {k: sorted(v) for k, v in labels.items()}


def cath_class(curies: list[str]) -> str:
    """The CATH class most of a protein's CATH assignments fall in.

    Not the first assignment in sorted order: 1,919 of the 6,246 CATH-labelled
    example proteins span more than one class, and a lexical sort hands 70% of
    those to class 1 ("Mainly alpha") whatever their composition. Ties break
    toward the lower class number so the label stays deterministic.
    """
    if not curies:
        return NO_FOLD
    counts = collections.Counter(c.split(":")[1].split(".")[0] for c in curies)
    top = max(counts.values())
    digit = min(d for d, n in counts.items() if n == top)
    return CATH_CLASS.get(digit, "Other class")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", choices=["pacmap", "umap", "pca"], default="pacmap")
    ap.add_argument("--emb-dir", default=str(EMB))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--pca", type=int, default=100, help="PCA dims before the projection")
    ap.add_argument("--neighbors", type=int, default=15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--sample", type=int, default=0, help="plot a random subset")
    ap.add_argument("--allow-partial", action="store_true",
                    help="build from an embedding made with --limit/--accession")
    args = ap.parse_args()

    emb = Path(args.emb_dir)
    for name in ("ids.json", "vectors.f16.npy", "proteins.jsonl", "meta.json"):
        if not (emb / name).exists():
            print(f"missing {rel(emb / name)} — run `just embed-sequences` first.",
                  file=sys.stderr)
            return 2
    # Checked before anything heavy is imported or read: a canary run leaves a
    # few rows behind, and a map of those must never replace the corpus map.
    meta = json.loads((emb / "meta.json").read_text(encoding="utf-8"))
    if meta.get("partial") and not args.allow_partial:
        print(f"{rel(emb / 'meta.json')} is marked partial ({meta.get('filter')}) — a "
              f"canary, not the corpus. Run `just embed-sequences` without --limit/"
              f"--accession, or pass --allow-partial to plot it anyway.", file=sys.stderr)
        return 2

    try:
        import numpy as np
        from sklearn.decomposition import PCA
    except ImportError:
        print("needs numpy + scikit-learn (+ pacmap/umap) — run with the interpreter "
              "that has them (miniforge python3 here), not `uv run`.", file=sys.stderr)
        return 2

    ids = json.loads((emb / "ids.json").read_text(encoding="utf-8"))
    vecs = np.load(emb / "vectors.f16.npy").astype(np.float32)
    proteins = [json.loads(line) for line in
                (emb / "proteins.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if len(ids) != len(proteins) or len(ids) != vecs.shape[0] \
            or any(p["accession"] != a for p, a in zip(proteins, ids)):
        print("ids.json, proteins.jsonl and vectors.f16.npy disagree — rebuild the "
              "embedding.", file=sys.stderr)
        return 1
    n_total = len(ids)
    if n_total < 3:
        print(f"only {n_total} protein(s) embedded — too few to project.", file=sys.stderr)
        return 1

    rng = np.random.default_rng(args.seed)
    keep = np.arange(n_total)
    if 0 < args.sample < n_total:
        keep = np.sort(rng.choice(n_total, size=args.sample, replace=False))
    X = vecs[keep]
    rows = [proteins[i] for i in keep]

    # L2 → PCA → L2 → projection. The vectors are stored normalised already;
    # normalising again is a no-op that keeps the pipeline explicit.
    X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    n_comp = min(args.pca, X.shape[0] - 1, X.shape[1])
    pca = PCA(n_components=n_comp, random_state=args.seed)
    scores = pca.fit_transform(X).astype(np.float32)
    kept_var = float(pca.explained_variance_ratio_.sum())
    Z = scores / np.maximum(np.linalg.norm(scores, axis=1, keepdims=True), 1e-12)
    print(f"{X.shape[0]:,} proteins × {X.shape[1]} → PCA({n_comp}) keeps "
          f"{100 * kept_var:.1f}% of variance", file=sys.stderr)

    explained = None
    if args.method == "pca":
        # the raw scores, not the row-normalised ones: the variance ratios the
        # page prints describe these two components as PCA produced them
        coords = scores[:, :2]
        explained = [float(v) for v in pca.explained_variance_ratio_[:2]]
    elif args.method == "umap":
        import umap
        coords = umap.UMAP(n_components=2, n_neighbors=args.neighbors,
                           random_state=args.seed).fit_transform(Z)
    else:
        import pacmap
        coords = pacmap.PaCMAP(n_components=2, n_neighbors=args.neighbors,
                               apply_pca=False, random_state=args.seed
                               ).fit_transform(Z, init="pca")
    coords = np.asarray(coords, dtype=float)
    lo, hi = coords.min(axis=0), coords.max(axis=0)
    span = np.where(hi - lo == 0, 1.0, hi - lo)
    norm = (coords - lo) / span

    cath = cath_labels(rows, PROFILES)

    def organism(r):
        return (r.get("taxon_label") or "Unknown").split(" (")[0]

    axes = [a for a in AXIS_ORDER if any(primary_axis(r["axes"]) == a for r in rows)]
    a_pos = {a: i for i, a in enumerate(axes)}
    orgs = sorted({organism(r) for r in rows})
    o_pos = {o: i for i, o in enumerate(orgs)}
    cats = sorted({cath_class(cath[r["accession"]]) for r in rows})
    c_pos = {c: i for i, c in enumerate(cats)}
    d_pos = {d: i for i, d in enumerate(LENGTH_BINS)}

    points = [[round(float(norm[i, 0]), 4), round(float(norm[i, 1]), 4),
               a_pos[primary_axis(r["axes"])], r["accession"],
               c_pos[cath_class(cath[r["accession"]])], o_pos[organism(r)],
               d_pos[length_bin(r["length"])]]
              for i, r in enumerate(rows)]

    payload = {
        "method": args.method,
        "axes": axes,
        "orgs": orgs,
        "cats": cats,
        "depths": list(LENGTH_BINS),
        "depth_label": "sequence length",
        "n_total": n_total,
        "n_shown": len(points),
        "points": points,
        "group_label": "trait axis exemplified",
        "cat_label": "CATH class",
        "link": "https://www.uniprot.org/uniprotkb/{id}/entry",
        "id_strip_prefix": "UniProtKB:",
        "unit": "proteins",
        "sample_label": "random sample",   # --sample here is uniform, not stratified
        "embedding": {"model": meta.get("model"), "revision": meta.get("revision"),
                      "dim": meta.get("dim"), "pooling": meta.get("pooling"),
                      "window": meta.get("window"), "overlap": meta.get("overlap"),
                      "pca": n_comp, "pca_variance": round(kept_var, 4),
                      "neighbors": args.neighbors, "seed": args.seed},
    }
    if explained is not None:
        payload["explained"] = explained

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    print(f"wrote {len(points):,} points ({args.method}) → {rel(outp)} "
          f"({outp.stat().st_size / 2**20:.2f} MB)", file=sys.stderr)
    by = collections.Counter(axes[p[2]] for p in points)
    print("  axis: " + ", ".join(f"{k} {v:,}" for k, v in by.most_common()), file=sys.stderr)
    by = collections.Counter(cats[p[4]] for p in points)
    print("  CATH class: " + ", ".join(f"{k} {v:,}" for k, v in by.most_common()),
          file=sys.stderr)
    by = collections.Counter(LENGTH_BINS[p[6]] for p in points)
    print("  length: " + ", ".join(f"{k} {by[k]:,}" for k in LENGTH_BINS if by[k]),
          file=sys.stderr)
    print(f"  organisms: {len(orgs):,}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
