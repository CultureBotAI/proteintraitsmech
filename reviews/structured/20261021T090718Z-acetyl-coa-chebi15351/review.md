# Review of requires acetyl-CoA

- Review: 20261021T090718Z-acetyl-coa-chebi15351
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:01:32Z
- Finished UTC: 2026-10-21T09:07:18Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact acetyl-CoA chemical identity and source coenzyme context are supported. One major grounding finding concerns chemical-entity equality in the protein-requirement xref; no particular protein requirement is qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 010. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618) covers 88 record paths, leaving 429271 before this batch. 10 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml | generated | requires acetyl-CoA |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | Full curation-history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15351 | CHEBI:15351, its chemical parent(s), conjugate and asserted coenzyme relation resolve in official structured sources. The chemical reference is authentic but not equivalent to the local protein-requirement trait. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The neutral acetyl-CoA chemical identity, S-acetyl linkage and specified stereochemistry agree with the source structure and acyl-CoA parent. The tetraanion is a distinct chemical entity. Acyl transfer and allosteric regulatory roles can coexist and do not by themselves establish or refute a protein cofactor requirement.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The chemical clause and coenzyme role are traceable to ChEBI. The requires-label and requirement wrapper are synthesized by seed_chebi_cofactor.py, rather than original ChEBI protein-requirement assertions. The licence is supported, and the exact original seed release remains unknown.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The complete local role-parent chain resolves. The coenzyme parent is broader within the proposed requirement-class representation and the source role ancestry is verified. Chemical is-a, functional-parent and conjugate links are not copied into trait hierarchy; this assessment does not certify the parent’s own equivalence xref or establish protein physiology.

### Representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class. Chemical-role grounding supplies candidate class context; no specific protein member, universal dependence, exact bound protonation state or demonstrated population of the class is claimed.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15351.

CHEBI:15351 denotes the chemical entity while the local identifier denotes a protein functional requirement. The schema reserves xrefs for true source-direct equivalences and provides chemical_participants for typed chemical grounding. Authentic chemical identity does not establish equality to the trait.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-15351.chemical-entity-equivalence.

The local requires-acetyl-CoA trait denotes a protein functional requirement, but its xrefs entry CHEBI:15351 resolves to the chemical entity itself. The source coenzyme role supplies ligand-role context; it does not assert equality between the protein trait and the molecule. The generated equivalence changes denotation despite otherwise supported chemical identity.

## Recommended Actions And Acceptance Checks

### A1

Change build in scripts/seed_chebi_cofactor.py to encode CHEBI:15351 as a chemical_participants entry with role COFACTOR while retaining the local requirement-class identifier, exact chemical scope, source-specific coenzyme context and attribution. Do not recast the trait as a chemical instance or merely relocate the association to mapped_xrefs. State the generator-derived requirement framing explicitly.

