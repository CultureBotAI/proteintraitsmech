# Review of group transfer coenzymes cofactor class

- Review: 20261021T123806Z-group-transfer-coenzymes-chebi24430
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:31:23Z
- Finished UTC: 2026-10-21T12:38:06Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The group-transfer coenzyme role and broader local coenzyme-requirement parent resolve. One confirmed major finding concerns biochemical-role-to-protein-requirement equivalence. The repair preserves role provenance and does not put a role identifier into a concrete chemical participant field.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 023. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5) covers 218 record paths, leaving 429141 before this batch. 23 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml | generated | group transfer coenzymes cofactor class |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24430 | CHEBI:24430 resolves as a nonobsolete role under coenzyme, with the coenzyme/cofactor/biochemical-role chain inspected. The review confirms source resolution while rejecting role-to-protein-requirement equivalence. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The local identifier and role-class label denote a proposed abstract requirement class rather than an individual protein or concrete coenzyme. No fixed formula, chemical participant, mandatory example or causal graph is required for this role-level representation.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Group-transfer coenzyme role and requirement-class identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The source accession and local role label resolve to the group-transfer coenzyme role under coenzyme. The short synthesized requirement text does not denote one molecule. Null source definition and fixed chemistry are faithfully preserved rather than treated as evidence of a missing molecule.

### Source role hierarchy and bounded class meaning

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The current official role hierarchy supports the group-transfer/coenzyme relationship. The parent definition supplies acceptor/donor context. This source evidence supports an abstract candidate class but does not qualify a particular protein, a complete list of coenzymes, or a mechanism.

### Broader coenzyme-requirement parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The captured local coenzyme-requirement parent corresponds to the direct source role parent. This supports the intended broader requirement relationship while leaving each role-to-requirement xref separately assessable.

### Role-based class membership and non-substrate scope

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

No activity-specific protein qualification is supplied, and coenzyme donor/acceptor roles can involve different catalytic participation. The source role does not by itself establish every member as a non-substrate requirement. Retain explicit class scope and uncertainty without inventing a concrete chemical participant or treating an absent optional example as a defect.

### Role-derived ChEBI source transformation

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

The maintained role branch explains the requirement wrapper and inherited source attribution. Official accession, role ancestry and ChEBI licence resolve; no source prose definition or original seed release is invented.

### Source role versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24430.

CHEBI:24430 is the group-transfer coenzyme role under coenzyme, whereas the local record denotes a protein requirement for that role-bearing coenzyme class. The current xrefs slot asserts true own-source equivalence, which this role-to-requirement transformation does not establish. The source role is not a concrete chemical participant.

## Findings

### F1: Biochemical role is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-24430.role-requirement-equivalence.

CHEBI:24430 is the group-transfer coenzyme role under coenzyme, whereas the local record denotes a protein requirement for that role-bearing coenzyme class. The current xrefs slot asserts true own-source equivalence, which this role-to-requirement transformation does not establish. The source role is not a concrete chemical participant.

## Recommended Actions And Acceptance Checks

### A1

Update the role branch of build in scripts/seed_chebi_cofactor.py to remove the false role-to-protein-class equivalence while preserving the requirement definition and broader local coenzyme-requirement parent. Retain CHEBI:24430 as definition_source or another supported provenance reference. Leave chemical_participants absent for this abstract role unless separately supported concrete chemical entities and activity-relative roles are introduced; never put CHEBI:24430 into a chemical-entity participant slot. Do not move the equality to mapped_xrefs or invent an unsupported relation predicate.

