#!/usr/bin/env python3
"""Residue-frame sidecar for the exemplar proteins (issue #7, phase 10).

`build_sequence_structure_alignment.py` (Path 1) links two trait records when
they share a `canonical_examples` protein **and overlap on that protein's UniProt
residue coordinates**. Its offline `stored` provider reads those coordinates from
`canonical_examples[].sequence` and `[].features`.

Phases 5-9 added `SWISSPROT_PROFILE` exemplars to ~131,700 records, which made
34,227 proteins shared by two or more records — a large new supply of candidate
pairs. But those exemplars carry no sequence and no features: **33 records in the
whole corpus have a stored sequence.** So Path 1 cannot see any of it.

Inlining sequences and feature tables into every record would repeat the same
protein hundreds of times (one protein is an exemplar of up to 574 records) and
add tens of MB of YAML. This fetches them once into a sidecar keyed by accession
instead, which a new `profile` provider reads.

Output: `data/raw/align_cache/residue_frame.json` (gitignored, regenerable)
  {"<ACC>": {"seq": "MSTA…", "ft": [[start, end, "<trait_category>"], …]}, …}

Feature types are routed to trait categories with the same table
`seed_uniprot.py` uses, so a sidecar interval is comparable to a record's own
`trait_category` exactly as a stored `features[]` entry would be.

Bounded by --query / --organisms (same shorthand as build_swissprot_profiles).
Dry-run unless --apply. Stdlib-only.

  just fetch-residue-frame --organisms --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "data" / "raw" / "align_cache" / "residue_frame.json"

# UniProt's JSON feature `type` is a human-readable label ("Active site",
# "Disulfide bond"), NOT the flat-file FT keyword ("ACT_SITE", "DISULFID"). Keys
# here are those labels normalised to lowercase alphanumerics, because keying off
# the flat-file names silently dropped active sites, binding sites, modified
# residues, disulfides and glycosylation — every category Path 1 most needs.
FT_CATEGORY = {
    "activesite":       "STRUCT_ACTIVE_SITE",
    "bindingsite":      "STRUCT_BINDING_SITE",   # re-routed to metal below
    "site":             "STRUCT_BINDING_SITE",
    "disulfidebond":    "STRUCT_DISULFIDE",
    "modifiedresidue":  "SEQ_MODIFIED_RESIDUE",
    "glycosylation":    "SEQ_GLYCOSYLATION_SITE",
    "lipidation":       "SEQ_LIPIDATION_SITE",
    "crosslink":        "SEQ_CROSSLINK_SITE",
    "signal":           "SEQ_SIGNAL_PEPTIDE",
    "transitpeptide":   "SEQ_TRANSIT_PEPTIDE",
    "propeptide":       "SEQ_PROPEPTIDE",
    "compositionalbias": "SEQ_COMPOSITION",
    "motif":            "SEQ_MOTIF",
    "shortsequencemotif": "SEQ_MOTIF",
}

# Deliberately NOT routed, because a category match would localize a record
# falsely rather than precisely:
#   • Domain — 12,055 of 30,574 proteins carry more than one, so a category match
#     would assign a record every domain of the protein rather than its own. The
#     right coordinate source for a domain/family record is the `interpro`
#     provider, which knows *which* signature matched *where*.
#   • Helix / Beta strand / Turn — per-protein secondary-structure elements, tens
#     per protein (they were 75% of a first cut's intervals). Matching a
#     STRUCT_SECONDARY record to all of them localizes nothing meaningful.
_UNROUTED = {"domain", "helix", "betastrand", "turn"}
# BINDING carries a ligand; a metal ligand routes to the metal-site category,
# the same re-route seed_uniprot.py applies.
_METAL_RE = re.compile(r"\b(zn|fe|mg|mn|ca|cu|co|ni|cd|k|na|metal)\b", re.I)

FIELDS = ("accession,sequence,ft_domain,ft_act_site,ft_binding,ft_site,"
          "ft_disulfid,ft_signal,ft_transit,ft_propep,ft_mod_res,ft_lipid,"
          "ft_carbohyd,ft_crosslnk,ft_motif,ft_compbias,ft_helix,ft_strand,"
          "ft_turn")

ORGANISMS = (9606, 10090, 7227, 6239, 3702, 559292, 36329, 83333, 224308, 243232)


def _get(url: str, tries: int = 4):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "ProteinTraitsMech-residue-frame/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8")), r.headers.get("Link", "")
        except Exception as e:                       # noqa: BLE001
            if i == tries - 1:
                print(f"  fetch failed: {e}", file=sys.stderr)
                return None, ""
            time.sleep(2.0 * (i + 1))
    return None, ""


def stream(query: str, limit: int, page: int = 200):
    url = ("https://rest.uniprot.org/uniprotkb/search?"
           + urllib.parse.urlencode({"query": query, "fields": FIELDS,
                                     "format": "json", "size": min(page, 500)}))
    got = 0
    while url and got < limit:
        data, link = _get(url)
        if not data:
            break
        for e in data.get("results", []):
            yield e
            got += 1
            if got >= limit:
                return
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
        time.sleep(0.15)


def entry_intervals(entry: dict) -> list:
    """[[start, end, trait_category], …] for the supported FT types."""
    out = []
    for f in entry.get("features") or []:
        t = re.sub(r"[^a-z0-9]", "", (f.get("type") or "").lower())
        if not t or t in _UNROUTED:
            continue
        loc = f.get("location") or {}
        s = (loc.get("start") or {}).get("value")
        e = (loc.get("end") or {}).get("value")
        if s is None or e is None:
            continue
        cat = FT_CATEGORY.get(t)
        if cat == "STRUCT_BINDING_SITE":
            lig = (((f.get("ligand") or {}).get("name") or "") + " "
                   + (f.get("description") or ""))
            if _METAL_RE.search(lig):
                cat = "STRUCT_METAL_SITE"
        if not cat:
            continue
        out.append([int(s), int(e), cat])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", action="append", metavar="Q")
    ap.add_argument("--organisms", action="store_true",
                    help="the ten proteomes of the standard matrix")
    ap.add_argument("--limit", type=int, default=25000, help="cap per query")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    queries = list(args.query or [])
    if args.organisms:
        queries += [f"reviewed:true AND organism_id:{t}" for t in ORGANISMS]
    if not queries:
        queries = ["reviewed:true AND organism_id:9606"]

    frame: dict = {}
    n_ft = 0
    for q in queries:
        before = len(frame)
        for entry in stream(q, args.limit):
            acc = entry.get("primaryAccession")
            if not acc or acc in frame:
                continue
            seq = ((entry.get("sequence") or {}).get("value")) or ""
            ft = entry_intervals(entry)
            n_ft += len(ft)
            frame[acc] = {"seq": seq, "ft": ft}
        print(f"  {q!r}: +{len(frame)-before:,}", file=sys.stderr)

    with_seq = sum(1 for v in frame.values() if v["seq"])
    with_ft = sum(1 for v in frame.values() if v["ft"])
    print(f"proteins: {len(frame):,} | with sequence: {with_seq:,} | "
          f"with >=1 routed feature: {with_ft:,} | intervals: {n_ft:,}")
    if not args.apply:
        print("Dry-run — pass --apply to write.")
        return 0
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(frame, separators=(",", ":")), encoding="utf-8")
    try:
        shown = outp.relative_to(REPO_ROOT)
    except ValueError:
        shown = outp
    print(f"WROTE {shown} ({outp.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