- Retain the chemical CURIE as a typed cofactor participant, preserving its exact charge and stereochemical scope without equivalent-trait semantics.
- Retain the proposed requirement class and supported role-parent context; do not merge conjugates, infer protein members or turn chemical functional-parent/is-a relations into protein-trait subclass links.
- A maintained source-transform fixture verifies typed participant output without the equivalent chemical xref; regenerate through the seeder, validate and save a new scoped review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical entity scope and Licensing section | supports | The inspected official ChEBI About page describes chemical entities/roles and its CC BY 4.0 data licence. This supports attribution, not equivalence of a chemical and a protein trait. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS metadata identifies ChEBI comparison ontology version 256. Reused raw response bytes retain the original access time and digest; this is not proof of the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15351/; Complete structured entity, definition, names, chemical data, structure and all outgoing ontology relations | supports | The released three-star entity has formula C23H38N7O17P3S and charge 0, with the S-acetyl thioester and stereochemically specified CoA scaffold. It has roles coenzyme, effector, acyl donor and fundamental metabolite, is an acyl-CoA, has functional parents coenzyme A/acetic acid, and is conjugate acid of acetyl-CoA(4−) CHEBI:57288. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:15351; Inspected source response captured at the recorded UTC time | supports | Official OLS resolves CHEBI:15351 as the matching nonobsolete chemical entity with consistent name, definition, charge, formula and structure; it does not denote the local protein-requirement class. |
| role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Definition and outgoing is-a relations; incoming chemical entities are not a protein-member dataset | supports | CHEBI:23354 defines a dissociable organic donor or acceptor of chemical groups/electrons and has direct is-a parent cofactor CHEBI:23357. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/57288/; Inspected source response captured at the recorded UTC time | supports | The corresponding conjugate independently resolves with distinct charge/formula and reciprocal acid/base relation. It supplies chemical context, not exact identity or equivalent protein requirements. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17984/; Inspected source response captured at the recorded UTC time | supports | The asserted chemical is-a parent CHEBI:17984 resolves with its own definition or structure. Chemical taxonomy and role-derived protein-requirement subclass links are different relationships. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | The cofactor role CHEBI:23357 resolves with biochemical-role parent CHEBI:52206. This establishes the source role context; it does not itself assert a protein requirement. |
| effector-context | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35224/; Inspected source response captured at the recorded UTC time | supports | CHEBI:35224 defines effector binding at an enzyme regulatory site distinct from its substrate-binding catalytic site. Acetyl-CoA explicitly bears this role alongside coenzyme and acyl donor. |
| source-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:36283412%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Title, identifiers and complete indexed abstract; full paper not inspected | supports | PMID:36283412; DOI:10.1016/j.molcel.2022.09.033. The complete indexed primary abstract reports structural/biochemical evidence that acetyl-CoA stabilizes a catalytically competent human pyruvate-carboxylase conformation. This supports a regulatory context without assigning universal dependence, a neutral bound species or a new qualified protein member. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml; Executed 2026-10-21T09:02:08Z through 2026-10-21T09:02:09Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml; Executed 2026-10-21T09:02:02Z through 2026-10-21T09:04:01Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml; Executed 2026-10-21T09:02:09Z through 2026-10-21T09:02:09Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:04:01Z through 2026-10-21T09:04:02Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The primary allostery study was inspected through its complete indexed abstract. It supports regulatory activation in the studied human pyruvate-carboxylase system, not universal dependence or specific selection of the neutral ChEBI form. Substrate use in other reactions does not exclude coenzyme or regulatory roles.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T090718Z-acetyl-coa-chebi15351
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires acetyl-CoA
started_at: '2026-10-21T09:01:32Z'
finished_at: '2026-10-21T09:07:18Z'
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
summary: The exact acetyl-CoA chemical identity and source coenzyme context are supported.
  One major grounding finding concerns chemical-entity equality in the protein-requirement
  xref; no particular protein requirement is qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
    sha256: fe5f5bf97f77b3efa62450404accd7966c5bae0b30bb2e5fea61d5276cd8c175
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
    role: context
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
  selection: Path-order position 8 in batch 010. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618)
    covers 88 record paths, leaving 429271 before this batch. 10 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
