# Review of requires iron-sulfur-vanadium cofactor

- Review: 20261021T131122Z-iron-sulfur-vanadium-cofactor-chebi60357
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:02:29Z
- Finished UTC: 2026-10-21T13:11:22Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Two confirmed majors concern the outdated defining FeV chemistry and the independent chemical-to-protein-class equivalence. Positive native spectroscopy/structure is retained, with tentative replacement-ligand assignment and chemistry-first mapping repair.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 025. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616) covers 238 record paths, leaving 429121 before this batch. 25 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml | generated | requires iron-sulfur-vanadium cofactor |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60357 | Official ChEBI/OLS resolve CHEBI:60357 and its direct cofactor role, but source chemistry requires the primary-supported correction. Local owner, source licence, chemical ancestry and bounded primary observations are inspected. Source identity and role are distinguished from protein-class equivalence and unqualified physiological requirements. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### FeV-cofactor identity and outdated defining chemistry

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

The intended FeV active cofactor resolves, but the copied unknown-X, assumed-structure and unqualified nine-sulfur description is outdated for the experimentally characterized A. vinelandii cofactor. The current source's nitrogen-containing depiction is an additional external inconsistency, not a structure asserted in this target. No distinct P-cluster identity is imposed.

### Positive native FeV-cofactor structural evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

Primary spectroscopy and the complete native nitrogenase structure support central carbide and the characterized eight-sulfide core. The tentative carbonate assignment retains the explicit nitrate alternative; synthetic P-cluster analogues do not resolve the native active-site chemistry.

### Exact chemical state and protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

The source cofactor role and positive native nitrogenase context are preserved. The current nitrogen-containing depiction must be adjudicated before importing an exact chemical participant. No universal net charge, complete metal-valence inventory, protonation state, catalytic-state composition or newly qualified protein instance follows from this review.

### Role-derived hierarchy and chemical ancestry

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

Direct cofactor role explains the broad local cofactor-requirement parent. Structural chemical parents and biochemical roles are distinct from protein-trait classes. Parent resolution does not certify the parent's own equivalence semantics or universal protein requirements.

### Maintained ChEBI emitter and source attribution

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

scripts/seed_chebi_cofactor.py synthesizes the requirement label and opening definition from the chemical name and role, then appends available chemical prose. Official chemical sources, licence and the local registry resolve this provenance. The copied FeV uncertainty is faithful to the source but scientifically outdated.

### Chemical entity versus protein-requirement class

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60357.

The ChEBI entry denotes a chemical entity, whereas the local requires-label denotes a protein functional class. Source role, chemical identity and positive biochemical context cannot make those denotations equivalent under xrefs.

## Findings

### F1: Definition retains an obsolete unknown central atom and assumed nine-sulfur structure

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-60357.defining-chemistry-obsolete.

The target explicitly says that the central X atom is unknown, possibly carbon or oxygen, and that a 7Fe-V-9S-X structure is assumed by analogy. Direct primary spectroscopy identifies interstitial carbide, and the characterized 1.35 Å A. vinelandii structure has a V:7Fe:8S:C core with a distinct replacement bridging ligand. The intended FeV cofactor remains identifiable, so this is a major defining-chemistry defect rather than a wrong-entity blocker. The external backend's nitrogen-centred formula/graph reinforces the need for source adjudication but is not itself copied into the YAML.

### F2: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-60357.chemical-entity-equivalence.

The target xrefs asserts CHEBI:60357 as a true equivalent of a protein-requirement class, but the official entry denotes a chemical entity. This violates the schema's own-source equivalence semantics independently of whether a particular activity requires it. Correcting the outdated cluster description alone would leave this emitter-level type error.

## Recommended Actions And Acceptance Checks

### A1

