#!/usr/bin/env python3
"""Build per-protein trait *profiles* from Swiss-Prot (issue #7).

The trait corpus is one YAML per *trait class* (ProteinTraitRecord). This builds
the complementary per-*protein* view: for each Swiss-Prot entry, which corpus
trait classes it carries — resolved by matching the entry's signature /
classification cross-references (Pfam, InterPro, CATH/Gene3D, PROSITE, SMART,
CDD, NCBIfam, SUPERFAMILY, EC, GO) against the identifiers of existing
ProteinTraitRecords — plus its GO terms and EC numbers.

The result (one `ProteinProfile` YAML per protein + a consolidated
`profiles.jsonl`) is the protein × trait matrix for the downstream analysis in
issue #7: trait↔function (GO) correlation, decision-tree function prediction, and
multi-trait-family clustering.

Steps:
  1. Index the corpus: {trait CURIE → (axis, category)} for every groundable
     ProteinTraitRecord identifier (cached to data/raw/profiles_cache/).
  2. Stream a Swiss-Prot slice from the UniProtKB REST API (reviewed:true).
  3. For each entry, resolve its xrefs to corpus traits + collect GO / EC.
  4. Emit data/profiles/<acc>.yaml (validated as ProteinProfile) + profiles.jsonl.

Bounded by --query / --limit. Dry-run (counts only) unless --apply. Stdlib-only.
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
TRAITS = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "data" / "profiles"
JSONL = OUT_DIR / "profiles.jsonl"
CACHE = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"

# UniProt cross-reference database name → corpus trait-CURIE prefix. These are
# the signature / classification namespaces the corpus grounds trait classes to.
DB2PREFIX = {
    "Pfam": "Pfam", "InterPro": "InterPro", "Gene3D": "CATH", "PROSITE": "PROSITE",
    "SMART": "SMART", "CDD": "CDD", "NCBIfam": "NCBIfam", "SUPFAM": "SUPERFAMILY",
    "HAMAP": "HAMAP", "PIRSF": "PIRSF", "PANTHER": "PANTHER", "PRINTS": "PRINTS",
}
_IDENT = re.compile(r"(?m)^identifier:\s*([A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+)\s*$")
_AXIS = re.compile(r"(?m)^trait_axis:\s*(\S+)")
_CAT = re.compile(r"(?m)^trait_category:\s*(\S+)")
_GROUND_PREFIXES = set(DB2PREFIX.values()) | {"GO", "EC"}


def build_trait_index(refresh: bool = False) -> dict:
    """{trait CURIE → [axis, category]} for groundable corpus trait classes."""
    if CACHE.exists() and not refresh:
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    idx: dict = {}
    n = 0
    for p in TRAITS.rglob("*.yaml"):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = _IDENT.search(text)
        if not m:
            continue
        cur = m.group(1)
        if cur.split(":", 1)[0] not in _GROUND_PREFIXES:
            continue
        a = _AXIS.search(text)
        c = _CAT.search(text)
        idx[cur] = [a.group(1) if a else "", c.group(1) if c else ""]
        n += 1
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(idx), encoding="utf-8")
    print(f"trait index: {n:,} groundable trait classes "
          f"({len({k.split(':')[0] for k in idx})} namespaces)", file=sys.stderr)
    return idx


def _get(url: str, tries: int = 4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "ProteinTraitsMech-profiles/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8")), r.headers.get("Link", "")
        except Exception as e:                       # noqa: BLE001 (network/JSON)
            if i == tries - 1:
                print(f"  fetch failed: {e}", file=sys.stderr)
                return None, ""
            time.sleep(1.5 * (i + 1))
    return None, ""


def stream_swissprot(query: str, limit: int, page: int = 300):
    """Yield UniProtKB entries (JSON) for `query`, up to `limit`, via cursor pages."""
    fields = ("accession,protein_name,organism_name,organism_id,length,reviewed,"
              "xref_pfam,xref_interpro,xref_gene3d,xref_prosite,xref_smart,xref_cdd,"
              "xref_ncbifam,xref_supfam,xref_hamap,xref_panther,xref_pirsf,go_id,ec")
    url = ("https://rest.uniprot.org/uniprotkb/search?"
           + urllib.parse.urlencode({"query": query, "fields": fields,
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
        time.sleep(0.2)


def profile(entry: dict, idx: dict) -> dict:
    acc = entry.get("primaryAccession")
    name = (((entry.get("proteinDescription") or {}).get("recommendedName") or {})
            .get("fullName", {}) or {}).get("value") or acc
    org = entry.get("organism") or {}
    xrefs = entry.get("uniProtKBCrossReferences") or []
    go, traits, seen = [], [], set()
    for x in xrefs:
        db, xid = x.get("database"), x.get("id")
        if not (db and xid):
            continue
        if db == "GO":
            go.append(xid if xid.startswith("GO:") else f"GO:{xid}")
            cur = xid if xid.startswith("GO:") else f"GO:{xid}"
        elif db in DB2PREFIX:
            local = xid.split(":", 1)[-1] if xid.startswith("G3DSA:") else xid
            cur = f"{DB2PREFIX[db]}:{local}"
        else:
            continue
        if cur in idx and cur not in seen:
            seen.add(cur)
            ax, cat = idx[cur]
            traits.append({"trait": cur, "trait_axis": ax, "trait_category": cat, "via": cur})
    # EC numbers (recommendedName + comments) → trait if the EC class is in the corpus
    ecs = []
    for ec in (((entry.get("proteinDescription") or {}).get("recommendedName") or {})
               .get("ecNumbers") or []):
        v = ec.get("value")
        if v:
            ecs.append(v)
            cur = f"EC:{v}"
            if cur in idx and cur not in seen:
                seen.add(cur)
                ax, cat = idx[cur]
                traits.append({"trait": cur, "trait_axis": ax, "trait_category": cat, "via": cur})
    traits.sort(key=lambda t: t["trait"])
    prof = {
        "accession": f"UniProtKB:{acc}",
        "protein_name": name,
        "sequence_length": entry.get("sequence", {}).get("length") or (entry.get("annotationScore") and None),
        "reviewed": entry.get("entryType", "").startswith("UniProtKB reviewed"),
        "go_terms": sorted(set(go)),
        "ec_numbers": sorted(set(ecs)),
        "traits": traits,
        "profile_source": "UniProtKB Swiss-Prot; build_swissprot_profiles.py",
    }
    if org.get("taxonId"):
        prof["taxon_id"] = f"NCBITaxon:{org['taxonId']}"
    if org.get("scientificName"):
        prof["taxon_label"] = org["scientificName"]
    if entry.get("sequence", {}).get("length"):
        prof["sequence_length"] = entry["sequence"]["length"]
    else:
        prof.pop("sequence_length", None)
    return prof


def _yq(t: str) -> str:
    t = str(t)
    if not t:
        return '""'
    if re.search(r'[:#\[\]{}",&*!|>%@`]', t) or t[:1] in "-?" or re.fullmatch(r"-?\d+(?:\.\d+)?", t):
        return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return t


def to_yaml(p: dict) -> str:
    L = [f"accession: {p['accession']}", f"protein_name: {_yq(p['protein_name'])}"]
    if p.get("taxon_id"):
        L.append(f"taxon_id: {p['taxon_id']}")
    if p.get("taxon_label"):
        L.append(f"taxon_label: {_yq(p['taxon_label'])}")
    if p.get("sequence_length"):
        L.append(f"sequence_length: {p['sequence_length']}")
    L.append(f"reviewed: {'true' if p['reviewed'] else 'false'}")
    for key in ("go_terms", "ec_numbers"):
        if p.get(key):
            L.append(f"{key}:")
            L += [f"  - {_yq(v)}" for v in p[key]]
    if p.get("traits"):
        L.append("traits:")
        for t in p["traits"]:
            L.append(f"  - trait: {t['trait']}")
            if t.get("trait_axis"):
                L.append(f"    trait_axis: {t['trait_axis']}")
            if t.get("trait_category"):
                L.append(f"    trait_category: {t['trait_category']}")
            L.append(f"    via: {t['via']}")
    L.append(f"profile_source: {_yq(p['profile_source'])}")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--query", default="reviewed:true AND organism_id:9606",
                    help="UniProtKB query (default: reviewed human)")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--apply", action="store_true", help="write YAML + jsonl (else dry-run)")
    ap.add_argument("--jsonl-only", action="store_true", help="write only profiles.jsonl (skip per-protein YAMLs) — for scaling the analysis matrix")
    ap.add_argument("--refresh-index", action="store_true")
    args = ap.parse_args()

    idx = build_trait_index(args.refresh_index)
    n = with_traits = tot_traits = 0
    axes: dict = {}
    if args.apply:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        jf = JSONL.open("w", encoding="utf-8")
    for entry in stream_swissprot(args.query, args.limit):
        p = profile(entry, idx)
        n += 1
        if p["traits"]:
            with_traits += 1
        tot_traits += len(p["traits"])
        for t in p["traits"]:
            axes[t["trait_axis"]] = axes.get(t["trait_axis"], 0) + 1
        if args.apply:
            acc = p["accession"].split(":", 1)[1]
            if not args.jsonl_only:
                (OUT_DIR / f"{acc}.yaml").write_text(to_yaml(p), encoding="utf-8")
            jf.write(json.dumps({"accession": p["accession"], "go": p["go_terms"],
                                 "ec": p["ec_numbers"],
                                 "traits": [t["trait"] for t in p["traits"]],
                                 "axes": {t["trait"]: t["trait_axis"] for t in p["traits"]}}) + "\n")
    if args.apply:
        jf.close()

    print(f"query={args.query!r} limit={args.limit}")
    print(f"proteins: {n:,}; with ≥1 corpus trait: {with_traits:,} "
          f"({100*with_traits//max(1,n)}%); mean traits/protein: {tot_traits/max(1,n):.1f}")
    print(f"trait matches by axis: {dict(sorted(axes.items(), key=lambda kv:-kv[1]))}")
    print(f"WROTE {n:,} profiles → {OUT_DIR.relative_to(REPO_ROOT)}/" if args.apply
          else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
