# Review of requires coelichelin

- Review: 20261021T103339Z-coelichelin-chebi80049
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:24:32Z
- Finished UTC: 2026-10-21T10:33:39Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Chemical identity and bounded siderophore context are supported for coelichelin. One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs. Exact physiological speciation and non-substrate protein dependence remain unqualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 015. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f) covers 138 record paths, leaving 429221 before this batch. 15 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml | generated | requires coelichelin |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_80049 | CHEBI:80049 resolves and is nonobsolete in OLS. Its actual chemical identity, stated role, relevant structural parents and conjugate comparison were inspected. The local parent and cofactor ancestor were captured and read. Successful resolution does not establish protein requirement or equivalence. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

The local label denotes a proposed reusable requirement for coelichelin; CHEBI:80049 coherently identifies the molecular referent, not an equivalent protein-requirement class.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

The ChEBI data licence is supported. The source supplies chemical descriptions and role assertions; the maintained role seeder synthesizes the protein-requirement wrapper. Current backend and OLS responses do not identify the original seed release.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

CHEBI:80049 in xrefs denotes a molecular entity while the target denotes a protein functional requirement. The schema requires true own-source equivalence; a chemical association is a different predicate.

### Coelichelin stereochemistry and chemical state

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

CHEBI:80049 is C21H39N7O11 with net charge 0. The source encodes three hydroxamic OH groups, a free carboxylic acid and amino groups. It is a four-residue ligand, not an iron-loaded complex; the neutral chemical representation is distinct from its trianion. The IUPAC structure contains two D-ornithyl units, D-allothreonyl and L-ornithine connectivity. The 2019 synthesis supports that scaffold and reports correlation through its gallium complex; it does not determine every aqueous microstate.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

The direct siderophore role explains the local broader siderophore-requirement parent; the captured parent leads to the cofactor-requirement ancestor. Chemical is-a and conjugacy relations are not automatically protein-class hierarchy or equivalence. Neither parent is certified by this one-record review.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_80049.

Source siderophore classification, isolation, synthetic identity, metal chelation and growth under iron restriction support a candidate chemical context. They do not establish which protein, if any, has the non-substrate requirement defined by FUNC_COFACTOR_REQUIREMENT. Biosynthesis and iron transport are not promoted into such evidence; neither do they prove the absence of all cofactor uses.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-80049.chemical-entity-equivalence.

The local requires-coelichelin class denotes a protein functional requirement, while CHEBI:80049 denotes the neutral coelichelin ligand. The xrefs slot asserts true equivalence between these different kinds of entity.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:80049 from trait-equivalence xrefs and retain its exact molecular identity through typed chemical grounding. Before emitting chemical_participants with role COFACTOR for a retained proposed requirement, adjudicate its non-substrate scope against the category definition; source roles and the inspected biological contexts alone do not qualify a protein. Preserve source attribution and candidate status. Do not use mapped_xrefs for this own-source association or silently substitute a conjugate, complex or reaction product.

