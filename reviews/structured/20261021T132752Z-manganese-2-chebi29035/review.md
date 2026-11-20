# Review of requires manganese(2+)

- Review: 20261021T132752Z-manganese-2-chebi29035
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:18:09Z
- Finished UTC: 2026-10-21T13:27:52Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Exact manganese(2+) identity and positive binuclear arginase context are supported. One confirmed major concerns chemical-to-protein-class equivalence without asserting universal metal exclusivity.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 026. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) covers 248 record paths, leaving 429111 before this batch. 26 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml | generated | requires manganese(2+) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_29035 | Official ChEBI and OLS resolve the exact chemical identity and direct cofactor role. Inspected chemical ancestry, source licence and bounded primary evidence support the stated observations without chemical-to-protein-class equivalence or automatic protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Exact divalent-ion identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The target chemical anchor resolves to the stated monatomic manganese +2 ion. The broader cation parents do not merge other charge states, a neutral atom or a whole coordinated complex. The copied divalent-cation definition matches the current source.

### Positive catalytic metal-ion evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The complete primary abstract supplies positive structural and catalytic context for the exact divalent ion in the studied enzyme. This supports biological plausibility of the requirement class while leaving protein-instance qualification and universal metal specificity unasserted.

### Protein qualification and coordinated-state scope

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The direct source cofactor role and positive enzyme evidence are retained. This review does not assign a release-pinned protein instance, all coordination geometries, occupancy under every condition or a complete metal-containing complex identity. A future typed participant still requires an activity-relative role decision.

### Role-derived parent and chemical hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The direct cofactor role explains the broad local cofactor-requirement parent. Chemical ancestry and role-derived trait hierarchy remain different assertions; parent resolution does not certify the parent's own equivalence semantics.

### ChEBI source transformation and attribution

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The maintained ChEBI emitter synthesizes the requirement label/opening sentence from chemical name and role and appends available chemical prose. Official snapshots and licensing support source attribution without identifying the original release or independently qualifying every protein requirement.

### Chemical class versus protein-requirement class

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_29035.

The official ChEBI anchor denotes a chemical entity or chemical class, while the local requires-label denotes a protein functional class. These are different denotations under the schema's true-equivalence xrefs semantics. Positive role and enzyme evidence are preserved but do not make the two entity types equivalent.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-29035.chemical-entity-equivalence.

The target uses CHEBI:29035 as a true-equivalence xref for a protein-requirement class, but the official entry denotes a chemical ion, molecule or chemical class. This is an independent schema-level entity-type mismatch. Direct source roles and positive biochemical context do not supply equivalent-class semantics.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so a chemical association is not emitted as true equality to the protein-requirement class. Preserve chemical provenance and adjudicate exact scope and the required activity-relative ChemicalParticipant.role before adding a typed participant or relation. If the supported scope or role cannot be represented, retain explicit provenance and uncertainty without inventing one. Do not move false equality into mapped_xrefs or automatically promote a protein instance.

