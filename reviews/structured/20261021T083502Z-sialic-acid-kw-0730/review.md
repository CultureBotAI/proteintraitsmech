# Review of Sialic acid

- Review: 20261021T083502Z-sialic-acid-kw-0730
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:29:37Z
- Finished UTC: 2026-10-21T08:35:02Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Sialic-acid protein-class identity is supported, but the source covalent glyco-composition predicate is routed as binding ability. This is one major representation finding requiring a maintained routing/schema decision.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 008. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5 covers 68 record paths, leaving 429291 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0730 | data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml | generated | Sialic acid |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0730 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0730 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0730 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0730 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0730 | KW-0730, both source parents KW-9993/KW-0325 and PTM KW-9991 resolve. The target has no GO equivalence; ChEBI is chemical context only. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0730.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0730.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0730.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0730.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0730.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0730.

KW-0730 denotes proteins carrying sialic-acid material, not a free sugar or a specific protein instance. Source label and definition match the target.

### Representation

representation: concern. Targets: UniProtKB-KW:KW-0730.

The source definition is a composition/modification predicate, supported by its explicit covalent Glycoprotein ancestry. The maintained Ligand-to-FUNC_BINDING_CAPACITY route recasts it as a molecular binding ability without representation-specific justification. This concerns the class predicate, not whether any particular member can bind.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0730.

The source has Ligand and Glycoprotein parents. The maintained seeder routes Ligand but not PTM keywords; dropping the PTM ancestry follows that implementation, yet exposes the representation issue. This review does not claim a dangling or missing existing local Glycoprotein record.

## Findings

### F1: Covalent glyco-composition is routed as binding capacity

major / open / confirmed; issue key: uniprot-keyword.KW-0730.composition-versus-binding-route.

The target says that a protein has sialic-acid material, and the source explicitly places it under Glycoprotein, defined by covalently linked carbohydrate, and PTM. The current generator routes every Ligand keyword to an ability-to-bind category. That category does not preserve the source defining predicate of protein composition/modification. No member is claimed unable to bind; possessing an attached glycan and possessing a molecular binding ability are different assertions.

## Recommended Actions And Acceptance Checks

### A1

Review the maintained Ligand routing policy and represent this whole-protein composition/modification class explicitly, preserving source identity and ancestry. Determine the appropriate schema representation before regeneration; do not automatically convert it to a residue-localized glycosylation-site class.

- The chosen representation preserves the whole-protein covalent glyco-composition predicate with explicit rationale.
- Do not infer nonbinding members or invent residue coordinates.
- Test the maintained route, regenerate through the seeder, run strict validation and save a new scoped review.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0730.json; Inspected source response captured at the recorded UTC time | supports | Complete official keyword response confirms stable identity, copied definition, aliases when present and asserted parent/GO references. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The source Ligand root includes binding, association and functional dependence, not only binding capacity. |
| glycoprotein | https://rest.uniprot.org/keywords/KW-0325.json; Inspected source response captured at the recorded UTC time | supports | Glycoprotein KW-0325 explicitly denotes proteins containing covalently linked carbohydrate and lists Sialic acid as a child; it is under PTM KW-9991. |
| ptm | https://rest.uniprot.org/keywords/KW-9991.json; Inspected source response captured at the recorded UTC time | supports | The source PTM category denotes differences from translation due to post-translational modification. It corroborates the covalent-modification interpretation of the source ancestry. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_26667; Inspected source response captured at the recorded UTC time | supports | ChEBI:26667 denotes a sialic-acid chemical group of N-acylneuraminic-acid derivatives. It supports group rather than single-sugar identity; the exact neuraminic-acid boundary is not adjudicated here. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-0730; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| member-context | https://rest.uniprot.org/uniprotkb/P02724.json; Keyword assignments and PTM comment; no canonical example or residue coordinates qualified | supports | Reviewed human glycophorin-A P02724 explicitly carries KW-0730 and Glycoprotein KW-0325. Its PTM comment describes NeuAc-bearing O-linked glycans with accession-linked experimental references. This illustrates the positive composition predicate, not an absence of binding activities. |
| primary-glycan | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15313217%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID and complete indexed abstract; full paper not inspected | supports | The complete indexed primary abstract PMID:15313217 reports isolated human glycophorin-A O-glycans with linked NeuAc residues and structural mass-spectrometric characterization. The paper is cited by P02724 for its PTM description. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml; Executed 2026-10-21T08:29:59Z through 2026-10-21T08:30:03Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml data/traits/function/binding_capacity/uniprot_keywords/sodium-kw-0915.yaml data/traits/function/binding_capacity/uniprot_keywords/steroid-binding-kw-0754.yaml data/traits/function/binding_capacity/uniprot_keywords/thiamine-pyrophosphate-kw-0786.yaml data/traits/function/binding_capacity/uniprot_keywords/tungsten-kw-0826.yaml data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml data/traits/function/binding_capacity/uniprot_keywords/vanadium-kw-0837.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-c-kw-0847.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-d-kw-0848.yaml; Executed 2026-10-21T08:29:58Z through 2026-10-21T08:33:41Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml; Executed 2026-10-21T08:30:03Z through 2026-10-21T08:30:03Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:33:41Z through 2026-10-21T08:33:43Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- The appropriate replacement whole-protein modification representation is unresolved. Existing residue/site categories are not automatically suitable. The source and ChEBI use somewhat different wording for the sialic-acid chemical boundary; no false chemical identity or source-member exclusion is inferred.
- The source-assigned P02724 example and its complete indexed primary abstract corroborate glyco-composition only. The full paper was not inspected; no example qualification, residue annotation or inference of absent binding is made.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T083502Z-sialic-acid-kw-0730
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Sialic acid
started_at: '2026-10-21T08:29:37Z'
finished_at: '2026-10-21T08:35:02Z'
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
summary: Sialic-acid protein-class identity is supported, but the source covalent
  glyco-composition predicate is routed as binding ability. This is one major representation
  finding requiring a maintained routing/schema decision.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
    sha256: 5b8f5cac8aa485cc20b70535da1892f2e8de80b1335e388add522da19ced8549
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
  selection: Path-order position 1 in batch 008. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc
    and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5
    covers 68 record paths, leaving 429291 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0730
