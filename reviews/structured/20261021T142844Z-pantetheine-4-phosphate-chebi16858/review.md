# Review of requires pantetheine 4'-phosphate

- Review: 20261021T142844Z-pantetheine-4-phosphate-chebi16858
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T14:15:14Z
- Finished UTC: 2026-10-21T14:28:44Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The free neutral acid identity is supported, with positive attached-PPant function kept distinct from biosynthetic substrate use. One confirmed major concerns chemical-to-protein-requirement equivalence; no mandatory optional representation or automatic stereochemical/state merge is introduced.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 7 in batch 029. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099, the union covers 278 record paths, leaving 429081 before this batch. 29 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml | generated | requires pantetheine 4'-phosphate |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16858 | Current backend/OLS resolve the exact free chemical, charge, unspecified stereochemistry and authentic cofactor role. The conjugate, D-specific child, attachment group and chemical parent were inspected together with complete ACP/PPAT primary abstracts and licence/release metadata. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Phosphopantetheine constitution, charge and unspecified stereochemistry

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The exact source graph supports the free neutral acid, terminal thiol and one phosphate. The pantoate stereocentre is unspecified, which does not assert a racemic mixture. The explicitly D(R) child, conjugate form and attachment-group representation are distinct chemical scopes; no silent stereochemical narrowing or charge-state merge is justified.

### Short requirement definition and source chemical name

nomenclature: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The target uses the source name in a synthesized requirement definition without extra chemical prose. The source itself has a null prose definition but a resolved structure, so this absence is not by itself an identity or completeness defect. Source aliases not copied into this target are not treated as local naming defects.

### Positive protein-attached phosphopantetheine function

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The holo-ACP synthase study supports an attached PPant moiety enabling acyl chemistry in E. coli ACP. The PPAT study separately identifies free PPant as a biosynthetic acceptor substrate. These are positive but different biological contexts, neither an automatic exact-free-state protein qualification nor proof that no non-substrate role can exist.

### Free chemical versus attached prosthetic-group requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The target has an authentic direct cofactor role. Translating it to a protein requirement must resolve stereochemical scope, free versus attached group and activity-relative non-substrate role. Neither the ACP attachment experiment nor PPAT turnover alone establishes a requirement for this exact free microstate. Optional examples and participants remain optional, and no broad absence of cofactor biology is inferred.

### Cofactor role and chemical hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The direct cofactor edge supports the source selection and local broader requirement parent. The inspected chemical superclass, conjugate and D(R) child remain chemical relations, not automatically missing protein-trait parents or true-equivalence links. No pH claim is made by this target or imported from comparison entries.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

CHEBI:16858 denotes the stereochemically unspecified phosphopantetheine free neutral acid, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The current schema reserves xrefs for true own-source equivalence. Chemical identity and an authentic source role or positive biological activity do not make these distinct entity types equivalent.

### Maintained owner, source attribution, release and licence

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16858.

The inspected ChEBI seeder selects chemicals through the cofactor-role subtree, synthesizes the requirement prefix and appends available chemical prose. The captured direct cofactor or coenzyme role explains the local parent. ChEBI data are CC BY 4.0, but source attribution does not independently establish the synthesized protein requirement or pin the original seed release.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-16858.chemical-entity-equivalence.

CHEBI:16858 denotes the stereochemically unspecified phosphopantetheine free neutral acid, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The current schema reserves xrefs for true own-source equivalence. Chemical identity and an authentic source role or positive biological activity do not make these distinct entity types equivalent.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so a chemical association is not emitted as protein-trait equality. Preserve the exact free charge and unspecified stereochemistry unless a curator documents a different intended scope. Distinguish the attached group from the free chemical before any activity-level association; do not infer identity from formula alone or silently replace the target with its D(R) child. Preserve chemical provenance and adjudicate the activity-relative non-substrate premise before any optional chemical_participants association with role COFACTOR. If identity, scope or role remains unresolved, retain explicit uncertainty without inventing a participant. Do not move the same false equality to mapped_xrefs, require optional protein examples or promote native status.

