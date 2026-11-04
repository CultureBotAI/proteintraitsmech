# Single-record scientific review of CDD:cd15854 (SNARE_SNAP47C; C-terminal SNARE motif of SNAP47)

- Review: 20261104T072000Z-cdd-cd15854-record-review
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-11-04T07:10:00Z
- Finished UTC: 2026-11-04T07:20:00Z
- Reviewer: Antigravity (independent)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

CDD:cd15854 (label SNARE_SNAP47C; opening definition phrase 'C-terminal SNARE motif of SNAP47') passes strict LinkML schema validation and represents a valid class-level sequence domain trait (SEQ_DOMAIN on SEQUENCE, parent_traits: [CDD:cl22856], 2 canonical_examples: Rattus norvegicus Snap47 UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570) modeling the C-terminal Qc SNARE motif of synaptosomal-associated protein 47 (SNAP47), a tandem Qb/Qc SNARE protein (PMID:16565078) distinct from its N-terminal Qb SNARE motif sibling CDD:cd15888 (SNARE_SNAP47N) and paralog C-terminal Qc SNARE motif profiles CDD:cd15855 (SNARE_SNAP25C_23C), CDD:cd15856 (SNARE_SNAP29C), CDD:cd15857 (SNARE_SEC9C), CDD:cd15884 (SNARE_SNAP23C), and CDD:cd15885 (SNARE_SNAP25C). However, its upstream CDD-seeded definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane domain, and SNAP47 specifically lacks both a transmembrane domain and the palmitoylated cysteine membrane anchor of SNAP25/SNAP23 (PMID:16565078, PMID:9759094), and CDD:cd15854 currently lacks a literature evidence block — the exact upstream CDD Qb/Qc SNARE template error repaired on sibling profiles CDD:cd15855, CDD:cd15889, CDD:cd15856, and CDD:cd15887 in Cycle 4 Stage 5 (#1217). Preserved as open finding F31 for Cycle 5 Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.

## Scope And Provenance

Full single-record scientific review of CDD:cd15854 covering identity, axis/category placement, hierarchy, tandem-motif relationship to N-terminal Qb sibling CDD:cd15888 and paralog C-terminal Qc SNARE profiles CDD:cd15855, CDD:cd15856, and CDD:cd15884, literature evidence, prose accuracy, and writer ownership.

Selection: Selected from the frozen 12-record Cycle 5 Stage 4 CDD SEQ_DOMAIN sibling inventory as the uncurated C-terminal Qc SNARE motif profile of SNAP47 (SNARE_SNAP47C) exhibiting the upstream CDD Qb/Qc SNARE transmembrane-domain overclaim.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: git_commit at Git base 568e78869fb08b86849d13f6a23b3a32ec27cd08.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| CDD:cd15854 | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml | generated | SNARE_SNAP47C |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML and OAK ontology-binding validation | passed | True | CDD:cd15854 | Record passes closed LinkML schema validation and OAK term-label bindings with 0 errors. |
| Release-pinned UniProt grounding and binding replay | passed | True | CDD:cd15854 | Record carries 2 unpromoted CDD seed examples (Rattus norvegicus Snap47 UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570); 24,026 corpus qualified_record_bindings verify across 14,024 registry proteins with 0 semantic findings. |
| Causal-graph structural and semantic audit | passed | False | CDD:cd15854 | Record has no causal_graphs block (0 graphs, 0 errors); absence is expected for uncurated CDD sequence domain records. |
| Registered write-route audit | passed | True | CDD:cd15854 | 621 scripts examined (52 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses) with 0 unguarded writer findings. |

## Scientific And Domain Assessments

### Class-level C-terminal Qc SNARE motif identity and CDD superfamily hierarchy

identity: supported. Targets: CDD:cd15854.

CDD:cd15854 is a valid class-level sequence domain trait (trait_axis: SEQUENCE, trait_category: SEQ_DOMAIN, label: SNARE_SNAP47C, parent_traits: [CDD:cl22856]) representing the C-terminal Qc SNARE motif of SNAP47, distinct from N-terminal Qb SNARE motif sibling CDD:cd15888 (SNARE_SNAP47N) and paralog C-terminal Qc SNARE motif profiles CDD:cd15855 (SNARE_SNAP25C_23C), CDD:cd15856 (SNARE_SNAP29C), CDD:cd15857 (SNARE_SEC9C), CDD:cd15884 (SNARE_SNAP23C), and CDD:cd15885 (SNARE_SNAP25C).

### Unpromoted CDD seed carrier proteins on CDD:cd15854

grounding: supported. Targets: CDD:cd15854.

CDD:cd15854 carries 2 unpromoted CDD seed examples on disk (Rattus norvegicus Snap47 UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570), both authentic mammalian SNAP47 orthologs characterized in PMID:16565078.

### Upstream CDD false claim that Qb/Qc SNAREs have a transmembrane domain and missing PMID:16565078 evidence block

consistency: concern. Targets: CDD:cd15854.

CDD:cd15854 inherits the false upstream NCBI CDD template sentence 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' even though Qb/Qc SNAREs lack a transmembrane domain and SNAP47 lacks both a transmembrane domain and palmitoylated cysteine membrane anchors (PMID:16565078), and lacks a literature evidence block.

## Findings

### F31: CDD:cd15854 (SNARE_SNAP47C) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP47 lacks both a transmembrane domain and palmitoylated cysteine membrane anchors

major / open / confirmed; issue key: cdd-cd15854-snap47c-transmembrane-domain-overclaim.

In data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml, the domain profile models the C-terminal Qc SNARE motif of SNAP47 (label SNARE_SNAP47C, parent_traits: [CDD:cl22856], canonical_examples: Rattus norvegicus Snap47 UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570). However, its upstream CDD definition states 'Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions with other SNARE proteins, and a transmembrane domain.' Qb/Qc SNAREs lack a transmembrane domain, and SNAP47 specifically lacks both a transmembrane domain and a palmitoylated cysteine cluster (PMID:16565078, PMID:9759094), and CDD:cd15854 currently lacks an evidence block citing PMID:16565078. Preserved open in Stage 4 for Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.

## Recommended Actions And Acceptance Checks

### repair-cd15854-definition-and-evidence-via-cdd-errata

Add an accession-keyed erratum for CDD:cd15854 in scripts/cdd_errata.py and apply it via scripts/repair_cdd_errata.py, replacing the false 'and a transmembrane domain' Qb/Qc SNARE template claim with accurate wording noting that Qb/Qc SNAREs lack a transmembrane domain and that SNAP47 lacks both a transmembrane domain and palmitoylated cysteine membrane anchors, and adding an evidence entry citing PMID:16565078.

- CDD:cd15854 definition states that Qb/Qc SNAREs lack a transmembrane domain and that SNAP47 lacks both a transmembrane domain and palmitoylated cysteine membrane anchors.
- CDD:cd15854 evidence block is populated with PMID:16565078 and a verbatim SNAP47 characterization snippet.
- scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay the erratum idempotently and scripts/validate_strict.py passes with 0 errors.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| ev-cd15854-yaml | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml; identifier, label, definition, definition_source, parent_traits, canonical_examples | partial | CDD:cd15854 (label SNARE_SNAP47C, parent_traits: [CDD:cl22856], SEEDED, 2 canonical_examples: Q6RHT0, Q8R570) models the C-terminal Qc SNARE motif of SNAP47, but falsely asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP47 lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines, and lacks an evidence block. |
| ev-cd15888-sibling | data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml; identifier, label, definition, parent_traits, canonical_examples | supports | N-terminal Qb SNARE motif sibling CDD:cd15888 (label SNARE_SNAP47N, parent_traits: [CDD:cl22856], carrying the same Rattus norvegicus Q6RHT0 and Mus musculus Q8R570 seed examples) confirms that CDD:cd15854 is the distinct C-terminal Qc SNARE motif repeat of SNAP47 and shares the identical upstream CDD Qb/Qc SNARE template error (finding F32). |
| ev-cd15856-paralog | data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml; identifier, label, definition, parent_traits, evidence (PMID:9736707), curation_history (source_erratum_cd15856) | supports | Paralog C-terminal Qc SNARE motif profile CDD:cd15856 (label SNARE_SNAP29C, parent_traits: [CDD:cl22856]) and sibling profiles CDD:cd15855 (SNARE_SNAP25C_23C), CDD:cd15884 (SNARE_SNAP23C), and CDD:cd15885 (SNARE_SNAP25C) were repaired in Cycles 1-4 (#1171, #1188, #1210, #1217) to replace the false Qb/Qc SNARE transmembrane-domain claim with accurate paralog-specific membrane-association wording. |
| ev-pmid-16565078 | https://pubmed.ncbi.nlm.nih.gov/16565078/; PMID:16565078 (Holt et al., 2006, Mol Biol Cell 17:2402-2413) | supports | Primary biochemical characterization of SNAP47 (Holt et al., 2006, Mol Biol Cell 17:2402-2413) establishing that SNAP47 is a ubiquitous Qb/Qc SNARE containing tandem N-terminal Qb and C-terminal Qc SNARE motifs and lacking both a transmembrane domain and a palmitoylated cysteine cluster. |
| ev-cdd-errata-writer | scripts/cdd_errata.py; CDD_ERRATA table (30 entries) and scripts/repair_cdd_errata.py | supports | scripts/cdd_errata.py currently contains 30 accession-keyed entries (including Qb/Qc SNARE motif siblings CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15885, CDD:cd15887, CDD:cd15889, CDD:cd15894, and CDD:cd15895) wired into scripts/seed_cdd.py and scripts/repair_cdd_errata.py, providing the exact registered repair route for adding CDD:cd15854 in Stage 5. |

## Limits And Additional Notes

- This single-record review covers CDD:cd15854 only; the full 12-record frozen Cycle 5 Stage 4 CDD sibling inventory is reviewed in companion category bundle 20261104T072100Z-cdd-cycle5-sibling-domain-cohort-review.
- No edits to data/traits/ were performed in Stage 4; finding F31 is preserved open for Stage 5 grouped remediation.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261104T072000Z-cdd-cd15854-record-review
kind: record
repository: CultureBotAI/proteintraitsmech
title: Single-record scientific review of CDD:cd15854 (SNARE_SNAP47C; C-terminal SNARE
  motif of SNAP47)
started_at: '2026-11-04T07:10:00Z'
finished_at: '2026-11-04T07:20:00Z'
reviewer:
  identity: Antigravity
  kind: agent
  model: Claude Opus 4.6
  independence: independent
  independence_basis: Cycle 5 Stage 4 single-record scientific audit of the committed
    CDD:cd15854 record and its tandem-motif and paralog-subfamily sibling boundary
    context (CDD:cd15888, CDD:cd15855, CDD:cd15856, CDD:cd15884) without modifying
    scientific records.
skill: review-yaml-record
completion: completed
verdict: needs_curation
native_verdict: NEEDS_CURATION
scientific_review: true
summary: 'CDD:cd15854 (label SNARE_SNAP47C; opening definition phrase ''C-terminal
  SNARE motif of SNAP47'') passes strict LinkML schema validation and represents a
  valid class-level sequence domain trait (SEQ_DOMAIN on SEQUENCE, parent_traits:
  [CDD:cl22856], 2 canonical_examples: Rattus norvegicus Snap47 UniProtKB:Q6RHT0 and
  Mus musculus Snap47 UniProtKB:Q8R570) modeling the C-terminal Qc SNARE motif of
  synaptosomal-associated protein 47 (SNAP47), a tandem Qb/Qc SNARE protein (PMID:16565078)
  distinct from its N-terminal Qb SNARE motif sibling CDD:cd15888 (SNARE_SNAP47N)
  and paralog C-terminal Qc SNARE motif profiles CDD:cd15855 (SNARE_SNAP25C_23C),
  CDD:cd15856 (SNARE_SNAP29C), CDD:cd15857 (SNARE_SEC9C), CDD:cd15884 (SNARE_SNAP23C),
  and CDD:cd15885 (SNARE_SNAP25C). However, its upstream CDD-seeded definition states
  ''Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging
  to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
  with other SNARE proteins, and a transmembrane domain.'' Qb/Qc SNAREs lack a transmembrane
  domain, and SNAP47 specifically lacks both a transmembrane domain and the palmitoylated
  cysteine membrane anchor of SNAP25/SNAP23 (PMID:16565078, PMID:9759094), and CDD:cd15854
  currently lacks a literature evidence block — the exact upstream CDD Qb/Qc SNARE
  template error repaired on sibling profiles CDD:cd15855, CDD:cd15889, CDD:cd15856,
  and CDD:cd15887 in Cycle 4 Stage 5 (#1217). Preserved as open finding F31 for Cycle
  5 Stage 5 grouped remediation via scripts/cdd_errata.py and scripts/repair_cdd_errata.py.'
source:
  git_revision: 568e78869fb08b86849d13f6a23b3a32ec27cd08
  state: git_commit
  inputs:
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml
    sha256: e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510
    role: context
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml
    sha256: fd7dc3af4c9120523b0d00017a4c8b631bcd635468f031a23fc9ef480646ab06
    role: context
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
    sha256: c5c11e86520d19d5bd1fccc934f8d80f4fa927e64cbd53e8d0f8e3ffa8315c0a
    role: context
  - path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
    sha256: fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8
    role: target
  - path: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml
    sha256: 5efe3d638e0e2553214d45509996fd6ced8e0cf4d336eb1fee3988ab415a54db
    role: context
  - path: scripts/cdd_errata.py
    sha256: 5528121218bde822769aebbc1a886200dcb6841087d4f445e757624f18cbdb6d
    role: context
  - path: scripts/record_io.py
    sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
    role: context
  - path: scripts/repair_cdd_errata.py
    sha256: 9af19aa9a592e7c34272db5bbe58b5aa5d7e8bbca8b299fd10945d1caeb07c0c
    role: context
  - path: scripts/seed_cdd.py
    sha256: 4fd337316239794623aaa2ad8afed44bb96ead33a1b387921272f26f8731365a
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Full single-record scientific review of CDD:cd15854 covering identity,
    axis/category placement, hierarchy, tandem-motif relationship to N-terminal Qb
    sibling CDD:cd15888 and paralog C-terminal Qc SNARE profiles CDD:cd15855, CDD:cd15856,
    and CDD:cd15884, literature evidence, prose accuracy, and writer ownership.
  selection: Selected from the frozen 12-record Cycle 5 Stage 4 CDD SEQ_DOMAIN sibling
    inventory as the uncurated C-terminal Qc SNARE motif profile of SNAP47 (SNARE_SNAP47C)
    exhibiting the upstream CDD Qb/Qc SNARE transmembrane-domain overclaim.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - CDD:cd15854
targets:
- target_id: CDD:cd15854
  path: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
  label: SNARE_SNAP47C
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
    sha256: fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8
    description: SHA-256 digest of the canonical ProteinTraitRecord YAML file at source.git_revision.
checks:
- check_id: schema
  name: Strict LinkML and OAK ontology-binding validation
  command: .venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Record passes closed LinkML schema validation and OAK term-label bindings
    with 0 errors.
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
- check_id: semantic
  name: Release-pinned UniProt grounding and binding replay
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_failures.tsv
    data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Record carries 2 unpromoted CDD seed examples (Rattus norvegicus Snap47
    UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570); 24,026 corpus qualified_record_bindings
    verify across 14,024 registry proteins with 0 semantic findings.
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
- check_id: graphs
  name: Causal-graph structural and semantic audit
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
  exit_code: 0
  status: passed
  required: false
  summary: Record has no causal_graphs block (0 graphs, 0 errors); absence is expected
    for uncurated CDD sequence domain records.
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
- check_id: writer-audit
  name: Registered write-route audit
  command: .venv/bin/python scripts/audit_writers.py
  exit_code: 0
  status: passed
  required: true
  summary: 621 scripts examined (52 seeders, 9 registered editors, 2 transactional
    promoters, 52 declared bypasses) with 0 unguarded writer findings.
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cdd-errata-writer
evidence:
- evidence_id: ev-cd15854-yaml
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml
  locator: identifier, label, definition, definition_source, parent_traits, canonical_examples
  accessed_at: '2026-11-04T07:12:00Z'
  snapshot_sha256: fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8
  support: partial
  quote: C-terminal SNARE motif of SNAP47. C-terminal SNARE motif of SNAP47, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. Qb/Qc SNAREs consist of 2 coiled-coil helices (called
    SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup),
    which mediate the interactions with other SNARE proteins, and a transmembrane
    domain. In general, the SNARE complex mediates membrane fusion, important for
    trafficking of newly synthesized proteins, recycling of pre-existing proteins
    and organelle formation. SNARE proteins are classified into four groups, Qa-,
    Qb-, Qc- and R-SNAREs, depending on whether the residue in the hydrophilic center
    layer of the four-helical bundle is a glutamine (Q) or arginine (R). Qa-, as well
    as Qb- and Qc-SNAREs, are localized to target organelle membranes, while R-SNARE
    is localized to vesicle membranes. They form unique complexes consisting of one
    member of each subgroup, that mediate fusion between a specific type of vesicles
    and their target organelle. Their SNARE motifs form twisted and parallel heterotetrameric
    helix bundles. Other members of the Qb/Qc SNAREs are SNAP23, SNAP25, SNAP29 and
    SEC9
  summary: 'CDD:cd15854 (label SNARE_SNAP47C, parent_traits: [CDD:cl22856], SEEDED,
    2 canonical_examples: Q6RHT0, Q8R570) models the C-terminal Qc SNARE motif of
    SNAP47, but falsely asserts that Qb/Qc SNAREs have a transmembrane domain whereas
    SNAP47 lacks both a transmembrane domain and palmitoylated membrane-anchoring
    cysteines, and lacks an evidence block.'
- evidence_id: ev-cd15888-sibling
  kind: record_content
  reference: data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml
  locator: identifier, label, definition, parent_traits, canonical_examples
  accessed_at: '2026-11-04T07:12:00Z'
  snapshot_sha256: 5efe3d638e0e2553214d45509996fd6ced8e0cf4d336eb1fee3988ab415a54db
  support: supports
  quote: N-terminal SNARE motif of SNAP47. N-terminal SNARE motif of SNAP47, a member
    of the Qb/Qc subfamily of SNARE (soluble N-ethylmaleimide-sensitive factor attachment
    protein receptor) proteins. Qb/Qc SNAREs consist of 2 coiled-coil helices (called
    SNARE motifs, one belonging to the Qb subgroup and one belonging to the Qc subgroup),
    which mediate the interactions with other SNARE proteins, and a transmembrane
    domain.
  summary: 'N-terminal Qb SNARE motif sibling CDD:cd15888 (label SNARE_SNAP47N, parent_traits:
    [CDD:cl22856], carrying the same Rattus norvegicus Q6RHT0 and Mus musculus Q8R570
    seed examples) confirms that CDD:cd15854 is the distinct C-terminal Qc SNARE motif
    repeat of SNAP47 and shares the identical upstream CDD Qb/Qc SNARE template error
    (finding F32).'
