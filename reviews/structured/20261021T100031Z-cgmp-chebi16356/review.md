# Review of requires cGMP

- Review: 20261021T100031Z-cgmp-chebi16356
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:51:52Z
- Finished UTC: 2026-10-21T10:00:31Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Chemical identification and explicit alignment provenance are supported, with unresolved protein requirement/energy scope. Two confirmed major findings concern chemical-to-trait equivalence and the incorrect guanidine nucleobase assertion.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 013. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0) covers 118 record paths, leaving 429241 before this batch. 13 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml | generated | requires cGMP |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16356 | CHEBI:16356 and compared source chemical references resolve in official structured responses. Captured alignment provenance, rather than a direct ChEBI cofactor assertion, supplies the candidate cofactor category; guanine/guanidine authorities distinguish the defining-word error. Identifier resolution does not certify every source chemical hierarchy statement or establish equality to the protein requirement trait. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The maintained alignment emitter owns generated cGMP content; the captured crosswalk establishes MicroGrowAgents provenance. No sibling checkout was accessed. Ordinary missing-ID selection must be addressed in controlled regeneration.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Biological requirement and chemical-state evidence

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The MicroGrowAgents alignment supplies the energy-cofactor/requirement framing. Current ChEBI direct roles and the inspected signalling abstract do not independently establish that exact scope for a protein; they also do not exclude other nonconsumed regulatory or cofactor roles.

### Chemical identity and protein requirement scope

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The exact identifier, neutral cyclic-nucleotide connectivity and source ribose stereochemistry support the cGMP chemical identity. Its guanosine name and structure identify a guanine base, contradicting the appended guanidine wording. The local cyclic_gmp and energy_cofactors values are source-labelled RELATED_SYNONYM entries from the MicroGrowAgents alignment, not exact chemical synonyms or independently established energy-donor functions.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

Chemical text is attributable to ChEBI; aliases, energy category and requirement wrapper are explicitly MicroGrowAgents-aligned generator synthesis. Source fidelity does not validate the guanidine assertion. The captured crosswalk does not recover the sibling source release.

### Chemical-role and protein-trait hierarchy

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The generic local cofactor parent resolves and is inserted by the alignment emitter; its applicability to a specific cGMP requirement remains independently unresolved.

### FUNCTION cofactor requirement representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

The requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class that remains SEEDED. No protein member, exclusive dependence or experimentally determined bound charge state is qualified by this review.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16356.

CHEBI:16356 identifies a chemical entity, whereas the local identifier denotes a protein requirement for it. xrefs requires true equivalence; chemical_participants provides typed chemical grounding.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-16356.chemical-entity-equivalence.

The local requires-cGMP trait denotes a protein functional requirement, while CHEBI:16356 in xrefs denotes the chemical entity. The curated alignment provides candidate association context, not equivalence or direct ChEBI cofactor-role evidence. This machine-readable equality changes denotation despite supported chemical identification.

### F2: Definition substitutes guanidine for the guanine nucleobase

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-16356.guanidine-base-definition.

The target and current ChEBI definition call the purine nucleobase guanidine. The same source identifies guanosine and guanyl ribonucleotide, and its structure has the guanine purine ring. Official guanine and guanidine entries confirm distinct identities: guanidine is an acyclic aminocarboxamidine. This is a materially incorrect defining chemical assertion, even though the stable target ID and label still identify cGMP.

## Recommended Actions And Acceptance Checks

### A1

Update build_aligned and its maintained input/controlled selection route in scripts/seed_cofactor_alignment.py to represent the supported chemical association to CHEBI:16356 through a typed chemical participant rather than equivalence. Preserve the proposed requirement class, exact chemical scope, explicit MicroGrowAgents attribution and unresolved role-evidence limits. Do not infer an independently verified COFACTOR role from the alignment category. The ordinary --force route does not select this existing ID, so regeneration must explicitly and auditably select it.

