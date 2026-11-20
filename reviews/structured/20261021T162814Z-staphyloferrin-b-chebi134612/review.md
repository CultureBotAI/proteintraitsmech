# Review of requires staphyloferrin B

- Review: 20261021T162814Z-staphyloferrin-b-chebi134612
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T16:16:22Z
- Finished UTC: 2026-10-21T16:28:14Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact staphyloferrin B chemical identity and source-role provenance are supported, with positive experimental context assessed at its stated scope. The record still asserts a chemical entity as an equivalent protein-requirement class, a confirmed major grounding defect. The siderophore annotation is authentic positive source context, with verified cofactor ancestry. A ferric-complex transport role or biosynthetic product role cannot by itself qualify the neutral free acid under the current non-substrate requirement category. A curator must adjudicate exact activity and state before adding an optional participant with its required role.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 035. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585, the union covers 338 record paths, leaving 429021 before this batch. 35 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml | generated | requires staphyloferrin B |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_134612 | The exact ChEBI backend and OLS identifiers, chemical state and source siderophore role with cofactor ancestry were inspected alongside current licence metadata, exact chemical comparisons and the cited primary sources. Source resolution passed; it does not validate the chemical-to-trait equivalence or independently qualify every proposed requirement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Exact chemical identity and state

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The target’s structural-unit definition agrees with the current graph and the primary biosynthesis/chemical-characterization abstracts. Its neutral free-acid state remains separate from the dianion and Fe(III) complex. The specified citryl stereochemistry matters: the primary synthesis study distinguishes the biological behavior of a citryl epimer from that of native SB.

### Source role and local requirement hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The local parent resolves and reflects the source siderophore→cofactor path. This supports provenance and the intended candidate grouping, while chemical-role membership is not itself a protein requirement or an assertion that all optional protein examples are qualified.

### Positive experimental context and its limits

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

Primary isolation, synthesis and biosynthesis evidence supports staphyloferrin B production, chemical assembly, iron acquisition and growth recovery under the tested iron-limited conditions. The SirA structure abstract supplies positive recognition of ferric SB. These observations do not establish a protein requirement for the neutral free acid as a non-substrate cofactor, and do not prove that all other roles are absent.

### Activity-relative requirement and chemical participant

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The siderophore annotation is authentic positive source context, with verified cofactor ancestry. A ferric-complex transport role or biosynthetic product role cannot by itself qualify the neutral free acid under the current non-substrate requirement category. A curator must adjudicate exact activity and state before adding an optional participant with its required role.

### Current source support and licence

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The copied chemical identity and definition are traceable to current ChEBI. The opening protein-requirement assertion is generated by the maintained seeder. CC BY 4.0 is supported by the source licence; the target does not pin the original ChEBI release. The source role and these current snapshots do not independently establish the synthesized requirement.

### Chemical entity versus equivalent trait

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_134612.

The xref resolves successfully, but CHEBI:134612 denotes staphyloferrin B as a chemical entity. The record denotes proteins requiring it. Those entity types are not source-direct equivalents under the captured schema.

## Findings

### F1: Chemical entity asserted as an equivalent protein-requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-134612.chemical-entity-equivalence.

The target places CHEBI:134612 in xrefs, whose schema meaning requires true source-direct equivalence. Current ChEBI identifies staphyloferrin B as a chemical entity, while the local identifier, label and synthesized first sentence identify a protein requirement. Source role membership and chemical provenance do not equate those classes. The defect concerns the asserted relation, not failure of the chemical ID or absence of an optional protein example.

## Recommended Actions And Acceptance Checks

### A1

Correct the maintained scripts/seed_chebi_cofactor.py transformation so this requirement class does not assert chemical-entity equivalence. Preserve CHEBI:134612 as chemical/source provenance with its exact state and uncertainty. Adjudicate the activity-relative role before considering an optional chemical_participants entry; the required role of any added entry must be justified rather than automatically set to COFACTOR. If evidence cannot support a typed participant, retain the source association and uncertainty through an appropriate supported representation. Preserve the positive biological context and distinguish the generated requirement sentence from copied chemical description. Preview and scope the normal ChEBI emitter repair through its audited writer route; main emits its selected cohort with --force/--apply, so control unintended cohort changes.