Correct the maintained ChEBI definition transformation or a documented source override in scripts/seed_chebi_cofactor.py. Retain the resolved FeV-cofactor identity and distinguish the characterized carbide/eight-sulfide structure from unqualified statements about all catalytic forms. Preserve the tentative carbonate-versus-nitrate ligand assignment. Reconcile the external nitrogen-centred depiction through curated chemistry before any exact participant transfer; do not silently change source data or invent a universal net charge.

- The regenerated definition no longer presents the central atom as unknown or the characterized structure as merely assumed. It cites inspected primary carbide and structural evidence and states the experimental scope.
- Any composition or participant enrichment distinguishes central carbide from the tentatively assigned replacement ligand, retains source provenance and resolves the nitrogen-containing source depiction before use.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

### A2

First complete the separate defining-chemistry/source adjudication; do not transfer the current inconsistent FeV depiction. Then correct build in scripts/seed_chebi_cofactor.py so chemical provenance is preserved without chemical-to-protein-class equality. Adjudicate exact chemical scope and the required activity-relative ChemicalParticipant.role before adding a typed participant. If a typed role cannot be supported, retain provenance and explicit uncertainty without inventing one.  Do not move the same false equivalence into mapped_xrefs or automatically promote a protein example.

- The regenerated class no longer asserts chemical-to-protein-class equivalence. Chemical provenance remains traceable, and any typed relation or participant has a curator-adjudicated exact identity and activity-relative role; otherwise explicit uncertainty is retained.
- Use audited regeneration for this existing target and focused transformation coverage. Complete the defining-chemistry prerequisite before dependent chemical mapping. No native status or per-protein requirement is automatically promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; reused body verified against its original digest and access UTC | supports | Official ChEBI Introduction and Licensing sections identify a chemical-entity/role resource licensed CC BY 4.0. Chemical-source attribution does not assert equivalence to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16, with its actual original access UTC retained. This does not identify the live backend release or exact release originally used by the seeder. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60357/; Complete chemical identity, names, definition or null, formula/charge, structure, origins/citations and outgoing relations | supports | CHEBI:60357 resolves to iron-sulfur-vanadium cofactor. Its definition still describes an assumed 7Fe-V-9S-X-homocitryl analogue with unknown X, possibly carbon or oxygen. The backend formula C7H12Fe7NO7S9V, charge −2 and default structure encode interstitial nitrogen, whereas a UniProt-derived name specifies C. These conflicting external fields are not all copied into the target. Direct cofactor role and vanadium-coordination-entity ancestry are asserted. The source charge and atom-level formal charges do not independently establish a native catalytic-state charge or metal oxidation-state inventory. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60357; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete CHEBI:60357 identifier and chemical name, with inspected formula/charge, structural annotations and synonyms. Its description repeats the relevant backend prose. Resolution verifies source attribution, not every scientific assertion or protein-class equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified reused original UTC | supports | Cofactor CHEBI:23357 is an organic molecule or ion required for enzyme activity, attached loosely or tightly, and is a biochemical role. A chemical has-role assertion supplies candidate context without equating a chemical entity to a protein class. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified reused original UTC | supports | Biochemical role CHEBI:52206 is a role played by an entity or part within a biochemical context; cofactor is its child. It is not a chemical identity or independently qualified protein requirement. |
| context-35166 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35166/; Exact identifier, definition or null, chemical data/default structure and complete outgoing relations | supports | Vanadium coordination entity CHEBI:35166 has null fixed structure, formula and prose definition, with transition-element-coordination-entity and vanadium-molecular-entity parents. This structural ancestry does not validate every atom in the current FeV-cofactor depiction. |
| carbide-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1002/anie.201505930&amp;format=json&amp;resultType=core; Verified bibliographic identifiers and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:26376620; DOI:10.1002/anie.201505930. Fe K-beta valence-to-core X-ray emission spectroscopy with calculations supplies direct evidence of interstitial carbide in Azotobacter vinelandii vanadium nitrogenase. Comparison with Mo nitrogenase does not validate an invariant nine-sulfur FeV structure or every formal atom charge. |
| structure-abstract | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1038/nchembio.2428&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full text captured separately as structure-fulltext | supports | PMID:28692069; DOI:10.1038/nchembio.2428. The 1.35 Å A. vinelandii vanadium-nitrogenase structure contains a [V:7Fe:8S:C] core with homocitrate and a bridging ligand assigned tentatively as carbonate, rather than the presumed nine-sulfur analogue. |
| structure-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5563456/fullTextXML; Complete primary main text, Results/Discussion, Online Methods and Figures 1–4 captions; especially Structure of the FeV cofactor and ligand assignment | supports | The primary 1.35 Å structure assigns the interstitial carbide unambiguously and identifies eight sulfides in the characterized A. vinelandii FeV cofactor. The replacement S3A-site ligand is tentatively carbonate: the authors cannot conclusively distinguish its central carbon from nitrogen in isoelectronic nitrate, although chemical context favours carbonate. The P-cluster is a separate Fe8S7 relay. Purification, crystallization and redox conditions bound these observations; the paper does not establish every catalytic-state charge or all FeV forms. |
| source-citation-context | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:12870953%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified bibliographic identifiers and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:12870953; DOI:10.1021/ic0301369. The source-linked study concerns synthetic vanadium–iron–sulfur clusters, including a V2Fe6S9 species topologically analogous to a P-cluster. It does not directly determine the composition of the native FeV active cofactor. Its chemical analogy is retained as context, not used to override modern native-protein evidence. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml; Executed 2026-10-21T13:03:10Z through 2026-10-21T13:03:11Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml; Executed 2026-10-21T13:03:10Z through 2026-10-21T13:04:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml; Executed 2026-10-21T13:03:11Z through 2026-10-21T13:03:12Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:04:47Z through 2026-10-21T13:04:48Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The complete 2017 primary main text was inspected, but not its supplementary coordinates. Carbonate is tentative in that paper and nitrate remains an electron-density alternative. The separate 2015 spectroscopy and 2003 synthetic-cluster papers were inspected through complete indexed abstracts. No exact proton inventory, universal eight-sulfide state or experimentally certified backend charge −2 is asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T131122Z-iron-sulfur-vanadium-cofactor-chebi60357
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires iron-sulfur-vanadium cofactor
started_at: '2026-10-21T13:02:29Z'
finished_at: '2026-10-21T13:11:22Z'
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
summary: Two confirmed majors concern the outdated defining FeV chemistry and the
  independent chemical-to-protein-class equivalence. Positive native spectroscopy/structure
  is retained, with tentative replacement-ligand assignment and chemistry-first mapping
  repair.
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
  - path: data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    sha256: 64da58cff2d2b902a7bea14196a3807e950cecdbae8f6363d1d17e3d03c146c5
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
  selection: Path-order position 1 in batch 025. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
