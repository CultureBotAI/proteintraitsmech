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
  docs/data/detail/NNN.json     — bucketed sidecars holding every field the
                                  list + facet views don't need: the full
                                  definition, path, parent_traits, xrefs,
                                  mapped_xrefs, chemical_participants, example
                                  proteins (with their heavy sequences + feature
                                  tracks), residue_sequence, and pattern. The
                                  browser fetches a record's bucket only when its
                                  detail view is opened. Records are hashed into
                                  DETAIL_BUCKETS files (one file per record would
                                  be 200k files and blow past the GitHub Pages
                                  Jekyll build's ~10-min file-copy timeout). Each
                                  bucket is `{record_id: detail}`; the record
                                  stores its bucket path in `"df"` (e.g.
                                  "detail/023.json"). This keeps the upfront
                                  list/facet payload ~5× smaller than inlining
                                  everything.
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
    "xr":  ["<xref>", ...],                  # source-direct cross-references
    "mx":  [["<object>", "<mapping_source>"], ...],  # mapping-derived xrefs
    "cp":  [["<chebi>", "<role>"], ...],     # chemical_participants (ChEBI+role)
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

# Number of detail-sidecar bucket files. Kept moderate: GitHub Pages' Jekyll
# builder copies every file in docs/ and times out around 10 min, so thousands
# of one-record files fail the build; but too few makes each bucket a large
# per-detail-view fetch. 200k records / 256 buckets ≈ 780 records per bucket
# (~350 KB, one cached fetch per detail view).
DETAIL_BUCKETS = 256

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
    if identifier.startswith("Pfam:"):
        return "Pfam"
    if identifier.startswith("CATH:"):
        return "CATH"
    if identifier.startswith("SCOP:"):
        return "SCOPe"
    if identifier.startswith("ECOD:"):
        return "ECOD"
    if identifier.startswith("DisProt:"):
        return "DisProt"
    if identifier.startswith("IDEAL:") or identifier == "proteintraitsmech:IDEAL_PROS":
        return "IDEAL"
    if identifier.startswith("IDPO:") or identifier.startswith("proteintraitsmech:IDPO_"):
        return "DisProt"
    if identifier.startswith("MCSA:"):
        return "M-CSA"
    if identifier.startswith("EC:"):
        return "ExPASy ENZYME"
    if identifier.startswith("Reactome:"):
        return "Reactome"
    if identifier.startswith("ARO:"):
        return "CARD/ARO"
    if identifier.startswith("TCDB:"):
        return "TCDB"
    if identifier.startswith("RHEA:"):
        return "Rhea"
    if identifier.startswith("RepeatsDB:"):
        return "RepeatsDB"
    if identifier.startswith("COG:") or identifier.startswith("proteintraitsmech:COG_CATEGORY_"):
        return "COG"
    if identifier.startswith("NCBIfam:"):
        return "NCBIfam"
    if identifier.startswith("CDD:"):
        return "CDD"
    if identifier.startswith("proteintraitsmech:UNIPROTKB_"):
        return "UniProtKB"
    if identifier.startswith(("proteintraitsmech:STABILITY_", "proteintraitsmech:EVO_")):
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
        # Mapping-derived xrefs, projected as [object, mapping_source] pairs so
        # the browser can render them distinctly from source-direct xrefs.
        "mx": [[m.get("object"), m.get("mapping_source")]
               for m in (data.get("mapped_xrefs") or []) if m.get("object")],
        # Chemistry the trait acts on, as [chebi, role] pairs; formula/InChIKey
        # resolve from docs/data/chebi.json in the browser.
        "cp": [[c.get("chebi"), c.get("role")]
               for c in (data.get("chemical_participants") or []) if c.get("chebi")],
        "ex": [_project_example(e) for e in (data.get("canonical_examples") or [])],
        "path": rel,
    }


# Axis display/shard order. Records with an unknown/empty axis fall into
# an "OTHER" shard so nothing is silently dropped.
AXIS_ORDER = ["STRUCTURE", "SEQUENCE", "SEQUENCE_STRUCTURE", "FUNCTION", "EVOLUTION"]

# Max records per shard file. Keeps each records.<AXIS>[.NN].json well under
# the git 50 MB warning (at ~0.5-1 KB/record in the lean projection).
MAX_SHARD_RECORDS = 25000


