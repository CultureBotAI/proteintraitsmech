# Review of requires methanophenazine

- Review: 20261021T132752Z-methanophenazine-chebi62733
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:18:16Z
- Finished UTC: 2026-10-21T13:27:52Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

A confirmed blocker separates the methanophenazine label from the aromatic-amide anchor. An independent confirmed mapping major and a category-token synonym minor require identity-first repair; positive phenazine chemistry is retained without automatic replacement or protein qualification.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 5 in batch 026. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) covers 248 record paths, leaving 429111 before this batch. 26 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml | generated | requires methanophenazine |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62733 | Official ChEBI and OLS resolve the requested anchor to aromatic amide, so source resolution is successful but alignment identity validation fails. External methanophenazine chemistry and the primary isolation study corroborate the collision. The captured owner/crosswalk explain provenance; no automatic replacement or protein requirement is certified. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

scripts/seed_cofactor_alignment.py owns this aligned requirement, with the captured ChEBI helper dependency and crosswalk provenance. No emitted record has been edited.

### Protein trait class completeness

completeness: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The target is shaped as a reusable requirement class, but its label, encoded identifier and copied chemical definition do not describe one coherent identity. Optional examples and mechanisms are not the cause of this failure and must not be added to conceal it.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Methanophenazine label versus aromatic-amide anchor

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The current official backend and OLS identify CHEBI:62733 as aromatic amide. The target label and copied alignment metadata say methanophenazine, whose separately resolved CHEBI:29118 structure is a phenazine ether without an amide linkage. This is a positive identity collision, not ambiguity about which local record was requested. The intended exact chemical and identifier lifecycle require curator adjudication.

### Positive methanophenazine identity with bounded functional inference

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The isolation study supports a hydrophobic phenazine ether consistent with the separate methanophenazine entry. Its soluble-analogue enzyme assays and inferred in-vivo role are distinguished from direct exact-state protein requirements. This does not validate the aromatic-amide anchor.

### Identity prerequisite for any chemical participant

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The wrong aromatic-amide identifier must not be moved into a typed participant as a mechanical mapping repair. Exact intended chemical scope, redox state, stereochemical scope and activity-relative role remain subject to adjudication after the identity collision is resolved. No universal negative biological claim follows from the absence of a direct role in the compared chemical snapshots.

### Alignment parent and unresolved chemical identity

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The broad cofactor parent was attached by the alignment emitter, not selected from a direct role of aromatic amide. Its local resolution and biochemical-role ancestry do not validate this child mapping; parent and category scope must be reconsidered with the identity repair.

### Maintained alignment ownership and copied metadata

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The captured alignment emitter, ChEBI helper dependency and exact crosswalk row explain the synthesized requirement, appended chemical prose and copied aliases. This supports provenance of the inconsistency, not the correctness of the mapping. The original upstream table/release was not independently inspected.

### Chemical class versus protein-requirement class

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62733.

The official ChEBI anchor denotes a chemical entity or chemical class, while the local requires-label denotes a protein functional class. These are different denotations under the schema's true-equivalence xrefs semantics. Even after the wrong identifier is corrected, retaining chemical-to-protein-class equality would leave an independent emitter defect.

## Findings

### F1: Methanophenazine requirement is anchored to aromatic amide

blocker / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-62733.identity-conflict.

The label and opening definition request methanophenazine, but CHEBI:62733 and the appended chemical definition denote aromatic amide. Both official chemical services confirm the mismatch, and the independently resolved phenazine-ether identity is chemically incompatible with an amide class. Because the local identifier also encodes 62733, the record cannot support a coherent requirement claim until identity and identifier lifecycle are adjudicated.

### F2: Alignment category other is emitted as a synonym

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-62733.alignment-category-token.

The captured emitter copies the MicroGrowAgents category other into RELATED_SYNONYM, although it is a grouping token rather than an alternate label for this requirement class. RELATED scope does not make arbitrary category metadata a scientific synonym. This local metadata issue is distinct from the blocking chemical identity collision.

### F3: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-62733.chemical-entity-equivalence.

The target uses CHEBI:62733 as a true-equivalence xref for a protein-requirement class, but the official entry denotes an aromatic-amide chemical class. This is an independent schema-level entity-type mismatch. Changing the wrong anchor alone would not repair the emitter's chemical-to-protein-class equality.