- The regenerated target preserves the exact CHEBI:80049 chemical referent without asserting chemical-to-protein-trait equality.
- Preserve stereochemistry and the distinction among the neutral ligand, hydroxamate trianion and metal complexes. Do not infer a physiological microstate or non-substrate enzyme dependence from chelation, uptake, growth rescue or biosynthesis.
- Any retained COFACTOR participant refers to the actual molecular entity and the intended candidate requirement; substrate, product and transport evidence is not silently promoted into non-substrate requirement evidence. No protein example is qualified.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml. These future curation checks do not imply the present finding has been fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The official Introduction describes chemical entities and the ontology; Licensing makes website data available under CC BY 4.0. This supports source-data licensing, not the locally synthesized protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the comparison ontology version, not a release assignment to live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_80049; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:80049 to nonobsolete coelichelin. Actual labels, description fields and synonyms were inspected. The role/molecular denotation is assessed separately from the local protein requirement. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/80049/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response supplies the actual name, definition field, chemical data, structure, aliases and outgoing relations. Its direct source role provides candidate context rather than a qualified protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing relations | supports | The cofactor source role describes an organic molecule or ion required by an enzyme; its parent is biochemical role. This source assertion is distinct from a protein requirement class. |
| specific-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; definition and outgoing relations | supports | The siderophore role describes microbial iron(III) chelation for transport/sequestration and has cofactor, iron(3+) chelator and iron-ionophore parents. Its source classification does not itself qualify non-substrate enzyme dependence. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | Complete captured broader cofactor-requirement ancestor inspected. Its requirement wrapper and source-role xref are distinguished; this review does not certify that ancestor. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/84724/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The independently identified acid/base counterpart has the same encoded stereochemical skeleton and differs by three hydroxamate protons and three charge units. Both retain the carboxylic acid and unprotonated amines in their source structures; the trianion is not a ferric complex. |
| primary-isolation | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:16408055%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID16408055; DOI10.1038/nchembio731; complete indexed abstract | supports | The complete 2005 primary abstract reports isolation and structure determination of a tris-hydroxamate tetrapeptide iron chelator from S. coelicolor, and CchH/CchJ involvement in biosynthesis. The biosynthetic enzyme requirements are not evidence that those proteins require coelichelin as a non-substrate cofactor. |
| primary-synthesis | https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC6474248/unicode; PMCIDPMC6474248; PMID30645132; DOI10.1021/acs.orglett.8b03857; BioC passages 0–12 and figure captions | supports | The complete primary article text was inspected through NCBI BioC. Passages 7–9 describe D-allo-threonine, L-ornithine and two D-ornithine building blocks and comparison of the synthetic gallium(III) complex with the natural-product spectra. Passages 10–12 report ferric binding and conditional growth support in siderophore-deficient P. aeruginosa. These establish bounded chemical/iron-delivery context, not an exact free-ligand protonation population or protein cofactor requirement. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/48030/; name, definition and outgoing relations | supports | The actual structural-parent name, definition and outgoing relations were inspected. This is chemical taxonomy, not directly a protein parent_traits assertion. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/; name, definition and outgoing relations | supports | The actual structural-parent name, definition and outgoing relations were inspected. This is chemical taxonomy, not directly a protein parent_traits assertion. |
| chemical-parent-3 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24079/; name, definition and outgoing relations | supports | The actual structural-parent name, definition and outgoing relations were inspected. This is chemical taxonomy, not directly a protein parent_traits assertion. |
| metabolite-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76969/; name, definition and outgoing relations | supports | The bacterial-metabolite source role resolves to a prokaryotic metabolite produced in a bacterial metabolic reaction; it does not independently qualify protein dependence. |
| source-citation | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:21342472%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID21342472; DOI10.1111/j.1751-7915.2010.00240.x; complete indexed abstract | supports | The source-linked primary abstract studies desE disruption and ferrioxamine-dependent growth/development in S. coelicolor, including a coelichelin biosynthesis/transport-minus background. It is not the original coelichelin isolation experiment and does not establish a non-substrate cofactor requirement. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml; Executed 2026-10-21T10:26:47Z through 2026-10-21T10:26:48Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-3-chebi84724.yaml data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-b-chebi28890.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-a-chebi62784.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-g-chebi62786.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-3-chebi59543.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-chebi59536.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Executed 2026-10-21T10:25:03Z through 2026-10-21T10:26:36Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml; Executed 2026-10-21T10:26:48Z through 2026-10-21T10:26:48Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:26:36Z through 2026-10-21T10:26:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The 2005 isolation paper and source-linked receptor study were inspected at complete indexed-abstract level where cited. The 2019 synthesis article was inspected as full BioC text, without supplementary procedures or numerical figure reanalysis. Its passage 11 contains ambiguous apo/iron-loaded wording; no apo-versus-holo ranking is used here. Its proposed octahedral complex and conditional growth assays are not universal coordination or microstate evidence.
- No transcriptomic or expression claim is made. The S. coelicolor and P. aeruginosa experiments are bounded chemical/biosynthetic/iron-delivery context, not protein-example qualification.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T103339Z-coelichelin-chebi80049
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires coelichelin
started_at: '2026-10-21T10:24:32Z'
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
summary: Chemical identity and bounded siderophore context are supported for coelichelin.
  One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs.
  Exact physiological speciation and non-substrate protein dependence remain unqualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
    sha256: 7505441bd9fb42ab33b0ff1061de97473737dce26d82752258872920b888c779
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
    sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
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
  selection: Path-order position 2 in batch 015. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
