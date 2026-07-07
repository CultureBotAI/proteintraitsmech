#!/usr/bin/env python3
"""Seed conserved-domain traits from NCBI CDD (US Gov public domain)
→ SEQUENCE / SEQ_DOMAIN (+ SEQ_HOMOLOGOUS_SUPERFAMILY), and KOG → FUNCTION /
FUNC_ORTHOLOG_GROUP.

CDD models are sequence-space PSSMs/profile alignments, so their domain and
superfamily records live on the SEQUENCE axis (the axis follows the
representation, not the biology).

CDD mirrors several external models. We seed only the NCBI-curated content that
is NOT already in the corpus and SKIP the true mirrors:
  SKIP  pfam (Pfam ✓), COG (COG ✓), TIGR + NF (NCBIfam ✓), smart, LOAD_*
  → SEQ_DOMAIN      cd (curated domains), PRK (protein clusters), PLN, PHA,
                    PTZ, MTH, CHL, sd — parented to their `cl` superfamilies
  → FUNC_ORTHOLOG_GROUP  KOG (euKaryotic Orthologous Groups, like COG)
The domain → superfamily link comes from family_superfamily_links.

Inputs (fetch via `just fetch-cdd`, gitignored):
  data/raw/cdd/cddid_all.tbl.gz          "<PSSMID>\\t<acc>\\t<short>\\t<desc>\\t<len>"
  data/raw/cdd/family_superfamily_links  "<acc>\\t<PSSMID>\\t<cl_acc>\\t<cl_PSSMID>"

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "cdd"
CDDID = RAW / "cddid_all.tbl.gz"
LINKS = RAW / "family_superfamily_links"
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure"
LICENSE = "US Government public domain"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "cdd"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


KIND = {
    "SEQ_DOMAIN": "conserved domain",
    "SEQ_HOMOLOGOUS_SUPERFAMILY": "domain superfamily",
    "FUNC_ORTHOLOG_GROUP": "orthologous group",
    "FUNC_PROTEIN_FAMILY": "protein family",
}
AXIS = {
    "SEQ_DOMAIN": "SEQUENCE",
    "SEQ_HOMOLOGOUS_SUPERFAMILY": "SEQUENCE",
    "FUNC_ORTHOLOG_GROUP": "FUNCTION",
    "FUNC_PROTEIN_FAMILY": "FUNCTION",
}


def clean_cdd_desc(desc: str) -> str:
    """The cddid description is a real functional title; strip CDD status cruft
    ('; Reviewed' / '; Validated' / '; Provisional') and the 'N/A' placeholder."""
    d = " ".join((desc or "").split())
    d = re.sub(r"\s*;\s*(Reviewed|Validated|Provisional)\s*\.?$", "", d, flags=re.I)
    d = d.rstrip(" .")
    return "" if d.upper() in ("N/A", "NA", "") else d


def build_yaml(acc, short, desc, category, parent):
    # label = the canonical CDD short name (readable domain/gene name); definition
    # = the real functional description. The old seeding put the description in
    # `label` and buried the short name in synonyms (record-sample-review-1 S5).
    desc_c = clean_cdd_desc(desc)
    opaque = (not short) or short == acc            # e.g. short 'PRK00009' == acc
    label = (desc_c or acc) if opaque else short
    definition = desc_c or f"NCBI CDD {KIND[category]} ({acc})."
    lines = [f"identifier: CDD:{acc}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: NCBI CDD", f"trait_axis: {AXIS[category]}",
              f"trait_category: {category}", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if parent:
        lines += ["parent_traits:", f"  - CDD:{parent}"]
    if short and short != label and short != acc:
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(short)}",
                  "    synonym_type: EXACT_SYNONYM", "    source: CDD"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not CDDID.exists():
        print("missing data/raw/cdd/cddid_all.tbl.gz; run `just fetch-cdd`",
              file=sys.stderr)
        return 2

    # accession → (shortname, description)
    info: dict[str, tuple[str, str]] = {}
    with gzip.open(CDDID, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) >= 4:
                info[c[1].strip()] = (c[2].strip(), c[3].strip())

    # curated-domain accession → superfamily accession (cl…)
    parent_of: dict[str, str] = {}
    if LINKS.exists():
        for line in LINKS.read_text(encoding="utf-8", errors="replace").splitlines():
            c = line.split("\t")
            if len(c) >= 3 and c[0].startswith("cd") and c[2].startswith("cl"):
                parent_of[c[0].strip()] = c[2].strip()

    # cd/sd are curated *domain* models → SEQUENCE. PRK/PLN/PHA/PTZ/MTH/CHL are
    # full-length *protein-cluster* models (whole-protein functional families) →
    # FUNCTION, consistent with the NCBIfam function-family carve-out (axis-split
    # review 1). KOG (eukaryotic orthologous groups) → FUNC_ORTHOLOG_GROUP.
    DOMAIN_PREFIXES = ("cd", "sd")
    PROTEIN_FAMILY_PREFIXES = ("PRK", "PLN", "PHA", "PTZ", "MTH", "CHL")

    def route(acc):
        if acc.startswith("KOG"):
            return "FUNC_ORTHOLOG_GROUP", "function/ortholog_group"
        if any(acc.startswith(p) for p in PROTEIN_FAMILY_PREFIXES):
            return "FUNC_PROTEIN_FAMILY", "function/protein_family"
        if any(acc.startswith(p) for p in DOMAIN_PREFIXES):
            return "SEQ_DOMAIN", "sequence/domain"
        return None  # pfam/COG/TIGR/NF/smart/cl/LOAD_* → skipped (covered/handled)

    seedable = {a: route(a) for a in info}
    seedable = {a: r for a, r in seedable.items() if r}
    domains = [a for a, (cat, _) in seedable.items() if cat == "SEQ_DOMAIN"]
    # Superfamilies that are parents of a seeded domain (emit as parent nodes).
    sfs = sorted({parent_of[a] for a in domains if a in parent_of and parent_of[a] in info})

    written = skipped = 0

    def emit(acc, category, subdir, parent):
        nonlocal written, skipped
        short, desc = info[acc]
        path = OUT_DIR.parent / subdir / "cdd" / f"{slugify(desc or short)}-{acc.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(acc, short, desc, category, parent),
                            encoding="utf-8")
            written += 1

    for sf in sfs:
        emit(sf, "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily", "")
    for acc, (cat, subdir) in sorted(seedable.items()):
        parent = parent_of.get(acc) if cat == "SEQ_DOMAIN" else ""
        emit(acc, cat, subdir, parent if parent in info else "")

    n_kog = sum(1 for _, (c, _) in seedable.items() if c == "FUNC_ORTHOLOG_GROUP")
    print(f"CDD: {len(domains)} curated domains + {len(sfs)} superfamilies "
          f"(SEQ) + {n_kog} KOG orthologous groups (FUNC_ORTHOLOG_GROUP); "
          f"pfam/COG/TIGR/NF/smart skipped (covered).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {len(seedable) + len(sfs) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
