#!/usr/bin/env python3
"""Give Rhea reaction records the catalytic residues that perform them, from M-CSA.

  python3 scripts/build_rhea_mcsa_residue_graphs.py --limit 3   # dry run
  python3 scripts/build_rhea_mcsa_residue_graphs.py --apply

After round 16 the corpus has two mechanism subgraphs that rarely meet. An M-CSA
graph says *these residues do the chemistry* (RESIDUE → STATE step → STATE step);
a Rhea graph says *these substrates become those products* (MOLECULAR_FUNCTION →
CHEMICAL). Across the 1,001 seeder-generated M-CSA graphs the two halves join only
at the top, so nothing there answers "which residues run this reaction".

The corpus is **not** free of RESIDUE → CHEMICAL edges, and an earlier version of
this docstring wrongly claimed it was. There are 1,870: 1,865 residue→metal from
MetalPDB, and 5 hand-curated in `beta-lactamase-class-a-mcsa2` and
`beta-lactamase-class-b1-mcsa15` — three pointing at the substrate, two at the water
of hydrolysis. Those two records do at curation time exactly what this script cannot
do at scale, and are the worked example to generalise from.

WHAT THIS DOES NOT DO, AND WHY
------------------------------
It does **not** write "residue X attacks substrate Y". M-CSA does not state that.
Each residue carries `roles` (`proton acceptor`, `electrostatic stabiliser`, …) with
a `function_type` of `reactant` / `interaction` / `spectator` and an EMO id — but no
target compound. The per-step `marvin_xml` field, which sounds like arrow-pushing
atom mappings, is a *filename* (max length 107 across all 4,586 steps). The only
place a residue and a compound are named together is the free-text step description,
where compounds appear as prose jargon ("the OSB C7 carboxylate group") rather than
by their ChEBI name. Matching those would be our reading, not M-CSA's.

So the edge written here is the one M-CSA does support: **this residue is causally
responsible for this reaction**, typed by M-CSA's own role classification.

THE JOIN, VERIFIED ON CHEMISTRY RATHER THAN INFERRED FROM EC
------------------------------------------------------------
All 1,003 M-CSA entries carry `reaction.compounds` with a `chebi_id` and a
`type: reactant|product`. Rhea gives each master reaction two ChEBI-typed sides. So
the join is checkable: an M-CSA entry matches a Rhea reaction when its reactant set
**equals** one Rhea side and its product set **equals** the other, as sets of ChEBI
CURIEs. EC agreement is required first (to bound the candidates) but is never
sufficient on its own — 289 EC-matched pairs fail the ChEBI check and are dropped.

**47 of the 472 matches are reverse-oriented**: M-CSA's reactants equal Rhea's `_R`
side. Both sources are right — a Rhea master is undirected and M-CSA curates the
physiological direction — so the orientation is recorded in the evidence notes
rather than reconciled away.

RESIDUE NODES ARE REUSED, NOT RE-DERIVED
-----------------------------------------
Rounds 12–13 already resolved every M-CSA residue's UniProt position through SIFTS
and wrote it into that record's `catalysis` graph. Those nodes are copied verbatim
rather than recomputed, so this round introduces no new residue-numbering claim and
cannot disagree with the M-CSA record it came from.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

import yaml

from record_io import _graph_ids, append_to_section

import rhea_rdf
from build_rhea_causal_graphs import short

REPO = Path(__file__).resolve().parent.parent
MCSA_RAW = REPO / "data" / "raw" / "mcsa.entries.jsonl"
MCSA_DIR = REPO / "data" / "traits" / "structure" / "active_site" / "mcsa"
RHEA_DIR = REPO / "data" / "traits" / "function" / "enzymatic_activity" / "rhea"

P_AGENT = ("is a catalytic agent in", "RO:0002500")   # causal agent in process
P_CLOSE = ("has its catalytic mechanism curated by", "skos:closeMatch")
TIMESTAMP = "2026-07-30T00:00:00Z"
GRAPH_ID = "catalytic_residues"


def mcsa_entries() -> dict[str, dict]:
    out = {}
    if not MCSA_RAW.exists():
        print(f"missing {MCSA_RAW} — run `just fetch-mcsa`", file=sys.stderr)
        raise SystemExit(1)
    for line in MCSA_RAW.open(encoding="utf-8"):
        d = json.loads(line)
        out[str(d["mcsa_id"])] = d
    return out


def mcsa_record_paths() -> dict[str, Path]:
    """MCSA id -> the KB record file, by reading each record's identifier."""
    out = {}
    for f in MCSA_DIR.glob("*.yaml"):
        m = re.search(r"^identifier:\s*MCSA:(\d+)\s*$", f.read_text(encoding="utf-8"),
                      re.M)
        if m:
            out[m.group(1)] = f
    return out


