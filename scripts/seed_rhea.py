#!/usr/bin/env python3
"""Seed enzymatic-reaction traits from Rhea (CC-BY 4.0)
→ FUNCTION / FUNC_ENZYMATIC_ACTIVITY.

Rhea is the reference set of curated biochemical reactions (the reactions
behind EC classes). We seed each **master** (undirected) reaction as a
specific enzymatic-activity trait; directional variants (LR/RL/BI) are
skipped as redundant. The equation text is the label, and the reaction's
EC number(s) — asserted via the rhea2ec mapping — go in `mapped_xrefs` with
provenance.

The reaction's ChEBI participants are deliberately NOT written here: reaction
participants are not equivalences and belong in a dedicated chemistry model,
decided by the chemistry deep-research work. They are retained in the raw
export and added during ChEBI enrichment.

Input (fetch via `just fetch-rhea`, gitignored):
  data/raw/rhea/rhea-reactions.tsv
    "Reaction identifier<TAB>Equation<TAB>ChEBI identifier<TAB>EC number"
    (Rhea REST export; columns rhea-id,equation,chebi-id,ec)

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "rhea" / "rhea-reactions.tsv"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "enzymatic_activity" / "rhea"
LICENSE = "CC-BY 4.0"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(t): return (_SLUG_RE.sub("-", t.lower()).strip("-")[:70]) or "rhea"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'') | {"=", "+"}
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text): return [">-", f"  {' '.join((text or '').split())}"]


def build_yaml(rid, equation, ecs):
    definition = (f"Enzymatic reaction ({rid}): {equation}. A specific curated "
                  f"biochemical reaction; a protein with this activity catalyses it.")
    lines = [f"identifier: {rid}", f"label: {yaml_escape(equation)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: Rhea", "trait_axis: FUNCTION",
              "trait_category: FUNC_ENZYMATIC_ACTIVITY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if ecs:
        lines.append("mapped_xrefs:")
        for ec in ecs:
            lines.append(f"  - object: {ec}")
            lines.append("    mapping_source: rhea2ec")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/rhea/rhea-reactions.tsv; run `just fetch-rhea`",
              file=sys.stderr)
        return 2

    written = skipped = total = with_ec = 0
    for i, line in enumerate(RAW.read_text(encoding="utf-8", errors="replace").splitlines()):
        if i == 0 or not line.strip():
            continue  # header
        cols = line.split("\t")
        if len(cols) < 2 or not cols[0].startswith("RHEA:"):
            continue
        rid = cols[0].strip()
        equation = cols[1].strip()
        ec_field = cols[3].strip() if len(cols) > 3 else ""
        ecs = [e.strip() for e in ec_field.split(";") if e.strip().startswith("EC:")]
        if not equation:
            continue
        total += 1
        if ecs:
            with_ec += 1
        num = rid.split(":")[1]
        path = OUT_DIR / f"{slugify(equation)}-rhea{num}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(rid, equation, ecs), encoding="utf-8")
            written += 1

    print(f"{total} Rhea master reactions → FUNC_ENZYMATIC_ACTIVITY "
          f"({with_ec} with EC via rhea2ec).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {total - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
