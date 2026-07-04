#!/usr/bin/env python3
"""Phase-3 structural equivalence (research/entry-merge-methods-round1.md, Tier 3).

CATH, SCOPe, ECOD and TED classify the *same folds* under different trees;
sequence member-overlap (Phase 2) is weak across these because homologs can
diverge past detectable sequence identity while keeping the fold. The decisive
signal is structure comparison of each entry's representative domain:

    Foldseek TM-score ≥ --tm-fold  (0.5) → same fold        → biolink:close_match
                       ≥ --tm-super (0.7) → same superfamily → biolink:close_match
                                                               (level noted in relation_source)

Pipeline (two stages, so the runnable part works even without Foldseek):

  1. `--derive-ted`  — build a representative manifest with NO external tools:
     scan TED records, whose identifier encodes an AlphaFold model
     (AF-<acc>-F1-model_v4_TEDnn) and whose note carries the domain chopping,
     and emit data/analysis/structural_reps.tsv (curie, af_acc, range).
     (CATH/SCOPe/ECOD reps come from their source domain lists — see
     reference at bottom; drop rows into the same manifest.)

  2. default run — read the manifest, fetch each AlphaFold model
     (cached under data/raw/af_structures/, gitignored), chop to the domain
     range (stdlib PDB parser — no biotite/gemmi needed), build a Foldseek DB,
     run all-vs-all `easy-search` reporting `alntmscore`, and emit
     data/equivalence/structural.tsv (close_match for cross-source pairs above
     threshold). Requires `foldseek` on PATH; if absent, prints install/run
     instructions and exits 3 (nothing else in the repo depends on it).

Foldseek + AlphaFold downloads are heavy; scope a run with --limit and/or a
pre-filtered manifest. Stdlib-only (PyYAML not needed).

  python3 scripts/build_structural_equivalence.py --derive-ted --limit 2000
  python3 scripts/build_structural_equivalence.py --manifest data/analysis/structural_reps.tsv
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EQ_DIR = REPO_ROOT / "data" / "equivalence"
AF_DIR = REPO_ROOT / "data" / "raw" / "af_structures"
WORK = REPO_ROOT / "data" / "raw" / "foldseek_work"
MANIFEST = REPO_ROOT / "data" / "analysis" / "structural_reps.tsv"
OUT = EQ_DIR / "structural.tsv"

AF_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"
# TED identifier: TED:AF-<acc>-F1-model_v4_TED<nn>; def "...residues 2-139...";
# note "...chopping 2-139...".
TED_DIRS = ["structure/fold/novel", "structure/fold/high_symmetry"]
TED_RE = re.compile(r"AF-([A-Z0-9]+)-F\d+-model_v\d+_TED\d+")
CHOP_RE = re.compile(r"(?:chopping|residues)\s+([\d\-_]+)")


# ---------------------------------------------------------------- derive stage
def derive_ted_manifest(limit: int) -> int:
    """Emit a (curie, af_acc, range) manifest from TED records — runnable with
    no external tools or network. Reads the raw YAMLs by text (the domain range
    lives in the definition, not the lean shard projection)."""
    traits = REPO_ROOT / "data" / "traits"
    rows = []
    for sub in TED_DIRS:
        for path in (traits / sub).rglob("*.yaml"):
            text = path.read_text(encoding="utf-8")
            mid = re.search(r"^identifier:\s*(TED:\S+)", text, re.M)
            if not mid:
                continue
            cid = mid.group(1)
            m = TED_RE.search(cid)
            if not m:
                continue
            cm = CHOP_RE.search(text)
            rows.append((cid, m.group(1), cm.group(1) if cm else ""))
    rows.sort()
    if limit:
        rows = rows[:limit]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8") as fh:
        fh.write("curie\taf_acc\trange\n")
        for cid, acc, rng in rows:
            fh.write(f"{cid}\t{acc}\t{rng}\n")
    print(f"derived {len(rows):,} TED representatives → {MANIFEST.relative_to(REPO_ROOT)}")
    print("  (drop CATH/SCOPe/ECOD reps into the same file to compare across sources)")
    return 0


# --------------------------------------------------------------- foldseek stage
def parse_range(rng: str) -> list[tuple[int, int]]:
    """'2-139' or '2-80_100-139' -> [(2,139)] / [(2,80),(100,139)]."""
    out = []
    for seg in filter(None, rng.split("_")):
        if "-" in seg:
            a, b = seg.split("-")[:2]
            if a.isdigit() and b.isdigit():
                out.append((int(a), int(b)))
    return out


def fetch_and_chop(acc: str, rng: str, dest: Path) -> bool:
    """Download an AF model (cached) and write a chopped PDB to dest. Stdlib PDB
    parse: keep ATOM/HETATM lines whose residue seq-number is in range."""
    raw = AF_DIR / f"AF-{acc}.pdb"
    if not raw.exists():
        try:
            AF_DIR.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(AF_URL.format(acc=acc), raw)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! AF fetch failed {acc}: {exc}", file=sys.stderr)
            return False
    segs = parse_range(rng)
    lines = []
    for ln in raw.read_text().splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            try:
                resnum = int(ln[22:26])
            except ValueError:
                continue
            if segs and not any(a <= resnum <= b for a, b in segs):
                continue
        if ln.startswith(("ATOM", "HETATM", "TER", "END")):
            lines.append(ln)
    if not any(l.startswith("ATOM") for l in lines):
        return False
    dest.write_text("\n".join(lines) + "\n")
    return True


def source_of(curie: str) -> str:
    return curie.split(":", 1)[0]


def run_foldseek(manifest: Path, limit: int, tm_fold: float, tm_super: float) -> int:
    if not shutil.which("foldseek"):
        print(
            "foldseek not found on PATH — Phase-3 structural comparison needs it.\n"
            "  Install:  conda install -c bioconda foldseek   # or download a static build\n"
            "            https://github.com/steineggerlab/foldseek\n"
            f"  Then re-run: python3 {Path(__file__).name} --manifest {manifest}\n"
            "The representative manifest (--derive-ted) is already usable input.",
            file=sys.stderr)
        return 3
    if not manifest.exists():
        print(f"no manifest at {manifest}; run --derive-ted first", file=sys.stderr)
        return 2

    rows = [ln.split("\t") for i, ln in enumerate(manifest.read_text().splitlines())
            if i and ln.strip()]
    if limit:
        rows = rows[:limit]
    if WORK.exists():
        shutil.rmtree(WORK)
    pdb_dir = WORK / "pdb"
    pdb_dir.mkdir(parents=True)
    curie_by_stem = {}
    ok = 0
    for cid, acc, rng in ((r + ["", ""])[:3] for r in rows):
        stem = re.sub(r"[^A-Za-z0-9]", "_", cid)
        if fetch_and_chop(acc, rng, pdb_dir / f"{stem}.pdb"):
            curie_by_stem[stem] = cid
            ok += 1
    print(f"prepared {ok:,}/{len(rows):,} representative structures")
    if ok < 2:
        print("need ≥2 structures to compare", file=sys.stderr)
        return 2

    res = WORK / "aln.tsv"
    cmd = ["foldseek", "easy-search", str(pdb_dir), str(pdb_dir), str(res), str(WORK / "tmp"),
           "--alignment-type", "1",  # TM-align mode
           "--format-output", "query,target,alntmscore", "-e", "10", "--max-seqs", "2000"]
    print("running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    edges = []
    for ln in res.read_text().splitlines():
        q, t, tm = (ln.split("\t") + ["", "", ""])[:3]
        cq, ct = curie_by_stem.get(q.replace(".pdb", "")), curie_by_stem.get(t.replace(".pdb", ""))
        if not cq or not ct or cq == ct:
            continue
        if source_of(cq) == source_of(ct):
            continue                      # cross-source only
        try:
            score = float(tm)
        except ValueError:
            continue
        if score >= tm_fold:
            level = "superfamily" if score >= tm_super else "fold"
            edges.append((cq, "biolink:close_match", ct, f"foldseek-tm{score:.2f}-{level}"))

    seen, uniq = set(), []
    for s, p, o, rs in sorted(edges):
        k = tuple(sorted((s, o)))
        if k in seen:
            continue
        seen.add(k)
        uniq.append((s, p, o, rs))
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, p, o, rs in uniq:
            fh.write(f"{s}\t{p}\t{o}\t{rs}\n")
    print(f"wrote {len(uniq):,} structural close_match edges → {OUT.relative_to(REPO_ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--derive-ted", action="store_true",
                    help="build the representative manifest from TED records (no tools/network)")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tm-fold", type=float, default=0.5)
    ap.add_argument("--tm-super", type=float, default=0.7)
    args = ap.parse_args()
    if args.derive_ted:
        return derive_ted_manifest(args.limit)
    return run_foldseek(args.manifest, args.limit, args.tm_fold, args.tm_super)


if __name__ == "__main__":
    sys.exit(main())
