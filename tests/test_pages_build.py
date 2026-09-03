from __future__ import annotations

import importlib.util
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

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
    pairs = [({"id": "Test:large"}, {"def": "x" * BUILD.DETAIL_BUCKET_TARGET_BYTES})]

    with pytest.raises(ValueError, match="Test:large"):
        BUILD.write_detail(pairs)

    assert existing.read_text(encoding="utf-8") == '{"known":"good"}'


def test_detail_bucket_files_stay_below_the_builder_target(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    pairs = [({"id": f"Test:{index}"}, {"def": "x" * (200 + index)}) for index in range(300)]
    count, files, _total_mb, largest = BUILD.write_detail(pairs)
    assert count == 300
    assert files > 0
    assert largest <= BUILD.DETAIL_BUCKET_TARGET_BYTES
    assert all("df" in record for record, _detail in pairs)


def test_record_shards_are_partitioned_and_publish_filter_coverage(tmp_path, monkeypatch):
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    records = [
        {"id": "RHEA:1", "axis": "FUNCTION", "cat": "FUNC_PATHWAY", "src": "Rhea", "sta": "SEEDED"},
        {
            "id": "EC:1",
            "axis": "FUNCTION",
            "cat": "FUNC_PATHWAY",
            "src": "ExPASy",
            "sta": "REVIEWED",
        },
        {
            "id": "ARO:1",
            "axis": "FUNCTION",
            "cat": "FUNC_RESISTANCE",
            "src": "CARD/ARO",
            "sta": "SEEDED",
        },
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
        "site_file_count": 10,
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


def _site_with(tmp_path, extra: dict[str, str] | None = None) -> pathlib.Path:
    """A minimal built site: one generated shard, one generated detail bucket, and
    index.html standing in for everything Jekyll renders or the repo commits."""
    site = tmp_path / "site"
    (site / "data" / "detail").mkdir(parents=True)
    (site / "index.html").write_text("home", encoding="utf-8")
    (site / "data" / "records.FUNCTION.FUNC_PATHWAY.json").write_text("[]", encoding="utf-8")
    (site / "data" / "detail" / "000.json").write_text("{}", encoding="utf-8")
    for name, body in (extra or {}).items():
        path = site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return site


def test_site_file_count_counts_files_no_build_step_generated(tmp_path):
    """The count is of what the site serves, not of builder output. #632: naming it
    `generated_file_count` while measuring the whole site understated the consumed
    budget by ~110 MB in #529's report. Committed sidecars from other steps
    (corpus_map, neighbors, chebi) and Jekyll's HTML are hosted, so they count."""
    bare = AUDIT.measure(_site_with(tmp_path / "bare"))
    with_sidecars = AUDIT.measure(
        _site_with(tmp_path / "full", {"data/corpus_map.json": "{}" * 40,
                                       "data/neighbors/0.json": "[]"})
    )
    assert bare["site_file_count"] == 3          # index.html + shard + detail bucket
    assert with_sidecars["site_file_count"] == 5
    # ... and those bytes are charged too, though neither file is a shard or bucket.
    assert with_sidecars["site_total_bytes"] > bare["site_total_bytes"]
    assert with_sidecars["browse_index_total_bytes"] == bare["browse_index_total_bytes"]
    assert with_sidecars["detail_total_bytes"] == bare["detail_total_bytes"]


def test_a_budgets_file_using_the_old_metric_name_fails_loudly(tmp_path):
    """The rename must not silently stop enforcing a limit: an unknown key is a
    failure, so a stale conf/pages_budgets.json breaks the build instead of passing."""
    site = _site_with(tmp_path)
    _metrics, failures = AUDIT.audit(site, {"generated_file_count": 10})
    assert failures == ["unknown budget metric: generated_file_count"]


def test_warn_band_fires_below_the_limit_and_never_above_it():
    metrics = {"site_total_bytes": 800, "site_file_count": 1000}
    budgets = {"site_total_bytes": 1000, "site_file_count": 1000}
    # Exactly at the fraction warns; a byte under does not.
    assert AUDIT.near_budget(metrics, budgets, 0.8) == {"site_total_bytes", "site_file_count"}
    assert AUDIT.near_budget({**metrics, "site_total_bytes": 799}, budgets, 0.8) == {
        "site_file_count"
    }
    # Over the limit is a failure, not a warning — the two sets must not overlap.
    over = AUDIT.near_budget({**metrics, "site_file_count": 1001}, budgets, 0.8)
    assert "site_file_count" not in over
    # A zero budget with zero usage is not "within 80% of budget".
    assert AUDIT.near_budget({"x": 0}, {"x": 0}, 0.8) == set()
    # An unmeasured budget key cannot warn.
    assert AUDIT.near_budget({}, {"x": 100}, 0.8) == set()


def test_cli_warns_without_failing_and_rejects_a_nonsense_fraction(tmp_path):
    site = _site_with(tmp_path)
    budgets = tmp_path / "budgets.json"
    measured = AUDIT.measure(site)
    budgets.write_text(json.dumps({"site_total_bytes": measured["site_total_bytes"],
                                   "site_file_count": 100}), encoding="utf-8")
    cmd = [sys.executable, str(REPO / "scripts" / "audit_pages_size.py"),
           "--site", str(site), "--budgets", str(budgets)]
    done = subprocess.run(cmd, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert "WARN  site_total_bytes" in done.stdout          # at 100% of its budget
    assert "OK    site_file_count" in done.stdout           # 3 of 100
    assert "WARN: within 80% of budget: site_total_bytes" in done.stdout
    assert "OK: Pages artifact is within all budgets." not in done.stdout

    rejected = subprocess.run(cmd + ["--warn-fraction", "1.5"], capture_output=True, text=True)
    assert rejected.returncode != 0 and "--warn-fraction" in rejected.stderr
    zero = subprocess.run(cmd + ["--warn-fraction", "0"], capture_output=True, text=True)
    assert zero.returncode != 0 and "--warn-fraction" in zero.stderr


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


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_shard_selection_never_under_fetches_across_shards():
    """The property the lazy browser rests on, which nothing held (#544).

    `selectShardFiles` is an over-approximation by construction -- `write_shards`
    stamps each shard with every source and status present in that chunk, so a
    record matching a filter always lives in a shard overlapping each selected
    group. Over-fetching is safe; under-fetching silently drops results.

    Nothing tested it. Mutating `selectedValues.some(...)` to `.every(...)` --
    which breaks OR-within-a-group and produces exactly that silent under-fetch
    -- left all six tests passing, because the existing manifest is hand-written
    with single-value Sets only and never crosses the Python and JS sides.

    The manifest here is built the way write_shards builds it: grouped by
    (axis, category), chunked, then stamped with the sorted union of the sources
    and statuses actually present in each chunk. Random multi-value selections
    are then compared against a full scan of the same records.
    """
    module = json.dumps(str(REPO / "docs" / "shard-selection.js"))
    program = f"""
const assert = require('assert');
const shards = require({module});

// Deterministic PRNG: a failure must be reproducible from the seed alone.
let seed = 20260902;
const rand = (n) => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) % n;

const AXES = ['SEQUENCE', 'FUNCTION', 'STRUCTURE'];
const CATS = ['SEQ_DOMAIN', 'FUNC_PATHWAY', 'FUNC_RESISTANCE', 'STRUCT_FOLD'];
const SRCS = ['Pfam', 'Rhea', 'CARD/ARO', 'CATH'];
const STAS = ['SEEDED', 'REVIEWED', 'PROPOSED'];

const records = [];
for (let i = 0; i < 600; i++) {{
  const axis = AXES[rand(AXES.length)];
  records.push({{
    id: 'R:' + String(i).padStart(4, '0'),
    axis,
    cat: CATS[rand(CATS.length)],
    src: SRCS[rand(SRCS.length)],
    sta: STAS[rand(STAS.length)],
  }});
}}

// Mirror write_shards: group by (axis, category), chunk, stamp the union.
const CHUNK = 40;
const groups = new Map();
for (const rec of records) {{
  const key = rec.axis + '\\u0000' + rec.cat;
  if (!groups.has(key)) groups.set(key, []);
  groups.get(key).push(rec);
}}
const manifest = [];
const byFile = new Map();
for (const [key, recs] of groups) {{
  const [axis, cat] = key.split('\\u0000');
  recs.sort((a, b) => a.id.localeCompare(b.id));
  for (let i = 0; i < recs.length; i += CHUNK) {{
    const chunk = recs.slice(i, i + CHUNK);
    const file = `records.${{axis}}.${{cat}}.${{String(i / CHUNK).padStart(2, '0')}}.json`;
    manifest.push({{
      file,
      axis,
      categories: [cat],
      sources: [...new Set(chunk.map(r => r.src))].sort(),
      statuses: [...new Set(chunk.map(r => r.sta))].sort(),
    }});
    byFile.set(file, chunk);
  }}
}}

const pick = (pool) => {{
  const chosen = new Set();
  const count = rand(pool.length) + 1;   // at least one, often several
  for (let i = 0; i < count; i++) chosen.add(pool[rand(pool.length)]);
  return chosen;
}};

let checked = 0;
for (let trial = 0; trial < 400; trial++) {{
  const selected = {{
    axis: rand(3) === 0 ? new Set() : pick(AXES),
    cat: rand(3) === 0 ? new Set() : pick(CATS),
    src: rand(3) === 0 ? new Set() : pick(SRCS),
    sta: rand(3) === 0 ? new Set() : pick(STAS),
  }};
  const hasFacet = ['axis', 'cat', 'src', 'sta'].some(k => selected[k].size > 0);
  if (!hasFacet) continue;
  checked++;

  const expected = records.filter(r =>
    (selected.axis.size === 0 || selected.axis.has(r.axis)) &&
    (selected.cat.size === 0 || selected.cat.has(r.cat)) &&
    (selected.src.size === 0 || selected.src.has(r.src)) &&
    (selected.sta.size === 0 || selected.sta.has(r.sta))
  ).map(r => r.id);

  const fetched = new Set();
  for (const file of shards.selectShardFiles(manifest, selected, '')) {{
    for (const rec of byFile.get(file)) fetched.add(rec.id);
  }}

  const missing = expected.filter(id => !fetched.has(id));
  assert.strictEqual(
    missing.length, 0,
    `under-fetch on trial ${{trial}}: ${{missing.length}} of ${{expected.length}} ` +
    `records unreachable, e.g. ${{missing.slice(0, 3).join(', ')}}`
  );
}}
assert.ok(checked > 300, `only ${{checked}} trials exercised a facet`);

// A manifest from a previous build carries no per-shard sources/statuses. The
// only safe reading is "might match" -- excluding it would drop every record in
// that shard until the next Pages build. Flipping this fallback to false is the
// third mutation #544 names, and the random trials above cannot reach it
// because they always stamp arrays.
const legacy = [{{file:'old.json', axis:'FUNCTION', categories:['FUNC_PATHWAY']}}];
const bySource = {{axis:new Set(), cat:new Set(), src:new Set(['Rhea']), sta:new Set()}};
assert.deepStrictEqual(
  shards.selectShardFiles(legacy, bySource, ''), ['old.json'],
  'a legacy shard was excluded, so its records became unreachable'
);
const byStatus = {{axis:new Set(), cat:new Set(), src:new Set(), sta:new Set(['SEEDED'])}};
assert.deepStrictEqual(shards.selectShardFiles(legacy, byStatus, ''), ['old.json']);
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_bucket_growth_actually_runs_and_keeps_every_bucket_under_target(tmp_path, monkeypatch):
    """The headline feature of #529, which its own tests never executed (#544).

    `test_detail_bucket_files_stay_below_the_builder_target` uses 300 records of
    ~250 bytes against a 900,000-byte target, so `bucket_count` is pinned at
    MIN_DETAIL_BUCKETS and the sizing loop never runs. Three mutations survived
    on that fixture, including `while entries:` to `while False:` -- deleting the
    growth loop entirely.

    A smaller target is what forces growth, rather than a fixture large enough to
    make the suite slow: the loop's behaviour depends on the ratio, not on the
    absolute size.
    """
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    monkeypatch.setattr(BUILD, "MIN_DETAIL_BUCKETS", 4)
    pairs = [({"id": f"Test:{index}"}, {"def": "x" * (400 + index)}) for index in range(400)]

    # Passed, not monkeypatched: `target_bytes` is a DEFAULT ARGUMENT bound at
    # import time, so setattr on the module constant has no effect on it. My
    # first version of this test set the attribute, saw bucket_count stay at the
    # floor, and would have read as "the loop still does not run".
    starting_count = max(4, (sum(len(str(d)) for _r, d in pairs) * 4) // (3 * 8_000))
    bucket_count = BUILD.detail_bucket_count(pairs, target_bytes=8_000)

    assert bucket_count > starting_count, "the growth loop never ran; the ratio cannot force it"
    sizes = [2] * bucket_count
    for record, detail in pairs:
        encoded = (
            json.dumps(record["id"], ensure_ascii=False)
            + ":"
            + json.dumps(detail, separators=(",", ":"), ensure_ascii=False)
        ).encode("utf-8")
        digest = int(hashlib.md5(record["id"].encode("utf-8")).hexdigest(), 16)
        sizes[digest % bucket_count] += len(encoded) + 1
    assert max(sizes) <= 8_000, f"the chosen count still overflows at {max(sizes)} bytes"


def test_size_accounting_charges_the_separator_between_entries(monkeypatch):
    """Dropping the comma byte survived the suite (#544).

    The accounting is exact, not conservative: a bucket of k entries writes
    `{e1,e2,...}` = 2 + sum(len) + (k - 1), and the builder adds exactly that.
    So under-counting the separator does not merely mis-report -- it can stop the
    growth loop one iteration early and write a bucket over the target, which is
    a Pages budget breach.

    The fixture is not arbitrary. Both accountings were simulated across record
    counts, sizes and targets to find one where they disagree in a way that
    matters: at this size the correct accounting picks 17 buckets and the
    separator-free one picks 13, whose largest bucket writes 335 bytes against a
    330-byte target. A fixture chosen by eye would very likely not discriminate,
    which is why the first version of this test passed against the mutation.
    """
    # Without lowering the floor every bucket holds at most one entry, so no
    # separator is ever charged and both accountings agree. MIN_DETAIL_BUCKETS is
    # read in the function body, unlike target_bytes, so setattr does reach it.
    monkeypatch.setattr(BUILD, "MIN_DETAIL_BUCKETS", 1)
    pairs = [({"id": f"T:{index}"}, {"d": "y" * 40}) for index in range(40)]
    target = 330

    bucket_count = BUILD.detail_bucket_count(pairs, target_bytes=target)

    grouped: dict[int, list[str]] = {}
    for record, detail in pairs:
        encoded = (
            json.dumps(record["id"], ensure_ascii=False)
            + ":"
            + json.dumps(detail, separators=(",", ":"), ensure_ascii=False)
        )
        digest = int(hashlib.md5(record["id"].encode("utf-8")).hexdigest(), 16)
        grouped.setdefault(digest % bucket_count, []).append(encoded)

    largest = max(
        len(("{" + ",".join(entries) + "}").encode("utf-8")) for entries in grouped.values()
    )
    assert largest <= target, (
        f"the chosen {bucket_count} buckets write {largest} bytes against a {target}-byte "
        f"target; the size accounting under-counts the separators"
    )
