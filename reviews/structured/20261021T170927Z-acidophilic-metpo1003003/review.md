# Review of acidophilic

- Review: 20261021T170927Z-acidophilic-metpo1003003
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T16:57:05Z
- Finished UTC: 2026-10-21T17:09:27Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The acidophilic record faithfully reproduces the METPO organism-growth phenotype, its exact synonyms and pH-growth parent. One confirmed major concerns importing that phenotype as a protein functional trait through the maintained OBO route. Source thresholds and identity remain valid as ontology assertions; they are not protein pH optima or experimentally qualified protein-response claims.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 9 in batch 037. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96, the union covers 358 record paths, leaving 429001 before this batch. 37 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| METPO:1003003 | data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml | generated | acidophilic |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | METPO:1003003 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | METPO:1003003 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | METPO:1003003 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | METPO:1003003 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | METPO:1003003 | Complete target, both local ancestors, current schema/project rules, maintained OBO emitter and relevant helpers/registry were inspected. METPO:1003003 and METPO:1003000/1000059 resolve in the actual official OBO at pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923. The captured project namespace and licence agree. This source-resolution pass establishes ontology identity and provenance; it does not qualify a protein trait or prove the original seed bytes. |

## Scientific And Domain Assessments

### Maintained METPO source route

ownership: supported. Targets: METPO:1003003.

seed_obo.py owns the reviewed term emission and pH-growth route; grouping-parent generation is separate. Registry and browser source labels are consistent. No generator or record was changed.

### Exact organism-phenotype identity

identity: supported. Targets: METPO:1003003.

The target faithfully identifies METPO:1003003 (acidophilic) in the captured ontology. Its synonyms and definition match this microbial phenotype rather than a similarly named protein property. The confirmed issue concerns eligibility as a protein trait, not a mistaken METPO identifier.

### Source-defined pH semantics

evidence: supported. Targets: METPO:1003003.

The source defines an organism growth optimum below pH 5. This is positive support for the ontology class definition. It does not independently establish a universal biochemical threshold, a particular strain growth curve, protein pH optimum or acid-response mechanism.

### Source hierarchy and synonym fidelity

consistency: supported. Targets: METPO:1003003.

The immediate pH-growth parent and exact synonyms are source-supported. The local ancestor chain is resolvable; the terminal phenotype grouping record deliberately stops at the configured scope boundary. No child-level broken-reference or synonym defect is established.

### Organism growth versus protein response

representation: concern. Targets: METPO:1003003.

The axis/category combination is syntactically allowed, but the defining observation concerns organism population growth. Neither the unchanged ontology definition nor branch membership identifies a protein capability or a supported protein-response class. This is the material domain-scope issue.

### Ontology grounding retained without equivalence inflation

grounding: supported. Targets: METPO:1003003.

The source-native METPO identifier resolves to the represented phenotype; no chemical or protein equivalence xref is present. A future protein class must not reuse this CURIE with a changed denotation or treat an associated organism phenotype as an equivalent protein property.

### Source snapshot and original seed distinction

provenance: unknown. Targets: METPO:1003003.

The exact target fields agree with the inspected commit-pinned ontology, whose header matches the target date label. The upstream file has later modifications while retaining that header, so this agreement does not recover the original seed snapshot. Source licence and generator ownership are positively identified.

### Protein-trait boundary before enrichment

completeness: concern. Targets: METPO:1003003.

The record is complete enough to identify the organism phenotype. Its eligibility in a protein-trait collection must be decided before enrichment. Missing optional examples, representations or causal graphs are not separate defects and cannot repair that semantic boundary by themselves.

### No molecular mechanism asserted

graph: not_applicable. Targets: METPO:1003003.

No causal graph or protein mechanism is asserted in the target. Passing graph validation does not add mechanism evidence.

### Source route eligibility and native status

scope: concern. Targets: METPO:1003003.

The reusable class is an organism growth phenotype. The pH route currently imports it into a protein-trait category without a distinct protein-level definition. SEEDED status is retained and no qualified protein, human review status or history event is promoted.

