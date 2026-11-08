# Review of obligately aerobic

- Review: 20261021T175302Z-obligately-aerobic-metpo1000606
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T17:48:40Z
- Finished UTC: 2026-10-21T17:53:02Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The obligately aerobic record resolves correctly and copies the current METPO phenotype. One confirmed major concerns its organism-growth meaning being represented as a protein trait. Keep the organism oxygen-growth requirement separate from protein oxygen chemistry, and retain the parent’s typically qualifier. Do not infer a universal oxygen concentration, enzyme substrate role or pathway from this class.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 10 in batch 040. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb; ee9a05771251fd84096ca40cfee30ea23e064f91; c589a5515b45e7337f41a032609859f3a20fb7f9, the union covers 388 record paths, leaving 428971 before this batch. 40 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| METPO:1000606 | data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml | generated | obligately aerobic |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | METPO:1000606 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | METPO:1000606 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | METPO:1000606 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | METPO:1000606 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | METPO:1000606 | Inspected complete METPO:1000606 target and recursive local ancestors, actual maintained route/dependencies, exact fresh official target/source ancestor stanzas, header, README, licence and commit metadata. Selected cited ontology objects were independently inspected at the recorded scope. Current source identity and copied fields agree, but this does not establish protein-domain eligibility, original seed bytes or every upstream physiological claim. |

## Scientific And Domain Assessments

### Exact microbial source identity

identity: supported. Targets: METPO:1000606.

METPO:1000606 resolves to obligately aerobic; the current source and local preferred name/definition agree. This is a correct source phenotype identity, distinct from eligibility as a protein-trait class.

### Source labels and synonym scope

nomenclature: supported. Targets: METPO:1000606.

Obligate aerobe and obligate aerobic are retained as RELATED synonyms. The repeated source obligate aerobic occurrence is deduplicated without changing scope. No independent protein identity is asserted by those aliases.

### Defining organism-growth assertion

evidence: supported. Targets: METPO:1000606.

The exact source requires molecular oxygen for organism growth. This differs from simply being able to grow in oxygen. It does not establish an oxygen substrate requirement of an individual protein, a universal respiratory enzyme mechanism or a numerical oxygen threshold. This assessment establishes authentic source meaning, not an independent assay of each organism or protein.

### Independent annotation support and limits

evidence: unknown. Targets: METPO:1000606.

The directly cited MICRO:0000516 annotation says the organism grows in oxygen and is incapable of anaerobic growth, supporting the obligate-growth distinction. Its additional source annotation quotes general respiratory background attributed to Wikipedia; that is not an independently inspected primary experiment and is not promoted to a universal protein mechanism.

### Numerical or qualitative growth boundary

quantity: unknown. Targets: METPO:1000606.

Keep the organism oxygen-growth requirement separate from protein oxygen chemistry, and retain the parent’s typically qualifier. Do not infer a universal oxygen concentration, enzyme substrate role or pathway from this class. Current ontology wording is verified; no new strain experiment or protein threshold was established.

### Local and source ancestry

consistency: supported. Targets: METPO:1000606.

The aerobic parent describes growth in oxygen, typically using it as terminal electron acceptor. The obligate child adds an oxygen-growth requirement and fits that broader phenotype. Typical parent mechanism wording is not proof that every protein in the organism directly consumes oxygen. Oxygen-preference and phenotype ancestors resolve. Correct copied hierarchy does not by itself resolve the project-domain mismatch.

### Organism phenotype versus protein capability

representation: concern. Targets: METPO:1000606.

The defining evidence describes growth of an organism or population, whereas the emitted object is a ProteinTraitRecord in FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. A protein mechanism or response cannot be inferred simply from that organism phenotype. This does not deny that proteins contribute to growth.

### Preserve resolved source identity

grounding: supported. Targets: METPO:1000606.

The METPO identifier correctly anchors the source phenotype. No chemical or other xref is asserted. A distinct future protein class would need its own justified identity and scoped relationship to the organism phenotype; the source identifier must not be silently reassigned.

### Maintained source route and disposition

ownership: supported. Targets: METPO:1000606.

seed_obo.py owns the target via the inspected METPO route; lexical helpers and the separate phenotype-grouping writer are captured. A change must address maintained eligibility plus existing output and references. Excluding future emission does not remove a previously emitted target.

### Current provenance and original-seed limit

provenance: unknown. Targets: METPO:1000606.

Current main and pinned OBO bodies agree, and their release/header/licence agree with the local fields. Fresh access metadata and path-commit response are captured. The actual original seed input and execution have not been reconstructed.

### Class scope before optional enrichment

completeness: concern. Targets: METPO:1000606.

The source phenotype has a complete reusable definition. The material concern is its protein-domain eligibility, not missing optional graphs, examples or representations. Supplying one protein example would not alone change the defining subject.

### No asserted molecular mechanism

graph: not_applicable. Targets: METPO:1000606.

The entire target contains no causal graph, reaction, participants, residues, sequence or structural coordinates. No mechanism validation or molecular claim is inferred.

