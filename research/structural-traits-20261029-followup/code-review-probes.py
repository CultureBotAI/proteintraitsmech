from pathlib import Path
import sys, json, subprocess, hashlib, copy, tempfile, contextlib, io
HEAD='93c1a021d76a94fd299e0a1e3cf8f1b9671a3703'
BASE='c4147394c698324ae537c0c63c2c9f6647c4f4fc'
OUT=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[2]
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True)
assert git('rev-parse','HEAD').strip()==HEAD
sys.path.insert(0,str(ROOT/'scripts'))
import yaml
import structural_trait_curations as cur
import curate_structural_traits as ed
import seed_secondary_structure as sec
import seed_localstructuralfeature as lsf
import seed_foundational_traits as fnd
from record_io import merge_on_reseed,extract_block
from validate_strict import validate_one
for p in ['scripts/structural_trait_curations.py','scripts/curate_structural_traits.py','scripts/seed_secondary_structure.py','scripts/seed_localstructuralfeature.py','scripts/seed_foundational_traits.py','scripts/record_io.py','scripts/validate_strict.py','data/curation/structural_trait_curations.yaml']:
 assert (ROOT/p).read_text()==git('show',f'{HEAD}:{p}'),p
ledger=cur.load_curations()
entries=[]; preimages={}
for p in git('ls-tree','-r','--name-only',HEAD,'research/structural-traits-20261028/followup-preimages').splitlines():
 t=git('show',f'{HEAD}:{p}');preimages[cur.digest(t)]=(p,t)
for ident,e in ledger.items():
 before=git('show',f'{BASE}:{e["path"]}');preimages[cur.digest(before)]=(f'{BASE}:{e["path"]}',before)
 rows={}
for ident,e in ledger.items():
 current=git('show',f'{HEAD}:{e["path"]}')
 assert cur.digest(current)==e['output_sha256'],ident
 assert ed.curate_record_text(current,e)==current,ident
 source,text=preimages[e['input_sha256']]
 assert ed.curate_record_text(text,e)==current,ident
 assert len(cur.parse_record(current).get('curation_history',[]))==len(cur.parse_record(text).get('curation_history',[]))+1
 entries.append({'id':ident,'input_source':source,'output_hash_matches':True,'editor_reproduces_committed_bytes':True,'committed_replay_noop':True,'history_appends_one':True})
seed_rows=[];original_emissions={}
for mod,func,items,owner in [(sec,sec.emit,sec.build_records(),'seed_secondary_structure'),(lsf,lsf.yaml_for,lsf.TERMS,'seed_localstructuralfeature'),(fnd,fnd.emit_record,fnd.SPECS,'seed_foundational_traits')]:
 original_hook=mod.curate_seed
 for item in items:
  mod.curate_seed=lambda text,_owner:text
  try:raw=func(item)
  finally:mod.curate_seed=original_hook
  ident=yaml.safe_load(raw)['identifier'];emitted=func(item)
  if ident not in ledger:
   assert emitted==raw,ident
   continue
  e=ledger[ident];original_emissions[(ident,owner)]=raw
  current=git('show',f'{HEAD}:{e["path"]}');merged=merge_on_reseed(current,emitted)
  semantic_equal=yaml.safe_load(merged)==yaml.safe_load(current)
  old_merged=merge_on_reseed(current,raw)
  old_equal=yaml.safe_load(old_merged)==yaml.safe_load(current)
  seed_rows.append({'id':ident,'owner':owner,'merge_semantic_preservation':semantic_equal,'history_block_preserved':extract_block(current,'curation_history')==extract_block(merged,'curation_history'),'second_merge_byte_stable':merge_on_reseed(merged,emitted)==merged,'old_unhooked_emission_would_regress_current_record':not old_equal})
  assert semantic_equal,ident
  assert extract_block(current,'curation_history')==extract_block(merged,'curation_history'),ident
  assert merge_on_reseed(merged,emitted)==merged,ident
# Revalidate scoped committed records with actual closed-schema validator; no repository report writes.
validation=[]
for ident,e in ledger.items():
 errors=validate_one(ROOT/e['path']);validation.append({'id':ident,'errors':errors});assert not errors,(ident,errors)
# Exercise stale reviewed block hashes without touching the ledger or corpus.
ident='proteintraitsmech:HELIX_TURN_HELIX';e=copy.deepcopy(ledger[ident])
e['blocks']['definition']='definition: This definition was changed without updating its reviewed output pin.\n'
original_loader=cur.load_curations
cur.load_curations=lambda:{ident:e}
try:
 raw=original_emissions[(ident,'seed_secondary_structure')]
 unpinned=cur.curate_seed(raw,'seed_secondary_structure')
 stale_seed_accepted='changed without updating' in yaml.safe_load(unpinned)['definition']
finally:cur.load_curations=original_loader
source,prior=preimages[e['input_sha256']]
try:ed.curate_record_text(prior,e);editor_rejected=False
except ValueError:editor_rejected=True
res={'reviewed_head':HEAD,'base':BASE,'entries':entries,'seed_emissions':seed_rows,'strict_validation':validation,'adversarial_stale_ledger_block':{'seed_accepted':stale_seed_accepted,'editor_rejected':editor_rejected,'hypothesis_only_pending_materiality_review':True},'git_head_after':git('rev-parse','HEAD').strip(),'git_status_after':git('status','--short')}
(OUT/'code-review-probes.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'entry_count':len(entries),'seed_emissions':len(seed_rows),'old_behavior_regressions_detected':sum(r['old_unhooked_emission_would_regress_current_record'] for r in seed_rows),'strict_validations':len(validation),'stale_ledger_probe':res['adversarial_stale_ledger_block'],'head':res['git_head_after'],'status':res['git_status_after']},indent=2))