targets:
- kind: generated
  label: requires acetyl-CoA
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_15351
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml
    data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml
    data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml
    data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml
    data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: CHEBI:15351, its chemical parent(s), conjugate and asserted coenzyme relation
    resolve in official structured sources. The chemical reference is authentic but
    not equivalent to the local protein-requirement trait.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  evidence_ids:
  - chemical
  - chemical-ontology
  - conjugate
  - role
  - licence
  - current-release
  - chemical-parent-1
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:01:32Z'
  snapshot_sha256: fe5f5bf97f77b3efa62450404accd7966c5bae0b30bb2e5fea61d5276cd8c175
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
  accessed_at: '2026-10-21T09:01:32Z'
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
  accessed_at: '2026-10-21T09:01:32Z'
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
  accessed_at: '2026-10-21T09:01:32Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:01:32Z'
  snapshot_sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
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
  locator: Chemical entity scope and Licensing section
  summary: The inspected official ChEBI About page describes chemical entities/roles
    and its CC BY 4.0 data licence. This supports attribution, not equivalence of
    a chemical and a protein trait.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS metadata identifies ChEBI comparison ontology version 256.
    Reused raw response bytes retain the original access time and digest; this is
    not proof of the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15351/
  accessed_at: '2026-10-21T09:02:19.204442Z'
  snapshot_sha256: ea5d881d8f09e20912c4c9efc26098ada1c482dc3282a04daf3c93dec095004c
  support: supports
  locator: Complete structured entity, definition, names, chemical data, structure
    and all outgoing ontology relations
  summary: The released three-star entity has formula C23H38N7O17P3S and charge 0,
    with the S-acetyl thioester and stereochemically specified CoA scaffold. It has
    roles coenzyme, effector, acyl donor and fundamental metabolite, is an acyl-CoA,
    has functional parents coenzyme A/acetic acid, and is conjugate acid of acetyl-CoA(4−)
    CHEBI:57288.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:15351
  accessed_at: '2026-10-21T09:02:17.718479Z'
  snapshot_sha256: f0287ab2168bfe922a9eaccbcbe0d0af0e5dcf0755e6b46103feb5c34961fb5d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS resolves CHEBI:15351 as the matching nonobsolete chemical
    entity with consistent name, definition, charge, formula and structure; it does
    not denote the local protein-requirement class.
- evidence_id: role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T08:48:04.740723Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Definition and outgoing is-a relations; incoming chemical entities are
    not a protein-member dataset
  summary: CHEBI:23354 defines a dissociable organic donor or acceptor of chemical
    groups/electrons and has direct is-a parent cofactor CHEBI:23357.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/57288/
  accessed_at: '2026-10-21T09:02:57.586539Z'
  snapshot_sha256: e7ff8a403fea284e504c3b7ff1b235b028eccf5e36d891c5b01ca887f295e13f
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The corresponding conjugate independently resolves with distinct charge/formula
    and reciprocal acid/base relation. It supplies chemical context, not exact identity
    or equivalent protein requirements.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17984/
  accessed_at: '2026-10-21T09:02:57.463640Z'
  snapshot_sha256: 92036d6d2d7c408d8bbf57dc54c60017c6b64608bcbd7c8f366e436d5792352d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The asserted chemical is-a parent CHEBI:17984 resolves with its own definition
    or structure. Chemical taxonomy and role-derived protein-requirement subclass
    links are different relationships.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The cofactor role CHEBI:23357 resolves with biochemical-role parent CHEBI:52206.
    This establishes the source role context; it does not itself assert a protein
    requirement.
- evidence_id: effector-context
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35224/
  accessed_at: '2026-10-21T09:02:57.272451Z'
  snapshot_sha256: 93f26912a2ca36e7f5b5fb72f79926e7195639ce218e6704c79541a389d02f93
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:35224 defines effector binding at an enzyme regulatory site distinct
    from its substrate-binding catalytic site. Acetyl-CoA explicitly bears this role
    alongside coenzyme and acyl donor.
