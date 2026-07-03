#!/usr/bin/env python3
"""Review the trait categories (and axes) each source contributes, and flag
records whose modelling looks wrong for a trait-*class* knowledge base.

For every `data/traits/**/*.yaml` this groups records by source (via the same
`infer_source` the docs build uses), then per source reports:
  - the trait_axis and trait_category distribution,
  - term_kind + mapping_status,
  - drift vs the `trait_categories` the source declares in download.yaml,
  - and ANOMALIES worth a human look:

    AXIS_CAT_MISMATCH  category prefix (SEQ_/STRUCT_/MIXED_/FUNC_/EVO_) does
                       not match the record's trait_axis.
    INSTANCE_LEVEL     the record is scoped to one protein (identifier
                       proteintraitsmech:UNIPROTKB_<acc>_… or a single
                       UniProtKB subject) — an annotation, not a reusable
                       trait class. Belongs as a canonical_example on the
                       class-level trait instead.
    FAMILY_AS_PARENT   parent_traits carries a family/domain SIGNATURE
                       (Pfam/InterPro/HAMAP/SMART/CATH/SCOP/…) on a record
                       that isn't itself a structural family — i.e. an
                       *association* misused as an rdfs:subClassOf parent.
    UNDECLARED_CAT     the record uses a category not in the source's
                       declared trait_categories (download.yaml).

Read-only. `--source NAME` restricts to one source; `--show N` lists up to N
example files per flag (default 3); `--flags-only` prints just the anomalies.
Stdlib + PyYAML.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import build_docs_index as bd  # noqa: E402  (reuse the canonical infer_source)

PREFIX_AXIS = {
    "SEQ": "SEQUENCE", "STRUCT": "STRUCTURE", "MIXED": "SEQUENCE_STRUCTURE",
    "FUNC": "FUNCTION", "EVO": "EVOLUTION",
}
FAMILY_PREFIXES = {
    "Pfam", "InterPro", "HAMAP", "SMART", "PRINTS", "PIRSF", "PANTHER",
    "NCBIfam", "PROSITE", "CATH", "SCOP", "SCOPe", "SUPERFAMILY", "Gene3D",
    "ECOD", "CDD", "TIGRFAMs",
}
# Categories that ARE structural families — a family signature IS a reasonable
# parent for these, so don't flag FAMILY_AS_PARENT on them.
FAMILY_CATEGORIES = {
    "STRUCT_DOMAIN", "STRUCT_FOLD", "STRUCT_HOMOLOGOUS_SUPERFAMILY",
    "STRUCT_TOPOLOGY", "STRUCT_ARCHITECTURE", "STRUCT_CLASS",
    "MIXED_STRUCTURAL_REPEAT", "MIXED_COILED_COIL", "SEQ_REPEAT",
    "SEQ_MOTIF", "SEQ_CONSERVATION",
}


def load_declared() -> dict[str, set[str]]:
    """source display-ish key → declared trait_categories, from download.yaml.
    Best-effort: keyed by both the `source:` slug and the `name:`'s first word,
    lowercased, so the reviewer can match a source label to a declared set."""
    out: dict[str, set[str]] = {}
    p = REPO_ROOT / "download.yaml"
    if not p.exists():
        return out
    import yaml
    for block in yaml.safe_load_all(p.open(encoding="utf-8")):
        if not isinstance(block, list):
            continue
        for b in block:
            if not isinstance(b, dict):
                continue
            cats = b.get("trait_categories")
            if not cats:
                continue
            cats = set(cats)
            for key in filter(None, [b.get("source"), b.get("name")]):
                out.setdefault(str(key).split()[0].lower(), set()).update(cats)
    return out


def norm(label: str) -> str:
    return label.split()[0].lower().replace("/", "").replace("-", "") if label else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", help="restrict to one source label")
    ap.add_argument("--show", type=int, default=3, help="example files per flag")
    ap.add_argument("--flags-only", action="store_true")
    args = ap.parse_args()

    import yaml
    declared = load_declared()

    by_src: dict[str, dict] = defaultdict(lambda: {
        "n": 0, "axis": Counter(), "cat": Counter(),
        "kind": Counter(), "status": Counter(),
        "flags": defaultdict(list),
    })

    for path in TRAITS.rglob("*.yaml"):
        try:
            d = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        ident = str(d.get("identifier", ""))
        rel = str(path.relative_to(REPO_ROOT))
        src = bd.infer_source(ident, path)
        if args.source and src != args.source:
            continue
        axis = d.get("trait_axis") or ""
        cat = d.get("trait_category") or ""
        s = by_src[src]
        s["n"] += 1
        s["axis"][axis] += 1
        s["cat"][cat] += 1
        s["kind"][d.get("term_kind") or ""] += 1
        s["status"][d.get("mapping_status") or ""] += 1

        # ---- anomaly flags ----
        pfx = cat.split("_")[0] if cat else ""
        if pfx in PREFIX_AXIS and PREFIX_AXIS[pfx] != axis:
            s["flags"]["AXIS_CAT_MISMATCH"].append(f"{rel}  ({axis} / {cat})")

        xrefs = [str(x) for x in (d.get("xrefs") or [])]
        up_subj = [x for x in xrefs if x.startswith("UniProtKB:")]
        if ident.startswith("proteintraitsmech:UNIPROTKB_") or (
                ident.startswith("proteintraitsmech:") and len(up_subj) == 1
                and up_subj[0].split(":")[1] in ident):
            s["flags"]["INSTANCE_LEVEL"].append(f"{rel}  ({ident})")

        # Family signatures as parents are only a problem when they are
        # CROSS-namespace associations (e.g. a UniProt-derived record parented
        # to Pfam/InterPro/HAMAP signatures). A source's own native hierarchy —
        # PROSITE pattern → PROSITE PDOC, Pfam family → Pfam clan — is a
        # legitimate broader grouping, so don't flag same-namespace parents.
        parents = [str(p) for p in (d.get("parent_traits") or [])]
        id_ns = ident.split(":")[0] if ":" in ident else ""
        fam_parents = [p for p in parents
                       if p.split(":")[0] in FAMILY_PREFIXES
                       and p.split(":")[0] != id_ns]
        if fam_parents and cat not in FAMILY_CATEGORIES:
            s["flags"]["FAMILY_AS_PARENT"].append(
                f"{rel}  (cat {cat}; parents {', '.join(fam_parents)})")

        dset = declared.get(norm(src))
        if dset and cat and cat not in dset:
            s["flags"]["UNDECLARED_CAT"].append(f"{rel}  ({cat} ∉ {sorted(dset)})")

    # ---- report ----
    total_flags = 0
    for src in sorted(by_src, key=lambda k: -by_src[k]["n"]):
        s = by_src[src]
        nflag = sum(len(v) for v in s["flags"].values())
        total_flags += nflag
        if args.flags_only and not nflag:
            continue
        print(f"\n=== {src}  ({s['n']:,} records) ===")
        if not args.flags_only:
            axes = ", ".join(f"{a}:{n}" for a, n in s["axis"].most_common())
            print(f"  axes:   {axes}")
            print(f"  status: {', '.join(f'{k}:{n}' for k, n in s['status'].most_common())}")
            print(f"  categories ({len(s['cat'])}):")
            for c, n in s["cat"].most_common():
                print(f"     {n:>7,}  {c}")
        if nflag:
            print(f"  ⚠ {nflag} flagged record(s):")
            for flag, items in sorted(s["flags"].items()):
                print(f"     {flag}: {len(items)}")
                for ex in items[:args.show]:
                    print(f"        - {ex}")
                if len(items) > args.show:
                    print(f"        … +{len(items) - args.show} more")

    print(f"\n{len(by_src)} sources reviewed; {total_flags} total flagged records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