## Recommended Actions And Acceptance Checks

### A1

Correct the maintained alignment mapping and its safeguards in scripts/seed_cofactor_alignment.py through a documented curator decision. Evaluate CHEBI:29118 as an external candidate rather than automatically replacing the identifier: resolve intended methanophenazine state and stereochemical scope, the existing encoded local identifier, aliases, definition, parent and downstream references. Do not reinterpret the record as an aromatic-amide requirement or transfer CHEBI:62733 into a participant. Preserve the original provenance and an auditable record lifecycle.

- The regenerated or formally superseded record has one curator-adjudicated chemical identity consistent across label, definition, identifier lifecycle, source association and synonyms. The aromatic-amide collision no longer survives.
- Focused transformation coverage rejects discordant chemical-name/identifier mappings. Existing-record repair uses an audited scoped route, because alignment main selects missing chemical IDs before --force. No unreviewed replacement, protein promotion or unrelated regeneration is performed.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

### A2

After identity adjudication, change build_aligned so the category other remains traceable as alignment provenance rather than being emitted as a trait synonym. Retain a meaningful methanophenazine alias only if it agrees with the adjudicated class.

- The regenerated synonym list omits the category token other, while the original category provenance remains auditable and the meaningful alias is checked against the resolved identity.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

### A3

First complete the identity/lifecycle adjudication; never transfer the currently wrong aromatic-amide identifier. Then correct build_aligned in scripts/seed_cofactor_alignment.py so a chemical association is not emitted as true equality to the protein-requirement class. Preserve chemical provenance and adjudicate exact scope and the required activity-relative ChemicalParticipant.role before adding a typed participant or relation. If the supported scope or role cannot be represented, retain explicit provenance and uncertainty without inventing one. Do not move false equality into mapped_xrefs or automatically promote a protein instance.

