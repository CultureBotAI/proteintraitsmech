# Review of requires coenzyme A

- Review: 20261021T103339Z-coenzyme-a-chebi15346
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:24:33Z
- Finished UTC: 2026-10-21T10:33:39Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Coenzyme A chemical identity and source coenzyme-role context are supported. One confirmed major finding concerns chemical-to-protein-trait equivalence and one minor finding concerns pantothenate spelling. Exact neutral-state non-substrate protein dependence remains unqualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 015. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f) covers 138 record paths, leaving 429221 before this batch. 15 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml | generated | requires coenzyme A |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15346 | CHEBI:15346 resolves and is nonobsolete in OLS. Its actual chemical identity, stated role, relevant structural parents and conjugate comparison were inspected. The local parent and cofactor ancestor were captured and read. Successful resolution does not establish protein requirement or equivalence. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The local label denotes a proposed reusable requirement for coenzyme A; CHEBI:15346 coherently identifies the molecular referent, not an equivalent protein-requirement class.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The ChEBI data licence is supported. The source supplies chemical descriptions and role assertions; the maintained role seeder synthesizes the protein-requirement wrapper. Current backend and OLS responses do not identify the original seed release.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

CHEBI:15346 in xrefs denotes a molecular entity while the target denotes a protein functional requirement. The schema requires true own-source equivalence; a chemical association is a different predicate.

### Coenzyme A structure and conjugate state

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

CHEBI:15346 is C21H36N7O16P3S, net0, with a free terminal thiol, pantothenate-derived scaffold and phosphorylated adenosine joined through a diphosphate. The encoded nucleotide stereochemistry and (3R) pantothenate-side stereocentre are specific. Its tetraanion loses four phosphate protons while retaining the thiol, so the short CoA/CoASH names do not establish neutral/tetraanion interchangeability.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The direct coenzyme role explains the captured coenzyme-requirement parent and broader cofactor ancestor. Structural-parent and functional-parent relations are chemical relationships, not equivalent protein classes. Alternative metabolite/drug roles neither qualify nor refute the proposed requirement.

### Pantothenate spelling in chemical background

nomenclature: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The copied panthothenate spelling conflicts with the authoritative pantothenate/pantothenic-acid names and the primary biosynthesis terminology. This is a bounded spelling error; chemical identity remains recoverable from the ID, structure and other nomenclature.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15346.

The source coenzyme role is broader evidence than the local non-substrate requirement category. The inspected experiment concerns CoA biosynthesis, not a protein requiring exact neutral CoA. A context-specific substrate/product/cofactor distinction and exact chemical-state evidence remain necessary; alternate roles are not proof that all non-substrate cofactor use is absent.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-15346.chemical-entity-equivalence.

The local requires-coenzyme-A class denotes a protein functional requirement, while CHEBI:15346 denotes the neutral thiol form of CoA. The xrefs slot asserts equality between these different denotations.

### F2: Chemical background misspells pantothenate

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-15346.pantothenate-spelling.

The target and current upstream definition use panthothenate. The official pantothenate/pantothenic-acid entries and the inspected biosynthesis paper use pantothenate. The extra h is a non-blocking nomenclature typo, not evidence for a different CoA identity.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:15346 from trait-equivalence xrefs and retain its exact molecular identity through typed chemical grounding. Before emitting chemical_participants with role COFACTOR for a retained proposed requirement, adjudicate its non-substrate scope against the category definition; source roles and the inspected biological contexts alone do not qualify a protein. Preserve source attribution and candidate status. Do not use mapped_xrefs for this own-source association or silently substitute a conjugate, complex or reaction product.

- The regenerated target preserves the exact CHEBI:15346 chemical referent without asserting chemical-to-protein-trait equality.
- Resolve non-substrate requirement scope without treating CoA biosynthesis as positive cofactor evidence. Retain neutral-versus-tetraanion, free-thiol-versus-acylated and stereochemical distinctions; no physiological population is asserted.
- Any retained COFACTOR participant refers to the actual molecular entity and the intended candidate requirement; substrate, product and transport evidence is not silently promoted into non-substrate requirement evidence. No protein example is qualified.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml. These future curation checks do not imply the present finding has been fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

