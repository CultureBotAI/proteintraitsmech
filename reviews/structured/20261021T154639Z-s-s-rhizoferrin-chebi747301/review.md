# Review of requires (S,S)-rhizoferrin

- Review: 20261021T154639Z-s-s-rhizoferrin-chebi747301
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T15:36:07Z
- Finished UTC: 2026-10-21T15:46:39Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

S,S-rhizoferrin identity and positive stereoselective uptake are supported. One major concerns chemical-to-protein equality and one minor concerns the literal empty-definition tail.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 8 in batch 033. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333, the union covers 318 record paths, leaving 429041 before this batch. 33 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml | generated | requires (S,S)-rhizoferrin |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_747301 | Current backend/OLS, structural parents, role hierarchy, licence/release, the complete original isolation abstract and the source-linked staphylococcal transport abstract were inspected. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Neutral S,S-rhizoferrin and ferric uptake context

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The label, ChEBI ID and stereodefined polycarboxylate structure agree. An absent chemical definition does not erase the resolved identity. R,R fungal rhizoferrin and iron-loaded complexes remain distinct from the exact free neutral source entry.

### Empty-definition quotation artifact

nomenclature: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The local folded definition visibly ends with two literal quotation characters. Current backend has an empty definition and OLS no description; the maintained loader accepts nonempty cleaned strings other than null, so a quoted-empty placeholder can be appended. The historical raw seed is not pinned, so its precise origin is not reconstructed. This is a bounded wording artifact, not an unresolved chemical identity.

### Positive stereoselective iron uptake

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The primary isolation and transport abstracts provide positive, organism-specific siderophore use and differing stereoselectivity. They establish neither universal enantiomer preference nor a named protein’s obligatory non-substrate dependence on the neutral free acid.

### Siderophore use versus protein activity requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The source siderophore role is retained. Iron acquisition and growth experiments need a separately qualified protein/activity and ligand-loading/protonation state before any protein-requirement assertion. Lack of a qualified example is not independently treated as a required-field defect or proof of inactivity.

### Role parent and structural ancestry

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The local siderophore parent and captured cofactor ancestor follow the source role hierarchy. The structural acid/amide/alcohol/diol classes describe the chemical and are not additional required protein parents. No pH population or metal stoichiometry is asserted by the local target.

### Maintained owner, current sources and licence

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

The captured normal ChEBI role parser selects candidates through cofactor-role ancestry. Its build function synthesizes a requirement prefix and appends source chemical text; definition_source attribution therefore includes a local transformation. Current official roles and CC BY 4.0 support source provenance, without proving the synthesized requirement or identifying the historical input release.

### Chemical identity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_747301.

CHEBI:747301 denotes the neutral stereodefined free S,S-rhizoferrin molecule, whereas the local COFACTOR_REQ class denotes a proposed protein functional requirement. The schema defines xrefs as true own-source equivalence. The chemical entity and proteins requiring it have different denotations; authentic source roles and positive activity evidence do not establish that equality.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-747301.chemical-entity-equivalence.

CHEBI:747301 denotes the neutral stereodefined free S,S-rhizoferrin molecule, whereas the local COFACTOR_REQ class denotes a proposed protein functional requirement. The schema defines xrefs as true own-source equivalence. The chemical entity and proteins requiring it have different denotations; authentic source roles and positive activity evidence do not establish that equality.

### F2: Remove literal empty-definition quotation marks

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-747301.empty-definition-placeholder.

The definition ends with a literal empty quoted string although current source prose is absent. The two characters add no definition and are a visible source-placeholder artifact; chemical identity and stereochemistry remain resolved.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so chemical association is not emitted as protein-trait equality. Retain organism-specific positive iron uptake while distinguishing free ligand, ferric complex and protein uptake/catalysis. Resolve the relevant activity and chemical state before optional enrichment; do not automatically merge R,R and S,S enantiomers. Preserve ChEBI provenance. Optional chemical_participants with role COFACTOR requires adjudication of the exact chemical and activity-relative non-substrate role; unresolved qualification can remain explicit without inventing a participant. Do not relocate this false equality to mapped_xrefs, require optional examples, merge distinct chemical states automatically or promote native status.

