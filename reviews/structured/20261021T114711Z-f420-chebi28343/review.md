# Review of requires F420

- Review: 20261021T114711Z-f420-chebi28343
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:35:33Z
- Finished UTC: 2026-10-21T11:47:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The F420-labelled requirement points to a macrolide glycoside, a confirmed identity blocker. A separate confirmed major chemical-to-protein-trait equivalence defect requires identity repair first. Exact F420 comparison chemistry and biosynthetic context do not automatically choose the intended chain length, charge or redox state.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 9 in batch 020. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87) covers 188 record paths, leaving 429171 before this batch. 20 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml | generated | requires F420 |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28343 | Official ChEBI and OLS resolve the exact source identifier but contradict the local F420 identity. Ownership, crosswalk and source/licence inspection are established; the alignment is not validated. External comparisons and primary context do not automatically select a replacement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

scripts/seed_cofactor_alignment.py owns this aligned requirement, with the captured ChEBI helper dependency and crosswalk provenance. No emitted record has been edited.

### Protein trait class completeness

completeness: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The YAML is shaped as a reusable requirement class rather than a protein instance, but its intended chemical identity is not coherent across label and identifier. Optional representations are not required to diagnose this positive identity conflict; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### F420 label versus macrolide glycoside identity

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

CHEBI:28343 positively resolves to 3-O-alpha-mycarosylerythronolide B, whose formula and glycosylated macrolide connectivity disagree with F420 deazaflavin chemistry. This is a different molecule, not a tail-length, protonation, stereochemical or redox variant. The source provides no prose definition; the local F420 label cannot supply one for the macrolide.

### F420 chemistry and biosynthetic context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The comparison F420-2 has a direct coenzyme role and an exact oxidized gamma-linked two-glutamyl structure. The primary CofD abstract reports precursor complexes and assays supporting F420 biosynthesis. It provides bounded positive F420 context, not direct proof that every generic F420 requirement selects this chain length or that a macrolide is F420. Reduction to the 1,5-dihydro form is distinct from deprotonation.

### Intended F420 class and exact state

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The current alignment does not support one coherent chemical identity. Generic F420, an exact glutamyl chain, a conjugate charge state and reduced versus oxidized forms must be adjudicated before any replacement or participant is selected. No source-role transfer from the comparison to the macrolide is legitimate.

### Maintained alignment provenance and source resolution

provenance: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The alignment emitter and exact crosswalk row explain the local source attribution, but they preserve a positively wrong chemical association; current official resolution does not validate the alignment. The ChEBI helper supplies chemistry/licensing, while the original MGA table and release remain uninspected.

### Alignment parent and chemical-role provenance

consistency: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The captured local cofactor parent resolves structurally. It was attached by the alignment emitter, not justified by a current direct ChEBI cofactor assertion for this exact chemical. The identity collision prevents coherent requirement hierarchy grounding until repaired.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28343.

The xref denotes a chemical entity while the local class denotes a protein functional requirement. Even after the identity collision is repaired, those different entity types cannot be asserted equal; this semantic defect has a separate dependent repair.

## Findings

### F1: F420 label is paired with 3-O-alpha-mycarosylerythronolide B

blocker / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-28343.f420-macrolide-identity-collision.

The defining label and alignment aliases identify F420, while the exact CHEBI identifier resolves to 3-O-alpha-mycarosylerythronolide B. Names, formula and structure provide positive incompatible identities. Resolving the local target path is possible, but it does not validate this association.

### F2: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-28343.chemical-entity-equivalence.

The source chemical in xrefs and the local requirement class have different denotations. Source roles, alignment metadata and bounded biological activity do not satisfy true own-source equivalence. This is distinct from the wrong-identity blocker and its repair depends on resolving that blocker first.

## Recommended Actions And Acceptance Checks

### A1

Audit and correct the maintained alignment input or registered override and build_aligned identity checks before regeneration. Adjudicate the intended chemical scope, including generic versus exact F420 chain length, stereochemistry, charge and redox state, and reconcile the existing identifier/path lifecycle and collisions through an audited route. Do not relabel the currently identified chemical, automatically select a comparison entry, transfer its biological evidence, or move the wrong ID into chemical_participants. Remove the copied broad category token from alternate-label output while preserving its provenance. The original upstream table must be inspected through an authorized source route before claiming it is fixed.