targets:
- kind: generated
  label: requires iron-sulfur-vanadium cofactor
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_60357
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:60357 and its direct cofactor role, but
    source chemistry requires the primary-supported correction. Local owner, source
    licence, chemical ancestry and bounded primary observations are inspected. Source
    identity and role are distinguished from protein-class equivalence and unqualified
    physiological requirements.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - context-35166
  - carbide-primary
  - structure-abstract
  - structure-fulltext
  - source-citation-context
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:02:29Z'
  snapshot_sha256: 64da58cff2d2b902a7bea14196a3807e950cecdbae8f6363d1d17e3d03c146c5
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
  accessed_at: '2026-10-21T13:02:29Z'
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
  accessed_at: '2026-10-21T13:02:29Z'
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
  accessed_at: '2026-10-21T13:02:29Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:02:29Z'
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
  locator: Introduction and Licensing sections; reused body verified against its original
    digest and access UTC
  summary: Official ChEBI Introduction and Licensing sections identify a chemical-entity/role
    resource licensed CC BY 4.0. Chemical-source attribution does not assert equivalence
    to a synthesized protein requirement.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16,
    with its actual original access UTC retained. This does not identify the live
    backend release or exact release originally used by the seeder.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60357/
  accessed_at: '2026-10-21T13:03:25.311147Z'
  snapshot_sha256: e6ea2be67b658ebfc0716c3e97b6bbab72b94a85e7ad491420e39dcacecd9a79
  support: supports
  locator: Complete chemical identity, names, definition or null, formula/charge,
    structure, origins/citations and outgoing relations
  summary: CHEBI:60357 resolves to iron-sulfur-vanadium cofactor. Its definition still
    describes an assumed 7Fe-V-9S-X-homocitryl analogue with unknown X, possibly carbon
    or oxygen. The backend formula C7H12Fe7NO7S9V, charge −2 and default structure
    encode interstitial nitrogen, whereas a UniProt-derived name specifies C. These
    conflicting external fields are not all copied into the target. Direct cofactor
    role and vanadium-coordination-entity ancestry are asserted. The source charge
    and atom-level formal charges do not independently establish a native catalytic-state
    charge or metal oxidation-state inventory.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60357
  accessed_at: '2026-10-21T13:03:25.311669Z'
  snapshot_sha256: 1d6a9b4fd4f3c88d00b286cf9b861f633a5eec8c7d5c67f7ea14c41633e26982
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete CHEBI:60357 identifier and chemical name,
    with inspected formula/charge, structural annotations and synonyms. Its description
    repeats the relevant backend prose. Resolution verifies source attribution, not
    every scientific assertion or protein-class equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Cofactor CHEBI:23357 is an organic molecule or ion required for enzyme
    activity, attached loosely or tightly, and is a biochemical role. A chemical has-role
    assertion supplies candidate context without equating a chemical entity to a protein
    class.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Biochemical role CHEBI:52206 is a role played by an entity or part within
    a biochemical context; cofactor is its child. It is not a chemical identity or
    independently qualified protein requirement.
