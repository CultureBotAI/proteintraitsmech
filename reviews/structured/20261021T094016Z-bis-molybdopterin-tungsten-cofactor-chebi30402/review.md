# Review of requires bis(molybdopterin)tungsten cofactor

- Review: 20261021T094016Z-bis-molybdopterin-tungsten-cofactor-chebi30402
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:33:57Z
- Finished UTC: 2026-10-21T09:40:16Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Chemical identity and the current source cofactor context are supported. One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs; no protein requirement is qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 012. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5) covers 108 record paths, leaving 429251 before this batch. 12 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml | generated | requires bis(molybdopterin)tungsten cofactor |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30402 | CHEBI:30402 and the compared chemical hierarchy resolve in official sources. The direct cofactor source role resolves; chemical identity does not establish equality to the protein requirement trait. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The label and exact referenced chemical scope are supported as the source Mg-containing bis(pterin) tungsten complex. It is not a generic tungsten ion or a guarantee that every tungsten-pterin cofactor has this composition. No absolute stereochemistry, complete protein-bound coordination sphere or redox-state universality is certified.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The chemical description and asserted cofactor role are traceable to ChEBI; the requirement wrapper is generator synthesis. The current role context and licence are supported, while the original seed release remains unknown.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The captured local cofactor requirement parent resolves; current source role ancestry supports its breadth within this proposed representation. Chemical structural taxonomy is not imported as protein-trait subclass assertions, and parent xref correctness is not certified.

### Representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class. It remains SEEDED; no protein member, exclusive dependence, bound chemical state or experimentally established class population is asserted.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30402.

CHEBI:30402 denotes a chemical entity, while the local identifier denotes a protein requirement for it. The schema requires true equivalence in xrefs and provides chemical_participants for typed chemical grounding.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-30402.chemical-entity-equivalence.

The local requires-bis(molybdopterin)tungsten cofactor trait denotes a protein functional requirement, but CHEBI:30402 in xrefs denotes the chemical entity itself. The source chemical-role assertion supplies candidate context, not equivalence between a molecule and its protein requirement. This machine-readable equality changes denotation despite supported chemical identity.

## Recommended Actions And Acceptance Checks

### A1

Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:30402 as a chemical_participants entry with role COFACTOR, retaining the local proposed requirement class, exact source chemical scope, cofactor context and attribution. Do not recast the record as a chemical instance or merely relocate the association to mapped_xrefs.

