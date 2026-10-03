#!/usr/bin/env python3
"""Build per-protein trait profiles from UniProtKB (reviewed by default).

The trait corpus is one YAML per *trait class* (ProteinTraitRecord). This builds
the complementary per-*protein* view: for each UniProtKB entry, which corpus
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
     ProteinTraitRecord identifier (the existing cache is read-only).
  2. Stream a release-consistent UniProtKB slice (default: reviewed:true).
  3. For each entry, resolve its xrefs to corpus traits + collect GO / EC.
  4. Publish profiles.jsonl, optional ProteinProfile YAMLs, the exact trait
     index, and an acquisition receipt together in a NEW output directory.

Bounded by --query / --limit. Dry-run never writes. Existing output directories
are never replaced: use --out-dir for isolated expansion. --require-complete
rejects a query larger than --limit; --limit 0 explicitly removes the cap.
These are discovery profiles, not qualified canonical examples or coordinates.
Stdlib-only; no broad crawl should run without a reviewed acquisition plan.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "data" / "profiles"
CACHE = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"
SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"
PROFILE_FIELDS = ("accession,protein_name,organism_name,organism_id,length,reviewed,"
                  "xref_pfam,xref_interpro,xref_gene3d,xref_prosite,xref_smart,xref_cdd,"
                  "xref_ncbifam,xref_supfam,xref_hamap,xref_panther,xref_pirsf,xref_prints,go_id,ec")
ACCESSION = re.compile(r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})")
RELEASE = re.compile(r"[0-9]{4}_[0-9]{2}")


class AcquisitionError(ValueError):
    """No complete, internally consistent acquisition can be published."""

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

# The standard multi-organism slice (--organisms). Human alone biases every
# downstream artefact — exemplar picks, and the support counts that decide which
# cross-axis rules clear threshold — toward traits that happen to occur in
# vertebrates.
#
# The first four were the phase-6 slice, and left the matrix 76% vertebrate with
# no archaea, plants or parasites: a "held-out organism" that is a second mammal
# is barely held out at all (phase 6 measured mouse as indistinguishable from a
# random split). The rest span the tree far enough that replication across them
# means something — two bacteria on opposite sides of the Gram stain, an
# archaeon, a plant, an apicomplexan parasite, and two invertebrate models.
ORGANISMS = {
    9606:   "Homo sapiens",                     # mammal
    10090:  "Mus musculus",                     # mammal
    7227:   "Drosophila melanogaster",          # insect
    6239:   "Caenorhabditis elegans",           # nematode
    3702:   "Arabidopsis thaliana",             # plant
    559292: "Saccharomyces cerevisiae S288C",   # fungus
    36329:  "Plasmodium falciparum 3D7",        # apicomplexan parasite
    83333:  "Escherichia coli K-12",            # Gram-negative bacterium
    224308: "Bacillus subtilis 168",            # Gram-positive bacterium
    243232: "Methanocaldococcus jannaschii",    # archaeon
}


def build_trait_index(refresh: bool = False, cache: Path | None = None) -> dict:
    """Read or rebuild {trait CURIE → [axis, category]} without changing the cache."""
    cache = CACHE if cache is None else cache
    if cache.exists() and not refresh:
        try:
            index = json.loads(cache.read_text(encoding="utf-8"))
            if not isinstance(index, dict) or not all(
                isinstance(k, str) and isinstance(v, list) and len(v) == 2
                and all(isinstance(part, str) for part in v)
                for k, v in index.items()
            ):
                raise AcquisitionError(f"invalid trait index: {cache}")
            return index
        except (ValueError, OSError):
            raise AcquisitionError(f"cannot read trait index: {cache}; use --refresh-index")
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
    print(f"trait index: {n:,} groundable trait classes "
          f"({len({k.split(':')[0] for k in idx})} namespaces)", file=sys.stderr)
    return idx


def _check_search_url(url: str, expected_params: dict, *, next_page: bool = False) -> None:
    parsed = urllib.parse.urlsplit(url)
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if (parsed.scheme != "https" or parsed.netloc != "rest.uniprot.org"
            or parsed.path != "/uniprotkb/search" or parsed.fragment
            or params.get("query") != expected_params.get("query")):
        raise AcquisitionError("search URL changed origin, endpoint, or query")
    if next_page:
        cursor = params.pop("cursor", [])
        if len(cursor) != 1 or not cursor[0]:
            raise AcquisitionError("next-page request parameters lack a unique cursor")
    if params != expected_params:
        raise AcquisitionError("search request parameters changed during acquisition")


def _get(url: str, tries: int = 4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                       "User-Agent": "ProteinTraitsMech-profiles/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                resolved_url = r.geturl()
                _check_search_url(resolved_url, urllib.parse.parse_qs(
                    urllib.parse.urlsplit(url).query, keep_blank_values=True))
                raw = r.read()
                return json.loads(raw), {
                    "url": url,
                    "resolved_url": resolved_url,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "release": r.headers.get("x-uniprot-release"),
                    "total": r.headers.get("x-total-results"),
                    "link": r.headers.get("Link", ""),
                }
        except Exception as e:                       # noqa: BLE001 (network/JSON)
            if i == tries - 1:
                raise AcquisitionError(f"fetch failed for {url}: {e}") from e
            time.sleep(1.5 * (i + 1))
    raise AcquisitionError(f"no fetch attempts for {url}")


def stream_swissprot(query: str, limit: int, page: int = 300, *,
                     expect_release: str | None = None, require_complete: bool = False,
                     receipt: dict | None = None):
    """Yield a checked query; incomplete or changing pagination raises, never stops silently.

    The historical function name is retained, but explicit queries may include
    unreviewed entries. A deliberate limit is recorded as incomplete, not full coverage.
    """
    if limit < 0 or page < 1 or page > 500:
        raise AcquisitionError("limit must be nonnegative and page size must be 1..500")
    if expect_release is not None and not RELEASE.fullmatch(expect_release):
        raise AcquisitionError("invalid expected UniProt release")
    url = (SEARCH_URL + "?"
           + urllib.parse.urlencode({"query": query, "fields": PROFILE_FIELDS,
                                     "format": "json", "sort": "accession asc",
                                     "size": min(page, limit) if limit else page}))
    expected_params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    stats = receipt if receipt is not None else {}
    stats.update(query=query, pages=[], returned_rows=0, complete=False)
    seen_urls: set[str] = set()
    seen_accessions: set[str] = set()
    release, total = expect_release, None
    while url:
        if url in seen_urls:
            raise AcquisitionError("repeated pagination URL")
        seen_urls.add(url)
        data, meta = _get(url)
        current = meta.get("release")
        if not isinstance(current, str) or not RELEASE.fullmatch(current):
            raise AcquisitionError("missing or invalid UniProt release header")
        if release is not None and current != release:
            raise AcquisitionError(f"UniProt release changed: expected {release}, got {current}")
        release = current
        count_header = meta.get("total")
        if not isinstance(count_header, str) or not re.fullmatch(r"[0-9]+", count_header):
            raise AcquisitionError("missing or invalid total-results header")
        page_total = int(count_header)
        if total is not None and page_total != total:
            raise AcquisitionError("total-results changed during pagination")
        total = page_total
        stats.update(release=release, total=total)
        if require_complete and limit and total > limit:
            raise AcquisitionError(f"query has {total} entries, exceeding complete-query limit {limit}")
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            raise AcquisitionError("invalid UniProt results page")
        entries = data["results"]
        if not entries and len(seen_accessions) != total:
            raise AcquisitionError("empty page before advertised total")
        for entry in entries:
            acc = entry.get("primaryAccession") if isinstance(entry, dict) else None
            if not isinstance(acc, str) or not ACCESSION.fullmatch(acc):
                raise AcquisitionError("invalid accession in search result")
            if acc in seen_accessions:
                raise AcquisitionError(f"duplicate accession during pagination: {acc}")
            seen_accessions.add(acc)
        if len(seen_accessions) > total:
            raise AcquisitionError("received more entries than advertised total")
        link = meta.get("link", "")
        matches = re.findall(r'<([^>]+)>;\s*rel="next"', link)
        if len(matches) > 1 or ("next" in link and not matches):
            raise AcquisitionError("invalid next-page link")
        next_url = matches[0] if matches else None
        if next_url:
            _check_search_url(next_url, expected_params, next_page=True)
            if len(seen_accessions) == total:
                raise AcquisitionError("next-page link after advertised total")
        elif len(seen_accessions) != total:
            raise AcquisitionError("pagination ended before advertised total")
        stats["pages"].append({**meta, "received_rows": len(entries)})
        for e in entries:
            if limit and stats["returned_rows"] == limit:
                return
            stats["returned_rows"] += 1
            yield e
        if stats["returned_rows"] == total:
            stats["complete"] = True
            return
        if limit and stats["returned_rows"] == limit:
            return
        url = next_url
        if url:
            time.sleep(0.2)


def description_ec_numbers(description: dict) -> list[str]:
    """Collect source-asserted ECs, including multifunctional and processed components.

    Stay inside proteinDescription name containers: do not mine prose, evidence
    references, or unrelated annotations for strings resembling enzyme numbers.
    """
    pending, ecs = [description], set()
    while pending:
        part = pending.pop()
        names = [part.get("recommendedName") or {}]
        for key in ("alternativeNames", "submissionNames"):
            names.extend(part.get(key) or [])
        for name in names:
            for ec in name.get("ecNumbers") or []:
                value = ec.get("value")
                if not isinstance(value, str) or not value.strip():
                    raise AcquisitionError("invalid EC number in protein description")
                ecs.add(value)
        for key in ("includes", "contains"):
            pending.extend(part.get(key) or [])
    return sorted(ecs)


def profile(entry: dict, idx: dict) -> dict:
    acc = entry.get("primaryAccession")
    if not isinstance(acc, str) or not ACCESSION.fullmatch(acc):
        raise AcquisitionError("invalid profile accession")
    entry_type = entry.get("entryType")
    if entry_type not in {"UniProtKB reviewed (Swiss-Prot)", "UniProtKB unreviewed (TrEMBL)"}:
        raise AcquisitionError(f"unknown entry status for {acc}")
    reviewed = entry_type == "UniProtKB reviewed (Swiss-Prot)"
    name = (((entry.get("proteinDescription") or {}).get("recommendedName") or {})
            .get("fullName", {}) or {}).get("value")
    if not name:
        name = next((n.get("fullName", {}).get("value")
                     for n in (entry.get("proteinDescription") or {}).get("submissionNames", [])
                     if n.get("fullName", {}).get("value")), acc)
    org = entry.get("organism") or {}
    length = (entry.get("sequence") or {}).get("length")
    if (type(org.get("taxonId")) is not int or org["taxonId"] <= 0
            or not isinstance(org.get("scientificName"), str) or not org["scientificName"]
            or type(length) is not int or length <= 0):
        raise AcquisitionError(f"missing or invalid organism/sequence metadata for {acc}")
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
    # EC discovery membership is not a claim of experimental evidence or coordinates.
    ecs = description_ec_numbers(entry.get("proteinDescription") or {})
    for v in ecs:
        cur = f"EC:{v}"
        if cur in idx and cur not in seen:
            seen.add(cur)
            ax, cat = idx[cur]
            traits.append({"trait": cur, "trait_axis": ax, "trait_category": cat, "via": cur})
    traits.sort(key=lambda t: t["trait"])
    prof = {
        "accession": f"UniProtKB:{acc}",
        "protein_name": name,
        "sequence_length": length,
        "taxon_id": f"NCBITaxon:{org['taxonId']}",
        "taxon_label": org["scientificName"],
        "reviewed": reviewed,
        "go_terms": sorted(set(go)),
        "ec_numbers": sorted(set(ecs)),
        "traits": traits,
        "profile_source": (f"UniProtKB {'Swiss-Prot' if reviewed else 'TrEMBL'}; "
                           "build_swissprot_profiles.py"),
    }
    return prof


def _yq(t: str) -> str:
    # JSON strings are YAML scalars too, including newlines and boolean-looking names.
    return json.dumps(str(t), ensure_ascii=False)


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


def matrix_row(p: dict) -> dict:
    """Keep the established discovery-matrix shape for downstream consumers."""
    return {"accession": p["accession"], "go": p["go_terms"], "ec": p["ec_numbers"],
            "name": p["protein_name"], "taxon": p["taxon_id"], "taxon_label": p["taxon_label"],
            "length": p["sequence_length"], "reviewed": p["reviewed"],
            "traits": [t["trait"] for t in p["traits"]],
            "axes": {t["trait"]: t["trait_axis"] for t in p["traits"]}}


def publish_directory(staged: Path, destination: Path) -> None:
    """Atomically publish without replacing even a concurrently created empty directory.

    Path.rename is overwrite-capable on POSIX. Use the native exclusive variant
    on macOS/Linux, and Windows' no-replace os.rename. Unsupported platforms or
    filesystems fail closed; there is deliberately no unsafe fallback.
    """
    if os.name == "nt":
        os.rename(staged, destination)
        return
    src, dst = os.fsencode(staged.absolute()), os.fsencode(destination.absolute())
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        if sys.platform == "darwin":
            rename = libc.renamex_np
            rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
            args = (src, dst, 0x00000004)  # RENAME_EXCL (sys/stdio.h)
        elif sys.platform.startswith("linux"):
            rename = libc.renameat2
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                               ctypes.c_char_p, ctypes.c_uint]
            # Absolute paths make both dirfds irrelevant. RENAME_NOREPLACE = 1.
            args = (0, src, 0, dst, 1)
        else:
            raise AcquisitionError("atomic no-replace publication is unsupported on this platform")
    except AttributeError as exc:
        raise AcquisitionError("native no-replace rename is unavailable; refusing publication") from exc
    rename.restype = ctypes.c_int
    if rename(*args) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--query", action="append", metavar="Q",
                    help="UniProtKB query; repeat for a multi-organism matrix "
                         "(default: reviewed human). --limit applies per query.")
    ap.add_argument("--organisms", action="store_true",
                    help="shorthand for the ten reviewed, exact-taxon queries in ORGANISMS")
    ap.add_argument("--limit", type=int, default=500,
                    help="cap per query, not in total; 0 explicitly removes the cap")
    ap.add_argument("--apply", action="store_true", help="write YAML + jsonl (else dry-run)")
    ap.add_argument("--jsonl-only", action="store_true", help="write only profiles.jsonl (skip per-protein YAMLs) — for scaling the analysis matrix")
    ap.add_argument("--refresh-index", action="store_true")
    ap.add_argument("--index-cache", type=Path, default=CACHE, help="read-only trait index cache")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR,
                    help="NEW acquisition directory; existing files/directories are never replaced")
    ap.add_argument("--expect-release", help="required UniProt release, e.g. 2026_03")
    ap.add_argument("--require-complete", action="store_true",
                    help="refuse a query whose advertised total exceeds --limit")
    args = ap.parse_args(argv)
    if args.limit < 0:
        ap.error("--limit must be nonnegative")
    if args.expect_release and not RELEASE.fullmatch(args.expect_release):
        ap.error("--expect-release must have the form YYYY_NN")
    if args.apply and (args.out_dir.exists() or args.out_dir.is_symlink()):
        ap.error("output already exists; choose a NEW --out-dir to preserve frozen inputs")

    queries = list(args.query or [])
    if args.organisms:
        queries += [f"reviewed:true AND organism_id:{t}" for t in ORGANISMS]
    if not queries:
        queries = ["reviewed:true AND organism_id:9606"]

    queries = list(dict.fromkeys(queries))
    n = with_traits = tot_traits = 0
    axes: dict = {}
    seen: dict[str, str] = {}  # overlapping queries must agree, not silently overwrite
    try:
        idx = build_trait_index(args.refresh_index, args.index_cache)
        index_bytes = (json.dumps(idx, sort_keys=True) + "\n").encode("utf-8")
        manifest = {
            "schema_version": 1, "source": "UniProtKB",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "purpose": "discovery only; not qualified examples or residue coordinates",
            "expected_release": args.expect_release, "release": args.expect_release,
            "limit_per_query": args.limit, "require_complete": args.require_complete,
            "trait_index_sha256": hashlib.sha256(index_bytes).hexdigest(), "queries": [],
        }
        matrix_hash = hashlib.sha256()
        with ExitStack() as stack:
            staged = jf = None
            if args.apply:
                args.out_dir.parent.mkdir(parents=True, exist_ok=True)
                staged = Path(stack.enter_context(tempfile.TemporaryDirectory(
                    prefix=".protein-profiles-", dir=args.out_dir.parent)))
                jf = stack.enter_context((staged / "profiles.jsonl").open("wb"))
            for query in queries:
                q_n, stats = 0, {}
                for entry in stream_swissprot(query, args.limit,
                                              expect_release=manifest["release"],
                                              require_complete=args.require_complete,
                                              receipt=stats):
                    p = profile(entry, idx)
                    digest = hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest()
                    acc = p["accession"]
                    if acc in seen:
                        if seen[acc] != digest:
                            raise AcquisitionError(f"conflicting profiles across queries: {acc}")
                        continue
                    seen[acc] = digest
                    n += 1
                    q_n += 1
                    with_traits += bool(p["traits"])
                    tot_traits += len(p["traits"])
                    for t in p["traits"]:
                        axes[t["trait_axis"]] = axes.get(t["trait_axis"], 0) + 1
                    row = (json.dumps(matrix_row(p), ensure_ascii=False) + "\n").encode("utf-8")
                    matrix_hash.update(row)
                    if jf is not None:
                        jf.write(row)
                        if not args.jsonl_only:
                            (staged / f"{acc.split(':', 1)[1]}.yaml").write_text(
                                to_yaml(p), encoding="utf-8")
                manifest["release"] = stats["release"]
                stats["new_profiles"] = q_n
                manifest["queries"].append(stats)
                note = "complete" if stats["complete"] else "LIMITED, not complete coverage"
                print(f"  {query!r}: {q_n:,} new profiles; "
                      f"{stats['returned_rows']}/{stats['total']} returned ({note})", file=sys.stderr)
            manifest.update(profiles=n, profiles_sha256=matrix_hash.hexdigest(),
                            complete=all(q["complete"] for q in manifest["queries"]))
            if jf is not None:
                jf.close()
                (staged / "trait_index.json").write_bytes(index_bytes)
                (staged / "acquisition.json").write_text(
                    json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
                if args.out_dir.exists() or args.out_dir.is_symlink():
                    raise AcquisitionError("output appeared during acquisition; refusing replacement")
                publish_directory(staged, args.out_dir)
    except (AcquisitionError, OSError) as exc:
        print(f"ERROR: {exc}; no acquisition published", file=sys.stderr)
        return 2

    print(f"queries: {len(queries)} (limit {args.limit} each)")
    print(f"proteins: {n:,}; with ≥1 corpus trait: {with_traits:,} "
          f"({100*with_traits//max(1,n)}%); mean traits/protein: {tot_traits/max(1,n):.1f}")
    print(f"trait matches by axis: {dict(sorted(axes.items(), key=lambda kv:-kv[1]))}")
    print(f"WROTE {n:,} profiles → {args.out_dir}/" if args.apply
          else "Dry-run — pass --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
