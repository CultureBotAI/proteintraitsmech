# Review of requires cAMP

- Review: 20261021T094016Z-camp-chebi17489
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:34:10Z
- Finished UTC: 2026-10-21T09:40:16Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Chemical identity and the explicitly attributed alignment provenance are supported. One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs; no protein requirement is qualified. The energy-cofactor scope remains independently unresolved, and one minor finding records a source-inherited repeated word.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 012. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5) covers 108 record paths, leaving 429251 before this batch. 12 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml | generated | requires cAMP |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17489 | CHEBI:17489 and the compared chemical hierarchy resolve in official sources. The MicroGrowAgents provenance is established from the captured local emitter/crosswalk, not a direct ChEBI cofactor assertion; chemical identity does not establish equality to the protein requirement trait. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The maintained alignment emitter owns generated cAMP content; the captured local crosswalk records MicroGrowAgents provenance. No sibling checkout was accessed. The ordinary missing-ID selection must be addressed in any controlled regeneration.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Evidence

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The source chemical identity is established, but the broad energy-cofactor/requirement framing is supplied by the local MicroGrowAgents alignment and has not been independently established for a protein. Current ChEBI direct roles and the signalling abstract do not resolve that exact scope; they do not disprove other cofactor or regulatory roles.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The exact cAMP chemical identity, cyclic-phosphate connectivity and source stereochemistry are supported. The neutral acid and its phosphate-deprotonated monoanion remain distinct chemical representations. The local cyclic_amp identifier and energy_cofactors category are explicitly RELATED_SYNONYM values from the inspected MicroGrowAgents alignment crosswalk, not exact chemical synonyms or independently demonstrated energy-donor functions.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The chemical description is attributable to ChEBI, while the cofactor category, aliases and requirement wrapper are explicitly MicroGrowAgents-aligned generator synthesis. The local crosswalk supports that provenance; it does not recover the sibling source release or establish the biological requirement.

### Consistency

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The generic local cofactor parent resolves and is inserted by the alignment emitter. Its experimental applicability to this proposed cAMP requirement is not independently established; no parent chemical-role equality is certified.

### Representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class. It remains SEEDED; no protein member, exclusive dependence, bound chemical state or experimentally established class population is asserted.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17489.

CHEBI:17489 denotes a chemical entity, while the local identifier denotes a protein requirement for it. The schema requires true equivalence in xrefs and provides chemical_participants for typed chemical grounding.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17489.chemical-entity-equivalence.

The local requires-cAMP trait denotes a protein functional requirement, but CHEBI:17489 in xrefs denotes the chemical entity itself. The curated alignment supplies candidate association context, not equivalence or direct ChEBI cofactor-role support. This machine-readable equality changes denotation despite supported chemical identity.

### F2: Chemical background repeats a word

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17489.duplicated-definition-word.

The background definition repeats having in both the target and current ChEBI source. This is a bounded readability defect, not a change of chemical identity or evidence for an incorrect molecule.

## Recommended Actions And Acceptance Checks

### A1

Update build_aligned and its maintained input/controlled selection route in scripts/seed_cofactor_alignment.py to represent the supported chemical association to CHEBI:17489 through a typed chemical participant rather than equivalence. Preserve the proposed requirement class, neutral chemical scope, explicit MicroGrowAgents attribution and unresolved role-evidence limits; do not assert an independently verified COFACTOR role from the alignment alone. The ordinary --force route does not select this existing ID, so regeneration must explicitly and auditably select it.

- Preserve exact chemical scope and source provenance without asserting chemical-to-trait equivalence or merging distinct chemical states.
- Retain candidate-class status and explicit evidence limits; do not qualify protein members or infer obligatory/exclusive physiological use.
- A maintained source-transform fixture verifies the corrected typed output and the explicit selection of the existing target; regenerate through an audited route, validate, and save a new review against changed bytes.
- A curator must explicitly adjudicate the required ChemicalParticipant.role and its evidence before implementation. Do not select COFACTOR solely from the alignment category; if no existing role represents the supported association, resolve the schema representation before emitting it. Preserve unresolved biological qualification separately.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused source-transform regression fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

### A2

Correct the duplicated word through the maintained alignment source-text handling or an explicit curated override, preserving chemical meaning and ChEBI attribution; retain the original raw source separately.

