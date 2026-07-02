#!/usr/bin/env python3
"""Build docs/data/records.json — a single JSON index used by
`docs/browse.html` for client-side faceted browsing over every
ProteinTraitRecord YAML.

Kept intentionally lean per record so 18K entries stay under ~10 MB
uncompressed. The browser renders detail pages from this index on the
fly; nothing else is generated per record.

Run:
  python3 scripts/build_docs_index.py

Output:
  docs/data/records.<AXIS>.json — records sharded by trait_axis (one file
                                  per axis; the browser fetches them in
                                  parallel and merges). Keeps any single
                                  file well under the 100 MB git limit.
  docs/data/seq/NNN.json        — bucketed sidecars holding the heavy example
                                  sequences + feature tracks, lazy-fetched by
                                  the browser only when a record detail view is
                                  opened. Records are hashed into a small,
                                  fixed number of bucket files (see
                                  SEQ_BUCKETS) — one file per record would be
                                  thousands of files and blows past the GitHub
                                  Pages Jekyll build's ~10-minute file-copy
                                  timeout. Each bucket is `{record_id: sidecar}`;
                                  the record stores its bucket path in `"sf"`
                                  (e.g. "seq/023.json") so the browser fetches
                                  it directly, and each example that has a
                                  sequence is flagged `"sq": 1`.
  docs/data/facets.json         — pre-computed facet counts + a `shards`
                                  manifest listing the per-axis files.

Record shape:
  {
    "id": "<identifier>",
    "label": "...",
    "def": "...",                     # truncated to ~500 chars
    "axis": "SEQUENCE" | "STRUCTURE" | "SEQUENCE_STRUCTURE" | "FUNCTION",
    "cat": "SEQ_MOTIF" | ...,
    "src": "PROSITE" | "TED" | "UniProtKB" | "LinkML LSF" | "manual",
    "sta": "SEEDED" | "REVIEWED" | ...,
    "pat": "<sequence_pattern or null>",
    "rs":  "<residue_sequence or null>",     # concrete residues
    "pt":  ["<parent_curie>", ...],          # parent_traits CURIEs
    "xr":  ["<xref>", ...],
    "ex":  [                                 # canonical_examples (lean projection)
      {
        "id":    "UniProtKB:P62258",
        "label": "14-3-3 protein epsilon",
        "tax":   "Homo sapiens (NCBITaxon:9606)",
        "len":   255,
        "rev":   true,
        "asc":   5,                          # annotation_score
        "fams":  ["Pfam:PF00244", ...],
        "src":   "UNIPROTKB_API",
        "seq":   "MDDREDLVYQAK...",          # full amino-acid sequence
        "feats": [                           # [start, end, ft_type, axis, note]
          [1, 255, "CHAIN", "SEQUENCE", "14-3-3 protein epsilon"],
          [234, 255, "REGION", "SEQUENCE", "Disordered"],
          [57, 57, "SITE", "STRUCTURE", "Interaction with phosphoserine"],
          ...
        ]
      }, ...
    ],
    "path": "data/traits/.../slug.yaml"     # for GitHub raw link
  }
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Number of sequence-sidecar bucket files. Keep this small: GitHub Pages'
# Jekyll builder copies every file in docs/ and times out around 10 min, so
# thousands of one-record files fail the build. ~4.5k seq records / 64 buckets
# ≈ 70 records (~200 KB) per bucket — one small fetch per detail view, cached.
SEQ_BUCKETS = 64

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "docs" / "data"
DEF_TRUNC = 500


def infer_source(identifier: str, path: Path) -> str:
    if identifier.startswith("PROSITE:"):
        return "PROSITE"
    if identifier.startswith("TED:"):
        return "TED"
    if identifier.startswith("MOD:"):
        return "PSI-MOD"
    if identifier.startswith("MI:"):
        return "PSI-MI"
    if identifier.startswith("PATO:"):
        return "PATO"
    if identifier.startswith("METPO:"):
        return "METPO"
    if identifier.startswith("InterPro:"):
        return "InterPro"
    if identifier.startswith("ECOD:"):
        return "ECOD"
    if identifier.startswith("DisProt:"):
        return "DisProt"
    if identifier.startswith("MCSA:"):
        return "M-CSA"
    if identifier.startswith("proteintraitsmech:UNIPROTKB_"):
        return "UniProtKB"
    if identifier.startswith("proteintraitsmech:STABILITY_"):
        return "curated"
    if identifier.startswith("proteintraitsmech:"):
        # LSF seed used bare TERM names; UniProt uses UNIPROTKB_ prefix.
        return "LinkML LSF"
    return "manual"


def truncate(text: str, limit: int = DEF_TRUNC) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _project_example(ex: dict) -> dict:
    """Lean projection of a CanonicalExample suitable for the browser
    detail view. Skips empty fields to keep records.json small."""
    proj: dict = {}
    if ex.get("protein_id"):
        proj["id"] = ex["protein_id"]
    if ex.get("protein_label"):
        proj["label"] = ex["protein_label"]
    tax = ex.get("taxon_label") or ""
    if ex.get("taxon_id"):
        tax = f"{tax} ({ex['taxon_id']})" if tax else ex["taxon_id"]
    if tax:
        proj["tax"] = tax
    if ex.get("sequence_length"):
        proj["len"] = ex["sequence_length"]
    if "reviewed" in ex:
        proj["rev"] = bool(ex["reviewed"])
    if ex.get("annotation_score"):
        proj["asc"] = ex["annotation_score"]
    if ex.get("family_classifications"):
        proj["fams"] = list(ex["family_classifications"])
    if ex.get("source"):
        proj["src"] = ex["source"]
    if ex.get("note"):
        proj["note"] = ex["note"]
    if ex.get("sequence"):
        proj["seq"] = ex["sequence"]
    feats = ex.get("features") or []
    if feats:
        # Compact tuple form to keep JSON small — the browser expands
        # into objects: [start, end, feature_type, trait_axis, note?]
        proj["feats"] = [
            [f["start"], f["end"], f["feature_type"],
             f.get("trait_axis") or "", f.get("note") or ""]
            for f in feats
        ]
    return proj


def load_record(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        print(f"WARN: {path.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        return None
    identifier = data.get("identifier") or ""
    if not identifier:
        return None
    rel = path.relative_to(REPO_ROOT).as_posix()
    return {
        "id": identifier,
        "label": data.get("label") or identifier,
        "def": truncate(data.get("definition") or ""),
        "axis": data.get("trait_axis") or "",
        "cat": data.get("trait_category") or "",
        "src": infer_source(identifier, path),
        "sta": data.get("mapping_status") or "",
        "pat": data.get("sequence_pattern") or None,
        "rs": data.get("residue_sequence") or None,
        "pt": list(data.get("parent_traits") or []),
        "xr": list(data.get("xrefs") or []),
        "ex": [_project_example(e) for e in (data.get("canonical_examples") or [])],
        "path": rel,
    }


# Axis display/shard order. Records with an unknown/empty axis fall into
# an "OTHER" shard so nothing is silently dropped.
AXIS_ORDER = ["STRUCTURE", "SEQUENCE", "SEQUENCE_STRUCTURE", "FUNCTION"]


def split_sequences(records: list[dict]) -> list[tuple[dict, list]]:
    """Move heavy per-example `seq`/`feats` out of each record into a
    sidecar list aligned to that record's `ex` array. Mutates records in
    place: pops seq/feats and flags each sequence-bearing example (`sq=1`).
    Returns [(record, sidecar), …] for records that had any sequence."""
    pairs: list[tuple[dict, list]] = []
    for rec in records:
        exs = rec.get("ex") or []
        side: list = []
        has = False
        for e in exs:
            if e.get("seq"):
                side.append({"seq": e.pop("seq"), "feats": e.pop("feats", [])})
                e["sq"] = 1
                has = True
            else:
                # feats are meaningless without a sequence to render on.
                e.pop("feats", None)
                side.append(None)
        if has:
            pairs.append((rec, side))
    return pairs


def write_sequences(pairs: list[tuple[dict, list]]) -> tuple[int, int, float]:
    """Write bucketed sequence sidecars under docs/data/seq/, clearing any
    stale files first. Each record is hashed (stable md5 of its identifier)
    into one of SEQ_BUCKETS files; the record stores its bucket path in
    `rec["sf"]` (e.g. "seq/023.json") and each bucket file is a JSON object
    `{record_id: sidecar}`. Returns (record_count, file_count, total_MB)."""
    seq_dir = OUT_DIR / "seq"
    if seq_dir.exists():
        for old in seq_dir.glob("*.json"):
            old.unlink()
    seq_dir.mkdir(parents=True, exist_ok=True)

    buckets: dict[str, dict[str, list]] = {}
    for rec, side in pairs:
        h = int(hashlib.md5(rec["id"].encode("utf-8")).hexdigest(), 16)
        name = f"seq/{h % SEQ_BUCKETS:03d}.json"
        rec["sf"] = name
        buckets.setdefault(name, {})[rec["id"]] = side

    total = 0
    for name, obj in buckets.items():
        path = OUT_DIR / name
        with path.open("w", encoding="utf-8") as fh:
            json.dump(obj, fh, separators=(",", ":"), ensure_ascii=False)
        total += path.stat().st_size
    return len(pairs), len(buckets), total / (1024 * 1024)


def write_shards(records: list[dict]) -> list[dict]:
    """Write records.<AXIS>.json (one file per trait_axis) and return the
    shard manifest. Also clears the legacy monolithic records.json and any
    stale records.*.json shard for an axis that no longer has records, so
    the build is self-correcting."""
    legacy = OUT_DIR / "records.json"
    if legacy.exists():
        legacy.unlink()

    by_axis: dict[str, list[dict]] = {}
    for rec in records:
        by_axis.setdefault(rec.get("axis") or "OTHER", []).append(rec)

    def axis_key(a: str) -> tuple[int, str]:
        return (AXIS_ORDER.index(a) if a in AXIS_ORDER else 99, a)

    manifest: list[dict] = []
    written: set[str] = set()
    for axis in sorted(by_axis, key=axis_key):
        recs = sorted(by_axis[axis], key=lambda r: r["id"])
        fname = f"records.{axis}.json"
        path = OUT_DIR / fname
        with path.open("w", encoding="utf-8") as fh:
            json.dump(recs, fh, separators=(",", ":"), ensure_ascii=False)
        written.add(fname)
        manifest.append({
            "file": fname,
            "axis": axis,
            "count": len(recs),
            "bytes": path.stat().st_size,
        })
    # Drop stale shards from a prior build whose axis is now empty.
    for old in OUT_DIR.glob("records.*.json"):
        if old.name not in written:
            old.unlink()
    return manifest


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    skipped = 0
    for path in sorted(TRAITS_DIR.rglob("*.yaml")):
        rec = load_record(path)
        if rec is None:
            skipped += 1
            continue
        records.append(rec)

    # Stable sort by identifier so JSON diffs stay small.
    records.sort(key=lambda r: r["id"])

    # Facets are computed before the seq split (which only removes example
    # payload, not any faceted field).
    facets = {
        "axis": _tally(records, "axis"),
        "cat": _tally(records, "cat"),
        "src": _tally(records, "src"),
        "sta": _tally(records, "sta"),
    }

    pairs = split_sequences(records)
    seq_count, seq_files, seq_mb = write_sequences(pairs)
    shards = write_shards(records)

    facets_path = OUT_DIR / "facets.json"
    with facets_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "total": len(records),
                "counts": facets,
                "shards": shards,
                "seqDir": "seq",
            },
            fh,
            indent=2,
        )

    print(f"Wrote {len(records)} records across {len(shards)} axis shard(s):")
    for s in shards:
        print(f"  {s['file']:34s} {s['count']:>7,}  ({s['bytes'] / (1024 * 1024):.2f} MB)")
    print(f"Wrote {seq_count:,} sequences into {seq_files} bucket file(s) → "
          f"docs/data/seq/ ({seq_mb:.2f} MB total)")
    print(f"Wrote facet index → {facets_path.relative_to(REPO_ROOT)}")
    if skipped:
        print(f"Skipped {skipped} unparseable files")
    return 0


def _tally(records: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in records:
        v = r.get(key)
        if not v:
            continue
        counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


if __name__ == "__main__":
    sys.exit(main())
