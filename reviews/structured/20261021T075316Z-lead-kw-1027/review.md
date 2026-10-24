# Review of Lead

- Review: 20261021T075316Z-lead-kw-1027
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:48:08Z
- Finished UTC: 2026-10-21T07:53:16Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The lead-associated protein identity and aliases are supported. One minor provisional finding asks whether the binding-capacity category covers the full functional-dependence branch.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 5 in batch 005. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca covers 38 record paths, leaving 429321 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-1027 | data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml | generated | Lead |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-1027 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-1027 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-1027 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-1027 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-1027 | UniProt resolves KW-1027 and category KW-9993. No local parent or GO xref is asserted; nonobsolete GO:0005488 is comparison-only. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-1027.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-1027.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-1027.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-1027.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-1027.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-1027.

The definition denotes lead-associated proteins, not elemental lead. Pb is the correct symbol; no essentiality, beneficial effect or particular oxidation state is asserted.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-1027.

No GO xref is asserted, consistent with both inspected official source surfaces. Generic binding is not promoted to a direct equivalent.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-1027.

The sole source parent is the intentionally excluded Ligand root; the source does not assert a Metal-binding parent for this keyword.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-1027.

The five lead/Pb aliases match the source in the protein-keyword context, without introducing a metal-species or oxidation-state restriction.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-1027.

The official source supports the protein-class identity and metallic-element background. The dependence branch warrants a separate bounded interpretation check.

### Representation

representation: concern. Targets: UniProtKB-KW:KW-1027.

The source covers lead binding or lead-dependent function. Dependence alone does not establish direct lead binding from the text. Routing every Ligand keyword to binding capacity therefore needs a bounded interpretation check; no concrete nonbinding member has been established here.

## Findings

### F1: Resolve the binding interpretation of functional dependence

minor / open / provisional; issue key: uniprot-keyword.KW-1027.binding-versus-dependence-scope.

The source definition includes lead binding or lead-dependent function; the local enum describes ability to bind. The textual entailment gap is confirmed, but actual misclassification of source members remains provisional because this review has not established a concrete nonbinding member.

## Recommended Actions And Acceptance Checks

### A1

Check source annotation rules or a bounded, source-asserted member set for KW-1027 before changing route() in scripts/seed_uniprot_keywords.py. Document whether binding capacity covers the complete source class; preserve identity and all supported branches if a different representation is needed.

- Use inspected annotation rules or member evidence to decide whether every stated branch entails binding.
- Do not equate the whole keyword to the comparison GO binding term without source-direct equivalence evidence.
- If routing changes, regenerate through the maintained seeder, validate and save a new scoped review; if supported, record the evidence resolving this provisional concern.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-1027; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| keyword | https://rest.uniprot.org/keywords/KW-1027.json; Inspected source response captured at the recorded UTC time | supports | UniProt resolves Lead KW-1027, reproducing the complete binding-or-dependence definition and five lead/Pb aliases. Only Ligand is an immediate parent; no GO mapping is supplied; comparison release2026_03. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | Ligand covers binding, association and activity dependence; it is intentionally omitted as a category root. |
| go-comparison | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005488; Inspected source response captured at the recorded UTC time | context_only | Nonobsolete GO:0005488 defines selective noncovalent binding; it is a generic scope comparison, not an asserted Lead equivalent. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml; Executed 2026-10-21T07:51:25Z through 2026-10-21T07:51:45Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml data/traits/function/binding_capacity/uniprot_keywords/iron-kw-0408.yaml data/traits/function/binding_capacity/uniprot_keywords/iron-sulfur-kw-0411.yaml data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml data/traits/function/binding_capacity/uniprot_keywords/lectin-kw-0430.yaml data/traits/function/binding_capacity/uniprot_keywords/lipid-binding-kw-0446.yaml data/traits/function/binding_capacity/uniprot_keywords/lithium-kw-0452.yaml data/traits/function/binding_capacity/uniprot_keywords/magnesium-kw-0460.yaml data/traits/function/binding_capacity/uniprot_keywords/manganese-kw-0464.yaml; Executed 2026-10-21T07:49:45Z through 2026-10-21T07:52:04Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml; Executed 2026-10-21T07:51:45Z through 2026-10-21T07:51:46Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:52:04Z through 2026-10-21T07:52:05Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- No concrete nonbinding lead-dependent source member was established. No biological essentiality, oxidation state, ligand geometry or protein example is qualified.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T075316Z-lead-kw-1027
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Lead
started_at: '2026-10-21T07:48:08Z'
finished_at: '2026-10-21T07:53:16Z'
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
summary: The lead-associated protein identity and aliases are supported. One minor
  provisional finding asks whether the binding-capacity category covers the full functional-dependence
  branch.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
    sha256: cbfa1e0c4473205655038cee06ac5e742a0a3f713651690918356f9466d8ad1c
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
  selection: Path-order position 5 in batch 005. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca covers 38 record paths,
    leaving 429321 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-1027
