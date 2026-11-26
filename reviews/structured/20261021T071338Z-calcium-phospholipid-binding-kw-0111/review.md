# Review of Calcium/phospholipid-binding

- Review: 20261021T071338Z-calcium-phospholipid-binding-kw-0111
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:11:03Z
- Finished UTC: 2026-10-21T07:13:38Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The calcium-dependent phospholipid-binding class, direct GO association, Calcium parent and synonym are supported. No actionable finding is established within the inspected source scope.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 003. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths, leaving 429339 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0111 | data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml | generated | Calcium/phospholipid-binding |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0111 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0111 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0111 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0111 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0111 | Official UniProt resolves KW-0111 and its asserted parent KW-0106; QuickGO resolves nonobsolete GO:0005544. No protein accession, residue interval or individual causal graph is asserted. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0111.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0111.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0111.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0111.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0111.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0111.

The identifier and label denote a protein-level calcium/phospholipid-binding capability; the record is not an individual protein or a claim of a specific residue interval.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0111.

GO:0005544 is a source-direct association that matches the intended binding scope expressed by the source synonym; calcium dependence is retained in interpreting the class.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0111.

Calcium is a valid broader parent locally and upstream. The current source asserts no additional immediate phospholipid parent, so none is invented.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0111.

The sole exact alias is the source calcium-dependent phospholipid-binding name and agrees with the GO functional scope.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0111.

A generic statement that proteins have a binding site does not supply coordinates or turn this class into STRUCT_BINDING_SITE. The entry-level FUNCTION/binding representation is appropriate.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-0111.

The source supports the bounded annexin/C2 examples. The qualifiers may and some avoid asserting that every annexin repeat pair or every C2 domain confers this trait.

## Findings

No findings recorded within this review's declared scope.

## Recommended Actions And Acceptance Checks

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| local-parent-1 | data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml; Entire local parent YAML | supports | Complete local parent record inspected for identifier, class, definition and broader-parent chain. |
| keyword | https://rest.uniprot.org/keywords/KW-0111.json; Complete keyword JSON and X-UniProt-Release response header | supports | UniProt 2026_03 resolves Calcium/phospholipid-binding KW-0111. The complete definition, calcium-dependent synonym, Calcium parent and GO:0005544 mapping match the target. Annexin repeats and some C2 proteins are examples rather than a universal family-membership rule. |
| parent | https://rest.uniprot.org/keywords/KW-0106.json; Inspected source response captured at the recorded UTC time | supports | Calcium KW-0106 resolves as a broader protein class covering calcium binding or calcium-dependent function; it lists this target as a child. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005544; Inspected source response captured at the recorded UTC time | supports | GO:0005544 is a nonobsolete molecular function for phospholipid binding in the presence of calcium. Together with the source synonym it supports the intended calcium-dependent binding scope. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml; Executed 2026-10-21T07:13:19Z through 2026-10-21T07:13:20Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml; Executed 2026-10-21T07:11:35Z through 2026-10-21T07:13:12Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml; Executed 2026-10-21T07:13:20Z through 2026-10-21T07:13:20Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:13:12Z through 2026-10-21T07:13:13Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- The annexin and C2 examples were verified as bounded source assertions, not through an exhaustive structural survey or a protein-specific binding assay. No universal domain detection rule or qualified example is inferred.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T071338Z-calcium-phospholipid-binding-kw-0111
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Calcium/phospholipid-binding
started_at: '2026-10-21T07:11:03Z'
finished_at: '2026-10-21T07:13:38Z'
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
summary: The calcium-dependent phospholipid-binding class, direct GO association,
  Calcium parent and synonym are supported. No actionable finding is established within
  the inspected source scope.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml
    sha256: 4f7243c438f46b7ed5564c423c643af0342f9e06e8de6ef812cbb70803bb89a6
    role: context
  - path: data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
    sha256: 1f831f11074b2f677663841e76c65ed8c1a365725588b93fbcbceb82df94d83d
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
  selection: Path-order position 1 in batch 003. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths,
    leaving 429339 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0111
