# Review of requires divinyl chlorophyll a(1−)

- Review: 20261021T112935Z-divinyl-chlorophyll-a-1-chebi73095
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:22:01Z
- Finished UTC: 2026-10-21T11:29:35Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The source divinyl chlorophyll a anion has a supported Mg-containing phytyl-ester structure and peripheral carbon deprotonation. One confirmed major finding concerns chemical-to-protein-trait equivalence. Pigment function and substrate conversion do not establish the exact anion requirement.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 019. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c) covers 178 record paths, leaving 429181 before this batch. 19 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml | generated | requires divinyl chlorophyll a(1−) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_73095 | Official ChEBI/OLS resolve CHEBI:73095 and its exact chemical/source-role context. The captured local cofactor parent, inspected external comparisons and bounded primary/authority sources are recorded separately from protein-trait equivalence and native protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Divinyl chlorophyll anion connectivity and phorbine numbering

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The source formula and paired neutral structure support loss of one peripheral beta-keto-ester carbon proton, identified as position 21 in the source phorbine name. This is distinct from conventional tetrapyrrole nitrogen numbering. Mg, both vinyl groups and the phytyl/methyl esters remain. Source (3S,4S) ring and (2E,7R,11R) phytyl stereochemistry remain specified while the deprotonated carbon no longer has the neutral 21R descriptor. The formal [Mg-2] SMILES notation is coordinate-bond bookkeeping, not a claim that magnesium has oxidation state −II.

### Pigment occurrence and reductase-substrate context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The source-cited rice study reports divinyl a/b accumulation and conversion of divinyl chlorophyll(ide) a by OsDVR. It does not directly test the exact source anion or establish b-anion reductase activity. Substrate conversion does not disprove other pigment/cofactor roles.

### Divinyl a pigment in photochemically active PSII

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The inspected Synechocystis study positively supports photochemical activity of isolated complexes containing divinyl chlorophyll a. Its pigment identity and singlet-oxygen comparison do not measure the C21-deprotonated state or establish a universal free-anion protein requirement.

### Exact anion activity-relative protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The exact anion is source-defined, while the inspected biological studies address pigment preparations or biosynthetic conversion. They do not independently qualify this exact protonation state as a non-substrate protein requirement. No pH-major-species assertion is added, no absence of a possible role is inferred, and neutral, anionic and Mg-free pigments are not merged.

### Chemical source and maintained requirement synthesis

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The exact chemical identifier, current source text or explicit null definition, direct role assertions and CC BY 4.0 licence resolve. The protein-requirement wrapper is generated by the maintained ChEBI seeder; current comparison snapshots do not identify its original seed release.

### Source cofactor role versus local broader requirement

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The captured cofactor-requirement parent resolves. Current source direct cofactor role explains the selection. Role taxonomy supplies candidate context but is not equality between a chemical and a protein trait, and this review does not certify the parent.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_73095.

The xref denotes a chemical entity while the local class denotes a protein functional requirement. Correct chemical identity and biological activity evidence do not make those different entity types equivalent.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-73095.chemical-entity-equivalence.

The source chemical entity in xrefs and the local protein functional requirement have different denotations. Authentic cofactor roles and bounded biological support do not satisfy true own-source equivalence.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-trait equivalence and preserve CHEBI:73095 through supported chemical grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role and exact chemical state before adding a typed participant; preserve protein attachment, charge, metal and stereochemical distinctions where relevant. If the evidence cannot support the required role, retain chemical provenance and explicit uncertainty without inventing a participant. Do not move the same equality to mapped_xrefs, merge conjugates or automatically qualify proteins.