- The regenerated xrefs no longer equate the source chemical or biochemical role with the protein requirement. Provenance and the intended requirement scope remain explicit; optional participant absence is not itself a defect.
- The group-transfer role remains a role reference, never a concrete chemical participant. No chemical formula, mandatory member exemplar or universal activity claim is invented for the abstract class.
- Run just validate data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml after the scoped repair.
- For maintained writer changes add focused pytest coverage and run just audit-writers, just lint and just test. Regenerate the existing target through an audited route. Run full just validate-all before merging record changes; capture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml; Entire target YAML | supports | Entire role-derived target YAML inspected: local requirement identifier and role-class label, short synthesized requirement definition, coenzyme-requirement parent, biochemical-role xref, CLASS/SEEDED status and ChEBI licence. This is an abstract requirement class, not a concrete molecule or protein example. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations traverses the cofactor role subtree; the is_role branch of build synthesizes a role-derived requirement label/definition and emits the ChEBI role as xrefs. The role and a protein requirement for its bearers have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The inspected official Introduction and Licensing sections establish ChEBI chemical-entity/role scope and CC BY 4.0 licensing. This supports ChEBI attribution, not chemical-to-protein equivalence or licensing of an uninspected MGA table. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Original access time and digest are preserved. This is distinct from the live backend and does not identify the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24430/; Exact identity, names, definition or null, formula/charge, structure and complete outgoing relations; incoming relations inspected for target scope | supports | CHEBI:24430 is the nonobsolete group transfer coenzymes role, a direct child of coenzyme CHEBI:23354. The current entry has one star, a null definition, no fixed chemical data/default structure, no incoming relations and no linked primary citations. Its role hierarchy is resolved; empty chemical fields are appropriate to this abstract role. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:24430; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:24430 as nonobsolete. Its actual names, definition or empty description, and available chemical annotations were inspected; a null field is not filled by assumption. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Exact identity, names, definition or null, formula/charge, structure and complete outgoing relations; incoming relations inspected for target scope | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, under biochemical role CHEBI:52206. This role is distinct from a protein class requiring a cofactor. |
| coenzyme-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Exact identity, names, definition or null, formula/charge, structure and complete outgoing relations; incoming relations inspected for target scope | supports | Coenzyme CHEBI:23354 is a biochemical role for a low-molecular-weight nonprotein compound participating as a dissociable acceptor or donor of groups or electrons; its direct parent is cofactor. CHEBI:24430 specializes the group-transfer side by its source label and role ancestry, not by a separately supplied prose definition. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Exact identity, names, definition or null, formula/charge, structure and complete outgoing relations; incoming relations inspected for target scope | supports | Biochemical role CHEBI:52206 is a biological role played by a molecular entity or part within a biochemical context. This confirms the role ancestry rather than a fixed chemical entity identity. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml; Executed 2026-10-21T12:32:04Z through 2026-10-21T12:32:07Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml; Executed 2026-10-21T12:31:57Z through 2026-10-21T12:33:46Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml; Executed 2026-10-21T12:32:07Z through 2026-10-21T12:32:07Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:33:46Z through 2026-10-21T12:33:47Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A biochemical-role hierarchy supports a candidate requirement-class concept, not a particular protein, exhaustive member list or universal non-substrate activity. No concrete chemical identity or protein qualification is asserted for this role.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record observation does not certify the broader role hierarchy or parent xrefs. No organism, gene or expression dataset is asserted; iModulonDB is not applicable to the reviewed role-class claim.
- The official role entry has no definition or primary citation in the inspected responses. The review relies on actual identity and parent-role text, not an invented experimental demonstration or an exhaustive literature-negative claim.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T123806Z-group-transfer-coenzymes-chebi24430
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of group transfer coenzymes cofactor class
started_at: '2026-10-21T12:31:23Z'
finished_at: '2026-10-21T12:38:06Z'
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
summary: The group-transfer coenzyme role and broader local coenzyme-requirement parent
  resolve. One confirmed major finding concerns biochemical-role-to-protein-requirement
  equivalence. The repair preserves role provenance and does not put a role identifier
  into a concrete chemical participant field.
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
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    sha256: 3e9fe8a126c6949fc0a6b894f633779022efa28882e5eca3d202dd6e33ffa7e9
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
  selection: Path-order position 3 in batch 023. Fresh main inventory has 429359 records;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5) covers 218 record paths,
    leaving 429141 before this batch. 23 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
