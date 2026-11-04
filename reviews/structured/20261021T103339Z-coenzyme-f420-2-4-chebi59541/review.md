# Review of requires coenzyme γ-F420-2(4−)

- Review: 20261021T103339Z-coenzyme-f420-2-4-chebi59541
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T10:24:38Z
- Finished UTC: 2026-10-21T10:33:39Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Chemical identity and current source coenzyme-role context are supported for coenzyme gamma-F420-2(4−). One confirmed major finding concerns chemical-to-protein-trait equivalence in xrefs. Exact physiological or per-protein requirement is not independently qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 015. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f) covers 138 record paths, leaving 429221 before this batch. 15 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml | generated | requires coenzyme γ-F420-2(4−) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59541 | CHEBI:59541 resolves in current official backend and OLS responses. Its direct coenzyme role, coenzyme-to-cofactor ancestry, and cited chemical context entries resolve. These relations establish source chemical context, not equivalent protein-trait identity or a qualified protein requirement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical connectivity and biosynthetic evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

Source structures and inspected primary ligation/chain analyses support the stated chemical connectivity and bounded biosynthetic context. The source-cited CofD papers concern precursor chemistry. No exact reviewed protonation state, universal chain preference, physiological dominance or protein member is independently qualified. Substrate/product context is not negative evidence against additional cofactor uses.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The tetraanion definition agrees with one phosphate and three carboxyl deprotonations of the two-glutamyl parent. Gamma specifies the interglutamate amide linkage, not an ester, and does not denote every terminal-alpha-linked F420 analogue. Its exact charge, chain length and stereochemistry remain distinct from related chemical states.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The chemical definition and direct coenzyme role match current ChEBI; the protein-requirement wrapper is maintained generator synthesis. Licence and current comparison release are traceable, while the exact seed release and independently qualified protein requirement remain unknown.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The captured local coenzyme requirement parent and cofactor ancestor resolve. Current direct coenzyme role and coenzyme-to-cofactor ancestry support candidate hierarchy context; functional-parent, chemical is-a and conjugate relations are kept distinct from protein-trait subclass semantics. Parent xref correctness is not certified.

### FUNCTION cofactor requirement representation

representation: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT class and remains SEEDED. Source roles are candidate context, and no experimental handling, binding or metabolic association is automatically promoted to a required protein cofactor.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59541.

CHEBI:59541 identifies a chemical entity, whereas the local record denotes a protein functional requirement for it. xrefs asserts true equivalence; chemical_participants permits a typed chemical association.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-59541.chemical-entity-equivalence.

The local requires-coenzyme gamma-F420-2(4−) trait denotes a protein functional requirement, while CHEBI:59541 in xrefs denotes the chemical referent. The source coenzyme-role assertion supplies candidate context, not equivalence between the chemical and a protein-requirement class. The machine-readable equality changes denotation despite supported chemical identification.

## Recommended Actions And Acceptance Checks

### A1

Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:59541 as a typed chemical_participants association with candidate role COFACTOR for the proposed requirement, preserving exact chemical scope and source-role provenance. Keep this a source-grounded candidate rather than a newly verified physiological or per-protein requirement; adjudicate the activity-relative role before qualification. Preserve nucleotide identity, charge, deazaflavin state, glutamyl number/linkage and stereochemistry. Do not substitute related compounds, merge conjugates or simply move the association to mapped_xrefs.

