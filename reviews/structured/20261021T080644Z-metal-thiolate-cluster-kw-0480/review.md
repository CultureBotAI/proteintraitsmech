# Review of Metal-thiolate cluster

- Review: 20261021T080644Z-metal-thiolate-cluster-kw-0480
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:59:37Z
- Finished UTC: 2026-10-21T08:06:44Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The metal-thiolate-cluster protein identity and Metal-binding parent are supported. One major finding identifies a broader GO association incorrectly represented as exact equivalence.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 006. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc covers 48 record paths, leaving 429311 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0480 | data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml | generated | Metal-thiolate cluster |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0480 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0480 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0480 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0480 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0480 | UniProt resolves KW-0480 and parent KW-0479; GO:0046872 is nonobsolete. Successful identifier resolution does not establish equivalence: its broader scope is recorded as a substantive finding. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0480.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0480.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0480.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0480.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0480.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0480.

The stable keyword denotes proteins binding a cysteinyl metal-thiolate cluster. It is a trait class, not an individual metal complex or protein instance.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0480.

The protein-level cluster-binding requirement fits FUNCTION / FUNC_BINDING_CAPACITY and CLASS. No unsupported cluster stoichiometry, metal species or residue coordinates are asserted.

### Grounding

grounding: concern. Targets: UniProtKB-KW:KW-0480.

The GO association is genuinely source-direct and resolves, but its generic metal-ion binding scope is broader than the defining cluster requirement. Source provenance alone does not meet the schema requirement for true equivalence in xrefs.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0480.

The retained Metal-binding parent is source-asserted and appropriately broader. It already represents the broad binding hierarchy that the GO xref incorrectly treats as equivalent.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0480.

Metal-thiolate cluster is the supported keyword name; the record asserts no unsupported exact synonyms.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0480.

The source definition and declared parent preserve a cluster-specific class. Encoding the broader GO term as equivalent removes that distinction under the local field semantics, independently of any untested protein activity.

## Findings

### F1: Do not encode generic metal-ion binding as cluster-class equivalence

major / open / confirmed; issue key: uniprot-keyword.KW-0480.broad-metal-binding-xref.

The record places GO:0046872 in xrefs, whose schema requires true source-direct equivalence. GO:0046872 denotes generic metal-ion binding; this target additionally requires a cysteinyl metal-thiolate cluster and has a broader Metal-binding parent that itself maps to the same GO term. The source association is authentic, but its relation is broader than identity. The defect is the semantic strength of the xref, not an invented absence of another function in an individual protein.

## Recommended Actions And Acceptance Checks

### A1

Correct the maintained keyword mapping transform or a reviewed mapping override consumed by scripts/seed_uniprot_keywords.py so broader source GO associations are not emitted as exact xrefs. Remove GO:0046872 from this target's equivalence field while retaining its valid Metal-binding parent and source-association provenance in an appropriate supported form.

- The regenerated target retains the cluster-specific definition and KW-0479 parent, without claiming equivalence to generic GO:0046872.
- Preserve provenance of the original source association; do not relabel it as external mapped_xrefs without actual external-mapping provenance.
- A targeted mapping fixture distinguishes source-direct provenance from semantic equivalence; strict validation and a new scoped review pass.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| local-parent-1 | data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml; Entire local parent YAML | supports | Complete local parent record inspected for identifier, class, definition and broader-parent chain. |
| keyword | https://rest.uniprot.org/keywords/KW-0480.json; Inspected source response captured at the recorded UTC time | supports | UniProt resolves Metal-thiolate cluster KW-0480, requiring a metal cluster with cysteinyl-thiolate bridges. It directly associates GO:0046872 and asserts Metal-binding KW-0479 as its only immediate parent; comparison release2026_03. |
| parent | https://rest.uniprot.org/keywords/KW-0479.json; Inspected source response captured at the recorded UTC time | supports | Metal-binding KW-0479 defines the broader metal-binding protein class, maps to GO:0046872 and explicitly lists Metal-thiolate cluster as a child. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0046872; Inspected source response captured at the recorded UTC time | supports | Nonobsolete GO:0046872 defines generic binding to a metal ion. Its definition does not require a cluster or cysteinyl-thiolate ligation and is broader than the target class. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml; Executed 2026-10-21T08:00:44Z through 2026-10-21T08:00:45Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/mannose-binding-kw-0465.yaml data/traits/function/binding_capacity/uniprot_keywords/mercury-kw-0476.yaml data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml data/traits/function/binding_capacity/uniprot_keywords/molybdenum-kw-0500.yaml data/traits/function/binding_capacity/uniprot_keywords/nad-kw-0520.yaml data/traits/function/binding_capacity/uniprot_keywords/nadp-kw-0521.yaml data/traits/function/binding_capacity/uniprot_keywords/nickel-kw-0533.yaml data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml data/traits/function/binding_capacity/uniprot_keywords/pheromone-binding-kw-0590.yaml; Executed 2026-10-21T08:00:03Z through 2026-10-21T08:02:09Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml; Executed 2026-10-21T08:00:45Z through 2026-10-21T08:00:46Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:02:09Z through 2026-10-21T08:02:10Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- This conclusion compares explicit class definitions and local relation semantics. No specific cluster, protein example, negative activity, coordination geometry or mechanism is qualified.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T080644Z-metal-thiolate-cluster-kw-0480
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Metal-thiolate cluster
started_at: '2026-10-21T07:59:37Z'
finished_at: '2026-10-21T08:06:44Z'
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
summary: The metal-thiolate-cluster protein identity and Metal-binding parent are
  supported. One major finding identifies a broader GO association incorrectly represented
  as exact equivalence.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml
    sha256: d10e02a25025a55164f0092bd661e65424e47d422358598ec596d9f810e5b083
    role: context
  - path: data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
    sha256: 27a55374e329c50cde9ce421672479c4292178bf5cb03c829bf9b77750c1e015
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
  selection: Path-order position 4 in batch 006. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc
    covers 48 record paths, leaving 429311 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0480
