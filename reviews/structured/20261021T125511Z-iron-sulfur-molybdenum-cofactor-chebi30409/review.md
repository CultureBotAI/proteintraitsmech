# Review of requires iron-sulfur-molybdenum cofactor

- Review: 20261021T125511Z-iron-sulfur-molybdenum-cofactor-chebi30409
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:45:45Z
- Finished UTC: 2026-10-21T12:55:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

FeMoco composition, central carbide and bounded positive nitrogenase context are supported. Findings are confirmed major chemical-to-protein-trait equivalence and minor mismatched composition delimiters. Exact bound net charge, full proton inventory and universal protein requirements are not inferred.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 024. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242) covers 228 record paths, leaving 429131 before this batch. 24 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml | generated | requires iron-sulfur-molybdenum cofactor |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_30409 | Official ChEBI/OLS resolve CHEBI:30409 and its direct cofactor role; local owner and source licence resolve. Exact chemical scope and bounded positive primary context are separated from protein-trait equivalence and universal state/requirement claims. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### FeMoco composition and central carbide

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The source identifier and main chemical definition consistently denote the Mo:7Fe:9S:C-homocitrate cofactor, with experimental support for central carbide. The separate cluster-part entry is not the full molecule. Backend net charge −6 and individual formal atom charges are source encodings, not independently measured universal metal valences or catalytic-state charge.

### Positive nitrogenase and retained-cofactor evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The primary central-atom, biosynthetic and isotope-retention abstracts support FeMoco chemistry, while the official EC entry supplies the molybdenum-dependent enzyme context. The retained carbide is distinguished from substrate carbon and from proposed mechanistic details.

### Protein requirement and catalytic-state scope

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

Source cofactor role and positive FeMoco biology are preserved. No release-pinned protein example or exact bound net charge, complete proton inventory or homocitrate stereochemical assignment is newly qualified here. The description of EC 1.18.6.1 is not expanded to all nitrogenase isoforms.

### Maintained ChEBI emitter and source fidelity

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

scripts/seed_chebi_cofactor.py synthesizes the requires-label and requirement assertion from the chemical entry and direct cofactor role. Current ChEBI/OLS, official licensing and the local registry resolve that provenance. The original source release remains unidentified; current source resolution is not independent protein qualification.

### Role-derived parent and chemical hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The direct chemical cofactor role explains candidate selection and the broad local cofactor-requirement parent. Chemical structural parents remain distinct from protein-trait hierarchy. Parent resolution does not certify that parent's own equivalence semantics or every protein requirement.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_30409.

The source chemical and the synthesized class of proteins requiring it have different denotations. A direct has-role assertion, exact identifier or positive enzyme context does not establish true own-source equivalence between these entity types. 

## Findings

### F1: Cluster-composition notation has mismatched delimiters

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-30409.composition-delimiter.

The copied composition opens with a brace and closes with a square bracket in {Mo:7Fe:9S:C]:homocitrate. The atom counts and carbide identity remain intelligible and are supported; this is a source-inherited notation defect, not a different cofactor.

### F2: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-30409.chemical-entity-equivalence.

The target xrefs treats CHEBI:30409 as equivalent to a protein functional-requirement class, although the source denotes a chemical entity. This violates the schema's true-equivalence semantics independently of the eventual activity-relative requirement decision. 

## Recommended Actions And Acceptance Checks

### A1

Correct the composition delimiters in the maintained source override/definition transformation while retaining the supported atom counts and homocitrate context. Preserve attribution and avoid changing chemical state or adding unsupported stereochemistry.

- The regenerated composition uses matched delimiters and retains Mo:7Fe:9S:C plus homocitrate. No chemical-identity, charge-state or protein-membership change is introduced by the editorial repair.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

### A2

correct build in scripts/seed_chebi_cofactor.py to preserve chemical provenance without asserting chemical-to-protein-class equality. Adjudicate the exact chemical scope and required activity-relative ChemicalParticipant.role before adding any typed participant. If a typed role cannot be supported, retain provenance and explicit uncertainty without inventing one. Do not move the equality into mapped_xrefs or automatically promote a protein example.