### A2

Correct panthothenate to pantothenate in maintained source-text handling or an explicit curated override, retain raw source provenance, and regenerate the scoped record rather than hand-editing emitted YAML.

- The regenerated definition uses pantothenate without changing the CoA identity, stereochemistry, charge scope or source attribution.
- A focused source-transform fixture preserves the correction and raw upstream text remains distinguishable.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml. These future curation checks do not imply the present finding has been fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The official Introduction describes chemical entities and the ontology; Licensing makes website data available under CC BY 4.0. This supports source-data licensing, not the locally synthesized protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the comparison ontology version, not a release assignment to live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_15346; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:15346 to nonobsolete coenzyme A. Actual labels, description fields and synonyms were inspected. The role/molecular denotation is assessed separately from the local protein requirement. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15346/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response supplies the actual name, definition field, chemical data, structure, aliases and outgoing relations. Its direct source role provides candidate context rather than a qualified protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing relations | supports | The cofactor source role describes an organic molecule or ion required by an enzyme; its parent is biochemical role. This source assertion is distinct from a protein requirement class. |
| specific-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; definition, chemical_data, default_structure and outgoing relations | supports | The coenzyme role describes a low-molecular-weight non-protein organic compound acting as a dissociable donor or acceptor of groups/electrons, and is-a cofactor. It is a role class, not a specific molecular structure. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | Complete captured broader cofactor-requirement ancestor inspected. Its requirement wrapper and source-role xref are distinguished; this review does not certify that ancestor. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/57287/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The tetraanion is C21H32N7O16P3S, net −4, with the same CoA scaffold; it differs by phosphate protonation, not loss of the thiol proton. Its short name does not make it equivalent to neutral CHEBI:15346. |
| functional-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/44672/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The functional-parent entry is 3-prime-phosphate-adenosine-5-prime-diphosphate, C10H16N5O13P3, net0. It supports the phosphorylated nucleotide substructure; its separate pharmacological assertions are not imported. |
| pantothenate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29032/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The official entry is (R)-pantothenate, C9H16NO5, net−1, conjugate base of (R)-pantothenic acid. Its actual chemical name supports the spelling pantothenate. |
| pantothenic-acid | https://www.ebi.ac.uk/chebi/backend/api/public/compound/46905/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The official (R)-pantothenic-acid entry is C9H17NO5, net0, with the stereochemical pantothenate scaffold and reciprocal conjugacy; this does not substitute a free vitamin for CoA. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/140325/; name, definition and outgoing relations | supports | The source structural parent resolves and its definition/outgoing relations were inspected; these chemical classes do not directly replace the protein requirement parent. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/29256/; name, definition and outgoing relations | supports | The source structural parent resolves and its definition/outgoing relations were inspected; these chemical classes do not directly replace the protein requirement parent. |
| chemical-parent-3 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/231540/; name, definition and outgoing relations | supports | The source structural parent resolves and its definition/outgoing relations were inspected; these chemical classes do not directly replace the protein requirement parent. |
| chemical-parent-4 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/20706/; name, definition and outgoing relations | supports | The source structural parent resolves and its definition/outgoing relations were inspected; these chemical classes do not directly replace the protein requirement parent. |
| other-role-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76971/; name, definition and outgoing relations | supports | The separately asserted metabolite/pharmacological role resolves. It is retained as source context, without extrapolating therapeutic efficacy or protein dependence. |
| other-role-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35610/; name, definition and outgoing relations | supports | The separately asserted metabolite/pharmacological role resolves. It is retained as source context, without extrapolating therapeutic efficacy or protein dependence. |
| other-role-3 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/75771/; name, definition and outgoing relations | supports | The separately asserted metabolite/pharmacological role resolves. It is retained as source context, without extrapolating therapeutic efficacy or protein dependence. |
| primary-biosynthesis | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11923312%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID11923312; DOI10.1074/jbc.M201708200; complete indexed abstract | supports | The complete primary abstract reports reconstitution of the human CoA biosynthetic pathway from phosphopantothenate with purified recombinant enzymes. It corroborates pantothenic-acid/pantothenate terminology and a product-biosynthesis context; it does not qualify those enzymes as requiring CoA as a non-substrate cofactor. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; Executed 2026-10-21T10:26:48Z through 2026-10-21T10:26:49Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-3-chebi84724.yaml data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-b-chebi28890.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-a-chebi62784.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-g-chebi62786.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-3-chebi59543.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-chebi59536.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Executed 2026-10-21T10:25:03Z through 2026-10-21T10:26:36Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml; Executed 2026-10-21T10:26:49Z through 2026-10-21T10:26:49Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:26:36Z through 2026-10-21T10:26:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMID11923312 was inspected at complete indexed-abstract level. Its biosynthetic pathway reconstruction is not qualification of a CoA-requiring protein, and its broad universality wording is not newly asserted by this review. No exact physiological protonation distribution or universal non-substrate role is inferred.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T103339Z-coenzyme-a-chebi15346
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires coenzyme A
started_at: '2026-10-21T10:24:33Z'
finished_at: '2026-10-21T10:33:39Z'
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
summary: Coenzyme A chemical identity and source coenzyme-role context are supported.
  One confirmed major finding concerns chemical-to-protein-trait equivalence and one
  minor finding concerns pantothenate spelling. Exact neutral-state non-substrate
  protein dependence remains unqualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
    sha256: 25584038516c8df53a5484d5f9d06bd0ebf68cbf23c9c1dfe1a0375035eb702a
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
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
  selection: Path-order position 3 in batch 015. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f) covers 138 record paths,
    leaving 429221 before this batch. 15 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
