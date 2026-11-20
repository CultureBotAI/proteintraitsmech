# Review of requires heme d cis-diol

- Review: 20261021T123806Z-heme-d-cis-diol-chebi62811
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:31:32Z
- Finished UTC: 2026-10-21T12:38:06Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Neutral heme d cis-diol identity and cis connectivity are supported, separately from its dianion and spirolactone. One confirmed major finding concerns chemical-to-protein-trait equivalence. Positive catalase evidence is retained without transferring the bound spirolactone conclusion to this diol.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 7 in batch 023. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5) covers 218 record paths, leaving 429141 before this batch. 23 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml | generated | requires heme d cis-diol |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_62811 | Official ChEBI/OLS resolve CHEBI:62811 and the exact chemical identity. The direct cofactor role and maintained ChEBI emitter resolve. Bounded primary context is distinguished from exact-state protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Exact cis-diol chemical state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The identifier, label and copied chemistry agree with current ChEBI/OLS. The neutral diol is retained separately from its dianion and the dehydratively cyclized spirolactone. No aggregated database charge or adjacent heme state replaces the exact source identity.

### Catalase heme context and chemical specificity

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

Both source-linked complete abstracts provide positive catalase heme evidence. The later structure explicitly identifies a spirolactone, and official ChEBI represents it as a different entity with a functional-parent relation to the diol. This distinction prevents transfer of the exact bound-state conclusion to the reviewed open diol.

### Exact cis-diol protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The direct source cofactor role is retained as positive candidate context. The inspected catalase evidence does not independently establish a non-substrate requirement for this exact open-diol chemical state. This is an explicit qualification limit, not proof that no protein can use the diol and not a reason to relabel it as the spirolactone.

### Chemical source and maintained emitter

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The exact chemical identifier, copied source text where present, direct cofactor role and ChEBI licence resolve. The requires-label and protein-requirement assertion are synthesized by scripts/seed_chebi_cofactor.py. Current snapshots do not establish the original seed release.

### Source role and local broader requirement

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The direct source cofactor role explains candidate selection and the local broader requirement parent. Chemical structural ancestry remains distinct from protein-trait hierarchy, and parent resolution does not certify the parent's own equivalence semantics.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_62811.

The chemical xref and the synthesized protein-requirement class have different denotations. Exact chemical identity, a source role or bounded positive biology does not satisfy true own-source equivalence between them.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-62811.chemical-entity-equivalence.

The ChEBI entity in xrefs is a chemical, whereas the target is a protein functional requirement. This violates the schema's true own-source equivalence semantics independently of whether a biological requirement can ultimately be supported.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py while preserving the exact supported chemical identity and provenance. Remove chemical-to-protein-class equality. Adjudicate the activity-relative ChemicalParticipant.role and chemical state before adding a typed participant; if unsupported, retain source provenance and explicit uncertainty without inventing a role. Do not move equality into mapped_xrefs, automatically substitute an ion/conjugate/spirolactone, or promote proteins.

