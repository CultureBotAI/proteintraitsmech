# Review of requires 6-decylubiquinone

- Review: 20261021T085404Z-6-decylubiquinone-chebi52020
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T08:46:28Z
- Finished UTC: 2026-10-21T08:54:04Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact 6-decylubiquinone chemical identity and cofactor-role source context are supported. One major grounding finding concerns chemical-entity equality in the protein-requirement xref; no individual protein requirement is established.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 009. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4) covers 78 record paths, leaving 429281 before this batch. 9 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml | generated | requires 6-decylubiquinone |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | Full curation-history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_52020 | CHEBI:52020, its direct chemical parent and cofactor-role relation resolve in official structured sources. The chemical reference is authentic but not equivalent to the local requirement trait. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The neutral substituted para-benzoquinone identity and saturated decyl chain are supported. The source name, substituent description and reindexed IUPAC name describe compatible ring connectivity; no positional-isomer error is established.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The chemical clause and has-role cofactor assertion are traceable to ChEBI; the requires-label and requirement wrapper are synthesized by seed_chebi_cofactor.py. The licence matches the official source. Neither the wrapper nor current ontology version is treated as an original ChEBI protein-requirement assertion.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The local cofactor-requirement parent resolves and is broader under the derived requirement-class model, consistent with this chemical having the cofactor role. Chemical is-a, conjugate and functional-parent links must not be copied directly into trait parents. This does not certify the local parent’s own equivalence xref.

### Representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

The local requires-label denotes a reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class. Source role annotation supplies candidate ligand-role grounding; this assessment asserts no particular protein member, universal dependence, native physiological necessity, or experimentally demonstrated population of the class.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_52020.

CHEBI:52020 denotes a chemical entity, while the local identifier denotes the protein functional requirement for that entity. The schema requires true source-direct equivalence in xrefs and provides chemical_participants for typed cofactor grounding. Source-direct chemical identity is authentic but not trait/chemical equivalence.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-52020.chemical-entity-equivalence.

The local requires-6-decylubiquinone trait is a protein functional requirement, but its xrefs entry CHEBI:52020 resolves to the chemical entity itself. ChEBI has-role cofactor supplies ligand-role context; it does not assert that a protein trait and the molecule are the same class. The generated equality changes denotation despite the otherwise supported chemical identity.

## Recommended Actions And Acceptance Checks

### A1

Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:52020 as a chemical_participants entry with role COFACTOR, retaining the local requirement-class identifier, precise chemical identity, supported role-parent context and source attribution. Do not reclassify the record as a chemical instance or merely move the association to mapped_xrefs; record the generator-derived requirement framing explicitly.