- Regenerated xrefs no longer equates a chemical source entity or chemical class with a protein functional requirement; source attribution remains traceable.
- Any optional typed participant follows identity adjudication and has a supported activity-relative role. Free chemical, protein-attached group, biosynthetic substrate and vitamin-family scopes are not silently interchanged.
- After scoped regeneration run just validate data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml. If identity repair changes the path, apply the same checks to the approved replacement and verify that stale references are reconciled.
- For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Use an audited scoped existing-record route with pinned ChEBI inputs: emit skips existing files unless --force is supplied and writes only with --apply, while main traverses a cohort, so broad --apply --force is not a one-record repair. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing; reused bytes digest verified and original access UTC retained | supports | The official Introduction describes chemical entities, groups and classes; Licensing establishes CC BY 4.0 for ChEBI data. This supports chemical source attribution, not independent protein-requirement evidence or terms for an uninspected external alignment table. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. The live backend and this ontology version are separate comparison snapshots; neither identifies the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16858/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:16858 is pantetheine 4′-phosphate, C11H23N2O7PS, net 0, with two phosphate OH groups, a terminal thiol and unspecified pantoate stereochemistry. The prose definition is null. Outgoing relations include direct cofactor role, thiol/phosphopantetheine ancestry and conjugate base CHEBI:47942. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16858; Exact label, description, synonyms, is_obsolete, formula/charge and structural annotations | supports | The nonobsolete OLS CHEBI:16858 term resolves the exact source name, definition or its absence, synonyms and available chemical annotations. These agree with backend identity; chemical source resolution does not establish equivalence to a protein requirement class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 is a role for an organic molecule or ion required by an enzyme for activity, loosely or tightly attached. Its outgoing parent is biochemical role CHEBI:52206; a chemical role is distinct from a class of proteins requiring the chemical. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Inspected source response captured at the recorded UTC time | supports | CHEBI:52206 defines a role played by a molecular entity or part within a biochemical context. It does not by itself establish a specific protein requirement. |
| acp-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7559576%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected unless separately cited | supports | PMID:7559576; DOI:10.1074/jbc.270.42.24658. The complete abstract reports transfer of the 4′-phosphopantetheine moiety from CoA to Ser36 of E. coli ACP by holo-ACP synthase, enabling holo-ACP acyl-group activation through the cysteamine thiol. This supplies positive protein-attached-group function, not qualification of the exact free neutral or dianionic chemical state. |
| ppat-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:12837781%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected unless separately cited | supports | PMID:12837781; DOI:10.1128/JB.185.14.4074-4080.2003. The complete abstract identifies 4′-phosphopantetheine as the acceptor substrate in PPAT adenylyl transfer from MgATP to form dephospho-CoA and pyrophosphate. Its structural results concern PPAT-bound CoA and dephospho-CoA conformations; they do not establish free PPant as a non-substrate cofactor of PPAT. |
| attached-group | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47982/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:47982 is pantetheine 4′-phosphate group, with an explicit attachment wildcard *OP(=O)([O−])O… and net −1. It is an organic anionic group with is-substituent-group-from CHEBI:47942. Its formula matches the free dianion but its attachment and charge differ; formula alone cannot collapse the two representations. |
| prosthetic-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Inspected source response captured at the recorded UTC time | supports | CHEBI:26348 defines a tightly bound specific nonpolypeptide unit involved in a protein’s biological activity and is a cofactor subclass. This supplies role context without identifying the exact chemical attachment state in an arbitrary protein. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47942/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:47942 is the corresponding free dianion C11H21N2O7PS, with two phosphate O− groups and unspecified pantoate stereochemistry. It differs from the neutral target by two protons. |
| stereo-child | https://www.ebi.ac.uk/chebi/backend/api/public/compound/4222/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:4222 is explicitly D(R)-pantetheine 4′-phosphate, with encoded stereochemistry and a direct prosthetic-group role. It is an is-a child of CHEBI:16858 and the conjugate acid of CHEBI:61723. The target does not automatically acquire this narrower stereochemical specification. |
| thiol-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29256/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:29256 defines an organosulfur compound with a carbon-attached SH group, with an R-group thiol drawing. This supports the terminal thiol class, not an equivalent protein trait. |
| chemical-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26073/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:26073 is phosphopantetheine, a broad chemical class with null definition, formula and default structure; outgoing ancestry includes pantetheines and amidoalkyl phosphate, with a conjugate-base class relation. Inherited role classification is not an additional direct role assertion. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml; Executed 2026-10-21T14:16:17Z through 2026-10-21T14:16:18Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml; Executed 2026-10-21T14:16:10Z through 2026-10-21T14:17:43Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml; Executed 2026-10-21T14:16:18Z through 2026-10-21T14:16:18Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T14:17:43Z through 2026-10-21T14:17:44Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The two primary papers were inspected through complete indexed abstracts. Exact free-state populations, stereoisomer-specific activity, attachment microstates and canonical protein coordinates were not independently qualified. No pH claim is made by this target or imported from comparison entries.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T142844Z-pantetheine-4-phosphate-chebi16858
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires pantetheine 4'-phosphate
started_at: '2026-10-21T14:15:14Z'
finished_at: '2026-10-21T14:28:44Z'
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
summary: The free neutral acid identity is supported, with positive attached-PPant
  function kept distinct from biosynthetic substrate use. One confirmed major concerns
  chemical-to-protein-requirement equivalence; no mandatory optional representation
  or automatic stereochemical/state merge is introduced.
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
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
    sha256: b6d3004517bebcfdd6e315f8850717fd8ab05c5a7db5dcdc2c9b3339378a7dc5
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
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 7 in batch 029. Fresh main inventory has 429359 records.
    Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87;
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df;
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242;
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98)
    cover 248 record paths. Including validated unpublished local review commit(s)
    da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd;
    f67243be00c3d9c891c24c22a32c932ea7bee099, the union covers 278 record paths, leaving
    429081 before this batch. 29 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
