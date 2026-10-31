# Review of requires enterobactin

- Review: 20261021T114710Z-enterobactin-chebi28855
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:35:29Z
- Finished UTC: 2026-10-21T11:47:10Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Neutral enterobactin identity, stereochemistry and source siderophore role are supported, with bounded bacterial iron-acquisition context. One confirmed major finding concerns chemical-to-protein-trait equivalence. Free ligand, conjugate anions, ferric complex and hydrolysed substrate remain distinct; exact protein requirement is unresolved.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 020. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87) covers 188 record paths, leaving 429171 before this batch. 20 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml | generated | requires enterobactin |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_28855 | Official ChEBI/OLS resolve CHEBI:28855 with its exact identity and direct siderophore role plus verified cofactor ancestry. The maintained owner, captured local parent, source metadata and bounded external chemistry/literature are distinct from protein-trait equivalence and native protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Enterobactin stereochemistry and free-ligand state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The current source supports neutral (3S,7S,11S) enterobactin with a three-ester macrocycle and six protonated phenolic groups. The monoanion, hexaanion and Fe(III) complex are different chemical states. Their relationship supports connectivity comparison, not chemical or protein-trait merging.

### Bacterial production and iron acquisition

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The complete Salmonella and E. coli abstracts support the bounded taxon examples, iron acquisition and ferric-ligand hydrolysis contexts. The source-linked E. coli model is retained as provenance rather than primary isolation evidence. No universal taxonomic or physiological requirement is inferred.

### Exact neutral ligand and activity-relative requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

Siderophore function is positively supported, but the inspected growth/transport and esterase experiments do not qualify the exact neutral free ligand as a non-substrate requirement of a particular protein. Ligand hydrolysis does not disprove other possible roles, and iron transport is not automatically recast as an enzyme-cofactor requirement.

### Source siderophore ancestry and local requirement hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The direct siderophore role and its explicit cofactor parent explain source selection and the captured local ancestry. This provenance does not certify the parent records or make chemical-role taxonomy equivalent to protein-requirement taxonomy.

### Chemical source and generated requirement wrapper

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The chemical identifier, source wording, direct siderophore role and stated ChEBI licence resolve. The protein-requirement wrapper is generated by the captured ChEBI seeder, not an official chemical-to-protein equivalence. Current snapshots do not identify the original seed release.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_28855.

The xref denotes a chemical entity while the local class denotes a protein functional requirement. A correct chemical identity or source role does not make those entity types equivalent.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-28855.chemical-entity-equivalence.

The source chemical in xrefs and the local requirement class have different denotations. Source roles and bounded biological activity do not satisfy true own-source equivalence. 

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py while retaining the exact supported chemical identity. Remove chemical-to-protein-trait equality and preserve supported chemical grounding/provenance. Adjudicate the activity-relative ChemicalParticipant.role and exact state before adding a typed participant; a source chemical role is not independent protein qualification. If the evidence cannot support the required participant role, retain provenance and explicit uncertainty without inventing a participant. Do not move the equality to mapped_xrefs, merge chemical states or automatically qualify proteins.

