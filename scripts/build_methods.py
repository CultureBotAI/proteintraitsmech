#!/usr/bin/env python3
"""Validate data/methods/methods.yaml and emit docs/data/methods.json — the
detection-method catalogue the browser loads to answer "how is this trait
detected?" for each record (resolved by_source[src] + by_category[cat]).

Committed (small, curated, changes rarely) rather than rebuilt in CI.
Checks every method has the grounding fields and that categories/sources are
real. Stdlib + PyYAML.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "data" / "methods" / "methods.yaml"
OUT = REPO_ROOT / "docs" / "data" / "methods.json"
FACETS = REPO_ROOT / "docs" / "data" / "facets.json"
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
DOCS_INDEX_SCRIPT = REPO_ROOT / "scripts" / "build_docs_index.py"

REQUIRED = ("name", "method_type", "edam", "tool", "recipe")
TYPES = {"SEQUENCE_PATTERN", "HMM_PROFILE", "PROFILE_MATRIX",
         "STRUCTURAL_ALGORITHM", "ML_PREDICTOR", "HOMOLOGY_TRANSFER",
         "EXPERIMENTAL"}
ABSTRACT_CATEGORIES = {"UPPER", "OTHER"}
PLACEHOLDER_RE = re.compile(r"\{([A-Za-z0-9_.-]+)\}")
ALLOWED_PLACEHOLDERS = {"id", "curie", "pat", "input", "output", "db"}


def is_valid_placeholder(token: str) -> bool:
    return token in ALLOWED_PLACEHOLDERS or token.startswith(("input.", "output.", "db."))


def inferred_sources() -> set[str]:
    """Extract all source strings returned by infer_source() in build_docs_index.py."""
    if not DOCS_INDEX_SCRIPT.exists():
        return set()
    tree = ast.parse(DOCS_INDEX_SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "infer_source":
            return {
                sub.value.value
                for sub in ast.walk(node)
                if isinstance(sub, ast.Return)
                and isinstance(sub.value, ast.Constant)
                and isinstance(sub.value.value, str)
            }
    return set()


def main() -> int:
    import yaml
    doc = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    by_source = doc.get("by_source") or {}
    by_category = doc.get("by_category") or {}

    schema_doc = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    enums = schema_doc.get("enums") or {}
    enum_pvs = (enums.get("ProteinTraitCategoryEnum") or {}).get("permissible_values") or {}
    cats = set(enum_pvs.keys()) - ABSTRACT_CATEGORIES
    schema_types = set(
        ((enums.get("MethodTypeEnum") or {}).get("permissible_values") or {}).keys()
    ) or TYPES

    errors = []
    if schema_types != TYPES:
        errors.append(f"TYPES mismatch vs schema MethodTypeEnum: {TYPES ^ schema_types}")

    n_methods = 0
    for scope, table in (("by_source", by_source), ("by_category", by_category)):
        for key, methods in table.items():
            if scope == "by_category" and cats and key not in cats:
                errors.append(f"{scope}: unknown category {key}")
            if not methods:
                errors.append(f"{scope}/{key}: empty method list")
            for m in methods or []:
                n_methods += 1
                for f in REQUIRED:
                    if not m.get(f):
                        errors.append(f"{scope}/{key}/{m.get('name','?')}: missing {f}")
                recipe = str(m.get("recipe") or "").strip()
                if recipe.startswith("#"):
                    errors.append(
                        f"{scope}/{key}/{m.get('name','?')}: comment-only recipe {recipe!r}"
                    )
                for tok in PLACEHOLDER_RE.findall(recipe):
                    if not is_valid_placeholder(tok):
                        errors.append(
                            f"{scope}/{key}/{m.get('name','?')}: unsupported placeholder {{{tok}}}"
                        )
                if m.get("method_type") not in schema_types:
                    errors.append(f"{scope}/{key}/{m.get('name')}: bad method_type {m.get('method_type')}")

    for missing_cat in sorted(cats - set(by_category.keys())):
        errors.append(f"by_category: missing concrete schema category {missing_cat}")

    for missing_src in sorted(inferred_sources() - set(by_source.keys())):
        errors.append(f"by_source: missing infer_source() source {missing_src!r}")

    if FACETS.exists():
        facets = json.loads(FACETS.read_text(encoding="utf-8"))
        counts = facets.get("counts") or facets
        for src_name, count in (counts.get("src") or counts.get("source") or {}).items():
            if count and src_name not in by_source:
                errors.append(f"by_source: missing facet source {src_name!r} ({count} records)")
        for cat_name, count in (counts.get("cat") or counts.get("category") or {}).items():
            if count and cat_name not in by_category:
                errors.append(f"by_category: missing facet category {cat_name!r} ({count} records)")

    if errors:
        print("methods.yaml validation FAILED:", file=sys.stderr)
        for e in errors[:30]:
            print("  -", e, file=sys.stderr)
        return 1

    payload = json.dumps(
        {"by_source": by_source, "by_category": by_category, "meta": doc.get("meta", {})},
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != payload:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(payload, encoding="utf-8")
    out_label = OUT.relative_to(REPO_ROOT) if OUT.is_relative_to(REPO_ROOT) else OUT
    print(f"OK — {n_methods} methods "
          f"({len(by_source)} sources, {len(by_category)} categories) → "
          f"{out_label} ({OUT.stat().st_size // 1024} KB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