targets:
- kind: generated
  label: requires coenzyme A
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_15346
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-3-chebi84724.yaml
    data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-b-chebi28890.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f390-a-chebi62784.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f390-g-chebi62786.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-3-chebi59543.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-chebi59536.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:15346 resolves and is nonobsolete in OLS. Its actual chemical identity,
    stated role, relevant structural parents and conjugate comparison were inspected.
    The local parent and cofactor ancestor were captured and read. Successful resolution
    does not establish protein requirement or equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  evidence_ids:
  - chemical
  - chemical-role
  - specific-role
  - cofactor-role
  - licence
  - release
  - conjugate
  - functional-parent
  - pantothenate
  - pantothenic-acid
  - primary-biosynthesis
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:24:33Z'
  snapshot_sha256: 25584038516c8df53a5484d5f9d06bd0ebf68cbf23c9c1dfe1a0375035eb702a
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
  accessed_at: '2026-10-21T10:24:33Z'
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
  accessed_at: '2026-10-21T10:24:33Z'
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
  accessed_at: '2026-10-21T10:24:33Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:24:33Z'
  snapshot_sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
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
  summary: The official Introduction describes chemical entities and the ontology;
    Licensing makes website data available under CC BY 4.0. This supports source-data
    licensing, not the locally synthesized protein requirement.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the comparison
    ontology version, not a release assignment to live backend responses or the original
    seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_15346
  accessed_at: '2026-10-21T10:25:31.938315Z'
  snapshot_sha256: 80c080833d148d34eb9290be639f8b85000e1fc2c5cd1b0ab7a222948a8c3571
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:15346 to nonobsolete coenzyme A. Actual labels, description
    fields and synonyms were inspected. The role/molecular denotation is assessed
    separately from the local protein requirement.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15346/
  accessed_at: '2026-10-21T10:25:31.468908Z'
  snapshot_sha256: 2209650a8f7d47f00ecce5d2f25e8630f895cb4bd0a95e1a3561b61e26227f7a
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The complete official response supplies the actual name, definition field,
    chemical data, structure, aliases and outgoing relations. Its direct source role
    provides candidate context rather than a qualified protein requirement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and outgoing relations
  summary: The cofactor source role describes an organic molecule or ion required
    by an enzyme; its parent is biochemical role. This source assertion is distinct
    from a protein requirement class.
