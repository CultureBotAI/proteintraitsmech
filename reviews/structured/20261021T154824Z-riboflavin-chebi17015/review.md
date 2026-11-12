# Review of requires riboflavin

- Review: 20261021T154824Z-riboflavin-chebi17015
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T15:36:05Z
- Finished UTC: 2026-10-21T15:48:24Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Neutral riboflavin identity and positive extracellular redox-shuttle context are supported. Two confirmed majors concern chemical-to-protein equality and the false exclusive free-form distribution statement. Exact protein qualification remains bounded.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 033. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333, the union covers 318 record paths, leaving 429041 before this batch. 33 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml | generated | requires riboflavin |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17015 | Backend/OLS, conjugate/family context, actual origins and primary secretion/model/CSF abstracts were inspected. The free-form finding uses the explicit soluble riboflavin identification, not inference from general metabolomics or failed full text. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Exact chemical identity and state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

CHEBI:17015 resolves to neutral oxidized riboflavin with C17H20N4O6, charge 0 and D-ribityl stereochemistry. Its reciprocal N3-anion link is CHEBI:57986. FMN and FAD are derivatives, not aliases of this exact chemical.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The chemical accession resolves, but it denotes a chemical entity rather than the class of proteins with a requirement for that entity. The emitted xrefs equality conflicts with the schema meaning of source-direct equivalence. An optional typed participant can be used only after an activity-relative role is justified.

### Maintained owner and chemical-source provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The actual owner is scripts/seed_chebi_cofactor.py. It selects role-bearing chemicals, constructs the requirement prefix, appends source chemical prose and emits the chemical accession as an equivalent xref. Current chemical identity and licence are verified; the original seed release and independent protein qualification remain unestablished.

### Exact neutral chemistry and broader families

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The source chemical structure and role parent are coherent. Riboflavin(1-), generic flavin/vitamin B2 and phosphorylated flavin derivatives remain distinct scopes.

### Extracellular riboflavin occurrence and redox function

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

The primary Shewanella experiment positively identifies soluble riboflavin in reactor supernatants and an electron-transfer contribution under the tested conditions. This contradicts an absolute restriction to three listed biological locations while preserving the paper’s organism/assay limits.

### Activity-relative protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17015.

Positive electron shuttling and the source cofactor role are retained. They do not alone qualify an exact non-substrate requirement of a named protein, and the record contains no promoted protein example.

## Findings

### F1: Chemical entity is asserted as an equivalent protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17015.chemical-entity-equivalence.

The local class denotes a functional requirement for riboflavin, while CHEBI:17015 denotes the chemical itself. The source resolves and may assert a cofactor-related role, but that does not make these two classes equivalent. This is a semantic emitter defect, distinct from whether a particular activity can use the compound.

### F2: The definition incorrectly restricts free riboflavin occurrence to three locations

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17015.free-form-distribution.

The target and current ChEBI say that free riboflavin occurs only in retina, whey and urine. The primary Shewanella study identifies soluble riboflavin in biofilm-reactor supernatants, distinct from riboflavin 5-phosphate, providing a concrete additional occurrence. This refutes the unqualified distribution restriction; it does not establish universal secretion or invalidate the neutral chemical identity.

## Recommended Actions And Acceptance Checks

### A1

Curate the maintained ChEBI emitter and this exact output so CHEBI:17015 is not asserted as an equivalent protein-trait xref. Preserve its source identity and bounded role evidence. A chemical_participants entry is optional; if added, adjudicate the role required by that representation against a specific activity and preserve the exact chemical state. If a suitable activity-relative role cannot be supported, retain provenance and uncertainty without inventing a required role. Do not substitute a conjugate or derivative automatically. Use an audited scoped regeneration path: the current ChEBI main loop addresses the selected cohort, skips existing outputs without force, and writes only with apply.

- The chemical is no longer represented as a true equivalent of the protein class; any optional participant has a curator-supported role, exact state and claim-specific evidence. Preserve class-level scope and SEEDED status until separately qualified. Run just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml, and just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml after scoped curation. For maintained writer changes, run focused tests plus just audit-writers, just lint and just test. Run full just validate-all before merge. Capture the changed inputs and create a fresh review; do not rewrite this immutable observation.

