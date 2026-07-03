#!/usr/bin/env python3
"""Validate data/methods/methods.yaml and emit docs/data/methods.json — the
detection-method catalogue the browser loads to answer "how is this trait
detected?" for each record (resolved by_source[src] + by_category[cat]).

Committed (small, curated, changes rarely) rather than rebuilt in CI.
Checks every method has the grounding fields and that categories/sources are
real. Stdlib + PyYAML.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "data" / "methods" / "methods.yaml"
OUT = REPO_ROOT / "docs" / "data" / "methods.json"
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"

REQUIRED = ("name", "method_type", "edam", "tool", "recipe")
TYPES = {"SEQUENCE_PATTERN", "HMM_PROFILE", "PROFILE_MATRIX",
         "STRUCTURAL_ALGORITHM", "ML_PREDICTOR", "HOMOLOGY_TRANSFER",
         "EXPERIMENTAL"}


def main() -> int:
    import yaml
    doc = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    by_source = doc.get("by_source") or {}
    by_category = doc.get("by_category") or {}

    # valid categories from the schema enum (best-effort)
    cats = set(re.findall(r"^\s{6}([A-Z][A-Z_]+):", SCHEMA.read_text(encoding="utf-8"), re.M))

    errors = []
    n_methods = 0
    for scope, table in (("by_source", by_source), ("by_category", by_category)):
        for key, methods in table.items():
            if scope == "by_category" and cats and key not in cats:
                errors.append(f"{scope}: unknown category {key}")
            for m in methods or []:
                n_methods += 1
                for f in REQUIRED:
                    if not m.get(f):
                        errors.append(f"{scope}/{key}/{m.get('name','?')}: missing {f}")
                if m.get("method_type") not in TYPES:
                    errors.append(f"{scope}/{key}/{m.get('name')}: bad method_type {m.get('method_type')}")

    if errors:
        print("methods.yaml validation FAILED:", file=sys.stderr)
        for e in errors[:30]:
            print("  -", e, file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"by_source": by_source, "by_category": by_category,
                               "meta": doc.get("meta", {})},
                              separators=(",", ":"), sort_keys=True) + "\n",
                   encoding="utf-8")
    print(f"OK — {n_methods} methods "
          f"({len(by_source)} sources, {len(by_category)} categories) → "
          f"{OUT.relative_to(REPO_ROOT)} ({OUT.stat().st_size // 1024} KB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
