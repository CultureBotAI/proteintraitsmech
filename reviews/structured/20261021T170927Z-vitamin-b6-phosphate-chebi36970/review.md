# Review of requires vitamin B6 phosphate

- Review: 20261021T170927Z-vitamin-b6-phosphate-chebi36970
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T16:56:56Z
- Finished UTC: 2026-10-21T17:09:27Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The broad vitamin B6 phosphate source identity and positive PLP/PMP protein contexts are supported. Curation is needed because the generated requirement trait asserts equivalence to the chemical class through xrefs; generic chemistry and optional exemplars need no forced completion.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 037. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96, the union covers 358 record paths, leaving 429001 before this batch. 37 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml | generated | requires vitamin B6 phosphate |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_36970 | Exact active ChEBI/OLS 36970, its structural and conjugate-class context, PLP/PMP/PNP comparisons, cofactor role, licence/release metadata and both complete primary abstracts were inspected. Current source resolution supports chemical identity and bounded biology, not chemical-to-protein-class equivalence. |

## Scientific And Domain Assessments

### Maintained trait emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Source identity and protein-trait scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The source anchor and local B6 phosphate name identify a broad chemical family, not a single fixed structure. PLP, PMP and PNP source entries are chemically distinct members. The absent source prose/formula is not automatically a target completeness defect.

### Trait hierarchy and source relationships

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The local cofactor parent is consistent with the direct source has_role assertion. Chemical is_a parents and the conjugate-base class are not imported as equivalent protein traits; no charge, stereochemical or pH-specific claim is made in the target.

### B6 phosphate member-specific protein evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

Primary structures positively support PLP and PMP enzyme-bound cofactor contexts. They support the biological relevance of the family while leaving individual-member, protein and protonation requirements to activity-specific adjudication.

### Protein requirement scope

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The proposed requirement class has positive member-specific biology and a source cofactor role, but the broad chemical family is not itself a set of qualified protein members. No universal requirement for every B6 phosphate, interchangeability, or exact bound free-state charge is established. Optional examples and mechanisms remain optional.

### Source attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The ChEBI role-seeding transformation and current source support are traceable; the generated requirement wording is distinguished from chemical source prose.

### Source grounding and trait associations

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_36970.

The chemical source reference resolves, but its use as an equivalent protein-requirement class conflicts with the schema. The finding concerns that relation rather than demanding optional examples or asserting universal nonmembership.

## Findings

### F1: Chemical identity is used as protein-trait equivalence

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-36970.chemical-entity-equivalence.

The record asserts a protein functional requirement but xrefs contains CHEBI:36970, which denotes a vitamin B6 phosphate chemical class. The schema reserves xrefs for true source-direct equivalence. An activity involving that chemical is not identical to the chemical entity or chemical class, even when a source role or positive protein experiment supports its relevance. The maintained emitter creates this relation by construction. 

## Recommended Actions And Acceptance Checks

### A1

Correct the maintained emitter so the requirement trait does not assert chemical identity through xrefs. Preserve the protein-class meaning and source provenance. Adjudicate the activity-specific chemical scope and role before optionally adding a typed chemical_participants association; if the evidence cannot justify a required role value, retain documented provenance and uncertainty without inventing a COFACTOR participant. Do not manufacture examples, mechanisms or fixed molecular details to repair the relation. 