- evidence_id: ev-cd15856-paralog
  kind: record_content
  reference: data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml
  locator: identifier, label, definition, parent_traits, evidence (PMID:9736707),
    curation_history (source_erratum_cd15856)
  accessed_at: '2026-11-04T07:12:00Z'
  snapshot_sha256: c5c11e86520d19d5bd1fccc934f8d80f4fa927e64cbd53e8d0f8e3ffa8315c0a
  support: supports
  quote: Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging
    to the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and lack a transmembrane domain; unlike SNAP25 and
    SNAP23, SNAP29 also lacks palmitoylated cysteine membrane anchors and associates
    with membranes via protein-protein interactions with syntaxins and other trafficking
    factors.
  summary: 'Paralog C-terminal Qc SNARE motif profile CDD:cd15856 (label SNARE_SNAP29C,
    parent_traits: [CDD:cl22856]) and sibling profiles CDD:cd15855 (SNARE_SNAP25C_23C),
    CDD:cd15884 (SNARE_SNAP23C), and CDD:cd15885 (SNARE_SNAP25C) were repaired in
    Cycles 1-4 (#1171, #1188, #1210, #1217) to replace the false Qb/Qc SNARE transmembrane-domain
    claim with accurate paralog-specific membrane-association wording.'
- evidence_id: ev-pmid-16565078
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/16565078/
  locator: PMID:16565078 (Holt et al., 2006, Mol Biol Cell 17:2402-2413)
  accessed_at: '2026-11-04T07:13:00Z'
  support: supports
  quote: Here we report the characterization of a novel SNAP-25-related protein, termed
    SNAP-47, that contains two SNARE motifs separated by a long linker region and
    lacks a transmembrane domain or a cysteine cluster for palmitoylation.
  summary: Primary biochemical characterization of SNAP47 (Holt et al., 2006, Mol
    Biol Cell 17:2402-2413) establishing that SNAP47 is a ubiquitous Qb/Qc SNARE containing
    tandem N-terminal Qb and C-terminal Qc SNARE motifs and lacking both a transmembrane
    domain and a palmitoylated cysteine cluster.
- evidence_id: ev-cdd-errata-writer
  kind: record_content
  reference: scripts/cdd_errata.py
  locator: CDD_ERRATA table (30 entries) and scripts/repair_cdd_errata.py
  accessed_at: '2026-11-04T07:13:00Z'
  snapshot_sha256: 5528121218bde822769aebbc1a886200dcb6841087d4f445e757624f18cbdb6d
  support: supports
  summary: scripts/cdd_errata.py currently contains 30 accession-keyed entries (including
    Qb/Qc SNARE motif siblings CDD:cd15855, CDD:cd15856, CDD:cd15884, CDD:cd15885,
    CDD:cd15887, CDD:cd15889, CDD:cd15894, and CDD:cd15895) wired into scripts/seed_cdd.py
    and scripts/repair_cdd_errata.py, providing the exact registered repair route
    for adding CDD:cd15854 in Stage 5.
assessments:
- assessment_id: identity-and-hierarchy
  area: identity
  topic: Class-level C-terminal Qc SNARE motif identity and CDD superfamily hierarchy
  outcome: supported
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
  - ev-cd15888-sibling
  - ev-cd15856-paralog
  summary: 'CDD:cd15854 is a valid class-level sequence domain trait (trait_axis:
    SEQUENCE, trait_category: SEQ_DOMAIN, label: SNARE_SNAP47C, parent_traits: [CDD:cl22856])
    representing the C-terminal Qc SNARE motif of SNAP47, distinct from N-terminal
    Qb SNARE motif sibling CDD:cd15888 (SNARE_SNAP47N) and paralog C-terminal Qc SNARE
    motif profiles CDD:cd15855 (SNARE_SNAP25C_23C), CDD:cd15856 (SNARE_SNAP29C), CDD:cd15857
    (SNARE_SEC9C), CDD:cd15884 (SNARE_SNAP23C), and CDD:cd15885 (SNARE_SNAP25C).'
