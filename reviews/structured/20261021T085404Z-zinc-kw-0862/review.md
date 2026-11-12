# Review of Zinc

- Review: 20261021T085404Z-zinc-kw-0862
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:46:19Z
- Finished UTC: 2026-10-21T08:54:04Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

Zinc keyword identity and source definition are supported. The dependence branch raises one minor provisional binding-capacity interpretation question.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 009. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4) covers 78 record paths, leaving 429281 before this batch. 9 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| UniProtKB-KW:KW-0862 | data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml | generated | Zinc |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | UniProtKB-KW:KW-0862 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | UniProtKB-KW:KW-0862 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | UniProtKB-KW:KW-0862 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | UniProtKB-KW:KW-0862 | Full curation-history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | UniProtKB-KW:KW-0862 | KW-0862, its Ligand parent, the scope-comparison GO term and the linked element page resolve. No direct GO equivalence or inferred Metal-binding parent is introduced. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: UniProtKB-KW:KW-0862.

The maintained UniProt keyword seeder owns future changes; this review does not modify emitted records.

### Provenance

provenance: supported. Targets: UniProtKB-KW:KW-0862.

Source identity and CC-BY 4.0 attribution are present. Current official source release is 2026_03; the original seed release is not claimed to be established.

### Completeness

completeness: supported. Targets: UniProtKB-KW:KW-0862.

This is a class record, with no instance sequence or specimen substituted for a trait. Optional motifs, structures, detection methods and canonical examples are not automatically required for this keyword.

### Graph

graph: not_applicable. Targets: UniProtKB-KW:KW-0862.

No causal_graphs or graph nodes occur in the target; no molecular mechanism or node-grounding coverage is claimed.

### Scope

scope: supported. Targets: UniProtKB-KW:KW-0862.

The record remains SEEDED. Review-bundle validation neither promotes scientific status nor qualifies any protein example.

### Identity

identity: supported. Targets: UniProtKB-KW:KW-0862.

KW-0862 denotes zinc-binding or zinc-dependent proteins, not elemental zinc as the trait itself. Source definition and element identity agree.

### Consistency

consistency: supported. Targets: UniProtKB-KW:KW-0862.

Only the Ligand category root is an immediate source parent. Its omission follows the seeder policy; a Metal-binding parent is not invented from elemental identity.

### Representation

representation: concern. Targets: UniProtKB-KW:KW-0862.

The source covers zinc binding or zinc-dependent function. Dependence alone does not establish direct zinc binding from the text. Routing every Ligand keyword to binding capacity therefore needs a bounded interpretation check; no concrete nonbinding member has been established here.

## Findings

### F1: Resolve the binding interpretation of functional dependence

minor / open / provisional; issue key: uniprot-keyword.KW-0862.binding-versus-dependence-scope.

The source definition includes zinc binding or zinc-dependent function; the local enum describes ability to bind. The textual entailment gap is confirmed, but actual misclassification of source members remains provisional because this review has not established a concrete nonbinding member.

## Recommended Actions And Acceptance Checks

### A1

Check source annotation rules or a bounded, source-asserted member set for KW-0862 before changing route() in scripts/seed_uniprot_keywords.py. Document whether binding capacity covers the complete source class; preserve identity and all supported branches if a different representation is needed.

