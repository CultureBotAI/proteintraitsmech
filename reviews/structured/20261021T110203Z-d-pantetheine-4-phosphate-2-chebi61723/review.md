# Review of requires D-pantetheine 4'-phosphate(2−)

- Review: 20261021T110203Z-d-pantetheine-4-phosphate-2-chebi61723
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:55:39Z
- Finished UTC: 2026-10-21T11:02:03Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

D/(R) phosphopantetheine dianion chemistry and source prosthetic-group ancestry are supported. One confirmed major finding concerns chemical-to-trait equivalence. Covalent prosthetic-moiety evidence is kept separate from free-state qualification; the source pH 7.3 population assertion remains independently unresolved.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 017. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd) covers 158 record paths, leaving 429201 before this batch. 17 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml | generated | requires D-pantetheine 4'-phosphate(2−) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61723 | Official structured ChEBI and OLS resolve CHEBI:61723 and the inspected chemical/role context. Resolution establishes chemical identity/provenance, not protein-trait equivalence or per-protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Phosphopantetheine connectivity, charge and stereochemistry

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The exact formula, charge, D/(R) stereocentre, phosphate monoester and free thiol agree with the target chemical definition. The neutral/dianion pair differs by two phosphate protons, not a redox change or stereochemical inversion; the stereounspecified parent remains broader.

### Covalent phosphopantetheine prosthetic-group evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The primary abstract supports phosphopantetheinyl transfer from CoA to a conserved protein serine and FDH activation. Covalent prosthetic-moiety evidence is distinguished from a requirement for an unchanged free neutral or dianionic molecule; ACP structural context does not settle that exact-state question.

### Phosphate speciation and exact protein-bound state

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The source pH 7.3 major-microspecies assertion is faithfully copied, but no inspected primary equilibrium measurement independently establishes that population. The covalent protein moiety is a separate state question; lack of independent confirmation is not a demonstrated chemical contradiction.

### Definition and maintained-source provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The chemical definition and direct source role are traceable to current official ChEBI; the requirement wrapper is maintained ChEBI-seeder synthesis. Licence and current OLS comparison release are documented, while the exact seed release remains unknown.

### Requirement-parent and source-relation scope

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The captured local requirement parent resolves. Direct chemical role and role ancestry supply candidate class context; chemical is-a and conjugate relations are not protein-trait equivalence.

### Protein requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The record proposes a reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class. The exact activity-relative, non-substrate protein requirement remains unqualified; source chemical-role assertions or alignment labels alone do not supply that evidence. No optional example, mechanism or native status is promoted.

### Chemical denotation versus protein-trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61723.

The ChEBI chemical referent differs from the protein-requirement class, while xrefs asserts true own-source equivalence. A chemical association requires typed grounding after chemical-state and activity-relative role adjudication.

## Findings

### F1: Chemical referent is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-61723.chemical-entity-equivalence.

The xref denotes a chemical entity while the local record denotes a protein functional requirement. Correct chemical identity or a source cofactor/prosthetic-group role would not establish equality of these classes.

## Recommended Actions And Acceptance Checks

### A1

change build in scripts/seed_chebi_cofactor.py to replace chemical-to-trait equality with an accurately typed chemical_participants association. Preserve CHEBI:61723 and its exact chemical-state scope. ChemicalParticipant.role is required: adjudicate the activity-relative role, including the category's non-substrate scope, rather than treating a source role assertion as independently verified COFACTOR. Keep candidate provenance distinct from new protein qualification, and do not simply move equality to mapped_xrefs. Distinguish the free chemical from any covalently attached prosthetic moiety; do not silently equate their protonation or connectivity.

