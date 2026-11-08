# Review of requires pantethine

- Review: 20261021T142844Z-pantethine-chebi31959
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T14:15:15Z
- Finished UTC: 2026-10-21T14:28:44Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Pantethine identity and source coenzyme role are supported. One confirmed major concerns chemical-to-protein equivalence; positive metabolic effects remain distinct from a directly qualified unchanged-pantethine requirement.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 029. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099, the union covers 278 record paths, leaving 429081 before this batch. 29 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml | generated | requires pantethine |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_31959 | Current backend/OLS resolve pantethine’s R,R disulfide and authentic coenzyme role. Structural parents and reduced-thiol comparison were inspected, with complete relevant primary abstracts and the mouse paper’s full main text. Source licence and release metadata were verified. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Pantethine disulfide constitution and stereochemistry

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The copied chemical definition and exact graph agree on the neutral (R,R) disulfide containing two pantetheine units. It is neither the reduced thiol pantetheine nor phosphorylated PPant or CoA. The source structural functional-parent relation to pantothenic acid does not collapse these chemicals.

### Pantethine name and copied source definition

nomenclature: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The local pantethine label and disulfide description agree with official chemical identity. The source and article sometimes use broader thiol-family language; the inspected S–S graph and explicitly reduced experimental comparator govern the exact state, without importing an uncopied external wording defect.

### Positive metabolic utilization and bounded enzyme-associated effects

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The Drosophila and bacterial studies show positive precursor/rescue biology, and the mouse paper reports preservation of measured activity after treatment. Its isolated-mitochondria results specifically distinguish reduced pantetheine from pantethine. These observations support biological relevance while preserving organism, treatment and chemical-state boundaries.

### Coenzyme role versus activity-relative non-substrate requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The ChEBI coenzyme assertion is authentic. The inspected primary work does not independently establish a particular enzyme’s obligatory use of unchanged pantethine as a non-substrate coenzyme: precursor utilization, restoration after treatment and reduced-thiol protection are different predicates. Those alternate roles do not prove absence of all pantethine coenzyme activity. Further activity-specific adjudication is needed before optional protein or participant qualification.

### Direct coenzyme role and local coenzyme parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The direct coenzyme role and coenzyme-to-cofactor ancestry explain the local coenzyme-requirement parent and its captured broader chain. Organic-disulfide ancestry and the pantothenic-acid functional parent describe chemical structure, not equivalent protein classes. A change of local parent is not inferred merely from metabolic precursor activity.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

CHEBI:31959 denotes the neutral, stereospecified pantethine disulfide, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The current schema reserves xrefs for true own-source equivalence. Chemical identity and an authentic source role or positive biological activity do not make these distinct entity types equivalent.

### Maintained owner, source attribution, release and licence

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_31959.

The inspected ChEBI seeder selects chemicals through the cofactor-role subtree, synthesizes the requirement prefix and appends available chemical prose. The captured direct cofactor or coenzyme role explains the local parent. ChEBI data are CC BY 4.0, but source attribution does not independently establish the synthesized protein requirement or pin the original seed release.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-31959.chemical-entity-equivalence.

CHEBI:31959 denotes the neutral, stereospecified pantethine disulfide, whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement. The current schema reserves xrefs for true own-source equivalence. Chemical identity and an authentic source role or positive biological activity do not make these distinct entity types equivalent.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so a chemical association is not emitted as protein-trait equality. Preserve the S–S dimer and specified R centres. Keep the reduced pantetheine comparator, free PPant, CoA and in vivo precursor effects distinct; adjudicate an actual coenzyme requirement before treating unchanged pantethine as an activity-level COFACTOR. Preserve chemical provenance and adjudicate the activity-relative non-substrate premise before any optional chemical_participants association with role COFACTOR. If identity, scope or role remains unresolved, retain explicit uncertainty without inventing a participant. Do not move the same false equality to mapped_xrefs, require optional protein examples or promote native status.

