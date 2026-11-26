# Review of requires coenzyme F420-6

- Review: 20261021T105035Z-coenzyme-f420-6-chebi63314
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:40:46Z
- Finished UTC: 2026-10-21T10:50:35Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The six-glutamate F420 chemical identity is supported. Two confirmed major findings concern chemical-to-protein-trait equivalence and a disproven M. tuberculosis-exclusive definition. Exact-state protein dependence remains unqualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 016. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50) covers 148 record paths, leaving 429211 before this batch. 16 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml | generated | requires coenzyme F420-6 |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_63314 | CHEBI:63314 resolves and is nonobsolete. Its actual structure, direct coenzyme role, structural/functional parents and reduced counterpart were inspected. Complete primary abstracts support bounded occurrence/redox context; PMC165758 main text independently reports γ-F420-6 outside M. tuberculosis. The local coenzyme parent and cofactor ancestor were read. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The local label denotes a proposed reusable protein requirement for coenzyme F420-6, while CHEBI:63314 denotes its chemical referent. Those are distinct classes.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The maintained ChEBI role seeder synthesizes the requirement wrapper and appends source chemical background. Current source licensing supports CC BY 4.0. OLS 256 and current backend snapshots do not identify the original seed release.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

CHEBI:63314 in xrefs denotes a chemical entity, while the target denotes a protein functional requirement. The schema requires true own-source equivalence; a chemical association is a different predicate.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The direct source role explains the local broader requirement parent. Chemical is-a, functional-parent and conjugacy relations describe chemicals and are not automatically protein-class parents or equivalent requirements. This one-record review does not certify the captured parent(s).

### F420-6 chain length, γ linkages and redox state

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

CHEBI:63314 is C49H64N9O30P, net 0, with six L-glutamates and five interglutamate γ-amide bonds on the oxidized deazaflavin-ribityl/lactyl-phosphate scaffold. Its two-hydrogen-reduced counterpart is a distinct chemical state. The primary NMR/HPLC study and PMC165758 Table 1 provide non-M. tuberculosis occurrences of F420-6.

### Requirement scope and scientific status

scope: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

The copied description makes F420-6 specific to M. tuberculosis. The primary structural study directly identifies F420-6 in M. smegmatis and reports it in several other mycobacteria. This refutes species exclusivity without asserting that every mycobacterium, strain or F420-dependent protein uses the six-glutamate form.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_63314.

Chemical occurrence, FGD1 binding to unspecified F420, and reduced-F420 polyglutamylation do not qualify an exact neutral oxidized F420-6 non-substrate requirement for any protein. Chain length, redox state, protonation and activity-relative role require specific evidence; the category is not validated by source coenzyme membership alone.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-63314.chemical-entity-equivalence.

The local requires-F420-6 class denotes a protein functional requirement, while CHEBI:63314 denotes the neutral oxidized six-glutamate chemical entity. xrefs asserts true equivalence between those different denotations.

### F2: F420-6 is incorrectly described as specific to M. tuberculosis

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-63314.mtb-exclusive-scope.

The target copies the source claim that F420-6 is specific to M. tuberculosis. The inspected primary structural study directly characterizes F420-6 from M. smegmatis and reports the same chain-length form in M. bovis BCG, M. fortuitum and M. avium as well as M. tuberculosis. PMC165758 also detects γ-F420-6 in M. smegmatis and other tested extracts. The taxonomic restriction therefore excludes demonstrated occurrences.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:63314 from trait-equivalence xrefs and retain accurate chemical-source provenance. For a retained proposed requirement, use typed chemical grounding only after the exact chemical referent and activity-relative non-substrate role are supported; any COFACTOR participant must denote that molecular entity, not a role class. Preserve SEEDED candidate status. Do not use mapped_xrefs for this own-source association or promote a protein from biosynthesis, binding or chemical-role membership alone.

- The regenerated target preserves resolved chemical provenance without asserting CHEBI:63314 chemical-to-protein-trait equality.
- Preserve six-glutamate length, encoded γ linkages and stereochemistry, and distinguish reduced versus oxidized and protonated versus deprotonated forms; do not infer exact-state dependence from unspecified F420 binding or biosynthesis.
- The activity-relative non-substrate criterion is explicit before any COFACTOR participant or protein qualification; no unreviewed protein example or automatic source-role promotion is introduced.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml. These future acceptance checks do not imply the finding is already fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing record through an audited route, run full-corpus just validate-all before merging record changes, and save a fresh structured scientific review against the changed bytes.

