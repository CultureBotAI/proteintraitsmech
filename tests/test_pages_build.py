from __future__ import annotations

import importlib.util
import hashlib
import json
import pathlib
import re
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


def test_the_shipped_budgets_file_names_metrics_the_audit_measures(tmp_path):
    """#634: the suite only ever fed audit() inline dicts, so conf/pages_budgets.json —
    the file CI actually uses — was unvalidated. Reverting just that file to a stale
    metric name left every test green while the deploy gate failed."""
    budgets = json.loads((REPO / "conf" / "pages_budgets.json").read_text(encoding="utf-8"))
    assert budgets and all(
        isinstance(key, str) and isinstance(value, int) and value >= 0
        for key, value in budgets.items()
    ), "main() would reject this file as malformed"
    measurable = set(AUDIT.measure(_site_with(tmp_path)))
    assert set(budgets) <= measurable, (
        f"budgeted but unmeasurable: {sorted(set(budgets) - measurable)}"
    )


def test_an_unmeasured_budget_metric_never_reads_as_ok(tmp_path):
    """#635: the report loop defaulted a missing metric to 0, printing OK for the one
    key that is broken. The run failed, but the line a person scans said otherwise."""
    site = _site_with(tmp_path)
    budgets = tmp_path / "budgets.json"
    budgets.write_text(json.dumps({"generated_file_count": 2000}), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_pages_size.py"),
         "--site", str(site), "--budgets", str(budgets)],
        capture_output=True, text=True,
    )
    assert done.returncode == 1
    assert "FAIL  generated_file_count" in done.stdout
    assert "OK    generated_file_count" not in done.stdout
    assert "unknown budget metric: generated_file_count" in done.stdout


def test_warnings_survive_a_failing_budget(tmp_path):
    """#636: the warn summary is what the band exists to surface, and it used to vanish
    exactly when the artifact was in the worst shape."""
    site = _site_with(tmp_path)
    measured = AUDIT.measure(site)
    budgets = tmp_path / "budgets.json"
    budgets.write_text(json.dumps({"site_total_bytes": measured["site_total_bytes"],
                                   "largest_detail_bucket_bytes": 1}), encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "audit_pages_size.py"),
         "--site", str(site), "--budgets", str(budgets)],
        capture_output=True, text=True,
    )
    assert done.returncode == 1
    assert "WARN: within 80% of budget: site_total_bytes" in done.stdout
    assert "FAIL: largest_detail_bucket_bytes" in done.stdout


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
// mulberry32, not an LCG -- `seed * 1103515245` loses low-order precision past
// 2^53, leaving the low bits stuck, and `% n` reads exactly those bits. That made
// rand(4) a constant and confined selections to two of four values (#639).
let seed = 20260902;
const rand = (n) => {{
  seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return (((t ^ (t >>> 14)) >>> 0) / 4294967296 * n) | 0;
}};

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


def _rec(axis, cat, src, sta, i=0):
    return {"id": f"T:{axis}:{cat}:{src}:{sta}:{i}", "axis": axis, "cat": cat,
            "src": src, "sta": sta}


def test_cube_rows_reproduce_every_marginal_tally(tmp_path):
    """The cube must agree with the marginal counts shipped beside it (#638).

    facets.json carries both `counts` (per-group totals) and `cube` (the joint
    distribution). If they disagree the sidebar's numbers change meaning the
    moment the browser falls back to global mode, which is precisely the kind of
    drift no one notices.
    """
    records = [_rec("SEQUENCE", "SEQ_DOMAIN", "Pfam", "SEEDED", i) for i in range(7)]
    records += [_rec("FUNCTION", "FUNC_PATHWAY", "Rhea", "REVIEWED", i) for i in range(3)]
    records += [_rec("FUNCTION", "FUNC_PATHWAY", "Pfam", "SEEDED", i) for i in range(2)]

    cube = BUILD._cube(records)
    assert cube is not None
    for position, key in enumerate(["axis", "cat", "src", "sta"]):
        marginal = {}
        for row in cube:
            marginal[row[position]] = marginal.get(row[position], 0) + row[4]
        assert marginal == BUILD._tally(records, key), f"cube disagrees with counts.{key}"
    assert sum(row[4] for row in cube) == len(records)


