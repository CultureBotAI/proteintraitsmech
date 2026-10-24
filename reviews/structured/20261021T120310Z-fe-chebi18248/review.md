# Review of requires Fe

- Review: 20261021T120310Z-fe-chebi18248
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:55:53Z
- Finished UTC: 2026-10-21T12:03:10Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The Fe label correctly resolves to neutral iron atom, while intended ionic versus element-level requirement remains unresolved. One confirmed major concerns chemical-to-protein-trait equivalence and one confirmed minor concerns the copied metals category synonym. Positive Fe2+ enzyme context does not automatically select a replacement chemical.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 021. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7) covers 198 record paths, leaving 429161 before this batch. 21 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml | generated | requires Fe |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_18248 | Current official ChEBI/OLS and RSC resolve neutral iron18248 with the correct element identity. Direct roles, cation comparisons, IUBMB Fe2+ enzyme context and exact captured alignment provenance were inspected. This does not resolve the intended ionic scope or validate protein-trait equivalence. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

scripts/seed_cofactor_alignment.py owns this aligned requirement, with the captured ChEBI helper dependency and crosswalk provenance. No emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Iron elemental identity and exact neutral state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

Fe and the copied atomic-number26 definition correctly identify iron, and CHEBI18248 specifically encodes a neutral atom. The local iron_ion token is RELATED_SYNONYM, so it is not treated as an exact-equivalence assertion or a wrong-element blocker. Ionic and element-level scope still require adjudication.

### Related ionic token and broad category metadata

nomenclature: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The scientific Fe name remains coherent. iron_ion points toward ionic scope while the source identifier is neutral; RELATED scope limits the strength of that discrepancy. The independently copied metals grouping token is not an alternate scientific label and supports the bounded minor finding.

### Positive iron-ion enzyme context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The IUBMB authority explicitly supports Fe2+ in the stated hydroxylase activity, and current iron-cation entries carry direct cofactor roles. This positive biology is retained without equating those ions to the neutral source atom or establishing a universal elemental requirement.

### Neutral atom versus intended iron requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The alignment name/category and RELATED ionic token do not resolve whether the intended class concerns an element, one cation state or a broader iron-containing species. A curator must adjudicate that scope before any participant or protein qualification. Lack of direct cofactor role on the neutral atom does not prove biological impossibility.

### Alignment parent and current source roles

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The local cofactor parent was attached by build_aligned. Present atom roles are micronutrient and E.coli metabolite, whereas cation comparisons have cofactor roles. This provenance difference is not a demonstrated universal nonmembership counterexample and does not justify an automatic replacement.

### Exact local alignment row and source release limit

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

Captured crosswalk row71 and the maintained alignment emitter explain Fe/iron_ion/metals output. Current official chemistry agrees with the element name but leaves physiological state unresolved. The upstream MGA table/release was not independently inspected; neither the crosswalk nor the model-origin annotation is experimental qualification.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_18248.

The source chemical and the synthesized protein-requirement class are different entity types. Correct chemistry and positive biochemical context do not satisfy the schema requirement for true own-source equivalence.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-18248.chemical-entity-equivalence.

The neutral iron chemical18248 is asserted in the xrefs field of a protein-requirement class. Chemical/elemental identity and positive Fe2+ enzyme evidence cannot make the neutral atom and protein requirement equivalent.

### F2: Broad metals category is copied into alternate labels

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-18248.category-token-synonym.

The RELATED_SYNONYM metals is the broad alignment grouping category, not an alternate scientific label of this exact requirement. RELATED scope is weaker than exact equivalence, but the schema still defines synonyms as alternate labels and build_aligned explicitly copies the category into that field.

## Recommended Actions And Acceptance Checks

### A1

Update build_aligned in scripts/seed_cofactor_alignment.py and its maintained input/registered override to remove chemical-to-protein-trait equality from xrefs while preserving supported chemical grounding and provenance. Resolve the intended elemental/ionic scope from maintained curation evidence before choosing a participant; do not automatically replace18248 with24875,29033 or29034. Adjudicate the activity-relative role before adding a COFACTOR chemical_participant. If that role is not supported, retain provenance and explicit uncertainty without inventing a participant. Do not relocate the equality to mapped_xrefs, merge chemical states or promote protein examples or native status.