## Findings

### F1: Organism growth phenotype is imported as a protein trait

major / open / confirmed; issue key: metpo.environmental-response.METPO-1003003.organism-growth-as-protein-trait.

METPO:1003003 defines acidophilic through organism growth under environmental pH. The maintained pH-growth route preserves that organism-level definition and identifier but places it in a ProteinTraitRecord under FUNC_ENVIRONMENTAL_RESPONSE. Source ancestry and keyword overlap do not supply a protein response or requirement class. The source term itself is correctly identified; the defect is the generator/domain boundary.

## Recommended Actions And Acceptance Checks

### A1

Gate the METPO pH-growth route in scripts/seed_obo.py against the protein-trait invariant and explicitly adjudicate the existing METPO:1003003 record and its hierarchy. Preserve the organism phenotype meaning and source thresholds. Excluding a term from future emission must be paired with an audited disposition or migration of the existing record and affected references; it does not remove the current record automatically. If a protein response capability is separately supported, give that class its own identity and explicit evidence, keeping its relationship to the METPO organism phenotype distinct from equivalence. Do not simply rename this METPO class as a protein pH optimum or gene-induction phenotype.

- A curator records an explicit eligibility/disposition decision for METPO:1003003; the METPO organism definition and identifier are not silently repurposed.
- Exercise the maintained OBO route against a pinned source snapshot in dry-run mode and inspect the reviewed target outcome; an exclusion alone must not be claimed to have migrated an existing file.
- Account for affected parent/child references and preserve resolvable identity during any separately authorized migration or deprecation. Review broader route members separately before generalizing this two-record result.
- Any proposed protein class has a distinct identifier, a protein-level definition, scoped supporting evidence and an explicitly justified relationship to the source phenotype. Optional protein examples require the existing reviewed grounding workflow.
- For a future generator change, run just lint, focused pytest, just test and just audit-writers. For separately authorized resulting records, run just validate &lt;resulting-path&gt;, just validate-all &lt;resulting-path&gt; and just audit-graphs &lt;resulting-path&gt;. Run full just validate-all before any eventual merge and just validate-history for the full history tree. An excluded original additionally requires the explicit retirement/reference audit above.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml; Entire target YAML | supports | Complete target YAML: METPO:1003003, acidophilic, organism-level pH growth definition, METPO (2026-06-12) attribution, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, CLASS/SEEDED, pH-growth parent, exact synonyms and CC-BY-4.0. No protein example, molecular representation, xref, chemical participant or causal graph is asserted. |
| project-contract | CLAUDE.md; Purpose and invariant; Safety rules; Common commands/status rule | supports | The project invariant defines a knowledge base of protein trait classes. Axis placement follows defining representation; generated records retain source provenance and cannot be promoted by automated validation alone. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord identifier, definition, parent_traits, trait_axis/category and optional representations; TraitAxisEnum FUNCTION; FUNC_ENVIRONMENTAL_RESPONSE | supports | ProteinTraitRecord identifies a trait class; existing source identifiers are preferred for one-to-one identity. FUNC_ENVIRONMENTAL_RESPONSE describes environmental response or requirement, grounded by GO response processes or UniProt induction. parent_traits means broader classes. The broader project invariant concerns protein traits, not organism population growth phenotypes. |
| owner | scripts/seed_obo.py; SOURCES metpo pH route; build_routing; build_yaml; read_release_stamp; seed_source | supports | The METPO:1003000 route imports pH-growth-preference descendants as FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. build_routing follows same-source is_a ancestry; build_yaml preserves source identifiers, definitions, synonyms and parents without deriving a protein capability. read_release_stamp selects a header date. A route exclusion prevents subsequent emission but does not itself dispose of existing files. |
| obo-syntax | scripts/obo_syntax.py; strip_comment, strip_suffixes, unescape | supports | The imported helpers unescape OBO strings and handle quoted descriptions, comments and qualifier suffixes. These lexical operations do not turn organism-level semantics into protein-level evidence. |
| yaml-emitter | scripts/yaml_emit.py; yaml_escape, slugify | supports | The shared scalar and slug helpers preserve strings and construct filenames. No biological-scope transformation is performed by these formatting helpers. |
| grouping-owner | scripts/seed_grouping_parents.py; TARGETS entry METPO:1000059; parse_obo; child_stamp; main | supports | The local METPO phenotype grouping parent is emitted as a scope boundary by this maintained helper, with inherited category and source stamp and no further parents. It is supporting hierarchy context, not the owner of either reviewed child term. |
| registry | download.yaml; METPO source block | supports | The METPO source entry names the official main OBO, declares CC-BY 4.0, seeded hierarchy and FUNC_ENVIRONMENTAL_RESPONSE/FUNC_ENZYMATIC_ACTIVITY, and identifies seed_obo.py. Declared routing does not establish that each imported phenotype is a protein trait. |
| browser-source | scripts/build_docs_index.py; infer_source METPO prefix branch | supports | infer_source recognizes the METPO identifier prefix as METPO. The source label agrees with the target; browser routing is not biological qualification. |
| local-ancestor-1 | data/traits/function/environmental_response/metpo/ph-growth-preference-metpo1003000.yaml; Entire ancestor YAML | supports | Complete local ancestor YAML inspected. The pH-growth class concerns rate and extent of population growth; its phenotype parent concerns differences among instances of a species. Both remain source-derived CLASS/SEEDED records. Their existence resolves local links without proving protein-level scope. |
| local-ancestor-2 | data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml; Entire ancestor YAML | supports | Complete local ancestor YAML inspected. The pH-growth class concerns rate and extent of population growth; its phenotype parent concerns differences among instances of a species. Both remain source-derived CLASS/SEEDED records. Their existence resolves local links without proving protein-level scope. |
| metpo-ontology | https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo; Header; complete [Term] stanzas METPO:1003003, METPO:1003000 and METPO:1000059; pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 | supports | The complete METPO:1003003 stanza supports the exact label, definition and synonyms (acidophil and acidophile), with is_a METPO:1003000. The source defines an organism growth optimum below pH 5. The complete parent stanzas METPO:1003000 and METPO:1000059 concern population growth and phenotype. The header declares version 2026-06-12, the w3id.org/metpo namespace and CC-BY 4.0. This commit-pinned body is byte-identical to the separately captured current main OBO. |
| metpo-project | https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md; Title/purpose; Versions; Identifiers and resolution; License | supports | The official project describes microbial ecophysiological traits and phenotypes, identifies the canonical https://w3id.org/metpo/ term namespace, and declares CC-BY 4.0. The ontology identifier is resolved here through the actual OBO stanza; no claim is made that every term landing-page redirect was tested. |
| metpo-license | https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE; License title and public-license identification | supports | The official LICENSE is Creative Commons Attribution 4.0 International, consistent with the target and ontology header. This is source-license identification, not a separate legal audit of every upstream definition source. |
| metpo-commit | https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&amp;per_page=1; Single returned commit SHA, date and path-scoped query; raw body equality recorded separately | context_only | The captured public commit query identifies 8fddadb3fbd79058e22fbd519e36ab43b3496923 as the latest returned modification of metpo.obo, dated 2026-09-03. Its raw OBO equals captured main despite the retained 2026-06-12 ontology header. A date label alone therefore does not identify the exact original seed bytes. |
| validation-1 | just validate data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml; Executed 2026-10-21T16:57:59Z through 2026-10-21T16:58:00Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml; Executed 2026-10-21T16:57:45Z through 2026-10-21T16:59:36Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml; Executed 2026-10-21T16:58:00Z through 2026-10-21T16:58:00Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T16:59:36Z through 2026-10-21T16:59:38Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed biological assertions are source-native ontology definitions and relations. This review does not independently validate a universal pH cutoff, a strain growth experiment or a protein mechanism.
- The current main and commit-pinned OBO bodies are identical and declare 2026-06-12, but the upstream file has later modifications. The target date label does not prove which exact bytes were used for the original seed.
- No protein example, molecular representation or causal graph is asserted or newly qualified. An organism phenotype may motivate protein research without being equivalent to a protein property.
- This review covers one complete target and reads its ancestors as context; it does not certify or reject the whole METPO source cohort. iModulonDB is not applicable without a specified gene, organism/dataset or expression component.
- External bodies are retained in session scratch; the saved observation retains URLs, actual access times, SHA256 digests and bounded reading scopes. Upstream definition-source annotations were read as source metadata, not independently verified as an exhaustive literature chain.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T170927Z-acidophilic-metpo1003003
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of acidophilic
started_at: '2026-10-21T16:57:05Z'
finished_at: '2026-10-21T17:09:27Z'
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
summary: The acidophilic record faithfully reproduces the METPO organism-growth phenotype,
  its exact synonyms and pH-growth parent. One confirmed major concerns importing
  that phenotype as a protein functional trait through the maintained OBO route. Source
  thresholds and identity remain valid as ontology assertions; they are not protein
  pH optima or experimentally qualified protein-response claims.
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
  - path: data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
    sha256: 5b81ce5bf88d8a302210b702f61bf188414e48310318494fd4e62e179c3cc81a
    role: target
  - path: data/traits/function/environmental_response/metpo/ph-growth-preference-metpo1003000.yaml
    sha256: 6502c3381d5ec6f995d48fc8e65d88e9306a9169ab650da18cb1a7b7f2066d9f
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
  selection: Path-order position 9 in batch 037. Fresh main inventory has 429359 records.
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
    c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4;
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96, the union covers 358 record paths, leaving
    429001 before this batch. 37 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - METPO:1003003