### A2

Replace the absolute only-location statement with a sourced, appropriately bounded distribution description or remove the exclusivity. Preserve riboflavin versus FMN/FAD chemistry and the tested microbial context; do not rewrite the whole class as an electron-shuttle requirement.

- No universal three-location restriction remains. Any retained occurrence examples have explicit primary-source and organism/context bounds, and neutral chemical identity remains distinct from phosphorylated derivatives. Run just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml, and just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml after scoped curation. For maintained writer changes, run focused tests plus just audit-writers, just lint and just test. Run full just validate-all before merge. Capture the changed inputs and create a fresh review; do not rewrite this immutable observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; About ChEBI and Licensing paragraphs; verified reused response with original access UTC | supports | The inspected official ChEBI about page describes chemical entities and explicitly licenses its data under CC BY 4.0. This supports chemical-source attribution, not the synthesized protein-requirement assertion. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; ontologyId, version, loaded and config.versionIri; original access UTC retained | supports | The captured OLS ontology metadata identifies ChEBI version 256, loaded on 2026-10-16. It is an OLS release comparison, not a verified release pin for the original seed or the live backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17015/; Exact accession, complete definition/names, chemical_data, default_structure, compound_origins, citations and outgoing ontology relations; broad incoming lists are not used to infer target membership | supports | The source gives the D-ribityl isoalloxazine chemistry, C17H20N4O6, charge 0, and an absolute free-form distribution claim limited to retina, whey and urine. It directly asserts cofactor and multiple metabolite/application roles; current compound_origins also lists E. coli, human blood/saliva/urine/CSF, mango and mouse contexts. These annotations are source assertions, not all independently measured chemical-state qualifications. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17015; Exact term label, description, obo_id, is_obsolete, replacement and chemical annotations | supports | OLS resolves the exact CHEBI:17015 accession as a non-obsolete chemical term, with the same chemical description and stated charge/structure annotations. It does not identify a protein-requirement class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition, null chemical_data/default_structure and outgoing is-a relation | supports | CHEBI:23357 is the abstract cofactor role: a molecule or ion required for enzyme activity, with loosely and tightly attached possibilities. Its fixed chemical_data/default_structure are null and its outgoing parent is biochemical role CHEBI:52206. |
| anion-comparison | https://www.ebi.ac.uk/chebi/backend/api/public/compound/57986/; Definition, chemistry and conjugate-base relation | supports | CHEBI:57986 is the N3-deprotonated conjugate base with one fewer H and net -1; the unchanged ribityl stereochemistry and reciprocal relation support state distinction, not protein equivalence. |
| flavin-family | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30527/; Definition and R-group structure | supports | CHEBI:30527 is the broader N10-substituted dimethylisoalloxazine family, represented with an R group. Its generic graph does not replace the exact ribityl derivative. |
| vitamin-family | https://www.ebi.ac.uk/chebi/backend/api/public/compound/176838/; Definition and null fixed chemistry | supports | The broad vitamin B2 vitamer class includes riboflavin and phosphate derivatives/state variants. This is a family context rather than proof that neutral riboflavin and FMN/FAD are identical. |
| secretion-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18316736%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID and returned bibliographic identifiers; complete indexed abstract inspected. Full text is not claimed unless separately linked. | supports | In poised-electrode Shewanella oneidensis MR-1 and Shewanella sp. MR-4 biofilms, analytical methods identified riboflavin and riboflavin 5-phosphate in supernatants, with riboflavin dominant after sustained incubations. Removal reduced electron transfer by more than 70%, supporting a soluble redox-shuttle role in that system. This directly establishes a free-riboflavin occurrence beyond retina/whey/urine without qualifying every protein or exact bound charge. |
| csf-origin | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A182198%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID and returned bibliographic identifiers; complete indexed abstract inspected. Full text is not claimed unless separately linked. | context_only | The source-linked clinical study assayed riboflavin and other B vitamins in blood and CSF from specified malnutrition/alcoholism patients and controls. The abstract supports study context, but does not resolve analytical free-versus-conjugated riboflavin fractions; it is not the sole basis for the free-form counterexample. |
| ecoli-origin | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID and returned bibliographic identifiers; complete indexed abstract inspected. Full text is not claimed unless separately linked. | context_only | The source-linked E. coli iJO1366 reconstruction combines curated metabolic-network information with gene-knockout/model comparisons. It provides organism/model provenance, not an exact-state binding or riboflavin-cofactor measurement. |
| mouse-origin | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19425150%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID and returned bibliographic identifiers; complete indexed abstract inspected. Full text is not claimed unless separately linked. | context_only | The source-linked mouse work reconstructs a compartmentalized genome-scale metabolic model. Its complete indexed abstract does not establish the target exact chemical population or a particular protein requirement. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml; Executed 2026-10-21T15:37:01Z through 2026-10-21T15:37:02Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml; Executed 2026-10-21T15:37:45Z through 2026-10-21T15:39:21Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml; Executed 2026-10-21T15:37:02Z through 2026-10-21T15:37:02Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T15:39:21Z through 2026-10-21T15:39:23Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The Shewanella article was inspected through its complete indexed primary abstract; attempted PMC full-text responses were empty/challenge bodies and are excluded. No uninspected methods or figures are claimed.
- Food-source ranking and every compound_origins row were not independently validated. The blood/CSF abstract does not distinguish free versus total flavin and is used only as provenance context.
- No universal protein dependence, exclusive organism distribution or protein-bound protonation state is inferred from the positive secretion experiment.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T154824Z-riboflavin-chebi17015
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires riboflavin
started_at: '2026-10-21T15:36:05Z'
finished_at: '2026-10-21T15:48:24Z'
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
summary: Neutral riboflavin identity and positive extracellular redox-shuttle context
  are supported. Two confirmed majors concern chemical-to-protein equality and the
  false exclusive free-form distribution statement. Exact protein qualification remains
  bounded.
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
  - path: data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    sha256: b4102ddd272da29b77b8529b9f9231e570a90642310b326364626076b4030825
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
  selection: Path-order position 4 in batch 033. Fresh main inventory has 429359 records.
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
    b6ee361647a739487903ad0d184297a280189333, the union covers 318 record paths, leaving
    429041 before this batch. 33 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