- The regenerated class has no chemical-to-protein-class equality. Chemical provenance remains explicit; every typed participant/relation has a curator-adjudicated identity, scope and activity-relative role, or uncertainty is retained.
- Use an audited scoped existing-record regeneration route and focused transformation coverage. Complete the identity prerequisite before any dependent chemical mapping.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml; Entire target YAML | supports | Entire YAML inspected: the requires-methanophenazine label and opening requirement sentence cite CHEBI:62733, while the appended definition describes aromatic amide. The local identifier encodes 62733. Copied RELATED_SYNONYM values methanophenazine and other carry MicroGrowAgents attribution. FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, broad cofactor parent, chemical xref and stated ChEBI licence are retained. No optional examples, causal graph or typed participant occurs. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main | supports | load_mg_cofactors reads sibling reference-table metadata; build_aligned synthesizes the protein requirement, attaches the broad cofactor parent, emits the chemical xref, and copies cofactor_id/category as RELATED_SYNONYM. main selects only missing chemical IDs before considering force, so an existing-record repair requires an audited scoped route. This local review does not access the sibling checkout. |
| chebi-dependency | scripts/seed_chebi_cofactor.py; load_names, rid, clean, LICENSE and imported helpers | supports | The alignment emitter imports ChEBI chemical-name/definition loading, identifiers, formatting, output location and ChEBI licensing from this module. This dependency does not itself establish a role for an alignment-selected chemical. |
| alignment-crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and exact CHEBI:62733 row, line 226 | supports | The captured row records CHEBI:62733, the local requirement identifier, methanophenazine as name and cofactor_id, and other as category. This corroborates the local alignment provenance, not the upstream table release, the chemical mapping or a protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; verified reused raw body with original access UTC | supports | The official ChEBI Introduction and Licensing sections describe a chemical-entity/role resource licensed CC BY 4.0. This supports chemical-source attribution, not equivalence to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS ontology metadata reports version 256 loaded 2026-10-16. Its original access UTC is retained. This does not identify the live backend release or the exact release originally used to generate the target. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/62733/; Complete material identity fields, names, definition/null, chemical data/default structure, citations/origins and complete outgoing relations; incoming descendant lists are not used to establish protein requirements | supports | CHEBI:62733 resolves to aromatic amide, with the definition of an amide linkage bonded directly to an aromatic system. The only listed synonym is aromatic amides; fixed chemical data and structure are null. Its complete outgoing relations are is-a organic aromatic compound and is-a amide, with no direct cofactor-role assertion in this snapshot. The target copies this chemical definition while labeling the requirement methanophenazine, an incompatible identity combination. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:62733; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete identifier and aromatic-amide identity, directly conflicting with the target methanophenazine label. Source resolution verifies attribution, not chemical-to-protein-class equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified original access UTC | supports | Cofactor CHEBI:23357 is an organic molecule or ion required by an enzyme for activity, attached loosely or tightly, and is a biochemical role. A chemical role supplies candidate context rather than protein-class identity. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified original access UTC | supports | Biochemical role CHEBI:52206 is a role of an entity or part within a biochemical context. This is role ancestry, not a chemical identity or independent physiological requirement. |
| context-33659 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33659/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Organic aromatic compound CHEBI:33659 is a broad chemical class under organic cyclic compound and aromatic compound. This ancestry does not make the aromatic-amide subclass equivalent to a phenazine ether. |
| context-32988 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/32988/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Amide CHEBI:32988 is defined by replacement of an acidic hydroxy group of an oxoacid by an amino or substituted amino group. The aromatic-amide parent relation is chemically coherent but does not support the target methanophenazine label. |
| context-29118 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29118/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | CHEBI:29118 resolves separately to methanophenazine, C37H50N2O, charge 0, with a phenazine ring linked through an ether to a partially saturated polyisoprenoid chain. Its prose definition is null. The structure specifies three E double bonds but leaves the side-chain stereocentre unspecified; the terminal alkene has no E/Z distinction. Its only outgoing relation is is-a phenazines CHEBI:39201. This is an identity comparison and candidate for curator adjudication, not an automatic replacement or newly qualified protein requirement. |
| context-39201 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/39201/; Exact identifier, chemical identity/definition, chemical data/default structure and complete outgoing relations | supports | Phenazines CHEBI:39201 comprises organonitrogen heterocycles based on a phenazine skeleton and derivatives. It is a structural parent of CHEBI:29118, distinct from the amide ancestry of CHEBI:62733. |
| candidate-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:29118; Inspected source response captured at the recorded UTC time | supports | OLS independently resolves CHEBI:29118 as methanophenazine, with neutral C37H50N2O phenazine-ether structure and absent prose definition. It does not resolve CHEBI:62733 to that identity. The comparison is external chemistry only, not a local sibling record or an automatic identifier replacement. |
| methanophenazine-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3APMC107126%20OR%20DOI%3A10.1128/jb.180.8.2027-2032.1998&amp;resultType=core&amp;format=json; Verified bibliographic identifiers and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:9555882; DOI:10.1128/jb.180.8.2027-2032.1998. Material isolated from Methanosarcina mazei Gö1 membranes was identified by mass spectroscopy and NMR as a 538 Da hydroxyphenazine derivative with a polyisoprenoid ether linkage. Because methanophenazine was almost insoluble in aqueous buffers, enzyme assays used soluble phenazine derivatives, including 2-hydroxyphenazine. The paper therefore supplies positive identity and electron-transport context, while its in-vivo methanophenazine role is an inference and the analogue assays are not direct exact-state protein qualification. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml; Executed 2026-10-21T13:18:52Z through 2026-10-21T13:18:54Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/magnesium-2-chebi18420.yaml data/traits/function/cofactor_requirement/chebi/manganese-2-chebi29035.yaml data/traits/function/cofactor_requirement/chebi/menaquinone-7-chebi44245.yaml data/traits/function/cofactor_requirement/chebi/metal-sulfur-cluster-chebi25214.yaml data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml data/traits/function/cofactor_requirement/chebi/methylcobalamin-chebi28115.yaml data/traits/function/cofactor_requirement/chebi/mevalonyl-coa-chebi133868.yaml data/traits/function/cofactor_requirement/chebi/mfr-chebi24024.yaml data/traits/function/cofactor_requirement/chebi/moco-chebi25374.yaml data/traits/function/cofactor_requirement/chebi/molybdopterin-cofactor-chebi25372.yaml; Executed 2026-10-21T13:18:40Z through 2026-10-21T13:20:44Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml; Executed 2026-10-21T13:18:54Z through 2026-10-21T13:18:55Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:20:44Z through 2026-10-21T13:20:46Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The candidate requirement comes from the captured alignment emitter and locally persisted crosswalk. The upstream MicroGrowAgents table/release was not independently inspected and no sibling checkout was accessed. Neither the crosswalk nor the chemical-source licence independently validates the alignment identity or physiological requirement.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The methanophenazine study was inspected through its complete indexed abstract. Full-text XML failed and the HTTP-200 HTML response is a reCAPTCHA challenge, both excluded. The complete abstract distinguishes isolated compound chemistry from soluble-analogue assays and inferred in-vivo function. The comparison entry has a null definition and unspecified side-chain stereocentre; no automatic exact replacement is certified.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T132752Z-methanophenazine-chebi62733
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires methanophenazine
started_at: '2026-10-21T13:18:16Z'
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
summary: A confirmed blocker separates the methanophenazine label from the aromatic-amide
  anchor. An independent confirmed mapping major and a category-token synonym minor
  require identity-first repair; positive phenazine chemistry is retained without
  automatic replacement or protein qualification.
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
  - path: data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    sha256: dc700b93c2662cc0d5c2ffc1ccd0854cd31647183143fb19414c78bcbe41a68f
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
  selection: Path-order position 5 in batch 026. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