### A2

Replace the species-exclusive background in maintained source-text handling or an explicit curated override with a chemically defined six-glutamate description and bounded supported occurrence wording. Preserve the original upstream text/provenance and regenerate the scoped target. Keep this chemical-occurrence correction separate from protein qualification.

- The regenerated definition no longer restricts F420-6 to M. tuberculosis; a structural description preserves the exact chemical state.
- Any occurrence examples retain the taxa and experimental scope actually supported and do not assert universality or exclude untested organisms.
- A focused source-transform fixture prevents reintroduction of the disproven exclusivity, while source provenance remains distinguishable.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml. These future acceptance checks do not imply the finding is already fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing record through an audited route, run full-corpus just validate-all before merging record changes, and save a fresh structured scientific review against the changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The official Introduction defines ChEBI as a database/ontology of chemical entities. Its Licensing section makes website data available under CC BY 4.0. This supports source-data licensing, not the local protein-requirement synthesis. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded on 2026-10-16. This is the comparison ontology version, not a release assignment to the live backend or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_63314; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:63314 to nonobsolete coenzyme F420-6. The actual description and synonyms were inspected; resolution alone does not establish coherence with all source structures or protein-trait equivalence. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/63314/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response was inspected, including the name, chemical definition, formula, net charge, stereochemical structure, aliases, source citations and outgoing relations. Its role assertion supplies chemical context, not a qualified protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition, chemical_data/default_structure and outgoing relations | supports | The official cofactor entry is a biochemical role for an organic molecule or ion required by an enzyme. Its outgoing is-a parent is biochemical role; it is not itself a concrete molecule. |
| specific-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; definition and outgoing relations | supports | The coenzyme role describes a dissociable donor or acceptor of groups/electrons and is-a cofactor. This source role is distinct from a non-substrate protein requirement. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | The complete captured cofactor-requirement ancestor was read. Its locally synthesized requirement predicate and ChEBI role xref are distinct; this review does not certify that parent. |
| functional-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/43034/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The source functional parent identifies the deazaflavin-ribityl scaffold, distinct from the complete six-glutamate molecule. |
| reduced-form | https://www.ebi.ac.uk/chebi/backend/api/public/compound/63313/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The reduced counterpart is C49H66N9O30P, net 0, with a 1,5-dihydro definition and functional-parent relation to 63314. Its separate taxonomic wording is not used to support exclusivity. |
| primary-occurrence | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11479701%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID11479701; DOI10.1007/s002030100290; complete indexed abstract | supports | The complete primary abstract reports proton NMR, amino-acid analysis and HPLC of M. smegmatis F420, identifying five- and six-glutamate forms. Peptidase results suggest γ bonds. HPLC also identifies F420-5/6 in M. tuberculosis, M. bovis BCG and M. fortuitum, and F420-5/6/7 in M. avium. These measured occurrences contradict a species-exclusive F420-6 definition. |
| primary-fgd1 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18434308%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID18434308; DOI10.1074/jbc.M801854200; complete indexed abstract | supports | The complete source-linked abstract reports apo and F420/citrate-bound M. tuberculosis FGD1 structures and F420 reduction in glucose-6-phosphate metabolism. It does not specify a six-glutamate ligand in the abstract and therefore does not qualify exact F420-6 dependence. |
| primary-polyglutamylation | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A30249701%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID30249701; DOI10.1128/JB.00375-18; complete indexed abstract | supports | The complete primary abstract reports that purified M. tuberculosis FbiB adds up to seven glutamates efficiently when F420 is supplied in its two-electron-reduced state, with genetic analysis in M. bovis BCG and M. smegmatis. This is biosynthetic/redox context, not exact neutral oxidized F420-6 requirement evidence. |
| primary-linkage | https://pmc.ncbi.nlm.nih.gov/articles/PMC165758/; PMCIDPMC165758; PMID12867481; DOI10.1128/JB.185.15.4662-4665.2003; main text, Table 1, peptidase experiments and Fig. 1 caption | supports | The complete primary main text, Table 1 and figure caption were inspected. Peptidase specificity, chromatography and chiral amino-acid analysis support γ-linked F420 chains capped with one terminal α-linked L-glutamate in the tested M. jannaschii extract; α-F420-3 is distinguished from γ-F420-3. The γ-F420-2 discussion identifies the terminal γ bond. These observations establish linkage nomenclature, not a particular free-ion microstate or protein qualification. |
| pyrimidoquinolines | https://www.ebi.ac.uk/chebi/backend/api/public/compound/59535/; name, definition and outgoing relations | supports | The pyrimidoquinoline structural class is a quinoline ring fused to a pyrimidine ring. This is chemical taxonomy, not a protein-requirement parent. |
| ribitol-phosphate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26554/; name, definition and outgoing relations | supports | The ribitol-phosphate chemical class resolves with a null definition and a pentitol-phosphate parent. This is chemical taxonomy, not a protein-requirement parent. |
| oligopeptide | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25676/; name, definition and outgoing relations | supports | The oligopeptide class concerns a peptide with a relatively small number of amino acids. This is chemical taxonomy, not a protein-requirement parent. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; Executed 2026-10-21T10:44:02Z through 2026-10-21T10:44:04Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml; Executed 2026-10-21T10:41:11Z through 2026-10-21T10:43:37Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml; Executed 2026-10-21T10:44:04Z through 2026-10-21T10:44:04Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:43:37Z through 2026-10-21T10:43:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMIDs 11479701, 18434308 and 30249701 were inspected at complete indexed-abstract level. PMC165758 full main text/Table 1 was inspected. The FGD1 abstract does not identify the bound F420 chain length. Biosynthesis using reduced F420 is not direct evidence for requirement for the exact neutral oxidized form.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T105035Z-coenzyme-f420-6-chebi63314
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires coenzyme F420-6
started_at: '2026-10-21T10:40:46Z'
finished_at: '2026-10-21T10:50:35Z'
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
summary: The six-glutamate F420 chemical identity is supported. Two confirmed major
  findings concern chemical-to-protein-trait equivalence and a disproven M. tuberculosis-exclusive
  definition. Exact-state protein dependence remains unqualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
    sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
    sha256: 78fa2621b1ba586c8802a898f83847a11aa4b3b1ac8dfdd40f264f31de5a734d
    role: target
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
  selection: Path-order position 4 in batch 016. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50)
    covers 148 record paths, leaving 429211 before this batch. 16 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
