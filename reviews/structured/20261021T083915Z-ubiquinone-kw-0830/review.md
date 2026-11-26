# Review of Ubiquinone

- Review: 20261021T083915Z-ubiquinone-kw-0830
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:29:42Z
- Finished UTC: 2026-10-21T08:39:15Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

Ubiquinone interaction-class identity, chemical aliases and bounded organism/homologue occurrence examples are supported. One minor finding qualifies universal mobility, absence-of-tight-binding and redox-fate wording.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 008. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5 covers 68 record paths, leaving 429291 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0830 | data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml | generated | Ubiquinone |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0830 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0830 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0830 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0830 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0830 | KW-0830 and Ligand parent resolve; ChEBI:16389 and the cited primary DOI/PMID resolve. No GO equivalence is asserted. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0830.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0830.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0830.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0830.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0830.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0830.

KW-0830 denotes ubiquinone-interacting proteins, not a single chemical species or protein instance. The core source identity remains supported.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0830.

Only the Ligand category is an immediate source parent. Omission of a category-root link follows the maintained generator policy.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0830.

A defined protein interaction with the ubiquinone ligand class supports FUNCTION/binding-capacity placement without asserting site coordinates.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0830.

Coenzyme Q and CoQ identify the source ligand class; they do not specify a single side-chain homologue.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0830.

The mobile-pool and universal absence-of-tight-binding background needs qualification. The direct Gluconobacter experiment reports tightly bound Q under stated preparation conditions, and the QA study distinguishes retained one-electron cycling from exchangeable QB quinol. The opening interaction class remains valid.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-0830.

All seven organism/homologue examples have bounded occurrence support. Rat/human tissue mixtures and R. capsulatus trace Q9 prevent interpreting the list as exclusive or universally predominant species composition.

## Findings

### F1: Qualify mobile-pool and redox-cycle generalizations

minor / open / confirmed; issue key: uniprot-keyword.KW-0830.mobile-pool-generalization.

The copied background states ubiquinone is not tightly bound and is mobile, alongside an unqualified full-reduction narrative. A primary Gluconobacter alcohol-dehydrogenase study reports tightly bound ubiquinone in dodecyl-maltoside preparation but not Triton X-100 preparation. The separate QA study describes retained neutral/semiquinone cycling versus exchangeable reduced QB quinol. These observations support qualifying the background by protein/site and preparation; they do not challenge the core interaction class, prove a covalent linkage, or establish a universal affinity threshold.

## Recommended Actions And Acceptance Checks

### A1

Qualify the maintained background to distinguish mobile membrane-pool/exchangeable QB contexts from retained QA roles and experimentally observed tight-binding contexts. Preserve the source attribution and core interaction-class definition.

