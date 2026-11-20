# Review of requires Eu

- Review: 20261021T114711Z-eu-chebi33375
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:35:32Z
- Finished UTC: 2026-10-21T11:47:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The Eu/europium-labelled requirement points to gadolinium atom, a confirmed identity blocker. A separate confirmed major chemical-to-protein-trait equivalence defect requires identity repair first. Positive Eu(III)-enzyme evidence is retained without transferring it to Gd or automatically selecting a replacement state.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 020. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87) covers 188 record paths, leaving 429171 before this batch. 20 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml | generated | requires Eu |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33375 | Official ChEBI and OLS resolve the exact source identifier but contradict the local Eu/europium identity. Ownership, crosswalk and source/licence inspection are established; the alignment is not validated. External comparisons and primary context do not automatically select a replacement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

scripts/seed_cofactor_alignment.py owns this aligned requirement, with the captured ChEBI helper dependency and crosswalk provenance. No emitted record has been edited.

### Protein trait class completeness

completeness: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The YAML is shaped as a reusable requirement class rather than a protein instance, but its intended chemical identity is not coherent across label and identifier. Optional representations are not required to diagnose this positive identity conflict; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Europium label versus gadolinium identifier

identity: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The local Eu/europium label and CHEBI:33375 refer to different elements. Official Gd names, formula, charge and structure positively resolve the collision; it is not a protonation variant or absent-source inference. The comparison Eu atom and Eu(II)/Eu(III) entries show why choosing the intended state still needs adjudication.

### Positive europium-ion enzyme context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The primary studies support active Eu(III)-containing methanol dehydrogenase in the specified SolV preparations and physiological-electron-transfer experiment. This positive context concerns europium ions, not neutral Gd CHEBI:33375, and does not establish a replacement identifier or universal enzyme dependence.

### Intended europium chemical state and requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

There is no coherent source-grounded identity for the current Eu-labelled/Gd-identified trait. A curator must resolve the intended element and atomic/ionic scope before deciding a participant or qualifying protein evidence. The true Eu-ion examples cannot be transferred onto the wrong Gd chemical.

### Maintained alignment provenance and source resolution

provenance: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The alignment emitter and exact crosswalk row explain the local source attribution, but they preserve a positively wrong chemical association; current official resolution does not validate the alignment. The ChEBI helper supplies chemistry/licensing, while the original MGA table and release remain uninspected.

### Alignment parent and chemical-role provenance

consistency: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The captured local cofactor parent resolves structurally. It was attached by the alignment emitter, not justified by a current direct ChEBI cofactor assertion for this exact chemical. The identity collision prevents coherent requirement hierarchy grounding until repaired.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33375.

The xref denotes a chemical entity while the local class denotes a protein functional requirement. Even after the identity collision is repaired, those different entity types cannot be asserted equal; this semantic defect has a separate dependent repair.

## Findings

### F1: Eu/europium label is paired with gadolinium atom

blocker / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-33375.eu-gadolinium-identity-collision.

The defining label and alignment aliases identify Eu/europium, while the exact CHEBI identifier resolves to gadolinium atom. Names, formula and structure provide positive incompatible identities. Resolving the local target path is possible, but it does not validate this association.

### F2: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-33375.chemical-entity-equivalence.

The source chemical in xrefs and the local requirement class have different denotations. Source roles, alignment metadata and bounded biological activity do not satisfy true own-source equivalence. This is distinct from the wrong-identity blocker and its repair depends on resolving that blocker first.

## Recommended Actions And Acceptance Checks

### A1

Audit and correct the maintained alignment input or registered override and build_aligned identity checks before regeneration. Adjudicate the intended chemical scope, including the element and atomic/ionic charge state, and reconcile the existing identifier/path lifecycle and collisions through an audited route. Do not relabel the currently identified chemical, automatically select a comparison entry, transfer its biological evidence, or move the wrong ID into chemical_participants. Remove the copied broad category token from alternate-label output while preserving its provenance. The original upstream table must be inspected through an authorized source route before claiming it is fixed.