- The source chemical association no longer asserts chemical-to-protein-trait equivalence; exact state and candidate source provenance remain auditable.
- A focused source-transform fixture verifies identity and required role adjudication. Regeneration follows an audited route explicitly selecting existing records. No protein/status promotion or silent conjugate merge occurs.
- For maintained writer changes run just audit-writers, just lint and just test with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml. Run full just validate-all before merging record changes. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | The complete captured cofactor requirement ancestor above the prosthetic-group parent was inspected. Resolving that hierarchy does not certify its chemical-role xref semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical scope and Licensing section | supports | The inspected official ChEBI About and Licensing sections support chemical-entity/role scope and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Reused OLS metadata records comparison ontology version 256; the original access UTC and digest are retained. It does not establish the seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/61723/; Complete identity, names, chemical_data/default_structure, source origins and outgoing relations | supports | CHEBI:61723 is D-pantetheine 4'-phosphate(2−), C11H21N2O7PS, charge −2. The sole stereocentre is specified as D/(R) at 2'; the two negative charges are on phosphate oxygens, with the terminal thiol still protonated. It has direct prosthetic-group role, stereounspecified parent CHEBI:47942, and neutral conjugate acid CHEBI:4222. The pH 7.3 major-microspecies sentence is authentic source text, not independently verified population evidence. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:61723; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete identifier, definition, source synonym scopes and chemical annotations. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 is the abstract cofactor biochemical role, not a molecular entity or a protein requirement; its outgoing parent is biochemical role CHEBI:52206. |
| context-47942 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47942/; Complete definition, chemical data/structure and outgoing relations | supports | CHEBI:47942 is stereounspecified pantetheine 4'-phosphate(2−), C11H21N2O7PS, with phosphate dianion and free thiol. It has cofactor and metabolite roles and is conjugate base of CHEBI:16858. Lack of stereochemical specification in the parent is not identity with the D-specific child. |
| context-26348 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Complete definition, chemical data/structure and outgoing relations | supports | Prosthetic group CHEBI:26348 is a tightly bound, specific nonpolypeptide unit involved in protein activity and is-a cofactor CHEBI:23357. The role does not itself specify a free molecule versus a covalent protein moiety. |
| context-4222 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/4222/; Complete definition, chemical data/structure and outgoing relations | supports | CHEBI:4222 is neutral D-pantetheine 4'-phosphate, C11H23N2O7PS, charge 0, with one D/(R) stereocentre, a free terminal thiol and protonated phosphate monoester. It has direct prosthetic-group role, stereounspecified parent CHEBI:16858 and dianionic conjugate base CHEBI:61723. It is a defined free chemical structure, not an automatically identical covalent protein adduct. |
| primary-19933275 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19933275%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:19933275; DOI:10.1074/jbc.M109.080556. The complete abstract describes transfer of 4'-phosphopantetheine from CoA to a conserved serine and human PPT-mediated conversion of apo-FDH to catalytically active holo-FDH. The covalently attached swinging-arm prosthetic moiety is supported; the exact free neutral/dianionic chemical is not thereby shown to be the unchanged protein-bound state. No residue coordinate is asserted from this abstract. |
| primary-19177367 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19177367%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:19177367; DOI:10.1002/pro.11. The complete abstract compares apo-ACP, ACP and butyryl-ACP solution structures under identical conditions and reports conformational changes associated with the acyl intermediate. It supports bounded carrier-protein structural context, not an exact free phosphopantetheine protonation state or a general requirement for every protein. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml; Executed 2026-10-21T10:57:38Z through 2026-10-21T10:57:39Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/copper-1-chebi49552.yaml data/traits/function/cofactor_requirement/chebi/copper-2-chebi29036.yaml data/traits/function/cofactor_requirement/chebi/copper-cation-chebi23378.yaml data/traits/function/cofactor_requirement/chebi/corrin-chebi33221.yaml data/traits/function/cofactor_requirement/chebi/corrinoid-chebi33913.yaml data/traits/function/cofactor_requirement/chebi/ctp-chebi17677.yaml data/traits/function/cofactor_requirement/chebi/cu-chebi28694.yaml data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-chebi4222.yaml data/traits/function/cofactor_requirement/chebi/decylplastoquinone-chebi72953.yaml; Executed 2026-10-21T10:55:55Z through 2026-10-21T10:57:11Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml; Executed 2026-10-21T10:57:39Z through 2026-10-21T10:57:39Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:57:11Z through 2026-10-21T10:57:12Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMC2804320 and PMC2708020 HTML captures were browser challenges; Europe PMC fullTextXML returned 500 and BioC returned 429. Those bodies are excluded as scientific support. The complete indexed abstracts support only the stated scope; no serine residue coordinate or full-paper result is claimed.
- The pH 7.3 population claim remains independently unresolved; no pKa, numerical abundance or universal intracellular state is inferred. This is a bounded evidence limitation rather than an additional proven defect.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T110203Z-d-pantetheine-4-phosphate-2-chebi61723
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires D-pantetheine 4'-phosphate(2−)
started_at: '2026-10-21T10:55:39Z'
finished_at: '2026-10-21T11:02:03Z'
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
summary: D/(R) phosphopantetheine dianion chemistry and source prosthetic-group ancestry
  are supported. One confirmed major finding concerns chemical-to-trait equivalence.
  Covalent prosthetic-moiety evidence is kept separate from free-state qualification;
  the source pH 7.3 population assertion remains independently unresolved.
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
  - path: data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
    sha256: 688fadaf54f9c15d5537bc8d88b7f4076370090360515d2d9696283a655eec10
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml
    sha256: b46e2badf95bf0718eb473668f579602de9e98d477f437c2114eb6a5e3d36393
    role: context
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
  selection: Path-order position 8 in batch 017. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd) covers 158 record paths,
    leaving 429201 before this batch. 17 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