- The regenerated xrefs no longer equate a chemical entity/class with the protein requirement. Chemical identity, scope and provenance remain auditable; any participant has a supported activity-relative role.
- Use an audited route selecting this existing target and a focused alignment fixture: main selects only missing IDs before --force, so an ordinary rerun or force alone does not repair it.
- Run just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml after the scoped repair. If adjudication changes the target path, validate the replacement and retained/deprecated target disposition explicitly.
- For maintained writer changes add focused pytest coverage and run just audit-writers, just lint and just test. Regenerate the existing target through an audited route. Run full just validate-all before merging record changes; capture changed inputs and save a fresh structured review without overwriting this observation.

### A2

Stop emitting the broad category as an alternate trait label in the maintained alignment input/transform or registered override. Preserve the source category as provenance and retain supported scientific names. Adjudicate the iron_ion scope separately; do not silently replace the neutral iron identifier with a particular cation.

- The regenerated synonym list distinguishes scientific names from broad grouping metadata, and original alignment provenance remains auditable.
- Use a focused alignment fixture and audited existing-target selection; main selects missing IDs before --force.
- Run just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml after the scoped repair. If adjudication changes the target path, validate the replacement and retained/deprecated target disposition explicitly.
- For maintained writer changes add focused pytest coverage and run just audit-writers, just lint and just test. Regenerate the existing target through an audited route. Run full just validate-all before merging record changes; capture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; Entire target YAML | supports | Complete target YAML inspected: local identifier, requires-label, synthesized alignment definition with appended ChEBI chemistry, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, cofactor parent, ChEBI chemical xref, licence and both MGA-attributed RELATED_SYNONYM values. No optional protein example, graph or chemical_participants is asserted. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main | supports | load_mg_cofactors reads sibling reference-table metadata; build_aligned synthesizes the protein requirement, attaches the broad cofactor parent, emits the chemical xref, and copies cofactor_id/category as RELATED_SYNONYM. main selects only missing chemical IDs before considering force, so an existing-record repair requires an audited scoped route. This local review does not access the sibling checkout. |
| chebi-dependency | scripts/seed_chebi_cofactor.py; load_names, rid, clean, LICENSE and imported helpers | supports | The alignment emitter imports ChEBI chemical-name/definition loading, identifiers, formatting, output location and ChEBI licensing from this module. This dependency does not itself establish a role for an alignment-selected chemical. |
| alignment-crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and exact row71 | supports | The captured row71 persists CHEBI:18248, Fe, iron_ion and metals. This corroborates local alignment output provenance, not an independently inspected upstream table release or protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction and Licensing sections identify a chemical-entity ontology and CC BY4.0. This supports chemical-source attribution, not equality to a synthesized protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ChEBI version256 loaded2026-10-16. Original actual access time and digest are preserved; this is not a release pin for the live backend or original seed. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:18248; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:18248 as a nonobsolete chemical term; its complete names, description and chemical annotations were inspected. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/18248/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | CHEBI:18248 is iron atom: atomic number26, formulaFe, charge0, SMILES[Fe], InChI=1S/Fe. Fe/iron aliases and the copied definition agree. Direct roles are micronutrient and E.coli metabolite, with iron-group-element-atom parent; the inspected outgoing relations do not directly assert cofactor. This is the same element as the label, not a wrong-element collision. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Cofactor is a biochemical role for an organic molecule or ion required by an enzyme, under biochemical role52206. It is not itself a chemical molecule or a protein-requirement class. |
| iron-group | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33356/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Iron-group-element atom has null prose/default structure and transition-element/d-block-atom parents. It is structural elemental classification. |
| micronutrient | https://www.ebi.ac.uk/chebi/backend/api/public/compound/27027/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Micronutrient is a nutrient required in small quantities by organisms for physiological functions. It does not specify a neutral free iron atom or a particular enzyme requirement. |
| ecoli-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76971/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | E.coli metabolite is a chemical role defined by production during a metabolic reaction in E.coli; its origin annotation is not direct neutral-atom physiology. |
| iron-cation | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24875/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Iron cation is a generic chemical class with formulaFe but null specified charge and default structure. It directly has cofactor role and is distinct from neutral iron atom. |
| ferrous | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29033/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Iron(2+) is the monatomic Fe2+ chemical, charge+2 and SMILES[Fe+2], with direct cofactor role. It is a comparison, not an automatically selected repair for the unresolved alignment scope. |
| ferric | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29034/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Iron(3+) is the monatomic Fe3+ chemical, charge+3 and SMILES[Fe+3], with direct cofactor role. It is chemically distinct from neutral iron and Fe2+; role membership alone does not select the intended state. |
| iron-authority | https://periodic-table.rsc.org/element/26/iron; Element identity and Fact box | supports | The inspected RSC element identity and fact box give Fe, atomic number26 and CAS7439-89-6, agreeing with the source element. Only elemental identity is used; broad statements about universal life/biological need are not promoted to exact-state requirements. |
| iron-enzyme | https://iubmb.qmul.ac.uk/enzyme/EC1/14/11/2.html; Complete reaction, Comments and references | supports | The complete IUBMB EC1.14.11.2 entry explicitly requires Fe2+ and ascorbate for procollagen-proline4-dioxygenase. It provides positive ion-specific enzyme context, not evidence for neutral iron atom18248. Original experimental papers in its reference list were not independently inspected. |
| ecoli-model | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Complete indexed abstract and bibliographic identity | context_only | PMID21988831, DOI10.1038/msb.2011.65: the complete abstract describes the iJO1366 metabolic reconstruction and growth screen. It is source-origin context, not direct measurement of elemental neutral iron in an enzyme. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; Executed 2026-10-21T11:56:31Z through 2026-10-21T11:56:32Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/fad-chebi16238.yaml data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-4-chebi68438.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml data/traits/function/cofactor_requirement/chebi/fe-s-cluster-chebi30408.yaml data/traits/function/cofactor_requirement/chebi/fe4s2o2-iron-sulfur-oxygen-cluster-chebi60519.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-1-chebi60532.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-chebi36183.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-2-chebi60344.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Executed 2026-10-21T11:56:29Z through 2026-10-21T11:58:14Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml; Executed 2026-10-21T11:56:32Z through 2026-10-21T11:56:32Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:58:14Z through 2026-10-21T11:58:15Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- This target was emitted from MGA name/category alignment metadata by seed_cofactor_alignment.py, with ChEBI helper chemistry/licensing. The exact upstream MGA input table and release were not accessed or independently verified; the captured local crosswalk is output provenance. No sibling checkout was accessed. Source role context alone does not qualify a protein or prove obligatory dependence.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The neutral atom and cation comparisons are external chemical evidence, not assessments of local sibling records. The IUBMB enzyme authority supports a specified Fe2+ use; its primary references and any universal neutral-atom requirement were not independently established.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T120310Z-fe-chebi18248
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires Fe
started_at: '2026-10-21T11:55:53Z'
finished_at: '2026-10-21T12:03:10Z'
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
summary: The Fe label correctly resolves to neutral iron atom, while intended ionic
  versus element-level requirement remains unresolved. One confirmed major concerns
  chemical-to-protein-trait equivalence and one confirmed minor concerns the copied
  metals category synonym. Positive Fe2+ enzyme context does not automatically select
  a replacement chemical.
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
  - path: data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
    sha256: 0501b30d73423cf780986830940d1bd8197f8fab4ef4312f1f495a78ddeabffe
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
  selection: Path-order position 2 in batch 021. Fresh main inventory has 429359 records;
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
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7) covers 198 record paths,
    leaving 429161 before this batch. 21 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
