#!/usr/bin/env python3
"""Write ligand-binding causal graphs onto the BioLiP `STRUCT_BINDING_SITE` records.

  python3 scripts/build_biolip_causal_graphs.py --limit 3   # dry run, prints YAML
  python3 scripts/build_biolip_causal_graphs.py --apply

6,019 BioLiP records carry a ligand, a PDB occurrence and a list of binding
residues, and none carried a causal graph. The mechanism here is not a reaction
but an interaction: *these residues contact this ligand*, which is exactly what
BioLiP curates from 3D complexes.

WHAT IS CITED
-------------
The snippet is the **binding-residue field of BioLiP's own record line**, quoted
verbatim from `data/raw/biolip/BioLiP_nr.txt`. It is data rather than prose, but
it is the source's own statement of the claim the edge makes, and it is checkable
against the file. The record's `canonical_examples` note is *not* used as
evidence: our seeder wrote it, so quoting it would be circular.

BioLiP's PubMed id for the occurrence travels in the edge `notes`, on the same
rule used for M-CSA — a PMID becomes the `reference` only when someone has read
the paper.

RESIDUE NUMBERING, VERIFIED
---------------------------
BioLiP gives binding residues twice: column 8 in PDB author numbering (which the
seeder used in the record notes, so it is the frame the corpus already speaks)
and column 9 renumbered from 1 against the receptor sequence in column 21.

That redundancy makes the residue letters checkable with no network: for every
residue, the code in column 9 must match the receptor sequence at that position.
A residue that fails is dropped rather than written. Labels state the PDB frame
explicitly and assert no UniProt position, because BioLiP does not provide one
and the UniProt sequence is not on these records.
"""

from __future__ import annotations

import argparse
import collections
import csv
import gzip
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
BIOLIP = REPO / "data" / "raw" / "biolip" / "BioLiP_nr.txt"
LIGTSV = REPO / "data" / "raw" / "biolip" / "ligand.tsv"
CHEBI = REPO / "data" / "raw" / "chebi" / "structures.tsv.gz"
ROOT = REPO / "data" / "traits" / "structure" / "binding_site" / "biolip"

AA1 = set("ACDEFGHIKLMNPQRSTVWY")
P_INTERACTS = ("molecularly interacts with", "RO:0002436")
P_PART_OF = ("part of", "BFO:0000050")
P_ENABLES = ("enables", "RO:0002327")


