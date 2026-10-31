# Review of Vitamin A

- Review: 20261021T083945Z-vitamin-a-kw-0845
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:29:45Z
- Finished UTC: 2026-10-21T08:39:45Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Vitamin A broad-class identity is supported. Retinal-binding xref equality and the exact Retinol alias are two major scope defects; exclusive beta-carotene background is one minor wording issue.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 008. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5 covers 68 record paths, leaving 429291 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0845 | data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml | generated | Vitamin A |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0845 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0845 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0845 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0845 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0845 | KW-0845, Ligand parent and GO:0016918 resolve; the GO reference is authentic but not equivalent in scope. ChEBI entities and NIH source resolve. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0845.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0845.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0845.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0845.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0845.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0845.

KW-0845 explicitly covers proteins interacting with any vitamin-A form, including retinol, retinal and retinoic acid. This broad class identity is clear despite overly narrow asserted equivalents.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0845.

Only the Ligand category is an immediate source parent. Omission of a category-root link follows the maintained generator policy.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0845.

The source defines interaction with a ligand group, supporting FUNCTION; the main problem is the scope of the claimed equivalents, not conversion to a site representation.

### Grounding

grounding: concern. Targets: UniProtKB-KW:KW-0845.

The own-source GO association is authentic, but retinal binding is narrower than the target any-form class. GO itself marks vitamin A binding as broader, contrary to true equivalence in xrefs.

### Nomenclature

nomenclature: concern. Targets: UniProtKB-KW:KW-0845.

Retinol is one explicit constituent of the target ligand group. The source untyped alias has been strengthened into EXACT_SYNONYM despite the declared broader target scope. Historical vitamin-A/retinol naming remains acknowledged.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0845.

Beta-carotene is a valid precursor, but the exclusive precursor wording omits other documented provitamin-A routes.

## Findings

### F1: Retinal-binding GO mapping is narrower than the target class

major / open / confirmed; issue key: uniprot-keyword.KW-0845.retinal-go-equivalence.

The target explicitly includes interaction with multiple vitamin-A forms, while GO:0016918 denotes retinal binding and marks vitamin A binding as a broad synonym. Copying the source association into xrefs therefore asserts true equality between a broad trait and a narrower binding class.

### F2: Retinol alias collapses the explicitly broader vitamer class

major / open / confirmed; issue key: uniprot-keyword.KW-0845.retinol-exact-alias.

The source definition lists retinol alongside retinal and retinoic acid, yet the emitted synonym marks Retinol EXACT_SYNONYM. Under this explicit any-form trait definition, one constituent ligand is not an exact label for the entire class. Historical chemical naming does not resolve the contextual scope conflict.

### F3: Avoid exclusive beta-carotene precursor wording

minor / open / confirmed; issue key: uniprot-keyword.KW-0845.beta-carotene-only-background.

The copied background says all forms derive from plant beta-carotene. The inspected authority describes other convertible provitamin-A carotenoids and preformed vitamin-A sources; beta-carotene should be one supported route rather than an exclusive origin statement.

## Recommended Actions And Acceptance Checks

### A1

Revise the maintained mapping transform to preserve the source association with correct scope rather than true equivalence. Do not narrow the target to retinal or blindly relabel an own-source association as an external mapping product.

- Retain the full source vitamin-A class and association provenance.
- Represent the narrower retinal relation with explicit supported semantics; do not use xrefs as equality here.
- Regenerate, validate and save a new scoped review.

### A2

Preserve the source alias with a narrower or related scope justified by the broad keyword definition, using the maintained synonym transform rather than hand-editing the emitted record.

- Retinol remains traceable to the own-source alias without being asserted exactly equivalent to the broad class.
- Retain all supported vitamin-A forms; do not infer all-trans-only scope.
- Test the transform, regenerate and validate.

### A3

Qualify the maintained background to include multiple precursor/dietary routes while retaining beta-carotene as a valid example and original source provenance.