targets:
- kind: generated
  label: group transfer coenzymes cofactor class
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_24430
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml
    data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:24430 resolves as a nonobsolete role under coenzyme, with the coenzyme/cofactor/biochemical-role
    chain inspected. The review confirms source resolution while rejecting role-to-protein-requirement
    equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  evidence_ids:
  - licence
  - release
  - chemical
  - chemical-ontology
  - cofactor-role
  - coenzyme-role
  - biochemical-role
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:31:23Z'
  snapshot_sha256: 3e9fe8a126c6949fc0a6b894f633779022efa28882e5eca3d202dd6e33ffa7e9
  support: supports
  summary: 'Entire role-derived target YAML inspected: local requirement identifier
    and role-class label, short synthesized requirement definition, coenzyme-requirement
    parent, biochemical-role xref, CLASS/SEEDED status and ChEBI licence. This is
    an abstract requirement class, not a concrete molecule or protein example.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T12:31:23Z'
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
  accessed_at: '2026-10-21T12:31:23Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: load_relations traverses the cofactor role subtree; the is_role branch
    of build synthesizes a role-derived requirement label/definition and emits the
    ChEBI role as xrefs. The role and a protein requirement for its bearers have different
    denotations.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T12:31:23Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:31:23Z'
  snapshot_sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
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
  summary: The inspected official Introduction and Licensing sections establish ChEBI
    chemical-entity/role scope and CC BY 4.0 licensing. This supports ChEBI attribution,
    not chemical-to-protein equivalence or licensing of an uninspected MGA table.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Original access time and digest are preserved. This is distinct from the live
    backend and does not identify the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24430/
  accessed_at: '2026-10-21T12:32:16.854170Z'
  snapshot_sha256: 30299f769e0fbd10c6bd48ad9b29df0405f275bd94a9769ca907ab2625aa134c
  support: supports
  locator: Exact identity, names, definition or null, formula/charge, structure and
    complete outgoing relations; incoming relations inspected for target scope
  summary: CHEBI:24430 is the nonobsolete group transfer coenzymes role, a direct
    child of coenzyme CHEBI:23354. The current entry has one star, a null definition,
    no fixed chemical data/default structure, no incoming relations and no linked
    primary citations. Its role hierarchy is resolved; empty chemical fields are appropriate
    to this abstract role.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:24430
  accessed_at: '2026-10-21T12:32:17.268907Z'
  snapshot_sha256: 5d1c5c593d217763b2404b28ab1f701850265507776c18c0e61c9e99952cac85
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:24430 as nonobsolete. Its actual names, definition or
    empty description, and available chemical annotations were inspected; a null field
    is not filled by assumption.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Exact identity, names, definition or null, formula/charge, structure and
    complete outgoing relations; incoming relations inspected for target scope
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity, under biochemical role CHEBI:52206. This role is
    distinct from a protein class requiring a cofactor.
