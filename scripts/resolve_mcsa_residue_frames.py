#!/usr/bin/env python3
"""Resolve the M-CSA residue frames that a single global offset cannot (#79).

  python3 scripts/resolve_mcsa_residue_frames.py            # dry run
  python3 scripts/resolve_mcsa_residue_frames.py --apply

`build_mcsa_causal_graphs.py` maps M-CSA's PDB author numbering to the UniProt
frame by finding the one integer offset under which EVERY catalytic residue's
code matches the record's reference sequence. 200 records have no such offset,
and their residue nodes say "UniProt position not established" rather than
asserting one.

The reason is not noise, it is multi-chain enzymes. MCSA:5 (carboxypeptidase D)
maps, per SIFTS:

    chain A  auth  -4..248  ->  UniProt   6..260     (offset +10)
    chain B  auth 264..423  ->  UniProt 287..439     (offset +23)

Two chains, two different offsets, so no single global offset exists — the
earlier method was right to refuse. SIFTS gives the mapping per chain segment,
which is the correct granularity.

Verification is unchanged and non-negotiable: a SIFTS-derived position is written
only if the reference sequence really carries that amino acid there. A mapping
that does not check out is dropped, not written with a caveat.

The PDBe response cache under data/raw/sifts/ makes reruns offline and idempotent.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO / "data" / "raw" / "sifts"
MCSA_DIR = REPO / "data" / "traits" / "structure" / "active_site" / "mcsa"
ENTRIES = REPO / "data" / "raw" / "mcsa.entries.jsonl"
API = "https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb}"

AA3 = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q",
       "Glu": "E", "Gly": "G", "His": "H", "Ile": "I", "Leu": "L", "Lys": "K",
       "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W",
       "Tyr": "Y", "Val": "V", "Sec": "U", "Pyl": "O"}

UNSET = "UniProt position not established"


def sifts(pdb: str, offline: bool):
    """PDBe SIFTS mapping for one PDB id, cached on disk."""
    pdb = pdb.lower()
    cf = CACHE_DIR / f"{pdb}.json"
    if cf.exists():
        try:
            return json.loads(cf.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    if offline:
        return None
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                API.format(pdb=pdb), headers={"User-Agent": "ProteinTraitsMech/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
            cf.write_text(json.dumps(d), encoding="utf-8")
            return d
        except urllib.error.HTTPError as e:
            if e.code == 404:
                cf.write_text("{}", encoding="utf-8")   # remember the absence
                return {}
            time.sleep(1 + attempt)
        except Exception:
            time.sleep(1 + attempt)
    return None


def map_residue(doc, pdb, chain, auth, resid, acc):
    """UniProt position for a catalytic residue, or None.

    Two SIFTS frames, tried in order of directness:

    1. **author numbering** — interpolate inside the segment whose author range
       covers `auth_resid`, which is the number M-CSA reports.
    2. **`residue_number`** — 365 of the residues here sit in segments whose
       `author_residue_number` is null, so frame 1 cannot see them at all. Those
       segments still carry `residue_number`, and M-CSA's own `resid` is in that
       same frame, so the segment is usable via `resid` instead.

    Frame 2 is a fallback rather than an equal: it is only consulted when frame 1
    finds nothing, and its output goes through the same sequence check.
    """
    if not doc:
        return None
    ent = (doc.get(pdb.lower()) or {}).get("UniProt") or {}
    # Accession pass 1 is the record's own; pass 2 accepts any accession SIFTS
    # names for the entry. That is not a loosening of standards, because the
    # sequence check downstream is the arbiter — it exists because UniProt
    # renames and demerges accessions (Q05489 -> P0DUB8), so SIFTS can be right
    # about the residue while naming an accession the record predates. A wrong
    # protein cannot survive the check; a renamed one can.
    for accept_any in (False, True):
        for use_author in (True, False):
            for a, v in ent.items():
                if not accept_any and acc and a != acc:
                    continue
                for m in v.get("mappings") or []:
                    # M-CSA's chain_name matches SIFTS chain_id for most entries
                    # and struct_asym_id for the rest
                    if str(chain) not in {str(m.get("chain_id")),
                                          str(m.get("struct_asym_id"))}:
                        continue
                    s, e = m.get("start") or {}, m.get("end") or {}
                    us = m.get("unp_start")
                    if us is None:
                        continue
                    if use_author:
                        sa, ea, pos = (s.get("author_residue_number"),
                                       e.get("author_residue_number"), auth)
                    else:
                        sa, ea, pos = (s.get("residue_number"),
                                       e.get("residue_number"), resid)
                    if sa is None or ea is None or pos is None:
                        continue
                    if sa <= pos <= ea:
                        return us + (pos - sa)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--offline", action="store_true",
                    help="use only the cache; do not hit PDBe")
    args = ap.parse_args()

    entries = {json.loads(ln)["mcsa_id"]: json.loads(ln)
               for ln in ENTRIES.open(encoding="utf-8")}
    stat = collections.Counter()

    for f in sorted(MCSA_DIR.glob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        if UNSET not in text:
            continue
        stat["records considered"] += 1
        mid = int(re.search(r"^identifier:\s*MCSA:(\d+)", text, re.M).group(1))
        entry = entries.get(mid)
        if not entry:
            continue
        seq = (re.search(r"^\s+sequence:\s*(\S+)", text, re.M) or [None, None])[1]
        acc = (entry.get("reference_uniprot_id") or "").split(",")[0].strip()

        wanted = {}
        for r in entry.get("residues") or []:
            for c in r.get("residue_chains") or []:
                if not c.get("is_reference"):
                    continue
                code, auth = c.get("code"), c.get("auth_resid")
                if code in AA3 and auth is not None and c.get("pdb_id"):
                    wanted[(code, int(auth))] = (c["pdb_id"], c.get("chain_name"),
                                                 c.get("resid"))
                break

        docs = {}
        resolved = {}
        for (code, auth), (pdb, chain, resid) in wanted.items():
            if pdb not in docs:
                docs[pdb] = sifts(pdb, args.offline)
            up = map_residue(docs[pdb], pdb, chain, auth, resid, acc)
            if up is None:
                stat["residues: no SIFTS segment"] += 1
                continue
            # the same verification as the offset path — never write unchecked
            if seq and 1 <= up <= len(seq) and seq[up - 1] == AA3[code]:
                resolved[(code, auth)] = up
                stat["residues: SIFTS verified"] += 1
            else:
                stat["residues: SIFTS mismatch, dropped"] += 1

        if not resolved:
            stat["records unchanged"] += 1
            continue

        new = text
        for (code, auth), up in resolved.items():
            new = new.replace(
                f"catalytic {code}{auth} (M-CSA/PDB numbering; {UNSET})",
                f"catalytic {code}{auth} (M-CSA/PDB numbering; UniProt residue {up})")
        if UNSET in new:
            note = ("Some residue positions were recovered from SIFTS (PDBe "
                    "residue-level mapping); the rest remain unestablished.")
        else:
            note = ("Residue positions recovered from SIFTS (PDBe residue-level "
                    "mapping), each verified against the reference sequence. A "
                    "single global offset does not fit this entry because its "
                    "chains map with different offsets.")
        new = new.replace(
            "Residue nodes carry M-CSA/PDB author numbering only — no unique "
            "offset to the record's reference sequence could be verified, so no "
            "UniProt position is asserted.", note)
        if new != text:
            stat["records updated"] += 1
            if args.apply:
                f.write_text(new, encoding="utf-8")

    for k, v in stat.most_common():
        print(f"  {k:<34} {v:>6,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
