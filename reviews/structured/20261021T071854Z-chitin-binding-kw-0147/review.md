# Review of Chitin-binding

- Review: 20261021T071854Z-chitin-binding-kw-0147
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:11:08Z
- Finished UTC: 2026-10-21T07:18:54Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The broad chitin-binding class and direct GO mapping are supported. One minor finding asks that an ancillary short-domain description be qualified as type-1 rather than generalized across binding architectures.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 003. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths, leaving 429339 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0147 | data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml | generated | Chitin-binding |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0147 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0147 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0147 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0147 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0147 | Official UniProt resolves KW-0147 and source category KW-9993; QuickGO resolves nonobsolete GO:0008061. PROSITE PDOC00025 and the primary PMID/DOI were resolved and their relevant source text inspected. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0147.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0147.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0147.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0147.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0147.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0147.

The first sentence and GO association define the broad protein chitin-binding function. No individual protein is substituted for the trait class.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0147.

GO:0008061 is a valid source-direct equivalent for the core binding class and ligand identity.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0147.

FUNCTION/binding capacity is appropriate. The record has no structural pattern or detector requiring every member to carry the short cysteine-rich motif.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0147.

Only the unseeded Ligand category is asserted as a parent upstream; no missing seeded immediate parent is established.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0147.

The stable label matches the source and the record adds no synonym assertions.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0147.

Core binding identity is supported, but the ancillary unqualified domain paragraph describes a type-1 architecture. PROSITE supplies that qualifier and CBP21 directly demonstrates a different chitin-binding fold.

## Findings

### F1: Qualify the short disulfide-rich domain description

minor / open / confirmed; issue key: uniprot-keyword.KW-0147.type1-domain-background-scope.

The ancillary domain paragraph describes a 30–43-residue cysteine/disulfide architecture without naming type-1. PROSITE explicitly limits that architecture to type-1, while primary CBP21 structure/binding evidence establishes another fold. The first broad binding sentence and GO mapping remain sound, and no detector makes this architecture a class-membership condition.

## Recommended Actions And Acceptance Checks

### A1

Add a maintained definition correction through scripts/seed_uniprot_keywords.py identifying the structural paragraph as a type-1 example, or omit that ancillary paragraph; retain the broad binding definition and source provenance.

- Corrected text does not imply all chitin-binding proteins use a 30–43-residue disulfide-rich domain.
- The type-1 statement is source-cited; CBP21 evidence is not relabeled as a current noncatalytic family classification or promoted as a qualified example.
- Regenerate and run strict validation, then review the corrected definition.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0147.json; Complete keyword JSON and X-UniProt-Release response header | supports | UniProt 2026_03 resolves Chitin-binding KW-0147 with the same complete definition and direct GO:0008061 association. Its only immediate source parent is the Ligand category. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | Ligand is the source category root, intentionally omitted by the local seeder. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0008061; Inspected source response captured at the recorded UTC time | supports | GO:0008061 is nonobsolete chitin binding, identifying beta-1,4-linked N-acetyl-D-glucosamine polymer as ligand; it imposes no single protein-domain architecture. |
| type1 | https://prosite.expasy.org/PDOC00025; Inspected type-1 domain description and structural-background paragraphs | supports | Official PROSITE documentation PDOC00025 explicitly assigns the common 30–43-residue, four-disulfide-core motif to chitin-binding domain type-1 and discusses it in a bounded protein-family context. |
| cbp21 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15590674+AND+SRC%3AMED&amp;format=json&amp;resultType=core; Complete primary abstract and citation metadata; full article not inspected | supports | Vaaje-Kolstad and colleagues, PMID 15590674, DOI 10.1074/jbc.m407175200: the complete primary abstract reports a beta-sandwich/budded fibronectin-type-III fold for Serratia marcescens CBP21 and chitin-affinity changes after surface-residue mutation. This demonstrates chitin binding with a different architecture; the article’s historical family label is not a claim about present classification. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml; Executed 2026-10-21T07:17:44Z through 2026-10-21T07:17:48Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml; Executed 2026-10-21T07:11:35Z through 2026-10-21T07:13:12Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml; Executed 2026-10-21T07:17:48Z through 2026-10-21T07:17:49Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:13:12Z through 2026-10-21T07:13:13Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- The primary CBP21 abstract was inspected, not the full paper. Its historical CBM33 designation is not used as a current taxonomy assertion, and no claim that CBP21 is noncatalytic is made. No sequence detector, residue coordinates or qualified protein exemplar is supplied.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T071854Z-chitin-binding-kw-0147
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Chitin-binding
started_at: '2026-10-21T07:11:08Z'
finished_at: '2026-10-21T07:18:54Z'
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
summary: The broad chitin-binding class and direct GO mapping are supported. One minor
  finding asks that an ancillary short-domain description be qualified as type-1 rather
  than generalized across binding architectures.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
    sha256: a449fdd8ac9cf2fd624dc04e6f49f09f802350dd49400a9a433fb710c0a44687
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
  selection: Path-order position 6 in batch 003. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths,
    leaving 429339 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0147