targets:
- kind: generated
  label: requires methanophenazine
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_62733
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve the requested anchor to aromatic amide,
    so source resolution is successful but alignment identity validation fails. External
    methanophenazine chemistry and the primary isolation study corroborate the collision.
    The captured owner/crosswalk explain provenance; no automatic replacement or protein
    requirement is certified.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - context-33659
  - context-32988
  - context-29118
  - context-39201
  - candidate-ontology
  - methanophenazine-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:18:16Z'
  snapshot_sha256: dc700b93c2662cc0d5c2ffc1ccd0854cd31647183143fb19414c78bcbe41a68f
  support: supports
  summary: 'Entire YAML inspected: the requires-methanophenazine label and opening
    requirement sentence cite CHEBI:62733, while the appended definition describes
    aromatic amide. The local identifier encodes 62733. Copied RELATED_SYNONYM values
    methanophenazine and other carry MicroGrowAgents attribution. FUNCTION/FUNC_COFACTOR_REQUIREMENT,
    CLASS/SEEDED, broad cofactor parent, chemical xref and stated ChEBI licence are
    retained. No optional examples, causal graph or typed participant occurs.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T13:18:16Z'
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
  accessed_at: '2026-10-21T13:18:16Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main
  accessed_at: '2026-10-21T13:18:16Z'
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
  accessed_at: '2026-10-21T13:18:16Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The alignment emitter imports ChEBI chemical-name/definition loading, identifiers,
    formatting, output location and ChEBI licensing from this module. This dependency
    does not itself establish a role for an alignment-selected chemical.
- evidence_id: alignment-crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and exact CHEBI:62733 row, line 226
  accessed_at: '2026-10-21T13:18:16Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The captured row records CHEBI:62733, the local requirement identifier,
    methanophenazine as name and cofactor_id, and other as category. This corroborates
    the local alignment provenance, not the upstream table release, the chemical mapping
    or a protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:18:16Z'
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/62733/
  accessed_at: '2026-10-21T13:18:50.655951Z'
  snapshot_sha256: 99a25b949fed6f15ea75bbf4613614e2a3f1fee016f7b27142a033afeb407e80
  support: supports
  locator: Complete material identity fields, names, definition/null, chemical data/default
    structure, citations/origins and complete outgoing relations; incoming descendant
    lists are not used to establish protein requirements
  summary: CHEBI:62733 resolves to aromatic amide, with the definition of an amide
    linkage bonded directly to an aromatic system. The only listed synonym is aromatic
    amides; fixed chemical data and structure are null. Its complete outgoing relations
    are is-a organic aromatic compound and is-a amide, with no direct cofactor-role
    assertion in this snapshot. The target copies this chemical definition while labeling
    the requirement methanophenazine, an incompatible identity combination.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:62733
  accessed_at: '2026-10-21T13:18:50.680876Z'
  snapshot_sha256: 085502977501f8cfce9d5b4b167d19aa89479c5bbcd1e712ce74f6b40535a1f4
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete identifier and aromatic-amide identity,
    directly conflicting with the target methanophenazine label. Source resolution
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
- evidence_id: context-33659
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33659/
  accessed_at: '2026-10-21T13:20:52.889405Z'
  snapshot_sha256: 3af906d577279f47792991cc923c544a263f13ef946e11efd257776beffa9c6a
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Organic aromatic compound CHEBI:33659 is a broad chemical class under organic
    cyclic compound and aromatic compound. This ancestry does not make the aromatic-amide
    subclass equivalent to a phenazine ether.
