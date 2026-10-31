# Review of requires desferrimycobactin T

- Review: 20261021T111506Z-desferrimycobactin-t-chebi61168
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:07:48Z
- Finished UTC: 2026-10-21T11:15:06Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact neutral saturated-icosanoyl desferrimycobactin T structure and source ancestry resolve. One confirmed major finding concerns chemical-to-trait equivalence. Positive secretion/vesicle-export evidence prevents a false cell-association contradiction, but exact free-congener secretion and protein requirement remain unresolved.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 9 in batch 018. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9) covers 168 record paths, leaving 429191 before this batch. 18 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml | generated | requires desferrimycobactin T |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_61168 | Official ChEBI and OLS resolve CHEBI:61168 and the inspected chemical comparisons. Its direct siderophore role and the source siderophore-to-cofactor ancestry are verified. Resolution is chemical/provenance support, not protein-trait equivalence or per-protein qualification. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Mycobactin T exact ligand and acyl-chain scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The source chemical is an iron-free neutral ligand with a fixed saturated twenty-carbon acyl group and specified stereochemistry. The name does not license replacing that structure with any acyl-chain congener, a ferric complex or soluble carboxymycobactin.

### Mycobactin localization and vesicle-export context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

Cell-wall association in the exochelin transfer study coexists with positive mycobactin secretion/vesicle-export evidence. The full vesicle paper reports ferric congeners, including 19:1. Thus cell association does not demonstrate that secretion is false, while the exact iron-free saturated icosanoyl entry is not independently resolved by these experiments.

### Exact-congener secretion and protein requirement

evidence: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The source-specific secretion statement is authentic, but the inspected experiments do not establish the exact free saturated CHEBI:61168 congener as the exported species or an obligatory non-substrate protein cofactor. This limited coverage is not a demonstrated secretion contradiction.

### Chemical definition and maintained-source provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The current official source supports the copied chemical definition and direct siderophore role; the protein-requirement wrapper is maintained ChEBI-seeder synthesis. Licence and comparison release are traceable; the original seed release remains unknown.

### Siderophore source ancestry versus requirement hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The complete local siderophore-to-cofactor requirement ancestry resolves, and current source siderophore is-a cofactor is verified. These source-role relations supply candidate context; chemical classification and role ancestry do not establish protein-trait equality or exact physiological dependence.

### Activity-relative protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class has not been independently qualified for the exact chemical state and activity-relative non-substrate role. Iron binding, transport, biosynthesis or source-role ancestry alone is insufficient; these contexts also do not prove absence of other cofactor roles.

### Chemical denotation versus protein-trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_61168.

The exact ChEBI chemical referent and the local protein-requirement class have different denotations, but xrefs asserts true own-source equivalence. A chemically accurate association requires typed grounding with curator-adjudicated activity-relative role.

## Findings

### F1: Chemical referent is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-61168.chemical-entity-equivalence.

The xref denotes a defined chemical entity, while the local record denotes a protein functional requirement. Correct chemical identity and a source siderophore role do not establish equality between those classes.

## Recommended Actions And Acceptance Checks

### A1

Change build in scripts/seed_chebi_cofactor.py to represent the exact chemical association through an accurately typed chemical_participants entry rather than a chemical-to-trait equality. Preserve CHEBI:61168 and its charge, stereochemical and metal-occupancy scope. ChemicalParticipant.role is required: adjudicate the activity-relative role, including non-substrate scope, rather than automatically converting a siderophore source assertion into independently verified COFACTOR. Preserve candidate provenance; do not move the equality to mapped_xrefs, merge conjugates, or promote protein examples. If role adjudication cannot support a typed participant, retain the chemical association as provenance with explicit uncertainty rather than inventing the required role.

