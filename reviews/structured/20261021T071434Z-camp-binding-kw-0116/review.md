# Review of cAMP-binding

- Review: 20261021T071434Z-camp-binding-kw-0116
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T07:11:04Z
- Finished UTC: 2026-10-21T07:14:34Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The direct cAMP-binding identity, aliases and source-directed GO equivalence are supported. One minor finding records the dropped Nucleotide-binding parent path.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 003. Fresh main inventory has 429359 records; union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths, leaving 429339 before this batch. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0116 | data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml | generated | cAMP-binding |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0116 | Single target validated in closed mode. |
| Closed schema and UniProt semantics | passed | True | UniProtKB-KW:KW-0116 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Registry consistency is not protein qualification for this target. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0116 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0116 | Full history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0116 | Official UniProt resolves KW-0116 and asserted parent KW-0114, plus omitted source parent KW-0547; QuickGO resolves nonobsolete GO:0030552. Parent resolution is distinguished from completeness of emitted links. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0116.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0116.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0116.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0116.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0116.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Consistency

consistency: concern. Targets: UniProtKB-KW:KW-0116.

The retained cAMP parent is source-asserted and broader, but the second immediate Nucleotide-binding parent is absent. The retained local parent chain terminates, so it does not recover the omitted ancestry.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0116.

The target denotes direct cAMP binding at protein-class level, distinct from the broader cAMP-dependent/hydrolytic source class.

### Grounding

grounding: supported. Targets: UniProtKB-KW:KW-0116.

The GO:0030552 association is source-direct and equivalent in intended binding-function scope.

### Nomenclature

nomenclature: supported. Targets: UniProtKB-KW:KW-0116.

All five aliases are source-attested cAMP-binding names; the cyclic nucleotide identity is explicit in the definition and GO term.

### Representation

representation: supported. Targets: UniProtKB-KW:KW-0116.

FUNCTION/binding capacity is appropriate; no localized motif, residue interval, obligatory hydrolysis or kinase activity is asserted.

### Evidence

evidence: supported. Targets: UniProtKB-KW:KW-0116.

The direct-binding claim and chemical name are supported by the inspected official keyword and GO definition; broader parent background is not silently made part of every target protein mechanism.

## Findings

### F1: Nucleotide-binding hierarchy path is omitted

minor / open / confirmed; issue key: uniprot-keyword.KW-0116.lost-nucleotide-binding-parent.

The current source asserts cAMP and Nucleotide-binding parents. The generator selects only one immediate parent and the local retained chain ends; Nucleotide-binding is therefore omitted despite an existing local class. The retained parent and target identity remain valid.

## Recommended Actions And Acceptance Checks

### A1

Update immediate_parent/build_yaml in scripts/seed_uniprot_keywords.py to preserve all valid seeded immediate parents while retaining the category-root policy; regenerate affected records through that maintained input.