def rhea_side_sets(rh: rhea_rdf.Rhea) -> dict[str, tuple[frozenset, frozenset]]:
    out = {}
    for rid, rxn in rh.reactions.items():
        if len(rxn["sides"]) != 2:
            continue
        L, R = rxn["sides"]

        def chebis(side):
            return frozenset(c["chebi"] for c, _, _ in rh.participants_of(side)
                             if c.get("chebi"))
        out[rid] = (chebis(L), chebis(R))
    return out


def compute_join(rh: rhea_rdf.Rhea, entries: dict) -> dict[str, dict]:
    """M-CSA id -> {rhea, orientation, reactants, products} for exact-set matches."""
    sides = rhea_side_sets(rh)
    ec2rhea = collections.defaultdict(set)
    for rid, rxn in rh.reactions.items():
        for ec in rxn["ec"]:
            ec2rhea[ec].add(rid)

    joins, stat = {}, collections.Counter()
    for mid, d in entries.items():
        stat["M-CSA entries"] += 1
        cs = d["reaction"].get("compounds") or []
        react = frozenset("CHEBI:" + c["chebi_id"] for c in cs
                          if c.get("type") == "reactant" and c.get("chebi_id"))
        prod = frozenset("CHEBI:" + c["chebi_id"] for c in cs
                         if c.get("type") == "product" and c.get("chebi_id"))
        if not react or not prod:
            stat["no reactant/product ChEBI"] += 1
            continue
        cands: set[str] = set()
        for ec in (d.get("all_ecs") or [d["reaction"].get("ec")]):
            if ec:
                cands |= ec2rhea.get(ec, set())
        if not cands:
            stat["EC matches no Rhea reaction"] += 1
            continue
        hit = None
        for rid in sorted(cands, key=int):
            L, R = sides.get(rid, (frozenset(), frozenset()))
            if react == L and prod == R:
                hit = (rid, "LR")
                break
            if react == R and prod == L:
                hit = (rid, "RL")
                break
        if not hit:
            stat["EC matched but ChEBI sets disagree"] += 1
            continue
        stat["joined (exact ChEBI set equality)"] += 1
        stat["  ...M-CSA runs Rhea's reverse direction"] += (hit[1] == "RL")
        joins[mid] = {"rhea": hit[0], "orientation": hit[1],
                      "reactants": sorted(react), "products": sorted(prod),
                      "names": [(c.get("name", ""), c.get("type", ""))
                                for c in cs if c.get("chebi_id")]}
    for k, v in stat.most_common():
        print(f"  {k:<44}{v:>6,}", file=sys.stderr)
    return joins


def residue_nodes_from_mcsa_record(path: Path) -> tuple[list, str]:
    """The RESIDUE nodes of an M-CSA record's own catalysis graph, plus its label.

    Reused verbatim: rounds 12–13 resolved these positions through SIFTS and this
    round has no business re-deriving them."""
    rec = yaml.safe_load(path.read_text(encoding="utf-8"))
    for g in rec.get("causal_graphs") or []:
        nodes = [n for n in g.get("nodes") or [] if n.get("node_type") == "RESIDUE"]
        if nodes:
            return nodes, rec.get("label") or ""
    return [], rec.get("label") or ""


def role_index(entry: dict) -> dict:
    """Aggregate M-CSA's role classification for the entry as a whole."""
    types = collections.Counter()
    emos = []
    for r in entry.get("residues") or []:
        for ro in r.get("roles") or []:
            if ro.get("function_type"):
                types[ro["function_type"]] += 1
            if ro.get("emo"):
                emos.append(ro["emo"].replace("_", ":"))
    return {"types": types, "emos": sorted(set(emos))}