- The regenerated class has no chemical-to-protein-class equality. Chemical provenance remains explicit; every typed participant/relation has a curator-adjudicated identity, scope and activity-relative role, or uncertainty is retained.
- Use an audited scoped existing-record regeneration route and focused transformation coverage. Preserve the supported exact chemical or generic-class distinctions and avoid automatic protein qualification.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; verified reused raw body with original access UTC | supports | The official ChEBI Introduction and Licensing sections describe a chemical-entity/role resource licensed CC BY 4.0. This supports chemical-source attribution, not equivalence to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS ontology metadata reports version 256 loaded 2026-10-16. Its original access UTC is retained. This does not identify the live backend release or the exact release originally used to generate the target. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29035/; Complete material identity fields, names, definition/null, chemical data/default structure, citations/origins and complete outgoing relations; incoming descendant lists are not used to establish protein requirements | supports | CHEBI:29035 resolves to manganese(2+), Mn, charge +2, with [Mn+2] and InChI=1S/Mn/q+2. The source definition describes a divalent manganese cation, matching the copied sentence. A direct cofactor role and manganese-cation, monoatomic-dication and divalent-metal-cation ancestry are asserted. The monatomic ion is distinct from a complete binuclear protein-bound cluster. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:29035; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete identifier and chemical name, with inspected description or absence, synonyms and structural annotations. Source resolution verifies attribution, not chemical-to-protein-class equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified original access UTC | supports | Cofactor CHEBI:23357 is an organic molecule or ion required by an enzyme for activity, attached loosely or tightly, and is a biochemical role. A chemical role supplies candidate context rather than protein-class identity. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified original access UTC | supports | Biochemical role CHEBI:52206 is a role of an entity or part within a biochemical context. This is role ancestry, not a chemical identity or independent physiological requirement. |
| context-25155 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25155/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Manganese cation CHEBI:25155 has Mn formula, unspecified charge, null prose definition and no fixed structure. Transition-element-cation and elemental-manganese ancestry support a broad cation class, not an exact alternative oxidation state. |
| context-30412 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30412/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Monoatomic dication CHEBI:30412 has the generic [*+2] representation and charge +2 under monoatomic cation. Its variable atom is a generic class placeholder, not a particular chemical species. |
| context-60240 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60240/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Divalent metal cation CHEBI:60240 is defined by a metal cation of valence two, with no fixed molecular structure. It is a broader chemical class than the exact magnesium or manganese ion. |
| enzyme-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8849731%20AND%20SRC%3AMED&amp;resultType=core&amp;format=json; Verified bibliographic identifiers and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:8849731; DOI:10.1038/383554a0. The 2.1 Å rat-liver arginase structure identifies a binuclear Mn2+–Mn2+ active-site cluster, and the complete abstract explicitly describes its catalytic requirement in vitro and in vivo. A bridging solvent nucleophile is the structure-based mechanistic interpretation. This positive exact-ion context does not establish universal exclusivity across all arginases or eliminate possible substitution under other conditions. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml; Executed 2026-10-21T13:18:44Z through 2026-10-21T13:18:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Executed 2026-10-21T13:18:40Z through 2026-10-21T13:20:44Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml; Executed 2026-10-21T13:18:47Z through 2026-10-21T13:18:47Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:20:44Z through 2026-10-21T13:20:46Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The enzyme study was inspected through its complete indexed abstract. No full atomic coordinates or assay tables were independently inspected, and no universal metal preference, concentration requirement or protein membership is certified.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T132752Z-manganese-2-chebi29035
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires manganese(2+)
started_at: '2026-10-21T13:18:09Z'
finished_at: '2026-10-21T13:27:52Z'
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
summary: Exact manganese(2+) identity and positive binuclear arginase context are
  supported. One confirmed major concerns chemical-to-protein-class equivalence without
  asserting universal metal exclusivity.
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
  - path: data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
    sha256: d9a119c67f22fccc427bc256bdb45293ec8331835f60da40b5076e4888f3e34a
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
  selection: Path-order position 2 in batch 026. Fresh main inventory has 429359 records;
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
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98)
    covers 248 record paths, leaving 429111 before this batch. 26 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