targets:
- kind: generated
  label: acidophilic
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  path: data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  record_class: ProteinTraitRecord
  target_id: METPO:1003003
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - METPO:1003003
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml
    data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml
    data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml
    data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
    data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - METPO:1003003
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - METPO:1003003
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
  - METPO:1003003
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Complete target, both local ancestors, current schema/project rules, maintained
    OBO emitter and relevant helpers/registry were inspected. METPO:1003003 and METPO:1003000/1000059
    resolve in the actual official OBO at pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923.
    The captured project namespace and licence agree. This source-resolution pass
    establishes ontology identity and provenance; it does not qualify a protein trait
    or prove the original seed bytes.
  target_ids:
  - METPO:1003003
  evidence_ids:
  - record
  - schema
  - project-contract
  - owner
  - registry
  - grouping-owner
  - obo-syntax
  - yaml-emitter
  - browser-source
  - local-ancestor-1
  - local-ancestor-2
  - metpo-ontology
  - metpo-project
  - metpo-license
  - metpo-commit
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 5b81ce5bf88d8a302210b702f61bf188414e48310318494fd4e62e179c3cc81a
  support: supports
  summary: 'Complete target YAML: METPO:1003003, acidophilic, organism-level pH growth
    definition, METPO (2026-06-12) attribution, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE,
    CLASS/SEEDED, pH-growth parent, exact synonyms and CC-BY-4.0. No protein example,
    molecular representation, xref, chemical participant or causal graph is asserted.'