- The chemical association no longer asserts equality to the protein requirement. Exact identity and candidate provenance remain auditable; any participant has a curator-adjudicated activity-relative role or uncertainty remains explicit.
- Use an audited route selecting the existing target and a focused source-transform fixture. No native status, protein example or obligatory physiological requirement is promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml. Run full just validate-all before merging record changes; capture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The inspected ChEBI chemical-scope and Licensing sections state CC BY 4.0. This supports ChEBI attribution, not chemical-to-protein-trait equality. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256, loaded 2026-10-16. Its original access time and digest are retained; this does not assign a release to the original seed or live backend. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/28855/; Complete identifier, names, definition or null, formula/charge, structure, origins, role classification and outgoing relations | supports | CHEBI:28855 is neutral enterobactin, C30H27N3O15, with a (3S,7S,11S) macrotriolide, three dihydroxybenzoyl amides and six phenolic OH groups. Its fixed structure contains no iron. The source definition describes production by certain Enterobacteriaceae, including E. coli and Salmonella. Direct roles are siderophore and bacterial metabolite; conjugate bases include CHEBI:77805 and CHEBI:38150. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:28855; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete chemical identifier and source identity. The actual definition, aliases and chemical annotations were inspected. Resolution of the chemical identifier is distinct from validation of the protein-trait assertion. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations | supports | Cofactor CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, under biochemical role CHEBI:52206. It is not itself a chemical molecule or an equivalent protein-requirement class. |
| context-26195 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26195/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Polyphenol is a structural class with more than one phenol unit; it does not independently establish a particular protein requirement. |
| context-33566 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33566/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Catechols are compounds with an ortho-diphenol skeleton. The R-group parent drawing is generic and is not the fixed formula of enterobactin. |
| context-145559 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/145559/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | A macrotriolide is a macrocycle containing three carboxylic ester linkages. This supports the target ring description without making the chemical a protein class. |
| context-37409 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37409/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Crown compound is a macrocyclic polydentate structural class; broad coordination potential does not establish a particular enzyme requirement. |
| context-76969 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76969/; Complete chemical identity, definition or explicit null, names, formula/charge, structure and outgoing relations | supports | Bacterial metabolite is a source role denoting a metabolite produced by bacteria, not a protein-requirement class. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Definition and complete outgoing relations | supports | Siderophore describes microbial low-molecular-mass Fe(III)-chelating compounds for iron transport/sequestration. Its explicit source parent is cofactor, along with iron(3+) chelator and iron ionophore. This is the role ancestry behind the local siderophore-to-cofactor requirement hierarchy. |
| monoanion | https://www.ebi.ac.uk/chebi/backend/api/public/compound/77805/; Inspected source response captured at the recorded UTC time | supports | CHEBI:77805 has one phenolic O−, C30H26N3O15 and charge −1, retaining the same three stereocentres. Its major-microspecies pH 7.3 statement explicitly names Marvin 6.2.0 prediction; that assertion is neither imported into neutral CHEBI:28855 nor treated as a new experiment. |
| hexaanion | https://www.ebi.ac.uk/chebi/backend/api/public/compound/38150/; Inspected source response captured at the recorded UTC time | supports | CHEBI:38150 is the same stereospecified scaffold with six phenolates, C30H21N3O15 and charge −6. Its prose definition is null. It is not the neutral ligand or an iron complex. |
| ferric-complex | https://www.ebi.ac.uk/chebi/backend/api/public/compound/28199/; Inspected source response captured at the recorded UTC time | supports | Ferrienterobactin(3−) CHEBI:28199 is C30H21FeN3O15, with the exact hexaanion CHEBI:38150 as a has-part relation and explicit Fe(III)-complexed siderophore classification. The complex has net −3; the [Fe-3] coordinate-bond SMILES notation does not make the iron oxidation state −III. No separate iron has-part relation is invented. |
| primary-4923066 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4923066%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | supports | PMID:4923066; DOI:10.1128/jb.104.2.635-639.1970. Salmonella typhimurium enterobactin-biosynthesis mutants were studied. The complete abstract reports wild-type secretion on low-iron medium, citrate-dependent inhibition of mutant growth and iron uptake, and rescue by enterobactin or iron. This supports the specified bacterial iron-acquisition context, not a universal growth requirement or an exact neutral protein cofactor. |
| primary-4565531 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4565531%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | supports | PMID:4565531; DOI:10.1128/jb.112.3.1142-1149.1972. The complete abstract reports E. coli mutants lacking ferric-enterochelin esterase activity, retained iron uptake and hydrolysis of the ligand to three dihydroxybenzoylserine molecules. Ferric-complex transport and ligand-substrate hydrolysis are distinguished from the free neutral chemical and do not negate other possible roles. |
| primary-21988831 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full article not inspected in this response | context_only | PMID:21988831; DOI:10.1038/msb.2011.65. The source-linked paper concerns the iJO1366 E. coli metabolic reconstruction and a knockout growth screen. The complete abstract was inspected as source-origin context; it is not a direct measurement of enterobactin neutral-state production or protein dependence. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml; Executed 2026-10-21T11:36:35Z through 2026-10-21T11:36:37Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/divinyl-chlorophyll-b-chebi73115.yaml data/traits/function/cofactor_requirement/chebi/dy-chebi33373.yaml data/traits/function/cofactor_requirement/chebi/echinenone-chebi4746.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-1-chebi77805.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-6-chebi38150.yaml data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml data/traits/function/cofactor_requirement/chebi/er-chebi33379.yaml data/traits/function/cofactor_requirement/chebi/eu-chebi33375.yaml data/traits/function/cofactor_requirement/chebi/f420-chebi28343.yaml data/traits/function/cofactor_requirement/chebi/fad-3-chebi57692.yaml; Executed 2026-10-21T11:36:19Z through 2026-10-21T11:38:17Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml; Executed 2026-10-21T11:36:37Z through 2026-10-21T11:36:38Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:38:17Z through 2026-10-21T11:38:18Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The two historical iron-acquisition papers and source-linked model were inspected through complete indexed abstracts. No exact neutral-state protein-bound population, coordination geometry, whole-cell pH equilibrium or newly qualified protein example is established. External chemical comparisons are not local sibling-record assessments.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T114710Z-enterobactin-chebi28855
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires enterobactin
started_at: '2026-10-21T11:35:29Z'
finished_at: '2026-10-21T11:47:10Z'
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
summary: Neutral enterobactin identity, stereochemistry and source siderophore role
  are supported, with bounded bacterial iron-acquisition context. One confirmed major
  finding concerns chemical-to-protein-trait equivalence. Free ligand, conjugate anions,
  ferric complex and hydrolysed substrate remain distinct; exact protein requirement
  is unresolved.
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
  - path: data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
    sha256: ce3af12fa4c551da57d2e8237ee8f56d89f56f16e220f315b5063856bea10d26
    role: target
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
  selection: Path-order position 6 in batch 020. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