- Positive chemical identity agrees across the regenerated label, identifier, definition and scientific aliases. The selected scope is explicitly adjudicated; a participant rewrite cannot hide the wrong identity.
- A focused alignment fixture rejects incompatible identifiers/names and grouping tokens. Existing targets are explicitly selected and reconciled; main selects missing IDs before --force, so force alone is not an existing-record repair. No implicit identity reassignment or protein/status promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

### A2

After the identity collision is resolved and the intended chemical scope is explicitly adjudicated, update build_aligned and its maintained input/override. Do not preserve the current wrong chemical ID as a participant for the labelled trait. Remove chemical-to-protein-trait equality and preserve supported chemical grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role and exact state before adding a typed participant; a source role or alignment label is not independent protein qualification. If the evidence cannot support the required participant role, retain provenance and explicit uncertainty without inventing a participant. Do not move the equality to mapped_xrefs, merge chemical states or automatically qualify proteins.

- The chemical association no longer asserts equality to the protein requirement. Exact identity and candidate provenance remain auditable; any participant has a curator-adjudicated activity-relative role or uncertainty remains explicit.
- Use an audited route selecting the existing target and a focused source-transform fixture. The alignment main missing-only selection is not bypassed by --force alone. No native status, protein example or obligatory physiological requirement is promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml; Entire target YAML | supports | Complete target YAML inspected: local identifier, requires-label, synthesized alignment definition, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, ChEBI chemical xref and CC-BY 4.0 statement, broad cofactor parent and MGA-attributed RELATED_SYNONYM values europium and metals. No optional example, graph, qualified protein assertion or chemical_participants is present. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main | supports | load_mg_cofactors reads sibling reference-table metadata; build_aligned synthesizes the protein requirement, attaches the broad cofactor parent, emits the chemical xref, and copies cofactor_id/category as RELATED_SYNONYM. main selects only missing chemical IDs before considering force, so an existing-record repair requires an audited scoped route. This local review does not access the sibling checkout. |
| chebi-dependency | scripts/seed_chebi_cofactor.py; load_names, rid, clean, LICENSE and imported helpers | supports | The alignment emitter imports ChEBI chemical-name/definition loading, identifiers, formatting, output location and ChEBI licensing from this module. This dependency does not itself establish a role for an alignment-selected chemical. |
| alignment-crosswalk | data/mappings/cofactor_crosswalk.tsv; Exact target CHEBI identifier row and header | supports | The exact chemical-ID row records the locally persisted alignment name, cofactor identifier and category. It is curation provenance, not an independently verified protein requirement or a release-pinned external source table. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The inspected ChEBI chemical-scope and Licensing sections state CC BY 4.0. This supports ChEBI attribution, not chemical-to-protein-trait equality. It does not certify the uninspected upstream MGA table. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16. Its original access time and digest are retained; this does not assign a release to the original seed or live backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33375/; Complete identifier, names, definition or null, formula/charge, structure, origins, role classification and outgoing relations | supports | CHEBI:33375 is gadolinium atom: formula Gd, charge 0, SMILES [Gd], InChI=1S/Gd and gadolinium/Gd names. It is not europium. Its prose definition and role classification are null, and its outgoing relations are lanthanoid atom and f-block element atom. The official identifier resolves positively to a different element than the local Eu/europium label. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:33375; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier and source identity. The actual prose definition is empty; it is not replaced by the local alignment label. Resolution of the chemical identifier is distinct from validation of the protein-trait assertion. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, under biochemical role CHEBI:52206. It is not itself a chemical molecule or an equivalent protein-requirement class. |
| context-33319 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33319/; Inspected source response captured at the recorded UTC time | supports | Lanthanoid atom is the current structural parent class. Its prose definition and fixed chemical data are null; the outgoing structural relation is inspected. This parent supplies no direct cofactor-role assertion. |
| context-33562 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33562/; Inspected source response captured at the recorded UTC time | supports | F-block element atom is the current structural parent class. Its prose definition and fixed chemical data are null; the outgoing structural relation is inspected. This parent supplies no direct cofactor-role assertion. |
| lanthanide-assay | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6085770/fullTextXML; Successful full-text XML: kinetic series, Fig. 3, Methods kinetic experiments and Conclusions; separate model discussion inspected as model context | supports | PMID:30020281; DOI:10.1039/c8dt01238e. The primary kinetic series added 20 micromolar Ln(III) chlorides, including ErCl3, to 200 nM partly apo Eu-MDH (approximately 70% Eu-loaded) at pH 7.2 and 45 °C. Later lanthanides decreased activity relative to no added ion under these conditions. This is a mixed-enzyme addition assay, not purified Er-MDH, a neutral-atom experiment or universal evidence that a later lanthanide cannot be a cofactor. Metal exchange is suggested rather than measured for every derivative; computational results are not promoted to experimental qualification. |
| context-32999 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/32999/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | CHEBI:32999 resolves to neutral europium atom, formula Eu, charge 0 and SMILES [Eu]. Its prose definition is null. It is a positive comparison distinct from Gd CHEBI:33375, not an automatically selected repair target for a requirement that may concern an ion. |
| context-49591 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/49591/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | CHEBI:49591 is europium(3+), formula Eu, charge +3 and SMILES [Eu+3], distinct from neutral europium and gadolinium. Its prose definition is null; the inspected structural relations do not assert an obligatory protein role. |
| context-49588 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/49588/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | CHEBI:49588 is europium(2+), formula Eu, charge +2 and SMILES [Eu+2]. It is chemically distinct from Eu(III) and neutral Eu; existence of this entry does not establish a role in the inspected enzyme. |
| primary-29524328 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A29524328%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | supports | PMID:29524328; DOI:10.1002/cbic.201800130. The complete abstract reports catalytically active Eu(III)-containing methanol dehydrogenase from Methylacidiphilum fumariolicum SolV with approximately 70% Eu occupancy and lower efficiency than earlier-lanthanide derivatives. This is positive Eu-ion cofactor context, not Gd identity, neutral-atom dependence or a universal lanthanide result. |
| primary-30908783 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A30908783%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | supports | PMID:30908783; DOI:10.1002/chem.201900525. The complete abstract reports catalytic electron transfer by Eu-containing methanol dehydrogenase through physiological cytochrome cGJ, with methanol and formaldehyde activity. It is independent positive Eu(III)-enzyme context; exact neutral Eu, gadolinium and the local identifier mismatch remain separate. |
| eu-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6100108/fullTextXML; Successful full-text XML: Introduction, Results/Discussion, Conclusion and Experimental Section, including crystal and activity sections; supplementary data/coordinates not independently inspected | supports | PMID:29524328; DOI:10.1002/cbic.201800130. The inspected primary article reports SolV growth with EuCl3, Eu-containing MDH, approximately 70% Eu occupancy by ICP-MS and catalytic activity. Eu(III) coordination and activity are positive ion-specific context. The 1.4 Å structure was refined without a substrate because the density did not securely identify methanol. Cross-lanthanide kinetic comparisons, incomplete occupancy and proposed redox explanations remain bounded; none repairs a gadolinium identifier. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml; Executed 2026-10-21T11:36:42Z through 2026-10-21T11:36:44Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-chebi73115.yaml data/traits/function/cofactor_requirement/chebi/dy-chebi33373.yaml data/traits/function/cofactor_requirement/chebi/echinenone-chebi4746.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-1-chebi77805.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-6-chebi38150.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml data/traits/function/cofactor_requirement/chebi/er-chebi33379.yaml data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml data/traits/function/cofactor_requirement/chebi/fad-3-chebi57692.yaml; Executed 2026-10-21T11:36:19Z through 2026-10-21T11:38:17Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml; Executed 2026-10-21T11:36:44Z through 2026-10-21T11:36:44Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:38:17Z through 2026-10-21T11:38:18Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The alignment-selected requirement comes from locally persisted MGA name/category metadata, not a demonstrated direct ChEBI cofactor-role selection. The original sibling reference table, its upstream provenance and release were not accessed or independently verified. The captured crosswalk is output provenance, not independent physiology or the emitter input.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The lanthanide experiments use salts and a particular Eu-MDH preparation, not neutral atoms. Mixed occupancy, metal-addition conditions and computational mechanisms cannot establish all native protein requirements. No absence of all possible erbium or gadolinium roles is claimed. The original MGA table remains uninspected.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T114711Z-eu-chebi33375
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires Eu
started_at: '2026-10-21T11:35:32Z'
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
summary: The Eu/europium-labelled requirement points to gadolinium atom, a confirmed
  identity blocker. A separate confirmed major chemical-to-protein-trait equivalence
  defect requires identity repair first. Positive Eu(III)-enzyme evidence is retained
  without transferring it to Gd or automatically selecting a replacement state.
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
  - path: data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
    sha256: be74e78718d97094c721ceb7981e6cff502364b1affd51dcdbf88825b0d031a9
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
  selection: Path-order position 8 in batch 020. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
