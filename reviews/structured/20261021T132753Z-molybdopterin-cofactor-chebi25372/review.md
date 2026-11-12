# Review of requires molybdopterin cofactor

- Review: 20261021T132753Z-molybdopterin-cofactor-chebi25372
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:18:28Z
- Finished UTC: 2026-10-21T13:27:53Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The broad metal-coordinated molybdopterin class and positive Mo/W protein contexts are supported. One confirmed major concerns chemical-class-to-protein-requirement equivalence. No Mo-only restriction, fixed-structure deficit or automatic protein qualification is inferred.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 026. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) covers 248 record paths, leaving 429111 before this batch. 26 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml | generated | requires molybdopterin cofactor |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_25372 | Current nonobsolete backend/OLS resolve the broad metal-coordinated class, direct cofactor role and Mo/W member definitions. Complete primary abstracts support bounded W- and Mo-enzyme contexts. Licence and ontology metadata were verified without claiming one fixed class formula. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Broad metal-coordinated molybdopterin cofactor

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The appended definition agrees with the current broad source class. It denotes coordinated metal/metal oxide plus molybdopterin, not the free ligand and not necessarily Mo. The absence of one fixed formula, charge and structure is appropriate for this variable class.

### Molybdopterin name does not impose a Mo-only complex

nomenclature: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The source class name and copied definition preserve metal-general scope. Explicit Mo and W children and primary tungsten-enzyme chemistry prevent interpreting the name as an assertion that every member contains molybdenum. No such false assertion is added to the target review.

### Positive Mo and W enzyme cofactor contexts

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The complete primary abstracts provide real metal-coordinated protein cofactors, including archaeal W enzymes and bacterial Mo-DMSO reductase. Their ligand counts, organic forms and redox states are member-specific. The positive catalytic context is retained without universalizing one geometry or chemical state.

### Broad class versus member-specific qualification

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The generic requirement does not specify a protein, metal, ligand variant, redox state or activity. The source class and demonstrated Mo/W members support a meaningful candidate, but not all combinations or universal physiological dependence. Optional participant or canonical-example enrichment requires activity-specific evidence; a fixed structure is not mandatory for the broad class.

### Authentic cofactor role and local broader parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The direct source cofactor role explains selection and the local broader cofactor-requirement parent. Prosthetic group occurs in the definition, while the captured direct role edge is cofactor. Chemical molybdopterin ancestry and Mo/W children are not automatically local protein-trait hierarchy edges.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

CHEBI:25372 currently denotes a broad class of metal-coordinated molybdopterin cofactors, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The schema reserves xrefs for true own-source equivalence. A chemical entity or chemical class is not identical to a class of proteins requiring it, even when its identity and a positive cofactor context are supported.

### Source attribution, licence and maintained emitter

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_25372.

The inspected ChEBI seeder explains role-based candidate selection, synthesized requirement wording, any appended chemical definition, the local role-requirement parent and chemical xref. Official ChEBI data are CC BY 4.0. That chemical attribution does not independently establish the synthesized protein requirement. Current backend and OLS version 256 are comparison snapshots; the original seed release remains unknown.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-25372.chemical-entity-equivalence.

CHEBI:25372 currently denotes a broad class of metal-coordinated molybdopterin cofactors, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The schema reserves xrefs for true own-source equivalence. A chemical entity or chemical class is not identical to a class of proteins requiring it, even when its identity and a positive cofactor context are supported.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py so chemical source entities are not emitted as protein-trait equals. Preserve the metal-general class and distinguish it from free organic ligand and specific Mo/W members. Define intended activity-relative scope without forcing a Mo-only replacement, a fixed formula or a particular bound redox/coordination state. Preserve source provenance. An optional chemical_participants association with role COFACTOR is appropriate only after the chemical identity and activity-relative non-substrate role are supported; otherwise retain explicit uncertainty without inventing a participant. Do not move the same false equality to mapped_xrefs, force optional protein examples or promote native status.