- The chemical association no longer asserts chemical-to-protein-trait equality. The exact ChEBI identifier and candidate source-role context are preserved.
- A focused maintained source-transform fixture verifies typed output and retained chemical distinctions. Regenerate through an audited route explicitly selecting the existing target; no protein examples or native status are promoted.
- For maintained writer changes run just audit-writers, just lint and just test, including the focused fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml. Run full just validate-all before merging record changes, as required by CLAUDE.md. Capture changed inputs and save a fresh validated review; do not overwrite this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| local-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | The captured cofactor requirement ancestor resolves above the local coenzyme requirement parent. Both are candidate protein-trait classes; this review does not certify their chemical-role xref equivalence. |
| licence | https://www.ebi.ac.uk/chebi/about/; About chemical scope and Licensing section | supports | Official chemical-entity and role scope plus the Licensing section support ChEBI attribution and CC BY 4.0. They do not equate chemical entities with protein traits. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The reused official OLS metadata records comparison ontology version 256. Its original UTC and digest are preserved; it does not identify the seed release. |
| coenzyme-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Full role definition and outgoing hierarchy | supports | CHEBI:23354 defines a low-molecular-weight nonprotein organic participant acting as a dissociable chemical-group or electron donor/acceptor and has direct is-a cofactor CHEBI:23357. This validates role ancestry, not a particular protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Full role definition and outgoing hierarchy | supports | CHEBI:23357 defines the chemical cofactor role and has direct biochemical-role parent CHEBI:52206. It supplies candidate role context rather than per-protein qualification. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/59541/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | C29H32N5O18P with charge -4. Its structure has one anionic phosphate oxygen and three carboxylates, with two L-glutamate residues joined through a gamma-carboxyl-to-amino amide. D-ribityl and (S)-lactyl stereochemistry are retained. The current source explicitly identifies neutral gamma-F420-2 CHEBI:16848 as the conjugate acid. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:59541; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete entity and matching definition, formula, charge, structure and InChI. Synonym scopes and source annotations were inspected; no chemical name is promoted to protein-trait equivalence. |
| chemical-context-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/43034/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | CHEBI:43034 resolves as 7,8-didemethyl-8-hydroxy-5-deazariboflavin (Fo), C16H17N3O7, charge 0. Its deazaflavin and D-ribityl structure support the source functional-parent relation; functional parent is not an is-a relation or a protein-trait parent. |
| chemical-context-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/58944/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | The dialkyl phosphate anion parent resolves as the conjugate base of a dialkyl phosphate, with organophosphate oxoanion as its parent. This supports the phosphate chemistry only. |
| chemical-context-3 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26554/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | The ribitol phosphate chemical parent resolves without a prose definition or single structure; its outgoing parent is pentitol phosphate. No missing fields are filled by inference. |
| chemical-context-4 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/59535/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | The asserted pyrimidoquinolines chemical class resolves with its fused heterocycle definition and no single formula or default structure. It does not denote a protein requirement. |
| chemical-context-5 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35753/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | The tricarboxylic acid anion parent denotes deprotonation of at least one carboxyl group; it does not alone fix a -3 carboxyl charge. The exact target structure supplies the three-carboxylate assignment. |
| chemical-context-6 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16848/; Complete identity/definition/names, chemical_data, default_structure and outgoing relations | supports | Neutral gamma-F420-2 CHEBI:16848 resolves as C29H36N5O18P, charge 0, with two gamma-linked L-glutamates and the same defined stereochemistry. It is the source conjugate acid of CHEBI:59541, not the same protonation state. |
| source-cited-primary-1 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11888293%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | context_only | PMID:11888293; DOI:10.1021/bi011937v. The source-cited complete abstract reports M. jannaschii CofD transfer of phospholactate to Fo to form F420-0 and GMP, with Mg2+ required in that assay. It concerns a biosynthetic precursor and does not directly establish the exact charge state or protein requirement of this reviewed glutamylated entity. |
| source-cited-primary-2 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18252724%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | context_only | PMID:18252724; DOI:10.1074/jbc.M710352200. The source-cited complete abstract reports M. mazei CofD structures with Fo plus phosphate or GDP and binding assays. These are F420-0 biosynthesis contexts, not exact reviewed-state cofactor qualification. |
| ligation-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:17669425%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full paper not inspected | supports | PMID:17669425; DOI:10.1016/j.jmb.2007.06.063. The complete abstract reports A. fulgidus CofE adding glutamate to F420-0 and F420-1 in two distinct steps, with apo and GDP-bound structures. This supports stepwise chain assembly and gamma-glutamyl ligase context; substrate/product use neither proves nor rules out other cofactor roles. |
| chain-primary | https://pmc.ncbi.nlm.nih.gov/articles/PMC165758/; Complete primary article text, especially chemical nomenclature, extraction/HPLC, peptidase and glutamate analyses; figure images not separately inspected | supports | PMID:12867481; DOI:10.1128/JB.185.15.4662-4665.2003. Full article text was inspected. Chemical explanation, HPLC, selective peptidase treatment and glutamate analysis distinguish gamma-amide-linked F420 chains from terminal alpha-linked L-glutamate analogues in the tested organisms. Its negative F420-1 detection is restricted to the sampled extracts and method; neither a universal absence nor an exact protein-bound charge is inferred. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Executed 2026-10-21T10:26:57Z through 2026-10-21T10:26:58Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/coelichelin-3-chebi84724.yaml data/traits/function/cofactor_requirement/chebi/coelichelin-chebi80049.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-a-chebi15346.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-b-chebi28890.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-a-chebi62784.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f390-g-chebi62786.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-3-chebi59543.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-1-chebi59536.yaml data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Executed 2026-10-21T10:25:03Z through 2026-10-21T10:26:36Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml; Executed 2026-10-21T10:26:58Z through 2026-10-21T10:26:58Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T10:26:36Z through 2026-10-21T10:26:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The source-cited CofD abstracts concern Fo/F420-0 precursor formation and binding, while the additional CofE and chain studies concern synthesis and glutamyl structure. None independently establishes that a protein obligatorily requires this exact charge state. Acid/base deprotonation, chromophore reduction and chain modification remain separate; no terminal-alpha analogue or reduced F420H2 form is substituted.
- The full primary chain-comparison article was inspected through PMC HTML after the XML endpoint returned HTTP 500. The failed response is not scientific evidence. Its extraction and assay conditions do not determine intracellular protonation populations; no target pH-major-species claim is introduced.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T103339Z-coenzyme-f420-2-4-chebi59541
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires coenzyme γ-F420-2(4−)
started_at: '2026-10-21T10:24:38Z'
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
summary: Chemical identity and current source coenzyme-role context are supported
  for coenzyme gamma-F420-2(4−). One confirmed major finding concerns chemical-to-protein-trait
  equivalence in xrefs. Exact physiological or per-protein requirement is not independently
  qualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
    sha256: 9c2f36cf1515d74687e554acd3d694254c11847c14fddabe5cf24d88612f83a1
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
  selection: Path-order position 10 in batch 015. Fresh main inventory has 429359
    records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