- Inspect the regenerated target data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml: no false chemical-to-trait xref, preserved exact chemical/source provenance and a documented activity/state decision; any optional participant has a curator-supported role, and no unqualified protein example or automatic state replacement is introduced.
- Run just validate data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml, recording actual results.
- For maintained writer/code changes run just audit-writers, just lint, focused pytest and just test; perform the required full record validation before merge. Review the regenerated diff and create a fresh source-pinned scientific observation; do not overwrite this review.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| chemical-source | https://www.ebi.ac.uk/chebi/backend/api/public/compound/134612/; Exact entry identity, names, definition, chemical_data, default_structure, compound_origins and complete outgoing ontology relations; source-linked citations inspected as specified separately | supports | CHEBI:134612 is neutral, iron-free staphyloferrin B, C16H24N4O11, charge 0, with the two stereocentres specified in its IUPAC name and default structure. The source definition identifies L-2,3-diaminopropionic acid, citrate, diaminoethane and α-ketoglutaric-acid units. Outgoing relations include siderophore/bacterial-metabolite roles and a conjugate link to CHEBI:136993. Source origins name S. aureus and S. hyicus with primary references. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:134612; Exact term identity, obsolete status, description, synonyms and chemical annotations | supports | The exact OLS term is current and nonobsolete, resolves the same chemical label and state, and provides the recorded description, aliases and structure annotations. These fields describe a chemical entity; they do not assert equivalence to the synthesized protein-requirement class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition, null chemical fields and complete outgoing role hierarchy | supports | CHEBI:23357 defines a biochemical role required for enzyme activity and is a subclass of biochemical role. Its null fixed chemical structure is appropriate for a role. The definition does not establish which protein requires the exact reviewed entity. |
| source-license | https://www.ebi.ac.uk/chebi/about/; About ChEBI chemical/ontology scope and Licensing section | supports | The official ChEBI About page describes chemical entities and roles and explicitly permits data reuse under CC BY 4.0. This supports upstream attribution/licence, without licensing all independently cited publisher material alike. |
| ontology-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Ontology configuration version/versionIri and load metadata | supports | The captured OLS metadata identifies ChEBI version 256. This describes that ontology service snapshot, not the unrecovered historical seeding release or a version guarantee for the live backend. |
| specific-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Definition, null fixed chemical fields and complete outgoing role hierarchy | supports | CHEBI:26672 describes microbial low-mass iron(III) chelators for iron transport and sequestration, with cofactor, iron(III)-chelator and iron-ionophore parents. This source role hierarchy does not itself qualify a non-substrate protein requirement for an exact free ligand. |
| conjugate-context | https://www.ebi.ac.uk/chebi/backend/api/public/compound/136993/; Definition, chemical_data, default_structure and outgoing conjugate relation | context_only | CHEBI:136993 represents staphyloferrin B(2−), C16H22N4O11, with three carboxylates and a protonated amine. It retains the two specified configurations of the neutral source graph and is linked as its conjugate base. Its pH 7.3 predominance statement remains external source context, not an independently measured target claim. |
| structure-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8400765%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID8400765; DOI10.1007/BF00205858; complete indexed abstract | supports | The primary abstract reports staphyloferrin B purification from S. hyicus DSM 20459, mass 448, hydrolysis products, NMR connectivity and iron-transport activity. Hydrolysis products are distinguished from the intact structural units. |
| biosynthesis-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19775248%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID19775248; DOI10.1111/j.1365-2958.2009.06880.x; complete indexed abstract | supports | Purified Sbn enzymes reconstituted SB biosynthesis in vitro from component substrates. The product promoted iron-starved S. aureus growth via SirABC; the diaminoethane unit arises through decarboxylation of a Dap-containing intermediate rather than requiring free diaminoethane input. |
| synthesis-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A26030732%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID26030732; DOI10.1021/jacs.5b04557; complete indexed abstract | supports | The primary abstract reports synthetic SB, citryl-epimer and imide comparisons. Native SB restored growth of iron-limited S. aureus USA300 JE2; citryl epimerization changed iron-binding and siderophore behavior. This supports stereochemical discrimination and iron acquisition in the tested system. |
| receptor-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20810662%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID20810662; DOI10.1074/jbc.M110.172924; complete indexed abstract | supports | The primary abstract reports apo and Fe(III)-SB-bound SirA structures, low-nanomolar complex affinity and comparison with HtsA/FeSA specificity. SB ligates Fe(III) with five oxygen atoms and one nitrogen in the reported complex. These are ferric-ligand binding observations, not evidence that the iron-free neutral acid is an obligatory non-substrate cofactor. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml; Executed 2026-10-21T16:17:08Z through 2026-10-21T16:17:09Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/sodium-ascorbate-chebi113451.yaml data/traits/function/cofactor_requirement/chebi/staphyloferrin-a-chebi84711.yaml data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml data/traits/function/cofactor_requirement/chebi/strontium-2-chebi35104.yaml data/traits/function/cofactor_requirement/chebi/sulfate-chebi16189.yaml data/traits/function/cofactor_requirement/chebi/tb-chebi33377.yaml data/traits/function/cofactor_requirement/chebi/tetra-3-sulfido-tetrairon-chebi49883.yaml data/traits/function/cofactor_requirement/chebi/tetrahydrodictyopterin-chebi52447.yaml data/traits/function/cofactor_requirement/chebi/tetrahydromonapterin-chebi71177.yaml data/traits/function/cofactor_requirement/chebi/thiamine-1-diphosphate-3-chebi58937.yaml; Executed 2026-10-21T16:17:04Z through 2026-10-21T16:18:28Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml; Executed 2026-10-21T16:17:09Z through 2026-10-21T16:17:09Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T16:18:28Z through 2026-10-21T16:18:29Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The external dianion source asserts dominance at pH 7.3; that quantitative population claim is not present in the reviewed neutral target and is not independently validated here. The primary abstracts do not resolve every bound protonation state, ferric-complex microstate or physiological protein requirement.
- Indexed primary abstracts were read in full where cited as abstracts; claims requiring full text are restricted to the explicitly named successful PMC HTML sources. Empty HTTP500 XML deliveries and exploratory queries are not scientific support. No search result snippet is used as experimental evidence.
- The chemical source may represent a free entity or salt while experiments use a bound, complexed or solution species. Positive activity is retained without inferring a universal physiological requirement, a chemical-state merge or the absence of other activities.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T162814Z-staphyloferrin-b-chebi134612
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires staphyloferrin B
started_at: '2026-10-21T16:16:22Z'
finished_at: '2026-10-21T16:28:14Z'
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
summary: The exact staphyloferrin B chemical identity and source-role provenance are
  supported, with positive experimental context assessed at its stated scope. The
  record still asserts a chemical entity as an equivalent protein-requirement class,
  a confirmed major grounding defect. The siderophore annotation is authentic positive
  source context, with verified cofactor ancestry. A ferric-complex transport role
  or biosynthetic product role cannot by itself qualify the neutral free acid under
  the current non-substrate requirement category. A curator must adjudicate exact
  activity and state before adding an optional participant with its required role.
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
  - path: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
    sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
    sha256: a749b94eb2a12a1466dadbe1d2d011efd164ca6786a2687948f49307f06e6e13
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
  selection: Path-order position 3 in batch 035. Fresh main inventory has 429359 records.
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
    b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb;
    c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585, the union covers 338 record paths, leaving
    429021 before this batch. 35 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