- Preserve exact chemical scope and attribution without chemical-to-trait equality or merging distinct charge, substituent or stereochemical states.
- Retain candidate-class status and limits; do not qualify protein members or infer obligatory/exclusive physiological use.
- A maintained source-transform fixture verifies typed output and audited selection/regeneration of the existing target; capture changed inputs and save a new review.
- A curator must adjudicate the required ChemicalParticipant.role and its evidence before implementation. Do not choose COFACTOR solely from the alignment category; if no enum role represents the supported association, resolve the schema representation before emitting it. Preserve unresolved biological qualification separately.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused source-transform regression fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml. Run full just validate-all before merging record changes, as required by CLAUDE.md. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

### A2

Correct the chemical-background noun to guanine through maintained alignment source-text handling or an explicit curated override. Preserve the cGMP identifier, neutral cyclic-phosphate state, ribose stereochemistry and original source attribution; retain the raw upstream response and the documented correction.

- The rendered definition names guanine, consistent with guanosine and the inspected structure; guanidine is not retained as an exact alternative.
- The correction is routed through the maintained emitter/override with an audited selection of this existing target and a focused regression fixture; source provenance remains explicit.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused source-transform regression fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml. Run full just validate-all before merging record changes, as required by CLAUDE.md. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml; Entire target YAML | supports | Complete target YAML inspected: local requirement identifier/label, composite ChEBI and MicroGrowAgents definition attribution, energy-cofactor wording, two source-labelled RELATED_SYNONYM entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local cofactor parent, chemical xref and stated ChEBI licence. No protein examples, causal graphs or chemical_participants occur. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| owner | scripts/seed_cofactor_alignment.py; Entire alignment emitter, especially load_mg_cofactors, build_aligned and main | supports | build_aligned synthesizes a requirement class from alignment name/category, appends ChEBI chemical text, emits RELATED_SYNONYM source identifiers/category, a generic cofactor parent and chemical xrefs. main selects only missing IDs; --force alone does not select this existing record. Future correction requires an audited route explicitly selecting it. |
| crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and exact CHEBI:16356 row | supports | The exact CHEBI:16356 row maps the current requirement identifier to cGMP, MicroGrowAgents ID cyclic_gmp and energy_cofactors category. This is alignment provenance, not an experimental requirement assertion. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical entity scope and Licensing section | supports | The official About page establishes ChEBI chemical-entity/role scope and CC BY 4.0 licensing, not equivalence to protein traits. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS metadata gives comparison ontology version 256. Reused metadata retain original access time and digest; this does not identify the seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16356/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | The current entity is neutral 3-prime,5-prime-cyclic GMP, C10H12N5O7P, charge 0, with stereochemically specified ribose and a 3-prime,5-prime cyclic phosphate. The IUPAC name is guanosine 3-prime,5-prime-(hydrogen phosphate), and cGMP is a source synonym. Its prose nevertheless names guanidine as the purine nucleobase. The full outgoing role list contains mouse, human, yeast, E. coli and plant metabolite roles, without a direct cofactor role; chemical parents are guanyl ribonucleotide and cyclic purine nucleotide. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16356; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical entity with matching formula, charge and InChI. Its definition matches the inspected ChEBI backend response. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and outgoing role hierarchy | supports | CHEBI:23357 denotes the chemical cofactor role and has direct is-a biochemical role CHEBI:52206. This supplies candidate context, not a set of independently demonstrated protein requirements. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/61295/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | Asserted source chemical parent CHEBI:61295 resolves. Its available definition, formula/charge and outgoing relations were inspected; resolution does not certify chemical-hierarchy correctness or imply protein-trait subclass relations. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/19834/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | Asserted source chemical parent CHEBI:19834 resolves. Its available definition, formula/charge and outgoing relations were inspected; resolution does not certify chemical-hierarchy correctness or imply protein-trait subclass relations. |
| guanine | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16235/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | Guanine is the 2-amino-6-oxopurine nucleobase, C5H5N5O, with a purine-ring structure. This matches the base in the cGMP source structure. |
| guanidine | https://www.ebi.ac.uk/chebi/backend/api/public/compound/42820/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | Guanidine is an aminocarboxamidine, CH5N3, with source SMILES N=C(N)N and no purine ring. It is a distinct chemical entity, not a spelling variant of guanine. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/57746/; Inspected identity, definition/names, formula/charge, default structure and outgoing relations | supports | The conjugate-base entry is C10H11N5O7P, charge minus one. The free phosphate OH is deprotonated while cyclic linkage/ribose stereochemistry remain; its source pH 7.3 assertion is not adopted as bound-state evidence. |
| signalling-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24591051%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified identifiers and complete indexed abstract; full paper not inspected | supports | PMID:24591051; DOI:10.1093/jxb/eru019. The complete indexed abstract reports Arabidopsis auxin-signalling experiments using endogenous cGMP accumulation, the 8-bromo-cGMP analogue and pathway inhibitors; it proposes PKG involvement. This is bounded signalling context, not exact neutral-form binding or energy-donor evidence. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml; Executed 2026-10-21T09:54:15Z through 2026-10-21T09:54:16Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml; Executed 2026-10-21T09:52:28Z through 2026-10-21T09:53:58Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml; Executed 2026-10-21T09:54:16Z through 2026-10-21T09:54:16Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:53:58Z through 2026-10-21T09:54:00Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The MicroGrowAgents alignment supplies candidate class provenance, not evidence that a particular protein requires cGMP or that ChEBI directly assigns a cofactor role. The exact requirement and energy-cofactor scope remain independently unresolved.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The alignment supplies candidate provenance, not independent evidence for a protein requirement or energy-cofactor function. Current direct ChEBI roles do not settle that biological question, and their omission of a cofactor role does not disprove possible regulatory/cofactor uses. The source-linked plant study used 8-bromo-cGMP and pathway interventions; the inspected abstract does not establish exact neutral-form binding or qualify a protein member.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T100031Z-cgmp-chebi16356
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires cGMP
started_at: '2026-10-21T09:51:52Z'
finished_at: '2026-10-21T10:00:31Z'
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
summary: Chemical identification and explicit alignment provenance are supported,
  with unresolved protein requirement/energy scope. Two confirmed major findings concern
  chemical-to-trait equivalence and the incorrect guanidine nucleobase assertion.
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
  - path: data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
    sha256: f0621f84c9e9cafe11ff2961214ec52d6626495c34d0631277b83052be573bd6
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
  selection: Path-order position 6 in batch 013. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0) covers 118 record paths,
    leaving 429241 before this batch. 13 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