- State that mobility and redox fate depend on the protein/site context.
- Do not equate kinetic residence with measured thermodynamic tightness or simulated energies with new experimental affinity measurements.
- Regenerate through the maintained source transform and validate.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0830.json; Inspected source response captured at the recorded UTC time | supports | Complete official keyword response confirms accession, label, copied definition, source aliases and GO associations where present, and sole immediate Ligand parent. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The Ligand category includes binding, association and activity dependence; its meaning is broader than direct binding capacity. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16389; Inspected source response captured at the recorded UTC time | supports | ChEBI:16389 defines the ubiquinone homologous chemical class and CoQ/coenzyme-Q naming with variable polyprenyl-chain lengths. |
| qa-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3202297/fullTextXML; Full-text abstract, introduction and methods/discussion context; no new experiment or affinity threshold inferred | supports | PMID:21863833; DOI:10.1021/ja205811f. The full-text abstract and introduction describe QA ubiquinone cycling between neutral and semiquinone states while remaining protein-bound under physiological conditions, unlike the released reduced QB quinol. The study uses computational unbinding models and cited prior experiments; kinetic residence and thermodynamic affinity are distinguished. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-0830; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| tight-binding-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1271/bbb.80363&amp;format=json&amp;resultType=core; Title, DOI/PMID and complete indexed abstract; full paper not inspected | supports | PMID:18838797; DOI:10.1271/bbb.80363. The complete indexed primary abstract reports tightly bound ubiquinone retained in Gluconobacter suboxydans alcohol dehydrogenase purified with dodecyl maltoside, unlike Triton X-100 preparation. Inhibitor kinetics suggest a high-affinity site. This establishes a context-specific exception to unqualified absence of tight binding. |
| yeast-q6 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9708911%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID/DOI and complete indexed primary abstract; full paper not inspected | supports | PMID:9708911 describes original Saccharomyces cerevisiae UQ6 while experimentally producing other chain lengths; this supports occurrence, not exclusive composition. |
| ecoli-q8 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15459799%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID/DOI and complete indexed primary abstract; full paper not inspected | supports | PMID:15459799 explicitly contrasts endogenous E. coli Q8 with engineered production of Q10; the recombinant Q10 result is not mistaken for the unmodified baseline. |
| gluconobacter-q10 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A2547757%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID/DOI and complete indexed primary abstract; full paper not inspected | supports | PMID:2547757 identifies Q10 as native Gluconobacter suboxydans ubiquinone while testing respiratory electron transfer. |
| pombe-q10 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A24911838%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID/DOI and complete indexed primary abstract; full paper not inspected | supports | PMID:24911838 describes Q10-deficient Schizosaccharomyces pombe deletion strains and restoration of Q10 production. |
| mammal-homologues | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A1586151%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Title, PMID/DOI and complete indexed primary abstract; full paper not inspected | supports | PMID:1586151 measures Q9 in rat and Q10 in human tissues, with additional Q10 in rat and Q9 in humans. This supports the stated occurrence examples without exclusivity. |
| capsulatus-homologues | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10626278/fullTextXML; Full-text Figure 4 caption and associated LC–MS methods/results | supports | PMID:37716914; DOI:10.1002/2211-5463.13707. Figure 4 explicitly reports major UQ10 and trace UQ9 in Rhodobacter capsulatus MT1131. Thus the target literal occurrence of Q9 is not disproven; the result is strain/context-specific. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml; Executed 2026-10-21T08:30:27Z through 2026-10-21T08:30:30Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/sialic-acid-kw-0730.yaml data/traits/function/binding_capacity/uniprot_keywords/sodium-kw-0915.yaml data/traits/function/binding_capacity/uniprot_keywords/steroid-binding-kw-0754.yaml data/traits/function/binding_capacity/uniprot_keywords/thiamine-pyrophosphate-kw-0786.yaml data/traits/function/binding_capacity/uniprot_keywords/tungsten-kw-0826.yaml data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml data/traits/function/binding_capacity/uniprot_keywords/vanadium-kw-0837.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-a-kw-0845.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-c-kw-0847.yaml data/traits/function/binding_capacity/uniprot_keywords/vitamin-d-kw-0848.yaml; Executed 2026-10-21T08:29:58Z through 2026-10-21T08:33:41Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml; Executed 2026-10-21T08:30:30Z through 2026-10-21T08:30:30Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:33:41Z through 2026-10-21T08:33:43Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- The QA primary paper is computational with cited experimental context; its kinetic residence description is not a new universal affinity measurement. The tight-binding result is preparation-specific and was inspected through a complete indexed abstract.
- Five complete indexed primary abstracts support the remaining organism/homologue examples; the R. capsulatus full-text figure supports trace Q9 in strain MT1131. These are occurrence checks, not exclusive or universal species compositions. No proteins, coordinates or mechanisms are qualified.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T083915Z-ubiquinone-kw-0830
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Ubiquinone
started_at: '2026-10-21T08:29:42Z'
finished_at: '2026-10-21T08:39:15Z'
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
summary: Ubiquinone interaction-class identity, chemical aliases and bounded organism/homologue
  occurrence examples are supported. One minor finding qualifies universal mobility,
  absence-of-tight-binding and redox-fate wording.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
    sha256: 4328bba9861e1634114c9585ed4f9e13d35f33c2bad1ea5c9712ffedbb5d6c34
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
  selection: Path-order position 6 in batch 008. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    and batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca and batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc
    and batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1 and batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5
    covers 68 record paths, leaving 429291 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0830
targets:
- kind: generated
  label: Ubiquinone
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0830
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0830
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
  - UniProtKB-KW:KW-0830
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0830
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
  - UniProtKB-KW:KW-0830
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: KW-0830 and Ligand parent resolve; ChEBI:16389 and the cited primary DOI/PMID
    resolve. No GO equivalence is asserted.
  target_ids:
  - UniProtKB-KW:KW-0830
  evidence_ids:
  - keyword
  - parent
  - chemical
  - qa-primary
  - mapping-file
  - tight-binding-primary
  - yeast-q6
  - ecoli-q8
  - gluconobacter-q10
  - pombe-q10
  - mammal-homologues
  - capsulatus-homologues
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:29:42Z'
  snapshot_sha256: 4328bba9861e1634114c9585ed4f9e13d35f33c2bad1ea5c9712ffedbb5d6c34
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T08:29:42Z'
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
  accessed_at: '2026-10-21T08:29:42Z'
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
  reference: https://rest.uniprot.org/keywords/KW-0830.json
  accessed_at: '2026-10-21T08:30:14.410247Z'
  snapshot_sha256: 41e08138903d7b744d7ebe760b4e3d31f5e9bc3873f5ba451e6a24f49d8dc050
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
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16389
  accessed_at: '2026-10-21T08:32:11.787041Z'
  snapshot_sha256: 4e0e9e0f77b543b84eb677da1c95d55838e5b952ee1324cf9d710897361e8f9e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: ChEBI:16389 defines the ubiquinone homologous chemical class and CoQ/coenzyme-Q
    naming with variable polyprenyl-chain lengths.
