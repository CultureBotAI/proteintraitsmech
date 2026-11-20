# Review of requires hydrogencarbonate

- Review: 20261021T125510Z-hydrogencarbonate-chebi17544
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:45:39Z
- Finished UTC: 2026-10-21T12:55:10Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Hydrogencarbonate identity and positive PSII ligand/regulatory context are supported. One confirmed major finding concerns chemical-to-protein-requirement equivalence. Exact activity dependence remains bounded; no universal absence or indispensability is inferred.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 024. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242) covers 228 record paths, leaving 429131 before this batch. 24 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml | generated | requires hydrogencarbonate |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17544 | Official backend and nonobsolete OLS identity, conjugate states, source cofactor role and licence resolve. Three complete primary abstracts support and bound the PSII context. The source-parent wording is preserved as a limitation, not certified as an exhaustive hierarchy. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Hydrogencarbonate identity and acid-base state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The target label and copied chemical definition resolve to the monoanion HCO3−, not neutral carbonic acid or carbonate(2−). Explicit structure and conjugate relations support this distinction. The source parent uses narrower literal wording than its own hydrogen-containing child; this does not make the target an unidentified ion.

### Bicarbonate as a PSII iron ligand and functional regulator

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The isotope-sensitive FTIR study supports bicarbonate specifically at the non-heme iron. Independent electrochemical work demonstrates functional redox tuning. The donor-side depletion study prevents importing a universal water-oxidation requirement or complete inactivity claim. These are positive bounded protein-complex contexts, not newly qualified canonical protein examples.

### Activity-specific bicarbonate requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

Positive binding and regulatory evidence is retained, but this generic record does not specify a protein, activity, assay conditions or the strength of dependence. The evidence does not justify every bicarbonate-associated protein or universal absolute dependence. Optional examples and participants are not mandatory repairs.

### Source cofactor role and local broader parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The direct chemical cofactor role and local cofactor-requirement parent explain source-driven selection. Parent resolution does not independently establish true equivalence or certify all parent wording and members.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

CHEBI:17544 denotes the hydrogencarbonate monoanion, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Accurate source identity and an authentic source role do not make the chemical entity identical to the protein requirement class.

### Source attribution, licence and maintained emitter

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17544.

The captured ChEBI seeder explains the synthesized requirement prefix, appended chemical text, role-derived parent and emitted chemical xref. The official licence is CC BY 4.0. The source chemical statement is attributable to ChEBI; the protein-requirement transformation is local and is not independently supplied by that attribution. Live backend and OLS version 256 are retained as comparison snapshots, with the original seed release unknown.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17544.chemical-entity-equivalence.

CHEBI:17544 denotes the hydrogencarbonate monoanion, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Accurate source identity and an authentic source role do not make the chemical entity identical to the protein requirement class.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality while preserving the exact supported chemical scope and source provenance. Preserve the bicarbonate/carbonate distinction and the positive PSII ligand/regulatory context; adjudicate the stated activity and dependence without turning a conditional regulatory result into universal absolute requirement. If the activity-relative role and chemical state are supported, an optional chemical_participants association with role COFACTOR may be used; otherwise preserve provenance and explicit uncertainty without inventing a participant. Do not move the same equality to mapped_xrefs, merge distinct chemical states, require optional examples or promote native status.