targets:
- kind: generated
  label: requires pantetheine 4'-phosphate
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_16858
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml
    data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml
    data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
    data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml
    data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current backend/OLS resolve the exact free chemical, charge, unspecified
    stereochemistry and authentic cofactor role. The conjugate, D-specific child,
    attachment group and chemical parent were inspected together with complete ACP/PPAT
    primary abstracts and licence/release metadata.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  evidence_ids:
  - licence
  - release
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - acp-primary
  - ppat-primary
  - attached-group
  - prosthetic-role
  - conjugate
  - stereo-child
  - thiol-parent
  - chemical-parent
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T14:15:14Z'
  snapshot_sha256: b6d3004517bebcfdd6e315f8850717fd8ab05c5a7db5dcdc2c9b3339378a7dc5
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
  accessed_at: '2026-10-21T14:15:14Z'
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
  accessed_at: '2026-10-21T14:15:14Z'
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
  accessed_at: '2026-10-21T14:15:14Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T14:15:14Z'
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
  locator: Introduction and Licensing; reused bytes digest verified and original access
    UTC retained
  summary: The official Introduction describes chemical entities, groups and classes;
    Licensing establishes CC BY 4.0 for ChEBI data. This supports chemical source
    attribution, not independent protein-requirement evidence or terms for an uninspected
    external alignment table.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    The live backend and this ontology version are separate comparison snapshots;
    neither identifies the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16858/
  accessed_at: '2026-10-21T14:16:06.155366Z'
  snapshot_sha256: 2cf321c894355b51c93623b1b99735064fe900a1f3ffae59c4efd742ff33e900
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:16858 is pantetheine 4′-phosphate, C11H23N2O7PS, net 0, with two
    phosphate OH groups, a terminal thiol and unspecified pantoate stereochemistry.
    The prose definition is null. Outgoing relations include direct cofactor role,
    thiol/phosphopantetheine ancestry and conjugate base CHEBI:47942.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:16858
  accessed_at: '2026-10-21T14:16:06.123809Z'
  snapshot_sha256: 1a6c16f689a3dd02dbbffc97adab910d8c1eacaa165e7d4ccd9ffe67b3a62bd1
  support: supports
  locator: Exact label, description, synonyms, is_obsolete, formula/charge and structural
    annotations
  summary: The nonobsolete OLS CHEBI:16858 term resolves the exact source name, definition
    or its absence, synonyms and available chemical annotations. These agree with
    backend identity; chemical source resolution does not establish equivalence to
    a protein requirement class.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:23357 is a role for an organic molecule or ion required by an enzyme
    for activity, loosely or tightly attached. Its outgoing parent is biochemical
    role CHEBI:52206; a chemical role is distinct from a class of proteins requiring
    the chemical.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:52206 defines a role played by a molecular entity or part within
    a biochemical context. It does not by itself establish a specific protein requirement.
- evidence_id: acp-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7559576%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:16:55.256651Z'
  snapshot_sha256: 1c8feb9dfd42d5cbc523148887609eb52dbe06449af65041211b43875ce42172
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected unless separately cited
  summary: PMID:7559576; DOI:10.1074/jbc.270.42.24658. The complete abstract reports
    transfer of the 4′-phosphopantetheine moiety from CoA to Ser36 of E. coli ACP
    by holo-ACP synthase, enabling holo-ACP acyl-group activation through the cysteamine
    thiol. This supplies positive protein-attached-group function, not qualification
    of the exact free neutral or dianionic chemical state.