- Positive chemical identity agrees across the regenerated label, identifier, definition and scientific aliases. The selected scope is explicitly adjudicated; a participant rewrite cannot hide the wrong identity.
- A focused alignment fixture rejects incompatible identifiers/names and grouping tokens. Existing targets are explicitly selected and reconciled; main selects missing IDs before --force, so force alone is not an existing-record repair. No implicit identity reassignment or protein/status promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

### A2

After the identity collision is resolved and the intended chemical scope is explicitly adjudicated, update build_aligned and its maintained input/override. Do not preserve the current wrong chemical ID as a participant for the labelled trait. Remove chemical-to-protein-trait equality and preserve supported chemical grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role and exact state before adding a typed participant; a source role or alignment label is not independent protein qualification. If the evidence cannot support the required participant role, retain provenance and explicit uncertainty without inventing a participant. Do not move the equality to mapped_xrefs, merge chemical states or automatically qualify proteins.

- The chemical association no longer asserts equality to the protein requirement. Exact identity and candidate provenance remain auditable; any participant has a curator-adjudicated activity-relative role or uncertainty remains explicit.
- Use an audited route selecting the existing target and a focused source-transform fixture. The alignment main missing-only selection is not bypassed by --force alone. No native status, protein example or obligatory physiological requirement is promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml; Entire target YAML | supports | Complete target YAML inspected: local identifier, requires-label, synthesized alignment definition, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, ChEBI chemical xref and CC-BY 4.0 statement, broad cofactor parent and MGA-attributed RELATED_SYNONYM values f420 and other. No optional example, graph, qualified protein assertion or chemical_participants is present. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main | supports | load_mg_cofactors reads sibling reference-table metadata; build_aligned synthesizes the protein requirement, attaches the broad cofactor parent, emits the chemical xref, and copies cofactor_id/category as RELATED_SYNONYM. main selects only missing chemical IDs before considering force, so an existing-record repair requires an audited scoped route. This local review does not access the sibling checkout. |
| chebi-dependency | scripts/seed_chebi_cofactor.py; load_names, rid, clean, LICENSE and imported helpers | supports | The alignment emitter imports ChEBI chemical-name/definition loading, identifiers, formatting, output location and ChEBI licensing from this module. This dependency does not itself establish a role for an alignment-selected chemical. |
| alignment-crosswalk | data/mappings/cofactor_crosswalk.tsv; Exact target CHEBI identifier row and header | supports | The exact chemical-ID row records the locally persisted alignment name, cofactor identifier and category. It is curation provenance, not an independently verified protein requirement or a release-pinned external source table. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The inspected ChEBI chemical-scope and Licensing sections state CC BY 4.0. This supports ChEBI attribution, not chemical-to-protein-trait equality. It does not certify the uninspected upstream MGA table. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16. Its original access time and digest are retained; this does not assign a release to the original seed or live backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/28343/; Complete identifier, names, definition or null, formula/charge, structure, origins, role classification and outgoing relations | supports | CHEBI:28343 is 3-O-alpha-mycarosylerythronolide B, a stereospecified neutral macrolide glycoside C28H50O10, with no nitrogen or phosphorus. Its names and fixed structure describe an alpha-mycarosyl substituent on an erythronolide scaffold, not a deazaflavin F420 coenzyme. The prose definition is null; the outgoing structural parent is erythronolide CHEBI:23955 and the displayed inherited role is metabolite, not a direct cofactor assertion. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:28343; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier and source identity. The actual prose definition is empty; it is not replaced by the local alignment label. Resolution of the chemical identifier is distinct from validation of the protein-trait assertion. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, under biochemical role CHEBI:52206. It is not itself a chemical molecule or an equivalent protein-requirement class. |
| context-23955 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23955/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Erythronolide CHEBI:23955 has a null prose definition and no fixed default structure in this response. Its outgoing relations place it under macrolide and assert metabolite role; this is context for CHEBI:28343, not an F420 identity. |
| context-25212 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25212/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Metabolite is a biochemical role for an intermediate or product of metabolism. The role is not a molecule, and it does not independently establish or exclude a cofactor role. |
| context-15823 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15823/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | 1,5-Dihydrocoenzyme F420 CHEBI:15823 has neutral formula C29H38N5O18P and functional parent CHEBI:16848. The extra two hydrogens and altered deazaflavin ring distinguish reduction from phosphate/carboxyl protonation. This exact reduced two-glutamyl structure is a comparison, not an automatically intended replacement for a generic F420 label. |
| context-23354 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Coenzyme is a biochemical role for a dissociable low-molecular-weight organic donor or acceptor of chemical groups or electrons; its parent is cofactor CHEBI:23357. The role and the chemical bearing it are not equivalent to a protein requirement. |
| f420-comparison | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16848/; Inspected source response captured at the recorded UTC time | supports | Verified reused official CHEBI:16848 identifies neutral coenzyme gamma-F420-2, C29H36N5O18P, with an oxidized deazaflavin, D-ribityl/S-lactyl connectivity and a gamma-linked L-glutamyl-L-glutamate tail. It directly has coenzyme role. Original access UTC and digest are retained. This is one exact two-glutamyl chemical, not an automatic resolution of every generic F420 label. |
| primary-18252724 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18252724%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | supports | PMID:18252724; DOI:10.1074/jbc.M710352200. The complete abstract identifies F420 as a hydride carrier and reports Methanosarcina mazei CofD structures with Fo and phosphate or GDP plus binding assays. The actual experiments concern biosynthetic substrates and complexes, not a macrolide F420 identity, universal chain length or qualification of every F420-dependent protein. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml; Executed 2026-10-21T11:36:44Z through 2026-10-21T11:36:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-chebi73115.yaml data/traits/function/cofactor_requirement/chebi/dy-chebi33373.yaml data/traits/function/cofactor_requirement/chebi/echinenone-chebi4746.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-1-chebi77805.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-6-chebi38150.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml data/traits/function/cofactor_requirement/chebi/er-chebi33379.yaml data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml data/traits/function/cofactor_requirement/chebi/fad-3-chebi57692.yaml; Executed 2026-10-21T11:36:19Z through 2026-10-21T11:38:17Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml; Executed 2026-10-21T11:36:47Z through 2026-10-21T11:36:47Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:38:17Z through 2026-10-21T11:38:18Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The alignment-selected requirement comes from locally persisted MGA name/category metadata, not a demonstrated direct ChEBI cofactor-role selection. The original sibling reference table, its upstream provenance and release were not accessed or independently verified. The captured crosswalk is output provenance, not independent physiology or the emitter input.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The F420 comparison is deliberately one exact neutral gamma-linked two-glutamyl chemical. Generic F420 scope, other chain lengths, stereochemistry, charge and redox states are not automatically interchangeable. The primary biosynthesis paper was inspected through its complete indexed abstract only; its older biosynthetic account is not used to certify every current biosynthetic pathway. The macrolide may have other biological roles, which neither repair nor excuse the F420 identity conflict.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T114711Z-f420-chebi28343
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires F420
started_at: '2026-10-21T11:35:33Z'
finished_at: '2026-10-21T11:47:11Z'
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
summary: The F420-labelled requirement points to a macrolide glycoside, a confirmed
  identity blocker. A separate confirmed major chemical-to-protein-trait equivalence
  defect requires identity repair first. Exact F420 comparison chemistry and biosynthetic
  context do not automatically choose the intended chain length, charge or redox state.
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
  - path: data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
    sha256: 0b82892d66a82771b9ffb71afbcd1e3558447cc88c26fd05425efd12d333704c
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
  selection: Path-order position 9 in batch 020. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87)
    covers 188 record paths, leaving 429171 before this batch. 20 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