- Do not imply that beta-carotene is the sole precursor/source route.
- Preserve the ligand-group definition and validate regenerated wording.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0845.json; Inspected source response captured at the recorded UTC time | supports | Complete official keyword response confirms accession, label, copied definition, source aliases and GO associations where present, and sole immediate Ligand parent. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The Ligand category includes binding, association and activity dependence; its meaning is broader than direct binding capacity. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0016918; Inspected source response captured at the recorded UTC time | supports | Nonobsolete GO:0016918 denotes retinal binding. Its vitamin A binding synonym is explicitly BROAD; retinaldehyde binding is exact. |
| vitamin-group | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:12777; Inspected source response captured at the recorded UTC time | supports | ChEBI:12777 identifies vitamin A as a group of biologically active retinoids, supporting a vitamer-group concept. |
| retinol | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17336; Inspected source response captured at the recorded UTC time | supports | ChEBI:17336 identifies all-trans-retinol and retains historical vitamin-A names. Those lexical usages do not make every vitamin-A form retinol under the target explicit broad definition. |
| retinal | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17898; Inspected source response captured at the recorded UTC time | supports | ChEBI:17898 identifies all-trans-retinal, a distinct retinal chemical entity. This example does not restrict the GO class to all-trans isomers. |
| vitamin-authority | https://ods.od.nih.gov/factsheets/VitaminA-HealthProfessional/; Introduction: vitamin-A forms, dietary sources and conversion pathways; no dosing guidance used | supports | NIH Office of Dietary Supplements describes preformed retinol/retinyl esters and multiple provitamin-A carotenoids, including alpha-carotene and beta-cryptoxanthin as well as beta-carotene. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml; Executed 2026-10-21T08:30:34Z through 2026-10-21T08:30:40Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml data/traits/function/binding_capacity/uniprot_keywords/sodium-kw-0915.yaml data/traits/function/binding_capacity/uniprot_keywords/steroid-binding-kw-0754.yaml data/traits/function/binding_capacity/uniprot_keywords/thiamine-pyrophosphate-kw-0786.yaml data/traits/function/binding_capacity/uniprot_keywords/tungsten-kw-0826.yaml data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml data/traits/function/binding_capacity/uniprot_keywords/vanadium-kw-0837.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-c-kw-0847.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-d-kw-0848.yaml; Executed 2026-10-21T08:29:58Z through 2026-10-21T08:33:41Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml; Executed 2026-10-21T08:30:40Z through 2026-10-21T08:30:41Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:33:41Z through 2026-10-21T08:33:43Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- Retinol and retinal chemical examples establish distinct forms, not exclusive isomer-specific protein binding. This review makes no nutritional or clinical recommendations and does not qualify individual proteins.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T083945Z-vitamin-a-kw-0845
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Vitamin A
started_at: '2026-10-21T08:29:45Z'
finished_at: '2026-10-21T08:39:45Z'
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
summary: Vitamin A broad-class identity is supported. Retinal-binding xref equality
  and the exact Retinol alias are two major scope defects; exclusive beta-carotene
  background is one minor wording issue.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
    sha256: 4ca1543053235c276196c76d06b133927f0dbf8dc691af88fe2ce3d61f102479
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
  - path: scripts/seed_uniprot_keywords.py
    sha256: 8b21fb8f61aea278c593f5afd22f0d137f159d66a75dad1067cc8eca44def576
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 8 in batch 008. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc
    and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5
    covers 68 record paths, leaving 429291 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0845
targets:
- kind: generated
  label: Vitamin A
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0845
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0845
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
    data/traits/function/binding_capacity/uniprot_keywords/sodium-kw-0915.yaml data/traits/function/binding_capacity/uniprot_keywords/steroid-binding-kw-0754.yaml
    data/traits/function/binding_capacity/uniprot_keywords/thiamine-pyrophosphate-kw-0786.yaml
    data/traits/function/binding_capacity/uniprot_keywords/tungsten-kw-0826.yaml data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vanadium-kw-0837.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vitamin-c-kw-0847.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vitamin-d-kw-0848.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0845
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0845
  evidence_ids:
  - validation-3