- assessment_id: grounding-and-carriers
  area: grounding
  topic: Unpromoted CDD seed carrier proteins on CDD:cd15854
  outcome: supported
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
  - ev-pmid-16565078
  summary: CDD:cd15854 carries 2 unpromoted CDD seed examples on disk (Rattus norvegicus
    Snap47 UniProtKB:Q6RHT0 and Mus musculus Snap47 UniProtKB:Q8R570), both authentic
    mammalian SNAP47 orthologs characterized in PMID:16565078.
- assessment_id: definition-transmembrane-domain-overclaim
  area: consistency
  topic: Upstream CDD false claim that Qb/Qc SNAREs have a transmembrane domain and
    missing PMID:16565078 evidence block
  outcome: concern
  target_ids:
  - CDD:cd15854
  evidence_ids:
  - ev-cd15854-yaml
  - ev-cd15888-sibling
  - ev-cd15856-paralog
  - ev-pmid-16565078
  - ev-cdd-errata-writer
  summary: CDD:cd15854 inherits the false upstream NCBI CDD template sentence 'Qb/Qc
    SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one belonging to
    the Qb subgroup and one belonging to the Qc subgroup), which mediate the interactions
    with other SNARE proteins, and a transmembrane domain.' even though Qb/Qc SNAREs
    lack a transmembrane domain and SNAP47 lacks both a transmembrane domain and palmitoylated
    cysteine membrane anchors (PMID:16565078), and lacks a literature evidence block.