targets:
- kind: generated
  label: requires coenzyme F420-6
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_63314
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml
    data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:63314 resolves and is nonobsolete. Its actual structure, direct coenzyme
    role, structural/functional parents and reduced counterpart were inspected. Complete
    primary abstracts support bounded occurrence/redox context; PMC165758 main text
    independently reports γ-F420-6 outside M. tuberculosis. The local coenzyme parent
    and cofactor ancestor were read.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - specific-role
  - functional-parent
  - reduced-form
  - primary-occurrence
  - primary-fgd1
  - primary-polyglutamylation
  - primary-linkage
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:40:46Z'
  snapshot_sha256: 78fa2621b1ba586c8802a898f83847a11aa4b3b1ac8dfdd40f264f31de5a734d
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
  accessed_at: '2026-10-21T10:40:46Z'
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
  accessed_at: '2026-10-21T10:40:46Z'
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
  accessed_at: '2026-10-21T10:40:46Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:40:46Z'
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
  summary: The official Introduction defines ChEBI as a database/ontology of chemical
    entities. Its Licensing section makes website data available under CC BY 4.0.
    This supports source-data licensing, not the local protein-requirement synthesis.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS metadata reports ChEBI version 256 loaded on 2026-10-16. This is the
    comparison ontology version, not a release assignment to the live backend or the
    original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_63314
  accessed_at: '2026-10-21T10:41:36.936775Z'
  snapshot_sha256: f34f98dabd502fbf4506ec492757e37b4813e85250896bd5cde95377b23914ca
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:63314 to nonobsolete coenzyme F420-6. The actual description
    and synonyms were inspected; resolution alone does not establish coherence with
    all source structures or protein-trait equivalence.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/63314/
  accessed_at: '2026-10-21T10:41:36.991533Z'
  snapshot_sha256: e210e681f7a7363f8c8418e52c812ed9487dd4a4872f97eb49a115f3e656e412
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The complete official response was inspected, including the name, chemical
    definition, formula, net charge, stereochemical structure, aliases, source citations
    and outgoing relations. Its role assertion supplies chemical context, not a qualified
    protein requirement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition, chemical_data/default_structure and outgoing relations
  summary: The official cofactor entry is a biochemical role for an organic molecule
    or ion required by an enzyme. Its outgoing is-a parent is biochemical role; it
    is not itself a concrete molecule.
