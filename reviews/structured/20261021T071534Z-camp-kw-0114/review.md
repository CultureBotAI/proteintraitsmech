# Review of cAMP

- Review: 20261021T071534Z-camp-kw-0114
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:11:05Z
- Finished UTC: 2026-10-21T07:15:34Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The cAMP-associated class and source aliases are supported. Two minor findings cover overgeneralized receptor/G-protein background and a provisional binding-versus-dependence interpretation question.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 003. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths, leaving 429339 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0114 | data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml | generated | cAMP |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0114 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0114 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0114 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0114 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0114 | Official UniProt resolves KW-0114 and source category KW-9993; no parent or GO xref is asserted locally. GO:0030552 is separately resolved as a comparison. Both primary PMIDs and DOIs were resolved in the inspected citation records. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0114.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0114.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0114.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0114.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0114.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0114.

The record denotes the broader cAMP-associated protein class, distinct from direct cAMP binding. It retains the source-dependent-function and hydrolysis alternatives.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0114.

No direct GO xref is present, consistent with both inspected official source surfaces. The binding GO term is comparison evidence only.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0114.

The only immediate source parent is the Ligand category root, intentionally excluded. No lost seeded parent is established for this target.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0114.

All five aliases are source-faithful cAMP names interpreted in protein-annotation context; the complete definition specifies the cyclic adenosine monophosphate identity.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0114.

The main class definition has source support. The unqualified receptor/G-protein background describes one important signaling route, but independent primary evidence establishes soluble cyclases with different regulation.

### Representation

representation: concern. Targets: UniProtKB-KW:KW-0114.

The source covers cAMP-dependent function or hydrolysis. Dependence alone does not establish direct cAMP binding from the text. Routing every Ligand keyword to binding capacity therefore needs a bounded interpretation check; no concrete nonbinding member has been established here.

## Findings

### F1: Qualify the receptor/G-protein signaling background

minor / open / confirmed; issue key: uniprot-keyword.KW-0114.g-protein-background-overgeneralization.

The copied background presents receptor/G-protein-coupled adenyl cyclase without a scope qualifier. Soluble mammalian cyclase is G-protein-insensitive and can be directly bicarbonate-stimulated. The core cAMP-associated protein identity remains intact, so this is a bounded background wording defect.

### F2: Resolve the binding interpretation of functional dependence

minor / open / provisional; issue key: uniprot-keyword.KW-0114.binding-versus-dependence-scope.

The source definition includes cAMP-dependent function or hydrolysis; the local enum describes ability to bind. The textual entailment gap is confirmed, but actual misclassification of source members remains provisional because this review has not established a concrete nonbinding member.

## Recommended Actions And Acceptance Checks

### A1

Add a maintained definition correction through scripts/seed_uniprot_keywords.py that labels receptor/G-protein coupling as one signaling context or shortens the ancillary background; retain original source wording as provenance.

- Corrected prose does not imply all cAMP generation requires hormone receptors or G proteins.
- Any alternative mechanism statement remains bounded to its inspected primary evidence.
- Preserve the full source class, regenerate and run strict validation plus a new review.

### A2

Check source annotation rules or a bounded, source-asserted member set for KW-0114 before changing route() in scripts/seed_uniprot_keywords.py. Document whether binding capacity covers the complete source class; preserve identity and all supported branches if a different representation is needed.