- The regenerated record no longer asserts a chemical entity as equivalent to its requirement class. Any typed participant has a curator-adjudicated identity and role; otherwise source provenance and uncertainty remain explicit.
- Use an audited regeneration route for this existing target and focused transformation coverage. No native status or per-protein requirement is automatically promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; verified reused body with original access UTC | supports | The inspected official ChEBI Introduction and Licensing sections describe a chemical-entity/role resource licensed CC BY 4.0. This supports chemical-source attribution, not equivalence to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16. Its actual original access UTC is retained. This does not identify the live backend release or the exact release used to seed the local record. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30409/; Complete identity, names, definition or null, formula/charge, default structure, origins/citations and outgoing relations | supports | CHEBI:30409 resolves to iron-sulfur-molybdenum cofactor. Its definition identifies a Mo:7Fe:9S:C cluster with homocitrate and central carbide(4−), but contains mismatched opening brace and closing bracket. The backend reports C8H12Fe7MoO7S9, charge −6, and central [C-4] in the structure. Formal SMILES/InChI bookkeeping is not an experimental assignment of every metal oxidation state or the net charge of every protein-bound catalytic state. The depiction does not supply a homocitrate absolute stereodescriptor. Direct cofactor role, molybdenum-coordination-entity ancestry and a has-part relation to iron-sulfur-molybdenum cluster are asserted. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:30409; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete CHEBI:30409 identifier and source name. Its source definition and annotations were inspected, including the copied wording defects. Resolution is not independent validation of all source science or protein-trait equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified reused original UTC | supports | Cofactor CHEBI:23357 denotes an organic molecule or ion required by an enzyme for activity, attached loosely or tightly, and is a biochemical role. A source has-role assertion supplies positive candidate context without itself equating a molecule/ion to a protein class. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified reused original UTC | supports | Biochemical role CHEBI:52206 is a biological role played by an entity or part in a biochemical context. It is the asserted parent of cofactor, not a molecular identity or independently qualified protein requirement. |
| context-35202 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35202/; Exact identity, definition or null, chemical data and complete outgoing relations; relevant incoming child/part links | supports | Molybdenum coordination entity CHEBI:35202 is a broad chemical class under transition element coordination entity and molybdenum molecular entity, with null definition and fixed chemical fields. It is not a protein-requirement class. |
| context-48796 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/48796/; Exact identity, definition or null, chemical data and complete outgoing relations; relevant incoming child/part links | supports | Iron-sulfur-molybdenum cluster CHEBI:48796 is defined by seven iron atoms, nine sulfur atoms and one molybdenum. CHEBI:30409 has part this entry. The part has a separate H6Fe7MoS9/charge-0 depiction without the full cofactor carbon and homocitrate; it is not an exact replacement for FeMoco. |
| femoco-structure | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22096190%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:22096190; DOI:10.1126/science.1214025. Atomic-resolution X-ray crystallography and electron-spin-echo envelope modulation identify carbon as the central atom of FeMoco. This is positive central-atom evidence, not a universal assignment of every proton or catalytic-state net charge. |
| femoco-carbide | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22096198%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:22096198; DOI:10.1126/science.1206445. Fe K-beta X-ray emission of intact MoFe protein, isolated FeMoco and a FeMoco-deficient variant, together with computations, identifies central carbon over nitrogen/oxygen and supports carbide(4−). The paper specifically separates that conclusion from overall cluster oxidation/spin state. |
| carbide-biosynthesis | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:23019652%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:23019652; DOI:10.1126/science.1224603. Radiolabel experiments trace the FeMoco interstitial carbon to the methyl group of SAM and insertion by NifB. The proposed detailed insertion mechanism is an interpretation, not proof that the mature carbide is consumed during nitrogen reduction. |
| carbide-retention | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:23514429%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:23514429; DOI:10.1021/ja401698d. Carbon-14/carbon-13 tracing shows that interstitial carbide was not exchanged with substrate/product carbon or released during the studied turnover. The authors leave an indirect reactivity role open. This supports retained cofactor chemistry rather than treating its central carbon as a consumed nitrogenase substrate. |
| nitrogenase-authority | https://iubmb.qmul.ac.uk/enzyme/EC1/18/6/1.html; Accepted/systematic names, reaction and Comments; complete entry | supports | The official IUBMB EC 1.18.6.1 entry explicitly denotes molybdenum-dependent ferredoxin:dinitrogen oxidoreductase. It distinguishes reductase and dinitrogenase components and describes the latter as a molybdenum-iron protein. This supports the target EC context, not a claim that every alternative nitrogenase uses FeMoco. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Executed 2026-10-21T12:46:28Z through 2026-10-21T12:46:32Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Executed 2026-10-21T12:46:32Z through 2026-10-21T12:46:33Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- FeMoco primary studies were inspected through complete indexed abstracts, not their full spectra, coordinates or isotope tables. Central-carbide support is stronger than any claim about the source net −6 charge across all protein-bound redox/protonation states. No absolute homocitrate stereochemistry is inferred from the source depiction lacking that descriptor.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T125511Z-iron-sulfur-molybdenum-cofactor-chebi30409
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires iron-sulfur-molybdenum cofactor
started_at: '2026-10-21T12:45:45Z'
finished_at: '2026-10-21T12:55:11Z'
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
summary: FeMoco composition, central carbide and bounded positive nitrogenase context
  are supported. Findings are confirmed major chemical-to-protein-trait equivalence
  and minor mismatched composition delimiters. Exact bound net charge, full proton
  inventory and universal protein requirements are not inferred.
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
  - path: data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
    sha256: 6b8def8218665a61c74370f48e89dc906207fa187bd08a39331d2266902ef3c3
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
  selection: Path-order position 10 in batch 024. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242)
    covers 228 record paths, leaving 429131 before this batch. 24 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
