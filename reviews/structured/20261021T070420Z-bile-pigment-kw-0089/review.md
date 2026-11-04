# Review of Bile pigment

- Review: 20261021T070420Z-bile-pigment-kw-0089
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T06:56:06Z
- Finished UTC: 2026-10-21T07:04:20Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The source-defined covalent bilin-chromophore protein class, local binding placement and Chromophore parent are supported. No actionable finding is established; a generic noncovalent pigment-binding GO term is not an equivalent.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 002. Fresh main inventory has 429359 records; union of validated main targets and published batch-001 targets at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d covers 10 record paths, leaving 429349 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0089 | data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml | generated | Bile pigment |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0089 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0089 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0089 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0089 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0089 | Official UniProt resolves target KW-0089 and asserted parent KW-0157. No GO reference occurs in the record; both comparison GO terms resolve and are explicitly kept separate from equivalence claims. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0089.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0089.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0089.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0089.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0089.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0089.

This record denotes proteins bearing a covalently attached bilin chromophore, not a free pigment molecule or all proteins that encounter bile pigments.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0089.

The local binding-capacity enum does not restrict attachment to noncovalent interactions. A protein-level covalent-binding class fits; absence of localized site coordinates does not force a sequence-site or PTM record.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0089.

Chromophore is the asserted upstream and local broader class; the retained link preserves the immediate keyword hierarchy.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0089.

There is no record xref and neither inspected official mapping snapshot supplies one. Generic GO pigment binding would lose the covalent constraint and is not adopted.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0089.

Bilin chromophore is the source alias for this protein-annotation keyword. It is interpreted within that class context, not as a chemical equivalence between protein and pigment.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-0089.

The complete definition, named pigment examples and heme-derived context agree with the inspected source. This establishes source support, with independent detailed pigment chemistry bounded below.

## Findings

No findings recorded within this review's declared scope.

## Recommended Actions And Acceptance Checks

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| local-parent-1 | data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml; Entire local parent YAML | supports | Complete local parent record inspected for identifier, class, definition and broader-parent chain. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-0089; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| keyword | https://rest.uniprot.org/keywords/KW-0089?format=json; Complete keyword JSON and X-UniProt-Release response header | supports | UniProt 2026_03 resolves Bile pigment KW-0089. The definition explicitly requires covalent attachment of a linear tetrapyrrole chromophore; the single alias and Chromophore parent match the record. |
| parent | https://rest.uniprot.org/keywords/KW-0157?format=json; Inspected source response captured at the recorded UTC time | supports | Chromophore KW-0157 resolves and lists Bile pigment as its child; interaction with a chromophore is broader than the target covalent attachment. |
| go-comparison | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0031409; Inspected source response captured at the recorded UTC time | context_only | GO:0031409 is a nonobsolete generic pigment-binding function and has broader ligand identity than bile-pigment attachment. It is a comparison, not an upstream mapping. |
| go-binding | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0005488; Inspected source response captured at the recorded UTC time | context_only | GO binding explicitly describes noncovalent interaction and lists pigment binding as a child; this does not equate to the target covalent-attachment class. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml; Executed 2026-10-21T07:03:54Z through 2026-10-21T07:03:55Z; exit 0 | supports | uv run python scripts/validate_strict.py --workers 1 'data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml'<br>Validating 1 files with 1 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml; Executed 2026-10-21T06:56:30Z through 2026-10-21T06:59:20Z; exit 0 | supports | uv run python scripts/validate_strict.py data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml<br>Validating 10 files with 17 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>uv run python scripts/validate_uniprot_grounding.py data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml; Executed 2026-10-21T07:03:55Z through 2026-10-21T07:03:55Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings<br><br>uv run python scripts/audit_causal_graphs.py data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml |
| validation-4 | just validate-history; Executed 2026-10-21T06:59:20Z through 2026-10-21T06:59:22Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- The named pigment examples and biosynthetic background were checked against the source definition, not independently audited through a full pigment-chemistry literature survey. No attachment residue or protein-specific experiment is claimed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T070420Z-bile-pigment-kw-0089
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Bile pigment
started_at: '2026-10-21T06:56:06Z'
finished_at: '2026-10-21T07:04:20Z'
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
summary: The source-defined covalent bilin-chromophore protein class, local binding
  placement and Chromophore parent are supported. No actionable finding is established;
  a generic noncovalent pigment-binding GO term is not an equivalent.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
    sha256: 09b7b60f76997cb5003503193f74e4d99860728f2a2c7cd4428dbf158998a6c6
    role: target
  - path: data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml
    sha256: 9565b191e1277358edb67a85395a2076607922f1f0ad18a19c21eecfa446ef3b
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
  - path: scripts/seed_uniprot_keywords.py
    sha256: 8b21fb8f61aea278c593f5afd22f0d137f159d66a75dad1067cc8eca44def576
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 6 in batch 002. Fresh main inventory has 429359 records;
    union of validated main targets and published batch-001 targets at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    covers 10 record paths, leaving 429349 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0089
