# Review of requires dehydro-D-arabinono-1,4-lactone

- Review: 20261021T111505Z-dehydro-d-arabinono-1-4-lactone-chebi17803
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:07:30Z
- Finished UTC: 2026-10-21T11:15:05Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The neutral five-carbon (5R) enediol identity and local naming are supported. One confirmed major finding concerns chemical-to-protein-trait equivalence. Historical trivial-name ambiguity and conjugate-base population claims are bounded source context, not additional target defects.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 018. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9) covers 168 record paths, leaving 429191 before this batch. 18 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml | generated | requires dehydro-D-arabinono-1,4-lactone |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_17803 | CHEBI:17803 resolves and is nonobsolete. Exact chemical data, (5R)structure, source roles, gamma-lactone parent and monoanion conjugacy were inspected. The complete IUBMB entry and three primary abstracts were read; historical names were resolved by explicit structure/context rather than assumed C6 equivalence. The local cofactor parent was captured and read. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

The complete local YAML denotes a proposed reusable protein requirement for dehydro-D-arabinono-1,4-lactone. CHEBI:17803 identifies its chemical referent or chemical class, not an equivalent protein-requirement class.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

scripts/seed_chebi_cofactor.py owns the generated target: it selects source roles, synthesizes the requirement wrapper, appends chemical text and emits a chemical xref. CC BY 4.0 is supported by the official source. Current comparison snapshots do not identify the original seed release.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

The inspected source role relation explains selection of the captured local broader requirement parent. Chemical-role taxonomy is not automatically a protein-requirement hierarchy or true equivalence; this one-record review does not certify the parent.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

CHEBI:17803 in xrefs denotes a chemical entity/class, whereas the target denotes a protein functional requirement. The schema requires true own-source equivalence rather than a chemical association.

### Five-carbon enediol identity and (5R) stereochemistry

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

CHEBI:17803 is the neutral C5H6O5 (5R)-3,4-dihydroxy-5-(hydroxymethyl)furan-2(5H)-one, with an enediol double bond in its five-membered lactone. The local chemical definition and exact name agree with the official source and IUBMB glossary. The prefix dehydro is not used to invent a C6 dehydroascorbate identity or a further oxidized dicarbonyl structure.

### Historical erythroascorbic naming limits

nomenclature: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

The source lists D-erythroascorbic acid as a related synonym, while IUBMB flags historically erroneous D-erythroascorbate/C6 CAS usage. The primary abstracts use the historical trivial name; one explicitly supplies the five-carbon pentenono-lactone identity. The target does not import the ambiguous synonym or C6 CAS and remains precisely named, so no additional target alias defect is inferred.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_17803.

Direct source cofactor, antioxidant and fungal-metabolite roles explain candidate context. ALO product formation, oxidative-stress effects and fungal occurrence do not establish exact-neutral non-substrate protein dependence. Conjugate-base chemistry does not prove biological interchangeability, neutral-state predominance or absence of cofactor use.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-17803.chemical-entity-equivalence.

The local class denotes a protein requirement for dehydro-D-arabinono-1,4-lactone, whereas CHEBI:17803 denotes a specific neutral five-carbon enediol lactone. xrefs falsely equates the functional requirement and chemical.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:17803 from trait-equivalence xrefs and preserve the exact source identity through schema-compatible grounding. Preserve chemical-source provenance separately from the locally synthesized requirement. Before assigning a COFACTOR chemical_participant, adjudicate whether the intended activity-relative role satisfies the non-substrate requirement category; otherwise retain that uncertainty and use only a supported representation. Do not blindly move this own-source association to mapped_xrefs, infer a required protein from chemical role alone, or promote SEEDED status.

