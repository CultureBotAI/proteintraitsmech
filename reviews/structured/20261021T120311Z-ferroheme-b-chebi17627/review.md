# Review of requires ferroheme b

- Review: 20261021T120311Z-ferroheme-b-chebi17627
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:56:05Z
- Finished UTC: 2026-10-21T12:03:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Neutral ferroheme b identity and Fe(II) assignment resolve with positive bounded heme-b electron-transfer context. One confirmed major finding concerns chemical-to-protein-trait equivalence. Component/model provenance does not independently qualify an exact free-state protein requirement.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 021. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7) covers 198 record paths, leaving 429161 before this batch. 21 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml | generated | requires ferroheme b |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17627 | Official ChEBI and OLS resolve CHEBI:17627 with its exact identity, current definition and direct cofactor role. The maintained seeder, captured local parent and source licence are established. HEM component connectivity and the bounded heme-b primary abstract are distinguished from exact protein-bound state; the metabolic-model citation supplies provenance. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Ferroheme b iron state and carboxyl protonation

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The source identity specifies Fe(II) protoporphyrin IX. The target is neutral with two COOH groups and has dianion CHEBI:60344 as its conjugate base. This acid-base difference does not oxidize iron, alter vinyl/methyl substituents or create a different tetrapyrrole. The [Fe-2] notation is distinct from the explicitly sourced +2 oxidation state.

### Positive heme-b electron-transfer context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The yeast flavocytochrome study positively links its heme domain to electron transfer and describes a structure with exposed propionate groups. Its docking model remains a proposal. The chemical-component descriptor and metabolic reconstruction are separate source contexts rather than independent measurements of exact protein-bound heme charge.

### Exact ferroheme state and protein qualification

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

General functional heme-b relevance is supported, while the exact neutral/dianionic component, Fe redox state during catalysis, protonation of protein-bound propionates and individual protein qualification remain distinct questions. No acid-base merging, universal dependence or newly qualified native example follows from the inspected sources.

### Maintained chemical-to-requirement source transformation

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

This target is owned by scripts/seed_chebi_cofactor.py and is emitted through its ChEBI role selection. The captured owner synthesizes its protein-requirement wrapper. No unrelated local alignment crosswalk is used as target evidence.

### Chemical source attribution and original-release limit

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The exact ChEBI identifier, copied source definition, direct cofactor role and licence resolve. Current ChEBI/OLS responses establish comparison chemistry and metadata, not the original release used by the seed or true chemical-to-protein-class equivalence.

### Direct cofactor role and local broader requirement

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The current source directly asserts cofactor role, explaining selection and the captured local cofactor-requirement parent. Chemical structural ancestry and inherited roles are separate contexts; this review does not certify the parent or qualify a protein from source-role membership alone.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17627.

The chemical entity in xrefs and the local protein functional requirement have different denotations. Correct source chemistry and positive bounded biological context do not make them true source-direct equivalents.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17627.chemical-entity-equivalence.

CHEBI:17627 denotes a chemical entity, whereas the local record denotes a protein functional requirement. Authentic cofactor roles, structural identity and bounded functional evidence do not satisfy the schema's true own-source equivalence meaning of xrefs.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality while retaining the supported exact chemical scope and source provenance. Adjudicate the activity-relative ChemicalParticipant.role and chemical state before adding a typed participant. If the required role cannot be supported, retain provenance and explicit uncertainty without inventing a participant. Preserve cluster composition or heme side chains, stereochemistry, acid-base and redox distinctions as applicable; do not replace the target by a nonidentical source-linked component, relocate the same equality to mapped_xrefs, merge states or automatically qualify proteins.