targets:
- kind: generated
  label: Sialic acid
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0730
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0730
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
  - UniProtKB-KW:KW-0730
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0730
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
  - UniProtKB-KW:KW-0730
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: KW-0730, both source parents KW-9993/KW-0325 and PTM KW-9991 resolve. The
    target has no GO equivalence; ChEBI is chemical context only.
  target_ids:
  - UniProtKB-KW:KW-0730
  evidence_ids:
  - keyword
  - parent
  - glycoprotein
  - ptm
  - chemical
  - mapping-file
  - member-context
  - primary-glycan
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:29:37Z'
  snapshot_sha256: 5b8f5cac8aa485cc20b70535da1892f2e8de80b1335e388add522da19ced8549
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T08:29:37Z'
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
  accessed_at: '2026-10-21T08:29:37Z'
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
  reference: https://rest.uniprot.org/keywords/KW-0730.json
  accessed_at: '2026-10-21T08:30:18.797708Z'
  snapshot_sha256: 44aceee2b51136e8e791ff0cecc493fc722799f4cbf247e42aef021132f95ce1
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Complete official keyword response confirms stable identity, copied definition,
    aliases when present and asserted parent/GO references.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The source Ligand root includes binding, association and functional dependence,
    not only binding capacity.
- evidence_id: glycoprotein
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0325.json
  accessed_at: '2026-10-21T08:30:46.907469Z'
  snapshot_sha256: 4548342dc017862fd3c8817ecfde0ff4a7b9e73558a30eec30cc4c482d0319cc
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Glycoprotein KW-0325 explicitly denotes proteins containing covalently
    linked carbohydrate and lists Sialic acid as a child; it is under PTM KW-9991.
- evidence_id: ptm
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9991.json
  accessed_at: '2026-10-21T08:30:46.931419Z'
  snapshot_sha256: d25ff04b1ec75de8e3a86d8b3b1d7001835d610dd7acd8f8db7b539b9a8f2b3d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The source PTM category denotes differences from translation due to post-translational
    modification. It corroborates the covalent-modification interpretation of the
    source ancestry.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_26667
  accessed_at: '2026-10-21T08:31:57.662666Z'
  snapshot_sha256: e4e93c19fd146a75a7b938c5d5db8994c7ce64fc5f7bba736bca2bfa3e4900e0
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: ChEBI:26667 denotes a sialic-acid chemical group of N-acylneuraminic-acid
    derivatives. It supports group rather than single-sugar identity; the exact neuraminic-acid
    boundary is not adjudicated here.
