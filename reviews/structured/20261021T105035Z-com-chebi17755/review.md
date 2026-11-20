# Review of requires CoM

- Review: 20261021T105035Z-com-chebi17755
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:40:57Z
- Finished UTC: 2026-10-21T10:50:35Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact local target is resolved, but its CoM/coenzyme_m identity conflicts with cystathionine CHEBI17755. A confirmed blocker covers that collision; a separate confirmed major covers chemical-to-trait equivalence and requires identity repair first. No automatic CoM state or protein requirement is qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 016. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50) covers 148 record paths, leaving 429211 before this batch. 16 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml | generated | requires CoM |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17755 | Current official ChEBI and OLS identify CHEBI:17755 and the cited chemical/role context. The references resolve as cystathionine, which conflicts with the target CoM label; resolution is not identity approval. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

seed_cofactor_alignment.py owns this generated alignment, with shared ChEBI name/definition helpers and the emitted local crosswalk. The original upstream curation table/release is not inspected; no sibling checkout is accessed.

### Protein trait class completeness

completeness: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The YAML has a class-shaped requirement identifier and label, but the label/alias and chemical definition identify different molecules. Optional representations cannot resolve this identity conflict.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### CoM versus cystathionine identity collision

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The exact record is resolved, but its scientific identity is internally inconsistent: CoM/coenzyme_m means mercaptoethanesulfonic acid in the positive official/primary comparison, whereas CHEBI17755 and the copied definition denote cystathionine. The mismatch is not a protonation, oxidation or stereochemical variant.

### Identity prerequisite to biological qualification

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The inspected cystathionine literature supplies metabolic/transport/inhibitor contexts, not support for the CoM-labelled requirement. No negative claim that cystathionine can never have a cofactor role follows. Identity must be resolved before protein-requirement qualification.

### Definition and maintained-source provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The copied chemical description is traceable to current official ChEBI. The requirement/category/alias wrapper comes from the captured MicroGrowAgents alignment emitter; current ChEBI roles do not automatically supply that wrapper. Licence and comparison release are traceable, while the exact seed release remains unknown.

### Requirement-parent and source-relation scope

consistency: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The captured cofactor requirement parent resolves as an alignment default. It does not itself prove a direct ChEBI cofactor role or repair the label/chemical identity collision.

### Protein requirement representation

representation: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The class-shaped FUNCTION requirement representation remains SEEDED, but molecular identity must be reconciled before it can be scientifically qualified.

### Source denotation versus protein-trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17755.

The ChEBI chemical referent/class differs from the protein-requirement class. xrefs asserts true own-source equivalence, whereas a chemical association requires typed grounding after identity and activity-relative role adjudication.

## Findings

### F1: CoM label is paired with cystathionine chemistry

blocker / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17755.com-cystathionine-identity-collision.

The target label CoM and coenzyme_m alias denote coenzymeM, whereas CHEBI17755 resolves to cystathionine and supplies the copied amino-acid definition. The two molecules differ in elemental composition and connectivity, not merely charge or stereochemistry. The captured alignment row preserves this wrong association.

### F2: Chemical referent is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17755.chemical-entity-equivalence.

The xref denotes a chemical entity while the local record denotes a protein functional requirement. Even a correct chemical identity or cofactor-role assertion would not establish equality of those classes. This separate semantic defect remains after the CoM/cystathionine mismatch is repaired; its action depends on resolving that blocker first.

## Recommended Actions And Acceptance Checks

### A1

Audit and correct the maintained alignment input/override and build_aligned identity checks before regeneration. Adjudicate whether the intended requirement is CoM, including its exact chemical state, and handle the existing identifier/path lifecycle and any collisions through an audited route. Do not relabel cystathionine as CoM, transfer evidence between the molecules, or merely move CHEBI17755 into chemical_participants. Remove grouping token other from alternate-label output while preserving provenance. The original sibling source table must be inspected through an authorized source route before claiming an upstream fix.

- Positive chemical identity evidence agrees across label, source ID, definition and aliases. Any intended CoM state is explicitly adjudicated; the wrong association is not hidden by a typed-participant rewrite.
- A focused alignment fixture rejects incompatible labels/IDs and grouping tokens. Regeneration explicitly selects/reconciles existing records because main's missing-only selection is not bypassed by --force. No implicit identifier reassignment or protein/status promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml. Run full just validate-all before merging record changes. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