- evidence_id: specific-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T10:10:09.158129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: definition and outgoing relations
  summary: The coenzyme role describes a dissociable donor or acceptor of groups/electrons
    and is-a cofactor. This source role is distinct from a non-substrate protein requirement.
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T10:40:46Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: The complete captured cofactor-requirement ancestor was read. Its locally
    synthesized requirement predicate and ChEBI role xref are distinct; this review
    does not certify that parent.
- evidence_id: functional-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/43034/
  accessed_at: '2026-10-21T10:43:24.285676Z'
  snapshot_sha256: 36431188feaa730d422b5f4cee6563eb23906cc8fc25488b065d1e068c0603ad
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The source functional parent identifies the deazaflavin-ribityl scaffold,
    distinct from the complete six-glutamate molecule.
- evidence_id: reduced-form
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/63313/
  accessed_at: '2026-10-21T10:43:24.950615Z'
  snapshot_sha256: 1d4b81875b722ed6a9d6d19907e24b575534c6e8aba61a854911d452a9d49def
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The reduced counterpart is C49H66N9O30P, net 0, with a 1,5-dihydro definition
    and functional-parent relation to 63314. Its separate taxonomic wording is not
    used to support exclusivity.
- evidence_id: primary-occurrence
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11479701%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T10:43:24.906992Z'
  snapshot_sha256: befc6139d600ae926c9ea69c10bc6b9bb15edd952dea1d84a683a1e5dee0d97e
  support: supports
  locator: PMID11479701; DOI10.1007/s002030100290; complete indexed abstract
  summary: The complete primary abstract reports proton NMR, amino-acid analysis and
    HPLC of M. smegmatis F420, identifying five- and six-glutamate forms. Peptidase
    results suggest γ bonds. HPLC also identifies F420-5/6 in M. tuberculosis, M.
    bovis BCG and M. fortuitum, and F420-5/6/7 in M. avium. These measured occurrences
    contradict a species-exclusive F420-6 definition.
- evidence_id: primary-fgd1
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18434308%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T10:43:25.518848Z'
  snapshot_sha256: cc9c8031ee9e04a104cfb741c4c9959e3afe195a828d97d23e2feccd65833a1f
  support: supports
  locator: PMID18434308; DOI10.1074/jbc.M801854200; complete indexed abstract
  summary: The complete source-linked abstract reports apo and F420/citrate-bound
    M. tuberculosis FGD1 structures and F420 reduction in glucose-6-phosphate metabolism.
    It does not specify a six-glutamate ligand in the abstract and therefore does
    not qualify exact F420-6 dependence.
- evidence_id: primary-polyglutamylation
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A30249701%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T10:43:25.640682Z'
  snapshot_sha256: 0b719052a682258b9b4941f3dc92b72b20415a9cbd89a1db565657818b7f18b5
  support: supports
  locator: PMID30249701; DOI10.1128/JB.00375-18; complete indexed abstract
  summary: The complete primary abstract reports that purified M. tuberculosis FbiB
    adds up to seven glutamates efficiently when F420 is supplied in its two-electron-reduced
    state, with genetic analysis in M. bovis BCG and M. smegmatis. This is biosynthetic/redox
    context, not exact neutral oxidized F420-6 requirement evidence.
- evidence_id: primary-linkage
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC165758/
  accessed_at: '2026-10-21T10:26:33.291195Z'
  snapshot_sha256: 20b6a0ffab1532ce30e9e47336c3cf5f5abe816291f30272c497785587c9b901
  support: supports
  locator: PMCIDPMC165758; PMID12867481; DOI10.1128/JB.185.15.4662-4665.2003; main
    text, Table 1, peptidase experiments and Fig. 1 caption
  summary: The complete primary main text, Table 1 and figure caption were inspected.
    Peptidase specificity, chromatography and chiral amino-acid analysis support γ-linked
    F420 chains capped with one terminal α-linked L-glutamate in the tested M. jannaschii
    extract; α-F420-3 is distinguished from γ-F420-3. The γ-F420-2 discussion identifies
    the terminal γ bond. These observations establish linkage nomenclature, not a
    particular free-ion microstate or protein qualification.
