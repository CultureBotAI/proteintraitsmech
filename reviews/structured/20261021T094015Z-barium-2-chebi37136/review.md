# Review of requires barium(2+)

- Review: 20261021T094015Z-barium-2-chebi37136
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:33:43Z
- Finished UTC: 2026-10-21T09:40:15Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

barium(2+) chemical identity and source-role context are supported within the stated charge and stereochemical scope. One confirmed major grounding finding concerns the chemical identifier encoded as equivalent to a protein requirement class; no individual protein requirement is qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 012. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5) covers 108 record paths, leaving 429251 before this batch. 12 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml | generated | requires barium(2+) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_37136 | CHEBI:37136 resolves and is nonobsolete in OLS; its asserted structural parents, role context and any cited conjugate/comparison entities were inspected. The local requirement parent was captured and read. Successful source inspection does not make chemical-to-trait equivalence valid. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The local identifier and requires-label denote a proposed reusable protein requirement for barium(2+). CHEBI:37136 identifies its chemical target, not the protein requirement class itself.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

Official ChEBI licensing supports the stated chemical-data licence. Chemical identity and roles are source assertions; the requirement wrapper is synthesized by the maintained seeder and is not a ChEBI-asserted protein class.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The official formula Ba, charge +2 and [Ba+2] structure specify a monatomic barium dication. The source aliases include Ba2+, barium ion and barium(II) cation; the shorter alias Barium does not erase the exact charge. The backend definition is null and OLS description is empty, so the local requirement sentence is generated rather than a source chemical definition. The term is not neutral barium metal, a salt or a specified protein-bound coordination complex.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The direct source cofactor role and local broader cofactor-requirement parent explain the candidate construction. Chemical has-role and structural taxonomy are not directly converted into protein membership or additional parent_traits. This review does not certify the parent record.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

CHEBI:37136 in xrefs denotes a chemical entity while the local class denotes a functional requirement. The schema requires true equivalence in xrefs and provides chemical_participants with role COFACTOR for the chemical association.

### Representation

representation: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The requirement class remains a candidate: a source role does not qualify a particular protein, an exact bound chemical state or obligatory physiological dependence. Typed chemical grounding is needed in place of chemical-to-trait equality.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_37136.

The complete primary abstract describes preparation of Ba2+-containing methanol dehydrogenase from Ca2+-free enzyme obtained from a processing mutant and reports catalytic activity with altered kinetics. This supports an experimentally substituted active-site metal context, not a naturally obligatory barium requirement or universal metal interchangeability. No qualified example is added.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-37136.chemical-entity-equivalence.

The local class denotes a functional requirement for barium(2+), while CHEBI:37136 denotes the chemical entity. The own-source xrefs slot asserts true equivalence, so this generated link equates different kinds of entity. Correct chemical identity and supported source-role context do not remove that mismatch.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to retain CHEBI:37136 as chemical_participants with role COFACTOR and remove it from trait-equivalence xrefs. Preserve the local requirement identity, exact chemical scope and attributed source-role context. Do not substitute a conjugate or stereoisomer, convert chemical taxonomy into parent_traits, or reclassify this own-source association as an external mapped_xrefs product.