- The chemical association no longer asserts chemical-to-protein-trait equivalence. Exact ligand state and source provenance remain auditable, with an explicitly adjudicated participant role. If no supported role can be adjudicated, the result retains provenance and uncertainty without inventing a typed participant.
- A focused source-transform fixture distinguishes free ligand, conjugate and ferric-complex scope where applicable. Use audited regeneration explicitly selecting the existing target; no unreviewed status or protein-qualification promotion occurs.
- For maintained writer changes run just audit-writers, just lint and just test with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml. Run full just validate-all before merging record changes. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured cofactor ancestor YAML | supports | The complete cofactor requirement ancestor above the siderophore parent was inspected. Local resolution does not certify chemical-role-to-protein-trait equivalence. |
| licence | https://www.ebi.ac.uk/chebi/about/; Chemical scope and Licensing section | supports | The official ChEBI chemical-scope and Licensing sections support chemical entities/roles and CC BY 4.0 attribution, not chemical-to-protein-trait equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS metadata reports comparison ontology version 256, loaded 2026-10-16. Original access UTC and digest are retained; neither original seed nor live-backend release is assigned from this metadata. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/61168/; Complete name/definition, aliases, chemical_data, default_structure, origins and outgoing relations | supports | CHEBI:61168 is neutral iron-free desferrimycobactin T, C46H75N5O10, charge 0. The structure fixes a saturated icosanoyl group, four specified stereocentres, a salicylate/oxazoline core, ester and N-hydroxylated lactam. It is a defined congener, not an R-group class covering every mycobactin acyl chain. The source asserts M. tuberculosis secretion and lipid solubility and assigns siderophore role. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:61168; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete identifier and source name/definition, with chemical annotations and synonym scopes inspected. Chemical resolution is not protein-trait equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected source response captured at the recorded UTC time | supports | CHEBI:23357 denotes the cofactor biochemical role, with biochemical role CHEBI:52206 as parent. It is not a molecule or a protein requirement class. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Inspected source response captured at the recorded UTC time | supports | CHEBI:26672 defines microbial iron(III)-chelating compounds for iron transport/sequestration; its current outgoing parents include cofactor, iron(3+) chelator and iron ionophore. This source-role ancestry supplies candidate context, not a qualified requirement for a particular protein. |
| context-46812 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/46812/; Complete chemical identity/structure, definition and outgoing relations | supports | The source 1,3-oxazoles parent resolves with a null definition and no fixed formula/structure, beneath oxazole. Its source-assigned relation is recorded without inventing a class definition. |
| context-24995 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24995/; Complete chemical identity/structure, definition and outgoing relations | supports | Lactam denotes a cyclic amide, including analogues with unsaturation or heteroatoms. This is structural classification. |
| context-33308 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33308/; Complete chemical identity/structure, definition and outgoing relations | supports | Carboxylic ester denotes a carboxylic-acid ester and has an R-group representation; it is chemical taxonomy rather than a protein requirement. |
| context-23445 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23445/; Complete chemical identity/structure, definition and outgoing relations | supports | Cyclic hydroxamic acid is a lactam bearing a hydroxy substituent on the amide nitrogen and is-a hydroxamic acid and lactam. |
| primary-10419938 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10419938%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and bibliographic record; no abstract returned | context_only | PMID:10419938. Iron acquisition and metabolism by mycobacteria; DOI:10.1128/jb.181.15.4443-4451.1999. The source-linked review identifier and bibliographic identity resolve, but the returned indexed record has no abstract. Its full text was not successfully retrieved, so no scientific assertion is supported by this bibliographic entry. |
| primary-8666910 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8666910%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:8666910. Exochelins of Mycobacterium tuberculosis remove iron from human iron-binding proteins and donate iron to mycobactins in the cell wall; DOI:10.1084/jem.183.4.1527. The complete abstract reports iron removal by purified desferri-exochelins and transfer by ferri-exochelins to cell-wall desferri-mycobactins, with polarity comparisons. These family/transport observations do not qualify an exact free-state non-substrate protein requirement. |
| primary-24415729 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24415729%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract response; full text captured separately as vesicle-fulltext | supports | PMID:24415729. Role for Mycobacterium tuberculosis membrane vesicles in iron acquisition; DOI:10.1128/JB.01090-13. The complete abstract reports increased vesicle release under iron limitation, mycobactin cargo and growth support for iron-starved bacteria. The separately inspected full text narrows the displayed lipid result to ferric congeners including 19:1, not the exact free saturated icosanoyl entry. |
| primary-35474308 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:35474308%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:35474308. A periplasmic cinched protein is required for siderophore secretion and virulence of Mycobacterium tuberculosis; DOI:10.1038/s41467-022-29873-6. The complete abstract reports reduced mycobactin and carboxymycobactin secretion in the rv0455c deletion mutant. This supports secretion at the reported family/strain level without resolving every exact acyl-chain and metal-state congener. |
| vesicle-fulltext | https://pmc.ncbi.nlm.nih.gov/articles/PMC3957709/; PMCID:PMC3957709; PMID:24415729; complete main text and figure legends, especially MV lipid content/Fig3 and MVs as iron transporters | supports | The inspected Methods, Results and Discussion report M. tuberculosis H37Rv vesicles from iron-limited culture supernatants, enrichment in Fe-loaded mycobactin and rescue of siderophore-deficient bacteria. Figure3 identifies a prominent 19:1 congener. This demonstrates that cell association and vesicle export coexist, but does not directly establish secretion of the exact iron-free saturated icosanoyl CHEBI:61168 species. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml; Executed 2026-10-21T11:10:58Z through 2026-10-21T11:10:59Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml; Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml; Executed 2026-10-21T11:10:59Z through 2026-10-21T11:10:59Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The source-linked 1999 review PMID:10419938 resolves bibliographically but its indexed abstract is absent and its attempted HTML delivery was a challenge; no scientific claim is grounded to that failed body. The 2014 vesicle article main text was successfully inspected through PMC HTML; its failed XML delivery is excluded. The 2022 secretion study was inspected through its complete indexed abstract only.
- Membrane association and vesicle export can coexist. Exact acyl-chain saturation, ferric occupancy and free-ligand state are not interchangeable; no unqualified contradiction of the source secretion statement is asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T111506Z-desferrimycobactin-t-chebi61168
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires desferrimycobactin T
started_at: '2026-10-21T11:07:48Z'
finished_at: '2026-10-21T11:15:06Z'
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
summary: The exact neutral saturated-icosanoyl desferrimycobactin T structure and
  source ancestry resolve. One confirmed major finding concerns chemical-to-trait
  equivalence. Positive secretion/vesicle-export evidence prevents a false cell-association
  contradiction, but exact free-congener secretion and protein requirement remain
  unresolved.
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
  - path: data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    sha256: aba73d5a8855cf4672002244e61f7d4e3733a2620365d12c3df84b09723e26c4
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
  selection: Path-order position 9 in batch 018. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
