# Review of requires sapropterin

- Review: 20261021T154639Z-sapropterin-chebi59560
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T15:36:08Z
- Finished UTC: 2026-10-21T15:46:39Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Exact sapropterin chemistry and positive BH4-dependent activity are supported. One confirmed major concerns chemical-to-protein equality; free, bound and salt states remain distinct.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 9 in batch 033. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333, the union covers 318 record paths, leaving 429041 before this batch. 33 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml | generated | requires sapropterin |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_59560 | Current backend/OLS, exact salt/component and broad-pterin comparisons, role hierarchy, licence/release, complete primary NOS/monoamine/PAH abstracts and official drug-label chemistry were inspected. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Sapropterin stereochemistry and salt distinction

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The target and source agree on 6R,1′R,2′S sapropterin. The stereounspecified parent and the dihydrochloride salt remain distinct; positive BH4 biology is not a reason to merge these representations.

### Reduced pterin definition and exact stereochemistry

nomenclature: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The copied tetrahydropterin substitution description and three stereochemical assignments agree with the source structure. No added pH population or salt requirement is stated by this target.

### Positive BH4 catalysis and sapropterin activity context

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

NOS reconstitution/redox studies provide positive catalytic pterin evidence, and rat monoamine/PAH studies preserve biological effects. The radical-reduction experiment specifically uses a 5-methyl analog. These findings are not dismissed merely because pterins also undergo redox chemistry or are used in pharmacological preparations.

### Exact free sapropterin versus enzyme-bound states

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

Established positive BH4 activity does not measure every free-state proton position or exclusively qualify this exact entry for every enzyme. Preserve activity-relative catalytic versus cosubstrate use and the bound pterin redox cycle. Optional examples are not mandatory.

### Source role hierarchy and chemical parent

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The local role-derived parent is supported by current source coenzyme/cofactor assertions and captured local ancestry. The chemical tetrahydrobiopterin parent and salt has-part relation classify chemistry; they do not mandate additional protein-class parents or a merge. No local pH 7.3 claim occurs.

### Maintained owner, current sources and licence

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

The captured normal ChEBI role parser selects candidates through cofactor-role ancestry. Its build function synthesizes a requirement prefix and appends source chemical text; definition_source attribution therefore includes a local transformation. Current official roles and CC BY 4.0 support source provenance, without proving the synthesized requirement or identifying the historical input release.

### Chemical identity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_59560.

CHEBI:59560 denotes the neutral stereodefined sapropterin molecule, whereas the local COFACTOR_REQ class denotes a proposed protein functional requirement. The schema defines xrefs as true own-source equivalence. The chemical entity and proteins requiring it have different denotations; authentic source roles and positive activity evidence do not establish that equality.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-59560.chemical-entity-equivalence.

CHEBI:59560 denotes the neutral stereodefined sapropterin molecule, whereas the local COFACTOR_REQ class denotes a proposed protein functional requirement. The schema defines xrefs as true own-source equivalence. The chemical entity and proteins requiring it have different denotations; authentic source roles and positive activity evidence do not establish that equality.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so chemical association is not emitted as protein-trait equality. Preserve positive BH4-dependent catalysis and 6R stereochemistry while separating free sapropterin, bound redox intermediates, the broader tetrahydrobiopterin class and administered salts. Preserve ChEBI provenance. Optional chemical_participants with role COFACTOR requires adjudication of the exact chemical and activity-relative non-substrate role; unresolved qualification can remain explicit without inventing a participant. Do not relocate this false equality to mapped_xrefs, require optional examples, merge distinct chemical states automatically or promote native status.

