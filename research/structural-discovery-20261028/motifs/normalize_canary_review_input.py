"""Deduplicate repeated evidence links in unsaved native review input only."""
from pathlib import Path
import hashlib
import json
import subprocess
import yaml
base=Path(__file__).resolve().parent
root=base.parents[2]
path=base/'canary-native-review-input.yaml'
record=yaml.safe_load(path.read_text())
for item in record['assessments']:
    item['evidence_ids']=list(dict.fromkeys(item['evidence_ids']))
path.write_text(yaml.safe_dump(record,sort_keys=False,allow_unicode=True,width=100))
result=subprocess.run([str(root/'.venv/bin/python'),'scripts/record_review.py','validate',str(path)],cwd=root,text=True,capture_output=True)
report={'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'note':'Only duplicate evidence references normalized; scientific assertions and source hashes unchanged.'}
with (base/'canary-native-review-input-validation-normalized.json').open('x') as stream:
    json.dump(report,stream,indent=2)
    stream.write('\n')
print(json.dumps(report,indent=2))
raise SystemExit(result.returncode)