targets:
- kind: generated
  label: requires coenzyme γ-F420-2(4−)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_59541
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:59541 resolves in current official backend and OLS responses. Its
    direct coenzyme role, coenzyme-to-cofactor ancestry, and cited chemical context
    entries resolve. These relations establish source chemical context, not equivalent
    protein-trait identity or a qualified protein requirement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  evidence_ids:
  - chemical
  - chemical-ontology
  - coenzyme-role
  - cofactor-role
  - licence
  - current-release
  - chemical-context-1
  - chemical-context-2
  - chemical-context-3
  - chemical-context-4
  - chemical-context-5
  - chemical-context-6
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T10:24:38Z'
  snapshot_sha256: 9c2f36cf1515d74687e554acd3d694254c11847c14fddabe5cf24d88612f83a1
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
  accessed_at: '2026-10-21T10:24:38Z'
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
  accessed_at: '2026-10-21T10:24:38Z'
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
  accessed_at: '2026-10-21T10:24:38Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/coenzyme-chebi23354.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T10:24:38Z'
  snapshot_sha256: 07990ad9e631ce6d8171bf6835e20b59e1542d8fc1894161c2beb60f81711449
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: local-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T10:24:38Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: The captured cofactor requirement ancestor resolves above the local coenzyme
    requirement parent. Both are candidate protein-trait classes; this review does
    not certify their chemical-role xref equivalence.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: About chemical scope and Licensing section
  summary: Official chemical-entity and role scope plus the Licensing section support
    ChEBI attribution and CC BY 4.0. They do not equate chemical entities with protein
    traits.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The reused official OLS metadata records comparison ontology version 256.
    Its original UTC and digest are preserved; it does not identify the seed release.