- The regenerated record no longer asserts chemical-to-protein-trait equality. Any typed participant has a curator-adjudicated role and state; otherwise provenance and uncertainty remain explicit.
- Use an audited regeneration route selecting the existing target and focused transformation coverage. No native review status or protein requirement is automatically promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | Official ChEBI Introduction and Licensing sections identify a chemical-entity/role resource under CC BY 4.0. This supports chemical-source attribution, not protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16. Original access UTC and digest are retained; this does not establish the live backend release or original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/62811/; Complete identity, names, actual definition or null, formula/charge, structure, source origins/citations and outgoing relations | supports | CHEBI:62811 is heme d cis-diol, C34H34FeN4O6, net charge 0. The structure contains two carboxylic acids and two cis chlorin hydroxy groups. The copied definition describes cis-dihydroxylation of ferroheme b at the source-numbered positions 5 and 6. Source IUPAC naming uses (2RS,3SR), while a stereochemical drawing is provided; this is not independent proof of a universal natural absolute configuration. Fe(II) in the InChI and ferroheme ancestry must not be confused with formal SMILES atom charges. Direct cofactor role, ferroheme/metallochlorin/diol/tertiary-alcohol/dicarboxylic-acid parents, functional parent ferroheme b and conjugate base CHEBI:62814 resolve. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:62811; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete ChEBI identifier and chemical name. The actual definition and annotations were inspected. Chemical resolution is distinct from validating a protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity; its parent is biochemical role CHEBI:52206. This role and a protein class requiring the chemical have different denotations. |
| context-62814 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/62814/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | CHEBI:62814 is heme d cis-diol(2−), C34H32FeN4O6, net charge −2. Both carboxyl groups are deprotonated while both chlorin hydroxy groups remain. The cis ring substitution and source stereochemical drawing are retained. Its IUPAC naming uses the (2RS,3SR) pair; no universal natural absolute configuration is inferred. The InChI iron component is +2, distinct from the formal [Fe-2] SMILES bookkeeping. Direct cofactor role, dicarboxylic-acid-dianion ancestry and the conjugate-base relation to CHEBI:62811 are explicit. |
| context-17627 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17627/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Ferroheme b CHEBI:17627 is explicitly heme b with iron oxidation state +2, C34H32FeN4O4 and net charge 0. The functional-parent relation describes a chemical transformation, not identity with the hydroxylated diol. |
| context-38573 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/38573/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Ferroheme CHEBI:38573 denotes iron(II)–porphyrin coordination complexes under heme; its fixed structure and formula are null. This resolves source oxidation-state ancestry without converting formal SMILES atom charges into metal oxidation states. |
| context-62804 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/62804/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Metallochlorin CHEBI:62804 has null definition/formula/structure and is a child of metalloporphyrin. This broader chemical parent is not a protein-requirement class. |
| context-23824 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23824/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Diol CHEBI:23824 denotes a compound with two hydroxy groups. This structural parent is consistent with the open cis-diol, distinct from a dehydratively cyclized spirolactone. |
| context-26878 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26878/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Tertiary alcohol CHEBI:26878 has an OH attached to saturated carbon bearing three other carbon atoms. Its R-group depiction is a generic class illustration, not a new fixed formula for the target. |
| context-35692 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35692/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | Dicarboxylic acid CHEBI:35692 denotes a carboxylic acid containing two carboxy groups. It supports the neutral diol structural classification without determining its protein-bound protonation state. |
| context-47459 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47459/; Identity, actual definition or null, chemical data, structure and complete outgoing relations | supports | CHEBI:47459 is cis-heme d hydroxychlorin gamma-spirolactone, C34H32FeN4O5 and net charge 0. Its definition describes intramolecular condensation of a hydroxy group and the carboxy group of the 6-carboxyethyl substituent. It has functional parent CHEBI:62811, not an equivalence relation: the cyclic ester has one fewer water molecule than the neutral diol and different connectivity. |
| catalase-structure | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7663946%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full paper not inspected through this response | supports | PMID:7663946; DOI:10.1016/S0969-2126(01)00182-4. The E. coli HPII structure was determined at 2.8 Å and described one cis-heme d prosthetic group per subunit. This is positive catalase heme context, not independent proof of the exact open-diol charge state. |
| spirolactone-structure | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8621527%20AND%20SRC:MED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full paper not inspected through this response | supports | PMID:8621527; DOI:10.1074/jbc.271.15.8863. Crystal structures of Penicillium vitale catalase and E. coli HPII identify cis-hydroxychlorin gamma-spirolactone, with identical absolute stereochemistry of its two chiral carbons. The inactive HPII N201H variant retains heme b. These observations support a bound spirolactone and self-catalyzed protoheme conversion; they do not identify the exact open cis-diol as the bound prosthetic group. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml; Executed 2026-10-21T12:32:13Z through 2026-10-21T12:32:16Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml; Executed 2026-10-21T12:31:57Z through 2026-10-21T12:33:46Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml; Executed 2026-10-21T12:32:16Z through 2026-10-21T12:32:16Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:33:46Z through 2026-10-21T12:33:47Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- Both catalase papers were inspected through complete indexed abstracts. JBC HTML/PDF attempts were denied and are excluded from support. Crystal-coordinate tables, figure-level stereochemistry and exact open-diol protein occupancy were not independently qualified. Source naming/drawing is retained without asserting that every natural heme d has this absolute configuration.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T123806Z-heme-d-cis-diol-chebi62811
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires heme d cis-diol
started_at: '2026-10-21T12:31:32Z'
finished_at: '2026-10-21T12:38:06Z'
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
summary: Neutral heme d cis-diol identity and cis connectivity are supported, separately
  from its dianion and spirolactone. One confirmed major finding concerns chemical-to-protein-trait
  equivalence. Positive catalase evidence is retained without transferring the bound
  spirolactone conclusion to this diol.
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
  - path: data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    sha256: daebaaafceb39e2a04d53b1fd3a696c5712185a57fee6b512fa4dcb6478e0498
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
  selection: Path-order position 7 in batch 023. Fresh main inventory has 429359 records;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5) covers 218 record paths,
    leaving 429141 before this batch. 23 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
