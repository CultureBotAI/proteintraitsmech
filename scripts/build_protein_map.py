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

Pipeline: binary protein × trait incidence (traits with ≥ --min-support carriers)
→ TruncatedSVD to --svd dims (the matrix is large and very sparse) → PaCMAP to
2-D, matching the corpus map's primary projection.

Points are coloured by organism and filterable by CATH structural class, so the
"organism vs. structure" reading can be checked both ways in the browser.

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
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
JSONL = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
INDEX = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"
OUT = REPO_ROOT / "docs" / "data" / "protein_map.json"

# Organism palette — distinct hues, readable in both themes. Keys are the
# taxon_label prefixes as they appear in the matrix.
ORGANISM_COLORS = {
    "Homo sapiens": "#2563eb",
    "Mus musculus": "#d97706",
    "Saccharomyces cerevisiae": "#16a34a",
    "Escherichia coli": "#a855f7",
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
    ap.add_argument("--min-support", type=int, default=5,
                    help="a trait needs this many carriers to become a feature")
    ap.add_argument("--svd", type=int, default=50,
                    help="dimensions to reduce to before the 2-D projection")
    ap.add_argument("--sample", type=int, default=-1,
                    help="-1 = all proteins; N = a random N (seeded)")
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
    rows = [json.loads(l) for l in JSONL.open(encoding="utf-8")]
    for r in rows:
        # same trait set the miners use: signatures plus GO / EC, corpus members only
        r["_ts"] = {t for t in (set(r["traits"]) | set(r["go"])
                                | {f"EC:{e}" for e in r["ec"]}) if t in idx}
    rows = [r for r in rows if r["_ts"]]

    if 0 < args.sample < len(rows):
        import random
        random.Random(args.seed).shuffle(rows)
        rows = rows[:args.sample]

    supp = collections.Counter()
    for r in rows:
        supp.update(r["_ts"])
    vocab = sorted(t for t, c in supp.items() if c >= args.min_support)
    pos = {t: i for i, t in enumerate(vocab)}
    if not vocab:
        print("no trait clears --min-support", file=sys.stderr)
        return 1

    indptr, indices = [0], []
    for r in rows:
        indices.extend(sorted(pos[t] for t in r["_ts"] if t in pos))
        indptr.append(len(indices))
    X = csr_matrix((np.ones(len(indices), dtype=np.float32), indices, indptr),
                   shape=(len(rows), len(vocab)))
    print(f"protein × trait matrix: {X.shape[0]:,} × {X.shape[1]:,} "
          f"({X.nnz:,} nonzero, {100*X.nnz/(X.shape[0]*X.shape[1]):.3f}% dense)",
          file=sys.stderr)

    n_comp = min(args.svd, min(X.shape) - 1)
    dense = TruncatedSVD(n_components=n_comp, random_state=args.seed).fit_transform(X)
    explained = None

    if args.method == "pca":
        coords = dense[:, :2]
        explained = None
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
        lab = (r.get("taxon_label") or "Unknown").split(" (")[0]
        return lab

    def cath_class(r):
        cs = sorted(t for t in r["_ts"] if t.startswith("CATH:"))
        if not cs:
            return NO_FOLD
        return CATH_CLASS.get(cs[0].split(":")[1].split(".")[0], "Other class")

    groups = sorted({organism(r) for r in rows})
    cats = sorted({cath_class(r) for r in rows})
    g_pos = {g: i for i, g in enumerate(groups)}
    c_pos = {c: i for i, c in enumerate(cats)}

    points = [[round(float(norm[i, 0]), 4), round(float(norm[i, 1]), 4),
               g_pos[organism(r)], r["accession"], c_pos[cath_class(r)]]
              for i, r in enumerate(rows)]

    payload = {
        "method": args.method,
        "axes": groups,                 # the page's grouping dimension
        "cats": cats,
        "n_total": len(rows),
        "n_shown": len(points),
        "points": points,
        # page-level presentation hints; embed_map.py's output omits these and
        # the page falls back to its trait-axis defaults
        "group_label": "organism",
        "cat_label": "CATH class",
        "colors": {g: ORGANISM_COLORS.get(g, "#888") for g in groups},
        "link": "https://www.uniprot.org/uniprotkb/{id}/entry",
        "id_strip_prefix": "UniProtKB:",
        "unit": "proteins",
    }
    if explained is not None:
        payload["explained"] = explained

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    by_org = collections.Counter(organism(r) for r in rows)
    by_cat = collections.Counter(cath_class(r) for r in rows)
    print(f"wrote {len(points):,} points ({args.method}) → {rel(outp)}", file=sys.stderr)
    print("  organisms: " + ", ".join(f"{k} {v:,}" for k, v in by_org.most_common()),
          file=sys.stderr)
    print("  CATH class: " + ", ".join(f"{k} {v:,}" for k, v in by_cat.most_common()),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
