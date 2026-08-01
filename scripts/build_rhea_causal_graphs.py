#!/usr/bin/env python3
"""Write reaction-chemistry causal graphs onto the Rhea `FUNC_ENZYMATIC_ACTIVITY` records.

  python3 scripts/build_rhea_causal_graphs.py --limit 3   # dry run, prints YAML
  python3 scripts/build_rhea_causal_graphs.py --apply

18,558 Rhea records carry a curated reaction and none carried a causal graph. The
mechanism here is neither a catalytic step sequence (M-CSA) nor an interaction
(BioLiP/MetalPDB) but a **transformation**: these substrates become those products.

WHERE THE DIRECTION COMES FROM
------------------------------
A Rhea *master* reaction is deliberately undirected — `pentanamide + H2O =
pentanoate + NH4(+)` — which is why the seeder could only write
`role: SUBSTRATE_OR_PRODUCT` on every participant. Calling the left side
"substrates" would therefore be our claim, not Rhea's.

Rhea does make that claim, just on a different entity: each master has a
left-to-right **directional child** whose RDF says `rh:substrates → <id>_L` and
`rh:products → <id>_R`. Every input/output edge below is cited to that child, and
the graph description says the master is undirected. Nothing asserts that the
reverse direction does not occur — Rhea curates an RL child too.

WHAT IS CITED
-------------
The snippet is Rhea's own text for the claim, from `data/raw/rhea/rhea.rdf.gz`:
the directional child's `rh:equation` for input/output edges, the reactive part's
`rh:name` for residue edges, and the verbatim cross-reference triple for the GO and
EC edges. The record's own `definition` is never quoted — our seeder wrote it, so
it is not evidence for our own claim (the rule established in round 15).

Rhea's `rh:citation` PMIDs travel in the edge `notes` on the standing rule that a
PMID becomes a `reference` only when someone has read the paper.

VERIFIED WITHOUT THE NETWORK
----------------------------
Rhea states each reaction twice — once as the `rh:equation` string and once as the
`rh:side`/`rh:contains<N>`/`rh:location` participant structure. Re-rendering the
structure must reproduce the equation character for character (coefficient, order,
transport side and all) or the record is skipped. All 18,558 seeded reactions pass,
so no side assignment written below is a guess.

PROTEIN EXEMPLARS, ONLY WHERE THE INFERENCE IS SOUND
----------------------------------------------------
`prot enables activity` edges come from ExPASy ENZYME's `DR` lines via Rhea's
`rh:ec`. An EC class that maps to several Rhea reactions does not tell us which one
a given protein runs, so those edges are written **only for the 5,098 records whose
EC class maps to exactly one Rhea master reaction**.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

from record_io import append_to_section, has_graph, insert_before_license

import rhea_rdf

REPO = Path(__file__).resolve().parent.parent
TRAITS = REPO / "data" / "traits"
ROOT = TRAITS / "function" / "enzymatic_activity" / "rhea"
GO_OBO = REPO / "data" / "raw" / "go.obo"
ENZYME = REPO / "data" / "raw" / "ec" / "enzyme.dat"

P_HAS_INPUT = ("has input", "RO:0002233")
P_HAS_OUTPUT = ("has output", "RO:0002234")
P_PART_OF = ("part of", "BFO:0000050")
P_ENABLES = ("enables", "RO:0002327")
P_CLOSE = ("is cross-referenced to the equivalent GO molecular function",
           "skos:closeMatch")
P_BROAD = ("is a curated reaction of the broader EC class", "skos:broadMatch")

MAX_LABEL = 90
MAX_PROTEINS = 3
# Rhea renders a coefficient of 1 as nothing and the polymerisation variables in
# parentheses; this table is what makes the equation round-trip check exact.
COEF_TEXT = {"1": "", "N": "n", "2n": "2n", "Nplus1": "(n+1)", "Nminus1": "(n-1)"}
TIMESTAMP = "2026-07-30T00:00:00Z"


def kb_identifiers() -> set[str]:
    """Every record identifier in the corpus, so a node is only ever grounded to a
    CURIE that actually resolves to a trait record."""
    out = set()
    for f in TRAITS.rglob("*.yaml"):
        with f.open(encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("identifier:"):
                    out.add(line.split(":", 1)[1].strip())
                    break
    return out


def go_labels() -> dict[str, str]:
    out, cur = {}, None
    if not GO_OBO.exists():
        return out
    for line in GO_OBO.open(encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("id: GO:"):
            cur = line[4:].strip()
        elif line.startswith("name: ") and cur:
            out[cur] = line[6:].strip()
            cur = None
    return out


def enzyme_entries() -> dict[str, dict]:
    """EC number -> {name, dr: [(accession, entry_name, verbatim DR line)]}."""
    out: dict[str, dict] = {}
    if not ENZYME.exists():
        return out
    for block in ENZYME.read_text(encoding="utf-8", errors="replace").split("\n//\n"):
        m = re.search(r"^ID   (\S+)", block, re.M)
        if not m:
            continue
        # ExPASy wraps a long enzyme name across several DE lines, so reading only
        # the first truncates 133 active entries — and not harmlessly: EC:1.3.1.67
        # would come out as "cis-1,2-dihydroxy-4-methylcyclohexa-3,5-diene-1-
        # carboxylate", a substrate standing in for the activity, and 1.1.1.170 /
        # 1.1.1.418 would silently lose the "(decarboxylating)" that tells them apart.
        de = re.findall(r"^DE   (.+)$", block, re.M)
        name = " ".join(x.strip() for x in de).rstrip(".")
        if name.startswith(("Deleted", "Transferred")):
            continue
        dr = []
        for line in re.findall(r"^DR   .+$", block, re.M):
            for acc, ent in re.findall(r"(\w+),\s*(\w+)\s*;", line):
                dr.append((acc, ent, line))
        ca = " ".join(x.strip() for x in re.findall(r"^CA   (.+)$", block, re.M))
        out[m.group(1)] = {"name": name, "dr": dr, "ca": ca}
    return out


def render_side(rh: rhea_rdf.Rhea, side_id: str) -> str:
    """Rebuild Rhea's own equation text for one side from the participant structure."""
    toks = []
    for comp, coef, part in rh.participants_of(side_id):
        name = comp["name"]
        loc = part.get("location")
        if loc:
            name += f"({loc.lower()})"
        toks.append(f"{COEF_TEXT.get(coef, coef)} {name}".strip())
    return " + ".join(toks)