targets:
- kind: generated
  label: requires staphyloferrin B
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_134612
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/sodium-ascorbate-chebi113451.yaml
    data/traits/function/cofactor_requirement/chebi/staphyloferrin-a-chebi84711.yaml
    data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
    data/traits/function/cofactor_requirement/chebi/strontium-2-chebi35104.yaml data/traits/function/cofactor_requirement/chebi/sulfate-chebi16189.yaml
    data/traits/function/cofactor_requirement/chebi/tb-chebi33377.yaml data/traits/function/cofactor_requirement/chebi/tetra-3-sulfido-tetrairon-chebi49883.yaml
    data/traits/function/cofactor_requirement/chebi/tetrahydrodictyopterin-chebi52447.yaml
    data/traits/function/cofactor_requirement/chebi/tetrahydromonapterin-chebi71177.yaml
    data/traits/function/cofactor_requirement/chebi/thiamine-1-diphosphate-3-chebi58937.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: The exact ChEBI backend and OLS identifiers, chemical state and source
    siderophore role with cofactor ancestry were inspected alongside current licence
    metadata, exact chemical comparisons and the cited primary sources. Source resolution
    passed; it does not validate the chemical-to-trait equivalence or independently
    qualify every proposed requirement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  evidence_ids:
  - chemical-source
  - chemical-ontology
  - cofactor-role
  - source-license
  - ontology-release
  - specific-role
  - conjugate-context
  - structure-primary
  - biosynthesis-primary
  - synthesis-primary
  - receptor-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T16:16:22Z'
  snapshot_sha256: a749b94eb2a12a1466dadbe1d2d011efd164ca6786a2687948f49307f06e6e13
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
  accessed_at: '2026-10-21T16:16:22Z'
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
  accessed_at: '2026-10-21T16:16:22Z'
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
  accessed_at: '2026-10-21T16:16:22Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T16:16:22Z'
  snapshot_sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: chemical-source
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/134612/
  accessed_at: '2026-10-21T16:17:12.199145Z'
  snapshot_sha256: 026e6864d78bb0270cddd4751ce6f1e877c24d590a6f9d1bcb23e01814fef988
  support: supports
  locator: Exact entry identity, names, definition, chemical_data, default_structure,
    compound_origins and complete outgoing ontology relations; source-linked citations
    inspected as specified separately
  summary: CHEBI:134612 is neutral, iron-free staphyloferrin B, C16H24N4O11, charge
    0, with the two stereocentres specified in its IUPAC name and default structure.
    The source definition identifies L-2,3-diaminopropionic acid, citrate, diaminoethane
    and α-ketoglutaric-acid units. Outgoing relations include siderophore/bacterial-metabolite
    roles and a conjugate link to CHEBI:136993. Source origins name S. aureus and
    S. hyicus with primary references.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:134612
  accessed_at: '2026-10-21T16:17:12.228751Z'
  snapshot_sha256: 4d9f506041c8733dd9411776ed381ce680e14a6bdf2da60b27800d4f7802dde7
  support: supports
  locator: Exact term identity, obsolete status, description, synonyms and chemical
    annotations
  summary: The exact OLS term is current and nonobsolete, resolves the same chemical
    label and state, and provides the recorded description, aliases and structure
    annotations. These fields describe a chemical entity; they do not assert equivalence
    to the synthesized protein-requirement class.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition, null chemical fields and complete outgoing role hierarchy
  summary: CHEBI:23357 defines a biochemical role required for enzyme activity and
    is a subclass of biochemical role. Its null fixed chemical structure is appropriate
    for a role. The definition does not establish which protein requires the exact
    reviewed entity.