- Regenerated xrefs no longer equates the source chemical with the protein requirement. Exact chemical provenance and the intended requirement scope remain explicit.
- Any optional participant is a separately justified chemical entity with an activity-relative role; absence of optional participants or examples is not itself a defect.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml.
- For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Regenerate this existing target through an audited scoped route. Run full just validate-all before merging record changes, recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The inspected official Introduction and Licensing sections describe ChEBI chemical entities and roles and establish CC BY 4.0 licensing. This supports chemical-source provenance, not equivalence with a protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Its original access time is retained. The live backend snapshot and OLS release are distinct; neither identifies the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17544/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | CHEBI:17544 is hydrogencarbonate (bicarbonate), CHO3, net −1, O=C([O-])O. Its retained hydroxyl distinguishes it from carbonate(2−); it is the conjugate base of carbonic acid and conjugate acid of carbonate. Direct source roles include cofactor and organism-metabolite contexts; the source classifies it under carbon oxoanion. These are chemical identity and role assertions, not universal physiological-state claims. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17544; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:17544 as nonobsolete. The actual name, definition, synonyms and formula/charge/SMILES/InChI annotations were inspected against the backend, including any explicitly described disagreement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | CHEBI:23357 is the biochemical role cofactor, defined for an organic molecule or ion required by an enzyme for activity. It is under biochemical role CHEBI:52206, not a protein class. Source role membership supplies candidate context rather than a qualified exact-state protein requirement. |
| acid | https://www.ebi.ac.uk/chebi/backend/api/public/compound/28976/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Carbonic acid CHEBI:28976 is CH2O3, net 0, with two hydroxyl groups and a conjugate-acid relation to hydrogencarbonate. The current prose definition is null. |
| base | https://www.ebi.ac.uk/chebi/backend/api/public/compound/41609/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Carbonate CHEBI:41609 is CO3, net −2, with no retained hydroxyl; it is the conjugate base of hydrogencarbonate. Its current prose definition is null. |
| structural-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35604/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | The source carbon-oxoanion class CHEBI:35604 has no fixed formula or structure. Its literal definition speaks of carbon and oxygen only, while the current source also places hydrogencarbonate beneath it. This inherited class wording is recorded as source context rather than used to erase the explicit hydrogen or certify the entire chemical hierarchy. |
| psii-ligand | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8845353%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full article not inspected unless a separate full-text evidence entry is cited | supports | PMID:8845353; DOI:10.1021/bi00050a008. Isotope-labelled FTIR on Tris-washed PSII membranes identifies bicarbonate, not carbonate, as a non-heme-iron ligand. COH and H/D-sensitive modes support the retained proton. The paper interprets coordination differences between Fe2+ and Fe3+ states; those experimental interpretations are not universal ligand geometries. |
| psii-regulation | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:27791001%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full article not inspected unless a separate full-text evidence entry is cited | supports | PMID:27791001; DOI:10.1073/pnas.1608862113. Spectroelectrochemistry on plant PSII-enriched membranes shows bicarbonate removal shifts the QA midpoint potential from approximately −145 to −70 mV, slows electron transfer and changes singlet-oxygen formation. The authors propose a regulatory/protective model. This supports positive bound-function context, not complete activity loss in every condition. |
| psii-site-boundary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18439416%20AND%20SRC%3AMED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full article not inspected unless a separate full-text evidence entry is cited | supports | PMID:18439416; DOI:10.1016/j.bbabio.2008.03.031. Isotope and membrane-inlet mass-spectrometry experiments distinguish acceptor-side non-heme-iron bicarbonate from the proposed donor-side water-oxidation association. At least 75% initial oxygen-evolving activity persisted after strong bicarbonate/CO2 depletion. This bounds a donor-side requirement claim without refuting the independently supported iron-ligand function. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml; Executed 2026-10-21T12:46:01Z through 2026-10-21T12:46:04Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml; Executed 2026-10-21T12:46:04Z through 2026-10-21T12:46:04Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- Primary PSII studies were inspected through complete indexed abstracts. Exact isotope-sensitive bicarbonate identity is supported in the tested membranes, while universal coordination geometry, donor-side indispensability and a release-pinned qualifying protein are not established.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T125510Z-hydrogencarbonate-chebi17544
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires hydrogencarbonate
started_at: '2026-10-21T12:45:39Z'
finished_at: '2026-10-21T12:55:10Z'
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
summary: Hydrogencarbonate identity and positive PSII ligand/regulatory context are
  supported. One confirmed major finding concerns chemical-to-protein-requirement
  equivalence. Exact activity dependence remains bounded; no universal absence or
  indispensability is inferred.
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
  - path: data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    sha256: 8da1ae4ff4e2cfb7d8906a99e25140a7cfcdc321592064f30b3d8ddbf3183472
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
  selection: Path-order position 1 in batch 024. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242)
    covers 228 record paths, leaving 429131 before this batch. 24 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
