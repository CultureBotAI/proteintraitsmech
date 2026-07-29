#!/usr/bin/env python3
"""Is a corpus map showing what it claims to show? (issue #7, phase 9)

`docs/map.html` colours the corpus map by **trait axis**, which presents axis as
the structure the embedding recovers. That has never been tested. The competing
explanation is mundane: records from one source database share templated
definition prose and identifier conventions, so a map of record *text* may be
recovering **which database the record came from** and nothing more.

This measures both. For every point it takes the k nearest neighbours and asks
what fraction share the point's label, for two labelings of the same
neighbourhoods:

  axis    — SEQUENCE / STRUCTURE / FUNCTION / …   (what the browser colours by)
  source  — the identifier's CURIE prefix          (Pfam, CATH, GO, CDD, …)

Each is reported against the purity expected from label proportions alone, so
the two are comparable despite having different numbers of classes: a lift of
1.0 means the neighbourhoods are no more homogeneous than a random draw.

Measured in the **embedding space** (what the projection was computed from) and
in the **2-D map** (what a reader actually sees), because a 2-D projection
distorts neighbourhoods and the gap between the two rows is itself the evidence
for how much of the picture to trust. This is the same treatment
`build_protein_map.py` got in phase 8.

Read-only. Prints a markdown report (optionally --out).

  just measure-map                        # the full-record corpus map
  python3 scripts/measure_map_structure.py --map corpus_map_definitions.json \
      --emb-dir data/embeddings/definition
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs" / "data"


def neighbours(space, k):
    """Indices of each point's k nearest neighbours (self excluded).

    Computed once per space and reused for every labeling, so the labelings are
    scored on provably identical neighbourhoods — which is the whole basis of
    the axis-vs-source comparison, not merely an optimisation.
    """
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=min(k, len(space) - 1) + 1).fit(space)
    return nn.kneighbors(space)[1][:, 1:]


def purity(ind, labels):
    """(observed purity, chance purity) over precomputed neighbourhoods."""
    same = float((labels[ind] == labels[:, None]).mean())
    counts = collections.Counter(labels.tolist())
    n = len(labels)
    chance = sum((c / n) ** 2 for c in counts.values())
    return same, chance


def layout_report(points, np) -> list:
    """2-D degeneracy of the rendered coordinates.

    Neighbour purity is computed in the pre-projection space, so it cannot see a
    projection artefact: when all-zero rows collapsed 9.3% of the protein map
    onto the origin, purity *rose* (0.816 → 0.823) while the picture broke
    (PR #72). These statistics look at what is actually drawn.
    """
    P = np.asarray([[p[0], p[1]] for p in points], dtype=np.float64)
    n = len(P)
    H, _, _ = np.histogram2d(P[:, 0], P[:, 1], bins=40)
    dens = float(H.max()) / n
    occupied = int((H > 0).sum())
    distinct = len({(round(float(x), 3), round(float(y), 3)) for x, y in P})
    verdict = ("**suspect** — a cell this dense is usually degenerate rows, not a "
               "cluster" if dens > 0.08 else "plausible")
    return ["## 2-D layout degeneracy", "",
            "What is rendered, independent of any embedding. A single 40×40 cell "
            "holding a large share of points is the signature of rows that carry "
            "no position (all-zero features) rather than of a real cluster; "
            "compare 10.0% when the protein map was broken against 5.8% after.",
            "", "| | |", "|---|--:|",
            f"| points | {n:,} |",
            f"| densest 40×40 cell | **{100*dens:.1f}%** ({verdict}) |",
            f"| distinct 3-dp coordinates | {distinct:,} ({100*distinct/n:.1f}%) |",
            f"| occupied cells | {occupied:,} / 1,600 |", ""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", default="corpus_map.json",
                    help="file under docs/data/ to measure")
    ap.add_argument("--emb-dir", default="data/embeddings",
                    help="embedding dir matching that map")
    ap.add_argument("--k", type=int, default=25, help="neighbours per point")
    ap.add_argument("--sample", type=int, default=40000,
                    help="points to measure (exact kNN over all 344k records in "
                         "1024-d is slow; the axis-vs-source comparison uses "
                         "identical neighbourhoods either way, so sampling is "
                         "fair — and the result is stable from 12k to the full "
                         "corpus, checked)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--retrieval-sample", type=int, default=1500,
                    help="cross-source pairs to query in the retrieval counter-test")
    ap.add_argument("--skip-retrieval", action="store_true",
                    help="skip the full-corpus retrieval test (the slow part)")
    ap.add_argument("--layout-only", action="store_true",
                    help="report only 2-D layout degeneracy, which needs no "
                         "embedding — the one check that applies to maps built "
                         "from traits rather than text (e.g. protein_map.json)")
    ap.add_argument("--out")
    args = ap.parse_args()

    try:
        import numpy as np
    except ImportError:
        print("needs numpy + scikit-learn — run with system python3.", file=sys.stderr)
        return 2

    mp = DOCS / args.map
    emb = REPO_ROOT / args.emb_dir
    needed = [mp] if args.layout_only else [mp, emb / "ids.json",
                                            emb / "vectors.f16.npy"]
    for p in needed:
        if not p.exists():
            print(f"missing {p} — build the map first (`just embed-map`).", file=sys.stderr)
            return 2

    d = json.loads(mp.read_text(encoding="utf-8"))

    if args.layout_only:
        report = "\n".join([f"# Layout degeneracy of `{args.map}`", ""]
                           + layout_report(d["points"], np))
        print(report)
        if args.out:
            Path(args.out).write_text(report + "\n", encoding="utf-8")
            print(f"\nwrote {args.out}", file=sys.stderr)
        return 0

    ids = json.loads((emb / "ids.json").read_text(encoding="utf-8"))
    vecs = np.load(emb / "vectors.f16.npy")

    # the map's points carry (x, y, axisIdx, id, catIdx); join to the embedding
    # rows by identifier so both spaces describe the same records
    row_of = {rid: i for i, rid in enumerate(ids)}
    pts, keep_rows = [], []
    for p in d["points"]:
        i = row_of.get(p[3])
        if i is not None:
            pts.append(p)
            keep_rows.append(i)
    dropped = len(d["points"]) - len(pts)
    if not pts:
        print("no map point matched an embedding id — the map and the embedding "
              "were built from different corpus snapshots.", file=sys.stderr)
        return 1
    if dropped:
        pct = 100 * dropped / len(d["points"])
        print(f"warning: {dropped:,} of {len(d['points']):,} map points ({pct:.1f}%) "
              f"have no row in {args.emb_dir} and were dropped — the two artefacts "
              f"are out of sync; rebuild the embedding or the map before trusting "
              f"these numbers.", file=sys.stderr)

    rng = np.random.default_rng(args.seed)
    if 0 < args.sample < len(pts):
        sel = rng.choice(len(pts), size=args.sample, replace=False)
        pts = [pts[i] for i in sel]
        keep_rows = [keep_rows[i] for i in sel]

    hi = vecs[np.asarray(keep_rows)].astype(np.float32)
    two = np.asarray([[p[0], p[1]] for p in pts], dtype=np.float32)
    axis = np.asarray([d["axes"][p[2]] for p in pts])
    source = np.asarray([p[3].split(":")[0] for p in pts])

    L = [f"# Does `{args.map}` show trait axis, or source database?", "",
         f"{len(pts):,} records sampled of {len(d['points']) - dropped:,} joined "
         f"to the embedding ({len(d['points']):,} on the map"
         + (f", **{dropped:,} dropped — artefacts out of sync**" if dropped else
            ", all matched") + f"); {len(set(axis.tolist()))} axes, "
         f"{len(set(source.tolist()))} source namespaces; k={args.k} neighbours.", "",
         "| space | label | purity | chance | lift |", "|---|---|--:|--:|--:|"]
    results = {}
    for space_name, space in (("embedding (pre-projection)", hi),
                              ("2-d map (what is rendered)", two)):
        ind = neighbours(space, args.k)
        for lab_name, lab in (("trait axis", axis), ("source database", source)):
            obs, ch = purity(ind, lab)
            results[(space_name, lab_name)] = obs / ch if ch else 0.0
            L.append(f"| {space_name} | {lab_name} | {obs:.3f} | {ch:.3f} "
                     f"| **{obs/ch:.2f}×** |")

    emb_axis = results[("embedding (pre-projection)", "trait axis")]
    emb_src = results[("embedding (pre-projection)", "source database")]
    L += ["", f"**Source database organises the embedding {emb_src/emb_axis:.2f}× "
              f"as strongly as trait axis does.**" if emb_src > emb_axis else
          f"**Trait axis organises the embedding {emb_axis/emb_src:.2f}× as strongly "
          f"as source database does.**"]

    # per-source axis composition: a source that only ever emits one axis cannot
    # have its two purities told apart, which is the obvious confound
    by_src = collections.defaultdict(collections.Counter)
    for a, s in zip(axis.tolist(), source.tolist()):
        by_src[s][a] += 1
    mixed = {s: c for s, c in by_src.items() if len(c) > 1}
    L += ["", "## Confound check: are source and axis just the same variable?", "",
          f"{len(mixed)} of {len(by_src)} source namespaces emit more than one axis. "
          f"Where a source maps to exactly one axis the two labelings are "
          f"indistinguishable by construction, so the comparison above is only "
          f"meaningful to the extent this number is large.", "",
          "| source | records | axes emitted |", "|---|--:|---|"]
    for s, c in sorted(by_src.items(), key=lambda kv: -sum(kv[1].values()))[:12]:
        L.append(f"| {s} | {sum(c.values()):,} | "
                 f"{', '.join(f'{a} {100*n/sum(c.values()):.0f}%' for a, n in c.most_common(3))} |")

    # The unconditional comparison above is weak on its own: `source` has many
    # more classes than `axis` and is very nearly a refinement of it, so it can
    # win on lift almost by construction. The sharp question is conditional —
    # *within* a single axis, where every record is the same colour on the map,
    # do neighbourhoods still sort by which database the record came from?
    L += ["", "## The conditional test: source structure *within* one axis", "",
          "Restricted to one axis at a time, so axis cannot explain the result. "
          "A high lift here means the map is separating provenance, not biology.",
          "", "| axis | records | sources | source purity | chance | lift |",
          "|---|--:|--:|--:|--:|--:|"]
    order = np.argsort(axis)
    for ax in sorted(set(axis.tolist())):
        m = axis == ax
        if m.sum() < 200 or len(set(source[m].tolist())) < 2:
            L.append(f"| {ax} | {int(m.sum()):,} | "
                     f"{len(set(source[m].tolist()))} | — | — | too few to judge |")
            continue
        obs, ch = purity(neighbours(hi[m], args.k), source[m])
        L.append(f"| {ax} | {int(m.sum()):,} | {len(set(source[m].tolist()))} | "
                 f"{obs:.3f} | {ch:.3f} | **{obs/ch:.2f}×** |")

    # Source-stratified neighbourhoods look damning on their own, and they are
    # not the whole story: a record can have same-source neighbours simply
    # because nothing else in the corpus describes the same thing. The test that
    # separates "the embedding cannot see across sources" from "there was
    # usually nothing to see" is retrieval — take pairs already known to be
    # cross-source equivalent and ask where the partner ranks, against the WHOLE
    # corpus rather than a convenient pool.
    xs = REPO_ROOT / "data" / "equivalence" / "cross_source.tsv"
    if xs.exists() and not args.skip_retrieval:
        row_all = {rid: i for i, rid in enumerate(ids)}
        pairs = []
        with xs.open(encoding="utf-8") as fh:
            next(fh, "")
            for line in fh:
                c = line.rstrip("\n").split("\t")
                if (len(c) >= 3 and c[0].split(":")[0] != c[2].split(":")[0]
                        and c[0] in row_all and c[2] in row_all):
                    pairs.append((c[0], c[2]))
        if pairs:
            n_q = min(args.retrieval_sample, len(pairs))
            pick = rng.choice(len(pairs), size=n_q, replace=False)
            qs = [pairs[i] for i in pick]
            qi = np.asarray([row_all[a] for a, _ in qs])
            ti = np.asarray([row_all[b] for _, b in qs])
            Q = vecs[qi].astype(np.float32)
            Q /= np.linalg.norm(Q, axis=1, keepdims=True) + 1e-9
            K = args.k
            best = np.full((n_q, K), -1, dtype=np.int64)
            bestv = np.full((n_q, K), -1e9, dtype=np.float32)
            for s in range(0, len(ids), 20000):     # chunked: the full score
                B = vecs[s:s + 20000].astype(np.float32)   # matrix would be ~4 GB
                B /= np.linalg.norm(B, axis=1, keepdims=True) + 1e-9
                cat = np.concatenate([bestv, Q @ B.T], axis=1)
                idn = np.concatenate(
                    [best, np.arange(s, s + B.shape[0])[None, :].repeat(n_q, 0)], axis=1)
                part = np.argpartition(-cat, K, axis=1)[:, :K]
                bestv, best = np.take_along_axis(cat, part, 1), np.take_along_axis(idn, part, 1)
            best = np.take_along_axis(best, np.argsort(-bestv, axis=1), 1)
            top1 = sum(1 for r in range(n_q)
                       if best[r, 0] == ti[r] or (best[r, 0] == qi[r] and best[r, 1] == ti[r]))
            topk = sum(1 for r in range(n_q) if ti[r] in best[r])
            same_share = float(np.mean([
                np.mean([ids[j].split(":")[0] == qs[r][0].split(":")[0]
                         for j in best[r] if j != qi[r]] or [0]) for r in range(n_q)]))
            L += ["", "## Counter-test: can the embedding retrieve cross-source equivalents?",
                  "",
                  f"{n_q:,} pairs from `cross_source.tsv` whose two ends come from "
                  f"different databases, queried against all {len(ids):,} embedded "
                  f"records.", "",
                  "| | |", "|---|--:|",
                  f"| partner ranked #1 | **{100*top1/n_q:.1f}%** |",
                  f"| partner within top-{K} | **{100*topk/n_q:.1f}%** |",
                  f"| share of those top-{K} that are same-source | {100*same_share:.1f}% |",
                  "",
                  "Read this against the purity tables above before concluding "
                  "anything. Source-dominated neighbourhoods do **not** mean the "
                  "embedding is blind across sources — where a genuine "
                  "cross-source equivalent exists it is usually the nearest "
                  "neighbour of all. Most records simply have no counterpart in "
                  "another database, and their neighbourhoods fill with "
                  "same-source records by default."]

    L += [""] + layout_report(d["points"], np)

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