targets:
- kind: generated
  label: Bile pigment
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0089
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0089
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml
    data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml
    data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml
    data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml
    data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
    data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0089
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0089
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
  - UniProtKB-KW:KW-0089
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: Official UniProt resolves target KW-0089 and asserted parent KW-0157. No
    GO reference occurs in the record; both comparison GO terms resolve and are explicitly
    kept separate from equivalence claims.
  target_ids:
  - UniProtKB-KW:KW-0089
  evidence_ids:
  - keyword
  - parent
  - mapping-file
  - go-comparison
  - go-binding
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T06:56:06Z'
  snapshot_sha256: 09b7b60f76997cb5003503193f74e4d99860728f2a2c7cd4428dbf158998a6c6
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T06:56:06Z'
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
  accessed_at: '2026-10-21T06:56:06Z'
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
  reference: data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T06:56:06Z'
  snapshot_sha256: 9565b191e1277358edb67a85395a2076607922f1f0ad18a19c21eecfa446ef3b
  support: supports
  summary: Complete local parent record inspected for identifier, class, definition
    and broader-parent chain.
- evidence_id: mapping-file
  kind: database
  reference: https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go
  accessed_at: '2026-10-21T06:55:26.808623Z'
  snapshot_sha256: f38e663ed40d606803242afca204c0f285f211423c237251012b61f68ebdb36d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The complete official mapping file, version 2026/07/06 14:08:43, was searched
    for KW-0089; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0089?format=json
  accessed_at: '2026-10-21T06:55:02.348717Z'
  snapshot_sha256: 2a557d56b96e490fbf4a2e1a4bb05d6971d15fab17bea84c67db4866b2859c67
  support: supports
  locator: Complete keyword JSON and X-UniProt-Release response header
  summary: UniProt 2026_03 resolves Bile pigment KW-0089. The definition explicitly
    requires covalent attachment of a linear tetrapyrrole chromophore; the single
    alias and Chromophore parent match the record.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0157?format=json
  accessed_at: '2026-10-21T06:55:26.826626Z'
  snapshot_sha256: 7658938a764bc94f8c8f059679059853b830a29ac303685054fd885d48f51625
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Chromophore KW-0157 resolves and lists Bile pigment as its child; interaction
    with a chromophore is broader than the target covalent attachment.
- evidence_id: go-comparison
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0031409
  accessed_at: '2026-10-21T06:56:27.227512Z'
  snapshot_sha256: 037768e022493371be03e10ddae27c205fc5e7f0bb6daddd32db753d9b744da8
  support: context_only
  locator: Inspected source response captured at the recorded UTC time
  summary: GO:0031409 is a nonobsolete generic pigment-binding function and has broader
    ligand identity than bile-pigment attachment. It is a comparison, not an upstream
    mapping.