- The regenerated xrefs does not equate the chemical entity with the protein requirement; source identity and provenance remain traceable.
- Resolve the stated chemical-state and activity-role boundaries before optional participant enrichment; preserve positive evidence without universal qualification.
- After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml.
- Use pinned source inputs and an audited scoped existing-record regeneration route. The normal ChEBI emitter skips existing files unless --force is supplied and writes only with --apply, but main traverses a cohort: broad --apply --force is not a one-record repair. For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; About ChEBI, data availability/licence paragraph | supports | The inspected official ChEBI About page explicitly licenses website data under CC BY 4.0. Reused raw bytes were hash verified and retain their original access time. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; config.version, config.versionIri, updated | supports | The captured OLS ontology metadata reports ChEBI version 256 and its versionIRI; this retained metadata snapshot is distinct from the live backend access time and does not reconstruct the original seed release. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing is-a relation | supports | CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, with is-a biochemical role 52206. It is not a molecule or a protein class. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/59560/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | The source resolves neutral sapropterin C9H15N5O3 with 6R,1′R,2′S stereochemistry, a reduced tetrahydropterin ring and two hydroxy groups. Direct coenzyme/cofactor roles and is-a broad tetrahydrobiopterin 15372 are explicit. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:59560; Embedded term label/description/is_obsolete and chemical annotations | supports | The nonobsolete OLS entry agrees with the current name, definition, formula and stereospecific source structure. This comparison is not a historical seed-release reconstruction. |
| salt-pair | https://www.ebi.ac.uk/chebi/backend/api/public/compound/32120/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Sapropterin 59560 and its dihydrochloride 32120 are separate source entries. The salt has-part sapropterin; formula accounting/representation does not prove that an intact salt or chloride contribution is required at an enzyme site. |
| bh4-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15372/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Broad 5,6,7,8-tetrahydrobiopterin 15372 has a null prose definition and unspecified stereochemistry in its structure. It is a chemical parent of sapropterin, not an automatic substitute for its exact three stereocentres. |
| salt-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/36807/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Hydrochloride is defined as a salt formally resulting from reaction of hydrochloric acid with an organic base. This defines salt chemistry, not a protein-specific chloride requirement. |
| coenzyme-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/; Definition and outgoing is-a cofactor | supports | Coenzyme 23354 is a dissociable group/electron donor or acceptor role under cofactor 23357. Role inheritance does not identify a specific physiological salt or protein-bound state. |
| nos-reconstitution | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9425051%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:9425051, title, DOI, publication types and complete indexed abstract | supports | The primary study reconstitutes pterin-free iNOS with eight tetrahydro/dihydropterins. NO synthesis and substrate-responsive heme-dependent NADPH oxidation require fully reduced tetrahydropterins in the experiment; several binding/assembly properties instead depend on side-chain structure or stereochemistry. No universal exclusive acceptance of sapropterin is inferred. |
| nos-redox | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10514451%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:10514451, title, DOI, publication types and complete indexed abstract | supports | The primary study measures NOS-bound BH4 during multiple and single turnovers and observes oxidation plus reductive regeneration. Its abstract interprets these results as consistent with electron donation; the mechanism remains bounded by the stated experiments. |
| nos-radical | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18283102%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:18283102, title, DOI, publication types and complete indexed abstract | supports | The primary study tests radical reduction in neuronal NOS with the 5-methyl-BH4 analog, freeze-quench and separate radical quantification. Calmodulin-dependent flavoprotein reduction supports catalytic pterin recycling; analog kinetics are not exact measurements of free CHEBI:59560 or the hydrochloride salt. |
| rat-monoamines | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4004257%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:4004257, title, DOI, publication types and complete indexed abstract | supports | The source-linked primary study synthesizes 6R-L-erythro-BH4 using dihydrofolate reductase and measures increased DOPA/5-HTP formation after intracerebroventricular administration in rats. The outcomes are positive in-vivo context, not direct binding-state or universal enzyme-requirement measurements. |
| pah-chaperone | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20179079%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:20179079, title, DOI, publication types and complete indexed abstract | supports | The primary Pahenu1 mouse study reports that BH4 stabilizes defective PAH, increases effective enzyme concentration and rescues phenotype/function. It retains positive sapropterin treatment context without establishing that chloride or intact dihydrochloride is a natural enzyme cofactor. |
| drug-label | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=eafec3a2-4f29-4afa-8728-a62b34cefd18; Sections 11 Description, 12.1 Mechanism of Action and 12.3 Metabolism | supports | The official label explicitly distinguishes a synthetic preparation of the dihydrochloride salt from naturally occurring BH4; it gives formula C9H15N5O3·2HCl and separate sapropterin-base equivalence. Mechanism text calls BH4 the PAH cofactor and describes residual-activity activation in responsive patients. This is chemical/pharmacological authority context, not medical advice or protein-site proof. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml; Executed 2026-10-21T15:37:07Z through 2026-10-21T15:37:08Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml; Executed 2026-10-21T15:37:45Z through 2026-10-21T15:39:21Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml; Executed 2026-10-21T15:37:08Z through 2026-10-21T15:37:09Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T15:39:21Z through 2026-10-21T15:39:23Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- All cited scientific papers were inspected at complete indexed abstract scope. NOS radical-reduction work uses a 5-methyl analog; rat and clinical outcomes do not measure an exact bound salt/protonation state. The drug label is authority evidence for formulation/natural-BH4 distinction, not a biochemical demonstration that chloride is required. No patient-specific advice or protein promotion is made.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T154639Z-sapropterin-chebi59560
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires sapropterin
started_at: '2026-10-21T15:36:08Z'
finished_at: '2026-10-21T15:46:39Z'
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
summary: Exact sapropterin chemistry and positive BH4-dependent activity are supported.
  One confirmed major concerns chemical-to-protein equality; free, bound and salt
  states remain distinct.
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
  - path: data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
    sha256: 6a7a552114c22eee312ed77a51da49eac970b844ec55210161ca40b58176eb1a
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
  selection: Path-order position 9 in batch 033. Fresh main inventory has 429359 records.
    Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87;
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df;
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242;
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98)
    cover 248 record paths. Including validated unpublished local review commit(s)
    da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd;
    f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18;
    ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7;
    b6ee361647a739487903ad0d184297a280189333, the union covers 318 record paths, leaving
    429041 before this batch. 33 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
