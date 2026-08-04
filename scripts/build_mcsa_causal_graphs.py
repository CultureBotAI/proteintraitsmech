#!/usr/bin/env python3
"""Transcribe M-CSA's curated catalytic mechanisms into `causal_graphs` blocks.

M-CSA is the one source that already encodes the causal steps *and* their
citations, so this is transcription-with-grounding, not invention. The step
descriptions in `data/raw/mcsa.entries.jsonl` are already causal statements —
"Asp7 deprotonates Cys70, activating it." — and each becomes the verbatim
`snippet` of the edge it backs.

  python3 scripts/build_mcsa_causal_graphs.py --limit 5     # dry run, prints YAML
  python3 scripts/build_mcsa_causal_graphs.py --apply

WHAT IS CITED, AND WHY IT IS NOT THE PMID
-----------------------------------------
Every snippet here is quoted from the **M-CSA entry**, so every edge cites the
M-CSA entry URL. M-CSA's own primary references are recorded in the edge `notes`
rather than as the `reference`: attaching a PMID to a snippet that was written by
M-CSA's curators — not by that paper — would misattribute the quote. Promoting a
PMID to `reference` is a per-edge curation act that requires reading the paper.

RESIDUE NUMBERING
-----------------
M-CSA gives PDB author numbering (`auth_resid`, the field-standard frame — e.g.
Ambler for beta-lactamases). The KB's records are in the UniProt frame. The two
are reconciled here by *verification, not assumption*: the unique integer offset
is found for which EVERY catalytic residue's one-letter code matches the
reference sequence already stored on the record. Entries with no unique offset
keep their residues in the M-CSA/PDB frame and say so in the label, rather than
asserting a UniProt position that was never checked. Validated against the
hand-curated MCSA:2, where this recovers the curator's SIFTS result (offset -2,
Ambler Ser70/Lys73/Ser130/Glu166 = UniProt 68/71/128/164).
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

from record_io import RecordError, append_to_section, has_graph

try:
    import yaml
except ImportError:
    print("needs PyYAML", file=sys.stderr)
    raise SystemExit(2)

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "data" / "raw" / "mcsa.entries.jsonl"
MCSA_DIR = REPO / "data" / "traits" / "structure" / "active_site" / "mcsa"
ENTRY_URL = "https://www.ebi.ac.uk/thornton-srv/m-csa/entry/{id}/"

AA3 = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q",
       "Glu": "E", "Gly": "G", "His": "H", "Ile": "I", "Leu": "L", "Lys": "K",
       "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W",
       "Tyr": "Y", "Val": "V", "Sec": "U", "Pyl": "O"}

# Deliberately few predicates, each load-bearing. RO:0002436 (molecularly
# interacts with) covers a residue acting chemically on a species; RO:0002411
# (causally upstream of) carries the step ordering; the rest wire the trait
# partonomy exactly as the hand-curated MCSA:2 graph does.
P_INTERACTS = ("participates in (chemical step)", "RO:0002436")
P_UPSTREAM = ("causally upstream of", "RO:0002411")
P_PART_OF = ("part of", "BFO:0000050")
P_ENABLES = ("enables", "RO:0002327")
P_INPUT = ("has input", "RO:0002233")
P_OUTPUT = ("has output", "RO:0002234")


def load_cache() -> dict:
    return {e["mcsa_id"]: e for e in
            (json.loads(ln) for ln in CACHE.open(encoding="utf-8"))}


def kb_cath() -> set:
    """CATH ids that exist as KB records — a fold node is only written if the
    trait it points at is really in the corpus."""
    out = set()
    for f in (REPO / "data" / "traits").rglob("*.yaml"):
        pass
    # much faster than walking every record: the identifiers are greppable
    import subprocess
    r = subprocess.run(["grep", "-rhoE", r"^identifier: CATH:[0-9.]+",
                        str(REPO / "data" / "traits"), "--include=*.yaml"],
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        out.add(line.split("identifier: ", 1)[1].strip())
    return out


def record_files() -> dict:
    """MCSA id → (path, text, reference sequence or None)."""
    out = {}
    for f in sorted(MCSA_DIR.glob("*.yaml")):
        t = f.read_text(encoding="utf-8")
        m = re.search(r"^identifier:\s*MCSA:(\d+)", t, re.M)
        if not m:
            continue
        s = re.search(r"^\s+sequence:\s*(\S+)", t, re.M)
        out[int(m.group(1))] = (f, t, s.group(1) if s else None)
    return out


def catalytic_residues(entry: dict) -> list:
    """(code3, auth_resid, cath_id) for the reference chain, deduped, ordered."""
    seen, out = set(), []
    for r in entry.get("residues") or []:
        for c in r.get("residue_chains") or []:
            if not c.get("is_reference"):
                continue
            code, pos = c.get("code"), c.get("auth_resid")
            if code not in AA3 or pos is None:
                continue
            key = (code, int(pos))
            if key in seen:
                break
            seen.add(key)
            out.append((code, int(pos), c.get("domain_cath_id") or "",
                        (r.get("roles_summary") or "").strip()))
            break
    return sorted(out, key=lambda x: x[1])


def resolve_offset(residues: list, seq: str | None):
    """The unique offset mapping auth_resid → UniProt position, or None.

    None is a real answer, not a failure: it means the reference sequence on the
    record does not agree with M-CSA's chain, and asserting a UniProt position
    anyway would be inventing one.
    """
    if not seq or not residues:
        return None
    cand = [d for d in range(-60, 61)
            if all(0 <= p + d - 1 < len(seq) and seq[p + d - 1] == AA3[c]
                   for c, p, _cath, _roles in residues)]
    return cand[0] if len(cand) == 1 else None


def build_graph(entry: dict, residues: list, offset, cath_ok: set) -> dict | None:
    mid = entry["mcsa_id"]
    url = ENTRY_URL.format(id=mid)
    mechs = (entry.get("reaction") or {}).get("mechanisms") or []
    mech = next((m for m in mechs
                 if any((s.get("description") or "").strip()
                        for s in (m.get("steps") or []))), None)
    stepwise = mech is not None
    if mech is None:
        # 264 entries carry arrow-pushing `marvin_xml` with empty per-step
        # `description`s, but a populated `mechanism_text` — prose of the same
        # kind, just not split into steps ("First, Asp 222 B deprotonates the
        # 2-hydroxy oxygen…"). Treating that as a single unstepped mechanism
        # keeps them citable instead of dropping them for a formatting reason.
        mech = next((m for m in mechs if (m.get("mechanism_text") or "").strip()),
                    None)
        if mech is None:
            return None
    if stepwise:
        steps = [s for s in mech["steps"] if (s.get("description") or "").strip()]
    else:
        steps = [{"description": (mech.get("mechanism_text") or "").strip()}]

    pmids = sorted({str(r["pubmed_id"]) for r in (mech.get("references") or [])
                    if r.get("pubmed_id")})
    cite = ("M-CSA entry %d, mechanism %s" % (mid, mech.get("mechanism_id"))
            + ("; M-CSA cites " + ", ".join("PMID:" + p for p in pmids)
               if pmids else ""))

    def ev(snippet: str, extra: str = "") -> list:
        return [{"reference": url,
                 "snippet": snippet.strip(),
                 "notes": (cite + ("; " + extra if extra else ""))}]

    nodes, edges = [], []

    # --- catalytic residues -------------------------------------------------
    acc = (entry.get("reference_uniprot_id") or "").split(",")[0].strip()
    res_nodes = {}
    for code, pos, _cath, roles in residues:
        nid = f"{code.lower()}{pos}"
        res_nodes[(code, pos)] = nid
        if offset is not None:
            label = (f"catalytic {code}{pos} "
                     f"(M-CSA/PDB numbering; UniProt residue {pos + offset})")
        else:
            label = (f"catalytic {code}{pos} "
                     f"(M-CSA/PDB numbering; UniProt position not established)")
        n = {"node_id": nid, "label": label, "node_type": "RESIDUE"}
        if acc:
            n["grounding"] = f"UniProtKB:{acc}"
        if roles:
            n["description"] = f"M-CSA roles: {roles}."
        nodes.append(n)

    # --- reactants / products ----------------------------------------------
    comps = (entry.get("reaction") or {}).get("compounds") or []
    def chem(kind, prefix):
        out = []
        for i, c in enumerate(x for x in comps if x.get("type") == kind):
            nid = f"{prefix}{i}"
            n = {"node_id": nid, "label": c.get("name") or kind,
                 "node_type": "CHEMICAL"}
            if c.get("chebi_id"):
                n["grounding"] = f"CHEBI:{c['chebi_id']}"
            out.append((nid, n))
        return out
    reactants = chem("reactant", "reactant")
    products = chem("product", "product")
    nodes += [n for _i, n in reactants + products]

    # --- one STATE per mechanism step --------------------------------------
    step_ids = []
    for i, s in enumerate(steps, 1):
        nid = f"step{i}"
        step_ids.append((nid, s))
        desc = (s.get("description") or "").strip()
        nodes.append({"node_id": nid,
                      "label": (f"mechanism step {i}" if stepwise
                                else "overall catalytic mechanism (not resolved "
                                     "into steps by M-CSA)"),
                      "node_type": "STATE",
                      "description": desc[:400]})

    # --- the trait partonomy the KB is actually about ----------------------
    nodes.append({"node_id": "active_site",
                  "label": f"{entry.get('enzyme_name') or 'enzyme'} catalytic site",
                  "node_type": "MOTIF",
                  "grounding": f"MCSA:{mid}",
                  "description": "KB trait record (STRUCT_ACTIVE_SITE) — the "
                                 "catalytic site this mechanism runs in."})
    cath_id = next((c for _code, _p, c, _r in residues if c), "")
    fold = f"CATH:{cath_id}" if cath_id and f"CATH:{cath_id}" in cath_ok else None
    if fold:
        nodes.append({"node_id": "fold", "label": f"{cath_id} superfamily fold",
                      "node_type": "DOMAIN", "grounding": fold,
                      "description": "KB trait record; CATH domain assigned by "
                                     "M-CSA to the catalytic chain."})
    ecs = [e for e in (entry.get("all_ecs") or []) if e]
    act = {"node_id": "activity",
           "label": f"{entry.get('enzyme_name') or 'enzyme'} activity",
           "node_type": "MOLECULAR_FUNCTION"}
    if ecs:
        act["xrefs"] = [f"EC:{e}" for e in ecs[:4]]
    nodes.append(act)

    # --- edges: the step chain ---------------------------------------------
    prev = None
    for idx, (nid, s) in enumerate(step_ids):
        desc = (s.get("description") or "").strip()
        # The chain starts at step 1 and ends at the last step. Attaching a
        # specific reactant to step 1 (or a specific product to the last step)
        # would mean choosing one of several compounds M-CSA lists without
        # ordering them — the substrate/product relations are carried honestly
        # by activity has-input / has-output below instead.
        if prev is not None:
            edges.append({"subject": prev, "predicate": P_UPSTREAM[0],
                          "predicate_id": P_UPSTREAM[1], "object": nid,
                          "description": f"Step {idx} leads to step {idx+1}.",
                          "evidence": ev(desc, f"step {idx+1}")})
        prev = nid

        # residues named in this step's text act in it
        for (code, pos), rid in res_nodes.items():
            if re.search(rf"\b{code}\s?{pos}\b", desc):
                edges.append({"subject": rid, "predicate": P_INTERACTS[0],
                              "predicate_id": P_INTERACTS[1], "object": nid,
                              "description": f"{code}{pos} acts in step {idx+1}.",
                              "evidence": ev(desc, f"step {idx+1}")})

    # --- edges: wire through the protein traits ----------------------------
    site_snip = (mech.get("mechanism_text") or "").strip()[:400] or \
                (steps[0].get("description") or "").strip()
    for (code, pos), rid in res_nodes.items():
        roles = next((r for c, p, _c, r in residues if (c, p) == (code, pos)), "")
        edges.append({"subject": rid, "predicate": P_PART_OF[0],
                      "predicate_id": P_PART_OF[1], "object": "active_site",
                      "description": f"{code}{pos} is a catalytic residue of the site.",
                      "evidence": ev(roles or site_snip,
                                     f"M-CSA catalytic-residue roles for {code}{pos}")})
    if fold:
        edges.append({"subject": "active_site", "predicate": P_PART_OF[0],
                      "predicate_id": P_PART_OF[1], "object": "fold",
                      "description": "The catalytic site lies within this fold.",
                      "evidence": ev(site_snip,
                                     f"CATH domain {cath_id} assigned to the "
                                     f"catalytic chain by M-CSA")})
    edges.append({"subject": "active_site", "predicate": P_ENABLES[0],
                  "predicate_id": P_ENABLES[1], "object": "activity",
                  "description": "The catalytic site carries out the activity.",
                  "evidence": ev(site_snip, "overall mechanism")})
    for rid, _n in reactants:
        edges.append({"subject": "activity", "predicate": P_INPUT[0],
                      "predicate_id": P_INPUT[1], "object": rid,
                      "description": "Substrate consumed by the reaction.",
                      "evidence": ev(site_snip, "M-CSA reaction reactants")})
    for pid, _n in products:
        edges.append({"subject": "activity", "predicate": P_OUTPUT[0],
                      "predicate_id": P_OUTPUT[1], "object": pid,
                      "description": "Product formed by the reaction.",
                      "evidence": ev(site_snip, "M-CSA reaction products")})

    frame = (f"Residue nodes carry M-CSA/PDB author numbering; the UniProt "
             f"position in each label was verified against the reference "
             f"sequence (offset {offset:+d})." if offset is not None else
             "Residue nodes carry M-CSA/PDB author numbering only — no unique "
             "offset to the record's reference sequence could be verified, so "
             "no UniProt position is asserted.")
    shape = (f"Stepwise mechanism transcribed from M-CSA entry {mid} "
             f"({len(steps)} steps)." if stepwise else
             f"Mechanism transcribed from M-CSA entry {mid}. M-CSA does not "
             f"resolve this one into steps, so the whole mechanism is a single "
             f"node quoting its `mechanism_text`; residue edges are still "
             f"per-residue.")
    return {"graph_id": "catalysis",
            "title": f"Catalytic mechanism of {entry.get('enzyme_name') or 'the enzyme'}",
            "description": (f"{shape} Every edge quotes the M-CSA entry; M-CSA's "
                            f"primary references are in the edge notes. {frame}"),
            "nodes": nodes, "edges": edges}


def splice(text: str, graph: dict, mid: int) -> "tuple[str | None, str]":
    block = yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                           allow_unicode=True, width=100, default_flow_style=False)
    hist = yaml.safe_dump({"curation_history": [{
        "timestamp": "2026-07-29T00:00:00Z",
        "curator": "edison-causal-graphs",
        "action": (f"Added causal_graphs 'catalysis' ({len(graph['edges'])} "
                   f"evidence-backed edges) transcribed from M-CSA entry {mid}; "
                   f"SEEDED -> REVIEWED"),
        "llm_assisted": True}]}, sort_keys=False, allow_unicode=True, width=100)
    out = re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED",
                 text, count=1, flags=re.M)
    # Append into each section rather than inserting a fresh key: a record may
    # already carry another builder's graph (and its history), and a second
    # top-level `causal_graphs:` would make PyYAML silently keep only the last,
    # discarding the existing graph.
    spliced = append_to_section(out, "causal_graphs", block)
    if spliced == out:
        return None, "graph"
    out2 = append_to_section(spliced, "curation_history", hist)
    if out2 == spliced:
        return None, "history"
    return out2, ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write (default: dry run)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", type=int, help="a single MCSA id")
    args = ap.parse_args()

    cache, files, cath_ok = load_cache(), record_files(), kb_cath()
    # Counter, not dict: the refusal path increments a key the literal did not
    # declare, which raised KeyError instead of counting the skip.
    stat = collections.Counter({"written": 0, "skip_has_graph": 0, "no_mechanism": 0,
            "no_record": 0, "offset_ok": 0, "offset_unresolved": 0,
            "edges": 0, "nodes": 0})
    done = 0
    for mid in sorted(cache):
        if args.only and mid != args.only:
            continue
        if mid not in files:
            stat["no_record"] += 1
            continue
        path, text, seq = files[mid]
        try:
            seen = has_graph(text, "catalysis")
        except RecordError as exc:
            # One unreadable record must not abort a run that has already
            # written to earlier ones (#104). Warn with the path and skip.
            stat["skipped: record could not be read"] += 1
            print(f"  WARN unreadable {path}: {exc}", file=sys.stderr)
            continue
        if seen:
            stat["skip_has_graph"] += 1
            continue
        entry = cache[mid]
        residues = catalytic_residues(entry)
        offset = resolve_offset(residues, seq)
        stat["offset_ok" if offset is not None else "offset_unresolved"] += 1
        graph = build_graph(entry, residues, offset, cath_ok)
        if graph is None:
            stat["no_mechanism"] += 1
            continue
        # Report WHICH splice refused. Returning a bare None made the caller blame
        # the graph even when the graph went in fine and the history was refused —
        # diagnostic only, but it would have sent a reader to the wrong place.
        new, why = splice(text, graph, mid)
        if new is None:
            stat[f"skipped: could not splice the {why} into the record"] += 1
            continue
        stat["written"] += 1
        stat["edges"] += len(graph["edges"])
        stat["nodes"] += len(graph["nodes"])
        if args.apply:
            path.write_text(new, encoding="utf-8")
        elif done == 0:
            print(yaml.safe_dump({"causal_graphs": [graph]}, sort_keys=False,
                                 allow_unicode=True, width=100)[:3000])
        done += 1
        if args.limit and done >= args.limit:
            break

    for k, v in stat.items():
        print(f"  {k:<20} {v:,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