- Preserve exact chemical scope and source provenance without asserting chemical-to-trait equivalence or merging distinct chemical states.
- Retain candidate-class status and explicit evidence limits; do not qualify protein members or infer obligatory/exclusive physiological use.
- A maintained source-transform fixture verifies the corrected typed output and the explicit selection of the existing target; regenerate through an audited route, validate, and save a new review against changed bytes.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused source-transform regression fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical entity scope and Licensing section | supports | Official ChEBI About text establishes chemical-entity/role scope and CC BY4.0 licensing. This supports chemical attribution, not equivalence to a protein trait. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS metadata gives comparison ontology version256. Reused metadata retain original access time and digest; this does not identify the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30402/; Entity identity, full names/definition, formula/charge, default structure and complete outgoing relations | supports | The released chemical entry has formula C20H20MgN10O12P2S4W and net charge −2. Its source structure includes two pterin dithiolene units coordinating W and a Mg atom associated with the phosphate groups. The source has no prose definition and does not encode stereochemistry in its SMILES/InChI. It has a direct cofactor role and W-molybdopterin-cofactor chemical parent. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:30402; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identity with matching formula, charge, InChI and available definition. Empty definition is preserved where the source supplies none. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and outgoing role hierarchy | supports | CHEBI:23357 is the chemical cofactor role, with direct is-a parent biochemical role CHEBI:52206. This role supplies candidate context rather than a dataset of demonstrated protein requirements. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60215/; Inspected source response captured at the recorded UTC time | supports | Asserted chemical parent CHEBI:60215 resolves with its label and outgoing taxonomy. Only available definition/structure fields were inspected; this does not certify all parent prose or translate chemical taxonomy to protein-trait subclass relations. |
| structure-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7878465%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified identifiers and complete indexed abstract; full paper not inspected | supports | PMID:7878465; DOI:10.1126/science.7878465. The complete indexed abstract reports a 2.3-angstrom P. furiosus AOR crystal structure with two molybdopterin molecules coordinating tungsten through four sulfur ligands per subunit. It does not establish all exact formula/charge details of the chemical entry or generalize to every W enzyme. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml; Executed 2026-10-21T09:34:59Z through 2026-10-21T09:35:01Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml data/traits/function/cofactor_requirement/chebi/biopterin-chebi15373.yaml data/traits/function/cofactor_requirement/chebi/biotin-carboxyl-carrier-protein-chebi61202.yaml data/traits/function/cofactor_requirement/chebi/biotin-chebi15956.yaml data/traits/function/cofactor_requirement/chebi/biotinate-chebi57586.yaml data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml data/traits/function/cofactor_requirement/chebi/bisucaberin-b-chebi209443.yaml data/traits/function/cofactor_requirement/chebi/cadmium-2-chebi48775.yaml data/traits/function/cofactor_requirement/chebi/calcium-2-chebi29108.yaml data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Executed 2026-10-21T09:34:31Z through 2026-10-21T09:37:06Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml; Executed 2026-10-21T09:35:01Z through 2026-10-21T09:35:01Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:37:06Z through 2026-10-21T09:37:08Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The inspected crystal-structure abstract supports two molybdopterin ligands coordinating tungsten through four sulfur ligands in Pyrococcus furiosus AOR. It does not independently establish every atom, charge or stereochemical state of CHEBI:30402 in every protein. The source structure lacks stereochemical specification, which is retained as a limit rather than filled in.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T094016Z-bis-molybdopterin-tungsten-cofactor-chebi30402
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires bis(molybdopterin)tungsten cofactor
started_at: '2026-10-21T09:33:57Z'
finished_at: '2026-10-21T09:40:16Z'
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
summary: Chemical identity and the current source cofactor context are supported.
  One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs;
  no protein requirement is qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
    sha256: 525a4a114fd581cce721272f6673d4b1ea4552ce851f8a64522d407a92ba4c00
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
  selection: Path-order position 6 in batch 012. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
targets:
- kind: generated
  label: requires bis(molybdopterin)tungsten cofactor
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_30402
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:30402 and the compared chemical hierarchy resolve in official sources.
    The direct cofactor source role resolves; chemical identity does not establish
    equality to the protein requirement trait.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - current-release
  - chemical-parent-1
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:33:57Z'
  snapshot_sha256: 525a4a114fd581cce721272f6673d4b1ea4552ce851f8a64522d407a92ba4c00
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
  accessed_at: '2026-10-21T09:33:57Z'
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
  accessed_at: '2026-10-21T09:33:57Z'
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
  accessed_at: '2026-10-21T09:33:57Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:33:57Z'
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
  locator: Chemical entity scope and Licensing section
  summary: Official ChEBI About text establishes chemical-entity/role scope and CC
    BY4.0 licensing. This supports chemical attribution, not equivalence to a protein
    trait.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS metadata gives comparison ontology version256. Reused metadata
    retain original access time and digest; this does not identify the original seed
    release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30402/
  accessed_at: '2026-10-21T09:34:40.491533Z'
  snapshot_sha256: 38a94ea5fce56206f08f9b05434824d3afa1b18e9a8a3b446a1da37a37ae4e51
  support: supports
  locator: Entity identity, full names/definition, formula/charge, default structure
    and complete outgoing relations
  summary: The released chemical entry has formula C20H20MgN10O12P2S4W and net charge
    −2. Its source structure includes two pterin dithiolene units coordinating W and
    a Mg atom associated with the phosphate groups. The source has no prose definition
    and does not encode stereochemistry in its SMILES/InChI. It has a direct cofactor
    role and W-molybdopterin-cofactor chemical parent.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:30402
  accessed_at: '2026-10-21T09:34:40.489446Z'
  snapshot_sha256: e9711d7db04da997d1e04257562337b90f9eca0afd5f89bfb67ca8fa59a5c7bc
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identity with matching formula,
    charge, InChI and available definition. Empty definition is preserved where the
    source supplies none.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and outgoing role hierarchy
  summary: CHEBI:23357 is the chemical cofactor role, with direct is-a parent biochemical
    role CHEBI:52206. This role supplies candidate context rather than a dataset of
    demonstrated protein requirements.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60215/
  accessed_at: '2026-10-21T09:35:25.813803Z'
  snapshot_sha256: 99d61da20563087876614a2d8ec380613963ebccaa04efa46571704127130eba
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Asserted chemical parent CHEBI:60215 resolves with its label and outgoing
    taxonomy. Only available definition/structure fields were inspected; this does
    not certify all parent prose or translate chemical taxonomy to protein-trait subclass
    relations.