- The regenerated target retains its exact source identity and class scope without chemical/protein-class equality. Any participant has an adjudicated activity-relative role; otherwise provenance and uncertainty remain explicit.
- Use an audited route selecting the existing target, with a focused source-transform fixture. Preserve positive functional evidence within its tested scope and the stated free-state/protein-bound limits. No status or protein-example promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction and Licensing sections identify a chemical entity/role resource distributed under CC BY 4.0. This supports source attribution, not equality to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata identifies comparison ontology version 256, loaded 2026-10-16. Its original access time and digest are retained; the original seed release and the live backend release are not thereby established. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17627/; Complete identifier/name/definition, aliases, formula/charge, structure, origins and incoming/outgoing relations | supports | CHEBI:17627 is ferroheme b, C34H32FeN4O4, molecular charge 0, with two COOH groups and iron oxidation state +2. The fixed protoporphyrin IX structure retains two vinyl and four methyl substituents. The InChI Fe(II) assignment is distinct from the [Fe-2] coordinate-bond SMILES notation. Direct roles are cofactor and human metabolite; source parents are heme b and ferroheme, with conjugate base CHEBI:60344. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17627; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier, with the source definition, aliases, formula/charge and structure annotations inspected. Chemical resolution does not make a chemical equivalent to a protein-requirement class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity. Its parent is biochemical role CHEBI:52206; it is not a molecular entity or a protein-requirement class. |
| context-60344 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60344/; Complete identity, names, actual definition or null, formula/charge, structure and outgoing relations | supports | CHEBI:60344 is ferroheme b(2−), C34H30FeN4O4, net −2, with both propionate groups deprotonated. The iron remains Fe(II), as supported by the source name and InChI; [Fe-2] in the SMILES is not oxidation state −II. The two vinyl groups and four methyl groups of the protoporphyrin IX scaffold remain. Its direct roles are cofactor and Saccharomyces cerevisiae metabolite, and its conjugate acid is CHEBI:17627. Major species at pH 7.3 is a current source assertion, not an independent population measurement. |
| context-26355 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26355/; Complete identity, names, actual definition or null, formula/charge, structure and outgoing relations | supports | Heme b CHEBI:26355 describes a metalloprotoporphyrin with four pyrrole nitrogens coordinated to iron. It is broader source taxonomy than the explicitly named ferroheme state. Its illustrative formula and structure are not a proof that every heme-b context has one oxidation/protonation state. |
| context-38573 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/38573/; Complete identity, names, actual definition or null, formula/charge, structure and outgoing relations | supports | Ferroheme CHEBI:38573 explicitly denotes any iron(II)-porphyrin coordination complex and has parent heme. This is chemical oxidation-state taxonomy, not a protein-requirement class. |
| context-30413 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30413/; Complete identity, names, actual definition or null, formula/charge, structure and outgoing relations | supports | Heme CHEBI:30413 is any tetrapyrrolic chelate of iron. It has prosthetic-group and metabolite roles and structural parents for iron coordination/tetrapyrrole chemistry. The broad role context does not make each heme molecule equivalent to a protein requirement. |
| context-77746 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/77746/; Complete identity, names, actual definition or null, formula/charge, structure and outgoing relations | supports | Human metabolite CHEBI:77746 denotes a mammalian metabolite produced during a metabolic reaction in humans. This source role does not itself establish an exact-state protein requirement. |
| prosthetic-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Definition and outgoing relations | supports | Prosthetic group is a tightly bound nonpolypeptide unit involved in protein activity and has parent cofactor. The heme family has this role; that does not establish exact-state protein qualification for each chemical entry. |
| heme-component | https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/HEM; Complete HEM component summary, formula, InChI/InChIKey and SMILES | supports | The official PDBe HEM component describes protoporphyrin IX containing Fe, C34H32FeN4O4, with the same InChIKey as neutral CHEBI:17627. The current summary formal-charge field is null. This matches chemical-component connectivity but does not measure the metal oxidation state or protonation of every HEM occurrence in a protein. |
| heme-b-function | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20546754%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper and PDB coordinates not independently inspected | supports | PMID:20546754; DOI:10.1016/j.jmb.2010.05.035. The complete indexed abstract reports yeast flavocytochrome b2, inhibition of flavin-to-heme electron transfer by a bound antibody and a 2.7 Å heme-domain/Fab structure. It describes exposed heme propionates and proposes a cytochrome-c docking model. This is positive heme-b functional context; the model remains proposed, and the abstract does not determine exact free-state charge or all protein-bound oxidation states. |
| origin-model | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1038/nbt.2488&amp;format=json&amp;resultType=core; Verified DOI/PMID and complete indexed abstract; full article not inspected | context_only | PMID:23455439; DOI:10.1038/nbt.2488. The complete source-linked Recon2 abstract concerns a consensus human metabolic reconstruction and model predictions/integration. It resolves the human-metabolite provenance citation, not a direct experiment establishing an exact neutral ferroheme protein requirement. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Executed 2026-10-21T11:56:43Z through 2026-10-21T11:56:45Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/fad-chebi16238.yaml data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-4-chebi68438.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml data/traits/function/cofactor_requirement/chebi/fe-s-cluster-chebi30408.yaml data/traits/function/cofactor_requirement/chebi/fe4s2o2-iron-sulfur-oxygen-cluster-chebi60519.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-1-chebi60532.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-chebi36183.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-2-chebi60344.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Executed 2026-10-21T11:56:29Z through 2026-10-21T11:58:14Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Executed 2026-10-21T11:56:45Z through 2026-10-21T11:56:45Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:58:14Z through 2026-10-21T11:58:15Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The functional paper and source-linked model were inspected through complete indexed abstracts. No full-paper or coordinate-level redox, protonation or residue qualification is claimed. Component descriptors establish their own chemistry and do not measure every protein-bound state; no unspecified parent heme is treated as interchangeable with the exact ferroheme target.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T120311Z-ferroheme-b-chebi17627
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires ferroheme b
started_at: '2026-10-21T11:56:05Z'
finished_at: '2026-10-21T12:03:11Z'
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
summary: Neutral ferroheme b identity and Fe(II) assignment resolve with positive
  bounded heme-b electron-transfer context. One confirmed major finding concerns chemical-to-protein-trait
  equivalence. Component/model provenance does not independently qualify an exact
  free-state protein requirement.
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
  - path: data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
    sha256: eee8206920c1a5111cd841d0ed6d20aef9a2b79e3c7b555c6f63709a3172a0a3
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
  selection: Path-order position 10 in batch 021. Fresh main inventory has 429359
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
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7) covers 198 record paths,
    leaving 429161 before this batch. 21 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
