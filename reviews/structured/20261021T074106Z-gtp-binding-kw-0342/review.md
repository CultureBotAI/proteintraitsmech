# Review of GTP-binding

- Review: 20261021T074106Z-gtp-binding-kw-0342
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:28:43Z
- Finished UTC: 2026-10-21T07:41:06Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

GTP-binding identity, aliases, direct GO association and Nucleotide-binding hierarchy are supported. One minor finding clarifies nucleoside terminology and phosphate connectivity.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 7 in batch 004. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a covers 30 record paths, leaving 429329 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0342 | data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml | generated | GTP-binding |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0342 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0342 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0342 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0342 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0342 | UniProt resolves KW-0342 and parent KW-0547; QuickGO resolves nonobsolete GO:0005525 and parent GO:0000166. ChEBI:16750 and ChEBI:15996 resolve the supporting ligand chemistry. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0342.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0342.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0342.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0342.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0342.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0342.

The record unambiguously denotes a protein GTP-binding class. The ligand name, two expanded aliases and GO mapping support that identity.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0342.

The source-direct GO:0005525 association resolves and matches binding, not GTP hydrolysis or a particular G-protein family.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0342.

The Nucleotide-binding parent exists locally and upstream; both its source identifier and GO xref resolve. The intended broader relation is chemically supported.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0342.

FUNCTION/binding capacity follows the explicit binding property without requiring catalytic activity, a localized motif or an individual protein example.

### Nomenclature

nomenclature: concern. Targets: UniProtKB-KW:KW-0342.

The background calls guanosine a ribonucleotide and describes the three phosphates as esterified to sugar without distinguishing the chain linkage. A concise corrected sentence should separate nucleoside identity from triphosphate connectivity.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-0342.

The core class and hierarchy are supported; the chemistry sources support a bounded wording correction, not a wrong-ligand identity or an inferred three-site detector.

## Findings

### F1: Clarify guanosine identity and triphosphate connectivity

minor / open / confirmed; issue key: uniprot-keyword.KW-0342.nucleoside-triphosphate-wording.

The source-inherited background calls guanosine a ribonucleotide although guanosine itself is a nucleoside. The phrase about three phosphates esterified to the sugar also leaves the chain connectivity unclear. GTP identity remains clear from its full name, aliases and GO mapping; no three-independent-ester structure is encoded.

## Recommended Actions And Acceptance Checks

### A1

Use a maintained definition correction consumed by scripts/seed_uniprot_keywords.py to describe GTP as guanosine 5-prime-triphosphate, with guanosine a nucleoside and a phosphate chain attached at the 5-prime hydroxyl. Preserve source provenance.

- The prose distinguishes the nucleoside guanosine from nucleotide GTP.
- The phosphate wording is compatible with one sugar ester followed by phosphoanhydride-linked phosphates.
- Preserve GTP-binding identity, aliases, GO mapping and Nucleotide-binding parent; regenerate and run strict validation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| local-parent-1 | data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml; Entire local parent YAML | supports | Complete local parent record inspected for identifier, class, definition and broader-parent chain. |
| keyword | https://rest.uniprot.org/keywords/KW-0342.json; Inspected source response captured at the recorded UTC time | supports | UniProt 2026_03 resolves GTP-binding KW-0342, reproducing the local definition and two aliases, mapping GO:0005525 and asserting Nucleotide-binding as parent. |
| parent | https://rest.uniprot.org/keywords/KW-0547.json; Inspected source response captured at the recorded UTC time | supports | Nucleotide-binding KW-0547 resolves and explicitly lists GTP-binding as child; it maps to GO:0000166. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0005525; Inspected source response captured at the recorded UTC time | supports | Nonobsolete GO:0005525 is GTP binding, matching the intended protein-binding function. |
| parent-go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0000166; Inspected source response captured at the recorded UTC time | supports | Nonobsolete GO:0000166 defines nucleotide binding and includes nucleoside esterification by phosphate or oligophosphate; it resolves the local parent xref. |
| guanosine | https://www.ebi.ac.uk/chebi/CHEBI:16750; Entity definition and chemical structure | supports | ChEBI:16750 defines guanosine as a purine nucleoside with guanine joined to ribofuranose. Its structure has no phosphate. |
| gtp | https://www.ebi.ac.uk/chebi/CHEBI:15996; Entity identity, formula, SMILES and InChI | supports | ChEBI:15996 identifies GTP with an explicit structure showing a 5-prime sugar-O-P bond followed by the P-O-P-O-P chain. This distinguishes the nucleotide from guanosine and clarifies phosphate connectivity. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml; Executed 2026-10-21T07:39:22Z through 2026-10-21T07:39:24Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/cobalt-kw-0170.yaml data/traits/function/binding_capacity/uniprot_keywords/copper-kw-0186.yaml data/traits/function/binding_capacity/uniprot_keywords/fad-kw-0274.yaml data/traits/function/binding_capacity/uniprot_keywords/flavoprotein-kw-0285.yaml data/traits/function/binding_capacity/uniprot_keywords/fmn-kw-0288.yaml data/traits/function/binding_capacity/uniprot_keywords/folate-binding-kw-0290.yaml data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml data/traits/function/binding_capacity/uniprot_keywords/heme-kw-0349.yaml data/traits/function/binding_capacity/uniprot_keywords/hemoglobin-binding-kw-0351.yaml data/traits/function/binding_capacity/uniprot_keywords/hyaluronic-acid-kw-0373.yaml; Executed 2026-10-21T07:29:12Z through 2026-10-21T07:32:00Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml; Executed 2026-10-21T07:39:24Z through 2026-10-21T07:39:24Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:32:00Z through 2026-10-21T07:32:01Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No nucleotide affinity, hydrolysis activity, guanine-nucleotide selectivity, residue-level binding geometry or protein instance is qualified. Chemical entity identifiers are contextual evidence, not new protein-trait xrefs.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T074106Z-gtp-binding-kw-0342
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of GTP-binding
started_at: '2026-10-21T07:28:43Z'
finished_at: '2026-10-21T07:41:06Z'
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
summary: GTP-binding identity, aliases, direct GO association and Nucleotide-binding
  hierarchy are supported. One minor finding clarifies nucleoside terminology and
  phosphate connectivity.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
    sha256: 81c6dbe62428e3b1976e2d3c33173d5c2b0155265c84fec7ecb8bb4634e96242
    role: target
  - path: data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml
    sha256: c724c9d8fe816fe98a1d25386813bf1b5c96077e619793dc51d1efabe34f7a60
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
  selection: Path-order position 7 in batch 004. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 and batch-003 at cc32a8c59ea04af980930b521773705380a9d85a
    covers 30 record paths, leaving 429329 before this batch. Published branch coverage
    is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0342
