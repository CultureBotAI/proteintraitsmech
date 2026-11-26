# Review of cloud protein

- Review: 20261021T064745Z-cloud-protein
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T06:47:19Z
- Finished UTC: 2026-10-21T06:47:45Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

The cloud-protein record coherently represents a Roary-style rare-frequency class: prevalence below 15 percent. The method explicitly supplies the exclusive upper bound. Its generic taxon scope is intentional, and it is not interchangeable with a statistically inferred PPanGGOLiN cloud partition.

## Scope And Provenance

Field-by-field review of one complete ProteinTraitRecord, including identity, source support, placement, hierarchy, representations, examples, graph applicability, completeness and audit status.

Selection: Path-order unreviewed record 4 of the batch. Initial ignore-independent data/traits/**/*.yaml inventory contained 429359 records; scripts/record_review.py list validated 1 record path as already targeted, leaving 429358. Snapshot-row context paths were not counted. This review covers exactly this target, not the whole queue.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:EVO_PANGENOME_CLOUD | data/traits/evolution/pangenome/cloud-protein.yaml | generated | cloud protein |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:EVO_PANGENOME_CLOUD | One record checked in closed mode. |
| Closed schema and UniProt semantics | passed | True | proteintraitsmech:EVO_PANGENOME_CLOUD | Target checked together with the repository grounding registry integrity; no qualification inferred. |
| Causal graph integrity | passed | True | proteintraitsmech:EVO_PANGENOME_CLOUD | Target inspected for graphs; zero graphs is not evidence of a mechanism. |
| Existing curation history validity | passed | True | proteintraitsmech:EVO_PANGENOME_CLOUD | Full history recipe completed: No issues found. Presence of a per-record history entry is advisory. This review adds no curation event. |
| Structured expression-module adapter applicability | not_applicable | False | proteintraitsmech:EVO_PANGENOME_CLOUD | The generic class identifies no organism, gene, locus or dataset for iModulonDB; module membership would not establish its class definition. |
| External and causal-node reference applicability | not_applicable | False | proteintraitsmech:EVO_PANGENOME_CLOUD | The complete target asserts no external accession, DOI/PMID, ontology CURIE value, parent relation or causal-node grounding. No applicable term or internal-node assertion exists. Generic mention of NCBITaxon is not a taxon identifier. |

## Scientific And Domain Assessments

### Class-level identity and synonyms

identity: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

The complete EVO_PANGENOME_CLOUD record denotes a generic low-frequency protein-family presence class, with cloud gene and rare accessory protein aliases under its declared pangenome convention.

### Representation-based evolutionary placement

schema: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

The defining variable is evolutionary distribution or conservation, so EVOLUTION and the declared schema category are appropriate. This is a class, not an individual protein instance.

### Definition and nearest source support

evidence: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

The qualitative rare-accessory definition is consistent with min_prevalence 0.0, max_prevalence 0.15 and the explicit cloud &lt;15% method. The pinned official Roary summary fixture supports that convention.

### Metric, method and scope completeness

representation: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

Presence-breadth and a named Roary-style method are explicit. Read the numeric bounds with the method text: 0 &lt;= prevalence &lt; 0.15, not an inclusive 15% cloud assignment. A zero lower boundary is a band convention, not an assertion that an observed pangenome family occurs in no genomes.

### Hierarchy and equivalence boundaries

scope: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

No parents or equivalence edges are asserted. Cloud membership depends on the selected genome set and gene-family calling. No automatic equivalence to the PPanGGOLiN statistical cloud is justified merely by the shared name.

### Source ownership, historical license and scientific status

provenance: supported. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

The definition is identified as curator synthesis; SEEDED status makes no human-review claim. Historical CC0 is explicitly preserved. No native status, record, generator, license or history event was changed.

### Examples, molecular representations, chemistry, mechanisms and discussions

completeness: not_applicable. Targets: proteintraitsmech:EVO_PANGENOME_CLOUD.

The complete target contains no individual protein example, residue/sequence representation, chemistry/function claim, causal graph, discussion or dataset. These are optional for the generic distribution class; their omission does not by itself require curation.

## Findings

No findings recorded within this review's declared scope.