- Use inspected annotation rules or member evidence to decide whether every stated branch entails binding.
- Do not equate the whole keyword to the comparison GO binding term without source-direct equivalence evidence.
- If routing changes, regenerate through the maintained seeder, validate and save a new scoped review; if supported, record the evidence resolving this provisional concern.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-0114; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| keyword | https://rest.uniprot.org/keywords/KW-0114.json; Complete keyword JSON and X-UniProt-Release response header | supports | UniProt 2026_03 resolves cAMP KW-0114 with the same complete definition and five aliases. It covers cAMP-dependent function or hydrolysis and has only the Ligand category parent. The broader signaling prose is faithfully reproduced. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The source Ligand category covers binding, association and activity dependence; category-root entries are deliberately excluded by the seeder. |
| go-comparison | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0030552; Inspected source response captured at the recorded UTC time | context_only | GO:0030552 resolves to direct cAMP binding; it is mapped by the separate KW-0116 binding keyword, not asserted as an equivalent by KW-0114. |
| soluble-cyclase | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9874775+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Complete primary abstract and citation metadata; full text was not inspected | refutes | Buck and colleagues (1999), PMID 9874775, DOI 10.1073/pnas.96.1.79: the inspected complete primary abstract reports soluble mammalian adenylyl cyclase insensitive to G-protein or forskolin regulation, including purified rat-testis enzyme. This refutes treating G-protein-coupled hormone-receptor regulation as the sole general cAMP-generation route. |
| bicarbonate | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10915626+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Complete primary abstract and citation metadata | supports | Chen and colleagues (2000), PMID 10915626, DOI 10.1126/science.289.5479.625: the complete primary abstract reports direct bicarbonate stimulation of mammalian soluble adenylyl cyclase in vivo and in vitro, independently of pH. It supports an alternative regulatory mechanism, not annotation of every cyclase to this trait. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml; Executed 2026-10-21T07:15:08Z through 2026-10-21T07:15:09Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml; Executed 2026-10-21T07:11:35Z through 2026-10-21T07:13:12Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml; Executed 2026-10-21T07:15:09Z through 2026-10-21T07:15:09Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:13:12Z through 2026-10-21T07:13:13Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- No concrete nonbinding member of the source keyword was established; category misclassification remains provisional. Primary abstracts were inspected completely, but full-text retrieval for PMC15096 returned HTTP 500; no full-paper inspection is claimed. Other historical/background signaling statements were verified against the source rather than comprehensively researched.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T071534Z-camp-kw-0114
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of cAMP
started_at: '2026-10-21T07:11:05Z'
finished_at: '2026-10-21T07:15:34Z'
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
summary: The cAMP-associated class and source aliases are supported. Two minor findings
  cover overgeneralized receptor/G-protein background and a provisional binding-versus-dependence
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
    sha256: 1a1cc1c859426dbf684718adc1fbcf0d34d9d3aabcef777c4b33d70ed8619eed
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
  selection: Path-order position 3 in batch 003. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths,
    leaving 429339 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0114
targets:
- kind: generated
  label: cAMP
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0114
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0114
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
  - UniProtKB-KW:KW-0114
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0114
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
  - UniProtKB-KW:KW-0114
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: Official UniProt resolves KW-0114 and source category KW-9993; no parent
    or GO xref is asserted locally. GO:0030552 is separately resolved as a comparison.
    Both primary PMIDs and DOIs were resolved in the inspected citation records.
  target_ids:
  - UniProtKB-KW:KW-0114
  evidence_ids:
  - keyword
  - parent
  - mapping-file
  - go-comparison
  - soluble-cyclase
  - bicarbonate
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:11:05Z'
  snapshot_sha256: 1a1cc1c859426dbf684718adc1fbcf0d34d9d3aabcef777c4b33d70ed8619eed
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:11:05Z'
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
  accessed_at: '2026-10-21T07:11:05Z'
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
    for KW-0114; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0114.json
  accessed_at: '2026-10-21T07:10:45.506620Z'
  snapshot_sha256: bd9422affee263b0ed1ef45e84ad156bb11efc0c3ec8e7f6d5f2ae5f67bbad4e
  support: supports
  locator: Complete keyword JSON and X-UniProt-Release response header
  summary: UniProt 2026_03 resolves cAMP KW-0114 with the same complete definition
    and five aliases. It covers cAMP-dependent function or hydrolysis and has only
    the Ligand category parent. The broader signaling prose is faithfully reproduced.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:10:46.123823Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The source Ligand category covers binding, association and activity dependence;
    category-root entries are deliberately excluded by the seeder.
- evidence_id: go-comparison
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0030552
  accessed_at: '2026-10-21T07:10:46.715509Z'
  snapshot_sha256: a6baa2636634a34d36f89a0ad4f93cdf6e0acfad2131fe6419f3361ca4c4ae96
  support: context_only
  locator: Inspected source response captured at the recorded UTC time
  summary: GO:0030552 resolves to direct cAMP binding; it is mapped by the separate
    KW-0116 binding keyword, not asserted as an equivalent by KW-0114.
- evidence_id: soluble-cyclase
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9874775+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T07:11:31.965486Z'
  snapshot_sha256: 72b828ebd803d4360c2a63cd86e663bd637aee2662c068daea2baf7f0a1f54b0
  support: refutes
  locator: Complete primary abstract and citation metadata; full text was not inspected
  summary: 'Buck and colleagues (1999), PMID 9874775, DOI 10.1073/pnas.96.1.79: the
    inspected complete primary abstract reports soluble mammalian adenylyl cyclase
    insensitive to G-protein or forskolin regulation, including purified rat-testis
    enzyme. This refutes treating G-protein-coupled hormone-receptor regulation as
    the sole general cAMP-generation route.'