findings:
- finding_id: F31
  issue_key: cdd-cd15854-snap47c-transmembrane-domain-overclaim
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: CDD:cd15854 (SNARE_SNAP47C) asserts that Qb/Qc SNAREs have a transmembrane
    domain whereas SNAP47 lacks both a transmembrane domain and palmitoylated cysteine
    membrane anchors
  description: 'In data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml,
    the domain profile models the C-terminal Qc SNARE motif of SNAP47 (label SNARE_SNAP47C,
    parent_traits: [CDD:cl22856], canonical_examples: Rattus norvegicus Snap47 UniProtKB:Q6RHT0
    and Mus musculus Snap47 UniProtKB:Q8R570). However, its upstream CDD definition
    states ''Qb/Qc SNAREs consist of 2 coiled-coil helices (called SNARE motifs, one
    belonging to the Qb subgroup and one belonging to the Qc subgroup), which mediate
    the interactions with other SNARE proteins, and a transmembrane domain.'' Qb/Qc
    SNAREs lack a transmembrane domain, and SNAP47 specifically lacks both a transmembrane
    domain and a palmitoylated cysteine cluster (PMID:16565078, PMID:9759094), and
    CDD:cd15854 currently lacks an evidence block citing PMID:16565078. Preserved
    open in Stage 4 for Stage 5 grouped remediation via scripts/cdd_errata.py and
    scripts/repair_cdd_errata.py.'
  target_ids:
  - CDD:cd15854
  field_paths:
  - data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml#/definition
  evidence_ids:
  - ev-cd15854-yaml
  - ev-cd15888-sibling
  - ev-cd15856-paralog
  - ev-pmid-16565078
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
- action_id: repair-cd15854-definition-and-evidence-via-cdd-errata
  description: Add an accession-keyed erratum for CDD:cd15854 in scripts/cdd_errata.py
    and apply it via scripts/repair_cdd_errata.py, replacing the false 'and a transmembrane
    domain' Qb/Qc SNARE template claim with accurate wording noting that Qb/Qc SNAREs
    lack a transmembrane domain and that SNAP47 lacks both a transmembrane domain
    and palmitoylated cysteine membrane anchors, and adding an evidence entry citing
    PMID:16565078.
  finding_ids:
  - F31
  target_ids:
  - CDD:cd15854
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
  - CDD:cd15854 definition states that Qb/Qc SNAREs lack a transmembrane domain and
    that SNAP47 lacks both a transmembrane domain and palmitoylated cysteine membrane
    anchors.
  - CDD:cd15854 evidence block is populated with PMID:16565078 and a verbatim SNAP47
    characterization snippet.
  - scripts/seed_cdd.py and scripts/repair_cdd_errata.py replay the erratum idempotently
    and scripts/validate_strict.py passes with 0 errors.
limitations:
- This single-record review covers CDD:cd15854 only; the full 12-record frozen Cycle
  5 Stage 4 CDD sibling inventory is reviewed in companion category bundle 20261104T072100Z-cdd-cycle5-sibling-domain-cohort-review.
- No edits to data/traits/ were performed in Stage 4; finding F31 is preserved open
  for Stage 5 grouped remediation.
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/605
```