targets:
- kind: generated
  label: requires hydrogencarbonate
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17544
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official backend and nonobsolete OLS identity, conjugate states, source
    cofactor role and licence resolve. Three complete primary abstracts support and
    bound the PSII context. The source-parent wording is preserved as a limitation,
    not certified as an exhaustive hierarchy.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:45:39Z'
  snapshot_sha256: 8da1ae4ff4e2cfb7d8906a99e25140a7cfcdc321592064f30b3d8ddbf3183472
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
  accessed_at: '2026-10-21T12:45:39Z'
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
  accessed_at: '2026-10-21T12:45:39Z'
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
  accessed_at: '2026-10-21T12:45:39Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:45:39Z'
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
  locator: Introduction and Licensing sections
  summary: The inspected official Introduction and Licensing sections describe ChEBI
    chemical entities and roles and establish CC BY 4.0 licensing. This supports chemical-source
    provenance, not equivalence with a protein requirement.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Its original access time is retained. The live backend snapshot and OLS release
    are distinct; neither identifies the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17544/
  accessed_at: '2026-10-21T12:46:36.090832Z'
  snapshot_sha256: 17d7e0250e8d8d6542425da8398bf21dae430299c70ca00a029249f7806f23c5
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: CHEBI:17544 is hydrogencarbonate (bicarbonate), CHO3, net −1, O=C([O-])O.
    Its retained hydroxyl distinguishes it from carbonate(2−); it is the conjugate
    base of carbonic acid and conjugate acid of carbonate. Direct source roles include
    cofactor and organism-metabolite contexts; the source classifies it under carbon
    oxoanion. These are chemical identity and role assertions, not universal physiological-state
    claims.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17544
  accessed_at: '2026-10-21T12:46:35.349047Z'
  snapshot_sha256: fd4fa251f21fa377691265d6ea1ad2f7b00def761dc2bb13d01a729d815290c1
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:17544 as nonobsolete. The actual name, definition, synonyms
    and formula/charge/SMILES/InChI annotations were inspected against the backend,
    including any explicitly described disagreement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: CHEBI:23357 is the biochemical role cofactor, defined for an organic molecule
    or ion required by an enzyme for activity. It is under biochemical role CHEBI:52206,
    not a protein class. Source role membership supplies candidate context rather
    than a qualified exact-state protein requirement.
- evidence_id: acid
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/28976/
  accessed_at: '2026-10-21T12:47:40.570943Z'
  snapshot_sha256: c60466e43cf01a0247340eb88bf2273b8e56ea2a90b52eb7ff6a7be1f51f6bb8
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Carbonic acid CHEBI:28976 is CH2O3, net 0, with two hydroxyl groups and
    a conjugate-acid relation to hydrogencarbonate. The current prose definition is
    null.
- evidence_id: base
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/41609/
  accessed_at: '2026-10-21T12:47:40.678980Z'
  snapshot_sha256: 6592d0ecf0608688ca944200408b35793c91f463e72642ba70d16ed924f1af47
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Carbonate CHEBI:41609 is CO3, net −2, with no retained hydroxyl; it is
    the conjugate base of hydrogencarbonate. Its current prose definition is null.
- evidence_id: structural-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35604/
  accessed_at: '2026-10-21T12:47:40.780901Z'
  snapshot_sha256: 8eea099989c6036a572b2ecb5b644594a96c81e97d353c7b9ad2e1db7e30cb61
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: The source carbon-oxoanion class CHEBI:35604 has no fixed formula or structure.
    Its literal definition speaks of carbon and oxygen only, while the current source
    also places hydrogencarbonate beneath it. This inherited class wording is recorded
    as source context rather than used to erase the explicit hydrogen or certify the
    entire chemical hierarchy.
- evidence_id: psii-ligand
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8845353%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:51:11.476711Z'
  snapshot_sha256: 9248aee17df02f88966bfde4eda180982a854e829e828b43c60c989398253793
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    unless a separate full-text evidence entry is cited
  summary: PMID:8845353; DOI:10.1021/bi00050a008. Isotope-labelled FTIR on Tris-washed
    PSII membranes identifies bicarbonate, not carbonate, as a non-heme-iron ligand.
    COH and H/D-sensitive modes support the retained proton. The paper interprets
    coordination differences between Fe2+ and Fe3+ states; those experimental interpretations
    are not universal ligand geometries.
- evidence_id: psii-regulation
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:27791001%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:51:11.501328Z'
  snapshot_sha256: 4976f3f2dacaac528046bbaa75cb54769d640e437fec4bd25995f8f73438ea01
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    unless a separate full-text evidence entry is cited
  summary: PMID:27791001; DOI:10.1073/pnas.1608862113. Spectroelectrochemistry on
    plant PSII-enriched membranes shows bicarbonate removal shifts the QA midpoint
    potential from approximately −145 to −70 mV, slows electron transfer and changes
    singlet-oxygen formation. The authors propose a regulatory/protective model. This
    supports positive bound-function context, not complete activity loss in every
    condition.
