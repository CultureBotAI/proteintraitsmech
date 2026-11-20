# Review of Pigment

- Review: 20261021T082314Z-pigment-kw-0608
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:17:43Z
- Finished UTC: 2026-10-21T08:23:14Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

Pigment identity and the source GO association are supported. One copied grammar defect is confirmed; transport-versus-binding equivalence remains a provisional interpretation question.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 007. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 covers 58 record paths, leaving 429301 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0608 | data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml | generated | Pigment |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0608 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0608 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0608 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0608 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0608 | KW-0608, its Ligand parent and directly asserted GO:0031409 resolve. The GO mapping provenance is verified; whole-class equivalence remains explicitly provisional. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0608.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0608.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0608.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0608.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0608.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0608.

KW-0608 denotes a protein trait associated with pigments, not a pigment molecule or an individual protein. Source accession, label and definition agree.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0608.

The current source has only the Ligand category as immediate parent. Omitting a category-root parent follows the maintained seeder policy; no missing seeded parent is established.

### Grounding

grounding: concern. Targets: UniProtKB-KW:KW-0608.

The asserted GO term is authentic and fits pigment binding. The keyword also explicitly includes transport, so complete class equivalence and binding-only routing need a bounded interpretation check. This review establishes no nonbinding member.

### Nomenclature

nomenclature: concern. Targets: UniProtKB-KW:KW-0608.

The copied verb phrase has singular subject/verb disagreement; this does not alter the target identity.

## Findings

### F1: Clarify transport scope before treating the GO mapping as equivalence

minor / open / provisional; issue key: uniprot-keyword.KW-0608.transport-binding-scope.

The keyword has binding and transport alternatives, while GO:0031409 describes pigment binding. The textual scopes differ, but transport may require direct binding; actual non-equivalence is not established.

### F2: Correct copied subject–verb agreement

minor / open / confirmed; issue key: uniprot-keyword.KW-0608.definition-verb-agreement.

The source and local definition use “binds or transport” for a singular protein subject. This is a bounded editorial error.

## Recommended Actions And Acceptance Checks

### A1

Inspect annotation rules or a bounded source-asserted member set to determine whether the transport branch entails pigment binding; retain source mapping provenance and avoid converting an untested association into true equivalence.

- Document whether every relevant transport branch entails binding.
- If an actual mismatch is established, correct the maintained source transform and mapping semantics, regenerate and revalidate.

### A2

Apply a provenance-preserving wording correction through the maintained keyword transform or upstream source, using “binds or transports”.

- Regenerated wording has consistent singular verb agreement.
- Preserve both supported branches and original source attribution; validate the record.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0608.json; Inspected source response captured at the recorded UTC time | supports | Complete current official keyword response confirms accession, label, copied definition, source aliases if present, immediate Ligand parent and source GO associations if present. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The sole immediate parent is the source Ligand category, which covers binding, association and activity dependence. The seeder excludes category roots rather than creating a dangling local parent. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0031409; Inspected source response captured at the recorded UTC time | supports | Nonobsolete GO:0031409 denotes pigment binding and defines interaction with coloring matter in living organisms. It confirms the binding branch of the keyword; it does not itself adjudicate every protein in the transport branch. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml; Executed 2026-10-21T08:18:09Z through 2026-10-21T08:18:11Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml data/traits/function/binding_capacity/uniprot_keywords/plastoquinone-kw-0618.yaml data/traits/function/binding_capacity/uniprot_keywords/potassium-kw-0630.yaml data/traits/function/binding_capacity/uniprot_keywords/pqq-kw-0634.yaml data/traits/function/binding_capacity/uniprot_keywords/pyridoxal-phosphate-kw-0663.yaml data/traits/function/binding_capacity/uniprot_keywords/pyruvate-kw-0670.yaml data/traits/function/binding_capacity/uniprot_keywords/retinol-binding-kw-0683.yaml data/traits/function/binding_capacity/uniprot_keywords/s-adenosyl-l-methionine-kw-0949.yaml data/traits/function/binding_capacity/uniprot_keywords/schiff-base-kw-0704.yaml data/traits/function/binding_capacity/uniprot_keywords/selenium-kw-0711.yaml; Executed 2026-10-21T08:18:07Z through 2026-10-21T08:20:49Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml; Executed 2026-10-21T08:18:11Z through 2026-10-21T08:18:11Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:20:49Z through 2026-10-21T08:20:51Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T082314Z-pigment-kw-0608
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Pigment
started_at: '2026-10-21T08:17:43Z'
finished_at: '2026-10-21T08:23:14Z'
reviewer:
  identity: Codex
  kind: agent
  independence: unknown
  independence_basis: Unchanged target bytes assessed against inspected primary sources
    and repository rules, with independent source-acquisition and scope checks. Prior
    authorship independence is not established; this is not human sign-off.