targets:
- kind: generated
  label: requires iron-sulfur-molybdenum cofactor
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_30409
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:30409 and its direct cofactor role; local
    owner and source licence resolve. Exact chemical scope and bounded positive primary
    context are separated from protein-trait equivalence and universal state/requirement
    claims.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - context-35202
  - context-48796
  - femoco-structure
  - femoco-carbide
  - carbide-biosynthesis
  - carbide-retention
  - nitrogenase-authority
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:45:45Z'
  snapshot_sha256: 6b8def8218665a61c74370f48e89dc906207fa187bd08a39331d2266902ef3c3
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
  accessed_at: '2026-10-21T12:45:45Z'
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
  accessed_at: '2026-10-21T12:45:45Z'
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
  accessed_at: '2026-10-21T12:45:45Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:45:45Z'
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
  locator: Introduction and Licensing sections; verified reused body with original
    access UTC
  summary: The inspected official ChEBI Introduction and Licensing sections describe
    a chemical-entity/role resource licensed CC BY 4.0. This supports chemical-source
    attribution, not equivalence to a synthesized protein requirement.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16.
    Its actual original access UTC is retained. This does not identify the live backend
    release or the exact release used to seed the local record.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30409/
  accessed_at: '2026-10-21T12:46:22.621058Z'
  snapshot_sha256: aae2dcec7f644666eb6c2540d6b9843249541b19205da4d0ca9cdddcaf2f17cf
  support: supports
  locator: Complete identity, names, definition or null, formula/charge, default structure,
    origins/citations and outgoing relations
  summary: CHEBI:30409 resolves to iron-sulfur-molybdenum cofactor. Its definition
    identifies a Mo:7Fe:9S:C cluster with homocitrate and central carbide(4−), but
    contains mismatched opening brace and closing bracket. The backend reports C8H12Fe7MoO7S9,
    charge −6, and central [C-4] in the structure. Formal SMILES/InChI bookkeeping
    is not an experimental assignment of every metal oxidation state or the net charge
    of every protein-bound catalytic state. The depiction does not supply a homocitrate
    absolute stereodescriptor. Direct cofactor role, molybdenum-coordination-entity
    ancestry and a has-part relation to iron-sulfur-molybdenum cluster are asserted.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:30409
  accessed_at: '2026-10-21T12:46:22.665904Z'
  snapshot_sha256: b39e9a9693af2a5a032539e2c028d75d7e3f5f9ea708ed123835390dc511b98c
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete CHEBI:30409 identifier and source name.
    Its source definition and annotations were inspected, including the copied wording
    defects. Resolution is not independent validation of all source science or protein-trait
    equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Cofactor CHEBI:23357 denotes an organic molecule or ion required by an
    enzyme for activity, attached loosely or tightly, and is a biochemical role. A
    source has-role assertion supplies positive candidate context without itself equating
    a molecule/ion to a protein class.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Biochemical role CHEBI:52206 is a biological role played by an entity or
    part in a biochemical context. It is the asserted parent of cofactor, not a molecular
    identity or independently qualified protein requirement.
- evidence_id: context-35202
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35202/
  accessed_at: '2026-10-21T12:46:46.941156Z'
  snapshot_sha256: 9ddc78c94c5e80d3114608c0476c2eade1999f1f51a3a0ea1495402376846950
  support: supports
  locator: Exact identity, definition or null, chemical data and complete outgoing
    relations; relevant incoming child/part links
  summary: Molybdenum coordination entity CHEBI:35202 is a broad chemical class under
    transition element coordination entity and molybdenum molecular entity, with null
    definition and fixed chemical fields. It is not a protein-requirement class.