- The chemical CURIE is retained as a typed cofactor participant, with exact charge and stereochemical scope preserved, and is not asserted as an equivalent protein trait.
- The local requirement class and supported broader requirement-parent remain; chemical conjugacy or functional-parent relations are not silently turned into trait equality/subclass assertions.
- A source-transform fixture verifies the typed participant output without an equivalent chemical xref; regenerate through the maintained seeder, validate and save a new scoped review without promoting protein members.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical-entity scope and Licensing section | supports | The inspected official ChEBI About page describes chemical entities and roles and makes its data available under CC BY 4.0; this supports the stated licence without equating chemical entities to protein traits. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS ChEBI ontology metadata reports version 256. This is the comparison ontology version; the backend entity response separately records its own last-modified timestamp and does not establish the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52020/; Complete structured entity: identifier, released status, definition, names, formula, charge, structure and all outgoing ontology relations | supports | The released three-star entity has formula C19H30O4, net charge 0 and a saturated decyl substituent. Its graph has role cofactor, belongs to the 1,4-benzoquinones class, and has functional parent 6-decylubiquinol CHEBI:52021. Source names and structure support decylubiquinone; the hydroquinone is a related reduced chemical, not an equivalent. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:52020; Inspected source response captured at the recorded UTC time | supports | The OLS entity independently resolves CHEBI:52020 with the matching chemical name, definition, chemical annotations and nonobsolete status; it does not denote a protein-requirement trait. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Role definition and outgoing relations; incoming chemical list is not a per-protein requirement dataset | supports | CHEBI:23357 defines a cofactor role for an organic molecule or ion required by an enzyme for activity; its outgoing is-a parent is CHEBI:52206 biochemical role. This supplies role context rather than an asserted class of proteins. |
| chemical-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/132124/; Inspected source response captured at the recorded UTC time | supports | The asserted chemical is-a parent resolves as 1,4-benzoquinones. This chemical taxonomy relation is kept distinct from subclass links among protein-requirement traits. |
| reduced-relative | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52021/; Inspected source response captured at the recorded UTC time | supports | CHEBI:52021 is 6-decylubiquinol, the corresponding reduced hydroquinone. The outgoing functional-parent association in CHEBI:52020 is chemical context, not a requirement-trait subclass/equality. |
| source-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15883782%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Title, identifiers and complete indexed abstract; full paper not inspected | supports | PMID:15883782; DOI:10.1007/s00203-005-0775-8. The complete indexed abstract reports decylubiquinone as an assay electron acceptor for purified Corynebacterium glutamicum succinate:menaquinone oxidoreductase. It supports that experimental use, not obligatory physiological cofactor status or its absence in other contexts. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml; Executed 2026-10-21T08:47:14Z through 2026-10-21T08:47:15Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/binding_capacity/uniprot_keywords/zinc-kw-0862.yaml data/traits/function/cofactor_requirement/chebi/1-4-benzoquinone-chebi16509.yaml data/traits/function/cofactor_requirement/chebi/3-hydroxyechinenone-chebi80214.yaml data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydrobiopterin-chebi15372.yaml data/traits/function/cofactor_requirement/chebi/5-6-7-8-tetrahydropteridine-chebi28889.yaml data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-1-chebi60494.yaml data/traits/function/cofactor_requirement/chebi/5-hydroxybenzimidazolylcob-i-amide-chebi17679.yaml data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-1-chebi58201.yaml data/traits/function/cofactor_requirement/chebi/6-7-dimethyl-8-1-d-ribityl-lumazine-chebi17601.yaml data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml; Executed 2026-10-21T08:46:51Z through 2026-10-21T08:48:29Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml; Executed 2026-10-21T08:47:15Z through 2026-10-21T08:47:15Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T08:48:29Z through 2026-10-21T08:48:30Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The source-linked primary abstract uses decylubiquinone as an assay electron acceptor for succinate:menaquinone oxidoreductase. That use does not establish obligatory physiological requirement or absence of another cofactor role. The related reduced hydroquinone is not a trait parent solely because ChEBI calls it a functional parent.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T085404Z-6-decylubiquinone-chebi52020
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires 6-decylubiquinone
started_at: '2026-10-21T08:46:28Z'
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
verdict: needs_curation
scientific_review: true
summary: The exact 6-decylubiquinone chemical identity and cofactor-role source context
  are supported. One major grounding finding concerns chemical-entity equality in
  the protein-requirement xref; no individual protein requirement is established.
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
  - path: data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
    sha256: a2b3df31031eb0601c686d3512a58138ee9145d48c2fa4c85a010afe5b911acc
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
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
  selection: Path-order position 10 in batch 009. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4) covers 78 record paths,
    leaving 429281 before this batch. 9 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