### Status, instances and expression context

scope: supported. Targets: METPO:1000606.

The target remains CLASS/SEEDED. No protein example, native status or curation-history event is promoted. iModulonDB is inapplicable without a specified gene, organism/dataset or expression claim; that is not negative biological evidence.

## Findings

### F1: Organism growth phenotype is emitted as a protein-trait class

major / open / confirmed; issue key: metpo.environmental-response.METPO-1000606.organism-growth-as-protein-trait.

The exact source requires molecular oxygen for organism growth. This differs from simply being able to grow in oxygen. It does not establish an oxygen substrate requirement of an individual protein, a universal respiratory enzyme mechanism or a numerical oxygen threshold. The official source and captured ancestors supply an organism-level denotation. The maintained route copies that unchanged into a protein-trait class without a separately supported protein predicate. This is a domain/representation error despite correct source identity; it is not a wrong-accession blocker or a universal denial of protein environmental responses.

## Recommended Actions And Acceptance Checks

### A1

Adjudicate METPO:1000606 in the maintained scripts/seed_obo.py source-eligibility/domain policy. Preserve its organism-phenotype meaning in an appropriate representation or explicitly exclude it from protein-trait emission, with an audited disposition of the existing file and references. If a separate protein response is justified, give it an independently supported definition and identity rather than reinterpreting this METPO identifier. Keep the organism oxygen-growth requirement separate from protein oxygen chemistry, and retain the parent’s typically qualifier. Do not infer a universal oxygen concentration, enzyme substrate role or pathway from this class. Do not hand-edit generated output or require optional protein examples/graphs merely to fill fields.