- evidence_id: project-contract
  kind: record_content
  reference: CLAUDE.md
  locator: Purpose and invariant; Safety rules; Common commands/status rule
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
  support: supports
  summary: The project invariant defines a knowledge base of protein trait classes.
    Axis placement follows defining representation; generated records retain source
    provenance and cannot be promoted by automated validation alone.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord identifier, definition, parent_traits, trait_axis/category
    and optional representations; TraitAxisEnum FUNCTION; FUNC_ENVIRONMENTAL_RESPONSE
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: ProteinTraitRecord identifies a trait class; existing source identifiers
    are preferred for one-to-one identity. FUNC_ENVIRONMENTAL_RESPONSE describes environmental
    response or requirement, grounded by GO response processes or UniProt induction.
    parent_traits means broader classes. The broader project invariant concerns protein
    traits, not organism population growth phenotypes.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_obo.py
  locator: SOURCES metpo pH route; build_routing; build_yaml; read_release_stamp;
    seed_source
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 8b33fbdac45c28420b3e6ca31d0d9feb16c90701eb77c392b571f1b3261c7a9f
  support: supports
  summary: The METPO:1003000 route imports pH-growth-preference descendants as FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE.
    build_routing follows same-source is_a ancestry; build_yaml preserves source identifiers,
    definitions, synonyms and parents without deriving a protein capability. read_release_stamp
    selects a header date. A route exclusion prevents subsequent emission but does
    not itself dispose of existing files.