- The regenerated target preserves the intended CHEBI:17803 chemical scope without asserting equality to a protein requirement.
- Preserve the exact (5R) C5 neutral identity and distinguish its monoanion, the ALO substrate, C6 ascorbate names and oxidation products. Do not convert historical naming or antioxidant/growth effects into exact-state non-substrate protein qualification.
- Any typed participant has the supported activity-relative role and exact chemical scope; no unreviewed protein example, universal requirement or automatic status promotion is introduced.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml. These are future curation acceptance checks, not claims that the target has already changed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction defines its chemical entities and chemical classes. Licensing makes website data available under CC BY 4.0. This supports source licensing, not the locally synthesized protein-requirement claim. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Its original access timestamp is preserved. It is comparison-ontology metadata, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_17803; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:17803 to nonobsolete dehydro-D-arabinono-1,4-lactone. The actual definition, identifiers, aliases and chemical annotations were inspected; the source term denotes chemistry rather than a protein requirement. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17803/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The complete target chemical response was inspected: exact name, definition, formula/charge or R-group class representation, stereochemical encoding, aliases and incoming/outgoing relations. The source chemical role supplies candidate context and does not qualify a protein. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | ChEBI cofactor is a biochemical role for an organic molecule or ion required by an enzyme. The role is not a protein-requirement class. |
| lactone-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37581/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines a five-membered lactone ring. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58277/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The separate monoanion is C5H5O5, charge −1, explicitly conjugate base of 17803. Its pH 7.3 population assertion is source-only context and is not transferred to the neutral target or independently validated here. |
| antioxidant-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/22586/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The antioxidant role concerns opposing oxidation; it is not by itself protein cofactor qualification. |
| fungal-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76946/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The fungal-metabolite role concerns production during fungal metabolism, not exact-state protein dependence. |
| nomenclature-authority | https://iubmb.qmul.ac.uk/enzyme/EC1/1/3/37.html; EC1.1.3.37 reaction, glossary, comments and reference | supports | The complete official EC entry identifies the C5 (5R) enediol product with the same systematic structure as17803. It warns that the historical D-erythroascorbate name/C6 CAS usage was erroneous. It classifies ALO as an FAD flavoprotein; that does not identify its product as its cofactor. |
| alo-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7957197%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID7957197; DOI10.1111/j.1432-1033.1994.1073b.x; complete indexed abstract | supports | The complete primary abstract describes C. albicans ATCC 10231 D-arabinono-lactone oxidase purification and product biosynthesis, under the historical erythroascorbic name. The flavin evidence concerns the enzyme; the lactone product is not thereby an exact neutral cofactor required by that enzyme. |
| origin-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7612007%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID7612007; DOI10.1006/bbrc.1995.1956; complete indexed abstract | supports | The complete primary abstract explicitly identifies a D-glycero-pentenono-lactone under the trivial D-erythroascorbic name in S. sclerotiorum and examines isotope-labelled biosynthesis and possible oxalic-acid precursor context. It does not establish exact-neutral protein dependence. |
| antioxidant-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10094636%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID10094636; DOI10.1046/j.1365-2958.1998.01133.x; complete indexed abstract | supports | The complete primary abstract reports ALO1-dependent production and altered oxidative-stress sensitivity in S. cerevisiae. This supports bounded antioxidant/biosynthetic context, not a direct non-substrate requirement for neutral 17803 by every protein affected. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml; Executed 2026-10-21T11:10:51Z through 2026-10-21T11:10:52Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml; Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml; Executed 2026-10-21T11:10:52Z through 2026-10-21T11:10:52Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The three primary studies were inspected at complete indexed-abstract level. The neutral-versus-anion physiological population, exact-state binding and activity-relative non-substrate requirement were not established. The full set of other ChEBI bibliography links was not used as blanket evidence.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T111505Z-dehydro-d-arabinono-1-4-lactone-chebi17803
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires dehydro-D-arabinono-1,4-lactone
started_at: '2026-10-21T11:07:30Z'
finished_at: '2026-10-21T11:15:05Z'
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
summary: The neutral five-carbon (5R) enediol identity and local naming are supported.
  One confirmed major finding concerns chemical-to-protein-trait equivalence. Historical
  trivial-name ambiguity and conjugate-base population claims are bounded source context,
  not additional target defects.
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
  - path: data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
    sha256: 1726a95c64c5d7ea5f649aa1dced775fff060460d7fee0a787bb53df6e79de1a
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
  selection: Path-order position 2 in batch 018. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9)
    covers 168 record paths, leaving 429191 before this batch. 18 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