targets:
- kind: generated
  label: requires Eu
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_33375
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve the exact source identifier but contradict
    the local Eu/europium identity. Ownership, crosswalk and source/licence inspection
    are established; the alignment is not validated. External comparisons and primary
    context do not automatically select a replacement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-33319
  - context-33562
  - context-32999
  - context-49591
  - context-49588
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:35:32Z'
  snapshot_sha256: be74e78718d97094c721ceb7981e6cff502364b1affd51dcdbf88825b0d031a9
  support: supports
  summary: 'Complete target YAML inspected: local identifier, requires-label, synthesized
    alignment definition, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED, ChEBI
    chemical xref and CC-BY 4.0 statement, broad cofactor parent and MGA-attributed
    RELATED_SYNONYM values europium and metals. No optional example, graph, qualified
    protein assertion or chemical_participants is present.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T11:35:32Z'
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
  accessed_at: '2026-10-21T11:35:32Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main
  accessed_at: '2026-10-21T11:35:32Z'
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
  accessed_at: '2026-10-21T11:35:32Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The alignment emitter imports ChEBI chemical-name/definition loading, identifiers,
    formatting, output location and ChEBI licensing from this module. This dependency
    does not itself establish a role for an alignment-selected chemical.
- evidence_id: alignment-crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Exact target CHEBI identifier row and header
  accessed_at: '2026-10-21T11:35:32Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The exact chemical-ID row records the locally persisted alignment name,
    cofactor identifier and category. It is curation provenance, not an independently
    verified protein requirement or a release-pinned external source table.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:35:32Z'
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33375/
  accessed_at: '2026-10-21T11:36:40.121240Z'
  snapshot_sha256: cda118c0cde9a94158167a71960f5046553a4f0fc34896d7975a753a43850d36
  support: supports
  locator: Complete identifier, names, definition or null, formula/charge, structure,
    origins, role classification and outgoing relations
  summary: 'CHEBI:33375 is gadolinium atom: formula Gd, charge 0, SMILES [Gd], InChI=1S/Gd
    and gadolinium/Gd names. It is not europium. Its prose definition and role classification
    are null, and its outgoing relations are lanthanoid atom and f-block element atom.
    The official identifier resolves positively to a different element than the local
    Eu/europium label.'
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:33375
  accessed_at: '2026-10-21T11:36:39.481561Z'
  snapshot_sha256: 19f69b5b830af72877282d41e684937e9f3669a81c4b12f5eebe9998064b16ee
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
- evidence_id: context-33319
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33319/
  accessed_at: '2026-10-21T11:37:39.300777Z'
  snapshot_sha256: dcdb76e4b6843482b687febb7c9b9d39d86bbe25ac53a40a744c9f433467332d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Lanthanoid atom is the current structural parent class. Its prose definition
    and fixed chemical data are null; the outgoing structural relation is inspected.
    This parent supplies no direct cofactor-role assertion.