targets:
- kind: generated
  label: requires Fe
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_18248
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/fad-chebi16238.yaml
    data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-4-chebi68438.yaml
    data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
    data/traits/function/cofactor_requirement/chebi/fe-s-cluster-chebi30408.yaml data/traits/function/cofactor_requirement/chebi/fe4s2o2-iron-sulfur-oxygen-cluster-chebi60519.yaml
    data/traits/function/cofactor_requirement/chebi/ferriheme-a-1-chebi60532.yaml
    data/traits/function/cofactor_requirement/chebi/ferriheme-a-chebi36183.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-2-chebi60344.yaml
    data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current official ChEBI/OLS and RSC resolve neutral iron18248 with the correct
    element identity. Direct roles, cation comparisons, IUBMB Fe2+ enzyme context
    and exact captured alignment provenance were inspected. This does not resolve
    the intended ionic scope or validate protein-trait equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
  - iron-group
  - micronutrient
  - ecoli-role
  - iron-cation
  - ferrous
  - ferric
  - iron-authority
  - alignment-crosswalk
  - chebi-dependency
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:55:53Z'
  snapshot_sha256: 0501b30d73423cf780986830940d1bd8197f8fab4ef4312f1f495a78ddeabffe
  support: supports
  summary: 'Complete target YAML inspected: local identifier, requires-label, synthesized
    alignment definition with appended ChEBI chemistry, FUNCTION/FUNC_COFACTOR_REQUIREMENT,
    CLASS/SEEDED, cofactor parent, ChEBI chemical xref, licence and both MGA-attributed
    RELATED_SYNONYM values. No optional protein example, graph or chemical_participants
    is asserted.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T11:55:53Z'
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
  accessed_at: '2026-10-21T11:55:53Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main
  accessed_at: '2026-10-21T11:55:53Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: load_mg_cofactors reads sibling reference-table metadata; build_aligned
    synthesizes the protein requirement, attaches the broad cofactor parent, emits
    the chemical xref, and copies cofactor_id/category as RELATED_SYNONYM. main selects
    only missing chemical IDs before considering force, so an existing-record repair
    requires an audited scoped route. This local review does not access the sibling
    checkout.
