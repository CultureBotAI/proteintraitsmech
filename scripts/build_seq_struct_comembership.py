#!/usr/bin/env python3
"""Cross-axis SEQUENCE↔STRUCTURE **co-membership** overlay (Path 2).

The residue-frame overlay (build_sequence_structure_alignment.py, Path 1) connects
a sequence signature and a structure record only when they overlap on a *shared
protein's residues*. That path is empty for signature×fold pairs because the
corpus's SEQUENCE-signature records (PROSITE/InterPro/Pfam, Swiss-Prot exemplars)
and STRUCT_FOLD records (TED, TrEMBL AlphaFold proteins) share **zero** exemplar
proteins (see research/sequence-structure-function-alignment-analysis-1.md §2).

This builder implements the analysis's **whole-protein co-membership path**: a
SEQUENCE signature and a STRUCTURE fold are related when the signature's exemplar
proteins are *consistently classified into that fold*. The bridge already lives in
the data — each SEQUENCE signature record's `canonical_examples[].family_classifications`
carry the CATH id(s) of the exemplar protein, and 8k+ STRUCTURE records are grounded
to CATH ids (identifier `CATH:x.y.z.w`, or an `xrefs` CATH). So:

  signature S  --(exemplars consistently CATH:X)-->  structure record grounded to CATH:X

Edges are **entity-level co-membership, relate-only** — `biolink:related_to`, never
`overlaps` (no residue support) and never a merge (cross-axis). Quality filters:
  • only CATH ids that are the *dominant* fold across S's exemplars (appear in
    ≥ --min-fraction of the exemplars that carry any CATH), top --max-cath per S —
    so an incidental co-domain on a multi-domain protein does not create an edge;
  • skip a CATH id that grounds > --anchor-cap structure records (a generic anchor).

Idempotent (fixed input → identical TSV). Stdlib + PyYAML. Read-only w.r.t.
records/schema; writes only data/equivalence/seq_struct_comembership.tsv.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT = REPO_ROOT / "data" / "equivalence" / "seq_struct_comembership.tsv"

MEMBERDB = {"InterPro", "Pfam", "SMART", "CDD", "PRINTS", "PANTHER", "NCBIfam",
            "PIRSF", "HAMAP", "SFLD", "PROSITE", "CATH", "SUPERFAMILY"}
# Only genuine structural-classification records are co-membership targets — a
# signature relates to a FOLD, not to a function site (active/binding/metal/…)
# that merely happens to share the fold.
FOLD_CATS = {"STRUCT_FOLD", "STRUCT_TOPOLOGY", "STRUCT_HOMOLOGOUS_SUPERFAMILY",
             "STRUCT_DOMAIN", "STRUCT_CLASS", "STRUCT_ARCHITECTURE"}
CATH_ID = re.compile(r"^[1-9][0-9]*(?:\.[0-9]+){3}$")   # 4-level CATH (superfamily)


def _cath_from(values) -> set[str]:
    out = set()
    for v in values or []:
        v = str(v)
        cid = v.split("CATH:", 1)[1] if v.startswith("CATH:") else None
        if cid and CATH_ID.match(cid):
            out.add(cid)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-fraction", type=float, default=0.5,
                    help="a CATH id must classify ≥ this fraction of a signature's "
                         "CATH-carrying exemplars to count (default 0.5)")
    ap.add_argument("--max-cath", type=int, default=3,
                    help="keep at most this many dominant CATH ids per signature (default 3)")
    ap.add_argument("--anchor-cap", type=int, default=8,
                    help="skip a CATH id grounding more than this many structure "
                         "records (generic anchor; default 8)")
    ap.add_argument("--limit", type=int, default=0, help="cap files parsed (debug)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # cath_id -> {structure record identifiers}, and the signature records with
    # their exemplar CATH multiset.
    cath_to_struct: dict[str, set] = defaultdict(set)
    signatures = []              # (identifier, n_ex_with_cath, Counter(cath->#ex), sample_proteins)
    parsed = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        axis = (re.search(r"^trait_axis:\s*(\S+)", text, re.M) or [0, ""])[1]
        if axis not in ("SEQUENCE", "STRUCTURE"):
            continue
        if axis == "STRUCTURE" and "CATH:" not in text:
            continue
        if axis == "SEQUENCE" and "family_classifications" not in text:
            continue
        try:
            rec = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        if not isinstance(rec, dict):
            continue
        parsed += 1
        rid = rec.get("identifier")
        if not rid:
            continue
        if axis == "STRUCTURE":
            if rec.get("trait_category") not in FOLD_CATS:
                continue                                 # skip sites/interface/etc.
            # ground by identifier CATH or any CATH xref
            gr = _cath_from([rid]) | _cath_from(rec.get("xrefs"))
            for cid in gr:
                cath_to_struct[cid].add(rid)
        else:
            prefix = rid.split(":", 1)[0]
            if prefix not in MEMBERDB:
                continue
            per_ex_cath = Counter()
            n_ex_cath = 0
            prots = []
            for ex in (rec.get("canonical_examples") or []):
                cids = _cath_from(ex.get("family_classifications"))
                if cids:
                    n_ex_cath += 1
                    for c in cids:
                        per_ex_cath[c] += 1
                    if ex.get("protein_id"):
                        prots.append(ex["protein_id"])
            if per_ex_cath:
                signatures.append((rid, n_ex_cath, per_ex_cath, prots))
        if args.limit and parsed >= args.limit:
            break

    rows = []
    skipped_generic = 0
    for rid, n_ex_cath, per_ex, prots in signatures:
        need = max(1, math.ceil(args.min_fraction * n_ex_cath))
        dominant = [(c, k) for c, k in per_ex.most_common() if k >= need]
        for cid, k in dominant[:args.max_cath]:
            targets = cath_to_struct.get(cid)
            if not targets:
                continue
            if len(targets) > args.anchor_cap:
                skipped_generic += 1
                continue
            for tid in sorted(targets):
                if tid == rid:
                    continue
                src = (f"seq-struct-comembership|{cid}|ex={k}/{n_ex_cath}"
                       f"|{','.join(sorted(set(prots))[:3])}")
                rows.append((rid, "biolink:related_to", tid, src))
    # dedup
    seen = set()
    uniq = []
    for r in rows:
        key = (r[0], r[2])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    uniq.sort()

    print(f"parsed {parsed:,} records; {len(signatures):,} signatures with CATH "
          f"classifications; {len(cath_to_struct):,} CATH ids grounding structure "
          f"records; {skipped_generic:,} (signature,CATH) pairs skipped (generic > "
          f"{args.anchor_cap})", file=sys.stderr)
    print(f"co-membership edges: {len(uniq):,} "
          f"({len(set(r[0] for r in uniq)):,} signatures → "
          f"{len(set(r[2] for r in uniq)):,} structure records)")
    if args.dry_run:
        for r in uniq[:8]:
            print("  ", *r)
        print("Dry-run — not written.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("subject\tpredicate\tobject\trelation_source\n")
        for r in uniq:
            fh.write("\t".join(r) + "\n")
    print(f"wrote {len(uniq):,} edges → {OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