skill: .claude/skills/review-yaml-record/SKILL.md
completion: completed
verdict: pass_with_limitations
scientific_review: true
summary: Pigment identity and the source GO association are supported. One copied
  grammar defect is confirmed; transport-versus-binding equivalence remains a provisional
  interpretation question.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
    sha256: eefecdef1215b74779862178b43cec3f70aa567cc798af30f96839afbab4d74c
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
  selection: Path-order position 1 in batch 007. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc
    and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 covers 58 record paths,
    leaving 429301 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0608
targets:
- kind: generated
  label: Pigment
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0608
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0608
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
    data/traits/function/binding_capacity/uniprot_keywords/plastoquinone-kw-0618.yaml
    data/traits/function/binding_capacity/uniprot_keywords/potassium-kw-0630.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pqq-kw-0634.yaml data/traits/function/binding_capacity/uniprot_keywords/pyridoxal-phosphate-kw-0663.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pyruvate-kw-0670.yaml data/traits/function/binding_capacity/uniprot_keywords/retinol-binding-kw-0683.yaml
    data/traits/function/binding_capacity/uniprot_keywords/s-adenosyl-l-methionine-kw-0949.yaml
    data/traits/function/binding_capacity/uniprot_keywords/schiff-base-kw-0704.yaml
    data/traits/function/binding_capacity/uniprot_keywords/selenium-kw-0711.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0608
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0608
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
  - UniProtKB-KW:KW-0608
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: KW-0608, its Ligand parent and directly asserted GO:0031409 resolve. The
    GO mapping provenance is verified; whole-class equivalence remains explicitly
    provisional.
  target_ids:
  - UniProtKB-KW:KW-0608
  evidence_ids:
  - keyword
  - parent
  - go
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:17:43Z'
  snapshot_sha256: eefecdef1215b74779862178b43cec3f70aa567cc798af30f96839afbab4d74c
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T08:17:43Z'
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
  accessed_at: '2026-10-21T08:17:43Z'
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
  reference: https://rest.uniprot.org/keywords/KW-0608.json
  accessed_at: '2026-10-21T08:18:19.191989Z'
  snapshot_sha256: 168ed334054880f36c3e0faba3a9df4d1c673bd49b75e1956e17b3791d4d3a07
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Complete current official keyword response confirms accession, label, copied
    definition, source aliases if present, immediate Ligand parent and source GO associations
    if present.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The sole immediate parent is the source Ligand category, which covers binding,
    association and activity dependence. The seeder excludes category roots rather
    than creating a dangling local parent.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0031409
  accessed_at: '2026-10-21T08:18:57.431724Z'
  snapshot_sha256: 037768e022493371be03e10ddae27c205fc5e7f0bb6daddd32db753d9b744da8
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0031409 denotes pigment binding and defines interaction
    with coloring matter in living organisms. It confirms the binding branch of the
    keyword; it does not itself adjudicate every protein in the transport branch.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  locator: Executed 2026-10-21T08:18:09Z through 2026-10-21T08:18:11Z; exit 0
  accessed_at: '2026-10-21T08:18:11Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
    data/traits/function/binding_capacity/uniprot_keywords/plastoquinone-kw-0618.yaml
    data/traits/function/binding_capacity/uniprot_keywords/potassium-kw-0630.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pqq-kw-0634.yaml data/traits/function/binding_capacity/uniprot_keywords/pyridoxal-phosphate-kw-0663.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pyruvate-kw-0670.yaml data/traits/function/binding_capacity/uniprot_keywords/retinol-binding-kw-0683.yaml
    data/traits/function/binding_capacity/uniprot_keywords/s-adenosyl-l-methionine-kw-0949.yaml
    data/traits/function/binding_capacity/uniprot_keywords/schiff-base-kw-0704.yaml
    data/traits/function/binding_capacity/uniprot_keywords/selenium-kw-0711.yaml
  locator: Executed 2026-10-21T08:18:07Z through 2026-10-21T08:20:49Z; exit 0
  accessed_at: '2026-10-21T08:20:49Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/pigment-kw-0608.yaml
  locator: Executed 2026-10-21T08:18:11Z through 2026-10-21T08:18:11Z; exit 0
  accessed_at: '2026-10-21T08:18:11Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T08:20:49Z through 2026-10-21T08:20:51Z; exit 0
  accessed_at: '2026-10-21T08:20:51Z'
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
  - UniProtKB-KW:KW-0608
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
  - UniProtKB-KW:KW-0608
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
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: KW-0608 denotes a protein trait associated with pigments, not a pigment
    molecule or an individual protein. Source accession, label and definition agree.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-6
  topic: Identity