- check_id: gate-4
  name: Curation history validity
  command: just validate-history
  exit_code: 0
  status: passed
  required: true
  summary: Full history gate; this review adds no history event.
  target_ids:
  - UniProtKB-KW:KW-0845
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: KW-0845, Ligand parent and GO:0016918 resolve; the GO reference is authentic
    but not equivalent in scope. ChEBI entities and NIH source resolve.
  target_ids:
  - UniProtKB-KW:KW-0845
  evidence_ids:
  - keyword
  - parent
  - go
  - vitamin-group
  - retinol
  - retinal
  - vitamin-authority
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:29:45Z'
  snapshot_sha256: 4ca1543053235c276196c76d06b133927f0dbf8dc691af88fe2ce3d61f102479
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T08:29:45Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct
    from localized sequence binding sites. parent_traits are broader classes; xrefs
    assert true source-direct equivalents. Optional examples and graphs are not mandatory
    for this class.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_uniprot_keywords.py
  locator: route, immediate_parent, build_yaml, main
  accessed_at: '2026-10-21T08:29:45Z'
  snapshot_sha256: 8b21fb8f61aea278c593f5afd22f0d137f159d66a75dad1067cc8eca44def576
  support: supports
  summary: Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied;
    first immediate parent only is retained if seeded; untyped source aliases become
    EXACT_SYNONYM and source GO associations become xrefs.
- evidence_id: licence
  kind: authority
  reference: https://rest.uniprot.org/help/license
  accessed_at: '2026-10-21T06:55:09.358488Z'
  snapshot_sha256: 5960c22bf17f22286504b927dbb3ca41713c571ed91a10fe7a88ddd964b416ce
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: UniProt permits copyrightable database content under Creative Commons Attribution
    4.0; the record licence is compatible.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0845.json
  accessed_at: '2026-10-21T08:30:14.411466Z'
  snapshot_sha256: 8e50c33ab6162c96b647d72a4b6d38c835bcd74c8fd02a1bb6ed8a725640608b
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Complete official keyword response confirms accession, label, copied definition,
    source aliases and GO associations where present, and sole immediate Ligand parent.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The Ligand category includes binding, association and activity dependence;
    its meaning is broader than direct binding capacity.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0016918
  accessed_at: '2026-10-21T08:30:39.595522Z'
  snapshot_sha256: a813ef0490092230112ae3eb9530301f50c88b06555db9ecd00daf0bf380a994
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0016918 denotes retinal binding. Its vitamin A binding synonym
    is explicitly BROAD; retinaldehyde binding is exact.
- evidence_id: vitamin-group
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:12777
  accessed_at: '2026-10-21T08:30:39.597590Z'
  snapshot_sha256: 0fb1c513cdcd87336f3ccbb21f5e8818bd5ca1b893380f1d9708bc7e5273b6fc
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: ChEBI:12777 identifies vitamin A as a group of biologically active retinoids,
    supporting a vitamer-group concept.
- evidence_id: retinol
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17336
  accessed_at: '2026-10-21T08:30:39.597738Z'
  snapshot_sha256: 03dc80ba04a07158001f20afec37d45fb8fbdcbf1aa191a5c4f9ac6c537a6ee3
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: ChEBI:17336 identifies all-trans-retinol and retains historical vitamin-A
    names. Those lexical usages do not make every vitamin-A form retinol under the
    target explicit broad definition.
- evidence_id: retinal
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17898
  accessed_at: '2026-10-21T08:30:39.597869Z'
  snapshot_sha256: 482aea1ef01515335101da59775474f181c99dfb80534953d56b673c9b8bf7d9
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: ChEBI:17898 identifies all-trans-retinal, a distinct retinal chemical entity.
    This example does not restrict the GO class to all-trans isomers.