targets:
- kind: generated
  label: requires riboflavin
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17015
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml
    data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml
    data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml
    data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
    data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Backend/OLS, conjugate/family context, actual origins and primary secretion/model/CSF
    abstracts were inspected. The free-form finding uses the explicit soluble riboflavin
    identification, not inference from general metabolomics or failed full text.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  evidence_ids:
  - licence
  - release
  - chemical
  - chemical-ontology
  - cofactor-role
  - anion-comparison
  - flavin-family
  - vitamin-family
  - secretion-primary
  - csf-origin
  - ecoli-origin
  - mouse-origin
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T15:36:05Z'
  snapshot_sha256: b4102ddd272da29b77b8529b9f9231e570a90642310b326364626076b4030825
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
  accessed_at: '2026-10-21T15:36:05Z'
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
  accessed_at: '2026-10-21T15:36:05Z'
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
  accessed_at: '2026-10-21T15:36:05Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T15:36:05Z'
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
  locator: About ChEBI and Licensing paragraphs; verified reused response with original
    access UTC
  summary: The inspected official ChEBI about page describes chemical entities and
    explicitly licenses its data under CC BY 4.0. This supports chemical-source attribution,
    not the synthesized protein-requirement assertion.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: ontologyId, version, loaded and config.versionIri; original access UTC
    retained
  summary: The captured OLS ontology metadata identifies ChEBI version 256, loaded
    on 2026-10-16. It is an OLS release comparison, not a verified release pin for
    the original seed or the live backend.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17015/
  accessed_at: '2026-10-21T15:36:57.525805Z'
  snapshot_sha256: 22d77dd317d20871798660889140fdc5851e768978599514b6238a8debfd88e3
  support: supports
  locator: Exact accession, complete definition/names, chemical_data, default_structure,
    compound_origins, citations and outgoing ontology relations; broad incoming lists
    are not used to infer target membership
  summary: The source gives the D-ribityl isoalloxazine chemistry, C17H20N4O6, charge
    0, and an absolute free-form distribution claim limited to retina, whey and urine.
    It directly asserts cofactor and multiple metabolite/application roles; current
    compound_origins also lists E. coli, human blood/saliva/urine/CSF, mango and mouse
    contexts. These annotations are source assertions, not all independently measured
    chemical-state qualifications.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17015
  accessed_at: '2026-10-21T15:36:57.531644Z'
  snapshot_sha256: 17f7ac7c03d75b85a96f951321902906266f3ce8fa44faea4814fac46560e3e6
  support: supports
  locator: Exact term label, description, obo_id, is_obsolete, replacement and chemical
    annotations
  summary: OLS resolves the exact CHEBI:17015 accession as a non-obsolete chemical
    term, with the same chemical description and stated charge/structure annotations.
    It does not identify a protein-requirement class.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition, null chemical_data/default_structure and outgoing is-a relation
  summary: 'CHEBI:23357 is the abstract cofactor role: a molecule or ion required
    for enzyme activity, with loosely and tightly attached possibilities. Its fixed
    chemical_data/default_structure are null and its outgoing parent is biochemical
    role CHEBI:52206.'