- evidence_id: context-35166
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35166/
  accessed_at: '2026-10-21T13:04:06.936245Z'
  snapshot_sha256: efa49ab84bade5757875eb4385c9ff9afbbf23c854d359d14dcbade08f6c381a
  support: supports
  locator: Exact identifier, definition or null, chemical data/default structure and
    complete outgoing relations
  summary: Vanadium coordination entity CHEBI:35166 has null fixed structure, formula
    and prose definition, with transition-element-coordination-entity and vanadium-molecular-entity
    parents. This structural ancestry does not validate every atom in the current
    FeV-cofactor depiction.
- evidence_id: carbide-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1002/anie.201505930&format=json&resultType=core
  accessed_at: '2026-10-21T13:04:08.460837Z'
  snapshot_sha256: 8cdae41249fbd19a093577fdb4f54fb967bcf9fd47e7fe0a3f6ba8b12e248756
  support: supports
  locator: Verified bibliographic identifiers and complete indexed abstract; full
    experimental paper not inspected through this response
  summary: PMID:26376620; DOI:10.1002/anie.201505930. Fe K-beta valence-to-core X-ray
    emission spectroscopy with calculations supplies direct evidence of interstitial
    carbide in Azotobacter vinelandii vanadium nitrogenase. Comparison with Mo nitrogenase
    does not validate an invariant nine-sulfur FeV structure or every formal atom
    charge.
- evidence_id: structure-abstract
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1038/nchembio.2428&format=json&resultType=core
  accessed_at: '2026-10-21T13:04:08.460518Z'
  snapshot_sha256: 40e3be0eab9b80193ff63a628e2bd3f66306c7ad45ff2c91a8ee0166c9f8f92d
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full text captured separately
    as structure-fulltext
  summary: PMID:28692069; DOI:10.1038/nchembio.2428. The 1.35 Å A. vinelandii vanadium-nitrogenase
    structure contains a [V:7Fe:8S:C] core with homocitrate and a bridging ligand
    assigned tentatively as carbonate, rather than the presumed nine-sulfur analogue.
