#!/usr/bin/env python3
"""Phase-3 structural equivalence (research/entry-merge-methods-round1.md, Tier 3).

CATH, SCOPe, ECOD and TED classify the *same folds* under different trees;
sequence member-overlap (Phase 2) is weak across these because homologs can
diverge past detectable sequence identity while keeping the fold. The decisive
signal is structure comparison of each entry's representative domain:

    Foldseek TM-score >= --tm-fold  (0.5) -> same fold        -> biolink:close_match
                       >= --tm-super (0.7) -> same superfamily -> biolink:close_match
                                                                 (level noted in relation_source)

Pipeline (two stages, so the runnable part works even without Foldseek):

  1. `--derive`  — build a *cross-source* representative manifest with NO
     external tools or network:
       - TED  : the AlphaFold model + domain chopping are encoded in the
                identifier (AF-<acc>-F1-model_v4_TEDnn) and definition.
       - CATH : each record carries a representative CATH domain xref
                (`CATH:<pdb><chain><dom>`, e.g. CATH:5fokA02) -> PDB pdb/chain.
       - ECOD : each F-group carries representative ECOD domain xrefs
                (`ECOD:e<pdb><chain><dom>`, e.g. ECOD:e2f2aB1)  -> PDB pdb/chain.
       - SCOPe: seeded records are class/fold-level nodes only (no px/domain
                sid), so no representative structure is derivable — skipped and
                logged.
     Emits data/analysis/structural_reps.tsv
     (curie, source, structure_type, structure_id, chain, range).
     `--derive-ted` keeps the old TED-only behaviour.

  2. default run — read the manifest, fetch each representative structure
     (AlphaFold model by accession, or PDB entry from RCSB; cached under
     data/raw/{af,pdb}_structures/, gitignored), chop to the domain range /
     chain (stdlib PDB parser — no biotite/gemmi needed), build a Foldseek DB,
     run all-vs-all `easy-search` reporting `alntmscore`, and emit
     data/equivalence/structural.tsv (close_match for cross-source pairs above
     threshold). Requires `foldseek` on PATH; if absent, prints install/run
     instructions and exits 3 (nothing else in the repo depends on it).

Foldseek + structure downloads are heavy; scope a run with --limit and/or a
pre-filtered manifest. Stdlib-only (PyYAML not needed).

  python3 scripts/build_structural_equivalence.py --derive --limit 4000
  python3 scripts/build_structural_equivalence.py --manifest data/analysis/structural_reps.tsv --limit 500

Caveat: CATH/ECOD representatives are compared at whole-chain granularity
(per-domain residue boundaries are not stored on the records), whereas TED
representatives are chopped to the domain. This is coarser for multi-domain
chains; note it when interpreting borderline TM-scores.
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
PDB_DIR = REPO_ROOT / "data" / "raw" / "pdb_structures"
WORK = REPO_ROOT / "data" / "raw" / "foldseek_work"
MANIFEST = REPO_ROOT / "data" / "analysis" / "structural_reps.tsv"
OUT = EQ_DIR / "structural.tsv"

AF_URL = "https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v4.pdb"
PDB_URL = "https://files.rcsb.org/download/{pdb}.pdb"

MANIFEST_COLS = ("curie", "source", "structure_type", "structure_id", "chain", "range")

# TED identifier: TED:AF-<acc>-F1-model_v4_TED<nn>; def "...residues 2-139...";
# note "...chopping 2-139...".
TED_RE = re.compile(r"AF-([A-Z0-9]+)-F\d+-model_v\d+_TED\d+")
CHOP_RE = re.compile(r"(?:chopping|residues)\s+([\d\-_]+)")
# CATH domain xref: CATH:<pdb4><chain1><dom2>  e.g. CATH:5fokA02
CATH_DOM_RE = re.compile(r"\bCATH:([0-9][0-9a-zA-Z]{3})([A-Za-z0-9])[0-9]{2}\b")
# ECOD domain xref: ECOD:e<pdb4><chain+><dom+>  e.g. ECOD:e2f2aB1
ECOD_DOM_RE = re.compile(r"\bECOD:e([0-9][0-9a-zA-Z]{3})([A-Za-z]+)\d+\b")


# --------------------------------------------------- representative extractors
# Each returns (structure_type, structure_id, chain, range) or None.
def _rep_ted(text: str):
    m = TED_RE.search(text)
    if not m:
        return None
    cm = CHOP_RE.search(text)
    return ("alphafold", m.group(1), "", cm.group(1) if cm else "")


def _rep_cath(text: str):
    m = CATH_DOM_RE.search(text)
    if not m:
        return None
    return ("pdb", m.group(1).lower(), m.group(2), "")


def _rep_ecod(text: str):
    m = ECOD_DOM_RE.search(text)
    if not m:
        return None
    return ("pdb", m.group(1).lower(), m.group(2), "")


# (source, [trait dirs], identifier regex, extractor)
SOURCE_SPECS = [
    ("TED", ["structure/fold/novel", "structure/fold/high_symmetry"],
     re.compile(r"^identifier:\s*(TED:\S+)", re.M), _rep_ted),
    ("CATH", ["structure/topology/cath", "structure/homologous_superfamily/cath"],
     re.compile(r"^identifier:\s*(CATH:\S+)", re.M), _rep_cath),
    ("ECOD", ["structure/fold/ecod"],
     re.compile(r"^identifier:\s*(ECOD:\S+)", re.M), _rep_ecod),
]
# SCOPe: seeded records are cl/cf/sf/fa nodes with no px domain sid -> no
# representative structure derivable. Reported in the derive summary.
SKIPPED_SOURCES = ["SCOPe (no representative px/domain sid on the seeded nodes)"]


# ---------------------------------------------------------------- derive stage
def derive_manifest(sources: list[str], limit: int) -> int:
    """Emit a cross-source (curie, source, structure_type, structure_id, chain,
    range) manifest — runnable with no external tools or network."""
    traits = REPO_ROOT / "data" / "traits"
    rows = []
    per_source: dict[str, int] = {}
    for name, dirs, id_re, extract in SOURCE_SPECS:
        if name not in sources:
            continue
        n = 0
        for sub in dirs:
            base = traits / sub
            if not base.exists():
                continue
            for path in base.rglob("*.yaml"):
                text = path.read_text(encoding="utf-8")
                mid = id_re.search(text)
                if not mid:
                    continue
                rep = extract(text)
                if not rep:
                    continue
                stype, sid, chain, rng = rep
                rows.append((mid.group(1), name, stype, sid, chain, rng))
                n += 1
        per_source[name] = n
    rows.sort()
    if limit:
        rows = rows[:limit]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(MANIFEST_COLS) + "\n")
        for row in rows:
            fh.write("\t".join(row) + "\n")
    summary = ", ".join(f"{k} {v:,}" for k, v in per_source.items())
    print(f"derived {len(rows):,} representatives ({summary}) "
          f"-> {MANIFEST.relative_to(REPO_ROOT)}")
    for s in SKIPPED_SOURCES:
        print(f"  skipped {s}")
    return 0


def enrich_ted(apply: bool) -> int:
    """Populate `structural_geometry_representations` on TED records — the
    AlphaFold representative + domain range are encoded in the identifier and
    definition, so this needs no compute. Makes each fold record carry an
    on-record 3D-geometry anchor (Foldseek/TM-score input). Idempotent."""
    traits = REPO_ROOT / "data" / "traits"
    enriched = skipped = 0
    for sub in ["structure/fold/novel", "structure/fold/high_symmetry"]:
        for path in (traits / sub).rglob("*.yaml"):
            text = path.read_text(encoding="utf-8")
            mid = re.search(r"^identifier:\s*(TED:\S+)", text, re.M)
            if not mid or "structural_geometry_representations:" in text:
                skipped += 1
                continue
            m = TED_RE.search(mid.group(1))
            if not m:
                skipped += 1
                continue
            acc = m.group(1)
            cm = CHOP_RE.search(text)
            block = ["structural_geometry_representations:",
                     f"- structure_ref: AlphaFoldDB:{acc}",
                     "  structure_source: TED"]
            if cm:
                block.append(f"  residue_range: {cm.group(1)}")
            block.append("  evidence_source: TED (Encyclopedia of Domains) v5")
            block_text = "\n".join(block) + "\n"
            # insert before canonical_examples (present on every TED record);
            # else append at end.
            if "\ncanonical_examples:" in text:
                text = text.replace("\ncanonical_examples:", "\n" + block_text + "canonical_examples:", 1)
            else:
                text = text.rstrip("\n") + "\n" + block_text
            if apply:
                path.write_text(text, encoding="utf-8")
            enriched += 1
    verb = "enriched" if apply else "would enrich"
    print(f"{verb} {enriched:,} TED records with structural_geometry_representations "
          f"({skipped:,} skipped). " + ("" if apply else "Pass --apply to write."))
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


def fetch_and_chop(stype: str, sid: str, chain: str, rng: str, dest: Path) -> bool:
    """Download a representative structure (cached) and write a chopped PDB to
    dest. AlphaFold models are fetched by accession; PDB entries from RCSB and
    filtered to `chain`. Stdlib PDB parse: keep ATOM/HETATM lines whose chain
    (col 22) matches and whose residue seq-number (cols 23-26) is in range."""
    if stype == "alphafold":
        raw = AF_DIR / f"AF-{sid}.pdb"
        url = AF_URL.format(acc=sid)
        cache_dir = AF_DIR
        want_chain = ""            # AF models are single chain A; keep all
    else:                          # "pdb"
        raw = PDB_DIR / f"{sid}.pdb"
        url = PDB_URL.format(pdb=sid)
        cache_dir = PDB_DIR
        want_chain = chain
    if not raw.exists():
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, raw)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {stype} fetch failed {sid}: {exc}", file=sys.stderr)
            return False
    segs = parse_range(rng)
    lines = []
    for ln in raw.read_text().splitlines():
        if ln.startswith(("ATOM", "HETATM")):
            if want_chain and ln[21:22].strip() != want_chain:
                continue
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


def read_manifest(manifest: Path) -> list[dict]:
    """Header-aware read; supports the new 6-col format and the legacy
    (curie, af_acc, range) TED-only format."""
    lines = [ln for ln in manifest.read_text().splitlines() if ln.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    out = []
    if header[:1] == ["curie"] and "structure_type" in header:
        idx = {c: header.index(c) for c in MANIFEST_COLS if c in header}
        for ln in lines[1:]:
            f = ln.split("\t")
            out.append({c: (f[idx[c]] if idx[c] < len(f) else "") for c in idx})
    else:  # legacy: curie \t af_acc \t range
        start = 0 if header[0].startswith(("TED:", "CATH:", "ECOD:")) else 1
        for ln in lines[start:]:
            f = (ln.split("\t") + ["", "", ""])[:3]
            out.append({"curie": f[0], "source": source_of(f[0]),
                        "structure_type": "alphafold", "structure_id": f[1],
                        "chain": "", "range": f[2]})
    return out


def run_foldseek(manifest: Path, limit: int, tm_fold: float, tm_super: float) -> int:
    if not shutil.which("foldseek"):
        print(
            "foldseek not found on PATH — Phase-3 structural comparison needs it.\n"
            "  Install:  conda install -c bioconda foldseek   # or download a static build\n"
            "            https://github.com/steineggerlab/foldseek\n"
            f"  Then re-run: python3 {Path(__file__).name} --manifest {manifest}\n"
            "The representative manifest (--derive) is already usable input.",
            file=sys.stderr)
        return 3
    if not manifest.exists():
        print(f"no manifest at {manifest}; run --derive first", file=sys.stderr)
        return 2

    rows = read_manifest(manifest)
    if limit:
        rows = rows[:limit]
    if WORK.exists():
        shutil.rmtree(WORK)
    pdb_dir = WORK / "pdb"
    pdb_dir.mkdir(parents=True)
    curie_by_stem = {}
    ok = 0
    for r in rows:
        cid = r["curie"]
        stem = re.sub(r"[^A-Za-z0-9]", "_", cid)
        if fetch_and_chop(r["structure_type"], r["structure_id"], r["chain"],
                          r["range"], pdb_dir / f"{stem}.pdb"):
            curie_by_stem[stem] = cid
            ok += 1
    print(f"prepared {ok:,}/{len(rows):,} representative structures")
    if ok < 2:
        print("need >=2 structures to compare", file=sys.stderr)
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
    EQ_DIR.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for s, p, o, rs in uniq:
            fh.write(f"{s}\t{p}\t{o}\t{rs}\n")
    print(f"wrote {len(uniq):,} structural close_match edges -> {OUT.relative_to(REPO_ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--derive", action="store_true",
                    help="build the cross-source representative manifest (TED+CATH+ECOD; no tools/network)")
    ap.add_argument("--derive-ted", action="store_true",
                    help="build a TED-only manifest (legacy)")
    ap.add_argument("--sources", default="TED,CATH,ECOD",
                    help="comma list of sources for --derive (default TED,CATH,ECOD)")
    ap.add_argument("--enrich-ted", action="store_true",
                    help="write structural_geometry_representations onto TED records")
    ap.add_argument("--apply", action="store_true", help="with --enrich-ted: write the YAMLs")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tm-fold", type=float, default=0.5)
    ap.add_argument("--tm-super", type=float, default=0.7)
    args = ap.parse_args()
    if args.enrich_ted:
        return enrich_ted(args.apply)
    if args.derive_ted:
        return derive_manifest(["TED"], args.limit)
    if args.derive:
        return derive_manifest([s.strip() for s in args.sources.split(",") if s.strip()], args.limit)
    return run_foldseek(args.manifest, args.limit, args.tm_fold, args.tm_super)


if __name__ == "__main__":
    sys.exit(main())
