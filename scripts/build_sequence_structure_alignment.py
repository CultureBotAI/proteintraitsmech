#!/usr/bin/env python3
"""Cross-axis residue-frame alignment overlay — SEQUENCE ↔ STRUCTURE ↔ function sites.

The corpus splits records by *representation axis* (a Pfam/PROSITE signature is
SEQUENCE; a CATH/ECOD fold or an M-CSA/BioLiP/MetalPDB site is STRUCTURE), so the
two views of one protein region are never connected. This builder finds records
that share an **exact canonical-example `protein_id`** and whose annotations
**overlap on that protein's UniProt residue coordinates**, and emits typed
cross-axis relationship edges.

Cross-axis pairs are a *relationship, never a merge* (per the merge-within-axis /
merge-traits skills), so this only ever writes `trait_relations`-style overlay
edges (loaded bidirectionally by build_docs_index.py, same as the other
equivalence overlays). Two overlays are written:
  • `data/equivalence/seq_struct_alignment.tsv`  — signature/domain/fold edges
    (neither endpoint a residue-localized *function site*);
  • `data/equivalence/seq_struct_func_sites.tsv` — **Path 1**: edges where at
    least one endpoint is a residue-localized FUNCTION site (active/binding/metal/
    cleavage/PTM). This is the three-way alignment's residue-frame path
    (research/sequence-structure-function-alignment-analysis-1.md §2, path 1):
    function sites ↔ each other and ↔ the SEQ signatures / STRUCT folds that host
    them, all on the shared UniProt residue frame.

Coordinate providers (`--providers`, comma list, union; default `stored` =
offline). A record is localized on each exemplar protein by any active provider:
  • `stored`   — `sequence_pattern` regex hits against the stored
    `canonical_examples[].sequence` (PROSITE syntax → regex), plus
    `canonical_examples[].features[]` intervals whose `trait_category` equals the
    record's own (e.g. an M-CSA STRUCT_ACTIVE_SITE record picks up its exemplar's
    ACT_SITE residues — 606 of them carry these). Offline; the default.
  • `interpro` — InterPro API match locations for a member-DB signature record
    (Pfam/InterPro/SMART/…) on each exemplar UniProt protein — already in UniProt
    numbering, so it localizes SEQUENCE domain/family records with no stored
    pattern.
  • `sifts`    — PDBe SIFTS UniProt residues covered by a STRUCTURE record's
    `structural_geometry_representations.structure_ref` PDB (author/label → UniProt;
    coarse: the mapped segment). NOTE: a no-op on the current corpus — STRUCT_FOLD
    records that carry protein_id exemplars use AlphaFoldDB refs (TED), and the
    PDB-geo records (3did interfaces) carry no exemplars, so nothing matches. A
    future AlphaFold/TED localizer could use the stored `residue_range` (AlphaFold
    numbering = UniProt, no SIFTS needed); those proteins still share none with
    signature records, so signature↔fold links come from the co-membership overlay
    (build_seq_struct_comembership.py), not here.
  • `biolip`   — **Path 1's workhorse for STRUCT_BINDING_SITE**: parse the receptor
    binding residues from a BioLiP record's `canonical_examples[].note`
    ("… in PDB <id> chain <X> …; binding residues: I302 I432 E449") and map each
    PDB-author residue → UniProt via SIFTS. Localizes the ~5.5k BioLiP binding-site
    records that store residues as prose, not structured features. Needs network.
interpro/sifts/biolip query external APIs and cache to `data/raw/align_cache/`; a
full run is a deliberate cached crawl, so they are off by default.

Predicate ladder (relate-only): identical residue set → `biolink:related_to`
(same physical feature by two representations); full containment (region×region) →
`biolink:part_of` (subject = the contained/smaller record); any other non-empty
overlap → `biolink:overlaps`. For *site* categories (active/binding/metal/cleavage/
PTM) any shared residue is meaningful; for region×region a reciprocal-overlap /
Jaccard floor applies.

Function sites also align **same-axis, cross-category** (e.g. a STRUCT_ACTIVE_SITE
coinciding with a STRUCT_METAL_SITE, or a SEQ_ACTIVE_SITE with a SEQ_CLEAVAGE_SITE)
— never same-axis *same-category* (that is a within-axis merge question, owned by
the merge-within-axis skill), and never a merge.

Idempotent (fixed input + fixed cache → identical TSVs). Stdlib + PyYAML. Read-only
w.r.t. records/schema; writes only the overlay TSVs (+ the API cache).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT_BASE = REPO_ROOT / "data" / "equivalence" / "seq_struct_alignment.tsv"
OUT_FUNC = REPO_ROOT / "data" / "equivalence" / "seq_struct_func_sites.tsv"
CACHE_DIR = REPO_ROOT / "data" / "raw" / "align_cache"

# Record identifier prefix → InterPro member-database slug for the API.
MEMBERDB = {
    "InterPro": "interpro", "Pfam": "pfam", "SMART": "smart", "CDD": "cdd",
    "PRINTS": "prints", "PANTHER": "panther", "NCBIfam": "ncbifam",
    "PIRSF": "pirsf", "HAMAP": "hamap", "SFLD": "sfld", "PROSITE": "prosite",
    "CATH": "cathgene3d", "SUPERFAMILY": "ssf",
}

# Residue-localized FUNCTION sites (the Path-1 categories). Their axis follows the
# representation (M-CSA/BioLiP/MetalPDB are STRUCTURE; UniProt/InterPro sites are
# SEQUENCE), but the biology they carry is function. An edge touching any of these
# is routed to the function-site overlay.
FUNC_SITE_CATS = {
    "SEQ_ACTIVE_SITE", "SEQ_BINDING_SITE", "SEQ_CLEAVAGE_SITE", "SEQ_PTM_SITE",
    "SEQ_MODIFIED_RESIDUE", "SEQ_GLYCOSYLATION_SITE", "SEQ_CROSSLINK_SITE",
    "SEQ_LIPIDATION_SITE",
    "STRUCT_ACTIVE_SITE", "STRUCT_BINDING_SITE", "STRUCT_METAL_SITE",
}
# Site categories: few residues, so ANY shared residue is a real correspondence
# (no region-overlap floor). Superset of FUNC_SITE_CATS minus cleavage, which is a
# specificity motif rather than a point.
SITE_CATS = FUNC_SITE_CATS - {"SEQ_CLEAVAGE_SITE"}
REGION_MIN_RECIPROCAL = 0.80   # region×region: strong reciprocal overlap …
REGION_MIN_JACCARD = 0.20      # … or this Jaccard floor


class Http:
    """Tiny cached GET-JSON client for the InterPro + PDBe SIFTS providers.
    Caches per-URL to a JSON file so re-runs (and partial runs) don't re-query;
    misses/404s are cached as null so absent mappings aren't re-fetched."""

    def __init__(self, cache_path: Path, sleep: float = 0.2):
        self.cache_path = cache_path
        self.sleep = sleep
        self.cache: dict = {}
        self.dirty = self.hits = self.misses = 0
        if cache_path.exists():
            try:
                self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                self.cache = {}

    def get(self, url: str):
        if url in self.cache:
            self.hits += 1
            return self.cache[url]
        self.misses += 1
        val = None
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "ProteinTraitsMech-align/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                val = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                print(f"  http {e.code}: {url}", file=sys.stderr)
        except (urllib.error.URLError, ValueError, TimeoutError, OSError) as e:
            print(f"  http err: {url} ({e})", file=sys.stderr)
        self.cache[url] = val
        self.dirty += 1
        if self.sleep:
            time.sleep(self.sleep)
        return val

    def flush(self):
        if self.dirty:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")
            self.dirty = 0


