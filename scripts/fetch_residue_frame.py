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

Feature types are routed to the same trait categories `seed_uniprot.py` targets,
so a sidecar interval is comparable to a record's own `trait_category` exactly as
a stored `features[]` entry would be. The routing table is *not* shared with that
seeder: it is keyed on UniProt's JSON labels rather than flat-file FT keywords,
and it deliberately drops two of the seeder's types (see `_UNROUTED`) because a
category match on them localizes falsely.

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
# A BINDING feature carries a ligand; a metal ligand routes to the metal-site
# category, the same re-route seed_uniprot.py applies.
#
# Matching bare element symbols with \b is wrong in both directions: a hyphen is
# a word boundary so "co-factor" matched cobalt, a stray capital matched
# potassium ("a K+ channel ligand"), and spelled-out metals were missed entirely
# ("sodium"). A symbol now only counts when it carries a charge or oxidation
# marker, which is how UniProt writes ions (`Zn(2+)`, `Fe cation`, `K(+)`), and
# the spelled-out names are listed explicitly. A misroute is one-directional
# damage: it fabricates a metal-site interval that then localizes a
# STRUCT_METAL_SITE record onto the wrong residues.
_METAL_SYMBOL = r"(?:zn|fe|mg|mn|ca|cu|co|ni|cd|mo|se|w|k|na)"
_METAL_RE = re.compile(
    rf"\b{_METAL_SYMBOL}\s*(?:\(\s*[0-9]*\s*[+-]\s*\)|[0-9]*\s*[+]|\s+(?:cation|ion))"
    r"|\b(?:zinc|iron|magnesium|manganese|calcium|copper|cobalt|nickel|cadmium|"
    r"molybdenum|potassium|sodium|tungsten|metal|heme iron)\b",
    re.I)

FIELDS = ("accession,sequence,ft_domain,ft_act_site,ft_binding,ft_site,"
          "ft_disulfid,ft_signal,ft_transit,ft_propep,ft_mod_res,ft_lipid,"
          "ft_carbohyd,ft_crosslnk,ft_motif,ft_compbias,ft_helix,ft_strand,"
          "ft_turn")

ORGANISMS = (9606, 10090, 7227, 6239, 3702, 559292, 36329, 83333, 224308, 243232)

TRAITS = REPO_ROOT / "data" / "traits"
# `\s*` not `\s+`: fetch_uniprot_examples.py writes its blocks through
# PyYAML, which emits list items at column 0 ("- protein_id:"). Requiring
# leading whitespace silently skipped 27,325 records — every UNIPROTKB_API
# exemplar block in the corpus.
_PID = re.compile(r"(?m)^\s*-\s+protein_id:\s*(\S+)")


def corpus_exemplars_missing(frame: dict) -> list:
    """Exemplar accessions referenced by records but absent from the sidecar.

    The ten proteomes cover the SWISSPROT_PROFILE picks, but CURATOR and
    UNIPROTKB_API exemplars point anywhere — 19,371 SEQ_EPITOPE records name an
    antigen outside them, and an epitope needs only its antigen's *sequence*
    because the peptide is already the record's `sequence_pattern`.
    """
    want = set()
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        i = text.find("\ncanonical_examples:")
        if i < 0:
            continue
        for pid in _PID.findall(text[i:]):
            acc = pid.split(":")[-1]
            if acc not in frame:
                want.add(acc)
    return sorted(want)


_dropped: list = []


def fetch_accessions(accs, batch: int = 100, sleep: float = 0.15):
    """Yield entries for an explicit accession list, 100 per request.

    Far cheaper than a proteome crawl for a scattered set: ~200 requests for
    ~20,000 proteins instead of one paged crawl per organism.
    """
    def _batch(chunk):
        """Fetch one chunk; on failure split it so one bad accession costs one.

        The endpoint rejects the whole request if any accession in it is
        malformed or withdrawn, so a flat retry loses the other 99 — which is
        exactly what a first run did. Splitting isolates the offender in
        log2(100) ≈ 7 extra requests instead of discarding the batch.
        """
        url = ("https://rest.uniprot.org/uniprotkb/accessions?"
               + urllib.parse.urlencode({"accessions": ",".join(chunk),
                                         "fields": FIELDS, "format": "json"}))
        data, _ = _get(url)
        if data is not None:
            yield from (data.get("results") if isinstance(data, dict) else data) or []
            return
        if len(chunk) == 1:
            # An accession the endpoint will never serve — malformed or
            # withdrawn. That is a fact about the corpus, not a fetch failure,
            # so it is reported but must not block the write (issue #54).
            _dropped.append(chunk[0])
            return
        mid = len(chunk) // 2
        time.sleep(sleep)
        yield from _batch(chunk[:mid])
        time.sleep(sleep)
        yield from _batch(chunk[mid:])

    for i in range(0, len(accs), batch):
        yield from _batch(accs[i:i + batch])
        time.sleep(sleep)


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