targets:
- kind: generated
  label: requires coelichelin
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_80049
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:80049 resolves and is nonobsolete in OLS. Its actual chemical identity,
    stated role, relevant structural parents and conjugate comparison were inspected.
    The local parent and cofactor ancestor were captured and read. Successful resolution
    does not establish protein requirement or equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  evidence_ids:
  - chemical
  - chemical-role
  - specific-role
  - cofactor-role
  - licence
  - release
  - conjugate
  - primary-isolation
  - primary-synthesis
  - chemical-parent-1
  - chemical-parent-2
  - chemical-parent-3
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:24:32Z'
  snapshot_sha256: 7505441bd9fb42ab33b0ff1061de97473737dce26d82752258872920b888c779
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
  accessed_at: '2026-10-21T10:24:32Z'
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
  accessed_at: '2026-10-21T10:24:32Z'
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
  accessed_at: '2026-10-21T10:24:32Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:24:32Z'
  snapshot_sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
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
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_80049
  accessed_at: '2026-10-21T10:25:31.452046Z'
  snapshot_sha256: ad5a3c9fb0349307a20e7b67a3799ad50a6bcb3e1da1e42c461188e7f761d785
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:80049 to nonobsolete coelichelin. Actual labels, description
    fields and synonyms were inspected. The role/molecular denotation is assessed
    separately from the local protein requirement.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/80049/
  accessed_at: '2026-10-21T10:25:31.307265Z'
  snapshot_sha256: 4351b9adba88fb046ff82a9b49a2578c51320a839a18fddbd27ce0a113dafb5d
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T09:02:57.586907Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: definition and outgoing relations
  summary: The siderophore role describes microbial iron(III) chelation for transport/sequestration
    and has cofactor, iron(3+) chelator and iron-ionophore parents. Its source classification
    does not itself qualify non-substrate enzyme dependence.
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T10:24:32Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: Complete captured broader cofactor-requirement ancestor inspected. Its
    requirement wrapper and source-role xref are distinguished; this review does not
    certify that ancestor.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/84724/
  accessed_at: '2026-10-21T10:25:31.292041Z'
  snapshot_sha256: 1ec0895c633561bec55c41fe24a153e03ab46df28040f0197e19f17525735d92
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The independently identified acid/base counterpart has the same encoded
    stereochemical skeleton and differs by three hydroxamate protons and three charge
    units. Both retain the carboxylic acid and unprotonated amines in their source
    structures; the trianion is not a ferric complex.
- evidence_id: primary-isolation
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:16408055%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:10.938180Z'
  snapshot_sha256: b71d3821963e77bfeecdb4b531325da8abc3b64a497529fad15e978ed2acb192
  support: supports
  locator: PMID16408055; DOI10.1038/nchembio731; complete indexed abstract
  summary: The complete 2005 primary abstract reports isolation and structure determination
    of a tris-hydroxamate tetrapeptide iron chelator from S. coelicolor, and CchH/CchJ
    involvement in biosynthesis. The biosynthetic enzyme requirements are not evidence
    that those proteins require coelichelin as a non-substrate cofactor.
- evidence_id: primary-synthesis
  kind: primary_source
  reference: https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC6474248/unicode
  accessed_at: '2026-10-21T10:27:17.719450Z'
  snapshot_sha256: 40af912d7a064554d1503d8ded874a58443bfa1953c2e6dc0a884a2501245cb8
  support: supports
  locator: PMCIDPMC6474248; PMID30645132; DOI10.1021/acs.orglett.8b03857; BioC passages
    0–12 and figure captions
  summary: The complete primary article text was inspected through NCBI BioC. Passages
    7–9 describe D-allo-threonine, L-ornithine and two D-ornithine building blocks
    and comparison of the synthetic gallium(III) complex with the natural-product
    spectra. Passages 10–12 report ferric binding and conditional growth support in
    siderophore-deficient P. aeruginosa. These establish bounded chemical/iron-delivery
    context, not an exact free-ligand protonation population or protein cofactor requirement.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/48030/
  accessed_at: '2026-10-21T10:26:07.443371Z'
  snapshot_sha256: c3478459ff1d1549310fb624be6004fec7a6fe98a68ef4c6c8a76b4b2d5ddc66
  support: supports
  locator: name, definition and outgoing relations
  summary: The actual structural-parent name, definition and outgoing relations were
    inspected. This is chemical taxonomy, not directly a protein parent_traits assertion.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/
  accessed_at: '2026-10-21T10:26:07.674612Z'
  snapshot_sha256: 489ee6f999b8a733ab1e6334c09f36828ec55ecae22082aca866ad781b0861bf
  support: supports
  locator: name, definition and outgoing relations
  summary: The actual structural-parent name, definition and outgoing relations were
    inspected. This is chemical taxonomy, not directly a protein parent_traits assertion.
- evidence_id: chemical-parent-3
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24079/
  accessed_at: '2026-10-21T10:26:07.313004Z'
  snapshot_sha256: b916d65a69d339dc1308f63a3bb4b4c6c0449d1b921e5d4f52860988c2985d66
  support: supports
  locator: name, definition and outgoing relations
  summary: The actual structural-parent name, definition and outgoing relations were
    inspected. This is chemical taxonomy, not directly a protein parent_traits assertion.