- evidence_id: bicarbonate
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10915626+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T07:11:32.086621Z'
  snapshot_sha256: 278f18d40fa8aa57864524c0240ea5b77596340b1fe4c03849a2b2df4ca03399
  support: supports
  locator: Complete primary abstract and citation metadata
  summary: 'Chen and colleagues (2000), PMID 10915626, DOI 10.1126/science.289.5479.625:
    the complete primary abstract reports direct bicarbonate stimulation of mammalian
    soluble adenylyl cyclase in vivo and in vitro, independently of pH. It supports
    an alternative regulatory mechanism, not annotation of every cyclase to this trait.'
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  locator: Executed 2026-10-21T07:15:08Z through 2026-10-21T07:15:09Z; exit 0
  accessed_at: '2026-10-21T07:15:09Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  locator: Executed 2026-10-21T07:15:09Z through 2026-10-21T07:15:09Z; exit 0
  accessed_at: '2026-10-21T07:15:09Z'
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
  - UniProtKB-KW:KW-0114
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
  - UniProtKB-KW:KW-0114
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
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The record denotes the broader cAMP-associated protein class, distinct
    from direct cAMP binding. It retains the source-dependent-function and hydrolysis
    alternatives.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: No direct GO xref is present, consistent with both inspected official source
    surfaces. The binding GO term is comparison evidence only.
  evidence_ids:
  - record
  - keyword
  - mapping-file
  - go-comparison
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-7
  topic: Grounding
- area: consistency
  outcome: supported
  summary: The only immediate source parent is the Ligand category root, intentionally
    excluded. No lost seeded parent is established for this target.
  evidence_ids:
  - record
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-8
  topic: Consistency
- area: nomenclature
  outcome: supported
  summary: All five aliases are source-faithful cAMP names interpreted in protein-annotation
    context; the complete definition specifies the cyclic adenosine monophosphate
    identity.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-9
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: The main class definition has source support. The unqualified receptor/G-protein
    background describes one important signaling route, but independent primary evidence
    establishes soluble cyclases with different regulation.
  evidence_ids:
  - record
  - keyword
  - soluble-cyclase
  - bicarbonate
  target_ids:
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-10
  topic: Evidence
- area: representation
  outcome: concern
  summary: The source covers cAMP-dependent function or hydrolysis. Dependence alone
    does not establish direct cAMP binding from the text. Routing every Ligand keyword
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
  - UniProtKB-KW:KW-0114
  assessment_id: assessment-11
  topic: Representation
findings:
- issue_key: uniprot-keyword.KW-0114.g-protein-background-overgeneralization
  category: scope
  severity: minor
  title: Qualify the receptor/G-protein signaling background
  description: The copied background presents receptor/G-protein-coupled adenyl cyclase
    without a scope qualifier. Soluble mammalian cyclase is G-protein-insensitive
    and can be directly bicarbonate-stimulated. The core cAMP-associated protein identity
    remains intact, so this is a bounded background wording defect.
  evidence_ids:
  - record
  - keyword
  - soluble-cyclase
  - bicarbonate
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0114
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: confirmed
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, hierarchy completeness
    or interpretation needs follow-up.
- issue_key: uniprot-keyword.KW-0114.binding-versus-dependence-scope
  category: scope
  severity: minor
  title: Resolve the binding interpretation of functional dependence
  description: The source definition includes cAMP-dependent function or hydrolysis;
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
  finding_id: F2
  status: open
  target_ids:
  - UniProtKB-KW:KW-0114
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
  description: Add a maintained definition correction through scripts/seed_uniprot_keywords.py
    that labels receptor/G-protein coupling as one signaling context or shortens the
    ancillary background; retain original source wording as provenance.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0114
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - Corrected prose does not imply all cAMP generation requires hormone receptors
    or G proteins.
  - Any alternative mechanism statement remains bounded to its inspected primary evidence.
  - Preserve the full source class, regenerate and run strict validation plus a new
    review.
- action_id: A2
  description: Check source annotation rules or a bounded, source-asserted member
    set for KW-0114 before changing route() in scripts/seed_uniprot_keywords.py. Document
    whether binding capacity covers the complete source class; preserve identity and
    all supported branches if a different representation is needed.
  finding_ids:
  - F2
  target_ids:
  - UniProtKB-KW:KW-0114
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
- No concrete nonbinding member of the source keyword was established; category misclassification
  remains provisional. Primary abstracts were inspected completely, but full-text
  retrieval for PMC15096 returned HTTP 500; no full-paper inspection is claimed. Other
  historical/background signaling statements were verified against the source rather
  than comprehensively researched.
tags:
- unreviewed-path-order
- batch-003
- uniprot-keywords
```