def _up_acc(uniprot: str) -> str:
    """`UniProtKB:P12345-2` → `P12345` (strip prefix + isoform)."""
    return uniprot.split(":", 1)[-1].split("-")[0]


def interpro_residues(prefix: str, acc: str, uniprot: str, http: Http) -> set[int]:
    """Residues a member-DB signature (Pfam/InterPro/SMART/…) matches on a UniProt
    protein, from the InterPro API (already in UniProt numbering — no SIFTS)."""
    db = MEMBERDB.get(prefix)
    if not db:
        return set()
    up = _up_acc(uniprot)
    url = f"https://www.ebi.ac.uk/interpro/api/protein/uniprot/{up}/entry/{db}/{acc}/"
    data = http.get(url)
    res: set[int] = set()
    if not isinstance(data, dict):
        return res
    for e in (data.get("entries") or []):
        for loc in (e.get("entry_protein_locations") or []):
            for fr in (loc.get("fragments") or []):
                try:
                    s, en = int(fr["start"]), int(fr["end"])
                except (KeyError, TypeError, ValueError):
                    continue
                res |= set(range(min(s, en), max(s, en) + 1))
    return res


def _sifts_mappings(pdb: str, http: Http):
    """Raw PDBe SIFTS UniProt mappings for a PDB id, or []."""
    data = http.get(f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb.lower()}")
    try:
        return data[pdb.lower()]["UniProt"]
    except (KeyError, TypeError):
        return {}