targets:
- kind: generated
  label: requires ferroheme b
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17627
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve CHEBI:17627 with its exact identity, current
    definition and direct cofactor role. The maintained seeder, captured local parent
    and source licence are established. HEM component connectivity and the bounded
    heme-b primary abstract are distinguished from exact protein-bound state; the
    metabolic-model citation supplies provenance.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-60344
  - context-26355
  - context-38573
  - context-30413
  - context-77746
  - prosthetic-role
  - heme-component
  - heme-b-function
  - origin-model
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:56:05Z'
  snapshot_sha256: eee8206920c1a5111cd841d0ed6d20aef9a2b79e3c7b555c6f63709a3172a0a3
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
  accessed_at: '2026-10-21T11:56:05Z'
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
  accessed_at: '2026-10-21T11:56:05Z'
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
  accessed_at: '2026-10-21T11:56:05Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:56:05Z'
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
  summary: The official ChEBI Introduction and Licensing sections identify a chemical
    entity/role resource distributed under CC BY 4.0. This supports source attribution,
    not equality to a synthesized protein requirement.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata identifies comparison ontology version 256,
    loaded 2026-10-16. Its original access time and digest are retained; the original
    seed release and the live backend release are not thereby established.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17627/
  accessed_at: '2026-10-21T11:56:32.751176Z'
  snapshot_sha256: 8212b376ee8bc1b5a65915e8fb1e446e0d7fe249ead1ab8916380bd77bb409ec
  support: supports
  locator: Complete identifier/name/definition, aliases, formula/charge, structure,
    origins and incoming/outgoing relations
  summary: CHEBI:17627 is ferroheme b, C34H32FeN4O4, molecular charge 0, with two
    COOH groups and iron oxidation state +2. The fixed protoporphyrin IX structure
    retains two vinyl and four methyl substituents. The InChI Fe(II) assignment is
    distinct from the [Fe-2] coordinate-bond SMILES notation. Direct roles are cofactor
    and human metabolite; source parents are heme b and ferroheme, with conjugate
    base CHEBI:60344.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:17627
  accessed_at: '2026-10-21T11:56:31.848713Z'
  snapshot_sha256: aa066e8596b1e864fc557c13c7ba2ecef5e0040dfdab9e629c3d09ae9b426677
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier, with the source
    definition, aliases, formula/charge and structure annotations inspected. Chemical
    resolution does not make a chemical equivalent to a protein-requirement class.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations
  summary: Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion
    required for enzyme activity. Its parent is biochemical role CHEBI:52206; it is
    not a molecular entity or a protein-requirement class.
- evidence_id: context-60344
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60344/
  accessed_at: '2026-10-21T11:56:32.748177Z'
  snapshot_sha256: 86a3f59e26c389838f1536460903b0270efacbea364d30bc135449c902c0d6c7
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure
    and outgoing relations
  summary: CHEBI:60344 is ferroheme b(2−), C34H30FeN4O4, net −2, with both propionate
    groups deprotonated. The iron remains Fe(II), as supported by the source name
    and InChI; [Fe-2] in the SMILES is not oxidation state −II. The two vinyl groups
    and four methyl groups of the protoporphyrin IX scaffold remain. Its direct roles
    are cofactor and Saccharomyces cerevisiae metabolite, and its conjugate acid is
    CHEBI:17627. Major species at pH 7.3 is a current source assertion, not an independent
    population measurement.