- The revised trait no longer treats a chemical accession as an equivalent protein-requirement class. Any optional participant uses a curator-adjudicated activity-relative role and the correct chemical scope; otherwise retain provenance/uncertainty without adding a typed participant.
- Run just validate data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml on the proposed target revision.
- The normal ChEBI emitter supports force/apply regeneration; use an audited, bounded route and inspect the intended target diff.
- For maintained writer changes, run just audit-writers, just lint, focused code tests and just test. Complete full just validate-all before merge, then capture a fresh immutable review of the revised target; do not promote protein examples or native status from this review.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/36970/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | supports | CHEBI:36970 resolves to vitamin B6 phosphate, a generic chemical class. The official definition, chemical_data and default_structure are null. It has a direct cofactor role and structural parents phosphoric ester, organic phosphate and vitamin B6; the anion class is a conjugate-base relation, not an equivalent. Incoming is_a entries include PLP, PMP and pyridoxine phosphate. No compound_origins are listed. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:36970; Exact OLS term response: accession, preferred label, descriptions, synonym scopes, annotations, obsolete/replacement flags | supports | OLS independently resolves active CHEBI:36970 with empty description, plural related synonyms and no fixed chemical annotations. These are appropriate generic-class source fields, not a missing mandatory molecular formula. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:23357 is a biochemical role for an organic molecule or ion needed by an enzyme for activity; it has no fixed formula or structure and is_a CHEBI:52206. A role assertion supplies candidate context rather than chemical/trait equivalence. |
| license | https://www.ebi.ac.uk/chebi/about/; Official About page: ChEBI scope and Licensing section | supports | The official Licensing section makes ChEBI data available under CC BY 4.0. This supports the chemical-source licence; it is not a release pin for the original seed or a separate licence determination for an uninspected alignment table. |
| ontology-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Ontology metadata: version, versionIri, loaded/updated and configuration | supports | The reused official OLS metadata identifies loaded ChEBI version 256 and its 2026-10-16 load time. Its original access UTC is retained; it does not date the independent backend response or establish the seed release. |
| phosphoric-ester | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37734/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:37734 is a phosphoric-ester structural class with null definition, formula and structure; it is_a ester and phosphoric-acid derivative. |
| organic-phosphate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25703/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:25703 is the generic organic-phosphate class with null fixed chemistry and phosphate/phosphoric-acid-derivative/organophosphorus parents. |
| vitamin-b6 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/27306/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:27306 defines the B6 vitamer family, including pyridoxine, pyridoxal, pyridoxamine, their phosphate esters and corresponding ionized/salt forms. It is a broader family, not a claim that every member has the same protein role. |
| anion-class | https://www.ebi.ac.uk/chebi/backend/api/public/compound/176894/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:176894 is the separate B6 phosphate anion class, with null fixed chemistry and a conjugate-base relation to 36970. No numerical pH population follows from this relation. |
| plp-chemistry | https://www.ebi.ac.uk/chebi/backend/api/public/compound/18405/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:18405 is pyridoxal 5-prime-phosphate, C8H10NO6P with source net charge0 and direct coenzyme/cofactor roles; it is_a 36970. Its aldehyde graph and source conjugate relation distinguish it from PMP/PNP and from a protein-bound aldimine. |
| pmp-chemistry | https://www.ebi.ac.uk/chebi/backend/api/public/compound/18335/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:18335 is pyridoxamine 5-prime-phosphate, C8H13N2O5P, source charge0, with aminoalkyl rather than aldehyde connectivity, is_a 36970 and a separate conjugate-base relation. Current outgoing roles are metabolite roles; that does not negate its experimentally observed enzyme-bound cofactor form. |
| pnp-chemistry | https://www.ebi.ac.uk/chebi/backend/api/public/compound/28803/; Official structured compound response: exact accession/name, definition, chemical_data/default_structure, names, outgoing ontology relations and compound_origins; incoming relations only where explicitly identified | context_only | CHEBI:28803 is pyridoxine 5-prime-phosphate, C8H12NO6P and charge0, with hydroxymethyl connectivity, null definition and is_a 36970. Its existence in this chemical class does not establish the same catalytic function as PLP or PMP. |
| plp-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A17559874%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI metadata and complete indexed abstract; full article was not inspected | supports | The complete primary abstract reports the 1.3 Å holo structure of Sphingomonas paucimobilis serine palmitoyltransferase and identifies PLP linked to Lys265 as an internal aldimine. This is positive protein-bound cofactor context for a B6 phosphate member; it does not determine the free source molecule’s exact bound protonation. |
| pmp-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7896726%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI metadata and complete indexed abstract; full article was not inspected | supports | The complete primary abstract reports E. coli aspartate aminotransferase in its PMP form and maleate/glutarate complexes, with distinct open/closed conformations. This supports a second B6 phosphate cofactor context without treating PMP, PLP and all family members as interchangeable. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml; Executed 2026-10-21T16:57:45Z through 2026-10-21T16:57:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml; Executed 2026-10-21T16:57:45Z through 2026-10-21T16:59:36Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml; Executed 2026-10-21T16:57:47Z through 2026-10-21T16:57:48Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T16:59:36Z through 2026-10-21T16:59:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The PLP and PMP papers were inspected through complete indexed abstracts only. No exact experimental protonation or requirement for every descendant of the generic source class was independently established.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T170927Z-vitamin-b6-phosphate-chebi36970
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires vitamin B6 phosphate
started_at: '2026-10-21T16:56:56Z'
finished_at: '2026-10-21T17:09:27Z'
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
summary: The broad vitamin B6 phosphate source identity and positive PLP/PMP protein
  contexts are supported. Curation is needed because the generated requirement trait
  asserts equivalence to the chemical class through xrefs; generic chemistry and optional
  exemplars need no forced completion.
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
  - path: data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    sha256: 5d586f4bb23a756ed8dbb8b34439bc70b87386b8256d24c1bc29a0db1fd01b50
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
  selection: Path-order position 1 in batch 037. Fresh main inventory has 429359 records.
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
    f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18;
    ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7;
    b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb;
    c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4;
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96, the union covers 358 record paths, leaving
    429001 before this batch. 37 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
