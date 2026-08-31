#!/usr/bin/env python3
"""Emit UniProt grounding candidates for ProteinTraitRecord YAMLs.

This is a candidate producer, not a trait-record writer. It queries the
UniProtKB REST API for proteins carrying a record's exact signature (or a
documented weaker anchor), writes those hits to a deterministic JSONL ledger,
and leaves ``data/traits`` byte-for-byte unchanged. Resolution, semantic
validation, review, and promotion belong to ``ground_uniprot_examples.py``.

Dispatch rules for building the UniProt search query, per record:

  identifier / parent_traits / xrefs — the first hit wins:
    PROSITE:PSxxxxx     → xref:prosite-PSxxxxx
    PROSITE:PDOCxxxxx   → xref:prosite-PDOCxxxxx        (rarely indexed;
                           we still try, then fall through to member PS
                           accessions when documented)
    Pfam:PFxxxxx        → xref:pfam-PFxxxxx
    InterPro:IPRxxxxxx  → xref:interpro-IPRxxxxxx
    SMART:SMxxxxx       → xref:smart-SMxxxxx
    HAMAP:MF_xxxxxx     → xref:hamap-MF_xxxxxx
    CATH:...            → xref:gene3d-<local>
    proteintraitsmech:UNIPROTKB_<ACC>_...  → direct: accession:<ACC>
                           (canonical example for a UniProt-seeded record
                           is the source entry itself)
    TED:AF-<UNIPROT>-... → direct: accession:<UNIPROT>

Everything is filtered by `reviewed:true` (Swiss-Prot) by default so
API examples are annotated entries, not TrEMBL guesses. Override with
`--include-unreviewed`.

Per accession returned by search, one candidate row is emitted with:
  protein_id, protein_label, taxon_id, taxon_label,
  sequence_length, reviewed, annotation_score,
  family_classifications (Pfam / InterPro / HAMAP / SMART / CATH refs on
that specific entry), and the exact query/anchor. Metadata-only search hits
remain candidates until a resolver obtains a release-pinned full sequence,
checksum, and record-specific occurrence evidence.

Only an exact xref query for a schema-permitted whole-protein record enters the
``ready-uniprot-membership`` batch. Even there the query hit is discovery only:
qualification requires the exact database+ID to reappear in the independent,
same-response membership snapshot built by ``fetch_uniprot_registry.py``.

Output is deterministic and atomically replaced. ``--apply`` is retained only
to fail loudly for old invocations; direct canonical-example writes are retired.

Rate: 4 req/s soft cap + exponential backoff on 429/503. Stdlib-only.

Usage:
  python3 scripts/fetch_uniprot_examples.py \\
      data/traits/sequence/pattern/1433-1.yaml \\
      --limit 5 --out reports/uniprot-grounding/uniprot-api-candidates.jsonl
  python3 scripts/fetch_uniprot_examples.py \\
      data/traits/sequence/pattern/ --limit 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
DEFAULT_CANDIDATES = (
    REPO_ROOT / "reports" / "uniprot-grounding" / "uniprot-api-candidates.jsonl"
)
READY_MEMBERSHIP_BATCH = "ready-uniprot-membership"
NEEDS_OCCURRENCE_BATCH = "needs-occurrence-evidence"

# Reuse the mature FT-line parser + FT-type routing dispatch that
# `seed_uniprot.py` uses when it converts a UniProt flat file into
# ProteinTraitRecord YAMLs. Same code path → the `features` list on a
# CanonicalExample carries exactly the same axis/category routing that
# seed_uniprot would apply if this feature were promoted to its own
# ProteinTraitRecord.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import seed_uniprot  # noqa: E402

UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_ACCESSIONS = "https://rest.uniprot.org/uniprotkb/accessions"
UNIPROT_FIELDS = ",".join([
    "accession",
    "protein_name",
    "organism_name",
    "organism_id",
    "length",
    "reviewed",
    "annotation_score",
    "xref_pfam",
    "xref_cdd",
    "xref_interpro",
    "xref_prosite",
    "xref_smart",
    "xref_hamap",
    "xref_ncbifam",
    "xref_panther",
    "xref_prints",
    "xref_sfld",
    "xref_supfam",
    "xref_gene3d",  # UniProt's key for the CATH namespace
])
USER_AGENT = "proteintraitsmech-example-fetcher/0.1"

# Rate limiting — UniProt tolerates ~10 req/s but we stay conservative
# (mostly bounded by fetch latency anyway).
MIN_INTERVAL_S = 0.25
_last_req = 0.0
_last_uniprot_release: str | None = None


# ---------------------------------------------------------------------------
# Trait YAML input. Candidate producers never write these paths.
# ---------------------------------------------------------------------------


def read_trait(path: Path) -> dict:
    """Return a parsed dict of the trait YAML. Requires PyYAML because
    the seeder files use folded scalars — a raw regex parse can't cope."""
    import yaml
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at top level")
    return data


