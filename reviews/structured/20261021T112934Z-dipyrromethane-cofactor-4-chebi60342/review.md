# Review of requires dipyrromethane cofactor(4−)

- Review: 20261021T112934Z-dipyrromethane-cofactor-4-chebi60342
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:22:00Z
- Finished UTC: 2026-10-21T11:29:34Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Dipyrromethane tetraanion connectivity and source role are supported, as is a retained covalent catalytic cofactor in inspected enzymes. One confirmed major finding concerns chemical-to-protein-trait equivalence. Exact free-state requirement and the source pH 7.3 population assertion remain independently unresolved.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 019. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c) covers 178 record paths, leaving 429181 before this batch. 19 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml | generated | requires dipyrromethane cofactor(4−) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60342 | Official ChEBI/OLS resolve CHEBI:60342 and its exact chemical/source-role context. The captured local cofactor parent, inspected external comparisons and bounded primary/authority sources are recorded separately from protein-trait equivalence and native protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Dipyrromethane connectivity and conjugate charge

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The official source and neutral CCD component resolve the substituted dipyrromethane scaffold with four carboxy groups. Neutral CHEBI:42121 and its tetracarboxylate CHEBI:60342 differ by four protons, not by redox state. These fixed structures are neither generic R-groups nor whole protein adducts. The neutral source has no prose definition; this absence is preserved rather than filled with an inferred mechanism.

### Retained catalytic dipyrromethane cofactor

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The E. coli primary experiment positively supports a covalently retained cofactor that binds catalytic intermediates without entering the released product. Assembly from preuroporphyrinogen and the B. megaterium structural observations are complementary, bounded contexts. The latter study distinguishes protein attachment and oxidation states; it does not justify equating every observed oxidized component with the reduced chemical entries.

### Exact chemical-state requirement and covalent attachment

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

A biologically functional dipyrromethane cofactor is supported in the inspected enzymes. The exact free neutral or tetraanionic component is not thereby established as an independently supplied molecule, the universal protein-bound charge or a newly qualified native protein example. Protein attachment and activity-relative role must remain explicit in any representation.

### Dipyrromethane population at pH 7.3

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The source faithfully asserts major species at pH 7.3, but the inspected primary work does not independently establish equilibrium populations of the exact free tetraanion at that pH. Carboxylate contacts in a covalent protein cofactor and its oxidation during storage are not a free-solution titration or a direct refutation.

### Chemical source and maintained requirement synthesis

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The exact chemical identifier, current source text or explicit null definition, direct role assertions and CC BY 4.0 licence resolve. The protein-requirement wrapper is generated by the maintained ChEBI seeder; current comparison snapshots do not identify its original seed release.

### Source cofactor role versus local broader requirement

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The captured cofactor-requirement parent resolves. Current source direct cofactor role explains the selection. CHEBI:42121 also has prosthetic-group role, whose source parent is cofactor. Role taxonomy supplies candidate context but is not equality between a chemical and a protein trait, and this review does not certify the parent.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60342.

The xref denotes a chemical entity while the local class denotes a protein functional requirement. Correct chemical identity and biological activity evidence do not make those different entity types equivalent.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-60342.chemical-entity-equivalence.

The source chemical entity in xrefs and the local protein functional requirement have different denotations. Authentic cofactor roles and bounded biological support do not satisfy true own-source equivalence.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-trait equivalence and preserve CHEBI:60342 through supported chemical grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role and exact chemical state before adding a typed participant; preserve protein attachment, charge, metal and stereochemical distinctions where relevant. If the evidence cannot support the required role, retain chemical provenance and explicit uncertainty without inventing a participant. Do not move the same equality to mapped_xrefs, merge conjugates or automatically qualify proteins.