- Regenerated xrefs no longer asserts equality between a chemical source entity and the protein requirement. Any identity prerequisite is resolved first, and source attribution remains traceable.
- Any optional participant uses a curator-supported chemical identity and an activity-relative role; a source role or one experiment is not converted into universal protein qualification.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml.
- For writer changes add focused regression coverage and run just audit-writers, just lint and just test. Regenerate this existing target through an audited scoped route using seed_chebi_cofactor.py and pinned inputs. emit skips existing paths unless --force is supplied and writes only with --apply; because main traverses a cohort, a broad --apply --force run is not a one-record repair. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing; reused bytes verified against original digest and access time | supports | The inspected official Introduction and Licensing sections describe chemical entities and biological roles and establish CC BY 4.0 for ChEBI data. This does not independently license or release-pin an uninspected MicroGrowAgents source table. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Original access time is retained. This ontology version and the live backend are separate comparison snapshots, not identification of the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25372/; Complete official compound response: identity, names, definition or null, chemical data, default structure, outgoing relations and relevant incoming context | supports | CHEBI:25372 is the broad molybdopterin cofactor class: a molybdopterin with a coordinated metal or metal oxide that acts as a prosthetic group. Fixed chemical data and default structure are null. Its direct role is cofactor, its chemical parent is molybdopterins, and incoming children include Mo-molybdopterin cofactor and W-molybdopterin cofactor. The definition does not require Mo exclusively. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:25372; Exact requested term: label, description, synonyms/annotations, obsolete flag and any replacement annotation | supports | Nonobsolete OLS CHEBI:25372 confirms the broad metal-coordinated prosthetic-group definition and class identity without asserting a single fixed formula, charge or structure. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 is the biochemical role cofactor: an organic molecule or ion required by an enzyme for activity, loosely or tightly attached. Its parent is biochemical role CHEBI:52206; it is not a class of proteins. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Inspected source response captured at the recorded UTC time | supports | CHEBI:52206 describes a role played by a molecular entity or part within a biochemical context. A role, the entity bearing it and a protein requirement class are distinct denotations. |
| prosthetic-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Inspected source response captured at the recorded UTC time | supports | CHEBI:26348 defines a tightly bound nonpolypeptide unit involved in protein biological activity, under cofactor. This explains the source definition terminology; it is not misreported as an additional direct has-role edge on 25372. |
| mpt-class | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35203/; Complete official compound response: identity, names, definition or null, chemical data, default structure, outgoing relations and relevant incoming context | supports | Molybdopterins CHEBI:35203 is the broader variable chemical class, with no fixed formula/structure. Its presence does not equate uncoordinated ligand with the metal-coordinated cofactor class. |
| mo-child | https://www.ebi.ac.uk/chebi/backend/api/public/compound/21437/; Complete official compound response: identity, names, definition or null, chemical data, default structure, outgoing relations and relevant incoming context | supports | CHEBI:21437 specifically defines Mo-molybdopterin cofactor by a mononuclear molybdenum or molybdate species coordinated to molybdopterin. It is a child of the reviewed broader class. |
| w-child | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60215/; Complete official compound response: identity, names, definition or null, chemical data, default structure, outgoing relations and relevant incoming context | supports | CHEBI:60215 specifically defines W-molybdopterin cofactor by a mononuclear tungsten or tungstate species coordinated to molybdopterin. It is also a child of 25372, demonstrating that the broader class is not restricted to Mo. |
| w-child-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60215; Inspected source response captured at the recorded UTC time | supports | Nonobsolete OLS CHEBI:60215 confirms the tungsten-coordinated child definition. |
| w-structure | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7878465%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected | supports | PMID:7878465; DOI:10.1126/science.7878465. The complete abstract reports a 2.3 Å Pyrococcus furiosus aldehyde ferredoxin oxidoreductase structure: each subunit contains an Fe4S4 cluster and a W cofactor, with two molybdopterin ligands coordinating W through four sulfur ligands. This gives positive tungsten-containing cofactor context, not Mo-only chemistry. |
| w-ligand-analysis | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8444863%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected | supports | PMID:8444863; DOI:10.1016/S0021-9258(18)53474-8. The complete abstract reports organic-cofactor analysis in four archaeal tungsten enzymes, identifying molybdopterin via derivatives and finding no evidence for listed nucleotide derivatives in those preparations. This supports organic ligand versus metal-cofactor distinction, not the absence of dinucleotide cofactors in all enzymes. |
| mo-structure | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8658134%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected | supports | PMID:8658134; DOI:10.1126/science.272.5268.1615. The complete abstract supplies a complementary Mo-containing DMSO-reductase context with two MGD ligands and redox-dependent coordination. It is one member context, not a single universal structure for the whole broad class. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Executed 2026-10-21T13:19:05Z through 2026-10-21T13:19:07Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Executed 2026-10-21T13:18:40Z through 2026-10-21T13:20:44Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Executed 2026-10-21T13:19:07Z through 2026-10-21T13:19:08Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:20:44Z through 2026-10-21T13:20:46Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- Primary protein chemistry was read through complete indexed abstracts. No full coordinate analysis, all-metals activity survey, universal ligand stoichiometry or new canonical protein qualification is claimed. Direct source role edges are distinguished from definition terminology and inherited class context.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T132753Z-molybdopterin-cofactor-chebi25372
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires molybdopterin cofactor
started_at: '2026-10-21T13:18:28Z'
finished_at: '2026-10-21T13:27:53Z'
reviewer:
  identity: Codex
  kind: agent
  independence: unknown
  independence_basis: Unchanged target bytes assessed against inspected primary sources
    and repository rules, with independent source-acquisition and scope checks. Prior
    authorship independence is not established; this is not human sign-off.