- The rendered definition contains one having with unchanged adenine and 3-prime,5-prime cyclic nucleotide meaning.
- The maintained transformation/override and audited regeneration explicitly select the existing target; validate and review changed bytes.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused source-transform regression fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Entire target YAML | supports | Complete target YAML inspected: local requirement identifier/label, composite ChEBI and MicroGrowAgents definition attribution, energy-cofactor category wording, two source-labelled RELATED_SYNONYM entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local cofactor parent, chemical xref and ChEBI licence. No optional protein examples, causal graphs or chemical_participants occur in this target. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| owner | scripts/seed_cofactor_alignment.py; Entire alignment emitter, especially load_mg_cofactors, build_aligned and main | supports | build_aligned synthesizes a requirement class from the curated alignment name/category, appends ChEBI chemical text, emits RELATED_SYNONYM source identifiers/category, a generic cofactor parent and chemical xrefs. main selects only IDs missing from the existing set; --force alone does not select this existing record. Future correction needs an audited path that explicitly selects it. |
| crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and exact CHEBI:17489 row | supports | The local CHEBI:17489 row maps to the current requirement identifier with cofactor_name cAMP, MicroGrowAgents ID cyclic_amp and category energy_cofactors. This records alignment provenance; it is not an experimental protein requirement assertion. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical entity scope and Licensing section | supports | Official ChEBI About text establishes chemical-entity/role scope and CC BY4.0 licensing. This supports chemical attribution, not equivalence to a protein trait. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS metadata gives comparison ontology version256. Reused metadata retain original access time and digest; this does not identify the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17489/; Entity identity, full names/definition, formula/charge, default structure and complete outgoing relations | supports | The released entity is neutral 3-prime,5-prime-cyclic AMP, C10H12N5O6P, charge 0, with adenine, stereochemically specified ribose and one cyclic phosphate joining the 3-prime and 5-prime positions. cAMP is an official synonym. The definition repeats the word having. Its complete outgoing role list contains mouse, Escherichia coli and human metabolite roles, without a direct cofactor role. It has adenyl-ribonucleotide and cyclic-purine-nucleotide chemical parents and conjugate base CHEBI:58165. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17489; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identity with matching formula, charge, InChI and available definition. Empty definition is preserved where the source supplies none. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and outgoing role hierarchy | supports | CHEBI:23357 is the chemical cofactor role, with direct is-a parent biochemical role CHEBI:52206. This role supplies candidate context rather than a dataset of demonstrated protein requirements. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/61296/; Inspected source response captured at the recorded UTC time | supports | Asserted chemical parent CHEBI:61296 resolves with its label and outgoing taxonomy. Only available definition/structure fields were inspected; this does not certify all parent prose or translate chemical taxonomy to protein-trait subclass relations. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/19834/; Inspected source response captured at the recorded UTC time | supports | Asserted chemical parent CHEBI:19834 resolves with its label and outgoing taxonomy. Only available definition/structure fields were inspected; this does not certify all parent prose or translate chemical taxonomy to protein-trait subclass relations. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58165/; Inspected source response captured at the recorded UTC time | supports | The official conjugate base has C10H11N5O6P and charge−1, with the free phosphate OH deprotonated while the cyclic linkage and ribose stereochemistry remain. This distinguishes chemical state; the source pH7.3 assertion is not adopted as protein-bound-state evidence. |
| signalling-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18372334%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified identifiers and complete indexed abstract; full paper not inspected | supports | PMID:18372334; DOI:10.1210/en.2007-1508. The complete indexed abstract reports experiments on forskolin stimulation, PKA-dependent phosphorylation and HCN-channel context in mouse nasal-explant GnRH-1 neurons. This is specific signalling context, not evidence for a generic energy-donor role or the exact neutral charge state in a protein. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Executed 2026-10-21T09:35:06Z through 2026-10-21T09:35:08Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/barium-2-chebi37136.yaml data/traits/function/cofactor_requirement/chebi/biopterin-chebi15373.yaml data/traits/function/cofactor_requirement/chebi/biotin-carboxyl-carrier-protein-chebi61202.yaml data/traits/function/cofactor_requirement/chebi/biotin-chebi15956.yaml data/traits/function/cofactor_requirement/chebi/biotinate-chebi57586.yaml data/traits/function/cofactor_requirement/chebi/bis-molybdopterin-tungsten-cofactor-chebi30402.yaml data/traits/function/cofactor_requirement/chebi/bisucaberin-b-chebi209443.yaml data/traits/function/cofactor_requirement/chebi/cadmium-2-chebi48775.yaml data/traits/function/cofactor_requirement/chebi/calcium-2-chebi29108.yaml data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Executed 2026-10-21T09:34:31Z through 2026-10-21T09:37:06Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml; Executed 2026-10-21T09:35:08Z through 2026-10-21T09:35:08Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:37:06Z through 2026-10-21T09:37:08Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The MicroGrowAgents alignment supplies candidate class provenance, not evidence that a particular protein requires cAMP or that ChEBI directly assigns a cofactor role. The exact requirement and energy-cofactor scope remain independently unresolved.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The current ChEBI direct role list does not independently establish the MicroGrowAgents cofactor/energy category. This absence is not proof that cAMP cannot act as a nonconsumed regulator or cofactor. The original sibling reference tables were not accessed; only the captured local crosswalk and maintained alignment emitter were inspected. A source-linked neuronal-signalling abstract provides bounded PKA context, not exact neutral-form dependence or a new qualified protein example.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T094016Z-camp-chebi17489
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires cAMP
started_at: '2026-10-21T09:34:10Z'
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
summary: Chemical identity and the explicitly attributed alignment provenance are
  supported. One confirmed major finding concerns chemical-to-protein-trait equivalence
  in xrefs; no protein requirement is qualified. The energy-cofactor scope remains
  independently unresolved, and one minor finding records a source-inherited repeated
  word.
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
  - path: data/mappings/cofactor_crosswalk.tsv
    sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
    sha256: c5755250b12814705e97a23ed21a42c2a92a11d68917d2cfb0b2b684ee01e784
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
  - path: scripts/seed_cofactor_alignment.py
    sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 10 in batch 012. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
