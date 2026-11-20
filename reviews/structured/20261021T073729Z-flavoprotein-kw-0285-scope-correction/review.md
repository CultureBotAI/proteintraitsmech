# Corrected scope assessment of Flavoprotein

- Review: 20261021T073729Z-flavoprotein-kw-0285-scope-correction
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:36:40Z
- Finished UTC: 2026-10-21T07:37:29Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

Flavoprotein identity and demonstrated flavin roles are supported. This successor corrects the earlier confirmed-major exclusion claim to one minor provisional definition-scope question; the evidence does not establish that the inspected proteins fail class membership.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 004. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a covers 30 record paths, leaving 429329 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded. This is an additive correction counted within the same ten-bundle batch.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0285 | data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml | generated | Flavoprotein |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0285 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0285 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0285 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0285 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0285 | UniProt resolves KW-0285 and root KW-9993, reviewed RibL Q58579 and unreviewed AppA Q53119. Primary abstracts resolve PMID:20822113/12779327/15667215 with their stated DOIs. No GO equivalence is asserted. Additional correction evidence resolves PMCID:PMC3760249 to PMID:23982072 and DOI:10.1128/mBio.00563-13. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0285.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0285.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0285.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0285.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0285.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0285.

The stable source keyword identifies the intended protein class. Its interpretation should preserve supported flavin-associated functions; no wrong class membership has been established.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0285.

The keyword resolves and no GO xref is asserted, consistent with the complete official mapping snapshots.

### Consistency

consistency: concern. Targets: UniProtKB-KW:KW-0285.

RibL shows a nonredox FMN-substrate/FAD-product role in an explicitly source-assigned member. That raises a wording question but does not prove an invalid hierarchy: a parent need not describe every role, and cosubstrate may be read more broadly than redox cofactor.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0285.

The protein-level ligand-association representation remains defensible. The inspected roles do not establish a nonbinding member or justify an unsupported replacement category.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0285.

The stable Flavoprotein name is used explicitly by the primary AppA study. No unsupported exact aliases are asserted in the local record.

### Evidence

evidence: concern. Targets: UniProtKB-KW:KW-0285.

The experiments establish specific flavin roles. They do not establish absence of every other qualifying activity, so the predecessor exclusion inference is withdrawn and a bounded interpretation question remains. Full-text AppA evidence explicitly documents a separate cysteine redox role, further limiting a whole-protein nonredox inference.

## Findings

### F1: Clarify how biosynthetic and signaling roles fit the definition

minor / open / provisional; issue key: uniprot-keyword.KW-0285.redox-enzyme-only-definition.

RibL has a demonstrated nonredox flavin substrate/product role; AppA has a flavin light-sensing role and a separate cysteine redox function. These observations motivate clarification of the enzyme/cofactor/cosubstrate wording but do not establish exclusion from the class. A parent need not describe every role, and the redox modifier scope is ambiguous. The predecessor confirmed-major inference is superseded.

Disposition: Reassesses the predecessor as minor/provisional: a demonstrated role does not rule out additional qualifying roles, and the modifier scope in redox cofactors or cosubstrates is ambiguous.

## Recommended Actions And Acceptance Checks

### A1

Clarify the intended enzyme/cofactor/cosubstrate scope in source annotation guidance or bounded member evidence before changing scripts/seed_uniprot_keywords.py or its maintained corrections. If wording is misleading, qualify it while preserving supported members and source identity; otherwise document evidence resolving this provisional question.

