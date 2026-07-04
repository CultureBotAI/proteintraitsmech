#!/usr/bin/env python3
"""Seed peptidase-family traits from MEROPS (Rawlings et al., EBI)
→ SEQUENCE / SEQ_FAMILY.

MEROPS classifies proteolytic enzymes into families (S01, C14, A01, M10 …)
grouped by catalytic type (the family's leading letter) and clan. We seed the
~370 **families** — a family is a group of homologous peptidases defined by
sequence homology to a type peptidase, i.e. a sequence-signature family (axis
follows the representation), complementing SEQ_CLEAVAGE_SITE. Each family is
labelled by its type peptidase (the `.001` member).

Input (fetch via `just fetch-merops`, gitignored):
  data/raw/merops/pepunit.lib  — FASTA; headers carry
    ">MERxxxxx - <name> (<organism>) [<Sxx.yyy>]#<subfamily>#…"

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "merops" / "pepunit.lib"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "family" / "merops"
LICENSE = "MEROPS (EBI; free for academic use)"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_HDR = re.compile(r"\[([A-Z])(\d+)\.(\d+)\]#([A-Z0-9]+)#")
_NAME = re.compile(r">MER\d+ - (.+?) \(")
CATALYTIC = {
    "A": "aspartic", "C": "cysteine", "G": "glutamic", "M": "metallo",
    "N": "asparagine", "P": "mixed", "S": "serine", "T": "threonine",
    "U": "unknown-type",
}


def slugify(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "merops"


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


def build_yaml(fam, letter, type_name, n_pep):
    is_inhib = letter == "I"
    kind = "peptidase inhibitors" if is_inhib else f"{CATALYTIC.get(letter, 'unknown-type')} peptidases"
    fam_word = "peptidase-inhibitor" if is_inhib else "peptidase"
    label = f"{type_name} family" if type_name else f"{fam_word} family {fam}"
    definition = (f"MEROPS {fam_word} family {fam}"
                  + (f" (type member: {type_name})" if type_name else "")
                  + f" — a family of {kind} ({n_pep} members).")
    lines = [f"identifier: MEROPS:{fam}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: MEROPS", "trait_axis: SEQUENCE",
              "trait_category: SEQ_FAMILY", "term_kind: CLASS",
              "mapping_status: SEEDED"]
    if type_name:
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(type_name)}",
                  "    synonym_type: RELATED_SYNONYM", "    source: MEROPS"]
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if not RAW.exists():
        print("missing data/raw/merops/pepunit.lib; run `just fetch-merops`",
              file=sys.stderr)
        return 2

    fam_letter: dict[str, str] = {}
    fam_count: dict[str, int] = defaultdict(int)
    type_name: dict[str, str] = {}
    with RAW.open("r", encoding="latin-1", errors="replace") as fh:
        for line in fh:
            if not line.startswith(">"):
                continue
            m = _HDR.search(line)
            if not m:
                continue
            fam = m.group(1) + m.group(2)
            fam_letter[fam] = m.group(1)
            fam_count[fam] += 1
            if m.group(3) == "001" and fam not in type_name:
                nm = _NAME.match(line)
                if nm:
                    type_name[fam] = nm.group(1).strip()

    written = skipped = 0
    for fam in sorted(fam_letter):
        tn = type_name.get(fam, "")
        path = OUT_DIR / f"{slugify(tn or fam)}-{fam.lower()}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(fam, fam_letter[fam], tn, fam_count[fam]),
                            encoding="utf-8")
            written += 1

    print(f"{len(fam_letter)} MEROPS peptidase families → STRUCT_DOMAIN "
          f"({len(type_name)} named).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(fam_letter) - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
