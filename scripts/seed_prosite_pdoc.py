#!/usr/bin/env python3
"""Materialize PROSITE **PDOC** documentation-group records
→ SEQUENCE / SEQ_FAMILY.

PROSITE signatures carry `parent_traits: [PROSITE:PDOC…]` (the documentation
entry that groups related patterns/profiles for a family), but the PDOC nodes
themselves were never seeded — ~2.7k dangling parent edges (see
research/schema-hierarchy-review-1.md). This seeds one record per referenced
PDOC so those parents resolve. A PDOC groups the signatures of a single protein
family and is the parent of those SEQ_DOMAIN/SEQ_MOTIF signature records, so it
is a sequence-signature family — `trait_category: SEQ_FAMILY` on the SEQUENCE
axis.

Input (from `just fetch-prosite`): data/raw/prosite.dat
  entries carry `AC  PS…;`, `DE  <description>.`, `DO  PDOC…;`
Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "prosite.dat"
TRAITS = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "family" / "prosite"
LICENSE = "CC BY-NC-ND 4.0 (SIB)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_GENERIC = re.compile(r"\b(signature|profile|domain profile|pattern|domain)\b\.?$", re.I)


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "pdoc"


def yaml_escape(text) -> str:
    text = str(text)
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def parse_prosite() -> dict[str, list[str]]:
    """PDOC id → list of member-signature descriptions."""
    pdoc_des: dict[str, list[str]] = defaultdict(list)
    de = None
    pdoc = None
    for line in RAW.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("DE   "):
            de = line[5:].strip().rstrip(".")
        elif line.startswith("DO   "):
            m = re.search(r"(PDOC\d+)", line)
            if m:
                pdoc = m.group(1)
        elif line.startswith("//"):
            if pdoc and de:
                pdoc_des[pdoc].append(de)
            de = pdoc = None
    return pdoc_des


def pick_label(des: list[str]) -> str:
    """A clean family label from the member descriptions: strip the generic
    'signature'/'profile' tail, prefer the shortest distinctive form."""
    cands = []
    for d in des:
        c = _GENERIC.sub("", d).strip(" .")
        # drop trailing enumerations like "1", "2", "type-1"
        c = re.sub(r"[\s,]+(type[- ]?\d+|\d+)$", "", c, flags=re.I).strip()
        if c:
            cands.append(c)
    cands = cands or des
    return min(cands, key=lambda s: (len(s), s)) if cands else "PROSITE family"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/prosite.dat; run `just fetch-prosite`", file=sys.stderr)
        return 2

    pdoc_des = parse_prosite()
    # only materialize PDOCs actually referenced as a parent in the corpus
    referenced = set()
    for p in TRAITS.rglob("*.yaml"):
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.findall(r"PROSITE:(PDOC\d+)", t):
            referenced.add(m)

    written = skipped = 0
    for pdoc in sorted(referenced):
        label = pick_label(pdoc_des.get(pdoc, []))
        definition = (f"{label} — a PROSITE documentation group ({pdoc}) that "
                      f"organises the signatures (patterns/profiles) for this "
                      f"protein family.")
        lines = [f"identifier: PROSITE:{pdoc}", f"label: {yaml_escape(label)}",
                 "definition: >-", f"  {definition}",
                 "definition_source: PROSITE (documentation)",
                 "trait_axis: SEQUENCE", "trait_category: SEQ_FAMILY",
                 "term_kind: CLASS", "mapping_status: SEEDED",
                 f"license: {LICENSE}"]
        path = OUT_DIR / f"{slugify(label)}-{pdoc.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            written += 1

    print(f"{len(referenced)} referenced PROSITE PDOC groups → SEQUENCE/SEQ_FAMILY.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(referenced) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