def sifts_residues(pdb: str, uniprot: str, http: Http) -> set[int]:
    """UniProt residues a PDB structure covers for a given accession, via PDBe
    SIFTS (coarse: the mapped segment(s), i.e. the region this structure resolves)."""
    up = _up_acc(uniprot)
    res: set[int] = set()
    for m in (_sifts_mappings(pdb, http).get(up, {}) or {}).get("mappings", []):
        try:
            s, e = int(m["unp_start"]), int(m["unp_end"])
        except (KeyError, TypeError, ValueError):
            continue
        res |= set(range(min(s, e), max(s, e) + 1))
    return res


def sifts_author_to_unp(pdb: str, uniprot: str, chain: str | None, http: Http):
    """Per-segment (author_lo, author_hi, author→unp offset) for a PDB/UniProt
    (optionally one chain), so a specific PDB author residue number can be mapped
    to UniProt numbering. offset = unp_start - author_start within each segment."""
    up = _up_acc(uniprot)
    segs = []
    for m in (_sifts_mappings(pdb, http).get(up, {}) or {}).get("mappings", []):
        if chain and m.get("chain_id") != chain:   # exact chain; no wrong-segment maps
            continue
        try:
            a_lo = int(m["start"]["author_residue_number"])
            a_hi = int(m["end"]["author_residue_number"])
            unp_s = int(m["unp_start"])
        except (KeyError, TypeError, ValueError):
            continue
        segs.append((min(a_lo, a_hi), max(a_lo, a_hi), unp_s - a_lo))
    return segs


def _map_author_residues(auth_nums, segs) -> set[int]:
    out: set[int] = set()
    for r in auth_nums:
        for lo, hi, off in segs:
            if lo <= r <= hi:
                out.add(r + off)
                break
    return out


# BioLiP note: "… in PDB 8fxi chain C (resolution 2.7 Å); binding residues: I302 I432 E449"
_BIOLIP_PDB = re.compile(r"\bPDB\s+([0-9a-zA-Z]{4})\b(?:\s+chain\s+(\w+))?", re.I)
_BIOLIP_RES = re.compile(r"binding\s+residues?:?\s*([^;.\n]+)", re.I)
# A residue token is one amino-acid letter + a bare author number. Tokens with a
# trailing insertion code (e.g. `H432A`) are intentionally NOT matched — mapping
# them by the number alone would collide with a genuine residue 432, so they are
# skipped (drop, never mis-map).
_RESTOKEN = re.compile(r"^[A-Za-z](\d+)$")