## Recommended Actions And Acceptance Checks

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/evolution/pangenome/cloud-protein.yaml; Entire YAML record | supports | The complete EVO_PANGENOME_CLOUD record denotes a generic low-frequency protein-family presence class, with cloud gene and rare accessory protein aliases under its declared pangenome convention. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord, EvolutionaryScope and TraitCategoryEnum | supports | The schema places distribution/conservation classes on EVOLUTION with EVO_CONSERVATION or EVO_PANGENOME. EvolutionaryScope explicitly permits an unfilled taxon_scope on a generic class; metric and method distinguish different meanings. |
| owner | scripts/seed_evolution.py; TERMS, SCOPE, record(), main() | supports | scripts/seed_evolution.py owns the exact identifier, label, definition, synonyms and evolutionary_scope through TERMS and SCOPE; the source is curated_evolution in download.yaml. Existing records are skipped unless forced. |
| license-policy | conf/landing_sources.json; curated integration: evolutionary / pangenome taxonomy; LICENSE final paragraph; download.yaml curated_evolution | supports | The maintained source configuration explicitly retains CC0 for historical evolution records; current project contributions use CC BY 4.0. This explains the record/current-generator license difference. |
| roary | https://raw.githubusercontent.com/sanger-pathogens/Roary/0ed3d0fb8abc4feb7b438158b33fa57812f56fa7/t/data/expected_summary_statistics.txt; Pinned official summary fixture, Cloud genes row | supports | Roary summary assigns cloud to prevalence from zero inclusive to 15 percent exclusive. |
| validation-1 | just validate data/traits/evolution/pangenome/cloud-protein.yaml; Executed 2026-10-21T06:47:21Z through 2026-10-21T06:47:22Z; exit 0 | supports | uv run python scripts/validate_strict.py --workers 1 'data/traits/evolution/pangenome/cloud-protein.yaml'<br>Validating 1 files with 1 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/evolution/conservation/conserved-protein.yaml data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml; Executed 2026-10-21T06:44:51Z through 2026-10-21T06:46:27Z; exit 0 | supports | uv run python scripts/validate_strict.py data/traits/evolution/conservation/conserved-protein.yaml data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml<br>Validating 9 files with 17 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      9<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>uv run python scripts/validate_uniprot_grounding.py data/traits/evolution/conservation/conserved-protein.yaml data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml<br>files scanned: 9<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/evolution/pangenome/cloud-protein.yaml; Executed 2026-10-21T06:47:22Z through 2026-10-21T06:47:22Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings<br><br>uv run python scripts/audit_causal_graphs.py data/traits/evolution/pangenome/cloud-protein.yaml |

## Limits And Additional Notes

- This is a generic class review, not a species-level distribution estimate or qualification of any protein.
- The record cites project curation rather than a versioned primary bibliography. This review records external support without changing the target.
- The comparator is preserved in definition_method prose; numeric bounds alone do not carry endpoint-inclusion flags.
- No source release, taxon panel or orthology cutoff is asserted for an instantiated pangenome.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T064745Z-cloud-protein
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of cloud protein
started_at: '2026-10-21T06:47:19Z'
finished_at: '2026-10-21T06:47:45Z'
reviewer:
  identity: Codex
  kind: agent
  independence: unknown
  independence_basis: Current session assessed unchanged record bytes using local
    rules and inspected external sources. Prior authorship independence is not established;
    this is not human sign-off.
skill: .claude/skills/review-yaml-record/SKILL.md
completion: completed
verdict: pass_with_limitations
scientific_review: true
summary: 'The cloud-protein record coherently represents a Roary-style rare-frequency
  class: prevalence below 15 percent. The method explicitly supplies the exclusive
  upper bound. Its generic taxon scope is intentional, and it is not interchangeable
  with a statistically inferred PPanGGOLiN cloud partition.'
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
  - path: conf/landing_sources.json
    sha256: 679b100d2c6313e2ec78fecbbbea8731595932ec52051d311ad0fc9d5a6b1004
    role: context
  - path: conf/record_review.yaml
    sha256: d3fd2e272546bf2505ded4ef86f7340753c4e422c691bd69f8e79f577b2c5f59
    role: context
  - path: data/traits/evolution/pangenome/cloud-protein.yaml
    sha256: 7eb6cae0ea34079e52e8cd33df3948279f5b83a4a5db34e2d85c23bfe1db80ed
    role: target
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: download.yaml
    sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
    role: context
  - path: justfile
    sha256: 090b16ab565dbc137f589ab913e57efac5cb37bb7511547391267ba6ea96dd5b
    role: context
  - path: research/equivalence-cutoffs-evolution.md
    sha256: b7da60078c50056c0b8866e535a6e34e3f681affdf3ad75312cee8bdd9801bb5
    role: context
  - path: schema/record_review.yaml
    sha256: 229baf9b69118a1fe318e4c31085c0820e4e3d1365e7b04d6ace451b7c35f9bb
    role: context
  - path: scripts/seed_evolution.py
    sha256: 98c34ef72148a445026b5c2faa0cc1b374438d4a1c9f20eef368cb3c0a1ae174
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field review of one complete ProteinTraitRecord, including
    identity, source support, placement, hierarchy, representations, examples, graph
    applicability, completeness and audit status.
  selection: Path-order unreviewed record 4 of the batch. Initial ignore-independent
    data/traits/**/*.yaml inventory contained 429359 records; scripts/record_review.py
    list validated 1 record path as already targeted, leaving 429358. Snapshot-row
    context paths were not counted. This review covers exactly this target, not the
    whole queue.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