### A2

After the identity collision is resolved and an intended chemical is explicitly adjudicated, change build_aligned and its maintained input/override to replace chemical-to-trait equality with an accurately typed chemical_participants association. Do not preserve CHEBI17755 as a CoM participant. ChemicalParticipant.role is required: adjudicate the activity-relative role, including the category's non-substrate scope, rather than treating an alignment label as independently verified COFACTOR. Keep source-backed candidate provenance distinct from new protein qualification, and do not simply move the claim to mapped_xrefs.

- The source chemical association no longer asserts chemical-to-protein-trait equivalence. Exact identity/class scope and candidate source provenance remain auditable.
- A focused source-transform fixture verifies identity and required participant-role adjudication. Regeneration follows an audited route explicitly selecting existing targets. The alignment missing-only selection is not bypassed by --force alone. No protein examples or native status are promoted.
- For maintained writer changes run just audit-writers, just lint and just test with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml. Run full just validate-all before merging record changes. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml; Entire target YAML | supports | Entire target YAML inspected, including its requires-label, mixed ChEBI/MicroGrowAgents definition provenance, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, root parent, RELATED_SYNONYM source tokens, chemical xref and licence. No optional protein examples, graphs or chemical_participants occur in this YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | The ChEBI seeder supplies imported names/definitions and emitter helpers. This target is emitted by seed_cofactor_alignment.py, not selected solely through ChEBI cofactor-role ancestry. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| alignment-owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main | supports | build_aligned combines a MicroGrowAgents label/category with a ChEBI definition selected by identifier, uses the cofactor root parent, copies both cofactor_id and category into RELATED_SYNONYM, and emits a chemical xref. main selects only missing ChEBI IDs; --force alone does not select an existing ID. |
| crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and exact CHEBI:17755 row | supports | The captured row maps CHEBI:17755 to CoM, coenzyme_m and other. This documents the local alignment assertion; it does not establish correct chemistry. |
| licence | https://www.ebi.ac.uk/chebi/about/; About chemical scope and Licensing section | supports | Official ChEBI chemical-entity/role scope and Licensing section support attribution and CC BY 4.0. Chemical or role identity is not protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Reused official OLS metadata records comparison ontology version 256; original access UTC and digest are preserved. It does not identify the seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17755/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | CHEBI:17755 resolves positively as cystathionine, C7H14N2O4S, charge 0, with two amino/carboxylic-acid groups joined by a thioether and unspecified stereochemistry. Its definition is the target's copied homocysteine/serine-derived amino-acid text. The structure is chemically different from CoM/HS-CoM CHEBI:17905; this conclusion does not depend on absence of a cofactor annotation. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17755; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier, matching definition and chemical annotations. The source synonym scopes are retained; class drawings and chemical names do not establish protein-trait equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | CHEBI:23357 is the abstract cofactor biochemical role, defined by participation required for enzyme activity and loose/tight association. It has is-a biochemical role CHEBI:52206, and chemical_data/default_structure are null. It is neither one molecular compound nor a protein requirement class, and no molecular formula, charge or participant should be invented. |
| context-25212 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25212/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | Metabolite CHEBI:25212 is a biochemical role for metabolic intermediates/products. That role does not prove or refute additional cofactor uses. |
| context-23505 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23505/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | Cystathionines CHEBI:23505 resolves under homocysteines without a single formula or prose definition. The chemical hierarchy is not a coenzyme M identity. |
| context-16385 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16385/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | Organic sulfide CHEBI:16385 denotes R-S-R with neither R being hydrogen, historically called thioethers. This supports the cystathionine linkage distinction from a free thiol. |
| context-17905 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17905/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | supports | CHEBI:17905 is coenzyme M/HS-CoM, neutral C2H6O3S2, represented as O=S(=O)(O)CCS: an achiral two-carbon sulfonic acid with a free terminal thiol. It has direct coenzyme role and organosulfonic-acid/thiol parents; CHEBI:58319 is its sulfonate conjugate base. Neither methyl-CoM nor a disulfide is this structure. |
| context-58319 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58319/; Complete identity, names, definition, chemical_data/default_structure and outgoing relations | context_only | CHEBI:58319 is coenzyme M(1−), C2H5O3S2, with sulfonate deprotonation and the thiol still protonated. Its source pH 7.3 major-species assertion is authentic comparison text, not independently quantified here or imported into the neutral target. |
| com-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10411892%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:10411892; DOI:10.1073/pnas.96.15.8432. The complete primary abstract explicitly identifies CoM as 2-mercaptoethanesulfonic acid in a bacterial epoxide-carboxylation pathway. This positive chemical identity is distinct from cystathionine; pathway usage does not independently qualify an exact-state protein requirement. |
| cystathionine-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22212096%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | context_only | PMID:22212096; DOI:10.1111/j.1574-6968.2011.02492.X. In Streptococcus mutans, DL-cystathionine competed with cystine uptake via TcyABC. This source-cited result concerns a different amino-acid chemical and assay context; it neither turns cystathionine into CoM nor excludes every possible other biological role. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml; Executed 2026-10-21T10:44:10Z through 2026-10-21T10:44:11Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml; Executed 2026-10-21T10:41:11Z through 2026-10-21T10:43:37Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml; Executed 2026-10-21T10:44:11Z through 2026-10-21T10:44:11Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:43:37Z through 2026-10-21T10:43:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- MicroGrowAgents alignment supplies candidate provenance, not a direct ChEBI cofactor-role assertion or proof that a particular protein requires the chemical. The upstream original alignment table and release remain uninspected.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The other source-cited cystathionine abstracts were inspected: PMID12907234 is a review of anaplerotic metabolism, PMID15033753 reports a cellular inhibitor context, and PMID22264337 describes a metabolomic study. These do not supply CoM identity or exact non-substrate protein qualification. No local sibling target is used as comparison evidence.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T105035Z-com-chebi17755
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires CoM
started_at: '2026-10-21T10:40:57Z'
finished_at: '2026-10-21T10:50:35Z'
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
summary: The exact local target is resolved, but its CoM/coenzyme_m identity conflicts
  with cystathionine CHEBI17755. A confirmed blocker covers that collision; a separate
  confirmed major covers chemical-to-trait equivalence and requires identity repair
  first. No automatic CoM state or protein requirement is qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
    sha256: f0636df7dccadb2d0e165430f6dbf755684072d682985aa4fe3ae8daf8611006
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
  - path: scripts/seed_cofactor_alignment.py
    sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 10 in batch 016. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50)
    covers 148 record paths, leaving 429211 before this batch. 16 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