- Use inspected annotation rules or member evidence to decide whether every stated branch entails binding.
- Do not equate the whole keyword to the comparison GO binding term without source-direct equivalence evidence.
- If routing changes, regenerate through the maintained seeder, validate and save a new scoped review; if supported, record the evidence resolving this provisional concern.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml; Entire target YAML | supports | Complete record inspected: stable keyword identity, definition/source, FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples, citations and graphs are absent from this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY | supports | FUNC_BINDING_CAPACITY is a protein-level ability to bind a ligand, distinct from localized sequence binding sites. parent_traits are broader classes; xrefs assert true source-direct equivalents. Optional examples and graphs are not mandatory for this class. |
| owner | scripts/seed_uniprot_keywords.py; route, immediate_parent, build_yaml, main | supports | Ligand keywords route to FUNC_BINDING_CAPACITY; definitions are copied; first immediate parent only is retained if seeded; untyped source aliases become EXACT_SYNONYM and source GO associations become xrefs. |
| licence | https://rest.uniprot.org/help/license; Inspected source response captured at the recorded UTC time | supports | UniProt permits copyrightable database content under Creative Commons Attribution 4.0; the record licence is compatible. |
| keyword | https://rest.uniprot.org/keywords/KW-0862.json; Inspected source response captured at the recorded UTC time | supports | Complete official KW-0862 response confirms Zinc identity, the binding-or-zinc-dependent definition, sole immediate Ligand parent and no geneOntologies field. The source child list is not evidence that those proteins cannot bind. |
| parent | https://rest.uniprot.org/keywords/KW-9993.json; Inspected source response captured at the recorded UTC time | supports | Ligand includes binding, association and activity dependence; it is a source category root rather than an emitted local parent. |
| go-comparison | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005488; Inspected source response captured at the recorded UTC time | supports | Current nonobsolete GO binding describes selective noncovalent interaction. This is scope context, not an asserted equivalent of KW-0862. |
| element | https://www.webelements.com/zinc/; Element identity table and description | supports | The element page linked by UniProt identifies zinc as Zn, atomic number 30, and metallic. It supports stable elemental identity, not protein membership or a universal binding inference. |
| mapping-file | https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go; Inspected source response captured at the recorded UTC time | supports | The complete official mapping file version 2026/07/06 14:08:43 was actually searched for KW-0862 and contains no entry. The current keyword JSON likewise lacks geneOntologies; absence is bounded to these two snapshots. |
| validation-1 | just validate data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml; Executed 2026-10-21T08:47:10Z through 2026-10-21T08:47:11Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml data/traits/function/cofactor_requirement/chebi/1-4-benzoquinone-chebi16509.yaml data/traits/function/cofactor_requirement/chebi/3-hydroxyechinenone-chebi80214.yaml data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydrobiopterin-chebi15372.yaml data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydropteridine-chebi28889.yaml data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-1-chebi60494.yaml data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-chebi17679.yaml data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-1-chebi58201.yaml data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-chebi17601.yaml data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml; Executed 2026-10-21T08:46:51Z through 2026-10-21T08:48:29Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml; Executed 2026-10-21T08:47:11Z through 2026-10-21T08:47:12Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:48:29Z through 2026-10-21T08:48:30Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The original keywlist release used for the original seed is not recoverable from this record. Current API release 2026_03 is a comparison snapshot, not an asserted historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle retains URLs, access times, digests and bounded observations, not full response bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are qualified. iModulonDB is not applicable to this generic ligand class without a gene, organism or expression dataset.
- No GO equivalence is asserted. The full mapping-file absence check does not establish absence of every possible zinc-related GO annotation.
- The Zinc transport and Zinc-finger children do not establish nonbinding members; no such inference is used.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T085404Z-zinc-kw-0862
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of Zinc
started_at: '2026-10-21T08:46:19Z'
finished_at: '2026-10-21T08:54:04Z'
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
summary: Zinc keyword identity and source definition are supported. The dependence
  branch raises one minor provisional binding-capacity interpretation question.
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
  - path: data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
    sha256: 2f5b4de1408958bd44645b3133c683ad2fd6f3e642bef633b071d5339d7b2257
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
  - path: scripts/seed_chebi_cofactor.py
    sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
    role: context
  - path: scripts/seed_uniprot_keywords.py
    sha256: 8b21fb8f61aea278c593f5afd22f0d137f159d66a75dad1067cc8eca44def576
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 1 in batch 009. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4) covers 78 record paths,
    leaving 429281 before this batch. 9 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - UniProtKB-KW:KW-0862
