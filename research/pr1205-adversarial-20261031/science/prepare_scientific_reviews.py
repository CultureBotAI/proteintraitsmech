#!/usr/bin/env python3
"""PR #1205; 2026-10-31. Author three exact-head native scientific review inputs.
Inputs: capture_science_context.py outputs, complete historical target bytes,
maintained manifest, schema/rubric and primary artifacts; reviewer judgements below
reflect fresh primary text/official webpage checks on 2026-10-31.
Outputs: three new *-review-input.yaml documents and validation JSON here only.
No record edits, historical-review rewrites, Git mutations, detector runs or save.
Beta-arch explicitly self_review because this reviewer researched that candidate.
"""
import datetime, hashlib, json, os, pathlib, subprocess
import yaml
ROOT=pathlib.Path.cwd(); OUT=pathlib.Path(__file__).resolve().parent; REL=OUT.relative_to(ROOT)
BASE='bc0c6d97aaab0ba20fcf8be28bc1527430679ccb'; ENV=dict(os.environ,GIT_NO_LAZY_FETCH='1')
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); stamp=now.replace('-','').replace(':','')
checks=json.loads((OUT/'native-check-results.json').read_text()); assert all(x['exit_code']==0 for x in checks)
pins=json.loads((OUT/'historical-pins.json').read_text()); pins_by_path={x['path']:x for x in pins['inputs']}
sem=json.loads((OUT/'emitted-semantics.json').read_text()); assert all(x['manifest_mapping_equal'] for x in sem)
def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
D='research/structural-discovery-20261028/motifs/'
config={
'beta-arch':{
'primary_url':'https://www.nature.com/articles/s41467-022-33004-6','primary_file':D+'natcomm-2022-immunoglobulin.xml','primary_locator':'Methods: Structural analysis of beta-arch loops; dIG8-CC characterization; Figure5 caption; Data availability; permissions',
'primary_summary':'Retained full primary XML reread after direct publisher access failed. Nonpaired flanking strands distinguish the motif. Sampling length is not a universal boundary. The engineered construct supports the representative; the Figure5c accession discrepancy is preserved in the record. Source permissions specify CC-BY-4.0.',
'pdb':'7SKO','pdb_summary':'Current RCSB confirms synthetic dIG8-CC, X-ray 2.05 angstrom, chains A-D, dimer assemblies and version1.2 revised2024-11-13. No residue occurrence is deposited by this review.',
'identity':'The local identifier, beta-arch label and exact aliases denote a supersecondary topology, not an immunoglobulin fold or all strand connectors. The absence of pairing is essential and explicitly retained.',
'placement':'STRUCTURE / STRUCT_SECONDARY and parent SUPER_SECONDARY_MOTIF fit a small connected arrangement. The connector may include a helix; the definition does not restrict it to a short unstructured loop.',
'relations':'The native parent exists and is broader. No exact external CURIE, domain/family identity or hairpin equivalence is asserted. The explicit nonpairing distinction prevents conflating this motif with a beta hairpin.',
'method':'The classic DSSP command is valid in installed mkdssp4.6.1. Connectivity and flanking-strand hydrogen-bond checks require the stated manual review; the executable alone does not classify beta arches. Missing backbone and chain breaks remain unresolved.',
'representation':'The TOPOLOGY value is an element-level representation rather than a residue string. 7SKO is supported by deposition identity and primary characterization; the record notices the misleading Figure5c 7SKP caption and does not derive coordinates from it.',
'rights':'Project-authored synthesis and the primary article are scoped separately. The article grants CC-BY-4.0; official DSSP LICENSE is BSD-2-Clause; wwPDB archive metadata are CC0-1.0. No restrictive-source prose/figure/code is imported into the trait.',
'limitation':'Prior candidate-research authorship makes this a self-review with partial independence. The coordinator must use a different reviewer for an independent beta-arch decision.',
'category':'STRUCT_SECONDARY','parent':'data/traits/structure/secondary/super-secondary-motif.yaml'},
'tunnel-bottleneck':{
'primary_url':'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002708','primary_file':D+'caver2012-plos-primary.html','primary_locator':'Design and Implementation section3; static analysis and Figure4; copyright notice',
'primary_summary':'Fresh publisher text and retained HTML inspected. A pathway minimum determines the bottleneck. Figure4/static analysis uses a hydrogen-added 1CQW model. The publisher copyright is CC-BY without an explicit version.',
'pdb':'1CQW','pdb_summary':'Current RCSB confirms DhaA chainA, author monomer, X-ray1.50angstrom and version1.4 revised2024-02-07. This is a sodium-iodide cocrystal and whole input anchor, not a deposited bottleneck annotation.',
'identity':'The identifier denotes a minimum-radius region of a specified path and coordinate/geometric model. A generic constriction can be merely local, so its BROAD synonym is appropriate. Neither the whole tunnel nor a numeric radius measurement is substituted for the region.',
'placement':'STRUCTURE / STRUCT_CAVITY fits the spatial region. CLASS and PROPOSED are appropriate; absence of a fabricated subclass parent is intentional.',
'relations':'biolink:part_of TUNNEL correctly distinguishes a path region from the entire tunnel. The native target exists. A catalytic-site channeling tunnel can contain a bottleneck but does not denote the same class.',
'method':'The manual supports the package-relative Java invocation and PDB-directory input. Starting point, probe/shell, atom treatment and seed are explicit prerequisites. compute_bottleneck_residues produces distance-based nearby residues; it does not define an intrinsic sequence interval.',
'representation':'The representation is tied to the paper calculation and whole PDB model. The deposited structure is not claimed to be the hydrogen-added analysis input itself. Alternative/tied minima remain model-sensitive; no local bounds or functional transport evidence is invented.',
'rights':'The record scopes CC-BY-4.0 to project-authored synthesis. The PLOS article has version-unspecified CC-BY, CAVER software/manual GPL-3.0, and archive data CC0-1.0. These grants are not conflated.',
'limitation':'The representative is an input to published geometry; no local CAVER output, bound residue set, physical permeability or qualified protein occurrence was produced.',
'category':'STRUCT_CAVITY','parent':'data/traits/structure/cavity/tunnel.yaml'},
'membrane-facing-channel-fenestration':{
'primary_url':'https://www.pnas.org/doi/10.1073/pnas.2401591121','primary_file':D+'fenestration-pnas-published.txt','primary_locator':'Published Results comparing apo6UZ3/7WLI; MOLE2.5 Methods; first-page license notice',
'primary_summary':'Published article reread through initial publisher access and retained full text. 7WLI is explicitly analyzed. The method filters computed paths for central-cavity starts and membrane-parallel direction. The notice grants CC-BY-4.0.',
'pdb':'7WLI','pdb_summary':'Current RCSB confirms human CaV3.3 chainA, author monomer, cryoEM3.30angstrom, version1.2 revised2024-10-30 and1135/2223 residues modeled. Apo is relative to the investigated inhibitors; lipids/calcium remain.',
'identity':'The class is a lateral passage through a channel wall to the membrane-facing exterior. It is distinct from the principal permeation path, a cellular fenestra, and a generic opening. BROAD lateral-fenestration synonym preserves this narrower scope.',
'placement':'STRUCTURE / STRUCT_CAVITY follows passage geometry. A lateral connection from internal channel cavity to exterior is compatible with native TUNNEL parent semantics.',
'relations':'TUNNEL is a valid broader class. The enclosed hydration microcavity lacks direct exterior tunnel access; catalytic intermediate-channeling connects active sites and asserts function. Neither new main class is identical to this membrane-facing passage.',
'method':'CAVER is clearly an alternative candidate generator, not a replay of the source MOLE2.5 pipeline. Explicit membrane-frame endpoint review discriminates lateral paths from aqueous mouths/main pore. Starting point, missing atoms and retained lipids require a stated model.',
'representation':'7WLI is an explicitly published whole-model analysis anchor, not a qualified local feature. Revision, assembly and incomplete modeling are disclosed. Geometry alone is not presented as proof of drug transit, selectivity, allostery or permeability.',
'rights':'The first-page published notice grants CC-BY-4.0. Project synthesis, GPL-3.0 CAVER/software documentation and CC0-1.0 archive metadata remain separately scoped; no imported source figure/code is relabeled.',
'limitation':'Supplemental FigureS1D image was not independently inspected. Published main-text Methods/Results support the limited whole-structure anchor; no width, path coordinates or local residue boundary is asserted.',
'category':'STRUCT_CAVITY','parent':'data/traits/structure/cavity/tunnel.yaml'}}
outputs=[]
for slug,c in config.items():
 inspection=json.loads((OUT/(slug+'-inspection.json')).read_text()); target=inspection['targets'][0]; tid=target['target_id']; path=target['path']
 source=inspection['source']; source['state']='git_commit'; source['git_revision']=BASE
 for item in source['inputs']:
  assert item['sha256']==pins_by_path[item['path']]['sha256']
  hist=subprocess.run(['git','show',BASE+':'+item['path']],capture_output=True,env=ENV,check=True).stdout
  assert hashlib.sha256(hist).hexdigest()==item['sha256']
 evidence=[]
 def ev(eid,kind,reference,locator,summary,snapshot=None,support='supports'):
  x=dict(evidence_id=eid,kind=kind,reference=reference,locator=locator,accessed_at=now,support=support,summary=summary)
  if snapshot:x['snapshot_sha256']=snapshot
  evidence.append(x)
 ev('record','record_content',path,'Full record at '+BASE,'All fields and maintained manifest row read; parsed contents agree, with PROPOSED status, zero canonical examples and zero causal graphs.',pins_by_path[path]['sha256'])
 ev('native','authority','.claude/skills/curate-yaml-record/references/review-checklist.md','All ten areas, with current schema and review profile','Applied full native rubric; DetectionMethod.recipe is documented template, and representative geometry need not assert a residue range.',pins_by_path['.claude/skills/curate-yaml-record/references/review-checklist.md']['sha256'])
 ev('parent','record_content',c['parent'],'Full native parent definition and identity','Broader native structural class read to test subtype versus part semantics.',pins_by_path[c['parent']]['sha256'])
 ev('primary','primary_source',c['primary_url'],c['primary_locator'],c['primary_summary'],pins_by_path[c['primary_file']]['sha256'])
 ev('pdb','database','https://www.rcsb.org/structure/'+c['pdb'],'Current entry identity, assembly, revision, experimental and ligand fields',c['pdb_summary'])
 ev('rights','authority','https://www.wwpdb.org/about/usage-policies','wwPDB archive-data terms','Archive data are CC0-1.0; this does not relicense journal articles or external software.')
 ev('gates','validation',str(REL/'native-check-results.json'),'All actual commands, exit statuses and linked complete logs','Strict schema, grounding and graph checks independently executed on the three unchanged historical target byte sets; all exited0.',sha(REL/'native-check-results.json'))
 ev('ownership','record_content','data/curation/structural_trait_discovery.yaml','Exact target row and scripts/seed_structural_discovery.py','Maintained row equals emitted mapping. Future scientific content fixes belong to the manifest; writer implementation review is outside this science assessment.',pins_by_path['data/curation/structural_trait_discovery.yaml']['sha256'])
 ev('identity_search','search',str(REL/'identity-scan.json'),'Bounded lexical screen with full retained hits','Ignored-inclusive local clone search and manual discrimination of identity hits; not an exhaustive external ontology or inaccessible staging absence claim.',sha(REL/'identity-scan.json'))
 ev('eco','authority','https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo','ECO:0007669 stanza','Official class is computational evidence used in automatic assertion; used here as detector evidence type, not proof of an execution.')
 if slug=='beta-arch':
  ev('tool','authority','https://raw.githubusercontent.com/PDB-REDO/dssp/trunk/doc/mkdssp.1','Command syntax, classic dssp output; local version/help logs','Official manual and installed mkdssp4.6.1 agree on the documented CLI; no structure run was performed.')
  ev('tool_license','authority','https://raw.githubusercontent.com/PDB-REDO/dssp/trunk/LICENSE','Full license notice','DSSP upstream license is BSD-2-Clause.')
 else:
  ev('tool','primary_source','https://www.caver.cz/fil/download/manual/caver_userguide.pdf','Package layout/CLI pages5-7; start/probe; bottleneck options and output tables','Official manual rechecked, including package layout. caver.jar and lib are under package home; the recipe is valid. This inspection is not an execution.',pins_by_path[D+'caver-discovery-userguide.pdf']['sha256'])
  ev('tool_identity','database','https://bio.tools/api/tool/caver/?format=json','Committed primary registry response reread: CURIE, publication, version, license','Retained registry identifies CAVER and PMID23093919 with GPL-3.0; listed3.02 does not imply execution of a specific release.',pins_by_path[D+'caver-biotools-registry.json']['sha256'])
  ev('edam','authority','https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl','operation_2406 class','Official operation denotes protein structure analysis and fits computed pathway geometry.')
  ev('adjacent','record_content','https://github.com/CultureBotAI/proteintraitsmech/tree/c0d87f89e18a1c4a09904a835cf782d84d9d53d1/data/traits/structure/cavity','internal-buried-hydration-packing-microcavity.yaml and intramolecular-substrate-channeling-tunnel.yaml; local hashes in adjacent-main-context.json','Two newer main classes read only to distinguish identities. This context is outside the historical target tree and is not a scientific endorsement of those records.')
 assessments=[]
 def assess(area,topic,summary,ids,outcome='supported'):
  assessments.append(dict(assessment_id='A%02d'%(len(assessments)+1),area=area,topic=topic,outcome=outcome,summary=summary,target_ids=[tid],evidence_ids=ids))
 assess('identity','Identifier, label, source definition and synonyms',c['identity'],['record','primary','identity_search'])
 assess('scope','Axis, category and defining representation',c['placement'],['record','primary','native','parent'])
 assess('consistency','Parents, relations, equivalence and neighboring identities',c['relations'],['record','parent','primary']+([] if slug=='beta-arch' else ['adjacent']))
 assess('representation','Executable method and discrimination limits',c['method'],['record','tool','native','eco'])
 assess('representation','Topology/geometry and representative structure',c['representation'],['record','pdb','primary','native'])
 assess('grounding','Examples and qualification','No canonical protein example, release-pinned occurrence or local residue coordinate is asserted. Whole-structure references remain explicitly limited representative anchors; the default grounding pass does not confer qualification.',['record','pdb','gates'])
 assess('graph','Chemistry/function and causal mechanism','No chemistry participants, reactions or causal graph are asserted. The class scope does not require inventing a universal mechanism.',['record','native','gates'],'not_applicable')
 assess('provenance','Source-specific rights and reuse',c['rights'],['record','primary','rights','tool']+(['tool_license'] if slug=='beta-arch' else []))
 assess('completeness','Durable discussions, datasets and remaining gaps','Evidence notes retain actionable limits. Optional discussions/datasets are not required for this proposed class; missing occurrence qualification is explicit rather than concealed.',['record','native'])
 assess('ownership','Status, history and maintained content','PROPOSED and model assistance are explicit. History makes no human sign-off claim. Maintained row equals emitted record. This review does not promote status, append a curation event or certify writer implementation.',['record','ownership','gates'])
 check_items=[]
 for key,label in [('strict','Native strict schema/semantic validation'),('grounding','Native grounding validation'),('graphs','Native causal graph audit')]:
  x=next(x for x in checks if x['log'].endswith('/'+key+'.log'))
  check_items.append(dict(check_id=key,name=label,status='passed',required=True,summary='Actual three-target run exited0; this review covers only the named target. No qualified-example requirement is claimed.',target_ids=[tid],command=x['command'],exit_code=x['exit_code'],evidence_ids=['gates']))
 check_items.append(dict(check_id='historical_input_identity',name='Tracked historical bytes and emitted semantics',status='passed',required=True,summary='Each native-inspected input hash was independently compared with git show at the stated commit; target equals its maintained manifest row.',target_ids=[tid],evidence_ids=['record','ownership']))
 check_items.append(dict(check_id='external_structure_run',name='External structure detection execution',status='not_applicable',required=False,summary='Only documented recipes and source evidence are reviewed; no CAVER/MOLE/DSSP structure analysis was performed.',target_ids=[tid],evidence_ids=['record','tool']))
 report=dict(schema_version='1.0.0',review_id=stamp+'-pr1205-science-'+slug,kind='record',repository='CultureBotAI/proteintraitsmech',title='Adversarial scientific review of '+target['label']+' at bc0c6d97',started_at='2026-10-31T20:40:38Z',finished_at=now,reviewer=dict(identity='Codex /root/grounding_route_audit',kind='agent',model='GPT-6',independence='self_review' if slug=='beta-arch' else 'independent',independence_basis='Previously researched beta-arch candidate but did not author emitted record/manifest/writer; fresh source cross-check is partially independent, not an independent-author review.' if slug=='beta-arch' else 'Authored neither cavity candidate nor maintained row/emitted record/writer. Prior October29 review is not treated as proof; fresh primary, native and archive checks performed.'),skill='.claude/skills/review-yaml-record/SKILL.md',completion='completed',verdict='pass_with_limitations',scientific_review=True,summary='No actionable scientific defect found in this complete historical record. Definition, relations, source-specific rights and bounded representative/detection claims are supported. No occurrence qualification, detector execution or human REVIEWED status is conferred.',source=source,scope=dict(description='Complete single record at historical PR head '+BASE+'; fresh primary checks and native ten-area rubric. This is not a current-working-tree or later-head review.',selection='Exact coordinator-named PR1205 target; no sampling.',coverage='full',population_size=1,reviewed_target_ids=[tid],exclusions=[dict(target='Other records, writer implementation, whole-corpus novelty and later feature heads',reason='Outside the scientific target; lexical/context checks do not certify those surfaces.')]),targets=[target],checks=check_items,evidence=evidence,assessments=assessments,findings=[],actions=[],limitations=[c['limitation'],'No structure coordinates were downloaded or analyzed and no canonical example was promoted. Documentation and source-linked whole-structure anchors are distinct from executed detection and qualified occurrences.','Ignored-inclusive search covers the isolated clone only, not inaccessible original-workspace ignored staging or all external ontology terms. Root owns complete collision/open-work coordination.','Historical input hashes are checked against bc0c6d97. Current main neighboring records are boundary context only; final merge-head scientific-byte equivalence is coordinator-owned.','Prior native observations are preserved unchanged. This clean observation does not close any prior issue or certify unrelated fields/records.'],tags=['pr1205','adversarial-science','historical-exact-head'])
 dest=OUT/(slug+'-review-input.yaml')
 if dest.exists():raise SystemExit('Refusing overwrite '+str(dest))
 dest.write_text(yaml.safe_dump(report,sort_keys=False,allow_unicode=True,width=110))
 outputs.append(str(dest.relative_to(ROOT)))
p=subprocess.run(['.venv/bin/python','scripts/record_review.py','validate',*outputs],capture_output=True,text=True,env=ENV)
(OUT/'review-input-validation.json').write_text(json.dumps({'command':['.venv/bin/python','scripts/record_review.py','validate',*outputs],'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timestamp':now},indent=2)+'\n')
print(json.dumps({'outputs':outputs,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}))
raise SystemExit(p.returncode)
