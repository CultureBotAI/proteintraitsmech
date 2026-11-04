# Review of requires lanthanum cation

- Review: 20261021T131123Z-lanthanum-cation-chebi231841
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:02:39Z
- Finished UTC: 2026-10-21T13:11:23Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The broad lanthanum-cation identity and source role are authentic; positive La3+ enzyme evidence remains member-specific. One confirmed major finding concerns chemical-class-to-protein-requirement equivalence.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 025. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616) covers 238 record paths, leaving 429121 before this batch. 25 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml | generated | requires lanthanum cation |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_231841 | Current backend/OLS resolve the broad lanthanum-cation definition, +2/+3 children, direct cofactor role and chemical parents. The primary/structural comparison supports La3+ specifically. Official licence and release metadata are verified. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Variable-charge lanthanum-cation class

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The copied definition, source identifier and broad class scope agree. The class intentionally includes +2 and +3 children; lack of a single formula/structure is appropriate rather than an incomplete exact molecule. It must not be silently collapsed to La3+.

### Specific ionic member with demonstrated protein function

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The La3+ XoxF1 study provides positive evidence for one member of this broad cation class. Its structure/function results do not establish activity for La2+ or every positively charged lanthanum species. A broad class can retain this positive member context without claiming every member was tested.

### Broad class requirement versus member-specific evidence

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The generic requirement does not specify a protein, activity or which ion members meet it. Source cofactor classification is authentic, but the inspected La3+ experiment is not an all-cation dependence demonstration. This is an explicit qualification limit, not proof that the broad source class or every untested member is biologically wrong.

### Source role, chemical parents and local requirement parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The direct cofactor role explains selection and the broader local requirement parent. The metal-cation and lanthanum-molecular-entity source parents classify chemicals, not automatically protein requirements. No extra local hierarchy edge or charge-state merge is inferred.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

CHEBI:231841 denotes a variable-charge class of positively charged lanthanum ions, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Correct chemical identity, source attribution and biological relevance cannot make these two denotations equivalent.

### Source attribution, licence and maintained emitter

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_231841.

The captured ChEBI seeder explains role-based candidate selection, the synthesized requirement prefix, any appended chemical definition, the source-role parent and the chemical xref. Official ChEBI data are CC BY 4.0. The chemical attribution does not independently establish the locally synthesized protein requirement. Current backend and OLS version 256 are comparison snapshots, with the original seed release unknown.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-231841.chemical-entity-equivalence.

CHEBI:231841 denotes a variable-charge class of positively charged lanthanum ions, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Correct chemical identity, source attribution and biological relevance cannot make these two denotations equivalent.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality while preserving the supported source identity and provenance. Preserve the broad class and distinguish it from its +2 and +3 members. Adjudicate the intended activity-relative breadth; the positive La3+ experiment must not silently qualify all cations or force replacement of the broad identifier. If an activity-relative role and the intended chemical scope are supported, an optional chemical_participants association with role COFACTOR may represent the chemical separately; otherwise retain provenance and explicit uncertainty without inventing a participant. Do not move the same equality to mapped_xrefs, automatically merge distinct charge states, require optional protein examples or promote native status.