targets:
- kind: generated
  label: requires 6-decylubiquinone
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_52020
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: CHEBI:52020, its direct chemical parent and cofactor-role relation resolve
    in official structured sources. The chemical reference is authentic but not equivalent
    to the local requirement trait.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  evidence_ids:
  - chemical
  - chemical-ontology
  - chemical-parent
  - cofactor-role
  - licence
  - current-release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T08:46:28Z'
  snapshot_sha256: a2b3df31031eb0601c686d3512a58138ee9145d48c2fa4c85a010afe5b911acc
  support: supports
  summary: Complete YAML inspected, including local protein-requirement identifier
    and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT,
    CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence.
    No optional examples, causal graphs, qualified protein assertions or chemical_participants
    occur in this target YAML.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T08:46:28Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required
    for activity. xrefs asserts true own-source equivalence; chemical_participants
    represents chemical entities with typed roles. parent_traits asserts a broader
    class. Optional examples and causal graphs are not mandatory class representations.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_chebi_cofactor.py
  locator: load_relations, load_names, build, main
  accessed_at: '2026-10-21T08:46:28Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: load_relations selects cofactor-role descendants and molecules with has_role;
    build synthesizes a protein-requirement label/definition, appends chemical source
    text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects
    one role-parent. The source chemical class and the synthesized requirement trait
    have different denotations.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T08:46:28Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T08:46:28Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Chemical-entity scope and Licensing section
  summary: The inspected official ChEBI About page describes chemical entities and
    roles and makes its data available under CC BY 4.0; this supports the stated licence
    without equating chemical entities to protein traits.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:28.461965Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS ChEBI ontology metadata reports version 256. This is the comparison
    ontology version; the backend entity response separately records its own last-modified
    timestamp and does not establish the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52020/
  accessed_at: '2026-10-21T08:47:28.457198Z'
  snapshot_sha256: 4fa63a2846d78877d9a8a8d9dcf730661499c98852b421bd1d5140cf90873363
  support: supports
  locator: 'Complete structured entity: identifier, released status, definition, names,
    formula, charge, structure and all outgoing ontology relations'
  summary: The released three-star entity has formula C19H30O4, net charge 0 and a
    saturated decyl substituent. Its graph has role cofactor, belongs to the 1,4-benzoquinones
    class, and has functional parent 6-decylubiquinol CHEBI:52021. Source names and
    structure support decylubiquinone; the hydroquinone is a related reduced chemical,
    not an equivalent.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:52020
  accessed_at: '2026-10-21T08:47:27.706176Z'
  snapshot_sha256: 39726df0918ea33d338395743da8b38d5a69cbff0703bcd9345fc6c495c26d21
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The OLS entity independently resolves CHEBI:52020 with the matching chemical
    name, definition, chemical annotations and nonobsolete status; it does not denote
    a protein-requirement trait.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Role definition and outgoing relations; incoming chemical list is not a
    per-protein requirement dataset
  summary: CHEBI:23357 defines a cofactor role for an organic molecule or ion required
    by an enzyme for activity; its outgoing is-a parent is CHEBI:52206 biochemical
    role. This supplies role context rather than an asserted class of proteins.
- evidence_id: chemical-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/132124/
  accessed_at: '2026-10-21T08:48:04.983865Z'
  snapshot_sha256: 22eb58b8ba23d0aadc8f0b1ac5802c1f3ec79c46898c571bee8654fcb2b6dc0b
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The asserted chemical is-a parent resolves as 1,4-benzoquinones. This chemical
    taxonomy relation is kept distinct from subclass links among protein-requirement
    traits.
- evidence_id: reduced-relative
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52021/
  accessed_at: '2026-10-21T08:48:05.825942Z'
  snapshot_sha256: e00ba3e53e734b1b8c296ec5eb23cb97ec156e6e6a4d3d057783c591e77c1fce
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:52021 is 6-decylubiquinol, the corresponding reduced hydroquinone.
    The outgoing functional-parent association in CHEBI:52020 is chemical context,
    not a requirement-trait subclass/equality.
- evidence_id: source-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15883782%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T08:48:07.197396Z'
  snapshot_sha256: f18dad10440e38c58d21e53e32fe8eed9bdfee8d30085329c7e814a689c2e9fc
  support: supports
  locator: Title, identifiers and complete indexed abstract; full paper not inspected
  summary: PMID:15883782; DOI:10.1007/s00203-005-0775-8. The complete indexed abstract
    reports decylubiquinone as an assay electron acceptor for purified Corynebacterium
    glutamicum succinate:menaquinone oxidoreductase. It supports that experimental
    use, not obligatory physiological cofactor status or its absence in other contexts.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  locator: Executed 2026-10-21T08:47:14Z through 2026-10-21T08:47:15Z; exit 0
  accessed_at: '2026-10-21T08:47:15Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/6-decylubiquinone-chebi52020.yaml
  locator: Executed 2026-10-21T08:47:15Z through 2026-10-21T08:47:15Z; exit 0
  accessed_at: '2026-10-21T08:47:15Z'
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
  summary: scripts/seed_chebi_cofactor.py owns generated target changes. Its source
    transformation is inspected; no emitted record has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-1
  topic: Ownership