- evidence_id: anion-comparison
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/57986/
  accessed_at: '2026-10-21T15:36:57.489895Z'
  snapshot_sha256: 75b1e7c7792a2b1e461adf49cde63b700718159edc47e86feaa2dba0bc916285
  support: supports
  locator: Definition, chemistry and conjugate-base relation
  summary: CHEBI:57986 is the N3-deprotonated conjugate base with one fewer H and
    net -1; the unchanged ribityl stereochemistry and reciprocal relation support
    state distinction, not protein equivalence.
- evidence_id: flavin-family
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30527/
  accessed_at: '2026-10-21T15:37:49.315183Z'
  snapshot_sha256: a9190b6419290dfa84513507eeab2a11b503c925af26bef154d25dd67de28bbf
  support: supports
  locator: Definition and R-group structure
  summary: CHEBI:30527 is the broader N10-substituted dimethylisoalloxazine family,
    represented with an R group. Its generic graph does not replace the exact ribityl
    derivative.
- evidence_id: vitamin-family
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/176838/
  accessed_at: '2026-10-21T15:37:49.212333Z'
  snapshot_sha256: 9845fe1a3e2f4b562d4ba3df549caf23b2063e0417864a6ddcd312c2494df2f3
  support: supports
  locator: Definition and null fixed chemistry
  summary: The broad vitamin B2 vitamer class includes riboflavin and phosphate derivatives/state
    variants. This is a family context rather than proof that neutral riboflavin and
    FMN/FAD are identical.
- evidence_id: secretion-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18316736%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:52.496787Z'
  snapshot_sha256: 2bf8b87d3b78feb830f7e95117d716118bb38f5541061776e7ab229d45ec42cd
  support: supports
  locator: Verified PMID and returned bibliographic identifiers; complete indexed
    abstract inspected. Full text is not claimed unless separately linked.
  summary: In poised-electrode Shewanella oneidensis MR-1 and Shewanella sp. MR-4
    biofilms, analytical methods identified riboflavin and riboflavin 5-phosphate
    in supernatants, with riboflavin dominant after sustained incubations. Removal
    reduced electron transfer by more than 70%, supporting a soluble redox-shuttle
    role in that system. This directly establishes a free-riboflavin occurrence beyond
    retina/whey/urine without qualifying every protein or exact bound charge.
