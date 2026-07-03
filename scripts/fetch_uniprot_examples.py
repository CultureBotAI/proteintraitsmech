#!/usr/bin/env python3
"""Populate `canonical_examples` on ProteinTraitRecord YAMLs by querying
the UniProtKB REST API for entries carrying each trait's anchoring
signature.

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
    CATH:...            → xref:cath-<local>
    proteintraitsmech:UNIPROTKB_<ACC>_...  → direct: accession:<ACC>
                           (canonical example for a UniProt-seeded record
                           is the source entry itself)
    TED:AF-<UNIPROT>-... → direct: accession:<UNIPROT>

Everything is filtered by `reviewed:true` (Swiss-Prot) by default so
API examples are annotated entries, not TrEMBL guesses. Override with
`--include-unreviewed`.

Per accession returned by search, one CanonicalExample is written with:
  protein_id, protein_label, taxon_id, taxon_label,
  sequence_length, reviewed, annotation_score,
  family_classifications (Pfam / InterPro / HAMAP / SMART / CATH refs on
  that specific entry), note (the UniProt query used), source =
  UNIPROTKB_API, fetched_at (today, UTC ISO date).

Idempotent — accessions already listed on the record are skipped unless
--force is passed. Dry-run by default; --apply to write.

Rate: 4 req/s soft cap + exponential backoff on 429/503. Stdlib-only.

Usage:
  python3 scripts/fetch_uniprot_examples.py \\
      data/traits/sequence/pattern/1433-1.yaml \\
      --limit 5 --apply
  python3 scripts/fetch_uniprot_examples.py \\
      data/traits/sequence/pattern/ --limit 3 --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"

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
    "xref_interpro",
    "xref_prosite",
    "xref_smart",
    "xref_hamap",
    "xref_gene3d",  # UniProt's key for the CATH namespace
])
USER_AGENT = "proteintraitsmech-example-fetcher/0.1"

# Rate limiting — UniProt tolerates ~10 req/s but we stay conservative
# (mostly bounded by fetch latency anyway).
MIN_INTERVAL_S = 0.25
_last_req = 0.0


# ---------------------------------------------------------------------------
# Trait YAML I/O (minimal — round-trip via PyYAML would reorder keys and
# blow up existing folded scalars, so we insert examples with light textual
# manipulation instead)
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


def write_trait(path: Path, data: dict) -> None:
    """Emit the trait YAML back to disk. We preserve the seeder's key
    order by rebuilding the file with a fixed order rather than round-
    tripping through PyYAML's default emitter (which loses folded
    scalars and reorders keys)."""
    import yaml

    class FoldedDefinition(str):
        """Marker so definition strings emit as folded scalars."""

    def _folded_representer(dumper, data):
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data, style=">"
        )

    yaml.add_representer(FoldedDefinition, _folded_representer)

    key_order = [
        "identifier", "label", "definition", "definition_source",
        "trait_axis", "trait_category", "term_kind", "mapping_status",
        "parent_traits", "sequence_pattern", "residue_sequence",
        "xrefs", "canonical_examples", "evidence", "curation_history",
        "causal_graphs",
    ]
    ordered = {}
    for k in key_order:
        if k in data:
            ordered[k] = data[k]
    for k in data:  # any straggler keys the seeder didn't anticipate
        if k not in ordered:
            ordered[k] = data[k]

    if "definition" in ordered and isinstance(ordered["definition"], str):
        ordered["definition"] = FoldedDefinition(ordered["definition"])

    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            ordered,
            fh,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100000,
        )


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
    ("InterPro", "interpro"),
    ("HAMAP",    "hamap"),
    ("SMART",    "smart"),
    ("CATH",     "cath"),
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
    for attempt in range(5):
        _throttle()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
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
            "Pfam":     "Pfam",
            "InterPro": "InterPro",
            "PROSITE":  "PROSITE",
            "SMART":    "SMART",
            "HAMAP":    "HAMAP",
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


def entry_to_example(entry: dict, query_note: str, today: str) -> dict:
    acc = entry.get("primaryAccession")
    if not acc:
        return {}
    taxon_id, taxon_label = _organism(entry)
    ann = entry.get("annotationScore")
    # UniProt returns annotation_score as 1.0-5.0 (float); the schema
    # constrains it to an integer 1-5.
    if isinstance(ann, (int, float)):
        ann = int(ann)
    ex = {
        "protein_id": f"UniProtKB:{acc}",
        "protein_label": _protein_label(entry),
        "sequence_length": entry.get("sequence", {}).get("length"),
        "reviewed": entry.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
        "annotation_score": ann,
        "family_classifications": _extract_family_curies(entry),
        "note": f"UniProt REST search: {query_note}",
        "source": "UNIPROTKB_API",
        "fetched_at": today,
    }
    if taxon_id:
        ex["taxon_id"] = f"NCBITaxon:{taxon_id}"
    if taxon_label:
        ex["taxon_label"] = taxon_label
    return ex


# ---------------------------------------------------------------------------
# Merge into record
# ---------------------------------------------------------------------------


def merge_examples(record: dict, new_examples: list[dict], force: bool) -> int:
    existing = list(record.get("canonical_examples") or [])
    existing_ids = {e.get("protein_id") for e in existing}
    if force:
        # Drop prior UNIPROTKB_API examples so this pass reflects the
        # latest UniProt state.
        existing = [
            e for e in existing
            if e.get("source") != "UNIPROTKB_API"
        ]
        existing_ids = {e.get("protein_id") for e in existing}
    added = 0
    for ex in new_examples:
        if not ex.get("protein_id") or ex["protein_id"] in existing_ids:
            continue
        # Strip keys with None values — the schema allows them, but they
        # bloat the YAML with `sequence_length: null` etc.
        ex = {k: v for k, v in ex.items() if v not in (None, [], "")}
        existing.append(ex)
        existing_ids.add(ex["protein_id"])
        added += 1
    if existing:
        record["canonical_examples"] = existing
    return added


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


# How many accessions to pack into one `/accessions` request. The endpoint
# accepts up to 100; 90 leaves headroom. Batching across records is what
# makes a large category (e.g. ~14k TED folds, ~1 accession each) fetch in
# minutes rather than hours — one request per record would be ~14k round
# trips; one request per 90 records is ~150.
ACCESSION_BATCH = 90


def refresh_sequences(
    targets: list[Path],
    apply_: bool,
    stop_on_error: bool,
) -> tuple[int, int, int, int]:
    """For every example anchored to a real UniProtKB accession that lacks a
    `sequence`, fill in `sequence` + `features`. Preserves every other
    example field (annotation_score, family_classifications, etc.).

    Accessions are pooled across *all* target records and fetched in batches
    of ACCESSION_BATCH via the `/accessions` endpoint, so a large category is
    ~N/90 round trips instead of one per record.

    Returns (records_touched, examples_enriched, records_skipped, errored)."""
    touched = enriched = skipped = errored = 0

    # ---- Pass 1: parse every record, collect the accessions it needs. ----
    pending: list[tuple[Path, dict]] = []  # records with at least one need
    all_accs: list[str] = []
    seen_acc: set[str] = set()
    for path in targets:
        rel = path.relative_to(REPO_ROOT)
        try:
            record = read_trait(path)
        except Exception as exc:
            print(f"WARN {rel}: cannot parse ({exc})", file=sys.stderr)
            continue
        need = [
            e for e in (record.get("canonical_examples") or [])
            if (e.get("protein_id") or "").startswith("UniProtKB:")
            and not e.get("sequence")
        ]
        if not need:
            skipped += 1
            continue
        pending.append((path, record))
        for e in need:
            acc = e["protein_id"].split(":", 1)[1]
            if acc not in seen_acc:
                seen_acc.add(acc)
                all_accs.append(acc)

    if not pending:
        return (touched, enriched, skipped, errored)

    # ---- Pass 2: batch-fetch the pooled accessions into one lookup. ----
    by_acc: dict = {}
    n_batches = (len(all_accs) + ACCESSION_BATCH - 1) // ACCESSION_BATCH
    for i in range(0, len(all_accs), ACCESSION_BATCH):
        chunk = all_accs[i:i + ACCESSION_BATCH]
        try:
            entries = fetch_flat_entries(chunk)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            errored += 1
            print(f"WARN batch {i // ACCESSION_BATCH + 1}/{n_batches} "
                  f"failed ({exc})", file=sys.stderr)
            if stop_on_error:
                return (touched, enriched, skipped, errored)
            continue
        for e in entries:
            if e.accession:
                by_acc[e.accession] = e
        print(f"  fetched batch {i // ACCESSION_BATCH + 1}/{n_batches} "
              f"({len(by_acc)}/{len(all_accs)} accessions resolved)")

    # ---- Pass 3: fill sequences + features from the lookup, write. ----
    for path, record in pending:
        rel = path.relative_to(REPO_ROOT)
        record_enriched = 0
        for ex in record.get("canonical_examples") or []:
            pid = ex.get("protein_id") or ""
            if ":" not in pid or ex.get("sequence"):
                continue
            src_entry = by_acc.get(pid.split(":", 1)[1])
            if src_entry is None or not src_entry.sequence:
                continue
            ex["sequence"] = src_entry.sequence
            feats = flat_features_for_example(src_entry)
            if feats:
                ex["features"] = feats
            record_enriched += 1
        if record_enriched:
            touched += 1
            enriched += record_enriched
            if apply_:
                write_trait(path, record)
    return (touched, enriched, skipped, errored)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*",
                        help="trait YAML files, dirs, or globs")
    parser.add_argument("--limit", type=int, default=5,
                        help="max API examples per record (default 5)")
    parser.add_argument("--include-unreviewed", action="store_true",
                        help="don't restrict to Swiss-Prot reviewed entries")
    parser.add_argument("--apply", action="store_true",
                        help="write back to disk (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="drop existing UNIPROTKB_API examples and re-fetch")
    parser.add_argument("--stop-on-error", action="store_true",
                        help="abort at first HTTP failure (default: skip)")
    parser.add_argument("--refresh-sequences", action="store_true",
                        help=("fill in `sequence` + `features` on existing "
                              "UNIPROTKB_API examples via a batch flat-file "
                              "fetch; does not add new examples"))
    args = parser.parse_args(argv)

    targets = collect_targets(args.paths)
    if not targets:
        print("no YAML files matched", file=sys.stderr)
        return 2

    if args.refresh_sequences:
        touched, enriched, skipped, errored = refresh_sequences(
            targets, args.apply, args.stop_on_error,
        )
        print()
        print(f"Scanned {len(targets)} record(s).")
        print(f"Enriched {enriched} example(s) across {touched} record(s).")
        if skipped:
            print(f"Skipped {skipped} record(s) — nothing to enrich.")
        if errored:
            print(f"Errored on {errored} record(s).")
        if not args.apply:
            print("Dry-run — re-run with --apply to write.")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_added = 0
    total_records = 0
    skipped_no_query = 0
    errored = 0

    for path in targets:
        rel = path.relative_to(REPO_ROOT)
        try:
            record = read_trait(path)
        except Exception as exc:
            print(f"WARN {rel}: cannot parse ({exc})", file=sys.stderr)
            continue
        candidates = build_queries(record)
        if not candidates:
            skipped_no_query += 1
            continue
        # Try each candidate; take the first that yields at least one
        # *new* example. A candidate whose only hit is the record's
        # existing example (common for UniProt-seeded records whose
        # source entry is already listed) still counts as consumed —
        # we fall through to the next family-level query.
        added = 0
        used_note = ""
        for query, cand_note in candidates:
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
            examples = [entry_to_example(h, cand_note, today) for h in hits]
            examples = [e for e in examples if e]
            added = merge_examples(record, examples, args.force)
            if added:
                used_note = cand_note
                break
        if not added:
            continue
        total_records += 1
        total_added += added
        print(f"  {rel}: +{added} example(s) via {used_note}")
        if args.apply:
            write_trait(path, record)

    print()
    print(f"Scanned {len(targets)} record(s).")
    print(f"Added {total_added} example(s) across {total_records} record(s).")
    if skipped_no_query:
        print(f"Skipped {skipped_no_query} record(s) — no queryable anchor.")
    if errored:
        print(f"Errored on {errored} record(s).")
    if not args.apply:
        print("Dry-run — re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