- Regenerated xrefs no longer equates the source chemical with the local protein requirement. The intended chemical and activity scope is explicitly adjudicated, preserving source attribution.
- Any optional participant has a supported chemical identity and activity-relative role; unqualified biology is not promoted and absence of optional representation is not itself a defect.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml.
- For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Regenerate this existing target through an audited scoped route using the maintained seed_chebi_cofactor.py transformation and release-pinned inputs. Its emit function skips existing paths unless --force is supplied and writes only with --apply; because main traverses the source cohort, do not treat a broad --apply --force invocation as a one-record repair. Run full just validate-all before merging record changes, recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; original timestamp and verified digest retained | supports | The inspected official Introduction and Licensing sections describe chemical entities and biological roles and establish CC BY 4.0 for ChEBI data. This does not independently license or release-pin an uninspected MicroGrowAgents source table. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. The original access time is retained. Live backend and OLS ontology version are distinct comparison snapshots, not identification of the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/231841/; Complete official compound response: exact identity, names, definition or null, chemical data, structure, outgoing relations and relevant incoming context | supports | CHEBI:231841 is the class lanthanum cation, defined as a positively charged lanthanum ion. Fixed chemical data and default structure are null, appropriately leaving charge variable. The source includes La(III) CHEBI:49701 and La(II) CHEBI:37317 as children, directly assigns cofactor role, and has lanthanum molecular entity and metal cation parents. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:231841; Inspected source response captured at the recorded UTC time | supports | Nonobsolete OLS CHEBI:231841 was inspected for the exact label, definition or empty definition, synonyms and available formula, charge, SMILES and InChI annotations. These agree with the specifically described chemical scope in the backend. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 is a biochemical role defined for an organic molecule or ion required by an enzyme for activity; it is under biochemical role CHEBI:52206. It is not itself a protein requirement class. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Inspected source response captured at the recorded UTC time | supports | CHEBI:52206 defines a role played by a molecular entity or part in a biochemical context. Role assignment and the entity bearing it remain distinct from a class of proteins requiring it. |
| trication | https://www.ebi.ac.uk/chebi/backend/api/public/compound/49701/; Complete official compound response: exact identity, names, definition or null, chemical data, structure, outgoing relations and relevant incoming context | supports | La(III) CHEBI:49701 explicitly has charge +3 and [La+3], with direct cofactor role and lanthanum-cation parent. |
| dication | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37317/; Complete official compound response: exact identity, names, definition or null, chemical data, structure, outgoing relations and relevant incoming context | supports | La(II) CHEBI:37317 explicitly has charge +2 and [La+2], with lanthanum-cation, lanthanum-molecular-entity and divalent/monoatomic-dication parents. Its outgoing array does not contain a direct cofactor-role edge; that observation is not a universal negative biological result. |
| element-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37215/; Complete official compound response: exact identity, names, definition or null, chemical data, structure, outgoing relations and relevant incoming context | supports | Lanthanum molecular entity CHEBI:37215 is broader chemical context with a has-part relation to lanthanum atom; it does not fix an ion charge. |
| cation-class | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25213/; Complete official compound response: exact identity, names, definition or null, chemical data, structure, outgoing relations and relevant incoming context | supports | Metal cation CHEBI:25213 is a broad class under monoatomic cation and inorganic cation, with no single fixed structure. |
| la-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:32366463%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI when supplied and complete indexed abstract; full article not inspected unless separately cited | supports | PMID:32366463; DOI:10.1074/jbc.RA120.013227. The complete abstract reports Methylorubrum extorquens AM1 XoxF1 structures with La3+ and Asp320 coordination, with and without PQQ. Asp320 substitution disrupts La3+ coordination and in vivo/in vitro function; Ca-bound preparations produced without La3+ show little or no activity. This supports a specific La(III)-enzyme context, not neutral La or every lanthanum cation. |
| la-structure-metadata | https://data.rcsb.org/rest/v1/core/entry/6OC6; Inspected source response captured at the recorded UTC time | supports | RCSB entry 6OC6 metadata identifies XoxF with La and PQQ, X-ray resolution 2.89 Å and the matching primary citation PMID:32366463. The component inventory contains LA and PQQ. This is inspected entry metadata, not a coordinate reanalysis or newly qualified canonical protein example. |
| la-component | https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/LA; Inspected source response captured at the recorded UTC time | supports | The actual PDBe CCD LA summary gives La with charge +3, SMILES [La+3] and a CHEBI:49701 cross-reference. Its ion identity agrees with the ChEBI La(III) entry; the ion is not equivalent to the whole metal-PQQ-protein complex. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml; Executed 2026-10-21T13:03:19Z through 2026-10-21T13:03:20Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml; Executed 2026-10-21T13:03:10Z through 2026-10-21T13:04:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml; Executed 2026-10-21T13:03:20Z through 2026-10-21T13:03:20Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:04:47Z through 2026-10-21T13:04:48Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- Member-specific La3+ primary evidence was read through the complete abstract and structural/component metadata. No La2+ enzyme experiment was established in this bounded source set; that is a qualification limit rather than an exhaustive absence claim. No universal ionic abundance or physiological charge distribution is asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T131123Z-lanthanum-cation-chebi231841
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires lanthanum cation
started_at: '2026-10-21T13:02:39Z'
finished_at: '2026-10-21T13:11:23Z'
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
summary: The broad lanthanum-cation identity and source role are authentic; positive
  La3+ enzyme evidence remains member-specific. One confirmed major finding concerns
  chemical-class-to-protein-requirement equivalence.
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
  - path: data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
    sha256: 621859fd86e2b8958b4d252681bc2b59e1f6809fef231a6c5af80fa5f663c9e7
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
  selection: Path-order position 8 in batch 025. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616) covers 238 record paths,
    leaving 429121 before this batch. 25 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