- evidence_id: mapping-file
  kind: database
  reference: https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go
  accessed_at: '2026-10-21T06:55:26.808623Z'
  snapshot_sha256: f38e663ed40d606803242afca204c0f285f211423c237251012b61f68ebdb36d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The complete official mapping file, version 2026/07/06 14:08:43, was searched
    for KW-0730; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: member-context
  kind: database
  reference: https://rest.uniprot.org/uniprotkb/P02724.json
  accessed_at: '2026-10-21T08:32:30.558362Z'
  snapshot_sha256: d18b167bb5d704790f94778378c9a445959098c84df1a601da22777ba06b2a43
  support: supports
  locator: Keyword assignments and PTM comment; no canonical example or residue coordinates
    qualified
  summary: Reviewed human glycophorin-A P02724 explicitly carries KW-0730 and Glycoprotein
    KW-0325. Its PTM comment describes NeuAc-bearing O-linked glycans with accession-linked
    experimental references. This illustrates the positive composition predicate,
    not an absence of binding activities.
- evidence_id: primary-glycan
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15313217%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:32:49.183093Z'
  snapshot_sha256: 01dedddd4d7ccf033e3e301834754a37329b2b70f19f790624b6298bca0c0d5e
  support: supports
  locator: Title, PMID and complete indexed abstract; full paper not inspected
  summary: The complete indexed primary abstract PMID:15313217 reports isolated human
    glycophorin-A O-glycans with linked NeuAc residues and structural mass-spectrometric
    characterization. The paper is cited by P02724 for its PTM description.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  locator: Executed 2026-10-21T08:29:59Z through 2026-10-21T08:30:03Z; exit 0
  accessed_at: '2026-10-21T08:30:03Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml
  locator: Executed 2026-10-21T08:30:03Z through 2026-10-21T08:30:03Z; exit 0
  accessed_at: '2026-10-21T08:30:03Z'
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
  - UniProtKB-KW:KW-0730
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
  - UniProtKB-KW:KW-0730
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
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: KW-0730 denotes proteins carrying sialic-acid material, not a free sugar
    or a specific protein instance. Source label and definition match the target.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-6
  topic: Identity
- area: representation
  outcome: concern
  summary: The source definition is a composition/modification predicate, supported
    by its explicit covalent Glycoprotein ancestry. The maintained Ligand-to-FUNC_BINDING_CAPACITY
    route recasts it as a molecular binding ability without representation-specific
    justification. This concerns the class predicate, not whether any particular member
    can bind.
  evidence_ids:
  - record
  - keyword
  - glycoprotein
  - ptm
  - parent
  - schema
  - owner
  - member-context
  - primary-glycan
  target_ids:
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-7
  topic: Representation
- area: consistency
  outcome: supported
  summary: The source has Ligand and Glycoprotein parents. The maintained seeder routes
    Ligand but not PTM keywords; dropping the PTM ancestry follows that implementation,
    yet exposes the representation issue. This review does not claim a dangling or
    missing existing local Glycoprotein record.
  evidence_ids:
  - record
  - keyword
  - glycoprotein
  - ptm
  - owner
  target_ids:
  - UniProtKB-KW:KW-0730
  assessment_id: assessment-8
  topic: Consistency
findings:
- issue_key: uniprot-keyword.KW-0730.composition-versus-binding-route
  category: representation
  severity: major
  title: Covalent glyco-composition is routed as binding capacity
  description: The target says that a protein has sialic-acid material, and the source
    explicitly places it under Glycoprotein, defined by covalently linked carbohydrate,
    and PTM. The current generator routes every Ligand keyword to an ability-to-bind
    category. That category does not preserve the source defining predicate of protein
    composition/modification. No member is claimed unable to bind; possessing an attached
    glycan and possessing a molecular binding ability are different assertions.
  evidence_ids:
  - record
  - keyword
  - glycoprotein
  - ptm
  - parent
  - schema
  - owner
  - member-context
  - primary-glycan
  normalization_reason: The generator materially changes the kind of trait asserted,
    from whole-protein covalent glyco-composition to binding ability.
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0730
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Review the maintained Ligand routing policy and represent this whole-protein
    composition/modification class explicitly, preserving source identity and ancestry.
    Determine the appropriate schema representation before regeneration; do not automatically
    convert it to a residue-localized glycosylation-site class.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0730
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - The chosen representation preserves the whole-protein covalent glyco-composition
    predicate with explicit rationale.
  - Do not infer nonbinding members or invent residue coordinates.
  - Test the maintained route, regenerate through the seeder, run strict validation
    and save a new scoped review.
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
- The appropriate replacement whole-protein modification representation is unresolved.
  Existing residue/site categories are not automatically suitable. The source and
  ChEBI use somewhat different wording for the sialic-acid chemical boundary; no false
  chemical identity or source-member exclusion is inferred.
- The source-assigned P02724 example and its complete indexed primary abstract corroborate
  glyco-composition only. The full paper was not inspected; no example qualification,
  residue annotation or inference of absent binding is made.
tags:
- unreviewed-path-order
- batch-008
- uniprot-keywords
```