targets:
- kind: generated
  label: GTP-binding
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0342
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0342
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
  - UniProtKB-KW:KW-0342
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0342
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
  - UniProtKB-KW:KW-0342
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: UniProt resolves KW-0342 and parent KW-0547; QuickGO resolves nonobsolete
    GO:0005525 and parent GO:0000166. ChEBI:16750 and ChEBI:15996 resolve the supporting
    ligand chemistry.
  target_ids:
  - UniProtKB-KW:KW-0342
  evidence_ids:
  - keyword
  - parent
  - go
  - parent-go
  - guanosine
  - gtp
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:28:43Z'
  snapshot_sha256: 81c6dbe62428e3b1976e2d3c33173d5c2b0155265c84fec7ecb8bb4634e96242
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:28:43Z'
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
  accessed_at: '2026-10-21T07:28:43Z'
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
  reference: data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T07:28:43Z'
  snapshot_sha256: c724c9d8fe816fe98a1d25386813bf1b5c96077e619793dc51d1efabe34f7a60
  support: supports
  summary: Complete local parent record inspected for identifier, class, definition
    and broader-parent chain.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0342.json
  accessed_at: '2026-10-21T07:29:17.045259Z'
  snapshot_sha256: 185709a06741b597408c7d3aaab776b1003567d4bfe9f2e0ab827e8f6ed019f1
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: UniProt 2026_03 resolves GTP-binding KW-0342, reproducing the local definition
    and two aliases, mapping GO:0005525 and asserting Nucleotide-binding as parent.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0547.json
  accessed_at: '2026-10-21T07:29:52.146734Z'
  snapshot_sha256: f74bb937d36c85aa47ae337c42027958e3fb9ff27285c3d592d1a7519c41d0a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nucleotide-binding KW-0547 resolves and explicitly lists GTP-binding as
    child; it maps to GO:0000166.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0005525
  accessed_at: '2026-10-21T07:29:52.174963Z'
  snapshot_sha256: e5a5dad601c6cdb7f3dd0f2194d4fd5e286fbb09083e24384246eef810044792
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0005525 is GTP binding, matching the intended protein-binding
    function.
- evidence_id: parent-go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0000166
  accessed_at: '2026-10-21T07:30:26.956264Z'
  snapshot_sha256: aeab67c05b0b1d212b5dd6548a40be40bc5a28f21c5818818c3e0d6b510ac7b3
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete GO:0000166 defines nucleotide binding and includes nucleoside
    esterification by phosphate or oligophosphate; it resolves the local parent xref.