- Exact source identity and state remain auditable without asserting chemical/protein-class equality. Any participant has a curator-adjudicated activity-relative role; otherwise provenance and uncertainty are retained.
- Use an audited route selecting the existing target and a focused source-transform fixture. Preserve the supported bound-cofactor or pigment context without equating free states, covalent adducts, biosynthetic substrates or oxidation products. No status or protein-example promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml. Run full just validate-all before merging record changes; inspect changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The inspected official ChEBI chemical-scope and Licensing sections support chemical entities/roles and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports comparison ontology version 256, loaded 2026-10-16. Original access time and digest are retained; this does not assign a release to the original seed or live chemical backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60342/; Complete identifier/name/definition, aliases, formula/charge, structure, origins and incoming/outgoing relations | supports | CHEBI:60342 denotes the fixed tetracarboxylate C20H20N2O8, charge −4, conjugate base of CHEBI:42121. All four carboxy groups are deprotonated; the two pyrrole rings and their methylene bridge are retained. It is not an R-group structure and contains no protein or sulfur attachment. The current definition states major species at pH 7.3; that population assertion is source provenance, not independently established by the inspected experiments. Its direct role is cofactor. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60342; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier, with the actual definition, names/synonym scopes and chemical annotations inspected. Chemical resolution is not equivalent protein-trait grounding. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity. Its parent is biochemical role CHEBI:52206. This role is not a protein-requirement class. |
| context-42121 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/42121/; Complete chemical identity, definition, names, structure and outgoing relations | supports | CHEBI:42121 denotes fixed neutral dipyrromethane cofactor, C20H24N2O8, with four carboxylic acids, two pyrrole rings and a methylene bridge. It has no specified stereocentre or R-group/protein attachment. The current prose definition is null; the source supplies names, structure, a PDBe DPM association, direct prosthetic-group and cofactor roles, and conjugate base CHEBI:60342. |
| context-35754 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35754/; Complete chemical identity, definition, names, structure and outgoing relations | supports | The structural parent tetracarboxylic acid anion covers removal of one or more carboxy protons. The target definition and structure, not the broader parent alone, specify four deprotonations. |
| context-26348 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Complete chemical identity, definition, names, structure and outgoing relations | supports | Prosthetic group is a tightly bound, specific nonpolypeptide unit involved in protein activity; its source parent is cofactor CHEBI:23357. This is a biochemical role, not a chemical molecule or equivalent protein class. |
| primary-3079571 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A3079571%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI; complete indexed abstract; full article not inspected | supports | PMID:3079571. Evidence for a dipyrromethane cofactor at the catalytic site of E. coli porphobilinogen deaminase; DOI:10.1016/0014-5793(87)81136-5. The complete abstract reports covalent linkage, binding of catalytic intermediates, radiolabel incorporation into the cofactor and no incorporation into product. This positively supports a retained catalytic cofactor in the tested enzyme; it does not establish the exact free 0/−4 chemical state or a physiological pH population. |
| primary-8687374 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8687374%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI; complete indexed abstract; full article not inspected | supports | PMID:8687374. Discovery that assembly of the dipyrromethane cofactor proceeds initially by reaction of preuroporphyrinogen with apoenzyme; DOI:10.1042/bj3160373. The complete abstract supports an enzyme-bound intermediate and preferred precursor in E. coli, with inactive D84A/D84N ES2 complexes. Formation from a substrate/product does not make the retained cofactor a consumed substrate. |
| component | https://www.ebi.ac.uk/pdbe/static/files/pdbechem_v2/DPM.cif; DPM chemical-component identity, atom/bond tables and InChI descriptors | supports | The official PDBe chemical-component dictionary DPM identifies neutral C20H24N2O8, charge 0, with the same InChIKey as CHEBI:42121. Its atom/bond and descriptor tables describe the isolated chemical component; they do not encode a whole cysteine-linked protein adduct or establish a measured protein-bound protonation state. No database drug-target association is used for protein qualification. |
| dpm-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3949521/fullTextXML; PMC3949521 complete main text, figure legends and Table 1; especially Methods and Results 3.2/Discussion | supports | PMID:24598743; DOI:10.1107/S139900471303294X. The complete article reports B. megaterium PBGD structures with a Cys241-linked cofactor, carboxylate interactions and time-dependent partially oxidized forms after storage. It distinguishes catalytic dipyrromethane from oxidized forms and explicitly limits X-ray discrimination of dipyrromethane versus dipyrromethene. The proposed oxidation sequence is not a measured pH 7.3 population of free CHEBI:60342. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml; Executed 2026-10-21T11:22:28Z through 2026-10-21T11:22:29Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml; Executed 2026-10-21T11:22:22Z through 2026-10-21T11:23:43Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml; Executed 2026-10-21T11:22:29Z through 2026-10-21T11:22:29Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:23:43Z through 2026-10-21T11:23:44Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The initial PMC HTML response was a browser challenge and is excluded. The successful Europe PMC full-text XML was inspected completely for main text, figure legends and table; the two earlier papers were inspected through complete indexed abstracts only. Failed exploratory zero-result queries are not evidence.
- No exact free-state titration, protein-bound charge measurement or whole-protein chemical identity is inferred from the component dictionary. Four carboxy deprotonations, covalent attachment and oxidative changes are separate chemical operations.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T112934Z-dipyrromethane-cofactor-4-chebi60342
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires dipyrromethane cofactor(4−)
started_at: '2026-10-21T11:22:00Z'
finished_at: '2026-10-21T11:29:34Z'
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
summary: Dipyrromethane tetraanion connectivity and source role are supported, as
  is a retained covalent catalytic cofactor in inspected enzymes. One confirmed major
  finding concerns chemical-to-protein-trait equivalence. Exact free-state requirement
  and the source pH 7.3 population assertion remain independently unresolved.
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
  - path: data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    sha256: 25b44403309b3307009ab62820ad58b8c39a86a7e2757d242cb51f3dc77b6a5a
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
  selection: Path-order position 6 in batch 019. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c) covers 178 record paths,
    leaving 429181 before this batch. 19 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