- evidence_id: coenzyme-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T10:10:09.158129Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Full role definition and outgoing hierarchy
  summary: CHEBI:23354 defines a low-molecular-weight nonprotein organic participant
    acting as a dissociable chemical-group or electron donor/acceptor and has direct
    is-a cofactor CHEBI:23357. This validates role ancestry, not a particular protein
    requirement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Full role definition and outgoing hierarchy
  summary: CHEBI:23357 defines the chemical cofactor role and has direct biochemical-role
    parent CHEBI:52206. It supplies candidate role context rather than per-protein
    qualification.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/59541/
  accessed_at: '2026-10-21T10:25:33.642025Z'
  snapshot_sha256: a1dd1b2149119850043db74e345ca02a088e01cbd2a7f795daef7daacbddf2e8
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: C29H32N5O18P with charge -4. Its structure has one anionic phosphate oxygen
    and three carboxylates, with two L-glutamate residues joined through a gamma-carboxyl-to-amino
    amide. D-ribityl and (S)-lactyl stereochemistry are retained. The current source
    explicitly identifies neutral gamma-F420-2 CHEBI:16848 as the conjugate acid.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:59541
  accessed_at: '2026-10-21T10:25:32.938517Z'
  snapshot_sha256: 2edf4e18f6cca3ff6c295799a7c9a2b560849920f5ab2a61fea1cfc51643c3bd
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete entity and matching definition, formula,
    charge, structure and InChI. Synonym scopes and source annotations were inspected;
    no chemical name is promoted to protein-trait equivalence.
- evidence_id: chemical-context-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/43034/
  accessed_at: '2026-10-21T10:25:59.620844Z'
  snapshot_sha256: 36431188feaa730d422b5f4cee6563eb23906cc8fc25488b065d1e068c0603ad
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: CHEBI:43034 resolves as 7,8-didemethyl-8-hydroxy-5-deazariboflavin (Fo),
    C16H17N3O7, charge 0. Its deazaflavin and D-ribityl structure support the source
    functional-parent relation; functional parent is not an is-a relation or a protein-trait
    parent.
- evidence_id: chemical-context-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/58944/
  accessed_at: '2026-10-21T10:25:59.621606Z'
  snapshot_sha256: 8b49fae437f36e16d4d8937d8e476e51718a3e68db625ab9175364b680454877
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: The dialkyl phosphate anion parent resolves as the conjugate base of a
    dialkyl phosphate, with organophosphate oxoanion as its parent. This supports
    the phosphate chemistry only.
- evidence_id: chemical-context-3
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26554/
  accessed_at: '2026-10-21T10:25:59.621524Z'
  snapshot_sha256: a5c0253eba0328e381567cc76d638b183c944b4acd6b6eae5380b370b7109694
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: The ribitol phosphate chemical parent resolves without a prose definition
    or single structure; its outgoing parent is pentitol phosphate. No missing fields
    are filled by inference.
- evidence_id: chemical-context-4
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/59535/
  accessed_at: '2026-10-21T10:25:59.621434Z'
  snapshot_sha256: d27052cd775aa577f332cb31624c4c95126a7cf840caedbe6b2783db7061056f
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: The asserted pyrimidoquinolines chemical class resolves with its fused
    heterocycle definition and no single formula or default structure. It does not
    denote a protein requirement.
- evidence_id: chemical-context-5
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35753/
  accessed_at: '2026-10-21T10:26:00.331617Z'
  snapshot_sha256: 60d2185965b3aec24d73ae229fe07f07ad81d7effafc9c4f18cfd702f40a7803
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: The tricarboxylic acid anion parent denotes deprotonation of at least one
    carboxyl group; it does not alone fix a -3 carboxyl charge. The exact target structure
    supplies the three-carboxylate assignment.
- evidence_id: chemical-context-6
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16848/
  accessed_at: '2026-10-21T10:26:00.410708Z'
  snapshot_sha256: 9803a4ae7bc3d8a3bb21d76a7a736e904d688d201343de93d90d0b6745a3d275
  support: supports
  locator: Complete identity/definition/names, chemical_data, default_structure and
    outgoing relations
  summary: Neutral gamma-F420-2 CHEBI:16848 resolves as C29H36N5O18P, charge 0, with
    two gamma-linked L-glutamates and the same defined stereochemistry. It is the
    source conjugate acid of CHEBI:59541, not the same protonation state.