targets:
- kind: generated
  label: requires dehydro-D-arabinono-1,4-lactone
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_17803
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
    data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
    data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml
    data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml
    data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:17803 resolves and is nonobsolete. Exact chemical data, (5R)structure,
    source roles, gamma-lactone parent and monoanion conjugacy were inspected. The
    complete IUBMB entry and three primary abstracts were read; historical names were
    resolved by explicit structure/context rather than assumed C6 equivalence. The
    local cofactor parent was captured and read.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - lactone-parent
  - conjugate
  - antioxidant-role
  - fungal-role
  - nomenclature-authority
  - alo-primary
  - origin-primary
  - antioxidant-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:07:30Z'
  snapshot_sha256: 1726a95c64c5d7ea5f649aa1dced775fff060460d7fee0a787bb53df6e79de1a
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
  accessed_at: '2026-10-21T11:07:30Z'
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
  accessed_at: '2026-10-21T11:07:30Z'
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
  accessed_at: '2026-10-21T11:07:30Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:07:30Z'
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
  summary: The official ChEBI Introduction defines its chemical entities and chemical
    classes. Licensing makes website data available under CC BY 4.0. This supports
    source licensing, not the locally synthesized protein-requirement claim.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Its original access timestamp is preserved. It is comparison-ontology metadata,
    not a release assignment for live backend responses or the original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_17803
  accessed_at: '2026-10-21T11:07:59.477488Z'
  snapshot_sha256: c4cc77ed934f3e04bb7a85ad5a4b946a4663ac9a5905038293930a7407688f7c
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:17803 to nonobsolete dehydro-D-arabinono-1,4-lactone.
    The actual definition, identifiers, aliases and chemical annotations were inspected;
    the source term denotes chemistry rather than a protein requirement.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17803/
  accessed_at: '2026-10-21T11:07:59.661831Z'
  snapshot_sha256: 16c0532b5b005a3c43b01a0cdcc2a8bd7a0c9fa675f989d3c58f080ab37512d3
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: 'The complete target chemical response was inspected: exact name, definition,
    formula/charge or R-group class representation, stereochemical encoding, aliases
    and incoming/outgoing relations. The source chemical role supplies candidate context
    and does not qualify a protein.'
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: ChEBI cofactor is a biochemical role for an organic molecule or ion required
    by an enzyme. The role is not a protein-requirement class.
- evidence_id: lactone-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37581/
  accessed_at: '2026-10-21T11:09:32.549242Z'
  snapshot_sha256: 428dcb85d1550a725868c00745aeaa879ad02efc495442ab2153e2b7c0940047
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines a five-membered lactone ring.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58277/
  accessed_at: '2026-10-21T11:09:32.176093Z'
  snapshot_sha256: 517f049a9a09798f992c8d6d4a8ede7014718be379f9b9249cc156866d33dfe3
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The separate monoanion is C5H5O5, charge −1, explicitly conjugate base
    of 17803. Its pH 7.3 population assertion is source-only context and is not transferred
    to the neutral target or independently validated here.
- evidence_id: antioxidant-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/22586/
  accessed_at: '2026-10-21T11:09:32.444235Z'
  snapshot_sha256: 03d9a13191da032718c94509d0d8325a94b8ab325d927ddc67e0256e32da4702
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The antioxidant role concerns opposing oxidation; it is not by itself protein
    cofactor qualification.