def stream(query: str, limit: int, page: int = 200, status: dict | None = None):
    """Yield entries; record {"complete": bool, "expected": int} in `status`.

    A failed page ends the crawl for this query. Without a status flag that
    truncation is invisible: the sidecar is written, the count looks plausible
    (the ten proteomes span 321 to 20,431 entries, so a short one does not stand
    out) and Path 1 simply finds fewer edges — indistinguishable from those
    records genuinely having no features (issue #53).
    """
    url = ("https://rest.uniprot.org/uniprotkb/search?"
           + urllib.parse.urlencode({"query": query, "fields": FIELDS,
                                     "format": "json", "size": min(page, 500)}))
    got = 0
    if status is not None:
        status.update({"complete": True, "expected": None})
    while url and got < limit:
        data, link = _get(url)
        if not data:
            if status is not None:
                status["complete"] = False
            break
        if status is not None and status.get("expected") is None:
            status["expected"] = data.get("total") 
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
            # Test `ligand.name` — the authoritative field — and fall back to the
            # free-text description only when there is no ligand. Testing both
            # together let prose about the protein decide the ligand's identity:
            # "a K+ channel ligand" names potassium but is not a potassium ligand.
            lig = ((f.get("ligand") or {}).get("name") or "").strip()
            if not lig:
                lig = f.get("description") or ""
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
    ap.add_argument("--top-up", action="store_true",
                    help="after the queries, fetch every exemplar accession the "
                         "corpus references that is still missing (CURATOR / "
                         "UNIPROTKB_API picks outside the ten proteomes)")
    ap.add_argument("--allow-partial", action="store_true",
                    help="write even if a query's pagination aborted early")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    queries = list(args.query or [])
    if args.organisms:
        queries += [f"reviewed:true AND organism_id:{t}" for t in ORGANISMS]

    frame: dict = {}
    outp_existing = Path(args.out)
    if args.top_up and not queries and outp_existing.exists():
        # top-up alone extends the sidecar in place rather than re-crawling the
        # proteomes that built it
        frame = json.loads(outp_existing.read_text(encoding="utf-8"))
        print(f"loaded {len(frame):,} proteins from {outp_existing.name}",
              file=sys.stderr)
    elif not queries:
        queries = ["reviewed:true AND organism_id:9606"]

    n_ft = 0
    if not args.apply:
        # A dry run must not hit the network. It previously streamed every
        # proteome and only gated the *write*, so "dry run" cost a full crawl
        # and, with --top-up, ~200 more requests.
        print(f"planned queries ({len(queries)}):")
        for q in queries:
            print(f"    {q}")
        if args.top_up:
            missing = corpus_exemplars_missing(frame)
            print(f"top-up would fetch {len(missing):,} exemplar accessions "
                  f"not yet in the frame")
        print(f"frame currently holds {len(frame):,} proteins")
        print("Dry-run — pass --apply to fetch and write.")
        return 0

    incomplete = []
    for q in queries:
        before = len(frame)
        st: dict = {}
        for entry in stream(q, args.limit, status=st):
            acc = entry.get("primaryAccession")
            if not acc or acc in frame:
                continue
            seq = ((entry.get("sequence") or {}).get("value")) or ""
            ft = entry_intervals(entry)
            n_ft += len(ft)
            frame[acc] = {"seq": seq, "ft": ft}
        if not st.get("complete", True):
            incomplete.append(q)
        print(f"  {q!r}: +{len(frame)-before:,}"
              + ("  ** INCOMPLETE — pagination aborted **" if not st.get("complete", True) else ""),
              file=sys.stderr)

    if args.top_up:
        missing = corpus_exemplars_missing(frame)
        print(f"top-up: {len(missing):,} exemplar accessions not yet in the frame",
              file=sys.stderr)
        _dropped.clear()
        got = 0
        for entry in fetch_accessions(missing):
            if entry is None:
                continue
            acc = entry.get("primaryAccession")
            if not acc or acc in frame:
                continue
            ft = entry_intervals(entry)
            n_ft += len(ft)
            frame[acc] = {"seq": ((entry.get("sequence") or {}).get("value")) or "",
                          "ft": ft}
            got += 1
        print(f"top-up: +{got:,} proteins", file=sys.stderr)
        if _dropped:
            print(f"top-up: {len(_dropped)} accession(s) the endpoint would not "
                  f"serve — these are corpus data errors, not fetch failures "
                  f"(see issue #54): {', '.join(sorted(_dropped)[:12])}",
                  file=sys.stderr)

    with_seq = sum(1 for v in frame.values() if v["seq"])
    with_ft = sum(1 for v in frame.values() if v["ft"])
    print(f"proteins: {len(frame):,} | with sequence: {with_seq:,} | "
          f"with >=1 routed feature: {with_ft:,} | intervals: {n_ft:,}")
    if incomplete:
        print(f"\n{len(incomplete)} of {len(queries)} queries ended early "
              f"(network failure after retries):", file=sys.stderr)
        for q in incomplete:
            print(f"    {q}", file=sys.stderr)
        if not args.allow_partial:
            print("refusing to write a partial sidecar — re-run, or pass "
                  "--allow-partial to accept it.", file=sys.stderr)
            return 1
        print("--allow-partial given; writing anyway.", file=sys.stderr)
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
