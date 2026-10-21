# Review of requires flavin adenine dinucleotide

- Review: 20261021T121753Z-flavin-adenine-dinucleotide-chebi24040
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:12:39Z
- Finished UTC: 2026-10-21T12:17:53Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The broad FAD chemical class is supported, distinct from exact oxidized, reduced and radical forms. One confirmed major finding concerns chemical-class/protein-requirement equivalence. Null fixed chemical fields are appropriate class context; positive enzyme evidence does not establish universal member interchangeability.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 022. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df) covers 208 record paths, leaving 429151 before this batch. 22 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml | generated | requires flavin adenine dinucleotide |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_24040 | Official ChEBI/OLS resolve the broad CHEBI:24040 class with direct cofactor role and actual null definition/chemical fields. Structural parents and distinct molecular subclasses were inspected, alongside the bounded enzyme authority. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Maintained ChEBI source transformation and release limits

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The captured ChEBI seeder selects role descendants or chemical entities with a cofactor-related role, synthesizes the requirement wrapper and emits the chemical xref. The current chemical identity, source attribution and licence resolve; the exact original seed release remains unassigned.

### Broad flavin chemical class and distinct molecular states

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The target denotes a reusable requirement candidate for the broad source chemical class. The inspected oxidized, reduced and semiquinone subclasses show why no single formula, charge or structure belongs to the whole class. Null source prose does not by itself make the concise requirement definition defective, and it does not license treating the generic class as the exact neutral member.

### Positive flavin enzyme context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The inspected enzyme authority provides a concrete FAD glucose-oxidase context. This supports biological relevance while preserving the tested class/member and evidence scope.

### Generic chemical-class requirement and exact-state qualification

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

Source chemical-role membership and positive enzyme contexts do not establish that a protein accepts every redox form or modified descendant. Any exact chemical participant or protein example needs activity-relative evidence and the intended member/state. A broad candidate class can remain useful without inventing a fixed formula, a mandatory optional example or universal interchangeability.

### Direct cofactor role and retained class hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

Direct cofactor role explains the local ChEBI-role seeder and broader cofactor-requirement parent. Source chemical ancestry is distinct from local protein-trait equivalence; the review preserves that hierarchy without certifying every upstream classification or local parent.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_24040.

The source chemical and the local protein functional requirement are different entity types. Correct chemistry, authentic source roles and bounded biological context do not establish true own-source equivalence.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-24040.chemical-entity-equivalence.

CHEBI:24040 denotes a broad chemical class, whereas the local record denotes the functional requirement of a protein. Authentic cofactor role and positive enzyme evidence cannot make the chemical class itself equivalent to the requiring protein class.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality from xrefs while preserving source grounding and provenance. Preserve the broad chemical-class scope unless a curator explicitly narrows it with evidence. Do not silently replace it by the exact oxidized member, collapse reduced/radical/modified descendants or assert that each protein accepts every class member. Adjudicate the activity-relative role before adding any COFACTOR chemical_participant. If that role cannot be supported, retain provenance and explicit uncertainty without inventing a participant. Do not relocate the equality to mapped_xrefs or promote a protein example or native status.