- evidence_id: structure-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5563456/fullTextXML
  accessed_at: '2026-10-21T13:04:09.102529Z'
  snapshot_sha256: e579699d18c0bbac023611ed1b093ce053db81d85b68330234f8e17803134ce8
  support: supports
  locator: Complete primary main text, Results/Discussion, Online Methods and Figures
    1–4 captions; especially Structure of the FeV cofactor and ligand assignment
  summary: 'The primary 1.35 Å structure assigns the interstitial carbide unambiguously
    and identifies eight sulfides in the characterized A. vinelandii FeV cofactor.
    The replacement S3A-site ligand is tentatively carbonate: the authors cannot conclusively
    distinguish its central carbon from nitrogen in isoelectronic nitrate, although
    chemical context favours carbonate. The P-cluster is a separate Fe8S7 relay. Purification,
    crystallization and redox conditions bound these observations; the paper does
    not establish every catalytic-state charge or all FeV forms.'
- evidence_id: source-citation-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:12870953%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T13:04:33.973136Z'
  snapshot_sha256: 957944bfa9c2d56577dcff7dbfa9cff42c145b9ccac7b0ebd28eb3e6b07ebbc6
  support: supports
  locator: Verified bibliographic identifiers and complete indexed abstract; full
    experimental paper not inspected through this response
  summary: PMID:12870953; DOI:10.1021/ic0301369. The source-linked study concerns
    synthetic vanadium–iron–sulfur clusters, including a V2Fe6S9 species topologically
    analogous to a P-cluster. It does not directly determine the composition of the
    native FeV active cofactor. Its chemical analogy is retained as context, not used
    to override modern native-protein evidence.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  locator: Executed 2026-10-21T13:03:10Z through 2026-10-21T13:03:11Z; exit 0
  accessed_at: '2026-10-21T13:03:11Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
  locator: Executed 2026-10-21T13:03:11Z through 2026-10-21T13:03:12Z; exit 0
  accessed_at: '2026-10-21T13:03:12Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: concern
  summary: The intended FeV active cofactor resolves, but the copied unknown-X, assumed-structure
    and unqualified nine-sulfur description is outdated for the experimentally characterized
    A. vinelandii cofactor. The current source's nitrogen-containing depiction is
    an additional external inconsistency, not a structure asserted in this target.
    No distinct P-cluster identity is imposed.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - carbide-primary
  - structure-fulltext
  topic: FeV-cofactor identity and outdated defining chemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: Primary spectroscopy and the complete native nitrogenase structure support
    central carbide and the characterized eight-sulfide core. The tentative carbonate
    assignment retains the explicit nitrate alternative; synthetic P-cluster analogues
    do not resolve the native active-site chemistry.
  evidence_ids:
  - carbide-primary
  - structure-abstract
  - structure-fulltext
  - source-citation-context
  topic: Positive native FeV-cofactor structural evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The source cofactor role and positive native nitrogenase context are preserved.
    The current nitrogen-containing depiction must be adjudicated before importing
    an exact chemical participant. No universal net charge, complete metal-valence
    inventory, protonation state, catalytic-state composition or newly qualified protein
    instance follows from this review.
  evidence_ids:
  - record
  - schema
  - chemical
  - cofactor-role
  - structure-fulltext
  topic: Exact chemical state and protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: Direct cofactor role explains the broad local cofactor-requirement parent.
    Structural chemical parents and biochemical roles are distinct from protein-trait
    classes. Parent resolution does not certify the parent's own equivalence semantics
    or universal protein requirements.
  evidence_ids:
  - record
  - owner
  - chemical
  - local-parent-1
  - cofactor-role
  topic: Role-derived hierarchy and chemical ancestry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: scripts/seed_chebi_cofactor.py synthesizes the requirement label and opening
    definition from the chemical name and role, then appends available chemical prose.
    Official chemical sources, licence and the local registry resolve this provenance.
    The copied FeV uncertainty is faithful to the source but scientifically outdated.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: Maintained ChEBI emitter and source attribution
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The ChEBI entry denotes a chemical entity, whereas the local requires-label
    denotes a protein functional class. Source role, chemical identity and positive
    biochemical context cannot make those denotations equivalent under xrefs.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical entity versus protein-requirement class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-60357.defining-chemistry-obsolete
  category: grounding
  severity: major
  title: Definition retains an obsolete unknown central atom and assumed nine-sulfur
    structure
  description: The target explicitly says that the central X atom is unknown, possibly
    carbon or oxygen, and that a 7Fe-V-9S-X structure is assumed by analogy. Direct
    primary spectroscopy identifies interstitial carbide, and the characterized 1.35
    Å A. vinelandii structure has a V:7Fe:8S:C core with a distinct replacement bridging
    ligand. The intended FeV cofactor remains identifiable, so this is a major defining-chemistry
    defect rather than a wrong-entity blocker. The external backend's nitrogen-centred
    formula/graph reinforces the need for source adjudication but is not itself copied
    into the YAML.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - carbide-primary
  - structure-fulltext
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: The resolved FeV-cofactor identity limits the defect to materially
    incorrect defining chemistry. Experimental evidence directly contradicts the retained
    uncertainty and assumed composition; it does not justify a universal statement
    about all redox or ligand states.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-60357.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The target xrefs asserts CHEBI:60357 as a true equivalent of a protein-requirement
    class, but the official entry denotes a chemical entity. This violates the schema's
    own-source equivalence semantics independently of whether a particular activity
    requires it. Correcting the outdated cluster description alone would leave this
    emitter-level type error.
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
    entity types, a major grounding defect. Its correction depends on the separately
    identified defining-chemistry repair.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct the maintained ChEBI definition transformation or a documented
    source override in scripts/seed_chebi_cofactor.py. Retain the resolved FeV-cofactor
    identity and distinguish the characterized carbide/eight-sulfide structure from
    unqualified statements about all catalytic forms. Preserve the tentative carbonate-versus-nitrate
    ligand assignment. Reconcile the external nitrogen-centred depiction through curated
    chemistry before any exact participant transfer; do not silently change source
    data or invent a universal net charge.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated definition no longer presents the central atom as unknown or the
    characterized structure as merely assumed. It cites inspected primary carbide
    and structural evidence and states the experimental scope.
  - Any composition or participant enrichment distinguishes central carbide from the
    tentatively assigned replacement ligand, retains source provenance and resolves
    the nitrogen-containing source depiction before use.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