- The regenerated xrefs does not equate the chemical entity with the protein requirement; source identity and provenance remain traceable.
- Resolve the stated chemical-state and activity-role boundaries before optional participant enrichment; preserve positive evidence without universal qualification.
- After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml.
- Use pinned source inputs and an audited scoped existing-record regeneration route. The normal ChEBI emitter skips existing files unless --force is supplied and writes only with --apply, but main traverses a cohort: broad --apply --force is not a one-record repair. For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

### A2

Harden the maintained definition-normalization/build path to treat a quoted-empty placeholder as absent prose, then regenerate only the scoped record. Preserve the valid requirement text and exact S,S identity; do not fabricate a source definition.

- The regenerated folded definition has no literal empty quoted tail and preserves the exact chemical identity.
- Regression coverage distinguishes absent/null/quoted-empty source prose from meaningful quoted text.
- After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml.
- Use pinned source inputs and an audited scoped existing-record regeneration route. The normal ChEBI emitter skips existing files unless --force is supplied and writes only with --apply, but main traverses a cohort: broad --apply --force is not a one-record repair. For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; About ChEBI, data availability/licence paragraph | supports | The inspected official ChEBI About page explicitly licenses website data under CC BY 4.0. Reused raw bytes were hash verified and retain their original access time. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; config.version, config.versionIri, updated | supports | The captured OLS ontology metadata reports ChEBI version 256 and its versionIRI; this retained metadata snapshot is distinct from the live backend access time and does not reconstruct the original seed release. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing is-a relation | supports | CHEBI:23357 is a biochemical role for an organic molecule or ion required for enzyme activity, with is-a biochemical role 52206. It is not a molecule or a protein class. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/747301/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | CHEBI:747301 resolves to neutral (S,S)-rhizoferrin, C16H24N2O12, with two specified citryl centres, four carboxylic-acid groups, two secondary amides and two hydroxy groups. The backend definition is an empty string, not a pair of quotation characters. Direct roles are siderophore and bacterial metabolite; the source origin is Ralstonia pickettii DSM 6297. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:747301; Embedded term identity, description[], is_obsolete and chemical annotations | supports | The nonobsolete OLS entry retains the S,S identity, formula, neutral charge and stereospecific graph; its description list is empty. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Definition and outgoing role relations | supports | The source defines siderophores as microbial iron(III) chelators for transport/sequestration and explicitly places the role under cofactor. That chemical-role hierarchy is authentic but is not itself a specific protein non-substrate requirement. |
| carboxy-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35742/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Tetracarboxylic acid is an oxoacid containing four carboxy groups; the class is not a protein requirement. |
| amide-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/140325/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Secondary carboxamide has the formal acid/primary-amine condensation definition and an R-group representative structure. |
| alcohol-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26878/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Tertiary alcohol has OH on a saturated carbon with three other carbon neighbours; its representative structure uses R groups. |
| diol-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23824/; id/name/definition; names; chemical_data; default_structure; ontology_relations; source citations | supports | Diol is defined by two hydroxy groups; this broad class has no fixed structure or chemical_data. |
| isolation | https://link.springer.com/article/10.1023/A:1009259118034?error=cookies_not_supported&amp;code=58ef55a5-59f9-4d6e-951a-57ace46fc428; Article title and complete public Abstract; Biometals 12 (1999),189–193 | supports | The publisher’s complete primary abstract for DOI 10.1023/A:1009259118034 reports isolation from iron-limited Ralstonia pickettii DSM 6297, spectroscopic S,S identity and radiolabelled-iron transport. The bacterial strain showed no difference between tested enantiomers; the producing Rhizopus strain preferred R,R. This is strain- and ferric-transport context, not an isolated enzyme requirement. |
| staph-uptake | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15865412%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; Europe PMC MED:15865412, title, DOI, publication types and complete indexed abstract | supports | The source-linked primary abstract assigns S,S citryl stereochemistry in staphyloferrin A and reports staphylococcal growth/iron uptake with S,S enantio-rhizoferrin but not fungal R,R-rhizoferrin. It does not make every bacterium stereoselective or equate iron-loaded ligand with the free neutral molecule. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; Executed 2026-10-21T15:37:06Z through 2026-10-21T15:37:07Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/rhizobactin-1021-chebi74252.yaml data/traits/function/cofactor_requirement/chebi/rhodotorulic-acid-chebi84731.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-1-chebi57986.yaml data/traits/function/cofactor_requirement/chebi/riboflavin-chebi17015.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-homocysteine-chebi16680.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-chebi15414.yaml data/traits/function/cofactor_requirement/chebi/s-adenosyl-l-methionine-zwitterion-chebi59789.yaml data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-chebi59560.yaml data/traits/function/cofactor_requirement/chebi/sapropterin-dihydrochloride-chebi32120.yaml; Executed 2026-10-21T15:37:45Z through 2026-10-21T15:39:21Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml; Executed 2026-10-21T15:37:07Z through 2026-10-21T15:37:07Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T15:39:21Z through 2026-10-21T15:39:23Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The two primary papers were inspected at complete public/indexed abstract scope. Uptake/growth effects are not direct protein-site measurements. The source-origin citation is not assumed to replace the original 1999 isolation study; no historical raw placeholder is reconstructed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T154639Z-s-s-rhizoferrin-chebi747301
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires (S,S)-rhizoferrin
started_at: '2026-10-21T15:36:07Z'
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
summary: S,S-rhizoferrin identity and positive stereoselective uptake are supported.
  One major concerns chemical-to-protein equality and one minor concerns the literal
  empty-definition tail.
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
  - path: data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
    sha256: d4a4fce4d3fb27a5885830cc8fb39a3d2d2f005f9b4e93b7a2efd2b2030e4bc5
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
  selection: Path-order position 8 in batch 033. Fresh main inventory has 429359 records.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
