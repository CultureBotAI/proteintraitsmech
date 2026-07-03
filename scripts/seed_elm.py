#!/usr/bin/env python3
"""Seed short-linear-motif traits from ELM (Eukaryotic Linear Motif resource)
→ SEQUENCE axis.

ELM curates ~350 motif **classes** (regex + description) in six categories.
We route them to the matching SEQ_* category:

  CLV_ (cleavage)      → SEQ_CLEAVAGE_SITE
  TRG_ (targeting)     → SEQ_TARGETING_SIGNAL   (NLS/NES/PTS/KDEL/…)
  MOD_ (modification)  → SEQ_PTM_SITE
  LIG_/DOC_/DEG_       → SEQ_MOTIF

Each class carries its regex in `sequence_pattern`.

⚠️ Licence: ELM is released for **non-commercial** use (ELM Software License) —
stamped per-record, distinct from the repo's CC0 default (as with PROSITE).

Input (fetch via `just fetch-elm`, gitignored):
  data/raw/elm/elm_classes.tsv  (elm.eu.org/elms/elms_index.tsv)
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "elm" / "elm_classes.tsv"
OUT_BASE = REPO_ROOT / "data" / "traits" / "sequence"
LICENSE = "ELM Software License (non-commercial)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")

ROUTE = {
    "CLV": ("SEQ_CLEAVAGE_SITE", "cleavage_site"),
    "TRG": ("SEQ_TARGETING_SIGNAL", "targeting_signal"),
    "MOD": ("SEQ_PTM_SITE", "ptm_site"),
    "LIG": ("SEQ_MOTIF", "motif"),
    "DOC": ("SEQ_MOTIF", "motif"),
    "DEG": ("SEQ_MOTIF", "motif"),
}


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "elm"


def yaml_escape(text) -> str:
    text = str(text)
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


def build_yaml(acc, elm_id, site_name, desc, regex, category):
    label = elm_id
    definition = f"{site_name or elm_id} — {desc}" if desc else (site_name or elm_id)
    lines = [f"identifier: ELM:{acc}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: ELM (Eukaryotic Linear Motif resource)",
              "trait_axis: SEQUENCE", f"trait_category: {category}",
              "term_kind: CLASS", "mapping_status: SEEDED"]
    if site_name and site_name != label:
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(site_name)}",
                  "    synonym_type: EXACT_SYNONYM", "    source: ELM"]
    if regex:
        lines.append(f"sequence_pattern: {yaml_escape(regex)}")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/elm/elm_classes.tsv; run `just fetch-elm`", file=sys.stderr)
        return 2

    rows = [ln for ln in RAW.read_text(encoding="utf-8", errors="replace").splitlines()
            if not ln.startswith("#")]
    reader = csv.reader(rows, delimiter="\t")
    header = next(reader)
    idx = {c: i for i, c in enumerate(header)}
    written = skipped = total = 0
    by_cat: dict[str, int] = {}
    for row in reader:
        if len(row) < len(header):
            continue

        def g(k): return row[idx[k]].strip() if k in idx else ""
        acc = g("Accession")
        elm_id = g("ELMIdentifier")
        if not acc or not elm_id:
            continue
        prefix = elm_id.split("_")[0]
        route = ROUTE.get(prefix)
        if not route:
            continue
        category, subdir = route
        by_cat[category] = by_cat.get(category, 0) + 1
        total += 1
        text = build_yaml(acc, elm_id, g("FunctionalSiteName"), g("Description"),
                          g("Regex"), category)
        path = OUT_BASE / subdir / "elm" / f"{slugify(elm_id)}-{acc.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    print(f"{total} ELM motif classes → SEQUENCE ({by_cat}).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