targets:
- kind: generated
  label: Lead
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-1027
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-1027
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml
    data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml
    data/traits/function/binding_capacity/uniprot_keywords/iron-kw-0408.yaml data/traits/function/binding_capacity/uniprot_keywords/iron-sulfur-kw-0411.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml data/traits/function/binding_capacity/uniprot_keywords/lectin-kw-0430.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lipid-binding-kw-0446.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lithium-kw-0452.yaml data/traits/function/binding_capacity/uniprot_keywords/magnesium-kw-0460.yaml
    data/traits/function/binding_capacity/uniprot_keywords/manganese-kw-0464.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-1027
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-1027
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
  - UniProtKB-KW:KW-1027
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: UniProt resolves KW-1027 and category KW-9993. No local parent or GO xref
    is asserted; nonobsolete GO:0005488 is comparison-only.
  target_ids:
  - UniProtKB-KW:KW-1027
  evidence_ids:
  - keyword
  - parent
  - mapping-file
  - go-comparison
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:48:08Z'
  snapshot_sha256: cbfa1e0c4473205655038cee06ac5e742a0a3f713651690918356f9466d8ad1c
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:48:08Z'
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
  accessed_at: '2026-10-21T07:48:08Z'
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
- evidence_id: mapping-file
  kind: database
  reference: https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go
  accessed_at: '2026-10-21T06:55:26.808623Z'
  snapshot_sha256: f38e663ed40d606803242afca204c0f285f211423c237251012b61f68ebdb36d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The complete official mapping file, version 2026/07/06 14:08:43, was searched
    for KW-1027; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-1027.json
  accessed_at: '2026-10-21T07:49:16.370349Z'
  snapshot_sha256: 390955665a919e685e073c324331b49c40d3f54cd4beb9f23e5fc8d522f4cf47
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: UniProt resolves Lead KW-1027, reproducing the complete binding-or-dependence
    definition and five lead/Pb aliases. Only Ligand is an immediate parent; no GO
    mapping is supplied; comparison release2026_03.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Ligand covers binding, association and activity dependence; it is intentionally
    omitted as a category root.