targets:
- kind: generated
  label: requires D-pantetheine 4'-phosphate(2−)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_61723
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/copper-1-chebi49552.yaml
    data/traits/function/cofactor_requirement/chebi/copper-2-chebi29036.yaml data/traits/function/cofactor_requirement/chebi/copper-cation-chebi23378.yaml
    data/traits/function/cofactor_requirement/chebi/corrin-chebi33221.yaml data/traits/function/cofactor_requirement/chebi/corrinoid-chebi33913.yaml
    data/traits/function/cofactor_requirement/chebi/ctp-chebi17677.yaml data/traits/function/cofactor_requirement/chebi/cu-chebi28694.yaml
    data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
    data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-chebi4222.yaml
    data/traits/function/cofactor_requirement/chebi/decylplastoquinone-chebi72953.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official structured ChEBI and OLS resolve CHEBI:61723 and the inspected
    chemical/role context. Resolution establishes chemical identity/provenance, not
    protein-trait equivalence or per-protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-47942
  - context-26348
  - context-4222
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:55:39Z'
  snapshot_sha256: 688fadaf54f9c15d5537bc8d88b7f4076370090360515d2d9696283a655eec10
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
  accessed_at: '2026-10-21T10:55:39Z'
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
  accessed_at: '2026-10-21T10:55:39Z'
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
  accessed_at: '2026-10-21T10:55:39Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:55:39Z'
  snapshot_sha256: b46e2badf95bf0718eb473668f579602de9e98d477f437c2114eb6a5e3d36393
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T10:55:39Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: The complete captured cofactor requirement ancestor above the prosthetic-group
    parent was inspected. Resolving that hierarchy does not certify its chemical-role
    xref semantics.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Chemical scope and Licensing section
  summary: The inspected official ChEBI About and Licensing sections support chemical-entity/role
    scope and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait
    equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Reused OLS metadata records comparison ontology version 256; the original
    access UTC and digest are retained. It does not establish the seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/61723/
  accessed_at: '2026-10-21T10:56:20.210851Z'
  snapshot_sha256: cdf22539cabff744c3364c6a290ff3dccb62bd8c582e31bc01e1c88a0ff31c78
  support: supports
  locator: Complete identity, names, chemical_data/default_structure, source origins
    and outgoing relations
  summary: CHEBI:61723 is D-pantetheine 4'-phosphate(2−), C11H21N2O7PS, charge −2.
    The sole stereocentre is specified as D/(R) at 2'; the two negative charges are
    on phosphate oxygens, with the terminal thiol still protonated. It has direct
    prosthetic-group role, stereounspecified parent CHEBI:47942, and neutral conjugate
    acid CHEBI:4222. The pH 7.3 major-microspecies sentence is authentic source text,
    not independently verified population evidence.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:61723
  accessed_at: '2026-10-21T10:56:19.573944Z'
  snapshot_sha256: c31414705eeb6d519796ac39861fc496f395c2e9ecfc96090c3f66c0629edfc1
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete identifier, definition, source synonym
    scopes and chemical annotations.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:23357 is the abstract cofactor biochemical role, not a molecular
    entity or a protein requirement; its outgoing parent is biochemical role CHEBI:52206.