targets:
- kind: generated
  label: requires cGMP
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_16356
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml
    data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
    data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:16356 and compared source chemical references resolve in official
    structured responses. Captured alignment provenance, rather than a direct ChEBI
    cofactor assertion, supplies the candidate cofactor category; guanine/guanidine
    authorities distinguish the defining-word error. Identifier resolution does not
    certify every source chemical hierarchy statement or establish equality to the
    protein requirement trait.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - current-release
  - chemical-parent-1
  - chemical-parent-2
  - guanine
  - guanidine
  - crosswalk
  - owner
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:51:52Z'
  snapshot_sha256: f0621f84c9e9cafe11ff2961214ec52d6626495c34d0631277b83052be573bd6
  support: supports
  summary: 'Complete target YAML inspected: local requirement identifier/label, composite
    ChEBI and MicroGrowAgents definition attribution, energy-cofactor wording, two
    source-labelled RELATED_SYNONYM entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED
    status, local cofactor parent, chemical xref and stated ChEBI licence. No protein
    examples, causal graphs or chemical_participants occur.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T09:51:52Z'
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
  accessed_at: '2026-10-21T09:51:52Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:51:52Z'
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
  accessed_at: '2026-10-21T09:51:52Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: build_aligned synthesizes a requirement class from alignment name/category,
    appends ChEBI chemical text, emits RELATED_SYNONYM source identifiers/category,
    a generic cofactor parent and chemical xrefs. main selects only missing IDs; --force
    alone does not select this existing record. Future correction requires an audited
    route explicitly selecting it.
