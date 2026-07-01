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
  docs/data/records.json      — array of record objects (see below)
  docs/data/facets.json       — pre-computed facet counts

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

import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
OUT_DIR = REPO_ROOT / "docs" / "data"
DEF_TRUNC = 500


def infer_source(identifier: str, path: Path) -> str:
    if identifier.startswith("PROSITE:"):
        return "PROSITE"
    if identifier.startswith("TED:"):
        return "TED"
    if identifier.startswith("proteintraitsmech:UNIPROTKB_"):
        return "UniProtKB"
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

    facets = {
        "axis": _tally(records, "axis"),
        "cat": _tally(records, "cat"),
        "src": _tally(records, "src"),
        "sta": _tally(records, "sta"),
    }

    records_path = OUT_DIR / "records.json"
    facets_path = OUT_DIR / "facets.json"
    with records_path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, separators=(",", ":"), ensure_ascii=False)
    with facets_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "total": len(records),
                "counts": facets,
            },
            fh,
            indent=2,
        )

    size_mb = records_path.stat().st_size / (1024 * 1024)
    print(f"Wrote {len(records)} records ({size_mb:.2f} MB) → {records_path.relative_to(REPO_ROOT)}")
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