- evidence_id: obo-syntax
  kind: record_content
  reference: scripts/obo_syntax.py
  locator: strip_comment, strip_suffixes, unescape
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 86cd5936ecb214f41073fc5ac56425efe647b56bf9a663dad62f6edfad3fbc0e
  support: supports
  summary: The imported helpers unescape OBO strings and handle quoted descriptions,
    comments and qualifier suffixes. These lexical operations do not turn organism-level
    semantics into protein-level evidence.
- evidence_id: yaml-emitter
  kind: record_content
  reference: scripts/yaml_emit.py
  locator: yaml_escape, slugify
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
  support: supports
  summary: The shared scalar and slug helpers preserve strings and construct filenames.
    No biological-scope transformation is performed by these formatting helpers.
- evidence_id: grouping-owner
  kind: record_content
  reference: scripts/seed_grouping_parents.py
  locator: TARGETS entry METPO:1000059; parse_obo; child_stamp; main
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 504e4630cce0d19e86fe47a55b02008a77ebc8cfb6f4cdfddf487f1401a724f7
  support: supports
  summary: The local METPO phenotype grouping parent is emitted as a scope boundary
    by this maintained helper, with inherited category and source stamp and no further
    parents. It is supporting hierarchy context, not the owner of either reviewed
    child term.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: METPO source block
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: The METPO source entry names the official main OBO, declares CC-BY 4.0,
    seeded hierarchy and FUNC_ENVIRONMENTAL_RESPONSE/FUNC_ENZYMATIC_ACTIVITY, and
    identifies seed_obo.py. Declared routing does not establish that each imported
    phenotype is a protein trait.
- evidence_id: browser-source
  kind: record_content
  reference: scripts/build_docs_index.py
  locator: infer_source METPO prefix branch
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 926f593f6d3c81b16ff72148f1777d0b6d81cabe5fe806f4667c5745f28bb818
  support: supports
  summary: infer_source recognizes the METPO identifier prefix as METPO. The source
    label agrees with the target; browser routing is not biological qualification.
- evidence_id: local-ancestor-1
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/ph-growth-preference-metpo1003000.yaml
  locator: Entire ancestor YAML
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 6502c3381d5ec6f995d48fc8e65d88e9306a9169ab650da18cb1a7b7f2066d9f
  support: supports
  summary: Complete local ancestor YAML inspected. The pH-growth class concerns rate
    and extent of population growth; its phenotype parent concerns differences among
    instances of a species. Both remain source-derived CLASS/SEEDED records. Their
    existence resolves local links without proving protein-level scope.
- evidence_id: local-ancestor-2
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml
  locator: Entire ancestor YAML
  accessed_at: '2026-10-21T16:57:05Z'
  snapshot_sha256: 903daba1e34fdc7cace6ae639bd6bab85f0fb9acb6dfd33979ed8e1970992ddc
  support: supports
  summary: Complete local ancestor YAML inspected. The pH-growth class concerns rate
    and extent of population growth; its phenotype parent concerns differences among
    instances of a species. Both remain source-derived CLASS/SEEDED records. Their
    existence resolves local links without proving protein-level scope.