targets:
- kind: generated
  label: requires sapropterin
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_59560
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml
    data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml
    data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml
    data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
    data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current backend/OLS, exact salt/component and broad-pterin comparisons,
    role hierarchy, licence/release, complete primary NOS/monoamine/PAH abstracts
    and official drug-label chemistry were inspected.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  evidence_ids:
  - licence
  - release
  - cofactor-role
  - chemical
  - chemical-ontology
  - salt-pair
  - bh4-parent
  - salt-parent
  - coenzyme-role
  - nos-reconstitution
  - nos-redox
  - nos-radical
  - rat-monoamines
  - pah-chaperone
  - drug-label
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T15:36:08Z'
  snapshot_sha256: 6a7a552114c22eee312ed77a51da49eac970b844ec55210161ca40b58176eb1a
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
  accessed_at: '2026-10-21T15:36:08Z'
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
  accessed_at: '2026-10-21T15:36:08Z'
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
  accessed_at: '2026-10-21T15:36:08Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T15:36:08Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: licence
  kind: database
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: About ChEBI, data availability/licence paragraph
  summary: The inspected official ChEBI About page explicitly licenses website data
    under CC BY 4.0. Reused raw bytes were hash verified and retain their original
    access time.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: config.version, config.versionIri, updated
  summary: The captured OLS ontology metadata reports ChEBI version 256 and its versionIRI;
    this retained metadata snapshot is distinct from the live backend access time
    and does not reconstruct the original seed release.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and outgoing is-a relation
  summary: CHEBI:23357 is a biochemical role for an organic molecule or ion required
    for enzyme activity, with is-a biochemical role 52206. It is not a molecule or
    a protein class.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/59560/
  accessed_at: '2026-10-21T15:37:12.135826Z'
  snapshot_sha256: 07d9d7a7530e66126564cf3b2a5d5091fccb7286a8ef8dc7938d6ff83c7b1ecd
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: The source resolves neutral sapropterin C9H15N5O3 with 6R,1′R,2′S stereochemistry,
    a reduced tetrahydropterin ring and two hydroxy groups. Direct coenzyme/cofactor
    roles and is-a broad tetrahydrobiopterin 15372 are explicit.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:59560
  accessed_at: '2026-10-21T15:37:11.573651Z'
  snapshot_sha256: 7641958bdf4ca66095ccb3772802fc13db199aee7f4a29cdc5d7071b4974d556
  support: supports
  locator: Embedded term label/description/is_obsolete and chemical annotations
  summary: The nonobsolete OLS entry agrees with the current name, definition, formula
    and stereospecific source structure. This comparison is not a historical seed-release
    reconstruction.