targets:
- kind: generated
  label: requires enterobactin
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_28855
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:28855 with its exact identity and direct
    siderophore role plus verified cofactor ancestry. The maintained owner, captured
    local parent, source metadata and bounded external chemistry/literature are distinct
    from protein-trait equivalence and native protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - cofactor-role
  - context-26195
  - context-33566
  - context-145559
  - context-37409
  - context-76969
  - siderophore-role
  - monoanion
  - hexaanion
  - ferric-complex
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:35:29Z'
  snapshot_sha256: ce3af12fa4c551da57d2e8237ee8f56d89f56f16e220f315b5063856bea10d26
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
  accessed_at: '2026-10-21T11:35:29Z'
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
  accessed_at: '2026-10-21T11:35:29Z'
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
  accessed_at: '2026-10-21T11:35:29Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:35:29Z'
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
  locator: Introduction and Licensing
  summary: The inspected ChEBI chemical-scope and Licensing sections state CC BY 4.0.
    This supports ChEBI attribution, not chemical-to-protein-trait equality.
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/28855/
  accessed_at: '2026-10-21T11:36:39.486673Z'
  snapshot_sha256: 99e39554bec30989361485c0e2f1a25f04be53cebd9206dbcde3efd464fc7b56
  support: supports
  locator: Complete identifier, names, definition or null, formula/charge, structure,
    origins, role classification and outgoing relations
  summary: CHEBI:28855 is neutral enterobactin, C30H27N3O15, with a (3S,7S,11S) macrotriolide,
    three dihydroxybenzoyl amides and six phenolic OH groups. Its fixed structure
    contains no iron. The source definition describes production by certain Enterobacteriaceae,
    including E. coli and Salmonella. Direct roles are siderophore and bacterial metabolite;
    conjugate bases include CHEBI:77805 and CHEBI:38150.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:28855
  accessed_at: '2026-10-21T11:36:39.475554Z'
  snapshot_sha256: 93639eaf990b3d651dff08efdb073ca94568b627c088dbed0443edb32f1a342e
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete chemical identifier and source identity.
    The actual definition, aliases and chemical annotations were inspected. Resolution
    of the chemical identifier is distinct from validation of the protein-trait assertion.
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
- evidence_id: context-26195
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26195/
  accessed_at: '2026-10-21T11:37:44.924814Z'
  snapshot_sha256: c0e8c956eae32deb6344f042dd56b0a4cd5ac428a15eb683b11ac6b791069bab
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Polyphenol is a structural class with more than one phenol unit; it does
    not independently establish a particular protein requirement.
- evidence_id: context-33566
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33566/
  accessed_at: '2026-10-21T11:37:44.941554Z'
  snapshot_sha256: c1c0e6d759b02cef0b7a41393b0521e3d2157f6f2c4a7084b9e7e17c512cf75a
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Catechols are compounds with an ortho-diphenol skeleton. The R-group parent
    drawing is generic and is not the fixed formula of enterobactin.
- evidence_id: context-145559
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/145559/
  accessed_at: '2026-10-21T11:37:44.961503Z'
  snapshot_sha256: 3c7c7fdc679c3379828cf03623d32667bf1c7d8df3124e553a286b05bad9e192
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: A macrotriolide is a macrocycle containing three carboxylic ester linkages.
    This supports the target ring description without making the chemical a protein
    class.