targets:
- kind: generated
  label: requires cAMP
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17489
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:17489 and the compared chemical hierarchy resolve in official sources.
    The MicroGrowAgents provenance is established from the captured local emitter/crosswalk,
    not a direct ChEBI cofactor assertion; chemical identity does not establish equality
    to the protein requirement trait.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - current-release
  - chemical-parent-1
  - chemical-parent-2
  - crosswalk
  - owner
  - conjugate
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: c5755250b12814705e97a23ed21a42c2a92a11d68917d2cfb0b2b684ee01e784
  support: supports
  summary: 'Complete target YAML inspected: local requirement identifier/label, composite
    ChEBI and MicroGrowAgents definition attribution, energy-cofactor category wording,
    two source-labelled RELATED_SYNONYM entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT,
    CLASS/SEEDED status, local cofactor parent, chemical xref and ChEBI licence. No
    optional protein examples, causal graphs or chemical_participants occur in this
    target.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required
    for activity. xrefs asserts true own-source equivalence; chemical_participants
    represents chemical entities with typed roles. parent_traits asserts a broader
    class. Optional examples and causal graphs are not mandatory class representations.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: Entire alignment emitter, especially load_mg_cofactors, build_aligned and
    main
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: build_aligned synthesizes a requirement class from the curated alignment
    name/category, appends ChEBI chemical text, emits RELATED_SYNONYM source identifiers/category,
    a generic cofactor parent and chemical xrefs. main selects only IDs missing from
    the existing set; --force alone does not select this existing record. Future correction
    needs an audited path that explicitly selects it.
