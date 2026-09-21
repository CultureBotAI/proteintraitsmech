#!/usr/bin/env python3
"""Which preprocessing and layout settings keep the most structure? (#711)

`build_sequence_map.py` shipped with #508's reasoned defaults — L2 → PCA(100) →
L2 → PaCMAP with 15 neighbours — and `measure_sequence_map.py` then showed the
2-D layout keeping only 55% of its input's CATH-superfamily lift, and the raw
vectors gaining lift when centred before normalising. Neither default was
measured. This measures them: for every combination of

  prep        centre (subtract the corpus mean, then L2) | l2 (L2 only)
  pca         0 (none) | 50 | 100 | 200
  neighbours  5 | 10 | 15 | 30 | 50

it builds the layout exactly as the builder would (`prepare` + `layout` are
imported from it) and scores neighbour-purity lift at k = 25 on the proteins
the sequence map shares with the protein map, in PaCMAP's input space and in
2-D.

Neighbour purity is a *local* score, and the settings that raise it — fewer
neighbours above all — are the ones that can buy it by tearing the global
picture apart. So every layout also gets a **global** score that plays no part
in the ranking: random-triplet accuracy, the share of random protein triplets
(i, j, k) whose "is j or k nearer to i?" answer in 2-D agrees with the centred
1,280-d embedding. 0.5 is a random layout. A configuration is only worth
adopting if it raises the local score without lowering this one, so the sweep
names two winners: the **best** by CATH superfamily alone, and the **choice** —
the best among configurations whose global score is not below the shipped
default's. Both are re-run over several seeds beside the shipped default.

Selection and its check are kept apart. Configurations are **ranked on CATH
superfamily**; **EC sub-subclass is reported but never used to choose**, so it
shows whether a CATH-selected setting generalises to a label it was not tuned
on. The shipped default and the winner are re-run over several seeds, so a
difference smaller than the seed-to-seed spread is visible as such.

Read-only apart from `--out`. Needs numpy + scikit-learn (neighbour search) + pacmap.

  just sweep-sequence-map --out research/sequence-map-sweep.md
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_sequence_map import PREPS, cath_labels, layout, prepare  # noqa: E402
from measure_map_structure import neighbours, purity  # noqa: E402
from measure_sequence_map import ec_levels, superfamily  # noqa: E402

DOCS = REPO_ROOT / "docs" / "data"
EMB = REPO_ROOT / "data" / "embeddings" / "esm2"
PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
SHIPPED = ("l2", 100, 15)       # the #508 defaults the map first shipped with


def lift(space, y, k):
    obs, chance = purity(neighbours(space, k), y)
    return obs / chance if chance else 0.0


def triplet_accuracy(reference, xy, triplets):
    """Share of (i, j, k) triplets ordered the same way in `xy` as in `reference`."""
    import numpy as np

    i, j, k = triplets.T

    def nearer_j(space):
        return (np.linalg.norm(space[i] - space[j], axis=1)
                < np.linalg.norm(space[i] - space[k], axis=1))

    return float((nearer_j(reference) == nearer_j(xy)).mean())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--emb-dir", default=str(EMB))
    ap.add_argument("--protein-map", default=str(DOCS / "protein_map.json"))
    ap.add_argument("--profiles", default=str(PROFILES))
    ap.add_argument("--pca", type=int, nargs="+", default=[0, 50, 100, 200])
    ap.add_argument("--neighbors", type=int, nargs="+", default=[5, 10, 15, 30, 50])
    ap.add_argument("--triplets", type=int, default=200_000,
                    help="random triplets for the global-structure score")
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 1, 2, 3, 4],
                    help="the first seed is used for the grid; all of them for the "
                         "shipped-vs-best comparison")
    ap.add_argument("--k", type=int, default=25)
    ap.add_argument("--out")
    args = ap.parse_args()

    try:
        import numpy as np
    except ImportError:
        print("needs numpy + scikit-learn + pacmap — run with the interpreter that has "
              "them (miniforge python3 here), not `uv run`.", file=sys.stderr)
        return 2

    emb, profiles = Path(args.emb_dir), Path(args.profiles)
    ids = json.loads((emb / "ids.json").read_text(encoding="utf-8"))
    vecs = np.load(emb / "vectors.f16.npy").astype(np.float32)
    proteins = [json.loads(line) for line in
                (emb / "proteins.jsonl").read_text(encoding="utf-8").splitlines() if line]
    row_of = {a: i for i, a in enumerate(ids)}
    on_protein_map = {p[3] for p in
                      json.loads(Path(args.protein_map).read_text(encoding="utf-8"))["points"]}
    cath = cath_labels(proteins, profiles)
    ec: dict[str, str] = {}
    with profiles.open(encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            if d["accession"] in row_of and d.get("ec"):
                level = ec_levels(sorted(d["ec"])[0], 3)
                if level:
                    ec[d["accession"]] = level

    sf_accs = sorted(a for a in ids if a in on_protein_map and cath.get(a))
    ec_accs = sorted(a for a in ids if a in on_protein_map and a in ec)
    sf_rows, ec_rows = [row_of[a] for a in sf_accs], [row_of[a] for a in ec_accs]
    sf_y = np.asarray([superfamily(cath[a][0]) for a in sf_accs])
    ec_y = np.asarray([ec[a] for a in ec_accs])

    # one fixed yardstick for every configuration: the centred, unit-length embedding
    reference, *_ = prepare(vecs, "centre", 0)
    triplets = np.random.default_rng(0).integers(0, len(ids), size=(args.triplets, 3))
    triplets = triplets[(triplets[:, 0] != triplets[:, 1]) & (triplets[:, 0] != triplets[:, 2])
                        & (triplets[:, 1] != triplets[:, 2])]

    seed0 = args.seeds[0]
    results = []
    t0 = time.time()
    for prep, pca in itertools.product(PREPS, args.pca):
        Z, _, n_comp, kept, _ = prepare(vecs, prep, pca)
        in_sf, in_ec = lift(Z[sf_rows], sf_y, args.k), lift(Z[ec_rows], ec_y, args.k)
        for nb in args.neighbors:
            xy = np.asarray(layout(Z, "pacmap", nb, seed0), dtype=np.float32)
            results.append({"prep": prep, "pca": pca, "neighbors": nb, "kept": kept,
                            "in_sf": in_sf, "in_ec": in_ec,
                            "sf": lift(xy[sf_rows], sf_y, args.k),
                            "ec": lift(xy[ec_rows], ec_y, args.k),
                            "glob": triplet_accuracy(reference, xy, triplets)})
            r = results[-1]
            print(f"  {prep:6s} pca={pca:<3d} nb={nb:<2d}  input {in_sf:5.1f}×  2-D CATH "
                  f"{r['sf']:5.1f}×  2-D EC {r['ec']:4.1f}×  global {r['glob']:.3f}  "
                  f"({time.time() - t0:.0f}s)", file=sys.stderr)

    ranked = sorted(results, key=lambda r: -r["sf"])
    best = ranked[0]
    best_cfg = (best["prep"], best["pca"], best["neighbors"])
    shipped_row = next((r for r in results
                        if (r["prep"], r["pca"], r["neighbors"]) == SHIPPED), None)
    floor = shipped_row["glob"] if shipped_row else 0.0
    choice = next(r for r in ranked if r["glob"] >= floor)
    choice_cfg = (choice["prep"], choice["pca"], choice["neighbors"])

    def over_seeds(cfg):
        prep, pca, nb = cfg
        out = []
        Z, *_ = prepare(vecs, prep, pca)      # exact SVD: only the layout is seeded
        for seed in args.seeds:
            xy = np.asarray(layout(Z, "pacmap", nb, seed), dtype=np.float32)
            out.append((lift(xy[sf_rows], sf_y, args.k), lift(xy[ec_rows], ec_y, args.k),
                        triplet_accuracy(reference, xy, triplets)))
        return np.asarray(out)

    seeded = {cfg: over_seeds(cfg) for cfg in dict.fromkeys([SHIPPED, best_cfg, choice_cfg])}

    def cfg_name(cfg):
        return f"{cfg[0]} → " + (f"PCA({cfg[1]})" if cfg[1] else "no PCA") + f" → {cfg[2]} nb"

    L = ["# Sequence map: preprocessing and layout sweep", "",
         f"{len(ids):,} proteins embedded; scored on {len(sf_accs):,} with a CATH superfamily "
         f"({len(set(sf_y.tolist())):,} classes) and {len(ec_accs):,} with an EC sub-subclass "
         f"({len(set(ec_y.tolist())):,} classes) that are also on the protein map. "
         f"Neighbour-purity lift at k={args.k}; PaCMAP, seed {seed0} for the grid. "
         f"**Ranked on CATH superfamily; EC and the global score were not used to "
         f"choose.** Global = random-triplet accuracy against the centred 1,280-d "
         f"embedding over {len(triplets):,} triplets (0.5 = random).", "",
         "| prep | PCA | neighbours | variance kept | input CATH | 2-D CATH | 2-D ÷ input "
         "| input EC | 2-D EC | global |", "|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for r in ranked:
        cfg = (r["prep"], r["pca"], r["neighbors"])
        mark = "".join(t for c, t in ((SHIPPED, " ← shipped"), (best_cfg, " ← best"),
                                      (choice_cfg, " ← choice")) if c == cfg)
        L.append(f"| {r['prep']} | {r['pca'] or 'none'} | {r['neighbors']} | "
                 f"{100 * r['kept']:.1f}% | {r['in_sf']:.1f}× | **{r['sf']:.1f}×** | "
                 f"{100 * r['sf'] / r['in_sf']:.0f}% | {r['in_ec']:.1f}× | "
                 f"{r['ec']:.1f}× | {r['glob']:.3f}{mark} |")

    L += ["", f"## Shipped default, best and choice, over {len(args.seeds)} seeds", "",
          f"*Best* = highest 2-D CATH-superfamily lift. *Choice* = highest among "
          f"configurations whose global score on the grid seed is at least the shipped "
          f"default's ({floor:.3f}).", "",
          "| configuration | 2-D CATH superfamily (mean, min–max) | 2-D EC sub-subclass "
          "(mean, min–max) | global (mean, min–max) |", "|---|--:|--:|--:|"]
    for cfg, arr in seeded.items():
        tag = " / ".join(t for c, t in ((SHIPPED, "shipped"), (best_cfg, "best"),
                                        (choice_cfg, "choice")) if c == cfg)
        L.append(f"| {cfg_name(cfg)} ({tag}) | {arr[:, 0].mean():.1f}× ({arr[:, 0].min():.1f}–"
                 f"{arr[:, 0].max():.1f}) | {arr[:, 1].mean():.1f}× ({arr[:, 1].min():.1f}–"
                 f"{arr[:, 1].max():.1f}) | {arr[:, 2].mean():.3f} ({arr[:, 2].min():.3f}–"
                 f"{arr[:, 2].max():.3f}) |")
    a = seeded[SHIPPED]
    for label, cfg in (("best", best_cfg), ("choice", choice_cfg)):
        if cfg == SHIPPED or (label == "choice" and cfg == best_cfg):
            continue
        b = seeded[cfg]
        L += ["", f"**{label.capitalize()} ({cfg_name(cfg)}) against the shipped default:**", "",
              f"- CATH superfamily, the label used to rank: worst seed "
              f"{b[:, 0].min():.1f}× vs the default's best seed {a[:, 0].max():.1f}× — "
              + ("clear of seed noise." if b[:, 0].min() > a[:, 0].max()
                 else "NOT clear of seed noise."),
              f"- EC sub-subclass, not used to rank: {b[:, 1].mean():.1f}× vs "
              f"{a[:, 1].mean():.1f}× — "
              + ("the gain carries over to a label the setting was not tuned on."
                 if b[:, 1].min() > a[:, 1].max() else
                 "the ranges overlap or reverse, so the gain does not clearly carry over."),
              f"- Global structure: {b[:, 2].mean():.3f} ({b[:, 2].min():.3f}–"
              f"{b[:, 2].max():.3f}) vs {a[:, 2].mean():.3f} ({a[:, 2].min():.3f}–"
              f"{a[:, 2].max():.3f}) — "
              + ("every seed is below every seed of the default: the local gain is paid "
                 "for with the global picture." if b[:, 2].max() < a[:, 2].min() else
                 "not below the default once seed spread is counted."
                 if b[:, 2].mean() >= a[:, 2].min() else
                 "lower on average, with overlapping seeds.")]
    if best_cfg == SHIPPED:
        L += ["", "- The shipped default is already the best configuration in this grid."]

    by_prep = {p: np.mean([r["sf"] for r in results if r["prep"] == p]) for p in PREPS}
    by_nb = {n: np.mean([r["sf"] for r in results if r["neighbors"] == n])
             for n in args.neighbors}
    glob_nb = {n: np.mean([r["glob"] for r in results if r["neighbors"] == n])
               for n in args.neighbors}
    by_pca = {c: np.mean([r["sf"] for r in results if r["pca"] == c]) for c in args.pca}
    L += ["", "## Marginal means of 2-D CATH-superfamily lift", "",
          "- prep: " + ", ".join(f"{p} {v:.1f}×" for p, v in by_prep.items()),
          "- PCA: " + ", ".join(f"{c or 'none'} {v:.1f}×" for c, v in by_pca.items()),
          "- neighbours: " + ", ".join(f"{n} {v:.1f}×" for n, v in by_nb.items()),
          "- global score by neighbours: "
          + ", ".join(f"{n} {v:.3f}" for n, v in glob_nb.items())]

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