- Document source-domain eligibility and the existing-record disposition for METPO:1000606; preserve the organism phenotype and source identifier unless an explicit audited migration is adjudicated.
- Keep the organism oxygen-growth requirement separate from protein oxygen chemistry, and retain the parent’s typically qualifier. Do not infer a universal oxygen concentration, enzyme substrate role or pathway from this class. Do not equate an association with a protein trait to a subclass or equivalent-class assertion.
- Exercise the maintained METPO route on a pinned input in dry-run mode. Inspect proposed output and separately audit existing-file retirement/migration and affected references; merely skipping future emission is insufficient.
- For a retained/changed target run just validate data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml, just validate-all data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml, and just audit-graphs data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml. If the disposition changes paths, run those checks on documented resulting path(s), verify the former path/identifier disposition with an audit trail, and do not silently substitute identifiers.
- For maintained-writer changes run just lint, applicable focused pytest, just test and just audit-writers. If the registry changes run just sources-check. Before a record-change merge run full just validate-all and just validate-history; preserve real logs and create a fresh immutable structured review of the resulting record or audited disposition.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml; Entire target YAML | supports | Complete YAML read: exact METPO identifier, preferred name, full growth definition, source date, CLASS/SEEDED, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, parent and all synonym scopes. The target contains no instance protein, extra evidence citation, xref, molecular representation, chemical participant, example, discussion or causal graph. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord; TraitAxisEnum; FUNC_ENVIRONMENTAL_RESPONSE; definition, parent_traits and optional representation slots | supports | ProteinTraitRecord and its environmental-response category remain protein-trait representations. parent_traits asserts broader classes; optional examples, graphs and molecular representations are not compulsory for every class. |
| project-rules | CLAUDE.md; Purpose; core invariants; curation and validation agreements | supports | The project invariant is protein-trait classes, with axes selected by defining representation and evidence scoped to the exact assertion. Generated corrections belong in maintained writers; review does not promote native scientific status. |
| checklist | .claude/skills/curate-yaml-record/references/review-checklist.md; Complete field-by-field audit | supports | The field audit requires correct class identity, source definitions and hierarchy, evidence-scoped representation and faithful status; it does not mandate every optional field. |
| owner | scripts/seed_obo.py; SOURCES METPO routes; build_routing; build_yaml; read_release_stamp; seed_source | supports | SOURCES defines METPO environmental routes. build_routing includes each route root and its is-a descendants. build_yaml copies source identity/definition, retains same-source parents independently of routing, emits CLASS/SEEDED and source licence, deduplicates synonyms and drops preferred-label duplicates. The transform does not independently establish protein meaning. seed_source skips existing paths unless force is used; route exclusion alone does not retire existing output. |
| obo-helper | scripts/obo_syntax.py; unescape, strip_comment, strip_suffixes | supports | The inspected lexical helpers handle quoted text, comments and suffix syntax; they do not alter the biological subject of the definition. |
| yaml-helper | scripts/yaml_emit.py; yaml_escape and slugify | supports | The scalar/slug helpers format names and output text, without supplying biological evidence. |
| grouping-owner | scripts/seed_grouping_parents.py; TARGETS METPO:1000059 and grouping emission | supports | The phenotype boundary record is maintained by the grouping writer. Its intentionally stopped local ancestry is not treated as a broken relation, and this writer is not the reviewed leaf owner. |
| registry | download.yaml; METPO block | supports | The METPO source entry declares seeded status, CC-BY-4.0, seed_obo.py and functional routes. These are provenance and maintenance declarations, not individual protein-class qualification. |
| browser-source | scripts/build_docs_index.py; infer_source METPO branch | supports | The METPO identifier/source is recognized by browser source inference; display provenance is not biological evidence. |
| local-ancestor-1 | data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml; Entire captured ancestor YAML | supports | Complete ancestor YAML read with its defining growth/phenotype subject, hierarchy, source date, licence, synonyms and status. It is context for this one record, not an independent certification of the parent. |
| local-ancestor-2 | data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml; Entire captured ancestor YAML | supports | Complete ancestor YAML read with its defining growth/phenotype subject, hierarchy, source date, licence, synonyms and status. It is context for this one record, not an independent certification of the parent. |
| local-ancestor-3 | data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml; Entire captured ancestor YAML | supports | Complete ancestor YAML read with its defining growth/phenotype subject, hierarchy, source date, licence, synonyms and status. It is context for this one record, not an independent certification of the parent. |
| obligate-oxygen-context | https://www.ebi.ac.uk/ols4/api/ontologies/micro/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMICRO_0000516; Complete exact OLS term object: identifier, label, description, all annotations, status, synonyms and page metadata | context_only | The nonobsolete MICRO:0000516 term has an annotation.definition for oxygen-present growth and inability to grow without oxygen, plus exact-synonym annotations. The description array is empty but the definition is present. Additional respiratory text is explicitly in a Wikipedia-attributed definition-source annotation; no primary experimental verification of that background is claimed. |
| metpo-ontology | https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo; Header; complete METPO:1000606 stanza at line 8280; all captured ancestor stanzas | supports | Exact METPO:1000606 name, definition, immediate parent and synonym scopes agree with the target. The exact source requires molecular oxygen for organism growth. This differs from simply being able to grow in oxygen. It does not establish an oxygen substrate requirement of an individual protein, a universal respiratory enzyme mechanism or a numerical oxygen threshold. The ontology header and complete source ancestors describe microbial phenotypes. Definition annotations are source citations, not automatic equivalent-class mappings. |
| metpo-main | https://raw.githubusercontent.com/berkeleybop/metpo/main/metpo.obo; Whole-body hash equality and exact stanzas | supports | The freshly captured main OBO body is byte-identical to the commit-pinned source. This establishes current agreement, not the original seed input bytes. |
| metpo-project | https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md; Full README; purpose, namespace and licence | supports | The complete official README identifies microbial ecophysiological trait/phenotype scope, the w3id.org/metpo seven-digit namespace and CC-BY-4.0. Term-body resolution was verified; universal landing-page redirects were not tested. |
| metpo-license | https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE; Official licence identification and terms | supports | The official licence identifies Creative Commons Attribution 4.0 International, consistent with the local field and ontology header. Individual upstream citation licences are not separately audited. |
| metpo-commit | https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&amp;per_page=1; Complete first returned commit object for metpo.obo | supports | The path-scoped response identifies commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 dated 2026-09-03, while the captured OBO header remains 2026-06-12. Access time, commit time and declared release are separate; none proves the original seed execution. |
| validation-1 | just validate data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml; Executed 2026-10-21T17:49:14Z through 2026-10-21T17:49:18Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/environmental_response/metpo/hyperthermophilic-metpo1000617.yaml data/traits/function/environmental_response/metpo/mesophilic-metpo1000615.yaml data/traits/function/environmental_response/metpo/metal-tolerance-metpo1007074.yaml data/traits/function/environmental_response/metpo/microaerophilic-metpo1000604.yaml data/traits/function/environmental_response/metpo/microaerotolerant-metpo1000610.yaml data/traits/function/environmental_response/metpo/moderately-halophilic-metpo1000623.yaml data/traits/function/environmental_response/metpo/neutrophilic-metpo1003001.yaml data/traits/function/environmental_response/metpo/non-halophilic-metpo1000624.yaml data/traits/function/environmental_response/metpo/obligately-acidophilic-metpo1003006.yaml data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml; Executed 2026-10-21T17:49:31Z through 2026-10-21T17:51:03Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml; Executed 2026-10-21T17:49:18Z through 2026-10-21T17:49:18Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T17:51:03Z through 2026-10-21T17:51:04Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The directly cited MICRO:0000516 annotation says the organism grows in oxygen and is incapable of anaerobic growth, supporting the obligate-growth distinction. Its additional source annotation quotes general respiratory background attributed to Wikipedia; that is not an independently inspected primary experiment and is not promoted to a universal protein mechanism.
- Current source stanzas, their declared release and licence were inspected; historical seed bytes were not reconstructed. Source annotation objects are provenance, not assumed equivalence assertions.
- The selected ontology definitions were inspected, not the entire upstream citation network, cited textbook contents or all strain-specific experiments. No numerical or mechanistic protein conclusion is qualified.
- Only this record and captured ancestors are reviewed. No corpus-wide missing-record/evidence assertion or broad negative search is made. Statements about optional omissions concern the entire target bytes read.
- This review does not deny molecular contributions to the organism phenotype. Optional examples, participants and mechanisms are not compulsory; iModulonDB is inapplicable to this generic class without a gene/dataset.
- Raw bodies, actual access times and digests are retained in scratch. Native checks and saving are root-owned; this author made no native gate, trait edit, Git mutation, public write or status promotion.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T175302Z-obligately-aerobic-metpo1000606
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of obligately aerobic
started_at: '2026-10-21T17:48:40Z'
finished_at: '2026-10-21T17:53:02Z'
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
summary: The obligately aerobic record resolves correctly and copies the current METPO
  phenotype. One confirmed major concerns its organism-growth meaning being represented
  as a protein trait. Keep the organism oxygen-growth requirement separate from protein
  oxygen chemistry, and retain the parent’s typically qualifier. Do not infer a universal
  oxygen concentration, enzyme substrate role or pathway from this class.
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
  - path: data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml
    sha256: 8dac2b83699a98e885de3c6caae21a23457f3a2b63f88190a4a5f21ce9323062
    role: context
  - path: data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
    sha256: 78de317cb197b4033ddbfe2f9786353308e251b8c2df30315bc8c9943ca3b44c
    role: target
  - path: data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml
    sha256: 1ca0c206d8dcb38047a5f09b4843571524d85af2915375b26f8fa4c69a9e07c5
    role: context
  - path: data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml
    sha256: 903daba1e34fdc7cace6ae639bd6bab85f0fb9acb6dfd33979ed8e1970992ddc
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
  - path: scripts/obo_syntax.py
    sha256: 86cd5936ecb214f41073fc5ac56425efe647b56bf9a663dad62f6edfad3fbc0e
    role: context
  - path: scripts/seed_grouping_parents.py
    sha256: 504e4630cce0d19e86fe47a55b02008a77ebc8cfb6f4cdfddf487f1401a724f7
    role: context
  - path: scripts/seed_obo.py
    sha256: 8b33fbdac45c28420b3e6ca31d0d9feb16c90701eb77c392b571f1b3261c7a9f
    role: context
  - path: scripts/yaml_emit.py
    sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 10 in batch 040. Fresh main inventory has 429359
    records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
    c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4;
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb;
    ee9a05771251fd84096ca40cfee30ea23e064f91; c589a5515b45e7337f41a032609859f3a20fb7f9,
    the union covers 388 record paths, leaving 428971 before this batch. 40 inventories
    were combined. Unpublished local coverage is explicitly not published or merged
    main coverage. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - METPO:1000606
