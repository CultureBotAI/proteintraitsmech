#!/usr/bin/env python3
"""Score each source/tool by the *value* of the traits it produces vs its
*compute cost*, to find the core subset of tools that give the most value for the
least computation.

Value model (per record, each component in [0,1], transparent + tweakable):
  groundings  min(#xrefs + #mapped_xrefs, 6) / 6   — cross-referenced = connected
  evidence    1 if an `evidence:` block (DOI/PMID) else 0 — citation-backed
  definition  min(len(definition), 400) / 400        — real content vs a stub
  layered     1 if a `definitions:` list (STRUCTURAL/MECHANISTIC/GENERAL) else 0
  represent.  1 if any representation slot (sequence_pattern / secondary_structure
              / structural_geometry / chemical_participants) else 0
  hierarchy   1 if parent_traits else 0
  value = weighted sum (weights below), normalized to [0,1].

Compute cost ∝ record count: the dominant recurring cost is per-record text
embedding (+ neighbours + map), which scales linearly with #records. So a tool's
"compute share" is its share of all records.

Output: per-tool table (records, mean value, total value, value-density) + the
Pareto/core subset that captures most of the total value for the least compute.
Read-only; ~1-2 min over the corpus. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"

WEIGHTS = {"groundings": 0.25, "evidence": 0.20, "definition": 0.20,
           "layered": 0.15, "representation": 0.10, "hierarchy": 0.10}
REP_SLOTS = ("sequence_pattern:", "secondary_structure_representations:",
             "structural_geometry_representations:", "chemical_participants:")
_DEF_RE = re.compile(r"^definition:\s*>-\s*\n((?:\s+.*\n)+)", re.M)


# A few identifier prefixes normalize to a canonical tool name.
_PREFIX_TOOL = {"scop": "scope", "rhea": "rhea", "go": "go", "cazy": "cazy"}


def source_of(text: str, path: Path) -> str:
    """The seeder/source, keyed on the identifier CURIE prefix (the authoritative
    provenance). Curator-minted `proteintraitsmech:` ids fall back to the source
    sub-directory that produced them."""
    m = re.search(r"(?m)^identifier:\s*([A-Za-z0-9_]+):", text)
    if not m:
        return path.parent.name
    pref = m.group(1).lower()
    if pref == "proteintraitsmech":
        return f"curated/{path.parent.name}"
    return _PREFIX_TOOL.get(pref, pref)


def _xrefs_block(text: str) -> str:
    """The `xrefs:` list body (up to the next top-level key), for counting items."""
    m = re.search(r"(?m)^xrefs:\s*\n((?:[ \t]+.*\n?)+)", text)
    return m.group(1) if m else ""


def score(text: str) -> tuple[float, dict]:
    # grounding CURIEs = xrefs list items + mapped_xrefs `object:` lines
    n_x = len(re.findall(r"(?m)^[ \t]+-\s+\S+", _xrefs_block(text)))
    n_mx = len(re.findall(r"(?m)^\s*(?:-\s+)?object:\s*\S", text))
    groundings = min(n_x + n_mx, 6) / 6
    evidence = 1.0 if re.search(r"(?m)^evidence:", text) else 0.0
    m = _DEF_RE.search(text)
    deflen = len(" ".join(m.group(1).split())) if m else 0
    definition = min(deflen, 400) / 400
    layered = 1.0 if re.search(r"(?m)^definitions:", text) else 0.0
    representation = 1.0 if any(s in text for s in REP_SLOTS) else 0.0
    hierarchy = 1.0 if re.search(r"(?m)^parent_traits:", text) else 0.0
    comp = {"groundings": groundings, "evidence": evidence, "definition": definition,
            "layered": layered, "representation": representation, "hierarchy": hierarchy}
    val = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
    return val, comp


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit raw per-tool JSON")
    args = ap.parse_args()

    agg: dict[str, dict] = {}
    for root, _, files in os.walk(TRAITS):
        for fn in files:
            if not fn.endswith(".yaml"):
                continue
            p = Path(root) / fn
            text = p.read_text(encoding="utf-8", errors="replace")
            src = source_of(text, p)
            val, comp = score(text)
            a = agg.setdefault(src, {"n": 0, "val": 0.0,
                                     **{k: 0.0 for k in WEIGHTS}})
            a["n"] += 1
            a["val"] += val
            for k in WEIGHTS:
                a[k] += comp[k]

    total_n = sum(a["n"] for a in agg.values())
    total_val = sum(a["val"] for a in agg.values())
    rows = []
    for src, a in agg.items():
        n = a["n"]
        rows.append({
            "tool": src, "records": n,
            "mean_value": a["val"] / n,
            "total_value": a["val"],
            "compute_share": n / total_n,
            "value_share": a["val"] / total_val,
            # value captured per unit compute: value_share / compute_share (>1 = above average)
            "efficiency": (a["val"] / total_val) / (n / total_n),
            **{k: a[k] / n for k in WEIGHTS},
        })

    if args.json:
        print(json.dumps({"total_records": total_n, "total_value": total_val,
                          "tools": rows}, indent=2))
        return 0

    rows.sort(key=lambda r: -r["total_value"])
    print(f"{'tool':<14}{'recs':>8}{'mean':>7}{'totVal':>9}{'cmp%':>7}{'val%':>7}{'eff':>6}  top components")
    for r in rows:
        comps = sorted(((k, r[k]) for k in WEIGHTS), key=lambda kv: -kv[1])[:3]
        cs = " ".join(f"{k[:4]}={v:.2f}" for k, v in comps)
        print(f"{r['tool']:<14}{r['records']:>8,}{r['mean_value']:>7.2f}"
              f"{r['total_value']:>9.0f}{r['compute_share']*100:>6.1f}%"
              f"{r['value_share']*100:>6.1f}%{r['efficiency']:>6.2f}  {cs}")

    # Core subset: greedily add tools by efficiency (value per compute) until we
    # capture 80% of total value; report the compute that buys.
    print("\n== Core subset (by value-per-compute efficiency) ==")
    by_eff = sorted(rows, key=lambda r: -r["efficiency"])
    cum_v = cum_c = 0.0
    for r in by_eff:
        cum_v += r["value_share"]; cum_c += r["compute_share"]
        print(f"  +{r['tool']:<13} eff={r['efficiency']:.2f}  "
              f"cum value {cum_v*100:5.1f}%  cum compute {cum_c*100:5.1f}%")
        if cum_v >= 0.80:
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