targets:
- kind: generated
  label: cloud protein
  owner_paths:
  - path: scripts/seed_evolution.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained class definitions and generator
  path: data/traits/evolution/pangenome/cloud-protein.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:EVO_PANGENOME_CLOUD
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/evolution/pangenome/cloud-protein.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One record checked in closed mode.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and UniProt semantics
  command: just validate-all data/traits/evolution/conservation/conserved-protein.yaml
    data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml
    data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml
    data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml
    data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Target checked together with the repository grounding registry integrity;
    no qualification inferred.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/evolution/pangenome/cloud-protein.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Target inspected for graphs; zero graphs is not evidence of a mechanism.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
  evidence_ids:
  - validation-3
- check_id: history
  name: Existing curation history validity
  command: UV_CACHE_DIR=/private/tmp/ptm-record-reviews-20261021/uv-cache UV_NO_SYNC=1
    just validate-history
  exit_code: 0
  status: passed
  required: true
  summary: 'Full history recipe completed: No issues found. Presence of a per-record
    history entry is advisory. This review adds no curation event.'
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- check_id: structured-adapter
  name: Structured expression-module adapter applicability
  status: not_applicable
  required: false
  summary: The generic class identifies no organism, gene, locus or dataset for iModulonDB;
    module membership would not establish its class definition.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- check_id: references
  name: External and causal-node reference applicability
  status: not_applicable
  required: false
  summary: The complete target asserts no external accession, DOI/PMID, ontology CURIE
    value, parent relation or causal-node grounding. No applicable term or internal-node
    assertion exists. Generic mention of NCBITaxon is not a taxon identifier.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/evolution/pangenome/cloud-protein.yaml
  locator: Entire YAML record
  accessed_at: '2026-10-21T06:47:19Z'
  support: supports
  snapshot_sha256: 7eb6cae0ea34079e52e8cd33df3948279f5b83a4a5db34e2d85c23bfe1db80ed
  summary: The complete EVO_PANGENOME_CLOUD record denotes a generic low-frequency
    protein-family presence class, with cloud gene and rare accessory protein aliases
    under its declared pangenome convention.
- evidence_id: schema
  kind: authority
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord, EvolutionaryScope and TraitCategoryEnum
  accessed_at: '2026-10-21T06:47:19Z'
  support: supports
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  summary: The schema places distribution/conservation classes on EVOLUTION with EVO_CONSERVATION
    or EVO_PANGENOME. EvolutionaryScope explicitly permits an unfilled taxon_scope
    on a generic class; metric and method distinguish different meanings.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_evolution.py
  locator: TERMS, SCOPE, record(), main()
  accessed_at: '2026-10-21T06:47:19Z'
  support: supports
  snapshot_sha256: 98c34ef72148a445026b5c2faa0cc1b374438d4a1c9f20eef368cb3c0a1ae174
  summary: scripts/seed_evolution.py owns the exact identifier, label, definition,
    synonyms and evolutionary_scope through TERMS and SCOPE; the source is curated_evolution
    in download.yaml. Existing records are skipped unless forced.
- evidence_id: license-policy
  kind: authority
  reference: conf/landing_sources.json
  locator: 'curated integration: evolutionary / pangenome taxonomy; LICENSE final
    paragraph; download.yaml curated_evolution'
  accessed_at: '2026-10-21T06:47:45Z'
  support: supports
  summary: The maintained source configuration explicitly retains CC0 for historical
    evolution records; current project contributions use CC BY 4.0. This explains
    the record/current-generator license difference.