- evidence_id: structure-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7878465%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:36:07.411792Z'
  snapshot_sha256: c77098d7dcc03bbbc7bdde6001717df779cd7ee9143f7953dd0618101daf7c95
  support: supports
  locator: Verified identifiers and complete indexed abstract; full paper not inspected
  summary: PMID:7878465; DOI:10.1126/science.7878465. The complete indexed abstract
    reports a 2.3-angstrom P. furiosus AOR crystal structure with two molybdopterin
    molecules coordinating tungsten through four sulfur ligands per subunit. It does
    not establish all exact formula/charge details of the chemical entry or generalize
    to every W enzyme.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  locator: Executed 2026-10-21T09:34:59Z through 2026-10-21T09:35:01Z; exit 0
  accessed_at: '2026-10-21T09:35:01Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
  locator: Executed 2026-10-21T09:35:01Z through 2026-10-21T09:35:01Z; exit 0
  accessed_at: '2026-10-21T09:35:01Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The label and exact referenced chemical scope are supported as the source
    Mg-containing bis(pterin) tungsten complex. It is not a generic tungsten ion or
    a guarantee that every tungsten-pterin cofactor has this composition. No absolute
    stereochemistry, complete protein-bound coordination sphere or redox-state universality
    is certified.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - chemical-parent-1
  - structure-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: The chemical description and asserted cofactor role are traceable to ChEBI;
    the requirement wrapper is generator synthesis. The current role context and licence
    are supported, while the original seed release remains unknown.
  evidence_ids:
  - record
  - chemical
  - owner
  - registry
  - licence
  - current-release
  - cofactor-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-6
  topic: Provenance
- area: consistency
  outcome: supported
  summary: The captured local cofactor requirement parent resolves; current source
    role ancestry supports its breadth within this proposed representation. Chemical
    structural taxonomy is not imported as protein-trait subclass assertions, and
    parent xref correctness is not certified.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-7
  topic: Consistency
- area: representation
  outcome: supported
  summary: The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT
    class. It remains SEEDED; no protein member, exclusive dependence, bound chemical
    state or experimentally established class population is asserted.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-8
  topic: Representation
- area: grounding
  outcome: concern
  summary: CHEBI:30402 denotes a chemical entity, while the local identifier denotes
    a protein requirement for it. The schema requires true equivalence in xrefs and
    provides chemical_participants for typed chemical grounding.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  assessment_id: assessment-9
  topic: Grounding
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-30402.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-bis(molybdopterin)tungsten cofactor trait denotes
    a protein functional requirement, but CHEBI:30402 in xrefs denotes the chemical
    entity itself. The source chemical-role assertion supplies candidate context,
    not equivalence between a molecule and its protein requirement. This machine-readable
    equality changes denotation despite supported chemical identity.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - registry
  - cofactor-role
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The xref equates distinct chemical and protein-requirement
    denotations; typed participant grounding exists in the schema.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:30402
    as a chemical_participants entry with role COFACTOR, retaining the local proposed
    requirement class, exact source chemical scope, cofactor context and attribution.
    Do not recast the record as a chemical instance or merely relocate the association
    to mapped_xrefs.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30402
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Preserve exact chemical scope and source provenance without asserting chemical-to-trait
    equivalence or merging distinct chemical states.
  - Retain candidate-class status and explicit evidence limits; do not qualify protein
    members or infer obligatory/exclusive physiological use.
  - A maintained source-transform fixture verifies the corrected typed output and
    the explicit selection of the existing target; regenerate through an audited route,
    validate, and save a new review against changed bytes.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused source-transform regression fixture. Then run just validate
    data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
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
- The inspected crystal-structure abstract supports two molybdopterin ligands coordinating
  tungsten through four sulfur ligands in Pyrococcus furiosus AOR. It does not independently
  establish every atom, charge or stereochemical state of CHEBI:30402 in every protein.
  The source structure lacks stereochemical specification, which is retained as a
  limit rather than filled in.
tags:
- unreviewed-path-order
- batch-012
- chebi-cofactor
```