targets:
- kind: generated
  label: Zinc
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  record_class: ProteinTraitRecord
  target_id: UniProtKB-KW:KW-0862
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - UniProtKB-KW:KW-0862
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
    data/traits/function/cofactor_requirement/chebi/1-4-benzoquinone-chebi16509.yaml
    data/traits/function/cofactor_requirement/chebi/3-hydroxyechinenone-chebi80214.yaml
    data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydrobiopterin-chebi15372.yaml
    data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydropteridine-chebi28889.yaml
    data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-1-chebi60494.yaml
    data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-chebi17679.yaml
    data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-1-chebi58201.yaml
    data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-chebi17601.yaml
    data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - UniProtKB-KW:KW-0862
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - UniProtKB-KW:KW-0862
  evidence_ids:
  - validation-3
- check_id: gate-4
  name: Curation history validity
  command: just validate-history
  exit_code: 0
  status: passed
  required: true
  summary: Full curation-history gate; this review adds no history event.
  target_ids:
  - UniProtKB-KW:KW-0862
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: KW-0862, its Ligand parent, the scope-comparison GO term and the linked
    element page resolve. No direct GO equivalence or inferred Metal-binding parent
    is introduced.
  target_ids:
  - UniProtKB-KW:KW-0862
  evidence_ids:
  - keyword
  - parent
  - go-comparison
  - element
  - mapping-file
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:46:19Z'
  snapshot_sha256: 2f5b4de1408958bd44645b3133c683ad2fd6f3e642bef633b071d5339d7b2257
  support: supports
  summary: 'Complete record inspected: stable keyword identity, definition/source,
    FUNCTION axis, FUNC_BINDING_CAPACITY category, CLASS kind, SEEDED status, parent
    list, synonyms, xrefs and CC-BY 4.0 licence; optional representations, examples,
    citations and graphs are absent from this YAML.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, parent_traits, xrefs and FUNC_BINDING_CAPACITY
  accessed_at: '2026-10-21T08:46:19Z'
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
  accessed_at: '2026-10-21T08:46:19Z'
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
  reference: https://rest.uniprot.org/keywords/KW-0862.json
  accessed_at: '2026-10-21T08:47:18.237222Z'
  snapshot_sha256: eea8b1cd9c6928ea2da9718d3650fb20bfeabc6eb1ae2db7f3f0b2de635e4c31
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Complete official KW-0862 response confirms Zinc identity, the binding-or-zinc-dependent
    definition, sole immediate Ligand parent and no geneOntologies field. The source
    child list is not evidence that those proteins cannot bind.
- evidence_id: parent
  kind: database
  reference: https://rest.uniprot.org/keywords/KW-9993.json
  accessed_at: '2026-10-21T07:29:38.225896Z'
  snapshot_sha256: af0b8fbd848293aacc57bd5fc3bbd1c5de88f31171ed37d123ca0bb8f480cc0e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Ligand includes binding, association and activity dependence; it is a source
    category root rather than an emitted local parent.
- evidence_id: go-comparison
  kind: database
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0005488
  accessed_at: '2026-10-21T07:30:35.712062Z'
  snapshot_sha256: 6015a69036105c45e68c1938c9169449c9c69dabee51b002563d8f9e97ab667a
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Current nonobsolete GO binding describes selective noncovalent interaction.
    This is scope context, not an asserted equivalent of KW-0862.
- evidence_id: element
  kind: authority
  reference: https://www.webelements.com/zinc/
  accessed_at: '2026-10-21T08:49:49.031955Z'
  snapshot_sha256: c3e65533723558e701f971afdaba1c74d1f7b12e4ffb62c24809334a0024b3ce
  support: supports
  locator: Element identity table and description
  summary: The element page linked by UniProt identifies zinc as Zn, atomic number
    30, and metallic. It supports stable elemental identity, not protein membership
    or a universal binding inference.
