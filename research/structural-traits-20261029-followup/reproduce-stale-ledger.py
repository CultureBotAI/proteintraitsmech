from pathlib import Path
import sys,tempfile,copy,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import yaml
import structural_trait_curations as cur
import curate_structural_traits as editor
import seed_secondary_structure as seed
from record_io import write_validated_record
from validate_strict import validate_one
original_ledger=cur.LEDGER
payload=yaml.safe_load(original_ledger.read_text())
identifier='proteintraitsmech:HELIX_TURN_HELIX'
entry=next(x for x in payload['records'] if x['identifier']==identifier)
unchanged_output_pin=entry['output_sha256']
entry['blocks']['definition']='definition: Changed scientific definition without a new reviewed output hash.\n'
with tempfile.TemporaryDirectory(prefix='ptm-independent-stale-ledger-') as tmp:
 p=Path(tmp)/'ledger.yaml';p.write_text(yaml.safe_dump(payload,sort_keys=False))
 cur.LEDGER=p;cur.load_curations.cache_clear()
 try:
  loaded=cur.load_curations();item=next(x for x in seed.build_records() if x['identifier']==identifier)
  emitted=seed.emit(item)
  out=Path(tmp)/'trait.yaml';write_validated_record(out,emitted)
  current=(ROOT/loaded[identifier]['path']).read_text()
  # Current correct output is accepted as unchanged, despite changed ledger intent.
  same=editor.curate_record_text(current,loaded[identifier])==current
  result={'identifier':identifier,'ledger_loader_accepted':True,'original_output_pin_retained':loaded[identifier]['output_sha256']==unchanged_output_pin,'seeded_definition':yaml.safe_load(out.read_text())['definition'],'schema_errors':validate_one(out),'guarded_temp_write_succeeded':out.is_file(),'record_editor_current_output_noop':same,'temporary_paths_only':True}
 finally:
  cur.LEDGER=original_ledger;cur.load_curations.cache_clear()
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