- Exact source identity and state remain auditable without asserting chemical/protein-class equality. Any participant has a curator-adjudicated activity-relative role; otherwise provenance and uncertainty are retained.
- Use an audited route selecting the existing target and a focused source-transform fixture. Preserve the supported bound-cofactor or pigment context without equating free states, covalent adducts, biosynthetic substrates or oxidation products. No status or protein-example promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml. Run full just validate-all before merging record changes; inspect changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The inspected official ChEBI chemical-scope and Licensing sections support chemical entities/roles and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports comparison ontology version 256, loaded 2026-10-16. Original access time and digest are retained; this does not assign a release to the original seed or live chemical backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/73095/; Complete identifier/name/definition, aliases, formula/charge, structure, origins and incoming/outgoing relations | supports | CHEBI:73095 denotes divinyl chlorophyll a(1−), C55H69MgN4O5, with Mg retained, two vinyl groups, a methyl ester and the stereospecified phytyl ester. Relative to neutral CHEBI:73113, the source SMILES replaces the peripheral [C@@H](C(=O)OC) beside the ketone with [C-](C(=O)OC); the source phorbine IUPAC name omits the neutral 21R stereodescriptor. Thus its 21-position wording refers here to this carbon in phorbine numbering, not a central pyrrole nitrogen. Direct role is cofactor and its source citation is PMID:20484022. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:73095; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier, with the actual definition, names/synonym scopes and chemical annotations inspected. Chemical resolution is not equivalent protein-trait grounding. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity. Its parent is biochemical role CHEBI:52206. This role is not a protein-requirement class. |
| context-73113 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/73113/; Complete chemical identity, definition, names, structure and outgoing relations | supports | CHEBI:73113 denotes fixed neutral Mg-containing divinyl chlorophyll a, C55H70MgN4O5, with two vinyl groups, methyl and phytyl esters, and source stereochemistry (3S,4S,21R) plus (2E,7R,11R) phytol. Its definition circularly names divinyl chlorophyll a itself as the acid precursor, but its functional-parent relation identifies divinyl chlorophyllide a CHEBI:38259. Direct role is cofactor; conjugate base is CHEBI:73095. |
| context-58941 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58941/; Complete chemical identity, definition, names, structure and outgoing relations | supports | Cyclic tetrapyrrole anion is defined as an organic anion arising from deprotonation of a cyclic tetrapyrrole compound. It does not alone specify the deprotonation site or a protein role. |
| primary-20484022 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20484022%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI; complete indexed abstract; full article not inspected | supports | PMID:20484022. Divinyl chlorophyll(ide) a can be converted to monovinyl chlorophyll(ide) a by a divinyl reductase in rice; DOI:10.1104/pp.110.158477. The complete abstract reports mutant rice accumulation of divinyl chlorophyll a and b and recombinant OsDVR conversion of divinyl chlorophyll(ide) a. It is pigment occurrence and substrate-conversion evidence, not a measurement of the exact C21-deprotonated a or b species or its non-substrate requirement. |
| primary-22387397 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A22387397%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI; complete indexed abstract; full article not inspected | supports | PMID:22387397. Luminescence of singlet oxygen in photosystem II complexes isolated from Synechocystis sp. PCC6803 containing monovinyl or divinyl chlorophyll a; DOI:10.1016/j.bbabio.2012.02.018. The complete abstract describes photochemically active isolated PSII complexes and greater singlet-oxygen yield from the modified divinyl-pigment preparation. This positively supports the reported pigment-complex function, not a universal protein requirement or determination of exact C21 protonation. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml; Executed 2026-10-21T11:22:30Z through 2026-10-21T11:22:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml; Executed 2026-10-21T11:22:22Z through 2026-10-21T11:23:43Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml; Executed 2026-10-21T11:22:31Z through 2026-10-21T11:22:31Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:23:43Z through 2026-10-21T11:23:44Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- Primary literature was inspected through complete indexed abstracts. Exact anion abundance, protein-bound protonation, pigment orientation and residue coordinates remain unqualified. The source uses phorbine numbering; no central-nitrogen deprotonation or metal-reduction claim is made. Neutral chemical comparisons are external sources, not uncaptured local sibling assessments.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T112935Z-divinyl-chlorophyll-a-1-chebi73095
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires divinyl chlorophyll a(1−)
started_at: '2026-10-21T11:22:01Z'
finished_at: '2026-10-21T11:29:35Z'
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
summary: The source divinyl chlorophyll a anion has a supported Mg-containing phytyl-ester
  structure and peripheral carbon deprotonation. One confirmed major finding concerns
  chemical-to-protein-trait equivalence. Pigment function and substrate conversion
  do not establish the exact anion requirement.
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
  - path: data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    sha256: 6acee17842872abb07b9e0d92a394af90d4710e3a70f33be1812b0767b686ca5
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
  selection: Path-order position 8 in batch 019. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c) covers 178 record paths,
    leaving 429181 before this batch. 19 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