- evidence_id: metabolite-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76969/
  accessed_at: '2026-10-21T10:26:07.832536Z'
  snapshot_sha256: 2e39bcf99dd2f2f7cbff545d082bbbe1794d7a951109c84f344672080b37df09
  support: supports
  locator: name, definition and outgoing relations
  summary: The bacterial-metabolite source role resolves to a prokaryotic metabolite
    produced in a bacterial metabolic reaction; it does not independently qualify
    protein dependence.
- evidence_id: source-citation
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:21342472%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:10.479358Z'
  snapshot_sha256: 156aafeb61667f735c3f4e11a78c4dd2fff939f3238794b015b4d83ce2725dbe
  support: supports
  locator: PMID21342472; DOI10.1111/j.1751-7915.2010.00240.x; complete indexed abstract
  summary: The source-linked primary abstract studies desE disruption and ferrioxamine-dependent
    growth/development in S. coelicolor, including a coelichelin biosynthesis/transport-minus
    background. It is not the original coelichelin isolation experiment and does not
    establish a non-substrate cofactor requirement.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  locator: Executed 2026-10-21T10:26:47Z through 2026-10-21T10:26:48Z; exit 0
  accessed_at: '2026-10-21T10:26:48Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml
  locator: Executed 2026-10-21T10:26:48Z through 2026-10-21T10:26:48Z; exit 0
  accessed_at: '2026-10-21T10:26:48Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The local label denotes a proposed reusable requirement for coelichelin;
    CHEBI:80049 coherently identifies the molecular referent, not an equivalent protein-requirement
    class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: grounding
  outcome: concern
  summary: CHEBI:80049 in xrefs denotes a molecular entity while the target denotes
    a protein functional requirement. The schema requires true own-source equivalence;
    a chemical association is a different predicate.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-7
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: CHEBI:80049 is C21H39N7O11 with net charge 0. The source encodes three
    hydroxamic OH groups, a free carboxylic acid and amino groups. It is a four-residue
    ligand, not an iron-loaded complex; the neutral chemical representation is distinct
    from its trianion. The IUPAC structure contains two D-ornithyl units, D-allothreonyl
    and L-ornithine connectivity. The 2019 synthesis supports that scaffold and reports
    correlation through its gallium complex; it does not determine every aqueous microstate.
  evidence_ids:
  - chemical
  - chemical-role
  - conjugate
  - primary-isolation
  - primary-synthesis
  topic: Coelichelin stereochemistry and chemical state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The direct siderophore role explains the local broader siderophore-requirement
    parent; the captured parent leads to the cofactor-requirement ancestor. Chemical
    is-a and conjugacy relations are not automatically protein-class hierarchy or
    equivalence. Neither parent is certified by this one-record review.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - local-ancestor
  - specific-role
  - cofactor-role
  - chemical-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-9
  topic: Chemical-role and protein-trait hierarchy
- area: representation
  outcome: unknown
  summary: Source siderophore classification, isolation, synthetic identity, metal
    chelation and growth under iron restriction support a candidate chemical context.
    They do not establish which protein, if any, has the non-substrate requirement
    defined by FUNC_COFACTOR_REQUIREMENT. Biosynthesis and iron transport are not
    promoted into such evidence; neither do they prove the absence of all cofactor
    uses.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - specific-role
  - primary-isolation
  - primary-synthesis
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  assessment_id: assessment-10
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-80049.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-coelichelin class denotes a protein functional requirement,
    while CHEBI:80049 denotes the neutral coelichelin ligand. The xrefs slot asserts
    true equivalence between these different kinds of entity.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:80049
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_80049
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves the exact CHEBI:80049 chemical referent without
    asserting chemical-to-protein-trait equality.
  - Preserve stereochemistry and the distinction among the neutral ligand, hydroxamate
    trianion and metal complexes. Do not infer a physiological microstate or non-substrate
    enzyme dependence from chelation, uptake, growth rescue or biosynthesis.
  - Any retained COFACTOR participant refers to the actual molecular entity and the
    intended candidate requirement; substrate, product and transport evidence is not
    silently promoted into non-substrate requirement evidence. No protein example
    is qualified.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml.
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
- The 2005 isolation paper and source-linked receptor study were inspected at complete
  indexed-abstract level where cited. The 2019 synthesis article was inspected as
  full BioC text, without supplementary procedures or numerical figure reanalysis.
  Its passage 11 contains ambiguous apo/iron-loaded wording; no apo-versus-holo ranking
  is used here. Its proposed octahedral complex and conditional growth assays are
  not universal coordination or microstate evidence.
- No transcriptomic or expression claim is made. The S. coelicolor and P. aeruginosa
  experiments are bounded chemical/biosynthetic/iron-delivery context, not protein-example
  qualification.
tags:
- unreviewed-path-order
- batch-015
- chebi-cofactor
```