targets:
- kind: generated
  label: requires heme d cis-diol
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_62811
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml
    data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:62811 and the exact chemical identity.
    The direct cofactor role and maintained ChEBI emitter resolve. Bounded primary
    context is distinguished from exact-state protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-62814
  - context-17627
  - context-38573
  - context-62804
  - context-23824
  - context-26878
  - context-35692
  - context-47459
  - catalase-structure
  - spirolactone-structure
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:31:32Z'
  snapshot_sha256: daebaaafceb39e2a04d53b1fd3a696c5712185a57fee6b512fa4dcb6478e0498
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
  accessed_at: '2026-10-21T12:31:32Z'
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
  accessed_at: '2026-10-21T12:31:32Z'
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
  accessed_at: '2026-10-21T12:31:32Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:31:32Z'
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
  locator: Introduction and Licensing sections
  summary: Official ChEBI Introduction and Licensing sections identify a chemical-entity/role
    resource under CC BY 4.0. This supports chemical-source attribution, not protein-trait
    equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16.
    Original access UTC and digest are retained; this does not establish the live
    backend release or original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/62811/
  accessed_at: '2026-10-21T12:32:02.253156Z'
  snapshot_sha256: adc88b6c3d920042012a277ac586be8fb72df5d05ff9490b6749a060c7b2b916
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure,
    source origins/citations and outgoing relations
  summary: CHEBI:62811 is heme d cis-diol, C34H34FeN4O6, net charge 0. The structure
    contains two carboxylic acids and two cis chlorin hydroxy groups. The copied definition
    describes cis-dihydroxylation of ferroheme b at the source-numbered positions
    5 and 6. Source IUPAC naming uses (2RS,3SR), while a stereochemical drawing is
    provided; this is not independent proof of a universal natural absolute configuration.
    Fe(II) in the InChI and ferroheme ancestry must not be confused with formal SMILES
    atom charges. Direct cofactor role, ferroheme/metallochlorin/diol/tertiary-alcohol/dicarboxylic-acid
    parents, functional parent ferroheme b and conjugate base CHEBI:62814 resolve.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:62811
  accessed_at: '2026-10-21T12:32:02.253371Z'
  snapshot_sha256: 4a64f84f6561a4515a17c0a6283fe9b4ce32f48ac005e3adf014ee800baa91b9
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete ChEBI identifier and chemical name. The
    actual definition and annotations were inspected. Chemical resolution is distinct
    from validating a protein requirement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity; its parent is biochemical role CHEBI:52206. This
    role and a protein class requiring the chemical have different denotations.
- evidence_id: context-62814
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/62814/
  accessed_at: '2026-10-21T12:32:02.244108Z'
  snapshot_sha256: 64dff9c793922ba74addab4aaa0b55a6ba0a5d52de3a891f88d33c6c4e54c749
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: CHEBI:62814 is heme d cis-diol(2−), C34H32FeN4O6, net charge −2. Both carboxyl
    groups are deprotonated while both chlorin hydroxy groups remain. The cis ring
    substitution and source stereochemical drawing are retained. Its IUPAC naming
    uses the (2RS,3SR) pair; no universal natural absolute configuration is inferred.
    The InChI iron component is +2, distinct from the formal [Fe-2] SMILES bookkeeping.
    Direct cofactor role, dicarboxylic-acid-dianion ancestry and the conjugate-base
    relation to CHEBI:62811 are explicit.
- evidence_id: context-17627
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17627/
  accessed_at: '2026-10-21T12:34:06.961261Z'
  snapshot_sha256: 8212b376ee8bc1b5a65915e8fb1e446e0d7fe249ead1ab8916380bd77bb409ec
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Ferroheme b CHEBI:17627 is explicitly heme b with iron oxidation state
    +2, C34H32FeN4O4 and net charge 0. The functional-parent relation describes a
    chemical transformation, not identity with the hydroxylated diol.
- evidence_id: context-38573
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/38573/
  accessed_at: '2026-10-21T12:34:06.961337Z'
  snapshot_sha256: 59c7e1afeb3835a7b0b7d2cfb82af492035387032b8429d26a2e4b5d4b02575a
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Ferroheme CHEBI:38573 denotes iron(II)–porphyrin coordination complexes
    under heme; its fixed structure and formula are null. This resolves source oxidation-state
    ancestry without converting formal SMILES atom charges into metal oxidation states.
