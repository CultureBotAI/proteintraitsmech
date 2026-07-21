#!/usr/bin/env python3
"""Enrich ARO FUNC_RESISTANCE determinant records with CARD/ARO's inherited
drug-class + mechanism relations, so a causal-graph pass can be *transcribed*
(like M-CSA) instead of researched one gene at a time.

The seeded determinant records are thin: label, definition, one AMR-family `is_a`
parent, one PMID. CARD models the clinically useful facts on the **AMR gene family
and its `is_a` ancestors**, not the leaf gene:
  • `confers_resistance_to_drug_class` — the drug class(es) resistance is conferred
    to (e.g. GOB family → carbapenem / cephalosporin / penicillin);
  • `participates_in` — the resistance **mechanism** (e.g. β-lactamase ancestor →
    "antibiotic inactivation" ARO:0001004, "hydrolysis of β-lactam by MBL"
    ARO:3000203).
This reads `data/raw/aro/aro.obo` (fetch: `just fetch-aro`), walks each record's
`is_a` ancestry, collects those relations from self + ancestors, and appends them
as `trait_relations` on the record — nearest-ancestor provenance in
`relation_source`. Drug-class → `biolink:related_to` (ARO has no cleaner predicate;
the specific ARO relation is named in `relation_source`); mechanism →
`RO:0000056` (participates in).

Idempotent: a record that already has `trait_relations` is skipped (re-run = no-op),
so existing curation (including round-3 `causal_graphs`) is never disturbed. Only
determinants (`is_a` descendants of ARO:3000000) are touched. Dry-run unless
--apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OBO = REPO_ROOT / "data" / "raw" / "aro" / "aro.obo"
ARO_DIR = REPO_ROOT / "data" / "traits" / "function" / "resistance" / "aro"
DETERMINANT_ROOT = "ARO:3000000"


def parse_obo(path: Path) -> dict:
    terms: dict = {}
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "[Term]":
            cur = {"is_a": [], "rel": [], "name": ""}
        elif cur is None:
            continue
        elif line.startswith("id: "):
            cur["id"] = line[4:]
            terms[cur["id"]] = cur
        elif line.startswith("name: "):
            cur["name"] = line[6:]
        elif line.startswith("is_a: "):
            cur["is_a"].append(line[6:].split(" ! ")[0])
        elif line.startswith("relationship: "):
            cur["rel"].append(line[len("relationship: "):])
    return terms


def ancestry(terms: dict, tid: str) -> list[str]:
    """is_a ancestors, nearest-first (BFS), inclusive of tid."""
    order, seen, frontier = [], set(), [tid]
    while frontier:
        nxt = []
        for t in frontier:
            if t in seen or t not in terms:
                continue
            seen.add(t)
            order.append(t)
            nxt.extend(terms[t]["is_a"])
        frontier = nxt
    return order


def inherited(terms: dict, tid: str):
    """(drug_classes, mechanisms) as {object: (via_id, via_name)}, nearest ancestor
    wins (so provenance points at the closest asserting term)."""
    drug: dict = {}
    mech: dict = {}
    for a in ancestry(terms, tid):
        for r in terms[a]["rel"]:
            rel, _, rest = r.partition(" ")
            obj = rest.split(" ! ")[0].strip()
            if not obj:
                continue
            if rel == "confers_resistance_to_drug_class" and obj not in drug:
                drug[obj] = (a, terms[a]["name"])
            elif rel == "participates_in" and obj not in mech:
                mech[obj] = (a, terms[a]["name"])
    return drug, mech


def _yq(text: str) -> str:
    """Minimal YAML scalar quoting for relation_source (may contain ':' / parens)."""
    if re.search(r"[:#]", text) or text != text.strip():
        return '"' + text.replace('"', '\\"') + '"'
    return text


def relation_block(drug: dict, mech: dict) -> list[str]:
    lines = ["trait_relations:"]
    for obj, (via, vname) in sorted(mech.items()):
        lines += [f"  - predicate: RO:0000056",
                  f"    object: {obj}",
                  f"    relation_source: {_yq(f'ARO participates_in (mechanism) via {via} {vname}')}"]
    for obj, (via, vname) in sorted(drug.items()):
        lines += [f"  - predicate: biolink:related_to",
                  f"    object: {obj}",
                  f"    relation_source: {_yq(f'ARO confers_resistance_to_drug_class via {via} {vname}')}"]
    return lines


def insert_after_parents(text: str, block: list[str]) -> str:
    """Insert `block` after the parent_traits list (if present) else after
    mapping_status — preserving everything else verbatim."""
    lines = text.splitlines()
    ms = next((i for i, l in enumerate(lines) if l.startswith("mapping_status:")), None)
    if ms is None:
        return text
    at = ms + 1
    if at < len(lines) and lines[at].startswith("parent_traits:"):
        at += 1
        while at < len(lines) and (lines[at].startswith((" ", "\t")) or lines[at].startswith("- ")):
            at += 1
    out = lines[:at] + block + lines[at:]
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not OBO.exists():
        print("missing data/raw/aro/aro.obo; run `just fetch-aro`")
        return 2
    terms = parse_obo(OBO)

    written = skipped_existing = skipped_nonterm = no_rel = 0
    n = 0
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        m = re.search(r"^identifier:\s*(ARO:\S+)", text, re.M)
        if not m:
            continue
        n += 1
        tid = m.group(1)
        if re.search(r"^trait_relations:", text, re.M):
            skipped_existing += 1
            continue
        if DETERMINANT_ROOT not in ancestry(terms, tid):
            skipped_nonterm += 1
            continue
        drug, mech = inherited(terms, tid)
        if not drug and not mech:
            no_rel += 1
            continue
        new = insert_after_parents(text, relation_block(drug, mech))
        if new != text and args.apply:
            pth.write_text(new, encoding="utf-8")
        written += 1
        if args.limit and written >= args.limit:
            break

    print(f"ARO records scanned: {n:,}")
    print(f"  would enrich: {written:,}  (drug_class + mechanism → trait_relations)")
    print(f"  skipped (already has trait_relations): {skipped_existing:,}")
    print(f"  skipped (not a determinant): {skipped_nonterm:,}")
    print(f"  determinant but no inheritable relations: {no_rel:,}")
    print("APPLIED." if args.apply else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