- evidence_id: go-binding
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0005488
  accessed_at: '2026-10-21T06:56:27.822423Z'
  snapshot_sha256: 6015a69036105c45e68c1938c9169449c9c69dabee51b002563d8f9e97ab667a
  support: context_only
  locator: Inspected source response captured at the recorded UTC time
  summary: GO binding explicitly describes noncovalent interaction and lists pigment
    binding as a child; this does not equate to the target covalent-attachment class.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  locator: Executed 2026-10-21T07:03:54Z through 2026-10-21T07:03:55Z; exit 0
  accessed_at: '2026-10-21T07:03:55Z'
  support: supports
  summary: "uv run python scripts/validate_strict.py --workers 1 'data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml'\n\
    Validating 1 files with 1 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      1\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml
    data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml
    data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml
    data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml
    data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
    data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml
    data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml
  locator: Executed 2026-10-21T06:56:30Z through 2026-10-21T06:59:20Z; exit 0
  accessed_at: '2026-10-21T06:59:20Z'
  support: supports
  summary: "uv run python scripts/validate_strict.py data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml\n\
    Validating 10 files with 17 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      10\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    uv run python scripts/validate_uniprot_grounding.py data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/3fe-4s-kw-0003.yaml data/traits/function/binding_capacity/uniprot_keywords/4fe-4s-kw-0004.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/atp-binding-kw-0067.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/bacteriochlorophyll-kw-0076.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/biotin-kw-0092.yaml data/traits/function/binding_capacity/uniprot_keywords/c-di-gmp-kw-0973.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/cadmium-kw-0104.yaml\
    \ data/traits/function/binding_capacity/uniprot_keywords/calcium-kw-0106.yaml\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml
  locator: Executed 2026-10-21T07:03:55Z through 2026-10-21T07:03:55Z; exit 0
  accessed_at: '2026-10-21T07:03:55Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings


    uv run python scripts/audit_causal_graphs.py data/traits/function/binding_capacity/uniprot_keywords/bile-pigment-kw-0089.yaml'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T06:59:20Z through 2026-10-21T06:59:22Z; exit 0
  accessed_at: '2026-10-21T06:59:22Z'
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
  - UniProtKB-KW:KW-0089
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
  - UniProtKB-KW:KW-0089
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
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: This record denotes proteins bearing a covalently attached bilin chromophore,
    not a free pigment molecule or all proteins that encounter bile pigments.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-6
  topic: Identity
- area: representation
  outcome: supported
  summary: The local binding-capacity enum does not restrict attachment to noncovalent
    interactions. A protein-level covalent-binding class fits; absence of localized
    site coordinates does not force a sequence-site or PTM record.
  evidence_ids:
  - record
  - keyword
  - schema
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-7
  topic: Representation
- area: consistency
  outcome: supported
  summary: Chromophore is the asserted upstream and local broader class; the retained
    link preserves the immediate keyword hierarchy.
  evidence_ids:
  - record
  - parent
  - local-parent-1
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-8
  topic: Consistency
- area: grounding
  outcome: supported
  summary: There is no record xref and neither inspected official mapping snapshot
    supplies one. Generic GO pigment binding would lose the covalent constraint and
    is not adopted.
  evidence_ids:
  - record
  - keyword
  - mapping-file
  - go-comparison
  - go-binding
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-9
  topic: Grounding
- area: nomenclature
  outcome: supported
  summary: Bilin chromophore is the source alias for this protein-annotation keyword.
    It is interpreted within that class context, not as a chemical equivalence between
    protein and pigment.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0089
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: supported
  summary: The complete definition, named pigment examples and heme-derived context
    agree with the inspected source. This establishes source support, with independent
    detailed pigment chemistry bounded below.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0089
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
- No GO equivalence is asserted in the record. Compared GO terms are external scope
  checks only and must not be added as direct equivalents without new source support.
- The named pigment examples and biosynthetic background were checked against the
  source definition, not independently audited through a full pigment-chemistry literature
  survey. No attachment residue or protein-specific experiment is claimed.
tags:
- unreviewed-path-order
- batch-002
- uniprot-keywords
```
