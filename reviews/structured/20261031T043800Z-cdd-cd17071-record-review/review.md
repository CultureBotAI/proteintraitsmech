# Single-record scientific review of CDD:cd17071 (DCX1_DCDC2_like; doublecortin-like domain 1 found in doublecortin domain-containing protein 2 and similar proteins)

- Review: 20261031T043800Z-cdd-cd17071-record-review
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-31T04:28:00Z
- Finished UTC: 2026-10-31T04:38:00Z
- Reviewer: Antigravity (independent)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

CDD:cd17071 (label DCX1_DCDC2_like; opening definition phrase 'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins') passes strict LinkML schema validation and represents a valid class-level sequence domain trait (SEQ_DOMAIN on SEQUENCE, parent_traits: [CDD:cl28922], 0 canonical_examples) modeling the N-terminal first doublecortin-like (DCX1) repeat subfamily profile of DCDC2 and its close paralogs DCDC2B and DCDC2C (grouping child profiles CDD:cd17149, CDD:cd17150, and CDD:cd17151), a microtubule-associated protein family with tandem ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated with developmental dyslexia (PMID:16278295). However, its upstream CDD-seeded definition starts with a typographical error ('Dublecortin-like domain 1...'), interpolates an off-target sentence defining the ubiquitin protein modifier ('Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.') even though DCX domains only adopt a ubiquitin-like beta-grasp tertiary fold and do not function as ubiquitin protein modifiers, and lacks a literature evidence block citing PMID:16278295 — the exact upstream defect class repaired on child N-terminal repeat 1 profile CDD:cd17149 (label DCX1_DCDC2) in Cycle 2 Stage 5 (#1188). Preserved as open finding F25 for Cycle 4 Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.

## Scope And Provenance

Full single-record scientific review of CDD:cd17071 covering identity, axis/category placement, hierarchy, subfamily relationship to child profiles CDD:cd17149, CDD:cd17150, and CDD:cd17151 and tandem-repeat sibling CDD:cd16113, literature evidence, prose accuracy, and writer ownership.

Selection: Selected from the frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN sibling inventory as the uncurated N-terminal repeat-1 subfamily parent profile of DCDC2 and similar proteins (DCX1_DCDC2_like) exhibiting both the opening 'Dublecortin-like' typo and the upstream CDD ubiquitin protein-modifier digression.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: git_commit at Git base 5869b9c877b532972a405523c7c6e21945c177e4.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| CDD:cd17071 | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml | generated | DCX1_DCDC2_like |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML and OAK ontology-binding validation | passed | True | CDD:cd17071 | Record passes closed LinkML schema validation and OAK term-label bindings with 0 errors. |
| Release-pinned UniProt grounding and binding replay | passed | True | CDD:cd17071 | Record has 0 canonical_examples on disk (subfamily parent profile) and 0 QUALIFIED bindings; 23,062 corpus qualified_record_bindings verify across 13,532 registry proteins with 0 semantic findings. |
| Causal-graph structural and semantic audit | passed | False | CDD:cd17071 | Record has no causal_graphs block (0 graphs, 0 errors); absence is expected for uncurated CDD sequence domain records. |
| Registered write-route audit | passed | True | CDD:cd17071 | 620 scripts examined (51 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses) with 0 unguarded writer findings. |

## Scientific And Domain Assessments

### Class-level N-terminal DCX1 subfamily identity and CDD superfamily hierarchy

identity: supported. Targets: CDD:cd17071.

CDD:cd17071 is a valid class-level sequence domain trait (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN, label: DCX1_DCDC2_like, parent_traits: [CDD:cl28922]) representing the N-terminal first doublecortin-like repeat subfamily profile of DCDC2 and similar proteins (DCDC2B, DCDC2C), distinct from C-terminal second-repeat subfamily sibling CDD:cd16113 (DCX2_DCDC2_like) and paralog-specific child repeat-1 profiles CDD:cd17149 (DCX1_DCDC2), CDD:cd17150 (DCX1_DCDC2B), and CDD:cd17151 (DCX1_DCDC2C).

### Subfamily parent profile carrier status

grounding: supported. Targets: CDD:cd17071.

CDD:cd17071 carries 0 canonical_examples on disk as a broader CDD subfamily hierarchy node above paralog-specific profiles cd17149 (human DCDC2 UniProtKB:Q9UHG0), cd17150 (human DCDC2B UniProtKB:A2VCK2), and cd17151 (human DCDC2C UniProtKB:A8MYV0).

### Upstream CDD opening typo ('Dublecortin-like'), off-target ubiquitin protein-modifier definition sentence, and missing PMID:16278295 evidence block

consistency: concern. Targets: CDD:cd17071.

CDD:cd17071 inherits the upstream NCBI CDD opening typo 'Dublecortin-like domain 1...' and the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.' even though DCX domains only adopt a ubiquitin-like beta-grasp fold and do not act as ubiquitin protein modifiers, and lacks a literature evidence block citing PMID:16278295.

## Findings

### F25: CDD:cd17071 (DCX1_DCDC2_like) starts its definition with typo 'Dublecortin-like' and interpolates an off-target ubiquitin protein-modifier sentence into a microtubule-binding DCX repeat profile

minor / open / confirmed; issue key: cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression.

In data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml, the domain profile models the N-terminal first doublecortin-like domain subfamily (label DCX1_DCDC2_like, parent_traits: [CDD:cl28922]) of DCDC2 and similar proteins (grouping child profiles CDD:cd17149 on DCDC2, CDD:cd17150 on DCDC2B, and CDD:cd17151 on DCDC2C), microtubule-associated proteins with tandem ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated with reading disability/dyslexia (PMID:16278295). However, its upstream CDD definition begins with the typographical error 'Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins.' and interpolates the off-target sentence 'Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various cellular processes, including transcriptional regulation, cell cycle control, and DNA repair.' DCX domains only share a ubiquitin-like beta-grasp tertiary fold and do not function as ubiquitin protein modifiers, and CDD:cd17071 currently lacks an evidence block citing PMID:16278295. Preserved open in Stage 4 for Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.

## Recommended Actions And Acceptance Checks

### repair-cd17071-definition-and-evidence-via-cdd-errata

Add an accession-keyed erratum for CDD:cd17071 in scripts/cdd_errata.py and apply it via scripts/repair_cdd_errata.py, correcting the opening 'Dublecortin-like' typo, replacing the off-target 'Ubiquitin (Ub) is a protein modifier in eukaryotes...' sentence with the tandem DCX ubiquitin-like beta-grasp repeat description, and adding an evidence entry citing PMID:16278295.

- CDD:cd17071 definition begins with 'Doublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins.' and accurately describes the N-terminal first DCX repeat subfamily adopting a ubiquitin-like beta-grasp tertiary fold without the off-target ubiquitin protein-modifier digression.
- CDD:cd17071 evidence block is populated with PMID:16278295 and a verbatim DCDC2 doublecortin-domain/dyslexia snippet.
- scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay the erratum idempotently and scripts/validate_strict.py passes with 0 errors.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| ev-cd17071-yaml | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml; identifier, label, definition, definition_source, parent_traits | partial | CDD:cd17071 (label DCX1_DCDC2_like, parent_traits: [CDD:cl28922], SEEDED, 0 canonical_examples) models the N-terminal first DCX repeat subfamily profile of DCDC2 and similar proteins, but starts its definition with the typo 'Dublecortin-like domain 1...', interpolates an off-target sentence defining the ubiquitin protein modifier even though DCX domains only share a ubiquitin-like beta-grasp fold, and lacks an evidence block. |
| ev-cd17149-child | data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml; identifier, label, definition, parent_traits, canonical_examples, evidence (PMID:16278295) | supports | Specific N-terminal repeat 1 child profile CDD:cd17149 (label DCX1_DCDC2, parent_traits: [CDD:cl28922], carrying human UniProtKB:Q9UHG0) and paralog repeat-1 profiles CDD:cd17150 (DCX1_DCDC2B) and CDD:cd17151 (DCX1_DCDC2C) were repaired in Cycles 1-2 (#1171, #1188) to fix the 'Dublecortin-like' opening typo, replace the off-target ubiquitin protein-modifier digression with the tandem DCX ubiquitin-like beta-grasp repeat description, and cite PMID:16278295. |
| ev-cd16113-sibling | data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml; identifier, label, definition, parent_traits | supports | C-terminal second-repeat subfamily sibling CDD:cd16113 (label DCX2_DCDC2_like, parent_traits: [CDD:cl28922]) confirms that CDD:cd17071 is the distinct N-terminal DCX1 subfamily parent profile of DCDC2/DCDC2B/DCDC2C. |
| ev-pmid-16278295 | https://pubmed.ncbi.nlm.nih.gov/16278295/; PMID:16278295 (Meng et al., 2005, Proc Natl Acad Sci U S A 102:17053-17058) | supports | Primary human genetics and functional study (Meng et al., 2005, PNAS 102:17053-17058) establishing that DCDC2 (UniProtKB:Q9UHG0) is a doublecortin-domain microtubule-associated protein involved in neuronal migration and associated with developmental dyslexia. |
| ev-cdd-errata-writer | scripts/cdd_errata.py; CDD_ERRATA table (24 entries) and scripts/repair_cdd_errata.py | supports | scripts/cdd_errata.py currently contains 24 accession-keyed entries (including child repeat-1 profiles CDD:cd17149, CDD:cd17150, and CDD:cd17151 and repeat-2 profiles CDD:cd17152, CDD:cd17153, and CDD:cd17154) wired into scripts/seed_cdd.py and scripts/repair_cdd_errata.py, providing the exact registered repair route for adding CDD:cd17071 in Stage 5. |

## Limits And Additional Notes

- This single-record review covers CDD:cd17071 only; the full 12-record frozen Cycle 4 Stage 4 CDD sibling inventory is reviewed in companion category bundle 20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review.
- No edits to data/traits/ were performed in Stage 4; finding F25 is preserved open for Stage 5 grouped remediation.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261031T043800Z-cdd-cd17071-record-review
kind: record
repository: CultureBotAI/proteintraitsmech
title: Single-record scientific review of CDD:cd17071 (DCX1_DCDC2_like; doublecortin-like
  domain 1 found in doublecortin domain-containing protein 2 and similar proteins)
started_at: '2026-10-31T04:28:00Z'
finished_at: '2026-10-31T04:38:00Z'
reviewer:
  identity: Antigravity
  kind: agent
  model: Claude Opus 4.6
  independence: independent
  independence_basis: Cycle 4 Stage 4 single-record scientific audit of the committed
    CDD:cd17071 record and its child-subfamily and tandem-repeat sibling boundary
    context (CDD:cd16113, CDD:cd17149, CDD:cd17150, CDD:cd17151) without modifying
    scientific records.
skill: review-yaml-record
completion: completed
verdict: needs_curation
native_verdict: NEEDS_CURATION
scientific_review: true
summary: 'CDD:cd17071 (label DCX1_DCDC2_like; opening definition phrase ''Dublecortin-like
  domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins'')
  passes strict LinkML schema validation and represents a valid class-level sequence
  domain trait (SEQ_DOMAIN on SEQUENCE, parent_traits: [CDD:cl28922], 0 canonical_examples)
  modeling the N-terminal first doublecortin-like (DCX1) repeat subfamily profile
  of DCDC2 and its close paralogs DCDC2B and DCDC2C (grouping child profiles CDD:cd17149,
  CDD:cd17150, and CDD:cd17151), a microtubule-associated protein family with tandem
  ubiquitin-like beta-grasp DCX repeats whose human DCDC2 variants are associated
  with developmental dyslexia (PMID:16278295). However, its upstream CDD-seeded definition
  starts with a typographical error (''Dublecortin-like domain 1...''), interpolates
  an off-target sentence defining the ubiquitin protein modifier (''Ubiquitin (Ub)
  is a protein modifier in eukaryotes that is involved in various cellular processes,
  including transcriptional regulation, cell cycle control, and DNA repair.'') even
  though DCX domains only adopt a ubiquitin-like beta-grasp tertiary fold and do not
  function as ubiquitin protein modifiers, and lacks a literature evidence block citing
  PMID:16278295 — the exact upstream defect class repaired on child N-terminal repeat
  1 profile CDD:cd17149 (label DCX1_DCDC2) in Cycle 2 Stage 5 (#1188). Preserved as
  open finding F25 for Cycle 4 Stage 5 grouped remediation via scripts/cdd_errata.py
  and scripts/repair_cdd_errata.py.'
source:
  git_revision: 5869b9c877b532972a405523c7c6e21945c177e4
  state: git_commit
  inputs:
  - path: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
    sha256: d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
    sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
    role: target
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
    sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml
    sha256: fe5af61fd44b4a50b6c9f0ab06ddd1d717895a010f788b8096ff64d3f68e4756
    role: context
  - path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml
    sha256: 6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d
    role: context
  - path: scripts/cdd_errata.py
    sha256: 332155e8c1f1a119ca0f3c4394b49fa775bcc8d9f4c68e1f43183bd97b64d962
    role: context
  - path: scripts/record_io.py
    sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
    role: context
  - path: scripts/repair_cdd_errata.py
    sha256: 0a7fcce6f8f00a4d20b1a4f94a6ec77f32c6ab62d9edc2fd4a228fbda48cea9d
    role: context
  - path: scripts/seed_cdd.py
    sha256: 4fd337316239794623aaa2ad8afed44bb96ead33a1b387921272f26f8731365a
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Full single-record scientific review of CDD:cd17071 covering identity,
    axis/category placement, hierarchy, subfamily relationship to child profiles CDD:cd17149,
    CDD:cd17150, and CDD:cd17151 and tandem-repeat sibling CDD:cd16113, literature
    evidence, prose accuracy, and writer ownership.
  selection: Selected from the frozen 12-record Cycle 4 Stage 4 CDD SEQ_DOMAIN sibling
    inventory as the uncurated N-terminal repeat-1 subfamily parent profile of DCDC2
    and similar proteins (DCX1_DCDC2_like) exhibiting both the opening 'Dublecortin-like'
    typo and the upstream CDD ubiquitin protein-modifier digression.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - CDD:cd17071
targets:
- target_id: CDD:cd17071
  path: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  label: DCX1_DCDC2_like
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  semantic_digest:
    algorithm: sha256_file
    sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
checks:
- check_id: schema
  name: Strict LinkML and OAK ontology-binding validation
  command: .venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Record passes closed LinkML schema validation and OAK term-label bindings
    with 0 errors.
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
- check_id: semantic
  name: Release-pinned UniProt grounding and binding replay
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv
    data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Record has 0 canonical_examples on disk (subfamily parent profile) and
    0 QUALIFIED bindings; 23,062 corpus qualified_record_bindings verify across 13,532
    registry proteins with 0 semantic findings.
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
- check_id: graphs
  name: Causal-graph structural and semantic audit
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  exit_code: 0
  status: passed
  required: false
  summary: Record has no causal_graphs block (0 graphs, 0 errors); absence is expected
    for uncurated CDD sequence domain records.
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
- check_id: writer-audit
  name: Registered write-route audit
  command: .venv/bin/python scripts/audit_writers.py
  exit_code: 0
  status: passed
  required: true
  summary: 620 scripts examined (51 seeders, 9 registered editors, 2 transactional
    promoters, 52 declared bypasses) with 0 unguarded writer findings.
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cdd-errata-writer
evidence:
- evidence_id: ev-cd17071-yaml
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml
  locator: identifier, label, definition, definition_source, parent_traits
  accessed_at: '2026-10-31T04:30:00Z'
  snapshot_sha256: deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50
  support: partial
  quote: Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2 (DCDC2) and similar proteins. DCDC2 is a member of the doublecortin (DCX) family.
    It is a microtubule-associated protein (MAP) with stable double tandem DCX repeats
    of ubiquitin-like tertiary fold. Ubiquitin (Ub) is a protein modifier in eukaryotes
    that is involved in various cellular processes, including transcriptional regulation,
    cell cycle control, and DNA repair. Microtubules are key components of the cytoskeleton
    that are involved in cell movement, shape determination, division and transport.
    DCDC2 genetic variation in humans is associated with reading disability, attention
    deficit hyperactivity disorder (ADHD), and difficulties in mathematics. A genetic
    variant of DCDC2 associates with dyslexia, a common neurobehavioral disorder of
    reading. DCDC2 protein interacts with many of the same cytoskeleton related proteins
    that other members of the DCX family interact with
  summary: 'CDD:cd17071 (label DCX1_DCDC2_like, parent_traits: [CDD:cl28922], SEEDED,
    0 canonical_examples) models the N-terminal first DCX repeat subfamily profile
    of DCDC2 and similar proteins, but starts its definition with the typo ''Dublecortin-like
    domain 1...'', interpolates an off-target sentence defining the ubiquitin protein
    modifier even though DCX domains only share a ubiquitin-like beta-grasp fold,
    and lacks an evidence block.'
- evidence_id: ev-cd17149-child
  kind: record_content
  reference: data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml
  locator: identifier, label, definition, parent_traits, canonical_examples, evidence
    (PMID:16278295)
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: 47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5
  support: supports
  quote: Doublecortin-like domain 1 found in doublecortin domain-containing protein
    2 (DCDC2). DCDC2 is a member of the doublecortin (DCX) family. It is a microtubule-associated
    protein (MAP) with stable double tandem DCX repeats adopting a ubiquitin-like
    beta-grasp tertiary fold. Microtubules are key components of the cytoskeleton
    that are involved in cell movement, shape determination, division and transport.
    DCDC2 genetic variation in humans is associated with reading disability, attention
    deficit hyperactivity disorder (ADHD), and difficulties in mathematics. A genetic
    variant of DCDC2 associates with dyslexia, a common neurobehavioral disorder of
    reading. DCDC2 protein interacts with many of the same cytoskeleton related proteins
    that other members of the DCX family interact with
  summary: 'Specific N-terminal repeat 1 child profile CDD:cd17149 (label DCX1_DCDC2,
    parent_traits: [CDD:cl28922], carrying human UniProtKB:Q9UHG0) and paralog repeat-1
    profiles CDD:cd17150 (DCX1_DCDC2B) and CDD:cd17151 (DCX1_DCDC2C) were repaired
    in Cycles 1-2 (#1171, #1188) to fix the ''Dublecortin-like'' opening typo, replace
    the off-target ubiquitin protein-modifier digression with the tandem DCX ubiquitin-like
    beta-grasp repeat description, and cite PMID:16278295.'
- evidence_id: ev-cd16113-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml
  locator: identifier, label, definition, parent_traits
  accessed_at: '2026-10-31T04:31:00Z'
  snapshot_sha256: d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f
  support: supports
  quote: Doublecortin-like domain 2 found in doublecortin domain-containing protein
    2 (DCDC2). DCDC2 is a member of the doublecortin (DCX) family. It is a microtubule-associated
    protein (MAP) with stable double tandem DCX repeats of a ubiquitin-like tertiary
    fold. Ubiquitin (Ub) is a protein modifier in eukaryotes that is involved in various
    cellular processes including transcriptional regulation, cell cycle control, and
    DNA repair. Microtubules are key components of cytoskeleton that are involved
    in cell movement, shape determination, division and transport. DCDC2 genetic variation
    in humans is associated with reading disability, attention deficit hyperactivity
    disorder (ADHD), and difficulties in mathematics. A genetic variant of DCDC2 associates
    with dyslexia, a common neurobehavioral disorder of reading. DCDC2 protein interacts
    with many of the same cytoskeleton related proteins that other members of the
    DCX family interact with
  summary: 'C-terminal second-repeat subfamily sibling CDD:cd16113 (label DCX2_DCDC2_like,
    parent_traits: [CDD:cl28922]) confirms that CDD:cd17071 is the distinct N-terminal
    DCX1 subfamily parent profile of DCDC2/DCDC2B/DCDC2C.'