- evidence_id: context-32988
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/32988/
  accessed_at: '2026-10-21T13:20:52.899878Z'
  snapshot_sha256: ca6bd95255b63645f1ef888d725d676946a181771c75fcd843d36b50414f1443
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Amide CHEBI:32988 is defined by replacement of an acidic hydroxy group
    of an oxoacid by an amino or substituted amino group. The aromatic-amide parent
    relation is chemically coherent but does not support the target methanophenazine
    label.
- evidence_id: context-29118
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29118/
  accessed_at: '2026-10-21T13:20:52.988195Z'
  snapshot_sha256: 0fd5cfa97aa6aeca7a808aa8e49adc69ba64ffec6bfb4215b4af43286236d7f6
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: CHEBI:29118 resolves separately to methanophenazine, C37H50N2O, charge
    0, with a phenazine ring linked through an ether to a partially saturated polyisoprenoid
    chain. Its prose definition is null. The structure specifies three E double bonds
    but leaves the side-chain stereocentre unspecified; the terminal alkene has no
    E/Z distinction. Its only outgoing relation is is-a phenazines CHEBI:39201. This
    is an identity comparison and candidate for curator adjudication, not an automatic
    replacement or newly qualified protein requirement.
- evidence_id: context-39201
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/39201/
  accessed_at: '2026-10-21T13:21:28.750163Z'
  snapshot_sha256: 00226f7409eb3f03bc6dd3a70f65671b50ee9eb677b85ecd66485ea5a5ac30d2
  support: supports
  locator: Exact identifier, chemical identity/definition, chemical data/default structure
    and complete outgoing relations
  summary: Phenazines CHEBI:39201 comprises organonitrogen heterocycles based on a
    phenazine skeleton and derivatives. It is a structural parent of CHEBI:29118,
    distinct from the amide ancestry of CHEBI:62733.
- evidence_id: candidate-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:29118
  accessed_at: '2026-10-21T13:20:53.182980Z'
  snapshot_sha256: 5632fb47e4cd458ab2136606608aff868fbe27f99949c22ad92dd2122a54d859
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS independently resolves CHEBI:29118 as methanophenazine, with neutral
    C37H50N2O phenazine-ether structure and absent prose definition. It does not resolve
    CHEBI:62733 to that identity. The comparison is external chemistry only, not a
    local sibling record or an automatic identifier replacement.