targets:
- kind: generated
  label: obligately aerobic
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  path: data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  record_class: ProteinTraitRecord
  target_id: METPO:1000606
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - METPO:1000606
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/environmental_response/metpo/hyperthermophilic-metpo1000617.yaml
    data/traits/function/environmental_response/metpo/mesophilic-metpo1000615.yaml
    data/traits/function/environmental_response/metpo/metal-tolerance-metpo1007074.yaml
    data/traits/function/environmental_response/metpo/microaerophilic-metpo1000604.yaml
    data/traits/function/environmental_response/metpo/microaerotolerant-metpo1000610.yaml
    data/traits/function/environmental_response/metpo/moderately-halophilic-metpo1000623.yaml
    data/traits/function/environmental_response/metpo/neutrophilic-metpo1003001.yaml
    data/traits/function/environmental_response/metpo/non-halophilic-metpo1000624.yaml
    data/traits/function/environmental_response/metpo/obligately-acidophilic-metpo1003006.yaml
    data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - METPO:1000606
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - METPO:1000606
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
  - METPO:1000606
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Inspected complete METPO:1000606 target and recursive local ancestors,
    actual maintained route/dependencies, exact fresh official target/source ancestor
    stanzas, header, README, licence and commit metadata. Selected cited ontology
    objects were independently inspected at the recorded scope. Current source identity
    and copied fields agree, but this does not establish protein-domain eligibility,
    original seed bytes or every upstream physiological claim.
  target_ids:
  - METPO:1000606
  evidence_ids:
  - record
  - schema
  - project-rules
  - checklist
  - owner
  - obo-helper
  - yaml-helper
  - grouping-owner
  - registry
  - browser-source
  - local-ancestor-1
  - local-ancestor-2
  - local-ancestor-3
  - obligate-oxygen-context
  - metpo-ontology
  - metpo-main
  - metpo-project
  - metpo-license
  - metpo-commit
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 78de317cb197b4033ddbfe2f9786353308e251b8c2df30315bc8c9943ca3b44c
  support: supports
  locator: Entire target YAML
  summary: 'Complete YAML read: exact METPO identifier, preferred name, full growth
    definition, source date, CLASS/SEEDED, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, parent
    and all synonym scopes. The target contains no instance protein, extra evidence
    citation, xref, molecular representation, chemical participant, example, discussion
    or causal graph.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  locator: ProteinTraitRecord; TraitAxisEnum; FUNC_ENVIRONMENTAL_RESPONSE; definition,
    parent_traits and optional representation slots
  summary: ProteinTraitRecord and its environmental-response category remain protein-trait
    representations. parent_traits asserts broader classes; optional examples, graphs
    and molecular representations are not compulsory for every class.