- evidence_id: specific-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T10:10:09.158129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: definition, chemical_data, default_structure and outgoing relations
  summary: The coenzyme role describes a low-molecular-weight non-protein organic
    compound acting as a dissociable donor or acceptor of groups/electrons, and is-a
    cofactor. It is a role class, not a specific molecular structure.
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T10:24:33Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: Complete captured broader cofactor-requirement ancestor inspected. Its
    requirement wrapper and source-role xref are distinguished; this review does not
    certify that ancestor.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/57287/
  accessed_at: '2026-10-21T10:26:09.502574Z'
  snapshot_sha256: 7cede4652a877f78adbe9254fa4a4047470cca8b037059c87914c788b5ecb5de
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The tetraanion is C21H32N7O16P3S, net −4, with the same CoA scaffold; it
    differs by phosphate protonation, not loss of the thiol proton. Its short name
    does not make it equivalent to neutral CHEBI:15346.
- evidence_id: functional-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/44672/
  accessed_at: '2026-10-21T10:26:07.930399Z'
  snapshot_sha256: 92704b1bc9c90023bb1614f7cb7f33b8aa4d56139945822a96bc5cea09fea5d1
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The functional-parent entry is 3-prime-phosphate-adenosine-5-prime-diphosphate,
    C10H16N5O13P3, net0. It supports the phosphorylated nucleotide substructure; its
    separate pharmacological assertions are not imported.
- evidence_id: pantothenate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29032/
  accessed_at: '2026-10-21T10:26:10.056976Z'
  snapshot_sha256: 51063c24759ba8cbb398841becae3bed19d36ba26f7ac161690a3245eb4a1513
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The official entry is (R)-pantothenate, C9H16NO5, net−1, conjugate base
    of (R)-pantothenic acid. Its actual chemical name supports the spelling pantothenate.
- evidence_id: pantothenic-acid
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/46905/
  accessed_at: '2026-10-21T10:26:10.154054Z'
  snapshot_sha256: 00feef1a79f485c42370fc113aaaf204bdf519e0027d58c06f520f3975890783
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The official (R)-pantothenic-acid entry is C9H17NO5, net0, with the stereochemical
    pantothenate scaffold and reciprocal conjugacy; this does not substitute a free
    vitamin for CoA.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/140325/
  accessed_at: '2026-10-21T10:26:08.849631Z'
  snapshot_sha256: 1092fd35107a93944e58088fa7e42b817c9889e6a027e88226ce3273beaebf7b
  support: supports
  locator: name, definition and outgoing relations
  summary: The source structural parent resolves and its definition/outgoing relations
    were inspected; these chemical classes do not directly replace the protein requirement
    parent.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/29256/
  accessed_at: '2026-10-21T10:26:08.644665Z'
  snapshot_sha256: 215dd317988cec50435f7d122262b435d514bd2ccee315c3abdbf137c6d8a5a5
  support: supports
  locator: name, definition and outgoing relations
  summary: The source structural parent resolves and its definition/outgoing relations
    were inspected; these chemical classes do not directly replace the protein requirement
    parent.
- evidence_id: chemical-parent-3
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/231540/
  accessed_at: '2026-10-21T10:26:09.315447Z'
  snapshot_sha256: 40bef2720b3624e4cd45a777620edaef392b7b1180bd8214300e9644d4e1d61e
  support: supports
  locator: name, definition and outgoing relations
  summary: The source structural parent resolves and its definition/outgoing relations
    were inspected; these chemical classes do not directly replace the protein requirement
    parent.
- evidence_id: chemical-parent-4
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/20706/
  accessed_at: '2026-10-21T10:26:09.365583Z'
  snapshot_sha256: 2cc546b4ec59039ce266046e9c88c789fc54f65fd1850b025011a0cc5929bd0e
  support: supports
  locator: name, definition and outgoing relations
  summary: The source structural parent resolves and its definition/outgoing relations
    were inspected; these chemical classes do not directly replace the protein requirement
    parent.