- The regenerated target preserves CHEBI:37136 as the exact typed chemical participant with role COFACTOR and retains the proposed protein requirement-class identity.
- No chemical entity is asserted equivalent to the requirement class; chemical charge, stereochemical scope and role provenance remain traceable.
- Test the maintained emitter, regenerate and validate changed target bytes, and obtain a fresh review. Per-protein qualification and obligatory physiological requirement remain separate evidence questions.
- After regeneration run just validate data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml. These are future curation acceptance checks, not evidence that the present scientific defect is fixed.
- For maintained Python/writer changes add and run focused pytest coverage of the changed emitter, then run just lint, just test and just audit-writers. Complete the required full record validation before merge and save a fresh structured scientific review against the changed target bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The inspected official Introduction describes chemical entities; the Licensing section makes website data available under CC BY 4.0. This supports the ChEBI chemical-content licence, not any mismatched protein label. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the OLS comparison release, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_37136; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:37136 to nonobsolete barium(2+). The actual label, description and aliases were inspected; it denotes a chemical entity rather than a protein requirement class. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37136/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response supplies name, definition, formula, charge, structure and outgoing chemical relations. The outgoing source relations directly assert cofactor role. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and ontology_relations.outgoing_relations | supports | The source cofactor role concerns an organic molecule or ion required by an enzyme and is-a biochemical role CHEBI:52206. A chemical-role assertion does not qualify a particular protein requirement. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30412/; name, definition, chemical_data and ontology_relations.outgoing_relations | supports | Official structural parent CHEBI:30412 resolves; its name, definition and outgoing relations were inspected. It classifies the source chemical, not the generated protein trait. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/39125/; name, definition, chemical_data and ontology_relations.outgoing_relations | supports | Official structural parent CHEBI:39125 resolves; its name, definition and outgoing relations were inspected. It classifies the source chemical, not the generated protein trait. |
| chemical-parent-3 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60240/; name, definition, chemical_data and ontology_relations.outgoing_relations | supports | Official structural parent CHEBI:60240 resolves; its name, definition and outgoing relations were inspected. It classifies the source chemical, not the generated protein trait. |
| primary-context | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8809062%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID8809062; complete indexed primary abstract | supports | The complete primary abstract describes preparation of Ba2+-containing methanol dehydrogenase from Ca2+-free enzyme obtained from a processing mutant and reports catalytic activity with altered kinetics. This supports an experimentally substituted active-site metal context, not a naturally obligatory barium requirement or universal metal interchangeability. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml; Executed 2026-10-21T09:34:31Z through 2026-10-21T09:34:39Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml data/traits/function/cofactor_requirement/chebi/biopterin-chebi15373.yaml data/traits/function/cofactor_requirement/chebi/biotin-carboxyl-carrier-protein-chebi61202.yaml data/traits/function/cofactor_requirement/chebi/biotin-chebi15956.yaml data/traits/function/cofactor_requirement/chebi/biotinate-chebi57586.yaml data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml data/traits/function/cofactor_requirement/chebi/bisucaberin-b-chebi209443.yaml data/traits/function/cofactor_requirement/chebi/cadmium-2-chebi48775.yaml data/traits/function/cofactor_requirement/chebi/calcium-2-chebi29108.yaml data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Executed 2026-10-21T09:34:31Z through 2026-10-21T09:37:06Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml; Executed 2026-10-21T09:34:39Z through 2026-10-21T09:34:40Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:37:06Z through 2026-10-21T09:37:08Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMID8809062 was inspected at complete indexed-abstract level, not full-paper level. Its observations are used only within the stated experimental scope and do not establish exact bound protonation or obligatory physiological requirement.
- No pKa, physiological-pH dominance, universal conjugate/stereoisomer interchangeability or bound-state identity is inferred from a short chemical name or source role.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T094015Z-barium-2-chebi37136
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires barium(2+)
started_at: '2026-10-21T09:33:43Z'
finished_at: '2026-10-21T09:40:15Z'
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
summary: barium(2+) chemical identity and source-role context are supported within
  the stated charge and stereochemical scope. One confirmed major grounding finding
  concerns the chemical identifier encoded as equivalent to a protein requirement
  class; no individual protein requirement is qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
    sha256: 3cff583f6fb208eb54000d62706743a74b8ea06511f4d9d887699f9e76501e87
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
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 1 in batch 012. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5)
    covers 108 record paths, leaving 429251 before this batch. 12 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
