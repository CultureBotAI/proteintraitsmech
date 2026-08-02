#!/usr/bin/env python3
"""Write reaction-chemistry causal graphs onto the EC `FUNC_ENZYMATIC_ACTIVITY` records.

  python3 scripts/build_ec_causal_graphs.py --limit 3   # dry run, prints YAML
  python3 scripts/build_ec_causal_graphs.py --apply

Companion to `build_rhea_causal_graphs.py`. The 7,375 EC records are the other half
of the corpus's reaction chemistry: where a Rhea record is one curated reaction, an
EC record is the *class* of enzymes that run it.

WHERE THE CHEMISTRY COMES FROM
------------------------------
ExPASy ENZYME's own `CA` line is free text (`RH + Br(-) + H2O2 = RBr + 2 H2O`) with
no ChEBI behind it, so parsing it into participants would be our reading, not the
source's. Rhea, which curates the same reactions with ChEBI participants, is used
instead, via Rhea's `rh:ec` assignment. The `CA` line is quoted in the graph
description so the two can be compared, but it is never the basis of an edge.

WHERE THE EDGES ARE ANCHORED, AND WHY IT DEPENDS ON THE MAPPING
---------------------------------------------------------------
An EC class that maps to **exactly one** Rhea master reaction has that reaction as
its chemistry, so `has input` / `has output` hang directly off the EC activity node.

An EC class that maps to **several** Rhea reactions does not: no single substrate
set is "the" chemistry of the class. There the graph adds one node per Rhea reaction
— each grounded to the Rhea record that already exists in this KB — and hangs that
reaction's inputs and outputs off it, with a `skos:narrowMatch` edge from the EC
class. The EC node never claims a substrate that only one of its reactions consumes.

WHAT IS CITED
-------------
  • input/output edges → the Rhea left-to-right directional child's `rh:equation`
    (Rhea's own statement of which side is the substrate side);
  • `enables` edges → the verbatim `DR` line of the ExPASy ENZYME entry;
  • the GO edge → the verbatim `ec2go` mapping line.
The record's own definition is never quoted: our seeder wrote it.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

from record_io import append_to_section, has_graph

import rhea_rdf
from build_rhea_causal_graphs import (COEF_TEXT, MAX_PROTEINS, P_CLOSE, P_ENABLES,
                                      P_HAS_INPUT, P_HAS_OUTPUT, P_PART_OF, TIMESTAMP,
                                      enzyme_entries, go_labels, kb_identifiers,
                                      render_side, short)

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "data" / "traits" / "function" / "enzymatic_activity" / "ec"
EC2GO = REPO / "data" / "raw" / "ec" / "ec2go"

P_NARROW = ("has as a curated reaction", "skos:narrowMatch")
MAX_REACTIONS = 3


def ec2go_lines() -> dict[str, tuple[str, str]]:
    """EC number -> (GO CURIE, the verbatim ec2go line asserting it)."""
    out = {}
    if not EC2GO.exists():
        return out
    for line in EC2GO.read_text(encoding="utf-8").splitlines():
        if line.startswith("!"):
            continue
        m = re.match(r"^EC:(\S+)\s*>\s*GO:.*;\s*(GO:\d+)\s*$", line)
        if m and m.group(1) not in out:
            out[m.group(1)] = (m.group(2), line)
    return out


def reaction_edges(rh: rhea_rdf.Rhea, rid: str, rxn: dict, host: str, prefix: str,
                   nodes: list, edges: list) -> bool:
    """Hang one Rhea reaction's participants off the node `host`. False if the
    reaction's participant structure does not re-render Rhea's own equation."""
    if len(rxn["sides"]) != 2:
        return False
    left, right = rxn["sides"]
    if f"{render_side(rh, left)} = {render_side(rh, right)}" != rxn["equation"]:
        return False
    lr = rh.lr_child(rxn)
    if not lr:
        return False
    acc, lr_acc, lr_eq = f"RHEA:{rid}", lr["accession"], lr["equation"]
    pmids = ("" if not rxn["pmids"] else
             " Rhea cites " + ", ".join(f"PMID:{p}" for p in rxn["pmids"][:4])
             + " for this reaction.")

    for side, tag, predicate in ((left, "sub", P_HAS_INPUT),
                                 (right, "prd", P_HAS_OUTPUT)):
        for i, (comp, coef, part) in enumerate(rh.participants_of(side), 1):
            nid = f"{prefix}{tag}{i}"
            loc = part.get("location")
            label = comp["name"] + (
                f" ({'outside' if loc == 'Out' else 'inside'} the membrane)" if loc else "")
            node = {"node_id": nid, "label": short(label),
                    "node_type": rhea_rdf.KIND_TO_NODE_TYPE.get(comp.get("kind"),
                                                                "CHEMICAL")}
            comp_curie = (f"RHEA-COMP:{comp['accession'].split(':', 1)[1]}"
                          if comp["accession"].startswith(("GENERIC:", "POLYMER:"))
                          else "")
            if comp.get("chebi"):
                node["grounding"] = comp["chebi"]
                if comp_curie:
                    node["xrefs"] = [comp_curie]
            elif comp_curie:
                node["grounding"] = comp_curie
            desc = []
            if comp_curie:
                desc.append(f"Rhea compound {comp['accession']}.")
            if len(comp["name"]) > 90:
                desc.append(f"Full Rhea name: {comp['name']}")
            if comp.get("formula"):
                desc.append(f"Formula {comp['formula']}.")
            if desc:
                node["description"] = " ".join(desc)
            nodes.append(node)

            stoich = COEF_TEXT.get(coef, coef) or "1"
            edges.append({
                "subject": host, "predicate": predicate[0],
                "predicate_id": predicate[1], "object": nid,
                "description": (f"{comp['name']} is a "
                                f"{'substrate consumed by' if tag == 'sub' else 'product released by'}"
                                f" {acc} (stoichiometric coefficient {stoich})."),
                "evidence": [{
                    "reference": lr_acc, "snippet": lr_eq,
                    "notes": (f"Rhea's left-to-right directional reaction {lr_acc} "
                              f"declares side {side} as its "
                              f"{'substrates (rh:substrates)' if tag == 'sub' else 'products (rh:products)'}; "
                              f"the master reaction {acc} is undirected. This "
                              f"participant is {comp['accession']} with coefficient "
                              f"{stoich}.{pmids}")}]})

            for k, rp in enumerate(rh.reactive_parts(comp), 1):
                rp_id = f"{nid}_rp{k}"
                pos = rp.get("position")
                rp_node = {"node_id": rp_id, "node_type": "RESIDUE",
                           "label": (f"{rp.get('name', 'reactive part')}"
                                     + (f" at position {pos}" if pos else "")),
                           "description": ("The reacting group Rhea names inside the "
                                           f"generic participant {comp['accession']} "
                                           f"({comp['name']}); no position on any "
                                           "specific protein sequence is asserted.")}
                if rp.get("chebi"):
                    rp_node["grounding"] = rp["chebi"]
                nodes.append(rp_node)
                edges.append({
                    "subject": rp_id, "predicate": P_PART_OF[0],
                    "predicate_id": P_PART_OF[1], "object": nid,
                    "description": (f"{rp.get('name')} is the reactive part of "
                                    f"{comp['name']}."),
                    "evidence": [{
                        "reference": acc, "snippet": rp.get("name", ""),
                        "notes": (f"Rhea compound {comp['accession']} "
                                  f"({comp['name']}) declares rh:reactivePart "
                                  + (f"at position {pos} " if pos else "")
                                  + f"= {rp.get('name')}"
                                  + (f" ({rp['chebi']})" if rp.get("chebi") else "")
                                  + ".")}]})
    return True


def build(ec: str, rh: rhea_rdf.Rhea, kb: set[str], go_lab: dict, ecdb: dict,
          e2g: dict, ec2rhea: dict):
    curie = f"EC:{ec}"
    entry = ecdb.get(ec)
    if not entry:
        return None, "not an active leaf entry in enzyme.dat"
    rxn_ids = sorted(ec2rhea.get(ec, ()), key=int)
    go_curie, go_line = e2g.get(ec, ("", ""))
    has_go = go_curie in kb
    if not rxn_ids and not entry["dr"] and not has_go:
        return None, "no Rhea reaction, no exemplar protein, no GO mapping"

    nodes = [{"node_id": "activity", "node_type": "MOLECULAR_FUNCTION",
              "label": short(entry["name"] or f"EC {ec}"), "grounding": curie,
              "description": ("KB trait record (FUNC_ENZYMATIC_ACTIVITY) — the "
                              "enzyme class this graph explains.")}]
    edges = []

    # --- chemistry
    used, single = [], len(rxn_ids) == 1
    for k, rid in enumerate(rxn_ids[:MAX_REACTIONS], 1):
        rxn = rh.reactions.get(rid)
        if not rxn:
            continue
        if single:
            if reaction_edges(rh, rid, rxn, "activity", "", nodes, edges):
                used.append(rid)
        else:
            nid = f"rxn{k}"
            if f"RHEA:{rid}" not in kb:
                continue
            probe_n, probe_e = [], []
            if not reaction_edges(rh, rid, rxn, nid, f"{nid}_", probe_n, probe_e):
                continue
            nodes.append({"node_id": nid, "node_type": "MOLECULAR_FUNCTION",
                          "label": short(f"catalysis of {rxn['equation']}"),
                          "grounding": f"RHEA:{rid}",
                          "description": ("KB trait record (FUNC_ENZYMATIC_ACTIVITY) "
                                          "— one of the curated Rhea reactions of "
                                          f"this EC class. Full equation: "
                                          f"{rxn['equation']}")})
            nodes.extend(probe_n)
            edges.append({
                "subject": "activity", "predicate": P_NARROW[0],
                "predicate_id": P_NARROW[1], "object": nid,
                "description": (f"RHEA:{rid} is one of the {len(rxn_ids)} curated "
                                f"reactions Rhea assigns to EC {ec}; its substrates "
                                f"are not claimed for the class as a whole."),
                "evidence": [{
                    "reference": f"RHEA:{rid}",
                    "snippet": f'<rh:ec rdf:resource="http://purl.uniprot.org/enzyme/{ec}"/>',
                    "notes": (f"The rh:ec triple on RHEA:{rid} in rhea.rdf assigns "
                              f"that reaction to EC {ec}.")}]})
            edges.extend(probe_e)
            used.append(rid)

    # --- GO molecular function
    if has_go:
        nodes.append({"node_id": "go", "node_type": "MOLECULAR_FUNCTION",
                      "label": go_lab.get(go_curie, go_curie), "grounding": go_curie,
                      "description": "KB trait record (FUNC_MOLECULAR_FUNCTION)."})
        edges.append({
            "subject": "activity", "predicate": P_CLOSE[0], "predicate_id": P_CLOSE[1],
            "object": "go",
            "description": ("The GO molecular function that describes the same "
                            "catalysis as this EC class."),
            "evidence": [{"reference": curie, "snippet": go_line,
                          "notes": (f"The ec2go mapping line maintained by the GO "
                                    f"Consortium. GO term {go_curie} is itself a "
                                    f"record in this KB.")}]})

    # --- exemplar enzymes
    for acc_u, name, drline in entry["dr"][:MAX_PROTEINS]:
        nodes.append({"node_id": f"prot_{acc_u}", "node_type": "PROTEIN",
                      "label": name, "grounding": f"UniProtKB:{acc_u}"})
        edges.append({
            "subject": f"prot_{acc_u}", "predicate": P_ENABLES[0],
            "predicate_id": P_ENABLES[1], "object": "activity",
            "description": f"{name} is an exemplar enzyme with EC {ec} activity.",
            "evidence": [{"reference": curie, "snippet": drline,
                          "notes": (f"ExPASy ENZYME entry EC {ec} cross-references "
                                    f"UniProtKB:{acc_u} ({name}) as a protein with "
                                    f"this activity.")}]})

    if not edges:
        return None, "nothing citable to say"

    if not used:
        chem = ("No Rhea reaction is assigned to this EC class, so no substrate or "
                "product is asserted; the graph records only the exemplar enzymes "
                "and the equivalent GO molecular function.")
    elif single:
        chem = (f"EC {ec} maps to exactly one curated Rhea reaction (RHEA:{used[0]}), "
                f"so that reaction's substrates and products are the class's and hang "
                f"directly off the activity.")
    else:
        chem = (f"Rhea assigns {len(rxn_ids)} curated reactions to EC {ec}"
                + (f" (the first {len(used)} are shown)" if len(rxn_ids) > len(used) else "")
                + ". No one substrate set is the class's chemistry, so each reaction "
                  "is its own node — grounded to the Rhea record in this KB — and "
                  "carries its own inputs and outputs.")
    ca = (f' ExPASy ENZYME states the catalysed reaction as: "{entry["ca"].rstrip(".")}".'
          if entry["ca"] else "")

    # The note on direction only belongs on a graph that actually asserts a
    # substrate; on the 689 classes with no Rhea reaction it would describe
    # something the graph does not contain.
    direction = ("" if not used else
                 " Substrate/product direction is the one Rhea states in each "
                 "reaction's left-to-right directional child; Rhea's master "
                 "reactions are undirected.")
    return {"graph_id": "reaction_chemistry",
            "title": short(f"Reaction chemistry of {entry['name'] or curie}", 110),
            "description": (f"Chemistry, exemplar enzymes and GO equivalence for "
                            f"{curie}. {chem}{ca}{direction}"),
            "nodes": nodes, "edges": edges}, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("parsing Rhea RDF + KB identifiers…", file=sys.stderr)
    rh = rhea_rdf.load()
    kb = kb_identifiers()
    go_lab, ecdb, e2g = go_labels(), enzyme_entries(), ec2go_lines()
    ec2rhea = collections.defaultdict(set)
    for rid, rxn in rh.reactions.items():
        if f"RHEA:{rid}" in kb:
            for ec in rxn["ec"]:
                ec2rhea[ec].add(rid)

    stat = collections.Counter()
    done = 0
    for f in sorted(ROOT.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        # Skip on THIS builder's graph_id rather than on any graph being present, so
        # a record that gained some other graph first is not locked out of its own.
        if has_graph(text, "reaction_chemistry"):
            stat["already has a graph"] += 1
            continue
        m = re.search(r"^identifier:\s*EC:(\S+)\s*$", text, re.M)
        if not m:
            stat["skipped: no EC identifier"] += 1
            continue
        ec = m.group(1)
        if ec.endswith("-"):
            stat["skipped: class-level EC node"] += 1
            continue
        graph, why = build(ec, rh, kb, go_lab, ecdb, e2g, ec2rhea)
        if graph is None:
            stat[f"skipped: {why}"] += 1
            continue
        stat["written"] += 1
        stat["nodes"] += len(graph["nodes"])
        stat["edges"] += len(graph["edges"])

        block = yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                               allow_unicode=True, width=100, default_flow_style=False)
        hist = yaml.safe_dump({"curation_history": [{
            "timestamp": TIMESTAMP,
            "curator": "edison-causal-graphs",
            "action": (f"Added causal_graphs 'reaction_chemistry' "
                       f"({len(graph['edges'])} evidence-backed edges) from Rhea + "
                       f"ExPASy ENZYME; SEEDED -> REVIEWED"),
            "llm_assisted": True}]}, sort_keys=False, allow_unicode=True, width=100)
        out = re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED",
                     text, count=1, flags=re.M)
        # Append into each section rather than inserting a fresh key: a record may
        # already carry another builder's graph (and its history), and a second
        # top-level `causal_graphs:` would make PyYAML silently keep only the last,
        # discarding the existing graph. append_to_section handles both the
        # key-present and key-absent cases.
        spliced = append_to_section(out, "causal_graphs", block)
        if spliced == out:
            # append_to_section refused (an inline flow value it cannot
            # safely extend). Skip rather than flip mapping_status and write
            # a history entry claiming a graph was added that was not.
            stat["skipped: could not splice the graph into the record"] += 1
            continue
        out = append_to_section(spliced, "curation_history", hist)
        if args.apply:
            f.write_text(out, encoding="utf-8")
        elif done == 0:
            print(out)
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.most_common():
        print(f"  {k:<44} {v:>8,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
