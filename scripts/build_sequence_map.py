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

Layout: subtract the corpus mean from the 1,280-d mean embeddings → L2-normalise
→ PaCMAP, Euclidean, 10 neighbours, PCA init, no PCA before or inside it. #508
proposed L2 → PCA(100) → L2 → 15 neighbours as a reasoned default; the sweep in
`research/sequence-map-sweep.md` measured it against the alternatives and these
settings keep 59% more CATH-superfamily structure in 2-D at the same global
triplet accuracy. UMAP and PCA are secondary `--method` options (`--method pca`
needs `--pca N`).

What the page shows. Colour is the **domain of life**, from UniProt's lineage
for each accession (`fetch_uniprot_lineage.py`; the protein map's validated
three hues, viruses and unresolved accessions in the page's neutral grey).
`--colour axis` colours by the trait axis the protein exemplifies instead. The
filter facet is **CATH class**, taken from the protein's own
`family_classifications` and from the Swiss-Prot profiles, because "does a
sequence map recover fold?" is the question this map exists for. The second
facet is **sequence length**, so the windowed >1,022-aa tail can be isolated.
Organism sits on the tooltip and in the CSV, from the same lineage, because
2,686 of these proteins carry no taxon id of their own (#712).

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
from build_protein_map import (  # noqa: E402
    CATH_CLASS,
    DOMAIN_COLORS_DARK,
    DOMAIN_COLORS_LIGHT,
    NO_FOLD,
    rel,
)

EMB = REPO_ROOT / "data" / "embeddings" / "esm2"
PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
OUT = REPO_ROOT / "docs" / "data" / "sequence_map.json"
LINEAGE = REPO_ROOT / "data" / "raw" / "uniprot_lineage" / "lineage.jsonl"

# Domain of life, in the protein map's order and hues (validated all-pairs for
# colour-vision deficiency there). Viruses and the few accessions UniProt no
# longer returns share the page's neutral fallback grey: a fourth hue does not
# pass that validation, and neither group is what the map is read for.
DOMAIN_ORDER = ("Eukaryota", "Bacteria", "Archaea")
OTHER_DOMAIN = "Viruses / unresolved"
OTHER_COLOR = "#8a8a85"          # docs/map.html's own colorOf fallback

# Order of operations before PCA. "centre" subtracts the corpus mean and then
# L2-normalises; "l2" only normalises. The raw ESM-2 means are strongly
# anisotropic (mean pairwise cosine 0.89), and `sweep_sequence_map.py` measures
# what the choice costs.
PREPS = ("centre", "l2")

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


def load_lineage(path: Path) -> tuple[dict[str, dict], str | None]:
    """accession → lineage row (`fetch_uniprot_lineage.py`), and its release."""
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                rows[row["accession"]] = row
    releases = {r.get("uniprot_release") for r in rows.values()}
    return rows, (releases.pop() if len(releases) == 1 else None)


def domain_group(row: dict | None) -> str:
    domain = (row or {}).get("domain")
    return domain if domain in DOMAIN_ORDER else OTHER_DOMAIN


def prepare(vecs, prep: str, pca_dims: int):
    """The space PaCMAP is given: (Z, raw PCA scores or None, n_comp, variance kept,
    explained-variance ratios). `pca_dims` 0 skips PCA.

    PCA is an exact SVD of the centred matrix, in float64, with each component's
    sign fixed by its largest loading — no solver choice and no seed, so the
    same vectors always give the same space.
    """
    import numpy as np

    X = np.asarray(vecs, dtype=np.float32).copy()
    if prep == "centre":
        X -= X.mean(axis=0, keepdims=True)
    elif prep != "l2":
        raise ValueError(f"unknown prep {prep!r}")
    X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    if not pca_dims:
        return X, None, 0, 1.0, []
    n_comp = min(pca_dims, X.shape[0] - 1, X.shape[1])
    Xc = X.astype(np.float64) - X.mean(axis=0, keepdims=True, dtype=np.float64)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    flip = np.sign(Vt[np.arange(len(S)), np.abs(Vt).argmax(axis=1)])
    flip[flip == 0] = 1.0
    scores = ((U * S) * flip)[:, :n_comp].astype(np.float32)
    ratios = (S ** 2) / float((S ** 2).sum())
    Z = scores / np.maximum(np.linalg.norm(scores, axis=1, keepdims=True), 1e-12)
    return Z, scores, n_comp, float(ratios[:n_comp].sum()), [float(v) for v in ratios[:n_comp]]


def layout(Z, method: str, neighbors: int, seed: int):
    """2-D coordinates from a prepared space (PaCMAP or UMAP)."""
    if method == "umap":
        import umap
        return umap.UMAP(n_components=2, n_neighbors=neighbors,
                         random_state=seed).fit_transform(Z)
    import pacmap
    return pacmap.PaCMAP(n_components=2, n_neighbors=neighbors, apply_pca=False,
                         random_state=seed).fit_transform(Z, init="pca")


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
    # Defaults measured by `sweep_sequence_map.py` (research/sequence-map-sweep.md):
    # against #508's L2 → PCA(100) → 15 neighbours they raise 2-D CATH-superfamily
    # lift 14.4× → 22.9× over five seeds with the global triplet score unchanged.
    # Five neighbours scores higher still, and pays for it with global structure.
    ap.add_argument("--prep", choices=PREPS, default="centre",
                    help="centre: subtract the corpus mean, then L2; l2: L2 only")
    ap.add_argument("--pca", type=int, default=0,
                    help="PCA dims before the projection (0 = none, the default)")
    ap.add_argument("--neighbors", type=int, default=10)
    ap.add_argument("--colour", choices=["domain", "axis"], default="domain",
                    help="domain of life (needs the lineage sidecar) or the trait "
                         "axis the protein exemplifies")
    ap.add_argument("--lineage", default=str(LINEAGE))
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

    lineage_path = Path(args.lineage)
    if args.colour == "domain" and not lineage_path.exists():
        print(f"missing {rel(lineage_path)} — run `just fetch-uniprot-lineage --apply`, or "
              f"pass --colour axis.", file=sys.stderr)
        return 2

    try:
        import numpy as np
    except ImportError:
        print("needs numpy (+ pacmap/umap) — run with the interpreter "
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

    if args.method == "pca" and not args.pca:
        print("--method pca needs --pca > 0", file=sys.stderr)
        return 2
    Z, scores, n_comp, kept_var, ratios = prepare(X, args.prep, args.pca)
    print(f"{X.shape[0]:,} proteins × {X.shape[1]} → {args.prep} → "
          + (f"PCA({n_comp}) keeps {100 * kept_var:.1f}% of variance" if n_comp
             else "no PCA"), file=sys.stderr)

    explained = None
    if args.method == "pca":
        # the raw scores, not the row-normalised ones: the variance ratios the
        # page prints describe these two components as PCA produced them
        coords = scores[:, :2]
        explained = ratios[:2]
    else:
        coords = layout(Z, args.method, args.neighbors, args.seed)
    coords = np.asarray(coords, dtype=float)
    lo, hi = coords.min(axis=0), coords.max(axis=0)
    span = np.where(hi - lo == 0, 1.0, hi - lo)
    norm = (coords - lo) / span

    cath = cath_labels(rows, PROFILES)

    lineage, lineage_release = ({}, None)
    if args.colour == "domain":
        lineage, lineage_release = load_lineage(lineage_path)

    def organism(r):
        # UniProt's name where the lineage has one: 2,686 examples carry no taxon
        name = (lineage.get(r["accession"]) or {}).get("organism") or r.get("taxon_label")
        return (name or "Unknown").split(" (")[0]

    if args.colour == "domain":
        def group(r):
            return domain_group(lineage.get(r["accession"]))
        order = DOMAIN_ORDER + (OTHER_DOMAIN,)
    else:
        def group(r):
            return primary_axis(r["axes"])
        order = AXIS_ORDER
    axes = [g for g in order if any(group(r) == g for r in rows)]
    a_pos = {a: i for i, a in enumerate(axes)}
    orgs = sorted({organism(r) for r in rows})
    o_pos = {o: i for i, o in enumerate(orgs)}
    cats = sorted({cath_class(cath[r["accession"]]) for r in rows})
    c_pos = {c: i for i, c in enumerate(cats)}
    d_pos = {d: i for i, d in enumerate(LENGTH_BINS)}

    points = [[round(float(norm[i, 0]), 4), round(float(norm[i, 1]), 4),
               a_pos[group(r)], r["accession"],
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
        "group_label": "domain of life" if args.colour == "domain"
                       else "trait axis exemplified",
        "cat_label": "CATH class",
        "link": "https://www.uniprot.org/uniprotkb/{id}/entry",
        "id_strip_prefix": "UniProtKB:",
        "unit": "proteins",
        "sample_label": "random sample",   # --sample here is uniform, not stratified
        "embedding": {"model": meta.get("model"), "revision": meta.get("revision"),
                      "dim": meta.get("dim"), "pooling": meta.get("pooling"),
                      "window": meta.get("window"), "overlap": meta.get("overlap"),
                      "prep": args.prep, "pca": n_comp,
                      "pca_variance": round(kept_var, 4),
                      "neighbors": args.neighbors, "seed": args.seed},
    }
    if args.colour == "domain":
        # the protein map's validated hues; the remainder takes the page's grey
        payload["colors"] = {g: DOMAIN_COLORS_LIGHT.get(g, OTHER_COLOR) for g in axes}
        payload["colors_dark"] = {g: DOMAIN_COLORS_DARK.get(g, OTHER_COLOR) for g in axes}
        payload["lineage"] = {"source": "UniProtKB accessions endpoint",
                              "uniprot_release": lineage_release,
                              "resolved": sum(1 for r in rows if r["accession"] in lineage),
                              "license": "CC BY 4.0 (UniProt Consortium)"}
    if explained is not None:
        payload["explained"] = explained

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    print(f"wrote {len(points):,} points ({args.method}) → {rel(outp)} "
          f"({outp.stat().st_size / 2**20:.2f} MB)", file=sys.stderr)
    by = collections.Counter(axes[p[2]] for p in points)
    print(f"  {payload['group_label']}: " + ", ".join(f"{k} {v:,}" for k, v in by.most_common()), file=sys.stderr)
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