- evidence_id: source-license
  kind: database
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: About ChEBI chemical/ontology scope and Licensing section
  summary: The official ChEBI About page describes chemical entities and roles and
    explicitly permits data reuse under CC BY 4.0. This supports upstream attribution/licence,
    without licensing all independently cited publisher material alike.
- evidence_id: ontology-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Ontology configuration version/versionIri and load metadata
  summary: The captured OLS metadata identifies ChEBI version 256. This describes
    that ontology service snapshot, not the unrecovered historical seeding release
    or a version guarantee for the live backend.
- evidence_id: specific-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T15:56:28.026593Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Definition, null fixed chemical fields and complete outgoing role hierarchy
  summary: CHEBI:26672 describes microbial low-mass iron(III) chelators for iron transport
    and sequestration, with cofactor, iron(III)-chelator and iron-ionophore parents.
    This source role hierarchy does not itself qualify a non-substrate protein requirement
    for an exact free ligand.
- evidence_id: conjugate-context
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/136993/
  accessed_at: '2026-10-21T16:19:10.591213Z'
  snapshot_sha256: e8846f4e968ba8d2479b9e3699d9823bf99040d37e394700464f0469e3f1a941
  support: context_only
  locator: Definition, chemical_data, default_structure and outgoing conjugate relation
  summary: CHEBI:136993 represents staphyloferrin B(2−), C16H22N4O11, with three carboxylates
    and a protonated amine. It retains the two specified configurations of the neutral
    source graph and is linked as its conjugate base. Its pH 7.3 predominance statement
    remains external source context, not an independently measured target claim.
- evidence_id: structure-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A8400765%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:19:12.606878Z'
  snapshot_sha256: 5b10937c3ed0dd81efdcd24e7b990b98a073f7e2115bc48e1f8a61dbdfbbcbfe
  support: supports
  locator: PMID8400765; DOI10.1007/BF00205858; complete indexed abstract
  summary: The primary abstract reports staphyloferrin B purification from S. hyicus
    DSM 20459, mass 448, hydrolysis products, NMR connectivity and iron-transport
    activity. Hydrolysis products are distinguished from the intact structural units.