- evidence_id: context-62804
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/62804/
  accessed_at: '2026-10-21T12:34:06.961559Z'
  snapshot_sha256: 6983377dc9a6fc377345f4bf79da80fd91e4420f75196b4a1ca217c671142427
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Metallochlorin CHEBI:62804 has null definition/formula/structure and is
    a child of metalloporphyrin. This broader chemical parent is not a protein-requirement
    class.
- evidence_id: context-23824
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23824/
  accessed_at: '2026-10-21T12:34:07.781222Z'
  snapshot_sha256: 1dfdd60a316ffadf99d33043c71b7366567611f84805a0cbf12d64337ea41325
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Diol CHEBI:23824 denotes a compound with two hydroxy groups. This structural
    parent is consistent with the open cis-diol, distinct from a dehydratively cyclized
    spirolactone.
- evidence_id: context-26878
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26878/
  accessed_at: '2026-10-21T12:34:07.867377Z'
  snapshot_sha256: 4b519b38e6e503a15759adddc5909ed07946c40f31082644f666f3832cca08e9
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Tertiary alcohol CHEBI:26878 has an OH attached to saturated carbon bearing
    three other carbon atoms. Its R-group depiction is a generic class illustration,
    not a new fixed formula for the target.
- evidence_id: context-35692
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35692/
  accessed_at: '2026-10-21T12:34:07.867587Z'
  snapshot_sha256: 0ec2fe53feed1afb338e255f276add8cc69e3917453a4fbf044e3afe9e0aa478
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: Dicarboxylic acid CHEBI:35692 denotes a carboxylic acid containing two
    carboxy groups. It supports the neutral diol structural classification without
    determining its protein-bound protonation state.
- evidence_id: context-47459
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47459/
  accessed_at: '2026-10-21T12:34:08.125948Z'
  snapshot_sha256: bb63b3dc42e65931891a453f1468af90278500b8947829530b82914dfbf3cd62
  support: supports
  locator: Identity, actual definition or null, chemical data, structure and complete
    outgoing relations
  summary: 'CHEBI:47459 is cis-heme d hydroxychlorin gamma-spirolactone, C34H32FeN4O5
    and net charge 0. Its definition describes intramolecular condensation of a hydroxy
    group and the carboxy group of the 6-carboxyethyl substituent. It has functional
    parent CHEBI:62811, not an equivalence relation: the cyclic ester has one fewer
    water molecule than the neutral diol and different connectivity.'
- evidence_id: catalase-structure
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:7663946%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:34:09.434241Z'
  snapshot_sha256: abf60505e3fb7ce233f0fdcfc01e3166a09eedd0f6ee1a2f6e5675a25f199d5a
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
    through this response
  summary: PMID:7663946; DOI:10.1016/S0969-2126(01)00182-4. The E. coli HPII structure
    was determined at 2.8 Å and described one cis-heme d prosthetic group per subunit.
    This is positive catalase heme context, not independent proof of the exact open-diol
    charge state.