- A multiple-parent source fixture deterministically preserves both seeded parents.
- Regenerated target retains its cyclic-nucleotide parent and reaches Nucleotide-binding without dangling category-root links.
- Run strict validation and save a new review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| local-parent-1 | data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml; Entire local parent YAML | supports | Complete local parent record inspected for identifier, class, definition and broader-parent chain. |
| keyword | https://rest.uniprot.org/keywords/KW-0116.json; Complete keyword JSON and X-UniProt-Release response header | supports | UniProt 2026_03 resolves cAMP-binding KW-0116. The full definition, five binding aliases and GO:0030552 association match the record. It asserts cAMP and Nucleotide-binding as immediate parents. |
| parent | https://rest.uniprot.org/keywords/KW-0114.json; Inspected source response captured at the recorded UTC time | supports | cAMP KW-0114 is a distinct broader dependence-or-hydrolysis class and explicitly lists cAMP-binding as a child; the target should not be merged with it. |
| go | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0030552; Inspected source response captured at the recorded UTC time | supports | GO:0030552 is nonobsolete cAMP binding, identifying cyclic adenosine 3-prime,5-prime monophosphate and the same direct ligand-binding capability. |
| nucleotide | https://rest.uniprot.org/keywords/KW-0547.json; Inspected source response captured at the recorded UTC time | supports | Nucleotide-binding KW-0547 resolves as a broader nucleotide-binding class and explicitly lists both cAMP-binding and cGMP-binding children. |
| local-nucleotide | data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml | supports | Complete local Nucleotide-binding record inspected; it exists as a separate class. The target retained cyclic-nucleotide parent has no parent_traits, so its local chain does not recover this source route. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml; Executed 2026-10-21T07:13:57Z through 2026-10-21T07:13:58Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/calcium-phospholipid-binding-kw-0111.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-binding-kw-0142.yaml data/traits/function/binding_capacity/uniprot_keywords/cgmp-kw-0140.yaml data/traits/function/binding_capacity/uniprot_keywords/chitin-binding-kw-0147.yaml data/traits/function/binding_capacity/uniprot_keywords/chloride-kw-0868.yaml data/traits/function/binding_capacity/uniprot_keywords/chlorophyll-kw-0148.yaml data/traits/function/binding_capacity/uniprot_keywords/chromophore-kw-0157.yaml data/traits/function/binding_capacity/uniprot_keywords/cobalamin-kw-0846.yaml; Executed 2026-10-21T07:11:35Z through 2026-10-21T07:13:12Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml; Executed 2026-10-21T07:13:58Z through 2026-10-21T07:13:58Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T07:13:12Z through 2026-10-21T07:13:13Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used in the July seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No family-specific ligand-affinity assay, universal binding motif or catalytic consequence is established. The broader cAMP record is used only as parent context and is reviewed separately in path order.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T071434Z-camp-binding-kw-0116
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of cAMP-binding
started_at: '2026-10-21T07:11:04Z'
finished_at: '2026-10-21T07:14:34Z'
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
summary: The direct cAMP-binding identity, aliases and source-directed GO equivalence
  are supported. One minor finding records the dropped Nucleotide-binding parent path.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
    sha256: 5b1b727d6335d51922c4fbd046a9f28023fe6ae13413f25458bd889072877588
    role: target
  - path: data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
    sha256: 1a1cc1c859426dbf684718adc1fbcf0d34d9d3aabcef777c4b33d70ed8619eed
    role: context
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
  selection: Path-order position 2 in batch 003. Fresh main inventory has 429359 records;
    union with validated published batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d
    and batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21 covers 20 record paths,
    leaving 429339 before this batch. Published branch coverage is not described as
    merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0116
targets:
- kind: generated
  label: cAMP-binding
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0116
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0116
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
  - UniProtKB-KW:KW-0116
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0116
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
  - UniProtKB-KW:KW-0116
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: Official UniProt resolves KW-0116 and asserted parent KW-0114, plus omitted
    source parent KW-0547; QuickGO resolves nonobsolete GO:0030552. Parent resolution
    is distinguished from completeness of emitted links.
  target_ids:
  - UniProtKB-KW:KW-0116
  evidence_ids:
  - keyword
  - parent
  - nucleotide
  - go
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T07:11:04Z'
  snapshot_sha256: 5b1b727d6335d51922c4fbd046a9f28023fe6ae13413f25458bd889072877588
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T07:11:04Z'
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
  accessed_at: '2026-10-21T07:11:04Z'
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
  reference: data/traits/function/binding_capacity/uniprot_keywords/camp-kw-0114.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T07:11:04Z'
  snapshot_sha256: 1a1cc1c859426dbf684718adc1fbcf0d34d9d3aabcef777c4b33d70ed8619eed
  support: supports
  summary: Complete local parent record inspected for identifier, class, definition
    and broader-parent chain.
- evidence_id: keyword
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0116.json
  accessed_at: '2026-10-21T07:10:44.821356Z'
  snapshot_sha256: 9e1515a069dbf62d05896046c6c932267346340fcc0947dd86febf32e5de573a
  support: supports
  locator: Complete keyword JSON and X-UniProt-Release response header
  summary: UniProt 2026_03 resolves cAMP-binding KW-0116. The full definition, five
    binding aliases and GO:0030552 association match the record. It asserts cAMP and
    Nucleotide-binding as immediate parents.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0114.json
  accessed_at: '2026-10-21T07:10:45.506620Z'
  snapshot_sha256: bd9422affee263b0ed1ef45e84ad156bb11efc0c3ec8e7f6d5f2ae5f67bbad4e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: cAMP KW-0114 is a distinct broader dependence-or-hydrolysis class and explicitly
    lists cAMP-binding as a child; the target should not be merged with it.
- evidence_id: go
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0030552
  accessed_at: '2026-10-21T07:10:46.715509Z'
  snapshot_sha256: a6baa2636634a34d36f89a0ad4f93cdf6e0acfad2131fe6419f3361ca4c4ae96
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: GO:0030552 is nonobsolete cAMP binding, identifying cyclic adenosine 3-prime,5-prime
    monophosphate and the same direct ligand-binding capability.
