"""Tests that every protein trait source and category resolves to a runnable detection recipe."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

BUILD_METHODS_SPEC = importlib.util.spec_from_file_location(
    "build_methods", ROOT / "scripts" / "build_methods.py"
)
BUILD_METHODS = importlib.util.module_from_spec(BUILD_METHODS_SPEC)
BUILD_METHODS_SPEC.loader.exec_module(BUILD_METHODS)

BUILD_DOCS_SPEC = importlib.util.spec_from_file_location(
    "build_docs_index", ROOT / "scripts" / "build_docs_index.py"
)
BUILD_DOCS = importlib.util.module_from_spec(BUILD_DOCS_SPEC)
BUILD_DOCS_SPEC.loader.exec_module(BUILD_DOCS)


def test_build_methods_validates_and_matches_committed_json():
    yaml_doc = yaml.safe_load((ROOT / "data" / "methods" / "methods.yaml").read_text(encoding="utf-8"))
    json_doc = json.loads((ROOT / "docs" / "data" / "methods.json").read_text(encoding="utf-8"))
    assert json_doc["by_source"] == yaml_doc["by_source"]
    assert json_doc["by_category"] == yaml_doc["by_category"]
    assert BUILD_METHODS.main() == 0


def test_every_method_has_runnable_non_comment_recipe():
    doc = yaml.safe_load((ROOT / "data" / "methods" / "methods.yaml").read_text(encoding="utf-8"))
    for scope in ("by_source", "by_category"):
        table = doc.get(scope) or {}
        assert table, f"{scope} must not be empty"
        for key, methods in table.items():
            assert methods, f"{scope}/{key} must define at least one method"
            for m in methods:
                for req in BUILD_METHODS.REQUIRED:
                    assert m.get(req), f"{scope}/{key}/{m.get('name', '?')} missing {req}"
                recipe = str(m["recipe"]).strip()
                assert recipe and not recipe.startswith("#"), (
                    f"{scope}/{key}/{m['name']} has comment-only recipe: {recipe!r}"
                )
                for tok in BUILD_METHODS.PLACEHOLDER_RE.findall(recipe):
                    assert BUILD_METHODS.is_valid_placeholder(tok), (
                        f"{scope}/{key}/{m['name']} has unsupported placeholder {{{tok}}}"
                    )


def test_all_concrete_schema_categories_and_facets_have_runnable_recipes():
    doc = yaml.safe_load((ROOT / "data" / "methods" / "methods.yaml").read_text(encoding="utf-8"))
    by_source = doc["by_source"]
    by_category = doc["by_category"]

    schema = yaml.safe_load(
        (ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml").read_text(encoding="utf-8")
    )
    pvs = schema["enums"]["ProteinTraitCategoryEnum"]["permissible_values"]
    concrete_cats = set(pvs.keys()) - BUILD_METHODS.ABSTRACT_CATEGORIES
    assert concrete_cats <= set(by_category.keys())

    inferred = BUILD_METHODS.inferred_sources()
    assert len(inferred) >= 35
    assert inferred <= set(by_source.keys())

    facets_path = ROOT / "docs" / "data" / "facets.json"
    if facets_path.exists():
        facets = json.loads(facets_path.read_text(encoding="utf-8"))
        counts = facets.get("counts") or facets
        for src, count in (counts.get("src") or counts.get("source") or {}).items():
            if count:
                assert src in by_source, f"Facet source {src!r} missing from by_source"
        for cat, count in (counts.get("cat") or counts.get("category") or {}).items():
            if count:
                assert cat in by_category, f"Facet category {cat!r} missing from by_category"
        for row in facets.get("cube") or []:
            _axis, cat, src, _sta, _count = row
            resolved = (by_source.get(src) or []) + (by_category.get(cat) or [])
            assert resolved, f"Cube entry ({src!r}, {cat!r}) resolved to 0 detection methods"
            assert all(
                str(m.get("recipe") or "").strip()
                and not str(m.get("recipe") or "").strip().startswith("#")
                for m in resolved
            ), f"Cube entry ({src!r}, {cat!r}) has non-runnable recipe"


def test_load_record_preserves_record_level_detection_methods(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD_DOCS, "REPO_ROOT", tmp_path)
    raw = {
        "identifier": "ELM:ELME000001",
        "label": "Test motif",
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_MOTIF",
        "detection_methods": [
            {
                "name": "Custom Motif Scan",
                "method_type": "SEQUENCE_PATTERN",
                "edam_operation": "EDAM:operation_0239",
                "tool": "biotools:slimsearch",
                "recipe": "grep -oP '{pat}' {input.fasta}",
            }
        ],
    }
    path = tmp_path / "ELME000001.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    rec = BUILD_DOCS.load_record(path)
    assert len(rec["dm"]) == 1
    lean, detail = BUILD_DOCS.split_detail([rec])[0]
    assert "dm" not in lean
    assert detail["dm"] == raw["detection_methods"]