- evidence_id: other-role-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76971/
  accessed_at: '2026-10-21T10:26:08.706746Z'
  snapshot_sha256: 7fc404f615d575d34db7d66cd3ab536694e7ae482367720c36a5002a09d3171d
  support: supports
  locator: name, definition and outgoing relations
  summary: The separately asserted metabolite/pharmacological role resolves. It is
    retained as source context, without extrapolating therapeutic efficacy or protein
    dependence.
- evidence_id: other-role-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35610/
  accessed_at: '2026-10-21T10:26:09.182049Z'
  snapshot_sha256: 4b8e6689294e3b82ec67135dece4ba2825a0c5339699881260f5e0564df0cc82
  support: supports
  locator: name, definition and outgoing relations
  summary: The separately asserted metabolite/pharmacological role resolves. It is
    retained as source context, without extrapolating therapeutic efficacy or protein
    dependence.
- evidence_id: other-role-3
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/75771/
  accessed_at: '2026-10-21T10:26:09.770625Z'
  snapshot_sha256: 578a9c9ac65cc6bcc50819277430318680718f95342e955c7eabfe89cbafad70
  support: supports
  locator: name, definition and outgoing relations
  summary: The separately asserted metabolite/pharmacological role resolves. It is
    retained as source context, without extrapolating therapeutic efficacy or protein
    dependence.
- evidence_id: primary-biosynthesis
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11923312%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:10.472404Z'
  snapshot_sha256: 39127f075b9a1963885bb2c1052a83f95dda52369ddd46682928a8d07b12592b
  support: supports
  locator: PMID11923312; DOI10.1074/jbc.M201708200; complete indexed abstract
  summary: The complete primary abstract reports reconstitution of the human CoA biosynthetic
    pathway from phosphopantothenate with purified recombinant enzymes. It corroborates
    pantothenic-acid/pantothenate terminology and a product-biosynthesis context;
    it does not qualify those enzymes as requiring CoA as a non-substrate cofactor.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  locator: Executed 2026-10-21T10:26:48Z through 2026-10-21T10:26:49Z; exit 0
  accessed_at: '2026-10-21T10:26:49Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-3-chebi84724.yaml
    data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-b-chebi28890.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f390-a-chebi62784.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f390-g-chebi62786.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-3-chebi59543.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-chebi59536.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  locator: Executed 2026-10-21T10:25:03Z through 2026-10-21T10:26:36Z; exit 0
  accessed_at: '2026-10-21T10:26:36Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml
  locator: Executed 2026-10-21T10:26:49Z through 2026-10-21T10:26:49Z; exit 0
  accessed_at: '2026-10-21T10:26:49Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T10:26:36Z through 2026-10-21T10:26:38Z; exit 0
  accessed_at: '2026-10-21T10:26:38Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The local label denotes a proposed reusable requirement for coenzyme A;
    CHEBI:15346 coherently identifies the molecular referent, not an equivalent protein-requirement
    class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: The ChEBI data licence is supported. The source supplies chemical descriptions
    and role assertions; the maintained role seeder synthesizes the protein-requirement
    wrapper. Current backend and OLS responses do not identify the original seed release.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: grounding
  outcome: concern
  summary: CHEBI:15346 in xrefs denotes a molecular entity while the target denotes
    a protein functional requirement. The schema requires true own-source equivalence;
    a chemical association is a different predicate.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-7
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: CHEBI:15346 is C21H36N7O16P3S, net0, with a free terminal thiol, pantothenate-derived
    scaffold and phosphorylated adenosine joined through a diphosphate. The encoded
    nucleotide stereochemistry and (3R) pantothenate-side stereocentre are specific.
    Its tetraanion loses four phosphate protons while retaining the thiol, so the
    short CoA/CoASH names do not establish neutral/tetraanion interchangeability.
  evidence_ids:
  - chemical
  - chemical-role
  - functional-parent
  - conjugate
  - pantothenate
  - pantothenic-acid
  topic: Coenzyme A structure and conjugate state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct coenzyme role explains the captured coenzyme-requirement parent
    and broader cofactor ancestor. Structural-parent and functional-parent relations
    are chemical relationships, not equivalent protein classes. Alternative metabolite/drug
    roles neither qualify nor refute the proposed requirement.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - local-ancestor
  - specific-role
  - cofactor-role
  - chemical-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-9
  topic: Chemical-role and protein-trait hierarchy