- evidence_id: salt-pair
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/32120/
  accessed_at: '2026-10-21T15:37:11.605001Z'
  snapshot_sha256: c41b4f25f9eba0514e720bbc381f89980218022e0646c8b3c4398fec1c5f9d2d
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Sapropterin 59560 and its dihydrochloride 32120 are separate source entries.
    The salt has-part sapropterin; formula accounting/representation does not prove
    that an intact salt or chloride contribution is required at an enzyme site.
- evidence_id: bh4-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15372/
  accessed_at: '2026-10-21T15:37:46.202721Z'
  snapshot_sha256: 8a867beb9c3136303778357ce4bd2288b8f7e97c9e7f9932d86a60b6fd8e21fe
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Broad 5,6,7,8-tetrahydrobiopterin 15372 has a null prose definition and
    unspecified stereochemistry in its structure. It is a chemical parent of sapropterin,
    not an automatic substitute for its exact three stereocentres.
- evidence_id: salt-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/36807/
  accessed_at: '2026-10-21T15:37:47.026806Z'
  snapshot_sha256: 7d0b5f297bb44ef12c3cac6c3e014cdb647620c7923a7d14c4c222cbf5265f19
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Hydrochloride is defined as a salt formally resulting from reaction of
    hydrochloric acid with an organic base. This defines salt chemistry, not a protein-specific
    chloride requirement.
- evidence_id: coenzyme-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23354/
  accessed_at: '2026-10-21T15:00:04.622974Z'
  snapshot_sha256: e3e53a2e0b270a5522895f4ca11bb26e0f3021b2e3571a4949af9931db321ce5
  support: supports
  locator: Definition and outgoing is-a cofactor
  summary: Coenzyme 23354 is a dissociable group/electron donor or acceptor role under
    cofactor 23357. Role inheritance does not identify a specific physiological salt
    or protein-bound state.
- evidence_id: nos-reconstitution
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A9425051%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:38:59.997923Z'
  snapshot_sha256: 1e0450c9af59eaf5581c79900598e53c0de686795d366d187bba8cbe761a808c
  support: supports
  locator: Europe PMC MED:9425051, title, DOI, publication types and complete indexed
    abstract
  summary: The primary study reconstitutes pterin-free iNOS with eight tetrahydro/dihydropterins.
    NO synthesis and substrate-responsive heme-dependent NADPH oxidation require fully
    reduced tetrahydropterins in the experiment; several binding/assembly properties
    instead depend on side-chain structure or stereochemistry. No universal exclusive
    acceptance of sapropterin is inferred.
- evidence_id: nos-redox
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10514451%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:38:59.982012Z'
  snapshot_sha256: ee5120f0375b18f5f8cc8346b6bc1c942df1272fee8b5652c49bba7c42a046c1
  support: supports
  locator: Europe PMC MED:10514451, title, DOI, publication types and complete indexed
    abstract
  summary: The primary study measures NOS-bound BH4 during multiple and single turnovers
    and observes oxidation plus reductive regeneration. Its abstract interprets these
    results as consistent with electron donation; the mechanism remains bounded by
    the stated experiments.
- evidence_id: nos-radical
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18283102%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:38:59.991080Z'
  snapshot_sha256: 3f4b0ce2a48dfe191a59ed2e40432ea0de128009d1ebc217c5615fce18ca594f
  support: supports
  locator: Europe PMC MED:18283102, title, DOI, publication types and complete indexed
    abstract
  summary: The primary study tests radical reduction in neuronal NOS with the 5-methyl-BH4
    analog, freeze-quench and separate radical quantification. Calmodulin-dependent
    flavoprotein reduction supports catalytic pterin recycling; analog kinetics are
    not exact measurements of free CHEBI:59560 or the hydrochloride salt.
