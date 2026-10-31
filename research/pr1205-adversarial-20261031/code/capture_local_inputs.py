"""Capture exact locally materialized PR1205/main inputs, 2026-10-31.

Context: adversarial PR #1205 review, issues #1204/#1206. Inputs: commit/path
allowlists from retained capture_review_inputs.py and root-materialized Git objects.
Outputs: immutable snapshots and a new inventory under this code evidence folder.
Only git show is used; no fetch, index/ref mutation or maintained-file edit occurs.
The initial API capture failed on a network/DNS outage; its helper remains intact.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import capture_review_inputs as original
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    rows=[]
    for revision,path in ([(original.PR_HEAD,p) for p in original.COMMON+original.PR_ONLY]
                          +[(original.MAIN_HEAD,p) for p in original.COMMON]):
        raw=subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)
        destination=HERE/'inputs'/revision/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists(): assert destination.read_bytes()==raw
        else:
            with destination.open('xb') as stream:stream.write(raw)
        rows.append({'revision':revision,'original_path':path,
                     'retained_path':str(destination.relative_to(HERE)),
                     'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    now=dt.datetime.now(dt.timezone.utc)
    output=HERE/('local-inputs-'+now.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    report={'created_utc':now.isoformat(),'method':__doc__,
            'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'allowlist_helper_sha256':hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),
            'inputs':rows,'prior_attempt':'capture_review_inputs.py first attempt failed with api.github.com connection errors before producing a complete inventory; this is a separately retained local-object route.'}
    with output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'path':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'inputs':len(rows)}))

if __name__=='__main__':main()