targets:
- kind: generated
  label: requires (S,S)-rhizoferrin
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_747301
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current backend/OLS, structural parents, role hierarchy, licence/release,
    the complete original isolation abstract and the source-linked staphylococcal
    transport abstract were inspected.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  evidence_ids:
  - licence
  - release
  - cofactor-role
  - chemical
  - chemical-ontology
  - siderophore-role
  - carboxy-parent
  - amide-parent
  - alcohol-parent
  - diol-parent
  - isolation
  - staph-uptake
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T15:36:07Z'
  snapshot_sha256: d4a4fce4d3fb27a5885830cc8fb39a3d2d2f005f9b4e93b7a2efd2b2030e4bc5
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
  accessed_at: '2026-10-21T15:36:07Z'
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
  accessed_at: '2026-10-21T15:36:07Z'
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
  accessed_at: '2026-10-21T15:36:07Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T15:36:07Z'
  snapshot_sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/747301/
  accessed_at: '2026-10-21T15:37:10.922093Z'
  snapshot_sha256: 5d39b803e7bde50e5ba657d3e23583f4299bc31f0c5ecc9915617606aec5e592
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: CHEBI:747301 resolves to neutral (S,S)-rhizoferrin, C16H24N2O12, with two
    specified citryl centres, four carboxylic-acid groups, two secondary amides and
    two hydroxy groups. The backend definition is an empty string, not a pair of quotation
    characters. Direct roles are siderophore and bacterial metabolite; the source
    origin is Ralstonia pickettii DSM 6297.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:747301
  accessed_at: '2026-10-21T15:37:11.445221Z'
  snapshot_sha256: 9ca8de4d413b32e8ad3017b91422c98d6446833698f420357cdf9d90c23f9af0
  support: supports
  locator: Embedded term identity, description[], is_obsolete and chemical annotations
  summary: The nonobsolete OLS entry retains the S,S identity, formula, neutral charge
    and stereospecific graph; its description list is empty.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T14:38:28.742321Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Definition and outgoing role relations
  summary: The source defines siderophores as microbial iron(III) chelators for transport/sequestration
    and explicitly places the role under cofactor. That chemical-role hierarchy is
    authentic but is not itself a specific protein non-substrate requirement.
- evidence_id: carboxy-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35742/
  accessed_at: '2026-10-21T15:37:46.067584Z'
  snapshot_sha256: 4b3f93222eff3a71bfdff6c2654d862a3de0a00979fef93eb0e44b254822fb75
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Tetracarboxylic acid is an oxoacid containing four carboxy groups; the
    class is not a protein requirement.