- evidence_id: chebi-dependency
  kind: record_content
  reference: scripts/seed_chebi_cofactor.py
  locator: load_names, rid, clean, LICENSE and imported helpers
  accessed_at: '2026-10-21T11:55:53Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The alignment emitter imports ChEBI chemical-name/definition loading, identifiers,
    formatting, output location and ChEBI licensing from this module. This dependency
    does not itself establish a role for an alignment-selected chemical.
- evidence_id: alignment-crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and exact row71
  accessed_at: '2026-10-21T11:55:53Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The captured row71 persists CHEBI:18248, Fe, iron_ion and metals. This
    corroborates local alignment output provenance, not an independently inspected
    upstream table release or protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:55:53Z'
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
  locator: Introduction and Licensing
  summary: The official ChEBI Introduction and Licensing sections identify a chemical-entity
    ontology and CC BY4.0. This supports chemical-source attribution, not equality
    to a synthesized protein requirement.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ChEBI version256 loaded2026-10-16.
    Original actual access time and digest are preserved; this is not a release pin
    for the live backend or original seed.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:18248
  accessed_at: '2026-10-21T11:56:55.438217Z'
  snapshot_sha256: 51f2d461cb94f976a3459104b2c2f419a56a386cbf71190689707e3b722b1238
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:18248 as a nonobsolete chemical term; its complete names,
    description and chemical annotations were inspected.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/18248/
  accessed_at: '2026-10-21T11:56:55.242925Z'
  snapshot_sha256: da16f118f0808d33a585f98804b19765f70cea7321b05e9aaf3744db134026b7
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: 'CHEBI:18248 is iron atom: atomic number26, formulaFe, charge0, SMILES[Fe],
    InChI=1S/Fe. Fe/iron aliases and the copied definition agree. Direct roles are
    micronutrient and E.coli metabolite, with iron-group-element-atom parent; the
    inspected outgoing relations do not directly assert cofactor. This is the same
    element as the label, not a wrong-element collision.'
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Cofactor is a biochemical role for an organic molecule or ion required
    by an enzyme, under biochemical role52206. It is not itself a chemical molecule
    or a protein-requirement class.
- evidence_id: iron-group
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33356/
  accessed_at: '2026-10-21T11:57:59.923275Z'
  snapshot_sha256: dfb2890dcf58dc765229e12a535cbecaedad1dbe56c03eb7c78648b04c891cb2
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Iron-group-element atom has null prose/default structure and transition-element/d-block-atom
    parents. It is structural elemental classification.