def test_a_record_missing_one_facet_still_counts_toward_the_others():
    """Dropping it would hide a value that is genuinely reachable (#641).

    filterRecords() only tests groups that carry a selection, so a record with a
    source but no category is reachable by selecting that source. Dropping it
    under-counts the source -- to zero if it is the only one -- and a zero count
    hides the value entirely. A dead end wastes a click; a hidden value cannot be
    clicked at all.
    """
    records = [_rec("SEQUENCE", "SEQ_DOMAIN", "Pfam", "SEEDED")]
    records.append({"id": "T:nocat", "axis": "SEQUENCE", "src": "Rhea", "sta": "SEEDED"})
    records.append({"id": "T:blank", "axis": "SEQUENCE", "cat": "", "src": "Rhea",
                    "sta": "SEEDED"})

    cube = BUILD._cube(records)
    assert sum(row[4] for row in cube) == 3, "an incomplete record was dropped"
    assert [r for r in cube if r[1] is None], "the missing category is not null"

    # Rhea is reachable by selecting it, so it must carry a count.
    for position, key in enumerate(["axis", "cat", "src", "sta"]):
        marginal = {}
        for row in cube:
            if row[position] is None:
                continue
            marginal[row[position]] = marginal.get(row[position], 0) + row[4]
        assert marginal == BUILD._tally(records, key), f"cube marginal != counts.{key}"
    assert BUILD._tally(records, "src")["Rhea"] == 2


def test_a_record_with_no_facets_at_all_is_dropped():
    """No selection can reach it, so counting it would promise an unreachable total."""
    records = [_rec("SEQUENCE", "SEQ_DOMAIN", "Pfam", "SEEDED"), {"id": "T:bare"}]
    cube = BUILD._cube(records)
    assert sum(row[4] for row in cube) == 1
    assert len(cube) == 1


def test_cube_is_abandoned_rather_than_shipped_unbounded(monkeypatch):
    """Past the ceiling the builder emits no cube instead of a huge facets.json.

    Nothing about the corpus bounds the number of distinct facet combinations, so
    the bound is explicit. Returning None (browser falls back to global counts)
    rather than raising keeps a display concern from failing the whole docs build.
    """
    monkeypatch.setattr(BUILD, "MAX_CUBE_ROWS", 4)
    under = [_rec("A", f"C{i}", "S", "SEEDED") for i in range(4)]
    assert BUILD._cube(under) is not None and len(BUILD._cube(under)) == 4

    over = [_rec("A", f"C{i}", "S", "SEEDED") for i in range(5)]
    assert BUILD._cube(over) is None


def test_the_built_facets_file_carries_a_cube(tmp_path, monkeypatch):
    """End to end: main() must actually write the key the browser reads."""
    monkeypatch.setattr(BUILD, "OUT_DIR", tmp_path)
    records = [_rec("SEQUENCE", "SEQ_DOMAIN", "Pfam", "SEEDED", i) for i in range(3)]
    cube = BUILD._cube(records)
    (tmp_path / "facets.json").write_text(json.dumps(
        {"total": len(records), "counts": {"axis": BUILD._tally(records, "axis")},
         "cube": cube, "shards": [], "detailDir": "detail"}))

    written = json.loads((tmp_path / "facets.json").read_text())
    assert written["cube"] == [["SEQUENCE", "SEQ_DOMAIN", "Pfam", "SEEDED", 3]]
    source = (REPO / "scripts" / "build_docs_index.py").read_text()
    assert '"cube": cube,' in source, "main() no longer emits the cube into facets.json"

    # Nulls and strings coexist in a row, so the row ordering must not compare them.
    mixed = records + [{"id": "T:nosrc", "axis": "SEQUENCE", "cat": "SEQ_DOMAIN",
                        "sta": "SEEDED"}]
    assert json.dumps(BUILD._cube(mixed))  # sorts without raising, and serialises


def test_browser_loads_facet_counts_helper_before_main_script():
    html = (REPO / "docs" / "browse.html").read_text()
    assert html.index('src="facet-counts.js"') < html.index('src="browse.js"')