- State whether cosubstrate is restricted to redox chemistry and how the demonstrated RibL substrate/product role fits.
- Account for both AppA flavin light sensing and its documented cysteine redox function without labeling the entire protein universally nonredox or nonenzymatic.
- Do not infer nonmembership or absence of other activities solely from a demonstrated different role.
- If evidence justifies a definition or hierarchy change, regenerate through the maintained input, validate and save a new scoped review; otherwise record the evidence resolving the concern.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file, version 2026/07/06 14:08:43, was searched for KW-0285; no entry occurs. The current keyword response also has no geneOntologies field. This bounds the absence claim to those two inspected snapshots. |
| keyword | https://rest.uniprot.org/keywords/KW-0285.json; Inspected source response captured at the recorded UTC time | supports | UniProt 2026_03 resolves Flavoprotein KW-0285 and reproduces the local definition: enzymes containing flavin nucleotides as redox cofactors or cosubstrates. The modifier scope is ambiguous. It has only Ligand as parent and FAD/FMN children. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | The omitted Ligand category includes binding, association and dependence; it does not impose an enzyme-only boundary. |
| ribl-member | https://rest.uniprot.org/uniprotkb/Q58579.json; Inspected source response captured at the recorded UTC time | supports | Reviewed Q58579 entry114 is experimentally characterized archaeal RibL, explicitly annotated with Flavoprotein, FAD and FMN keywords. Its function and catalytic-activity comments describe FMN adenylylation producing FAD. |
| ribl-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20822113+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Complete indexed primary abstract | supports | PMID:20822113 / DOI:10.1021/bi100817q reports experimentally expressed MJ1179/RibL transferring AMP from ATP to FMN to produce FAD. These are nonredox substrate/product roles in the demonstrated reaction. |
| appa-member | https://rest.uniprot.org/uniprotkb/Q53119.json; Entry type, accession, gene, organism, keywords and entryAudit | context_only | UniProt Q53119 entry98 resolves to AppA in Cereibacter/Rhodobacter sphaeroides. It is unreviewed and carries a PDB-derived Flavoprotein keyword assignment; this is explicit source membership, not independent experimental confirmation of every annotation. |
| appa-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A12779327+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Complete indexed abstract | supports | PMID:12779327 / DOI:10.1021/bi030055o explicitly calls AppA a flavoprotein blue-light photoreceptor and antirepressor; its experiments show an FAD-binding photoactive N-terminal domain and a reversible light-induced spectral change. |
| appa-signaling | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15667215+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; Complete indexed abstract | supports | PMID:15667215 / DOI:10.1021/bi047876t describes AppA antirepression through direct PpsR association and reconstitutes a functional FAD-binding BLUF signaling domain. This supports a signaling role without proving absence of every possible enzyme activity. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml; Executed 2026-10-21T07:31:50Z through 2026-10-21T07:31:52Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/cobalt-kw-0170.yaml data/traits/function/binding_capacity/uniprot_keywords/copper-kw-0186.yaml data/traits/function/binding_capacity/uniprot_keywords/fad-kw-0274.yaml data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml data/traits/function/binding_capacity/uniprot_keywords/fmn-kw-0288.yaml data/traits/function/binding_capacity/uniprot_keywords/folate-binding-kw-0290.yaml data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml data/traits/function/binding_capacity/uniprot_keywords/heme-kw-0349.yaml data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml; Executed 2026-10-21T07:29:12Z through 2026-10-21T07:32:00Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml; Executed 2026-10-21T07:31:52Z through 2026-10-21T07:31:53Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:32:00Z through 2026-10-21T07:32:01Z; exit 0 | supports | No issues found |
| prior-review | reviews/structured/20261021T073502Z-flavoprotein-kw-0285/review.yaml | context_only | The predecessor overstated the certainty and severity of a role-versus-membership inference. Its empirical observations remain usable, but it did not prove exclusion of a source-assigned member. |
| appa-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3760249/fullTextXML; Body paragraphs 3, 17 and 30, read in full; article identifiers | supports | PMCID:PMC3760249, PMID:23982072, DOI:10.1128/mBio.00563-13 describes an N-terminal flavin light sensor and a separate C-terminal cysteine redox function in AppA. The paper identifies a redox-active cysteine pair; it does not establish absence of every possible qualifying flavin role. |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted in the record. Compared GO terms are external scope checks only and must not be added as direct equivalents without new source support.
- The original RibL and AppA abstracts were inspected in full; this successor additionally inspected the cited sections of the AppA PMC full text. AppA source membership is unreviewed/PDB-derived; the primary AppA evidence specifically concerns FAD and is not used to qualify every cofactor annotation in that entry.
- These proteins are scoped research evidence, not qualified examples. Demonstrated nonredox/signaling roles do not prove absence of all other activities or define the complete diversity of flavoproteins.
- The concern remains open and provisional; no negative experiment excluding all qualifying functions or curator definition of cosubstrate scope was established.
- This immutable successor preserves the earlier bundle and explicitly replaces its confirmed-major interpretation with a minor provisional scope question. No trait bytes changed and no scientific status was promoted.
- All target and original validation inputs were SHA256-checked unchanged before this reassessment. The recorded required gates are reused for those same bytes; this bundle receives its own validate/save/check.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T073729Z-flavoprotein-kw-0285-scope-correction
kind: record
repository: CultureBotAI/proteintraitsmech
title: Corrected scope assessment of Flavoprotein
started_at: '2026-10-21T07:36:40Z'
finished_at: '2026-10-21T07:37:29Z'
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
summary: Flavoprotein identity and demonstrated flavin roles are supported. This successor
  corrects the earlier confirmed-major exclusion claim to one minor provisional definition-scope
  question; the evidence does not establish that the inspected proteins fail class
  membership.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
    sha256: 327d390ee1692e0bab38c3820cb154699f65d0dd3ef095284d0d97f3c324c746
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
  - path: reviews/structured/20261021T073502Z-flavoprotein-kw-0285/review.yaml
    sha256: 7689246657bccd1c07c347e06e85becaadc6d8fb8415c5c2352bcdf8025b5e2a
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
  selection: Path-order position 4 in batch 004. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    covers 30 record paths, leaving 429329 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded. This
    is an additive correction counted within the same ten-bundle batch.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0285
