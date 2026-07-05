#!/usr/bin/env python3
"""Backfill real source prose into existing CDD + NCBIfam records IN PLACE
(record-sample-review-1 S1/S5) — so the enrichment already on the records
(trait_relations, license, xrefs, parents) is preserved (a re-seed would drop it).

  CDD (S5):    label = the cddid short name (readable), definition = the cddid
               functional description (cleaned of '; Reviewed' etc. and 'N/A').
               Was: label = the description, short name buried in synonyms.
  NCBIfam (S1): label = hmm_PGAP product_name (readable) instead of the terse HMM
               model name; the model name is demoted to a synonym.

Reads data/raw/cdd/cddid_all.tbl.gz and data/raw/ncbifam/hmm_PGAP.tsv. Idempotent;
dry-run unless --apply. Stdlib-only. Mirrors the updated seed_cdd/seed_ncbifam.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
CDDID = REPO_ROOT / "data" / "raw" / "cdd" / "cddid_all.tbl.gz"
NCBIFAM = REPO_ROOT / "data" / "raw" / "ncbifam" / "hmm_PGAP.tsv"

ID_RE = re.compile(r"^identifier:\s*(\S+)", re.M)
KIND = {"SEQ_DOMAIN": "conserved domain",
        "SEQ_HOMOLOGOUS_SUPERFAMILY": "domain superfamily",
        "FUNC_ORTHOLOG_GROUP": "orthologous group"}


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if any(c in unsafe for c in text) or text[0] in "-?" or text.lower() in {
            "null", "true", "false", "yes", "no", "on", "off"}:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def clean_cdd_desc(desc: str) -> str:
    d = " ".join((desc or "").split())
    d = re.sub(r"\s*;\s*(Reviewed|Validated|Provisional)\s*\.?$", "", d, flags=re.I)
    d = d.rstrip(" .")
    return "" if d.upper() in ("N/A", "NA", "") else d


def set_label(text: str, new: str) -> str:
    return re.sub(r"^label:.*$", f"label: {yaml_escape(new)}", text, count=1, flags=re.M)


def set_definition(text: str, new_def: str) -> str:
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("definition:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                j += 1
            block = ["definition: >-", "  " + " ".join(new_def.split())]
            return "\n".join(lines[:i] + block + lines[j:])
    return text


def drop_synonym(text: str, syn: str) -> str:
    """Remove a synonym entry whose text == syn (now redundant with the label),
    and the `synonyms:` header if no entries remain."""
    for form in (yaml_escape(syn), syn):
        text = re.sub(rf"^  - synonym_text: {re.escape(form)}\s*\n    synonym_type:.*\n    source:.*\n",
                      "", text, flags=re.M)
    return re.sub(r"^synonyms:\n(?=\S)", "", text, flags=re.M)


def add_synonym(text: str, syn: str, source: str) -> str:
    if not syn or re.search(rf"^\s*- synonym_text: {re.escape(yaml_escape(syn))}\s*$", text, re.M):
        return text
    entry = [f"  - synonym_text: {yaml_escape(syn)}",
             "    synonym_type: EXACT_SYNONYM", f"    source: {source}"]
    if re.search(r"^synonyms:\s*$", text, re.M):
        return re.sub(r"^synonyms:\s*$", "synonyms:\n" + "\n".join(entry), text, count=1, flags=re.M)
    block = "synonyms:\n" + "\n".join(entry) + "\n"
    if re.search(r"^license:", text, re.M):
        return re.sub(r"^license:", block + "license:", text, count=1, flags=re.M)
    return text.rstrip("\n") + "\n" + block


def load_cddid() -> dict[str, tuple[str, str]]:
    out = {}
    with gzip.open(CDDID, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) >= 4:
                out[c[1]] = (c[2].strip(), c[3].strip())   # acc -> (short, desc)
    return out


def load_ncbifam() -> dict[str, tuple[str, str, str]]:
    out = {}
    lines = NCBIFAM.read_text(encoding="utf-8", errors="replace").splitlines()
    hdr = {c: i for i, c in enumerate(lines[0].lstrip("#").split("\t"))}
    def col(cols, k): return cols[hdr[k]].strip() if k in hdr and hdr[k] < len(cols) else ""
    for line in lines[1:]:
        cols = line.split("\t")
        acc = col(cols, "ncbi_accession").split(".")[0]
        src = col(cols, "source_identifier").split(".")[0]
        rec = (col(cols, "product_name"), col(cols, "label"), col(cols, "gene_symbol"))
        for a in (acc, src):
            if a:
                out[a] = rec
    return out


def enrich_cdd(text: str, short: str, desc: str) -> tuple[str, bool]:
    acc = ID_RE.search(text).group(1).split(":", 1)[1]
    cat_m = re.search(r"^trait_category:\s*(\S+)", text, re.M)
    cat = cat_m.group(1) if cat_m else ""
    desc_c = clean_cdd_desc(desc)
    opaque = (not short) or short == acc
    label = (desc_c or acc) if opaque else short
    definition = desc_c or f"NCBI CDD {KIND.get(cat, 'model')} ({acc})."
    new = set_definition(set_label(text, label), definition)
    new = drop_synonym(new, label)          # short synonym now == label
    return new, new != text


def enrich_ncbifam(text: str, product: str, model: str, gene: str) -> tuple[str, bool]:
    label = product or model
    if not label:
        return text, False
    new = set_label(text, label)
    for syn in (model, gene):
        if syn and syn != label:
            new = add_synonym(new, syn, "NCBIfam")
    return new, new != text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--source", choices=["cdd", "ncbifam", "both"], default="both")
    args = ap.parse_args()

    counts = {"cdd": 0, "ncbifam": 0}
    if args.source in ("cdd", "both"):
        cddid = load_cddid()
        for path in TRAITS.rglob("*.yaml"):
            if "/cdd/" not in str(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            m = ID_RE.search(text)
            if not m or not m.group(1).startswith("CDD:"):
                continue
            acc = m.group(1).split(":", 1)[1]
            if acc not in cddid:
                continue
            new, changed = enrich_cdd(text, *cddid[acc])
            if changed:
                counts["cdd"] += 1
                if args.apply:
                    path.write_text(new, encoding="utf-8")
    if args.source in ("ncbifam", "both"):
        ncbi = load_ncbifam()
        for path in TRAITS.rglob("*.yaml"):
            if "/ncbifam/" not in str(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            m = ID_RE.search(text)
            if not m or not m.group(1).startswith("NCBIfam:"):
                continue
            acc = m.group(1).split(":", 1)[1]
            if acc not in ncbi:
                continue
            new, changed = enrich_ncbifam(text, *ncbi[acc])
            if changed:
                counts["ncbifam"] += 1
                if args.apply:
                    path.write_text(new, encoding="utf-8")

    verb = "updated" if args.apply else "would update"
    print(f"{verb}: CDD {counts['cdd']:,}, NCBIfam {counts['ncbifam']:,}"
          + ("" if args.apply else "  (dry-run; pass --apply)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