- evidence_id: project-rules
  kind: record_content
  reference: CLAUDE.md
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
  support: supports
  locator: Purpose; core invariants; curation and validation agreements
  summary: The project invariant is protein-trait classes, with axes selected by defining
    representation and evidence scoped to the exact assertion. Generated corrections
    belong in maintained writers; review does not promote native scientific status.
- evidence_id: checklist
  kind: record_content
  reference: .claude/skills/curate-yaml-record/references/review-checklist.md
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
  support: supports
  locator: Complete field-by-field audit
  summary: The field audit requires correct class identity, source definitions and
    hierarchy, evidence-scoped representation and faithful status; it does not mandate
    every optional field.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_obo.py
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 8b33fbdac45c28420b3e6ca31d0d9feb16c90701eb77c392b571f1b3261c7a9f
  support: supports
  locator: SOURCES METPO routes; build_routing; build_yaml; read_release_stamp; seed_source
  summary: SOURCES defines METPO environmental routes. build_routing includes each
    route root and its is-a descendants. build_yaml copies source identity/definition,
    retains same-source parents independently of routing, emits CLASS/SEEDED and source
    licence, deduplicates synonyms and drops preferred-label duplicates. The transform
    does not independently establish protein meaning. seed_source skips existing paths
    unless force is used; route exclusion alone does not retire existing output.
- evidence_id: obo-helper
  kind: record_content
  reference: scripts/obo_syntax.py
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 86cd5936ecb214f41073fc5ac56425efe647b56bf9a663dad62f6edfad3fbc0e
  support: supports
  locator: unescape, strip_comment, strip_suffixes
  summary: The inspected lexical helpers handle quoted text, comments and suffix syntax;
    they do not alter the biological subject of the definition.
- evidence_id: yaml-helper
  kind: record_content
  reference: scripts/yaml_emit.py
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
  support: supports
  locator: yaml_escape and slugify
  summary: The scalar/slug helpers format names and output text, without supplying
    biological evidence.
- evidence_id: grouping-owner
  kind: record_content
  reference: scripts/seed_grouping_parents.py
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 504e4630cce0d19e86fe47a55b02008a77ebc8cfb6f4cdfddf487f1401a724f7
  support: supports
  locator: TARGETS METPO:1000059 and grouping emission
  summary: The phenotype boundary record is maintained by the grouping writer. Its
    intentionally stopped local ancestry is not treated as a broken relation, and
    this writer is not the reviewed leaf owner.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  locator: METPO block
  summary: The METPO source entry declares seeded status, CC-BY-4.0, seed_obo.py and
    functional routes. These are provenance and maintenance declarations, not individual
    protein-class qualification.
- evidence_id: browser-source
  kind: record_content
  reference: scripts/build_docs_index.py
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 926f593f6d3c81b16ff72148f1777d0b6d81cabe5fe806f4667c5745f28bb818
  support: supports
  locator: infer_source METPO branch
  summary: The METPO identifier/source is recognized by browser source inference;
    display provenance is not biological evidence.
- evidence_id: local-ancestor-1
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 8dac2b83699a98e885de3c6caae21a23457f3a2b63f88190a4a5f21ce9323062
  support: supports
  locator: Entire captured ancestor YAML
  summary: Complete ancestor YAML read with its defining growth/phenotype subject,
    hierarchy, source date, licence, synonyms and status. It is context for this one
    record, not an independent certification of the parent.
- evidence_id: local-ancestor-2
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 1ca0c206d8dcb38047a5f09b4843571524d85af2915375b26f8fa4c69a9e07c5
  support: supports
  locator: Entire captured ancestor YAML
  summary: Complete ancestor YAML read with its defining growth/phenotype subject,
    hierarchy, source date, licence, synonyms and status. It is context for this one
    record, not an independent certification of the parent.
- evidence_id: local-ancestor-3
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml
  accessed_at: '2026-10-21T17:48:40Z'
  snapshot_sha256: 903daba1e34fdc7cace6ae639bd6bab85f0fb9acb6dfd33979ed8e1970992ddc
  support: supports
  locator: Entire captured ancestor YAML
  summary: Complete ancestor YAML read with its defining growth/phenotype subject,
    hierarchy, source date, licence, synonyms and status. It is context for this one
    record, not an independent certification of the parent.
- evidence_id: obligate-oxygen-context
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/micro/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FMICRO_0000516
  accessed_at: '2026-10-21T17:49:29.441210Z'
  snapshot_sha256: acebfccf5a90ddc93bc9fd5d2a76e250e1fc1b139ccfce1092f10da3c2899ccf
  support: context_only
  locator: 'Complete exact OLS term object: identifier, label, description, all annotations,
    status, synonyms and page metadata'
  summary: The nonobsolete MICRO:0000516 term has an annotation.definition for oxygen-present
    growth and inability to grow without oxygen, plus exact-synonym annotations. The
    description array is empty but the definition is present. Additional respiratory
    text is explicitly in a Wikipedia-attributed definition-source annotation; no
    primary experimental verification of that background is claimed.