- area: nomenclature
  outcome: concern
  summary: The copied panthothenate spelling conflicts with the authoritative pantothenate/pantothenic-acid
    names and the primary biosynthesis terminology. This is a bounded spelling error;
    chemical identity remains recoverable from the ID, structure and other nomenclature.
  evidence_ids:
  - record
  - chemical-role
  - pantothenate
  - pantothenic-acid
  - primary-biosynthesis
  topic: Pantothenate spelling in chemical background
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-10
- area: representation
  outcome: unknown
  summary: The source coenzyme role is broader evidence than the local non-substrate
    requirement category. The inspected experiment concerns CoA biosynthesis, not
    a protein requiring exact neutral CoA. A context-specific substrate/product/cofactor
    distinction and exact chemical-state evidence remain necessary; alternate roles
    are not proof that all non-substrate cofactor use is absent.
  evidence_ids:
  - record
  - schema
  - specific-role
  - chemical-role
  - primary-biosynthesis
  - conjugate
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-15346.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-coenzyme-A class denotes a protein functional requirement,
    while CHEBI:15346 denotes the neutral thiol form of CoA. The xrefs slot asserts
    equality between these different denotations.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The source molecular entity and its protein-requirement class
    have different denotations; the intended candidate identity remains recoverable
    through correctly typed grounding.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-15346.pantothenate-spelling
  category: consistency
  severity: minor
  title: Chemical background misspells pantothenate
  description: The target and current upstream definition use panthothenate. The official
    pantothenate/pantothenic-acid entries and the inspected biosynthesis paper use
    pantothenate. The extra h is a non-blocking nomenclature typo, not evidence for
    a different CoA identity.
  evidence_ids:
  - record
  - chemical-role
  - pantothenate
  - pantothenic-acid
  - primary-biosynthesis
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: A bounded spelling defect leaves the stable chemical identity
    intact.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:15346
    from trait-equivalence xrefs and retain its exact molecular identity through typed
    chemical grounding. Before emitting chemical_participants with role COFACTOR for
    a retained proposed requirement, adjudicate its non-substrate scope against the
    category definition; source roles and the inspected biological contexts alone
    do not qualify a protein. Preserve source attribution and candidate status. Do
    not use mapped_xrefs for this own-source association or silently substitute a
    conjugate, complex or reaction product.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves the exact CHEBI:15346 chemical referent without
    asserting chemical-to-protein-trait equality.
  - Resolve non-substrate requirement scope without treating CoA biosynthesis as positive
    cofactor evidence. Retain neutral-versus-tetraanion, free-thiol-versus-acylated
    and stereochemical distinctions; no physiological population is asserted.
  - Any retained COFACTOR participant refers to the actual molecular entity and the
    intended candidate requirement; substrate, product and transport evidence is not
    silently promoted into non-substrate requirement evidence. No protein example
    is qualified.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml.
    These future curation checks do not imply the present finding has been fixed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing target
    through an audited route. Run full-corpus just validate-all before merging record
    changes and save a fresh structured scientific review against changed bytes.
- action_id: A2
  description: Correct panthothenate to pantothenate in maintained source-text handling
    or an explicit curated override, retain raw source provenance, and regenerate
    the scoped record rather than hand-editing emitted YAML.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15346
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated definition uses pantothenate without changing the CoA identity,
    stereochemistry, charge scope or source attribution.
  - A focused source-transform fixture preserves the correction and raw upstream text
    remains distinguishable.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml.
    These future curation checks do not imply the present finding has been fixed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing target
    through an audited route. Run full-corpus just validate-all before merging record
    changes and save a fresh structured scientific review against changed bytes.
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
- PMID11923312 was inspected at complete indexed-abstract level. Its biosynthetic
  pathway reconstruction is not qualification of a CoA-requiring protein, and its
  broad universality wording is not newly asserted by this review. No exact physiological
  protonation distribution or universal non-substrate role is inferred.
tags:
- unreviewed-path-order
- batch-015
- chebi-cofactor
```