def short(text: str, limit: int = MAX_LABEL) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def build(rid: str, rxn: dict, rh: rhea_rdf.Rhea, kb: set[str],
          go_lab: dict, ecdb: dict, ec_single: dict[str, str]):
    acc = f"RHEA:{rid}"
    if len(rxn["sides"]) != 2:
        return None, "reaction does not have two sides"
    left, right = rxn["sides"]
    # The equation must round-trip from the participant structure, or the sides we
    # are about to call substrates and products are not the ones Rhea describes.
    if f"{render_side(rh, left)} = {render_side(rh, right)}" != rxn["equation"]:
        return None, "equation did not round-trip from participants"
    lr = rh.lr_child(rxn)
    if not lr:
        return None, "no left-to-right directional child"
    lr_acc, lr_eq = lr["accession"], lr["equation"]

    pmid_note = ""
    if rxn["pmids"]:
        pmid_note = (" Rhea cites "
                     + ", ".join(f"PMID:{p}" for p in rxn["pmids"][:4])
                     + " for this reaction.")

    nodes = [{
        "node_id": "activity",
        "label": short(f"catalysis of {rxn['equation']}"),
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": acc,
        "description": ("KB trait record (FUNC_ENZYMATIC_ACTIVITY) — the enzymatic "
                        "activity this graph explains. Full equation: "
                        + rxn["equation"]),
    }]
    edges = []
    ungrounded = 0

    def chem_nodes(side_id: str, prefix: str, predicate, ref_side: str):
        nonlocal ungrounded
        for i, (comp, coef, part) in enumerate(rh.participants_of(side_id), 1):
            nid = f"{prefix}{i}"
            loc = part.get("location")
            label = comp["name"]
            if loc:
                label += f" ({'outside' if loc == 'Out' else 'inside'} the membrane)"
            node = {
                "node_id": nid,
                "label": short(label),
                "node_type": rhea_rdf.KIND_TO_NODE_TYPE.get(comp.get("kind"), "CHEMICAL"),
            }
            # A generic participant such as `[protein]-dithiol` has no ChEBI of its
            # own — Rhea identifies it by its own accession (`GENERIC:10594`), for
            # which the identifier UniProt and bioregistry use is `RHEA-COMP:10594`.
            # Falling back to it keeps the node identified rather than label-only,
            # the same choice round 15 made for PDB chemical components; Rhea's own
            # spelling is kept in the node description.
            comp_curie = (f"RHEA-COMP:{comp['accession'].split(':', 1)[1]}"
                          if comp["accession"].startswith(("GENERIC:", "POLYMER:"))
                          else "")
            if comp.get("chebi"):
                node["grounding"] = comp["chebi"]
                if comp_curie:
                    node["xrefs"] = [comp_curie]
            elif comp_curie:
                node["grounding"] = comp_curie
            else:
                ungrounded += 1
            desc = []
            if comp["accession"].startswith(("GENERIC:", "POLYMER:")):
                desc.append(f"Rhea compound {comp['accession']}.")
            if len(comp["name"]) > MAX_LABEL:
                desc.append(f"Full Rhea name: {comp['name']}")
            if comp.get("formula"):
                desc.append(f"Formula {comp['formula']}.")
            if comp.get("polymer_index"):
                desc.append(f"Polymerisation index {comp['polymer_index']}.")
            if desc:
                node["description"] = " ".join(desc)
            nodes.append(node)

            stoich = COEF_TEXT.get(coef, coef) or "1"
            where = (f" It is transported, and appears on the "
                     f"{'outside' if loc == 'Out' else 'inside'} of the membrane."
                     if loc else "")
            edges.append({
                "subject": "activity",
                "predicate": predicate[0],
                "predicate_id": predicate[1],
                "object": nid,
                "description": (f"{comp['name']} is a "
                                f"{'substrate consumed by' if prefix == 'sub' else 'product released by'}"
                                f" this reaction (stoichiometric coefficient {stoich})."),
                "evidence": [{
                    "reference": lr_acc,
                    "snippet": lr_eq,
                    "notes": (f"Rhea's left-to-right directional reaction {lr_acc} "
                              f"declares side {ref_side} as its "
                              f"{'substrates (rh:substrates)' if prefix == 'sub' else 'products (rh:products)'}; "
                              f"the master reaction {acc} is undirected. This "
                              f"participant is {comp['accession']} with coefficient "
                              f"{stoich}.{where}{pmid_note}"),
                }],
            })

            # A `[protein]-…` participant is a protein trait, not a metabolite:
            # Rhea names the amino-acid residue that actually reacts.
            for k, rp in enumerate(rh.reactive_parts(comp), 1):
                rp_id = f"{nid}_rp{k}"
                pos = rp.get("position")
                rp_node = {
                    "node_id": rp_id,
                    "label": (f"{rp.get('name', 'reactive part')}"
                              + (f" at position {pos}" if pos else "")),
                    "node_type": "RESIDUE",
                    "description": ("The reacting group Rhea names inside the generic "
                                    f"participant {comp['accession']} "
                                    f"({comp['name']}); no position on any specific "
                                    "protein sequence is asserted."),
                }
                if rp.get("chebi"):
                    rp_node["grounding"] = rp["chebi"]
                else:
                    ungrounded += 1
                nodes.append(rp_node)
                edges.append({
                    "subject": rp_id,
                    "predicate": P_PART_OF[0],
                    "predicate_id": P_PART_OF[1],
                    "object": nid,
                    "description": (f"{rp.get('name')} is the reactive part of "
                                    f"{comp['name']}."),
                    "evidence": [{
                        "reference": acc,
                        "snippet": rp.get("name", ""),
                        "notes": (f"Rhea compound {comp['accession']} ({comp['name']}) "
                                  f"declares rh:reactivePart "
                                  + (f"at position {pos} " if pos else "")
                                  + f"= {rp.get('name')}"
                                  + (f" ({rp['chebi']})" if rp.get("chebi") else "")
                                  + (f", formula {rp['formula']}" if rp.get("formula") else "")
                                  + "."),
                    }],
                })

    chem_nodes(left, "sub", P_HAS_INPUT, left)
    chem_nodes(right, "prd", P_HAS_OUTPUT, right)

    # --- cross-reference edges into the KB's other FUNCTION trait records
    for go in rxn["go"]:
        if go not in kb:
            continue
        nodes.append({"node_id": "go", "node_type": "MOLECULAR_FUNCTION",
                      "label": go_lab.get(go, go), "grounding": go,
                      "description": "KB trait record (FUNC_MOLECULAR_FUNCTION)."})
        edges.append({
            "subject": "activity", "predicate": P_CLOSE[0], "predicate_id": P_CLOSE[1],
            "object": "go",
            "description": ("Rhea cross-references this reaction to the GO molecular "
                            "function that describes the same catalysis."),
            "evidence": [{
                "reference": acc,
                "snippet": f'<rdfs:seeAlso rdf:resource="http://purl.obolibrary.org/obo/{go.replace(":", "_")}"/>',
                "notes": (f"The rdfs:seeAlso triple on {acc} in rhea.rdf. GO term "
                          f"{go} is itself a record in this KB."),
            }],
        })
        break

    ec_nodes = []
    for i, ec in enumerate(rxn["ec"], 1):
        curie = f"EC:{ec}"
        if curie not in kb:
            continue
        nid = f"ec{i}"
        ec_nodes.append((nid, ec, curie))
        nodes.append({"node_id": nid, "node_type": "MOLECULAR_FUNCTION",
                      "label": ecdb.get(ec, {}).get("name") or f"EC {ec}",
                      "grounding": curie,
                      "description": "KB trait record (FUNC_ENZYMATIC_ACTIVITY)."})
        edges.append({
            "subject": "activity", "predicate": P_BROAD[0], "predicate_id": P_BROAD[1],
            "object": nid,
            "description": (f"Rhea assigns this reaction to EC {ec}; the EC class "
                            f"covers the chemistry, this reaction is one curated "
                            f"instance of it."),
            "evidence": [{
                "reference": acc,
                "snippet": f'<rh:ec rdf:resource="http://purl.uniprot.org/enzyme/{ec}"/>',
                "notes": (f"The rh:ec triple on {acc} in rhea.rdf. EC {ec} is itself "
                          f"a record in this KB."),
            }],
        })

    # --- exemplar catalysts, only when the EC class maps to this reaction alone
    for nid, ec, curie in ec_nodes:
        if ec_single.get(ec) != rid:
            continue
        for acc_u, entry, drline in (ecdb.get(ec, {}).get("dr") or [])[:MAX_PROTEINS]:
            pid = f"prot_{acc_u}"
            nodes.append({"node_id": pid, "node_type": "PROTEIN",
                          "label": entry, "grounding": f"UniProtKB:{acc_u}"})
            edges.append({
                "subject": pid, "predicate": P_ENABLES[0],
                "predicate_id": P_ENABLES[1], "object": "activity",
                "description": (f"{entry} is an exemplar enzyme carrying EC {ec}, "
                                f"the class whose only curated Rhea reaction is this "
                                f"one, so it catalyses this reaction."),
                "evidence": [
                    {"reference": curie, "snippet": drline,
                     "notes": (f"ExPASy ENZYME entry EC {ec} cross-references "
                               f"UniProtKB:{acc_u} ({entry}) as a protein with this "
                               f"activity.")},
                    {"reference": acc,
                     "snippet": f'<rh:ec rdf:resource="http://purl.uniprot.org/enzyme/{ec}"/>',
                     "notes": (f"Rhea assigns {acc} to EC {ec}, and EC {ec} maps to "
                               f"exactly one Rhea master reaction ({acc}), so the "
                               f"enzyme's activity is this reaction. Where an EC "
                               f"class maps to several Rhea reactions no exemplar "
                               f"protein is written.")},
                ],
            })
        break

    n_sub = len(rh.sides.get(left, {}))
    n_prd = len(rh.sides.get(right, {}))
    desc = (f"Substrate-to-product chemistry of {acc}, transcribed from the Rhea RDF "
            f"release. The master reaction is undirected; the substrate/product "
            f"assignment is the one Rhea itself makes in its left-to-right "
            f"directional child {lr_acc} (rh:substrates → {left}, rh:products → "
            f"{right}), and Rhea curates the reverse direction too. "
            f"{n_sub} substrate{'s' if n_sub != 1 else ''}, "
            f"{n_prd} product{'s' if n_prd != 1 else ''}. "
            f"{'Chemically balanced. ' if rxn['balanced'] else ''}"
            f"{'A transport reaction: a participant crosses a membrane, and Rhea gives its side (in/out) but not the membrane. ' if rxn['transport'] else ''}"
            f"Participant structure was checked by re-rendering Rhea's own equation "
            f"string from it.")

    return {"graph_id": "reaction_chemistry",
            "title": short(f"Reaction chemistry of {rxn['equation']}", 110),
            "description": desc, "nodes": nodes, "edges": edges}, ungrounded


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("parsing Rhea RDF + KB identifiers…", file=sys.stderr)
    rh = rhea_rdf.load()
    kb = kb_identifiers()
    go_lab, ecdb = go_labels(), enzyme_entries()

    ec2rhea = collections.defaultdict(set)
    for rid, rxn in rh.reactions.items():
        if f"RHEA:{rid}" in kb:
            for ec in rxn["ec"]:
                ec2rhea[ec].add(rid)
    ec_single = {ec: next(iter(v)) for ec, v in ec2rhea.items() if len(v) == 1}
    print(f"  {len(rh.reactions):,} master reactions · {len(kb):,} KB records · "
          f"{len(ec_single):,} EC classes with a single Rhea reaction", file=sys.stderr)

    stat = collections.Counter()
    done = 0
    for f in sorted(ROOT.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        # Skip on THIS builder's graph_id, not on the presence of any graph at all.
        # A record that gained a `catalytic_residues_*` graph first would otherwise be
        # permanently skipped here and never get its reaction chemistry.
        if has_graph(text, "reaction_chemistry"):
            stat["already has a graph"] += 1
            continue
        m = re.search(r"^identifier:\s*RHEA:(\d+)\s*$", text, re.M)
        if not m:
            stat["skipped: no RHEA identifier"] += 1
            continue
        rxn = rh.reactions.get(m.group(1))
        if not rxn:
            stat["skipped: not in the RDF release"] += 1
            continue
        graph, info = build(m.group(1), rxn, rh, kb, go_lab, ecdb, ec_single)
        if graph is None:
            stat[f"skipped: {info}"] += 1
            continue
        stat["written"] += 1
        stat["nodes"] += len(graph["nodes"])
        stat["edges"] += len(graph["edges"])
        stat["ungrounded nodes"] += info

        block = yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                               allow_unicode=True, width=100,
                               default_flow_style=False)
        hist = yaml.safe_dump({"curation_history": [{
            "timestamp": TIMESTAMP,
            "curator": "edison-causal-graphs",
            "action": (f"Added causal_graphs 'reaction_chemistry' "
                       f"({len(graph['edges'])} evidence-backed edges) from the Rhea "
                       f"RDF release; SEEDED -> REVIEWED"),
            "llm_assisted": True}]}, sort_keys=False, allow_unicode=True, width=100)
        out = re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED",
                     text, count=1, flags=re.M)
        if re.search(r"^license:", out, re.M):
            # lambda, not a replacement string: a literal template would interpret
            # any backslash or \g in the spliced YAML. No Rhea/ENZYME release has
            # one today, which is exactly why this would surface as corruption long
            # after the change that introduced it.
            out = insert_before_license(out, block + hist)
        else:
            out = out.rstrip("\n") + "\n" + block + hist
        if args.apply:
            f.write_text(out, encoding="utf-8")
        elif done == 0:
            print(out)
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.most_common():
        print(f"  {k:<38} {v:>8,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
