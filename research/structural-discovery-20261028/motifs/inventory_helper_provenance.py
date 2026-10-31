#!/usr/bin/env python3
"""2026-10-29: inventory helper provenance for parent discovery goal/#1200/#1201/#1204.

Inputs: local README purpose/input/output table and all local *.py helper bytes.
Output: new helper-provenance-20261029.json. No /tmp input or corpus/Git mutation.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
readme=HERE/'README.md'
rows=[]
text=readme.read_text()
for path in sorted(HERE.glob('*.py')):
    assert f'`{path.name}`' in text, f'Missing purpose/input/output provenance: {path.name}'
    rows.append({'path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'created_used_date_utc':'2026-10-29','purpose_inputs_outputs':'README.md#helper-provenance'})
result={'timestamp':datetime.now(timezone.utc).isoformat(),'goal_reference':'Parent-owned structural discovery on discover/structural-traits-20261028-04f08f; #1200/#1201/#1204 coordination, no issue closure claimed','inventory_scope':'All local *.py helpers, including ignored files; pathlib glob is gitignore-independent','readme_sha256':hashlib.sha256(readme.read_bytes()).hexdigest(),'helpers':rows,'tmp_inputs_documented':'README.md#historical-and-portable-inputs'}
with (HERE/'helper-provenance-20261029.json').open('x') as stream:
    json.dump(result,stream,indent=2)
    stream.write('\n')
print(json.dumps({'helpers':len(rows),'output':'helper-provenance-20261029.json'}))
