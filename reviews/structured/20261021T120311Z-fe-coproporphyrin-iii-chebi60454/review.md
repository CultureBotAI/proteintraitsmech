# Review of requires Fe-coproporphyrin III

- Review: 20261021T120311Z-fe-coproporphyrin-iii-chebi60454
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:55:56Z
- Finished UTC: 2026-10-21T12:03:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The neutral Fe-coproporphyrinIII identity and direct cofactor role are supported, with positive bacterioferritin prosthetic-group evidence. One confirmed major finding concerns chemical-to-protein-trait equivalence. Four-carboxyl protonation, iron oxidation state and porphyrin isomer are kept distinct; the exact protein-bound state is not newly qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 021. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7) covers 198 record paths, leaving 429161 before this batch. 21 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml | generated | requires Fe-coproporphyrin III |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_60454 | Official ChEBI/OLS resolve CHEBI:60454 with its exact definition, structure, net charge and direct cofactor role. The conjugate and structural-class sources and complete bacterioferritin primary abstract were inspected. The chemical identity is supported; exact bound state and trait-equivalence semantics remain separate. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### CoproporphyrinIII chemical identity and acid-base state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The exact neutral complex has four carboxylic-acid groups; removal of those four protons yields the tetraanion. Both encode the same FeII/porphyrin connectivity. III is the porphyrin isomer designation, not ferric oxidation state; source coordinate-bond charges are not read as metal oxidation numbers.

### Iron-coproporphyrinIII as a natural protein cofactor

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The inspected primary abstract positively identifies iron-coproporphyrinIII in the stated D.desulfuricans bacterioferritin by complementary analytical methods. That supports the cofactor concept and distinguishes this chemistry from haemB, while preserving the single strain/protein scope and analytical limits.

### Exact protonation and metal state in the bound protein

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The chemical source defines an exact conjugate state, while the primary abstract establishes the iron-coproporphyrinIII prosthetic group without measuring that exact bound protonation population. No universal state, obligatorily required physiological species or newly qualified protein example is inferred. Absence of an optional participant is not the reported defect.

### Direct chemical role and local cofactor parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

Direct cofactor role explains the ChEBI seeder selection and captured broad local parent. Structural chemical ancestry and the conjugate relation do not make neighboring chemical states or protein-requirement classes equivalent. This review does not separately certify the parent.

### Maintained source transform and current chemistry

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The ChEBI seeder appends the copied source definition to a generated protein-requirement wrapper. Current official identifier, role, structure and licence resolve; the original seed release is unassigned. The primary protein context does not turn a chemical ontology entry into an equivalent protein trait.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_60454.

The source chemical and the synthesized protein-requirement class are different entity types. Correct chemistry and positive biochemical context do not satisfy the schema requirement for true own-source equivalence.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-60454.chemical-entity-equivalence.

CHEBI:60454 denotes the exact neutral iron-coproporphyrinIII chemical, while the local class denotes a protein requirement. Positive bacterioferritin cofactor evidence and direct source cofactor role support context but cannot establish chemical/protein-class equality.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality from xrefs while preserving supported chemical grounding and provenance. Preserve the exact carboxyl-protonation, porphyrin-isomer and iron-state scope; do not automatically merge the conjugate pair or infer bound protonation from the free chemical drawing. Adjudicate the activity-relative role before adding a COFACTOR chemical_participant. If that role is not supported, retain provenance and explicit uncertainty without inventing a participant. Do not relocate the equality to mapped_xrefs, merge chemical states or promote protein examples or native status.