skill: .claude/skills/review-yaml-record/SKILL.md
completion: completed
verdict: needs_curation
scientific_review: true
summary: The broad metal-coordinated molybdopterin class and positive Mo/W protein
  contexts are supported. One confirmed major concerns chemical-class-to-protein-requirement
  equivalence. No Mo-only restriction, fixed-structure deficit or automatic protein
  qualification is inferred.
source:
  git_revision: 6cbcac34bb17f44ea7516dd3308d890367014e2b
  state: working_tree
  inputs:
  - path: .claude/skills/curate-yaml-record/references/review-checklist.md
    sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
    role: context
  - path: .claude/skills/review-yaml-record/SKILL.md
    sha256: ac1094d8aef512845dbe56ee041e62e62aeeed32326578ff3f7dd8455495f303
    role: context
  - path: CLAUDE.md
    sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
    role: context
  - path: LICENSE
    sha256: d920683ada4ab4646467cbe49944e08172d8f10c92ce3e631d6f3460b4b40a52
    role: context
  - path: LICENSE-DATA
    sha256: 9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94
    role: context
  - path: conf/record_review.yaml
    sha256: d3fd2e272546bf2505ded4ef86f7340753c4e422c691bd69f8e79f577b2c5f59
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
    sha256: b36424b24e3bc41a2d3ef82928542c19199aa88565e51a0094c3ff42bbdd5338
    role: target
  - path: docs/fetch-migration.md
    sha256: 11718531ccc1346002cfafbe62e8cfdc3859271ded178c34a17e26dabc70b55c
    role: context
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: download.yaml
    sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
    role: context
  - path: history/README.md
    sha256: db3db1da49f08244c863689856f31bc764aadb6e629b25aff45b3b4598dbef2c
    role: context
  - path: justfile
    sha256: 090b16ab565dbc137f589ab913e57efac5cb37bb7511547391267ba6ea96dd5b
    role: context
  - path: schema/record_review.yaml
    sha256: 229baf9b69118a1fe318e4c31085c0820e4e3d1365e7b04d6ace451b7c35f9bb
    role: context
  - path: scripts/build_docs_index.py
    sha256: 926f593f6d3c81b16ff72148f1777d0b6d81cabe5fe806f4667c5745f28bb818
    role: context
  - path: scripts/seed_chebi_cofactor.py
    sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 10 in batch 026. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87;
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df;
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242;
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98)
    covers 248 record paths, leaving 429111 before this batch. 26 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
targets:
- kind: generated
  label: requires molybdopterin cofactor
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_25372
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml
    data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml
    data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml
    data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml
    data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml
    data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml
    data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  evidence_ids:
  - validation-3