- evidence_id: biosynthesis-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19775248%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:19:12.766285Z'
  snapshot_sha256: de25320f2c2cb57b7e959273c02dc2587bac11f39a59f758a49d622715ac91ae
  support: supports
  locator: PMID19775248; DOI10.1111/j.1365-2958.2009.06880.x; complete indexed abstract
  summary: Purified Sbn enzymes reconstituted SB biosynthesis in vitro from component
    substrates. The product promoted iron-starved S. aureus growth via SirABC; the
    diaminoethane unit arises through decarboxylation of a Dap-containing intermediate
    rather than requiring free diaminoethane input.
- evidence_id: synthesis-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A26030732%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:19:12.884563Z'
  snapshot_sha256: 85900842dc240cf7d59598d899b4ae387ea12e8c18b57219bee3122b59f66c5b
  support: supports
  locator: PMID26030732; DOI10.1021/jacs.5b04557; complete indexed abstract
  summary: The primary abstract reports synthetic SB, citryl-epimer and imide comparisons.
    Native SB restored growth of iron-limited S. aureus USA300 JE2; citryl epimerization
    changed iron-binding and siderophore behavior. This supports stereochemical discrimination
    and iron acquisition in the tested system.
- evidence_id: receptor-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20810662%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T16:19:40.383039Z'
  snapshot_sha256: a49424f2af1696dcc4e6d0a1df1eaaa1001e5ff960e9830ceda96e54bd413a09
  support: supports
  locator: PMID20810662; DOI10.1074/jbc.M110.172924; complete indexed abstract
  summary: The primary abstract reports apo and Fe(III)-SB-bound SirA structures,
    low-nanomolar complex affinity and comparison with HtsA/FeSA specificity. SB ligates
    Fe(III) with five oxygen atoms and one nitrogen in the reported complex. These
    are ferric-ligand binding observations, not evidence that the iron-free neutral
    acid is an obligatory non-substrate cofactor.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  locator: Executed 2026-10-21T16:17:08Z through 2026-10-21T16:17:09Z; exit 0
  accessed_at: '2026-10-21T16:17:09Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/sodium-ascorbate-chebi113451.yaml
    data/traits/function/cofactor_requirement/chebi/staphyloferrin-a-chebi84711.yaml
    data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
    data/traits/function/cofactor_requirement/chebi/strontium-2-chebi35104.yaml data/traits/function/cofactor_requirement/chebi/sulfate-chebi16189.yaml
    data/traits/function/cofactor_requirement/chebi/tb-chebi33377.yaml data/traits/function/cofactor_requirement/chebi/tetra-3-sulfido-tetrairon-chebi49883.yaml
    data/traits/function/cofactor_requirement/chebi/tetrahydrodictyopterin-chebi52447.yaml
    data/traits/function/cofactor_requirement/chebi/tetrahydromonapterin-chebi71177.yaml
    data/traits/function/cofactor_requirement/chebi/thiamine-1-diphosphate-3-chebi58937.yaml
  locator: Executed 2026-10-21T16:17:04Z through 2026-10-21T16:18:28Z; exit 0
  accessed_at: '2026-10-21T16:18:28Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml
  locator: Executed 2026-10-21T16:17:09Z through 2026-10-21T16:17:09Z; exit 0
  accessed_at: '2026-10-21T16:17:09Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T16:18:28Z through 2026-10-21T16:18:29Z; exit 0
  accessed_at: '2026-10-21T16:18:29Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: 'The target’s structural-unit definition agrees with the current graph
    and the primary biosynthesis/chemical-characterization abstracts. Its neutral
    free-acid state remains separate from the dianion and Fe(III) complex. The specified
    citryl stereochemistry matters: the primary synthesis study distinguishes the
    biological behavior of a citryl epimer from that of native SB.'
  evidence_ids:
  - record
  - chemical-source
  - chemical-ontology
  - conjugate-context
  - structure-primary
  - biosynthesis-primary
  - synthesis-primary
  topic: Exact chemical identity and state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-5
- area: consistency
  outcome: supported
  summary: The local parent resolves and reflects the source siderophore→cofactor
    path. This supports provenance and the intended candidate grouping, while chemical-role
    membership is not itself a protein requirement or an assertion that all optional
    protein examples are qualified.
  evidence_ids:
  - chemical-source
  - cofactor-role
  - local-parent-1
  - specific-role
  - owner
  topic: Source role and local requirement hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-6