targets:
- kind: generated
  label: requires CoM
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17755
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml
    data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current official ChEBI and OLS identify CHEBI:17755 and the cited chemical/role
    context. The references resolve as cystathionine, which conflicts with the target
    CoM label; resolution is not identity approval.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-25212
  - context-23505
  - context-16385
  - context-17905
  - context-58319
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: f0636df7dccadb2d0e165430f6dbf755684072d682985aa4fe3ae8daf8611006
  support: supports
  summary: Entire target YAML inspected, including its requires-label, mixed ChEBI/MicroGrowAgents
    definition provenance, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status,
    root parent, RELATED_SYNONYM source tokens, chemical xref and licence. No optional
    protein examples, graphs or chemical_participants occur in this YAML.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T10:40:57Z'
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
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The ChEBI seeder supplies imported names/definitions and emitter helpers.
    This target is emitted by seed_cofactor_alignment.py, not selected solely through
    ChEBI cofactor-role ancestry.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: alignment-owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: build_aligned combines a MicroGrowAgents label/category with a ChEBI definition
    selected by identifier, uses the cofactor root parent, copies both cofactor_id
    and category into RELATED_SYNONYM, and emits a chemical xref. main selects only
    missing ChEBI IDs; --force alone does not select an existing ID.
- evidence_id: crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and exact CHEBI:17755 row
  accessed_at: '2026-10-21T10:40:57Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The captured row maps CHEBI:17755 to CoM, coenzyme_m and other. This documents
    the local alignment assertion; it does not establish correct chemistry.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: About chemical scope and Licensing section
  summary: Official ChEBI chemical-entity/role scope and Licensing section support
    attribution and CC BY 4.0. Chemical or role identity is not protein-trait equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Reused official OLS metadata records comparison ontology version 256; original
    access UTC and digest are preserved. It does not identify the seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17755/
  accessed_at: '2026-10-21T10:41:31.356185Z'
  snapshot_sha256: 4e33131fd0ed669c20c087c98f2949a831d8f31e8bef6268ed4f0e3120ae5dbf
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: CHEBI:17755 resolves positively as cystathionine, C7H14N2O4S, charge 0,
    with two amino/carboxylic-acid groups joined by a thioether and unspecified stereochemistry.
    Its definition is the target's copied homocysteine/serine-derived amino-acid text.
    The structure is chemically different from CoM/HS-CoM CHEBI:17905; this conclusion
    does not depend on absence of a cofactor annotation.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17755
  accessed_at: '2026-10-21T10:41:30.677575Z'
  snapshot_sha256: b939b6ce078583f9d622005c6428689ede559cde31acfda0390fc394c119d3a5
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier, matching definition
    and chemical annotations. The source synonym scopes are retained; class drawings
    and chemical names do not establish protein-trait equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: CHEBI:23357 is the abstract cofactor biochemical role, defined by participation
    required for enzyme activity and loose/tight association. It has is-a biochemical
    role CHEBI:52206, and chemical_data/default_structure are null. It is neither
    one molecular compound nor a protein requirement class, and no molecular formula,
    charge or participant should be invented.
