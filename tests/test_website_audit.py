"""October website audit: public data must retain identity and honest load states."""
from __future__ import annotations

import hashlib
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("audit_docs_build", ROOT / "scripts/build_docs_index.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def test_projection_preserves_synonyms_graph_history_and_placeholder_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "REPO_ROOT", tmp_path)
    raw = {"identifier": "test:1", "label": "-", "synonyms": [
        {"synonym_text": f"alias{i}"} for i in range(9)],
        "causal_graphs": [{"edges": [{"subject": "a", "object": "b", "evidence": ["PMID:1"]}]}],
        "curation_history": [{"date": "2026-01-01", "action": "CREATED"}]}
    path = tmp_path / "record.yaml"
    path.write_text(yaml.safe_dump(raw))
    original = path.read_bytes()
    record = BUILD.load_record(path)
    assert record["label"] == "test:1"
    assert len(record["syn"]) == 9
    assert record["cg"] == raw["causal_graphs"]
    assert record["history"] == raw["curation_history"]
    lean, detail = BUILD.split_detail([record])[0]
    assert len(lean["syn"]) == 9
    assert "cg" not in lean and detail["cg"] == raw["causal_graphs"]
    assert path.read_bytes() == original


def test_lookup_is_complete_bounded_and_cleans_stale_files(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    records = [{"id": f"test:{i}", "axis": "SEQUENCE", "cat": "SEQ_FAMILY"} for i in range(8100)]
    shards = BUILD.write_shards(records)
    count = BUILD.lookup_count(len(records))
    assert count == 4
    lookups = {i: json.loads((tmp_path / "lookup" / f"{i:04d}.json").read_text()) for i in range(count)}
    for record in records:
        bucket = int(hashlib.sha256(record["id"].encode()).hexdigest()[:4], 16) % count
        entries = lookups[bucket]
        assert entries[record["id"]] == shards[0]["file"]
    BUILD.write_lookup({"test:1": "one.json"})
    assert len(list((tmp_path / "lookup").glob("*.json"))) == 1


def test_map_coverage_compares_identities_without_changing_points(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    path = tmp_path / "corpus_map.json"
    path.write_text(json.dumps({"points": [[0, 0, 0, "a"], [1, 1, 0, "old"]]}))
    original = path.read_bytes()
    BUILD.write_map_coverage([{"id": "a"}, {"id": "b"}])
    result = json.loads((tmp_path / "map-coverage.json").read_text())[path.name]
    assert result["current_plotted"] == 1 and result["not_plotted"] == 1
    assert result["outside_current"] == 1 and result["browser_total"] == 2
    assert result["embedding_date"] is None
    assert path.read_bytes() == original


def test_license_policy_is_present_on_every_page_shell():
    policy = (ROOT / "LICENSE").read_text()
    assert "CC-BY-4.0" in policy and "BSD-3-Clause" in policy and "Third-party" in policy
    for name in ["_layouts/default.html", "index.html", "browse.html", "map.html"]:
        page = (ROOT / "docs" / name).read_text()
        assert "LICENSE-DATA" in page and "CC BY 4.0" in page
        assert "LICENSE-CODE" in page and "BSD-3-Clause" in page
        assert "Third-party terms and attribution apply" in page
        assert "CC0-1.0" not in page.split("<footer", 1)[1]


def test_browser_error_recovery_identity_and_navigation():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js required for browser unit harness")
    subprocess.run([node, str(ROOT / "tests/website_audit_harness.cjs")], check=True, cwd=ROOT)


def test_landing_distinguishes_historical_curated_terms_from_current_policy():
    sources = json.loads((ROOT / "conf/landing_sources.json").read_text())
    curated = next(source for source in sources if source["source"] == "curated")
    for row in curated["integrations"]:
        assert "historical records retain CC0" in row["description"]
        assert "current project contributions: CC BY 4.0" in row["description"]
    reactome = next(source for source in sources if source["source"] == "Reactome")
    assert any("CC0" in row["description"] for row in reactome["integrations"])


def test_graph_sidecars_are_lossless_bounded_deterministic_and_only_for_populated_records(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    graph = [{"nodes": [{"id": "a", "label": "α <x>"}],
              "edges": [{"subject": "a", "object": "b", "evidence": ["PMID:1"]}]}]
    records = [{"id": "test:1", "cg": graph}, {"id": "test:2", "cg": []}]
    BUILD.write_graphs(records)
    assert "gf" not in records[1] and "cg" not in records[0]
    path = tmp_path / records[0]["gf"]
    original = path.read_bytes()
    assert json.loads(gzip.decompress(original)) == {"test:1": graph}
    assert len(original) < 900_000
    BUILD.write_graphs([{"id": "test:1", "cg": graph}])
    assert path.read_bytes() == original
    BUILD.write_graphs([])
    assert not list((tmp_path / "graphs").iterdir())