- area: evidence
  outcome: supported
  summary: Primary isolation, synthesis and biosynthesis evidence supports staphyloferrin
    B production, chemical assembly, iron acquisition and growth recovery under the
    tested iron-limited conditions. The SirA structure abstract supplies positive
    recognition of ferric SB. These observations do not establish a protein requirement
    for the neutral free acid as a non-substrate cofactor, and do not prove that all
    other roles are absent.
  evidence_ids:
  - structure-primary
  - biosynthesis-primary
  - synthesis-primary
  - receptor-primary
  topic: Positive experimental context and its limits
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-7
- area: representation
  outcome: unknown
  summary: The siderophore annotation is authentic positive source context, with verified
    cofactor ancestry. A ferric-complex transport role or biosynthetic product role
    cannot by itself qualify the neutral free acid under the current non-substrate
    requirement category. A curator must adjudicate exact activity and state before
    adding an optional participant with its required role.
  evidence_ids:
  - schema
  - chemical-source
  - structure-primary
  - biosynthesis-primary
  - synthesis-primary
  - receptor-primary
  topic: Activity-relative requirement and chemical participant
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The copied chemical identity and definition are traceable to current ChEBI.
    The opening protein-requirement assertion is generated by the maintained seeder.
    CC BY 4.0 is supported by the source licence; the target does not pin the original
    ChEBI release. The source role and these current snapshots do not independently
    establish the synthesized requirement.
  evidence_ids:
  - record
  - owner
  - chemical-source
  - chemical-ontology
  - source-license
  - ontology-release
  topic: Current source support and licence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The xref resolves successfully, but CHEBI:134612 denotes staphyloferrin
    B as a chemical entity. The record denotes proteins requiring it. Those entity
    types are not source-direct equivalents under the captured schema.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical-source
  topic: Chemical entity versus equivalent trait
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-134612.chemical-entity-equivalence
  category: grounding
  severity: major
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  title: Chemical entity asserted as an equivalent protein-requirement class
  description: The target places CHEBI:134612 in xrefs, whose schema meaning requires
    true source-direct equivalence. Current ChEBI identifies staphyloferrin B as a
    chemical entity, while the local identifier, label and synthesized first sentence
    identify a protein requirement. Source role membership and chemical provenance
    do not equate those classes. The defect concerns the asserted relation, not failure
    of the chemical ID or absence of an optional protein example.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical-source
  normalization_reason: The record equates different entity types in a defining grounding
    field. This materially changes representation semantics while the exact chemical
    identity remains resolved.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct the maintained scripts/seed_chebi_cofactor.py transformation
    so this requirement class does not assert chemical-entity equivalence. Preserve
    CHEBI:134612 as chemical/source provenance with its exact state and uncertainty.
    Adjudicate the activity-relative role before considering an optional chemical_participants
    entry; the required role of any added entry must be justified rather than automatically
    set to COFACTOR. If evidence cannot support a typed participant, retain the source
    association and uncertainty through an appropriate supported representation. Preserve
    the positive biological context and distinguish the generated requirement sentence
    from copied chemical description. Preview and scope the normal ChEBI emitter repair
    through its audited writer route; main emits its selected cohort with --force/--apply,
    so control unintended cohort changes.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_134612
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - 'Inspect the regenerated target data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml:
    no false chemical-to-trait xref, preserved exact chemical/source provenance and
    a documented activity/state decision; any optional participant has a curator-supported
    role, and no unqualified protein example or automatic state replacement is introduced.'
  - Run just validate data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/staphyloferrin-b-chebi134612.yaml,
    recording actual results.
  - For maintained writer/code changes run just audit-writers, just lint, focused
    pytest and just test; perform the required full record validation before merge.
    Review the regenerated diff and create a fresh source-pinned scientific observation;
    do not overwrite this review.
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
- The external dianion source asserts dominance at pH 7.3; that quantitative population
  claim is not present in the reviewed neutral target and is not independently validated
  here. The primary abstracts do not resolve every bound protonation state, ferric-complex
  microstate or physiological protein requirement.
- Indexed primary abstracts were read in full where cited as abstracts; claims requiring
  full text are restricted to the explicitly named successful PMC HTML sources. Empty
  HTTP500 XML deliveries and exploratory queries are not scientific support. No search
  result snippet is used as experimental evidence.
- The chemical source may represent a free entity or salt while experiments use a
  bound, complexed or solution species. Positive activity is retained without inferring
  a universal physiological requirement, a chemical-state merge or the absence of
  other activities.
tags:
- unreviewed-path-order
- batch-035
- chebi-cofactor
```