targets:
- kind: generated
  label: Chitin-binding
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0147
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0147
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
  - UniProtKB-KW:KW-0147
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0147
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
  - UniProtKB-KW:KW-0147
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: Official UniProt resolves KW-0147 and source category KW-9993; QuickGO
    resolves nonobsolete GO:0008061. PROSITE PDOC00025 and the primary PMID/DOI were
    resolved and their relevant source text inspected.
  target_ids:
  - UniProtKB-KW:KW-0147
  evidence_ids:
  - keyword
  - parent
  - go
  - type1
  - cbp21
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:11:08Z'
  snapshot_sha256: a449fdd8ac9cf2fd624dc04e6f49f09f802350dd49400a9a433fb710c0a44687
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:11:08Z'
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
  accessed_at: '2026-10-21T07:11:08Z'
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
  reference: https://rest.uniprot.org/keywords/KW-0147.json
  accessed_at: '2026-10-21T07:11:07.428690Z'
  snapshot_sha256: f15a9d93c068a25d5f3c8aad73489a6accff55b41c9ae9c228439ffc9d29d574
  support: supports
  locator: Complete keyword JSON and X-UniProt-Release response header
  summary: UniProt 2026_03 resolves Chitin-binding KW-0147 with the same complete
    definition and direct GO:0008061 association. Its only immediate source parent
    is the Ligand category.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T06:55:11.470683Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Ligand is the source category root, intentionally omitted by the local
    seeder.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0008061
  accessed_at: '2026-10-21T07:11:54.281615Z'
  snapshot_sha256: 31af25e9abc453fcc1df6433f826d057a03978718aac6a4f408068d04fb4479e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: GO:0008061 is nonobsolete chitin binding, identifying beta-1,4-linked N-acetyl-D-glucosamine
    polymer as ligand; it imposes no single protein-domain architecture.
- evidence_id: type1
  kind: authority
  reference: https://prosite.expasy.org/PDOC00025
  accessed_at: '2026-10-21T07:11:54.662040Z'
  snapshot_sha256: 7e25281a8a194befa84d0e92550cb13a7db7190b1baeac7c399082899f59842c
  support: supports
  locator: Inspected type-1 domain description and structural-background paragraphs
  summary: Official PROSITE documentation PDOC00025 explicitly assigns the common
    30–43-residue, four-disulfide-core motif to chitin-binding domain type-1 and discusses
    it in a bounded protein-family context.
- evidence_id: cbp21
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15590674+AND+SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T07:11:54.302743Z'
  snapshot_sha256: 2eaf9df7f8d9a8c0951436ae09a8d248f14345aad9cf7927edd47da034a1c4dc
  support: supports
  locator: Complete primary abstract and citation metadata; full article not inspected
  summary: 'Vaaje-Kolstad and colleagues, PMID 15590674, DOI 10.1074/jbc.m407175200:
    the complete primary abstract reports a beta-sandwich/budded fibronectin-type-III
    fold for Serratia marcescens CBP21 and chitin-affinity changes after surface-residue
    mutation. This demonstrates chitin binding with a different architecture; the
    article’s historical family label is not a claim about present classification.'
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  locator: Executed 2026-10-21T07:17:44Z through 2026-10-21T07:17:48Z; exit 0
  accessed_at: '2026-10-21T07:17:48Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml
  locator: Executed 2026-10-21T07:17:48Z through 2026-10-21T07:17:49Z; exit 0
  accessed_at: '2026-10-21T07:17:49Z'
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
  - UniProtKB-KW:KW-0147
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
  - UniProtKB-KW:KW-0147
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
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The first sentence and GO association define the broad protein chitin-binding
    function. No individual protein is substituted for the trait class.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: GO:0008061 is a valid source-direct equivalent for the core binding class
    and ligand identity.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-7
  topic: Grounding
- area: representation
  outcome: supported
  summary: FUNCTION/binding capacity is appropriate. The record has no structural
    pattern or detector requiring every member to carry the short cysteine-rich motif.
  evidence_ids:
  - record
  - schema
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-8
  topic: Representation
- area: consistency
  outcome: supported
  summary: Only the unseeded Ligand category is asserted as a parent upstream; no
    missing seeded immediate parent is established.
  evidence_ids:
  - record
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-9
  topic: Consistency
- area: nomenclature
  outcome: supported
  summary: The stable label matches the source and the record adds no synonym assertions.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: Core binding identity is supported, but the ancillary unqualified domain
    paragraph describes a type-1 architecture. PROSITE supplies that qualifier and
    CBP21 directly demonstrates a different chitin-binding fold.
  evidence_ids:
  - record
  - keyword
  - type1
  - cbp21
  - go
  target_ids:
  - UniProtKB-KW:KW-0147
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0147.type1-domain-background-scope
  category: scope
  severity: minor
  title: Qualify the short disulfide-rich domain description
  description: The ancillary domain paragraph describes a 30–43-residue cysteine/disulfide
    architecture without naming type-1. PROSITE explicitly limits that architecture
    to type-1, while primary CBP21 structure/binding evidence establishes another
    fold. The first broad binding sentence and GO mapping remain sound, and no detector
    makes this architecture a class-membership condition.
  evidence_ids:
  - record
  - keyword
  - type1
  - cbp21
  - go
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0147
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
  description: Add a maintained definition correction through scripts/seed_uniprot_keywords.py
    identifying the structural paragraph as a type-1 example, or omit that ancillary
    paragraph; retain the broad binding definition and source provenance.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0147
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Corrected text does not imply all chitin-binding proteins use a 30–43-residue
    disulfide-rich domain.
  - The type-1 statement is source-cited; CBP21 evidence is not relabeled as a current
    noncatalytic family classification or promoted as a qualified example.
  - Regenerate and run strict validation, then review the corrected definition.
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
- The primary CBP21 abstract was inspected, not the full paper. Its historical CBM33
  designation is not used as a current taxonomy assertion, and no claim that CBP21
  is noncatalytic is made. No sequence detector, residue coordinates or qualified
  protein exemplar is supplied.
tags:
- unreviewed-path-order
- batch-003
- uniprot-keywords
```
