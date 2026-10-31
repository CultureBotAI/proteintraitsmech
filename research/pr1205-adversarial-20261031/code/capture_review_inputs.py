"""Retain exact PR1205/current-main code inputs, 2026-10-31.

Purpose: independent adversarial code review; context PR #1205, issues #1204/#1206.
Inputs: literal GitHub repository/commit/path allowlist below, read through gh API.
Outputs: immutable exact source snapshots and a new hash inventory in this directory.
No Git operations, remote writes, providers, sessions, goals or maintained edits.
Re-running accepts byte-identical existing snapshots and refuses differing bytes.
"""
from __future__ import annotations
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPOSITORY = 'CultureBotAI/proteintraitsmech'
PR_HEAD = 'bc0c6d97aaab0ba20fcf8be28bc1527430679ccb'
MAIN_HEAD = 'c0d87f89e18a1c4a09904a835cf782d84d9d53d1'
COMMON = ['AGENTS.md','docs/record-reviews.md','docs/record-review-profile.md',
          'scripts/record_review.py','tests/test_record_review_contract.py',
          '.github/workflows/checks.yml','conf/internal_id_label_baseline.yaml',
          'src/proteintraitsmech/schema/proteintraitsmech.yaml','scripts/record_io.py',
          'scripts/validate_strict.py','scripts/build_docs_index.py']
PR_ONLY = ['scripts/seed_structural_discovery.py','tests/test_seed_structural_discovery.py',
           'scripts/adhoc/structural_discovery_20261028/package_evidence.py',
           'scripts/adhoc/structural_discovery_20261028/observe_open_work.py',
           'data/curation/structural_trait_discovery.yaml','.claude/skills/add-record/SKILL.md',
           'research/structural-discovery-20261028/ci-followup/README.md',
           'research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json']

def capture(item):
    revision, path = item
    endpoint = f'repos/{REPOSITORY}/contents/{path}?ref={revision}'
    raw = subprocess.check_output(['gh','api',endpoint,'-H','Accept: application/vnd.github.raw+json'],cwd=HERE)
    destination = HERE/'inputs'/revision/path
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == raw, str(destination)
    else:
        with destination.open('xb') as stream: stream.write(raw)
    return {'repository':REPOSITORY,'revision':revision,'original_path':path,
            'retained_path':str(destination.relative_to(HERE)),
            'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
            'url':f'https://github.com/{REPOSITORY}/blob/{revision}/{path}'}

def main():
    inputs = [(PR_HEAD,p) for p in COMMON+PR_ONLY]+[(MAIN_HEAD,p) for p in COMMON]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(capture,inputs))
    timestamp=dt.datetime.now(dt.timezone.utc)
    output=HERE/('captured-inputs-'+timestamp.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    report={'created_utc':timestamp.isoformat(),'purpose':__doc__,
            'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'inputs':rows,'limits':['Exact pinned remote bytes only; this does not fetch a Git object database or establish complete corpus absence.']}
    with output.open('x') as stream: json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'input_count':len(rows)}))

if __name__ == '__main__': main()