targets:
- kind: generated
  label: requires F420
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_28343
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-chebi73115.yaml
    data/traits/function/cofactor_requirement/chebi/dy-chebi33373.yaml data/traits/function/cofactor_requirement/chebi/echinenone-chebi4746.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-1-chebi77805.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-6-chebi38150.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml data/traits/function/cofactor_requirement/chebi/er-chebi33379.yaml
    data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
    data/traits/function/cofactor_requirement/chebi/fad-3-chebi57692.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve the exact source identifier but contradict
    the local F420 identity. Ownership, crosswalk and source/licence inspection are
    established; the alignment is not validated. External comparisons and primary
    context do not automatically select a replacement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-23955
  - context-25212
  - context-15823
  - context-23354
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:35:33Z'
  snapshot_sha256: 0b82892d66a82771b9ffb71afbcd1e3558447cc88c26fd05425efd12d333704c
  support: supports
  summary: 'Complete target YAML inspected: local identifier, requires-label, synthesized
    alignment definition, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, ChEBI
    chemical xref and CC-BY 4.0 statement, broad cofactor parent and MGA-attributed
    RELATED_SYNONYM values f420 and other. No optional example, graph, qualified protein
    assertion or chemical_participants is present.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T11:35:33Z'
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
  accessed_at: '2026-10-21T11:35:33Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main
  accessed_at: '2026-10-21T11:35:33Z'
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
  accessed_at: '2026-10-21T11:35:33Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The alignment emitter imports ChEBI chemical-name/definition loading, identifiers,
    formatting, output location and ChEBI licensing from this module. This dependency
    does not itself establish a role for an alignment-selected chemical.