- evidence_id: context-48796
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/48796/
  accessed_at: '2026-10-21T12:46:46.383371Z'
  snapshot_sha256: 52d4a201e607b56f994894a9d7d7f7651b7ae972211328e67378e0cec9f01226
  support: supports
  locator: Exact identity, definition or null, chemical data and complete outgoing
    relations; relevant incoming child/part links
  summary: Iron-sulfur-molybdenum cluster CHEBI:48796 is defined by seven iron atoms,
    nine sulfur atoms and one molybdenum. CHEBI:30409 has part this entry. The part
    has a separate H6Fe7MoS9/charge-0 depiction without the full cofactor carbon and
    homocitrate; it is not an exact replacement for FeMoco.
- evidence_id: femoco-structure
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22096190%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:46:46.995177Z'
  snapshot_sha256: a6146c6e5a3cbf39969d15b3da194e4748795e975bba4d1359dca06cbd17cbb8
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental paper
    not inspected through this response
  summary: PMID:22096190; DOI:10.1126/science.1214025. Atomic-resolution X-ray crystallography
    and electron-spin-echo envelope modulation identify carbon as the central atom
    of FeMoco. This is positive central-atom evidence, not a universal assignment
    of every proton or catalytic-state net charge.
- evidence_id: femoco-carbide
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:22096198%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:46:47.056751Z'
  snapshot_sha256: 23ab2ad8415719382c03399a8a2e60c322aec6f3c2e70224a58f37f916ceabd3
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental paper
    not inspected through this response
  summary: PMID:22096198; DOI:10.1126/science.1206445. Fe K-beta X-ray emission of
    intact MoFe protein, isolated FeMoco and a FeMoco-deficient variant, together
    with computations, identifies central carbon over nitrogen/oxygen and supports
    carbide(4−). The paper specifically separates that conclusion from overall cluster
    oxidation/spin state.
- evidence_id: carbide-biosynthesis
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:23019652%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:46:47.588428Z'
  snapshot_sha256: 6051517abf6c97382414234ad14c70b1c5c6a73f33ff939cb00bc60bd077c7d1
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental paper
    not inspected through this response
  summary: PMID:23019652; DOI:10.1126/science.1224603. Radiolabel experiments trace
    the FeMoco interstitial carbon to the methyl group of SAM and insertion by NifB.
    The proposed detailed insertion mechanism is an interpretation, not proof that
    the mature carbide is consumed during nitrogen reduction.
- evidence_id: carbide-retention
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:23514429%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:46:47.611567Z'
  snapshot_sha256: ef44b5f65925806533a5e5c9bbb7380f53a2dfad3f04633ab4b5f4043ba8924f
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental paper
    not inspected through this response
  summary: PMID:23514429; DOI:10.1021/ja401698d. Carbon-14/carbon-13 tracing shows
    that interstitial carbide was not exchanged with substrate/product carbon or released
    during the studied turnover. The authors leave an indirect reactivity role open.
    This supports retained cofactor chemistry rather than treating its central carbon
    as a consumed nitrogenase substrate.
- evidence_id: nitrogenase-authority
  kind: authority
  reference: https://iubmb.qmul.ac.uk/enzyme/EC1/18/6/1.html
  accessed_at: '2026-10-21T12:46:48.817630Z'
  snapshot_sha256: 7490f9249e01c22f225513197b75da1cbf5389bbfc688b6a282d7375995e7734
  support: supports
  locator: Accepted/systematic names, reaction and Comments; complete entry
  summary: The official IUBMB EC 1.18.6.1 entry explicitly denotes molybdenum-dependent
    ferredoxin:dinitrogen oxidoreductase. It distinguishes reductase and dinitrogenase
    components and describes the latter as a molybdenum-iron protein. This supports
    the target EC context, not a claim that every alternative nitrogenase uses FeMoco.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Executed 2026-10-21T12:46:28Z through 2026-10-21T12:46:32Z; exit 0
  accessed_at: '2026-10-21T12:46:32Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0
  accessed_at: '2026-10-21T12:48:55Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Executed 2026-10-21T12:46:32Z through 2026-10-21T12:46:33Z; exit 0
  accessed_at: '2026-10-21T12:46:33Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0
  accessed_at: '2026-10-21T12:48:57Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source identifier and main chemical definition consistently denote
    the Mo:7Fe:9S:C-homocitrate cofactor, with experimental support for central carbide.
    The separate cluster-part entry is not the full molecule. Backend net charge −6
    and individual formal atom charges are source encodings, not independently measured
    universal metal valences or catalytic-state charge.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-35202
  - context-48796
  - femoco-structure
  - femoco-carbide
  topic: FeMoco composition and central carbide
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The primary central-atom, biosynthetic and isotope-retention abstracts
    support FeMoco chemistry, while the official EC entry supplies the molybdenum-dependent
    enzyme context. The retained carbide is distinguished from substrate carbon and
    from proposed mechanistic details.
  evidence_ids:
  - femoco-structure
  - femoco-carbide
  - carbide-biosynthesis
  - carbide-retention
  - nitrogenase-authority
  topic: Positive nitrogenase and retained-cofactor evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: Source cofactor role and positive FeMoco biology are preserved. No release-pinned
    protein example or exact bound net charge, complete proton inventory or homocitrate
    stereochemical assignment is newly qualified here. The description of EC 1.18.6.1
    is not expanded to all nitrogenase isoforms.
  evidence_ids:
  - record
  - schema
  - chemical
  - cofactor-role
  - femoco-carbide
  - carbide-retention
  - nitrogenase-authority
  topic: Protein requirement and catalytic-state scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-7