- evidence_id: coenzyme-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T11:38:19.854129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Exact identity, names, definition or null, formula/charge, structure and
    complete outgoing relations; incoming relations inspected for target scope
  summary: Coenzyme CHEBI:23354 is a biochemical role for a low-molecular-weight nonprotein
    compound participating as a dissociable acceptor or donor of groups or electrons;
    its direct parent is cofactor. CHEBI:24430 specializes the group-transfer side
    by its source label and role ancestry, not by a separately supplied prose definition.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Exact identity, names, definition or null, formula/charge, structure and
    complete outgoing relations; incoming relations inspected for target scope
  summary: Biochemical role CHEBI:52206 is a biological role played by a molecular
    entity or part within a biochemical context. This confirms the role ancestry rather
    than a fixed chemical entity identity.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  locator: Executed 2026-10-21T12:32:04Z through 2026-10-21T12:32:07Z; exit 0
  accessed_at: '2026-10-21T12:32:07Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml
    data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml
  locator: Executed 2026-10-21T12:31:57Z through 2026-10-21T12:33:46Z; exit 0
  accessed_at: '2026-10-21T12:33:46Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
  locator: Executed 2026-10-21T12:32:07Z through 2026-10-21T12:32:07Z; exit 0
  accessed_at: '2026-10-21T12:32:07Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:33:46Z through 2026-10-21T12:33:47Z; exit 0
  accessed_at: '2026-10-21T12:33:47Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: supported
  summary: The local identifier and role-class label denote a proposed abstract requirement
    class rather than an individual protein or concrete coenzyme. No fixed formula,
    chemical participant, mandatory example or causal graph is required for this role-level
    representation.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source accession and local role label resolve to the group-transfer
    coenzyme role under coenzyme. The short synthesized requirement text does not
    denote one molecule. Null source definition and fixed chemistry are faithfully
    preserved rather than treated as evidence of a missing molecule.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - coenzyme-role
  topic: Group-transfer coenzyme role and requirement-class identity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The current official role hierarchy supports the group-transfer/coenzyme
    relationship. The parent definition supplies acceptor/donor context. This source
    evidence supports an abstract candidate class but does not qualify a particular
    protein, a complete list of coenzymes, or a mechanism.
  evidence_ids:
  - chemical
  - coenzyme-role
  - cofactor-role
  - biochemical-role
  topic: Source role hierarchy and bounded class meaning
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-6
- area: consistency
  outcome: supported
  summary: The captured local coenzyme-requirement parent corresponds to the direct
    source role parent. This supports the intended broader requirement relationship
    while leaving each role-to-requirement xref separately assessable.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - coenzyme-role
  topic: Broader coenzyme-requirement parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: No activity-specific protein qualification is supplied, and coenzyme donor/acceptor
    roles can involve different catalytic participation. The source role does not
    by itself establish every member as a non-substrate requirement. Retain explicit
    class scope and uncertainty without inventing a concrete chemical participant
    or treating an absent optional example as a defect.
  evidence_ids:
  - record
  - schema
  - chemical
  - coenzyme-role
  topic: Role-based class membership and non-substrate scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The maintained role branch explains the requirement wrapper and inherited
    source attribution. Official accession, role ancestry and ChEBI licence resolve;
    no source prose definition or original seed release is invented.
  evidence_ids:
  - record
  - owner
  - chemical
  - chemical-ontology
  - licence
  - release
  topic: Role-derived ChEBI source transformation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: CHEBI:24430 is the group-transfer coenzyme role under coenzyme, whereas
    the local record denotes a protein requirement for that role-bearing coenzyme
    class. The current xrefs slot asserts true own-source equivalence, which this
    role-to-requirement transformation does not establish. The source role is not
    a concrete chemical participant.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  topic: Source role versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-24430.role-requirement-equivalence
  category: grounding
  severity: major
  title: Biochemical role is asserted equivalent to a protein requirement
  description: CHEBI:24430 is the group-transfer coenzyme role under coenzyme, whereas
    the local record denotes a protein requirement for that role-bearing coenzyme
    class. The current xrefs slot asserts true own-source equivalence, which this
    role-to-requirement transformation does not establish. The source role is not
    a concrete chemical participant.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - definition_source
  normalization_reason: The source denotation and the synthesized protein-requirement
    class are distinct. This is a major grounding defect even when identity and biological
    relevance are supported; it is not a finding about an absent optional representation.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update the role branch of build in scripts/seed_chebi_cofactor.py to
    remove the false role-to-protein-class equivalence while preserving the requirement
    definition and broader local coenzyme-requirement parent. Retain CHEBI:24430 as
    definition_source or another supported provenance reference. Leave chemical_participants
    absent for this abstract role unless separately supported concrete chemical entities
    and activity-relative roles are introduced; never put CHEBI:24430 into a chemical-entity
    participant slot. Do not move the equality to mapped_xrefs or invent an unsupported
    relation predicate.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24430
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated xrefs no longer equate the source chemical or biochemical role
    with the protein requirement. Provenance and the intended requirement scope remain
    explicit; optional participant absence is not itself a defect.
  - The group-transfer role remains a role reference, never a concrete chemical participant.
    No chemical formula, mandatory member exemplar or universal activity claim is
    invented for the abstract class.
  - Run just validate data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    after the scoped repair.
  - For maintained writer changes add focused pytest coverage and run just audit-writers,
    just lint and just test. Regenerate the existing target through an audited route.
    Run full just validate-all before merging record changes; capture changed inputs
    and save a fresh structured review without overwriting this observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- A biochemical-role hierarchy supports a candidate requirement-class concept, not
  a particular protein, exhaustive member list or universal non-substrate activity.
  No concrete chemical identity or protein qualification is asserted for this role.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record observation does not certify the broader role hierarchy or parent
  xrefs. No organism, gene or expression dataset is asserted; iModulonDB is not applicable
  to the reviewed role-class claim.
- The official role entry has no definition or primary citation in the inspected responses.
  The review relies on actual identity and parent-role text, not an invented experimental
  demonstration or an exhaustive literature-negative claim.
tags:
- unreviewed-path-order
- batch-023
- chebi-cofactor
```