- evidence_id: alignment-crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Exact target CHEBI identifier row and header
  accessed_at: '2026-10-21T11:35:33Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The exact chemical-ID row records the locally persisted alignment name,
    cofactor identifier and category. It is curation provenance, not an independently
    verified protein requirement or a release-pinned external source table.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:35:33Z'
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
  summary: The inspected ChEBI chemical-scope and Licensing sections state CC BY 4.0.
    This supports ChEBI attribution, not chemical-to-protein-trait equality. It does
    not certify the uninspected upstream MGA table.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16.
    Its original access time and digest are retained; this does not assign a release
    to the original seed or live backend.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/28343/
  accessed_at: '2026-10-21T11:36:40.153842Z'
  snapshot_sha256: 015598eb97554d05104ff17b2dc5f097508f1bbaa015911b769a346dbc8cfd3a
  support: supports
  locator: Complete identifier, names, definition or null, formula/charge, structure,
    origins, role classification and outgoing relations
  summary: CHEBI:28343 is 3-O-alpha-mycarosylerythronolide B, a stereospecified neutral
    macrolide glycoside C28H50O10, with no nitrogen or phosphorus. Its names and fixed
    structure describe an alpha-mycarosyl substituent on an erythronolide scaffold,
    not a deazaflavin F420 coenzyme. The prose definition is null; the outgoing structural
    parent is erythronolide CHEBI:23955 and the displayed inherited role is metabolite,
    not a direct cofactor assertion.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:28343
  accessed_at: '2026-10-21T11:36:39.483954Z'
  snapshot_sha256: 359477cc54c88ad1f530a7d5c4cf20decc11b28987f8a55b4d5303671b1205b7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier and source identity.
    The actual prose definition is empty; it is not replaced by the local alignment
    label. Resolution of the chemical identifier is distinct from validation of the
    protein-trait assertion.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity, under biochemical role CHEBI:52206. It is not itself
    a chemical molecule or an equivalent protein-requirement class.
- evidence_id: context-23955
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23955/
  accessed_at: '2026-10-21T11:37:44.209831Z'
  snapshot_sha256: 7c8d8ff5efc532598d810204213a86412d4806ecc9cd851b6c4b82c79f65d72f
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Erythronolide CHEBI:23955 has a null prose definition and no fixed default
    structure in this response. Its outgoing relations place it under macrolide and
    assert metabolite role; this is context for CHEBI:28343, not an F420 identity.
- evidence_id: context-25212
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25212/
  accessed_at: '2026-10-21T11:38:19.854200Z'
  snapshot_sha256: 596fe26466d05ad247af5b0026873d927902432b013fe65daa73a51512ebb53a
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Metabolite is a biochemical role for an intermediate or product of metabolism.
    The role is not a molecule, and it does not independently establish or exclude
    a cofactor role.
- evidence_id: context-15823
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15823/
  accessed_at: '2026-10-21T11:38:19.854053Z'
  snapshot_sha256: 97567cc7a804ba3fd909dbba27da4e4c7a19ebed4d81a1a0b49dae6b39b1fc5d
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: 1,5-Dihydrocoenzyme F420 CHEBI:15823 has neutral formula C29H38N5O18P and
    functional parent CHEBI:16848. The extra two hydrogens and altered deazaflavin
    ring distinguish reduction from phosphate/carboxyl protonation. This exact reduced
    two-glutamyl structure is a comparison, not an automatically intended replacement
    for a generic F420 label.
- evidence_id: context-23354
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T11:38:19.854129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Coenzyme is a biochemical role for a dissociable low-molecular-weight organic
    donor or acceptor of chemical groups or electrons; its parent is cofactor CHEBI:23357.
    The role and the chemical bearing it are not equivalent to a protein requirement.
- evidence_id: f420-comparison
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16848/
  accessed_at: '2026-10-21T10:26:00.410708Z'
  snapshot_sha256: 9803a4ae7bc3d8a3bb21d76a7a736e904d688d201343de93d90d0b6745a3d275
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused official CHEBI:16848 identifies neutral coenzyme gamma-F420-2,
    C29H36N5O18P, with an oxidized deazaflavin, D-ribityl/S-lactyl connectivity and
    a gamma-linked L-glutamyl-L-glutamate tail. It directly has coenzyme role. Original
    access UTC and digest are retained. This is one exact two-glutamyl chemical, not
    an automatic resolution of every generic F420 label.