targets:
- kind: generated
  label: requires dipyrromethane cofactor(4−)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_60342
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:60342 and its exact chemical/source-role
    context. The captured local cofactor parent, inspected external comparisons and
    bounded primary/authority sources are recorded separately from protein-trait equivalence
    and native protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-42121
  - context-35754
  - context-26348
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:22:00Z'
  snapshot_sha256: 25b44403309b3307009ab62820ad58b8c39a86a7e2757d242cb51f3dc77b6a5a
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
  accessed_at: '2026-10-21T11:22:00Z'
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
  accessed_at: '2026-10-21T11:22:00Z'
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
  accessed_at: '2026-10-21T11:22:00Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:22:00Z'
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
  locator: Introduction and Licensing
  summary: The inspected official ChEBI chemical-scope and Licensing sections support
    chemical entities/roles and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait
    equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports comparison ontology version 256, loaded
    2026-10-16. Original access time and digest are retained; this does not assign
    a release to the original seed or live chemical backend.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60342/
  accessed_at: '2026-10-21T11:22:44.379329Z'
  snapshot_sha256: f289fa492de212fe580c024187a639d2d10e8dfbd8b883bbc48812379674f790
  support: supports
  locator: Complete identifier/name/definition, aliases, formula/charge, structure,
    origins and incoming/outgoing relations
  summary: CHEBI:60342 denotes the fixed tetracarboxylate C20H20N2O8, charge −4, conjugate
    base of CHEBI:42121. All four carboxy groups are deprotonated; the two pyrrole
    rings and their methylene bridge are retained. It is not an R-group structure
    and contains no protein or sulfur attachment. The current definition states major
    species at pH 7.3; that population assertion is source provenance, not independently
    established by the inspected experiments. Its direct role is cofactor.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60342
  accessed_at: '2026-10-21T11:22:44.378524Z'
  snapshot_sha256: aa1d9fec74f8ad7568cd2204fdd8ba7042976a0be2015f58e09ba04d42431f7f
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier, with the actual
    definition, names/synonym scopes and chemical annotations inspected. Chemical
    resolution is not equivalent protein-trait grounding.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity. Its parent is biochemical role CHEBI:52206. This
    role is not a protein-requirement class.
- evidence_id: context-42121
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/42121/
  accessed_at: '2026-10-21T11:22:45.008373Z'
  snapshot_sha256: ee1eed2d89fe464cbbee7b09eb021e090ad5a2079015fa0c0fdf9f047a4c1722
  support: supports
  locator: Complete chemical identity, definition, names, structure and outgoing relations
  summary: CHEBI:42121 denotes fixed neutral dipyrromethane cofactor, C20H24N2O8,
    with four carboxylic acids, two pyrrole rings and a methylene bridge. It has no
    specified stereocentre or R-group/protein attachment. The current prose definition
    is null; the source supplies names, structure, a PDBe DPM association, direct
    prosthetic-group and cofactor roles, and conjugate base CHEBI:60342.
- evidence_id: context-35754
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35754/
  accessed_at: '2026-10-21T11:23:15.322715Z'
  snapshot_sha256: f3fa298e63fe2176bc9f3134342386ef50cda721501e2f8532365266b33628f5
  support: supports
  locator: Complete chemical identity, definition, names, structure and outgoing relations
  summary: The structural parent tetracarboxylic acid anion covers removal of one
    or more carboxy protons. The target definition and structure, not the broader
    parent alone, specify four deprotonations.