- Regenerated xrefs no longer equates a chemical source entity or chemical class with a protein functional requirement; source attribution remains traceable.
- Any optional typed participant follows identity adjudication and has a supported activity-relative role. Free chemical, protein-attached group, biosynthetic substrate and vitamin-family scopes are not silently interchanged.
- After scoped regeneration run just validate data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml. If identity repair changes the path, apply the same checks to the approved replacement and verify that stale references are reconciled.
- For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Use an audited scoped existing-record route with pinned ChEBI inputs: emit skips existing files unless --force is supplied and writes only with --apply, while main traverses a cohort, so broad --apply --force is not a one-record repair. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing; reused bytes digest verified and original access UTC retained | supports | The official Introduction describes chemical entities, groups and classes; Licensing establishes CC BY 4.0 for ChEBI data. This supports chemical source attribution, not independent protein-requirement evidence or terms for an uninspected external alignment table. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. The live backend and this ontology version are separate comparison snapshots; neither identifies the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/31959/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:31959 is pantethine, C22H42N4O8S2, net 0, with an S–S bridge and two specified R-configured pantoate stereocentres. Its definition describes two pantothenic-acid units amide-linked to a cysteamine-disulfide bridge. Direct roles are coenzyme and nutraceutical; outgoing relations include organic-disulfide ancestry and functional parent pantothenic acid CHEBI:7916. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:31959; Exact label, description, synonyms, is_obsolete, formula/charge and structural annotations | supports | The nonobsolete OLS CHEBI:31959 term resolves the exact source name, definition or its absence, synonyms and available chemical annotations. These agree with backend identity; chemical source resolution does not establish equivalence to a protein requirement class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 is a role for an organic molecule or ion required by an enzyme for activity, loosely or tightly attached. Its outgoing parent is biochemical role CHEBI:52206; a chemical role is distinct from a class of proteins requiring the chemical. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Inspected source response captured at the recorded UTC time | supports | CHEBI:52206 defines a role played by a molecular entity or part within a biochemical context. It does not by itself establish a specific protein requirement. |
| coenzyme-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23354 defines a low-molecular-weight non-protein compound participating as a dissociable group/electron donor or acceptor and is a cofactor subclass. The authentic role is not itself proof of an activity-specific non-substrate protein requirement. |
| disulfide-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35489/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:35489 is organic disulfide, RSSR′, with a generic S–S graph. It supports pantethine’s disulfide constitution without identifying pantetheine as the same molecule. |
| acid-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/7916/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:7916 is stereochemically unspecified pantothenic acid, C9H17NO5, net 0, an amide of pantoic acid and beta-alanine. It is pantethine’s structural functional parent, not the complete disulfide. |
| thiol-comparison | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16753/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:16753 is pantetheine, C11H22N2O4S, net 0, specified R configuration and a terminal SH group. It is the distinct reduced thiol monomer, not pantethine’s S–S dimer. |
| nutraceutical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/50733/; Exact identity, definition, names, chemical_data/default_structure, complete outgoing relations and relevant incoming chemical context | supports | CHEBI:50733 describes a formulated nutrient product and has drug ancestry. This is an application-role context, not proof of a required enzyme cofactor. |
| fly-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:20351285%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected unless separately cited | supports | PMID:20351285; DOI:10.1073/pnas.0912105107. The complete primary abstract reports pantethine feeding restoring CoA levels and multiple phenotypes in a Drosophila pantothenate-kinase impairment model, with evidence for its use as a CoA-biosynthetic precursor. These are scoped metabolic effects, not a direct non-substrate enzyme requirement. |
| bacterial-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:21551303%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected unless separately cited | supports | PMID:21551303; DOI:10.1128/JB.00334-11. The complete abstract reports E. coli pantethine utilization bypassing coaBC deficiency, unlike P. aeruginosa, and connects this difference to endogenous pantothenate-kinase substrate specificity. It establishes organism-dependent metabolic utilization, not universal pathway bypass or protein-cofactor membership. |
| mouse-abstract | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:20416081%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed primary abstract; full article not inspected unless separately cited | supports | PMID:20416081; DOI:10.1186/1471-2202-11-51. The complete abstract reports pantethine-associated preservation of dehydrogenase activity and mitochondrial/ketone-body outcomes in an MPTP mouse model. The complete main text separately distinguishes pantethine treatment from reduced-pantetheine additions to isolated mitochondria. |
| mouse-full | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2880308/fullTextXML; Methods: Animals and treatment; Mitochondrial function. Results: L-3-hydroxybutyryl-CoA dehydrogenase activity and circulating KB levels; Mitochondrial activity; Figures4–5. Discussion; complete main text inspected | supports | The complete main text reports in vivo D-pantethine treatment and explicitly describes TCEP reduction to pantetheine for comparison. Results/Mitochondrial activity report isolated-mitochondria protection by reduced pantetheine, while pantethine itself had no effect under those in vitro conditions. Discussion allows changes in enzyme amount and metabolites to contribute. Positive treatment effects are retained without converting them to direct obligatory pantethine-coenzyme activity. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml; Executed 2026-10-21T14:16:18Z through 2026-10-21T14:16:19Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml; Executed 2026-10-21T14:16:10Z through 2026-10-21T14:17:43Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml; Executed 2026-10-21T14:16:19Z through 2026-10-21T14:16:19Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T14:17:43Z through 2026-10-21T14:17:44Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The complete mouse-paper main text was inspected; the Drosophila and bacterial papers were read through complete indexed abstracts. The attempted bacterial full-text endpoint failed and supplies no evidence. Other source-linked clinical/pharmacology abstracts were inspected for context but do not establish an exact enzyme requirement; the monograph has no indexed abstract. No universal role exclusion, clinical recommendation or new protein qualification is claimed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T142844Z-pantethine-chebi31959
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires pantethine
started_at: '2026-10-21T14:15:15Z'
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
summary: Pantethine identity and source coenzyme role are supported. One confirmed
  major concerns chemical-to-protein equivalence; positive metabolic effects remain
  distinct from a directly qualified unchanged-pantethine requirement.
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
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
    sha256: 6aad18531465d2dbaf4f5e6fb64ac9c3b53efac22b67e89e299c08c64db9713a
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
  selection: Path-order position 8 in batch 029. Fresh main inventory has 429359 records.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