- evidence_id: primary-18252724
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18252724%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:38:20.518809Z'
  snapshot_sha256: f4c719ace4c5688a2ade290d3410f02097baea9f4ad070381429686d912d2511
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:18252724; DOI:10.1074/jbc.M710352200. The complete abstract identifies
    F420 as a hydride carrier and reports Methanosarcina mazei CofD structures with
    Fo and phosphate or GDP plus binding assays. The actual experiments concern biosynthetic
    substrates and complexes, not a macrolide F420 identity, universal chain length
    or qualification of every F420-dependent protein.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  locator: Executed 2026-10-21T11:36:44Z through 2026-10-21T11:36:47Z; exit 0
  accessed_at: '2026-10-21T11:36:47Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-chebi73115.yaml
    data/traits/function/cofactor_requirement/chebi/dy-chebi33373.yaml data/traits/function/cofactor_requirement/chebi/echinenone-chebi4746.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-1-chebi77805.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-6-chebi38150.yaml
    data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml data/traits/function/cofactor_requirement/chebi/er-chebi33379.yaml
    data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
    data/traits/function/cofactor_requirement/chebi/fad-3-chebi57692.yaml
  locator: Executed 2026-10-21T11:36:19Z through 2026-10-21T11:38:17Z; exit 0
  accessed_at: '2026-10-21T11:38:17Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
  locator: Executed 2026-10-21T11:36:47Z through 2026-10-21T11:36:47Z; exit 0
  accessed_at: '2026-10-21T11:36:47Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:38:17Z through 2026-10-21T11:38:18Z; exit 0
  accessed_at: '2026-10-21T11:38:18Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-1
  topic: Maintained cofactor requirement emitter
- area: completeness
  outcome: concern
  summary: The YAML is shaped as a reusable requirement class rather than a protein
    instance, but its intended chemical identity is not coherent across label and
    identifier. Optional representations are not required to diagnose this positive
    identity conflict; none are newly qualified.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: concern
  summary: CHEBI:28343 positively resolves to 3-O-alpha-mycarosylerythronolide B,
    whose formula and glycosylated macrolide connectivity disagree with F420 deazaflavin
    chemistry. This is a different molecule, not a tail-length, protonation, stereochemical
    or redox variant. The source provides no prose definition; the local F420 label
    cannot supply one for the macrolide.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - f420-comparison
  - context-15823
  - alignment-crosswalk
  topic: F420 label versus macrolide glycoside identity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The comparison F420-2 has a direct coenzyme role and an exact oxidized
    gamma-linked two-glutamyl structure. The primary CofD abstract reports precursor
    complexes and assays supporting F420 biosynthesis. It provides bounded positive
    F420 context, not direct proof that every generic F420 requirement selects this
    chain length or that a macrolide is F420. Reduction to the 1,5-dihydro form is
    distinct from deprotonation.
  evidence_ids:
  - f420-comparison
  - context-15823
  - context-23354
  - primary-18252724
  topic: F420 chemistry and biosynthetic context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The current alignment does not support one coherent chemical identity.
    Generic F420, an exact glutamyl chain, a conjugate charge state and reduced versus
    oxidized forms must be adjudicated before any replacement or participant is selected.
    No source-role transfer from the comparison to the macrolide is legitimate.
  evidence_ids:
  - record
  - schema
  - chemical
  - f420-comparison
  - context-15823
  - owner
  topic: Intended F420 class and exact state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-7
