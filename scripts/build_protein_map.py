#!/usr/bin/env python3
"""2-D map of the protein × trait matrix → docs/data/protein_map.json (issue #7, phase 8).

The corpus map (`embed_map.py`) plots one point per trait *class*. This plots one
point per *protein*, positioned by which corpus traits it carries — the other
half of the matrix built in phases 1-6, and open since phase 4.

It exists to make one question visible: **do proteins group by organism, or by
what they do?** Phases 6-7 kept finding that parts of the overlay were tracking
proteome membership and curation practice rather than biology. If the map
separates cleanly into four organism blobs, the trait profiles are dominated by
organism-specific annotation. If organisms interleave and the structure follows
fold and function instead, the profiles carry biology that survives the species
boundary.

Pipeline: L2-normalised TF-IDF over the protein × *signature* trait matrix
(traits with ≥ --min-support carriers; GO/EC excluded, see SIG_PREFIXES)
→ TruncatedSVD to --svd dims (the matrix is large and very sparse) → PaCMAP to
2-D, matching the corpus map's primary projection.

Two guards keep thin annotation from inventing structure. Proteins whose traits
are all rarer than --min-support are dropped rather than embedded — an all-zero
row carries no position, so projecting it fabricates a blob at the origin. And
the matrix is normalised rather than binary, so a vector's *length* no longer
tracks how well studied the protein is; without that, the thinly annotated tail
sits near the origin and packs together regardless of what those proteins are.
The vocabulary is built over the whole corpus before any --sample.

Points are coloured by organism and filterable by CATH structural class, so the
"organism vs. structure" reading can be checked both ways in the browser. They
also carry an *annotation depth* facet — how many features actually place the
protein — because the thinly annotated tail crowds together no matter how the
matrix is weighted, and a reader needs to be able to tell that region apart from
a real family rather than guess.

Output schema matches embed_map.py so docs/map.html renders it unchanged, plus
optional `group_label` / `colors` / `link` fields the page uses to label and
colour a non-axis grouping.

  just protein-map                       # PaCMAP over the whole matrix
  python3 scripts/build_protein_map.py --sample 20000
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JSONL = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
INDEX = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"
OUT = REPO_ROOT / "docs" / "data" / "protein_map.json"

# Points are coloured by DOMAIN OF LIFE, not by organism, and that is a
# constraint rather than a preference. A dense scatter has no labels on its
# marks, so every pair of hues must be separable — the all-pairs test. Run
# through the dataviz skill's validator, no 10-hue set passes it, no 5-hue set
# passes it in dark mode, and only 3-hue sets clear it in both modes. Colouring
# by organism also left six of the ten proteomes sharing one fallback grey once
# the matrix grew from four organisms to ten (issue #5).
#
# Domain is the grouping the analysis actually turns on anyway: phase 9 measured
# transfer decaying with phylogenetic distance. Organism stays available on the
# point tooltip and in the CSV, and remains the unit of the underlying data.
#
# Validated all-pairs, both modes: worst CVD ΔE 13.2 (deutan).
DOMAIN_COLORS_LIGHT = {"Eukaryota": "#2a78d6", "Bacteria": "#c98500",
                       "Archaea": "#d55181"}
DOMAIN_COLORS_DARK = {"Eukaryota": "#3987e5", "Bacteria": "#c98500",
                      "Archaea": "#d55181"}
DOMAIN_OF = {
    "Homo sapiens": "Eukaryota", "Mus musculus": "Eukaryota",
    "Drosophila melanogaster": "Eukaryota", "Caenorhabditis elegans": "Eukaryota",
    "Arabidopsis thaliana": "Eukaryota", "Saccharomyces cerevisiae": "Eukaryota",
    "Plasmodium falciparum": "Eukaryota",
    "Escherichia coli": "Bacteria", "Bacillus subtilis": "Bacteria",
    "Methanocaldococcus jannaschii": "Archaea",
}

# CATH top-level class → readable label, used as the filterable facet.
CATH_CLASS = {
    "1": "Mainly alpha",
    "2": "Mainly beta",
    "3": "Alpha-beta",
    "4": "Few secondary structures",
    "6": "Special",
}
NO_FOLD = "No CATH fold assigned"

# Ordered — the page renders them in this order rather than alphabetically, so
# the facet reads as a scale. The first bin is the one worth naming: a protein
# with a single placeable trait carries one bit of position, which is why those
# proteins pile up rather than spreading (#74).
DEPTH_BINS = ("1 trait (sparsely annotated)", "2–3 traits",
              "4–7 traits", "8+ traits")

# Traits that describe what a protein *is*. GO/EC describe what it does, and
# their density tracks curation effort rather than biology — mouse averages 16.1
# GO terms to human's 12.6, the same confound that forced within-proteome
# normalisation in the exemplar ranking. Including them made the map 44% GO
# features by vocabulary and measurably worse at its actual job:
#
#   feature space              organism purity   CATH-class purity
#   signatures + GO/EC             2.27x               2.34x
#   signatures only                1.86x               3.12x
#
# Excluding GO cuts the organism signal by 18% and improves structural
# organisation by 33%. cluster_trait_families.py already excluded them for the
# same reason; this brings the map into line.
SIG_PREFIXES = ("Pfam", "InterPro", "CDD", "PROSITE", "SMART", "NCBIfam",
                "CATH", "SUPERFAMILY", "HAMAP", "PIRSF", "PANTHER", "PRINTS")


def rel(p: Path) -> str:
    """Repo-relative path for logging, tolerating --out anywhere on disk."""
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", choices=["pacmap", "umap", "pca"], default="pacmap",
                    help="pacmap (primary, matches the corpus map) or umap/pca")
    ap.add_argument("--weighting", choices=("tfidf", "binary"), default="tfidf",
                    help="tfidf: L2-normalised TF-IDF, so a protein's position "
                         "does not depend on how well studied it is (default); "
                         "binary: raw incidence, the pre-#74 matrix")
    ap.add_argument("--min-support", type=int, default=5,
                    help="a trait needs this many carriers to become a feature")
    ap.add_argument("--svd", type=int, default=50,
                    help="dimensions to reduce to before the 2-D projection")
    ap.add_argument("--sample", type=int, default=-1,
                    help="-1 = all proteins; N = a seeded sample of N, stratified "
                         "by organism so the smaller proteomes keep their share")
    ap.add_argument("--neighbors", type=int, default=15)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    try:
        import numpy as np
        from scipy.sparse import csr_matrix
        from sklearn.decomposition import TruncatedSVD
    except ImportError:
        print("needs numpy + scipy + scikit-learn — run with the interpreter that "
              "has them (system python3 here).", file=sys.stderr)
        return 2

    if not JSONL.exists():
        print(f"no protein matrix at {JSONL} — build it with "
              f"`just build-profiles --organisms --limit 25000 --jsonl-only --apply`",
              file=sys.stderr)
        return 2

    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    rows = [json.loads(ln) for ln in JSONL.open(encoding="utf-8")]
    for r in rows:
        # signature traits only — see SIG_PREFIXES for why GO/EC are excluded
        r["_ts"] = {t for t in r["traits"]
                    if t.split(":")[0] in SIG_PREFIXES and t in idx}
    rows = [r for r in rows if r["_ts"]]

    # The vocabulary is built over the whole corpus, before sampling, for two
    # reasons: --sample must not change the feature space, and a protein is
    # placeable or not on the corpus's terms rather than the sample's.
    supp = collections.Counter()
    for r in rows:
        supp.update(r["_ts"])
    vocab = sorted(t for t, c in supp.items() if c >= args.min_support)
    pos = {t: i for i, t in enumerate(vocab)}
    if not vocab:
        print("no trait clears --min-support", file=sys.stderr)
        return 1

    # Drop proteins retaining no feature. Their row is all-zero, so SVD sends
    # them to the origin and PaCMAP renders them as one dense ball that is an
    # artefact of the vocabulary cut, not a cluster of similar proteins. They
    # are unplaceable, not central. (cluster_trait_families.py already filters
    # this way; the map was the inconsistent one.)
    placeable = [r for r in rows if any(t in pos for t in r["_ts"])]
    if len(placeable) < len(rows):
        print(f"unplaceable (no trait clears --min-support): "
              f"{len(rows) - len(placeable):,} of {len(rows):,} proteins dropped",
              file=sys.stderr)
    rows = placeable

    n_corpus = len(rows)          # before sampling — the page compares against it
    if 0 < args.sample < len(rows):
        # Stratified by organism: a uniform sample of a matrix whose proteomes
        # differ 4.5-fold (human 20,023 … E. coli 4,400) leaves the smallest
        # ones thinly represented in exactly the comparison the map is for.
        import random
        rng = random.Random(args.seed)
        by_org: dict = collections.defaultdict(list)
        for r in rows:
            by_org[(r.get("taxon_label") or "Unknown").split(" (")[0]].append(r)
        keep: list = []
        share = args.sample / len(rows)
        for org in sorted(by_org):
            group = by_org[org]
            rng.shuffle(group)
            keep.extend(group[:max(1, round(len(group) * share))])
        rng.shuffle(keep)
        rows = keep[:args.sample]

    # TF-IDF + L2 rather than raw binary incidence. Binary makes a protein's
    # vector length grow with how well studied it is, so the thinly annotated
    # end of the corpus sits near the origin and PaCMAP packs it into one blob
    # regardless of what those proteins actually are. L2 makes every protein a
    # unit vector — a one-trait protein points somewhere definite instead of
    # being short — and IDF lets a rare trait say more about identity than a
    # ubiquitous one. Measured: densest cell 5.8% → 3.7%, CATH-class purity
    # 0.833 → 0.853. --weighting binary restores the old matrix.
    idf = {}
    if args.weighting == "tfidf":
        idf = {t: math.log(n_corpus / supp[t]) for t in vocab}
    indptr, indices, values = [0], [], []
    for r in rows:
        js = sorted(pos[t] for t in r["_ts"] if t in pos)
        indices.extend(js)
        values.extend([idf[vocab[j]] for j in js] if idf else [1.0] * len(js))
        indptr.append(len(indices))
    X = csr_matrix((np.array(values, dtype=np.float32), indices, indptr),
                   shape=(len(rows), len(vocab)))
    if args.weighting == "tfidf":
        norm = np.sqrt(X.multiply(X).sum(axis=1))
        norm[norm == 0] = 1.0
        X = csr_matrix(X.multiply(1.0 / norm))
    print(f"protein × trait matrix: {X.shape[0]:,} × {X.shape[1]:,} "
          f"({X.nnz:,} nonzero, {100*X.nnz/(X.shape[0]*X.shape[1]):.3f}% dense)",
          file=sys.stderr)

    n_comp = min(args.svd, min(X.shape) - 1)
    svd = TruncatedSVD(n_components=n_comp, random_state=args.seed)
    dense = svd.fit_transform(X)
    explained = None

    if args.method == "pca":
        # the first two components of an *uncentred* truncated SVD — reporting
        # the variance ratio keeps that visible rather than implying true PCA
        coords = dense[:, :2]
        explained = [float(v) for v in svd.explained_variance_ratio_[:2]]
    elif args.method == "umap":
        import umap
        coords = umap.UMAP(n_components=2, n_neighbors=args.neighbors,
                           random_state=args.seed).fit_transform(dense)
    else:
        import pacmap
        coords = pacmap.PaCMAP(n_components=2, n_neighbors=args.neighbors,
                               random_state=args.seed).fit_transform(dense)
    coords = np.asarray(coords, dtype=float)

    # normalise into [0,1] the way embed_map.py does, so the page's px() works
    lo, hi = coords.min(axis=0), coords.max(axis=0)
    span = np.where(hi - lo == 0, 1.0, hi - lo)
    norm = (coords - lo) / span

    def organism(r):
        return (r.get("taxon_label") or "Unknown").split(" (")[0]

    def domain(r):
        return DOMAIN_OF.get(organism(r), "Eukaryota")

    def cath_class(r):
        cs = sorted(t for t in r["_ts"] if t.startswith("CATH:"))
        if not cs:
            return NO_FOLD
        return CATH_CLASS.get(cs[0].split(":")[1].split(".")[0], "Other class")

    # How many features actually position this protein. The dense region left of
    # centre is not a family — it is the proteins with almost nothing to place
    # them by, and a reader has no way to tell those apart by eye. Shipping the
    # count as a facet lets the map say so instead of leaving an unexplained
    # blob. Counted over the vocabulary, not over raw traits, because a trait
    # below --min-support contributes no coordinate.
    def depth_bin(r):
        n = sum(1 for t in r["_ts"] if t in pos)
        return (DEPTH_BINS[0] if n <= 1 else DEPTH_BINS[1] if n <= 3
                else DEPTH_BINS[2] if n <= 7 else DEPTH_BINS[3])

    groups = [d for d in ("Eukaryota", "Bacteria", "Archaea")
              if any(domain(r) == d for r in rows)]
    orgs = sorted({organism(r) for r in rows})
    o_pos = {o: i for i, o in enumerate(orgs)}
    cats = sorted({cath_class(r) for r in rows})
    g_pos = {g: i for i, g in enumerate(groups)}
    c_pos = {c: i for i, c in enumerate(cats)}
    d_pos = {d: i for i, d in enumerate(DEPTH_BINS)}

    points = [[round(float(norm[i, 0]), 4), round(float(norm[i, 1]), 4),
               g_pos[domain(r)], r["accession"], c_pos[cath_class(r)],
               o_pos[organism(r)], d_pos[depth_bin(r)]]
              for i, r in enumerate(rows)]

    payload = {
        "method": args.method,
        "axes": groups,                 # the page's grouping dimension
        "orgs": orgs,                   # per-point organism, shown on hover
        "cats": cats,
        "depths": DEPTH_BINS,           # ordered, so the page keeps them ordered
        "depth_label": "annotation depth",
        "n_total": n_corpus,
        "n_shown": len(points),
        "points": points,
        # page-level presentation hints; embed_map.py's output omits these and
        # the page falls back to its trait-axis defaults
        "group_label": "domain of life",
        "cat_label": "CATH class",
        "colors": {g: DOMAIN_COLORS_LIGHT[g] for g in groups},
        "colors_dark": {g: DOMAIN_COLORS_DARK[g] for g in groups},
        "link": "https://www.uniprot.org/uniprotkb/{id}/entry",
        "id_strip_prefix": "UniProtKB:",
        "unit": "proteins",
    }
    if explained is not None:
        payload["explained"] = explained

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    by_org = collections.Counter(f"{organism(r)} [{domain(r)}]" for r in rows)
    by_cat = collections.Counter(cath_class(r) for r in rows)
    print(f"wrote {len(points):,} points ({args.method}) → {rel(outp)}", file=sys.stderr)
    print("  organisms: " + ", ".join(f"{k} {v:,}" for k, v in by_org.most_common()),
          file=sys.stderr)
    print("  CATH class: " + ", ".join(f"{k} {v:,}" for k, v in by_cat.most_common()),
          file=sys.stderr)
    by_depth = collections.Counter(depth_bin(r) for r in rows)
    print("  annotation depth: "
          + ", ".join(f"{k} {by_depth[k]:,}" for k in DEPTH_BINS if by_depth[k]),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