targets:
- kind: generated
  label: Calcium/phospholipid-binding
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0111
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0111
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
    data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
    data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
    data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml
    data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0111
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0111
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
  - UniProtKB-KW:KW-0111
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: Official UniProt resolves KW-0111 and its asserted parent KW-0106; QuickGO
    resolves nonobsolete GO:0005544. No protein accession, residue interval or individual
    causal graph is asserted.
  target_ids:
  - UniProtKB-KW:KW-0111
  evidence_ids:
  - keyword
  - parent
  - go
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:11:03Z'
  snapshot_sha256: 1f831f11074b2f677663841e76c65ed8c1a365725588b93fbcbceb82df94d83d
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:11:03Z'
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
  accessed_at: '2026-10-21T07:11:03Z'
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
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T07:11:03Z'
  snapshot_sha256: 4f7243c438f46b7ed5564c423c643af0342f9e06e8de6ef812cbb70803bb89a6
  support: supports
  summary: Complete local parent record inspected for identifier, class, definition
    and broader-parent chain.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0111.json
  accessed_at: '2026-10-21T07:10:44.811758Z'
  snapshot_sha256: 30d14db622c49d38326121f3e23d51987333774768336e2dd6c1cd733d3287b8
  support: supports
  locator: Complete keyword JSON and X-UniProt-Release response header
  summary: UniProt 2026_03 resolves Calcium/phospholipid-binding KW-0111. The complete
    definition, calcium-dependent synonym, Calcium parent and GO:0005544 mapping match
    the target. Annexin repeats and some C2 proteins are examples rather than a universal
    family-membership rule.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0106.json
  accessed_at: '2026-10-21T07:10:46.095257Z'
  snapshot_sha256: a87750da3f18cba32d7a10ab5fa73ac7d063dc62964c62ce70e453d3e9e16aed
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Calcium KW-0106 resolves as a broader protein class covering calcium binding
    or calcium-dependent function; it lists this target as a child.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005544
  accessed_at: '2026-10-21T07:10:46.724892Z'
  snapshot_sha256: 096a80a197e90b2470ee7670377e557bee3f07b21ac35d1decaa55a52c25e1e9
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: GO:0005544 is a nonobsolete molecular function for phospholipid binding
    in the presence of calcium. Together with the source synonym it supports the intended
    calcium-dependent binding scope.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  locator: Executed 2026-10-21T07:13:19Z through 2026-10-21T07:13:20Z; exit 0
  accessed_at: '2026-10-21T07:13:20Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
    data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
    data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
    data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml
    data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml
  locator: Executed 2026-10-21T07:11:35Z through 2026-10-21T07:13:12Z; exit 0
  accessed_at: '2026-10-21T07:13:12Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml
  locator: Executed 2026-10-21T07:13:20Z through 2026-10-21T07:13:20Z; exit 0
  accessed_at: '2026-10-21T07:13:20Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T07:13:12Z through 2026-10-21T07:13:13Z; exit 0
  accessed_at: '2026-10-21T07:13:13Z'
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
  - UniProtKB-KW:KW-0111
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
  - UniProtKB-KW:KW-0111
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
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The identifier and label denote a protein-level calcium/phospholipid-binding
    capability; the record is not an individual protein or a claim of a specific residue
    interval.
  evidence_ids:
  - record
  - keyword
  - schema
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: GO:0005544 is a source-direct association that matches the intended binding
    scope expressed by the source synonym; calcium dependence is retained in interpreting
    the class.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-7
  topic: Grounding
- area: consistency
  outcome: supported
  summary: Calcium is a valid broader parent locally and upstream. The current source
    asserts no additional immediate phospholipid parent, so none is invented.
  evidence_ids:
  - record
  - parent
  - local-parent-1
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-8
  topic: Consistency
- area: nomenclature
  outcome: supported
  summary: The sole exact alias is the source calcium-dependent phospholipid-binding
    name and agrees with the GO functional scope.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-9
  topic: Nomenclature
- area: representation
  outcome: supported
  summary: A generic statement that proteins have a binding site does not supply coordinates
    or turn this class into STRUCT_BINDING_SITE. The entry-level FUNCTION/binding
    representation is appropriate.
  evidence_ids:
  - record
  - schema
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-10
  topic: Representation
- area: evidence
  outcome: supported
  summary: The source supports the bounded annexin/C2 examples. The qualifiers may
    and some avoid asserting that every annexin repeat pair or every C2 domain confers
    this trait.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0111
  assessment_id: assessment-11
  topic: Evidence
findings: []
actions: []
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
- The annexin and C2 examples were verified as bounded source assertions, not through
  an exhaustive structural survey or a protein-specific binding assay. No universal
  domain detection rule or qualified example is inferred.
tags:
- unreviewed-path-order
- batch-003
- uniprot-keywords
```