- evidence_id: context-37409
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37409/
  accessed_at: '2026-10-21T11:37:44.968697Z'
  snapshot_sha256: ecaa61d6d1bab190f9b09e2e859e9b5f74418e81a457c94bb939f31fe783d201
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Crown compound is a macrocyclic polydentate structural class; broad coordination
    potential does not establish a particular enzyme requirement.
- evidence_id: context-76969
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76969/
  accessed_at: '2026-10-21T11:37:45.447651Z'
  snapshot_sha256: 2e39bcf99dd2f2f7cbff545d082bbbe1794d7a951109c84f344672080b37df09
  support: supports
  locator: Complete chemical identity, definition or explicit null, names, formula/charge,
    structure and outgoing relations
  summary: Bacterial metabolite is a source role denoting a metabolite produced by
    bacteria, not a protein-requirement class.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T09:02:57.586907Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Definition and complete outgoing relations
  summary: Siderophore describes microbial low-molecular-mass Fe(III)-chelating compounds
    for iron transport/sequestration. Its explicit source parent is cofactor, along
    with iron(3+) chelator and iron ionophore. This is the role ancestry behind the
    local siderophore-to-cofactor requirement hierarchy.
- evidence_id: monoanion
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/77805/
  accessed_at: '2026-10-21T11:36:35.269792Z'
  snapshot_sha256: e57b19878de00bfc04341c0ab9153a72401891248adfd2163fa3a208ce778fa7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:77805 has one phenolic O−, C30H26N3O15 and charge −1, retaining the
    same three stereocentres. Its major-microspecies pH 7.3 statement explicitly names
    Marvin 6.2.0 prediction; that assertion is neither imported into neutral CHEBI:28855
    nor treated as a new experiment.
- evidence_id: hexaanion
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/38150/
  accessed_at: '2026-10-21T11:36:35.283634Z'
  snapshot_sha256: af8597d984782db3bc23fe7cf69fbd99b28dbd558458edc2daf119ab786c0031
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:38150 is the same stereospecified scaffold with six phenolates, C30H21N3O15
    and charge −6. Its prose definition is null. It is not the neutral ligand or an
    iron complex.
- evidence_id: ferric-complex
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/28199/
  accessed_at: '2026-10-21T11:37:40.028427Z'
  snapshot_sha256: dd88e4c013bdc954829016bd5bcf2c6e01ba6dad6d6df573b094d688f89de5d9
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Ferrienterobactin(3−) CHEBI:28199 is C30H21FeN3O15, with the exact hexaanion
    CHEBI:38150 as a has-part relation and explicit Fe(III)-complexed siderophore
    classification. The complex has net −3; the [Fe-3] coordinate-bond SMILES notation
    does not make the iron oxidation state −III. No separate iron has-part relation
    is invented.
- evidence_id: primary-4923066
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4923066%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:38:19.854255Z'
  snapshot_sha256: 4d7f9d2c2ddca5892629e6cdf55e7e82fa9fb6254a4cacc665564b1aa71b6e58
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:4923066; DOI:10.1128/jb.104.2.635-639.1970. Salmonella typhimurium
    enterobactin-biosynthesis mutants were studied. The complete abstract reports
    wild-type secretion on low-iron medium, citrate-dependent inhibition of mutant
    growth and iron uptake, and rescue by enterobactin or iron. This supports the
    specified bacterial iron-acquisition context, not a universal growth requirement
    or an exact neutral protein cofactor.
- evidence_id: primary-4565531
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4565531%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:38:20.506422Z'
  snapshot_sha256: 6ffc8b54f3485863e8f8d27f896a8ecaebc2ac7cbcb205061b1ee09896d7bdae
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:4565531; DOI:10.1128/jb.112.3.1142-1149.1972. The complete abstract
    reports E. coli mutants lacking ferric-enterochelin esterase activity, retained
    iron uptake and hydrolysis of the ligand to three dihydroxybenzoylserine molecules.
    Ferric-complex transport and ligand-substrate hydrolysis are distinguished from
    the free neutral chemical and do not negate other possible roles.