- evidence_id: context-47942
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47942/
  accessed_at: '2026-10-21T10:57:06.908735Z'
  snapshot_sha256: 5e808d15fb753cddcd25c8fa08d7c9ad194e7212236d3fd1856ba8a5c0ce2db6
  support: supports
  locator: Complete definition, chemical data/structure and outgoing relations
  summary: CHEBI:47942 is stereounspecified pantetheine 4'-phosphate(2−), C11H21N2O7PS,
    with phosphate dianion and free thiol. It has cofactor and metabolite roles and
    is conjugate base of CHEBI:16858. Lack of stereochemical specification in the
    parent is not identity with the D-specific child.
- evidence_id: context-26348
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:57:07.526865Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Complete definition, chemical data/structure and outgoing relations
  summary: Prosthetic group CHEBI:26348 is a tightly bound, specific nonpolypeptide
    unit involved in protein activity and is-a cofactor CHEBI:23357. The role does
    not itself specify a free molecule versus a covalent protein moiety.
- evidence_id: context-4222
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/4222/
  accessed_at: '2026-10-21T10:56:20.215271Z'
  snapshot_sha256: 7b6b6477a8cdc31e34a736b3a32b52aeff9ac1ef3095cc25e2bcf3f94da1b210
  support: supports
  locator: Complete definition, chemical data/structure and outgoing relations
  summary: CHEBI:4222 is neutral D-pantetheine 4'-phosphate, C11H23N2O7PS, charge
    0, with one D/(R) stereocentre, a free terminal thiol and protonated phosphate
    monoester. It has direct prosthetic-group role, stereounspecified parent CHEBI:16858
    and dianionic conjugate base CHEBI:61723. It is a defined free chemical structure,
    not an automatically identical covalent protein adduct.
- evidence_id: primary-19933275
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19933275%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:57:07.761577Z'
  snapshot_sha256: e0a67ea72a597022a9462de7097c2da9bde046c21b91510aaf422a87be9f0992
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:19933275; DOI:10.1074/jbc.M109.080556. The complete abstract describes
    transfer of 4'-phosphopantetheine from CoA to a conserved serine and human PPT-mediated
    conversion of apo-FDH to catalytically active holo-FDH. The covalently attached
    swinging-arm prosthetic moiety is supported; the exact free neutral/dianionic
    chemical is not thereby shown to be the unchanged protein-bound state. No residue
    coordinate is asserted from this abstract.
- evidence_id: primary-19177367
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19177367%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:57:08.165085Z'
  snapshot_sha256: 84998cf9fdf73a7efd84bcd414fba857c86390424da46a67fa841c0153fa9ce4
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:19177367; DOI:10.1002/pro.11. The complete abstract compares apo-ACP,
    ACP and butyryl-ACP solution structures under identical conditions and reports
    conformational changes associated with the acyl intermediate. It supports bounded
    carrier-protein structural context, not an exact free phosphopantetheine protonation
    state or a general requirement for every protein.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  locator: Executed 2026-10-21T10:57:38Z through 2026-10-21T10:57:39Z; exit 0
  accessed_at: '2026-10-21T10:57:39Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/copper-1-chebi49552.yaml
    data/traits/function/cofactor_requirement/chebi/copper-2-chebi29036.yaml data/traits/function/cofactor_requirement/chebi/copper-cation-chebi23378.yaml
    data/traits/function/cofactor_requirement/chebi/corrin-chebi33221.yaml data/traits/function/cofactor_requirement/chebi/corrinoid-chebi33913.yaml
    data/traits/function/cofactor_requirement/chebi/ctp-chebi17677.yaml data/traits/function/cofactor_requirement/chebi/cu-chebi28694.yaml
    data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
    data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-chebi4222.yaml
    data/traits/function/cofactor_requirement/chebi/decylplastoquinone-chebi72953.yaml
  locator: Executed 2026-10-21T10:55:55Z through 2026-10-21T10:57:11Z; exit 0
  accessed_at: '2026-10-21T10:57:11Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
  locator: Executed 2026-10-21T10:57:39Z through 2026-10-21T10:57:39Z; exit 0
  accessed_at: '2026-10-21T10:57:39Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T10:57:11Z through 2026-10-21T10:57:12Z; exit 0
  accessed_at: '2026-10-21T10:57:12Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The exact formula, charge, D/(R) stereocentre, phosphate monoester and
    free thiol agree with the target chemical definition. The neutral/dianion pair
    differs by two phosphate protons, not a redox change or stereochemical inversion;
    the stereounspecified parent remains broader.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-4222
  - context-47942
  topic: Phosphopantetheine connectivity, charge and stereochemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The primary abstract supports phosphopantetheinyl transfer from CoA to
    a conserved protein serine and FDH activation. Covalent prosthetic-moiety evidence
    is distinguished from a requirement for an unchanged free neutral or dianionic
    molecule; ACP structural context does not settle that exact-state question.
  evidence_ids:
  - primary-19933275
  - primary-19177367
  - chemical
  topic: Covalent phosphopantetheine prosthetic-group evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-6