targets:
- kind: generated
  label: requires manganese(2+)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_29035
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml
    data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml
    data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml
    data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml
    data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml
    data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml
    data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve the exact chemical identity and direct cofactor
    role. Inspected chemical ancestry, source licence and bounded primary evidence
    support the stated observations without chemical-to-protein-class equivalence
    or automatic protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - context-25155
  - context-30412
  - context-60240
  - enzyme-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:18:09Z'
  snapshot_sha256: d9a119c67f22fccc427bc256bdb45293ec8331835f60da40b5076e4888f3e34a
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
  accessed_at: '2026-10-21T13:18:09Z'
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
  accessed_at: '2026-10-21T13:18:09Z'
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
  accessed_at: '2026-10-21T13:18:09Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:18:09Z'
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
  locator: Introduction and Licensing sections; verified reused raw body with original
    access UTC
  summary: The official ChEBI Introduction and Licensing sections describe a chemical-entity/role
    resource licensed CC BY 4.0. This supports chemical-source attribution, not equivalence
    to a synthesized protein requirement.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The verified reused OLS ontology metadata reports version 256 loaded 2026-10-16.
    Its original access UTC is retained. This does not identify the live backend release
    or the exact release originally used to generate the target.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29035/
  accessed_at: '2026-10-21T13:18:49.366003Z'
  snapshot_sha256: 74a2d5482c8756c88dfa7167ffb0b8cde80b6d62fa718f69089e8b02d068eeaa
  support: supports
  locator: Complete material identity fields, names, definition/null, chemical data/default
    structure, citations/origins and complete outgoing relations; incoming descendant
    lists are not used to establish protein requirements
  summary: CHEBI:29035 resolves to manganese(2+), Mn, charge +2, with [Mn+2] and InChI=1S/Mn/q+2.
    The source definition describes a divalent manganese cation, matching the copied
    sentence. A direct cofactor role and manganese-cation, monoatomic-dication and
    divalent-metal-cation ancestry are asserted. The monatomic ion is distinct from
    a complete binuclear protein-bound cluster.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:29035
  accessed_at: '2026-10-21T13:18:49.366182Z'
  snapshot_sha256: 2a7673e24a47791991361da9bbfb37f2f85f7d7d146978fa61c5df950b91faef
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete identifier and chemical name, with inspected
    description or absence, synonyms and structural annotations. Source resolution
    verifies attribution, not chemical-to-protein-class equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations; verified original access UTC
  summary: Cofactor CHEBI:23357 is an organic molecule or ion required by an enzyme
    for activity, attached loosely or tightly, and is a biochemical role. A chemical
    role supplies candidate context rather than protein-class identity.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Definition and complete outgoing relations; verified original access UTC
  summary: Biochemical role CHEBI:52206 is a role of an entity or part within a biochemical
    context. This is role ancestry, not a chemical identity or independent physiological
    requirement.
- evidence_id: context-25155
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25155/
  accessed_at: '2026-10-21T13:20:51.547139Z'
  snapshot_sha256: 8c41529e3a4694e032b5aa31ec7942b3352c9800b56127e0c4ca163b3a3d4d07
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Manganese cation CHEBI:25155 has Mn formula, unspecified charge, null prose
    definition and no fixed structure. Transition-element-cation and elemental-manganese
    ancestry support a broad cation class, not an exact alternative oxidation state.
- evidence_id: context-30412
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30412/
  accessed_at: '2026-10-21T13:20:51.546713Z'
  snapshot_sha256: 26ffa576f22e8d1c8951ee196a9d5b77533353a58800e9f7bf77026699d0d428
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Monoatomic dication CHEBI:30412 has the generic [*+2] representation and
    charge +2 under monoatomic cation. Its variable atom is a generic class placeholder,
    not a particular chemical species.
- evidence_id: context-60240
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60240/
  accessed_at: '2026-10-21T13:20:51.548622Z'
  snapshot_sha256: ae17ca03a6f40e7436e6b4bae08e793dc67d910b9b8f29f3b180135dfab4afd9
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Divalent metal cation CHEBI:60240 is defined by a metal cation of valence
    two, with no fixed molecular structure. It is a broader chemical class than the
    exact magnesium or manganese ion.