targets:
- kind: generated
  label: requires desferrimycobactin T
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_61168
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve CHEBI:61168 and the inspected chemical comparisons.
    Its direct siderophore role and the source siderophore-to-cofactor ancestry are
    verified. Resolution is chemical/provenance support, not protein-trait equivalence
    or per-protein qualification.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  evidence_ids:
  - chemical
  - chemical-ontology
  - licence
  - current-release
  - siderophore-role
  - cofactor-role
  - context-46812
  - context-24995
  - context-33308
  - context-23445
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:07:48Z'
  snapshot_sha256: aba73d5a8855cf4672002244e61f7d4e3733a2620365d12c3df84b09723e26c4
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
  accessed_at: '2026-10-21T11:07:48Z'
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
  accessed_at: '2026-10-21T11:07:48Z'
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
  accessed_at: '2026-10-21T11:07:48Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:07:48Z'
  snapshot_sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured cofactor ancestor YAML
  accessed_at: '2026-10-21T11:07:48Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: The complete cofactor requirement ancestor above the siderophore parent
    was inspected. Local resolution does not certify chemical-role-to-protein-trait
    equivalence.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Chemical scope and Licensing section
  summary: The official ChEBI chemical-scope and Licensing sections support chemical
    entities/roles and CC BY 4.0 attribution, not chemical-to-protein-trait equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The verified reused OLS metadata reports comparison ontology version 256,
    loaded 2026-10-16. Original access UTC and digest are retained; neither original
    seed nor live-backend release is assigned from this metadata.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/61168/
  accessed_at: '2026-10-21T11:08:06.851496Z'
  snapshot_sha256: 82396ce4798dc5d9edbe8e168a19748942393ba37c6ea503e523c526e89d4e8a
  support: supports
  locator: Complete name/definition, aliases, chemical_data, default_structure, origins
    and outgoing relations
  summary: CHEBI:61168 is neutral iron-free desferrimycobactin T, C46H75N5O10, charge
    0. The structure fixes a saturated icosanoyl group, four specified stereocentres,
    a salicylate/oxazoline core, ester and N-hydroxylated lactam. It is a defined
    congener, not an R-group class covering every mycobactin acyl chain. The source
    asserts M. tuberculosis secretion and lipid solubility and assigns siderophore
    role.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:61168
  accessed_at: '2026-10-21T11:08:05.321964Z'
  snapshot_sha256: 1315b18c00a3abf043fd0267d6963a475d437703ea547aa115fcc1ff5c78bccc
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete identifier and source name/definition,
    with chemical annotations and synonym scopes inspected. Chemical resolution is
    not protein-trait equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:23357 denotes the cofactor biochemical role, with biochemical role
    CHEBI:52206 as parent. It is not a molecule or a protein requirement class.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T09:02:57.586907Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: CHEBI:26672 defines microbial iron(III)-chelating compounds for iron transport/sequestration;
    its current outgoing parents include cofactor, iron(3+) chelator and iron ionophore.
    This source-role ancestry supplies candidate context, not a qualified requirement
    for a particular protein.