targets:
- kind: generated
  label: requires barium(2+)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_37136
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
    data/traits/function/cofactor_requirement/chebi/biopterin-chebi15373.yaml data/traits/function/cofactor_requirement/chebi/biotin-carboxyl-carrier-protein-chebi61202.yaml
    data/traits/function/cofactor_requirement/chebi/biotin-chebi15956.yaml data/traits/function/cofactor_requirement/chebi/biotinate-chebi57586.yaml
    data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
    data/traits/function/cofactor_requirement/chebi/bisucaberin-b-chebi209443.yaml
    data/traits/function/cofactor_requirement/chebi/cadmium-2-chebi48775.yaml data/traits/function/cofactor_requirement/chebi/calcium-2-chebi29108.yaml
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:37136 resolves and is nonobsolete in OLS; its asserted structural
    parents, role context and any cited conjugate/comparison entities were inspected.
    The local requirement parent was captured and read. Successful source inspection
    does not make chemical-to-trait equivalence valid.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - chemical-parent-1
  - chemical-parent-2
  - chemical-parent-3
  - primary-context
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:33:43Z'
  snapshot_sha256: 3cff583f6fb208eb54000d62706743a74b8ea06511f4d9d887699f9e76501e87
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
  accessed_at: '2026-10-21T09:33:43Z'
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
  accessed_at: '2026-10-21T09:33:43Z'
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
  accessed_at: '2026-10-21T09:33:43Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:33:43Z'
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
  locator: Introduction and Licensing sections
  summary: The inspected official Introduction describes chemical entities; the Licensing
    section makes website data available under CC BY 4.0. This supports the ChEBI
    chemical-content licence, not any mismatched protein label.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the OLS
    comparison release, not a release assignment for live backend responses or the
    original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_37136
  accessed_at: '2026-10-21T09:34:26.766257Z'
  snapshot_sha256: f38f24c8db661d11d401f5e83ad014789e0e7eb4bb0c2f7ec1d58cc07bbfd9ac
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:37136 to nonobsolete barium(2+). The actual label, description
    and aliases were inspected; it denotes a chemical entity rather than a protein
    requirement class.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37136/
  accessed_at: '2026-10-21T09:34:25.760757Z'
  snapshot_sha256: 0ab676c5e7db8905c6c6255f3e4b754f8343108b0332b794b9a91e384c3d0e28
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The complete official response supplies name, definition, formula, charge,
    structure and outgoing chemical relations. The outgoing source relations directly
    assert cofactor role.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and ontology_relations.outgoing_relations
  summary: The source cofactor role concerns an organic molecule or ion required by
    an enzyme and is-a biochemical role CHEBI:52206. A chemical-role assertion does
    not qualify a particular protein requirement.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30412/
  accessed_at: '2026-10-21T09:35:25.317031Z'
  snapshot_sha256: 26ffa576f22e8d1c8951ee196a9d5b77533353a58800e9f7bf77026699d0d428
  support: supports
  locator: name, definition, chemical_data and ontology_relations.outgoing_relations
  summary: Official structural parent CHEBI:30412 resolves; its name, definition and
    outgoing relations were inspected. It classifies the source chemical, not the
    generated protein trait.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/39125/
  accessed_at: '2026-10-21T09:35:25.262951Z'
  snapshot_sha256: 50f237e3b61b50e1ff869e0b8ee5a4151e1604ad76ffd2e1d4beac87dcc52d0b
  support: supports
  locator: name, definition, chemical_data and ontology_relations.outgoing_relations
  summary: Official structural parent CHEBI:39125 resolves; its name, definition and
    outgoing relations were inspected. It classifies the source chemical, not the
    generated protein trait.
- evidence_id: chemical-parent-3
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60240/
  accessed_at: '2026-10-21T09:35:25.276625Z'
  snapshot_sha256: ae17ca03a6f40e7436e6b4bae08e793dc67d910b9b8f29f3b180135dfab4afd9
  support: supports
  locator: name, definition, chemical_data and ontology_relations.outgoing_relations
  summary: Official structural parent CHEBI:60240 resolves; its name, definition and
    outgoing relations were inspected. It classifies the source chemical, not the
    generated protein trait.
- evidence_id: primary-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8809062%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:35:27.256606Z'
  snapshot_sha256: 4afe4195e5d43bac832ffcc7b012c3cfbd6057a7cb9c43098a4a71fb1420c86b
  support: supports
  locator: PMID8809062; complete indexed primary abstract
  summary: The complete primary abstract describes preparation of Ba2+-containing
    methanol dehydrogenase from Ca2+-free enzyme obtained from a processing mutant
    and reports catalytic activity with altered kinetics. This supports an experimentally
    substituted active-site metal context, not a naturally obligatory barium requirement
    or universal metal interchangeability.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  locator: Executed 2026-10-21T09:34:31Z through 2026-10-21T09:34:39Z; exit 0
  accessed_at: '2026-10-21T09:34:39Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
    data/traits/function/cofactor_requirement/chebi/biopterin-chebi15373.yaml data/traits/function/cofactor_requirement/chebi/biotin-carboxyl-carrier-protein-chebi61202.yaml
    data/traits/function/cofactor_requirement/chebi/biotin-chebi15956.yaml data/traits/function/cofactor_requirement/chebi/biotinate-chebi57586.yaml
    data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
    data/traits/function/cofactor_requirement/chebi/bisucaberin-b-chebi209443.yaml
    data/traits/function/cofactor_requirement/chebi/cadmium-2-chebi48775.yaml data/traits/function/cofactor_requirement/chebi/calcium-2-chebi29108.yaml
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  locator: Executed 2026-10-21T09:34:31Z through 2026-10-21T09:37:06Z; exit 0
  accessed_at: '2026-10-21T09:37:06Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml
  locator: Executed 2026-10-21T09:34:39Z through 2026-10-21T09:34:40Z; exit 0
  accessed_at: '2026-10-21T09:34:40Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:37:06Z through 2026-10-21T09:37:08Z; exit 0
  accessed_at: '2026-10-21T09:37:08Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable protein
    requirement for barium(2+). CHEBI:37136 identifies its chemical target, not the
    protein requirement class itself.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: Official ChEBI licensing supports the stated chemical-data licence. Chemical
    identity and roles are source assertions; the requirement wrapper is synthesized
    by the maintained seeder and is not a ChEBI-asserted protein class.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-6
  topic: Provenance