- evidence_id: csf-origin
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A182198%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:52.504132Z'
  snapshot_sha256: d598fd3ce312729536eda9066c65be9af2706a5d0881fbc113f579161eb31b6f
  support: context_only
  locator: Verified PMID and returned bibliographic identifiers; complete indexed
    abstract inspected. Full text is not claimed unless separately linked.
  summary: The source-linked clinical study assayed riboflavin and other B vitamins
    in blood and CSF from specified malnutrition/alcoholism patients and controls.
    The abstract supports study context, but does not resolve analytical free-versus-conjugated
    riboflavin fractions; it is not the sole basis for the free-form counterexample.
- evidence_id: ecoli-origin
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:52.689236Z'
  snapshot_sha256: e25a797a813b88b0e3053e41aacefa22b641206af4570c409c52515a8233a3e0
  support: context_only
  locator: Verified PMID and returned bibliographic identifiers; complete indexed
    abstract inspected. Full text is not claimed unless separately linked.
  summary: The source-linked E. coli iJO1366 reconstruction combines curated metabolic-network
    information with gene-knockout/model comparisons. It provides organism/model provenance,
    not an exact-state binding or riboflavin-cofactor measurement.
- evidence_id: mouse-origin
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19425150%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:53.047078Z'
  snapshot_sha256: ac9747be911a86fd9ddca3187da9a837bb098a6e33461797277ff5a1e4ad0fcd
  support: context_only
  locator: Verified PMID and returned bibliographic identifiers; complete indexed
    abstract inspected. Full text is not claimed unless separately linked.
  summary: The source-linked mouse work reconstructs a compartmentalized genome-scale
    metabolic model. Its complete indexed abstract does not establish the target exact
    chemical population or a particular protein requirement.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  locator: Executed 2026-10-21T15:37:01Z through 2026-10-21T15:37:02Z; exit 0
  accessed_at: '2026-10-21T15:37:02Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml
    data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml
    data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml
    data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
    data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml
  locator: Executed 2026-10-21T15:37:45Z through 2026-10-21T15:39:21Z; exit 0
  accessed_at: '2026-10-21T15:39:21Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
  locator: Executed 2026-10-21T15:37:02Z through 2026-10-21T15:37:02Z; exit 0
  accessed_at: '2026-10-21T15:37:02Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T15:39:21Z through 2026-10-21T15:39:23Z; exit 0
  accessed_at: '2026-10-21T15:39:23Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  topic: Exact chemical identity and state
  summary: CHEBI:17015 resolves to neutral oxidized riboflavin with C17H20N4O6, charge
    0 and D-ribityl stereochemistry. Its reciprocal N3-anion link is CHEBI:57986.
    FMN and FAD are derivatives, not aliases of this exact chemical.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-5
- area: grounding
  outcome: concern
  topic: Chemical entity versus protein-requirement equivalence
  summary: The chemical accession resolves, but it denotes a chemical entity rather
    than the class of proteins with a requirement for that entity. The emitted xrefs
    equality conflicts with the schema meaning of source-direct equivalence. An optional
    typed participant can be used only after an activity-relative role is justified.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-6
- area: provenance
  outcome: supported
  topic: Maintained owner and chemical-source provenance
  summary: The actual owner is scripts/seed_chebi_cofactor.py. It selects role-bearing
    chemicals, constructs the requirement prefix, appends source chemical prose and
    emits the chemical accession as an equivalent xref. Current chemical identity
    and licence are verified; the original seed release and independent protein qualification
    remain unestablished.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  topic: Exact neutral chemistry and broader families
  summary: The source chemical structure and role parent are coherent. Riboflavin(1-),
    generic flavin/vitamin B2 and phosphorylated flavin derivatives remain distinct
    scopes.
  evidence_ids:
  - chemical
  - anion-comparison
  - flavin-family
  - vitamin-family
  - cofactor-role
  - local-parent-1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-8