- evidence_id: ev-pmid-16278295
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/16278295/
  locator: PMID:16278295 (Meng et al., 2005, Proc Natl Acad Sci U S A 102:17053-17058)
  accessed_at: '2026-10-31T04:32:00Z'
  support: supports
  quote: DCDC2 contains a doublecortin peptide domain and is associated with reading
    disability (dyslexia)
  summary: Primary human genetics and functional study (Meng et al., 2005, PNAS 102:17053-17058)
    establishing that DCDC2 (UniProtKB:Q9UHG0) is a doublecortin-domain microtubule-associated
    protein involved in neuronal migration and associated with developmental dyslexia.
- evidence_id: ev-cdd-errata-writer
  kind: record_content
  reference: scripts/cdd_errata.py
  locator: CDD_ERRATA table (24 entries) and scripts/repair_cdd_errata.py
  accessed_at: '2026-10-31T04:32:00Z'
  snapshot_sha256: 332155e8c1f1a119ca0f3c4394b49fa775bcc8d9f4c68e1f43183bd97b64d962
  support: supports
  summary: scripts/cdd_errata.py currently contains 24 accession-keyed entries (including
    child repeat-1 profiles CDD:cd17149, CDD:cd17150, and CDD:cd17151 and repeat-2
    profiles CDD:cd17152, CDD:cd17153, and CDD:cd17154) wired into scripts/seed_cdd.py
    and scripts/repair_cdd_errata.py, providing the exact registered repair route
    for adding CDD:cd17071 in Stage 5.