- evidence_id: vitamin-authority
  kind: authority
  reference: https://ods.od.nih.gov/factsheets/VitaminA-HealthProfessional/
  accessed_at: '2026-10-21T08:31:29.921865Z'
  snapshot_sha256: c6ec4bb5a05f2fa2228badb0e58081e077d8fdd7d250a1a820cf83e2f5459225
  support: supports
  locator: 'Introduction: vitamin-A forms, dietary sources and conversion pathways;
    no dosing guidance used'
  summary: NIH Office of Dietary Supplements describes preformed retinol/retinyl esters
    and multiple provitamin-A carotenoids, including alpha-carotene and beta-cryptoxanthin
    as well as beta-carotene.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  locator: Executed 2026-10-21T08:30:34Z through 2026-10-21T08:30:40Z; exit 0
  accessed_at: '2026-10-21T08:30:40Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
    data/traits/function/binding_capacity/uniprot_keywords/sodium-kw-0915.yaml data/traits/function/binding_capacity/uniprot_keywords/steroid-binding-kw-0754.yaml
    data/traits/function/binding_capacity/uniprot_keywords/thiamine-pyrophosphate-kw-0786.yaml
    data/traits/function/binding_capacity/uniprot_keywords/tungsten-kw-0826.yaml data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vanadium-kw-0837.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vitamin-c-kw-0847.yaml
    data/traits/function/binding_capacity/uniprot_keywords/vitamin-d-kw-0848.yaml
  locator: Executed 2026-10-21T08:29:58Z through 2026-10-21T08:33:41Z; exit 0
  accessed_at: '2026-10-21T08:33:41Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml
  locator: Executed 2026-10-21T08:30:40Z through 2026-10-21T08:30:41Z; exit 0
  accessed_at: '2026-10-21T08:30:41Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T08:33:41Z through 2026-10-21T08:33:43Z; exit 0
  accessed_at: '2026-10-21T08:33:43Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: The maintained UniProt keyword seeder owns future changes; this review
    does not modify emitted records.
  evidence_ids:
  - owner
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-1
  topic: Ownership
- area: provenance
  outcome: supported
  summary: Source identity and CC-BY 4.0 attribution are present. Current official
    source release is 2026_03; the original seed release is not claimed to be established.
  evidence_ids:
  - record
  - licence
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-2
  topic: Provenance
- area: completeness
  outcome: supported
  summary: This is a class record, with no instance sequence or specimen substituted
    for a trait. Optional motifs, structures, detection methods and canonical examples
    are not automatically required for this keyword.
  evidence_ids:
  - record
  - schema
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: KW-0845 explicitly covers proteins interacting with any vitamin-A form,
    including retinol, retinal and retinoic acid. This broad class identity is clear
    despite overly narrow asserted equivalents.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-6
  topic: Identity
- area: consistency
  outcome: supported
  summary: Only the Ligand category is an immediate source parent. Omission of a category-root
    link follows the maintained generator policy.
  evidence_ids:
  - record
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: supported
  summary: The source defines interaction with a ligand group, supporting FUNCTION;
    the main problem is the scope of the claimed equivalents, not conversion to a
    site representation.
  evidence_ids:
  - record
  - keyword
  - schema
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-8
  topic: Representation
- area: grounding
  outcome: concern
  summary: The own-source GO association is authentic, but retinal binding is narrower
    than the target any-form class. GO itself marks vitamin A binding as broader,
    contrary to true equivalence in xrefs.
  evidence_ids:
  - record
  - keyword
  - go
  - schema
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-9
  topic: Grounding