- evidence_id: context-26348
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T11:23:15.323178Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Complete chemical identity, definition, names, structure and outgoing relations
  summary: Prosthetic group is a tightly bound, specific nonpolypeptide unit involved
    in protein activity; its source parent is cofactor CHEBI:23357. This is a biochemical
    role, not a chemical molecule or equivalent protein class.
- evidence_id: primary-3079571
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A3079571%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:23:16.270606Z'
  snapshot_sha256: aa395953848ae4c39b5a2694d39ea3b4aa900edffe9e27c3338d176633f6a594
  support: supports
  locator: Verified PMID/DOI; complete indexed abstract; full article not inspected
  summary: PMID:3079571. Evidence for a dipyrromethane cofactor at the catalytic site
    of E. coli porphobilinogen deaminase; DOI:10.1016/0014-5793(87)81136-5. The complete
    abstract reports covalent linkage, binding of catalytic intermediates, radiolabel
    incorporation into the cofactor and no incorporation into product. This positively
    supports a retained catalytic cofactor in the tested enzyme; it does not establish
    the exact free 0/−4 chemical state or a physiological pH population.
- evidence_id: primary-8687374
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8687374%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:23:16.272270Z'
  snapshot_sha256: c854ef8e0e37e23782c2d2fbce726bd09f635738689cca883cf5fd2c3ba5fc66
  support: supports
  locator: Verified PMID/DOI; complete indexed abstract; full article not inspected
  summary: PMID:8687374. Discovery that assembly of the dipyrromethane cofactor proceeds
    initially by reaction of preuroporphyrinogen with apoenzyme; DOI:10.1042/bj3160373.
    The complete abstract supports an enzyme-bound intermediate and preferred precursor
    in E. coli, with inactive D84A/D84N ES2 complexes. Formation from a substrate/product
    does not make the retained cofactor a consumed substrate.
- evidence_id: component
  kind: database
  reference: https://www.ebi.ac.uk/pdbe/static/files/pdbechem_v2/DPM.cif
  accessed_at: '2026-10-21T11:23:18.113995Z'
  snapshot_sha256: 84d484a711196a2dd0781ec318880d6f91446f25852fc03efee5670728e7f17b
  support: supports
  locator: DPM chemical-component identity, atom/bond tables and InChI descriptors
  summary: The official PDBe chemical-component dictionary DPM identifies neutral
    C20H24N2O8, charge 0, with the same InChIKey as CHEBI:42121. Its atom/bond and
    descriptor tables describe the isolated chemical component; they do not encode
    a whole cysteine-linked protein adduct or establish a measured protein-bound protonation
    state. No database drug-target association is used for protein qualification.