# ---------------------------------------------------------------------------
# Query dispatch
# ---------------------------------------------------------------------------

_UNIPROT_IDENT_RE = re.compile(
    r"^proteintraitsmech:UNIPROTKB_([A-Z0-9]+)_"
)
_TED_IDENT_RE = re.compile(
    r"^TED:AF-([A-Z0-9]+)-F1-"
)

# CURIE prefix → UniProt xref key. Order matters — we try each in turn
# on parent_traits + xrefs; the first prefix whose CURIE is present
# wins. PROSITE PATTERN accessions (PS…) are the tightest anchor;
# PDOC / InterPro / Pfam are looser family-level anchors.
_XREF_DISPATCH: tuple[tuple[str, str], ...] = (
    ("PROSITE",  "prosite"),
    ("Pfam",     "pfam"),
    ("CDD",      "cdd"),
    ("NCBIfam",  "ncbifam"),
    ("PANTHER",  "panther"),
    ("InterPro", "interpro"),
    ("HAMAP",    "hamap"),
    ("PRINTS",   "prints"),
    ("SFLD",     "sfld"),
    ("SMART",    "smart"),
    ("SUPERFAMILY", "supfam"),
    # UniProtKB does not expose a raw CATH cross-reference search field.
    # Its CATH-backed domain assignments are the Gene3D cross-references.
    ("CATH",     "gene3d"),
)


def build_queries(data: dict) -> list[tuple[str, str]]:
    """Return an ordered list of (uniprot_query, human_note) candidates
    for this trait. The caller tries them in order, stopping at the
    first query that returns hits. Empty list = no queryable anchor.

    Priority: direct accessions (UniProt-seeded / TED source) → own
    identifier (PROSITE PS accessions are indexed) → parent_traits (Pfam
    / InterPro / HAMAP family-level) → xrefs (PROSITE PS from a ProRule's
    trigger list). Within each pool, walk the prefix dispatch order."""
    ident = data.get("identifier", "")
    queries: list[tuple[str, str]] = []

    # UniProt-seeded trait — the source entry is the primary example.
    m = _UNIPROT_IDENT_RE.match(ident)
    if m:
        acc = m.group(1)
        queries.append((f"accession:{acc}", f"accession:{acc} (source entry)"))
    # TED fold — the AlphaFoldDB accession is the source protein.
    m = _TED_IDENT_RE.match(ident)
    if m:
        acc = m.group(1)
        queries.append((f"accession:{acc}", f"accession:{acc} (TED source entry)"))

    seen: set[str] = set()
    for pool in (
        [ident],
        list(data.get("parent_traits") or []),
        list(data.get("xrefs") or []),
    ):
        for prefix, uniprot_key in _XREF_DISPATCH:
            for curie in pool:
                if not isinstance(curie, str) or ":" not in curie:
                    continue
                p, _, local = curie.partition(":")
                if p != prefix:
                    continue
                q = f"xref:{uniprot_key}-{local}"
                if q in seen:
                    continue
                seen.add(q)
                queries.append((q, q))
    return queries


# ---------------------------------------------------------------------------
# UniProt REST client
# ---------------------------------------------------------------------------


def _throttle() -> None:
    global _last_req
    now = time.monotonic()
    dt = now - _last_req
    if dt < MIN_INTERVAL_S:
        time.sleep(MIN_INTERVAL_S - dt)
    _last_req = time.monotonic()


def _fetch_json(url: str) -> dict:
    """GET a UniProt REST URL and return decoded JSON. Retries with
    exponential backoff on transient HTTP errors (429, 502, 503, 504)."""
    global _last_uniprot_release
    for attempt in range(5):
        _throttle()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                release = resp.headers.get("x-uniprot-release")
                if release:
                    _last_uniprot_release = release
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 502, 503, 504) and attempt < 4:
                backoff = min(30.0, 2 ** attempt)
                print(f"    HTTP {exc.code} — retrying in {backoff:.0f}s",
                      file=sys.stderr)
                time.sleep(backoff)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # Socket read timeouts / transient network errors surface as
            # URLError or a bare TimeoutError — retry rather than crash a
            # long batch run.
            if attempt < 4:
                backoff = min(30.0, 2 ** attempt)
                print(f"    network error ({exc}) — retrying in {backoff:.0f}s",
                      file=sys.stderr)
                time.sleep(backoff)
                continue
            raise
    raise RuntimeError(f"Repeated failure fetching {url}")