- The regenerated xrefs no longer equate the chemical entity or chemical class with the requirement trait; exact supported scope and provenance remain auditable. Any participant has an adjudicated activity-relative role, and optional participant absence is not itself a defect.
- Run just validate data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml after the scoped repair.
- For maintained writer changes add focused pytest coverage and run just audit-writers, just lint and just test. Regenerate the existing target through an audited route. Run full just validate-all before merging record changes; capture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction and Licensing sections establish chemical-entity/role scope and CC BY 4.0 licensing. They do not equate a chemical with a synthesized protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata identifies ChEBI version 256, loaded 2026-10-16. The original access timestamp and digest are retained; neither the live backend release nor the original seed release is established by this metadata. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:24040; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:24040 as nonobsolete; actual names, description and available chemical annotations were inspected. Empty fields are retained as empty rather than treated as a fixed chemical formula. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24040/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | CHEBI:24040 is the broad flavin adenine dinucleotide chemical class. The current definition, chemical_data and default_structure are null and aliases are empty. It directly has cofactor role and flavin, flavin-nucleotide and dinucleotide parents. Incoming subclasses include oxidized FAD, reduced FADH2, semiquinone and modified flavins; the broad class is not an exact synonym for one oxidation, protonation or derivative state. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | Cofactor is a biochemical role for an organic molecule or ion required by an enzyme for activity, under biochemical role CHEBI:52206. It is not itself a protein-requirement class. |
| flavin-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30527/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | Flavin is a derivative of the dimethylisoalloxazine skeleton substituted at position 10; the source supplies an R-group drawing rather than one fixed molecular identity. |
| nucleotide-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/36981/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | Flavin nucleotide has null definition, formula and default structure in this response, with nucleotide as its structural parent. Its lack of a fixed molecule is compatible with class scope. |
| specific-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47885/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | The dinucleotide source class has a generic R-group formula and no prose definition or default structure; its parent is nucleotide. |
| prosthetic-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | Prosthetic group is a tightly bound nonpolypeptide unit involved in biological activity, under cofactor; the role does not identify a molecular redox state. |
| oxidized-member | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16238/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | CHEBI:16238 is neutral oxidized FAD, C27H33N9O15P2, with specified D-ribityl/ribose stereochemistry, two phosphates and an imide N3-H. It has CHEBI:24040 as parent and direct cofactor/prosthetic roles. |
| reduced-member | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17877/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | CHEBI:17877 is neutral FADH2, C27H35N9O15P2, with the reduced flavin connectivity and the same specified sugar-chain stereochemistry. Its prose definition is null; its direct parent is CHEBI:24040. This is a redox-related subclass, not a conjugate-base substitute for the oxidized member. |
| radical-member | https://www.ebi.ac.uk/chebi/backend/api/public/compound/30788/; Exact identifier, names, actual definition field, formula/charge, structure and complete source relations | supports | CHEBI:30788 is the FADH semiquinone radical, with formula C27H34N9O15P2, charge 0, a radical site in its drawing and parent CHEBI:24040. No prose definition is supplied. |
| flavin-enzyme | https://iubmb.qmul.ac.uk/enzyme/EC1/1/3/4.html; Complete enzyme entry: reaction, comments and references; original reference articles not inspected | supports | The complete IUBMB EC 1.1.3.4 entry identifies glucose oxidase as an FAD flavoprotein and supplies its glucose/oxygen reaction. This is positive enzyme context, not evidence that every FAD derivative or free protonation state is interchangeable. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml; Executed 2026-10-21T12:13:06Z through 2026-10-21T12:13:07Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/ferroheme-c-2-chebi61717.yaml data/traits/function/cofactor_requirement/chebi/ferroheme-c-chebi60562.yaml data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml data/traits/function/cofactor_requirement/chebi/flavin-mononucleotide-chebi24041.yaml data/traits/function/cofactor_requirement/chebi/fmn-3-chebi58210.yaml data/traits/function/cofactor_requirement/chebi/fmn-chebi17621.yaml data/traits/function/cofactor_requirement/chebi/fmnh2-2-chebi57618.yaml data/traits/function/cofactor_requirement/chebi/fmnh2-chebi16048.yaml data/traits/function/cofactor_requirement/chebi/folic-acid-chebi27470.yaml data/traits/function/cofactor_requirement/chebi/gd-chebi33376.yaml; Executed 2026-10-21T12:13:03Z through 2026-10-21T12:14:24Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml; Executed 2026-10-21T12:13:07Z through 2026-10-21T12:13:07Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:14:24Z through 2026-10-21T12:14:24Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The short definition is a recognizable synthesized requirement wrapper; the current source has no prose definition to append. Incoming modified descendants indicate breadth, but this review does not separately certify every descendant or upstream chemical-taxonomy edge. External comparisons are not reviews of local sibling records. Enzyme authority references were not independently read as original articles.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T121753Z-flavin-adenine-dinucleotide-chebi24040
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires flavin adenine dinucleotide
started_at: '2026-10-21T12:12:39Z'
finished_at: '2026-10-21T12:17:53Z'
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
summary: The broad FAD chemical class is supported, distinct from exact oxidized,
  reduced and radical forms. One confirmed major finding concerns chemical-class/protein-requirement
  equivalence. Null fixed chemical fields are appropriate class context; positive
  enzyme evidence does not establish universal member interchangeability.
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
  - path: data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
    sha256: fa74faa7325621b77b1654bab61aca9e88395ff15b8eadbafa8a3fa8bb66e9c6
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
  selection: Path-order position 3 in batch 022. Fresh main inventory has 429359 records;
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
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df)
    covers 208 record paths, leaving 429151 before this batch. 22 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
