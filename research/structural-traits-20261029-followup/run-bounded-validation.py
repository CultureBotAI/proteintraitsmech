from pathlib import Path
import os,sys,subprocess,json,hashlib,datetime
sys.path.insert(0,'scripts')
import structural_trait_curations as c
root=Path.cwd(); dest=root/'research/structural-traits-20261029-followup'; entries=c.load_curations(); paths=[e['path'] for e in entries.values()]
cmds=[['just','validate-all',*paths],['just','audit-graphs',*paths],['just','validate-history'],['just','check-vendored-sync'],['.venv/bin/python','scripts/curate_structural_traits.py'],['.venv/bin/python','scripts/record_review.py','check','--base','93c1a021d76a94fd299e0a1e3cf8f1b9671a3703']]
env=dict(os.environ,UV_CACHE_DIR='/tmp/ptm-structural-029cc7-uv-cache');rows=[]
for i,cmd in enumerate(cmds):
 p=Path(f'/tmp/ptm-1202-followup-gate-{i}.log')
 with p.open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'command':cmd,'exit_code':r.returncode,'log':str(p),'output':p.read_text()})
 print(i,r.returncode,flush=True)
 if r.returncode:break
out={'head_at_execution':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'state':'working_tree','time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'validation_scope':'24-record structural cohort; writer/history/review gates repository scope','target_count':len(paths),'inputs':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths+['scripts/structural_trait_curations.py','scripts/curate_structural_traits.py','data/curation/structural_trait_curations.yaml']},'results':rows}
(dest/'native-validation.json').write_text(json.dumps(out,indent=2)+'\n')
sys.exit(any(x['exit_code'] for x in rows))
