#!/usr/bin/env python3
"""Write metal-coordination causal graphs onto the MetalPDB `STRUCT_METAL_SITE` records.

  python3 scripts/build_metalpdb_causal_graphs.py --limit 2   # dry run
  python3 scripts/build_metalpdb_causal_graphs.py --apply

The 291 MetalPDB records name a metal (CHEBI-grounded) and a coordination class,
and carried no causal graph. MetalPDB's own XML has what is needed: for every
site, each coordinating residue with its donor atom, the metal-donor distance,
and the coordination geometry.

WHAT IS CITED
-------------
The snippet is the field values of MetalPDB's own site entry — residue, chain,
donor atom, distance — quoted from `flat_db_file.xml.gz`. As with BioLiP, the
record's seeder-written `definition` is deliberately NOT quoted: our text is not
evidence for our own claim.

WHICH LIGANDS BECOME NODES
--------------------------
Only standard amino-acid residues. MetalPDB also lists waters (the single most
common coordinating "residue", 12,344 occurrences in the matched sites) and
nucleotides for DNA/RNA sites; those are real chemistry but not protein traits,
and a node per water would bury the residues that matter. The site node records
the full coordination number, so nothing is hidden by the choice.

MATCHING
--------
A record is a *class* ("mononuclear chromium site"), and its canonical examples
name PDB entries. A PDB entry usually has many metal sites, so a site counts only
if its metal symbol AND nuclearity both match the record.
"""

from __future__ import annotations

import argparse
import collections
import gzip
import io
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from record_io import append_to_section, has_graph

REPO = Path(__file__).resolve().parent.parent
XML = REPO / "data" / "raw" / "metalpdb" / "flat_db_file.xml.gz"
ROOT = REPO / "data" / "traits" / "structure" / "metal_site" / "metalpdb"

AA3 = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
       "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
       "SEC", "PYL", "MSE"}
AMP = re.compile(r"&(?!(amp|lt|gt|quot|apos|#\d+);)")
# "PDB 4nvz" but never the "PDB" inside "MetalPDB"
PDBRE = re.compile(r"(?<![A-Za-z])PDB ([0-9][A-Za-z0-9]{3})\b")
NUCL = ["mononuclear", "dinuclear", "trinuclear", "tetranuclear", "pentanuclear",
        "hexanuclear", "heptanuclear", "octanuclear", "nonanuclear", "decanuclear"]

P_INTERACTS = ("molecularly interacts with (coordinates)", "RO:0002436")
P_PART_OF = ("part of", "BFO:0000050")