targets:
- kind: generated
  label: requires flavin adenine dinucleotide
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_24040
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/ferroheme-c-2-chebi61717.yaml
    data/traits/function/cofactor_requirement/chebi/ferroheme-c-chebi60562.yaml data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
    data/traits/function/cofactor_requirement/chebi/flavin-mononucleotide-chebi24041.yaml
    data/traits/function/cofactor_requirement/chebi/fmn-3-chebi58210.yaml data/traits/function/cofactor_requirement/chebi/fmn-chebi17621.yaml
    data/traits/function/cofactor_requirement/chebi/fmnh2-2-chebi57618.yaml data/traits/function/cofactor_requirement/chebi/fmnh2-chebi16048.yaml
    data/traits/function/cofactor_requirement/chebi/folic-acid-chebi27470.yaml data/traits/function/cofactor_requirement/chebi/gd-chebi33376.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve the broad CHEBI:24040 class with direct cofactor
    role and actual null definition/chemical fields. Structural parents and distinct
    molecular subclasses were inspected, alongside the bounded enzyme authority.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
  - flavin-parent
  - nucleotide-parent
  - specific-parent
  - prosthetic-role
  - oxidized-member
  - reduced-member
  - radical-member
  - flavin-enzyme
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:12:39Z'
  snapshot_sha256: fa74faa7325621b77b1654bab61aca9e88395ff15b8eadbafa8a3fa8bb66e9c6
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
  accessed_at: '2026-10-21T12:12:39Z'
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
  accessed_at: '2026-10-21T12:12:39Z'
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
  accessed_at: '2026-10-21T12:12:39Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:12:39Z'
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
  summary: The official ChEBI Introduction and Licensing sections establish chemical-entity/role
    scope and CC BY 4.0 licensing. They do not equate a chemical with a synthesized
    protein requirement.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata identifies ChEBI version 256, loaded 2026-10-16.
    The original access timestamp and digest are retained; neither the live backend
    release nor the original seed release is established by this metadata.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:24040
  accessed_at: '2026-10-21T12:13:26.466165Z'
  snapshot_sha256: d90389f623734ef9551f4f2ef87350594fa33ec417a57a918700c5d34e791834
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:24040 as nonobsolete; actual names, description and
    available chemical annotations were inspected. Empty fields are retained as empty
    rather than treated as a fixed chemical formula.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24040/
  accessed_at: '2026-10-21T12:13:25.716168Z'
  snapshot_sha256: d3fc7f127e08f77a653da5c722af0862a8bc79f343662fb42f73c23856422309
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: CHEBI:24040 is the broad flavin adenine dinucleotide chemical class. The
    current definition, chemical_data and default_structure are null and aliases are
    empty. It directly has cofactor role and flavin, flavin-nucleotide and dinucleotide
    parents. Incoming subclasses include oxidized FAD, reduced FADH2, semiquinone
    and modified flavins; the broad class is not an exact synonym for one oxidation,
    protonation or derivative state.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: Cofactor is a biochemical role for an organic molecule or ion required
    by an enzyme for activity, under biochemical role CHEBI:52206. It is not itself
    a protein-requirement class.
- evidence_id: flavin-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30527/
  accessed_at: '2026-10-21T12:14:11.756891Z'
  snapshot_sha256: a9190b6419290dfa84513507eeab2a11b503c925af26bef154d25dd67de28bbf
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: Flavin is a derivative of the dimethylisoalloxazine skeleton substituted
    at position 10; the source supplies an R-group drawing rather than one fixed molecular
    identity.