def biolip_note_residues(rec: dict, http: Http) -> dict[str, set[int]]:
    """{protein_id: UniProt residue set} from a BioLiP record's exemplar notes —
    parse the receptor binding residues (PDB author numbering) and map to UniProt
    via SIFTS for the cited PDB/chain."""
    out: dict[str, set[int]] = {}
    for ex in (rec.get("canonical_examples") or []):
        pid = ex.get("protein_id")
        note = ex.get("note") or ""
        if not pid or "binding residues" not in note.lower():
            continue
        mpdb = _BIOLIP_PDB.search(note)
        mres = _BIOLIP_RES.search(note)
        if not (mpdb and mres):
            continue
        pdb, chain = mpdb.group(1), mpdb.group(2)
        auth = [int(m.group(1)) for tok in re.split(r"[\s,]+", mres.group(1).strip())
                if (m := _RESTOKEN.match(tok))]
        if not auth:
            continue
        segs = sifts_author_to_unp(pdb, pid, chain, http)
        res = _map_author_residues(auth, segs)
        if res:
            out.setdefault(pid, set()).update(res)
    return out


def prosite_to_regex(pattern: str) -> str | None:
    """Convert a PROSITE pattern (e.g. `[SA]-x(2)-{P}-L.`) to a Python regex.
    x=any, x(n)/x(n,m)=repeat, [..]=one of, {..}=none of, <=N-term, >=C-term.
    Returns None for non-positional patterns (e.g. a MEROPS `… | …` consensus)."""
    p = (pattern or "").strip().rstrip(".")
    if not p or "|" in p:          # scissile-bond markers etc. aren't a regex
        return None
    p = p.replace("-", "")
    p = p.replace("{", "[^").replace("}", "]")   # negation set (before repeats)
    p = p.replace("(", "{").replace(")", "}")     # repetition count
    p = p.replace("x", ".").replace("X", ".")
    p = p.replace("<", "^").replace(">", "$")
    try:
        re.compile(p)
    except re.error:
        return None
    return p


def _feature_residues(feat: dict) -> set[int]:
    try:
        s, e = int(feat["start"]), int(feat["end"])
    except (KeyError, TypeError, ValueError):
        return set()
    return set(range(min(s, e), max(s, e) + 1)) if s and e else set()


def located_residues(rec: dict, providers=("stored",),
                     http: "Http | None" = None) -> dict[str, set[int]]:
    """{protein_id: residue set} where this record's own trait falls on each
    exemplar, unioned across the active providers (stored / interpro / sifts /
    biolip)."""
    cat = rec.get("trait_category")
    prefix, _, acc = (rec.get("identifier") or "").partition(":")
    pat = rec.get("sequence_pattern")
    rx = prosite_to_regex(pat) if pat else None
    pdbs = []
    if "sifts" in providers:
        for g in (rec.get("structural_geometry_representations") or []):
            sr = g.get("structure_ref", "") if isinstance(g, dict) else ""
            if sr.startswith("PDB:"):
                pdbs.append(sr.split(":", 1)[1])
    out: dict[str, set[int]] = {}
    if http and "biolip" in providers and cat == "STRUCT_BINDING_SITE":
        for pid, res in biolip_note_residues(rec, http).items():
            out.setdefault(pid, set()).update(res)
    for ex in (rec.get("canonical_examples") or []):
        pid = ex.get("protein_id")
        if not pid:
            continue
        res: set[int] = set()
        if "stored" in providers:
            seq = ex.get("sequence")
            if rx and seq:
                for m in re.finditer(rx, seq):
                    res |= set(range(m.start() + 1, m.end() + 1))  # 1-indexed
            for f in (ex.get("features") or []):
                if isinstance(f, dict) and f.get("trait_category") == cat:
                    res |= _feature_residues(f)
        if http and "interpro" in providers and prefix in MEMBERDB and acc:
            res |= interpro_residues(prefix, acc, pid, http)
        if http and "sifts" in providers and pdbs:
            for pdb in pdbs:
                res |= sifts_residues(pdb, pid, http)
        if res:
            out.setdefault(pid, set()).update(res)
    return out


# Predicate strength for keeping the best edge when a pair overlaps on several
# proteins (related_to > part_of > overlaps).
PRED_RANK = {"biolink:related_to": 3, "biolink:part_of": 2, "biolink:overlaps": 1}