- evidence_id: amide-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/140325/
  accessed_at: '2026-10-21T15:37:46.352524Z'
  snapshot_sha256: 1092fd35107a93944e58088fa7e42b817c9889e6a027e88226ce3273beaebf7b
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Secondary carboxamide has the formal acid/primary-amine condensation definition
    and an R-group representative structure.
- evidence_id: alcohol-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26878/
  accessed_at: '2026-10-21T15:37:46.334570Z'
  snapshot_sha256: 4b519b38e6e503a15759adddc5909ed07946c40f31082644f666f3832cca08e9
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Tertiary alcohol has OH on a saturated carbon with three other carbon neighbours;
    its representative structure uses R groups.
- evidence_id: diol-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23824/
  accessed_at: '2026-10-21T15:37:46.130962Z'
  snapshot_sha256: 1dfdd60a316ffadf99d33043c71b7366567611f84805a0cbf12d64337ea41325
  support: supports
  locator: id/name/definition; names; chemical_data; default_structure; ontology_relations;
    source citations
  summary: Diol is defined by two hydroxy groups; this broad class has no fixed structure
    or chemical_data.
- evidence_id: isolation
  kind: primary_source
  reference: https://link.springer.com/article/10.1023/A:1009259118034?error=cookies_not_supported&code=58ef55a5-59f9-4d6e-951a-57ace46fc428
  accessed_at: '2026-10-21T15:38:48.994110Z'
  snapshot_sha256: 3c461043e535c3bc09146622f8f7e49d85a4267478f00fd447710fb3a4af9e5a
  support: supports
  locator: Article title and complete public Abstract; Biometals 12 (1999),189–193
  summary: The publisher’s complete primary abstract for DOI 10.1023/A:1009259118034
    reports isolation from iron-limited Ralstonia pickettii DSM 6297, spectroscopic
    S,S identity and radiolabelled-iron transport. The bacterial strain showed no
    difference between tested enantiomers; the producing Rhizopus strain preferred
    R,R. This is strain- and ferric-transport context, not an isolated enzyme requirement.
- evidence_id: staph-uptake
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A15865412%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T15:37:46.954130Z'
  snapshot_sha256: 51b3456777a8812a75b088465e10747c31bd56d97f93d40910a966581effe32e
  support: supports
  locator: Europe PMC MED:15865412, title, DOI, publication types and complete indexed
    abstract
  summary: The source-linked primary abstract assigns S,S citryl stereochemistry in
    staphyloferrin A and reports staphylococcal growth/iron uptake with S,S enantio-rhizoferrin
    but not fungal R,R-rhizoferrin. It does not make every bacterium stereoselective
    or equate iron-loaded ligand with the free neutral molecule.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  locator: Executed 2026-10-21T15:37:06Z through 2026-10-21T15:37:07Z; exit 0
  accessed_at: '2026-10-21T15:37:07Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml
  locator: Executed 2026-10-21T15:37:07Z through 2026-10-21T15:37:07Z; exit 0
  accessed_at: '2026-10-21T15:37:07Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The label, ChEBI ID and stereodefined polycarboxylate structure agree.
    An absent chemical definition does not erase the resolved identity. R,R fungal
    rhizoferrin and iron-loaded complexes remain distinct from the exact free neutral
    source entry.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - isolation
  - staph-uptake
  topic: Neutral S,S-rhizoferrin and ferric uptake context
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-5
- area: nomenclature
  outcome: concern
  summary: The local folded definition visibly ends with two literal quotation characters.
    Current backend has an empty definition and OLS no description; the maintained
    loader accepts nonempty cleaned strings other than null, so a quoted-empty placeholder
    can be appended. The historical raw seed is not pinned, so its precise origin
    is not reconstructed. This is a bounded wording artifact, not an unresolved chemical
    identity.
  evidence_ids:
  - record
  - owner
  - chemical
  - chemical-ontology
  topic: Empty-definition quotation artifact
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: The primary isolation and transport abstracts provide positive, organism-specific
    siderophore use and differing stereoselectivity. They establish neither universal
    enantiomer preference nor a named protein’s obligatory non-substrate dependence
    on the neutral free acid.
  evidence_ids:
  - isolation
  - staph-uptake
  - siderophore-role
  topic: Positive stereoselective iron uptake
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The source siderophore role is retained. Iron acquisition and growth experiments
    need a separately qualified protein/activity and ligand-loading/protonation state
    before any protein-requirement assertion. Lack of a qualified example is not independently
    treated as a required-field defect or proof of inactivity.
  evidence_ids:
  - record
  - schema
  - chemical
  - siderophore-role
  - isolation
  - staph-uptake
  topic: Siderophore use versus protein activity requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-8