- evidence_id: spirolactone-structure
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8621527%20AND%20SRC:MED&resultType=core&format=json
  accessed_at: '2026-10-21T12:34:09.543262Z'
  snapshot_sha256: f7754df7d2387092996ef64e044abfb0ac07df7a24472f10775b18c94117e033
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
    through this response
  summary: PMID:8621527; DOI:10.1074/jbc.271.15.8863. Crystal structures of Penicillium
    vitale catalase and E. coli HPII identify cis-hydroxychlorin gamma-spirolactone,
    with identical absolute stereochemistry of its two chiral carbons. The inactive
    HPII N201H variant retains heme b. These observations support a bound spirolactone
    and self-catalyzed protoheme conversion; they do not identify the exact open cis-diol
    as the bound prosthetic group.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  locator: Executed 2026-10-21T12:32:13Z through 2026-10-21T12:32:16Z; exit 0
  accessed_at: '2026-10-21T12:32:16Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/glutathionate-1-chebi57925.yaml
    data/traits/function/cofactor_requirement/chebi/glutathione-chebi16856.yaml data/traits/function/cofactor_requirement/chebi/group-transfer-coenzymes-chebi24430.yaml
    data/traits/function/cofactor_requirement/chebi/gtp-chebi15996.yaml data/traits/function/cofactor_requirement/chebi/heme-chebi30413.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-2-chebi62814.yaml
    data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    data/traits/function/cofactor_requirement/chebi/heme-o-chebi24480.yaml data/traits/function/cofactor_requirement/chebi/ho-chebi49648.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogen-peroxide-chebi16240.yaml
  locator: Executed 2026-10-21T12:31:57Z through 2026-10-21T12:33:46Z; exit 0
  accessed_at: '2026-10-21T12:33:46Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
  locator: Executed 2026-10-21T12:32:16Z through 2026-10-21T12:32:16Z; exit 0
  accessed_at: '2026-10-21T12:32:16Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:33:46Z through 2026-10-21T12:33:47Z; exit 0
  accessed_at: '2026-10-21T12:33:47Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The identifier, label and copied chemistry agree with current ChEBI/OLS.
    The neutral diol is retained separately from its dianion and the dehydratively
    cyclized spirolactone. No aggregated database charge or adjacent heme state replaces
    the exact source identity.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-62814
  - context-17627
  - context-38573
  - context-62804
  - context-23824
  - context-26878
  - context-35692
  - context-47459
  topic: Exact cis-diol chemical state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: Both source-linked complete abstracts provide positive catalase heme evidence.
    The later structure explicitly identifies a spirolactone, and official ChEBI represents
    it as a different entity with a functional-parent relation to the diol. This distinction
    prevents transfer of the exact bound-state conclusion to the reviewed open diol.
  evidence_ids:
  - chemical
  - catalase-structure
  - spirolactone-structure
  - context-47459
  topic: Catalase heme context and chemical specificity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The direct source cofactor role is retained as positive candidate context.
    The inspected catalase evidence does not independently establish a non-substrate
    requirement for this exact open-diol chemical state. This is an explicit qualification
    limit, not proof that no protein can use the diol and not a reason to relabel
    it as the spirolactone.
  evidence_ids:
  - record
  - schema
  - chemical
  - cofactor-role
  - spirolactone-structure
  - context-47459
  topic: Exact cis-diol protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-7
- area: provenance
  outcome: supported
  summary: The exact chemical identifier, copied source text where present, direct
    cofactor role and ChEBI licence resolve. The requires-label and protein-requirement
    assertion are synthesized by scripts/seed_chebi_cofactor.py. Current snapshots
    do not establish the original seed release.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  topic: Chemical source and maintained emitter
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct source cofactor role explains candidate selection and the local
    broader requirement parent. Chemical structural ancestry remains distinct from
    protein-trait hierarchy, and parent resolution does not certify the parent's own
    equivalence semantics.
  evidence_ids:
  - record
  - chemical
  - cofactor-role
  - owner
  - local-parent-1
  topic: Source role and local broader requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The chemical xref and the synthesized protein-requirement class have different
    denotations. Exact chemical identity, a source role or bounded positive biology
    does not satisfy true own-source equivalence between them.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-62811.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The ChEBI entity in xrefs is a chemical, whereas the target is a protein
    functional requirement. This violates the schema's true own-source equivalence
    semantics independently of whether a biological requirement can ultimately be
    supported.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical entity and protein-requirement class are different
    entity types, a major grounding defect independent of exact-state physiology.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build in scripts/seed_chebi_cofactor.py while preserving the
    exact supported chemical identity and provenance. Remove chemical-to-protein-class
    equality. Adjudicate the activity-relative ChemicalParticipant.role and chemical
    state before adding a typed participant; if unsupported, retain source provenance
    and explicit uncertainty without inventing a role. Do not move equality into mapped_xrefs,
    automatically substitute an ion/conjugate/spirolactone, or promote proteins.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_62811
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated record no longer asserts chemical-to-protein-trait equality. Any
    typed participant has a curator-adjudicated role and state; otherwise provenance
    and uncertainty remain explicit.
  - Use an audited regeneration route selecting the existing target and focused transformation
    coverage. No native review status or protein requirement is automatically promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/heme-d-cis-diol-chebi62811.yaml.
    Run full just validate-all before merging record changes; capture changed inputs
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
- Both catalase papers were inspected through complete indexed abstracts. JBC HTML/PDF
  attempts were denied and are excluded from support. Crystal-coordinate tables, figure-level
  stereochemistry and exact open-diol protein occupancy were not independently qualified.
  Source naming/drawing is retained without asserting that every natural heme d has
  this absolute configuration.
tags:
- unreviewed-path-order
- batch-023
- chebi-cofactor
```