targets:
- kind: generated
  label: requires pantethine
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_31959
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current backend/OLS resolve pantethine’s R,R disulfide and authentic coenzyme
    role. Structural parents and reduced-thiol comparison were inspected, with complete
    relevant primary abstracts and the mouse paper’s full main text. Source licence
    and release metadata were verified.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  evidence_ids:
  - licence
  - release
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - coenzyme-role
  - disulfide-parent
  - acid-parent
  - thiol-comparison
  - nutraceutical-role
  - fly-primary
  - bacterial-primary
  - mouse-abstract
  - mouse-full
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T14:15:15Z'
  snapshot_sha256: 6aad18531465d2dbaf4f5e6fb64ac9c3b53efac22b67e89e299c08c64db9713a
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
  accessed_at: '2026-10-21T14:15:15Z'
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
  accessed_at: '2026-10-21T14:15:15Z'
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
  accessed_at: '2026-10-21T14:15:15Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T14:15:15Z'
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/31959/
  accessed_at: '2026-10-21T14:16:06.239770Z'
  snapshot_sha256: 1cfdfcf55f093677e242a68732d1b90a5ce9852f1f4acaa22d5a84904c5d22b9
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:31959 is pantethine, C22H42N4O8S2, net 0, with an S–S bridge and
    two specified R-configured pantoate stereocentres. Its definition describes two
    pantothenic-acid units amide-linked to a cysteamine-disulfide bridge. Direct roles
    are coenzyme and nutraceutical; outgoing relations include organic-disulfide ancestry
    and functional parent pantothenic acid CHEBI:7916.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:31959
  accessed_at: '2026-10-21T14:16:06.807576Z'
  snapshot_sha256: 9589bc1805b5680415de2b4729d15b4878dd1436a16f22393e5df106f1a4af43
  support: supports
  locator: Exact label, description, synonyms, is_obsolete, formula/charge and structural
    annotations
  summary: The nonobsolete OLS CHEBI:31959 term resolves the exact source name, definition
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
- evidence_id: coenzyme-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T11:38:19.854129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:23354 defines a low-molecular-weight non-protein compound participating
    as a dissociable group/electron donor or acceptor and is a cofactor subclass.
    The authentic role is not itself proof of an activity-specific non-substrate protein
    requirement.
- evidence_id: disulfide-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35489/
  accessed_at: '2026-10-21T14:16:53.911876Z'
  snapshot_sha256: bcd4c88e1e0f692185b2b8b9bc6b28e1f14d7a2a350ffb4841384947d201aa8e
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:35489 is organic disulfide, RSSR′, with a generic S–S graph. It supports
    pantethine’s disulfide constitution without identifying pantetheine as the same
    molecule.
