#!/usr/bin/env python3
"""Cross-axis SEQUENCE↔STRUCTURE alignment overlay — STEP 1 pilot.

The corpus splits records by *representation axis* (a Pfam/PROSITE signature is
SEQUENCE; a CATH/ECOD fold or an M-CSA/BioLiP/MetalPDB site is STRUCTURE), so the
two views of one protein region are never connected. This builder finds SEQUENCE
and STRUCTURE records that share an **exact canonical-example `protein_id`** and
whose annotations **overlap on that protein's residue coordinates**, and emits
typed cross-axis relationship edges.

Cross-axis pairs are a *relationship, never a merge* (per the merge-within-axis /
merge-traits skills), so this only ever writes `trait_relations`-style overlay
edges to `data/equivalence/seq_struct_alignment.tsv` (loaded bidirectionally by
build_docs_index.py, same as the other equivalence overlays).

STEP 1 uses ONLY already-stored coordinates on one shared UniProt frame:
  • `sequence_pattern` regex hits against the stored `canonical_examples[].sequence`
    (localizes SEQUENCE signature/motif records; PROSITE syntax → regex);
  • `canonical_examples[].features[]` intervals whose `trait_category` equals the
    record's own `trait_category` (localizes UniProt-FT-derived site/region
    records — e.g. an M-CSA STRUCT_ACTIVE_SITE record picks up the ACT_SITE
    residues on its exemplar).
It deliberately does NOT resolve PDB/CATH/ECOD `structure_ref` residues (that
needs SIFTS UniProt↔PDB mapping — step 2) and queries no external APIs, so
structure records located only by a representative PDB are out of scope here.

Predicate ladder (relate-only): identical residue set → `biolink:related_to`
(same physical feature by two representations); any other non-empty overlap →
`biolink:overlaps`. For *site* categories (active/binding/metal/PTM), any shared
residue is meaningful; for region×region, a reciprocal-overlap / Jaccard floor
applies. Finer predicates (part_of/narrow_match) and SIFTS providers are deferred.

Idempotent (fixed input → identical TSV). Stdlib + PyYAML. Read-only w.r.t.
records/schema; writes only the overlay TSV.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "equivalence" / "seq_struct_alignment.tsv"

# Site categories: few residues, so ANY shared residue is a real correspondence.
SITE_CATS = {
    "SEQ_ACTIVE_SITE", "SEQ_BINDING_SITE", "SEQ_PTM_SITE", "SEQ_MODIFIED_RESIDUE",
    "SEQ_GLYCOSYLATION_SITE", "SEQ_CROSSLINK_SITE", "SEQ_LIPIDATION_SITE",
    "STRUCT_ACTIVE_SITE", "STRUCT_BINDING_SITE", "STRUCT_METAL_SITE",
}
REGION_MIN_RECIPROCAL = 0.80   # region×region: strong reciprocal overlap …
REGION_MIN_JACCARD = 0.20      # … or this Jaccard floor


def prosite_to_regex(pattern: str) -> str | None:
    """Convert a PROSITE pattern (e.g. `[SA]-x(2)-{P}-L.`) to a Python regex.
    x=any, x(n)/x(n,m)=repeat, [..]=one of, {..}=none of, <=N-term, >=C-term."""
    p = (pattern or "").strip().rstrip(".")
    if not p:
        return None
    p = p.replace("-", "")
    p = p.replace("{", "[^").replace("}", "]")   # negation set (before repeats)
    p = p.replace("(", "{").replace(")", "}")     # repetition count
    p = p.replace("x", ".").replace("X", ".")
    p = p.replace("<", "^").replace(">", "$")
    try:
        re.compile(p)
    except re.error:
        return None
    return p


def _feature_residues(feat: dict) -> set[int]:
    try:
        s, e = int(feat["start"]), int(feat["end"])
    except (KeyError, TypeError, ValueError):
        return set()
    return set(range(min(s, e), max(s, e) + 1)) if s and e else set()


def located_residues(rec: dict) -> dict[str, set[int]]:
    """{protein_id: residue set} where this record's own trait falls on each
    exemplar, from stored pattern hits and category-matching FT features."""
    cat = rec.get("trait_category")
    pat = rec.get("sequence_pattern")
    rx = prosite_to_regex(pat) if pat else None
    out: dict[str, set[int]] = {}
    for ex in (rec.get("canonical_examples") or []):
        pid = ex.get("protein_id")
        if not pid:
            continue
        res: set[int] = set()
        seq = ex.get("sequence")
        if rx and seq:
            for m in re.finditer(rx, seq):
                res |= set(range(m.start() + 1, m.end() + 1))  # 1-indexed
        for f in (ex.get("features") or []):
            if isinstance(f, dict) and f.get("trait_category") == cat:
                res |= _feature_residues(f)
        if res:
            out.setdefault(pid, set()).update(res)
    return out


def classify(a: set[int], b: set[int], cat_a: str, cat_b: str):
    """(predicate, metric) for an overlapping SEQ/STRUCT residue-set pair, or None."""
    inter = a & b
    if not inter:
        return None
    if a == b:
        return "biolink:related_to", f"same-residues={len(inter)}"
    site = cat_a in SITE_CATS or cat_b in SITE_CATS
    if not site:
        recip = min(len(inter) / len(a), len(inter) / len(b))
        jacc = len(inter) / len(a | b)
        if recip < REGION_MIN_RECIPROCAL and jacc < REGION_MIN_JACCARD:
            return None
    return "biolink:overlaps", f"inter={len(inter)}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="cap files parsed (debug)")
    ap.add_argument("--dry-run", action="store_true", help="print stats, don't write")
    args = ap.parse_args()

    # protein_id → [(identifier, axis, category, residue set)]
    by_protein: dict[str, list] = {}
    parsed = with_loc = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        if "protein_id:" not in text or "canonical_examples:" not in text:
            continue
        if "sequence_pattern:" not in text and "feature_type:" not in text:
            continue  # nothing locatable from stored coordinates
        try:
            rec = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        if not isinstance(rec, dict):
            continue
        parsed += 1
        axis, cat, rid = (rec.get("trait_axis"), rec.get("trait_category"),
                          rec.get("identifier"))
        if axis not in ("SEQUENCE", "STRUCTURE") or not rid or not cat:
            continue
        loc = located_residues(rec)
        if loc:
            with_loc += 1
        for pid, res in loc.items():
            by_protein.setdefault(pid, []).append((rid, axis, cat, res))
        if args.limit and parsed >= args.limit:
            break

    # cross-axis pairs sharing a protein, with coordinate overlap
    edges: dict[tuple, tuple] = {}   # (seq_id, struct_id) → (pred, src)
    shared_proteins = 0
    for pid, recs in by_protein.items():
        seqs = [r for r in recs if r[1] == "SEQUENCE"]
        strs = [r for r in recs if r[1] == "STRUCTURE"]
        if not seqs or not strs:
            continue
        shared_proteins += 1
        for sid, _, scat, sres in seqs:
            for tid, _, tcat, tres in strs:
                if sid == tid:
                    continue
                got = classify(sres, tres, scat, tcat)
                if not got:
                    continue
                pred, metric = got
                key = (sid, tid)
                src = f"seq-struct-coord-overlap|{pid}|{metric}"
                # keep the strongest edge per pair (related_to > overlaps)
                if key not in edges or (pred == "biolink:related_to"
                                        and edges[key][0] != "biolink:related_to"):
                    edges[key] = (pred, src)

    rows = sorted((s, p, o, src) for (s, o), (p, src) in edges.items())
    print(f"parsed {parsed:,} example-bearing records; {with_loc:,} localized; "
          f"{len(by_protein):,} proteins ({shared_proteins:,} with both axes)")
    from collections import Counter
    pc = Counter(r[1] for r in rows)
    print(f"cross-axis alignment edges: {len(rows):,}  {dict(pc)}")
    if args.dry_run:
        for r in rows[:8]:
            print("  ", *r)
        print("Dry-run — not written.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print(f"wrote {len(rows):,} edges → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
