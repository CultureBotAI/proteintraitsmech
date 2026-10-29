from pathlib import Path
import sys,json,subprocess,hashlib,datetime
sys.path.insert(0,'scripts')
import structural_trait_curations as c,curate_structural_traits as ed
import seed_secondary_structure as s,seed_localstructuralfeature as l,seed_foundational_traits as f
from record_io import merge_on_reseed
HEAD='93c1a021d76a94fd299e0a1e3cf8f1b9671a3703';BASE='c4147394c698324ae537c0c63c2c9f6647c4f4fc'
def git(*args):return subprocess.check_output(['git',*args],text=True)
entries=c.load_curations();preimages={};rows=[];seeds=[]
for p in git('ls-tree','-r','--name-only',HEAD,'research/structural-traits-20261028/followup-preimages').splitlines():
 t=git('show',f'{HEAD}:{p}');preimages[c.digest(t)]=(p,t)
for e in entries.values():
 t=git('show',f'{BASE}:{e["path"]}');preimages[c.digest(t)]=(f'{BASE}:{e["path"]}',t)
for i,e in entries.items():
 current=(c.ROOT/e['path']).read_text(); old=git('show',f'{HEAD}:{e["path"]}')
 assert current==old and c.digest(current)==e['output_sha256']
 name,pre=preimages[e['input_sha256']];assert ed.curate_record_text(pre,e)==current
 assert ed.curate_record_text(current,e)==current
 rows.append({'identifier':i,'path':e['path'],'sha256':c.digest(current),'preimage':name,'unchanged_since_scientific_review':True,'exact_replay':True,'idempotent':True})
unrelated=0
for mod,emit,items,owner in [(s,s.emit,s.build_records(),'seed_secondary_structure'),(l,l.yaml_for,l.TERMS,'seed_localstructuralfeature'),(f,f.emit_record,f.SPECS,'seed_foundational_traits')]:
 for item in items:
  hook=mod.curate_seed;mod.curate_seed=lambda t,o:t
  try:raw=emit(item)
  finally:mod.curate_seed=hook
  i=c.parse_record(raw)['identifier'];out=emit(item)
  if i not in entries:assert out==raw;unrelated+=1;continue
  e=entries[i];current=(c.ROOT/e['path']).read_text()
  assert c.digest(raw)==e['seed_preimages'][owner]
  assert c.digest(out)==e['seed_outputs'][owner]
  merged=merge_on_reseed(current,out)
  assert c.parse_record(merged)==c.parse_record(current)
  assert merge_on_reseed(merged,out)==merged
  seeds.append({'identifier':i,'owner':owner,'raw_sha256':c.digest(raw),'output_sha256':c.digest(out),'merge_preserves_record_semantics':True,'reseed_idempotent':True})
assert len(rows)==24 and len(seeds)==25
out={'baseline':HEAD,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':rows,'source_owner_emissions':seeds,'unrelated_emissions_unchanged':unrelated,'limit':'Integrity hashes detect stale edits; deliberately replacing blocks and all relevant hashes constitutes new review metadata, not cryptographic proof of human approval.'}
Path('research/structural-traits-20261029-followup/replay-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(len(rows),len(seeds),unrelated)