- check_id: gate-4
  name: Curation history validity
  command: just validate-history
  exit_code: 0
  status: passed
  required: true
  summary: Full curation-history gate; this review adds no history event.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current nonobsolete backend/OLS resolve the broad metal-coordinated class,
    direct cofactor role and Mo/W member definitions. Complete primary abstracts support
    bounded W- and Mo-enzyme contexts. Licence and ontology metadata were verified
    without claiming one fixed class formula.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:18:28Z'
  snapshot_sha256: b36424b24e3bc41a2d3ef82928542c19199aa88565e51a0094c3ff42bbdd5338
  support: supports
  summary: Complete YAML inspected, including local protein-requirement identifier
    and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT,
    CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence.
    No optional examples, causal graphs, qualified protein assertions or chemical_participants
    occur in this target YAML.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T13:18:28Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required
    for activity. xrefs asserts true own-source equivalence; chemical_participants
    represents chemical entities with typed roles. parent_traits asserts a broader
    class. Optional examples and causal graphs are not mandatory class representations.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_chebi_cofactor.py
  locator: load_relations, load_names, build, main
  accessed_at: '2026-10-21T13:18:28Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: load_relations selects cofactor-role descendants and molecules with has_role;
    build synthesizes a protein-requirement label/definition, appends chemical source
    text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects
    one role-parent. The source chemical class and the synthesized requirement trait
    have different denotations.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T13:18:28Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:18:28Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Introduction and Licensing; reused bytes verified against original digest
    and access time
  summary: The inspected official Introduction and Licensing sections describe chemical
    entities and biological roles and establish CC BY 4.0 for ChEBI data. This does
    not independently license or release-pin an uninspected MicroGrowAgents source
    table.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Original access time is retained. This ontology version and the live backend are
    separate comparison snapshots, not identification of the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25372/
  accessed_at: '2026-10-21T13:19:05.013341Z'
  snapshot_sha256: 8d58fc2f21311f17b4478728f24c3e2e864906c8d99cb833d93a3e32d26164bf
  support: supports
  locator: 'Complete official compound response: identity, names, definition or null,
    chemical data, default structure, outgoing relations and relevant incoming context'
  summary: 'CHEBI:25372 is the broad molybdopterin cofactor class: a molybdopterin
    with a coordinated metal or metal oxide that acts as a prosthetic group. Fixed
    chemical data and default structure are null. Its direct role is cofactor, its
    chemical parent is molybdopterins, and incoming children include Mo-molybdopterin
    cofactor and W-molybdopterin cofactor. The definition does not require Mo exclusively.'
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:25372
  accessed_at: '2026-10-21T13:19:05.122918Z'
  snapshot_sha256: 9a9d5fa34b60216e2926a27ac8106659c0e1c502625cc90d7bee2db8662e1ee1
  support: supports
  locator: 'Exact requested term: label, description, synonyms/annotations, obsolete
    flag and any replacement annotation'
  summary: Nonobsolete OLS CHEBI:25372 confirms the broad metal-coordinated prosthetic-group
    definition and class identity without asserting a single fixed formula, charge
    or structure.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: 'CHEBI:23357 is the biochemical role cofactor: an organic molecule or ion
    required by an enzyme for activity, loosely or tightly attached. Its parent is
    biochemical role CHEBI:52206; it is not a class of proteins.'
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:52206 describes a role played by a molecular entity or part within
    a biochemical context. A role, the entity bearing it and a protein requirement
    class are distinct denotations.
- evidence_id: prosthetic-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:10:09.154369Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:26348 defines a tightly bound nonpolypeptide unit involved in protein
    biological activity, under cofactor. This explains the source definition terminology;
    it is not misreported as an additional direct has-role edge on 25372.
- evidence_id: mpt-class
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35203/
  accessed_at: '2026-10-21T13:20:09.169397Z'
  snapshot_sha256: e057ddba994c479c597941108a7353e842ab2a84cb03b510b326c60808015a4f
  support: supports
  locator: 'Complete official compound response: identity, names, definition or null,
    chemical data, default structure, outgoing relations and relevant incoming context'
  summary: Molybdopterins CHEBI:35203 is the broader variable chemical class, with
    no fixed formula/structure. Its presence does not equate uncoordinated ligand
    with the metal-coordinated cofactor class.
- evidence_id: mo-child
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/21437/
  accessed_at: '2026-10-21T13:20:09.761102Z'
  snapshot_sha256: d9ba9ee42920d9b89ad37fa13bb5a1a3b3d03e9a7dc36d2200d7f7522d416530
  support: supports
  locator: 'Complete official compound response: identity, names, definition or null,
    chemical data, default structure, outgoing relations and relevant incoming context'
  summary: CHEBI:21437 specifically defines Mo-molybdopterin cofactor by a mononuclear
    molybdenum or molybdate species coordinated to molybdopterin. It is a child of
    the reviewed broader class.
- evidence_id: w-child
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60215/
  accessed_at: '2026-10-21T13:20:09.847982Z'
  snapshot_sha256: 99d61da20563087876614a2d8ec380613963ebccaa04efa46571704127130eba
  support: supports
  locator: 'Complete official compound response: identity, names, definition or null,
    chemical data, default structure, outgoing relations and relevant incoming context'
  summary: CHEBI:60215 specifically defines W-molybdopterin cofactor by a mononuclear
    tungsten or tungstate species coordinated to molybdopterin. It is also a child
    of 25372, demonstrating that the broader class is not restricted to Mo.