- evidence_id: micronutrient
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/27027/
  accessed_at: '2026-10-21T11:57:58.589193Z'
  snapshot_sha256: 897b6a0cfa9329e434bddcbedc1130d5c1d8477fcad9218f6f1cd8e48013db84
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Micronutrient is a nutrient required in small quantities by organisms for
    physiological functions. It does not specify a neutral free iron atom or a particular
    enzyme requirement.
- evidence_id: ecoli-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76971/
  accessed_at: '2026-10-21T11:58:00.026086Z'
  snapshot_sha256: 7fc404f615d575d34db7d66cd3ab536694e7ae482367720c36a5002a09d3171d
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: E.coli metabolite is a chemical role defined by production during a metabolic
    reaction in E.coli; its origin annotation is not direct neutral-atom physiology.
- evidence_id: iron-cation
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24875/
  accessed_at: '2026-10-21T11:57:59.925793Z'
  snapshot_sha256: 1904b51785d298775e39ded7d29c6f5dbe68c411668975e2cff304b5ef517d43
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Iron cation is a generic chemical class with formulaFe but null specified
    charge and default structure. It directly has cofactor role and is distinct from
    neutral iron atom.
- evidence_id: ferrous
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29033/
  accessed_at: '2026-10-21T11:58:01.149788Z'
  snapshot_sha256: 2041145da7d4c93d6f8aa2714b8cf0f5ca964725167c991e6e544547c6e145fd
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Iron(2+) is the monatomic Fe2+ chemical, charge+2 and SMILES[Fe+2], with
    direct cofactor role. It is a comparison, not an automatically selected repair
    for the unresolved alignment scope.
- evidence_id: ferric
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29034/
  accessed_at: '2026-10-21T11:58:01.150350Z'
  snapshot_sha256: 73beb7147f1a4bc749c1b4284fdff572962862daade2129d5d3519d800fb928b
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Iron(3+) is the monatomic Fe3+ chemical, charge+3 and SMILES[Fe+3], with
    direct cofactor role. It is chemically distinct from neutral iron and Fe2+; role
    membership alone does not select the intended state.
- evidence_id: iron-authority
  kind: authority
  reference: https://periodic-table.rsc.org/element/26/iron
  accessed_at: '2026-10-21T11:58:58.414770Z'
  snapshot_sha256: 51d2d12fd58c037e223113b5b537510e164e4d22bf607ff1d2ed9cf89de7ffbb
  support: supports
  locator: Element identity and Fact box
  summary: The inspected RSC element identity and fact box give Fe, atomic number26
    and CAS7439-89-6, agreeing with the source element. Only elemental identity is
    used; broad statements about universal life/biological need are not promoted to
    exact-state requirements.
- evidence_id: iron-enzyme
  kind: authority
  reference: https://iubmb.qmul.ac.uk/enzyme/EC1/14/11/2.html
  accessed_at: '2026-10-21T11:58:57.970035Z'
  snapshot_sha256: 55230201e5b80406de1ca6eb3c886ce097704d2bce3a46aee1614f8604573074
  support: supports
  locator: Complete reaction, Comments and references
  summary: The complete IUBMB EC1.14.11.2 entry explicitly requires Fe2+ and ascorbate
    for procollagen-proline4-dioxygenase. It provides positive ion-specific enzyme
    context, not evidence for neutral iron atom18248. Original experimental papers
    in its reference list were not independently inspected.