- area: provenance
  outcome: supported
  summary: scripts/seed_chebi_cofactor.py synthesizes the requires-label and requirement
    assertion from the chemical entry and direct cofactor role. Current ChEBI/OLS,
    official licensing and the local registry resolve that provenance. The original
    source release remains unidentified; current source resolution is not independent
    protein qualification.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: Maintained ChEBI emitter and source fidelity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct chemical cofactor role explains candidate selection and the
    broad local cofactor-requirement parent. Chemical structural parents remain distinct
    from protein-trait hierarchy. Parent resolution does not certify that parent's
    own equivalence semantics or every protein requirement.
  evidence_ids:
  - record
  - owner
  - chemical
  - cofactor-role
  - biochemical-role
  - local-parent-1
  topic: Role-derived parent and chemical hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: 'The source chemical and the synthesized class of proteins requiring it
    have different denotations. A direct has-role assertion, exact identifier or positive
    enzyme context does not establish true own-source equivalence between these entity
    types. '
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-30409.composition-delimiter
  category: nomenclature
  severity: minor
  title: Cluster-composition notation has mismatched delimiters
  description: The copied composition opens with a brace and closes with a square
    bracket in {Mo:7Fe:9S:C]:homocitrate. The atom counts and carbide identity remain
    intelligible and are supported; this is a source-inherited notation defect, not
    a different cofactor.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: The core FeMoco identity is intact; matched-delimiter repair
    improves notation without altering class scope.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
- issue_key: chebi.cofactor-requirement.CHEBI-30409.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: 'The target xrefs treats CHEBI:30409 as equivalent to a protein functional-requirement
    class, although the source denotes a chemical entity. This violates the schema''s
    true-equivalence semantics independently of the eventual activity-relative requirement
    decision. '
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical entity and protein-requirement class are different
    entity types, a major grounding defect. Positive biochemical context does not
    make the classes equivalent.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct the composition delimiters in the maintained source override/definition
    transformation while retaining the supported atom counts and homocitrate context.
    Preserve attribution and avoid changing chemical state or adding unsupported stereochemistry.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated composition uses matched delimiters and retains Mo:7Fe:9S:C plus
    homocitrate. No chemical-identity, charge-state or protein-membership change is
    introduced by the editorial repair.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
- action_id: A2
  description: correct build in scripts/seed_chebi_cofactor.py to preserve chemical
    provenance without asserting chemical-to-protein-class equality. Adjudicate the
    exact chemical scope and required activity-relative ChemicalParticipant.role before
    adding any typed participant. If a typed role cannot be supported, retain provenance
    and explicit uncertainty without inventing one. Do not move the equality into
    mapped_xrefs or automatically promote a protein example.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_30409
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated record no longer asserts a chemical entity as equivalent to its
    requirement class. Any typed participant has a curator-adjudicated identity and
    role; otherwise source provenance and uncertainty remain explicit.
  - Use an audited regeneration route for this existing target and focused transformation
    coverage. No native status or per-protein requirement is automatically promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
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
- FeMoco primary studies were inspected through complete indexed abstracts, not their
  full spectra, coordinates or isotope tables. Central-carbide support is stronger
  than any claim about the source net −6 charge across all protein-bound redox/protonation
  states. No absolute homocitrate stereochemistry is inferred from the source depiction
  lacking that descriptor.
tags:
- unreviewed-path-order
- batch-024
- chebi-cofactor
```