- evidence_id: go-comparison
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005488
  accessed_at: '2026-10-21T07:30:35.712062Z'
  snapshot_sha256: 6015a69036105c45e68c1938c9169449c9c69dabee51b002563d8f9e97ab667a
  support: context_only
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0005488 defines selective noncovalent binding; it is a generic
    scope comparison, not an asserted Lead equivalent.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  locator: Executed 2026-10-21T07:51:25Z through 2026-10-21T07:51:45Z; exit 0
  accessed_at: '2026-10-21T07:51:45Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml
    data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml
    data/traits/function/binding_capacity/uniprot_keywords/iron-kw-0408.yaml data/traits/function/binding_capacity/uniprot_keywords/iron-sulfur-kw-0411.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml data/traits/function/binding_capacity/uniprot_keywords/lectin-kw-0430.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lipid-binding-kw-0446.yaml
    data/traits/function/binding_capacity/uniprot_keywords/lithium-kw-0452.yaml data/traits/function/binding_capacity/uniprot_keywords/magnesium-kw-0460.yaml
    data/traits/function/binding_capacity/uniprot_keywords/manganese-kw-0464.yaml
  locator: Executed 2026-10-21T07:49:45Z through 2026-10-21T07:52:04Z; exit 0
  accessed_at: '2026-10-21T07:52:04Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/lead-kw-1027.yaml
  locator: Executed 2026-10-21T07:51:45Z through 2026-10-21T07:51:46Z; exit 0
  accessed_at: '2026-10-21T07:51:46Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T07:52:04Z through 2026-10-21T07:52:05Z; exit 0
  accessed_at: '2026-10-21T07:52:05Z'
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
  - UniProtKB-KW:KW-1027
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
  - UniProtKB-KW:KW-1027
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
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The definition denotes lead-associated proteins, not elemental lead. Pb
    is the correct symbol; no essentiality, beneficial effect or particular oxidation
    state is asserted.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: No GO xref is asserted, consistent with both inspected official source
    surfaces. Generic binding is not promoted to a direct equivalent.
  evidence_ids:
  - record
  - keyword
  - mapping-file
  - go-comparison
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-7
  topic: Grounding
- area: consistency
  outcome: supported
  summary: The sole source parent is the intentionally excluded Ligand root; the source
    does not assert a Metal-binding parent for this keyword.
  evidence_ids:
  - record
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-8
  topic: Consistency
- area: nomenclature
  outcome: supported
  summary: The five lead/Pb aliases match the source in the protein-keyword context,
    without introducing a metal-species or oxidation-state restriction.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-9
  topic: Nomenclature
- area: evidence
  outcome: supported
  summary: The official source supports the protein-class identity and metallic-element
    background. The dependence branch warrants a separate bounded interpretation check.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-10
  topic: Evidence
- area: representation
  outcome: concern
  summary: The source covers lead binding or lead-dependent function. Dependence alone
    does not establish direct lead binding from the text. Routing every Ligand keyword
    to binding capacity therefore needs a bounded interpretation check; no concrete
    nonbinding member has been established here.
  evidence_ids:
  - record
  - keyword
  - parent
  - schema
  - owner
  - go-comparison
  target_ids:
  - UniProtKB-KW:KW-1027
  assessment_id: assessment-11
  topic: Representation
findings:
- issue_key: uniprot-keyword.KW-1027.binding-versus-dependence-scope
  category: scope
  severity: minor
  title: Resolve the binding interpretation of functional dependence
  description: The source definition includes lead binding or lead-dependent function;
    the local enum describes ability to bind. The textual entailment gap is confirmed,
    but actual misclassification of source members remains provisional because this
    review has not established a concrete nonbinding member.
  evidence_ids:
  - record
  - keyword
  - parent
  - schema
  - owner
  - go-comparison
  certainty: provisional
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-1027
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, hierarchy completeness
    or interpretation needs follow-up.
actions:
- action_id: A1
  description: Check source annotation rules or a bounded, source-asserted member
    set for KW-1027 before changing route() in scripts/seed_uniprot_keywords.py. Document
    whether binding capacity covers the complete source class; preserve identity and
    all supported branches if a different representation is needed.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-1027
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Use inspected annotation rules or member evidence to decide whether every stated
    branch entails binding.
  - Do not equate the whole keyword to the comparison GO binding term without source-direct
    equivalence evidence.
  - If routing changes, regenerate through the maintained seeder, validate and save
    a new scoped review; if supported, record the evidence resolving this provisional
    concern.
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
- No concrete nonbinding lead-dependent source member was established. No biological
  essentiality, oxidation state, ligand geometry or protein example is qualified.
tags:
- unreviewed-path-order
- batch-005
- uniprot-keywords
```