def wanted_codes() -> dict:
    out = collections.defaultdict(set)
    for f in sorted(ROOT.glob("*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        for ce in d.get("canonical_examples") or []:
            m = PDBRE.search(ce.get("note") or "")
            if m:
                out[m.group(1).lower()].add(f.name)
    return out


def load_sites(codes) -> dict:
    """pdb code -> [site dicts], for the entries the corpus actually references."""
    buf = io.StringIO("".join(
        AMP.sub("&amp;", l)
        for l in gzip.open(XML, "rt", errors="replace")))
    out = collections.defaultdict(list)
    for _ev, el in ET.iterparse(buf, events=("end",)):
        if el.tag != "site":
            continue
        code = (el.findtext("pdb_code") or "").lower()
        if code not in codes:
            el.clear()
            continue
        metals = el.findall("metal")
        if metals:
            first = metals[0]
            ligands = []
            for mt in metals:
                for lg in mt.findall("ligand"):
                    ligands.append({
                        "residue_name": (lg.findtext("residue_name") or "").strip(),
                        "residue_pdb_number": (lg.findtext("residue_pdb_number") or "").strip(),
                        "chain_letter": (lg.findtext("chain_letter") or "").strip(),
                        "donor": (lg.findtext("donor") or "").strip(),
                        "distance": (lg.findtext("distance") or "").strip(),
                    })
            out[code].append({
                "site_name": (el.findtext("site_name") or "").strip(),
                "nuclearity": (el.findtext("site_nuclearity") or "").strip().lower(),
                "symbol": (first.findtext("periodic_symbol") or "").strip(),
                "periodic_name": (first.findtext("periodic_name") or "").strip(),
                "geometry": (first.findtext("geometry") or "").strip(),
                "coordination_number": (first.findtext("coordination_number") or "").strip(),
                "ligands": ligands,
            })
        el.clear()
    return out


def build(record, sites_by_code):
    metal = next((c for c in record.get("chemical_participants") or []
                  if c.get("chebi")), None)
    if not metal:
        return None, "no CHEBI metal on the record"
    label = (record.get("label") or "").lower()
    nucl = next((n for n in NUCL if n in label), None)

    chosen = []
    for ce in record.get("canonical_examples") or []:
        m = PDBRE.search(ce.get("note") or "")
        if not m:
            continue
        code = m.group(1).lower()
        for s in sites_by_code.get(code, []):
            if nucl and s["nuclearity"] != nucl:
                continue
            if (metal.get("name") or "").lower() not in (s["periodic_name"] or "").lower():
                continue
            if any(l["residue_name"].upper() in AA3 for l in s["ligands"]):
                chosen.append((ce, code, s))
                break
        if len(chosen) >= 3:      # a class needs exemplars, not every occurrence
            break
    if not chosen:
        return None, "no site matched metal + nuclearity with protein ligands"

    nodes = [{"node_id": "metal", "label": metal.get("name") or metal["chebi"],
              "node_type": "CHEMICAL", "grounding": metal["chebi"]},
             {"node_id": "site", "label": record.get("label") or "metal site",
              "node_type": "MOTIF", "grounding": record["identifier"],
              "description": "KB trait record (STRUCT_METAL_SITE) — the "
                             "coordination class this site belongs to."}]
    edges = []
    seen = set()
    for ce, code, s in chosen:
        acc = (ce.get("protein_id") or "").strip()
        geo = f"; geometry {s['geometry']}" if s.get("geometry") else ""
        base_note = (f"MetalPDB site {s['site_name']} (PDB {code}, "
                     f"{s['nuclearity']} {s['periodic_name']}, coordination number "
                     f"{s['coordination_number']}{geo}). Field values quoted from "
                     f"flat_db_file.xml.gz; MetalPDB also lists non-protein "
                     f"coordinating ligands (water, nucleotides) that are not "
                     f"written as nodes here.")
        for l in s["ligands"]:
            rn = l["residue_name"].upper()
            if rn not in AA3 or not l["residue_pdb_number"]:
                continue
            # the PDB code belongs in the id: the same residue number in two
            # exemplar structures is two different residues in two different
            # proteins, and must not collapse into one node
            nid = f"res{code}{rn}{l['residue_pdb_number']}{l['chain_letter']}"
            nid = re.sub(r"[^A-Za-z0-9_]", "", nid)
            if nid in seen:
                continue
            seen.add(nid)
            snippet = (f"residue_name {rn}; residue_pdb_number "
                       f"{l['residue_pdb_number']}; chain_letter {l['chain_letter']}"
                       + (f"; donor {l['donor']}" if l["donor"] else "")
                       + (f"; distance {l['distance']}" if l["distance"] else ""))
            nodes.append({"node_id": nid,
                          "label": (f"coordinating {rn}{l['residue_pdb_number']} "
                                    f"(PDB {code} chain {l['chain_letter']} author "
                                    f"numbering; no UniProt position asserted)"),
                          "node_type": "RESIDUE",
                          **({"grounding": acc} if acc else {})})
            # a fresh dict per edge: sharing one object makes yaml.safe_dump
            # emit an anchor/alias (&id001 / *id001), which is valid YAML but
            # unreadable in a curated record
            def ev():
                return [{"reference": f"PDB:{code}", "snippet": snippet,
                         "notes": base_note}]
            edges.append({"subject": nid, "predicate": P_INTERACTS[0],
                          "predicate_id": P_INTERACTS[1], "object": "metal",
                          "description": (f"{rn}{l['residue_pdb_number']} donates "
                                          f"{l['donor'] or 'a donor atom'} to the "
                                          f"coordinated {metal.get('name')}."),
                          "evidence": ev()})
            edges.append({"subject": nid, "predicate": P_PART_OF[0],
                          "predicate_id": P_PART_OF[1], "object": "site",
                          "description": "A coordinating residue of this metal site.",
                          "evidence": ev()})
    if not edges:
        return None, "no protein residue after filtering"
    edges.append({"subject": "metal", "predicate": P_PART_OF[0],
                  "predicate_id": P_PART_OF[1], "object": "site",
                  "description": "The coordinated metal ion of this site.",
                  "evidence": [{"reference": f"PDB:{chosen[0][1]}",
                                "snippet": (f"periodic_symbol {chosen[0][2]['symbol']}; "
                                            f"coordination_number "
                                            f"{chosen[0][2]['coordination_number']}"),
                                "notes": (f"MetalPDB site {chosen[0][2]['site_name']} "
                                          f"metal record.")}]})

    return {"graph_id": "metal_coordination",
            "title": f"Coordination of {metal.get('name')} at the {record.get('label')}",
            "description": (f"Protein residues coordinating the metal, transcribed "
                            f"from MetalPDB across {len(chosen)} exemplar site(s). "
                            f"Residue numbering is the PDB author frame MetalPDB "
                            f"reports; no UniProt position is asserted."),
            "nodes": nodes, "edges": edges}, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    codes = wanted_codes()
    print(f"indexing MetalPDB for {len(codes):,} referenced PDB entries…",
          file=sys.stderr)
    sites = load_sites(set(codes))
    stat = collections.Counter()
    done = 0

    for f in sorted(ROOT.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if has_graph(text, "metal_coordination"):
            stat["already has a graph"] += 1
            continue
        record = yaml.safe_load(text)
        graph, why = build(record, sites)
        if graph is None:
            stat[f"skipped: {why}"] += 1
            continue
        stat["written"] += 1
        stat["edges"] += len(graph["edges"])
        stat["nodes"] += len(graph["nodes"])
        block = yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                               allow_unicode=True, width=100,
                               default_flow_style=False)
        hist = yaml.safe_dump({"curation_history": [{
            "timestamp": "2026-07-29T00:00:00Z",
            "curator": "edison-causal-graphs",
            "action": (f"Added causal_graphs 'metal_coordination' "
                       f"({len(graph['edges'])} evidence-backed edges) from "
                       f"MetalPDB; SEEDED -> REVIEWED"),
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
            print(block[:2200])
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.most_common():
        print(f"  {k:<52} {v:>6,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