targets:
- kind: generated
  label: requires lanthanum cation
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_231841
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml
    data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml
    data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml
    data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
    data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current backend/OLS resolve the broad lanthanum-cation definition, +2/+3
    children, direct cofactor role and chemical parents. The primary/structural comparison
    supports La3+ specifically. Official licence and release metadata are verified.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:02:39Z'
  snapshot_sha256: 621859fd86e2b8958b4d252681bc2b59e1f6809fef231a6c5af80fa5f663c9e7
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
  accessed_at: '2026-10-21T13:02:39Z'
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
  accessed_at: '2026-10-21T13:02:39Z'
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
  accessed_at: '2026-10-21T13:02:39Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:02:39Z'
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
  locator: Introduction and Licensing sections; original timestamp and verified digest
    retained
  summary: The inspected official Introduction and Licensing sections describe chemical
    entities and biological roles and establish CC BY 4.0 for ChEBI data. This does
    not independently license or release-pin an uninspected MicroGrowAgents source
    table.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    The original access time is retained. Live backend and OLS ontology version are
    distinct comparison snapshots, not identification of the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/231841/
  accessed_at: '2026-10-21T13:03:26.510564Z'
  snapshot_sha256: 2e4c63f9a7b92ef9b59ba2d048384905053b6f0b926f0b4746917083e9a1cc73
  support: supports
  locator: 'Complete official compound response: exact identity, names, definition
    or null, chemical data, structure, outgoing relations and relevant incoming context'
  summary: CHEBI:231841 is the class lanthanum cation, defined as a positively charged
    lanthanum ion. Fixed chemical data and default structure are null, appropriately
    leaving charge variable. The source includes La(III) CHEBI:49701 and La(II) CHEBI:37317
    as children, directly assigns cofactor role, and has lanthanum molecular entity
    and metal cation parents.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:231841
  accessed_at: '2026-10-21T13:03:27.223179Z'
  snapshot_sha256: 085421b783aa37d427ee5ce58353eefc961a5fc2f3da0374b9121ca4cfae84b0
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Nonobsolete OLS CHEBI:231841 was inspected for the exact label, definition
    or empty definition, synonyms and available formula, charge, SMILES and InChI
    annotations. These agree with the specifically described chemical scope in the
    backend.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:23357 is a biochemical role defined for an organic molecule or ion
    required by an enzyme for activity; it is under biochemical role CHEBI:52206.
    It is not itself a protein requirement class.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:52206 defines a role played by a molecular entity or part in a biochemical
    context. Role assignment and the entity bearing it remain distinct from a class
    of proteins requiring it.
- evidence_id: trication
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/49701/
  accessed_at: '2026-10-21T13:03:26.531681Z'
  snapshot_sha256: 4c9304185d7ac88e88a3cffce704440147d6b86669755bbe2e1c8f35ae43f09a
  support: supports
  locator: 'Complete official compound response: exact identity, names, definition
    or null, chemical data, structure, outgoing relations and relevant incoming context'
  summary: La(III) CHEBI:49701 explicitly has charge +3 and [La+3], with direct cofactor
    role and lanthanum-cation parent.
- evidence_id: dication
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37317/
  accessed_at: '2026-10-21T13:03:53.541345Z'
  snapshot_sha256: 8d6a30a0424f68b4bd043a01f8ccf9717ac816fb3d0879594fb8ac598cc3702c
  support: supports
  locator: 'Complete official compound response: exact identity, names, definition
    or null, chemical data, structure, outgoing relations and relevant incoming context'
  summary: La(II) CHEBI:37317 explicitly has charge +2 and [La+2], with lanthanum-cation,
    lanthanum-molecular-entity and divalent/monoatomic-dication parents. Its outgoing
    array does not contain a direct cofactor-role edge; that observation is not a
    universal negative biological result.