targets:
- kind: generated
  label: requires vitamin B6 phosphate
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_36970
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml
    data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml
    data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml
    data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
    data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Exact active ChEBI/OLS 36970, its structural and conjugate-class context,
    PLP/PMP/PNP comparisons, cofactor role, licence/release metadata and both complete
    primary abstracts were inspected. Current source resolution supports chemical
    identity and bounded biology, not chemical-to-protein-class equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - phosphoric-ester
  - organic-phosphate
  - vitamin-b6
  - anion-class
  - plp-chemistry
  - pmp-chemistry
  - pnp-chemistry
  - plp-primary
  - pmp-primary
  - license
  - ontology-release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T16:56:56Z'
  snapshot_sha256: 5d586f4bb23a756ed8dbb8b34439bc70b87386b8256d24c1bc29a0db1fd01b50
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
  accessed_at: '2026-10-21T16:56:56Z'
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
  accessed_at: '2026-10-21T16:56:56Z'
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
  accessed_at: '2026-10-21T16:56:56Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T16:56:56Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/36970/
  accessed_at: '2026-10-21T16:57:52.220256Z'
  snapshot_sha256: 6eb29c0600dcb5120bf40ae9de9fae4ba588ded383e994c9d8c9e1612da36f16
  support: supports
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:36970 resolves to vitamin B6 phosphate, a generic chemical class.
    The official definition, chemical_data and default_structure are null. It has
    a direct cofactor role and structural parents phosphoric ester, organic phosphate
    and vitamin B6; the anion class is a conjugate-base relation, not an equivalent.
    Incoming is_a entries include PLP, PMP and pyridoxine phosphate. No compound_origins
    are listed.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:36970
  accessed_at: '2026-10-21T16:57:52.218890Z'
  snapshot_sha256: 5971712cdadf8db0ab6aa5a3b1e46359365f918f0244bac292d8bc7431a8593a
  support: supports
  locator: 'Exact OLS term response: accession, preferred label, descriptions, synonym
    scopes, annotations, obsolete/replacement flags'
  summary: OLS independently resolves active CHEBI:36970 with empty description, plural
    related synonyms and no fixed chemical annotations. These are appropriate generic-class
    source fields, not a missing mandatory molecular formula.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:23357 is a biochemical role for an organic molecule or ion needed
    by an enzyme for activity; it has no fixed formula or structure and is_a CHEBI:52206.
    A role assertion supplies candidate context rather than chemical/trait equivalence.
- evidence_id: license
  kind: database
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: 'Official About page: ChEBI scope and Licensing section'
  summary: The official Licensing section makes ChEBI data available under CC BY 4.0.
    This supports the chemical-source licence; it is not a release pin for the original
    seed or a separate licence determination for an uninspected alignment table.
- evidence_id: ontology-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: 'Ontology metadata: version, versionIri, loaded/updated and configuration'
  summary: The reused official OLS metadata identifies loaded ChEBI version 256 and
    its 2026-10-16 load time. Its original access UTC is retained; it does not date
    the independent backend response or establish the seed release.
- evidence_id: phosphoric-ester
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37734/
  accessed_at: '2026-10-21T16:59:53.199959Z'
  snapshot_sha256: e21e10d5916aba18013b3a7bd3701bce36bd792cb442de97c122cc3e711065ce
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:37734 is a phosphoric-ester structural class with null definition,
    formula and structure; it is_a ester and phosphoric-acid derivative.
- evidence_id: organic-phosphate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25703/
  accessed_at: '2026-10-21T16:59:53.198976Z'
  snapshot_sha256: 8d45c61f84c6e9c74296ab2ef714746014a15f3f488b05a99669602519c7518c
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:25703 is the generic organic-phosphate class with null fixed chemistry
    and phosphate/phosphoric-acid-derivative/organophosphorus parents.