- evidence_id: crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and exact CHEBI:17489 row
  accessed_at: '2026-10-21T09:34:10Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The local CHEBI:17489 row maps to the current requirement identifier with
    cofactor_name cAMP, MicroGrowAgents ID cyclic_amp and category energy_cofactors.
    This records alignment provenance; it is not an experimental protein requirement
    assertion.
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17489/
  accessed_at: '2026-10-21T09:34:42.641192Z'
  snapshot_sha256: b0213fc3774034e2ba9acdb6bb1b01b0bd4bd7fde16b2c6b8e989ffdceaecf5d
  support: supports
  locator: Entity identity, full names/definition, formula/charge, default structure
    and complete outgoing relations
  summary: The released entity is neutral 3-prime,5-prime-cyclic AMP, C10H12N5O6P,
    charge 0, with adenine, stereochemically specified ribose and one cyclic phosphate
    joining the 3-prime and 5-prime positions. cAMP is an official synonym. The definition
    repeats the word having. Its complete outgoing role list contains mouse, Escherichia
    coli and human metabolite roles, without a direct cofactor role. It has adenyl-ribonucleotide
    and cyclic-purine-nucleotide chemical parents and conjugate base CHEBI:58165.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17489
  accessed_at: '2026-10-21T09:34:40.491377Z'
  snapshot_sha256: 2cb786ce4a0635b074a4f1e3d463f33ada867e3f184da3b14fcf9c3bb3284e61
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/61296/
  accessed_at: '2026-10-21T09:35:27.272947Z'
  snapshot_sha256: d7bab371341594de6b9edd3fb5df1c52b2e6b8ff337ad6e20f5ac2936a6e1595
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Asserted chemical parent CHEBI:61296 resolves with its label and outgoing
    taxonomy. Only available definition/structure fields were inspected; this does
    not certify all parent prose or translate chemical taxonomy to protein-trait subclass
    relations.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/19834/
  accessed_at: '2026-10-21T09:35:27.397976Z'
  snapshot_sha256: a31b13b7332e7b697ce1e5d60041fd967ce54801bb101fc921b32276cb235c89
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Asserted chemical parent CHEBI:19834 resolves with its label and outgoing
    taxonomy. Only available definition/structure fields were inspected; this does
    not certify all parent prose or translate chemical taxonomy to protein-trait subclass
    relations.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58165/
  accessed_at: '2026-10-21T09:35:27.441194Z'
  snapshot_sha256: a050c7df17003fe66feb60827792728649182f04fe38f6fa9bb7722078b94a58
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The official conjugate base has C10H11N5O6P and charge−1, with the free
    phosphate OH deprotonated while the cyclic linkage and ribose stereochemistry
    remain. This distinguishes chemical state; the source pH7.3 assertion is not adopted
    as protein-bound-state evidence.
- evidence_id: signalling-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18372334%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:35:28.070233Z'
  snapshot_sha256: 71ae00bfeb4c57ee4b850c31933d87a4c011cc4fc7afd1ff46caca4cfcc7457c
  support: supports
  locator: Verified identifiers and complete indexed abstract; full paper not inspected
  summary: PMID:18372334; DOI:10.1210/en.2007-1508. The complete indexed abstract
    reports experiments on forskolin stimulation, PKA-dependent phosphorylation and
    HCN-channel context in mouse nasal-explant GnRH-1 neurons. This is specific signalling
    context, not evidence for a generic energy-donor role or the exact neutral charge
    state in a protein.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  locator: Executed 2026-10-21T09:35:06Z through 2026-10-21T09:35:08Z; exit 0
  accessed_at: '2026-10-21T09:35:08Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml
  locator: Executed 2026-10-21T09:35:08Z through 2026-10-21T09:35:08Z; exit 0
  accessed_at: '2026-10-21T09:35:08Z'
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
  summary: The maintained alignment emitter owns generated cAMP content; the captured
    local crosswalk records MicroGrowAgents provenance. No sibling checkout was accessed.
    The ordinary missing-ID selection must be addressed in any controlled regeneration.
  evidence_ids:
  - owner
  - crosswalk
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-4
  topic: Scope
- area: evidence
  outcome: unknown
  summary: The source chemical identity is established, but the broad energy-cofactor/requirement
    framing is supplied by the local MicroGrowAgents alignment and has not been independently
    established for a protein. Current ChEBI direct roles and the signalling abstract
    do not resolve that exact scope; they do not disprove other cofactor or regulatory
    roles.
  evidence_ids:
  - record
  - chemical
  - crosswalk
  - owner
  - signalling-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-5
  topic: Evidence
- area: identity
  outcome: supported
  summary: The exact cAMP chemical identity, cyclic-phosphate connectivity and source
    stereochemistry are supported. The neutral acid and its phosphate-deprotonated
    monoanion remain distinct chemical representations. The local cyclic_amp identifier
    and energy_cofactors category are explicitly RELATED_SYNONYM values from the inspected
    MicroGrowAgents alignment crosswalk, not exact chemical synonyms or independently
    demonstrated energy-donor functions.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - chemical-parent-1
  - chemical-parent-2
  - conjugate
  - signalling-primary
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-6
  topic: Identity