- area: completeness
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable requirement
    class rather than a protein instance. Optional examples, sequence/structure representations
    and mechanisms are not automatically required; none are newly qualified.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The neutral substituted para-benzoquinone identity and saturated decyl
    chain are supported. The source name, substituent description and reindexed IUPAC
    name describe compatible ring connectivity; no positional-isomer error is established.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: The chemical clause and has-role cofactor assertion are traceable to ChEBI;
    the requires-label and requirement wrapper are synthesized by seed_chebi_cofactor.py.
    The licence matches the official source. Neither the wrapper nor current ontology
    version is treated as an original ChEBI protein-requirement assertion.
  evidence_ids:
  - record
  - chemical
  - cofactor-role
  - licence
  - current-release
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-6
  topic: Provenance
- area: consistency
  outcome: supported
  summary: The local cofactor-requirement parent resolves and is broader under the
    derived requirement-class model, consistent with this chemical having the cofactor
    role. Chemical is-a, conjugate and functional-parent links must not be copied
    directly into trait parents. This does not certify the local parent’s own equivalence
    xref.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - chemical-parent
  - cofactor-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: supported
  summary: The local requires-label denotes a reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT
    class. Source role annotation supplies candidate ligand-role grounding; this assessment
    asserts no particular protein member, universal dependence, native physiological
    necessity, or experimentally demonstrated population of the class.
  evidence_ids:
  - record
  - chemical
  - cofactor-role
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-8
  topic: Representation
- area: grounding
  outcome: concern
  summary: CHEBI:52020 denotes a chemical entity, while the local identifier denotes
    the protein functional requirement for that entity. The schema requires true source-direct
    equivalence in xrefs and provides chemical_participants for typed cofactor grounding.
    Source-direct chemical identity is authentic but not trait/chemical equivalence.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  assessment_id: assessment-9
  topic: Grounding
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-52020.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-6-decylubiquinone trait is a protein functional
    requirement, but its xrefs entry CHEBI:52020 resolves to the chemical entity itself.
    ChEBI has-role cofactor supplies ligand-role context; it does not assert that
    a protein trait and the molecule are the same class. The generated equality changes
    denotation despite the otherwise supported chemical identity.
  evidence_ids:
  - record
  - chemical
  - cofactor-role
  - schema
  - owner
  - registry
  certainty: confirmed
  normalization_reason: The machine-readable xref asserts equality across distinct
    chemical-entity and protein-requirement denotations; typed chemical-participant
    grounding already exists in the schema.
  field_paths:
  - xrefs
  - chemical_participants
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:52020
    as a chemical_participants entry with role COFACTOR, retaining the local requirement-class
    identifier, precise chemical identity, supported role-parent context and source
    attribution. Do not reclassify the record as a chemical instance or merely move
    the association to mapped_xrefs; record the generator-derived requirement framing
    explicitly.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_52020
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained source parser, category routing, parent selection and YAML emitter
  acceptance_checks:
  - The chemical CURIE is retained as a typed cofactor participant, with exact charge
    and stereochemical scope preserved, and is not asserted as an equivalent protein
    trait.
  - The local requirement class and supported broader requirement-parent remain; chemical
    conjugacy or functional-parent relations are not silently turned into trait equality/subclass
    assertions.
  - A source-transform fixture verifies the typed participant output without an equivalent
    chemical xref; regenerate through the maintained seeder, validate and save a new
    scoped review without promoting protein members.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that
  a particular protein requires that chemical, that every related protein does, or
  that the chemical is an obligatory physiological cofactor. No such per-protein qualification
  is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The source-linked primary abstract uses decylubiquinone as an assay electron acceptor
  for succinate:menaquinone oxidoreductase. That use does not establish obligatory
  physiological requirement or absence of another cofactor role. The related reduced
  hydroquinone is not a trait parent solely because ChEBI calls it a functional parent.
tags:
- unreviewed-path-order
- batch-009
- chebi-cofactor
```