- action_id: A2
  description: First complete the separate defining-chemistry/source adjudication;
    do not transfer the current inconsistent FeV depiction. Then correct build in
    scripts/seed_chebi_cofactor.py so chemical provenance is preserved without chemical-to-protein-class
    equality. Adjudicate exact chemical scope and the required activity-relative ChemicalParticipant.role
    before adding a typed participant. If a typed role cannot be supported, retain
    provenance and explicit uncertainty without inventing one.  Do not move the same
    false equivalence into mapped_xrefs or automatically promote a protein example.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60357
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated class no longer asserts chemical-to-protein-class equivalence.
    Chemical provenance remains traceable, and any typed relation or participant has
    a curator-adjudicated exact identity and activity-relative role; otherwise explicit
    uncertainty is retained.
  - Use audited regeneration for this existing target and focused transformation coverage.
    Complete the defining-chemistry prerequisite before dependent chemical mapping.
    No native status or per-protein requirement is automatically promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
  depends_on:
  - A1
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
- The complete 2017 primary main text was inspected, but not its supplementary coordinates.
  Carbonate is tentative in that paper and nitrate remains an electron-density alternative.
  The separate 2015 spectroscopy and 2003 synthetic-cluster papers were inspected
  through complete indexed abstracts. No exact proton inventory, universal eight-sulfide
  state or experimentally certified backend charge −2 is asserted.
tags:
- unreviewed-path-order
- batch-025
- chebi-cofactor
```