- evidence_id: guanosine
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/CHEBI:16750
  accessed_at: '2026-10-21T07:30:26.958311Z'
  snapshot_sha256: b9c5e98c7d807332c64ac52b36e897dae4d83af0b5b9d034aafd3a5fa966263e
  support: supports
  locator: Entity definition and chemical structure
  summary: ChEBI:16750 defines guanosine as a purine nucleoside with guanine joined
    to ribofuranose. Its structure has no phosphate.
- evidence_id: gtp
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/CHEBI:15996
  accessed_at: '2026-10-21T07:29:52.775439Z'
  snapshot_sha256: 74b9a6a41afb0c11a62e955b5d5e377071a3432655bc67587c0edd85b331a0aa
  support: supports
  locator: Entity identity, formula, SMILES and InChI
  summary: ChEBI:15996 identifies GTP with an explicit structure showing a 5-prime
    sugar-O-P bond followed by the P-O-P-O-P chain. This distinguishes the nucleotide
    from guanosine and clarifies phosphate connectivity.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  locator: Executed 2026-10-21T07:39:22Z through 2026-10-21T07:39:24Z; exit 0
  accessed_at: '2026-10-21T07:39:24Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/gtp-binding-kw-0342.yaml
  locator: Executed 2026-10-21T07:39:24Z through 2026-10-21T07:39:24Z; exit 0
  accessed_at: '2026-10-21T07:39:24Z'
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
assessments:
- area: ownership
  outcome: supported
  summary: The maintained UniProt keyword seeder owns future changes; this review
    does not modify emitted records.
  evidence_ids:
  - owner
  target_ids:
  - UniProtKB-KW:KW-0342
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
  - UniProtKB-KW:KW-0342
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
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: The record unambiguously denotes a protein GTP-binding class. The ligand
    name, two expanded aliases and GO mapping support that identity.
  evidence_ids:
  - record
  - keyword
  - go
  - gtp
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-6
  topic: Identity
- area: grounding
  outcome: supported
  summary: The source-direct GO:0005525 association resolves and matches binding,
    not GTP hydrolysis or a particular G-protein family.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-7
  topic: Grounding
- area: consistency
  outcome: supported
  summary: The Nucleotide-binding parent exists locally and upstream; both its source
    identifier and GO xref resolve. The intended broader relation is chemically supported.
  evidence_ids:
  - record
  - keyword
  - parent
  - local-parent-1
  - parent-go
  - gtp
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-8
  topic: Consistency
- area: representation
  outcome: supported
  summary: FUNCTION/binding capacity follows the explicit binding property without
    requiring catalytic activity, a localized motif or an individual protein example.
  evidence_ids:
  - record
  - schema
  - go
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-9
  topic: Representation
- area: nomenclature
  outcome: concern
  summary: The background calls guanosine a ribonucleotide and describes the three
    phosphates as esterified to sugar without distinguishing the chain linkage. A
    concise corrected sentence should separate nucleoside identity from triphosphate
    connectivity.
  evidence_ids:
  - record
  - keyword
  - guanosine
  - gtp
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-10
  topic: Nomenclature
- area: evidence
  outcome: supported
  summary: The core class and hierarchy are supported; the chemistry sources support
    a bounded wording correction, not a wrong-ligand identity or an inferred three-site
    detector.
  evidence_ids:
  - record
  - keyword
  - parent
  - go
  - guanosine
  - gtp
  target_ids:
  - UniProtKB-KW:KW-0342
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0342.nucleoside-triphosphate-wording
  category: nomenclature
  severity: minor
  title: Clarify guanosine identity and triphosphate connectivity
  description: The source-inherited background calls guanosine a ribonucleotide although
    guanosine itself is a nucleoside. The phrase about three phosphates esterified
    to the sugar also leaves the chain connectivity unclear. GTP identity remains
    clear from its full name, aliases and GO mapping; no three-independent-ester structure
    is encoded.
  evidence_ids:
  - record
  - keyword
  - guanosine
  - gtp
  - go
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0342
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
  description: Use a maintained definition correction consumed by scripts/seed_uniprot_keywords.py
    to describe GTP as guanosine 5-prime-triphosphate, with guanosine a nucleoside
    and a phosphate chain attached at the 5-prime hydroxyl. Preserve source provenance.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0342
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - The prose distinguishes the nucleoside guanosine from nucleotide GTP.
  - The phosphate wording is compatible with one sugar ester followed by phosphoanhydride-linked
    phosphates.
  - Preserve GTP-binding identity, aliases, GO mapping and Nucleotide-binding parent;
    regenerate and run strict validation.
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
- No nucleotide affinity, hydrolysis activity, guanine-nucleotide selectivity, residue-level
  binding geometry or protein instance is qualified. Chemical entity identifiers are
  contextual evidence, not new protein-trait xrefs.
tags:
- unreviewed-path-order
- batch-004
- uniprot-keywords
```