- evidence_id: pyrimidoquinolines
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/59535/
  accessed_at: '2026-10-21T10:43:24.144662Z'
  snapshot_sha256: d27052cd775aa577f332cb31624c4c95126a7cf840caedbe6b2783db7061056f
  support: supports
  locator: name, definition and outgoing relations
  summary: The pyrimidoquinoline structural class is a quinoline ring fused to a pyrimidine
    ring. This is chemical taxonomy, not a protein-requirement parent.
- evidence_id: ribitol-phosphate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26554/
  accessed_at: '2026-10-21T10:43:24.204077Z'
  snapshot_sha256: a5c0253eba0328e381567cc76d638b183c944b4acd6b6eae5380b370b7109694
  support: supports
  locator: name, definition and outgoing relations
  summary: The ribitol-phosphate chemical class resolves with a null definition and
    a pentitol-phosphate parent. This is chemical taxonomy, not a protein-requirement
    parent.
- evidence_id: oligopeptide
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25676/
  accessed_at: '2026-10-21T10:43:25.838598Z'
  snapshot_sha256: a1216acd2eb2462f50eb5cfa267472ab15ab2c5fc36eef0728f8f2eac9b967c1
  support: supports
  locator: name, definition and outgoing relations
  summary: The oligopeptide class concerns a peptide with a relatively small number
    of amino acids. This is chemical taxonomy, not a protein-requirement parent.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  locator: Executed 2026-10-21T10:44:02Z through 2026-10-21T10:44:04Z; exit 0
  accessed_at: '2026-10-21T10:44:04Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-chebi16848.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-5-chebi59539.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-3-chebi59537.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-4-chebi60540.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-f430-chebi28265.yaml
    data/traits/function/cofactor_requirement/chebi/coenzyme-m-chebi17905.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-q-chebi16389.yaml
    data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml data/traits/function/cofactor_requirement/chebi/com-chebi17755.yaml
  locator: Executed 2026-10-21T10:41:11Z through 2026-10-21T10:43:37Z; exit 0
  accessed_at: '2026-10-21T10:43:37Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml
  locator: Executed 2026-10-21T10:44:04Z through 2026-10-21T10:44:04Z; exit 0
  accessed_at: '2026-10-21T10:44:04Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T10:43:37Z through 2026-10-21T10:43:38Z; exit 0
  accessed_at: '2026-10-21T10:43:38Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The local label denotes a proposed reusable protein requirement for coenzyme
    F420-6, while CHEBI:63314 denotes its chemical referent. Those are distinct classes.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: The maintained ChEBI role seeder synthesizes the requirement wrapper and
    appends source chemical background. Current source licensing supports CC BY 4.0.
    OLS 256 and current backend snapshots do not identify the original seed release.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: grounding
  outcome: concern
  summary: CHEBI:63314 in xrefs denotes a chemical entity, while the target denotes
    a protein functional requirement. The schema requires true own-source equivalence;
    a chemical association is a different predicate.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-7
  topic: Chemical association versus trait equivalence
- area: consistency
  outcome: supported
  summary: The direct source role explains the local broader requirement parent. Chemical
    is-a, functional-parent and conjugacy relations describe chemicals and are not
    automatically protein-class parents or equivalent requirements. This one-record
    review does not certify the captured parent(s).
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - cofactor-role
  - chemical-role
  - local-ancestor
  - specific-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-8
  topic: Chemical-role and protein-trait hierarchy
- area: evidence
  outcome: supported
  summary: CHEBI:63314 is C49H64N9O30P, net 0, with six L-glutamates and five interglutamate
    γ-amide bonds on the oxidized deazaflavin-ribityl/lactyl-phosphate scaffold. Its
    two-hydrogen-reduced counterpart is a distinct chemical state. The primary NMR/HPLC
    study and PMC165758 Table 1 provide non-M. tuberculosis occurrences of F420-6.
  evidence_ids:
  - chemical-role
  - functional-parent
  - reduced-form
  - primary-occurrence
  - primary-linkage
  topic: F420-6 chain length, γ linkages and redox state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-9