- evidence_id: metpo-ontology
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo
  accessed_at: '2026-10-21T17:48:13.106573Z'
  snapshot_sha256: 951019bb3917cd48105e4b3e1cc745af697e0d60a50d5292925310d615108b32
  support: supports
  locator: Header; complete METPO:1000606 stanza at line 8280; all captured ancestor
    stanzas
  summary: Exact METPO:1000606 name, definition, immediate parent and synonym scopes
    agree with the target. The exact source requires molecular oxygen for organism
    growth. This differs from simply being able to grow in oxygen. It does not establish
    an oxygen substrate requirement of an individual protein, a universal respiratory
    enzyme mechanism or a numerical oxygen threshold. The ontology header and complete
    source ancestors describe microbial phenotypes. Definition annotations are source
    citations, not automatic equivalent-class mappings.
- evidence_id: metpo-main
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/metpo.obo
  accessed_at: '2026-10-21T17:48:11.979324Z'
  snapshot_sha256: 951019bb3917cd48105e4b3e1cc745af697e0d60a50d5292925310d615108b32
  support: supports
  locator: Whole-body hash equality and exact stanzas
  summary: The freshly captured main OBO body is byte-identical to the commit-pinned
    source. This establishes current agreement, not the original seed input bytes.
- evidence_id: metpo-project
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md
  accessed_at: '2026-10-21T17:48:11.671236Z'
  snapshot_sha256: 3fbbd78aef5c77e8dfa9c09447fed03c26211a52d79382b0ac763482500667f1
  support: supports
  locator: Full README; purpose, namespace and licence
  summary: The complete official README identifies microbial ecophysiological trait/phenotype
    scope, the w3id.org/metpo seven-digit namespace and CC-BY-4.0. Term-body resolution
    was verified; universal landing-page redirects were not tested.
- evidence_id: metpo-license
  kind: authority
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE
  accessed_at: '2026-10-21T17:48:11.671544Z'
  snapshot_sha256: 9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411
  support: supports
  locator: Official licence identification and terms
  summary: The official licence identifies Creative Commons Attribution 4.0 International,
    consistent with the local field and ontology header. Individual upstream citation
    licences are not separately audited.
- evidence_id: metpo-commit
  kind: database
  reference: https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&per_page=1
  accessed_at: '2026-10-21T17:48:11.672173Z'
  snapshot_sha256: cb72f320df01d1039edd9d170b784ad1f2bd699bedaba0b3176a1d4ed22ccee1
  support: supports
  locator: Complete first returned commit object for metpo.obo
  summary: The path-scoped response identifies commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
    dated 2026-09-03, while the captured OBO header remains 2026-06-12. Access time,
    commit time and declared release are separate; none proves the original seed execution.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  locator: Executed 2026-10-21T17:49:14Z through 2026-10-21T17:49:18Z; exit 0
  accessed_at: '2026-10-21T17:49:18Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/environmental_response/metpo/hyperthermophilic-metpo1000617.yaml
    data/traits/function/environmental_response/metpo/mesophilic-metpo1000615.yaml
    data/traits/function/environmental_response/metpo/metal-tolerance-metpo1007074.yaml
    data/traits/function/environmental_response/metpo/microaerophilic-metpo1000604.yaml
    data/traits/function/environmental_response/metpo/microaerotolerant-metpo1000610.yaml
    data/traits/function/environmental_response/metpo/moderately-halophilic-metpo1000623.yaml
    data/traits/function/environmental_response/metpo/neutrophilic-metpo1003001.yaml
    data/traits/function/environmental_response/metpo/non-halophilic-metpo1000624.yaml
    data/traits/function/environmental_response/metpo/obligately-acidophilic-metpo1003006.yaml
    data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  locator: Executed 2026-10-21T17:49:31Z through 2026-10-21T17:51:03Z; exit 0
  accessed_at: '2026-10-21T17:51:03Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml
  locator: Executed 2026-10-21T17:49:18Z through 2026-10-21T17:49:18Z; exit 0
  accessed_at: '2026-10-21T17:49:18Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T17:51:03Z through 2026-10-21T17:51:04Z; exit 0
  accessed_at: '2026-10-21T17:51:04Z'
  support: supports
  summary: No issues found
