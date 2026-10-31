#!/usr/bin/env python3
"""PR #1205; 2026-10-31. Read-only context/gate capture for exact-head science review.
Inputs: three target records, their maintained owners, native review/schema/rubric,
committed primary artifacts, current local corpus (ignored-inclusive bounded scan).
Outputs: new inspection JSON/target YAML, historical pins, check logs/results,
identity-hit metadata, and adjacent-main context under this script's directory.
No network, Git mutation, record edit, immutable native save or detector run.
Run once from repository root; refuses existing primary output.
"""
import concurrent.futures, datetime, hashlib, json, os, pathlib, shlex, subprocess
import yaml
ROOT=pathlib.Path.cwd(); OUT=pathlib.Path(__file__).resolve().parent; REL=OUT.relative_to(ROOT)
BASE='bc0c6d97aaab0ba20fcf8be28bc1527430679ccb'
if (OUT/'historical-pins.json').exists(): raise SystemExit('Refusing to replace previous capture')
ENV=dict(os.environ, GIT_NO_LAZY_FETCH='1')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
def sha(b): return hashlib.sha256(b).hexdigest()
def run(args, name):
 p=subprocess.run(args,capture_output=True,text=True,env=ENV)
 (OUT/(name+'.log')).write_text('$ '+shlex.join(args)+'\n'+p.stdout+'\nSTDERR:\n'+p.stderr+'\n')
 return {'command':shlex.join(args),'exit_code':p.returncode,'log':str(REL/(name+'.log')),'accessed_at':now(),'stdout':p.stdout}
paths=['data/traits/structure/secondary/beta-arch.yaml','data/traits/structure/cavity/tunnel-bottleneck.yaml','data/traits/structure/cavity/membrane-facing-channel-fenestration.yaml']
common=['AGENTS.md','.claude/skills/review-yaml-record/SKILL.md','.claude/skills/curate-yaml-record/SKILL.md','.claude/skills/curate-yaml-record/references/review-checklist.md','conf/record_review.yaml','docs/record-reviews.md','docs/record-review-profile.md','schema/record_review.yaml','src/proteintraitsmech/schema/proteintraitsmech.yaml','data/curation/structural_trait_discovery.yaml','scripts/seed_structural_discovery.py','scripts/record_review.py','scripts/validate_strict.py','scripts/validate_uniprot_grounding.py','scripts/audit_causal_graphs.py','justfile','data/traits/structure/cavity/tunnel.yaml','data/traits/structure/secondary/super-secondary-motif.yaml']
artifact_dir='research/structural-discovery-20261028/motifs/'
artifacts=['natcomm-2022-immunoglobulin.xml','caver2012-plos-primary.html','caver-discovery-userguide.pdf','caver-discovery-userguide.txt','caver-biotools-registry.json','rcsb-1cqw-entry.json','fenestration-pnas-published.pdf','fenestration-pnas-published.txt','fenestration-rcsb-7wli-entry.json','primary-artifact-retrieval.json','fenestration-source-retrieval.json','fenestration-pdf-provenance.json']
inputs=common+[artifact_dir+p for p in artifacts]
allpins=[]
for p in paths+inputs:
 historic=subprocess.run(['git','show',BASE+':'+p],capture_output=True,env=ENV,check=True).stdout
 current=(ROOT/p).read_bytes()
 if historic!=current: raise SystemExit('Changed historical input '+p)
 allpins.append({'path':p,'sha256':sha(historic),'role':'target' if p in paths else 'context'})