- evidence_id: fungal-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76946/
  accessed_at: '2026-10-21T11:09:33.217503Z'
  snapshot_sha256: a50f9c0e2cb55276ca888c7858cc6c95009d7d8cfe8f041dd5a143962b92fd8e
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The fungal-metabolite role concerns production during fungal metabolism,
    not exact-state protein dependence.
- evidence_id: nomenclature-authority
  kind: authority
  reference: https://iubmb.qmul.ac.uk/enzyme/EC1/1/3/37.html
  accessed_at: '2026-10-21T11:09:34.649500Z'
  snapshot_sha256: 5a658560f7f0a42ef3f0aafe2b54d0bfb8f775725092dc14c89f6822c6a13493
  support: supports
  locator: EC1.1.3.37 reaction, glossary, comments and reference
  summary: The complete official EC entry identifies the C5 (5R) enediol product with
    the same systematic structure as17803. It warns that the historical D-erythroascorbate
    name/C6 CAS usage was erroneous. It classifies ALO as an FAD flavoprotein; that
    does not identify its product as its cofactor.
- evidence_id: alo-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7957197%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:57.461393Z'
  snapshot_sha256: c3c1f410c9e9bac5898fc74a98934ccff68491fceac93c4e75173c3dbc770a86
  support: supports
  locator: PMID7957197; DOI10.1111/j.1432-1033.1994.1073b.x; complete indexed abstract
  summary: The complete primary abstract describes C. albicans ATCC 10231 D-arabinono-lactone
    oxidase purification and product biosynthesis, under the historical erythroascorbic
    name. The flavin evidence concerns the enzyme; the lactone product is not thereby
    an exact neutral cofactor required by that enzyme.
- evidence_id: origin-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A7612007%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:57.460215Z'
  snapshot_sha256: e3fec15e86c1454a6ca857d2e0876bf09007f6e2feffefec905e6d92a8f2dcae
  support: supports
  locator: PMID7612007; DOI10.1006/bbrc.1995.1956; complete indexed abstract
  summary: The complete primary abstract explicitly identifies a D-glycero-pentenono-lactone
    under the trivial D-erythroascorbic name in S. sclerotiorum and examines isotope-labelled
    biosynthesis and possible oxalic-acid precursor context. It does not establish
    exact-neutral protein dependence.
- evidence_id: antioxidant-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10094636%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:57.506899Z'
  snapshot_sha256: 2e7431d026b0ffff956ceab8663abef3035761c78d1ad0ac3571fc989fcaeafe
  support: supports
  locator: PMID10094636; DOI10.1046/j.1365-2958.1998.01133.x; complete indexed abstract
  summary: The complete primary abstract reports ALO1-dependent production and altered
    oxidative-stress sensitivity in S. cerevisiae. This supports bounded antioxidant/biosynthetic
    context, not a direct non-substrate requirement for neutral 17803 by every protein
    affected.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  locator: Executed 2026-10-21T11:10:51Z through 2026-10-21T11:10:52Z; exit 0
  accessed_at: '2026-10-21T11:10:52Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
    data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
    data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml
    data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml
    data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml
  locator: Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0
  accessed_at: '2026-10-21T11:10:31Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
  locator: Executed 2026-10-21T11:10:52Z through 2026-10-21T11:10:52Z; exit 0
  accessed_at: '2026-10-21T11:10:52Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0
  accessed_at: '2026-10-21T11:10:33Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The complete local YAML denotes a proposed reusable protein requirement
    for dehydro-D-arabinono-1,4-lactone. CHEBI:17803 identifies its chemical referent
    or chemical class, not an equivalent protein-requirement class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: 'scripts/seed_chebi_cofactor.py owns the generated target: it selects source
    roles, synthesizes the requirement wrapper, appends chemical text and emits a
    chemical xref. CC BY 4.0 is supported by the official source. Current comparison
    snapshots do not identify the original seed release.'
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: consistency
  outcome: supported
  summary: The inspected source role relation explains selection of the captured local
    broader requirement parent. Chemical-role taxonomy is not automatically a protein-requirement
    hierarchy or true equivalence; this one-record review does not certify the parent.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - cofactor-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-7
  topic: Chemical-role and protein-trait hierarchy