- evidence_id: primary-21988831
  kind: database
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21988831%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:37:45.903388Z'
  snapshot_sha256: e25a797a813b88b0e3053e41aacefa22b641206af4570c409c52515a8233a3e0
  support: context_only
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    in this response
  summary: PMID:21988831; DOI:10.1038/msb.2011.65. The source-linked paper concerns
    the iJO1366 E. coli metabolic reconstruction and a knockout growth screen. The
    complete abstract was inspected as source-origin context; it is not a direct measurement
    of enterobactin neutral-state production or protein dependence.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  locator: Executed 2026-10-21T11:36:35Z through 2026-10-21T11:36:37Z; exit 0
  accessed_at: '2026-10-21T11:36:37Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
  locator: Executed 2026-10-21T11:36:37Z through 2026-10-21T11:36:38Z; exit 0
  accessed_at: '2026-10-21T11:36:38Z'
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
  summary: scripts/seed_chebi_cofactor.py owns generated target changes. Its source
    transformation is inspected; no emitted record has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The current source supports neutral (3S,7S,11S) enterobactin with a three-ester
    macrocycle and six protonated phenolic groups. The monoanion, hexaanion and Fe(III)
    complex are different chemical states. Their relationship supports connectivity
    comparison, not chemical or protein-trait merging.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - monoanion
  - hexaanion
  - ferric-complex
  topic: Enterobactin stereochemistry and free-ligand state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The complete Salmonella and E. coli abstracts support the bounded taxon
    examples, iron acquisition and ferric-ligand hydrolysis contexts. The source-linked
    E. coli model is retained as provenance rather than primary isolation evidence.
    No universal taxonomic or physiological requirement is inferred.
  evidence_ids:
  - chemical
  - primary-4923066
  - primary-4565531
  - primary-21988831
  topic: Bacterial production and iron acquisition
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: Siderophore function is positively supported, but the inspected growth/transport
    and esterase experiments do not qualify the exact neutral free ligand as a non-substrate
    requirement of a particular protein. Ligand hydrolysis does not disprove other
    possible roles, and iron transport is not automatically recast as an enzyme-cofactor
    requirement.
  evidence_ids:
  - record
  - schema
  - chemical
  - ferric-complex
  - primary-4923066
  - primary-4565531
  topic: Exact neutral ligand and activity-relative requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The direct siderophore role and its explicit cofactor parent explain source
    selection and the captured local ancestry. This provenance does not certify the
    parent records or make chemical-role taxonomy equivalent to protein-requirement
    taxonomy.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - siderophore-role
  - cofactor-role
  - owner
  topic: Source siderophore ancestry and local requirement hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The chemical identifier, source wording, direct siderophore role and stated
    ChEBI licence resolve. The protein-requirement wrapper is generated by the captured
    ChEBI seeder, not an official chemical-to-protein equivalence. Current snapshots
    do not identify the original seed release.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  topic: Chemical source and generated requirement wrapper
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The xref denotes a chemical entity while the local class denotes a protein
    functional requirement. A correct chemical identity or source role does not make
    those entity types equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-28855.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: 'The source chemical in xrefs and the local requirement class have
    different denotations. Source roles and bounded biological activity do not satisfy
    true own-source equivalence. '
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The proposed requirement is recognizable, but the chemical
    and protein-requirement denotations differ; the equivalence assertion is a major
    grounding defect.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py while retaining the
    exact supported chemical identity. Remove chemical-to-protein-trait equality and
    preserve supported chemical grounding/provenance. Adjudicate the activity-relative
    ChemicalParticipant.role and exact state before adding a typed participant; a
    source chemical role is not independent protein qualification. If the evidence
    cannot support the required participant role, retain provenance and explicit uncertainty
    without inventing a participant. Do not move the equality to mapped_xrefs, merge
    chemical states or automatically qualify proteins.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_28855
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The chemical association no longer asserts equality to the protein requirement.
    Exact identity and candidate provenance remain auditable; any participant has
    a curator-adjudicated activity-relative role or uncertainty remains explicit.
  - Use an audited route selecting the existing target and a focused source-transform
    fixture. No native status, protein example or obligatory physiological requirement
    is promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/enterobactin-chebi28855.yaml.
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
- The two historical iron-acquisition papers and source-linked model were inspected
  through complete indexed abstracts. No exact neutral-state protein-bound population,
  coordination geometry, whole-cell pH equilibrium or newly qualified protein example
  is established. External chemical comparisons are not local sibling-record assessments.
tags:
- unreviewed-path-order
- batch-020
- chebi-cofactor
```