- evidence_id: nucleotide
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-0547.json
  accessed_at: '2026-10-21T07:10:46.107043Z'
  snapshot_sha256: f74bb937d36c85aa47ae337c42027958e3fb9ff27285c3d592d1a7519c41d0a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nucleotide-binding KW-0547 resolves as a broader nucleotide-binding class
    and explicitly lists both cAMP-binding and cGMP-binding children.
- evidence_id: local-nucleotide
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/nucleotide-binding-kw-0547.yaml
  accessed_at: '2026-10-21T07:14:34Z'
  snapshot_sha256: c724c9d8fe816fe98a1d25386813bf1b5c96077e619793dc51d1efabe34f7a60
  support: supports
  summary: Complete local Nucleotide-binding record inspected; it exists as a separate
    class. The target retained cyclic-nucleotide parent has no parent_traits, so its
    local chain does not recover this source route.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  locator: Executed 2026-10-21T07:13:57Z through 2026-10-21T07:13:58Z; exit 0
  accessed_at: '2026-10-21T07:13:58Z'
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
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/camp-binding-kw-0116.yaml
  locator: Executed 2026-10-21T07:13:58Z through 2026-10-21T07:13:58Z; exit 0
  accessed_at: '2026-10-21T07:13:58Z'
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
  - UniProtKB-KW:KW-0116
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
  - UniProtKB-KW:KW-0116
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
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-5
  topic: Scope
- area: consistency
  outcome: concern
  summary: The retained cAMP parent is source-asserted and broader, but the second
    immediate Nucleotide-binding parent is absent. The retained local parent chain
    terminates, so it does not recover the omitted ancestry.
  evidence_ids:
  - record
  - keyword
  - parent
  - local-parent-1
  - nucleotide
  - local-nucleotide
  - owner
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-6
  topic: Consistency
- area: identity
  outcome: supported
  summary: The target denotes direct cAMP binding at protein-class level, distinct
    from the broader cAMP-dependent/hydrolytic source class.
  evidence_ids:
  - record
  - keyword
  - parent
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-7
  topic: Identity
- area: grounding
  outcome: supported
  summary: The GO:0030552 association is source-direct and equivalent in intended
    binding-function scope.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-8
  topic: Grounding
- area: nomenclature
  outcome: supported
  summary: All five aliases are source-attested cAMP-binding names; the cyclic nucleotide
    identity is explicit in the definition and GO term.
  evidence_ids:
  - record
  - keyword
  - go
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-9
  topic: Nomenclature
- area: representation
  outcome: supported
  summary: FUNCTION/binding capacity is appropriate; no localized motif, residue interval,
    obligatory hydrolysis or kinase activity is asserted.
  evidence_ids:
  - record
  - schema
  - keyword
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-10
  topic: Representation
- area: evidence
  outcome: supported
  summary: The direct-binding claim and chemical name are supported by the inspected
    official keyword and GO definition; broader parent background is not silently
    made part of every target protein mechanism.
  evidence_ids:
  - record
  - keyword
  - go
  - parent
  target_ids:
  - UniProtKB-KW:KW-0116
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: uniprot-keyword.KW-0116.lost-nucleotide-binding-parent
  category: consistency
  severity: minor
  title: Nucleotide-binding hierarchy path is omitted
  description: The current source asserts cAMP and Nucleotide-binding parents. The
    generator selects only one immediate parent and the local retained chain ends;
    Nucleotide-binding is therefore omitted despite an existing local class. The retained
    parent and target identity remain valid.
  evidence_ids:
  - record
  - keyword
  - parent
  - local-parent-1
  - nucleotide
  - local-nucleotide
  - owner
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0116
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
  description: Update immediate_parent/build_yaml in scripts/seed_uniprot_keywords.py
    to preserve all valid seeded immediate parents while retaining the category-root
    policy; regenerate affected records through that maintained input.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0116
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - A multiple-parent source fixture deterministically preserves both seeded parents.
  - Regenerated target retains its cyclic-nucleotide parent and reaches Nucleotide-binding
    without dangling category-root links.
  - Run strict validation and save a new review against changed bytes.
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
- No family-specific ligand-affinity assay, universal binding motif or catalytic consequence
  is established. The broader cAMP record is used only as parent context and is reviewed
  separately in path order.
tags:
- unreviewed-path-order
- batch-003
- uniprot-keywords
```