- evidence_id: context-25212
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25212/
  accessed_at: '2026-10-21T10:42:19.410364Z'
  snapshot_sha256: 596fe26466d05ad247af5b0026873d927902432b013fe65daa73a51512ebb53a
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: Metabolite CHEBI:25212 is a biochemical role for metabolic intermediates/products.
    That role does not prove or refute additional cofactor uses.
- evidence_id: context-23505
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23505/
  accessed_at: '2026-10-21T10:42:20.039753Z'
  snapshot_sha256: 31d99caa69322219270ff1e9a2b053d63fdce50aa8712e185148b22f4ae4ec53
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: Cystathionines CHEBI:23505 resolves under homocysteines without a single
    formula or prose definition. The chemical hierarchy is not a coenzyme M identity.
- evidence_id: context-16385
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16385/
  accessed_at: '2026-10-21T10:42:20.042248Z'
  snapshot_sha256: 78bd9ce729531a45fbdb48f3e1cd9a1d471feb33ef98b7a1f75aafed93eef194
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: Organic sulfide CHEBI:16385 denotes R-S-R with neither R being hydrogen,
    historically called thioethers. This supports the cystathionine linkage distinction
    from a free thiol.
- evidence_id: context-17905
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17905/
  accessed_at: '2026-10-21T10:41:31.344363Z'
  snapshot_sha256: bbe82fd3150fffc35d6f2588b2826eecabacb74a7d231c11c2bbe630fb19d661
  support: supports
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: 'CHEBI:17905 is coenzyme M/HS-CoM, neutral C2H6O3S2, represented as O=S(=O)(O)CCS:
    an achiral two-carbon sulfonic acid with a free terminal thiol. It has direct
    coenzyme role and organosulfonic-acid/thiol parents; CHEBI:58319 is its sulfonate
    conjugate base. Neither methyl-CoM nor a disulfide is this structure.'
- evidence_id: context-58319
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58319/
  accessed_at: '2026-10-21T10:42:18.579736Z'
  snapshot_sha256: a8642b3e504d19fd2850ea09fb658a6f33bf2383907769b6516e41b62f4dfe8a
  support: context_only
  locator: Complete identity, names, definition, chemical_data/default_structure and
    outgoing relations
  summary: CHEBI:58319 is coenzyme M(1−), C2H5O3S2, with sulfonate deprotonation and
    the thiol still protonated. Its source pH 7.3 major-species assertion is authentic
    comparison text, not independently quantified here or imported into the neutral
    target.