targets:
- kind: generated
  label: Flavoprotein
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0285
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0285
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/cobalt-kw-0170.yaml
    data/traits/function/binding_capacity/uniprot_keywords/copper-kw-0186.yaml data/traits/function/binding_capacity/uniprot_keywords/fad-kw-0274.yaml
    data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
    data/traits/function/binding_capacity/uniprot_keywords/fmn-kw-0288.yaml data/traits/function/binding_capacity/uniprot_keywords/folate-binding-kw-0290.yaml
    data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
    data/traits/function/binding_capacity/uniprot_keywords/heme-kw-0349.yaml data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml
    data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Registry consistency is not protein qualification
    for this target.
  target_ids:
  - UniProtKB-KW:KW-0285
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0285
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
  - UniProtKB-KW:KW-0285
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: UniProt resolves KW-0285 and root KW-9993, reviewed RibL Q58579 and unreviewed
    AppA Q53119. Primary abstracts resolve PMID:20822113/12779327/15667215 with their
    stated DOIs. No GO equivalence is asserted. Additional correction evidence resolves
    PMCID:PMC3760249 to PMID:23982072 and DOI:10.1128/mBio.00563-13.
  target_ids:
  - UniProtKB-KW:KW-0285
  evidence_ids:
  - keyword
  - parent
  - mapping-file
  - ribl-member
  - ribl-primary
  - appa-member
  - appa-primary
  - appa-signaling
  - appa-fulltext
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:28:37Z'
  snapshot_sha256: 327d390ee1692e0bab38c3820cb154699f65d0dd3ef095284d0d97f3c324c746
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:28:37Z'
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
  accessed_at: '2026-10-21T07:28:37Z'
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
    for KW-0285; no entry occurs. The current keyword response also has no geneOntologies
    field. This bounds the absence claim to those two inspected snapshots.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0285.json
  accessed_at: '2026-10-21T07:29:36.990770Z'
  snapshot_sha256: 19fd294afc608a7c5bc5efbceb70d945bb3adc56de84e9ab25c97c8c56003794
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: 'UniProt 2026_03 resolves Flavoprotein KW-0285 and reproduces the local
    definition: enzymes containing flavin nucleotides as redox cofactors or cosubstrates.
    The modifier scope is ambiguous. It has only Ligand as parent and FAD/FMN children.'
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The omitted Ligand category includes binding, association and dependence;
    it does not impose an enzyme-only boundary.
- evidence_id: ribl-member
  kind: database
  reference: https://rest.uniprot.org/uniprotkb/Q58579.json
  accessed_at: '2026-10-21T07:32:12.450167Z'
  snapshot_sha256: da39a0d550173d88ce2931842e09c2e5ea0935312d8854d8c31cc2d26660f572
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Reviewed Q58579 entry114 is experimentally characterized archaeal RibL,
    explicitly annotated with Flavoprotein, FAD and FMN keywords. Its function and
    catalytic-activity comments describe FMN adenylylation producing FAD.
- evidence_id: ribl-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20822113+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T07:32:12.429876Z'
  snapshot_sha256: 4e242d72169380d4f625c87239a93145b9ce8e3a98df8995304d60e45d41c120
  support: supports
  locator: Complete indexed primary abstract
  summary: PMID:20822113 / DOI:10.1021/bi100817q reports experimentally expressed
    MJ1179/RibL transferring AMP from ATP to FMN to produce FAD. These are nonredox
    substrate/product roles in the demonstrated reaction.
- evidence_id: appa-member
  kind: database
  reference: https://rest.uniprot.org/uniprotkb/Q53119.json
  accessed_at: '2026-10-21T07:30:35.741139Z'
  snapshot_sha256: 47f56e2296effa91bdf93420fd25a513423e418aa0d23708f6f46c3d073693c4
  support: context_only
  locator: Entry type, accession, gene, organism, keywords and entryAudit
  summary: UniProt Q53119 entry98 resolves to AppA in Cereibacter/Rhodobacter sphaeroides.
    It is unreviewed and carries a PDB-derived Flavoprotein keyword assignment; this
    is explicit source membership, not independent experimental confirmation of every
    annotation.