targets:
- kind: generated
  label: requires divinyl chlorophyll a(1−)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_73095
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:73095 and its exact chemical/source-role
    context. The captured local cofactor parent, inspected external comparisons and
    bounded primary/authority sources are recorded separately from protein-trait equivalence
    and native protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-73113
  - context-58941
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:22:01Z'
  snapshot_sha256: 6acee17842872abb07b9e0d92a394af90d4710e3a70f33be1812b0767b686ca5
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
  accessed_at: '2026-10-21T11:22:01Z'
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
  accessed_at: '2026-10-21T11:22:01Z'
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
  accessed_at: '2026-10-21T11:22:01Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:22:01Z'
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
  summary: The inspected official ChEBI chemical-scope and Licensing sections support
    chemical entities/roles and CC BY 4.0 attribution; they do not assert chemical-to-protein-trait
    equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports comparison ontology version 256, loaded
    2026-10-16. Original access time and digest are retained; this does not assign
    a release to the original seed or live chemical backend.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/73095/
  accessed_at: '2026-10-21T11:22:45.008544Z'
  snapshot_sha256: ea92f7bceacaa11847267e7ef6f4535e543d0c40e8598a1657b8e4fbe3507cd7
  support: supports
  locator: Complete identifier/name/definition, aliases, formula/charge, structure,
    origins and incoming/outgoing relations
  summary: CHEBI:73095 denotes divinyl chlorophyll a(1−), C55H69MgN4O5, with Mg retained,
    two vinyl groups, a methyl ester and the stereospecified phytyl ester. Relative
    to neutral CHEBI:73113, the source SMILES replaces the peripheral [C@@H](C(=O)OC)
    beside the ketone with [C-](C(=O)OC); the source phorbine IUPAC name omits the
    neutral 21R stereodescriptor. Thus its 21-position wording refers here to this
    carbon in phorbine numbering, not a central pyrrole nitrogen. Direct role is cofactor
    and its source citation is PMID:20484022.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:73095
  accessed_at: '2026-10-21T11:22:44.379057Z'
  snapshot_sha256: 571cc5472000b3227ed4e7dd1d810f78ab236a9ee0f644b9f5ce73e57bffabed
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier, with the actual
    definition, names/synonym scopes and chemical annotations inspected. Chemical
    resolution is not equivalent protein-trait grounding.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity. Its parent is biochemical role CHEBI:52206. This
    role is not a protein-requirement class.
- evidence_id: context-73113
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/73113/
  accessed_at: '2026-10-21T11:22:45.015908Z'
  snapshot_sha256: a1a6f1e391dc22d340116cba597d0e9f6196b47962c28ab0c84b29f829c2ea9c
  support: supports
  locator: Complete chemical identity, definition, names, structure and outgoing relations
  summary: CHEBI:73113 denotes fixed neutral Mg-containing divinyl chlorophyll a,
    C55H70MgN4O5, with two vinyl groups, methyl and phytyl esters, and source stereochemistry
    (3S,4S,21R) plus (2E,7R,11R) phytol. Its definition circularly names divinyl chlorophyll
    a itself as the acid precursor, but its functional-parent relation identifies
    divinyl chlorophyllide a CHEBI:38259. Direct role is cofactor; conjugate base
    is CHEBI:73095.