def classify(a: set[int], b: set[int], cat_a: str, cat_b: str):
    """(predicate, metric, a_is_subject) for an overlapping residue-set pair, or
    None. `a_is_subject` gives the directed orientation (matters for the asymmetric
    `part_of`; subject = the contained/smaller record)."""
    inter = a & b
    if not inter:
        return None
    if a == b:
        return "biolink:related_to", f"same-residues={len(inter)}", True
    site = cat_a in SITE_CATS or cat_b in SITE_CATS
    if not site:
        # Containment: the smaller region lies wholly inside the larger → part_of.
        if len(inter) == min(len(a), len(b)):
            a_is_subject = len(a) <= len(b)          # smaller set is the subject
            return "biolink:part_of", f"contained={len(inter)}", a_is_subject
        recip = min(len(inter) / len(a), len(inter) / len(b))
        jacc = len(inter) / len(a | b)
        if recip < REGION_MIN_RECIPROCAL and jacc < REGION_MIN_JACCARD:
            return None
    return "biolink:overlaps", f"inter={len(inter)}", True


def _comparable(axis_a: str, cat_a: str, axis_b: str, cat_b: str) -> bool:
    """Which same-protein record pairs to compare: cross-axis (SEQUENCE×STRUCTURE),
    OR same-axis but different category with at least one function-site endpoint.
    Never same category (that is a within-axis *merge* question, not an alignment)."""
    if cat_a == cat_b:
        return False
    if axis_a != axis_b:
        return True
    return cat_a in FUNC_SITE_CATS or cat_b in FUNC_SITE_CATS


def _selftest() -> int:
    """Assert PROSITE→regex, SIFTS author mapping, BioLiP note parse, overlap
    classification, and the comparability rule behave."""
    ok = True
    cases = [
        ("[SA]-[FY]-x-L.", "MASYAL", [(3, 6)]),           # [SA][FY].L
        ("C-x(2)-C.", "AACGGCAA", [(3, 6)]),              # C..C
        ("A-{P}-A.", "AQAAPA", [(1, 3)]),                 # A[^P]A → AQA only
        ("<M-x.", "MAXX", [(1, 2)]),                      # N-term anchor
    ]
    for pat, seq, expect in cases:
        rx = prosite_to_regex(pat)
        got = [(m.start() + 1, m.end()) for m in re.finditer(rx or "(?!)", seq)]
        if got != expect:
            print(f"FAIL {pat!r} on {seq!r}: regex={rx!r} got={got} want={expect}")
            ok = False
    # MEROPS scissile consensus is not a positional regex → None
    assert prosite_to_regex("[ILV]-x-x-R | x") is None
    # SIFTS author→UniProt: TEM-1 1BTL author 26..290 = UniProt 24..286 (offset -2)
    segs = [(26, 290, 24 - 26)]
    assert _map_author_residues([70, 130], segs) == {68, 128}   # Ser70→68, Ser130→128
    # BioLiP note parse (with a stubbed SIFTS)
    rec = {"trait_category": "STRUCT_BINDING_SITE", "canonical_examples": [
        {"protein_id": "UniProtKB:P0", "note":
         "BioLiP2 binding-site occurrence in PDB 1abc chain A; binding residues: H57 D102 S195"}]}

    class _Stub:
        def get(self, url):
            return {"1abc": {"UniProt": {"P0": {"mappings": [
                {"chain_id": "A", "unp_start": 16,
                 "start": {"author_residue_number": 16},
                 "end": {"author_residue_number": 245}}]}}}}
    got = biolip_note_residues(rec, _Stub())
    assert got == {"UniProtKB:P0": {57, 102, 195}}, got     # offset 0 here
    # classification + comparability
    assert classify({5, 6, 7}, {1, 2, 3, 4, 5, 6, 7, 8}, "SEQ_MOTIF",
                    "SEQ_DOMAIN")[0] == "biolink:part_of"
    assert classify({62, 63, 64}, {64}, "SEQ_MOTIF",
                    "STRUCT_ACTIVE_SITE")[0] == "biolink:overlaps"
    assert classify({1, 2}, {5, 6}, "SEQ_MOTIF", "SEQ_DOMAIN") is None
    assert _comparable("STRUCTURE", "STRUCT_ACTIVE_SITE",
                       "STRUCTURE", "STRUCT_METAL_SITE")     # same-axis func pair
    assert not _comparable("STRUCTURE", "STRUCT_FOLD",
                           "STRUCTURE", "STRUCT_DOMAIN")     # same-axis, no func
    assert not _comparable("SEQUENCE", "SEQ_ACTIVE_SITE",
                           "SEQUENCE", "SEQ_ACTIVE_SITE")    # same category
    assert _comparable("SEQUENCE", "SEQ_MOTIF",
                       "STRUCTURE", "STRUCT_FOLD")           # cross-axis
    print("selftest: OK" if ok else "selftest: FAILED")
    return 0 if ok else 1