- evidence_id: crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and exact CHEBI:16356 row
  accessed_at: '2026-10-21T09:51:52Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The exact CHEBI:16356 row maps the current requirement identifier to cGMP,
    MicroGrowAgents ID cyclic_gmp and energy_cofactors category. This is alignment
    provenance, not an experimental requirement assertion.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Chemical entity scope and Licensing section
  summary: The official About page establishes ChEBI chemical-entity/role scope and
    CC BY 4.0 licensing, not equivalence to protein traits.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS metadata gives comparison ontology version 256. Reused metadata
    retain original access time and digest; this does not identify the seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16356/
  accessed_at: '2026-10-21T09:52:42.981849Z'
  snapshot_sha256: 62a746b350b296a457bc0f70b3928c68d3a9f692ca6085449da2234b28f0f216
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: The current entity is neutral 3-prime,5-prime-cyclic GMP, C10H12N5O7P,
    charge 0, with stereochemically specified ribose and a 3-prime,5-prime cyclic
    phosphate. The IUPAC name is guanosine 3-prime,5-prime-(hydrogen phosphate), and
    cGMP is a source synonym. Its prose nevertheless names guanidine as the purine
    nucleobase. The full outgoing role list contains mouse, human, yeast, E. coli
    and plant metabolite roles, without a direct cofactor role; chemical parents are
    guanyl ribonucleotide and cyclic purine nucleotide.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16356
  accessed_at: '2026-10-21T09:52:42.980919Z'
  snapshot_sha256: 2330c580eed8293cfe3da81ee3a1fcfcaecc3ffbe8ea956412f916a9a49cd60f
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical entity with matching formula,
    charge and InChI. Its definition matches the inspected ChEBI backend response.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and outgoing role hierarchy
  summary: CHEBI:23357 denotes the chemical cofactor role and has direct is-a biochemical
    role CHEBI:52206. This supplies candidate context, not a set of independently
    demonstrated protein requirements.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/61295/
  accessed_at: '2026-10-21T09:53:11.117466Z'
  snapshot_sha256: 3a8809ed4f641416142d14ddeddc1e22f279e8bbb337ef7279a5c102da264481
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: Asserted source chemical parent CHEBI:61295 resolves. Its available definition,
    formula/charge and outgoing relations were inspected; resolution does not certify
    chemical-hierarchy correctness or imply protein-trait subclass relations.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/19834/
  accessed_at: '2026-10-21T09:53:11.117918Z'
  snapshot_sha256: a31b13b7332e7b697ce1e5d60041fd967ce54801bb101fc921b32276cb235c89
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: Asserted source chemical parent CHEBI:19834 resolves. Its available definition,
    formula/charge and outgoing relations were inspected; resolution does not certify
    chemical-hierarchy correctness or imply protein-trait subclass relations.
- evidence_id: guanine
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16235/
  accessed_at: '2026-10-21T09:53:11.118149Z'
  snapshot_sha256: 50a1801fce27c5cf4e81a4c235fcca58ed16d67cf4c1670bac138d9c4978b1d5
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: Guanine is the 2-amino-6-oxopurine nucleobase, C5H5N5O, with a purine-ring
    structure. This matches the base in the cGMP source structure.
- evidence_id: guanidine
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/42820/
  accessed_at: '2026-10-21T09:53:33.482849Z'
  snapshot_sha256: 8ea73e00ae15f4a46aa26ff4baca30a203359d7fe39f8988db07b8bf67189905
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: Guanidine is an aminocarboxamidine, CH5N3, with source SMILES N=C(N)N and
    no purine ring. It is a distinct chemical entity, not a spelling variant of guanine.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/57746/
  accessed_at: '2026-10-21T09:53:11.118057Z'
  snapshot_sha256: 959f3cf6b9afbe70d61ec5ff3442cec89661df817779536167e90db5456ec820
  support: supports
  locator: Inspected identity, definition/names, formula/charge, default structure
    and outgoing relations
  summary: The conjugate-base entry is C10H11N5O7P, charge minus one. The free phosphate
    OH is deprotonated while cyclic linkage/ribose stereochemistry remain; its source
    pH 7.3 assertion is not adopted as bound-state evidence.