- evidence_id: context-58941
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58941/
  accessed_at: '2026-10-21T11:23:15.323459Z'
  snapshot_sha256: babc23c3ca6c646fc0251a085862cd4f024809ccc0052f07989b863839897ec5
  support: supports
  locator: Complete chemical identity, definition, names, structure and outgoing relations
  summary: Cyclic tetrapyrrole anion is defined as an organic anion arising from deprotonation
    of a cyclic tetrapyrrole compound. It does not alone specify the deprotonation
    site or a protein role.
- evidence_id: primary-20484022
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20484022%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:23:16.475116Z'
  snapshot_sha256: 586a9aaebb31d106d7b6fb801c794f64b6d2da0171dc9acd6b88b6e491608a23
  support: supports
  locator: Verified PMID/DOI; complete indexed abstract; full article not inspected
  summary: PMID:20484022. Divinyl chlorophyll(ide) a can be converted to monovinyl
    chlorophyll(ide) a by a divinyl reductase in rice; DOI:10.1104/pp.110.158477.
    The complete abstract reports mutant rice accumulation of divinyl chlorophyll
    a and b and recombinant OsDVR conversion of divinyl chlorophyll(ide) a. It is
    pigment occurrence and substrate-conversion evidence, not a measurement of the
    exact C21-deprotonated a or b species or its non-substrate requirement.