def _prefilter(text: str, providers) -> bool:
    """Cheap text gate: can any active provider possibly localize this record?"""
    if "protein_id:" not in text or "canonical_examples:" not in text:
        return False
    if "sequence_pattern:" in text or "feature_type:" in text:
        return True
    if "interpro" in providers:
        return True                                  # any member-DB signature
    if "sifts" in providers and "structure_ref:" in text:
        return True
    if "biolip" in providers and "binding residues" in text.lower():
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--providers", default="stored",
                    help="comma list of stored,interpro,sifts,biolip (default stored)")
    ap.add_argument("--limit", type=int, default=0, help="cap files parsed (debug)")
    ap.add_argument("--dry-run", action="store_true", help="print stats, don't write")
    ap.add_argument("--selftest", action="store_true",
                    help="run offline unit self-tests and exit")
    args = ap.parse_args()
    if args.selftest:
        return _selftest()

    providers = tuple(p.strip() for p in args.providers.split(",") if p.strip())
    unknown = set(providers) - {"stored", "interpro", "sifts", "biolip"}
    if unknown:
        print(f"unknown provider(s): {sorted(unknown)}", file=sys.stderr)
        return 2
    http = None
    if {"interpro", "sifts", "biolip"} & set(providers):
        http = Http(CACHE_DIR / "align_http_cache.json")

    # interpro is scoped: an interpro call only matters if the exemplar protein is
    # already localized by another record (only then can a pair form). So localize
    # with every provider EXCEPT interpro first, then (phase 2) call interpro just
    # for pattern-less signatures on already-shared proteins.
    base_providers = tuple(p for p in providers if p != "interpro")
    interpro_on = "interpro" in providers

    # protein_id → [(identifier, axis, category, residue set)]
    by_protein: dict[str, list] = {}
    sig_stash = []          # (rid, axis, cat, prefix, acc, [pids]) pattern-less signatures
    parsed = with_loc = unconvertible = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        if not _prefilter(text, providers):
            continue
        try:
            rec = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        if not isinstance(rec, dict):
            continue
        parsed += 1
        axis, cat, rid = (rec.get("trait_axis"), rec.get("trait_category"),
                          rec.get("identifier"))
        if axis not in ("SEQUENCE", "STRUCTURE") or not rid or not cat:
            continue
        pat = rec.get("sequence_pattern")
        if pat and "|" not in pat and prosite_to_regex(pat) is None:
            unconvertible += 1
        loc = located_residues(rec, base_providers, http)
        if loc:
            with_loc += 1
        for pid, res in loc.items():
            by_protein.setdefault(pid, []).append((rid, axis, cat, res))
        if interpro_on and not pat:
            prefix, _, acc = rid.partition(":")
            if prefix in MEMBERDB and acc:
                pids = [ex.get("protein_id") for ex in (rec.get("canonical_examples")
                        or []) if isinstance(ex, dict) and ex.get("protein_id")]
                if pids:
                    sig_stash.append((rid, axis, cat, prefix, acc, pids))
        if args.limit and parsed >= args.limit:
            break
        if http and http.misses and http.misses % 500 == 0:
            http.flush()

    # Phase 2 — scoped interpro: only for shared proteins already in by_protein.
    ipro_calls = ipro_hits = 0
    if interpro_on and http:
        for rid, axis, cat, prefix, acc, pids in sig_stash:
            for pid in pids:
                if pid not in by_protein:          # no pairing partner → skip
                    continue
                r = interpro_residues(prefix, acc, pid, http)
                ipro_calls += 1
                if r:
                    by_protein[pid].append((rid, axis, cat, r))
                    ipro_hits += 1
                if ipro_calls % 300 == 0:
                    http.flush()
        print(f"scoped interpro: {ipro_calls:,} calls on shared proteins, "
              f"{ipro_hits:,} localized", file=sys.stderr)
    if http:
        http.flush()

    # record pairs sharing a protein, with coordinate overlap. Aggregate the
    # supporting proteins per (subject,object) pair and keep the strongest edge.
    # edges keyed by (subj,obj) → {pred, proteins, func} ; func = touches a site cat
    edges: dict[tuple, dict] = {}
    shared_proteins = 0
    for pid, recs in by_protein.items():
        if len(recs) < 2:
            continue
        paired_here = False
        for i in range(len(recs)):
            rid_a, axis_a, cat_a, res_a = recs[i]
            for j in range(i + 1, len(recs)):
                rid_b, axis_b, cat_b, res_b = recs[j]
                if rid_a == rid_b or not _comparable(axis_a, cat_a, axis_b, cat_b):
                    continue
                got = classify(res_a, res_b, cat_a, cat_b)
                if not got:
                    continue
                paired_here = True
                pred, _metric, a_is_subject = got
                subj, obj = (rid_a, rid_b) if a_is_subject else (rid_b, rid_a)
                func = cat_a in FUNC_SITE_CATS or cat_b in FUNC_SITE_CATS
                key = (subj, obj)
                e = edges.get(key)
                if e is None:
                    edges[key] = {"pred": pred, "proteins": {pid}, "func": func}
                else:
                    e["proteins"].add(pid)
                    e["func"] = e["func"] or func
                    if PRED_RANK[pred] > PRED_RANK[e["pred"]]:
                        e["pred"] = pred
        shared_proteins += paired_here

    base_rows, func_rows = [], []
    for (subj, obj), e in edges.items():
        prots = sorted(e["proteins"])
        tag = "func-site" if e["func"] else "seq-struct"
        src = (f"{tag}-coord-overlap|{','.join(prots[:5])}"
               f"{'…' if len(prots) > 5 else ''}|n={len(prots)}")
        (func_rows if e["func"] else base_rows).append((subj, e["pred"], obj, src))
    base_rows.sort()
    func_rows.sort()

    print(f"providers={list(providers)}; parsed {parsed:,} candidate records; "
          f"{with_loc:,} localized; {unconvertible:,} unconvertible patterns; "
          f"{len(by_protein):,} proteins ({shared_proteins:,} with ≥2 comparable "
          f"records)", file=sys.stderr)
    if http:
        print(f"http: {http.hits:,} cache hits, {http.misses:,} misses",
              file=sys.stderr)
    print(f"seq-struct edges: {len(base_rows):,}  {dict(Counter(r[1] for r in base_rows))}")
    print(f"func-site edges:  {len(func_rows):,}  {dict(Counter(r[1] for r in func_rows))}")
    if args.dry_run:
        for label, rows in (("seq-struct", base_rows), ("func-site", func_rows)):
            print(f"  --- {label} sample ---")
            for r in rows[:6]:
                print("   ", *r)
        print("Dry-run — not written.")
        return 0

    for out, rows in ((OUT_BASE, base_rows), (OUT_FUNC, func_rows)):
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            fh.write("subject\tpredicate\tobject\trelation_source\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
        print(f"wrote {len(rows):,} edges → {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