- evidence_id: context-33562
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33562/
  accessed_at: '2026-10-21T11:37:39.306962Z'
  snapshot_sha256: 5e91d035a028a4b18c486bfdebfa98fea090498a216b40b8a33ab956967d7679
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: F-block element atom is the current structural parent class. Its prose
    definition and fixed chemical data are null; the outgoing structural relation
    is inspected. This parent supplies no direct cofactor-role assertion.
- evidence_id: lanthanide-assay
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6085770/fullTextXML
  accessed_at: '2026-10-21T11:37:46.579717Z'
  snapshot_sha256: 8c91c7a1644d6e75b94acc379485ef57487b04a3f7e48080cf987d89778980e0
  support: supports
  locator: 'Successful full-text XML: kinetic series, Fig. 3, Methods kinetic experiments
    and Conclusions; separate model discussion inspected as model context'
  summary: PMID:30020281; DOI:10.1039/c8dt01238e. The primary kinetic series added
    20 micromolar Ln(III) chlorides, including ErCl3, to 200 nM partly apo Eu-MDH
    (approximately 70% Eu-loaded) at pH 7.2 and 45 °C. Later lanthanides decreased
    activity relative to no added ion under these conditions. This is a mixed-enzyme
    addition assay, not purified Er-MDH, a neutral-atom experiment or universal evidence
    that a later lanthanide cannot be a cofactor. Metal exchange is suggested rather
    than measured for every derivative; computational results are not promoted to
    experimental qualification.