- evidence_id: context-46812
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/46812/
  accessed_at: '2026-10-21T11:08:48.015607Z'
  snapshot_sha256: 440aaf7d028685024765a3431911cd8c7d0a409f3eed2874d6098ead712592c1
  support: supports
  locator: Complete chemical identity/structure, definition and outgoing relations
  summary: The source 1,3-oxazoles parent resolves with a null definition and no fixed
    formula/structure, beneath oxazole. Its source-assigned relation is recorded without
    inventing a class definition.
- evidence_id: context-24995
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24995/
  accessed_at: '2026-10-21T11:08:47.973346Z'
  snapshot_sha256: 756b98d8f4522d63e5de0d229faca338b84ee6b76048309c5cfae75652b1ee1d
  support: supports
  locator: Complete chemical identity/structure, definition and outgoing relations
  summary: Lactam denotes a cyclic amide, including analogues with unsaturation or
    heteroatoms. This is structural classification.
- evidence_id: context-33308
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33308/
  accessed_at: '2026-10-21T11:08:47.247681Z'
  snapshot_sha256: d66dc82dfb3683a0ba8466ffbae9ad0f1b8cb17065f81ee7561f0cab2ea806df
  support: supports
  locator: Complete chemical identity/structure, definition and outgoing relations
  summary: Carboxylic ester denotes a carboxylic-acid ester and has an R-group representation;
    it is chemical taxonomy rather than a protein requirement.
- evidence_id: context-23445
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23445/
  accessed_at: '2026-10-21T11:08:48.271961Z'
  snapshot_sha256: fcf0e50331f34fd6345276da4b27d8482da66c1ce189d67ad66961f83f7c4d79
  support: supports
  locator: Complete chemical identity/structure, definition and outgoing relations
  summary: Cyclic hydroxamic acid is a lactam bearing a hydroxy substituent on the
    amide nitrogen and is-a hydroxamic acid and lactam.
- evidence_id: primary-10419938
  kind: database
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10419938%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T11:08:49.626064Z'
  snapshot_sha256: 5b94eb8a774012a5f007e89c37b2c83964b6e7382b6a590d55b35b9e8d9a160c
  support: context_only
  locator: Verified PMID/DOI and bibliographic record; no abstract returned
  summary: PMID:10419938. Iron acquisition and metabolism by mycobacteria; DOI:10.1128/jb.181.15.4443-4451.1999.
    The source-linked review identifier and bibliographic identity resolve, but the
    returned indexed record has no abstract. Its full text was not successfully retrieved,
    so no scientific assertion is supported by this bibliographic entry.