- evidence_id: metpo-ontology
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo
  accessed_at: '2026-10-21T16:58:21.154794Z'
  snapshot_sha256: 951019bb3917cd48105e4b3e1cc745af697e0d60a50d5292925310d615108b32
  support: supports
  locator: Header; complete [Term] stanzas METPO:1003003, METPO:1003000 and METPO:1000059;
    pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
  summary: The complete METPO:1003003 stanza supports the exact label, definition
    and synonyms (acidophil and acidophile), with is_a METPO:1003000. The source defines
    an organism growth optimum below pH 5. The complete parent stanzas METPO:1003000
    and METPO:1000059 concern population growth and phenotype. The header declares
    version 2026-06-12, the w3id.org/metpo namespace and CC-BY 4.0. This commit-pinned
    body is byte-identical to the separately captured current main OBO.
- evidence_id: metpo-project
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md
  accessed_at: '2026-10-21T16:58:20.792010Z'
  snapshot_sha256: 3fbbd78aef5c77e8dfa9c09447fed03c26211a52d79382b0ac763482500667f1
  support: supports
  locator: Title/purpose; Versions; Identifiers and resolution; License
  summary: The official project describes microbial ecophysiological traits and phenotypes,
    identifies the canonical https://w3id.org/metpo/ term namespace, and declares
    CC-BY 4.0. The ontology identifier is resolved here through the actual OBO stanza;
    no claim is made that every term landing-page redirect was tested.
- evidence_id: metpo-license
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE
  accessed_at: '2026-10-21T16:58:20.767515Z'
  snapshot_sha256: 9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411
  support: supports
  locator: License title and public-license identification
  summary: The official LICENSE is Creative Commons Attribution 4.0 International,
    consistent with the target and ontology header. This is source-license identification,
    not a separate legal audit of every upstream definition source.
- evidence_id: metpo-commit
  kind: database
  reference: https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&per_page=1
  accessed_at: '2026-10-21T16:58:20.907500Z'
  snapshot_sha256: cb72f320df01d1039edd9d170b784ad1f2bd699bedaba0b3176a1d4ed22ccee1
  support: context_only
  locator: Single returned commit SHA, date and path-scoped query; raw body equality
    recorded separately
  summary: The captured public commit query identifies 8fddadb3fbd79058e22fbd519e36ab43b3496923
    as the latest returned modification of metpo.obo, dated 2026-09-03. Its raw OBO
    equals captured main despite the retained 2026-06-12 ontology header. A date label
    alone therefore does not identify the exact original seed bytes.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  locator: Executed 2026-10-21T16:57:59Z through 2026-10-21T16:58:00Z; exit 0
  accessed_at: '2026-10-21T16:58:00Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/vitamin-b6-phosphate-chebi36970.yaml
    data/traits/function/cofactor_requirement/chebi/vitamin-k2-chebi16374.yaml data/traits/function/cofactor_requirement/chebi/w-chebi30154.yaml
    data/traits/function/cofactor_requirement/chebi/yb-chebi33381.yaml data/traits/function/cofactor_requirement/chebi/yersiniabactin-chebi29707.yaml
    data/traits/function/cofactor_requirement/chebi/zeaxanthin-chebi27547.yaml data/traits/function/cofactor_requirement/chebi/zinc-2-chebi29105.yaml
    data/traits/function/cofactor_requirement/chebi/zn-chebi27363.yaml data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
    data/traits/function/environmental_response/metpo/acidotolerant-metpo1003008.yaml
  locator: Executed 2026-10-21T16:57:45Z through 2026-10-21T16:59:36Z; exit 0
  accessed_at: '2026-10-21T16:59:36Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/environmental_response/metpo/acidophilic-metpo1003003.yaml
  locator: Executed 2026-10-21T16:58:00Z through 2026-10-21T16:58:00Z; exit 0
  accessed_at: '2026-10-21T16:58:00Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T16:59:36Z through 2026-10-21T16:59:38Z; exit 0
  accessed_at: '2026-10-21T16:59:38Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  topic: Maintained METPO source route
  summary: seed_obo.py owns the reviewed term emission and pH-growth route; grouping-parent
    generation is separate. Registry and browser source labels are consistent. No
    generator or record was changed.
  evidence_ids:
  - owner
  - grouping-owner
  - registry
  - browser-source
  target_ids:
  - METPO:1003003
  assessment_id: assessment-1