- evidence_id: element-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37215/
  accessed_at: '2026-10-21T13:03:53.614763Z'
  snapshot_sha256: 6a6b37143f6c6890cbc27e8cd15645d05dce650a7467f692ae6ae91ac728dd38
  support: supports
  locator: 'Complete official compound response: exact identity, names, definition
    or null, chemical data, structure, outgoing relations and relevant incoming context'
  summary: Lanthanum molecular entity CHEBI:37215 is broader chemical context with
    a has-part relation to lanthanum atom; it does not fix an ion charge.
- evidence_id: cation-class
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25213/
  accessed_at: '2026-10-21T13:03:53.528099Z'
  snapshot_sha256: 26bbbf91f6fe1546cb3bd2e3e8f5dd7f7e5ed9aeec58bcc1761ddd4ac8010833
  support: supports
  locator: 'Complete official compound response: exact identity, names, definition
    or null, chemical data, structure, outgoing relations and relevant incoming context'
  summary: Metal cation CHEBI:25213 is a broad class under monoatomic cation and inorganic
    cation, with no single fixed structure.
- evidence_id: la-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:32366463%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T13:04:49.875174Z'
  snapshot_sha256: 831021d81a8641bafa5d3a80485c463efc3ca984bff164573580fcbcb6c63f45
  support: supports
  locator: Verified PMID/DOI when supplied and complete indexed abstract; full article
    not inspected unless separately cited
  summary: PMID:32366463; DOI:10.1074/jbc.RA120.013227. The complete abstract reports
    Methylorubrum extorquens AM1 XoxF1 structures with La3+ and Asp320 coordination,
    with and without PQQ. Asp320 substitution disrupts La3+ coordination and in vivo/in
    vitro function; Ca-bound preparations produced without La3+ show little or no
    activity. This supports a specific La(III)-enzyme context, not neutral La or every
    lanthanum cation.
- evidence_id: la-structure-metadata
  kind: database
  reference: https://data.rcsb.org/rest/v1/core/entry/6OC6
  accessed_at: '2026-10-21T13:04:19.989130Z'
  snapshot_sha256: aa6daf9520623cf3a099135ab7c9a28091a861d9c1ae08107d1e099e20442c6c
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: RCSB entry 6OC6 metadata identifies XoxF with La and PQQ, X-ray resolution
    2.89 Å and the matching primary citation PMID:32366463. The component inventory
    contains LA and PQQ. This is inspected entry metadata, not a coordinate reanalysis
    or newly qualified canonical protein example.
- evidence_id: la-component
  kind: database
  reference: https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/LA
  accessed_at: '2026-10-21T13:04:50.212923Z'
  snapshot_sha256: 8354ee42ab3246b738eb7b9853f7ff54d2b200416a0c3e50c0a41bf05ea753c3
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The actual PDBe CCD LA summary gives La with charge +3, SMILES [La+3] and
    a CHEBI:49701 cross-reference. Its ion identity agrees with the ChEBI La(III)
    entry; the ion is not equivalent to the whole metal-PQQ-protein complex.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  locator: Executed 2026-10-21T13:03:19Z through 2026-10-21T13:03:20Z; exit 0
  accessed_at: '2026-10-21T13:03:20Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml
    data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml
    data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml
    data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
    data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml
  locator: Executed 2026-10-21T13:03:10Z through 2026-10-21T13:04:47Z; exit 0
  accessed_at: '2026-10-21T13:04:47Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
  locator: Executed 2026-10-21T13:03:20Z through 2026-10-21T13:03:20Z; exit 0
  accessed_at: '2026-10-21T13:03:20Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T13:04:47Z through 2026-10-21T13:04:48Z; exit 0
  accessed_at: '2026-10-21T13:04:48Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The copied definition, source identifier and broad class scope agree. The
    class intentionally includes +2 and +3 children; lack of a single formula/structure
    is appropriate rather than an incomplete exact molecule. It must not be silently
    collapsed to La3+.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - trication
  - dication
  topic: Variable-charge lanthanum-cation class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The La3+ XoxF1 study provides positive evidence for one member of this
    broad cation class. Its structure/function results do not establish activity for
    La2+ or every positively charged lanthanum species. A broad class can retain this
    positive member context without claiming every member was tested.
  evidence_ids:
  - la-primary
  - la-structure-metadata
  - la-component
  - trication
  - dication
  topic: Specific ionic member with demonstrated protein function
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The generic requirement does not specify a protein, activity or which ion
    members meet it. Source cofactor classification is authentic, but the inspected
    La3+ experiment is not an all-cation dependence demonstration. This is an explicit
    qualification limit, not proof that the broad source class or every untested member
    is biologically wrong.
  evidence_ids:
  - record
  - schema
  - chemical
  - la-primary
  - trication
  - dication
  topic: Broad class requirement versus member-specific evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The direct cofactor role explains selection and the broader local requirement
    parent. The metal-cation and lanthanum-molecular-entity source parents classify
    chemicals, not automatically protein requirements. No extra local hierarchy edge
    or charge-state merge is inferred.
  evidence_ids:
  - chemical
  - cofactor-role
  - owner
  - local-parent-1
  - element-parent
  - cation-class
  topic: Source role, chemical parents and local requirement parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-8