targets:
- kind: generated
  label: Metal-thiolate cluster
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0480
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0480
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/mannose-binding-kw-0465.yaml
    data/traits/function/binding_capacity/uniprot_keywords/mercury-kw-0476.yaml data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml
    data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
    data/traits/function/binding_capacity/uniprot_keywords/molybdenum-kw-0500.yaml
    data/traits/function/binding_capacity/uniprot_keywords/nad-kw-0520.yaml data/traits/function/binding_capacity/uniprot_keywords/nadp-kw-0521.yaml
    data/traits/function/binding_capacity/uniprot_keywords/nickel-kw-0533.yaml data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pheromone-binding-kw-0590.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0480
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0480
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
  - UniProtKB-KW:KW-0480
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: 'UniProt resolves KW-0480 and parent KW-0479; GO:0046872 is nonobsolete.
    Successful identifier resolution does not establish equivalence: its broader scope
    is recorded as a substantive finding.'
  target_ids:
  - UniProtKB-KW:KW-0480
  evidence_ids:
  - keyword
  - parent
  - go
  - schema
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:59:37Z'
  snapshot_sha256: 27a55374e329c50cde9ce421672479c4292178bf5cb03c829bf9b77750c1e015
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:59:37Z'
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
  accessed_at: '2026-10-21T07:59:37Z'
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
  reference: data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T07:59:37Z'
  snapshot_sha256: d10e02a25025a55164f0092bd661e65424e47d422358598ec596d9f810e5b083
  support: supports
  summary: Complete local parent record inspected for identifier, class, definition
    and broader-parent chain.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0480.json
  accessed_at: '2026-10-21T08:00:26.418643Z'
  snapshot_sha256: f99693a0a07c57accb72c41b11b4b7b5d3114aac97bce660ce0ef567664972ba
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: UniProt resolves Metal-thiolate cluster KW-0480, requiring a metal cluster
    with cysteinyl-thiolate bridges. It directly associates GO:0046872 and asserts
    Metal-binding KW-0479 as its only immediate parent; comparison release2026_03.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0479.json
  accessed_at: '2026-10-21T07:29:52.153949Z'
  snapshot_sha256: e93ca03a4a8a79a9efbc7fd77e67ec2833bf4fe68f274dd1b229827566bcddb1
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Metal-binding KW-0479 defines the broader metal-binding protein class,
    maps to GO:0046872 and explicitly lists Metal-thiolate cluster as a child.