- evidence_id: ppat-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:12837781%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:16:55.264294Z'
  snapshot_sha256: 3f1f2274b43d418fb76603c244ef2e81b119f1c93014447581b53d6b372f08e0
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected unless separately cited
  summary: PMID:12837781; DOI:10.1128/JB.185.14.4074-4080.2003. The complete abstract
    identifies 4′-phosphopantetheine as the acceptor substrate in PPAT adenylyl transfer
    from MgATP to form dephospho-CoA and pyrophosphate. Its structural results concern
    PPAT-bound CoA and dephospho-CoA conformations; they do not establish free PPant
    as a non-substrate cofactor of PPAT.
- evidence_id: attached-group
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47982/
  accessed_at: '2026-10-21T14:16:53.122621Z'
  snapshot_sha256: 5afa76406c880d8c0e2d7d805b8977a2600b874be1120216419f822de3e596f5
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:47982 is pantetheine 4′-phosphate group, with an explicit attachment
    wildcard *OP(=O)([O−])O… and net −1. It is an organic anionic group with is-substituent-group-from
    CHEBI:47942. Its formula matches the free dianion but its attachment and charge
    differ; formula alone cannot collapse the two representations.
- evidence_id: prosthetic-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:10:09.154369Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:26348 defines a tightly bound specific nonpolypeptide unit involved
    in a protein’s biological activity and is a cofactor subclass. This supplies role
    context without identifying the exact chemical attachment state in an arbitrary
    protein.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47942/
  accessed_at: '2026-10-21T14:16:06.155684Z'
  snapshot_sha256: 5e808d15fb753cddcd25c8fa08d7c9ad194e7212236d3fd1856ba8a5c0ce2db6
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:47942 is the corresponding free dianion C11H21N2O7PS, with two phosphate
    O− groups and unspecified pantoate stereochemistry. It differs from the neutral
    target by two protons.
- evidence_id: stereo-child
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/4222/
  accessed_at: '2026-10-21T14:16:53.151803Z'
  snapshot_sha256: 7b6b6477a8cdc31e34a736b3a32b52aeff9ac1ef3095cc25e2bcf3f94da1b210
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:4222 is explicitly D(R)-pantetheine 4′-phosphate, with encoded stereochemistry
    and a direct prosthetic-group role. It is an is-a child of CHEBI:16858 and the
    conjugate acid of CHEBI:61723. The target does not automatically acquire this
    narrower stereochemical specification.
- evidence_id: thiol-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29256/
  accessed_at: '2026-10-21T14:16:53.227412Z'
  snapshot_sha256: 215dd317988cec50435f7d122262b435d514bd2ccee315c3abdbf137c6d8a5a5
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:29256 defines an organosulfur compound with a carbon-attached SH
    group, with an R-group thiol drawing. This supports the terminal thiol class,
    not an equivalent protein trait.
- evidence_id: chemical-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26073/
  accessed_at: '2026-10-21T14:16:53.777915Z'
  snapshot_sha256: ad677bf037c8a2760a1e7856a77ac4dad65471aa9dcba3edd6ea0a21d33595f6
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:26073 is phosphopantetheine, a broad chemical class with null definition,
    formula and default structure; outgoing ancestry includes pantetheines and amidoalkyl
    phosphate, with a conjugate-base class relation. Inherited role classification
    is not an additional direct role assertion.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  locator: Executed 2026-10-21T14:16:17Z through 2026-10-21T14:16:18Z; exit 0
  accessed_at: '2026-10-21T14:16:18Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml
    data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml
    data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
    data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml
    data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml
  locator: Executed 2026-10-21T14:16:10Z through 2026-10-21T14:17:43Z; exit 0
  accessed_at: '2026-10-21T14:17:43Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
  locator: Executed 2026-10-21T14:16:18Z through 2026-10-21T14:16:18Z; exit 0
  accessed_at: '2026-10-21T14:16:18Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T14:17:43Z through 2026-10-21T14:17:44Z; exit 0
  accessed_at: '2026-10-21T14:17:44Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The exact source graph supports the free neutral acid, terminal thiol and
    one phosphate. The pantoate stereocentre is unspecified, which does not assert
    a racemic mixture. The explicitly D(R) child, conjugate form and attachment-group
    representation are distinct chemical scopes; no silent stereochemical narrowing
    or charge-state merge is justified.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - conjugate
  - stereo-child
  - attached-group
  topic: Phosphopantetheine constitution, charge and unspecified stereochemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-5