- The regenerated xrefs no longer equate a chemical entity/class with the protein requirement. Chemical identity, scope and provenance remain auditable; any participant has a supported activity-relative role.
- Run just validate data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml after the scoped repair. If adjudication changes the target path, validate the replacement and retained/deprecated target disposition explicitly.
- For maintained writer changes add focused pytest coverage and run just audit-writers, just lint and just test. Regenerate the existing target through an audited route. Run full just validate-all before merging record changes; capture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction and Licensing sections identify a chemical-entity ontology and CC BY4.0. This supports chemical-source attribution, not equality to a synthesized protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ChEBI version256 loaded2026-10-16. Original actual access time and digest are preserved; this is not a release pin for the live backend or original seed. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60454; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:60454 as a nonobsolete chemical term; its complete names, description and chemical annotations were inspected. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60454/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | CHEBI:60454 is Fe-coproporphyrinIII, C36H36FeN4O8, net0, with four carboxylic-acid groups. The source connectivity is the iron complex of coproporphyrinIII; its InChI explicitly separates Fe+2 and ligand deprotonation. The coordinate-bond SMILES [Fe-2] notation is not an Fe(−II) oxidation-state claim. The other conjugate differs by four protons, not metal redox or porphyrin isomer. Direct cofactor role is asserted. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Cofactor is a biochemical role for an organic molecule or ion required by an enzyme, under biochemical role52206. It is not itself a chemical molecule or a protein-requirement class. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/68438/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | The tetraanion68438 is C36H32FeN4O8, net−4, with four carboxylates and the same FeII/porphyrin connectivity. Source conjugate relations explicitly link the pair; the four-proton difference must not be treated as reduction/oxidation. |
| metalloporphyrin | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25216/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | The metalloporphyrin structural class has null prose/formula/default structure and porphyrin/metallotetrapyrrole/coordination-entity parents. Its role display is inherited cofactor context; it is not an exact free/complexed protein-state measurement. |
| tetrapyrrole-anion | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58941/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Cyclic tetrapyrrole anion is an organic anion formed by deprotonation of a cyclic tetrapyrrole compound. It does not fix the oxidation state of every complex metal. |
| carboxylate-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35754/; Exact identity, definition field, names, formula/charge, structure and source relations | supports | Tetracarboxylic-acid anion covers removal of one or more carboxyl protons. The exact target/conjugate structures, rather than this broad parent alone, establish four removed protons. |
| bacterioferritin-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11034331%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified bibliographic identity and complete indexed abstract; full article not independently inspected | supports | PMID11034331, DOI10.1016/S0014-5793(00)01939-6: the complete abstract identifies iron-coproporphyrinIII as the bacterioferritin prosthetic group from Desulfovibrio desulfuricans ATCC27774 using visible/NMR spectroscopy and mass spectrometry. This is positive protein-associated cofactor evidence, not merely a presumed biosynthetic intermediate. The abstract does not determine the exact bound carboxyl-protonation population or fully resolve every metal redox state. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml; Executed 2026-10-21T11:56:34Z through 2026-10-21T11:56:35Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/fad-chebi16238.yaml data/traits/function/cofactor_requirement/chebi/fe-chebi18248.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-4-chebi68438.yaml data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml data/traits/function/cofactor_requirement/chebi/fe-s-cluster-chebi30408.yaml data/traits/function/cofactor_requirement/chebi/fe4s2o2-iron-sulfur-oxygen-cluster-chebi60519.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-1-chebi60532.yaml data/traits/function/cofactor_requirement/chebi/ferriheme-a-chebi36183.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-2-chebi60344.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-b-chebi17627.yaml; Executed 2026-10-21T11:56:29Z through 2026-10-21T11:58:14Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml; Executed 2026-10-21T11:56:35Z through 2026-10-21T11:56:35Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:58:14Z through 2026-10-21T11:58:15Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The bacterioferritin study was inspected through its complete indexed abstract, not full methods/results. It establishes the named prosthetic group in one strain/protein context but does not determine the exact free/anion or bound-protonation equilibrium. Structural/conjugate comparisons are external chemical entries, not local sibling-record assessments.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T120311Z-fe-coproporphyrin-iii-chebi60454
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires Fe-coproporphyrin III
started_at: '2026-10-21T11:55:56Z'
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
summary: The neutral Fe-coproporphyrinIII identity and direct cofactor role are supported,
  with positive bacterioferritin prosthetic-group evidence. One confirmed major finding
  concerns chemical-to-protein-trait equivalence. Four-carboxyl protonation, iron
  oxidation state and porphyrin isomer are kept distinct; the exact protein-bound
  state is not newly qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
    sha256: 1ecb1a9aeb65851869c91590a095e76708ee8d148f7bbdcaf2ee80cc7bf2b781
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
  selection: Path-order position 4 in batch 021. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