- evidence_id: source-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:36283412%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:03:26.746216Z'
  snapshot_sha256: 5a97fe40ee0868b5785b375d39ed9452dff74e124e8018e222b256ebd4c1d174
  support: supports
  locator: Title, identifiers and complete indexed abstract; full paper not inspected
  summary: PMID:36283412; DOI:10.1016/j.molcel.2022.09.033. The complete indexed primary
    abstract reports structural/biochemical evidence that acetyl-CoA stabilizes a
    catalytically competent human pyruvate-carboxylase conformation. This supports
    a regulatory context without assigning universal dependence, a neutral bound species
    or a new qualified protein member.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  locator: Executed 2026-10-21T09:02:08Z through 2026-10-21T09:02:09Z; exit 0
  accessed_at: '2026-10-21T09:02:09Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml
    data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml
    data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml
    data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml
    data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml
  locator: Executed 2026-10-21T09:02:02Z through 2026-10-21T09:04:01Z; exit 0
  accessed_at: '2026-10-21T09:04:01Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml
  locator: Executed 2026-10-21T09:02:09Z through 2026-10-21T09:02:09Z; exit 0
  accessed_at: '2026-10-21T09:02:09Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:04:01Z through 2026-10-21T09:04:02Z; exit 0
  accessed_at: '2026-10-21T09:04:02Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The neutral acetyl-CoA chemical identity, S-acetyl linkage and specified
    stereochemistry agree with the source structure and acyl-CoA parent. The tetraanion
    is a distinct chemical entity. Acyl transfer and allosteric regulatory roles can
    coexist and do not by themselves establish or refute a protein cofactor requirement.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - conjugate
  - effector-context
  - source-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: The chemical clause and coenzyme role are traceable to ChEBI. The requires-label
    and requirement wrapper are synthesized by seed_chebi_cofactor.py, rather than
    original ChEBI protein-requirement assertions. The licence is supported, and the
    exact original seed release remains unknown.
  evidence_ids:
  - record
  - chemical
  - role
  - owner
  - registry
  - licence
  - current-release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-6
  topic: Provenance
- area: consistency
  outcome: supported
  summary: The complete local role-parent chain resolves. The coenzyme parent is broader
    within the proposed requirement-class representation and the source role ancestry
    is verified. Chemical is-a, functional-parent and conjugate links are not copied
    into trait hierarchy; this assessment does not certify the parent’s own equivalence
    xref or establish protein physiology.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: supported
  summary: The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT
    class. Chemical-role grounding supplies candidate class context; no specific protein
    member, universal dependence, exact bound protonation state or demonstrated population
    of the class is claimed.
  evidence_ids:
  - record
  - chemical
  - role
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-8
  topic: Representation
- area: grounding
  outcome: concern
  summary: CHEBI:15351 denotes the chemical entity while the local identifier denotes
    a protein functional requirement. The schema reserves xrefs for true source-direct
    equivalences and provides chemical_participants for typed chemical grounding.
    Authentic chemical identity does not establish equality to the trait.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  assessment_id: assessment-9
  topic: Grounding
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-15351.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-acetyl-CoA trait denotes a protein functional requirement,
    but its xrefs entry CHEBI:15351 resolves to the chemical entity itself. The source
    coenzyme role supplies ligand-role context; it does not assert equality between
    the protein trait and the molecule. The generated equivalence changes denotation
    despite otherwise supported chemical identity.
  evidence_ids:
  - record
  - chemical
  - role
  - schema
  - owner
  - registry
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The machine-readable xref equates distinct chemical-entity
    and protein-requirement denotations; the schema already has typed chemical-participant
    grounding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Change build in scripts/seed_chebi_cofactor.py to encode CHEBI:15351
    as a chemical_participants entry with role COFACTOR while retaining the local
    requirement-class identifier, exact chemical scope, source-specific coenzyme context
    and attribution. Do not recast the trait as a chemical instance or merely relocate
    the association to mapped_xrefs. State the generator-derived requirement framing
    explicitly.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15351
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Retain the chemical CURIE as a typed cofactor participant, preserving its exact
    charge and stereochemical scope without equivalent-trait semantics.
  - Retain the proposed requirement class and supported role-parent context; do not
    merge conjugates, infer protein members or turn chemical functional-parent/is-a
    relations into protein-trait subclass links.
  - A maintained source-transform fixture verifies typed participant output without
    the equivalent chemical xref; regenerate through the seeder, validate and save
    a new scoped review against changed bytes.
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
- The primary allostery study was inspected through its complete indexed abstract.
  It supports regulatory activation in the studied human pyruvate-carboxylase system,
  not universal dependence or specific selection of the neutral ChEBI form. Substrate
  use in other reactions does not exclude coenzyme or regulatory roles.
tags:
- unreviewed-path-order
- batch-010
- chebi-cofactor
```