- evidence_id: rat-monoamines
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A4004257%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:47.463808Z'
  snapshot_sha256: d0d2d0ee12eae8a4e1c2a6a21514e134e425e2abf469ca87b6546bdf40a1e5c9
  support: supports
  locator: Europe PMC MED:4004257, title, DOI, publication types and complete indexed
    abstract
  summary: The source-linked primary study synthesizes 6R-L-erythro-BH4 using dihydrofolate
    reductase and measures increased DOPA/5-HTP formation after intracerebroventricular
    administration in rats. The outcomes are positive in-vivo context, not direct
    binding-state or universal enzyme-requirement measurements.
- evidence_id: pah-chaperone
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20179079%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:47.601363Z'
  snapshot_sha256: 18a374ed3ab8b5783ebfb6eb1a7496a15bad842ce269de541553faa278bd81cf
  support: supports
  locator: Europe PMC MED:20179079, title, DOI, publication types and complete indexed
    abstract
  summary: The primary Pahenu1 mouse study reports that BH4 stabilizes defective PAH,
    increases effective enzyme concentration and rescues phenotype/function. It retains
    positive sapropterin treatment context without establishing that chloride or intact
    dihydrochloride is a natural enzyme cofactor.
- evidence_id: drug-label
  kind: database
  reference: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=eafec3a2-4f29-4afa-8728-a62b34cefd18
  accessed_at: '2026-10-21T15:38:11.388040Z'
  snapshot_sha256: a76ce374b8c7bae72508b8727401f3c7f991320c3862844cbe8f427a4898fd2a
  support: supports
  locator: Sections 11 Description, 12.1 Mechanism of Action and 12.3 Metabolism
  summary: The official label explicitly distinguishes a synthetic preparation of
    the dihydrochloride salt from naturally occurring BH4; it gives formula C9H15N5O3·2HCl
    and separate sapropterin-base equivalence. Mechanism text calls BH4 the PAH cofactor
    and describes residual-activity activation in responsive patients. This is chemical/pharmacological
    authority context, not medical advice or protein-site proof.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  locator: Executed 2026-10-21T15:37:07Z through 2026-10-21T15:37:08Z; exit 0
  accessed_at: '2026-10-21T15:37:08Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml
    data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml
    data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml
    data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml
    data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
    data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml
  locator: Executed 2026-10-21T15:37:45Z through 2026-10-21T15:39:21Z; exit 0
  accessed_at: '2026-10-21T15:39:21Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml
  locator: Executed 2026-10-21T15:37:08Z through 2026-10-21T15:37:09Z; exit 0
  accessed_at: '2026-10-21T15:37:09Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T15:39:21Z through 2026-10-21T15:39:23Z; exit 0
  accessed_at: '2026-10-21T15:39:23Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The target and source agree on 6R,1′R,2′S sapropterin. The stereounspecified
    parent and the dihydrochloride salt remain distinct; positive BH4 biology is not
    a reason to merge these representations.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - salt-pair
  - bh4-parent
  - salt-parent
  topic: Sapropterin stereochemistry and salt distinction
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-5
- area: nomenclature
  outcome: supported
  summary: The copied tetrahydropterin substitution description and three stereochemical
    assignments agree with the source structure. No added pH population or salt requirement
    is stated by this target.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - drug-label
  - nos-reconstitution
  - nos-redox
  topic: Reduced pterin definition and exact stereochemistry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: NOS reconstitution/redox studies provide positive catalytic pterin evidence,
    and rat monoamine/PAH studies preserve biological effects. The radical-reduction
    experiment specifically uses a 5-methyl analog. These findings are not dismissed
    merely because pterins also undergo redox chemistry or are used in pharmacological
    preparations.
  evidence_ids:
  - nos-reconstitution
  - nos-redox
  - nos-radical
  - rat-monoamines
  - pah-chaperone
  topic: Positive BH4 catalysis and sapropterin activity context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: Established positive BH4 activity does not measure every free-state proton
    position or exclusively qualify this exact entry for every enzyme. Preserve activity-relative
    catalytic versus cosubstrate use and the bound pterin redox cycle. Optional examples
    are not mandatory.
  evidence_ids:
  - schema
  - chemical
  - salt-pair
  - salt-parent
  - drug-label
  - nos-reconstitution
  - nos-redox
  - pah-chaperone
  topic: Exact free sapropterin versus enzyme-bound states
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The local role-derived parent is supported by current source coenzyme/cofactor
    assertions and captured local ancestry. The chemical tetrahydrobiopterin parent
    and salt has-part relation classify chemistry; they do not mandate additional
    protein-class parents or a merge. No local pH 7.3 claim occurs.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - cofactor-role
  - coenzyme-role
  - bh4-parent
  - salt-pair
  topic: Source role hierarchy and chemical parent
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-9
- area: provenance
  outcome: supported
  summary: The captured normal ChEBI role parser selects candidates through cofactor-role
    ancestry. Its build function synthesizes a requirement prefix and appends source
    chemical text; definition_source attribution therefore includes a local transformation.
    Current official roles and CC BY 4.0 support source provenance, without proving
    the synthesized requirement or identifying the historical input release.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  - cofactor-role
  - coenzyme-role
  topic: Maintained owner, current sources and licence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: CHEBI:59560 denotes the neutral stereodefined sapropterin molecule, whereas
    the local COFACTOR_REQ class denotes a proposed protein functional requirement.
    The schema defines xrefs as true own-source equivalence. The chemical entity and
    proteins requiring it have different denotations; authentic source roles and positive
    activity evidence do not establish that equality.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - salt-pair
  - bh4-parent
  - drug-label
  - nos-reconstitution
  - nos-redox
  - pah-chaperone
  topic: Chemical identity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-59560.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: CHEBI:59560 denotes the neutral stereodefined sapropterin molecule,
    whereas the local COFACTOR_REQ class denotes a proposed protein functional requirement.
    The schema defines xrefs as true own-source equivalence. The chemical entity and
    proteins requiring it have different denotations; authentic source roles and positive
    activity evidence do not establish that equality.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - salt-pair
  - bh4-parent
  - drug-label
  - nos-reconstitution
  - nos-redox
  - pah-chaperone
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: Chemical-to-protein-class equality is a major grounding defect
    independently of valid cofactor biology. Optional representations and unresolved
    qualification are not additional mandatory-field defects.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build in scripts/seed_chebi_cofactor.py so chemical association
    is not emitted as protein-trait equality. Preserve positive BH4-dependent catalysis
    and 6R stereochemistry while separating free sapropterin, bound redox intermediates,
    the broader tetrahydrobiopterin class and administered salts. Preserve ChEBI provenance.
    Optional chemical_participants with role COFACTOR requires adjudication of the
    exact chemical and activity-relative non-substrate role; unresolved qualification
    can remain explicit without inventing a participant. Do not relocate this false
    equality to mapped_xrefs, require optional examples, merge distinct chemical states
    automatically or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_59560
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated xrefs does not equate the chemical entity with the protein requirement;
    source identity and provenance remain traceable.
  - Resolve the stated chemical-state and activity-role boundaries before optional
    participant enrichment; preserve positive evidence without universal qualification.
  - After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml.
  - 'Use pinned source inputs and an audited scoped existing-record regeneration route.
    The normal ChEBI emitter skips existing files unless --force is supplied and writes
    only with --apply, but main traverses a cohort: broad --apply --force is not a
    one-record repair. For maintained writer changes add focused regression coverage
    and run just audit-writers, just lint and just test. Run full just validate-all
    before merging record changes; recapture changed inputs and save a fresh structured
    review without overwriting this observation.'
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
- All cited scientific papers were inspected at complete indexed abstract scope. NOS
  radical-reduction work uses a 5-methyl analog; rat and clinical outcomes do not
  measure an exact bound salt/protonation state. The drug label is authority evidence
  for formulation/natural-BH4 distinction, not a biochemical demonstration that chloride
  is required. No patient-specific advice or protein promotion is made.
tags:
- unreviewed-path-order
- batch-033
- chebi-cofactor
```
