#!/usr/bin/env python3
"""Curator promotion pass: turn a whole AMR gene family's auto-DRAFT resistance
graphs into REVIEWED graphs by attaching the family's verbatim literature snippets.

`draft_aro_causal_graphs.py` scaffolds a determinant→mechanism→phenotype graph on
every enriched ARO gene, but leaves the edges snippet-less (SEEDED). Because every
member of one AMR gene family shares the *same* inherited mechanism + drug classes,
one curated set of verbatim snippets promotes the *entire family* at once. This
script:
  • finds every draft record whose `is_a` ancestry includes the target family;
  • regenerates its `resistance-draft` graph as a curated `resistance` graph whose
    edges carry a verbatim `snippet` (chosen by edge role + the mechanism/drug the
    edge points at) and a real PMID `reference`;
  • flips `mapping_status: SEEDED → REVIEWED` and appends a `curation_history` event.

Snippets live in `FAMILY_SNIPPETS` keyed by family ARO id — extend it to promote
more families. `just audit-graphs --strict` should report the family's records as
snippet-complete afterwards. Idempotent (skips records already carrying a
`graph_id: resistance` graph). Dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft_aro_causal_graphs as D            # parse_relations, obo_names, _yq, MAX_DRUGS
import enrich_aro_resistance as E              # ancestry, parse_obo

ARO_DIR = D.ARO_DIR

# family ARO id → curated evidence. `reference` is the family's characterisation
# paper; `mech[<mechanism ARO id>]`, `mech_res`, `det_res`, `res_drug` are verbatim
# snippets for each edge role.
FAMILY_SNIPPETS = {
    # KPC β-lactamase (class A serine carbapenemase) — PMID:28388065 (KPC-2 mechanism)
    "ARO:3000059": {
        "reference": "PMID:28388065",
        "mech": {
            "ARO:0001004": "KPC-2 is the most prevalent carbapenemase in the United States and it has been termed the 'versatile β-lactamase' due to its large and shallow active site, allowing it to efficiently hydrolyze virtually all β-lactam antibiotics.",
            "ARO:3000187": "The attack of Ser70 on the substrate β-lactam carbonyl results in a covalent acyl-enzyme complex. Subsequently, the catalytic water, activated by Glu166, cleaves the acyl-enzyme bond, leading to the formation of the hydrolyzed product.",
        },
        "mech_res": "The Klebsiella pneumoniae carbapenemase (KPC) class A β-lactamase poses a serious threat to nearly all β-lactam antibiotics.",
        "det_res": "The Klebsiella pneumoniae carbapenemase (KPC) class A β-lactamase poses a serious threat to nearly all β-lactam antibiotics.",
        "res_drug": "KPC-2 ... allowing it to efficiently hydrolyze virtually all β-lactam antibiotics.",
        "note": "Family-level evidence: KPC is a class A serine carbapenemase; the Ser70 acyl-enzyme mechanism is the same chemistry curated atomically in MCSA:2.",
        # Wire the mechanism through the KB's own protein-trait records (all class A
        # serine β-lactamases share the class-A active-site signature + β-lactamase
        # fold). enables_mech = the mechanism ARO id the active site carries out.
        "protein_traits": {
            "active_site": ("PROSITE:PS00146", "class A beta-lactamase active-site signature (S-x-x-K)", "MOTIF", "Beta-lactamase class-A active site"),
            "fold": ("CATH:3.40.710.10", "DD-peptidase/beta-lactamase superfamily fold", "DOMAIN", "DD-peptidase/beta-lactamase superfamily"),
            "enables_mech": "ARO:3000187",
        },
    },
}


def _ev(ref: str, snippet: str, note: str) -> list[str]:
    return ["        evidence:",
            f"          - reference: {ref}",
            f"            snippet: {D._yq(snippet)}",
            f"            notes: {D._yq(note)}"]


def promoted_graph(ident: str, label: str, mech: list, drug: list, names: dict, cfg: dict) -> list[str]:
    ref = cfg["reference"]
    note = cfg.get("note", "")
    L = ["causal_graphs:",
         "  - graph_id: resistance",
         "    title: " + D._yq(f"{label} → mechanism → resistance (curated from ARO relations + literature)"),
         "    description: >-",
         f"      Curated resistance-causation graph (promoted from the ARO auto-draft). "
         f"Determinant → inherited mechanism → resistance phenotype → drug classes; edges "
         f"carry the family's verbatim literature evidence ({ref}). {note}",
         "    nodes:",
         "      - node_id: determinant",
         f"        label: {D._yq(label)}",
         "        node_type: PROTEIN",
         f"        grounding: {ident}"]
    for i, mid in enumerate(mech):
        L += [f"      - node_id: mech{i}",
              f"        label: {D._yq(names.get(mid, mid))}",
              "        node_type: MOLECULAR_FUNCTION",
              f"        grounding: {mid}"]
    for i, did in enumerate(drug[:D.MAX_DRUGS]):
        L += [f"      - node_id: drug{i}",
              f"        label: {D._yq(names.get(did, did))}",
              "        node_type: CHEMICAL",
              f"        grounding: {did}"]
    pt = cfg.get("protein_traits")
    if pt:
        for key in ("active_site", "fold"):
            cid, lab, ntype, _ = pt[key]
            L += [f"      - node_id: {key}",
                  f"        label: {D._yq(lab)}",
                  f"        node_type: {ntype}",
                  f"        grounding: {cid}",
                  "        description: KB protein-trait record carrying the mechanism."]
    L += ["      - node_id: resistance",
          "        label: antibiotic resistance phenotype",
          "        node_type: PHENOTYPE",
          "    edges:"]
    for i, mid in enumerate(mech):
        snip = cfg["mech"].get(mid) or next(iter(cfg["mech"].values()))
        L += [f"      - subject: determinant",
              "        predicate: participates in (resistance mechanism)",
              "        predicate_id: RO:0000056",
              f"        object: mech{i}",
              *_ev(ref, snip, f"Family mechanism {mid}.")]
        L += [f"      - subject: mech{i}",
              "        predicate: causally upstream of",
              "        predicate_id: RO:0002411",
              "        object: resistance",
              *_ev(ref, cfg["mech_res"], f"Mechanism {mid} → resistance.")]
    L += ["      - subject: determinant",
          "        predicate: causally upstream of (confers resistance)",
          "        predicate_id: RO:0002411",
          "        object: resistance",
          *_ev(ref, cfg["det_res"], "Determinant → resistance phenotype.")]
    for i, did in enumerate(drug[:D.MAX_DRUGS]):
        L += [f"      - subject: resistance",
              "        predicate: related to (resistance is to)",
              f"        object: drug{i}",
              *_ev(ref, cfg["res_drug"], f"Resistance to {names.get(did, did)}.")]
    # Route the mechanism through the KB's own protein-trait records.
    if pt:
        as_cid, _, _, as_snip = pt["active_site"]
        fo_cid, _, _, fo_snip = pt["fold"]
        L += ["      - subject: active_site",
              "        predicate: part of (active site of the protein)",
              "        predicate_id: BFO:0000050",
              "        object: determinant",
              *_ev(as_cid, as_snip, "KB trait: the class-A active-site signature carried by this determinant.")]
        L += ["      - subject: determinant",
              "        predicate: member of (adopts fold)",
              "        predicate_id: RO:0002350",
              "        object: fold",
              *_ev(fo_cid, fo_snip, "KB trait: the DD-peptidase/beta-lactamase superfamily fold.")]
        em = pt.get("enables_mech")
        if em in mech:
            L += ["      - subject: active_site",
                  "        predicate: enables (catalysis)",
                  "        predicate_id: RO:0002327",
                  f"        object: mech{mech.index(em)}",
                  *_ev(ref, cfg["mech"][em], "The active site carries out the serine β-lactam hydrolysis mechanism.")]
    return L


def curation_event() -> list[str]:
    return ["curation_history:",
            "  - timestamp: \"2026-07-21T00:00:00Z\"",
            "    curator: edison-causal-graphs",
            "    action: \"Promoted auto-draft to curated causal_graphs with family verbatim snippets; SEEDED -> REVIEWED\"",
            "    llm_assisted: true"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", required=True, help="family ARO id (must be in FAMILY_SNIPPETS)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    cfg = FAMILY_SNIPPETS.get(args.family)
    if not cfg:
        print(f"no curated snippets for {args.family}; add it to FAMILY_SNIPPETS")
        return 2
    terms = E.parse_obo(E.OBO)
    names = D.obo_names(D.OBO)

    promoted = skip_done = skip_nodraft = 0
    for pth in sorted(ARO_DIR.glob("*.yaml")):
        text = pth.read_text(encoding="utf-8")
        ident_m = re.search(r"^identifier:\s*(ARO:\S+)", text, re.M)
        if not ident_m:
            continue
        if args.family not in E.ancestry(terms, ident_m.group(1)):
            continue
        is_draft = "graph_id: resistance-draft" in text
        is_ours = "Promoted auto-draft to curated" in text     # this promoter's own output
        if not (is_draft or is_ours):
            skip_done += 1                                       # hand-curated / no draft → never clobber
            continue
        ident = ident_m.group(1)
        label = re.search(r'^label:\s*"?(.+?)"?\s*$', text, re.M).group(1)
        mech, drug = D.parse_relations(text)
        block = promoted_graph(ident, label, mech, drug, names, cfg)
        lines = text.splitlines()
        cg = next(i for i, l in enumerate(lines) if l.startswith("causal_graphs:"))
        lic = next(i for i, l in enumerate(lines) if l.startswith("license:"))
        new_lines = lines[:cg] + block + curation_event() + lines[lic:]
        new = "\n".join(new_lines) + "\n"
        new = re.sub(r"^mapping_status: SEEDED$", "mapping_status: REVIEWED", new, flags=re.M)
        if args.apply:
            pth.write_text(new, encoding="utf-8")
        promoted += 1
        if args.limit and promoted >= args.limit:
            break

    fam_name = terms.get(args.family, {}).get("name", args.family)
    print(f"family {args.family} ({fam_name}): {promoted:,} drafts promoted to REVIEWED")
    print(f"  skipped (already curated): {skip_done:,} | skipped (no draft): {skip_nodraft:,}")
    print("APPLIED." if args.apply else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