- area: grounding
  outcome: concern
  summary: CHEBI:231841 denotes a variable-charge class of positively charged lanthanum
    ions, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement.
    The xrefs slot asserts true own-source equivalence. Correct chemical identity,
    source attribution and biological relevance cannot make these two denotations
    equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - la-primary
  - trication
  - dication
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-9
- area: provenance
  outcome: supported
  summary: The captured ChEBI seeder explains role-based candidate selection, the
    synthesized requirement prefix, any appended chemical definition, the source-role
    parent and the chemical xref. Official ChEBI data are CC BY 4.0. The chemical
    attribution does not independently establish the locally synthesized protein requirement.
    Current backend and OLS version 256 are comparison snapshots, with the original
    seed release unknown.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  topic: Source attribution, licence and maintained emitter
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-231841.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:231841 denotes a variable-charge class of positively charged
    lanthanum ions, whereas the local COFACTOR_REQ identifier denotes a protein functional
    requirement. The xrefs slot asserts true own-source equivalence. Correct chemical
    identity, source attribution and biological relevance cannot make these two denotations
    equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - la-primary
  - trication
  - dication
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: A chemical entity or chemical class and a synthesized protein
    functional requirement have different denotations. This major grounding defect
    does not depend on proving that the chemical lacks biological activity.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait
    equality while preserving the supported source identity and provenance. Preserve
    the broad class and distinguish it from its +2 and +3 members. Adjudicate the
    intended activity-relative breadth; the positive La3+ experiment must not silently
    qualify all cations or force replacement of the broad identifier. If an activity-relative
    role and the intended chemical scope are supported, an optional chemical_participants
    association with role COFACTOR may represent the chemical separately; otherwise
    retain provenance and explicit uncertainty without inventing a participant. Do
    not move the same equality to mapped_xrefs, automatically merge distinct charge
    states, require optional protein examples or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_231841
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Regenerated xrefs no longer equates the source chemical with the local protein
    requirement. The intended chemical and activity scope is explicitly adjudicated,
    preserving source attribution.
  - Any optional participant has a supported chemical identity and activity-relative
    role; unqualified biology is not promoted and absence of optional representation
    is not itself a defect.
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml.
  - For maintained writer changes add focused regression coverage and run just audit-writers,
    just lint and just test. Regenerate this existing target through an audited scoped
    route using the maintained seed_chebi_cofactor.py transformation and release-pinned
    inputs. Its emit function skips existing paths unless --force is supplied and
    writes only with --apply; because main traverses the source cohort, do not treat
    a broad --apply --force invocation as a one-record repair. Run full just validate-all
    before merging record changes, recapture changed inputs and save a fresh structured
    review without overwriting this observation.
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
- Member-specific La3+ primary evidence was read through the complete abstract and
  structural/component metadata. No La2+ enzyme experiment was established in this
  bounded source set; that is a qualification limit rather than an exhaustive absence
  claim. No universal ionic abundance or physiological charge distribution is asserted.
tags:
- unreviewed-path-order
- batch-025
- chebi-cofactor
```
