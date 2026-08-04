#!/usr/bin/env python3
"""Multi-trait families: DiviK-style clustering of the protein × trait matrix (issue #7).

The last unbuilt ask of issue #7, and the one in its title — "+ build multi-trait
families", citing **doi:10.1186/s12859-022-05093-z** (DiviK: divisive intelligent
K-means for hands-free unsupervised clustering in big biological data).

What existed before this was *exact signature-architecture matching*: group
proteins whose signature-trait set is identical. That was computed ad-hoc in
`research/swissprot-trait-profiles-1.md` for a 1,000-protein pilot (45 families)
and never became a script. It finds only proteins that match perfectly, so a
protein with one extra domain falls out of its own family.

DiviK's two defining ideas, both implemented here:

  • **Divisive, top-down.** Start with every protein in one cluster and split
    recursively, accepting a split only when it is justified. Agglomerative or
    flat k-means would need the family count up front; a trait matrix has no
    natural k.
  • **Local feature-space adaptation.** At each node the feature set is
    re-selected from *that node's* proteins. A trait carried by every protein in
    a node (or by almost none) cannot separate it, and globally-rare traits are
    exactly the ones that distinguish a subfamily once you are inside it. This is
    the part that makes the method "hands-free" and the part a plain k-means
    lacks.

Deviations from the paper, stated rather than buried: DiviK uses the GAP
statistic to pick k per node and an amplitude/variance filter tuned for mass
spectrometry imaging. Here k is fixed at 2 (a binary trait space has no
continuous amplitude to threshold, and repeated binary splits reach the same
partitions), and a split is accepted on mean silhouette over the locally-selected
features. The stopping rules — minimum family size, minimum informative features,
minimum silhouette — are the hyperparameters, all exposed as flags.

Output: `data/families/trait_families.tsv`, one row per family with its size, the
**core traits** (carried by ≥ --core-frac of members, i.e. what defines the
family), and a readable label taken from the most specific core trait.

  just cluster-families                 # dry-run, prints the summary
  just cluster-families --apply
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
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "families" / "trait_families.tsv"

# traits that describe what a protein *is*; GO/EC describe what it does and would
# cluster by annotation depth rather than architecture
SIG_PREFIXES = ("Pfam", "InterPro", "CDD", "PROSITE", "SMART", "NCBIfam",
                "CATH", "SUPERFAMILY", "HAMAP", "PIRSF", "PANTHER", "PRINTS")


def load_matrix(min_support: int):
    """(rows, vocab, csr matrix) over signature traits only."""
    import numpy as np
    from scipy.sparse import csr_matrix

    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    rows = []
    for line in JSONL.open(encoding="utf-8"):
        r = json.loads(line)
        ts = {t for t in r["traits"]
              if t.split(":")[0] in SIG_PREFIXES and t in idx}
        if ts:
            r["_ts"] = ts
            rows.append(r)
    supp = collections.Counter()
    for r in rows:
        supp.update(r["_ts"])
    vocab = sorted(t for t, c in supp.items() if c >= min_support)
    pos = {t: i for i, t in enumerate(vocab)}
    indptr, indices = [0], []
    for r in rows:
        indices.extend(sorted(pos[t] for t in r["_ts"] if t in pos))
        indptr.append(len(indices))
    X = csr_matrix((np.ones(len(indices), dtype=np.float32), indices, indptr),
                   shape=(len(rows), len(vocab)))
    keep = np.asarray((X.getnnz(axis=1) > 0)).ravel()
    return [r for r, k in zip(rows, keep) if k], vocab, X[keep]


def divik(X, members, args, depth=0):
    """Recursively split `members`; yield leaf index arrays.

    The feature re-selection at the top of each call is DiviK's contribution —
    without it a split is decided by whichever traits happen to be common
    globally, which are exactly the traits that carry no information *inside* a
    node that already shares them.
    """
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    n = len(members)
    if n < 2 * args.min_size or depth >= args.max_depth:
        yield members
        return

    sub = X[members]
    count = np.asarray(sub.sum(axis=0)).ravel()
    # An ABSOLUTE floor, not a fraction. A fractional floor scales with node size
    # and so discards precisely the traits that discriminate inside a large node:
    # at the root a 2% floor demanded 1,373 carriers when the median trait has 10,
    # leaving 22 usable features of 19,894 and stranding 82% of proteins in one
    # unsplittable blob. The upper bound stays fractional — a trait carried by
    # nearly everything in a node genuinely cannot separate it.
    informative = np.where((count >= args.min_feature_count) &
                           (count <= args.max_prevalence * n))[0]
    if len(informative) < args.min_features:
        yield members                      # nothing here can separate this node
        return

    local = sub[:, informative]
    norm = np.sqrt(local.multiply(local).sum(axis=1))
    norm[norm == 0] = 1
    local = local.multiply(1.0 / norm).tocsr()

    # Project locally before splitting. Both k-means and silhouette are
    # meaningless directly on ~20,000-dim sparse binary vectors — every pair is
    # nearly equidistant, so the root split scored below any sane threshold and
    # the whole matrix came back as one family. Selecting features (DiviK's
    # step) fixes *which* dimensions; it does not fix *how many*.
    from sklearn.decomposition import TruncatedSVD
    k = min(args.svd, local.shape[1] - 1, local.shape[0] - 1)
    space = TruncatedSVD(n_components=k, random_state=args.seed).fit_transform(local) \
        if k >= 2 else local.toarray()

    labels = KMeans(n_clusters=2, n_init=4, random_state=args.seed).fit_predict(space)
    a, b = members[labels == 0], members[labels == 1]
    if len(a) < args.min_size or len(b) < args.min_size:
        yield members
        return

    take = np.random.default_rng(args.seed).choice(
        n, size=min(n, 2000), replace=False)
    try:
        sil = silhouette_score(space[take], labels[take])
    except ValueError:
        sil = -1.0
    if sil < args.min_silhouette:
        yield members                      # the split is not justified
        return

    yield from divik(X, a, args, depth + 1)
    yield from divik(X, b, args, depth + 1)


def record_labels(curies: set) -> dict:
    """{trait CURIE → record label} for the given traits."""
    import re
    want = set(curies)
    out = {}
    ident = re.compile(r"(?m)^identifier:\s*(\S+)\s*$")
    label = re.compile(r"(?m)^label:\s*\"?([^\"\n]+)")
    for p in TRAITS.rglob("*.yaml"):
        head = p.read_text(encoding="utf-8", errors="replace")[:400]
        m = ident.search(head)
        if m and m.group(1) in want:
            lm = label.search(head)
            out[m.group(1)] = (lm.group(1).strip() if lm else m.group(1))
            if len(out) == len(want):
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-support", type=int, default=5,
                    help="a trait needs this many carriers to be a feature at all")
    ap.add_argument("--min-size", type=int, default=5,
                    help="smallest acceptable family")
    ap.add_argument("--min-features", type=int, default=3,
                    help="informative traits a node needs before it may split")
    ap.add_argument("--min-feature-count", type=int, default=5,
                    help="carriers a trait needs *within a node* to inform its "
                         "split (absolute, not a fraction — see divik())")
    ap.add_argument("--max-prevalence", type=float, default=0.98,
                    help="…and no commoner than this (universal traits separate nothing)")
    ap.add_argument("--min-silhouette", type=float, default=0.02,
                    help="reject a split below this silhouette")
    ap.add_argument("--svd", type=int, default=20,
                    help="dimensions to project a node into before splitting it")
    ap.add_argument("--max-depth", type=int, default=40)
    ap.add_argument("--core-frac", type=float, default=0.8,
                    help="a trait is 'core' if this fraction of members carry it")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--report")
    args = ap.parse_args()

    try:
        import numpy as np
    except ImportError:
        print("needs numpy + scipy + scikit-learn — run with system python3.",
              file=sys.stderr)
        return 2
    if not JSONL.exists():
        print(f"no protein matrix at {JSONL} — build it with `just build-profiles "
              f"--organisms --limit 25000 --jsonl-only --apply`", file=sys.stderr)
        return 2

    rows, vocab, X = load_matrix(args.min_support)
    print(f"matrix: {X.shape[0]:,} proteins × {X.shape[1]:,} signature traits",
          file=sys.stderr)

    leaves = [f for f in divik(X, np.arange(X.shape[0]), args)
              if len(f) >= args.min_size]

    # A cluster is a *family* only if its members actually share something: a
    # core trait set. Binary divisive k-means peels small coherent groups off a
    # large remainder one at a time, so the remainder survives as a big
    # core-less leaf (44,582 at depth 24, 34,412 at depth 60 — it shrinks
    # monotonically with depth but never dissolves). Calling that a family would
    # be a lie about the data; it is reported as UNASSIGNED.
    families, cores, unassigned = [], [], 0
    for fam in sorted(leaves, key=len, reverse=True):
        prev = np.asarray(X[fam].sum(axis=0)).ravel() / len(fam)
        core = [vocab[i] for i in np.where(prev >= args.core_frac)[0]]
        if not core:
            unassigned += len(fam)
            continue
        families.append(fam)
        cores.append(sorted(core, key=lambda c: -prev[vocab.index(c)])[:12])

    labels = record_labels({c for core in cores for c in core[:1]})
    clustered = sum(len(f) for f in families)
    sizes = sorted((len(f) for f in families), reverse=True) or [0]
    L = ["# Multi-trait families (DiviK-style divisive clustering)", "",
         f"matrix: {X.shape[0]:,} proteins × {X.shape[1]:,} signature traits "
         f"(GO/EC excluded — they cluster by annotation depth, not architecture)",
         "",
         f"**{len(families):,} families** with a shared core, covering "
         f"{clustered:,} proteins ({100*clustered/X.shape[0]:.0f}%); largest "
         f"{sizes[0]:,}, median {sizes[len(sizes)//2]}", "",
         f"{unassigned:,} proteins ({100*unassigned/X.shape[0]:.0f}%) are "
         f"**unassigned** — they end up in core-less leaves. Binary divisive "
         f"k-means peels coherent groups off a large remainder one at a time, so "
         f"that remainder shrinks with `--max-depth` (44,582 at 24, 34,412 at 60) "
         f"without dissolving. They are reported as unassigned rather than "
         f"labelled a family.", "",
         "| size | core traits (carried by ≥%d%% of members) | label |" % (100*args.core_frac),
         "|--:|---|---|"]
    for fam, core in list(zip(families, cores))[:25]:
        lbl = labels.get(core[0], core[0]) if core else "—"
        L.append(f"| {len(fam):,} | {', '.join(core[:4]) or '—'} | {lbl} |")
    report = "\n".join(L)
    print(report)
    if args.report:
        Path(args.report).write_text(report + "\n", encoding="utf-8")

    if not args.apply:
        print("\nDry-run — pass --apply to write.", file=sys.stderr)
        return 0

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    from datetime import datetime, timezone
    organisms = len({r.get("taxon_label") for r in rows if r.get("taxon_label")})
    with outp.open("w", encoding="utf-8") as fh:
        # Provenance header. The input matrix (data/profiles/profiles.jsonl) is
        # gitignored, so without this a reader cannot tell what this file was
        # clustered from, and the hyperparameters materially change it (#64).
        fh.write(f"# built: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n")
        fh.write("# script: cluster_trait_families.py (DiviK, "
                 "doi:10.1186/s12859-022-05093-z)\n")
        fh.write(f"# matrix: {X.shape[0]:,} proteins x {X.shape[1]:,} signature "
                 f"traits, {organisms} organisms\n")
        fh.write(f"# params: min_support={args.min_support} min_size={args.min_size} "
                 f"min_features={args.min_features} "
                 f"min_feature_count={args.min_feature_count} "
                 f"max_prevalence={args.max_prevalence} "
                 f"min_silhouette={args.min_silhouette} svd={args.svd} "
                 f"max_depth={args.max_depth} core_frac={args.core_frac} "
                 f"seed={args.seed}\n")
        fh.write(f"# families: {len(families):,} covering {clustered:,} proteins; "
                 f"unassigned: {unassigned:,}\n")
        fh.write("family_id\tsize\tcore_traits\tlabel\tmembers\n")
        for i, (fam, core) in enumerate(zip(families, cores), 1):
            lbl = labels.get(core[0], core[0]) if core else ""
            fh.write(f"TF{i:05d}\t{len(fam)}\t{'|'.join(core)}\t{lbl}\t"
                     f"{','.join(rows[j]['accession'] for j in fam)}\n")
    print(f"\nwrote {len(families):,} families → "
          f"{outp.relative_to(REPO_ROOT) if str(outp).startswith(str(REPO_ROOT)) else outp}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