- evidence_id: primary-8666910
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:8666910%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T11:08:49.570752Z'
  snapshot_sha256: f14460d9a3f7a2add086abeec02f52a1a2fb85b6869ccccc6348cb17fee09f89
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:8666910. Exochelins of Mycobacterium tuberculosis remove iron from
    human iron-binding proteins and donate iron to mycobactins in the cell wall; DOI:10.1084/jem.183.4.1527.
    The complete abstract reports iron removal by purified desferri-exochelins and
    transfer by ferri-exochelins to cell-wall desferri-mycobactins, with polarity
    comparisons. These family/transport observations do not qualify an exact free-state
    non-substrate protein requirement.
- evidence_id: primary-24415729
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24415729%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T11:08:49.711789Z'
  snapshot_sha256: c4064c3622cef71316f224b6edf8a578afadc22be8e17773f242d5beff30a973
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract response; full text captured
    separately as vesicle-fulltext
  summary: PMID:24415729. Role for Mycobacterium tuberculosis membrane vesicles in
    iron acquisition; DOI:10.1128/JB.01090-13. The complete abstract reports increased
    vesicle release under iron limitation, mycobactin cargo and growth support for
    iron-starved bacteria. The separately inspected full text narrows the displayed
    lipid result to ferric congeners including 19:1, not the exact free saturated
    icosanoyl entry.
- evidence_id: primary-35474308
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:35474308%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T11:08:49.772654Z'
  snapshot_sha256: 546dc2b2535a73ae295e7e7219c3c08a545cf1ee47e1586b8c8dc7d81cfd6090
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:35474308. A periplasmic cinched protein is required for siderophore
    secretion and virulence of Mycobacterium tuberculosis; DOI:10.1038/s41467-022-29873-6.
    The complete abstract reports reduced mycobactin and carboxymycobactin secretion
    in the rv0455c deletion mutant. This supports secretion at the reported family/strain
    level without resolving every exact acyl-chain and metal-state congener.
- evidence_id: vesicle-fulltext
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC3957709/
  accessed_at: '2026-10-21T11:08:50.243130Z'
  snapshot_sha256: def5ea418295caa50b45c7d17b1abf9b11e892f6b080379e7458110081b0f7ca
  support: supports
  locator: PMCID:PMC3957709; PMID:24415729; complete main text and figure legends,
    especially MV lipid content/Fig3 and MVs as iron transporters
  summary: The inspected Methods, Results and Discussion report M. tuberculosis H37Rv
    vesicles from iron-limited culture supernatants, enrichment in Fe-loaded mycobactin
    and rescue of siderophore-deficient bacteria. Figure3 identifies a prominent 19:1
    congener. This demonstrates that cell association and vesicle export coexist,
    but does not directly establish secretion of the exact iron-free saturated icosanoyl
    CHEBI:61168 species.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  locator: Executed 2026-10-21T11:10:58Z through 2026-10-21T11:10:59Z; exit 0
  accessed_at: '2026-10-21T11:10:59Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
  locator: Executed 2026-10-21T11:10:59Z through 2026-10-21T11:10:59Z; exit 0
  accessed_at: '2026-10-21T11:10:59Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source chemical is an iron-free neutral ligand with a fixed saturated
    twenty-carbon acyl group and specified stereochemistry. The name does not license
    replacing that structure with any acyl-chain congener, a ferric complex or soluble
    carboxymycobactin.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  topic: Mycobactin T exact ligand and acyl-chain scope
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: Cell-wall association in the exochelin transfer study coexists with positive
    mycobactin secretion/vesicle-export evidence. The full vesicle paper reports ferric
    congeners, including 19:1. Thus cell association does not demonstrate that secretion
    is false, while the exact iron-free saturated icosanoyl entry is not independently
    resolved by these experiments.
  evidence_ids:
  - primary-8666910
  - primary-24415729
  - primary-35474308
  - vesicle-fulltext
  - chemical
  topic: Mycobactin localization and vesicle-export context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-6
- area: evidence
  outcome: unknown
  summary: The source-specific secretion statement is authentic, but the inspected
    experiments do not establish the exact free saturated CHEBI:61168 congener as
    the exported species or an obligatory non-substrate protein cofactor. This limited
    coverage is not a demonstrated secretion contradiction.
  evidence_ids:
  - record
  - chemical
  - vesicle-fulltext
  - primary-35474308
  topic: Exact-congener secretion and protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-7