- area: grounding
  outcome: concern
  summary: CHEBI:17803 in xrefs denotes a chemical entity/class, whereas the target
    denotes a protein functional requirement. The schema requires true own-source
    equivalence rather than a chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-8
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: CHEBI:17803 is the neutral C5H6O5 (5R)-3,4-dihydroxy-5-(hydroxymethyl)furan-2(5H)-one,
    with an enediol double bond in its five-membered lactone. The local chemical definition
    and exact name agree with the official source and IUBMB glossary. The prefix dehydro
    is not used to invent a C6 dehydroascorbate identity or a further oxidized dicarbonyl
    structure.
  evidence_ids:
  - chemical
  - chemical-role
  - lactone-parent
  - nomenclature-authority
  topic: Five-carbon enediol identity and (5R) stereochemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-9
- area: nomenclature
  outcome: supported
  summary: The source lists D-erythroascorbic acid as a related synonym, while IUBMB
    flags historically erroneous D-erythroascorbate/C6 CAS usage. The primary abstracts
    use the historical trivial name; one explicitly supplies the five-carbon pentenono-lactone
    identity. The target does not import the ambiguous synonym or C6 CAS and remains
    precisely named, so no additional target alias defect is inferred.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - nomenclature-authority
  - origin-primary
  - alo-primary
  topic: Historical erythroascorbic naming limits
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-10
- area: representation
  outcome: unknown
  summary: Direct source cofactor, antioxidant and fungal-metabolite roles explain
    candidate context. ALO product formation, oxidative-stress effects and fungal
    occurrence do not establish exact-neutral non-substrate protein dependence. Conjugate-base
    chemistry does not prove biological interchangeability, neutral-state predominance
    or absence of cofactor use.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - cofactor-role
  - antioxidant-role
  - fungal-role
  - conjugate
  - alo-primary
  - antioxidant-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-17803.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local class denotes a protein requirement for dehydro-D-arabinono-1,4-lactone,
    whereas CHEBI:17803 denotes a specific neutral five-carbon enediol lactone. xrefs
    falsely equates the functional requirement and chemical.
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
  normalization_reason: A chemical entity/class and a protein requirement for it have
    different denotations. The intended candidate requirement is recoverable through
    correctly typed grounding and activity-relative role adjudication.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:17803
    from trait-equivalence xrefs and preserve the exact source identity through schema-compatible
    grounding. Preserve chemical-source provenance separately from the locally synthesized
    requirement. Before assigning a COFACTOR chemical_participant, adjudicate whether
    the intended activity-relative role satisfies the non-substrate requirement category;
    otherwise retain that uncertainty and use only a supported representation. Do
    not blindly move this own-source association to mapped_xrefs, infer a required
    protein from chemical role alone, or promote SEEDED status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_17803
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves the intended CHEBI:17803 chemical scope without
    asserting equality to a protein requirement.
  - Preserve the exact (5R) C5 neutral identity and distinguish its monoanion, the
    ALO substrate, C6 ascorbate names and oxidation products. Do not convert historical
    naming or antioxidant/growth effects into exact-state non-substrate protein qualification.
  - Any typed participant has the supported activity-relative role and exact chemical
    scope; no unreviewed protein example, universal requirement or automatic status
    promotion is introduced.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml.
    These are future curation acceptance checks, not claims that the target has already
    changed.
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
- The three primary studies were inspected at complete indexed-abstract level. The
  neutral-versus-anion physiological population, exact-state binding and activity-relative
  non-substrate requirement were not established. The full set of other ChEBI bibliography
  links was not used as blanket evidence.
tags:
- unreviewed-path-order
- batch-018
- chebi-cofactor
```