- area: scope
  outcome: concern
  summary: The copied description makes F420-6 specific to M. tuberculosis. The primary
    structural study directly identifies F420-6 in M. smegmatis and reports it in
    several other mycobacteria. This refutes species exclusivity without asserting
    that every mycobacterium, strain or F420-dependent protein uses the six-glutamate
    form.
  evidence_ids:
  - record
  - chemical-role
  - primary-occurrence
  - primary-linkage
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-10
  topic: Requirement scope and scientific status
- area: representation
  outcome: unknown
  summary: Chemical occurrence, FGD1 binding to unspecified F420, and reduced-F420
    polyglutamylation do not qualify an exact neutral oxidized F420-6 non-substrate
    requirement for any protein. Chain length, redox state, protonation and activity-relative
    role require specific evidence; the category is not validated by source coenzyme
    membership alone.
  evidence_ids:
  - record
  - schema
  - specific-role
  - primary-fgd1
  - primary-polyglutamylation
  - chemical-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-63314.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-F420-6 class denotes a protein functional requirement,
    while CHEBI:63314 denotes the neutral oxidized six-glutamate chemical entity.
    xrefs asserts true equivalence between those different denotations.
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
  normalization_reason: A molecular entity and a protein functional requirement have
    different denotations; source resolution and chemical role membership do not establish
    equivalence.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-63314.mtb-exclusive-scope
  category: scope
  severity: major
  title: F420-6 is incorrectly described as specific to M. tuberculosis
  description: The target copies the source claim that F420-6 is specific to M. tuberculosis.
    The inspected primary structural study directly characterizes F420-6 from M. smegmatis
    and reports the same chain-length form in M. bovis BCG, M. fortuitum and M. avium
    as well as M. tuberculosis. PMC165758 also detects γ-F420-6 in M. smegmatis and
    other tested extracts. The taxonomic restriction therefore excludes demonstrated
    occurrences.
  evidence_ids:
  - record
  - chemical-role
  - primary-occurrence
  - primary-linkage
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: A species-exclusive definition excludes chemically identified
    occurrences in other organisms; this is material scope restriction rather than
    a stylistic taxon mention.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:63314
    from trait-equivalence xrefs and retain accurate chemical-source provenance. For
    a retained proposed requirement, use typed chemical grounding only after the exact
    chemical referent and activity-relative non-substrate role are supported; any
    COFACTOR participant must denote that molecular entity, not a role class. Preserve
    SEEDED candidate status. Do not use mapped_xrefs for this own-source association
    or promote a protein from biosynthesis, binding or chemical-role membership alone.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves resolved chemical provenance without asserting
    CHEBI:63314 chemical-to-protein-trait equality.
  - Preserve six-glutamate length, encoded γ linkages and stereochemistry, and distinguish
    reduced versus oxidized and protonated versus deprotonated forms; do not infer
    exact-state dependence from unspecified F420 binding or biosynthesis.
  - The activity-relative non-substrate criterion is explicit before any COFACTOR
    participant or protein qualification; no unreviewed protein example or automatic
    source-role promotion is introduced.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml.
    These future acceptance checks do not imply the finding is already fixed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing record
    through an audited route, run full-corpus just validate-all before merging record
    changes, and save a fresh structured scientific review against the changed bytes.
- action_id: A2
  description: Replace the species-exclusive background in maintained source-text
    handling or an explicit curated override with a chemically defined six-glutamate
    description and bounded supported occurrence wording. Preserve the original upstream
    text/provenance and regenerate the scoped target. Keep this chemical-occurrence
    correction separate from protein qualification.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_63314
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated definition no longer restricts F420-6 to M. tuberculosis; a structural
    description preserves the exact chemical state.
  - Any occurrence examples retain the taxa and experimental scope actually supported
    and do not assert universality or exclude untested organisms.
  - A focused source-transform fixture prevents reintroduction of the disproven exclusivity,
    while source provenance remains distinguishable.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-6-chebi63314.yaml.
    These future acceptance checks do not imply the finding is already fixed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing record
    through an audited route, run full-corpus just validate-all before merging record
    changes, and save a fresh structured scientific review against the changed bytes.
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
- PMIDs 11479701, 18434308 and 30249701 were inspected at complete indexed-abstract
  level. PMC165758 full main text/Table 1 was inspected. The FGD1 abstract does not
  identify the bound F420 chain length. Biosynthesis using reduced F420 is not direct
  evidence for requirement for the exact neutral oxidized form.
tags:
- unreviewed-path-order
- batch-016
- chebi-cofactor
```