assessments:
- assessment_id: identity-and-hierarchy
  area: identity
  topic: Class-level N-terminal DCX1 subfamily identity and CDD superfamily hierarchy
  outcome: supported
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
  - ev-cd17149-child
  - ev-cd16113-sibling
  summary: 'CDD:cd17071 is a valid class-level sequence domain trait (trait_axis:
    SEQUENCE, trait_category: SEQ_DOMAIN, label: DCX1_DCDC2_like, parent_traits: [CDD:cl28922])
    representing the N-terminal first doublecortin-like repeat subfamily profile of
    DCDC2 and similar proteins (DCDC2B, DCDC2C), distinct from C-terminal second-repeat
    subfamily sibling CDD:cd16113 (DCX2_DCDC2_like) and paralog-specific child repeat-1
    profiles CDD:cd17149 (DCX1_DCDC2), CDD:cd17150 (DCX1_DCDC2B), and CDD:cd17151
    (DCX1_DCDC2C).'
- assessment_id: grounding-and-carriers
  area: grounding
  topic: Subfamily parent profile carrier status
  outcome: supported
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
  - ev-cd17149-child
  - ev-pmid-16278295
  summary: CDD:cd17071 carries 0 canonical_examples on disk as a broader CDD subfamily
    hierarchy node above paralog-specific profiles cd17149 (human DCDC2 UniProtKB:Q9UHG0),
    cd17150 (human DCDC2B UniProtKB:A2VCK2), and cd17151 (human DCDC2C UniProtKB:A8MYV0).