- area: identity
  outcome: supported
  topic: Exact organism-phenotype identity
  summary: The target faithfully identifies METPO:1003003 (acidophilic) in the captured
    ontology. Its synonyms and definition match this microbial phenotype rather than
    a similarly named protein property. The confirmed issue concerns eligibility as
    a protein trait, not a mistaken METPO identifier.
  evidence_ids:
  - record
  - metpo-ontology
  - metpo-project
  target_ids:
  - METPO:1003003
  assessment_id: assessment-2
- area: evidence
  outcome: supported
  topic: Source-defined pH semantics
  summary: The source defines an organism growth optimum below pH 5. This is positive
    support for the ontology class definition. It does not independently establish
    a universal biochemical threshold, a particular strain growth curve, protein pH
    optimum or acid-response mechanism.
  evidence_ids:
  - record
  - metpo-ontology
  target_ids:
  - METPO:1003003
  assessment_id: assessment-3
- area: consistency
  outcome: supported
  topic: Source hierarchy and synonym fidelity
  summary: The immediate pH-growth parent and exact synonyms are source-supported.
    The local ancestor chain is resolvable; the terminal phenotype grouping record
    deliberately stops at the configured scope boundary. No child-level broken-reference
    or synonym defect is established.
  evidence_ids:
  - record
  - metpo-ontology
  - grouping-owner
  - local-ancestor-1
  - local-ancestor-2
  target_ids:
  - METPO:1003003
  assessment_id: assessment-4
- area: representation
  outcome: concern
  topic: Organism growth versus protein response
  summary: The axis/category combination is syntactically allowed, but the defining
    observation concerns organism population growth. Neither the unchanged ontology
    definition nor branch membership identifies a protein capability or a supported
    protein-response class. This is the material domain-scope issue.
  evidence_ids:
  - record
  - schema
  - project-contract
  - owner
  - metpo-ontology
  target_ids:
  - METPO:1003003
  assessment_id: assessment-5
- area: grounding
  outcome: supported
  topic: Ontology grounding retained without equivalence inflation
  summary: The source-native METPO identifier resolves to the represented phenotype;
    no chemical or protein equivalence xref is present. A future protein class must
    not reuse this CURIE with a changed denotation or treat an associated organism
    phenotype as an equivalent protein property.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  target_ids:
  - METPO:1003003
  assessment_id: assessment-6
- area: provenance
  outcome: unknown
  topic: Source snapshot and original seed distinction
  summary: The exact target fields agree with the inspected commit-pinned ontology,
    whose header matches the target date label. The upstream file has later modifications
    while retaining that header, so this agreement does not recover the original seed
    snapshot. Source licence and generator ownership are positively identified.
  evidence_ids:
  - record
  - owner
  - registry
  - metpo-ontology
  - metpo-commit
  - metpo-project
  - metpo-license
  target_ids:
  - METPO:1003003
  assessment_id: assessment-7
- area: completeness
  outcome: concern
  topic: Protein-trait boundary before enrichment
  summary: The record is complete enough to identify the organism phenotype. Its eligibility
    in a protein-trait collection must be decided before enrichment. Missing optional
    examples, representations or causal graphs are not separate defects and cannot
    repair that semantic boundary by themselves.
  evidence_ids:
  - record
  - schema
  - project-contract
  - metpo-ontology
  target_ids:
  - METPO:1003003
  assessment_id: assessment-8
- area: graph
  outcome: not_applicable
  topic: No molecular mechanism asserted
  summary: No causal graph or protein mechanism is asserted in the target. Passing
    graph validation does not add mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - METPO:1003003
  assessment_id: assessment-9
- area: scope
  outcome: concern
  topic: Source route eligibility and native status
  summary: The reusable class is an organism growth phenotype. The pH route currently
    imports it into a protein-trait category without a distinct protein-level definition.
    SEEDED status is retained and no qualified protein, human review status or history
    event is promoted.
  evidence_ids:
  - record
  - owner
  - project-contract
  - metpo-ontology
  target_ids:
  - METPO:1003003
  assessment_id: assessment-10