- evidence_id: primary-22387397
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A22387397%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:23:17.703676Z'
  snapshot_sha256: fc0679cd7c2a87e03276f8317fbba1cbc8d98e2265f6b8ab62cabb2b498d3276
  support: supports
  locator: Verified PMID/DOI; complete indexed abstract; full article not inspected
  summary: PMID:22387397. Luminescence of singlet oxygen in photosystem II complexes
    isolated from Synechocystis sp. PCC6803 containing monovinyl or divinyl chlorophyll
    a; DOI:10.1016/j.bbabio.2012.02.018. The complete abstract describes photochemically
    active isolated PSII complexes and greater singlet-oxygen yield from the modified
    divinyl-pigment preparation. This positively supports the reported pigment-complex
    function, not a universal protein requirement or determination of exact C21 protonation.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  locator: Executed 2026-10-21T11:22:30Z through 2026-10-21T11:22:31Z; exit 0
  accessed_at: '2026-10-21T11:22:31Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-chebi4356.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-3-chebi84730.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-e-chebi50437.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrogenvanadate-chebi35169.yaml
    data/traits/function/cofactor_requirement/chebi/dihydrolipoamide-chebi17694.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-4-chebi60342.yaml
    data/traits/function/cofactor_requirement/chebi/dipyrromethane-cofactor-chebi42121.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-chebi73113.yaml
    data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-1-chebi73096.yaml
  locator: Executed 2026-10-21T11:22:22Z through 2026-10-21T11:23:43Z; exit 0
  accessed_at: '2026-10-21T11:23:43Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
  locator: Executed 2026-10-21T11:22:31Z through 2026-10-21T11:22:31Z; exit 0
  accessed_at: '2026-10-21T11:22:31Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:23:43Z through 2026-10-21T11:23:44Z; exit 0
  accessed_at: '2026-10-21T11:23:44Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source formula and paired neutral structure support loss of one peripheral
    beta-keto-ester carbon proton, identified as position 21 in the source phorbine
    name. This is distinct from conventional tetrapyrrole nitrogen numbering. Mg,
    both vinyl groups and the phytyl/methyl esters remain. Source (3S,4S) ring and
    (2E,7R,11R) phytyl stereochemistry remain specified while the deprotonated carbon
    no longer has the neutral 21R descriptor. The formal [Mg-2] SMILES notation is
    coordinate-bond bookkeeping, not a claim that magnesium has oxidation state −II.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-73113
  topic: Divinyl chlorophyll anion connectivity and phorbine numbering
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The source-cited rice study reports divinyl a/b accumulation and conversion
    of divinyl chlorophyll(ide) a by OsDVR. It does not directly test the exact source
    anion or establish b-anion reductase activity. Substrate conversion does not disprove
    other pigment/cofactor roles.
  evidence_ids:
  - primary-20484022
  - chemical
  topic: Pigment occurrence and reductase-substrate context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The inspected Synechocystis study positively supports photochemical activity
    of isolated complexes containing divinyl chlorophyll a. Its pigment identity and
    singlet-oxygen comparison do not measure the C21-deprotonated state or establish
    a universal free-anion protein requirement.
  evidence_ids:
  - primary-22387397
  - chemical
  - context-73113
  topic: Divinyl a pigment in photochemically active PSII
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The exact anion is source-defined, while the inspected biological studies
    address pigment preparations or biosynthetic conversion. They do not independently
    qualify this exact protonation state as a non-substrate protein requirement. No
    pH-major-species assertion is added, no absence of a possible role is inferred,
    and neutral, anionic and Mg-free pigments are not merged.
  evidence_ids:
  - record
  - schema
  - chemical
  - primary-20484022
  - context-73113
  topic: Exact anion activity-relative protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The exact chemical identifier, current source text or explicit null definition,
    direct role assertions and CC BY 4.0 licence resolve. The protein-requirement
    wrapper is generated by the maintained ChEBI seeder; current comparison snapshots
    do not identify its original seed release.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  topic: Chemical source and maintained requirement synthesis
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-9
- area: consistency
  outcome: supported
  summary: The captured cofactor-requirement parent resolves. Current source direct
    cofactor role explains the selection. Role taxonomy supplies candidate context
    but is not equality between a chemical and a protein trait, and this review does
    not certify the parent.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - owner
  topic: Source cofactor role versus local broader requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The xref denotes a chemical entity while the local class denotes a protein
    functional requirement. Correct chemical identity and biological activity evidence
    do not make those different entity types equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-73095.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The source chemical entity in xrefs and the local protein functional
    requirement have different denotations. Authentic cofactor roles and bounded biological
    support do not satisfy true own-source equivalence.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The candidate requirement is recognizable, but chemical and
    protein-requirement denotations differ; the class-equivalence assertion is a major
    grounding defect.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-trait
    equivalence and preserve CHEBI:73095 through supported chemical grounding/provenance.
    Adjudicate the activity-relative ChemicalParticipant.role and exact chemical state
    before adding a typed participant; preserve protein attachment, charge, metal
    and stereochemical distinctions where relevant. If the evidence cannot support
    the required role, retain chemical provenance and explicit uncertainty without
    inventing a participant. Do not move the same equality to mapped_xrefs, merge
    conjugates or automatically qualify proteins.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_73095
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Exact source identity and state remain auditable without asserting chemical/protein-class
    equality. Any participant has a curator-adjudicated activity-relative role; otherwise
    provenance and uncertainty are retained.
  - Use an audited route selecting the existing target and a focused source-transform
    fixture. Preserve the supported bound-cofactor or pigment context without equating
    free states, covalent adducts, biosynthetic substrates or oxidation products.
    No status or protein-example promotion occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-a-1-chebi73095.yaml.
    Run full just validate-all before merging record changes; inspect changed inputs
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
- Primary literature was inspected through complete indexed abstracts. Exact anion
  abundance, protein-bound protonation, pigment orientation and residue coordinates
  remain unqualified. The source uses phorbine numbering; no central-nitrogen deprotonation
  or metal-reduction claim is made. Neutral chemical comparisons are external sources,
  not uncaptured local sibling assessments.
tags:
- unreviewed-path-order
- batch-019
- chebi-cofactor
```