def search_uniprot(query: str, limit: int, reviewed_only: bool) -> list[dict]:
    """Run a UniProt search and return up to `limit` results, ordered by
    UniProt's default score (annotation_score desc, effectively)."""
    q = query
    if reviewed_only:
        q = f"({q}) AND (reviewed:true)"
    params = {
        "query": q,
        "format": "json",
        "size": str(limit),
        "fields": UNIPROT_FIELDS,
    }
    url = f"{UNIPROT_SEARCH}?{urllib.parse.urlencode(params)}"
    payload = _fetch_json(url)
    return list(payload.get("results") or [])


def _fetch_text(url: str) -> str:
    """GET a UniProt REST URL and return the raw text body. Retries on
    the same transient error set as `_fetch_json`."""
    for attempt in range(5):
        _throttle()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/plain",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 502, 503, 504) and attempt < 4:
                backoff = min(30.0, 2 ** attempt)
                print(f"    HTTP {exc.code} — retrying in {backoff:.0f}s",
                      file=sys.stderr)
                time.sleep(backoff)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt < 4:
                backoff = min(30.0, 2 ** attempt)
                print(f"    network error ({exc}) — retrying in {backoff:.0f}s",
                      file=sys.stderr)
                time.sleep(backoff)
                continue
            raise
    raise RuntimeError(f"Repeated failure fetching {url}")


def fetch_flat_entries(accessions: list[str]) -> list:
    """Batch-fetch flat file entries for a list of accessions and parse
    them via `seed_uniprot.parse_flatfile`. Returns a list of
    UniProtEntry objects (may be shorter than `accessions` if some
    weren't found)."""
    if not accessions:
        return []
    url = f"{UNIPROT_ACCESSIONS}?accessions={','.join(accessions)}&format=txt"
    text = _fetch_text(url)
    return seed_uniprot.parse_flatfile(text)


def flat_features_for_example(entry) -> list[dict]:
    """Convert a UniProtEntry's `.features` list into the
    SequenceFeatureAnnotation shape written to YAML. Routes each FT
    line via seed_uniprot's own dispatch so the axis/category label the
    docs browser sees matches what seed_uniprot would emit."""
    out: list[dict] = []
    for ft in entry.features:
        routed = seed_uniprot.route_feature(ft)
        if routed is None:
            continue
        start, end = ft.get("start"), ft.get("end")
        if start is None or end is None:
            continue
        axis, category, _ = routed
        feat: dict = {
            "start": int(start),
            "end": int(end),
            "feature_type": ft["ft_type"],
            "trait_axis": axis,
            "trait_category": category,
        }
        note = (ft.get("note") or "").strip()
        if note:
            feat["note"] = note
        out.append(feat)
    return out


# ---------------------------------------------------------------------------
# Example construction
# ---------------------------------------------------------------------------


def _extract_family_curies(entry: dict) -> list[str]:
    curies: list[str] = []
    for xref in entry.get("uniProtKBCrossReferences") or []:
        db = xref.get("database")
        acc = xref.get("id")
        if not db or not acc:
            continue
        prefix = {
            "CDD":      "CDD",
            "Pfam":     "Pfam",
            "InterPro": "InterPro",
            "PROSITE":  "PROSITE",
            "SMART":    "SMART",
            "HAMAP":    "HAMAP",
            "NCBIfam":  "NCBIfam",
            "PANTHER":  "PANTHER",
            "PRINTS":   "PRINTS",
            "SFLD":     "SFLD",
            "SUPFAM":   "SUPERFAMILY",
            "CATHDB":   "CATH",   # UniProt uses `CATHDB`, our schema uses `CATH`
            "Gene3D":   "CATH",   # Gene3D IDs share the CATH namespace
        }.get(db)
        if prefix:
            curies.append(f"{prefix}:{acc}")
    # Preserve first-seen order.
    return list(dict.fromkeys(curies))


def _protein_label(entry: dict) -> str:
    """UniProt's `proteinDescription.recommendedName.fullName.value` when
    present; otherwise the entry's primary name."""
    pd = entry.get("proteinDescription") or {}
    rec = (pd.get("recommendedName") or {}).get("fullName") or {}
    if rec.get("value"):
        return rec["value"]
    for sub in pd.get("submissionNames") or []:
        v = (sub.get("fullName") or {}).get("value")
        if v:
            return v
    return entry.get("uniProtkbId") or entry.get("primaryAccession") or ""