- evidence_id: methanophenazine-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3APMC107126%20OR%20DOI%3A10.1128/jb.180.8.2027-2032.1998&resultType=core&format=json
  accessed_at: '2026-10-21T13:20:53.881451Z'
  snapshot_sha256: 7ae1cc05f8dfc18d316b2d749977c6662e72cee24637bc28e7995a89aefcde6f
  support: supports
  locator: Verified bibliographic identifiers and complete indexed abstract; full
    experimental paper not inspected through this response
  summary: PMID:9555882; DOI:10.1128/jb.180.8.2027-2032.1998. Material isolated from
    Methanosarcina mazei Gö1 membranes was identified by mass spectroscopy and NMR
    as a 538 Da hydroxyphenazine derivative with a polyisoprenoid ether linkage. Because
    methanophenazine was almost insoluble in aqueous buffers, enzyme assays used soluble
    phenazine derivatives, including 2-hydroxyphenazine. The paper therefore supplies
    positive identity and electron-transport context, while its in-vivo methanophenazine
    role is an inference and the analogue assays are not direct exact-state protein
    qualification.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  locator: Executed 2026-10-21T13:18:52Z through 2026-10-21T13:18:54Z; exit 0
  accessed_at: '2026-10-21T13:18:54Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
  locator: Executed 2026-10-21T13:18:54Z through 2026-10-21T13:18:55Z; exit 0
  accessed_at: '2026-10-21T13:18:55Z'
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
  summary: scripts/seed_cofactor_alignment.py owns this aligned requirement, with
    the captured ChEBI helper dependency and crosswalk provenance. No emitted record
    has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: concern
  summary: The target is shaped as a reusable requirement class, but its label, encoded
    identifier and copied chemical definition do not describe one coherent identity.
    Optional examples and mechanisms are not the cause of this failure and must not
    be added to conceal it.
  evidence_ids:
  - record
  - schema
  - chemical
  - context-29118
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: concern
  summary: The current official backend and OLS identify CHEBI:62733 as aromatic amide.
    The target label and copied alignment metadata say methanophenazine, whose separately
    resolved CHEBI:29118 structure is a phenazine ether without an amide linkage.
    This is a positive identity collision, not ambiguity about which local record
    was requested. The intended exact chemical and identifier lifecycle require curator
    adjudication.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-29118
  - candidate-ontology
  - methanophenazine-primary
  topic: Methanophenazine label versus aromatic-amide anchor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The isolation study supports a hydrophobic phenazine ether consistent with
    the separate methanophenazine entry. Its soluble-analogue enzyme assays and inferred
    in-vivo role are distinguished from direct exact-state protein requirements. This
    does not validate the aromatic-amide anchor.
  evidence_ids:
  - methanophenazine-primary
  - context-29118
  topic: Positive methanophenazine identity with bounded functional inference
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The wrong aromatic-amide identifier must not be moved into a typed participant
    as a mechanical mapping repair. Exact intended chemical scope, redox state, stereochemical
    scope and activity-relative role remain subject to adjudication after the identity
    collision is resolved. No universal negative biological claim follows from the
    absence of a direct role in the compared chemical snapshots.
  evidence_ids:
  - record
  - schema
  - chemical
  - context-29118
  - methanophenazine-primary
  topic: Identity prerequisite for any chemical participant
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-7
- area: consistency
  outcome: unknown
  summary: The broad cofactor parent was attached by the alignment emitter, not selected
    from a direct role of aromatic amide. Its local resolution and biochemical-role
    ancestry do not validate this child mapping; parent and category scope must be
    reconsidered with the identity repair.
  evidence_ids:
  - record
  - owner
  - alignment-crosswalk
  - local-parent-1
  - chemical
  - cofactor-role
  topic: Alignment parent and unresolved chemical identity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The captured alignment emitter, ChEBI helper dependency and exact crosswalk
    row explain the synthesized requirement, appended chemical prose and copied aliases.
    This supports provenance of the inconsistency, not the correctness of the mapping.
    The original upstream table/release was not independently inspected.
  evidence_ids:
  - record
  - owner
  - chebi-dependency
  - alignment-crosswalk
  - registry
  - chemical
  - licence
  topic: Maintained alignment ownership and copied metadata
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The official ChEBI anchor denotes a chemical entity or chemical class,
    while the local requires-label denotes a protein functional class. These are different
    denotations under the schema's true-equivalence xrefs semantics. Even after the
    wrong identifier is corrected, retaining chemical-to-protein-class equality would
    leave an independent emitter defect.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical class versus protein-requirement class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-62733.identity-conflict
  category: grounding
  severity: blocker
  title: Methanophenazine requirement is anchored to aromatic amide
  description: The label and opening definition request methanophenazine, but CHEBI:62733
    and the appended chemical definition denote aromatic amide. Both official chemical
    services confirm the mismatch, and the independently resolved phenazine-ether
    identity is chemically incompatible with an amide class. Because the local identifier
    also encodes 62733, the record cannot support a coherent requirement claim until
    identity and identifier lifecycle are adjudicated.
  evidence_ids:
  - record
  - owner
  - alignment-crosswalk
  - chemical
  - chemical-ontology
  - context-29118
  - candidate-ontology
  - methanophenazine-primary
  certainty: confirmed
  field_paths:
  - identifier
  - label
  - definition
  - synonyms
  - xrefs
  - parent_traits
  normalization_reason: The chemical anchor resolves to a different chemical class
    from the named requirement, preventing coherent interpretation. This is a blocker
    requiring identity adjudication, not a failure to locate the requested record.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: blocker
