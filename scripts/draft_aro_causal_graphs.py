#!/usr/bin/env python3
"""Auto-DRAFT determinant→mechanism→phenotype causal graphs for ARO resistance
records, from the CARD relations already enriched onto them
(`enrich_aro_resistance.py`).

Round-4 enrichment put each gene's mechanism (`RO:0000056` participates_in) and
drug classes (`biolink:related_to` confers_resistance_to_drug_class) into
`trait_relations`. That is enough to *scaffold* a causal graph without per-gene
research: determinant —participates in→ mechanism —causally upstream of→
resistance-to-drug-class. This writes that scaffold as a `causal_graphs` block.

These are **DRAFTS**, and are treated as such:
  • `mapping_status` is LEFT UNCHANGED (SEEDED) — a draft is not a REVIEWED graph;
  • each edge carries an `EvidenceItem` whose `reference` is the record's own
    citation (or the ARO CURIE) but **no `snippet`** — the `notes` say the edge is
    auto-drafted from an ARO relationship and a curator must add a verbatim quote
    before promotion. `just audit-graphs --strict` will flag the missing snippets,
    which is exactly the "still needs curation" signal.
Records that already carry a (hand-curated) `causal_graphs` block are skipped, so
the round-1..6 REVIEWED graphs are never touched. Idempotent; dry-run unless
--apply. Stdlib-only; reads `data/raw/aro/aro.obo` for node labels.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OBO = REPO_ROOT / "data" / "raw" / "aro" / "aro.obo"
ARO_DIR = REPO_ROOT / "data" / "traits" / "function" / "resistance" / "aro"
MAX_DRUGS = 4


def obo_names(path: Path) -> dict:
    names, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("id: "):
            cur = line[4:]
        elif line.startswith("name: ") and cur:
            names[cur] = line[6:]
            cur = None
    return names


def _yq(text: str) -> str:
    text = " ".join((text or "").split())
    if not text:
        return '""'
    if re.search(r'[:#\[\]{}",&*!|>%@`]', text) or text[:1] in "-?" or re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def parse_relations(text: str):
    """(mechanisms, drug_classes) as ARO CURIEs, from the enriched trait_relations."""
    mech, drug = [], []
    block = re.search(r"(?m)^trait_relations:\n((?:[ \t].*\n?)+)", text)
    if not block:
        return mech, drug
    items = re.split(r"(?m)^  - ", block.group(1))
    for it in items:
        pm = re.search(r"predicate:\s*(\S+)", it)
        om = re.search(r"object:\s*(\S+)", it)
        sm = re.search(r"relation_source:.*", it)
        if not (pm and om):
            continue
        pred, obj, src = pm.group(1), om.group(1), (sm.group(0) if sm else "")
        if pred == "RO:0000056" and "mechanism" in src:
            mech.append(obj)
        elif "confers_resistance_to_drug_class" in src:
            drug.append(obj)
    return mech, drug


def first_reference(text: str) -> str:
    m = re.search(r"reference:\s*(\S+)", text) or re.search(r"(PMID:\d+)", text)
    if m:
        return m.group(1)
    ident = re.search(r"^identifier:\s*(ARO:\S+)", text, re.M)
    return ident.group(1) if ident else "ARO:0000000"


def _ev(ref: str, note: str) -> list[str]:
    return ["        evidence:",
            f"          - reference: {ref}",
            f"            notes: {_yq(note)}"]


def build_graph(ident: str, label: str, mech: list, drug: list, names: dict, ref: str) -> list[str]:
    L = ["causal_graphs:",
         "  - graph_id: resistance-draft",
         "    title: " + _yq(f"[DRAFT] {label} → mechanism → resistance (auto-scaffold from ARO relations)"),
         "    description: >-",
         "      Auto-drafted from this record's enriched ARO trait_relations "
         "(participates_in mechanism + confers_resistance_to_drug_class). NOT curator-"
         "reviewed: edges cite the ARO record but carry no verbatim snippet yet. A "
         "curator should verify each edge and add quotes before flipping to REVIEWED.",
         "    nodes:",
         "      - node_id: determinant",
         f"        label: {_yq(label)}",
         "        node_type: PROTEIN",
         f"        grounding: {ident}"]
    for i, mid in enumerate(mech):
        L += [f"      - node_id: mech{i}",
              f"        label: {_yq(names.get(mid, mid))}",
              "        node_type: MOLECULAR_FUNCTION",
              f"        grounding: {mid}"]
    for i, did in enumerate(drug[:MAX_DRUGS]):
        L += [f"      - node_id: drug{i}",
              f"        label: {_yq(names.get(did, did))}",
              "        node_type: CHEMICAL",
              f"        grounding: {did}"]
    L += ["      - node_id: resistance",
          "        label: antibiotic resistance phenotype",
          "        node_type: PHENOTYPE",
          "    edges:"]
    for i, mid in enumerate(mech):
        L += [f"      - subject: determinant",
              "        predicate: participates in (resistance mechanism)",
              "        predicate_id: RO:0000056",
              f"        object: mech{i}",
              *_ev(ref, f"Auto-drafted from ARO participates_in {mid}; verbatim snippet pending curation.")]
        L += [f"      - subject: mech{i}",
              "        predicate: causally upstream of",
              "        predicate_id: RO:0002411",
              "        object: resistance",
              *_ev(ref, f"Auto-drafted: mechanism {mid} → resistance; snippet pending curation.")]
    L += ["      - subject: determinant",
          "        predicate: causally upstream of (confers resistance)",
          "        predicate_id: RO:0002411",
          "        object: resistance",
          *_ev(ref, "Auto-drafted: determinant → resistance phenotype; snippet pending curation.")]
    for i, did in enumerate(drug[:MAX_DRUGS]):
        L += [f"      - subject: resistance",
              "        predicate: related to (resistance is to)",
              f"        object: drug{i}",
              *_ev(ref, f"Auto-drafted from ARO confers_resistance_to_drug_class {did}; snippet pending curation.")]
    return L


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not OBO.exists():
        print("missing data/raw/aro/aro.obo; run `just fetch-aro`")
        return 2
    names = obo_names(OBO)

    drafted = skip_graph = skip_norel = 0
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        if "causal_graphs:" in text:
            skip_graph += 1
            continue
        mech, drug = parse_relations(text)
        if not mech:
            skip_norel += 1
            continue
        ident = re.search(r"^identifier:\s*(ARO:\S+)", text, re.M).group(1)
        label = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M).group(1)
        block = build_graph(ident, label, mech, drug, names, first_reference(text))
        lines = text.splitlines()
        lic = next((i for i, l in enumerate(lines) if l.startswith("license:")), len(lines))
        new = "\n".join(lines[:lic] + block + lines[lic:]) + "\n"
        if args.apply:
            pth.write_text(new, encoding="utf-8")
        drafted += 1
        if args.limit and drafted >= args.limit:
            break

    print(f"ARO draft graphs: {drafted:,} would be written")
    print(f"  skipped (already has a causal_graphs block): {skip_graph:,}")
    print(f"  skipped (no enriched mechanism relation): {skip_norel:,}")
    print("APPLIED." if args.apply else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