assessments:
- area: identity
  outcome: supported
  topic: Exact microbial source identity
  summary: METPO:1000606 resolves to obligately aerobic; the current source and local
    preferred name/definition agree. This is a correct source phenotype identity,
    distinct from eligibility as a protein-trait class.
  evidence_ids:
  - record
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-1
- area: nomenclature
  outcome: supported
  topic: Source labels and synonym scope
  summary: Obligate aerobe and obligate aerobic are retained as RELATED synonyms.
    The repeated source obligate aerobic occurrence is deduplicated without changing
    scope. No independent protein identity is asserted by those aliases.
  evidence_ids:
  - record
  - owner
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-2
- area: evidence
  outcome: supported
  topic: Defining organism-growth assertion
  summary: The exact source requires molecular oxygen for organism growth. This differs
    from simply being able to grow in oxygen. It does not establish an oxygen substrate
    requirement of an individual protein, a universal respiratory enzyme mechanism
    or a numerical oxygen threshold. This assessment establishes authentic source
    meaning, not an independent assay of each organism or protein.
  evidence_ids:
  - record
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-3
- area: evidence
  outcome: unknown
  topic: Independent annotation support and limits
  summary: The directly cited MICRO:0000516 annotation says the organism grows in
    oxygen and is incapable of anaerobic growth, supporting the obligate-growth distinction.
    Its additional source annotation quotes general respiratory background attributed
    to Wikipedia; that is not an independently inspected primary experiment and is
    not promoted to a universal protein mechanism.
  evidence_ids:
  - record
  - metpo-ontology
  - obligate-oxygen-context
  target_ids:
  - METPO:1000606
  assessment_id: assessment-4
- area: quantity
  outcome: unknown
  topic: Numerical or qualitative growth boundary
  summary: Keep the organism oxygen-growth requirement separate from protein oxygen
    chemistry, and retain the parent’s typically qualifier. Do not infer a universal
    oxygen concentration, enzyme substrate role or pathway from this class. Current
    ontology wording is verified; no new strain experiment or protein threshold was
    established.
  evidence_ids:
  - record
  - metpo-ontology
  - obligate-oxygen-context
  target_ids:
  - METPO:1000606
  assessment_id: assessment-5
- area: consistency
  outcome: supported
  topic: Local and source ancestry
  summary: The aerobic parent describes growth in oxygen, typically using it as terminal
    electron acceptor. The obligate child adds an oxygen-growth requirement and fits
    that broader phenotype. Typical parent mechanism wording is not proof that every
    protein in the organism directly consumes oxygen. Oxygen-preference and phenotype
    ancestors resolve. Correct copied hierarchy does not by itself resolve the project-domain
    mismatch.
  evidence_ids:
  - record
  - metpo-ontology
  - owner
  - grouping-owner
  - local-ancestor-1
  - local-ancestor-2
  - local-ancestor-3
  target_ids:
  - METPO:1000606
  assessment_id: assessment-6
- area: representation
  outcome: concern
  topic: Organism phenotype versus protein capability
  summary: The defining evidence describes growth of an organism or population, whereas
    the emitted object is a ProteinTraitRecord in FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE.
    A protein mechanism or response cannot be inferred simply from that organism phenotype.
    This does not deny that proteins contribute to growth.
  evidence_ids:
  - record
  - schema
  - project-rules
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-7
- area: grounding
  outcome: supported
  topic: Preserve resolved source identity
  summary: The METPO identifier correctly anchors the source phenotype. No chemical
    or other xref is asserted. A distinct future protein class would need its own
    justified identity and scoped relationship to the organism phenotype; the source
    identifier must not be silently reassigned.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-8
- area: ownership
  outcome: supported
  topic: Maintained source route and disposition
  summary: seed_obo.py owns the target via the inspected METPO route; lexical helpers
    and the separate phenotype-grouping writer are captured. A change must address
    maintained eligibility plus existing output and references. Excluding future emission
    does not remove a previously emitted target.
  evidence_ids:
  - owner
  - obo-helper
  - yaml-helper
  - registry
  - grouping-owner
  - browser-source
  target_ids:
  - METPO:1000606
  assessment_id: assessment-9
- area: provenance
  outcome: unknown
  topic: Current provenance and original-seed limit
  summary: Current main and pinned OBO bodies agree, and their release/header/licence
    agree with the local fields. Fresh access metadata and path-commit response are
    captured. The actual original seed input and execution have not been reconstructed.
  evidence_ids:
  - record
  - metpo-ontology
  - metpo-main
  - metpo-project
  - metpo-license
  - metpo-commit
  target_ids:
  - METPO:1000606
  assessment_id: assessment-10
- area: completeness
  outcome: concern
  topic: Class scope before optional enrichment
  summary: The source phenotype has a complete reusable definition. The material concern
    is its protein-domain eligibility, not missing optional graphs, examples or representations.
    Supplying one protein example would not alone change the defining subject.
  evidence_ids:
  - record
  - schema
  - checklist
  - metpo-ontology
  target_ids:
  - METPO:1000606
  assessment_id: assessment-11
- area: graph
  outcome: not_applicable
  topic: No asserted molecular mechanism
  summary: The entire target contains no causal graph, reaction, participants, residues,
    sequence or structural coordinates. No mechanism validation or molecular claim
    is inferred.
  evidence_ids:
  - record
  - schema
  target_ids:
  - METPO:1000606
  assessment_id: assessment-12