findings:
- issue_key: metpo.environmental-response.METPO-1003003.organism-growth-as-protein-trait
  category: scope
  severity: major
  certainty: confirmed
  title: Organism growth phenotype is imported as a protein trait
  description: METPO:1003003 defines acidophilic through organism growth under environmental
    pH. The maintained pH-growth route preserves that organism-level definition and
    identifier but places it in a ProteinTraitRecord under FUNC_ENVIRONMENTAL_RESPONSE.
    Source ancestry and keyword overlap do not supply a protein response or requirement
    class. The source term itself is correctly identified; the defect is the generator/domain
    boundary.
  field_paths:
  - definition
  - trait_category
  - parent_traits
  evidence_ids:
  - record
  - project-contract
  - schema
  - owner
  - metpo-ontology
  rule_id: 'ProteinTraitRecord checklist: identity boundary, representation-based
    category and exact evidence scope'
  normalization_reason: 'Major: the source identifier and phenotype identity remain
    intact, but organism-level defining evidence is systematically imported as a protein
    trait without a supported protein-level interpretation. This is not a wrong-identifier
    collision.'
  finding_id: F1
  status: open
  target_ids:
  - METPO:1003003
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  native_severity: major
actions:
- action_id: A1
  description: Gate the METPO pH-growth route in scripts/seed_obo.py against the protein-trait
    invariant and explicitly adjudicate the existing METPO:1003003 record and its
    hierarchy. Preserve the organism phenotype meaning and source thresholds. Excluding
    a term from future emission must be paired with an audited disposition or migration
    of the existing record and affected references; it does not remove the current
    record automatically. If a protein response capability is separately supported,
    give that class its own identity and explicit evidence, keeping its relationship
    to the METPO organism phenotype distinct from equivalence. Do not simply rename
    this METPO class as a protein pH optimum or gene-induction phenotype.
  finding_ids:
  - F1
  target_ids:
  - METPO:1003003
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  acceptance_checks:
  - A curator records an explicit eligibility/disposition decision for METPO:1003003;
    the METPO organism definition and identifier are not silently repurposed.
  - Exercise the maintained OBO route against a pinned source snapshot in dry-run
    mode and inspect the reviewed target outcome; an exclusion alone must not be claimed
    to have migrated an existing file.
  - Account for affected parent/child references and preserve resolvable identity
    during any separately authorized migration or deprecation. Review broader route
    members separately before generalizing this two-record result.
  - Any proposed protein class has a distinct identifier, a protein-level definition,
    scoped supporting evidence and an explicitly justified relationship to the source
    phenotype. Optional protein examples require the existing reviewed grounding workflow.
  - For a future generator change, run just lint, focused pytest, just test and just
    audit-writers. For separately authorized resulting records, run just validate
    <resulting-path>, just validate-all <resulting-path> and just audit-graphs <resulting-path>.
    Run full just validate-all before any eventual merge and just validate-history
    for the full history tree. An excluded original additionally requires the explicit
    retirement/reference audit above.
limitations:
- The reviewed biological assertions are source-native ontology definitions and relations.
  This review does not independently validate a universal pH cutoff, a strain growth
  experiment or a protein mechanism.
- The current main and commit-pinned OBO bodies are identical and declare 2026-06-12,
  but the upstream file has later modifications. The target date label does not prove
  which exact bytes were used for the original seed.
- No protein example, molecular representation or causal graph is asserted or newly
  qualified. An organism phenotype may motivate protein research without being equivalent
  to a protein property.
- This review covers one complete target and reads its ancestors as context; it does
  not certify or reject the whole METPO source cohort. iModulonDB is not applicable
  without a specified gene, organism/dataset or expression component.
- External bodies are retained in session scratch; the saved observation retains URLs,
  actual access times, SHA256 digests and bounded reading scopes. Upstream definition-source
  annotations were read as source metadata, not independently verified as an exhaustive
  literature chain.
tags:
- unreviewed-path-order
- batch-037
- metpo
```
