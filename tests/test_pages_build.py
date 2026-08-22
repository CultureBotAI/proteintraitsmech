from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = _load("build_docs_index", REPO / "scripts" / "build_docs_index.py")
AUDIT = _load("audit_pages_size", REPO / "scripts" / "audit_pages_size.py")


def test_detail_bucket_planner_rejects_an_impossible_single_record():
    pairs = [({"id": "Test:large"}, {"def": "x" * 200})]
    with pytest.raises(ValueError, match="Test:large"):
        BUILD.detail_bucket_count(pairs, target_bytes=100)


def test_detail_validation_failure_preserves_existing_buckets(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    existing = tmp_path / "detail" / "000.json"
    existing.parent.mkdir()
    existing.write_text('{"known":"good"}', encoding="utf-8")
    pairs = [
        ({"id": "Test:large"}, {"def": "x" * BUILD.DETAIL_BUCKET_TARGET_BYTES})
    ]

    with pytest.raises(ValueError, match="Test:large"):
        BUILD.write_detail(pairs)

    assert existing.read_text(encoding="utf-8") == '{"known":"good"}'


def test_detail_bucket_files_stay_below_the_builder_target(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    pairs = [
        ({"id": f"Test:{index}"}, {"def": "x" * (200 + index)})
        for index in range(300)
    ]
    count, files, _total_mb, largest = BUILD.write_detail(pairs)
    assert count == 300
    assert files > 0
    assert largest <= BUILD.DETAIL_BUCKET_TARGET_BYTES
    assert all("df" in record for record, _detail in pairs)


def test_record_shards_are_partitioned_and_publish_filter_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    records = [
        {"id": "RHEA:1", "axis": "FUNCTION", "cat": "FUNC_PATHWAY", "src": "Rhea", "sta": "SEEDED"},
        {"id": "EC:1", "axis": "FUNCTION", "cat": "FUNC_PATHWAY", "src": "ExPASy", "sta": "REVIEWED"},
        {"id": "ARO:1", "axis": "FUNCTION", "cat": "FUNC_RESISTANCE", "src": "CARD/ARO", "sta": "SEEDED"},
        {"id": "Pfam:1", "axis": "SEQUENCE", "cat": "SEQ_DOMAIN", "src": "Pfam", "sta": "SEEDED"},
    ]
    manifest = BUILD.write_shards(records)
    assert len(manifest) == 3
    pathway = next(item for item in manifest if item["categories"] == ["FUNC_PATHWAY"])
    assert pathway["axis"] == "FUNCTION"
    assert pathway["sources"] == ["ExPASy", "Rhea"]
    assert pathway["statuses"] == ["REVIEWED", "SEEDED"]
    assert json.loads((tmp_path / pathway["file"]).read_text())


def test_pages_audit_reports_each_budget_and_fails_closed(tmp_path):
    site = tmp_path / "site"
    (site / "data" / "detail").mkdir(parents=True)
    (site / "index.html").write_text("home", encoding="utf-8")
    (site / "data" / "records.FUNCTION.FUNC_PATHWAY.json").write_text("[]", encoding="utf-8")
    (site / "data" / "detail" / "000.json").write_text("{}", encoding="utf-8")
    generous = {
        "site_total_bytes": 100,
        "generated_file_count": 10,
        "browse_index_total_bytes": 10,
        "largest_browse_shard_bytes": 10,
        "detail_total_bytes": 10,
        "largest_detail_bucket_bytes": 10,
    }
    metrics, failures = AUDIT.audit(site, generous)
    assert failures == []
    assert metrics["browse_shards"] == 1 and metrics["detail_buckets"] == 1

    strict = dict(generous, largest_detail_bucket_bytes=1)
    _metrics, failures = AUDIT.audit(site, strict)
    assert failures == ["largest_detail_bucket_bytes: 2 > 1"]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_browser_shard_selection_covers_filters_search_links_and_empty_results():
    module = json.dumps(str(REPO / "docs" / "shard-selection.js"))
    program = f"""
const assert = require('assert');
const shards = require({module});
const manifest = [
  {{file:'pathway.json', axis:'FUNCTION', categories:['FUNC_PATHWAY'], sources:['Rhea'], statuses:['SEEDED']}},
  {{file:'resistance.json', axis:'FUNCTION', categories:['FUNC_RESISTANCE'], sources:['CARD/ARO'], statuses:['REVIEWED']}},
  {{file:'domain.json', axis:'SEQUENCE', categories:['SEQ_DOMAIN'], sources:['Pfam'], statuses:['SEEDED']}}
];
const empty = {{axis:new Set(), cat:new Set(), src:new Set(), sta:new Set()}};
assert.deepStrictEqual(shards.selectShardFiles(manifest, empty, ''), []); // landing
assert.deepStrictEqual(shards.selectShardFiles(manifest, {{...empty, cat:new Set(['FUNC_PATHWAY'])}}, ''), ['pathway.json']);
assert.deepStrictEqual(shards.selectShardFiles(manifest, {{...empty, src:new Set(['Rhea'])}}, ''), ['pathway.json']);
assert.deepStrictEqual(shards.selectShardFiles(manifest, {{...empty, axis:new Set(['FUNCTION'])}}, ''), ['pathway.json','resistance.json']);
assert.deepStrictEqual(shards.selectShardFiles(manifest, {{...empty, sta:new Set(['REVIEWED'])}}, ''), ['resistance.json']);
assert.deepStrictEqual(shards.selectShardFiles(manifest, {{...empty, cat:new Set(['FUNC_RESISTANCE']), src:new Set(['Rhea'])}}, ''), []); // combined empty
assert.deepStrictEqual(shards.selectShardFiles(manifest, empty, 'kinase'), ['pathway.json','resistance.json','domain.json']); // free text
assert.deepStrictEqual(shards.allShardFiles(manifest), ['pathway.json','resistance.json','domain.json']); // cold record link

(async () => {{
  let calls = 0;
  const accepted = [];
  const loader = shards.createLoader(
    async () => (++calls === 1
      ? {{ok:false, status:503, json:async () => []}}
      : {{ok:true, status:200, json:async () => [{{id:'RHEA:1'}}]}}),
    records => accepted.push(...records)
  );
  await assert.rejects(loader.load('pathway.json'), /HTTP 503/);
  assert.strictEqual(loader.loaded.has('pathway.json'), false);
  assert.strictEqual(loader.pending.size, 0);
  await loader.load('pathway.json');
  assert.strictEqual(calls, 2);
  assert.strictEqual(loader.loaded.has('pathway.json'), true);
  assert.deepStrictEqual(accepted, [{{id:'RHEA:1'}}]);
}})().catch(error => {{ console.error(error); process.exitCode = 1; }});
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


def test_browser_loads_selection_helper_before_main_script():
    html = (REPO / "docs" / "browse.html").read_text(encoding="utf-8")
    assert html.index('src="shard-selection.js"') < html.index('src="browse.js"')