- area: nomenclature
  outcome: concern
  summary: Retinol is one explicit constituent of the target ligand group. The source
    untyped alias has been strengthened into EXACT_SYNONYM despite the declared broader
    target scope. Historical vitamin-A/retinol naming remains acknowledged.
  evidence_ids:
  - record
  - keyword
  - vitamin-group
  - retinol
  - retinal
  - owner
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: Beta-carotene is a valid precursor, but the exclusive precursor wording
    omits other documented provitamin-A routes.
  evidence_ids:
  - record
  - keyword
  - vitamin-authority
  target_ids:
  - UniProtKB-KW:KW-0845
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0845.retinal-go-equivalence
  category: grounding
  severity: major
  title: Retinal-binding GO mapping is narrower than the target class
  description: The target explicitly includes interaction with multiple vitamin-A
    forms, while GO:0016918 denotes retinal binding and marks vitamin A binding as
    a broad synonym. Copying the source association into xrefs therefore asserts true
    equality between a broad trait and a narrower binding class.
  evidence_ids:
  - record
  - keyword
  - go
  - schema
  - owner
  normalization_reason: The xref materially asserts equality with a narrower function
    despite explicit broader-synonym evidence in GO.
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: uniprot-keyword.KW-0845.retinol-exact-alias
  category: nomenclature
  severity: major
  title: Retinol alias collapses the explicitly broader vitamer class
  description: The source definition lists retinol alongside retinal and retinoic
    acid, yet the emitted synonym marks Retinol EXACT_SYNONYM. Under this explicit
    any-form trait definition, one constituent ligand is not an exact label for the
    entire class. Historical chemical naming does not resolve the contextual scope
    conflict.
  evidence_ids:
  - record
  - keyword
  - vitamin-group
  - retinol
  - retinal
  - owner
  normalization_reason: An exact-synonym assertion materially collapses one explicitly
    included ligand form into the broader trait class.
  finding_id: F2
  status: open
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: uniprot-keyword.KW-0845.beta-carotene-only-background
  category: scope
  severity: minor
  title: Avoid exclusive beta-carotene precursor wording
  description: The copied background says all forms derive from plant beta-carotene.
    The inspected authority describes other convertible provitamin-A carotenoids and
    preformed vitamin-A sources; beta-carotene should be one supported route rather
    than an exclusive origin statement.
  evidence_ids:
  - record
  - keyword
  - vitamin-authority
  - owner
  finding_id: F3
  status: open
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, hierarchy completeness
    or interpretation needs follow-up.
actions:
- action_id: A1
  description: Revise the maintained mapping transform to preserve the source association
    with correct scope rather than true equivalence. Do not narrow the target to retinal
    or blindly relabel an own-source association as an external mapping product.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Retain the full source vitamin-A class and association provenance.
  - Represent the narrower retinal relation with explicit supported semantics; do
    not use xrefs as equality here.
  - Regenerate, validate and save a new scoped review.
- action_id: A2
  description: Preserve the source alias with a narrower or related scope justified
    by the broad keyword definition, using the maintained synonym transform rather
    than hand-editing the emitted record.
  finding_ids:
  - F2
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Retinol remains traceable to the own-source alias without being asserted exactly
    equivalent to the broad class.
  - Retain all supported vitamin-A forms; do not infer all-trans-only scope.
  - Test the transform, regenerate and validate.
- action_id: A3
  description: Qualify the maintained background to include multiple precursor/dietary
    routes while retaining beta-carotene as a valid example and original source provenance.
  finding_ids:
  - F3
  target_ids:
  - UniProtKB-KW:KW-0845
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Do not imply that beta-carotene is the sole precursor/source route.
  - Preserve the ligand-group definition and validate regenerated wording.
limitations:
- The original keywlist release used in the July seed is not recoverable from this
  record. Current API release 2026_03 is a comparison snapshot, not an asserted historical
  seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle
  retains URLs, access times, digests and bounded observations, not full response
  bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are
  qualified. iModulonDB is not applicable to this generic ligand class without a gene,
  organism or expression dataset.
- Retinol and retinal chemical examples establish distinct forms, not exclusive isomer-specific
  protein binding. This review makes no nutritional or clinical recommendations and
  does not qualify individual proteins.
tags:
- unreviewed-path-order
- batch-008
- uniprot-keywords
```