- area: evidence
  outcome: supported
  topic: Extracellular riboflavin occurrence and redox function
  summary: The primary Shewanella experiment positively identifies soluble riboflavin
    in reactor supernatants and an electron-transfer contribution under the tested
    conditions. This contradicts an absolute restriction to three listed biological
    locations while preserving the paper’s organism/assay limits.
  evidence_ids:
  - secretion-primary
  - record
  - chemical
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-9
- area: representation
  outcome: unknown
  topic: Activity-relative protein requirement
  summary: Positive electron shuttling and the source cofactor role are retained.
    They do not alone qualify an exact non-substrate requirement of a named protein,
    and the record contains no promoted protein example.
  evidence_ids:
  - schema
  - chemical
  - secretion-primary
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17015.chemical-entity-equivalence
  severity: major
  category: grounding
  title: Chemical entity is asserted as an equivalent protein requirement
  description: The local class denotes a functional requirement for riboflavin, while
    CHEBI:17015 denotes the chemical itself. The source resolves and may assert a
    cofactor-related role, but that does not make these two classes equivalent. This
    is a semantic emitter defect, distinct from whether a particular activity can
    use the compound.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - cofactor-role
  - secretion-primary
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The record equates distinct entity types; this materially
    misstates grounding even where chemical identity and a positive activity context
    are correct.
  certainty: confirmed
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-17015.free-form-distribution
  severity: major
  category: scope
  title: The definition incorrectly restricts free riboflavin occurrence to three
    locations
  description: The target and current ChEBI say that free riboflavin occurs only in
    retina, whey and urine. The primary Shewanella study identifies soluble riboflavin
    in biofilm-reactor supernatants, distinct from riboflavin 5-phosphate, providing
    a concrete additional occurrence. This refutes the unqualified distribution restriction;
    it does not establish universal secretion or invalidate the neutral chemical identity.
  evidence_ids:
  - record
  - chemical
  - secretion-primary
  field_paths:
  - definition
  normalization_reason: The explicit exclusivity materially misstates biological distribution,
    so this is a scope error rather than a spelling-only background defect.
  certainty: confirmed
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: 'Curate the maintained ChEBI emitter and this exact output so CHEBI:17015
    is not asserted as an equivalent protein-trait xref. Preserve its source identity
    and bounded role evidence. A chemical_participants entry is optional; if added,
    adjudicate the role required by that representation against a specific activity
    and preserve the exact chemical state. If a suitable activity-relative role cannot
    be supported, retain provenance and uncertainty without inventing a required role.
    Do not substitute a conjugate or derivative automatically. Use an audited scoped
    regeneration path: the current ChEBI main loop addresses the selected cohort,
    skips existing outputs without force, and writes only with apply.'
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The chemical is no longer represented as a true equivalent of the protein class;
    any optional participant has a curator-supported role, exact state and claim-specific
    evidence. Preserve class-level scope and SEEDED status until separately qualified.
    Run just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml,
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    after scoped curation. For maintained writer changes, run focused tests plus just
    audit-writers, just lint and just test. Run full just validate-all before merge.
    Capture the changed inputs and create a fresh review; do not rewrite this immutable
    observation.
- action_id: A2
  description: Replace the absolute only-location statement with a sourced, appropriately
    bounded distribution description or remove the exclusivity. Preserve riboflavin
    versus FMN/FAD chemistry and the tested microbial context; do not rewrite the
    whole class as an electron-shuttle requirement.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17015
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - No universal three-location restriction remains. Any retained occurrence examples
    have explicit primary-source and organism/context bounds, and neutral chemical
    identity remains distinct from phosphorylated derivatives. Run just validate data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml,
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    after scoped curation. For maintained writer changes, run focused tests plus just
    audit-writers, just lint and just test. Run full just validate-all before merge.
    Capture the changed inputs and create a fresh review; do not rewrite this immutable
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
- The Shewanella article was inspected through its complete indexed primary abstract;
  attempted PMC full-text responses were empty/challenge bodies and are excluded.
  No uninspected methods or figures are claimed.
- Food-source ranking and every compound_origins row were not independently validated.
  The blood/CSF abstract does not distinguish free versus total flavin and is used
  only as provenance context.
- No universal protein dependence, exclusive organism distribution or protein-bound
  protonation state is inferred from the positive secretion experiment.
tags:
- unreviewed-path-order
- batch-033
- chebi-cofactor
```