def _organism(entry: dict) -> tuple[str, str]:
    org = entry.get("organism") or {}
    taxon_id = str(org.get("taxonId") or "")
    label = org.get("scientificName") or ""
    return taxon_id, label


def _query_anchor(record: dict, query: str) -> str:
    """The record CURIE that produced ``query``, or the record id for direct hits."""
    identifier = str(record.get("identifier") or "")
    if query.startswith("accession:"):
        return identifier
    for curie in [identifier, *(record.get("parent_traits") or []), *(record.get("xrefs") or [])]:
        if not isinstance(curie, str) or ":" not in curie:
            continue
        prefix, _, local = curie.partition(":")
        for known_prefix, database in _XREF_DISPATCH:
            if prefix == known_prefix and query == f"xref:{database}-{local}":
                return curie
    return identifier


def _candidate_scope(record: dict) -> str:
    axis = str(record.get("trait_axis") or "")
    category = str(record.get("trait_category") or "")
    namespace = str(record.get("identifier") or "").partition(":")[0]
    if axis in {"FUNCTION", "EVOLUTION"}:
        return "WHOLE_PROTEIN"
    if category in {
        "SEQ_FAMILY",
        "SEQ_HOMOLOGOUS_SUPERFAMILY",
        "FUNC_PROTEIN_FAMILY",
        "FUNC_ORTHOLOG_GROUP",
    } \
            and namespace in {"PANTHER", "NCBIfam", "PIRSF"}:
        return "WHOLE_PROTEIN"
    return "LOCALIZED"


def _whole_protein_permitted(record: dict) -> bool:
    """Mirror the semantic validator's explicit WHOLE_PROTEIN boundary."""

    return (
        record.get("trait_axis") in {"FUNCTION", "EVOLUTION"}
        or record.get("trait_category") in {"SEQ_FAMILY", "SEQ_HOMOLOGOUS_SUPERFAMILY"}
    )


def _is_exact_whole_protein_membership(
    *, trait_id: str, source_trait_id: str, scope: str, query: str, permitted: bool
) -> bool:
    """Gate the batch whose query can be replayed as an exact UniProt xref fact.

    This only routes candidates; the query hit itself is never trusted as evidence.
    The resolver must independently find the exact database+ID in the release-pinned
    membership snapshot produced by ``fetch_uniprot_registry.py``.
    """

    return (
        scope == "WHOLE_PROTEIN"
        and permitted
        and source_trait_id == trait_id
        and query.startswith("xref:")
    )


def _candidate_id(row: dict) -> str:
    identity = {
        key: row.get(key)
        for key in (
            "trait_id",
            "protein_id",
            "source_trait_id",
            "mapping_method",
            "evidence_source",
            "source_release",
            "query",
        )
    }
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "ug-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def entry_to_candidate(
    entry: dict,
    record: dict,
    record_path: str,
    query: str,
    release: str | None,
) -> dict:
    """Convert one API search hit into the external candidate-ledger contract."""
    acc = entry.get("primaryAccession")
    if not acc:
        return {}
    taxon_id, taxon_label = _organism(entry)
    ann = entry.get("annotationScore")
    if isinstance(ann, (int, float)):
        ann = int(ann)
    trait_id = str(record.get("identifier") or "")
    anchor = _query_anchor(record, query)
    scope = _candidate_scope(record)
    exact_whole_membership = _is_exact_whole_protein_membership(
        trait_id=trait_id,
        source_trait_id=anchor,
        scope=scope,
        query=query,
        permitted=_whole_protein_permitted(record),
    )
    reasons = ["full release-pinned sequence and checksum require resolution"]
    if exact_whole_membership:
        reasons.append(
            "exact membership must be replayed from a same-response UniProt xref snapshot"
        )
    if anchor != trait_id:
        reasons.append("query anchor is not the record's exact trait identifier")
    if scope == "LOCALIZED":
        reasons.append("record-specific occurrence coordinates require resolution")
    row = {
        "schema_version": 1,
        "batch": (
            READY_MEMBERSHIP_BATCH if exact_whole_membership else NEEDS_OCCURRENCE_BATCH
        ),
        "candidate_status": "PROTEIN_RESOLVED",
        "qualification_status": "CANDIDATE_PROTEIN",
        "trait_id": trait_id,
        "record_path": record_path,
        "trait_axis": record.get("trait_axis"),
        "trait_category": record.get("trait_category"),
        "source_namespace": trait_id.partition(":")[0],
        "protein_id": f"UniProtKB:{acc}",
        "protein_label": _protein_label(entry),
        "sequence_length": entry.get("sequence", {}).get("length"),
        "reviewed": entry.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
        "annotation_score": ann,
        "family_classifications": _extract_family_curies(entry),
        "scope": scope,
        "source_trait_id": anchor,
        "mapping_method": "SOURCE_MEMBERSHIP",
        "evidence_source": "UniProtKB",
        "source_release": release,
        "evidence_tier": "A" if anchor == trait_id else "D",
        "query": query,
        "reasons": reasons,
    }
    if taxon_id:
        row["taxon_id"] = f"NCBITaxon:{taxon_id}"
    if taxon_label:
        row["taxon_label"] = taxon_label
    row = {key: value for key, value in row.items() if value not in (None, "", [])}
    row["candidate_id"] = _candidate_id(row)
    return row


