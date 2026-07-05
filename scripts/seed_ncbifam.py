#!/usr/bin/env python3
"""Seed protein-family traits from NCBIfam (ex-TIGRFAMs, US Gov public domain)
→ SEQUENCE (SEQ_DOMAIN / SEQ_FAMILY-superfamily / SEQ_REPEAT) or FUNCTION
(FUNC_PROTEIN_FAMILY for equivalog/subfamily) — routed by TIGRFAM isology type;
see route().

NCBIfam is NCBI's curated library of ~38k prokaryotic protein-family HMMs (the
PGAP set, which absorbed TIGRFAMs). Each HMM defines a family/domain — a trait
class, like Pfam. EC / GO assignments are NCBIfam-curated (source-direct → xrefs).

Input (fetch via `just fetch-ncbifam`, gitignored):
  data/raw/ncbifam/hmm_PGAP.tsv  — tab table, columns include:
    ncbi_accession, source_identifier, label, …, family_type, …, product_name,
    gene_symbol, gene_synonyms, ec_numbers, go_terms, …

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "ncbifam" / "hmm_PGAP.tsv"
OUT_DIR = REPO_ROOT / "data" / "traits"
LICENSE = "US Government public domain"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "ncbifam"


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


# NCBIfam/TIGRFAM models are sequence-profile HMMs, so their trait axis follows
# the *representation* (sequence space), not the biology:
#   repeat                                   → SEQUENCE / SEQ_REPEAT
#   *_domain, domain, signature              → SEQUENCE / SEQ_DOMAIN
#   superfamily                              → SEQUENCE / SEQ_HOMOLOGOUS_SUPERFAMILY
#   equivalog, subfamily, exception, paralog → FUNCTION / FUNC_PROTEIN_FAMILY
#     (whole-protein families whose defining property is a conserved function)
# The TIGRFAM "isology type" distinguishes these; `*_domain` variants (e.g.
# equivalog_domain) are domain-level and stay on SEQ_DOMAIN.
_FUNC_FAMILY_TYPES = {"equivalog", "subfamily", "exception", "hypoth_equivalog", "paralog"}


# family_type → (axis, category, subdir)
def route(family_type: str):
    ft = (family_type or "").lower()
    if "repeat" in ft:
        return "SEQUENCE", "SEQ_REPEAT", "sequence/repeat/ncbifam"
    if ft.endswith("_domain") or ft in ("domain", "signature"):
        return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/ncbifam"
    if ft == "superfamily":
        return "SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY", "sequence/homologous_superfamily/ncbifam"
    if ft in _FUNC_FAMILY_TYPES:
        return "FUNCTION", "FUNC_PROTEIN_FAMILY", "function/protein_family/ncbifam"
    # unknown / blank isology → default to sequence-signature domain
    return "SEQUENCE", "SEQ_DOMAIN", "sequence/domain/ncbifam"


def build_yaml(acc, label, definition, axis, category, ecs, gos, gene, family_type,
               model=""):
    lines = [f"identifier: NCBIfam:{acc}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: NCBIfam (NCBI PGAP HMM library)",
              f"trait_axis: {axis}", f"trait_category: {category}",
              "term_kind: CLASS", "mapping_status: SEEDED"]
    # synonyms: gene symbol + the HMM model name (kept discoverable now that the
    # readable product_name is the label), deduped against the label.
    syns = [s for s in (gene, model) if s and s != label]
    if syns:
        lines.append("synonyms:")
        for s in dict.fromkeys(syns):
            lines += [f"  - synonym_text: {yaml_escape(s)}",
                      "    synonym_type: EXACT_SYNONYM", "    source: NCBIfam"]
    # EC + GO are NCBIfam-curated assignments on the family → source-direct xrefs.
    xrefs = [f"EC:{e}" for e in ecs] + list(gos)
    if xrefs:
        lines += ["xrefs:"] + [f"  - {x}" for x in xrefs]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/ncbifam/hmm_PGAP.tsv; run `just fetch-ncbifam`",
              file=sys.stderr)
        return 2

    lines_in = RAW.read_text(encoding="utf-8", errors="replace").splitlines()
    header = lines_in[0].lstrip("#").split("\t")
    idx = {c: i for i, c in enumerate(header)}
    written = skipped = total = 0
    for line in lines_in[1:]:
        cols = line.split("\t")
        if len(cols) < len(header):
            cols += [""] * (len(header) - len(cols))

        def g(k): return cols[idx[k]].strip() if k in idx and idx[k] < len(cols) else ""
        acc = g("ncbi_accession").split(".")[0]
        if not acc:
            continue
        model = g("label")
        product = g("product_name")
        # readable product_name is the label; the terse HMM model name (e.g.
        # trim_DfrA1_rpt) is demoted to a synonym.
        label = product or model
        if not label:
            continue
        family_type = g("family_type")
        gene = g("gene_symbol")
        ecs = [e.strip() for e in re.split(r"[;, ]+", g("ec_numbers")) if e.strip()]
        gos = [x.strip() for x in re.split(r"[;, ]+", g("go_terms")) if x.strip().startswith("GO:")]
        axis, category, subdir = route(family_type)
        definition = (f"{product or model} — an NCBIfam protein family "
                      f"({acc}, {family_type or 'family'}); members share this "
                      f"conserved family signature.")
        total += 1
        path = OUT_DIR / subdir / f"{slugify(label)}-{acc.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(acc, label, definition, axis, category,
                                       ecs, gos, gene, family_type, model),
                            encoding="utf-8")
            written += 1

    print(f"{total} NCBIfam families → SEQ_DOMAIN / SEQ_HOMOLOGOUS_SUPERFAMILY / "
          f"SEQ_REPEAT / FUNC_PROTEIN_FAMILY (by isology type).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