- evidence_id: mapping-file
  kind: database
  reference: https://current.geneontology.org/ontology/external2go/uniprotkb_kw2go
  accessed_at: '2026-10-21T06:55:26.808623Z'
  snapshot_sha256: f38e663ed40d606803242afca204c0f285f211423c237251012b61f68ebdb36d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The complete official mapping file version 2026/07/06 14:08:43 was actually
    searched for KW-0862 and contains no entry. The current keyword JSON likewise
    lacks geneOntologies; absence is bounded to these two snapshots.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  locator: Executed 2026-10-21T08:47:10Z through 2026-10-21T08:47:11Z; exit 0
  accessed_at: '2026-10-21T08:47:11Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
    data/traits/function/cofactor_requirement/chebi/1-4-benzoquinone-chebi16509.yaml
    data/traits/function/cofactor_requirement/chebi/3-hydroxyechinenone-chebi80214.yaml
    data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydrobiopterin-chebi15372.yaml
    data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydropteridine-chebi28889.yaml
    data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-1-chebi60494.yaml
    data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-chebi17679.yaml
    data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-1-chebi58201.yaml
    data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-chebi17601.yaml
    data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  locator: Executed 2026-10-21T08:46:51Z through 2026-10-21T08:48:29Z; exit 0
  accessed_at: '2026-10-21T08:48:29Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml
  locator: Executed 2026-10-21T08:47:11Z through 2026-10-21T08:47:12Z; exit 0
  accessed_at: '2026-10-21T08:47:12Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T08:48:29Z through 2026-10-21T08:48:30Z; exit 0
  accessed_at: '2026-10-21T08:48:30Z'
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
  - UniProtKB-KW:KW-0862
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
  - UniProtKB-KW:KW-0862
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
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-3
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal_graphs or graph nodes occur in the target; no molecular mechanism
    or node-grounding coverage is claimed.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-4
  topic: Graph
- area: scope
  outcome: supported
  summary: The record remains SEEDED. Review-bundle validation neither promotes scientific
    status nor qualifies any protein example.
  evidence_ids:
  - record
  target_ids:
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-5
  topic: Scope
- area: identity
  outcome: supported
  summary: KW-0862 denotes zinc-binding or zinc-dependent proteins, not elemental
    zinc as the trait itself. Source definition and element identity agree.
  evidence_ids:
  - record
  - keyword
  - element
  target_ids:
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-6
  topic: Identity
- area: consistency
  outcome: supported
  summary: Only the Ligand category root is an immediate source parent. Its omission
    follows the seeder policy; a Metal-binding parent is not invented from elemental
    identity.
  evidence_ids:
  - keyword
  - parent
  - owner
  target_ids:
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: concern
  summary: The source covers zinc binding or zinc-dependent function. Dependence alone
    does not establish direct zinc binding from the text. Routing every Ligand keyword
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
  - UniProtKB-KW:KW-0862
  assessment_id: assessment-8
  topic: Representation
findings:
- issue_key: uniprot-keyword.KW-0862.binding-versus-dependence-scope
  category: scope
  severity: minor
  title: Resolve the binding interpretation of functional dependence
  description: The source definition includes zinc binding or zinc-dependent function;
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
  field_paths:
  - trait_category
  - definition
  finding_id: F1
  status: open
  target_ids:
  - UniProtKB-KW:KW-0862
  owner_paths:
  - path: scripts/seed_uniprot_keywords.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, completeness
    or interpretation needs follow-up.
actions:
- action_id: A1
  description: Check source annotation rules or a bounded, source-asserted member
    set for KW-0862 before changing route() in scripts/seed_uniprot_keywords.py. Document
    whether binding capacity covers the complete source class; preserve identity and
    all supported branches if a different representation is needed.
  finding_ids:
  - F1
  target_ids:
  - UniProtKB-KW:KW-0862
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
- The original keywlist release used for the original seed is not recoverable from
  this record. Current API release 2026_03 is a comparison snapshot, not an asserted
  historical seed release.
- External responses were inspected and SHA256-captured in session scratch; the bundle
  retains URLs, access times, digests and bounded observations, not full response
  bodies.
- This is one record review, not a source-wide audit. No examples or mechanisms are
  qualified. iModulonDB is not applicable to this generic ligand class without a gene,
  organism or expression dataset.
- No GO equivalence is asserted. The full mapping-file absence check does not establish
  absence of every possible zinc-related GO annotation.
- The Zinc transport and Zinc-finger children do not establish nonbinding members;
  no such inference is used.
tags:
- unreviewed-path-order
- batch-009
- uniprot-keywords
```