- evidence_id: acid-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/7916/
  accessed_at: '2026-10-21T14:16:53.777677Z'
  snapshot_sha256: e69f24d921cc94937172a65434bb0d86cae0046c1c7690976408f50b91449fc3
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:7916 is stereochemically unspecified pantothenic acid, C9H17NO5,
    net 0, an amide of pantoic acid and beta-alanine. It is pantethine’s structural
    functional parent, not the complete disulfide.
- evidence_id: thiol-comparison
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16753/
  accessed_at: '2026-10-21T14:19:27.313569Z'
  snapshot_sha256: bdad2c02502763fe63a6f983e34b85109fc81d810deac3d8123ddafc05c5ab31
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:16753 is pantetheine, C11H22N2O4S, net 0, specified R configuration
    and a terminal SH group. It is the distinct reduced thiol monomer, not pantethine’s
    S–S dimer.
- evidence_id: nutraceutical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/50733/
  accessed_at: '2026-10-21T14:16:53.844393Z'
  snapshot_sha256: 0b78cc45ccad10fa949d740a5c55a4e6aedf32ca0647f3516ffa8040e198a0a3
  support: supports
  locator: Exact identity, definition, names, chemical_data/default_structure, complete
    outgoing relations and relevant incoming chemical context
  summary: CHEBI:50733 describes a formulated nutrient product and has drug ancestry.
    This is an application-role context, not proof of a required enzyme cofactor.
- evidence_id: fly-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:20351285%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:16:55.565550Z'
  snapshot_sha256: a56ddeb7c7fbebb515dbeb5f721fe15df1f04ed5047661b869a6f08a09f87f52
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected unless separately cited
  summary: PMID:20351285; DOI:10.1073/pnas.0912105107. The complete primary abstract
    reports pantethine feeding restoring CoA levels and multiple phenotypes in a Drosophila
    pantothenate-kinase impairment model, with evidence for its use as a CoA-biosynthetic
    precursor. These are scoped metabolic effects, not a direct non-substrate enzyme
    requirement.
- evidence_id: bacterial-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:21551303%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:16:56.057769Z'
  snapshot_sha256: 432d5ac4f5bbf66473a95095eb5d6ee1f5f10bd7f3bc8293460c05765359729b
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected unless separately cited
  summary: PMID:21551303; DOI:10.1128/JB.00334-11. The complete abstract reports E.
    coli pantethine utilization bypassing coaBC deficiency, unlike P. aeruginosa,
    and connects this difference to endogenous pantothenate-kinase substrate specificity.
    It establishes organism-dependent metabolic utilization, not universal pathway
    bypass or protein-cofactor membership.
- evidence_id: mouse-abstract
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:20416081%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:16:55.710135Z'
  snapshot_sha256: b3fda4511612207abf6aa019257ae747244d67fff68baf559bc898de5bbb6ca8
  support: supports
  locator: Verified PMID/DOI and complete indexed primary abstract; full article not
    inspected unless separately cited
  summary: PMID:20416081; DOI:10.1186/1471-2202-11-51. The complete abstract reports
    pantethine-associated preservation of dehydrogenase activity and mitochondrial/ketone-body
    outcomes in an MPTP mouse model. The complete main text separately distinguishes
    pantethine treatment from reduced-pantetheine additions to isolated mitochondria.
- evidence_id: mouse-full
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2880308/fullTextXML
  accessed_at: '2026-10-21T14:19:41.365577Z'
  snapshot_sha256: 46951e885d5f5a58060da0a6aeb4de31f793896140d3ac352ea966a8ea226d6c
  support: supports
  locator: 'Methods: Animals and treatment; Mitochondrial function. Results: L-3-hydroxybutyryl-CoA
    dehydrogenase activity and circulating KB levels; Mitochondrial activity; Figures4–5.
    Discussion; complete main text inspected'
  summary: The complete main text reports in vivo D-pantethine treatment and explicitly
    describes TCEP reduction to pantetheine for comparison. Results/Mitochondrial
    activity report isolated-mitochondria protection by reduced pantetheine, while
    pantethine itself had no effect under those in vitro conditions. Discussion allows
    changes in enzyme amount and metabolites to contribute. Positive treatment effects
    are retained without converting them to direct obligatory pantethine-coenzyme
    activity.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  locator: Executed 2026-10-21T14:16:18Z through 2026-10-21T14:16:19Z; exit 0
  accessed_at: '2026-10-21T14:16:19Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml
  locator: Executed 2026-10-21T14:16:19Z through 2026-10-21T14:16:19Z; exit 0
  accessed_at: '2026-10-21T14:16:19Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The copied chemical definition and exact graph agree on the neutral (R,R)
    disulfide containing two pantetheine units. It is neither the reduced thiol pantetheine
    nor phosphorylated PPant or CoA. The source structural functional-parent relation
    to pantothenic acid does not collapse these chemicals.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - disulfide-parent
  - acid-parent
  - thiol-comparison
  topic: Pantethine disulfide constitution and stereochemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-5