targets:
- kind: generated
  label: requires Fe-coproporphyrin III
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_60454
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:60454 with its exact definition, structure,
    net charge and direct cofactor role. The conjugate and structural-class sources
    and complete bacterioferritin primary abstract were inspected. The chemical identity
    is supported; exact bound state and trait-equivalence semantics remain separate.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
  - conjugate
  - metalloporphyrin
  - tetrapyrrole-anion
  - carboxylate-parent
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:55:56Z'
  snapshot_sha256: 1ecb1a9aeb65851869c91590a095e76708ee8d148f7bbdcaf2ee80cc7bf2b781
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
  accessed_at: '2026-10-21T11:55:56Z'
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
  accessed_at: '2026-10-21T11:55:56Z'
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
  accessed_at: '2026-10-21T11:55:56Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:55:56Z'
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
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:60454
  accessed_at: '2026-10-21T11:56:55.967355Z'
  snapshot_sha256: 423e66bfbbc66f18cda91ba6897190fd2e406eee32b541dff579f60ac3d22897
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:60454 as a nonobsolete chemical term; its complete names,
    description and chemical annotations were inspected.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60454/
  accessed_at: '2026-10-21T11:56:55.893345Z'
  snapshot_sha256: 635515589583eba9122d34ca68eedda45edd45377dd5cce169b333d0ba6a5f4a
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: CHEBI:60454 is Fe-coproporphyrinIII, C36H36FeN4O8, net0, with four carboxylic-acid
    groups. The source connectivity is the iron complex of coproporphyrinIII; its
    InChI explicitly separates Fe+2 and ligand deprotonation. The coordinate-bond
    SMILES [Fe-2] notation is not an Fe(−II) oxidation-state claim. The other conjugate
    differs by four protons, not metal redox or porphyrin isomer. Direct cofactor
    role is asserted.
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
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/68438/
  accessed_at: '2026-10-21T11:56:55.239486Z'
  snapshot_sha256: 20e1566f56c09b72e8d7696febc3e79b5a7f03ad777ef1cec0c3432712de0edd
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: The tetraanion68438 is C36H32FeN4O8, net−4, with four carboxylates and
    the same FeII/porphyrin connectivity. Source conjugate relations explicitly link
    the pair; the four-proton difference must not be treated as reduction/oxidation.
- evidence_id: metalloporphyrin
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25216/
  accessed_at: '2026-10-21T11:58:02.376957Z'
  snapshot_sha256: 466ce14d4e6ec13e4167828f76a513f387abb9e07cff991d08b32e9a4ab25b93
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: The metalloporphyrin structural class has null prose/formula/default structure
    and porphyrin/metallotetrapyrrole/coordination-entity parents. Its role display
    is inherited cofactor context; it is not an exact free/complexed protein-state
    measurement.
- evidence_id: tetrapyrrole-anion
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58941/
  accessed_at: '2026-10-21T11:58:02.127702Z'
  snapshot_sha256: babc23c3ca6c646fc0251a085862cd4f024809ccc0052f07989b863839897ec5
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Cyclic tetrapyrrole anion is an organic anion formed by deprotonation of
    a cyclic tetrapyrrole compound. It does not fix the oxidation state of every complex
    metal.
- evidence_id: carboxylate-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35754/
  accessed_at: '2026-10-21T11:58:02.997204Z'
  snapshot_sha256: f3fa298e63fe2176bc9f3134342386ef50cda721501e2f8532365266b33628f5
  support: supports
  locator: Exact identity, definition field, names, formula/charge, structure and
    source relations
  summary: Tetracarboxylic-acid anion covers removal of one or more carboxyl protons.
    The exact target/conjugate structures, rather than this broad parent alone, establish
    four removed protons.