- evidence_id: dpm-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3949521/fullTextXML
  accessed_at: '2026-10-21T11:23:55.289432Z'
  snapshot_sha256: a5dc77c3030083f5b67f3019ff73c1743528d0cb351f71109c4b85caa86cdfa7
  support: supports
  locator: PMC3949521 complete main text, figure legends and Table 1; especially Methods
    and Results 3.2/Discussion
  summary: PMID:24598743; DOI:10.1107/S139900471303294X. The complete article reports
    B. megaterium PBGD structures with a Cys241-linked cofactor, carboxylate interactions
    and time-dependent partially oxidized forms after storage. It distinguishes catalytic
    dipyrromethane from oxidized forms and explicitly limits X-ray discrimination
    of dipyrromethane versus dipyrromethene. The proposed oxidation sequence is not
    a measured pH 7.3 population of free CHEBI:60342.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  locator: Executed 2026-10-21T11:22:28Z through 2026-10-21T11:22:29Z; exit 0
  accessed_at: '2026-10-21T11:22:29Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml
  locator: Executed 2026-10-21T11:22:22Z through 2026-10-21T11:23:43Z; exit 0
  accessed_at: '2026-10-21T11:23:43Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
  locator: Executed 2026-10-21T11:22:29Z through 2026-10-21T11:22:29Z; exit 0
  accessed_at: '2026-10-21T11:22:29Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:23:43Z through 2026-10-21T11:23:44Z; exit 0
  accessed_at: '2026-10-21T11:23:44Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The official source and neutral CCD component resolve the substituted dipyrromethane
    scaffold with four carboxy groups. Neutral CHEBI:42121 and its tetracarboxylate
    CHEBI:60342 differ by four protons, not by redox state. These fixed structures
    are neither generic R-groups nor whole protein adducts. The neutral source has
    no prose definition; this absence is preserved rather than filled with an inferred
    mechanism.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-42121
  - component
  topic: Dipyrromethane connectivity and conjugate charge
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The E. coli primary experiment positively supports a covalently retained
    cofactor that binds catalytic intermediates without entering the released product.
    Assembly from preuroporphyrinogen and the B. megaterium structural observations
    are complementary, bounded contexts. The latter study distinguishes protein attachment
    and oxidation states; it does not justify equating every observed oxidized component
    with the reduced chemical entries.
  evidence_ids:
  - primary-3079571
  - primary-8687374
  - dpm-fulltext
  topic: Retained catalytic dipyrromethane cofactor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: A biologically functional dipyrromethane cofactor is supported in the inspected
    enzymes. The exact free neutral or tetraanionic component is not thereby established
    as an independently supplied molecule, the universal protein-bound charge or a
    newly qualified native protein example. Protein attachment and activity-relative
    role must remain explicit in any representation.
  evidence_ids:
  - record
  - schema
  - chemical
  - component
  - primary-3079571
  - dpm-fulltext
  topic: Exact chemical-state requirement and covalent attachment
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-7
- area: evidence
  outcome: unknown
  summary: The source faithfully asserts major species at pH 7.3, but the inspected
    primary work does not independently establish equilibrium populations of the exact
    free tetraanion at that pH. Carboxylate contacts in a covalent protein cofactor
    and its oxidation during storage are not a free-solution titration or a direct
    refutation.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - dpm-fulltext
  topic: Dipyrromethane population at pH 7.3
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The exact chemical identifier, current source text or explicit null definition,
    direct role assertions and CC BY 4.0 licence resolve. The protein-requirement
    wrapper is generated by the maintained ChEBI seeder; current comparison snapshots
    do not identify its original seed release.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  topic: Chemical source and maintained requirement synthesis
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-9
- area: consistency
  outcome: supported
  summary: The captured cofactor-requirement parent resolves. Current source direct
    cofactor role explains the selection. CHEBI:42121 also has prosthetic-group role,
    whose source parent is cofactor. Role taxonomy supplies candidate context but
    is not equality between a chemical and a protein trait, and this review does not
    certify the parent.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - owner
  - context-26348
  - context-42121
  topic: Source cofactor role versus local broader requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The xref denotes a chemical entity while the local class denotes a protein
    functional requirement. Correct chemical identity and biological activity evidence
    do not make those different entity types equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-60342.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The source chemical entity in xrefs and the local protein functional
    requirement have different denotations. Authentic cofactor roles and bounded biological
    support do not satisfy true own-source equivalence.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The candidate requirement is recognizable, but chemical and
    protein-requirement denotations differ; the class-equivalence assertion is a major
    grounding defect.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-trait
    equivalence and preserve CHEBI:60342 through supported chemical grounding/provenance.
    Adjudicate the activity-relative ChemicalParticipant.role and exact chemical state
    before adding a typed participant; preserve protein attachment, charge, metal
    and stereochemical distinctions where relevant. If the evidence cannot support
    the required role, retain chemical provenance and explicit uncertainty without
    inventing a participant. Do not move the same equality to mapped_xrefs, merge
    conjugates or automatically qualify proteins.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60342
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Exact source identity and state remain auditable without asserting chemical/protein-class
    equality. Any participant has a curator-adjudicated activity-relative role; otherwise
    provenance and uncertainty are retained.
  - Use an audited route selecting the existing target and a focused source-transform
    fixture. Preserve the supported bound-cofactor or pigment context without equating
    free states, covalent adducts, biosynthetic substrates or oxidation products.
    No status or protein-example promotion occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml.
    Run full just validate-all before merging record changes; inspect changed inputs
    and save a fresh validated review rather than overwriting this observation.
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
- The initial PMC HTML response was a browser challenge and is excluded. The successful
  Europe PMC full-text XML was inspected completely for main text, figure legends
  and table; the two earlier papers were inspected through complete indexed abstracts
  only. Failed exploratory zero-result queries are not evidence.
- No exact free-state titration, protein-bound charge measurement or whole-protein
  chemical identity is inferred from the component dictionary. Four carboxy deprotonations,
  covalent attachment and oxidative changes are separate chemical operations.
tags:
- unreviewed-path-order
- batch-019
- chebi-cofactor
```