- evidence_id: context-26355
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26355/
  accessed_at: '2026-10-21T11:57:00.167338Z'
  snapshot_sha256: bcabde14d60370a3cfb4640210110283fcbd622d3008e2298299179ae0b5a763
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure
    and outgoing relations
  summary: Heme b CHEBI:26355 describes a metalloprotoporphyrin with four pyrrole
    nitrogens coordinated to iron. It is broader source taxonomy than the explicitly
    named ferroheme state. Its illustrative formula and structure are not a proof
    that every heme-b context has one oxidation/protonation state.
- evidence_id: context-38573
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/38573/
  accessed_at: '2026-10-21T11:57:00.169807Z'
  snapshot_sha256: 59c7e1afeb3835a7b0b7d2cfb82af492035387032b8429d26a2e4b5d4b02575a
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure
    and outgoing relations
  summary: Ferroheme CHEBI:38573 explicitly denotes any iron(II)-porphyrin coordination
    complex and has parent heme. This is chemical oxidation-state taxonomy, not a
    protein-requirement class.
- evidence_id: context-30413
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30413/
  accessed_at: '2026-10-21T11:57:51.493934Z'
  snapshot_sha256: 39ffafcfd4c939d9283d2fa52598b9a119543eaad7841f8de09e625ff264c44e
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure
    and outgoing relations
  summary: Heme CHEBI:30413 is any tetrapyrrolic chelate of iron. It has prosthetic-group
    and metabolite roles and structural parents for iron coordination/tetrapyrrole
    chemistry. The broad role context does not make each heme molecule equivalent
    to a protein requirement.
- evidence_id: context-77746
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/77746/
  accessed_at: '2026-10-21T11:57:00.908456Z'
  snapshot_sha256: 1ef2b7a3d31fedcf864bedc43cbaee8d3e328f30c1902a4150143cda62df0ee4
  support: supports
  locator: Complete identity, names, actual definition or null, formula/charge, structure
    and outgoing relations
  summary: Human metabolite CHEBI:77746 denotes a mammalian metabolite produced during
    a metabolic reaction in humans. This source role does not itself establish an
    exact-state protein requirement.
- evidence_id: prosthetic-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:10:09.154369Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Definition and outgoing relations
  summary: Prosthetic group is a tightly bound nonpolypeptide unit involved in protein
    activity and has parent cofactor. The heme family has this role; that does not
    establish exact-state protein qualification for each chemical entry.
- evidence_id: heme-component
  kind: database
  reference: https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/HEM
  accessed_at: '2026-10-21T11:57:02.268518Z'
  snapshot_sha256: fe03550f20d39863185172dd85cae9bd0bbe236644b80f2e1e3597196b0684a1
  support: supports
  locator: Complete HEM component summary, formula, InChI/InChIKey and SMILES
  summary: The official PDBe HEM component describes protoporphyrin IX containing
    Fe, C34H32FeN4O4, with the same InChIKey as neutral CHEBI:17627. The current summary
    formal-charge field is null. This matches chemical-component connectivity but
    does not measure the metal oxidation state or protonation of every HEM occurrence
    in a protein.
- evidence_id: heme-b-function
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20546754%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:57:01.585014Z'
  snapshot_sha256: 6f32273955c6d050728c53d6a8b239f0f04100fd8676ddd91c304833ff28bd7b
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper and PDB coordinates
    not independently inspected
  summary: PMID:20546754; DOI:10.1016/j.jmb.2010.05.035. The complete indexed abstract
    reports yeast flavocytochrome b2, inhibition of flavin-to-heme electron transfer
    by a bound antibody and a 2.7 Å heme-domain/Fab structure. It describes exposed
    heme propionates and proposes a cytochrome-c docking model. This is positive heme-b
    functional context; the model remains proposed, and the abstract does not determine
    exact free-state charge or all protein-bound oxidation states.