- evidence_id: appa-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A12779327+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T07:30:36.046400Z'
  snapshot_sha256: 84e624ad4946bc8680a81fdf4288faf0f33fa8df03a07e9230bd1d9b2e2c8fa4
  support: supports
  locator: Complete indexed abstract
  summary: PMID:12779327 / DOI:10.1021/bi030055o explicitly calls AppA a flavoprotein
    blue-light photoreceptor and antirepressor; its experiments show an FAD-binding
    photoactive N-terminal domain and a reversible light-induced spectral change.
- evidence_id: appa-signaling
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15667215+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T07:30:36.337856Z'
  snapshot_sha256: 1fc6796d4b2fcee488bbe1de25c38f1f08c09a6d7890fdb96a755782e02087a9
  support: supports
  locator: Complete indexed abstract
  summary: PMID:15667215 / DOI:10.1021/bi047876t describes AppA antirepression through
    direct PpsR association and reconstitutes a functional FAD-binding BLUF signaling
    domain. This supports a signaling role without proving absence of every possible
    enzyme activity.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  locator: Executed 2026-10-21T07:31:50Z through 2026-10-21T07:31:52Z; exit 0
  accessed_at: '2026-10-21T07:31:52Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/cobalt-kw-0170.yaml
    data/traits/function/binding_capacity/uniprot_keywords/copper-kw-0186.yaml data/traits/function/binding_capacity/uniprot_keywords/fad-kw-0274.yaml
    data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
    data/traits/function/binding_capacity/uniprot_keywords/fmn-kw-0288.yaml data/traits/function/binding_capacity/uniprot_keywords/folate-binding-kw-0290.yaml
    data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
    data/traits/function/binding_capacity/uniprot_keywords/heme-kw-0349.yaml data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml
    data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml
  locator: Executed 2026-10-21T07:29:12Z through 2026-10-21T07:32:00Z; exit 0
  accessed_at: '2026-10-21T07:32:00Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml
  locator: Executed 2026-10-21T07:31:52Z through 2026-10-21T07:31:53Z; exit 0
  accessed_at: '2026-10-21T07:31:53Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T07:32:00Z through 2026-10-21T07:32:01Z; exit 0
  accessed_at: '2026-10-21T07:32:01Z'
  support: supports
  summary: No issues found
- evidence_id: prior-review
  kind: prior_review
  reference: reviews/structured/20261021T073502Z-flavoprotein-kw-0285/review.yaml
  snapshot_sha256: 7689246657bccd1c07c347e06e85becaadc6d8fb8415c5c2352bcdf8025b5e2a
  accessed_at: '2026-10-21T07:36:40Z'
  support: context_only
  summary: The predecessor overstated the certainty and severity of a role-versus-membership
    inference. Its empirical observations remain usable, but it did not prove exclusion
    of a source-assigned member.
- evidence_id: appa-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3760249/fullTextXML
  accessed_at: '2026-10-21T07:34:35.558090Z'
  snapshot_sha256: 16e13d9d85888236a580727871630dea0ecad5353f28c0f5ec5617b0a3950cdf
  support: supports
  locator: Body paragraphs 3, 17 and 30, read in full; article identifiers
  summary: PMCID:PMC3760249, PMID:23982072, DOI:10.1128/mBio.00563-13 describes an
    N-terminal flavin light sensor and a separate C-terminal cysteine redox function
    in AppA. The paper identifies a redox-active cysteine pair; it does not establish
    absence of every possible qualifying flavin role.
assessments:
- area: ownership
  outcome: supported
  summary: The maintained UniProt keyword seeder owns future changes; this review
    does not modify emitted records.
  evidence_ids:
  - owner
  target_ids:
  - UniProtKB-KW:KW-0285
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
  - UniProtKB-KW:KW-0285
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
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The stable source keyword identifies the intended protein class. Its interpretation
    should preserve supported flavin-associated functions; no wrong class membership
    has been established.
  evidence_ids:
  - record
  - keyword
  - ribl-member
  - ribl-primary
  - appa-primary
  - appa-signaling
  - prior-review
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: The keyword resolves and no GO xref is asserted, consistent with the complete
    official mapping snapshots.
  evidence_ids:
  - record
  - keyword
  - mapping-file
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-7
  topic: Grounding