def chebi_by_inchikey() -> dict:
    csv.field_size_limit(10 ** 9)
    out = {}
    with gzip.open(CHEBI, "rt", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            k = (row.get("standard_inchi_key") or "").strip()
            cid = (row.get("compound_id") or "").strip()
            if k and cid and k not in out:
                out[k] = f"CHEBI:{cid}"
    return out


def ligand_table() -> dict:
    out = {}
    with LIGTSV.open(newline="") as f:
        for row in csv.reader(f, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            out[row[0]] = {"inchikey": row[3].strip() if len(row) > 3 else "",
                           "name": (row[5].split(";")[0].strip()
                                    if len(row) > 5 else "")}
    return out


def biolip_index() -> dict:
    """(pdb, chain, ligand CCD) -> the first record line's fields we need."""
    idx = {}
    with BIOLIP.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 21:
                continue
            key = (p[0].lower(), p[1], p[4])
            if key in idx:
                continue
            idx[key] = {"res_pdb": p[7], "res_seq": p[8], "ec": p[11],
                        "uniprot": p[17], "pmid": p[18], "seq": p[20]}
    return idx


def verified_residues(rec) -> list:
    """[(code, pdb_pos)] whose letter checks out against BioLiP's own sequence.

    Column 9 positions index the receptor sequence in column 21, so a residue
    that does not match there is not a residue BioLiP is describing — most often
    a parsing slip on our side, and never something to write.
    """
    pdb_toks = rec["res_pdb"].split()
    seq_toks = rec["res_seq"].split()
    seq = rec["seq"]
    if len(pdb_toks) != len(seq_toks) or not seq:
        return []
    out = []
    for a, b in zip(pdb_toks, seq_toks):
        ma, mb = re.match(r"^([A-Z])(-?\d+[A-Za-z]?)$", a), re.match(r"^([A-Z])(\d+)$", b)
        if not ma or not mb or ma.group(1) != mb.group(1):
            continue
        code, pos = mb.group(1), int(mb.group(2))
        if code in AA1 and 1 <= pos <= len(seq) and seq[pos - 1] == code:
            out.append((code, ma.group(2)))
    return out


def build(record: dict, text: str, idx, ligs, chebi):
    ccd = None
    m = re.search(r"^\s+- pdb\.ligand:(\S+)\s*$", text, re.M)
    if m:
        ccd = m.group(1)
    if not ccd:
        return None, "no ligand CCD"

    occurrences = []
    for ce in record.get("canonical_examples") or []:
        note = ce.get("note") or ""
        mm = re.search(r"PDB (\w{4}) chain (\w+)", note)
        if not mm:
            continue
        key = (mm.group(1).lower(), mm.group(2), ccd)
        if key in idx:
            occurrences.append((ce, key, idx[key]))
    if not occurrences:
        return None, "no matching BioLiP line"

    ce, key, rec = occurrences[0]
    residues = verified_residues(rec)
    if not residues:
        return None, "no residue survived verification"

    pdb, chain, _ = key
    # The residues quoted below are BioLiP's for THIS chain, so they are grounded
    # to the accession BioLiP maps that chain to. On 197 records that differs from
    # the accession the seeder put in canonical_examples; the note records the
    # disagreement instead of silently preferring one.
    rec_acc = (ce.get("protein_id") or "").strip()
    bl_raw = (rec.get("uniprot") or "").strip()
    # BioLiP names several accessions for a chimeric/fusion chain
    # ("P0ABE7,P30939"). Which half a given residue belongs to is not something
    # the file states, so nothing is grounded rather than guessing one; the note
    # records the fusion so a curator can resolve it.
    fusion = "," in bl_raw
    bl_acc = "" if fusion or bl_raw in ("", "-") else bl_raw
    acc = f"UniProtKB:{bl_acc}" if bl_acc else ("" if fusion else rec_acc)
    if fusion:
        acc_note = (f" BioLiP maps this chain to several accessions ({bl_raw}), a "
                    f"chimeric or fusion construct, so no single protein is "
                    f"asserted for these residues.")
    elif bl_acc and rec_acc and f"UniProtKB:{bl_acc}" != rec_acc:
        acc_note = (f" BioLiP maps this chain to UniProtKB:{bl_acc}, while the "
                    f"record's canonical example names {rec_acc}; the residues "
                    f"quoted here are BioLiP's for this chain.")
    else:
        acc_note = ""
    lig = ligs.get(ccd) or {}
    full_name = lig.get("name") or ccd
    # PDB chemical names run to 200+ characters; a label that long is unreadable
    # in the browser and useless in a graph title. The full name stays on the
    # record itself (label + EXACT_SYNONYM), so nothing is lost by shortening here.
    ligand_name = full_name if len(full_name) <= 48 else f"ligand {ccd}"
    grounding = chebi.get(lig.get("inchikey", "")) or f"pdb.ligand:{ccd}"

    def ev(extra=""):
        note = (f"BioLiP2 record line for PDB {pdb} chain {chain}, ligand {ccd}: "
                f"binding-site residues in PDB author numbering (column 8 of "
                f"BioLiP_nr.txt), cross-checked against BioLiP's own receptor "
                f"sequence via its renumbered column 9.")
        if rec.get("pmid"):
            note += f" BioLiP cites PMID:{rec['pmid']} for this structure."
        return [{"reference": f"PDB:{pdb}",
                 "snippet": rec["res_pdb"],
                 "notes": note + acc_note + (f" {extra}" if extra else "")}]

    nodes = [{"node_id": "ligand", "label": ligand_name, "node_type": "LIGAND",
              "grounding": grounding, "xrefs": [f"pdb.ligand:{ccd}"]},
             {"node_id": "site",
              "label": f"{ligand_name}-binding site",
              "node_type": "MOTIF",
              "grounding": record["identifier"],
              "description": "KB trait record (STRUCT_BINDING_SITE) — the site "
                             "this interaction defines."}]
    if acc:
        nodes.append({"node_id": "protein", "label": ce.get("protein_label") or acc,
                      "node_type": "PROTEIN", "grounding": acc})

    edges = []
    for code, pos in residues:
        nid = f"res{code}{pos}".replace("-", "m")
        nodes.append({"node_id": nid,
                      "label": (f"binding residue {code}{pos} (PDB {pdb} chain "
                                f"{chain} author numbering; no UniProt position "
                                f"asserted)"),
                      "node_type": "RESIDUE",
                      **({"grounding": acc} if acc else {})})
        edges.append({"subject": nid, "predicate": P_INTERACTS[0],
                      "predicate_id": P_INTERACTS[1], "object": "ligand",
                      "description": f"{code}{pos} contacts the bound {ligand_name}.",
                      "evidence": ev()})
        edges.append({"subject": nid, "predicate": P_PART_OF[0],
                      "predicate_id": P_PART_OF[1], "object": "site",
                      "description": f"{code}{pos} is one of the site's binding residues.",
                      "evidence": ev()})
    if acc:
        edges.append({"subject": "site", "predicate": P_PART_OF[0],
                      "predicate_id": P_PART_OF[1], "object": "protein",
                      "description": "The binding site lies in this receptor chain.",
                      "evidence": ev(f"Receptor mapped by BioLiP to {acc}.")})
    # BioLiP's EC field is "?" on 35k lines, blank on 18k, and elsewhere a
    # comma-separated list that can mix "?" with real numbers. Only well-formed
    # EC numbers become xrefs; "EC:?" is not a CURIE and fails closed-mode
    # validation.
    ecs = [e for e in re.split(r"[,\s]+", (rec.get("ec") or "").strip())
           if re.fullmatch(r"\d+(\.[\d-]+){0,3}", e)]
    if ecs:
        nodes.append({"node_id": "activity",
                      "label": "enzymatic activity EC " + ", ".join(ecs[:3]),
                      "node_type": "MOLECULAR_FUNCTION",
                      "xrefs": [f"EC:{e}" for e in ecs[:3]]})
        edges.append({"subject": "site", "predicate": P_ENABLES[0],
                      "predicate_id": P_ENABLES[1], "object": "activity",
                      "description": "The site participates in this activity.",
                      "evidence": ev("EC " + ", ".join(ecs[:3])
                                     + " recorded by BioLiP for this receptor.")})

    return {"graph_id": "ligand_binding",
            "title": f"Binding of {ligand_name} at the {ligand_name}-binding site",
            "description": (f"Residue-level ligand contact transcribed from BioLiP2 "
                            f"for PDB {pdb} chain {chain}. Residue numbering is the "
                            f"PDB author frame BioLiP reports; each residue's identity "
                            f"was checked against BioLiP's own receptor sequence. "
                            f"{len(residues)} binding residues."),
            "nodes": nodes, "edges": edges}, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("indexing BioLiP + CHEBI…", file=sys.stderr)
    idx, ligs, chebi = biolip_index(), ligand_table(), chebi_by_inchikey()
    stat = collections.Counter()
    done = 0

    for f in sorted(ROOT.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if "causal_graphs:" in text:
            stat["already has a graph"] += 1
            continue
        record = yaml.safe_load(text)
        graph, why = build(record, text, idx, ligs, chebi)
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
            "action": (f"Added causal_graphs 'ligand_binding' ({len(graph['edges'])} "
                       f"evidence-backed edges) from BioLiP2; SEEDED -> REVIEWED"),
            "llm_assisted": True}]}, sort_keys=False, allow_unicode=True, width=100)
        out = re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED",
                     text, count=1, flags=re.M)
        if re.search(r"^license:", out, re.M):
            out = re.sub(r"^license:", block + hist + "license:", out, count=1, flags=re.M)
        else:
            out = out.rstrip("\n") + "\n" + block + hist
        if args.apply:
            f.write_text(out, encoding="utf-8")
        elif done == 0:
            print(block[:2500])
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.most_common():
        print(f"  {k:<34} {v:>7,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