- area: evidence
  outcome: supported
  summary: The official formula Ba, charge +2 and [Ba+2] structure specify a monatomic
    barium dication. The source aliases include Ba2+, barium ion and barium(II) cation;
    the shorter alias Barium does not erase the exact charge. The backend definition
    is null and OLS description is empty, so the local requirement sentence is generated
    rather than a source chemical definition. The term is not neutral barium metal,
    a salt or a specified protein-bound coordination complex.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - chemical-parent-1
  - chemical-parent-2
  - chemical-parent-3
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-7
  topic: Evidence
- area: consistency
  outcome: supported
  summary: The direct source cofactor role and local broader cofactor-requirement
    parent explain the candidate construction. Chemical has-role and structural taxonomy
    are not directly converted into protein membership or additional parent_traits.
    This review does not certify the parent record.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - cofactor-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-8
  topic: Consistency
- area: grounding
  outcome: concern
  summary: CHEBI:37136 in xrefs denotes a chemical entity while the local class denotes
    a functional requirement. The schema requires true equivalence in xrefs and provides
    chemical_participants with role COFACTOR for the chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-9
  topic: Grounding
- area: representation
  outcome: concern
  summary: 'The requirement class remains a candidate: a source role does not qualify
    a particular protein, an exact bound chemical state or obligatory physiological
    dependence. Typed chemical grounding is needed in place of chemical-to-trait equality.'
  evidence_ids:
  - record
  - schema
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-10
  topic: Representation
- area: evidence
  outcome: supported
  summary: The complete primary abstract describes preparation of Ba2+-containing
    methanol dehydrogenase from Ca2+-free enzyme obtained from a processing mutant
    and reports catalytic activity with altered kinetics. This supports an experimentally
    substituted active-site metal context, not a naturally obligatory barium requirement
    or universal metal interchangeability. No qualified example is added.
  evidence_ids:
  - primary-context
  - chemical-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-37136.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local class denotes a functional requirement for barium(2+), while
    CHEBI:37136 denotes the chemical entity. The own-source xrefs slot asserts true
    equivalence, so this generated link equates different kinds of entity. Correct
    chemical identity and supported source-role context do not remove that mismatch.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The maintained generator asserts equality between chemical
    and protein-requirement denotations; the candidate requirement identity remains
    recoverable through typed chemical grounding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to retain CHEBI:37136
    as chemical_participants with role COFACTOR and remove it from trait-equivalence
    xrefs. Preserve the local requirement identity, exact chemical scope and attributed
    source-role context. Do not substitute a conjugate or stereoisomer, convert chemical
    taxonomy into parent_traits, or reclassify this own-source association as an external
    mapped_xrefs product.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_37136
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves CHEBI:37136 as the exact typed chemical participant
    with role COFACTOR and retains the proposed protein requirement-class identity.
  - No chemical entity is asserted equivalent to the requirement class; chemical charge,
    stereochemical scope and role provenance remain traceable.
  - Test the maintained emitter, regenerate and validate changed target bytes, and
    obtain a fresh review. Per-protein qualification and obligatory physiological
    requirement remain separate evidence questions.
  - After regeneration run just validate data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml.
    These are future curation acceptance checks, not evidence that the present scientific
    defect is fixed.
  - For maintained Python/writer changes add and run focused pytest coverage of the
    changed emitter, then run just lint, just test and just audit-writers. Complete
    the required full record validation before merge and save a fresh structured scientific
    review against the changed target bytes.
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
- PMID8809062 was inspected at complete indexed-abstract level, not full-paper level.
  Its observations are used only within the stated experimental scope and do not establish
  exact bound protonation or obligatory physiological requirement.
- No pKa, physiological-pH dominance, universal conjugate/stereoisomer interchangeability
  or bound-state identity is inferred from a short chemical name or source role.
tags:
- unreviewed-path-order
- batch-012
- chebi-cofactor
```