def test_every_browser_script_is_published_by_jekyll():
    """A script missing from `include:` fails totally and silently (#544).

    Jekyll serves the site; a helper it never copies leaves BrowseFacetCounts (or
    BrowseShards) undefined in a browser that reports no build error at all. Every
    script browse.html loads must be listed.

    Every <script> tag is enumerated first and its src read second (#642). Matching
    the whole tag shape instead would let a script drop out of the checked set the
    moment it gained `defer` or `type=module` -- still green, quietly covering less.
    """
    config = (REPO / "docs" / "_config.yml").read_text()
    html = (REPO / "docs" / "browse.html").read_text()

    tags = re.findall(r"<script\b[^>]*>", html)
    assert tags, "no script tags found in browse.html"
    srcs = [m.group(1) for m in (re.search(r'src="([^"]+)"', t) for t in tags) if m]
    local = [s for s in srcs if not s.startswith(("http://", "https://", "//"))]
    # If the tag pattern ever goes blind, this is what notices.
    assert len(local) >= 4, f"only {len(local)} local scripts found: {local}"

    listed = set(re.findall(r"^  - (\S+)$", config, re.M))
    missing = [s for s in local if s not in listed]
    assert not missing, f"not in _config.yml include: {missing}"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_cube_counts_equal_a_full_scan_for_every_selection():
    """Subset-aware facet counts must equal what a full record scan would give (#638).

    This is the acceptance bar for replacing global counts. Random multi-value
    selections across all four groups are counted twice: once by summing the cube,
    once by scanning the records the cube was built from.

    The mutation to beat is dropping the `i === g` guard in countsFor -- letting a
    group constrain its own counts. That is self-referential: the selected value
    keeps its count, every sibling reads 0, and the group can never be widened.
    The scan below models the correct semantics, so it fails on that mutation.
    """
    module = json.dumps(str(REPO / "docs" / "facet-counts.js"))
    program = f"""
const assert = require('assert');
const fc = require({module});

// Deterministic PRNG: a failure must be reproducible from the seed alone.
// mulberry32, not an LCG -- `seed * 1103515245` loses low-order precision past
// 2^53, leaving the low bits stuck, and `% n` reads exactly those bits. That made
// rand(4) a constant and confined selections to two of four values (#639).
let seed = 20260904;
const rand = (n) => {{
  seed = (seed + 0x6D2B79F5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return (((t ^ (t >>> 14)) >>> 0) / 4294967296 * n) | 0;
}};

const KEYS = ['axis', 'cat', 'src', 'sta'];
const AXES = ['SEQUENCE', 'FUNCTION', 'STRUCTURE', 'EVOLUTION'];
const CATS = ['SEQ_DOMAIN', 'SEQ_MOTIF', 'FUNC_PATHWAY', 'FUNC_RESISTANCE',
              'STRUCT_FOLD', 'EVOL_ORTHOLOGY'];
const SRCS = ['Pfam', 'InterPro', 'PROSITE', 'Rhea', 'CARD', 'CATH', 'SCOP', 'OrthoDB'];
const STAS = ['SEEDED', 'REVIEWED', 'PROPOSED'];
const POOLS = [AXES, CATS, SRCS, STAS];

// Model the corpus's real structure rather than drawing all four fields
// independently: categories belong to an axis, sources to a category, and Pfam
// deliberately spans two axes. That is what makes the cube sparse -- 27 of 576
// cells -- and a sparse cube is what distinguishes a correct sum from a
// cross-product. Uniform draws would fill nearly every cell and hide the bug.
const CAT_OF = {{
  SEQUENCE: ['SEQ_DOMAIN', 'SEQ_MOTIF'],
  FUNCTION: ['FUNC_PATHWAY', 'FUNC_RESISTANCE'],
  STRUCTURE: ['STRUCT_FOLD'],
  EVOLUTION: ['EVOL_ORTHOLOGY'],
}};
const SRC_OF = {{
  SEQ_DOMAIN: ['Pfam', 'InterPro'], SEQ_MOTIF: ['PROSITE'],
  FUNC_PATHWAY: ['Rhea', 'Pfam'], FUNC_RESISTANCE: ['CARD'],
  STRUCT_FOLD: ['CATH', 'SCOP'], EVOL_ORTHOLOGY: ['OrthoDB'],
}};
const records = [];
for (let i = 0; i < 900; i++) {{
  const axis = AXES[rand(AXES.length)];
  const cat = CAT_OF[axis][rand(CAT_OF[axis].length)];
  const rec = {{axis, cat, src: SRC_OF[cat][rand(SRC_OF[cat].length)],
               sta: STAS[rand(STAS.length)]}};
  // One record in twelve is missing a field (#641). It stays reachable through
  // the groups it does have, and must vanish only once its empty group is
  // constrained -- the case a hand-written cube would not cover.
  if (rand(12) === 0) rec[KEYS[rand(KEYS.length)]] = null;
  records.push(rec);
}}
let incomplete = 0;
for (const r of records) if (KEYS.some(k => r[k] === null)) incomplete++;
assert.ok(incomplete > 40, `only ${{incomplete}} incomplete records generated`);

const tally = new Map();
for (const r of records) {{
  const key = JSON.stringify(KEYS.map(k => r[k]));
  tally.set(key, (tally.get(key) || 0) + 1);
}}
// Key on JSON so a null stays a null instead of becoming the string "null" --
// exactly the round-trip the builder must not do either.
const cube = [...tally].map(([key, n]) => [...JSON.parse(key), n]);
cube.sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
assert.ok(cube.some(row => row.slice(0, 4).includes(null)), 'no null row in the cube');
const CELLS = AXES.length * CATS.length * SRCS.length * STAS.length;
assert.ok(cube.length > 20 && cube.length < CELLS / 4,
  `cube is degenerate at ${{cube.length}} of ${{CELLS}} cells`);

const pick = (pool) => {{
  const chosen = new Set();
  const count = rand(pool.length) + 1;
  for (let i = 0; i < count; i++) chosen.add(pool[rand(pool.length)]);
  return chosen;
}};

let sawNarrowed = 0;
for (let trial = 0; trial < 300; trial++) {{
  const selected = {{}};
  KEYS.forEach((k, i) => {{ selected[k] = rand(3) === 0 ? new Set() : pick(POOLS[i]); }});

  const got = fc.countsFor(cube, selected);
  assert.ok(got, 'countsFor returned null for a well-formed cube');

  // Independent full scan: for group g, apply every selection EXCEPT g's own.
  KEYS.forEach((g, gi) => {{
    const expected = {{}};
    for (const r of records) {{
      let ok = true;
      KEYS.forEach((k, i) => {{
        if (i === gi) return;
        if (selected[k].size && !selected[k].has(r[k])) ok = false;
      }});
      if (ok && r[g] !== null) expected[r[g]] = (expected[r[g]] || 0) + 1;
    }}
    assert.ok(!('null' in expected) && !(null in got[g]), 'null became a facet value');
    assert.deepStrictEqual(got[g], expected,
      `trial ${{trial}} group ${{g}}: cube counts differ from a full scan\\n` +
      `  selected=${{JSON.stringify(KEYS.map(k => [...selected[k]]))}}\\n` +
      `  cube=${{JSON.stringify(got[g])}}\\n  scan=${{JSON.stringify(expected)}}`);

    // The guard under test: a selected group must still offer its unselected
    // siblings. Self-constrained counts would zero them.
    if (selected[g].size && selected[g].size < POOLS[gi].length) {{
      const others = POOLS[gi].filter(v => !selected[g].has(v));
      if (others.some(v => (expected[v] || 0) > 0)) sawNarrowed++;
    }}
  }});

  // Whole-selection total: here every group does constrain itself.
  const total = fc.matchingTotal(cube, selected);
  const scanned = records.filter(r =>
    KEYS.every(k => !selected[k].size || selected[k].has(r[k]))).length;
  assert.strictEqual(total, scanned, `trial ${{trial}}: matchingTotal ${{total}} != ${{scanned}}`);
}}
assert.ok(sawNarrowed > 50,
  `only ${{sawNarrowed}} trials could distinguish self-constrained counts`);

// A cube that is absent, empty or malformed yields null so the caller can fall
// back to global counts and relabel -- never a half-populated object.
for (const bad of [undefined, null, [], 'cube', [['A', 'B', 'C']],
                   [['A', 'B', 'C', 'D', 'E']], [['A', 'B', 'C', 'D', -1]],
                   [['A', 'B', 'C', 'D', 5, 'extra']], [['A', 'B', 'C', 'D']]]) {{
  assert.strictEqual(fc.countsFor(bad, {{}}), null, `accepted a bad cube: ${{JSON.stringify(bad)}}`);
  assert.strictEqual(fc.matchingTotal(bad, {{}}), null);
}}

// Plain arrays must work as well as Sets: deep-link parsing hands over arrays.
assert.deepStrictEqual(
  fc.countsFor(cube, {{axis: [...new Set(['SEQUENCE'])]}}),
  fc.countsFor(cube, {{axis: new Set(['SEQUENCE'])}}));
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_no_facet_value_on_screen_can_return_an_empty_result():
    """The user-visible promise: nothing clickable is a dead end (#638).

    Under `axis=EVOLUTION` the shipped sidebar offers 54 of 56 categories and 32 of
    33 sources that return "No records match". A value is shown only when its
    subset-aware count is above zero, so this holds for every selection.
    """
    module = json.dumps(str(REPO / "docs" / "facet-counts.js"))
    program = f"""
const assert = require('assert');
const fc = require({module});
const KEYS = ['axis', 'cat', 'src', 'sta'];

const cube = [
  ['EVOLUTION', 'EVOL_ORTHOLOGY', 'OrthoDB', 'SEEDED', 9],
  ['SEQUENCE', 'SEQ_DOMAIN', 'Pfam', 'SEEDED', 75931],
  ['SEQUENCE', 'SEQ_MOTIF', 'PROSITE', 'REVIEWED', 120],
  ['FUNCTION', 'FUNC_PATHWAY', 'Rhea', 'SEEDED', 400],
];
const selected = {{axis: new Set(['EVOLUTION']), cat: new Set(), src: new Set(), sta: new Set()}};
const counts = fc.countsFor(cube, selected);

// Every value the sidebar would still show (count > 0) must really be reachable.
for (const g of KEYS) {{
  for (const [value, n] of Object.entries(counts[g])) {{
    if (n === 0) continue;
    const probe = {{}};
    for (const k of KEYS) probe[k] = new Set(selected[k]);
    probe[g].add(value);
    assert.ok(fc.matchingTotal(cube, probe) > 0,
      `${{g}}=${{value}} shows ${{n}} but selecting it returns nothing`);
  }}
}}
// And the dead ends really are zeroed, not merely reordered.
assert.strictEqual(counts.cat['SEQ_DOMAIN'] || 0, 0, 'SEQ_DOMAIN is a dead end under EVOLUTION');
assert.strictEqual(counts.src['Pfam'] || 0, 0, 'Pfam is a dead end under EVOLUTION');
assert.strictEqual(counts.cat['EVOL_ORTHOLOGY'], 9);
// The axis group is not constrained by itself, so other axes stay switchable.
assert.strictEqual(counts.axis['SEQUENCE'], 76051);
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_only_dead_ends_are_hidden_and_never_a_selected_value():
    """Hiding rules, kept out of browse.js's DOM loop so they can be tested.

    Hiding a *selected* value would remove the control that produced the current
    view, leaving no way to undo it. Hiding on a global count would hide values
    that are perfectly reachable, since a global zero says nothing about the
    current selection.
    """
    module = json.dumps(str(REPO / "docs" / "facet-counts.js"))
    program = f"""
const assert = require('assert');
const fc = require({module});

assert.strictEqual(fc.isDeadEnd(0, true, false), true,  'an unselected zero is a dead end');
assert.strictEqual(fc.isDeadEnd(0, true, true), false,  'a selected value must stay visible');
assert.strictEqual(fc.isDeadEnd(5, true, false), false, 'a reachable value must stay visible');
assert.strictEqual(fc.isDeadEnd(0, false, false), false, 'global mode hides nothing');
// Missing counts read as zero, not as visible.
assert.strictEqual(fc.isDeadEnd(undefined, true, false), true);
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_the_sidebar_note_never_claims_counts_it_is_not_showing():
    """The disclosure must track the mode in force (#544's tradeoff, kept honest).

    Global counts were disclosed in static markup. Now that the mode can change at
    runtime -- an old facets.json, a corpus past MAX_CUBE_ROWS, a query typed --
    static wording would be a lie in whichever mode it does not describe.
    """
    module = json.dumps(str(REPO / "docs" / "facet-counts.js"))
    program = f"""
const assert = require('assert');
const fc = require({module});

const global_ = fc.note(false, false);
const globalQ = fc.note(false, true);
const subset = fc.note(true, false);
const subsetQ = fc.note(true, true);

for (const n of [global_, globalQ, subset, subsetQ]) {{
  assert.ok(n.short && n.long, 'a mode has no wording');
}}
// Global mode must say global, and must not promise filter-aware counts.
assert.ok(/global/i.test(global_.short) && /global/i.test(global_.long));
assert.ok(!/reflect the active filters/i.test(global_.short));
assert.deepStrictEqual(global_, globalQ, 'a query does not change what global counts are');

// Subset mode must not describe itself as global...
assert.ok(!/global/i.test(subset.short), 'subset-aware counts described as global');
assert.ok(!/global/i.test(subsetQ.short));
// ...and with a query active it must disclose that the search text is excluded.
assert.ok(/search/i.test(subsetQ.short) || /search/i.test(subsetQ.long),
  'the query/cube gap is undisclosed');
assert.notDeepStrictEqual(subset, subsetQ, 'the query gap is not disclosed differently');
assert.ok(/hidden/i.test(subset.short), 'hiding empty values is undisclosed');
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr


def test_browse_js_delegates_the_count_rules_rather_than_restating_them():
    """browse.js must call the tested helpers, not re-implement them inline.

    An inline copy of the dead-end rule or the wording is invisible to every test
    above -- the DOM loop is the one part node cannot exercise, so it has to stay
    a loop and nothing more.
    """
    js = (REPO / "docs" / "browse.js").read_text()
    assert "BrowseFacetCounts.sidebarState(" in js
    assert "BrowseFacetCounts.isDeadEnd(" in js
    assert "Counts are global corpus totals" not in js, "wording duplicated in browse.js"
    # The mode flag must be the one sidebarState derived. Recomputing it in the
    # page is how the note and the numbers come to describe different modes.
    assert "state.subsetAware" in js
    assert "describeFacetCounts(state.note)" in js


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
def test_the_sidebar_state_cannot_describe_a_mode_it_is_not_in():
    """Counts, hiding, and wording are one decision or they drift apart (#638).

    The page reads all three from `sidebarState`, so a usable cube must yield
    subset-aware counts *and* subset-aware wording, and an unusable one must yield
    the global tallies *and* the global wording -- never a mix.
    """
    module = json.dumps(str(REPO / "docs" / "facet-counts.js"))
    program = f"""
const assert = require('assert');
const fc = require({module});

const cube = [['A', 'C1', 'S1', 'SEEDED', 3], ['B', 'C2', 'S2', 'REVIEWED', 7]];
const globals = {{axis: {{A: 3, B: 7}}, cat: {{C1: 3, C2: 7}}, src: {{}}, sta: {{}}}};

const live = fc.sidebarState(cube, {{axis: new Set(['A'])}}, '', globals);
assert.strictEqual(live.subsetAware, true);
assert.deepStrictEqual(live.note, fc.note(true, false));
assert.strictEqual(live.counts.cat['C2'], undefined, 'cat was not narrowed by axis=A');
assert.strictEqual(live.counts.axis['B'], 7, 'axis was narrowed by its own selection');

// Every way the cube can be unusable must land in global mode, wording included.
for (const bad of [undefined, null, [], 'nope', [['A', 'B', 'C']]]) {{
  const fallback = fc.sidebarState(bad, {{axis: new Set(['A'])}}, '', globals);
  assert.strictEqual(fallback.subsetAware, false, `bad cube read as subset-aware`);
  assert.deepStrictEqual(fallback.counts, globals, 'global tallies were not used');
  assert.deepStrictEqual(fallback.note, fc.note(false, false), 'wording claims the wrong mode');
}}

// No cube and no global tallies either: empty, not a crash.
assert.deepStrictEqual(fc.sidebarState(null, {{}}, '', undefined).counts, {{}});

// The query flag reaches the wording.
assert.deepStrictEqual(fc.sidebarState(cube, {{}}, 'kinase', globals).note, fc.note(true, true));
assert.deepStrictEqual(fc.sidebarState(cube, {{}}, '', globals).note, fc.note(true, false));
"""
    out = subprocess.run(["node", "-e", program], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