(OUT/'historical-pins.json').write_text(json.dumps({'git_revision':BASE,'state':'git_commit','inputs':allpins,'captured_at':now()},indent=2)+'\n')
manifest=yaml.safe_load((ROOT/'data/curation/structural_trait_discovery.yaml').read_text())
semantic=[]
for p in paths:
 r=yaml.safe_load((ROOT/p).read_text()); slug=pathlib.Path(p).stem
 target={'target_id':r['identifier'],'path':p,'label':r['label'],'record_class':'ProteinTraitRecord','kind':'generated','owner_paths':[{'repository':'CultureBotAI/proteintraitsmech','path':'data/curation/structural_trait_discovery.yaml','role':'Maintained discovery content'},{'repository':'CultureBotAI/proteintraitsmech','path':'scripts/seed_structural_discovery.py','role':'Guarded native emitter'}]}
 tp=REL/(slug+'-targets.yaml'); (ROOT/tp).write_text(yaml.safe_dump({'targets':[target]},sort_keys=False))
 args=['.venv/bin/python','scripts/record_review.py','inspect','--targets',str(tp)]
 for inp in inputs: args+=['--input',inp]
 res=run(args,slug+'-inspect'); assert res['exit_code']==0,res
 (OUT/(slug+'-inspection.json')).write_text(res['stdout'])
 row=next(x['record'] for x in manifest['records'] if x['path']==p)
 semantic.append({'path':p,'sha256':sha((ROOT/p).read_bytes()),'manifest_mapping_equal':r==row,'canonical_examples':len(r.get('canonical_examples',[])),'causal_graphs':len(r.get('causal_graphs',[])),'mapping_status':r['mapping_status']})
 assert r==row and r['mapping_status']=='PROPOSED'
(OUT/'emitted-semantics.json').write_text(json.dumps(semantic,indent=2)+'\n')
commands=[(['.venv/bin/python','scripts/validate_strict.py','--workers','1','--out',str(REL/'strict.tsv')]+paths,'strict'),(['.venv/bin/python','scripts/validate_uniprot_grounding.py','--out',str(REL/'grounding.tsv')]+paths,'grounding'),(['.venv/bin/python','scripts/audit_causal_graphs.py']+paths,'graphs'),(['mkdssp','--version'],'mkdssp-version'),(['mkdssp','--help'],'mkdssp-help')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 results=list(ex.map(lambda item:run(*item),commands))
for r in results: r.pop('stdout',None)
(OUT/'native-check-results.json').write_text(json.dumps(results,indent=2)+'\n')
pattern=r'beta[- _]?arch\b|β[- _]?arch\b|tunnel[- _]?(bottleneck|constriction)|fenestrat'
res=run(['rg','--no-ignore','--hidden','-l','-i','--glob','*.yaml',pattern,'data/traits'],'identity-scan')
hits=[]
for p in res['stdout'].splitlines():
 raw=(ROOT/p).read_bytes(); r=yaml.safe_load(raw)
 hits.append({'path':p,'sha256':sha(raw),'identifier':r.get('identifier'),'label':r.get('label'),'definition':r.get('definition'),'synonyms':r.get('synonyms',[])})
(OUT/'identity-scan.json').write_text(json.dumps({'command':res['command'],'exit_code':res['exit_code'],'accessed_at':res['accessed_at'],'scope':'Current isolated clone data/traits; hidden and ignored files included. Bounded lexical screen, not proof of global absence; original Documents staging inaccessible. Main has been integrated by coordinator; historical target pins separately asserted.','hit_count':len(hits),'hits':hits},indent=2)+'\n')
adj=[]
for p in ['data/traits/structure/cavity/internal-buried-hydration-packing-microcavity.yaml','data/traits/structure/cavity/intramolecular-substrate-channeling-tunnel.yaml']:
 b=(ROOT/p).read_bytes(); r=yaml.safe_load(b); adj.append({'path':p,'sha256':sha(b),'identifier':r['identifier'],'definition':r['definition']})
(OUT/'adjacent-main-context.json').write_text(json.dumps({'reference_revision':'c0d87f89e18a1c4a09904a835cf782d84d9d53d1','accessed_at':now(),'records':adj,'assessment':'No identity collision. Enclosed hydration void lacks direct bulk-solvent tunnel access; lateral fenestration traverses channel wall to lipid exterior. Intermediate-channeling tunnel joins catalytic sites with asserted function; a bottleneck is a minimum-radius region of a path. These neighboring records were read solely for boundary discrimination, not scientifically audited or endorsed.'},indent=2)+'\n')
print(json.dumps({'pins':len(allpins),'checks':results,'identity_hits':len(hits),'output':str(REL)}))