- area: consistency
  outcome: supported
  summary: The current source has only the Ligand category as immediate parent. Omitting
    a category-root parent follows the maintained seeder policy; no missing seeded
    parent is established.
  evidence_ids:
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-7
  topic: Consistency
- area: grounding
  outcome: concern
  summary: The asserted GO term is authentic and fits pigment binding. The keyword
    also explicitly includes transport, so complete class equivalence and binding-only
    routing need a bounded interpretation check. This review establishes no nonbinding
    member.
  evidence_ids:
  - record
  - keyword
  - go
  - schema
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-8
  topic: Grounding
- area: nomenclature
  outcome: concern
  summary: The copied verb phrase has singular subject/verb disagreement; this does
    not alter the target identity.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0608
  assessment_id: assessment-9
  topic: Nomenclature
findings:
- issue_key: uniprot-keyword.KW-0608.transport-binding-scope
  category: grounding
  severity: minor
  title: Clarify transport scope before treating the GO mapping as equivalence
  description: The keyword has binding and transport alternatives, while GO:0031409
    describes pigment binding. The textual scopes differ, but transport may require
    direct binding; actual non-equivalence is not established.
  evidence_ids:
  - record
  - keyword
  - go
  - schema
  - owner
  certainty: provisional
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0608
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, hierarchy completeness
    or interpretation needs follow-up.
- issue_key: uniprot-keyword.KW-0608.definition-verb-agreement
  category: nomenclature
  severity: minor
  title: Correct copied subject–verb agreement
  description: The source and local definition use “binds or transport” for a singular
    protein subject. This is a bounded editorial error.
  evidence_ids:
  - record
  - keyword
  - owner
  finding_id: F2
  status: open
  target_ids:
  - UniProtKB-KW:KW-0608
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
  description: Inspect annotation rules or a bounded source-asserted member set to
    determine whether the transport branch entails pigment binding; retain source
    mapping provenance and avoid converting an untested association into true equivalence.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0608
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Document whether every relevant transport branch entails binding.
  - If an actual mismatch is established, correct the maintained source transform
    and mapping semantics, regenerate and revalidate.
- action_id: A2
  description: Apply a provenance-preserving wording correction through the maintained
    keyword transform or upstream source, using “binds or transports”.
  finding_ids:
  - F2
  target_ids:
  - UniProtKB-KW:KW-0608
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Regenerated wording has consistent singular verb agreement.
  - Preserve both supported branches and original source attribution; validate the
    record.
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
tags:
- unreviewed-path-order
- batch-007
- uniprot-keywords
```