- area: consistency
  outcome: concern
  summary: 'RibL shows a nonredox FMN-substrate/FAD-product role in an explicitly
    source-assigned member. That raises a wording question but does not prove an invalid
    hierarchy: a parent need not describe every role, and cosubstrate may be read
    more broadly than redox cofactor.'
  evidence_ids:
  - record
  - keyword
  - parent
  - ribl-member
  - ribl-primary
  - prior-review
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-8
  topic: Consistency
- area: representation
  outcome: supported
  summary: The protein-level ligand-association representation remains defensible.
    The inspected roles do not establish a nonbinding member or justify an unsupported
    replacement category.
  evidence_ids:
  - record
  - schema
  - ribl-primary
  - appa-primary
  - prior-review
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-9
  topic: Representation
- area: nomenclature
  outcome: supported
  summary: The stable Flavoprotein name is used explicitly by the primary AppA study.
    No unsupported exact aliases are asserted in the local record.
  evidence_ids:
  - record
  - keyword
  - appa-primary
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: concern
  summary: The experiments establish specific flavin roles. They do not establish
    absence of every other qualifying activity, so the predecessor exclusion inference
    is withdrawn and a bounded interpretation question remains. Full-text AppA evidence
    explicitly documents a separate cysteine redox role, further limiting a whole-protein
    nonredox inference.
  evidence_ids:
  - record
  - keyword
  - ribl-member
  - ribl-primary
  - appa-member
  - appa-primary
  - appa-signaling
  - prior-review
  - appa-fulltext
  target_ids:
  - UniProtKB-KW:KW-0285
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0285.redox-enzyme-only-definition
  category: scope
  severity: minor
  title: Clarify how biosynthetic and signaling roles fit the definition
  description: RibL has a demonstrated nonredox flavin substrate/product role; AppA
    has a flavin light-sensing role and a separate cysteine redox function. These
    observations motivate clarification of the enzyme/cofactor/cosubstrate wording
    but do not establish exclusion from the class. A parent need not describe every
    role, and the redox modifier scope is ambiguous. The predecessor confirmed-major
    inference is superseded.
  evidence_ids:
  - record
  - keyword
  - ribl-member
  - ribl-primary
  - appa-member
  - appa-primary
  - appa-signaling
  - appa-fulltext
  - prior-review
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0285
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  certainty: provisional
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The evidence establishes a bounded wording/interpretation
    question, not a demonstrated false class membership or subclass relation.
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261021T073502Z-flavoprotein-kw-0285
    finding_id: F1
  disposition_reason: 'Reassesses the predecessor as minor/provisional: a demonstrated
    role does not rule out additional qualifying roles, and the modifier scope in
    redox cofactors or cosubstrates is ambiguous.'
actions:
- action_id: A1
  description: Clarify the intended enzyme/cofactor/cosubstrate scope in source annotation
    guidance or bounded member evidence before changing scripts/seed_uniprot_keywords.py
    or its maintained corrections. If wording is misleading, qualify it while preserving
    supported members and source identity; otherwise document evidence resolving this
    provisional question.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0285
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - State whether cosubstrate is restricted to redox chemistry and how the demonstrated
    RibL substrate/product role fits.
  - Account for both AppA flavin light sensing and its documented cysteine redox function
    without labeling the entire protein universally nonredox or nonenzymatic.
  - Do not infer nonmembership or absence of other activities solely from a demonstrated
    different role.
  - If evidence justifies a definition or hierarchy change, regenerate through the
    maintained input, validate and save a new scoped review; otherwise record the
    evidence resolving the concern.
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
- The original RibL and AppA abstracts were inspected in full; this successor additionally
  inspected the cited sections of the AppA PMC full text. AppA source membership is
  unreviewed/PDB-derived; the primary AppA evidence specifically concerns FAD and
  is not used to qualify every cofactor annotation in that entry.
- These proteins are scoped research evidence, not qualified examples. Demonstrated
  nonredox/signaling roles do not prove absence of all other activities or define
  the complete diversity of flavoproteins.
- The concern remains open and provisional; no negative experiment excluding all qualifying
  functions or curator definition of cosubstrate scope was established.
tags:
- unreviewed-path-order
- batch-004
- uniprot-keywords
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261021T073502Z-flavoprotein-kw-0285
  relationship: Explicitly reconciles and supersedes the predecessor severity, certainty
    and exclusion inference for the same open issue; retains target and empirical
    evidence.
notes:
- This immutable successor preserves the earlier bundle and explicitly replaces its
  confirmed-major interpretation with a minor provisional scope question. No trait
  bytes changed and no scientific status was promoted.
- All target and original validation inputs were SHA256-checked unchanged before this
  reassessment. The recorded required gates are reused for those same bytes; this
  bundle receives its own validate/save/check.
```