def write_candidates(path: Path, rows: list[dict]) -> None:
    """Atomically replace a deterministic JSONL candidate ledger."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for row in sorted(rows, key=lambda item: (item["trait_id"], item["protein_id"])):
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def collect_targets(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(TRAITS_DIR.rglob("*.yaml"))
    files: list[Path] = []
    for arg in paths:
        p = Path(arg)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if p.is_dir():
            files.extend(sorted(p.rglob("*.yaml")))
        elif p.is_file():
            files.append(p)
        else:
            matches = sorted(REPO_ROOT.glob(arg))
            if not matches:
                print(f"warn: no match for {arg}", file=sys.stderr)
            files.extend(matches)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*",
                        help="trait YAML files, dirs, or globs")
    parser.add_argument("--limit", type=int, default=5,
                        help="max API examples per record (default 5)")
    parser.add_argument("--include-unreviewed", action="store_true",
                        help="don't restrict to Swiss-Prot reviewed entries")
    parser.add_argument("--apply", action="store_true",
                        help="retired: direct record writes are refused")
    parser.add_argument("--stop-on-error", action="store_true",
                        help="abort at first HTTP failure (default: skip)")
    parser.add_argument("--refresh-sequences", action="store_true",
                        help="retired: use the grounding resolver and protein registry")
    parser.add_argument("--skip-with-examples", action="store_true",
                        help=("skip any record that already has a "
                              "canonical_example; legacy examples remain unverified"))
    parser.add_argument("--out", type=Path, default=DEFAULT_CANDIDATES,
                        help=f"candidate JSONL output (default: {DEFAULT_CANDIDATES})")
    args = parser.parse_args(argv)

    if args.apply or args.refresh_sequences:
        print(
            "direct canonical-example mutation is retired; emit candidates and use "
            "ground_uniprot_examples.py resolve/promote",
            file=sys.stderr,
        )
        return 2

    targets = collect_targets(args.paths)
    if not targets:
        print("no YAML files matched", file=sys.stderr)
        return 2

    rows: list[dict] = []
    records_with_candidates = 0
    skipped_no_query = 0
    errored = 0

    for path in targets:
        rel = path.relative_to(REPO_ROOT)
        try:
            record = read_trait(path)
        except Exception as exc:
            print(f"WARN {rel}: cannot parse ({exc})", file=sys.stderr)
            continue
        if args.skip_with_examples and record.get("canonical_examples"):
            continue
        queries = build_queries(record)
        if not queries:
            skipped_no_query += 1
            continue
        emitted: list[dict] = []
        used_query = ""
        for query, _note in queries:
            try:
                hits = search_uniprot(
                    query, args.limit, not args.include_unreviewed
                )
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                errored += 1
                print(f"WARN {rel}: UniProt fetch failed for {query} ({exc})",
                      file=sys.stderr)
                if args.stop_on_error:
                    return 1
                continue
            if not hits:
                continue
            emitted = [
                entry_to_candidate(h, record, str(rel), query, _last_uniprot_release)
                for h in hits
            ]
            emitted = [row for row in emitted if row]
            if emitted:
                used_query = query
                break
        if not emitted:
            continue
        records_with_candidates += 1
        rows.extend(emitted)
        print(f"  {rel}: +{len(emitted)} candidate(s) via {used_query}")

    # De-duplicate query aliases without making result order network-dependent.
    rows = list({row["candidate_id"]: row for row in rows}.values())
    write_candidates(args.out, rows)

    print()
    print(f"Scanned {len(targets)} record(s).")
    print(f"Emitted {len(rows)} candidate(s) across {records_with_candidates} record(s).")
    if skipped_no_query:
        print(f"Skipped {skipped_no_query} record(s) — no queryable anchor.")
    if errored:
        print(f"Errored on {errored} record(s).")
    print(f"Candidate ledger: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