- evidence_id: qa-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3202297/fullTextXML
  accessed_at: '2026-10-21T08:32:11.785279Z'
  snapshot_sha256: 38ba3cb5f3cee2bb206c0887f02c1566af2dfe9e8e3e861ca38e981ed935187a
  support: supports
  locator: Full-text abstract, introduction and methods/discussion context; no new
    experiment or affinity threshold inferred
  summary: PMID:21863833; DOI:10.1021/ja205811f. The full-text abstract and introduction
    describe QA ubiquinone cycling between neutral and semiquinone states while remaining
    protein-bound under physiological conditions, unlike the released reduced QB quinol.
    The study uses computational unbinding models and cited prior experiments; kinetic
    residence and thermodynamic affinity are distinguished.
- evidence_id: mapping-file
  kind: database
  reference: https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go
  accessed_at: '2026-10-21T06:55:26.808623Z'
  snapshot_sha256: f38e663ed40d606803242afca204c0f285f211423c237251012b61f68ebdb36d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The complete official mapping file, version 2026/07/06 14:08:43, was searched
    for KW-0830; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: tight-binding-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1271/bbb.80363&format=json&resultType=core
  accessed_at: '2026-10-21T08:36:15.482204Z'
  snapshot_sha256: 0b1b220feae29b130705dfb1d94c6dc85b05b154250920e8ff35c643d644480e
  support: supports
  locator: Title, DOI/PMID and complete indexed abstract; full paper not inspected
  summary: PMID:18838797; DOI:10.1271/bbb.80363. The complete indexed primary abstract
    reports tightly bound ubiquinone retained in Gluconobacter suboxydans alcohol
    dehydrogenase purified with dodecyl maltoside, unlike Triton X-100 preparation.
    Inhibitor kinetics suggest a high-affinity site. This establishes a context-specific
    exception to unqualified absence of tight binding.
- evidence_id: yeast-q6
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9708911%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:36:25.640042Z'
  snapshot_sha256: 7cd33a56a5c5489fc65a41a0700fe65f9428958ee1dbf9ab93372b334ecdf14c
  support: supports
  locator: Title, PMID/DOI and complete indexed primary abstract; full paper not inspected
  summary: PMID:9708911 describes original Saccharomyces cerevisiae UQ6 while experimentally
    producing other chain lengths; this supports occurrence, not exclusive composition.
- evidence_id: ecoli-q8
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15459799%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:36:06.352989Z'
  snapshot_sha256: efd4116a8335e8c7fe5b55f13330ce103fff66ee1592b96ca3270ae59bba7bec
  support: supports
  locator: Title, PMID/DOI and complete indexed primary abstract; full paper not inspected
  summary: PMID:15459799 explicitly contrasts endogenous E. coli Q8 with engineered
    production of Q10; the recombinant Q10 result is not mistaken for the unmodified
    baseline.
- evidence_id: gluconobacter-q10
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A2547757%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:36:06.361609Z'
  snapshot_sha256: 69fab44397d8a4e50ec1580f2e3ce0bba3f780c309630b00d6412e9255175dfd
  support: supports
  locator: Title, PMID/DOI and complete indexed primary abstract; full paper not inspected
  summary: PMID:2547757 identifies Q10 as native Gluconobacter suboxydans ubiquinone
    while testing respiratory electron transfer.
- evidence_id: pombe-q10
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A24911838%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:36:06.344863Z'
  snapshot_sha256: f67bd6fd3341f54c6262d07263309eaad9aaba038295c89692b587aa1641381c
  support: supports
  locator: Title, PMID/DOI and complete indexed primary abstract; full paper not inspected
  summary: PMID:24911838 describes Q10-deficient Schizosaccharomyces pombe deletion
    strains and restoration of Q10 production.
- evidence_id: mammal-homologues
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A1586151%20AND%20SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T08:36:06.348043Z'
  snapshot_sha256: 8e708dc1b39de0bdbc455927633944aa932890e5649c6defa52f9da3578a3a78
  support: supports
  locator: Title, PMID/DOI and complete indexed primary abstract; full paper not inspected
  summary: PMID:1586151 measures Q9 in rat and Q10 in human tissues, with additional
    Q10 in rat and Q9 in humans. This supports the stated occurrence examples without
    exclusivity.