- evidence_id: bacterioferritin-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11034331%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:58:03.708985Z'
  snapshot_sha256: 705a2c7df2428846d4abe2513947ee57071a39d5e120347c6a20ded1d04ebcd6
  support: supports
  locator: Verified bibliographic identity and complete indexed abstract; full article
    not independently inspected
  summary: 'PMID11034331, DOI10.1016/S0014-5793(00)01939-6: the complete abstract
    identifies iron-coproporphyrinIII as the bacterioferritin prosthetic group from
    Desulfovibrio desulfuricans ATCC27774 using visible/NMR spectroscopy and mass
    spectrometry. This is positive protein-associated cofactor evidence, not merely
    a presumed biosynthetic intermediate. The abstract does not determine the exact
    bound carboxyl-protonation population or fully resolve every metal redox state.'
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  locator: Executed 2026-10-21T11:56:34Z through 2026-10-21T11:56:35Z; exit 0
  accessed_at: '2026-10-21T11:56:35Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
  locator: Executed 2026-10-21T11:56:35Z through 2026-10-21T11:56:35Z; exit 0
  accessed_at: '2026-10-21T11:56:35Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The exact neutral complex has four carboxylic-acid groups; removal of those
    four protons yields the tetraanion. Both encode the same FeII/porphyrin connectivity.
    III is the porphyrin isomer designation, not ferric oxidation state; source coordinate-bond
    charges are not read as metal oxidation numbers.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - conjugate
  topic: CoproporphyrinIII chemical identity and acid-base state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The inspected primary abstract positively identifies iron-coproporphyrinIII
    in the stated D.desulfuricans bacterioferritin by complementary analytical methods.
    That supports the cofactor concept and distinguishes this chemistry from haemB,
    while preserving the single strain/protein scope and analytical limits.
  evidence_ids:
  - chemical
  - bacterioferritin-primary
  topic: Iron-coproporphyrinIII as a natural protein cofactor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The chemical source defines an exact conjugate state, while the primary
    abstract establishes the iron-coproporphyrinIII prosthetic group without measuring
    that exact bound protonation population. No universal state, obligatorily required
    physiological species or newly qualified protein example is inferred. Absence
    of an optional participant is not the reported defect.
  evidence_ids:
  - record
  - schema
  - chemical
  - conjugate
  - bacterioferritin-primary
  topic: Exact protonation and metal state in the bound protein
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: Direct cofactor role explains the ChEBI seeder selection and captured broad
    local parent. Structural chemical ancestry and the conjugate relation do not make
    neighboring chemical states or protein-requirement classes equivalent. This review
    does not separately certify the parent.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - conjugate
  - cofactor-role
  - metalloporphyrin
  - tetrapyrrole-anion
  - carboxylate-parent
  topic: Direct chemical role and local cofactor parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The ChEBI seeder appends the copied source definition to a generated protein-requirement
    wrapper. Current official identifier, role, structure and licence resolve; the
    original seed release is unassigned. The primary protein context does not turn
    a chemical ontology entry into an equivalent protein trait.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - release
  - bacterioferritin-primary
  topic: Maintained source transform and current chemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-9
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-60454.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:60454 denotes the exact neutral iron-coproporphyrinIII chemical,
    while the local class denotes a protein requirement. Positive bacterioferritin
    cofactor evidence and direct source cofactor role support context but cannot establish
    chemical/protein-class equality.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
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
    equality from xrefs while preserving supported chemical grounding and provenance.
    Preserve the exact carboxyl-protonation, porphyrin-isomer and iron-state scope;
    do not automatically merge the conjugate pair or infer bound protonation from
    the free chemical drawing. Adjudicate the activity-relative role before adding
    a COFACTOR chemical_participant. If that role is not supported, retain provenance
    and explicit uncertainty without inventing a participant. Do not relocate the
    equality to mapped_xrefs, merge chemical states or promote protein examples or
    native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_60454
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated xrefs no longer equate a chemical entity/class with the protein
    requirement. Chemical identity, scope and provenance remain auditable; any participant
    has a supported activity-relative role.
  - Run just validate data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/fe-coproporphyrin-iii-chebi60454.yaml
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
- The bacterioferritin study was inspected through its complete indexed abstract,
  not full methods/results. It establishes the named prosthetic group in one strain/protein
  context but does not determine the exact free/anion or bound-protonation equilibrium.
  Structural/conjugate comparisons are external chemical entries, not local sibling-record
  assessments.
tags:
- unreviewed-path-order
- batch-021
- chebi-cofactor
```
