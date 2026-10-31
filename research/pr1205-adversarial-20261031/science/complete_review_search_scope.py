#!/usr/bin/env python3
"""PR #1205, 2026-10-31. Complete required native bounded search-scope field.
Inputs: three draft review inputs and identity-scan.json produced in this directory.
Outputs: new *-review-completed.yaml plus completed-review-validation.json.
Preserves original drafts and failed validation evidence; no record/Git/native save.
"""
import datetime,json,pathlib,subprocess,yaml
ROOT=pathlib.Path.cwd(); OUT=pathlib.Path(__file__).resolve().parent
scan=json.loads((OUT/'identity-scan.json').read_text())
outputs=[]
for p in sorted(OUT.glob('*-review-input.yaml')):
 r=yaml.safe_load(p.read_text())
 for ev in r['evidence']:
  if ev['kind']=='search':
   ev['search_scope']=scan['command']+'; '+scan['scope']+' Six files matched: the three reviewed targets plus GO0180024 membrane grommet activity, GO0036053 cellular glomerular fenestra, and GO0002930 tissue development. Their definitions were inspected and do not denote these protein geometric classes.'
 dest=p.with_name(p.name.replace('-review-input.yaml','-review-completed.yaml'))
 if dest.exists():raise SystemExit('Refusing overwrite')
 dest.write_text(yaml.safe_dump(r,sort_keys=False,allow_unicode=True,width=110)); outputs.append(str(dest.relative_to(ROOT)))
args=['.venv/bin/python','scripts/record_review.py','validate',*outputs]
p=subprocess.run(args,capture_output=True,text=True)
(OUT/'completed-review-validation.json').write_text(json.dumps({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
print(json.dumps({'outputs':outputs,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
raise SystemExit(p.returncode)