- area: provenance
  outcome: concern
  summary: The alignment emitter and exact crosswalk row explain the local source
    attribution, but they preserve a positively wrong chemical association; current
    official resolution does not validate the alignment. The ChEBI helper supplies
    chemistry/licensing, while the original MGA table and release remain uninspected.
  evidence_ids:
  - record
  - owner
  - chebi-dependency
  - alignment-crosswalk
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: Maintained alignment provenance and source resolution
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-8
- area: consistency
  outcome: concern
  summary: The captured local cofactor parent resolves structurally. It was attached
    by the alignment emitter, not justified by a current direct ChEBI cofactor assertion
    for this exact chemical. The identity collision prevents coherent requirement
    hierarchy grounding until repaired.
  evidence_ids:
  - record
  - local-parent-1
  - owner
  - chemical
  - cofactor-role
  topic: Alignment parent and chemical-role provenance
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The xref denotes a chemical entity while the local class denotes a protein
    functional requirement. Even after the identity collision is repaired, those different
    entity types cannot be asserted equal; this semantic defect has a separate dependent
    repair.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-28343.f420-macrolide-identity-collision
  category: identity
  severity: blocker
  title: F420 label is paired with 3-O-alpha-mycarosylerythronolide B
  description: The defining label and alignment aliases identify F420, while the exact
    CHEBI identifier resolves to 3-O-alpha-mycarosylerythronolide B. Names, formula
    and structure provide positive incompatible identities. Resolving the local target
    path is possible, but it does not validate this association.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - alignment-crosswalk
  - f420-comparison
  - context-15823
  certainty: confirmed
  field_paths:
  - identifier
  - label
  - definition
  - definition_source
  - synonyms
  - xrefs
  normalization_reason: The defining chemical identity is incompatible across label
    and grounding, a blocker despite the exact local target remaining identifiable
    and reviewable. The action must resolve this identity first.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: blocker
- issue_key: chebi.cofactor-requirement.CHEBI-28343.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The source chemical in xrefs and the local requirement class have different
    denotations. Source roles, alignment metadata and bounded biological activity
    do not satisfy true own-source equivalence. This is distinct from the wrong-identity
    blocker and its repair depends on resolving that blocker first.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Resolving the positive identity collision is prerequisite
    to this distinct major chemical-versus-protein-class grounding repair.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
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
  description: Audit and correct the maintained alignment input or registered override
    and build_aligned identity checks before regeneration. Adjudicate the intended
    chemical scope, including generic versus exact F420 chain length, stereochemistry,
    charge and redox state, and reconcile the existing identifier/path lifecycle and
    collisions through an audited route. Do not relabel the currently identified chemical,
    automatically select a comparison entry, transfer its biological evidence, or
    move the wrong ID into chemical_participants. Remove the copied broad category
    token from alternate-label output while preserving its provenance. The original
    upstream table must be inspected through an authorized source route before claiming
    it is fixed.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - Positive chemical identity agrees across the regenerated label, identifier, definition
    and scientific aliases. The selected scope is explicitly adjudicated; a participant
    rewrite cannot hide the wrong identity.
  - A focused alignment fixture rejects incompatible identifiers/names and grouping
    tokens. Existing targets are explicitly selected and reconciled; main selects
    missing IDs before --force, so force alone is not an existing-record repair. No
    implicit identity reassignment or protein/status promotion occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml.
    Run full just validate-all before merging record changes; capture changed inputs
    and save a fresh validated review rather than overwriting this observation.
- action_id: A2
  description: After the identity collision is resolved and the intended chemical
    scope is explicitly adjudicated, update build_aligned and its maintained input/override.
    Do not preserve the current wrong chemical ID as a participant for the labelled
    trait. Remove chemical-to-protein-trait equality and preserve supported chemical
    grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role
    and exact state before adding a typed participant; a source role or alignment
    label is not independent protein qualification. If the evidence cannot support
    the required participant role, retain provenance and explicit uncertainty without
    inventing a participant. Do not move the equality to mapped_xrefs, merge chemical
    states or automatically qualify proteins.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28343
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - The chemical association no longer asserts equality to the protein requirement.
    Exact identity and candidate provenance remain auditable; any participant has
    a curator-adjudicated activity-relative role or uncertainty remains explicit.
  - Use an audited route selecting the existing target and a focused source-transform
    fixture. The alignment main missing-only selection is not bypassed by --force
    alone. No native status, protein example or obligatory physiological requirement
    is promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml.
    Run full just validate-all before merging record changes; capture changed inputs
    and save a fresh validated review rather than overwriting this observation.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The alignment-selected requirement comes from locally persisted MGA name/category
  metadata, not a demonstrated direct ChEBI cofactor-role selection. The original
  sibling reference table, its upstream provenance and release were not accessed or
  independently verified. The captured crosswalk is output provenance, not independent
  physiology or the emitter input.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The F420 comparison is deliberately one exact neutral gamma-linked two-glutamyl
  chemical. Generic F420 scope, other chain lengths, stereochemistry, charge and redox
  states are not automatically interchangeable. The primary biosynthesis paper was
  inspected through its complete indexed abstract only; its older biosynthetic account
  is not used to certify every current biosynthetic pathway. The macrolide may have
  other biological roles, which neither repair nor excuse the F420 identity conflict.
tags:
- unreviewed-path-order
- batch-020
- chebi-cofactor
```