- area: scope
  outcome: supported
  topic: Status, instances and expression context
  summary: The target remains CLASS/SEEDED. No protein example, native status or curation-history
    event is promoted. iModulonDB is inapplicable without a specified gene, organism/dataset
    or expression claim; that is not negative biological evidence.
  evidence_ids:
  - record
  - project-rules
  - checklist
  target_ids:
  - METPO:1000606
  assessment_id: assessment-13
findings:
- issue_key: metpo.environmental-response.METPO-1000606.organism-growth-as-protein-trait
  category: scope
  severity: major
  certainty: confirmed
  title: Organism growth phenotype is emitted as a protein-trait class
  description: The exact source requires molecular oxygen for organism growth. This
    differs from simply being able to grow in oxygen. It does not establish an oxygen
    substrate requirement of an individual protein, a universal respiratory enzyme
    mechanism or a numerical oxygen threshold. The official source and captured ancestors
    supply an organism-level denotation. The maintained route copies that unchanged
    into a protein-trait class without a separately supported protein predicate. This
    is a domain/representation error despite correct source identity; it is not a
    wrong-accession blocker or a universal denial of protein environmental responses.
  field_paths:
  - definition
  - trait_axis
  - trait_category
  - term_kind
  - parent_traits
  evidence_ids:
  - record
  - schema
  - project-rules
  - checklist
  - owner
  - metpo-ontology
  - metpo-project
  - local-ancestor-1
  - local-ancestor-2
  - local-ancestor-3
  rule_id: 'ProteinTraitRecord checklist: identity, axis/category and evidence scope;
    project protein-trait invariant'
  normalization_reason: 'Major: the defining subject is organism growth, not a protein
    trait, materially affecting domain eligibility while the source identifier remains
    correctly resolved.'
  finding_id: F1
  status: open
  target_ids:
  - METPO:1000606
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  native_severity: major
actions:
- action_id: A1
  description: Adjudicate METPO:1000606 in the maintained scripts/seed_obo.py source-eligibility/domain
    policy. Preserve its organism-phenotype meaning in an appropriate representation
    or explicitly exclude it from protein-trait emission, with an audited disposition
    of the existing file and references. If a separate protein response is justified,
    give it an independently supported definition and identity rather than reinterpreting
    this METPO identifier. Keep the organism oxygen-growth requirement separate from
    protein oxygen chemistry, and retain the parent’s typically qualifier. Do not
    infer a universal oxygen concentration, enzyme substrate role or pathway from
    this class. Do not hand-edit generated output or require optional protein examples/graphs
    merely to fill fields.
  finding_ids:
  - F1
  target_ids:
  - METPO:1000606
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  acceptance_checks:
  - Document source-domain eligibility and the existing-record disposition for METPO:1000606;
    preserve the organism phenotype and source identifier unless an explicit audited
    migration is adjudicated.
  - Keep the organism oxygen-growth requirement separate from protein oxygen chemistry,
    and retain the parent’s typically qualifier. Do not infer a universal oxygen concentration,
    enzyme substrate role or pathway from this class. Do not equate an association
    with a protein trait to a subclass or equivalent-class assertion.
  - Exercise the maintained METPO route on a pinned input in dry-run mode. Inspect
    proposed output and separately audit existing-file retirement/migration and affected
    references; merely skipping future emission is insufficient.
  - For a retained/changed target run just validate data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml,
    just validate-all data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml,
    and just audit-graphs data/traits/function/environmental_response/metpo/obligately-aerobic-metpo1000606.yaml.
    If the disposition changes paths, run those checks on documented resulting path(s),
    verify the former path/identifier disposition with an audit trail, and do not
    silently substitute identifiers.
  - For maintained-writer changes run just lint, applicable focused pytest, just test
    and just audit-writers. If the registry changes run just sources-check. Before
    a record-change merge run full just validate-all and just validate-history; preserve
    real logs and create a fresh immutable structured review of the resulting record
    or audited disposition.
limitations:
- The directly cited MICRO:0000516 annotation says the organism grows in oxygen and
  is incapable of anaerobic growth, supporting the obligate-growth distinction. Its
  additional source annotation quotes general respiratory background attributed to
  Wikipedia; that is not an independently inspected primary experiment and is not
  promoted to a universal protein mechanism.
- Current source stanzas, their declared release and licence were inspected; historical
  seed bytes were not reconstructed. Source annotation objects are provenance, not
  assumed equivalence assertions.
- The selected ontology definitions were inspected, not the entire upstream citation
  network, cited textbook contents or all strain-specific experiments. No numerical
  or mechanistic protein conclusion is qualified.
- Only this record and captured ancestors are reviewed. No corpus-wide missing-record/evidence
  assertion or broad negative search is made. Statements about optional omissions
  concern the entire target bytes read.
- This review does not deny molecular contributions to the organism phenotype. Optional
  examples, participants and mechanisms are not compulsory; iModulonDB is inapplicable
  to this generic class without a gene/dataset.
- Raw bodies, actual access times and digests are retained in scratch. Native checks
  and saving are root-owned; this author made no native gate, trait edit, Git mutation,
  public write or status promotion.
tags:
- unreviewed-path-order
- batch-040
- metpo
```