def build(rid: str, rxn: dict, mid: str, join: dict, entry: dict,
          mcsa_path: Path) -> tuple[dict | None, str]:
    residues, mcsa_label = residue_nodes_from_mcsa_record(mcsa_path)
    if not residues:
        return None, "M-CSA record has no residue nodes to reuse"

    acc, mcsa_curie = f"RHEA:{rid}", f"MCSA:{mid}"
    orient = join["orientation"]
    sideL, sideR = rxn["sides"]
    react_side, prod_side = (sideL, sideR) if orient == "LR" else (sideR, sideL)
    names = "; ".join(f"{n} [{t}]" for n, t in join["names"])
    roles = role_index(entry)

    join_note = (
        f"Join verified on chemistry, not inferred from EC: M-CSA entry {mid}'s "
        f"reactant set ({', '.join(join['reactants'])}) equals Rhea side {react_side} "
        f"exactly, and its product set ({', '.join(join['products'])}) equals side "
        f"{prod_side} exactly. EC agreement bounded the candidates but was not "
        f"sufficient on its own."
        + ("" if orient == "LR" else
           f" NOTE: M-CSA curates this reaction in the direction opposite to Rhea's "
           f"left-hand side — M-CSA's reactants are Rhea's {react_side}. Both are "
           f"correct: a Rhea master reaction is undirected, and M-CSA records the "
           f"physiological direction. The disagreement is recorded, not reconciled."))

    nodes = [{
        "node_id": "activity",
        # Use the same shortener round 16 uses for this node, so the two graphs in a
        # record label the same RHEA: grounding identically. The earlier ternary was
        # inverted: a long equation dropped the "catalysis of " prefix entirely (73
        # records) and a mid-length one was cut at exactly 90 chars mid-word with no
        # ellipsis (57 records).
        "label": short(f"catalysis of {rxn['equation']}"),
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": acc,
        "description": ("KB trait record (FUNC_ENZYMATIC_ACTIVITY) — the reaction "
                        f"these residues carry out. Full equation: {rxn['equation']}"),
    }, {
        "node_id": "mcsa",
        "label": mcsa_label or f"M-CSA entry {mid}",
        "node_type": "MOTIF",
        "grounding": mcsa_curie,
        "description": ("KB trait record (STRUCT_ACTIVE_SITE) — the curated catalytic "
                        "site whose stepwise mechanism this reaction's chemistry is."),
    }]
    edges = [{
        "subject": "activity",
        "predicate": P_CLOSE[0], "predicate_id": P_CLOSE[1], "object": "mcsa",
        "description": (f"M-CSA entry {mid} curates the catalytic mechanism of this "
                        f"reaction."),
        "evidence": [{
            "reference": mcsa_curie,
            "snippet": names,
            "notes": (f"The `reaction.compounds` field of M-CSA entry {mid}, each "
                      f"compound with the reactant/product type M-CSA assigns it. "
                      + join_note),
        }],
    }]

    for n in residues:
        node = dict(n)
        node["description"] = ((n.get("description", "") + " ").strip()
                               + f" Reused verbatim from the {mcsa_curie} record's "
                               f"catalysis graph, where the UniProt position was "
                               f"resolved through SIFTS.").strip()
        nodes.append(node)
        edges.append({
            "subject": n["node_id"],
            "predicate": P_AGENT[0], "predicate_id": P_AGENT[1], "object": "activity",
            "description": ("M-CSA lists this residue as catalytic for the mechanism "
                            "that carries out this reaction."),
            "evidence": [{
                "reference": mcsa_curie,
                "snippet": re.sub(r"^M-CSA roles:\s*", "", n.get("description", "")
                                  ).rstrip(".") or "catalytic residue",
                "notes": (f"M-CSA entry {mid} annotates this residue with the roles "
                          f"quoted. Across the entry M-CSA types its residue roles as "
                          + ", ".join(f"{v} {k}" for k, v in roles["types"].most_common())
                          + ". M-CSA states which residues are catalytic and what role "
                          "each plays, but never which compound a residue acts on, so "
                          "no residue-to-substrate edge is asserted. " + join_note),
            }],
        })

    return {
        # One graph per M-CSA entry, not per reaction: 35 of the 430 joined reactions
        # are curated by more than one M-CSA entry (up to 4). Those are different
        # enzymes — different proteins, often different folds — arriving at the same
        # chemistry, which is worth keeping rather than collapsing to whichever entry
        # happened to be processed first.
        "graph_id": f"{GRAPH_ID}_mcsa{mid}",
        "title": f"Catalytic residues of {acc} (from {mcsa_curie})",
        "description": (
            f"The catalytic residues that carry out {acc}, joined from M-CSA entry "
            f"{mid}. {len(residues)} residues, reused verbatim from the {mcsa_curie} "
            f"record rather than re-derived. M-CSA annotates each residue's role "
            f"(proton donor, electrostatic stabiliser, …) and whether it is a chemical "
            f"reactant, an interaction partner or a spectator, but does not say which "
            f"compound a residue acts on — so this graph asserts residue-to-reaction "
            f"causation, not residue-to-substrate. {join_note}"),
        "nodes": nodes, "edges": edges,
    }, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("parsing Rhea RDF + M-CSA…", file=sys.stderr)
    rh = rhea_rdf.load()
    entries = mcsa_entries()
    paths = mcsa_record_paths()
    joins = compute_join(rh, entries)

    rhea_paths = {}
    for f in RHEA_DIR.glob("*.yaml"):
        m = re.search(r"^identifier:\s*RHEA:(\d+)\s*$", f.read_text(encoding="utf-8"),
                      re.M)
        if m:
            rhea_paths[m.group(1)] = f

    stat = collections.Counter()
    done = 0
    # graph ids per record, parsed once (#106). 472 join pairs touch only 430 distinct
    # Rhea records -- 35 are visited more than once, up to 4 times -- so the same
    # section was parsed 42 times over. The cache is updated on write rather than
    # invalidated, because the loop appends to a record it may visit again.
    ids_by_path: dict = {}
    for mid, join in sorted(joins.items(), key=lambda kv: int(kv[0])):
        rid = join["rhea"]
        rpath, mpath = rhea_paths.get(rid), paths.get(mid)
        if not rpath:
            stat["skipped: Rhea reaction is not a KB record"] += 1
            continue
        if not mpath:
            stat["skipped: M-CSA entry is not a KB record"] += 1
            continue
        text = rpath.read_text(encoding="utf-8")
        if rpath not in ids_by_path:
            ids_by_path[rpath] = _graph_ids(text)
        # Whole-id membership, not a prefix test: `..._mcsa45` is a substring of
        # `..._mcsa454`, so a plain `in` on the text would report a genuinely new entry
        # as already wired and silently never write it. A set gives that for free.
        graph_id = f"{GRAPH_ID}_mcsa{mid}"
        if graph_id in ids_by_path[rpath]:
            stat["already wired"] += 1
            continue
        graph, why = build(rid, rh.reactions[rid], mid, join, entries[mid], mpath)
        if graph is None:
            stat[f"skipped: {why}"] += 1
            continue

        block = yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                               allow_unicode=True, width=100, default_flow_style=False)
        hist = yaml.safe_dump({"curation_history": [{
            "timestamp": TIMESTAMP, "curator": "edison-causal-graphs",
            "action": (f"Added causal_graphs '{graph['graph_id']}' ({len(graph['edges'])} "
                       f"evidence-backed edges) joining MCSA:{mid} on exact ChEBI "
                       f"set equality"),
            "llm_assisted": True}]}, sort_keys=False, allow_unicode=True, width=100)

        spliced = append_to_section(text, "causal_graphs", block)
        if spliced == text:
            # Checked on the GRAPH splice alone. The old guard compared the
            # final text, so a refused graph whose history splice succeeded
            # looked like success and wrote a history entry claiming a graph
            # that is not there.
            stat["skipped: could not splice the graph into the record"] += 1
            continue
        out = append_to_section(spliced, "curation_history", hist)
        if out == spliced:
            # The history splice was refused too. Writing the graph while
            # silently leaving history empty would leave no audit trail of
            # why the record changed. (This builder does not touch
            # mapping_status; its five twins do.)
            stat["skipped: could not splice the history into the record"] += 1
            continue
        stat["written"] += 1
        stat["residue edges"] += len(graph["edges"]) - 1
        stat["reverse-oriented"] += (join["orientation"] == "RL")
        # Defensive, not required today: every iteration tests a DIFFERENT id
        # (`_mcsa{mid}`, and mids are unique), so a stale entry is never queried even
        # on the 35 records this loop visits more than once. Kept because that is a
        # property of the current id scheme rather than of the cache, and the failure
        # it would cause — appending a graph the record already has — is silent.
        # Removing this line breaks no test and no dry run, which is exactly why the
        # reasoning is written down here instead of being left implicit.
        ids_by_path[rpath].add(graph_id)
        if args.apply:
            rpath.write_text(out, encoding="utf-8")
        elif done == 0:
            print(block + hist)
        done += 1
        if args.limit and done >= args.limit:
            break

    print(file=sys.stderr)
    for k, v in stat.most_common():
        print(f"  {k:<44}{v:>6,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