- area: nomenclature
  outcome: supported
  summary: The target uses the source name in a synthesized requirement definition
    without extra chemical prose. The source itself has a null prose definition but
    a resolved structure, so this absence is not by itself an identity or completeness
    defect. Source aliases not copied into this target are not treated as local naming
    defects.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  topic: Short requirement definition and source chemical name
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The holo-ACP synthase study supports an attached PPant moiety enabling
    acyl chemistry in E. coli ACP. The PPAT study separately identifies free PPant
    as a biosynthetic acceptor substrate. These are positive but different biological
    contexts, neither an automatic exact-free-state protein qualification nor proof
    that no non-substrate role can exist.
  evidence_ids:
  - acp-primary
  - ppat-primary
  - attached-group
  - prosthetic-role
  topic: Positive protein-attached phosphopantetheine function
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The target has an authentic direct cofactor role. Translating it to a protein
    requirement must resolve stereochemical scope, free versus attached group and
    activity-relative non-substrate role. Neither the ACP attachment experiment nor
    PPAT turnover alone establishes a requirement for this exact free microstate.
    Optional examples and participants remain optional, and no broad absence of cofactor
    biology is inferred.
  evidence_ids:
  - record
  - schema
  - chemical
  - cofactor-role
  - acp-primary
  - ppat-primary
  - stereo-child
  - attached-group
  topic: Free chemical versus attached prosthetic-group requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct cofactor edge supports the source selection and local broader
    requirement parent. The inspected chemical superclass, conjugate and D(R) child
    remain chemical relations, not automatically missing protein-trait parents or
    true-equivalence links. No pH claim is made by this target or imported from comparison
    entries.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - chemical-parent
  - cofactor-role
  - conjugate
  - stereo-child
  topic: Cofactor role and chemical hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: CHEBI:16858 denotes the stereochemically unspecified phosphopantetheine
    free neutral acid, whereas the local COFACTOR_REQ record denotes a proposed protein
    functional requirement. The current schema reserves xrefs for true own-source
    equivalence. Chemical identity and an authentic source role or positive biological
    activity do not make these distinct entity types equivalent.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - acp-primary
  - ppat-primary
  - attached-group
  - stereo-child
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-10
- area: provenance
  outcome: supported
  summary: The inspected ChEBI seeder selects chemicals through the cofactor-role
    subtree, synthesizes the requirement prefix and appends available chemical prose.
    The captured direct cofactor or coenzyme role explains the local parent. ChEBI
    data are CC BY 4.0, but source attribution does not independently establish the
    synthesized protein requirement or pin the original seed release.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  - cofactor-role
  topic: Maintained owner, source attribution, release and licence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-16858.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:16858 denotes the stereochemically unspecified phosphopantetheine
    free neutral acid, whereas the local COFACTOR_REQ record denotes a proposed protein
    functional requirement. The current schema reserves xrefs for true own-source
    equivalence. Chemical identity and an authentic source role or positive biological
    activity do not make these distinct entity types equivalent.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - acp-primary
  - ppat-primary
  - attached-group
  - stereo-child
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical-to-protein-class type mismatch is an independently
    repairable major grounding defect. It neither denies positive biological activity
    nor makes optional representations mandatory.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build in scripts/seed_chebi_cofactor.py so a chemical association
    is not emitted as protein-trait equality. Preserve the exact free charge and unspecified
    stereochemistry unless a curator documents a different intended scope. Distinguish
    the attached group from the free chemical before any activity-level association;
    do not infer identity from formula alone or silently replace the target with its
    D(R) child. Preserve chemical provenance and adjudicate the activity-relative
    non-substrate premise before any optional chemical_participants association with
    role COFACTOR. If identity, scope or role remains unresolved, retain explicit
    uncertainty without inventing a participant. Do not move the same false equality
    to mapped_xrefs, require optional protein examples or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16858
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Regenerated xrefs no longer equates a chemical source entity or chemical class
    with a protein functional requirement; source attribution remains traceable.
  - Any optional typed participant follows identity adjudication and has a supported
    activity-relative role. Free chemical, protein-attached group, biosynthetic substrate
    and vitamin-family scopes are not silently interchanged.
  - After scoped regeneration run just validate data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml.
    If identity repair changes the path, apply the same checks to the approved replacement
    and verify that stale references are reconciled.
  - 'For maintained writer changes add focused regression coverage and run just audit-writers,
    just lint and just test. Use an audited scoped existing-record route with pinned
    ChEBI inputs: emit skips existing files unless --force is supplied and writes
    only with --apply, while main traverses a cohort, so broad --apply --force is
    not a one-record repair. Run full just validate-all before merging record changes;
    recapture changed inputs and save a fresh structured review without overwriting
    this observation.'
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
- The two primary papers were inspected through complete indexed abstracts. Exact
  free-state populations, stereoisomer-specific activity, attachment microstates and
  canonical protein coordinates were not independently qualified. No pH claim is made
  by this target or imported from comparison entries.
tags:
- unreviewed-path-order
- batch-029
- chebi-cofactor
```