- evidence_id: context-32999
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/32999/
  accessed_at: '2026-10-21T11:37:44.208678Z'
  snapshot_sha256: 155affa69ec4fff3f7c0906873a44cf0d26889f23aeab41cae451a304657f13a
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: CHEBI:32999 resolves to neutral europium atom, formula Eu, charge 0 and
    SMILES [Eu]. Its prose definition is null. It is a positive comparison distinct
    from Gd CHEBI:33375, not an automatically selected repair target for a requirement
    that may concern an ion.
- evidence_id: context-49591
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/49591/
  accessed_at: '2026-10-21T11:38:19.853555Z'
  snapshot_sha256: f3e98479893fd99fb25ec99c0480053dd3621656ba6e3aa74d7456ab9031949a
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: CHEBI:49591 is europium(3+), formula Eu, charge +3 and SMILES [Eu+3], distinct
    from neutral europium and gadolinium. Its prose definition is null; the inspected
    structural relations do not assert an obligatory protein role.
- evidence_id: context-49588
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/49588/
  accessed_at: '2026-10-21T11:38:19.853969Z'
  snapshot_sha256: 6492ebfb1871cadb208487d8f1d2efe8fa8b156cf082d20a0c5d0a7f8816f47c
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: CHEBI:49588 is europium(2+), formula Eu, charge +2 and SMILES [Eu+2]. It
    is chemically distinct from Eu(III) and neutral Eu; existence of this entry does
    not establish a role in the inspected enzyme.
- evidence_id: primary-29524328
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A29524328%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:37:46.226667Z'
  snapshot_sha256: 75c79da5a07bc9578c14fa15d18aaee553c87df5236581b190a771d7ecca6a20
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:29524328; DOI:10.1002/cbic.201800130. The complete abstract reports
    catalytically active Eu(III)-containing methanol dehydrogenase from Methylacidiphilum
    fumariolicum SolV with approximately 70% Eu occupancy and lower efficiency than
    earlier-lanthanide derivatives. This is positive Eu-ion cofactor context, not
    Gd identity, neutral-atom dependence or a universal lanthanide result.
- evidence_id: primary-30908783
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A30908783%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:37:46.227555Z'
  snapshot_sha256: 2fb52b105f4af4fe48070acbef612b439f3b1d5141fb22acc182d152d973d576
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:30908783; DOI:10.1002/chem.201900525. The complete abstract reports
    catalytic electron transfer by Eu-containing methanol dehydrogenase through physiological
    cytochrome cGJ, with methanol and formaldehyde activity. It is independent positive
    Eu(III)-enzyme context; exact neutral Eu, gadolinium and the local identifier
    mismatch remain separate.