- evidence_id: roary
  kind: authority
  reference: https://raw.githubusercontent.com/sanger-pathogens/Roary/0ed3d0fb8abc4feb7b438158b33fa57812f56fa7/t/data/expected_summary_statistics.txt
  locator: Pinned official summary fixture, Cloud genes row
  accessed_at: '2026-10-21T06:41:55Z'
  support: supports
  summary: Roary summary assigns cloud to prevalence from zero inclusive to 15 percent
    exclusive.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/evolution/pangenome/cloud-protein.yaml
  locator: Executed 2026-10-21T06:47:21Z through 2026-10-21T06:47:22Z; exit 0
  accessed_at: '2026-10-21T06:47:22Z'
  support: supports
  summary: "uv run python scripts/validate_strict.py --workers 1 'data/traits/evolution/pangenome/cloud-protein.yaml'\n\
    Validating 1 files with 1 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      1\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/evolution/conservation/conserved-protein.yaml
    data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml
    data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml
    data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml
    data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml
  locator: Executed 2026-10-21T06:44:51Z through 2026-10-21T06:46:27Z; exit 0
  accessed_at: '2026-10-21T06:46:27Z'
  support: supports
  summary: "uv run python scripts/validate_strict.py data/traits/evolution/conservation/conserved-protein.yaml\
    \ data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml\
    \ data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml\
    \ data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml\
    \ data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml\n\
    Validating 9 files with 17 workers; schema=/private/tmp/ptm-record-reviews-20261021/repo/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      9\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    uv run python scripts/validate_uniprot_grounding.py data/traits/evolution/conservation/conserved-protein.yaml\
    \ data/traits/evolution/conservation/variable-protein.yaml data/traits/evolution/pangenome/cloud-protein.yaml\
    \ data/traits/evolution/pangenome/core-genome-protein.yaml data/traits/evolution/pangenome/persistent-genome-protein.yaml\
    \ data/traits/evolution/pangenome/shell-protein.yaml data/traits/evolution/pangenome/singleton-protein.yaml\
    \ data/traits/evolution/pangenome/soft-core-protein.yaml data/traits/function/binding_capacity/uniprot_keywords/2fe-2s-kw-0001.yaml\n\
    files scanned: 9\nregistry proteins: 12700\nsource evidence objects: 21048\nqualified\
    \ record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/evolution/pangenome/cloud-protein.yaml
  locator: Executed 2026-10-21T06:47:22Z through 2026-10-21T06:47:22Z; exit 0
  accessed_at: '2026-10-21T06:47:22Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings


    uv run python scripts/audit_causal_graphs.py data/traits/evolution/pangenome/cloud-protein.yaml'
assessments:
- assessment_id: identity
  area: identity
  topic: Class-level identity and synonyms
  outcome: supported
  evidence_ids:
  - record
  - owner
  summary: The complete EVO_PANGENOME_CLOUD record denotes a generic low-frequency
    protein-family presence class, with cloud gene and rare accessory protein aliases
    under its declared pangenome convention.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: placement
  area: schema
  topic: Representation-based evolutionary placement
  outcome: supported
  evidence_ids:
  - record
  - schema
  summary: The defining variable is evolutionary distribution or conservation, so
    EVOLUTION and the declared schema category are appropriate. This is a class, not
    an individual protein instance.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: definition
  area: evidence
  topic: Definition and nearest source support
  outcome: supported
  evidence_ids:
  - record
  - owner
  - roary
  summary: The qualitative rare-accessory definition is consistent with min_prevalence
    0.0, max_prevalence 0.15 and the explicit cloud <15% method. The pinned official
    Roary summary fixture supports that convention.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: representation
  area: representation
  topic: Metric, method and scope completeness
  outcome: supported
  evidence_ids:
  - record
  - schema
  - roary
  summary: 'Presence-breadth and a named Roary-style method are explicit. Read the
    numeric bounds with the method text: 0 <= prevalence < 0.15, not an inclusive
    15% cloud assignment. A zero lower boundary is a band convention, not an assertion
    that an observed pangenome family occurs in no genomes.'
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: hierarchy
  area: scope
  topic: Hierarchy and equivalence boundaries
  outcome: supported
  evidence_ids:
  - record
  - schema
  - owner
  - roary
  summary: No parents or equivalence edges are asserted. Cloud membership depends
    on the selected genome set and gene-family calling. No automatic equivalence to
    the PPanGGOLiN statistical cloud is justified merely by the shared name.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: provenance-status
  area: provenance
  topic: Source ownership, historical license and scientific status
  outcome: supported
  evidence_ids:
  - record
  - owner
  - license-policy
  summary: The definition is identified as curator synthesis; SEEDED status makes
    no human-review claim. Historical CC0 is explicitly preserved. No native status,
    record, generator, license or history event was changed.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
- assessment_id: optional-fields
  area: completeness
  topic: Examples, molecular representations, chemistry, mechanisms and discussions
  outcome: not_applicable
  evidence_ids:
  - record
  - owner
  summary: The complete target contains no individual protein example, residue/sequence
    representation, chemistry/function claim, causal graph, discussion or dataset.
    These are optional for the generic distribution class; their omission does not
    by itself require curation.
  target_ids:
  - proteintraitsmech:EVO_PANGENOME_CLOUD
findings: []
actions: []
limitations:
- This is a generic class review, not a species-level distribution estimate or qualification
  of any protein.
- The record cites project curation rather than a versioned primary bibliography.
  This review records external support without changing the target.
- The comparator is preserved in definition_method prose; numeric bounds alone do
  not carry endpoint-inclusion flags.
- No source release, taxon panel or orthology cutoff is asserted for an instantiated
  pangenome.
tags:
- unreviewed-path-order
- batch-001
```