- evidence_id: origin-model
  kind: database
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.1038/nbt.2488&format=json&resultType=core
  accessed_at: '2026-10-21T11:57:02.545207Z'
  snapshot_sha256: e6a50fe7a7ea11cdfc6ef2fcbc532577e913d89e2612fd95883a1f0cf422737d
  support: context_only
  locator: Verified DOI/PMID and complete indexed abstract; full article not inspected
  summary: PMID:23455439; DOI:10.1038/nbt.2488. The complete source-linked Recon2
    abstract concerns a consensus human metabolic reconstruction and model predictions/integration.
    It resolves the human-metabolite provenance citation, not a direct experiment
    establishing an exact neutral ferroheme protein requirement.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  locator: Executed 2026-10-21T11:56:43Z through 2026-10-21T11:56:45Z; exit 0
  accessed_at: '2026-10-21T11:56:45Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
  locator: Executed 2026-10-21T11:56:45Z through 2026-10-21T11:56:45Z; exit 0
  accessed_at: '2026-10-21T11:56:45Z'
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
  summary: scripts/seed_chebi_cofactor.py owns generated target changes. Its source
    transformation is inspected; no emitted record has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source identity specifies Fe(II) protoporphyrin IX. The target is neutral
    with two COOH groups and has dianion CHEBI:60344 as its conjugate base. This acid-base
    difference does not oxidize iron, alter vinyl/methyl substituents or create a
    different tetrapyrrole. The [Fe-2] notation is distinct from the explicitly sourced
    +2 oxidation state.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-60344
  - context-38573
  - heme-component
  topic: Ferroheme b iron state and carboxyl protonation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The yeast flavocytochrome study positively links its heme domain to electron
    transfer and describes a structure with exposed propionate groups. Its docking
    model remains a proposal. The chemical-component descriptor and metabolic reconstruction
    are separate source contexts rather than independent measurements of exact protein-bound
    heme charge.
  evidence_ids:
  - heme-b-function
  - heme-component
  - origin-model
  - chemical
  topic: Positive heme-b electron-transfer context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: General functional heme-b relevance is supported, while the exact neutral/dianionic
    component, Fe redox state during catalysis, protonation of protein-bound propionates
    and individual protein qualification remain distinct questions. No acid-base merging,
    universal dependence or newly qualified native example follows from the inspected
    sources.
  evidence_ids:
  - record
  - schema
  - chemical
  - context-60344
  - heme-b-function
  - heme-component
  - prosthetic-role
  topic: Exact ferroheme state and protein qualification
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-7
- area: ownership
  outcome: supported
  summary: This target is owned by scripts/seed_chebi_cofactor.py and is emitted through
    its ChEBI role selection. The captured owner synthesizes its protein-requirement
    wrapper. No unrelated local alignment crosswalk is used as target evidence.
  evidence_ids:
  - record
  - owner
  - registry
  topic: Maintained chemical-to-requirement source transformation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The exact ChEBI identifier, copied source definition, direct cofactor role
    and licence resolve. Current ChEBI/OLS responses establish comparison chemistry
    and metadata, not the original release used by the seed or true chemical-to-protein-class
    equivalence.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - licence
  - current-release
  topic: Chemical source attribution and original-release limit
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-9
- area: consistency
  outcome: supported
  summary: The current source directly asserts cofactor role, explaining selection
    and the captured local cofactor-requirement parent. Chemical structural ancestry
    and inherited roles are separate contexts; this review does not certify the parent
    or qualify a protein from source-role membership alone.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - owner
  topic: Direct cofactor role and local broader requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The chemical entity in xrefs and the local protein functional requirement
    have different denotations. Correct source chemistry and positive bounded biological
    context do not make them true source-direct equivalents.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17627.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: CHEBI:17627 denotes a chemical entity, whereas the local record denotes
    a protein functional requirement. Authentic cofactor roles, structural identity
    and bounded functional evidence do not satisfy the schema's true own-source equivalence
    meaning of xrefs.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The proposed requirement is recognizable, but a chemical entity
    and a protein requirement for it have different denotations. This is a major grounding
    defect even when chemistry and bounded biological function are supported.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait
    equality while retaining the supported exact chemical scope and source provenance.
    Adjudicate the activity-relative ChemicalParticipant.role and chemical state before
    adding a typed participant. If the required role cannot be supported, retain provenance
    and explicit uncertainty without inventing a participant. Preserve cluster composition
    or heme side chains, stereochemistry, acid-base and redox distinctions as applicable;
    do not replace the target by a nonidentical source-linked component, relocate
    the same equality to mapped_xrefs, merge states or automatically qualify proteins.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17627
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target retains its exact source identity and class scope without
    chemical/protein-class equality. Any participant has an adjudicated activity-relative
    role; otherwise provenance and uncertainty remain explicit.
  - Use an audited route selecting the existing target, with a focused source-transform
    fixture. Preserve positive functional evidence within its tested scope and the
    stated free-state/protein-bound limits. No status or protein-example promotion
    occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml.
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
- The functional paper and source-linked model were inspected through complete indexed
  abstracts. No full-paper or coordinate-level redox, protonation or residue qualification
  is claimed. Component descriptors establish their own chemistry and do not measure
  every protein-bound state; no unspecified parent heme is treated as interchangeable
  with the exact ferroheme target.
tags:
- unreviewed-path-order
- batch-021
- chebi-cofactor
```