- evidence_id: source-cited-primary-1
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11888293%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:01.098232Z'
  snapshot_sha256: f05568e754988bb6df520e66edce7b21871e7ff84475bebdd7f38ced6bad584c
  support: context_only
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:11888293; DOI:10.1021/bi011937v. The source-cited complete abstract
    reports M. jannaschii CofD transfer of phospholactate to Fo to form F420-0 and
    GMP, with Mg2+ required in that assay. It concerns a biosynthetic precursor and
    does not directly establish the exact charge state or protein requirement of this
    reviewed glutamylated entity.
- evidence_id: source-cited-primary-2
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18252724%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:01.133565Z'
  snapshot_sha256: f4c719ace4c5688a2ade290d3410f02097baea9f4ad070381429686d912d2511
  support: context_only
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:18252724; DOI:10.1074/jbc.M710352200. The source-cited complete abstract
    reports M. mazei CofD structures with Fo plus phosphate or GDP and binding assays.
    These are F420-0 biosynthesis contexts, not exact reviewed-state cofactor qualification.
- evidence_id: ligation-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:17669425%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T10:26:01.157725Z'
  snapshot_sha256: 16227473599c37e368c69d9dfd3d4fd5dbca34b7032fcacbf2bda2f70db40077
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full paper not inspected
  summary: PMID:17669425; DOI:10.1016/j.jmb.2007.06.063. The complete abstract reports
    A. fulgidus CofE adding glutamate to F420-0 and F420-1 in two distinct steps,
    with apo and GDP-bound structures. This supports stepwise chain assembly and gamma-glutamyl
    ligase context; substrate/product use neither proves nor rules out other cofactor
    roles.
- evidence_id: chain-primary
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC165758/
  accessed_at: '2026-10-21T10:26:33.291195Z'
  snapshot_sha256: 20b6a0ffab1532ce30e9e47336c3cf5f5abe816291f30272c497785587c9b901
  support: supports
  locator: Complete primary article text, especially chemical nomenclature, extraction/HPLC,
    peptidase and glutamate analyses; figure images not separately inspected
  summary: PMID:12867481; DOI:10.1128/JB.185.15.4662-4665.2003. Full article text
    was inspected. Chemical explanation, HPLC, selective peptidase treatment and glutamate
    analysis distinguish gamma-amide-linked F420 chains from terminal alpha-linked
    L-glutamate analogues in the tested organisms. Its negative F420-1 detection is
    restricted to the sampled extracts and method; neither a universal absence nor
    an exact protein-bound charge is inferred.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  locator: Executed 2026-10-21T10:26:57Z through 2026-10-21T10:26:58Z; exit 0
  accessed_at: '2026-10-21T10:26:58Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
  locator: Executed 2026-10-21T10:26:58Z through 2026-10-21T10:26:58Z; exit 0
  accessed_at: '2026-10-21T10:26:58Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: evidence
  outcome: supported
  summary: Source structures and inspected primary ligation/chain analyses support
    the stated chemical connectivity and bounded biosynthetic context. The source-cited
    CofD papers concern precursor chemistry. No exact reviewed protonation state,
    universal chain preference, physiological dominance or protein member is independently
    qualified. Substrate/product context is not negative evidence against additional
    cofactor uses.
  evidence_ids:
  - chemical
  - source-cited-primary-1
  - source-cited-primary-2
  - ligation-primary
  - chain-primary
  topic: Chemical connectivity and biosynthetic evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-5
- area: identity
  outcome: supported
  summary: The tetraanion definition agrees with one phosphate and three carboxyl
    deprotonations of the two-glutamyl parent. Gamma specifies the interglutamate
    amide linkage, not an ester, and does not denote every terminal-alpha-linked F420
    analogue. Its exact charge, chain length and stereochemistry remain distinct from
    related chemical states.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - chemical-context-1
  - chemical-context-2
  - chemical-context-3
  - chemical-context-4
  - chemical-context-5
  - chemical-context-6
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-6
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: The chemical definition and direct coenzyme role match current ChEBI; the
    protein-requirement wrapper is maintained generator synthesis. Licence and current
    comparison release are traceable, while the exact seed release and independently
    qualified protein requirement remain unknown.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - owner
  - registry
  - licence
  - current-release
  - coenzyme-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-7
  topic: ChEBI attribution and release provenance