- evidence_id: vitamin-b6
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/27306/
  accessed_at: '2026-10-21T16:59:53.200597Z'
  snapshot_sha256: d97662b368202150c520141f80f514e0f66ab51a2d501f510c4db5ffdbad3bad
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:27306 defines the B6 vitamer family, including pyridoxine, pyridoxal,
    pyridoxamine, their phosphate esters and corresponding ionized/salt forms. It
    is a broader family, not a claim that every member has the same protein role.
- evidence_id: anion-class
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/176894/
  accessed_at: '2026-10-21T16:59:53.201043Z'
  snapshot_sha256: acaf5fe88605a17a1ef725226b5d6817c1539eb97705f9b4bf8bfede91c34d37
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:176894 is the separate B6 phosphate anion class, with null fixed
    chemistry and a conjugate-base relation to 36970. No numerical pH population follows
    from this relation.
- evidence_id: plp-chemistry
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/18405/
  accessed_at: '2026-10-21T17:00:23.683062Z'
  snapshot_sha256: a88a8a2519abe6bca236c25b12f5f805682ac073126f9020f461f8302d951f23
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:18405 is pyridoxal 5-prime-phosphate, C8H10NO6P with source net charge0
    and direct coenzyme/cofactor roles; it is_a 36970. Its aldehyde graph and source
    conjugate relation distinguish it from PMP/PNP and from a protein-bound aldimine.
- evidence_id: pmp-chemistry
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/18335/
  accessed_at: '2026-10-21T17:00:23.683462Z'
  snapshot_sha256: abd55f805fc32a1191a4831f18236f0ed3b0df9e8350bb1a22e5e2fd00faf952
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:18335 is pyridoxamine 5-prime-phosphate, C8H13N2O5P, source charge0,
    with aminoalkyl rather than aldehyde connectivity, is_a 36970 and a separate conjugate-base
    relation. Current outgoing roles are metabolite roles; that does not negate its
    experimentally observed enzyme-bound cofactor form.
- evidence_id: pnp-chemistry
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/28803/
  accessed_at: '2026-10-21T17:00:23.683621Z'
  snapshot_sha256: 1a37aced54fbf2d7ae2d8047db6247a76a46ff7e8cb9dee51354774eba2ec622
  support: context_only
  locator: 'Official structured compound response: exact accession/name, definition,
    chemical_data/default_structure, names, outgoing ontology relations and compound_origins;
    incoming relations only where explicitly identified'
  summary: CHEBI:28803 is pyridoxine 5-prime-phosphate, C8H12NO6P and charge0, with
    hydroxymethyl connectivity, null definition and is_a 36970. Its existence in this
    chemical class does not establish the same catalytic function as PLP or PMP.
- evidence_id: plp-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A17559874%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:59:55.126570Z'
  snapshot_sha256: 33ac4b38aa7396a324337672a0e32c79b494d5083bf6e30768684f29276915b8
  support: supports
  locator: Verified PMID/DOI metadata and complete indexed abstract; full article
    was not inspected
  summary: The complete primary abstract reports the 1.3 Å holo structure of Sphingomonas
    paucimobilis serine palmitoyltransferase and identifies PLP linked to Lys265 as
    an internal aldimine. This is positive protein-bound cofactor context for a B6
    phosphate member; it does not determine the free source molecule’s exact bound
    protonation.
- evidence_id: pmp-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7896726%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:59:55.377393Z'
  snapshot_sha256: 2c8a025baec9c80a450b65581fad3cc0233a31f64827c6719cbbff65c65ab417
  support: supports
  locator: Verified PMID/DOI metadata and complete indexed abstract; full article
    was not inspected
  summary: The complete primary abstract reports E. coli aspartate aminotransferase
    in its PMP form and maleate/glutarate complexes, with distinct open/closed conformations.
    This supports a second B6 phosphate cofactor context without treating PMP, PLP
    and all family members as interchangeable.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  locator: Executed 2026-10-21T16:57:45Z through 2026-10-21T16:57:47Z; exit 0
  accessed_at: '2026-10-21T16:57:47Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml
    data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml
    data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml
    data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
    data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml
  locator: Executed 2026-10-21T16:57:45Z through 2026-10-21T16:59:36Z; exit 0
  accessed_at: '2026-10-21T16:59:36Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
  locator: Executed 2026-10-21T16:57:47Z through 2026-10-21T16:57:48Z; exit 0
  accessed_at: '2026-10-21T16:57:48Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T16:59:36Z through 2026-10-21T16:59:38Z; exit 0
  accessed_at: '2026-10-21T16:59:38Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-1
  topic: Maintained trait emitter