- evidence_id: com-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10411892%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:42:21.759156Z'
  snapshot_sha256: 91adcefc9e10d518ad2d9613335961e219eda2c5247ddd9dbfcd8e12de1d63b0
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:10411892; DOI:10.1073/pnas.96.15.8432. The complete primary abstract
    explicitly identifies CoM as 2-mercaptoethanesulfonic acid in a bacterial epoxide-carboxylation
    pathway. This positive chemical identity is distinct from cystathionine; pathway
    usage does not independently qualify an exact-state protein requirement.
- evidence_id: cystathionine-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22212096%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:42:21.639348Z'
  snapshot_sha256: 66ecc9b10452b9e23c78a158c060dadd26f06ea5eddef61cf35009cb60d3e6b8
  support: context_only
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:22212096; DOI:10.1111/j.1574-6968.2011.02492.X. In Streptococcus mutans,
    DL-cystathionine competed with cystine uptake via TcyABC. This source-cited result
    concerns a different amino-acid chemical and assay context; it neither turns cystathionine
    into CoM nor excludes every possible other biological role.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  locator: Executed 2026-10-21T10:44:10Z through 2026-10-21T10:44:11Z; exit 0
  accessed_at: '2026-10-21T10:44:11Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml
    data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  locator: Executed 2026-10-21T10:41:11Z through 2026-10-21T10:43:37Z; exit 0
  accessed_at: '2026-10-21T10:43:37Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  locator: Executed 2026-10-21T10:44:11Z through 2026-10-21T10:44:11Z; exit 0
  accessed_at: '2026-10-21T10:44:11Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T10:43:37Z through 2026-10-21T10:43:38Z; exit 0
  accessed_at: '2026-10-21T10:43:38Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: seed_cofactor_alignment.py owns this generated alignment, with shared ChEBI
    name/definition helpers and the emitted local crosswalk. The original upstream
    curation table/release is not inspected; no sibling checkout is accessed.
  evidence_ids:
  - alignment-owner
  - owner
  - crosswalk
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: concern
  summary: The YAML has a class-shaped requirement identifier and label, but the label/alias
    and chemical definition identify different molecules. Optional representations
    cannot resolve this identity conflict.
  evidence_ids:
  - record
  - chemical
  - context-17905
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: concern
  summary: 'The exact record is resolved, but its scientific identity is internally
    inconsistent: CoM/coenzyme_m means mercaptoethanesulfonic acid in the positive
    official/primary comparison, whereas CHEBI17755 and the copied definition denote
    cystathionine. The mismatch is not a protonation, oxidation or stereochemical
    variant.'
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-17905
  - com-primary
  - crosswalk
  topic: CoM versus cystathionine identity collision
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-5
- area: evidence
  outcome: unknown
  summary: The inspected cystathionine literature supplies metabolic/transport/inhibitor
    contexts, not support for the CoM-labelled requirement. No negative claim that
    cystathionine can never have a cofactor role follows. Identity must be resolved
    before protein-requirement qualification.
  evidence_ids:
  - chemical
  - cystathionine-primary
  - context-17905
  - com-primary
  topic: Identity prerequisite to biological qualification
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-6
- area: provenance
  outcome: supported
  summary: The copied chemical description is traceable to current official ChEBI.
    The requirement/category/alias wrapper comes from the captured MicroGrowAgents
    alignment emitter; current ChEBI roles do not automatically supply that wrapper.
    Licence and comparison release are traceable, while the exact seed release remains
    unknown.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - registry
  - owner
  - alignment-owner
  - crosswalk
  topic: Definition and maintained-source provenance
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-7
- area: consistency
  outcome: concern
  summary: The captured cofactor requirement parent resolves as an alignment default.
    It does not itself prove a direct ChEBI cofactor role or repair the label/chemical
    identity collision.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - schema
  - alignment-owner
  topic: Requirement-parent and source-relation scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-8