- area: evidence
  outcome: unknown
  summary: The source pH 7.3 major-microspecies assertion is faithfully copied, but
    no inspected primary equilibrium measurement independently establishes that population.
    The covalent protein moiety is a separate state question; lack of independent
    confirmation is not a demonstrated chemical contradiction.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - primary-19933275
  topic: Phosphate speciation and exact protein-bound state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-7
- area: provenance
  outcome: supported
  summary: The chemical definition and direct source role are traceable to current
    official ChEBI; the requirement wrapper is maintained ChEBI-seeder synthesis.
    Licence and current OLS comparison release are documented, while the exact seed
    release remains unknown.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - registry
  - owner
  topic: Definition and maintained-source provenance
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The captured local requirement parent resolves. Direct chemical role and
    role ancestry supply candidate class context; chemical is-a and conjugate relations
    are not protein-trait equivalence.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - schema
  - context-26348
  - local-ancestor
  topic: Requirement-parent and source-relation scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-9
- area: representation
  outcome: unknown
  summary: The record proposes a reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class.
    The exact activity-relative, non-substrate protein requirement remains unqualified;
    source chemical-role assertions or alignment labels alone do not supply that evidence.
    No optional example, mechanism or native status is promoted.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Protein requirement representation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The ChEBI chemical referent differs from the protein-requirement class,
    while xrefs asserts true own-source equivalence. A chemical association requires
    typed grounding after chemical-state and activity-relative role adjudication.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  topic: Chemical denotation versus protein-trait equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-61723.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical referent is asserted equivalent to a protein requirement
  description: The xref denotes a chemical entity while the local record denotes a
    protein functional requirement. Correct chemical identity or a source cofactor/prosthetic-group
    role would not establish equality of these classes.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Chemical denotation and protein-requirement denotation differ.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: 'change build in scripts/seed_chebi_cofactor.py to replace chemical-to-trait
    equality with an accurately typed chemical_participants association. Preserve
    CHEBI:61723 and its exact chemical-state scope. ChemicalParticipant.role is required:
    adjudicate the activity-relative role, including the category''s non-substrate
    scope, rather than treating a source role assertion as independently verified
    COFACTOR. Keep candidate provenance distinct from new protein qualification, and
    do not simply move equality to mapped_xrefs. Distinguish the free chemical from
    any covalently attached prosthetic moiety; do not silently equate their protonation
    or connectivity.'
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61723
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The source chemical association no longer asserts chemical-to-protein-trait equivalence;
    exact state and candidate source provenance remain auditable.
  - A focused source-transform fixture verifies identity and required role adjudication.
    Regeneration follows an audited route explicitly selecting existing records. No
    protein/status promotion or silent conjugate merge occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/d-pantetheine-4-phosphate-2-chebi61723.yaml.
    Run full just validate-all before merging record changes. Capture changed inputs
    and save a fresh validated review; do not overwrite this observation.
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
- PMC2804320 and PMC2708020 HTML captures were browser challenges; Europe PMC fullTextXML
  returned 500 and BioC returned 429. Those bodies are excluded as scientific support.
  The complete indexed abstracts support only the stated scope; no serine residue
  coordinate or full-paper result is claimed.
- The pH 7.3 population claim remains independently unresolved; no pKa, numerical
  abundance or universal intracellular state is inferred. This is a bounded evidence
  limitation rather than an additional proven defect.
tags:
- unreviewed-path-order
- batch-017
- chebi-cofactor
```