- area: provenance
  outcome: supported
  summary: The chemical description is attributable to ChEBI, while the cofactor category,
    aliases and requirement wrapper are explicitly MicroGrowAgents-aligned generator
    synthesis. The local crosswalk supports that provenance; it does not recover the
    sibling source release or establish the biological requirement.
  evidence_ids:
  - record
  - chemical
  - owner
  - registry
  - licence
  - current-release
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-7
  topic: Provenance
- area: consistency
  outcome: unknown
  summary: The generic local cofactor parent resolves and is inserted by the alignment
    emitter. Its experimental applicability to this proposed cAMP requirement is not
    independently established; no parent chemical-role equality is certified.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - schema
  - owner
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-8
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-9
  topic: Representation
- area: grounding
  outcome: concern
  summary: CHEBI:17489 denotes a chemical entity, while the local identifier denotes
    a protein requirement for it. The schema requires true equivalence in xrefs and
    provides chemical_participants for typed chemical grounding.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  assessment_id: assessment-10
  topic: Grounding
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17489.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-cAMP trait denotes a protein functional requirement,
    but CHEBI:17489 in xrefs denotes the chemical entity itself. The curated alignment
    supplies candidate association context, not equivalence or direct ChEBI cofactor-role
    support. This machine-readable equality changes denotation despite supported chemical
    identity.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - registry
  - crosswalk
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The xref equates distinct chemical and protein-requirement
    denotations; typed participant grounding exists in the schema.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-17489.duplicated-definition-word
  category: consistency
  severity: minor
  title: Chemical background repeats a word
  description: The background definition repeats having in both the target and current
    ChEBI source. This is a bounded readability defect, not a change of chemical identity
    or evidence for an incorrect molecule.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: A source-inherited repeated word is a minor editorial defect
    with no chemical identity impact.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
actions:
- action_id: A1
  description: Update build_aligned and its maintained input/controlled selection
    route in scripts/seed_cofactor_alignment.py to represent the supported chemical
    association to CHEBI:17489 through a typed chemical participant rather than equivalence.
    Preserve the proposed requirement class, neutral chemical scope, explicit MicroGrowAgents
    attribution and unresolved role-evidence limits; do not assert an independently
    verified COFACTOR role from the alignment alone. The ordinary --force route does
    not select this existing ID, so regeneration must explicitly and auditably select
    it.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - Preserve exact chemical scope and source provenance without asserting chemical-to-trait
    equivalence or merging distinct chemical states.
  - Retain candidate-class status and explicit evidence limits; do not qualify protein
    members or infer obligatory/exclusive physiological use.
  - A maintained source-transform fixture verifies the corrected typed output and
    the explicit selection of the existing target; regenerate through an audited route,
    validate, and save a new review against changed bytes.
  - A curator must explicitly adjudicate the required ChemicalParticipant.role and
    its evidence before implementation. Do not select COFACTOR solely from the alignment
    category; if no existing role represents the supported association, resolve the
    schema representation before emitting it. Preserve unresolved biological qualification
    separately.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused source-transform regression fixture. Then run just validate
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml, just validate-all
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml and just
    audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
- action_id: A2
  description: Correct the duplicated word through the maintained alignment source-text
    handling or an explicit curated override, preserving chemical meaning and ChEBI
    attribution; retain the original raw source separately.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17489
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The rendered definition contains one having with unchanged adenine and 3-prime,5-prime
    cyclic nucleotide meaning.
  - The maintained transformation/override and audited regeneration explicitly select
    the existing target; validate and review changed bytes.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused source-transform regression fixture. Then run just validate
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml, just validate-all
    data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml and just
    audit-graphs data/traits/function/cofactor_requirement/chebi/camp-chebi17489.yaml.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The MicroGrowAgents alignment supplies candidate class provenance, not evidence
  that a particular protein requires cAMP or that ChEBI directly assigns a cofactor
  role. The exact requirement and energy-cofactor scope remain independently unresolved.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The current ChEBI direct role list does not independently establish the MicroGrowAgents
  cofactor/energy category. This absence is not proof that cAMP cannot act as a nonconsumed
  regulator or cofactor. The original sibling reference tables were not accessed;
  only the captured local crosswalk and maintained alignment emitter were inspected.
  A source-linked neuronal-signalling abstract provides bounded PKA context, not exact
  neutral-form dependence or a new qualified protein example.
tags:
- unreviewed-path-order
- batch-012
- chebi-cofactor
```