- area: provenance
  outcome: supported
  summary: The current official source supports the copied chemical definition and
    direct siderophore role; the protein-requirement wrapper is maintained ChEBI-seeder
    synthesis. Licence and comparison release are traceable; the original seed release
    remains unknown.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  topic: Chemical definition and maintained-source provenance
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The complete local siderophore-to-cofactor requirement ancestry resolves,
    and current source siderophore is-a cofactor is verified. These source-role relations
    supply candidate context; chemical classification and role ancestry do not establish
    protein-trait equality or exact physiological dependence.
  evidence_ids:
  - record
  - local-parent-1
  - local-ancestor
  - siderophore-role
  - cofactor-role
  - chemical
  - schema
  topic: Siderophore source ancestry versus requirement hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-9
- area: representation
  outcome: unknown
  summary: The proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class has not
    been independently qualified for the exact chemical state and activity-relative
    non-substrate role. Iron binding, transport, biosynthesis or source-role ancestry
    alone is insufficient; these contexts also do not prove absence of other cofactor
    roles.
  evidence_ids:
  - record
  - schema
  - chemical
  - siderophore-role
  - owner
  topic: Activity-relative protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: The exact ChEBI chemical referent and the local protein-requirement class
    have different denotations, but xrefs asserts true own-source equivalence. A chemically
    accurate association requires typed grounding with curator-adjudicated activity-relative
    role.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  topic: Chemical denotation versus protein-trait equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-61168.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical referent is asserted equivalent to a protein requirement
  description: The xref denotes a defined chemical entity, while the local record
    denotes a protein functional requirement. Correct chemical identity and a source
    siderophore role do not establish equality between those classes.
  evidence_ids:
  - record
  - schema
  - chemical
  - owner
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Chemical identity is supported, but chemical denotation and
    protein-requirement denotation differ; the semantic mismatch is a major grounding
    defect.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: 'Change build in scripts/seed_chebi_cofactor.py to represent the exact
    chemical association through an accurately typed chemical_participants entry rather
    than a chemical-to-trait equality. Preserve CHEBI:61168 and its charge, stereochemical
    and metal-occupancy scope. ChemicalParticipant.role is required: adjudicate the
    activity-relative role, including non-substrate scope, rather than automatically
    converting a siderophore source assertion into independently verified COFACTOR.
    Preserve candidate provenance; do not move the equality to mapped_xrefs, merge
    conjugates, or promote protein examples. If role adjudication cannot support a
    typed participant, retain the chemical association as provenance with explicit
    uncertainty rather than inventing the required role.'
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_61168
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The chemical association no longer asserts chemical-to-protein-trait equivalence.
    Exact ligand state and source provenance remain auditable, with an explicitly
    adjudicated participant role. If no supported role can be adjudicated, the result
    retains provenance and uncertainty without inventing a typed participant.
  - A focused source-transform fixture distinguishes free ligand, conjugate and ferric-complex
    scope where applicable. Use audited regeneration explicitly selecting the existing
    target; no unreviewed status or protein-qualification promotion occurs.
  - For maintained writer changes run just audit-writers, just lint and just test
    with a focused source-transform fixture. Run just validate data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml.
    Run full just validate-all before merging record changes. Capture changed inputs
    and save a fresh validated review; do not overwrite this observation.
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
- The source-linked 1999 review PMID:10419938 resolves bibliographically but its indexed
  abstract is absent and its attempted HTML delivery was a challenge; no scientific
  claim is grounded to that failed body. The 2014 vesicle article main text was successfully
  inspected through PMC HTML; its failed XML delivery is excluded. The 2022 secretion
  study was inspected through its complete indexed abstract only.
- Membrane association and vesicle export can coexist. Exact acyl-chain saturation,
  ferric occupancy and free-ligand state are not interchangeable; no unqualified contradiction
  of the source secretion statement is asserted.
tags:
- unreviewed-path-order
- batch-018
- chebi-cofactor
```