- evidence_id: ecoli-model
  kind: database
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:37:45.903388Z'
  snapshot_sha256: e25a797a813b88b0e3053e41aacefa22b641206af4570c409c52515a8233a3e0
  support: context_only
  locator: Complete indexed abstract and bibliographic identity
  summary: 'PMID21988831, DOI10.1038/msb.2011.65: the complete abstract describes
    the iJO1366 metabolic reconstruction and growth screen. It is source-origin context,
    not direct measurement of elemental neutral iron in an enzyme.'
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  locator: Executed 2026-10-21T11:56:31Z through 2026-10-21T11:56:32Z; exit 0
  accessed_at: '2026-10-21T11:56:32Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/fad-chebi16238.yaml
    data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-4-chebi68438.yaml
    data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
    data/traits/function/cofactor_requirement/chebi/fe-s-cluster-chebi30408.yaml data/traits/function/cofactor_requirement/chebi/fe4s2o2-iron-sulfur-oxygen-cluster-chebi60519.yaml
    data/traits/function/cofactor_requirement/chebi/ferriheme-a-1-chebi60532.yaml
    data/traits/function/cofactor_requirement/chebi/ferriheme-a-chebi36183.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-2-chebi60344.yaml
    data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  locator: Executed 2026-10-21T11:56:29Z through 2026-10-21T11:58:14Z; exit 0
  accessed_at: '2026-10-21T11:58:14Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
  locator: Executed 2026-10-21T11:56:32Z through 2026-10-21T11:56:32Z; exit 0
  accessed_at: '2026-10-21T11:56:32Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:58:14Z through 2026-10-21T11:58:15Z; exit 0
  accessed_at: '2026-10-21T11:58:15Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: scripts/seed_cofactor_alignment.py owns this aligned requirement, with
    the captured ChEBI helper dependency and crosswalk provenance. No emitted record
    has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: Fe and the copied atomic-number26 definition correctly identify iron, and
    CHEBI18248 specifically encodes a neutral atom. The local iron_ion token is RELATED_SYNONYM,
    so it is not treated as an exact-equivalence assertion or a wrong-element blocker.
    Ionic and element-level scope still require adjudication.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - iron-authority
  - iron-cation
  - ferrous
  - ferric
  topic: Iron elemental identity and exact neutral state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-5
- area: nomenclature
  outcome: concern
  summary: The scientific Fe name remains coherent. iron_ion points toward ionic scope
    while the source identifier is neutral; RELATED scope limits the strength of that
    discrepancy. The independently copied metals grouping token is not an alternate
    scientific label and supports the bounded minor finding.
  evidence_ids:
  - record
  - schema
  - owner
  - alignment-crosswalk
  - chemical
  - iron-cation
  topic: Related ionic token and broad category metadata
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The IUBMB authority explicitly supports Fe2+ in the stated hydroxylase
    activity, and current iron-cation entries carry direct cofactor roles. This positive
    biology is retained without equating those ions to the neutral source atom or
    establishing a universal elemental requirement.
  evidence_ids:
  - iron-enzyme
  - iron-cation
  - ferrous
  - ferric
  - chemical
  topic: Positive iron-ion enzyme context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The alignment name/category and RELATED ionic token do not resolve whether
    the intended class concerns an element, one cation state or a broader iron-containing
    species. A curator must adjudicate that scope before any participant or protein
    qualification. Lack of direct cofactor role on the neutral atom does not prove
    biological impossibility.
  evidence_ids:
  - record
  - schema
  - chemical
  - iron-cation
  - ferrous
  - ferric
  - iron-enzyme
  - alignment-crosswalk
  topic: Neutral atom versus intended iron requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-8