- evidence_id: go
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0046872
  accessed_at: '2026-10-21T07:30:26.957853Z'
  snapshot_sha256: 76b0bb1865d4f8bb74550041e1605bfff852c49515174223ff271926c63ba985
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0046872 defines generic binding to a metal ion. Its definition
    does not require a cluster or cysteinyl-thiolate ligation and is broader than
    the target class.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  locator: Executed 2026-10-21T08:00:44Z through 2026-10-21T08:00:45Z; exit 0
  accessed_at: '2026-10-21T08:00:45Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/mannose-binding-kw-0465.yaml
    data/traits/function/binding_capacity/uniprot_keywords/mercury-kw-0476.yaml data/traits/function/binding_capacity/uniprot_keywords/metal-binding-kw-0479.yaml
    data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
    data/traits/function/binding_capacity/uniprot_keywords/molybdenum-kw-0500.yaml
    data/traits/function/binding_capacity/uniprot_keywords/nad-kw-0520.yaml data/traits/function/binding_capacity/uniprot_keywords/nadp-kw-0521.yaml
    data/traits/function/binding_capacity/uniprot_keywords/nickel-kw-0533.yaml data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml
    data/traits/function/binding_capacity/uniprot_keywords/pheromone-binding-kw-0590.yaml
  locator: Executed 2026-10-21T08:00:03Z through 2026-10-21T08:02:09Z; exit 0
  accessed_at: '2026-10-21T08:02:09Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/metal-thiolate-cluster-kw-0480.yaml
  locator: Executed 2026-10-21T08:00:45Z through 2026-10-21T08:00:46Z; exit 0
  accessed_at: '2026-10-21T08:00:46Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T08:02:09Z through 2026-10-21T08:02:10Z; exit 0
  accessed_at: '2026-10-21T08:02:10Z'
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
  - UniProtKB-KW:KW-0480
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
  - UniProtKB-KW:KW-0480
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
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The stable keyword denotes proteins binding a cysteinyl metal-thiolate
    cluster. It is a trait class, not an individual metal complex or protein instance.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-6
  topic: Identity
- area: representation
  outcome: supported
  summary: The protein-level cluster-binding requirement fits FUNCTION / FUNC_BINDING_CAPACITY
    and CLASS. No unsupported cluster stoichiometry, metal species or residue coordinates
    are asserted.
  evidence_ids:
  - record
  - schema
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-7
  topic: Representation
- area: grounding
  outcome: concern
  summary: The GO association is genuinely source-direct and resolves, but its generic
    metal-ion binding scope is broader than the defining cluster requirement. Source
    provenance alone does not meet the schema requirement for true equivalence in
    xrefs.
  evidence_ids:
  - record
  - keyword
  - go
  - schema
  - owner
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-8
  topic: Grounding
- area: consistency
  outcome: supported
  summary: The retained Metal-binding parent is source-asserted and appropriately
    broader. It already represents the broad binding hierarchy that the GO xref incorrectly
    treats as equivalent.
  evidence_ids:
  - record
  - keyword
  - parent
  - local-parent-1
  - go
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-9
  topic: Consistency
- area: nomenclature
  outcome: supported
  summary: Metal-thiolate cluster is the supported keyword name; the record asserts
    no unsupported exact synonyms.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: The source definition and declared parent preserve a cluster-specific class.
    Encoding the broader GO term as equivalent removes that distinction under the
    local field semantics, independently of any untested protein activity.
  evidence_ids:
  - record
  - keyword
  - parent
  - go
  - schema
  target_ids:
  - UniProtKB-KW:KW-0480
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0480.broad-metal-binding-xref
  category: grounding
  severity: major
  title: Do not encode generic metal-ion binding as cluster-class equivalence
  description: The record places GO:0046872 in xrefs, whose schema requires true source-direct
    equivalence. GO:0046872 denotes generic metal-ion binding; this target additionally
    requires a cysteinyl metal-thiolate cluster and has a broader Metal-binding parent
    that itself maps to the same GO term. The source association is authentic, but
    its relation is broader than identity. The defect is the semantic strength of
    the xref, not an invented absence of another function in an individual protein.
  evidence_ids:
  - record
  - keyword
  - parent
  - local-parent-1
  - go
  - schema
  - owner
  normalization_reason: The asserted exact equivalence erases a defining cluster restriction
    and materially conflates a narrower trait with its broader binding class.
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0480
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct the maintained keyword mapping transform or a reviewed mapping
    override consumed by scripts/seed_uniprot_keywords.py so broader source GO associations
    are not emitted as exact xrefs. Remove GO:0046872 from this target's equivalence
    field while retaining its valid Metal-binding parent and source-association provenance
    in an appropriate supported form.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0480
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - The regenerated target retains the cluster-specific definition and KW-0479 parent,
    without claiming equivalence to generic GO:0046872.
  - Preserve provenance of the original source association; do not relabel it as external
    mapped_xrefs without actual external-mapping provenance.
  - A targeted mapping fixture distinguishes source-direct provenance from semantic
    equivalence; strict validation and a new scoped review pass.
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
- This conclusion compares explicit class definitions and local relation semantics.
  No specific cluster, protein example, negative activity, coordination geometry or
  mechanism is qualified.
tags:
- unreviewed-path-order
- batch-006
- uniprot-keywords
```
