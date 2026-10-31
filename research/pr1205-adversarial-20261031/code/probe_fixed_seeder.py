"""Independent fix probes for PR1205 issues #1225/#1226, 2026-10-31.

Inputs: current maintained seeder and unchanged native validator/writer; fixtures
from retained probe_seeder_boundaries.py. Outputs: exact source snapshot named by
SHA and a new timestamped JSON result. Old helpers/results are not overwritten.
Only synthetic temporary trees are mutated; no actual corpus/Git/session actions.
Current valid output comparison reads three real records without applying them.
"""
from __future__ import annotations
import contextlib
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import yaml
sys.dont_write_bytecode=True
import probe_seeder_boundaries as prior
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def digest(raw):return hashlib.sha256(raw).hexdigest()

def cli_positive_or_readonly(readonly=False):
 with tempfile.TemporaryDirectory(prefix='ptm-fixed-report-') as tmp:
  root=Path(tmp).resolve();namespace,_,destination=prior.fixture(root,copy.deepcopy(prior.BASE_RECORD))
  folder=root/'research/structural-discovery-20261028';folder.mkdir(parents=True)
  report=folder/'new.json'
  if readonly:folder.chmod(0o555)
  previous=sys.argv
  try:
   sys.argv=['seed_structural_discovery.py','--apply','--report',str(report)]
   with contextlib.redirect_stdout(io.StringIO()):namespace['main']()
   error=None
  except Exception as exc:error={'type':type(exc).__name__,'message':str(exc)}
  finally:
   sys.argv=previous
   if readonly:folder.chmod(0o755)
  return {'case':'readonly_existing_report_parent' if readonly else 'positive_cli_report',
          'effective_uid':os.geteuid(),'error':error,'destination_created':destination.exists(),
          'report_created':report.exists()}

def main():
 source=ROOT/'scripts/seed_structural_discovery.py';raw=source.read_bytes();checksum=digest(raw)
 snapshot=HERE/'fixed-source-snapshots'/(checksum+'.py');snapshot.parent.mkdir(exist_ok=True)
 if snapshot.exists():assert snapshot.read_bytes()==raw
 else:
  with snapshot.open('xb') as stream:stream.write(raw)
 prior.SOURCE=snapshot
 rows=[prior.apply_record_case('positive_structural_fixture',{}),
       prior.apply_record_case('mismatched_structural_folder',{'trait_category':'STRUCT_CAVITY'}),
       prior.apply_record_case('null_detection_recipe',{'detection_methods':[{'name':'synthetic','recipe':None}]}),
       prior.apply_record_case('protein_identifier',{'identifier':'UniProtKB:P12345'}),
       prior.cli_case('allowed_root_symlink'),prior.cli_case('parent_is_file'),
       cli_positive_or_readonly(),cli_positive_or_readonly(True)]
 namespace={'__name__':'independent_fixed_emission','__file__':str(source)}
 exec(compile(raw,str(snapshot),'exec'),namespace)
 manifest=ROOT/'data/curation/structural_trait_discovery.yaml'
 emissions=[]
 for path,record,text in namespace['load_candidates'](manifest,ROOT):
  emissions.append({'path':str(path.relative_to(ROOT)),'identifier':record['identifier'],
                    'existing_sha256':digest(path.read_bytes()),'emitted_sha256':digest(text.encode()),
                    'byte_identical':path.read_bytes()==text.encode()})
 assert source.read_bytes()==raw
 now=dt.datetime.now(dt.timezone.utc)
 report={'created_utc':now.isoformat(),'reviewer':'Codex agent /root/preflight_boundary_review',
         'issues':['https://github.com/CultureBotAI/proteintraitsmech/issues/1225','https://github.com/CultureBotAI/proteintraitsmech/issues/1226'],
         'source_sha256':checksum,'retained_source':str(snapshot.relative_to(ROOT)),
         'helper_sha256':digest(Path(__file__).read_bytes()),
         'fixture_helper':{'path':str(Path(prior.__file__).relative_to(ROOT)),'sha256':digest(Path(prior.__file__).read_bytes())},
         'cases':rows,'existing_record_emissions':emissions,
         'limits':['Synthetic temporary-fixture apply only. Current three-record emission is a read-only byte comparison.','The read-only-directory probe tests a predictable permission condition, not arbitrary races or a transactional guarantee.','Recorded source snapshot preserves this exact attempt if root fixes further afterward.']}
 output=HERE/('fixed-seeder-probes-'+now.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 with output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 print(json.dumps({'path':str(output),'sha256':digest(output.read_bytes()),'source_sha256':checksum,
                   'cases':[{'case':r['case'],'created':r['destination_created'],'error':r['error']} for r in rows],
                   'emissions_identical':all(r['byte_identical'] for r in emissions)}))

if __name__=='__main__':main()