- issue_key: chebi.cofactor-requirement.CHEBI-62733.alignment-category-token
  category: nomenclature
  severity: minor
  title: Alignment category other is emitted as a synonym
  description: The captured emitter copies the MicroGrowAgents category other into
    RELATED_SYNONYM, although it is a grouping token rather than an alternate label
    for this requirement class. RELATED scope does not make arbitrary category metadata
    a scientific synonym. This local metadata issue is distinct from the blocking
    chemical identity collision.
  evidence_ids:
  - record
  - schema
  - owner
  - alignment-crosswalk
  certainty: confirmed
  field_paths:
  - synonyms
  normalization_reason: This is an ancillary category-to-label transformation defect;
    its minor severity does not imply that the separate blocked identity is valid.
    Repair follows identity adjudication.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
- issue_key: chebi.cofactor-requirement.CHEBI-62733.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The target uses CHEBI:62733 as a true-equivalence xref for a protein-requirement
    class, but the official entry denotes an aromatic-amide chemical class. This is
    an independent schema-level entity-type mismatch. Changing the wrong anchor alone
    would not repair the emitter's chemical-to-protein-class equality.
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
    defect independently of biological plausibility. This repair is dependent on the
    separate blocking identity adjudication and must not preserve the wrong chemical
    in a participant.
  finding_id: F3
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
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
  description: 'Correct the maintained alignment mapping and its safeguards in scripts/seed_cofactor_alignment.py
    through a documented curator decision. Evaluate CHEBI:29118 as an external candidate
    rather than automatically replacing the identifier: resolve intended methanophenazine
    state and stereochemical scope, the existing encoded local identifier, aliases,
    definition, parent and downstream references. Do not reinterpret the record as
    an aromatic-amide requirement or transfer CHEBI:62733 into a participant. Preserve
    the original provenance and an auditable record lifecycle.'
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The regenerated or formally superseded record has one curator-adjudicated chemical
    identity consistent across label, definition, identifier lifecycle, source association
    and synonyms. The aromatic-amide collision no longer survives.
  - Focused transformation coverage rejects discordant chemical-name/identifier mappings.
    Existing-record repair uses an audited scoped route, because alignment main selects
    missing chemical IDs before --force. No unreviewed replacement, protein promotion
    or unrelated regeneration is performed.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
- action_id: A2
  description: After identity adjudication, change build_aligned so the category other
    remains traceable as alignment provenance rather than being emitted as a trait
    synonym. Retain a meaningful methanophenazine alias only if it agrees with the
    adjudicated class.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The regenerated synonym list omits the category token other, while the original
    category provenance remains auditable and the meaningful alias is checked against
    the resolved identity.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
  depends_on:
  - A1
  blockers:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261021T132752Z-methanophenazine-chebi62733
    finding_id: F1
- action_id: A3
  description: First complete the identity/lifecycle adjudication; never transfer
    the currently wrong aromatic-amide identifier. Then correct build_aligned in scripts/seed_cofactor_alignment.py
    so a chemical association is not emitted as true equality to the protein-requirement
    class. Preserve chemical provenance and adjudicate exact scope and the required
    activity-relative ChemicalParticipant.role before adding a typed participant or
    relation. If the supported scope or role cannot be represented, retain explicit
    provenance and uncertainty without inventing one. Do not move false equality into
    mapped_xrefs or automatically promote a protein instance.
  finding_ids:
  - F3
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62733
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The regenerated class has no chemical-to-protein-class equality. Chemical provenance
    remains explicit; every typed participant/relation has a curator-adjudicated identity,
    scope and activity-relative role, or uncertainty is retained.
  - Use an audited scoped existing-record regeneration route and focused transformation
    coverage. Complete the identity prerequisite before any dependent chemical mapping.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/methanophenazine-chebi62733.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
  depends_on:
  - A1
  blockers:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261021T132752Z-methanophenazine-chebi62733
    finding_id: F1
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The candidate requirement comes from the captured alignment emitter and locally
  persisted crosswalk. The upstream MicroGrowAgents table/release was not independently
  inspected and no sibling checkout was accessed. Neither the crosswalk nor the chemical-source
  licence independently validates the alignment identity or physiological requirement.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The methanophenazine study was inspected through its complete indexed abstract.
  Full-text XML failed and the HTTP-200 HTML response is a reCAPTCHA challenge, both
  excluded. The complete abstract distinguishes isolated compound chemistry from soluble-analogue
  assays and inferred in-vivo function. The comparison entry has a null definition
  and unspecified side-chain stereocentre; no automatic exact replacement is certified.
tags:
- unreviewed-path-order
- batch-026
- chebi-cofactor
```
