#!/usr/bin/env python3
"""Does the sequence map recover structure better than the trait map? (#508)

The bar the issue set: if a protein-language-model sequence map does not beat
the TF-IDF protein map on CATH enrichment, it is not worth shipping. This
measures that, the same way `measure_map_structure.py` and
`research/protein-map-feature-space.md` measured the existing maps — neighbour
purity as lift over the purity expected from label proportions alone.

CATH signatures are among the protein map's input features (`SIG_PREFIXES`),
so part of its CATH purity is the label read back. How large that part is gets
measured rather than assumed: pass `--control-map`, a protein map rebuilt with
`build_protein_map.py --exclude-prefix CATH --out …`, and the report states the
share of the shipped map's lift that disappears with the CATH features. EC
labels are an input to neither map and are reported alongside.

Labels:

  organism           — from the Swiss-Prot profiles (one spelling per proteome)
  CATH class         — majority class of the protein's CATH assignments
  CATH superfamily   — first sorted assignment (or any shared one: --any-match)
  EC class / EC sub-subclass — enzyme function, one and three levels

Spaces, all scored on the same proteins with the same k:

  ESM-2 embedding, raw            the stored 1,280-d vectors
  ESM-2 embedding, centred + L2   the same minus the corpus mean, then unit
                                  length again — the raw vectors are strongly
                                  anisotropic; centring alone would change
                                  nothing, Euclidean neighbours being
                                  translation-invariant
  PCA(100) + L2                   what PaCMAP is actually given
  sequence map 2-D                what a reader sees
  protein map 2-D                 the shipped trait map (only 2-D is shipped)
  control protein map 2-D         optional, CATH excluded from its inputs

`--breakdown` adds CATH-superfamily lifts for single- vs multi-superfamily
proteins and by sequence length, each with a bootstrap 95% interval (proteins
resampled, neighbourhoods fixed). Lifts are NOT comparable across subsets —
chance and the multi-superfamily fraction both change with length — so the
comparable number is the embedding-to-trait-map ratio *within* a subset, which
is reported with its own interval.

Read-only. Prints a markdown report (optionally --out). Needs numpy +
scikit-learn: run with the interpreter that has them, not `uv run`.

  just measure-sequence-map
  just measure-sequence-map --control-map /path/to/protein_map_nocath.json \\
      --breakdown --out research/sequence-map-structure.measured.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_sequence_map import LENGTH_BINS, cath_class, cath_labels, length_bin  # noqa: E402
from measure_map_structure import neighbours, purity  # noqa: E402

DOCS = REPO_ROOT / "docs" / "data"
EMB = REPO_ROOT / "data" / "embeddings" / "esm2"
PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"

SEQ_RAW = "ESM-2 embedding, raw (1,280-d)"
SEQ_CEN = "ESM-2 embedding, centred + L2 (1,280-d)"
SEQ_PCA = "PCA + L2 (PaCMAP's input)"
SEQ_2D = "sequence map 2-D"
PROT_2D = "protein map 2-D (TF-IDF traits, CATH among the inputs)"
CTRL_2D = "control protein map 2-D (CATH excluded from the inputs)"


def superfamily(curie: str) -> str:
    return ".".join(curie.split(":")[1].split(".")[:4])


def ec_levels(ec: str, n: int) -> str | None:
    """'EC:3.4.24.-' → '3.4.24' for n=3, or None if that level is unassigned."""
    parts = ec.split(":")[-1].split(".")
    if len(parts) < n or any(p in ("-", "") for p in parts[:n]):
        return None
    return ".".join(parts[:n])


def any_match_purity(ind, label_sets):
    """Purity where a neighbour counts if it shares any label; chance is the
    mean pairwise share rate over a random draw of the same neighbourhoods."""
    import numpy as np

    n, k = ind.shape
    obs = sum(1 for i in range(n) for j in ind[i] if label_sets[i] & label_sets[j]) / (n * k)
    rng = np.random.default_rng(0)
    rand = rng.integers(0, n, size=(n, k))
    ch = sum(1 for i in range(n) for j in rand[i] if label_sets[i] & label_sets[j]) / (n * k)
    return obs, ch


def bootstrap_lifts(ind, y, resamples):
    """Lift for each bootstrap resample of the proteins, neighbourhoods fixed.

    Per-protein purity is computed once; each resample re-averages it and
    recomputes chance on the resampled labels, so the interval covers both the
    numerator and the baseline. Chance uses the collision estimator
    (n·Σp̂² − 1)/(n − 1) rather than the plug-in Σp̂²: drawing with replacement
    duplicates proteins, which inflates Σp̂² by about (1 − Σp²)/n — 15% with
    several hundred rare superfamilies in under a thousand proteins — and would
    push every interval below its own point estimate.
    """
    import numpy as np

    codes = np.unique(y, return_inverse=True)[1]
    per_point = (codes[ind] == codes[:, None]).mean(axis=1)
    k = int(codes.max()) + 1
    out = np.empty(len(resamples), dtype=float)
    for b, idx in enumerate(resamples):
        n = len(idx)
        p = np.bincount(codes[idx], minlength=k) / n
        out[b] = per_point[idx].mean() / ((n * float((p ** 2).sum()) - 1.0) / (n - 1))
    return out


def load_map(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        p = DOCS / path
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sequence-map", default="sequence_map.json")
    ap.add_argument("--protein-map", default="protein_map.json")
    ap.add_argument("--control-map", default=None,
                    help="a protein map built with --exclude-prefix CATH")
    ap.add_argument("--emb-dir", default=str(EMB))
    ap.add_argument("--k", type=int, default=25)
    ap.add_argument("--any-match", action="store_true",
                    help="superfamily purity counts any shared superfamily")
    ap.add_argument("--breakdown", action="store_true",
                    help="CATH-superfamily lifts by domain count and sequence "
                         "length, with bootstrap intervals")
    ap.add_argument("--bootstrap", type=int, default=1000, help="resamples for --breakdown")
    ap.add_argument("--out")
    args = ap.parse_args()

    try:
        import numpy as np
        from sklearn.decomposition import PCA
    except ImportError:
        print("needs numpy + scikit-learn — run with the interpreter that has them "
              "(miniforge python3 here), not `uv run`.", file=sys.stderr)
        return 2

    emb = Path(args.emb_dir)
    for p in (emb / "ids.json", emb / "vectors.f16.npy", emb / "proteins.jsonl"):
        if not p.exists():
            print(f"missing {p} — run `just embed-sequences` first.", file=sys.stderr)
            return 2
    try:
        seq = load_map(args.sequence_map)
        maps = {PROT_2D: load_map(args.protein_map)}
        if args.control_map:
            maps[CTRL_2D] = load_map(args.control_map)
    except FileNotFoundError as e:
        print(f"missing map: {e} — build the maps first.", file=sys.stderr)
        return 2

    ids = json.loads((emb / "ids.json").read_text(encoding="utf-8"))
    vecs = np.load(emb / "vectors.f16.npy").astype(np.float32)
    proteins = {p["accession"]: p for p in
                (json.loads(line) for line in
                 (emb / "proteins.jsonl").read_text(encoding="utf-8").splitlines() if line)}
    row_of = {a: i for i, a in enumerate(ids)}
    cath = cath_labels(list(proteins.values()), PROFILES)

    # The spaces the layout passes through, rebuilt the way build_sequence_map.py
    # builds them (over every embedded protein, not just the scored subset).
    lay = seq.get("embedding") or {}
    centred = vecs - vecs.mean(axis=0, keepdims=True)
    centred /= np.maximum(np.linalg.norm(centred, axis=1, keepdims=True), 1e-12)
    n_comp = min(int(lay.get("pca") or 100), vecs.shape[0] - 1, vecs.shape[1])
    unit = vecs / np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-12)
    scores = PCA(n_components=n_comp, random_state=int(lay.get("seed") or 42)
                 ).fit_transform(unit).astype(np.float32)
    pca_in = scores / np.maximum(np.linalg.norm(scores, axis=1, keepdims=True), 1e-12)
    mean_cos = float(np.linalg.norm(unit.mean(axis=0)) ** 2)   # ≈ mean pairwise cosine

    # organism and EC from the Swiss-Prot profiles: one spelling per proteome,
    # and an input to neither map
    org: dict[str, str] = {}
    ec: dict[str, list[str]] = {}
    with PROFILES.open(encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            a = d["accession"]
            if a not in proteins:
                continue
            if d.get("taxon_label"):
                org[a] = d["taxon_label"].split(" (")[0]
            if d.get("ec"):
                ec[a] = sorted(d["ec"])

    seq_pt = {p[3]: p for p in seq["points"]}
    map_pts = {name: {p[3]: p for p in m["points"]} for name, m in maps.items()}
    shared_all = sorted(a for a in seq_pt if a in row_of
                        and all(a in pts for pts in map_pts.values()))

    label_sets = {
        "organism": {a: org[a] for a in shared_all if a in org},
        "CATH class": {a: cath_class(cath[a]) for a in shared_all if cath.get(a)},
        "CATH superfamily": {a: superfamily(cath[a][0]) for a in shared_all if cath.get(a)},
        "EC class": {a: lv for a in shared_all if a in ec
                     for lv in [ec_levels(ec[a][0], 1)] if lv},
        "EC sub-subclass": {a: lv for a in shared_all if a in ec
                            for lv in [ec_levels(ec[a][0], 3)] if lv},
    }
    if len(label_sets["CATH superfamily"]) < 100:
        print(f"only {len(label_sets['CATH superfamily'])} proteins are on every map with a "
              f"CATH label — not enough to compare.", file=sys.stderr)
        return 1

    def space(name, accs):
        rows = [row_of[a] for a in accs]
        if name == SEQ_RAW:
            return vecs[rows]
        if name == SEQ_CEN:
            return centred[rows]
        if name == SEQ_PCA:
            return pca_in[rows]
        pts = seq_pt if name == SEQ_2D else map_pts[name]
        return np.asarray([[pts[a][0], pts[a][1]] for a in accs], dtype=np.float32)

    space_names = [SEQ_RAW, SEQ_CEN, SEQ_PCA, SEQ_2D] + list(maps)
    lifts: dict[tuple[str, str], float] = {}
    lab_names = [n for n, lab in label_sets.items() if len(lab) >= 100]

    L = ["# Sequence map vs. protein map: neighbour-purity lifts", "",
         f"Scored on the proteins present on every map compared: {len(shared_all):,} "
         f"({len(seq_pt):,} on the sequence map"
         + "".join(f", {len(pts):,} on the {n.split(' 2-D')[0]}" for n, pts in map_pts.items())
         + f"). Per label, only proteins carrying that label count; k={args.k} "
         f"neighbours. Lift = purity / purity expected from label proportions; "
         f"1.0× is no structure. PCA({n_comp}); mean pairwise cosine of the raw "
         f"embedding {mean_cos:.2f}.", "",
         "| label | proteins | classes | chance |", "|---|--:|--:|--:|"]
    table = {sn: [] for sn in space_names}
    for lab_name in lab_names:
        lab = label_sets[lab_name]
        accs = sorted(lab)
        y = np.asarray([lab[a] for a in accs])
        sf_sets = [{superfamily(c) for c in cath[a]} for a in accs] \
            if lab_name == "CATH superfamily" and args.any_match else None
        chance = None
        for sn in space_names:
            ind = neighbours(space(sn, accs), args.k)
            obs, ch = any_match_purity(ind, sf_sets) if sf_sets is not None \
                else purity(ind, y)
            chance = ch
            lifts[(sn, lab_name)] = obs / ch if ch else 0.0
            table[sn].append(f"{lifts[(sn, lab_name)]:.2f}×")
        L.append(f"| {lab_name} | {len(accs):,} | {len(set(y.tolist())):,} | {chance:.4f} |")
    L += ["", "| space | " + " | ".join(lab_names) + " |",
          "|---|" + "--:|" * len(lab_names)]
    L += [f"| {sn} | " + " | ".join(table[sn]) + " |" for sn in space_names]

    sf = "CATH superfamily"
    s2, sp, sc, sr = (lifts[(n, sf)] for n in (SEQ_2D, SEQ_PCA, SEQ_CEN, SEQ_RAW))
    p2 = lifts[(PROT_2D, sf)]
    L += ["", "## What the numbers say", "",
          f"- **#508's bar, CATH superfamily in 2-D:** sequence map {s2:.2f}×, shipped "
          f"protein map {p2:.2f}× — the sequence map is "
          + ("above" if s2 > p2 else "below") + " it."]
    if CTRL_2D in maps:
        c2 = lifts[(CTRL_2D, sf)]
        L.append(f"- **How much of the protein map's figure is CATH read back:** removing "
                 f"the CATH features moves it {p2:.2f}× → {c2:.2f}×, so they account for "
                 f"{100 * (p2 - c2) / p2:.0f}% of it. Against that control the sequence map "
                 f"is " + ("above" if s2 > c2 else "below") + f" ({s2:.2f}× vs {c2:.2f}×).")
    L.append(f"- **Where the sequence map's signal goes:** centring and re-normalising "
             f"the raw embedding moves it {sr:.2f}× → {sc:.2f}×; PCA + L2, PaCMAP's actual "
             f"input, holds {sp:.2f}× ({100 * sp / sc:.0f}% of that); the 2-D layout holds "
             f"{s2:.2f}× ({100 * s2 / sp:.0f}% of its input).")
    if (SEQ_2D, "EC sub-subclass") in lifts:
        L.append(f"- **Enzyme function (EC sub-subclass), an input to neither map:** "
                 f"sequence map 2-D {lifts[(SEQ_2D, 'EC sub-subclass')]:.2f}× "
                 f"(centred embedding {lifts[(SEQ_CEN, 'EC sub-subclass')]:.2f}×), protein "
                 f"map 2-D {lifts[(PROT_2D, 'EC sub-subclass')]:.2f}×.")
    if (SEQ_2D, "organism") in lifts:
        L.append(f"- **Organism:** sequence map 2-D {lifts[(SEQ_2D, 'organism')]:.2f}×, "
                 f"protein map 2-D {lifts[(PROT_2D, 'organism')]:.2f}×. The cause of the "
                 f"difference is not measured here.")

    if args.breakdown:
        trait = CTRL_2D if CTRL_2D in maps else PROT_2D
        lab = label_sets[sf]
        accs_all = sorted(lab)
        n_sf = {a: len({superfamily(c) for c in cath[a]}) for a in accs_all}
        subsets = [("all", accs_all),
                   ("single-superfamily proteins", [a for a in accs_all if n_sf[a] == 1]),
                   ("multi-superfamily proteins", [a for a in accs_all if n_sf[a] > 1])]
        subsets += [(b, [a for a in accs_all if length_bin(proteins[a]["length"]) == b])
                    for b in LENGTH_BINS]
        cols = [SEQ_CEN, SEQ_2D, trait]
        L += ["", f"## Breakdown: CATH superfamily, with bootstrap 95% intervals "
              f"({args.bootstrap:,} resamples)", "",
              "Lifts are not comparable *across* rows: chance and the share of "
              "multi-superfamily proteins both change with length. The last column, the "
              "embedding-to-trait-map ratio *within* a row, is the comparable quantity. "
              f"Trait map here: {trait}.", "",
              "| subset | n | chance | multi-superfamily | " + " | ".join(cols)
              + " | centred embedding ÷ trait map |", "|---|--:|--:|--:|" + "--:|" * (len(cols) + 1)]
        rng = np.random.default_rng(0)
        for name, accs in subsets:
            if len(accs) < 100:
                L.append(f"| {name} | {len(accs)} | — | — | " + " | ".join(["too few"] * (len(cols) + 1)) + " |")
                continue
            y = np.asarray([lab[a] for a in accs])
            res = rng.integers(0, len(accs), size=(args.bootstrap, len(accs)))
            boots, point, cells, chance = {}, {}, [], 0.0
            for sn in cols:
                ind = neighbours(space(sn, accs), args.k)
                obs, chance = purity(ind, y)
                boots[sn] = bootstrap_lifts(ind, y, res)
                point[sn] = obs / chance
                lo, hi = np.percentile(boots[sn], [2.5, 97.5])
                cells.append(f"{point[sn]:.1f}× [{lo:.1f}, {hi:.1f}]")
            # chance cancels in the ratio: same proteins, same labels, same resample
            lo, hi = np.percentile(boots[SEQ_CEN] / boots[trait], [2.5, 97.5])
            multi = sum(n_sf[a] > 1 for a in accs) / len(accs)
            L.append(f"| {name} | {len(accs):,} | {chance:.4f} | {100 * multi:.0f}% | "
                     + " | ".join(cells)
                     + f" | {point[SEQ_CEN] / point[trait]:.2f} [{lo:.2f}, {hi:.2f}] |")

    L += ["", "## Caveats", "",
          "- The protein map ships only 2-D coordinates, so its pre-projection (50-d "
          "SVD) space is not measured here; `research/protein-map-feature-space.md` "
          "reports 3.12× CATH-*class* lift there on a different, larger protein set.",
          "- The two 2-D layouts were computed over different populations (the protein "
          "map over every profile protein, the sequence map over the example proteins); "
          "both are scored on the shared subset.",
          "- CATH class is the majority class of a protein's assignments; CATH "
          "superfamily is the first sorted assignment"
          + (" relaxed to any shared superfamily (`--any-match`)." if args.any_match
             else " (`--any-match` relaxes it)."),
          "- EC and organism labels come from the Swiss-Prot profiles, so those rows "
          "cover only the profile proteomes; the first EC number is used for multi-EC "
          "proteins.",
          "- Every row is scored on the shared subset, which is biased toward "
          "well-characterised proteins."]

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