- area: completeness
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable requirement
    class rather than a protein instance. Optional examples, sequence/structure representations
    and mechanisms are not automatically required; none are newly qualified.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source anchor and local B6 phosphate name identify a broad chemical
    family, not a single fixed structure. PLP, PMP and PNP source entries are chemically
    distinct members. The absent source prose/formula is not automatically a target
    completeness defect.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - plp-chemistry
  - pmp-chemistry
  - pnp-chemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-5
  topic: Source identity and protein-trait scope
- area: consistency
  outcome: supported
  summary: The local cofactor parent is consistent with the direct source has_role
    assertion. Chemical is_a parents and the conjugate-base class are not imported
    as equivalent protein traits; no charge, stereochemical or pH-specific claim is
    made in the target.
  evidence_ids:
  - chemical
  - cofactor-role
  - local-parent-1
  - phosphoric-ester
  - organic-phosphate
  - vitamin-b6
  - anion-class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-6
  topic: Trait hierarchy and source relationships
- area: evidence
  outcome: supported
  summary: Primary structures positively support PLP and PMP enzyme-bound cofactor
    contexts. They support the biological relevance of the family while leaving individual-member,
    protein and protonation requirements to activity-specific adjudication.
  evidence_ids:
  - plp-primary
  - pmp-primary
  - plp-chemistry
  - pmp-chemistry
  topic: B6 phosphate member-specific protein evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The proposed requirement class has positive member-specific biology and
    a source cofactor role, but the broad chemical family is not itself a set of qualified
    protein members. No universal requirement for every B6 phosphate, interchangeability,
    or exact bound free-state charge is established. Optional examples and mechanisms
    remain optional.
  evidence_ids:
  - record
  - schema
  - chemical
  - plp-primary
  - pmp-primary
  topic: Protein requirement scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The ChEBI role-seeding transformation and current source support are traceable;
    the generated requirement wording is distinguished from chemical source prose.
  evidence_ids:
  - owner
  - registry
  - chemical
  - license
  - ontology-release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-9
  topic: Source attribution and release provenance
- area: grounding
  outcome: concern
  summary: The chemical source reference resolves, but its use as an equivalent protein-requirement
    class conflicts with the schema. The finding concerns that relation rather than
    demanding optional examples or asserting universal nonmembership.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  assessment_id: assessment-10
  topic: Source grounding and trait associations
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-36970.chemical-entity-equivalence
  category: grounding
  severity: major
  certainty: confirmed
  title: Chemical identity is used as protein-trait equivalence
  description: 'The record asserts a protein functional requirement but xrefs contains
    CHEBI:36970, which denotes a vitamin B6 phosphate chemical class. The schema reserves
    xrefs for true source-direct equivalence. An activity involving that chemical
    is not identical to the chemical entity or chemical class, even when a source
    role or positive protein experiment supports its relevance. The maintained emitter
    creates this relation by construction. '
  field_paths:
  - xrefs
  - chemical_participants
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - plp-primary
  - pmp-primary
  normalization_reason: The record equates different entity types in a defining grounding
    field; the schema requires their distinction. This is independent of whether a
    particular protein can use the chemical.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: 'Correct the maintained emitter so the requirement trait does not assert
    chemical identity through xrefs. Preserve the protein-class meaning and source
    provenance. Adjudicate the activity-specific chemical scope and role before optionally
    adding a typed chemical_participants association; if the evidence cannot justify
    a required role value, retain documented provenance and uncertainty without inventing
    a COFACTOR participant. Do not manufacture examples, mechanisms or fixed molecular
    details to repair the relation. '
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_36970
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The revised trait no longer treats a chemical accession as an equivalent protein-requirement
    class. Any optional participant uses a curator-adjudicated activity-relative role
    and the correct chemical scope; otherwise retain provenance/uncertainty without
    adding a typed participant.
  - Run just validate data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    on the proposed target revision.
  - The normal ChEBI emitter supports force/apply regeneration; use an audited, bounded
    route and inspect the intended target diff.
  - For maintained writer changes, run just audit-writers, just lint, focused code
    tests and just test. Complete full just validate-all before merge, then capture
    a fresh immutable review of the revised target; do not promote protein examples
    or native status from this review.
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
- The PLP and PMP papers were inspected through complete indexed abstracts only. No
  exact experimental protonation or requirement for every descendant of the generic
  source class was independently established.
tags:
- unreviewed-path-order
- batch-037
- chebi-cofactor
```