- evidence_id: w-child-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60215
  accessed_at: '2026-10-21T13:20:10.461106Z'
  snapshot_sha256: 24791ba7039bcc45f1430d674b8d28ba2cabe04386810601b08ab37951bb9e1e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete OLS CHEBI:60215 confirms the tungsten-coordinated child definition.
- evidence_id: w-structure
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7878465%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T13:20:11.101726Z'
  snapshot_sha256: c77098d7dcc03bbbc7bdde6001717df779cd7ee9143f7953dd0618101daf7c95
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected
  summary: 'PMID:7878465; DOI:10.1126/science.7878465. The complete abstract reports
    a 2.3 Å Pyrococcus furiosus aldehyde ferredoxin oxidoreductase structure: each
    subunit contains an Fe4S4 cluster and a W cofactor, with two molybdopterin ligands
    coordinating W through four sulfur ligands. This gives positive tungsten-containing
    cofactor context, not Mo-only chemistry.'
- evidence_id: w-ligand-analysis
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8444863%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T13:20:11.112181Z'
  snapshot_sha256: 3ca34d6650368204deb8312a7189bb1da1678832fa7507e27ddf3740fb9bb320
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected
  summary: PMID:8444863; DOI:10.1016/S0021-9258(18)53474-8. The complete abstract
    reports organic-cofactor analysis in four archaeal tungsten enzymes, identifying
    molybdopterin via derivatives and finding no evidence for listed nucleotide derivatives
    in those preparations. This supports organic ligand versus metal-cofactor distinction,
    not the absence of dinucleotide cofactors in all enzymes.
- evidence_id: mo-structure
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8658134%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T13:22:28.446680Z'
  snapshot_sha256: 96b32c7ed9f63d0365b4c804839ce6b54efc0b28f896197dca2160027bb1525e
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected
  summary: PMID:8658134; DOI:10.1126/science.272.5268.1615. The complete abstract
    supplies a complementary Mo-containing DMSO-reductase context with two MGD ligands
    and redox-dependent coordination. It is one member context, not a single universal
    structure for the whole broad class.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  locator: Executed 2026-10-21T13:19:05Z through 2026-10-21T13:19:07Z; exit 0
  accessed_at: '2026-10-21T13:19:07Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml
    data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml
    data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml
    data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml
    data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml
    data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml
    data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  locator: Executed 2026-10-21T13:18:40Z through 2026-10-21T13:20:44Z; exit 0
  accessed_at: '2026-10-21T13:20:44Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  locator: Executed 2026-10-21T13:19:07Z through 2026-10-21T13:19:08Z; exit 0
  accessed_at: '2026-10-21T13:19:08Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T13:20:44Z through 2026-10-21T13:20:46Z; exit 0
  accessed_at: '2026-10-21T13:20:46Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: scripts/seed_chebi_cofactor.py owns generated target changes. Its source
    transformation is inspected; no emitted record has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable requirement
    class rather than a protein instance. Optional examples, sequence/structure representations
    and mechanisms are not automatically required; none are newly qualified.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The appended definition agrees with the current broad source class. It
    denotes coordinated metal/metal oxide plus molybdopterin, not the free ligand
    and not necessarily Mo. The absence of one fixed formula, charge and structure
    is appropriate for this variable class.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - mpt-class
  - mo-child
  - w-child
  - w-child-ontology
  topic: Broad metal-coordinated molybdopterin cofactor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-5