- evidence_id: nucleotide-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/36981/
  accessed_at: '2026-10-21T12:14:11.756850Z'
  snapshot_sha256: 5213713ff9fa0b806be5c2e58dabeb98125308a3598f7b618597ef2e8da69c8c
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: Flavin nucleotide has null definition, formula and default structure in
    this response, with nucleotide as its structural parent. Its lack of a fixed molecule
    is compatible with class scope.
- evidence_id: specific-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47885/
  accessed_at: '2026-10-21T12:14:11.757937Z'
  snapshot_sha256: 91ecc83aef80dfd0215e719acb3a8ec4fe6f602364babef10b3119ccb73ed8ce
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: The dinucleotide source class has a generic R-group formula and no prose
    definition or default structure; its parent is nucleotide.
- evidence_id: prosthetic-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:10:09.154369Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: Prosthetic group is a tightly bound nonpolypeptide unit involved in biological
    activity, under cofactor; the role does not identify a molecular redox state.
- evidence_id: oxidized-member
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16238/
  accessed_at: '2026-10-21T11:56:55.388503Z'
  snapshot_sha256: 5d9d0e9682c43ecab665d35f0c55bba573c46e823816a12b5aa6f8c11dd90bc3
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: CHEBI:16238 is neutral oxidized FAD, C27H33N9O15P2, with specified D-ribityl/ribose
    stereochemistry, two phosphates and an imide N3-H. It has CHEBI:24040 as parent
    and direct cofactor/prosthetic roles.
- evidence_id: reduced-member
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17877/
  accessed_at: '2026-10-21T12:14:12.408333Z'
  snapshot_sha256: 3b7c983bb35eda35184f6ffe54674511b6fe990ece5fdb2c43626b1b67037d52
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: CHEBI:17877 is neutral FADH2, C27H35N9O15P2, with the reduced flavin connectivity
    and the same specified sugar-chain stereochemistry. Its prose definition is null;
    its direct parent is CHEBI:24040. This is a redox-related subclass, not a conjugate-base
    substitute for the oxidized member.
- evidence_id: radical-member
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/30788/
  accessed_at: '2026-10-21T12:14:12.494965Z'
  snapshot_sha256: b46127ea03181127fc8ca74b507f2a8147256a4062cb6955d104f6413341b529
  support: supports
  locator: Exact identifier, names, actual definition field, formula/charge, structure
    and complete source relations
  summary: CHEBI:30788 is the FADH semiquinone radical, with formula C27H34N9O15P2,
    charge 0, a radical site in its drawing and parent CHEBI:24040. No prose definition
    is supplied.
