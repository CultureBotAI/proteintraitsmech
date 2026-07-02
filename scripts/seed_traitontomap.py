#!/usr/bin/env python3
"""Seed enzymatic-activity traits from the ENIGMA trait-onto-map catalog.

trait-onto-map (github.com/enigma-org/trait-onto-map, MIT) is a large catalogue
of traits parsed from genome-annotation tools (DRAM, GapMind, GTDB-Tk, RGI,
antiSMASH, CheckM, Bakta, VirSorter2, MicroTraits, …). Most of its ~740k rows
are per-genome, gene-level, or off-axis (mobile elements, viral, QC) and are NOT
protein sequence/structure traits.

This seeder ingests only the clean, protein-level, definable subset: **enzyme
activities identified by an EC number**. Rows whose `ontology_ids` contain a
complete EC number are grouped by that EC into one FUNC_ENZYMATIC_ACTIVITY
record — EC-anchored so it is groundable and mergeable, additive to (not
redundant with) the InterPro domains. Distinct catalogue names for the same EC
become synonyms; KEGG orthologs (K#####) become xrefs.

Pfam domains from the catalogue are deliberately skipped — they are already
covered by InterPro.

Input: data/raw/traitontomap/trait_catalog.tsv (copy via `just fetch-traitontomap`).
Each record: identifier EC:<ec>, FUNCTION / FUNC_ENZYMATIC_ACTIVITY, under
data/traits/function/enzymatic_activity/traitontomap/. Idempotent; dry-run
unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG = REPO_ROOT / "data" / "raw" / "traitontomap" / "trait_catalog.tsv"
EC2GO = REPO_ROOT / "data" / "raw" / "mappings" / "ec2go"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "enzymatic_activity" / "traitontomap"

LICENSE = "MIT (ENIGMA trait-onto-map)"
DEFINITION_SOURCE = "ENIGMA trait-onto-map (EC-grounded enzyme activities)"

_EC_RE = re.compile(r"\b(\d+\.\d+\.\d+\.\d+)\b")
_KEGG_RE = re.compile(r"\b(K\d{5})\b")
_EC_SUFFIX_RE = re.compile(r"\s*\(EC\s*\d+\.\d+\.\d+\.\d+\)\s*$", re.I)
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_GENERIC = ("domain-containing protein", "family protein", "unknown",
            "hypothetical", "uncharacterized")


def clean_name(name: str) -> str:
    return _EC_SUFFIX_RE.sub("", (name or "").strip()).strip()


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:70]) or "ec"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    text = " ".join((text or "").split())
    return [">-", f"  {text}"]


def load_ec_groups() -> dict[str, dict]:
    """EC -> {names:set, kegg:set}."""
    groups: dict[str, dict] = defaultdict(lambda: {"names": set(), "kegg": set()})
    with CATALOG.open(encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            onto = row.get("ontology_ids", "") or ""
            m = _EC_RE.search(onto)
            if not m:
                continue
            ec = m.group(1)
            name = clean_name(row.get("canonical_name", ""))
            if name:
                groups[ec]["names"].add(name)
            for k in _KEGG_RE.findall(onto):
                groups[ec]["kegg"].add(k)
    return groups


_EC2GO_RE = re.compile(r"^EC:(\d+\.\d+\.\d+\.\d+)\b.*;\s*(GO:\d{7})\s*$")


def load_ec2go() -> dict[str, list[str]]:
    """Complete EC -> [GO CURIEs], from the GO ec2go mapping (if present)."""
    out: dict[str, list[str]] = defaultdict(list)
    if not EC2GO.exists():
        return out
    for line in EC2GO.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _EC2GO_RE.match(line)
        if m and m.group(2) not in out[m.group(1)]:
            out[m.group(1)].append(m.group(2))
    return out


def pick_label(names: set[str]) -> str:
    """Prefer a specific, non-generic, letter-initial name; shortest wins."""
    cands = [n for n in names if n and not any(g in n.lower() for g in _GENERIC)]
    cands = cands or list(names)
    cands.sort(key=lambda n: (0 if n[:1].isalpha() else 1, len(n), n))
    return cands[0]


def build_yaml(ec: str, names: set[str], kegg: set[str], go: list[str]) -> str:
    label = pick_label(names)
    definition = (f"Enzymatic activity — {label} (EC {ec}); a catalogued "
                  f"enzyme function grounded to its Enzyme Commission number.")
    synonyms = sorted(n for n in names if n != label)
    lines = [f"identifier: EC:{ec}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines.append(f"definition: {f[0]}")
    lines.extend(f[1:])
    lines.append(f"definition_source: {yaml_escape(DEFINITION_SOURCE)}")
    lines.append("trait_axis: FUNCTION")
    lines.append("trait_category: FUNC_ENZYMATIC_ACTIVITY")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")
    xrefs = list(go) + [f"KEGG:{k}" for k in sorted(kegg)]
    if xrefs:
        lines.append("xrefs:")
        lines.extend(f"  - {x}" for x in xrefs)
    if synonyms:
        lines.append("synonyms:")
        for s in synonyms:
            lines.append(f"  - synonym_text: {yaml_escape(s)}")
            lines.append("    synonym_type: EXACT_SYNONYM")
    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not CATALOG.exists():
        print(f"missing {CATALOG.relative_to(REPO_ROOT)}; run `just fetch-traitontomap`",
              file=sys.stderr)
        return 2

    groups = load_ec_groups()
    ec2go = load_ec2go()
    written = skipped = with_go = 0
    for ec, data in sorted(groups.items()):
        label = pick_label(data["names"])
        go = ec2go.get(ec, [])
        if go:
            with_go += 1
        path = OUT_DIR / f"{slugify(label)}-ec{ec.replace('.', '-')}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(ec, data["names"], data["kegg"], go), encoding="utf-8")
            written += 1

    print(f"{len(groups)} EC-grounded enzyme activities from the catalog "
          f"({with_go} GO-grounded via ec2go).")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → {OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {len(groups) - skipped}; {skipped} exist. Re-run with --apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