- area: nomenclature
  outcome: supported
  summary: The source class name and copied definition preserve metal-general scope.
    Explicit Mo and W children and primary tungsten-enzyme chemistry prevent interpreting
    the name as an assertion that every member contains molybdenum. No such false
    assertion is added to the target review.
  evidence_ids:
  - record
  - chemical
  - mo-child
  - w-child
  - w-structure
  topic: Molybdopterin name does not impose a Mo-only complex
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The complete primary abstracts provide real metal-coordinated protein cofactors,
    including archaeal W enzymes and bacterial Mo-DMSO reductase. Their ligand counts,
    organic forms and redox states are member-specific. The positive catalytic context
    is retained without universalizing one geometry or chemical state.
  evidence_ids:
  - w-structure
  - w-ligand-analysis
  - mo-structure
  topic: Positive Mo and W enzyme cofactor contexts
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The generic requirement does not specify a protein, metal, ligand variant,
    redox state or activity. The source class and demonstrated Mo/W members support
    a meaningful candidate, but not all combinations or universal physiological dependence.
    Optional participant or canonical-example enrichment requires activity-specific
    evidence; a fixed structure is not mandatory for the broad class.
  evidence_ids:
  - record
  - schema
  - chemical
  - mo-child
  - w-child
  - w-structure
  - mo-structure
  topic: Broad class versus member-specific qualification
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct source cofactor role explains selection and the local broader
    cofactor-requirement parent. Prosthetic group occurs in the definition, while
    the captured direct role edge is cofactor. Chemical molybdopterin ancestry and
    Mo/W children are not automatically local protein-trait hierarchy edges.
  evidence_ids:
  - chemical
  - owner
  - cofactor-role
  - prosthetic-role
  - local-parent-1
  - mpt-class
  - mo-child
  - w-child
  topic: Authentic cofactor role and local broader parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: CHEBI:25372 currently denotes a broad class of metal-coordinated molybdopterin
    cofactors, whereas the local COFACTOR_REQ record denotes a proposed protein functional
    requirement. The schema reserves xrefs for true own-source equivalence. A chemical
    entity or chemical class is not identical to a class of proteins requiring it,
    even when its identity and a positive cofactor context are supported.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - w-structure
  - mo-structure
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-10
- area: provenance
  outcome: supported
  summary: The inspected ChEBI seeder explains role-based candidate selection, synthesized
    requirement wording, any appended chemical definition, the local role-requirement
    parent and chemical xref. Official ChEBI data are CC BY 4.0. That chemical attribution
    does not independently establish the synthesized protein requirement. Current
    backend and OLS version 256 are comparison snapshots; the original seed release
    remains unknown.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  topic: Source attribution, licence and maintained emitter
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-25372.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:25372 currently denotes a broad class of metal-coordinated molybdopterin
    cofactors, whereas the local COFACTOR_REQ record denotes a proposed protein functional
    requirement. The schema reserves xrefs for true own-source equivalence. A chemical
    entity or chemical class is not identical to a class of proteins requiring it,
    even when its identity and a positive cofactor context are supported.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - w-structure
  - mo-structure
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The entity-to-trait type mismatch is an independently repairable
    major grounding defect. It does not require proving that the chemical lacks biological
    activity or that optional examples must be present.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py so chemical source entities
    are not emitted as protein-trait equals. Preserve the metal-general class and
    distinguish it from free organic ligand and specific Mo/W members. Define intended
    activity-relative scope without forcing a Mo-only replacement, a fixed formula
    or a particular bound redox/coordination state. Preserve source provenance. An
    optional chemical_participants association with role COFACTOR is appropriate only
    after the chemical identity and activity-relative non-substrate role are supported;
    otherwise retain explicit uncertainty without inventing a participant. Do not
    move the same false equality to mapped_xrefs, force optional protein examples
    or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_25372
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Regenerated xrefs no longer asserts equality between a chemical source entity
    and the protein requirement. Any identity prerequisite is resolved first, and
    source attribution remains traceable.
  - Any optional participant uses a curator-supported chemical identity and an activity-relative
    role; a source role or one experiment is not converted into universal protein
    qualification.
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml.
  - For writer changes add focused regression coverage and run just audit-writers,
    just lint and just test. Regenerate this existing target through an audited scoped
    route using seed_chebi_cofactor.py and pinned inputs. emit skips existing paths
    unless --force is supplied and writes only with --apply; because main traverses
    a cohort, a broad --apply --force run is not a one-record repair. Run full just
    validate-all before merging record changes; recapture changed inputs and save
    a fresh structured review without overwriting this observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that
  a particular protein requires that chemical, that every related protein does, or
  that the chemical is an obligatory physiological cofactor. No such per-protein qualification
  is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- Primary protein chemistry was read through complete indexed abstracts. No full coordinate
  analysis, all-metals activity survey, universal ligand stoichiometry or new canonical
  protein qualification is claimed. Direct source role edges are distinguished from
  definition terminology and inherited class context.
tags:
- unreviewed-path-order
- batch-026
- chebi-cofactor
```