- assessment_id: definition-typo-and-ubiquitin-digression
  area: consistency
  topic: Upstream CDD opening typo ('Dublecortin-like'), off-target ubiquitin protein-modifier
    definition sentence, and missing PMID:16278295 evidence block
  outcome: concern
  target_ids:
  - CDD:cd17071
  evidence_ids:
  - ev-cd17071-yaml
  - ev-cd17149-child
  - ev-pmid-16278295
  - ev-cdd-errata-writer
  summary: CDD:cd17071 inherits the upstream NCBI CDD opening typo 'Dublecortin-like
    domain 1...' and the off-target sentence 'Ubiquitin (Ub) is a protein modifier
    in eukaryotes that is involved in various cellular processes, including transcriptional
    regulation, cell cycle control, and DNA repair.' even though DCX domains only
    adopt a ubiquitin-like beta-grasp fold and do not act as ubiquitin protein modifiers,
    and lacks a literature evidence block citing PMID:16278295.
findings:
- finding_id: F25
  issue_key: cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression
  category: consistency
  severity: minor
  status: open
  certainty: confirmed
  title: CDD:cd17071 (DCX1_DCDC2_like) starts its definition with typo 'Dublecortin-like'
    and interpolates an off-target ubiquitin protein-modifier sentence into a microtubule-binding
    DCX repeat profile
  description: 'In data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml,
    the domain profile models the N-terminal first doublecortin-like domain subfamily
    (label DCX1_DCDC2_like, parent_traits: [CDD:cl28922]) of DCDC2 and similar proteins
    (grouping child profiles CDD:cd17149 on DCDC2, CDD:cd17150 on DCDC2B, and CDD:cd17151
    on DCDC2C), microtubule-associated proteins with tandem ubiquitin-like beta-grasp
    DCX repeats whose human DCDC2 variants are associated with reading disability/dyslexia
    (PMID:16278295). However, its upstream CDD definition begins with the typographical
    error ''Dublecortin-like domain 1 found in doublecortin domain-containing protein
    2 (DCDC2) and similar proteins.'' and interpolates the off-target sentence ''Ubiquitin
    (Ub) is a protein modifier in eukaryotes that is involved in various cellular
    processes, including transcriptional regulation, cell cycle control, and DNA repair.''
    DCX domains only share a ubiquitin-like beta-grasp tertiary fold and do not function
    as ubiquitin protein modifiers, and CDD:cd17071 currently lacks an evidence block
    citing PMID:16278295. Preserved open in Stage 4 for Stage 5 grouped remediation
    via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.'
  target_ids:
  - CDD:cd17071
  field_paths:
  - data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml#/definition
  evidence_ids:
  - ev-cd17071-yaml
  - ev-cd17149-child
  - ev-cd16113-sibling
  - ev-pmid-16278295
  - ev-cdd-errata-writer
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/605
actions:
- action_id: repair-cd17071-definition-and-evidence-via-cdd-errata
  description: Add an accession-keyed erratum for CDD:cd17071 in scripts/cdd_errata.py
    and apply it via scripts/repair_cdd_errata.py, correcting the opening 'Dublecortin-like'
    typo, replacing the off-target 'Ubiquitin (Ub) is a protein modifier in eukaryotes...'
    sentence with the tandem DCX ubiquitin-like beta-grasp repeat description, and
    adding an evidence entry citing PMID:16278295.
  finding_ids:
  - F25
  target_ids:
  - CDD:cd17071
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/cdd_errata.py
    role: Canonical accession-keyed CDD source-definition errata table
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/repair_cdd_errata.py
    role: Registered in-place CDD errata repair writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cdd.py
    role: Maintained CDD seeder transform wired to cdd_errata
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/record_io.py
    role: Guarded validated record writer
  acceptance_checks:
  - CDD:cd17071 definition begins with 'Doublecortin-like domain 1 found in doublecortin
    domain-containing protein 2 (DCDC2) and similar proteins.' and accurately describes
    the N-terminal first DCX repeat subfamily adopting a ubiquitin-like beta-grasp
    tertiary fold without the off-target ubiquitin protein-modifier digression.
  - CDD:cd17071 evidence block is populated with PMID:16278295 and a verbatim DCDC2
    doublecortin-domain/dyslexia snippet.
  - scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay the erratum idempotently
    and scripts/validate_strict.py passes with 0 errors.
limitations:
- This single-record review covers CDD:cd17071 only; the full 12-record frozen Cycle
  4 Stage 4 CDD sibling inventory is reviewed in companion category bundle 20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review.
- No edits to data/traits/ were performed in Stage 4; finding F25 is preserved open
  for Stage 5 grouped remediation.
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/605
```
