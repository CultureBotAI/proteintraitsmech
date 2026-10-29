#!/usr/bin/env python3
"""2026-10-29: prepare independently assessed native review; never save a bundle.

Goal: parent-owned structural discovery; coordination #1200/#1201/#1204.
Inputs: native inspection JSON, pinned emitted record and manifest, retained sources,
and completed native check results observed by the reviewer in this session.
Outputs: new native review input, semantic comparison and review-validation JSON.
No /tmp reads here; historical PDF/manual acquisition is documented separately.
No corpus, Git or prior review mutation. Execution requires already-completed gates.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
inspection=json.loads((HERE/'fenestration-native-inspection.json').read_text())
hashes={r['path']:r['sha256'] for r in inspection['source']['inputs']}
for path,digest in hashes.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest, f'Input drift: {path}'
record_path='data/traits/structure/cavity/membrane-facing-channel-fenestration.yaml'
manifest_path='data/curation/structural_trait_discovery.yaml'
assert hashes[record_path]=='7ba68696bc371b02f6d8f1abcfe18f20d91df74f7beb237e45c0f9ec4965aa2f'
assert hashes[manifest_path]=='c08c4170529368497d507c91d42f2dfccbd7e08d770ab65b187468ffe47c091d'
record=yaml.safe_load((ROOT/record_path).read_text())
target=record['identifier']
rows=yaml.safe_load((ROOT/manifest_path).read_text())['records']
selected=[row for row in rows if row['path']==record_path]
assert len(selected)==1 and selected[0]['record']==record
assert record['mapping_status']=='PROPOSED' and record['term_kind']=='CLASS'
assert not record.get('canonical_examples') and not record.get('causal_graphs')
assert len(record['curation_history'])==1 and record['curation_history'][0]['llm_assisted']
assert (HERE/'fenestration-grounding.tsv').exists(), 'Await actual completed grounding command'
now=datetime.now(timezone.utc)
finish=now.strftime('%Y-%m-%dT%H:%M:%SZ')
stamp=now.strftime('%Y%m%dT%H%M%SZ')
semantics={'timestamp':finish,'record_path':record_path,'record_sha256':hashes[record_path],'manifest_sha256':hashes[manifest_path],'whole_mapping_equal':True,'qualified_examples':0,'causal_graphs':0,'history_events':1}
with (HERE/'fenestration-emitted-semantic-comparison.json').open('x') as stream:
    json.dump(semantics,stream,indent=2)
    stream.write('\n')
evidence=[]
def ev(eid,kind,reference,locator,summary,path=None,support='supports'):
    row=dict(evidence_id=eid,kind=kind,reference=reference,locator=locator,accessed_at=finish,support=support,summary=summary)
    if path:
        row['snapshot_sha256']=hashes[path]
    evidence.append(row)
ev('record','record_content',record_path,'Entire emitted YAML','Read every field. Emitted mapping equals the exact maintained manifest row, with PROPOSED status, one model-assisted creation event and no canonical examples or causal graphs.',record_path)
ev('PNAS','primary_source','https://www.pnas.org/doi/10.1073/pnas.2401591121','Published paper pages1-2 and10; publisher Results, MOLE2.5 Methods and copyright section','Published PMID38787877/DOI identity verified. Primary text describes membrane-side passages to the central cavity, includes7WLI, and uses MOLE2.5 with central-origin and membrane-parallel filtering. Published license is CC-BY4.0.','research/structural-discovery-20261028/motifs/fenestration-pnas-published.pdf')
ev('RCSB','database','https://www.rcsb.org/structure/7WLI','Archive entry, assembly, chain, ligand and revision metadata; retained core-entry JSON','Human CaV3.3, chainA, author monomer; cryo-EM3.3angstrom, revision1.2 dated2024-10-30.1135/2223 residues modeled. Apo designation is relative to investigated inhibitors; lipids and calcium are present.','research/structural-discovery-20261028/motifs/fenestration-rcsb-7wli-entry.json')
ev('manual','primary_source','https://www.caver.cz/fil/download/manual/caver_userguide.pdf','CLI pages6-7; input/configuration pages21-22; software/documentation license notice','Inspected manual supports PDB-directory command, required start and probe/shell configuration. It provides no automatic membrane-frame fenestration classifier. Software/manual retain GPL3.0.','research/structural-discovery-20261028/motifs/caver-discovery-userguide.pdf')
ev('registry','database','https://bio.tools/api/tool/caver/?format=json','biotoolsID, primary publication, software license','Exact caver identifier resolves to CAVER with primary PMID23093919 and GPL3.0; presently listed version3.02 does not certify execution of the documented3.0/3.01 interface.','research/structural-discovery-20261028/motifs/caver-biotools-registry.json')
ev('EDAM','authority','https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl','operation_2406','Official exact Protein structure analysis class inspected during immediately preceding canary source audit; reused only for the unchanged method identifier.')
ev('ECO','authority','https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo','Release2026-07-10, ECO0007669','Official exact computational evidence used in automatic assertion class inspected during immediately preceding canary source audit; it labels the method, not a completed run.')
ev('wwPDB','authority','https://www.wwpdb.org/about/usage-policies','Archive usage policy','Inspected archive CC0-1.0 policy; archive licensing does not relicense the primary crystallography/cryo-EM article.')
ev('schema','authority','src/proteintraitsmech/schema/proteintraitsmech.yaml','ProteinTraitRecord; StructuralGeometryRepresentation; DetectionMethod','Representative structure references may omit residue ranges. The method recipe is documented executable syntax, not a claim that a workflow ran.','src/proteintraitsmech/schema/proteintraitsmech.yaml')
ev('rubric','authority','.claude/skills/curate-yaml-record/references/review-checklist.md','All ten field-by-field areas','Applied current native identity, axis, definition, hierarchy, representation, chemistry/function, examples, graph, discussions/datasets and audit rubric.','.claude/skills/curate-yaml-record/references/review-checklist.md')
ev('tunnel','record_content','data/traits/structure/cavity/tunnel.yaml','Existing identifier and whole-passage definition','The native parent denotes an entire connecting protein passage. The proposed child is a geometric specialization of that class.','data/traits/structure/cavity/tunnel.yaml')
ev('owners','record_content',manifest_path+'; scripts/seed_structural_discovery.py; justfile','Exact manifest row and native seed-structural-discovery recipe','Maintained content, emitter ownership and native command route are explicit; this is not a separate implementation audit.',manifest_path)
ev('card','record_content','research/structural-discovery-20261028/cavities/membrane-fenestration-card.json','Candidate definition, scope, methods and example dossier','Used as the candidate proposal to independently test against primary sources, not as proof of its scientific assertions.','research/structural-discovery-20261028/cavities/membrane-fenestration-card.json',support='context_only')
ev('validation','validation','research/structural-discovery-20261028/motifs/fenestration-strict.tsv; fenestration-grounding.tsv','Independent native commands and observed output','One target passed closed strict validation, grounding validation with zero semantic findings, and graph audit with zero graphs/errors/warnings. Registry context counts do not imply examples on this target.')
assessments=[]
def assess(aid,area,topic,summary,ids,outcome='supported'):
    assessments.append(dict(assessment_id=aid,area=area,topic=topic,outcome=outcome,summary=summary,target_ids=[target],evidence_ids=ids))
assess('A01','identity','Identifier, class boundary and label','A geometric lateral connecting passage is a reusable structural class. The scope excludes cellular fenestrae and the principal pore; no equivalent external CURIE is asserted.',['record','PNAS','rubric'])
assess('A02','nomenclature','Synonyms','The membrane-facing alias is exact within the stated class. Generic lateral fenestration is marked broader with an explicit curator scope distinction.',['record','rubric'])
assess('A03','scope','Axis and category','STRUCTURE / STRUCT_CAVITY follows the defining geometric representation. CLASS and PROPOSED preserve class-level identity without human-review promotion.',['record','schema','rubric'])
assess('A04','evidence','Definition and source scope','The definition is a conservative geometry synthesis of the cited study. It makes no claim that every channel has this feature.',['record','PNAS'])
assess('A05','consistency','Hierarchy','TUNNEL is an appropriate broader class for this complete connecting passage, unlike the bottleneck part reviewed separately. No erroneous whole-channel parent or cavity-equivalence assertion is present.',['record','tunnel','rubric'])
assess('A06','representation','Detection method and discriminator','CAVER generates path candidates; the required membrane-frame endpoint review discriminates the proposed class. This alternative route is explicitly separated from published MOLE2.5 analysis.',['record','manual','PNAS','registry'])
assess('A07','representation','Input state, parameters and invocation','The executable template matches the manual. PDB directory, justified central-cavity origin, probe/shell settings, membrane placement, missing atoms and retained lipids are explicitly required context. CLI output alone is insufficient. The method is unexecuted.',['record','manual','schema'])
assess('A08','representation','Structure anchor and coordinate frame','7WLI is directly named in the computational study. Archive revision, experimental resolution, monomer/chain, partial modeling and apo qualifications match. No invented local bounds occur.',['record','RCSB','PNAS','schema'])
assess('A09','grounding','Canonical examples and qualification','Zero canonical examples and zero qualified occurrences are asserted. A source-linked whole-structure representation is allowed by the native schema and confers no protein qualification.',['record','schema','validation'])
assess('A10','graph','Chemistry, function and causal graph','No graph or chemistry/function participant is asserted. Record notes explicitly avoid inferring permeability, ligand access, selectivity or allostery from geometry. A universal mechanism is unnecessary for this class.',['record','rubric','validation'],outcome='not_applicable')
assess('A11','completeness','Discussions, datasets and optional fields','Evidence notes are relevant and actionable. Optional discussion/dataset fields and a causal graph are unnecessary. Qualified examples remain an explicit unfilled optional capability.',['record','rubric'])
assess('A12','provenance','License and attribution','PNAS CC-BY4.0, CAVER GPL3.0 and archive CC0-1.0 remain distinguished. Record CC-BY4.0 is scoped to original attributed synthesis; upstream code, prose and figures are not relicensed.',['record','PNAS','manual','wwPDB'])
assess('A13','provenance','Status and audit history','One creation event records its agent and LLM assistance. PROPOSED status is retained. Historical corpus/open-work checks are attributed to the coordinator rather than independently recertified here.',['record','owners','rubric'])
assess('A14','ownership','Maintained record inputs and emitted semantics','The actual emitted mapping exactly equals the reviewed manifest row. Future record changes belong to the maintained manifest and native writer; neither was edited by this reviewer.',['record','owners'])
assess('A15','evidence','Stable method identifiers','biotools:caver, PMID23093919, EDAM operation2406 and ECO0007669 resolve to the intended software, paper, operation and automatic computational evidence type. Their placement does not imply execution.',['registry','EDAM','ECO','record'])
checks=[]
def check(cid,name,command,summary):
    checks.append(dict(check_id=cid,name=name,status='passed',required=True,summary=summary,target_ids=[target],command=command,exit_code=0,evidence_ids=['validation']))
check('strict','Native closed strict validation','.venv/bin/python scripts/validate_strict.py --workers 1 --out research/structural-discovery-20261028/motifs/fenestration-strict.tsv '+record_path,'Independently executed: one emitted file, zero errors.')
check('grounding','Native grounding validation','.venv/bin/python scripts/validate_uniprot_grounding.py '+record_path+' --out research/structural-discovery-20261028/motifs/fenestration-grounding.tsv','Independently executed: one emitted file, zero semantic findings; no require-qualified gate or qualification claim.')
check('graphs','Native graph audit','.venv/bin/python scripts/audit_causal_graphs.py '+record_path,'Independently executed: zero graphs, errors and warnings.')
checks.append(dict(check_id='semantics',name='Maintained versus emitted semantics',status='passed',required=True,summary='Entire mapping, history and optional example/graph absence agree with the manifest.',target_ids=[target],evidence_ids=['record','owners']))
for cid,name,summary in [('detector_execution','External geometry execution','No CAVER/MOLE run, membrane-orientation assignment or automatic class call was performed; only a documented template and manual discriminator are asserted.'),('imodulondb','Expression-source adapter','Geometric class without a transcriptomic or regulator claim; iModulonDB evidence is not applicable.')]:
    checks.append(dict(check_id=cid,name=name,status='not_applicable',required=False,summary=summary,target_ids=[target],evidence_ids=['record']))
review=dict(schema_version='1.0.0',review_id=stamp+'-independent-membrane-fenestration',kind='record',repository=inspection['repository'],title='Independent scientific review of membrane-facing lateral channel fenestration',started_at='2026-10-29T07:13:59Z',finished_at=finish,reviewer=dict(identity='Codex /root/grounding_route_audit',kind='agent',model='GPT-6',independence='independent',independence_basis='Reviewer authored neither cavity proposal nor manifest/emitted record. Independently inspected published primary text, retained published PDF and archive metadata; reread every emitted field against current native rubric.'),skill='.claude/skills/review-yaml-record/SKILL.md',completion='completed',verdict='pass_with_limitations',scientific_review=True,summary='One emitted PROPOSED structural class is supported within its geometric scope, with appropriate tunnel hierarchy, source-linked whole-structure anchor and an explicitly unexecuted candidate-generation/manual-review method. Fifteen assessments; zero findings. No residue occurrence, protein qualification or universal functional mechanism is conferred.',source=inspection['source'],scope=dict(description='Entire emitted membrane-facing lateral channel fenestration record.',selection='Exact coordinator-named path and stable identifier; no sampling.',coverage='full',population_size=1,reviewed_target_ids=[target],exclusions=[dict(target='Other discovery records and corpus-wide identity/remote-work audits',reason='Outside this single-record scientific review; no broader acceptance or issue closure implied.')]),targets=inspection['targets'],checks=checks,evidence=evidence,assessments=assessments,findings=[],actions=[],limitations=['CAVER is a documented alternative candidate generator. No detector was executed, publication analysis replayed, membrane frame assigned, or local residue boundary qualified.','The published main-text description of SI FigureS1D was inspected; this review does not claim independent image-level analysis of that supplemental panel.','The 7WLI archive is only partially modeled and includes lipids/calcium. Apo is relative to the investigated inhibitors; representation does not assert a fully modeled or ligand-free channel.','A geometric class does not establish permeability, ligand access, selectivity or allostery across its members.','Qualified examples remain zero; REVIEWED human status and occurrence qualification are not conferred by this review.','Corpus collision/remote-work checks and writer implementation are coordinator-owned. This review identifies maintained owners but does not independently certify those whole-workflow gates.','Raw primary snapshots and historical downloads may remain ignored local evidence; source URLs and hashes are preserved. The PDF originally came from /tmp/nalcn-fenestration.pdf and is retained unchanged with provenance. Portable reproduction may require reacquisition and explicit byte/version checking.','Publisher HTML worked through the browser tool but direct retention returned403. Scientific inspection used the publisher text plus the same published CC-BY4 PDF; the failed retrieval is preserved in fenestration-source-retrieval.json.'],links=['research/structural-discovery-20261028/motifs/fenestration-pdf-provenance.json','research/structural-discovery-20261028/cavities/membrane-fenestration-card.json'],tags=['structural-discovery','independent-science','fenestration'])
destination=HERE/'fenestration-native-review-input.yaml'
with destination.open('x') as stream:
    yaml.safe_dump(review,stream,sort_keys=False,allow_unicode=True,width=100)
result=subprocess.run([str(ROOT/'.venv/bin/python'),'scripts/record_review.py','validate',str(destination)],cwd=ROOT,capture_output=True,text=True)
report={'timestamp':finish,'path':str(destination.relative_to(ROOT)),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'command':result.args,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
with (HERE/'fenestration-native-review-validation.json').open('x') as stream:
    json.dump(report,stream,indent=2)
    stream.write('\n')
print(json.dumps(report,indent=2))
raise SystemExit(result.returncode)