- evidence_id: eu-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6100108/fullTextXML
  accessed_at: '2026-10-21T11:37:46.474318Z'
  snapshot_sha256: 3188f430c31671921c0cbdc06e51141208bb923563ffa8d27ddde0427fa3c297
  support: supports
  locator: 'Successful full-text XML: Introduction, Results/Discussion, Conclusion
    and Experimental Section, including crystal and activity sections; supplementary
    data/coordinates not independently inspected'
  summary: PMID:29524328; DOI:10.1002/cbic.201800130. The inspected primary article
    reports SolV growth with EuCl3, Eu-containing MDH, approximately 70% Eu occupancy
    by ICP-MS and catalytic activity. Eu(III) coordination and activity are positive
    ion-specific context. The 1.4 Å structure was refined without a substrate because
    the density did not securely identify methanol. Cross-lanthanide kinetic comparisons,
    incomplete occupancy and proposed redox explanations remain bounded; none repairs
    a gadolinium identifier.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  locator: Executed 2026-10-21T11:36:42Z through 2026-10-21T11:36:44Z; exit 0
  accessed_at: '2026-10-21T11:36:44Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
  locator: Executed 2026-10-21T11:36:44Z through 2026-10-21T11:36:44Z; exit 0
  accessed_at: '2026-10-21T11:36:44Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: concern
  summary: The local Eu/europium label and CHEBI:33375 refer to different elements.
    Official Gd names, formula, charge and structure positively resolve the collision;
    it is not a protonation variant or absent-source inference. The comparison Eu
    atom and Eu(II)/Eu(III) entries show why choosing the intended state still needs
    adjudication.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-32999
  - context-49591
  - context-49588
  - alignment-crosswalk
  topic: Europium label versus gadolinium identifier
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The primary studies support active Eu(III)-containing methanol dehydrogenase
    in the specified SolV preparations and physiological-electron-transfer experiment.
    This positive context concerns europium ions, not neutral Gd CHEBI:33375, and
    does not establish a replacement identifier or universal enzyme dependence.
  evidence_ids:
  - primary-29524328
  - primary-30908783
  - eu-fulltext
  - context-49591
  topic: Positive europium-ion enzyme context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: There is no coherent source-grounded identity for the current Eu-labelled/Gd-identified
    trait. A curator must resolve the intended element and atomic/ionic scope before
    deciding a participant or qualifying protein evidence. The true Eu-ion examples
    cannot be transferred onto the wrong Gd chemical.
  evidence_ids:
  - record
  - schema
  - chemical
  - context-32999
  - context-49591
  - eu-fulltext
  topic: Intended europium chemical state and requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-33375.eu-gadolinium-identity-collision
  category: identity
  severity: blocker
  title: Eu/europium label is paired with gadolinium atom
  description: The defining label and alignment aliases identify Eu/europium, while
    the exact CHEBI identifier resolves to gadolinium atom. Names, formula and structure
    provide positive incompatible identities. Resolving the local target path is possible,
    but it does not validate this association.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - alignment-crosswalk
  - context-32999
  - context-49591
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: blocker
- issue_key: chebi.cofactor-requirement.CHEBI-33375.chemical-entity-equivalence
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
    chemical scope, including the element and atomic/ionic charge state, and reconcile
    the existing identifier/path lifecycle and collisions through an audited route.
    Do not relabel the currently identified chemical, automatically select a comparison
    entry, transfer its biological evidence, or move the wrong ID into chemical_participants.
    Remove the copied broad category token from alternate-label output while preserving
    its provenance. The original upstream table must be inspected through an authorized
    source route before claiming it is fixed.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33375
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
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml.
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
- The lanthanide experiments use salts and a particular Eu-MDH preparation, not neutral
  atoms. Mixed occupancy, metal-addition conditions and computational mechanisms cannot
  establish all native protein requirements. No absence of all possible erbium or
  gadolinium roles is claimed. The original MGA table remains uninspected.
tags:
- unreviewed-path-order
- batch-020
- chebi-cofactor
```
