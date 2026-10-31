"""Independent two-base CI recovery probes, 2026-10-31, PR1205 / issue1206.

Inputs: current checks.yml exact shell and the unchanged retained 2026-10-29
single-base fixture helper. Outputs: new timestamped dual-base JSON evidence.
Only the two asserted literal production SHAs are substituted. Disposable local
Git origins/clients test both missing, both present offline, mixed, and unavailable
second base. No actual repository Git state, remote or session is mutated.
The old helper/results remain unchanged; temporary fixture paths are historical
and not portable dependencies. These probes do not certify GitHub availability.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import yaml

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=ROOT/'research/structural-discovery-20261028/ci-followup/probe_review_base_restore.py'
spec=importlib.util.spec_from_file_location('retained_single_base_fixtures',OLD)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
for key in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'):
 old.ENV.pop(key,None)
PINS=['93c1a021d76a94fd299e0a1e3cf8f1b9671a3703','bc0c6d97aaab0ba20fcf8be28bc1527430679ccb']

def digest(raw):return hashlib.sha256(raw).hexdigest()
def available(client,pin):return old.git(client,'cat-file','-e',pin+'^{commit}',check=False).returncode==0

def execute(client,origin,shell,pins,name,expected_before,expected_after,success):
 transformed=shell
 for production,fixture in zip(PINS,pins):transformed=transformed.replace(production,fixture)
 reverted=transformed
 for production,fixture in zip(PINS,pins):reverted=reverted.replace(fixture,production)
 assert reverted==shell
 before=old.state(client);origin_before=old.refs(origin)
 assert [available(client,p) for p in pins]==expected_before
 result=old.run(client,'bash','--noprofile','--norc','-c',transformed,check=False)
 assert (result.returncode==0)==success,(name,result.stderr)
 after=[available(client,p) for p in pins];assert after==expected_after,(name,after)
 assert old.state(client)==before and old.refs(origin)==origin_before
 for present,pin in zip(after,pins):
  if present:assert old.git(client,'rev-parse','--verify',pin+'^{commit}').stdout.strip()==pin
 return {'case':name,'fixture_pins':pins,'only_literal_pins_substituted':True,
         'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
         'available_before':expected_before,'available_after':after,
         'head_refs_index_fetch_head_config_and_worktree_preserved':True,
         'origin_refs_preserved':True,'protected_state_before_and_after':before}

def main():
 workflow=ROOT/'.github/workflows/checks.yml';raw=workflow.read_bytes()
 steps=yaml.safe_load(raw)['jobs']['checks']['steps']
 matches=[s for s in steps if s.get('name')=='Restore inherited review Git base'];assert len(matches)==1
 step=matches[0];shell=step['run'];assert re.findall(r'\b[0-9a-f]{40}\b',shell)==PINS
 assert steps[steps.index(step)+1]['name']=='Structured record review contract'
 assert shell.startswith('set -euo pipefail\n')
 assert 'git fetch --no-tags --no-write-fetch-head origin "$review_revision"' in shell
 with tempfile.TemporaryDirectory(prefix='ptm-dual-base-probe-') as temp:
  parent=Path(temp).resolve();origin=parent/'local-origin';old.git(parent,'init','--initial-branch=main',str(origin))
  old.git(origin,'config','user.name','Synthetic fixture');old.git(origin,'config','user.email','fixture@example.invalid')
  (origin/'tracked.txt').write_text('main fixture\n');old.git(origin,'add','tracked.txt');old.git(origin,'commit','-m','Synthetic main')
  fixture_pins=[]
  for number in (1202,1205):
   branch='synthetic-'+str(number);old.git(origin,'switch','-c',branch)
   (origin/(str(number)+'.txt')).write_text('retained historical fixture\n')
   old.git(origin,'add',str(number)+'.txt');old.git(origin,'commit','-m','Synthetic historical '+str(number))
   pin=old.git(origin,'rev-parse','HEAD').stdout.strip();fixture_pins.append(pin)
   old.git(origin,'update-ref','refs/pull/'+str(number)+'/head',pin)
   old.git(origin,'switch','main');old.git(origin,'branch','-D',branch)
  first=old.clone_fixture(parent,origin,'both-missing')
  rows=[execute(first,origin,shell,fixture_pins,'both_missing',[False,False],[True,True],True)]
  old.git(first,'remote','set-url','origin',str(parent/'no-origin'))
  rows.append(execute(first,origin,shell,fixture_pins,'both_present_offline',[True,True],[True,True],True))
  mixed=old.clone_fixture(parent,origin,'mixed')
  old.git(mixed,'fetch','--no-tags','--no-write-fetch-head','origin',fixture_pins[0])
  rows.append(execute(mixed,origin,shell,fixture_pins,'first_present_second_missing',[True,False],[True,True],True))
  failed=old.clone_fixture(parent,origin,'unavailable-second');missing='f'*40
  assert not available(origin,missing)
  rows.append(execute(failed,origin,shell,[fixture_pins[0],missing],'unavailable_second_fails',[False,False],[True,False],False))
 assert workflow.read_bytes()==raw
 now=dt.datetime.now(dt.timezone.utc)
 result={'created_utc':now.isoformat(),'reviewer':'Codex agent /root/preflight_boundary_review',
         'context':'PR1205 adversarial follow-up; issue1206 explicit historical-base retention',
         'production_pins':PINS,'production_shell':shell,'workflow_sha256':digest(raw),
         'helper_sha256':digest(Path(__file__).read_bytes()),
         'reused_helper':{'path':str(OLD.relative_to(ROOT)),'sha256':digest(OLD.read_bytes())},
         'cases':rows,'all_passed':True,
         'limits':['Only disposable local Git repositories were mutated.','Production SHA literals were asserted separately; only those literals were substituted.','A failed second fetch may retain the first fetched object; it must still fail the step and preserves protected refs/HEAD/index/FETCH_HEAD.','Actual GitHub object retrieval and full exact-head CI remain root-owned verification.']}
 output=HERE/('dual-base-probes-'+now.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
 print(json.dumps({'path':str(output),'sha256':digest(output.read_bytes()),'all_passed':True,'workflow_sha256':digest(raw),'cases':len(rows)}))

if __name__=='__main__':main()