- area: representation
  outcome: concern
  summary: The class-shaped FUNCTION requirement representation remains SEEDED, but
    molecular identity must be reconciled before it can be scientifically qualified.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  - alignment-owner
  - crosswalk
  topic: Protein requirement representation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The ChEBI chemical referent/class differs from the protein-requirement
    class. xrefs asserts true own-source equivalence, whereas a chemical association
    requires typed grounding after identity and activity-relative role adjudication.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - alignment-owner
  - crosswalk
  topic: Source denotation versus protein-trait equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17755.com-cystathionine-identity-collision
  category: identity
  severity: blocker
  title: CoM label is paired with cystathionine chemistry
  description: The target label CoM and coenzyme_m alias denote coenzymeM, whereas
    CHEBI17755 resolves to cystathionine and supplies the copied amino-acid definition.
    The two molecules differ in elemental composition and connectivity, not merely
    charge or stereochemistry. The captured alignment row preserves this wrong association.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-17905
  - com-primary
  - alignment-owner
  - crosswalk
  certainty: confirmed
  field_paths:
  - label
  - definition
  - definition_source
  - synonyms
  - xrefs
  normalization_reason: The wrong molecular identity in the defining label/grounding
    is a blocker; the exact local target is nevertheless resolved and reviewable.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: blocker
- issue_key: chebi.cofactor-requirement.CHEBI-17755.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical referent is asserted equivalent to a protein requirement
  description: The xref denotes a chemical entity while the local record denotes a
    protein functional requirement. Even a correct chemical identity or cofactor-role
    assertion would not establish equality of those classes. This separate semantic
    defect remains after the CoM/cystathionine mismatch is repaired; its action depends
    on resolving that blocker first.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - alignment-owner
  - crosswalk
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Chemical denotation and protein-requirement denotation differ.
    Resolving the CoM/cystathionine identity collision is a prerequisite to this separate
    grounding repair.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
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
  description: Audit and correct the maintained alignment input/override and build_aligned
    identity checks before regeneration. Adjudicate whether the intended requirement
    is CoM, including its exact chemical state, and handle the existing identifier/path
    lifecycle and any collisions through an audited route. Do not relabel cystathionine
    as CoM, transfer evidence between the molecules, or merely move CHEBI17755 into
    chemical_participants. Remove grouping token other from alternate-label output
    while preserving provenance. The original sibling source table must be inspected
    through an authorized source route before claiming an upstream fix.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - Positive chemical identity evidence agrees across label, source ID, definition
    and aliases. Any intended CoM state is explicitly adjudicated; the wrong association
    is not hidden by a typed-participant rewrite.
  - A focused alignment fixture rejects incompatible labels/IDs and grouping tokens.
    Regeneration explicitly selects/reconciles existing records because main's missing-only
    selection is not bypassed by --force. No implicit identifier reassignment or protein/status
    promotion occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml.
    Run full just validate-all before merging record changes. Capture changed inputs
    and save a fresh validated review; do not overwrite this observation.
- action_id: A2
  description: 'After the identity collision is resolved and an intended chemical
    is explicitly adjudicated, change build_aligned and its maintained input/override
    to replace chemical-to-trait equality with an accurately typed chemical_participants
    association. Do not preserve CHEBI17755 as a CoM participant. ChemicalParticipant.role
    is required: adjudicate the activity-relative role, including the category''s
    non-substrate scope, rather than treating an alignment label as independently
    verified COFACTOR. Keep source-backed candidate provenance distinct from new protein
    qualification, and do not simply move the claim to mapped_xrefs.'
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17755
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The source chemical association no longer asserts chemical-to-protein-trait equivalence.
    Exact identity/class scope and candidate source provenance remain auditable.
  - A focused source-transform fixture verifies identity and required participant-role
    adjudication. Regeneration follows an audited route explicitly selecting existing
    targets. The alignment missing-only selection is not bypassed by --force alone.
    No protein examples or native status are promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml.
    Run full just validate-all before merging record changes. Capture changed inputs
    and save a fresh validated review; do not overwrite this observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- MicroGrowAgents alignment supplies candidate provenance, not a direct ChEBI cofactor-role
  assertion or proof that a particular protein requires the chemical. The upstream
  original alignment table and release remain uninspected.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- 'The other source-cited cystathionine abstracts were inspected: PMID12907234 is
  a review of anaplerotic metabolism, PMID15033753 reports a cellular inhibitor context,
  and PMID22264337 describes a metabolomic study. These do not supply CoM identity
  or exact non-substrate protein qualification. No local sibling target is used as
  comparison evidence.'
tags:
- unreviewed-path-order
- batch-016
- chebi-cofactor
```