- evidence_id: flavin-enzyme
  kind: authority
  reference: https://iubmb.qmul.ac.uk/enzyme/EC1/1/3/4.html
  accessed_at: '2026-10-21T11:37:46.844173Z'
  snapshot_sha256: 93ae647b2c8a0e18717f705f9dba5cec19dfa627fb2c2aa3816325b7d877c8a8
  support: supports
  locator: 'Complete enzyme entry: reaction, comments and references; original reference
    articles not inspected'
  summary: The complete IUBMB EC 1.1.3.4 entry identifies glucose oxidase as an FAD
    flavoprotein and supplies its glucose/oxygen reaction. This is positive enzyme
    context, not evidence that every FAD derivative or free protonation state is interchangeable.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  locator: Executed 2026-10-21T12:13:06Z through 2026-10-21T12:13:07Z; exit 0
  accessed_at: '2026-10-21T12:13:07Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/ferroheme-c-2-chebi61717.yaml
    data/traits/function/cofactor_requirement/chebi/ferroheme-c-chebi60562.yaml data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
    data/traits/function/cofactor_requirement/chebi/flavin-mononucleotide-chebi24041.yaml
    data/traits/function/cofactor_requirement/chebi/fmn-3-chebi58210.yaml data/traits/function/cofactor_requirement/chebi/fmn-chebi17621.yaml
    data/traits/function/cofactor_requirement/chebi/fmnh2-2-chebi57618.yaml data/traits/function/cofactor_requirement/chebi/fmnh2-chebi16048.yaml
    data/traits/function/cofactor_requirement/chebi/folic-acid-chebi27470.yaml data/traits/function/cofactor_requirement/chebi/gd-chebi33376.yaml
  locator: Executed 2026-10-21T12:13:03Z through 2026-10-21T12:14:24Z; exit 0
  accessed_at: '2026-10-21T12:14:24Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
  locator: Executed 2026-10-21T12:13:07Z through 2026-10-21T12:13:07Z; exit 0
  accessed_at: '2026-10-21T12:13:07Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:14:24Z through 2026-10-21T12:14:24Z; exit 0
  accessed_at: '2026-10-21T12:14:24Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: provenance
  outcome: supported
  summary: The captured ChEBI seeder selects role descendants or chemical entities
    with a cofactor-related role, synthesizes the requirement wrapper and emits the
    chemical xref. The current chemical identity, source attribution and licence resolve;
    the exact original seed release remains unassigned.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - release
  topic: Maintained ChEBI source transformation and release limits
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-5
- area: identity
  outcome: supported
  summary: The target denotes a reusable requirement candidate for the broad source
    chemical class. The inspected oxidized, reduced and semiquinone subclasses show
    why no single formula, charge or structure belongs to the whole class. Null source
    prose does not by itself make the concise requirement definition defective, and
    it does not license treating the generic class as the exact neutral member.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - oxidized-member
  - reduced-member
  - radical-member
  topic: Broad flavin chemical class and distinct molecular states
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The inspected enzyme authority provides a concrete FAD glucose-oxidase
    context. This supports biological relevance while preserving the tested class/member
    and evidence scope.
  evidence_ids:
  - flavin-enzyme
  topic: Positive flavin enzyme context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: Source chemical-role membership and positive enzyme contexts do not establish
    that a protein accepts every redox form or modified descendant. Any exact chemical
    participant or protein example needs activity-relative evidence and the intended
    member/state. A broad candidate class can remain useful without inventing a fixed
    formula, a mandatory optional example or universal interchangeability.
  evidence_ids:
  - record
  - schema
  - chemical
  - oxidized-member
  - reduced-member
  - radical-member
  - flavin-enzyme
  topic: Generic chemical-class requirement and exact-state qualification
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: Direct cofactor role explains the local ChEBI-role seeder and broader cofactor-requirement
    parent. Source chemical ancestry is distinct from local protein-trait equivalence;
    the review preserves that hierarchy without certifying every upstream classification
    or local parent.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical
  - cofactor-role
  - flavin-parent
  - nucleotide-parent
  - specific-parent
  topic: Direct cofactor role and retained class hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The source chemical and the local protein functional requirement are different
    entity types. Correct chemistry, authentic source roles and bounded biological
    context do not establish true own-source equivalence.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-24040.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:24040 denotes a broad chemical class, whereas the local record
    denotes the functional requirement of a protein. Authentic cofactor role and positive
    enzyme evidence cannot make the chemical class itself equivalent to the requiring
    protein class.
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
  normalization_reason: The candidate identity remains recognizable, but chemical
    entities/classes and protein requirements have different denotations. This is
    a major grounding defect even where biological relevance is supported; optional
    representation absence is not the finding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
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
    equality from xrefs while preserving source grounding and provenance. Preserve
    the broad chemical-class scope unless a curator explicitly narrows it with evidence.
    Do not silently replace it by the exact oxidized member, collapse reduced/radical/modified
    descendants or assert that each protein accepts every class member. Adjudicate
    the activity-relative role before adding any COFACTOR chemical_participant. If
    that role cannot be supported, retain provenance and explicit uncertainty without
    inventing a participant. Do not relocate the equality to mapped_xrefs or promote
    a protein example or native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_24040
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated xrefs no longer equate the chemical entity or chemical class with
    the requirement trait; exact supported scope and provenance remain auditable.
    Any participant has an adjudicated activity-relative role, and optional participant
    absence is not itself a defect.
  - Run just validate data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/flavin-adenine-dinucleotide-chebi24040.yaml
    after the scoped repair.
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
- The short definition is a recognizable synthesized requirement wrapper; the current
  source has no prose definition to append. Incoming modified descendants indicate
  breadth, but this review does not separately certify every descendant or upstream
  chemical-taxonomy edge. External comparisons are not reviews of local sibling records.
  Enzyme authority references were not independently read as original articles.
tags:
- unreviewed-path-order
- batch-022
- chebi-cofactor
```