- evidence_id: enzyme-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8849731%20AND%20SRC%3AMED&resultType=core&format=json
  accessed_at: '2026-10-21T13:20:53.632318Z'
  snapshot_sha256: 7e07f16c93b22be7fd6fcb36c038c7a6be2a30f1eac3f0d870a1b60349b25c22
  support: supports
  locator: Verified bibliographic identifiers and complete indexed abstract; full
    experimental paper not inspected through this response
  summary: PMID:8849731; DOI:10.1038/383554a0. The 2.1 Å rat-liver arginase structure
    identifies a binuclear Mn2+–Mn2+ active-site cluster, and the complete abstract
    explicitly describes its catalytic requirement in vitro and in vivo. A bridging
    solvent nucleophile is the structure-based mechanistic interpretation. This positive
    exact-ion context does not establish universal exclusivity across all arginases
    or eliminate possible substitution under other conditions.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  locator: Executed 2026-10-21T13:18:44Z through 2026-10-21T13:18:47Z; exit 0
  accessed_at: '2026-10-21T13:18:47Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml
    data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml
    data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml
    data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml
    data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml
    data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml
    data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml
  locator: Executed 2026-10-21T13:18:40Z through 2026-10-21T13:20:44Z; exit 0
  accessed_at: '2026-10-21T13:20:44Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
  locator: Executed 2026-10-21T13:18:47Z through 2026-10-21T13:18:47Z; exit 0
  accessed_at: '2026-10-21T13:18:47Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T13:20:44Z through 2026-10-21T13:20:46Z; exit 0
  accessed_at: '2026-10-21T13:20:46Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The target chemical anchor resolves to the stated monatomic manganese +2
    ion. The broader cation parents do not merge other charge states, a neutral atom
    or a whole coordinated complex. The copied divalent-cation definition matches
    the current source.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-25155
  - context-30412
  - context-60240
  topic: Exact divalent-ion identity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The complete primary abstract supplies positive structural and catalytic
    context for the exact divalent ion in the studied enzyme. This supports biological
    plausibility of the requirement class while leaving protein-instance qualification
    and universal metal specificity unasserted.
  evidence_ids:
  - enzyme-primary
  topic: Positive catalytic metal-ion evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The direct source cofactor role and positive enzyme evidence are retained.
    This review does not assign a release-pinned protein instance, all coordination
    geometries, occupancy under every condition or a complete metal-containing complex
    identity. A future typed participant still requires an activity-relative role
    decision.
  evidence_ids:
  - record
  - schema
  - chemical
  - cofactor-role
  - enzyme-primary
  topic: Protein qualification and coordinated-state scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The direct cofactor role explains the broad local cofactor-requirement
    parent. Chemical ancestry and role-derived trait hierarchy remain different assertions;
    parent resolution does not certify the parent's own equivalence semantics.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - cofactor-role
  topic: Role-derived parent and chemical hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The maintained ChEBI emitter synthesizes the requirement label/opening
    sentence from chemical name and role and appends available chemical prose. Official
    snapshots and licensing support source attribution without identifying the original
    release or independently qualifying every protein requirement.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: ChEBI source transformation and attribution
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The official ChEBI anchor denotes a chemical entity or chemical class,
    while the local requires-label denotes a protein functional class. These are different
    denotations under the schema's true-equivalence xrefs semantics. Positive role
    and enzyme evidence are preserved but do not make the two entity types equivalent.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical class versus protein-requirement class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-29035.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The target uses CHEBI:29035 as a true-equivalence xref for a protein-requirement
    class, but the official entry denotes a chemical ion, molecule or chemical class.
    This is an independent schema-level entity-type mismatch. Direct source roles
    and positive biochemical context do not supply equivalent-class semantics.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Different entity types are equated, constituting a major grounding
    defect independently of biological plausibility. No denial of positive biochemical
    roles or forced representation follows.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
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
    is not emitted as true equality to the protein-requirement class. Preserve chemical
    provenance and adjudicate exact scope and the required activity-relative ChemicalParticipant.role
    before adding a typed participant or relation. If the supported scope or role
    cannot be represented, retain explicit provenance and uncertainty without inventing
    one. Do not move false equality into mapped_xrefs or automatically promote a protein
    instance.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_29035
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated class has no chemical-to-protein-class equality. Chemical provenance
    remains explicit; every typed participant/relation has a curator-adjudicated identity,
    scope and activity-relative role, or uncertainty is retained.
  - Use an audited scoped existing-record regeneration route and focused transformation
    coverage. Preserve the supported exact chemical or generic-class distinctions
    and avoid automatic protein qualification.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml.
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
- The enzyme study was inspected through its complete indexed abstract. No full atomic
  coordinates or assay tables were independently inspected, and no universal metal
  preference, concentration requirement or protein membership is certified.
tags:
- unreviewed-path-order
- batch-026
- chebi-cofactor
```