- area: consistency
  outcome: supported
  summary: The captured local coenzyme requirement parent and cofactor ancestor resolve.
    Current direct coenzyme role and coenzyme-to-cofactor ancestry support candidate
    hierarchy context; functional-parent, chemical is-a and conjugate relations are
    kept distinct from protein-trait subclass semantics. Parent xref correctness is
    not certified.
  evidence_ids:
  - record
  - local-parent-1
  - local-ancestor
  - chemical
  - coenzyme-role
  - cofactor-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-8
  topic: Chemical-role and protein-trait hierarchy
- area: representation
  outcome: supported
  summary: The local requires-label denotes a proposed reusable FUNCTION/FUNC_COFACTOR_REQUIREMENT
    class and remains SEEDED. Source roles are candidate context, and no experimental
    handling, binding or metabolic association is automatically promoted to a required
    protein cofactor.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-9
  topic: FUNCTION cofactor requirement representation
- area: grounding
  outcome: concern
  summary: CHEBI:59541 identifies a chemical entity, whereas the local record denotes
    a protein functional requirement for it. xrefs asserts true equivalence; chemical_participants
    permits a typed chemical association.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  assessment_id: assessment-10
  topic: Chemical association versus trait equivalence
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-59541.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement class
  description: The local requires-coenzyme gamma-F420-2(4−) trait denotes a protein
    functional requirement, while CHEBI:59541 in xrefs denotes the chemical referent.
    The source coenzyme-role assertion supplies candidate context, not equivalence
    between the chemical and a protein-requirement class. The machine-readable equality
    changes denotation despite supported chemical identification.
  evidence_ids:
  - record
  - chemical
  - schema
  - owner
  - registry
  - coenzyme-role
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical referent and its protein-requirement class have
    different denotations; typed chemical grounding is available in the schema.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Change build in scripts/seed_chebi_cofactor.py to represent CHEBI:59541
    as a typed chemical_participants association with candidate role COFACTOR for
    the proposed requirement, preserving exact chemical scope and source-role provenance.
    Keep this a source-grounded candidate rather than a newly verified physiological
    or per-protein requirement; adjudicate the activity-relative role before qualification.
    Preserve nucleotide identity, charge, deazaflavin state, glutamyl number/linkage
    and stereochemistry. Do not substitute related compounds, merge conjugates or
    simply move the association to mapped_xrefs.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59541
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The chemical association no longer asserts chemical-to-protein-trait equality.
    The exact ChEBI identifier and candidate source-role context are preserved.
  - A focused maintained source-transform fixture verifies typed output and retained
    chemical distinctions. Regenerate through an audited route explicitly selecting
    the existing target; no protein examples or native status are promoted.
  - For maintained writer changes run just audit-writers, just lint and just test,
    including the focused fixture. Then run just validate data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/coenzyme-f420-2-4-chebi59541.yaml.
    Run full just validate-all before merging record changes, as required by CLAUDE.md.
    Capture changed inputs and save a fresh validated review; do not overwrite this
    observation.
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
- The source-cited CofD abstracts concern Fo/F420-0 precursor formation and binding,
  while the additional CofE and chain studies concern synthesis and glutamyl structure.
  None independently establishes that a protein obligatorily requires this exact charge
  state. Acid/base deprotonation, chromophore reduction and chain modification remain
  separate; no terminal-alpha analogue or reduced F420H2 form is substituted.
- The full primary chain-comparison article was inspected through PMC HTML after the
  XML endpoint returned HTTP 500. The failed response is not scientific evidence.
  Its extraction and assay conditions do not determine intracellular protonation populations;
  no target pH-major-species claim is introduced.
tags:
- unreviewed-path-order
- batch-015
- chebi-cofactor
```
