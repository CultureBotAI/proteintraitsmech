"""Adversarial seeder boundary probes for PR #1205, 2026-10-31.

Inputs: captured bc0c6d97 seeder bytes, native writer/validator/schema pinned by
initial-code-inspection.json, and synthetic class records. Outputs: a new JSON
observation under this directory. Only temporary fixture trees are mutated.
Actual corpus, Git/index/refs, providers, sessions and goals are untouched.
Context issues #1204/#1206; later issue links belong in review disposition.
"""
from __future__ import annotations
import contextlib
import copy
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE/'inputs/bc0c6d97aaab0ba20fcf8be28bc1527430679ccb/scripts/seed_structural_discovery.py'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
import validate_strict  # noqa: E402

BASE_RECORD={
 'identifier':'proteintraitsmech:ADVERSARIAL_FIXTURE',
 'label':'synthetic fixture','definition':'Synthetic class for writer boundary probes only.',
 'definition_source':'synthetic fixture','trait_axis':'STRUCTURE','trait_category':'STRUCT_SECONDARY',
 'term_kind':'CLASS','mapping_status':'PROPOSED','license':'CC0-1.0',
 'evidence':[{'reference':'synthetic fixture'}],
 'detection_methods':[{'name':'synthetic fixture','recipe':'fixture {input}'}],
}
RELATIVE='data/traits/structure/secondary/adversarial-fixture.yaml'

def digest(raw):return hashlib.sha256(raw).hexdigest()

def fixture(root, record):
 manifest=root/'data/curation/structural_trait_discovery.yaml'
 manifest.parent.mkdir(parents=True)
 manifest.write_text(yaml.safe_dump({'version':1,'records':[{'path':RELATIVE,'record':record}]}))
 (root/'data/traits').mkdir(parents=True)
 namespace={'__name__':'independent_seeder_fixture','__file__':str(root/'scripts/seed_structural_discovery.py')}
 exec(compile(SOURCE.read_bytes(),str(SOURCE),'exec'),namespace)
 return namespace,manifest,root/RELATIVE

def apply_record_case(name, edits):
 with tempfile.TemporaryDirectory(prefix='ptm-adversarial-record-') as temp:
  root=Path(temp);record=copy.deepcopy(BASE_RECORD);record.update(edits)
  namespace,manifest,destination=fixture(root,record)
  try:
   result=namespace['seed'](manifest=manifest,root=root,apply=True)
   error=None
  except Exception as exc:
   result=None;error={'type':type(exc).__name__,'message':str(exc)}
  return {'case':name,'record_edits':edits,'report':result,'error':error,
          'destination_created':destination.exists(),
          'native_validation_errors':validate_strict.validate_one(destination) if destination.exists() else None,
          'written_bytes_sha256':digest(destination.read_bytes()) if destination.exists() else None}

def cli_case(kind):
 with tempfile.TemporaryDirectory(prefix='ptm-adversarial-report-') as temp:
  root=Path(temp);namespace,_,destination=fixture(root,copy.deepcopy(BASE_RECORD))
  owned=root/'research/structural-discovery-20261028'
  if kind=='allowed_root_symlink':
   external=root/'outside-owned-evidence';external.mkdir();owned.parent.mkdir()
   owned.symlink_to(external,target_is_directory=True);report=owned/'new.json'
   resolved=external/'new.json'
  else:
   owned.mkdir(parents=True);obstruction=owned/'file-not-directory';obstruction.write_text('retain prior evidence\n')
   report=obstruction/'new.json';resolved=report
  before=sys.argv
  try:
   sys.argv=['seed_structural_discovery.py','--apply','--report',str(report)]
   with contextlib.redirect_stdout(io.StringIO()):namespace['main']()
   error=None
  except Exception as exc:error={'type':type(exc).__name__,'message':str(exc)}
  finally:sys.argv=before
  return {'case':kind,'error':error,'destination_created':destination.exists(),
          'report_created':resolved.exists(),'report_inside_owned_lexical_path':True,
          'report_resolved_inside_owned_root':resolved.is_relative_to(owned),
          'report_resolved_outside_repository':False,
          'note':'outside-owned-evidence remains inside the disposable fixture root; it stands in for an unauthorized sibling path, not an actual external file.' if kind=='allowed_root_symlink' else 'Existing parent is a regular file, so report writing is predictably invalid before seeding.'}

def main():
 inspection=json.loads((HERE/'initial-code-inspection.json').read_bytes())
 contexts=['scripts/record_io.py','scripts/validate_strict.py','src/proteintraitsmech/schema/proteintraitsmech.yaml']
 for path in contexts:
  expected=next(i['sha256'] for i in inspection['source']['inputs'] if i['path']==path)
  assert digest((ROOT/path).read_bytes())==expected,path
 rows=[apply_record_case('positive_structural_fixture',{}),
       apply_record_case('nonstructural_category',{'trait_category':'SEQ_MOTIF'}),
       apply_record_case('mismatched_structural_folder',{'trait_category':'STRUCT_CAVITY'}),
       apply_record_case('null_detection_recipe',{'detection_methods':[{'name':'synthetic fixture','recipe':None}]}),
       apply_record_case('protein_identifier',{'identifier':'UniProtKB:P12345'}),
       cli_case('allowed_root_symlink'),cli_case('parent_is_file')]
 now=dt.datetime.now(dt.timezone.utc)
 report={'created_utc':now.isoformat(),'reviewer':'Codex agent /root/preflight_boundary_review',
         'context':'PR1205 independent adversarial code audit; #1204/#1206 history',
         'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':digest(SOURCE.read_bytes())},
         'helper_sha256':digest(Path(__file__).read_bytes()),
         'native_contexts':[{'path':p,'sha256':digest((ROOT/p).read_bytes())} for p in contexts],
         'cases':rows,'limits':['These are deliberately malformed synthetic inputs, not claims that the three submitted records contain these faults.','Schema-valid acceptance is only a machine fact; reviewer judgment distinguishes supported invariants from hypothetical threats.','No actual corpus, Git/index/refs, network, providers, sessions or goals were mutated.']}
 output=HERE/('seeder-boundary-probes-'+now.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
 with output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
 print(json.dumps({'path':str(output),'sha256':digest(output.read_bytes()),'cases':[{'case':r['case'],'created':r['destination_created'],'error':r['error'],'validation_errors':r.get('native_validation_errors')} for r in rows]}))

if __name__=='__main__':main()
