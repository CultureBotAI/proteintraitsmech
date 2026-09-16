#!/usr/bin/env python3
"""Does the sequence map recover structure better than the trait map? (#508)

The bar the issue set: if a protein-language-model sequence map does not beat
the TF-IDF protein map on CATH enrichment, it is not worth shipping. This
measures that, the same way `measure_map_structure.py` and
`research/protein-map-feature-space.md` measured the existing maps — neighbour
purity as lift over the purity expected from label proportions alone.

The bar as literally stated cannot be met by construction: CATH signatures are
*input features* of the protein map (`SIG_PREFIXES`), so its CATH purity is
label leakage, not recovery. Two comparisons are leakage-free and reported
alongside it:

  --control-map      a protein map rebuilt with CATH excluded from its features
                     (`build_protein_map.py --exclude-prefix CATH --out …`)
  EC class labels    what the protein does — an input to neither map

Labels, each held independently of the sequence (which is all the sequence
map saw):

  organism           — is this a curation-effort / proteome map?
  CATH class         — the coarse fold label the protein map is filtered by
  CATH superfamily   — the sharp one: fold *and* evolutionary relationship
  EC class / EC sub-subclass — enzyme function, top level and three levels

Compared on the proteins **both maps contain** that carry the label, so the
maps are scored on the same proteins with the same k. The sequence map is
measured in its embedding space (what the layout was computed from) and in 2-D
(what a reader sees); the protein map ships only its 2-D coordinates, so it is
measured there. A protein with several CATH assignments is labelled by its
first sorted one, as `build_protein_map.py` does for class; with `--any-match`
a neighbour counts as pure when the two proteins share *any* superfamily.

Read-only. Prints a markdown report (optionally --out).

  just measure-sequence-map
  just measure-sequence-map --control-map /path/to/protein_map_nocath.json \\
      --out research/sequence-map-structure.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from build_sequence_map import cath_class, cath_labels  # noqa: E402
from measure_map_structure import neighbours, purity  # noqa: E402

DOCS = REPO_ROOT / "docs" / "data"
EMB = REPO_ROOT / "data" / "embeddings" / "esm2"
PROFILES = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"

SEQ_EMB = "sequence map · ESM-2 embedding (1,280-d)"
SEQ_2D = "sequence map · 2-D layout"
PROT_2D = "protein map · 2-D layout (TF-IDF traits, CATH among the inputs)"
CTRL_2D = "control protein map · 2-D layout (CATH excluded from the inputs)"


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
    ap.add_argument("--out")
    args = ap.parse_args()

    try:
        import numpy as np
    except ImportError:
        print("needs numpy + scikit-learn — run with system python3.", file=sys.stderr)
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

    # EC from the Swiss-Prot profiles — an input to neither map
    ec: dict[str, list[str]] = {}
    with PROFILES.open(encoding="utf-8") as fh:
        for line in fh:
            d = json.loads(line)
            if d["accession"] in proteins and d.get("ec"):
                ec[d["accession"]] = sorted(d["ec"])

    seq_pt = {p[3]: p for p in seq["points"]}
    map_pts = {name: {p[3]: p for p in m["points"]} for name, m in maps.items()}
    shared_all = sorted(a for a in seq_pt if a in row_of
                        and all(a in pts for pts in map_pts.values()))

    def org(a):
        return (proteins[a].get("taxon_label") or "Unknown").split(" (")[0]

    # label → (accessions carrying it, label per accession)
    label_sets = {
        "organism": {a: org(a) for a in shared_all},
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
        if name == SEQ_EMB:
            return vecs[[row_of[a] for a in accs]]
        pts = seq_pt if name == SEQ_2D else map_pts[name]
        return np.asarray([[pts[a][0], pts[a][1]] for a in accs], dtype=np.float32)

    space_names = [SEQ_EMB, SEQ_2D] + list(maps)
    lifts: dict[tuple[str, str], float] = {}
    L = ["# Sequence map vs. protein map: which recovers CATH structure?", "",
         f"Scored on the proteins present on every map compared: {len(shared_all):,} "
         f"({len(seq_pt):,} on the sequence map"
         + "".join(f", {len(pts):,} on the {n.split(' ·')[0]}" for n, pts in map_pts.items())
         + f"). Per label, only proteins carrying that label count; k={args.k} "
         f"neighbours. Lift = purity / purity expected from label proportions; "
         f"1.0× is no structure.", "",
         "| label | proteins | classes | " + " | ".join(space_names) + " |",
         "|---|--:|--:|" + "--:|" * len(space_names)]
    for lab_name, lab in label_sets.items():
        accs = sorted(lab)
        if len(accs) < 100:
            L.append(f"| {lab_name} | {len(accs)} | — | " + " | ".join("too few" for _ in space_names) + " |")
            continue
        y = np.asarray([lab[a] for a in accs])
        sf_sets = [{superfamily(c) for c in cath[a]} for a in accs] \
            if lab_name == "CATH superfamily" else None
        cells = []
        for sn in space_names:
            ind = neighbours(space(sn, accs), args.k)
            if sf_sets is not None and args.any_match:
                obs, ch = any_match_purity(ind, sf_sets)
            else:
                obs, ch = purity(ind, y)
            lift = obs / ch if ch else 0.0
            lifts[(sn, lab_name)] = lift
            cells.append(f"{obs:.3f} / {ch:.3f} = **{lift:.2f}×**")
        L.append(f"| {lab_name} | {len(accs):,} | {len(set(y.tolist())):,} | "
                 + " | ".join(cells) + " |")

    s2, se = lifts[(SEQ_2D, "CATH superfamily")], lifts[(SEQ_EMB, "CATH superfamily")]
    p2 = lifts[(PROT_2D, "CATH superfamily")]
    L += ["", "## Verdict", ""]
    L.append(f"**Against the protein map as shipped, the sequence map's CATH-superfamily "
             f"lift in 2-D is {s2:.2f}× vs {p2:.2f}×** — "
             + ("above" if s2 > p2 else "below")
             + " it. That map takes CATH signatures as input features, so its figure is "
             "label leakage rather than recovery; it is the bar #508 wrote down, "
             "reported for the record.")
    if CTRL_2D in maps:
        c2 = lifts[(CTRL_2D, "CATH superfamily")]
        L.append(f"**Against the control protein map with CATH removed from its inputs, "
                 f"the sequence map's 2-D lift is {s2:.2f}× vs {c2:.2f}×** — "
                 + (f"the sequence map recovers CATH superfamilies {s2 / c2:.2f}× as "
                    f"strongly from sequence alone." if s2 > c2 else
                    "the remaining signatures (Pfam, InterPro, SUPERFAMILY …) still "
                    "encode fold more sharply than the sequence embedding's 2-D layout "
                    "does; they are expert structural classifications, not independent "
                    "of CATH."))
    L.append(f"In its own embedding space the sequence map's superfamily lift is "
             f"{se:.2f}×; the 2-D projection keeps {100 * s2 / se:.0f}% of it.")
    if (SEQ_2D, "EC sub-subclass") in lifts:
        e_s, e_p = lifts[(SEQ_2D, "EC sub-subclass")], lifts[(PROT_2D, "EC sub-subclass")]
        L.append(f"On enzyme function (EC sub-subclass), which neither map takes as input, "
                 f"the sequence map scores {e_s:.2f}× in 2-D "
                 f"({lifts[(SEQ_EMB, 'EC sub-subclass')]:.2f}× in embedding space) "
                 f"against the protein map's {e_p:.2f}×.")
    so, po = lifts[(SEQ_2D, "organism")], lifts[(PROT_2D, "organism")]
    L.append(f"Organism lift: sequence map {so:.2f}×, protein map {po:.2f}×. "
             + ("The sequence map is *less* organised by organism." if so < po else
                "The sequence map is *more* organism-organised: orthologues across the "
                "profile proteomes have near-identical sequences, so proximity by "
                "organism here is phylogeny rather than curation practice — but it is "
                "still organism."))

    L += ["", "## Caveats", "",
          "- The protein map ships only 2-D coordinates, so its pre-projection (50-d "
          "SVD) space is not measured here; `research/protein-map-feature-space.md` "
          "reports 3.12× CATH-*class* lift there on a different, larger protein set.",
          "- Multi-CATH proteins are labelled by their first sorted assignment"
          + (" for class; superfamily uses any-match." if args.any_match else
             " for both labels; `--any-match` relaxes superfamily."),
          "- EC labels come from the Swiss-Prot profiles, so the EC rows cover only "
          "the profile proteomes' enzymes; the first EC number is used for "
          "multi-EC proteins.",
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