- area: consistency
  outcome: unknown
  summary: The local cofactor parent was attached by build_aligned. Present atom roles
    are micronutrient and E.coli metabolite, whereas cation comparisons have cofactor
    roles. This provenance difference is not a demonstrated universal nonmembership
    counterexample and does not justify an automatic replacement.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - micronutrient
  - ecoli-role
  - iron-cation
  - cofactor-role
  topic: Alignment parent and current source roles
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-9
- area: provenance
  outcome: supported
  summary: Captured crosswalk row71 and the maintained alignment emitter explain Fe/iron_ion/metals
    output. Current official chemistry agrees with the element name but leaves physiological
    state unresolved. The upstream MGA table/release was not independently inspected;
    neither the crosswalk nor the model-origin annotation is experimental qualification.
  evidence_ids:
  - record
  - owner
  - chebi-dependency
  - alignment-crosswalk
  - chemical
  - ecoli-model
  - licence
  - release
  topic: Exact local alignment row and source release limit
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The source chemical and the synthesized protein-requirement class are different
    entity types. Correct chemistry and positive biochemical context do not satisfy
    the schema requirement for true own-source equivalence.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-18248.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: The neutral iron chemical18248 is asserted in the xrefs field of a
    protein-requirement class. Chemical/elemental identity and positive Fe2+ enzyme
    evidence cannot make the neutral atom and protein requirement equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The candidate chemical identity is recognizable, but a chemical
    entity or chemical class and a protein requirement have different denotations.
    The true-equivalence assertion is a major grounding defect; optional participant
    absence is not itself the finding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-18248.category-token-synonym
  category: nomenclature
  severity: minor
  title: Broad metals category is copied into alternate labels
  description: The RELATED_SYNONYM metals is the broad alignment grouping category,
    not an alternate scientific label of this exact requirement. RELATED scope is
    weaker than exact equivalence, but the schema still defines synonyms as alternate
    labels and build_aligned explicitly copies the category into that field.
  evidence_ids:
  - record
  - schema
  - owner
  - alignment-crosswalk
  certainty: confirmed
  field_paths:
  - synonyms
  normalization_reason: The scientific chemical identity remains recognizable. The
    category token is a bounded alternate-label defect; uncertain physiological state
    or universal requirement is not asserted as a confirmed finding.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
actions:
- action_id: A1
  description: Update build_aligned in scripts/seed_cofactor_alignment.py and its
    maintained input/registered override to remove chemical-to-protein-trait equality
    from xrefs while preserving supported chemical grounding and provenance. Resolve
    the intended elemental/ionic scope from maintained curation evidence before choosing
    a participant; do not automatically replace18248 with24875,29033 or29034. Adjudicate
    the activity-relative role before adding a COFACTOR chemical_participant. If that
    role is not supported, retain provenance and explicit uncertainty without inventing
    a participant. Do not relocate the equality to mapped_xrefs, merge chemical states
    or promote protein examples or native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The regenerated xrefs no longer equate a chemical entity/class with the protein
    requirement. Chemical identity, scope and provenance remain auditable; any participant
    has a supported activity-relative role.
  - 'Use an audited route selecting this existing target and a focused alignment fixture:
    main selects only missing IDs before --force, so an ordinary rerun or force alone
    does not repair it.'
  - Run just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
    after the scoped repair. If adjudication changes the target path, validate the
    replacement and retained/deprecated target disposition explicitly.
  - For maintained writer changes add focused pytest coverage and run just audit-writers,
    just lint and just test. Regenerate the existing target through an audited route.
    Run full just validate-all before merging record changes; capture changed inputs
    and save a fresh structured review without overwriting this observation.
- action_id: A2
  description: Stop emitting the broad category as an alternate trait label in the
    maintained alignment input/transform or registered override. Preserve the source
    category as provenance and retain supported scientific names. Adjudicate the iron_ion
    scope separately; do not silently replace the neutral iron identifier with a particular
    cation.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_18248
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The regenerated synonym list distinguishes scientific names from broad grouping
    metadata, and original alignment provenance remains auditable.
  - Use a focused alignment fixture and audited existing-target selection; main selects
    missing IDs before --force.
  - Run just validate data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml
    after the scoped repair. If adjudication changes the target path, validate the
    replacement and retained/deprecated target disposition explicitly.
  - For maintained writer changes add focused pytest coverage and run just audit-writers,
    just lint and just test. Regenerate the existing target through an audited route.
    Run full just validate-all before merging record changes; capture changed inputs
    and save a fresh structured review without overwriting this observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- This target was emitted from MGA name/category alignment metadata by seed_cofactor_alignment.py,
  with ChEBI helper chemistry/licensing. The exact upstream MGA input table and release
  were not accessed or independently verified; the captured local crosswalk is output
  provenance. No sibling checkout was accessed. Source role context alone does not
  qualify a protein or prove obligatory dependence.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The neutral atom and cation comparisons are external chemical evidence, not assessments
  of local sibling records. The IUBMB enzyme authority supports a specified Fe2+ use;
  its primary references and any universal neutral-atom requirement were not independently
  established.
tags:
- unreviewed-path-order
- batch-021
- chebi-cofactor
```