- evidence_id: psii-site-boundary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18439416%20AND%20SRC%3AMED&resultType=core&format=json
  accessed_at: '2026-10-21T12:47:45.131071Z'
  snapshot_sha256: 79944010ff3f73e8dbfa6036ab5f27113a310be52ea98666c79e8252af16d1ba
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    unless a separate full-text evidence entry is cited
  summary: PMID:18439416; DOI:10.1016/j.bbabio.2008.03.031. Isotope and membrane-inlet
    mass-spectrometry experiments distinguish acceptor-side non-heme-iron bicarbonate
    from the proposed donor-side water-oxidation association. At least 75% initial
    oxygen-evolving activity persisted after strong bicarbonate/CO2 depletion. This
    bounds a donor-side requirement claim without refuting the independently supported
    iron-ligand function.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  locator: Executed 2026-10-21T12:46:01Z through 2026-10-21T12:46:04Z; exit 0
  accessed_at: '2026-10-21T12:46:04Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0
  accessed_at: '2026-10-21T12:48:55Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
  locator: Executed 2026-10-21T12:46:04Z through 2026-10-21T12:46:04Z; exit 0
  accessed_at: '2026-10-21T12:46:04Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0
  accessed_at: '2026-10-21T12:48:57Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The target label and copied chemical definition resolve to the monoanion
    HCO3−, not neutral carbonic acid or carbonate(2−). Explicit structure and conjugate
    relations support this distinction. The source parent uses narrower literal wording
    than its own hydrogen-containing child; this does not make the target an unidentified
    ion.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - acid
  - base
  - structural-parent
  topic: Hydrogencarbonate identity and acid-base state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The isotope-sensitive FTIR study supports bicarbonate specifically at the
    non-heme iron. Independent electrochemical work demonstrates functional redox
    tuning. The donor-side depletion study prevents importing a universal water-oxidation
    requirement or complete inactivity claim. These are positive bounded protein-complex
    contexts, not newly qualified canonical protein examples.
  evidence_ids:
  - psii-ligand
  - psii-regulation
  - psii-site-boundary
  topic: Bicarbonate as a PSII iron ligand and functional regulator
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: Positive binding and regulatory evidence is retained, but this generic
    record does not specify a protein, activity, assay conditions or the strength
    of dependence. The evidence does not justify every bicarbonate-associated protein
    or universal absolute dependence. Optional examples and participants are not mandatory
    repairs.
  evidence_ids:
  - record
  - schema
  - chemical
  - psii-ligand
  - psii-regulation
  topic: Activity-specific bicarbonate requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The direct chemical cofactor role and local cofactor-requirement parent
    explain source-driven selection. Parent resolution does not independently establish
    true equivalence or certify all parent wording and members.
  evidence_ids:
  - chemical
  - cofactor-role
  - local-parent-1
  - owner
  topic: Source cofactor role and local broader parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-8
- area: grounding
  outcome: concern
  summary: CHEBI:17544 denotes the hydrogencarbonate monoanion, whereas the local
    COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot
    asserts true own-source equivalence. Accurate source identity and an authentic
    source role do not make the chemical entity identical to the protein requirement
    class.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - psii-ligand
  - psii-regulation
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-9
- area: provenance
  outcome: supported
  summary: The captured ChEBI seeder explains the synthesized requirement prefix,
    appended chemical text, role-derived parent and emitted chemical xref. The official
    licence is CC BY 4.0. The source chemical statement is attributable to ChEBI;
    the protein-requirement transformation is local and is not independently supplied
    by that attribution. Live backend and OLS version 256 are retained as comparison
    snapshots, with the original seed release unknown.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  topic: Source attribution, licence and maintained emitter
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17544.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:17544 denotes the hydrogencarbonate monoanion, whereas the local
    COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot
    asserts true own-source equivalence. Accurate source identity and an authentic
    source role do not make the chemical entity identical to the protein requirement
    class.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - psii-ligand
  - psii-regulation
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical entity and synthesized protein-requirement class
    have different denotations. This is a major grounding defect independent of biological
    relevance or the presence of optional representations.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait
    equality while preserving the exact supported chemical scope and source provenance.
    Preserve the bicarbonate/carbonate distinction and the positive PSII ligand/regulatory
    context; adjudicate the stated activity and dependence without turning a conditional
    regulatory result into universal absolute requirement. If the activity-relative
    role and chemical state are supported, an optional chemical_participants association
    with role COFACTOR may be used; otherwise preserve provenance and explicit uncertainty
    without inventing a participant. Do not move the same equality to mapped_xrefs,
    merge distinct chemical states, require optional examples or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17544
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Regenerated xrefs no longer equates the source chemical with the protein requirement.
    Exact chemical provenance and the intended requirement scope remain explicit.
  - Any optional participant is a separately justified chemical entity with an activity-relative
    role; absence of optional participants or examples is not itself a defect.
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml.
  - For maintained writer changes add focused regression coverage and run just audit-writers,
    just lint and just test. Regenerate this existing target through an audited scoped
    route. Run full just validate-all before merging record changes, recapture changed
    inputs and save a fresh structured review without overwriting this observation.
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
- Primary PSII studies were inspected through complete indexed abstracts. Exact isotope-sensitive
  bicarbonate identity is supported in the tested membranes, while universal coordination
  geometry, donor-side indispensability and a release-pinned qualifying protein are
  not established.
tags:
- unreviewed-path-order
- batch-024
- chebi-cofactor
```