- evidence_id: signalling-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24591051%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:53:13.319154Z'
  snapshot_sha256: 2adebd7ce6c983acfbd0e6bd542d01d09cc9b37899a1785ce2e9d25a112d36f6
  support: supports
  locator: Verified identifiers and complete indexed abstract; full paper not inspected
  summary: PMID:24591051; DOI:10.1093/jxb/eru019. The complete indexed abstract reports
    Arabidopsis auxin-signalling experiments using endogenous cGMP accumulation, the
    8-bromo-cGMP analogue and pathway inhibitors; it proposes PKG involvement. This
    is bounded signalling context, not exact neutral-form binding or energy-donor
    evidence.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  locator: Executed 2026-10-21T09:54:15Z through 2026-10-21T09:54:16Z; exit 0
  accessed_at: '2026-10-21T09:54:16Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml
    data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
    data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml
  locator: Executed 2026-10-21T09:52:28Z through 2026-10-21T09:53:58Z; exit 0
  accessed_at: '2026-10-21T09:53:58Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml
  locator: Executed 2026-10-21T09:54:16Z through 2026-10-21T09:54:16Z; exit 0
  accessed_at: '2026-10-21T09:54:16Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:53:58Z through 2026-10-21T09:54:00Z; exit 0
  accessed_at: '2026-10-21T09:54:00Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: The maintained alignment emitter owns generated cGMP content; the captured
    crosswalk establishes MicroGrowAgents provenance. No sibling checkout was accessed.
    Ordinary missing-ID selection must be addressed in controlled regeneration.
  evidence_ids:
  - owner
  - crosswalk
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable requirement
    class rather than a protein instance. Optional examples, sequence/structure representations
    and mechanisms are not automatically required; none are newly qualified.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: evidence
  outcome: unknown
  summary: The MicroGrowAgents alignment supplies the energy-cofactor/requirement
    framing. Current ChEBI direct roles and the inspected signalling abstract do not
    independently establish that exact scope for a protein; they also do not exclude
    other nonconsumed regulatory or cofactor roles.
  evidence_ids:
  - record
  - chemical
  - owner
  - crosswalk
  - signalling-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-5
  topic: Biological requirement and chemical-state evidence
- area: identity
  outcome: concern
  summary: The exact identifier, neutral cyclic-nucleotide connectivity and source
    ribose stereochemistry support the cGMP chemical identity. Its guanosine name
    and structure identify a guanine base, contradicting the appended guanidine wording.
    The local cyclic_gmp and energy_cofactors values are source-labelled RELATED_SYNONYM
    entries from the MicroGrowAgents alignment, not exact chemical synonyms or independently
    established energy-donor functions.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - guanine
  - guanidine
  - conjugate
  - chemical-parent-1
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-6
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: Chemical text is attributable to ChEBI; aliases, energy category and requirement
    wrapper are explicitly MicroGrowAgents-aligned generator synthesis. Source fidelity
    does not validate the guanidine assertion. The captured crosswalk does not recover
    the sibling source release.
  evidence_ids:
  - record
  - chemical
  - owner
  - registry
  - licence
  - current-release
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-7
  topic: ChEBI attribution and release provenance
- area: consistency
  outcome: unknown
  summary: The generic local cofactor parent resolves and is inserted by the alignment
    emitter; its applicability to a specific cGMP requirement remains independently
    unresolved.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - schema
  - owner
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-8
  topic: Chemical-role and protein-trait hierarchy
- area: representation
  outcome: supported
  summary: The requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT
    class that remains SEEDED. No protein member, exclusive dependence or experimentally
    determined bound charge state is qualified by this review.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-9
  topic: FUNCTION cofactor requirement representation