- area: nomenclature
  outcome: supported
  summary: The local pantethine label and disulfide description agree with official
    chemical identity. The source and article sometimes use broader thiol-family language;
    the inspected S–S graph and explicitly reduced experimental comparator govern
    the exact state, without importing an uncopied external wording defect.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - mouse-full
  topic: Pantethine name and copied source definition
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The Drosophila and bacterial studies show positive precursor/rescue biology,
    and the mouse paper reports preservation of measured activity after treatment.
    Its isolated-mitochondria results specifically distinguish reduced pantetheine
    from pantethine. These observations support biological relevance while preserving
    organism, treatment and chemical-state boundaries.
  evidence_ids:
  - fly-primary
  - bacterial-primary
  - mouse-abstract
  - mouse-full
  - thiol-comparison
  topic: Positive metabolic utilization and bounded enzyme-associated effects
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: 'The ChEBI coenzyme assertion is authentic. The inspected primary work
    does not independently establish a particular enzyme’s obligatory use of unchanged
    pantethine as a non-substrate coenzyme: precursor utilization, restoration after
    treatment and reduced-thiol protection are different predicates. Those alternate
    roles do not prove absence of all pantethine coenzyme activity. Further activity-specific
    adjudication is needed before optional protein or participant qualification.'
  evidence_ids:
  - record
  - schema
  - chemical
  - coenzyme-role
  - fly-primary
  - bacterial-primary
  - mouse-full
  topic: Coenzyme role versus activity-relative non-substrate requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct coenzyme role and coenzyme-to-cofactor ancestry explain the
    local coenzyme-requirement parent and its captured broader chain. Organic-disulfide
    ancestry and the pantothenic-acid functional parent describe chemical structure,
    not equivalent protein classes. A change of local parent is not inferred merely
    from metabolic precursor activity.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - coenzyme-role
  - cofactor-role
  - disulfide-parent
  - acid-parent
  topic: Direct coenzyme role and local coenzyme parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: CHEBI:31959 denotes the neutral, stereospecified pantethine disulfide,
    whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement.
    The current schema reserves xrefs for true own-source equivalence. Chemical identity
    and an authentic source role or positive biological activity do not make these
    distinct entity types equivalent.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - coenzyme-role
  - thiol-comparison
  - mouse-full
  - bacterial-primary
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-31959.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:31959 denotes the neutral, stereospecified pantethine disulfide,
    whereas the local COFACTOR_REQ record denotes a proposed protein functional requirement.
    The current schema reserves xrefs for true own-source equivalence. Chemical identity
    and an authentic source role or positive biological activity do not make these
    distinct entity types equivalent.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - coenzyme-role
  - thiol-comparison
  - mouse-full
  - bacterial-primary
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
    is not emitted as protein-trait equality. Preserve the S–S dimer and specified
    R centres. Keep the reduced pantetheine comparator, free PPant, CoA and in vivo
    precursor effects distinct; adjudicate an actual coenzyme requirement before treating
    unchanged pantethine as an activity-level COFACTOR. Preserve chemical provenance
    and adjudicate the activity-relative non-substrate premise before any optional
    chemical_participants association with role COFACTOR. If identity, scope or role
    remains unresolved, retain explicit uncertainty without inventing a participant.
    Do not move the same false equality to mapped_xrefs, require optional protein
    examples or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_31959
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
  - After scoped regeneration run just validate data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml.
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
- The complete mouse-paper main text was inspected; the Drosophila and bacterial papers
  were read through complete indexed abstracts. The attempted bacterial full-text
  endpoint failed and supplies no evidence. Other source-linked clinical/pharmacology
  abstracts were inspected for context but do not establish an exact enzyme requirement;
  the monograph has no indexed abstract. No universal role exclusion, clinical recommendation
  or new protein qualification is claimed.
tags:
- unreviewed-path-order
- batch-029
- chebi-cofactor
```