# Fields the list + facet views never touch — they exist only in the record
# detail view, so they move to a lazy per-record detail sidecar to keep the
# upfront payload small (~200k records × everything = ~108 MB → ~21 MB lean).
# `def` is special-cased: the list keeps a short snippet (card preview +
# search); the full text goes to the sidecar.
DETAIL_ONLY = ("path", "pt", "xr", "mx", "cp", "ex", "rs", "pat")
LIST_DEF = 140


def split_detail(records: list[dict]) -> list[tuple[dict, dict]]:
    """Move detail-only fields (and the full definition, keeping a short
    snippet inline) out of each record into a sidecar dict. Mutates records
    in place. Returns [(record, detail), …] for every record."""
    pairs: list[tuple[dict, dict]] = []
    for rec in records:
        detail: dict = {}
        full = rec.get("def") or ""
        if full:
            detail["def"] = full                 # full text → sidecar
            rec["def"] = truncate(full, LIST_DEF)  # short snippet stays inline
        for k in DETAIL_ONLY:
            v = rec.pop(k, None)
            if v not in (None, [], "", 0):
                detail[k] = v
        pairs.append((rec, detail))
    return pairs


def write_detail(pairs: list[tuple[dict, dict]]) -> tuple[int, int, float]:
    """Write bucketed detail sidecars under docs/data/detail/, clearing stale
    files first. Each record is hashed (stable md5 of its identifier) into one
    of DETAIL_BUCKETS files; the record stores its bucket path in `rec["df"]`
    (e.g. "detail/023.json") and each bucket is `{record_id: detail}`. Heavy
    example sequences ride along inside each detail's `ex`, so a detail view is
    a single lazy fetch. Returns (record_count, file_count, total_MB)."""
    det_dir = OUT_DIR / "detail"
    if det_dir.exists():
        for old in det_dir.glob("*.json"):
            old.unlink()
    det_dir.mkdir(parents=True, exist_ok=True)

    buckets: dict[str, dict[str, dict]] = {}
    for rec, detail in pairs:
        h = int(hashlib.md5(rec["id"].encode("utf-8")).hexdigest(), 16)
        name = f"detail/{h % DETAIL_BUCKETS:03d}.json"
        rec["df"] = name
        buckets.setdefault(name, {})[rec["id"]] = detail

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
        # Chunk large axes so no single shard approaches the 50 MB git
        # warning / 100 MB hard limit (STRUCTURE alone is ~90k records).
        chunks = [recs[i:i + MAX_SHARD_RECORDS]
                  for i in range(0, len(recs), MAX_SHARD_RECORDS)] or [[]]
        for idx, chunk in enumerate(chunks):
            fname = (f"records.{axis}.json" if len(chunks) == 1
                     else f"records.{axis}.{idx:02d}.json")
            path = OUT_DIR / fname
            with path.open("w", encoding="utf-8") as fh:
                json.dump(chunk, fh, separators=(",", ":"), ensure_ascii=False)
            written.add(fname)
            manifest.append({
                "file": fname,
                "axis": axis,
                "count": len(chunk),
                "bytes": path.stat().st_size,
            })
    # Drop stale shards from a prior build (empty axis, or a re-chunk that
    # changed the shard count).
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

    # Which axes each source / category / status appears in — lets the browser
    # lazily load only the axis shards a filter actually needs (a source or
    # category rarely spans all axes), instead of the whole corpus upfront.
    def _axes_by(field: str) -> dict[str, list[str]]:
        m: dict[str, set[str]] = {}
        for r in records:
            key, ax = r.get(field), r.get("axis")
            if key and ax:
                m.setdefault(key, set()).add(ax)
        return {k: sorted(v) for k, v in m.items()}

    axes_by = {"src": _axes_by("src"), "cat": _axes_by("cat"), "sta": _axes_by("sta")}

    pairs = split_detail(records)
    det_count, det_files, det_mb = write_detail(pairs)
    shards = write_shards(records)

    facets_path = OUT_DIR / "facets.json"
    with facets_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "total": len(records),
                "counts": facets,
                "axesBy": axes_by,
                "shards": shards,
                "detailDir": "detail",
            },
            fh,
            indent=2,
        )

    print(f"Wrote {len(records)} records across {len(shards)} axis shard(s):")
    for s in shards:
        print(f"  {s['file']:34s} {s['count']:>7,}  ({s['bytes'] / (1024 * 1024):.2f} MB)")
    print(f"Wrote {det_count:,} detail sidecars into {det_files} bucket file(s) → "
          f"docs/data/detail/ ({det_mb:.2f} MB total)")
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