- area: grounding
  outcome: concern
  summary: CHEBI:16356 identifies a chemical entity, whereas the local identifier
    denotes a protein requirement for it. xrefs requires true equivalence; chemical_participants
    provides typed chemical grounding.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  assessment_id: assessment-10
  topic: Chemical association versus trait equivalence
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-16356.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-cGMP trait denotes a protein functional requirement,
    while CHEBI:16356 in xrefs denotes the chemical entity. The curated alignment
    provides candidate association context, not equivalence or direct ChEBI cofactor-role
    evidence. This machine-readable equality changes denotation despite supported
    chemical identification.
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
  normalization_reason: Chemical and protein-requirement denotations differ; the schema
    provides typed participant grounding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-16356.guanidine-base-definition
  category: grounding
  severity: major
  title: Definition substitutes guanidine for the guanine nucleobase
  description: 'The target and current ChEBI definition call the purine nucleobase
    guanidine. The same source identifies guanosine and guanyl ribonucleotide, and
    its structure has the guanine purine ring. Official guanine and guanidine entries
    confirm distinct identities: guanidine is an acyclic aminocarboxamidine. This
    is a materially incorrect defining chemical assertion, even though the stable
    target ID and label still identify cGMP.'
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - chemical-parent-1
  - guanine
  - guanidine
  - owner
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: A different chemical identity is substituted in the defining
    assertion. Stable label/ID bound the defect but do not reduce it to a spelling-only
    issue.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build_aligned and its maintained input/controlled selection
    route in scripts/seed_cofactor_alignment.py to represent the supported chemical
    association to CHEBI:16356 through a typed chemical participant rather than equivalence.
    Preserve the proposed requirement class, exact chemical scope, explicit MicroGrowAgents
    attribution and unresolved role-evidence limits. Do not infer an independently
    verified COFACTOR role from the alignment category. The ordinary --force route
    does not select this existing ID, so regeneration must explicitly and auditably
    select it.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - Preserve exact chemical scope and attribution without chemical-to-trait equality
    or merging distinct charge, substituent or stereochemical states.
  - Retain candidate-class status and limits; do not qualify protein members or infer
    obligatory/exclusive physiological use.
  - A maintained source-transform fixture verifies typed output and audited selection/regeneration
    of the existing target; capture changed inputs and save a new review.
  - A curator must adjudicate the required ChemicalParticipant.role and its evidence
    before implementation. Do not choose COFACTOR solely from the alignment category;
    if no enum role represents the supported association, resolve the schema representation
    before emitting it. Preserve unresolved biological qualification separately.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused source-transform regression fixture. Then run just validate
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml, just validate-all
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml and just
    audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml.
    Run full just validate-all before merging record changes, as required by CLAUDE.md.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
- action_id: A2
  description: Correct the chemical-background noun to guanine through maintained
    alignment source-text handling or an explicit curated override. Preserve the cGMP
    identifier, neutral cyclic-phosphate state, ribose stereochemistry and original
    source attribution; retain the raw upstream response and the documented correction.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16356
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The rendered definition names guanine, consistent with guanosine and the inspected
    structure; guanidine is not retained as an exact alternative.
  - The correction is routed through the maintained emitter/override with an audited
    selection of this existing target and a focused regression fixture; source provenance
    remains explicit.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused source-transform regression fixture. Then run just validate
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml, just validate-all
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml and just
    audit-graphs data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml.
    Run full just validate-all before merging record changes, as required by CLAUDE.md.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The MicroGrowAgents alignment supplies candidate class provenance, not evidence
  that a particular protein requires cGMP or that ChEBI directly assigns a cofactor
  role. The exact requirement and energy-cofactor scope remain independently unresolved.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The alignment supplies candidate provenance, not independent evidence for a protein
  requirement or energy-cofactor function. Current direct ChEBI roles do not settle
  that biological question, and their omission of a cofactor role does not disprove
  possible regulatory/cofactor uses. The source-linked plant study used 8-bromo-cGMP
  and pathway interventions; the inspected abstract does not establish exact neutral-form
  binding or qualify a protein member.
tags:
- unreviewed-path-order
- batch-013
- chebi-cofactor
```