- area: consistency
  outcome: supported
  summary: The local siderophore parent and captured cofactor ancestor follow the
    source role hierarchy. The structural acid/amide/alcohol/diol classes describe
    the chemical and are not additional required protein parents. No pH population
    or metal stoichiometry is asserted by the local target.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - siderophore-role
  - cofactor-role
  - carboxy-parent
  - amide-parent
  - alcohol-parent
  - diol-parent
  topic: Role parent and structural ancestry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
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
  - siderophore-role
  topic: Maintained owner, current sources and licence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-10
- area: grounding
  outcome: concern
  summary: CHEBI:747301 denotes the neutral stereodefined free S,S-rhizoferrin molecule,
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
  - siderophore-role
  - isolation
  - staph-uptake
  topic: Chemical identity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  assessment_id: assessment-11
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-747301.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: CHEBI:747301 denotes the neutral stereodefined free S,S-rhizoferrin
    molecule, whereas the local COFACTOR_REQ class denotes a proposed protein functional
    requirement. The schema defines xrefs as true own-source equivalence. The chemical
    entity and proteins requiring it have different denotations; authentic source
    roles and positive activity evidence do not establish that equality.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  - chemical-ontology
  - siderophore-role
  - isolation
  - staph-uptake
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-747301.empty-definition-placeholder
  category: nomenclature
  severity: minor
  title: Remove literal empty-definition quotation marks
  description: The definition ends with a literal empty quoted string although current
    source prose is absent. The two characters add no definition and are a visible
    source-placeholder artifact; chemical identity and stereochemistry remain resolved.
  evidence_ids:
  - record
  - owner
  - chemical
  - chemical-ontology
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: A harmless but visible placeholder is a minor wording defect;
    the chemical identifier and stereochemical scope are intact.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
actions:
- action_id: A1
  description: Correct build in scripts/seed_chebi_cofactor.py so chemical association
    is not emitted as protein-trait equality. Retain organism-specific positive iron
    uptake while distinguishing free ligand, ferric complex and protein uptake/catalysis.
    Resolve the relevant activity and chemical state before optional enrichment; do
    not automatically merge R,R and S,S enantiomers. Preserve ChEBI provenance. Optional
    chemical_participants with role COFACTOR requires adjudication of the exact chemical
    and activity-relative non-substrate role; unresolved qualification can remain
    explicit without inventing a participant. Do not relocate this false equality
    to mapped_xrefs, require optional examples, merge distinct chemical states automatically
    or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
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
  - After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml.
  - 'Use pinned source inputs and an audited scoped existing-record regeneration route.
    The normal ChEBI emitter skips existing files unless --force is supplied and writes
    only with --apply, but main traverses a cohort: broad --apply --force is not a
    one-record repair. For maintained writer changes add focused regression coverage
    and run just audit-writers, just lint and just test. Run full just validate-all
    before merging record changes; recapture changed inputs and save a fresh structured
    review without overwriting this observation.'
- action_id: A2
  description: Harden the maintained definition-normalization/build path to treat
    a quoted-empty placeholder as absent prose, then regenerate only the scoped record.
    Preserve the valid requirement text and exact S,S identity; do not fabricate a
    source definition.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_747301
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated folded definition has no literal empty quoted tail and preserves
    the exact chemical identity.
  - Regression coverage distinguishes absent/null/quoted-empty source prose from meaningful
    quoted text.
  - After scoped repair run just validate data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/s-s-rhizoferrin-chebi747301.yaml.
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
- The two primary papers were inspected at complete public/indexed abstract scope.
  Uptake/growth effects are not direct protein-site measurements. The source-origin
  citation is not assumed to replace the original 1999 isolation study; no historical
  raw placeholder is reconstructed.
tags:
- unreviewed-path-order
- batch-033
- chebi-cofactor
```