- evidence_id: capsulatus-homologues
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10626278/fullTextXML
  accessed_at: '2026-10-21T08:35:54.117261Z'
  snapshot_sha256: ed6e0888123cf603a9cca2d9440a84ecae1461495ea66db0a24b33132000079b
  support: supports
  locator: Full-text Figure 4 caption and associated LC–MS methods/results
  summary: PMID:37716914; DOI:10.1002/2211-5463.13707. Figure 4 explicitly reports
    major UQ10 and trace UQ9 in Rhodobacter capsulatus MT1131. Thus the target literal
    occurrence of Q9 is not disproven; the result is strain/context-specific.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  locator: Executed 2026-10-21T08:30:27Z through 2026-10-21T08:30:30Z; exit 0
  accessed_at: '2026-10-21T08:30:30Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/ubiquinone-kw-0830.yaml
  locator: Executed 2026-10-21T08:30:30Z through 2026-10-21T08:30:30Z; exit 0
  accessed_at: '2026-10-21T08:30:30Z'
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
  - UniProtKB-KW:KW-0830
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
  - UniProtKB-KW:KW-0830
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
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: KW-0830 denotes ubiquinone-interacting proteins, not a single chemical
    species or protein instance. The core source identity remains supported.
  evidence_ids:
  - record
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0830
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
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: supported
  summary: A defined protein interaction with the ubiquinone ligand class supports
    FUNCTION/binding-capacity placement without asserting site coordinates.
  evidence_ids:
  - record
  - keyword
  - chemical
  - schema
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-8
  topic: Representation
- area: nomenclature
  outcome: supported
  summary: Coenzyme Q and CoQ identify the source ligand class; they do not specify
    a single side-chain homologue.
  evidence_ids:
  - record
  - keyword
  - chemical
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-9
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: The mobile-pool and universal absence-of-tight-binding background needs
    qualification. The direct Gluconobacter experiment reports tightly bound Q under
    stated preparation conditions, and the QA study distinguishes retained one-electron
    cycling from exchangeable QB quinol. The opening interaction class remains valid.
  evidence_ids:
  - record
  - keyword
  - qa-primary
  - tight-binding-primary
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-10
  topic: Evidence
- area: evidence
  outcome: supported
  summary: All seven organism/homologue examples have bounded occurrence support.
    Rat/human tissue mixtures and R. capsulatus trace Q9 prevent interpreting the
    list as exclusive or universally predominant species composition.
  evidence_ids:
  - record
  - keyword
  - yeast-q6
  - ecoli-q8
  - gluconobacter-q10
  - pombe-q10
  - mammal-homologues
  - capsulatus-homologues
  target_ids:
  - UniProtKB-KW:KW-0830
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0830.mobile-pool-generalization
  category: scope
  severity: minor
  title: Qualify mobile-pool and redox-cycle generalizations
  description: The copied background states ubiquinone is not tightly bound and is
    mobile, alongside an unqualified full-reduction narrative. A primary Gluconobacter
    alcohol-dehydrogenase study reports tightly bound ubiquinone in dodecyl-maltoside
    preparation but not Triton X-100 preparation. The separate QA study describes
    retained neutral/semiquinone cycling versus exchangeable reduced QB quinol. These
    observations support qualifying the background by protein/site and preparation;
    they do not challenge the core interaction class, prove a covalent linkage, or
    establish a universal affinity threshold.
  evidence_ids:
  - record
  - keyword
  - qa-primary
  - owner
  - tight-binding-primary
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0830
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
  description: Qualify the maintained background to distinguish mobile membrane-pool/exchangeable
    QB contexts from retained QA roles and experimentally observed tight-binding contexts.
    Preserve the source attribution and core interaction-class definition.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0830
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - State that mobility and redox fate depend on the protein/site context.
  - Do not equate kinetic residence with measured thermodynamic tightness or simulated
    energies with new experimental affinity measurements.
  - Regenerate through the maintained source transform and validate.
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
- The QA primary paper is computational with cited experimental context; its kinetic
  residence description is not a new universal affinity measurement. The tight-binding
  result is preparation-specific and was inspected through a complete indexed abstract.
- Five complete indexed primary abstracts support the remaining organism/homologue
  examples; the R. capsulatus full-text figure supports trace Q9 in strain MT1131.
  These are occurrence checks, not exclusive or universal species compositions. No
  proteins, coordinates or mechanisms are qualified.
tags:
- unreviewed-path-order
- batch-008
- uniprot-keywords
```
