# Review of anaerobic

- Review: 20261021T172425Z-anaerobic-metpo1000603
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T17:19:07Z
- Finished UTC: 2026-10-21T17:24:25Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The anaerobic record faithfully represents the current METPO microbial growth phenotype and source hierarchy. One confirmed major concerns importing that organism-level class as a protein functional trait. The source identifies growth without molecular oxygen. This definition alone does not assert oxygen toxicity, strict anaerobiosis, a particular alternative electron acceptor or a particular fermentation pathway. Original seed bytes remain unresolved; no protein mechanism or example is qualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 5 in batch 038. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb, the union covers 368 record paths, leaving 428991 before this batch. 38 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| METPO:1000603 | data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml | generated | anaerobic |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | METPO:1000603 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | METPO:1000603 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | METPO:1000603 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | METPO:1000603 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | METPO:1000603 | The complete target and recursive local ancestors were inspected against the captured schema, project rules, OBO emitter, syntax/emission helpers, registry and grouping route. METPO:1000603, METPO:1000601 and METPO:1000059 resolve in the actual official OBO at commit 8fddadb3fbd79058e22fbd519e36ab43b3496923, with source name, definition, synonym scopes and ancestry matching the target. Namespace and licence are verified. This resolution establishes source identity and current fidelity, not protein-trait eligibility or original seed bytes. |

## Scientific And Domain Assessments

### Maintained source route and inherited grouping

ownership: supported. Targets: METPO:1000603.

The oxygen-preference branch and reviewed record emission are maintained in seed_obo.py; the grouping ancestor has a separate generator. Registry and browser provenance agree. Any correction belongs to that maintained route and an audited existing-record disposition, not an untracked hand edit.

### Exact microbial phenotype identity

identity: supported. Targets: METPO:1000603.

The full target correctly resolves to METPO:1000603 (anaerobic). Its source definition, retained synonym scopes and immediate parent match the current official ontology. The finding concerns protein-trait eligibility, not a wrong accession or an obsolete term.

### Source-defined growth and tolerance semantics

evidence: supported. Targets: METPO:1000603.

The source identifies growth without molecular oxygen. This definition alone does not assert oxygen toxicity, strict anaerobiosis, a particular alternative electron acceptor or a particular fermentation pathway. This positively supports the represented ontology meaning; no particular strain experiment, protein activity or universal environmental boundary is independently certified.

### Source hierarchy and lexical fidelity

consistency: supported. Targets: METPO:1000603.

The immediate oxygen-preference parent concerns organism oxygen requirements or tolerance for growth. The two retained aliases, anaerobe and Ox_anaerobic, have RELATED scope. The source alias identical to the label is omitted by the emitter. The local phenotype ancestor stops at the documented grouping boundary. No separate broken-parent or alias defect is established for this target.

### Organism phenotype versus protein capability

representation: concern. Targets: METPO:1000603.

Growth in the absence of oxygen describes an organism phenotype. It does not specify a protein that functions only anaerobically, an oxygen-labile enzyme, or a defined anaerobic-response mechanism. The FUNCTION/category combination is permitted syntactically, but the defining evidence remains organism-level and has not been converted into a supported protein trait.

### Source identity retained without repurposing

grounding: supported. Targets: METPO:1000603.

METPO:1000603 genuinely identifies the source phenotype. The record contains no equivalence xref to adjudicate separately. A future protein-response class must not silently reuse this identifier with a different meaning or treat mere association with the organism phenotype as equivalence.

### Current source agreement versus original seed snapshot

provenance: unknown. Targets: METPO:1000603.

The present record fields agree with the current commit-pinned ontology and its 2026-06-12 header. The captured file modification is later than that date; the original seed bytes and original input sidecar have not been established in this review. Current source identity, maintained owner and licence are positively supported.

### Class eligibility before optional enrichment

completeness: concern. Targets: METPO:1000603.

The target identifies a reusable microbial phenotype sufficiently for review. Its protein-trait eligibility must be resolved before enrichment. Missing optional examples, sequences, structures or causal graphs are not separate completeness findings, and adding them cannot by itself change the source class denotation.

### No mechanism graph asserted

graph: not_applicable. Targets: METPO:1000603.

The full YAML contains no causal graph. Deterministic graph validation does not establish a protein mechanism.

### Domain boundary and status

scope: concern. Targets: METPO:1000603.

Preserve growth without oxygen without adding strict oxygen intolerance or a particular respiratory or fermentative mechanism. A protein oxygen-sensitivity class would require its own identity and evidence. The target remains SEEDED; this observation neither promotes scientific status nor qualifies any protein example.

## Findings

### F1: Organism growth phenotype is imported as a protein trait

major / open / confirmed; issue key: metpo.environmental-response.METPO-1000603.organism-growth-as-protein-trait.

METPO:1000603 (anaerobic) is defined by organism growth or tolerance. Growth in the absence of oxygen describes an organism phenotype. It does not specify a protein that functions only anaerobically, an oxygen-labile enzyme, or a defined anaerobic-response mechanism. The maintained METPO:1000601 route copies that phenotype into a ProteinTraitRecord under FUNC_ENVIRONMENTAL_RESPONSE without a distinct protein-level defining assertion. The METPO identifier and source meaning are correct; the error is the source-to-domain eligibility decision.

## Recommended Actions And Acceptance Checks

### A1

Adjudicate METPO:1000603 eligibility in the maintained oxygen-preference route in scripts/seed_obo.py and document the disposition of this existing record and its references. Preserve growth without oxygen without adding strict oxygen intolerance or a particular respiratory or fermentative mechanism. A protein oxygen-sensitivity class would require its own identity and evidence. If excluded from protein-trait emission, use an audited migration or deprecation/reference plan; a route exclusion alone does not remove an existing record. If a separate protein capability is supported, give it its own identity and protein-level definition with explicit scoped evidence and an appropriate relationship to the organism phenotype. Do not relabel this METPO phenotype as that new protein property.

- Record a curator-adjudicated eligibility and existing-record disposition for METPO:1000603, preserving the source organism-phenotype identity and documented meaning.
- Exercise the maintained OBO route against a pinned source snapshot in dry-run mode and inspect the reviewed term outcome. Verify that route exclusion is not mistaken for retirement of a pre-existing file.
- Audit affected parent/child references and any old identifier disposition for resulting paths after a separately authorized migration or deprecation. Do not generalize this one-record judgment to unreviewed branch members.
- Any distinct protein class requires its own identity, protein-level definition and scoped support. Keep its relationship to the organism phenotype separate from equivalence; optional examples use the existing reviewed qualification workflow.
- For a future generator change, run just lint, focused pytest, just test and just audit-writers. For resulting records, run just validate &lt;resulting-path&gt;, just validate-all &lt;resulting-path&gt; and just audit-graphs &lt;resulting-path&gt;; run full just validate-all before merge and just validate-history for the full history tree. Add a fresh immutable review of the actual corrected outcome.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml; Entire target YAML | supports | Complete YAML read: METPO:1000603 (anaerobic), its growth-phenotype definition, METPO (2026-06-12) source label, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, CLASS/SEEDED, parent METPO:1000601 and CC-BY-4.0. The two retained aliases, anaerobe and Ox_anaerobic, have RELATED scope. The source alias identical to the label is omitted by the emitter. No protein exemplar, molecular representation, chemical participant, xref or causal graph is asserted. |
| project-contract | CLAUDE.md; Purpose and invariant; Safety rules; status and change-to-gate rules | supports | The project invariant is a knowledge base of protein trait classes. Axes follow the defining representation; generated records require an audited maintenance route and scientific status is not promoted by automated validation. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord identifier, definition, parent_traits and optional representations; FUNCTION and FUNC_ENVIRONMENTAL_RESPONSE | supports | ProteinTraitRecord uses source identifiers for one-to-one class identity; parent_traits expresses broader classes. FUNC_ENVIRONMENTAL_RESPONSE covers environmental response or requirement with response-process or induction grounding. This category remains subject to the project protein-trait invariant. Examples, molecular representations and causal graphs are optional, not a means of changing an organism phenotype into a protein class. |
| owner | scripts/seed_obo.py; SOURCES metpo route; build_routing; build_yaml; read_release_stamp; seed_source | supports | The configured METPO:1000601 oxygen-preference route selects descendants by is_a and assigns FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. build_yaml retains source identifier, definition, parents and non-label synonyms; it does not derive a protein capability from an organism phenotype. read_release_stamp selects a header date. Existing records are skipped unless force is used; dry-run is default and applying a changed route does not automatically retire excluded existing records. |
| obo-syntax | scripts/obo_syntax.py; unescape, strip_comment and strip_suffixes | supports | The shared parser helpers handle escaping, comments and suffix syntax. These are lexical transformations, not independent biological support. |
| yaml-emitter | scripts/yaml_emit.py; yaml_escape and slugify | supports | The scalar and slug helpers preserve text and construct paths. They do not change biological denotation. |
| registry | download.yaml; METPO source block | supports | The METPO registry block declares the official main OBO, CC-BY 4.0, hierarchy, the two functional categories and seed_obo.py. This establishes maintained provenance, not protein-level eligibility of each selected class. |
| grouping-owner | scripts/seed_grouping_parents.py; TARGETS METPO:1000059; parse_obo; child_stamp; main | supports | This helper emits the METPO:1000059 phenotype grouping ancestor at the configured scope boundary, inheriting the source stamp and category and stopping its parent chain. It does not own the reviewed child term. |
| browser-source | scripts/build_docs_index.py; infer_source METPO branch | supports | infer_source recognizes a METPO-prefixed identifier as METPO; the browser source label is consistent with the record. |
| local-ancestor-1 | data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml; Entire local ancestor YAML | supports | The immediate oxygen-preference parent concerns organism oxygen requirements or tolerance for growth. The phenotype ancestor describes variation among instances of a species. Complete local ancestor YAML was read; local link resolution does not independently qualify either class as a protein trait. |
| local-ancestor-2 | data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml; Entire local ancestor YAML | supports | The immediate oxygen-preference parent concerns organism oxygen requirements or tolerance for growth. The phenotype ancestor describes variation among instances of a species. Complete local ancestor YAML was read; local link resolution does not independently qualify either class as a protein trait. |
| metpo-ontology | https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo; Header and complete stanzas METPO:1000603, METPO:1000601, METPO:1000059; pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 | supports | The exact METPO:1000603 stanza matches the target name, definition and parent METPO:1000601. The two retained aliases, anaerobe and Ox_anaerobic, have RELATED scope. The source alias identical to the label is omitted by the emitter. The source identifies growth without molecular oxygen. This definition alone does not assert oxygen toxicity, strict anaerobiosis, a particular alternative electron acceptor or a particular fermentation pathway. The immediate oxygen-preference parent concerns organism oxygen requirements or tolerance for growth. The complete phenotype ancestor and header establish the microbial-phenotype context, canonical w3id.org/metpo namespace, version label 2026-06-12 and CC-BY 4.0. The pinned response is byte-identical to captured main. |
| metpo-project | https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md; Title and purpose; Versions; Identifiers and resolution; License | supports | The official project describes microbial ecophysiological traits and phenotypes and specifies the https://w3id.org/metpo/ namespace for bare seven-digit term identifiers. It declares CC-BY 4.0. This review resolves the target through the actual ontology body; it does not claim every term-page redirect was tested. |
| metpo-license | https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE; License title and public-license identification | supports | The official LICENSE identifies Creative Commons Attribution 4.0 International, consistent with the record, project README and ontology header. This is licence identification rather than an independent audit of all upstream source licensing. |
| metpo-commit | https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&amp;per_page=1; Returned commit SHA/date and path-scoped query; equality with pinned raw response checked from captured bytes | context_only | The path-scoped query returns commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 dated 2026-09-03. The separately captured raw file at that commit equals current main, while its header still reports 2026-06-12. Neither the header date nor present field agreement recovers the original seed snapshot. |
| validation-1 | just validate data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml; Executed 2026-10-21T17:20:01Z through 2026-10-21T17:20:02Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml data/traits/function/environmental_response/metpo/aerotolerant-metpo1000609.yaml data/traits/function/environmental_response/metpo/alkaliphilic-metpo1003002.yaml data/traits/function/environmental_response/metpo/alkalotolerant-metpo1003009.yaml data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml data/traits/function/environmental_response/metpo/barophile-phenotype-metpo1007071.yaml data/traits/function/environmental_response/metpo/capnophilic-metpo1005021.yaml data/traits/function/environmental_response/metpo/euryhaline-metpo1000627.yaml data/traits/function/environmental_response/metpo/extreme-hyperthermophilic-metpo1000721.yaml data/traits/function/environmental_response/metpo/extremely-halophilic-metpo1000628.yaml; Executed 2026-10-21T17:22:15Z through 2026-10-21T17:23:24Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml; Executed 2026-10-21T17:20:02Z through 2026-10-21T17:20:03Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T17:23:24Z through 2026-10-21T17:23:25Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- Source-native definitions and relations are the biological grounding reviewed here. No specific strain growth experiment, universal environmental cutoff or protein mechanism is independently validated.
- Preserve growth without oxygen without adding strict oxygen intolerance or a particular respiratory or fermentative mechanism. A protein oxygen-sensitivity class would require its own identity and evidence.
- Current main and the captured commit-pinned OBO agree byte-for-byte and retain a 2026-06-12 header despite a later file modification. This does not establish the original seed snapshot or independently reproduce its historical run.
- Upstream definition-source annotations were read within the exact METPO stanza as metadata. The complete secondary-ontology and literature chains behind those annotations were not independently resolved; no separate equivalence or mechanistic claim is made from them.
- This review covers the complete named target with ancestors as context. It does not certify or reject the whole source cohort. iModulonDB is not applicable without a specified gene, organism/dataset or expression component.
- External response bodies are retained in session scratch; the review retains source URLs, actual access UTC, SHA256 and exact reading scope. No protein example, native review status or curation-history event is promoted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T172425Z-anaerobic-metpo1000603
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of anaerobic
started_at: '2026-10-21T17:19:07Z'
finished_at: '2026-10-21T17:24:25Z'
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
summary: The anaerobic record faithfully represents the current METPO microbial growth
  phenotype and source hierarchy. One confirmed major concerns importing that organism-level
  class as a protein functional trait. The source identifies growth without molecular
  oxygen. This definition alone does not assert oxygen toxicity, strict anaerobiosis,
  a particular alternative electron acceptor or a particular fermentation pathway.
  Original seed bytes remain unresolved; no protein mechanism or example is qualified.
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
  - path: data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
    sha256: 57c6c36ab4559931fbb294aa920e4fdbf3c92f565f303a53ea0ebd326f0c45b3
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
  selection: Path-order position 5 in batch 038. Fresh main inventory has 429359 records.
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
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb,
    the union covers 368 record paths, leaving 428991 before this batch. 38 inventories
    were combined. Unpublished local coverage is explicitly not published or merged
    main coverage. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - METPO:1000603
targets:
- kind: generated
  label: anaerobic
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  path: data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  record_class: ProteinTraitRecord
  target_id: METPO:1000603
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - METPO:1000603
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml
    data/traits/function/environmental_response/metpo/aerotolerant-metpo1000609.yaml
    data/traits/function/environmental_response/metpo/alkaliphilic-metpo1003002.yaml
    data/traits/function/environmental_response/metpo/alkalotolerant-metpo1003009.yaml
    data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
    data/traits/function/environmental_response/metpo/barophile-phenotype-metpo1007071.yaml
    data/traits/function/environmental_response/metpo/capnophilic-metpo1005021.yaml
    data/traits/function/environmental_response/metpo/euryhaline-metpo1000627.yaml
    data/traits/function/environmental_response/metpo/extreme-hyperthermophilic-metpo1000721.yaml
    data/traits/function/environmental_response/metpo/extremely-halophilic-metpo1000628.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - METPO:1000603
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - METPO:1000603
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
  - METPO:1000603
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: The complete target and recursive local ancestors were inspected against
    the captured schema, project rules, OBO emitter, syntax/emission helpers, registry
    and grouping route. METPO:1000603, METPO:1000601 and METPO:1000059 resolve in
    the actual official OBO at commit 8fddadb3fbd79058e22fbd519e36ab43b3496923, with
    source name, definition, synonym scopes and ancestry matching the target. Namespace
    and licence are verified. This resolution establishes source identity and current
    fidelity, not protein-trait eligibility or original seed bytes.
  target_ids:
  - METPO:1000603
  evidence_ids:
  - record
  - schema
  - project-contract
  - owner
  - obo-syntax
  - yaml-emitter
  - registry
  - grouping-owner
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
  reference: data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 57c6c36ab4559931fbb294aa920e4fdbf3c92f565f303a53ea0ebd326f0c45b3
  support: supports
  summary: 'Complete YAML read: METPO:1000603 (anaerobic), its growth-phenotype definition,
    METPO (2026-06-12) source label, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, CLASS/SEEDED,
    parent METPO:1000601 and CC-BY-4.0. The two retained aliases, anaerobe and Ox_anaerobic,
    have RELATED scope. The source alias identical to the label is omitted by the
    emitter. No protein exemplar, molecular representation, chemical participant,
    xref or causal graph is asserted.'
- evidence_id: project-contract
  kind: record_content
  reference: CLAUDE.md
  locator: Purpose and invariant; Safety rules; status and change-to-gate rules
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
  support: supports
  summary: The project invariant is a knowledge base of protein trait classes. Axes
    follow the defining representation; generated records require an audited maintenance
    route and scientific status is not promoted by automated validation.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord identifier, definition, parent_traits and optional representations;
    FUNCTION and FUNC_ENVIRONMENTAL_RESPONSE
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: ProteinTraitRecord uses source identifiers for one-to-one class identity;
    parent_traits expresses broader classes. FUNC_ENVIRONMENTAL_RESPONSE covers environmental
    response or requirement with response-process or induction grounding. This category
    remains subject to the project protein-trait invariant. Examples, molecular representations
    and causal graphs are optional, not a means of changing an organism phenotype
    into a protein class.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_obo.py
  locator: SOURCES metpo route; build_routing; build_yaml; read_release_stamp; seed_source
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 8b33fbdac45c28420b3e6ca31d0d9feb16c90701eb77c392b571f1b3261c7a9f
  support: supports
  summary: The configured METPO:1000601 oxygen-preference route selects descendants
    by is_a and assigns FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. build_yaml retains source
    identifier, definition, parents and non-label synonyms; it does not derive a protein
    capability from an organism phenotype. read_release_stamp selects a header date.
    Existing records are skipped unless force is used; dry-run is default and applying
    a changed route does not automatically retire excluded existing records.
- evidence_id: obo-syntax
  kind: record_content
  reference: scripts/obo_syntax.py
  locator: unescape, strip_comment and strip_suffixes
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 86cd5936ecb214f41073fc5ac56425efe647b56bf9a663dad62f6edfad3fbc0e
  support: supports
  summary: The shared parser helpers handle escaping, comments and suffix syntax.
    These are lexical transformations, not independent biological support.
- evidence_id: yaml-emitter
  kind: record_content
  reference: scripts/yaml_emit.py
  locator: yaml_escape and slugify
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
  support: supports
  summary: The scalar and slug helpers preserve text and construct paths. They do
    not change biological denotation.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: METPO source block
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: The METPO registry block declares the official main OBO, CC-BY 4.0, hierarchy,
    the two functional categories and seed_obo.py. This establishes maintained provenance,
    not protein-level eligibility of each selected class.
- evidence_id: grouping-owner
  kind: record_content
  reference: scripts/seed_grouping_parents.py
  locator: TARGETS METPO:1000059; parse_obo; child_stamp; main
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 504e4630cce0d19e86fe47a55b02008a77ebc8cfb6f4cdfddf487f1401a724f7
  support: supports
  summary: This helper emits the METPO:1000059 phenotype grouping ancestor at the
    configured scope boundary, inheriting the source stamp and category and stopping
    its parent chain. It does not own the reviewed child term.
- evidence_id: browser-source
  kind: record_content
  reference: scripts/build_docs_index.py
  locator: infer_source METPO branch
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 926f593f6d3c81b16ff72148f1777d0b6d81cabe5fe806f4667c5745f28bb818
  support: supports
  summary: infer_source recognizes a METPO-prefixed identifier as METPO; the browser
    source label is consistent with the record.
- evidence_id: local-ancestor-1
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml
  locator: Entire local ancestor YAML
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 1ca0c206d8dcb38047a5f09b4843571524d85af2915375b26f8fa4c69a9e07c5
  support: supports
  summary: The immediate oxygen-preference parent concerns organism oxygen requirements
    or tolerance for growth. The phenotype ancestor describes variation among instances
    of a species. Complete local ancestor YAML was read; local link resolution does
    not independently qualify either class as a protein trait.
- evidence_id: local-ancestor-2
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml
  locator: Entire local ancestor YAML
  accessed_at: '2026-10-21T17:19:07Z'
  snapshot_sha256: 903daba1e34fdc7cace6ae639bd6bab85f0fb9acb6dfd33979ed8e1970992ddc
  support: supports
  summary: The immediate oxygen-preference parent concerns organism oxygen requirements
    or tolerance for growth. The phenotype ancestor describes variation among instances
    of a species. Complete local ancestor YAML was read; local link resolution does
    not independently qualify either class as a protein trait.
- evidence_id: metpo-ontology
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo
  accessed_at: '2026-10-21T17:19:10.890311Z'
  snapshot_sha256: 951019bb3917cd48105e4b3e1cc745af697e0d60a50d5292925310d615108b32
  support: supports
  locator: Header and complete stanzas METPO:1000603, METPO:1000601, METPO:1000059;
    pinned commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
  summary: The exact METPO:1000603 stanza matches the target name, definition and
    parent METPO:1000601. The two retained aliases, anaerobe and Ox_anaerobic, have
    RELATED scope. The source alias identical to the label is omitted by the emitter.
    The source identifies growth without molecular oxygen. This definition alone does
    not assert oxygen toxicity, strict anaerobiosis, a particular alternative electron
    acceptor or a particular fermentation pathway. The immediate oxygen-preference
    parent concerns organism oxygen requirements or tolerance for growth. The complete
    phenotype ancestor and header establish the microbial-phenotype context, canonical
    w3id.org/metpo namespace, version label 2026-06-12 and CC-BY 4.0. The pinned response
    is byte-identical to captured main.
- evidence_id: metpo-project
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md
  accessed_at: '2026-10-21T17:19:10.533888Z'
  snapshot_sha256: 3fbbd78aef5c77e8dfa9c09447fed03c26211a52d79382b0ac763482500667f1
  support: supports
  locator: Title and purpose; Versions; Identifiers and resolution; License
  summary: The official project describes microbial ecophysiological traits and phenotypes
    and specifies the https://w3id.org/metpo/ namespace for bare seven-digit term
    identifiers. It declares CC-BY 4.0. This review resolves the target through the
    actual ontology body; it does not claim every term-page redirect was tested.
- evidence_id: metpo-license
  kind: authority
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE
  accessed_at: '2026-10-21T17:19:10.543005Z'
  snapshot_sha256: 9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411
  support: supports
  locator: License title and public-license identification
  summary: The official LICENSE identifies Creative Commons Attribution 4.0 International,
    consistent with the record, project README and ontology header. This is licence
    identification rather than an independent audit of all upstream source licensing.
- evidence_id: metpo-commit
  kind: database
  reference: https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&per_page=1
  accessed_at: '2026-10-21T17:19:10.721498Z'
  snapshot_sha256: cb72f320df01d1039edd9d170b784ad1f2bd699bedaba0b3176a1d4ed22ccee1
  support: context_only
  locator: Returned commit SHA/date and path-scoped query; equality with pinned raw
    response checked from captured bytes
  summary: The path-scoped query returns commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
    dated 2026-09-03. The separately captured raw file at that commit equals current
    main, while its header still reports 2026-06-12. Neither the header date nor present
    field agreement recovers the original seed snapshot.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  locator: Executed 2026-10-21T17:20:01Z through 2026-10-21T17:20:02Z; exit 0
  accessed_at: '2026-10-21T17:20:02Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/environmental_response/metpo/aerobic-metpo1000602.yaml
    data/traits/function/environmental_response/metpo/aerotolerant-metpo1000609.yaml
    data/traits/function/environmental_response/metpo/alkaliphilic-metpo1003002.yaml
    data/traits/function/environmental_response/metpo/alkalotolerant-metpo1003009.yaml
    data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
    data/traits/function/environmental_response/metpo/barophile-phenotype-metpo1007071.yaml
    data/traits/function/environmental_response/metpo/capnophilic-metpo1005021.yaml
    data/traits/function/environmental_response/metpo/euryhaline-metpo1000627.yaml
    data/traits/function/environmental_response/metpo/extreme-hyperthermophilic-metpo1000721.yaml
    data/traits/function/environmental_response/metpo/extremely-halophilic-metpo1000628.yaml
  locator: Executed 2026-10-21T17:22:15Z through 2026-10-21T17:23:24Z; exit 0
  accessed_at: '2026-10-21T17:23:24Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/environmental_response/metpo/anaerobic-metpo1000603.yaml
  locator: Executed 2026-10-21T17:20:02Z through 2026-10-21T17:20:03Z; exit 0
  accessed_at: '2026-10-21T17:20:03Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T17:23:24Z through 2026-10-21T17:23:25Z; exit 0
  accessed_at: '2026-10-21T17:23:25Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  topic: Maintained source route and inherited grouping
  summary: The oxygen-preference branch and reviewed record emission are maintained
    in seed_obo.py; the grouping ancestor has a separate generator. Registry and browser
    provenance agree. Any correction belongs to that maintained route and an audited
    existing-record disposition, not an untracked hand edit.
  evidence_ids:
  - owner
  - registry
  - grouping-owner
  - browser-source
  target_ids:
  - METPO:1000603
  assessment_id: assessment-1
- area: identity
  outcome: supported
  topic: Exact microbial phenotype identity
  summary: The full target correctly resolves to METPO:1000603 (anaerobic). Its source
    definition, retained synonym scopes and immediate parent match the current official
    ontology. The finding concerns protein-trait eligibility, not a wrong accession
    or an obsolete term.
  evidence_ids:
  - record
  - metpo-ontology
  - metpo-project
  target_ids:
  - METPO:1000603
  assessment_id: assessment-2
- area: evidence
  outcome: supported
  topic: Source-defined growth and tolerance semantics
  summary: The source identifies growth without molecular oxygen. This definition
    alone does not assert oxygen toxicity, strict anaerobiosis, a particular alternative
    electron acceptor or a particular fermentation pathway. This positively supports
    the represented ontology meaning; no particular strain experiment, protein activity
    or universal environmental boundary is independently certified.
  evidence_ids:
  - record
  - metpo-ontology
  target_ids:
  - METPO:1000603
  assessment_id: assessment-3
- area: consistency
  outcome: supported
  topic: Source hierarchy and lexical fidelity
  summary: The immediate oxygen-preference parent concerns organism oxygen requirements
    or tolerance for growth. The two retained aliases, anaerobe and Ox_anaerobic,
    have RELATED scope. The source alias identical to the label is omitted by the
    emitter. The local phenotype ancestor stops at the documented grouping boundary.
    No separate broken-parent or alias defect is established for this target.
  evidence_ids:
  - record
  - metpo-ontology
  - owner
  - grouping-owner
  - local-ancestor-1
  - local-ancestor-2
  target_ids:
  - METPO:1000603
  assessment_id: assessment-4
- area: representation
  outcome: concern
  topic: Organism phenotype versus protein capability
  summary: Growth in the absence of oxygen describes an organism phenotype. It does
    not specify a protein that functions only anaerobically, an oxygen-labile enzyme,
    or a defined anaerobic-response mechanism. The FUNCTION/category combination is
    permitted syntactically, but the defining evidence remains organism-level and
    has not been converted into a supported protein trait.
  evidence_ids:
  - record
  - schema
  - project-contract
  - owner
  - metpo-ontology
  target_ids:
  - METPO:1000603
  assessment_id: assessment-5
- area: grounding
  outcome: supported
  topic: Source identity retained without repurposing
  summary: METPO:1000603 genuinely identifies the source phenotype. The record contains
    no equivalence xref to adjudicate separately. A future protein-response class
    must not silently reuse this identifier with a different meaning or treat mere
    association with the organism phenotype as equivalence.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  target_ids:
  - METPO:1000603
  assessment_id: assessment-6
- area: provenance
  outcome: unknown
  topic: Current source agreement versus original seed snapshot
  summary: The present record fields agree with the current commit-pinned ontology
    and its 2026-06-12 header. The captured file modification is later than that date;
    the original seed bytes and original input sidecar have not been established in
    this review. Current source identity, maintained owner and licence are positively
    supported.
  evidence_ids:
  - record
  - owner
  - registry
  - metpo-ontology
  - metpo-commit
  - metpo-project
  - metpo-license
  target_ids:
  - METPO:1000603
  assessment_id: assessment-7
- area: completeness
  outcome: concern
  topic: Class eligibility before optional enrichment
  summary: The target identifies a reusable microbial phenotype sufficiently for review.
    Its protein-trait eligibility must be resolved before enrichment. Missing optional
    examples, sequences, structures or causal graphs are not separate completeness
    findings, and adding them cannot by itself change the source class denotation.
  evidence_ids:
  - record
  - schema
  - project-contract
  - metpo-ontology
  target_ids:
  - METPO:1000603
  assessment_id: assessment-8
- area: graph
  outcome: not_applicable
  topic: No mechanism graph asserted
  summary: The full YAML contains no causal graph. Deterministic graph validation
    does not establish a protein mechanism.
  evidence_ids:
  - record
  target_ids:
  - METPO:1000603
  assessment_id: assessment-9
- area: scope
  outcome: concern
  topic: Domain boundary and status
  summary: Preserve growth without oxygen without adding strict oxygen intolerance
    or a particular respiratory or fermentative mechanism. A protein oxygen-sensitivity
    class would require its own identity and evidence. The target remains SEEDED;
    this observation neither promotes scientific status nor qualifies any protein
    example.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  - owner
  target_ids:
  - METPO:1000603
  assessment_id: assessment-10
findings:
- issue_key: metpo.environmental-response.METPO-1000603.organism-growth-as-protein-trait
  category: scope
  severity: major
  certainty: confirmed
  title: Organism growth phenotype is imported as a protein trait
  description: METPO:1000603 (anaerobic) is defined by organism growth or tolerance.
    Growth in the absence of oxygen describes an organism phenotype. It does not specify
    a protein that functions only anaerobically, an oxygen-labile enzyme, or a defined
    anaerobic-response mechanism. The maintained METPO:1000601 route copies that phenotype
    into a ProteinTraitRecord under FUNC_ENVIRONMENTAL_RESPONSE without a distinct
    protein-level defining assertion. The METPO identifier and source meaning are
    correct; the error is the source-to-domain eligibility decision.
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
  rule_id: 'ProteinTraitRecord checklist: class identity, defining representation,
    hierarchy and exact evidence scope'
  normalization_reason: 'Major: a correctly identified organism phenotype is systematically
    represented as a protein trait without supported protein-level semantics. The
    retained source identity prevents treating this as a wrong-identifier blocker.'
  finding_id: F1
  status: open
  target_ids:
  - METPO:1000603
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  native_severity: major
actions:
- action_id: A1
  description: Adjudicate METPO:1000603 eligibility in the maintained oxygen-preference
    route in scripts/seed_obo.py and document the disposition of this existing record
    and its references. Preserve growth without oxygen without adding strict oxygen
    intolerance or a particular respiratory or fermentative mechanism. A protein oxygen-sensitivity
    class would require its own identity and evidence. If excluded from protein-trait
    emission, use an audited migration or deprecation/reference plan; a route exclusion
    alone does not remove an existing record. If a separate protein capability is
    supported, give it its own identity and protein-level definition with explicit
    scoped evidence and an appropriate relationship to the organism phenotype. Do
    not relabel this METPO phenotype as that new protein property.
  finding_ids:
  - F1
  target_ids:
  - METPO:1000603
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  acceptance_checks:
  - Record a curator-adjudicated eligibility and existing-record disposition for METPO:1000603,
    preserving the source organism-phenotype identity and documented meaning.
  - Exercise the maintained OBO route against a pinned source snapshot in dry-run
    mode and inspect the reviewed term outcome. Verify that route exclusion is not
    mistaken for retirement of a pre-existing file.
  - Audit affected parent/child references and any old identifier disposition for
    resulting paths after a separately authorized migration or deprecation. Do not
    generalize this one-record judgment to unreviewed branch members.
  - Any distinct protein class requires its own identity, protein-level definition
    and scoped support. Keep its relationship to the organism phenotype separate from
    equivalence; optional examples use the existing reviewed qualification workflow.
  - For a future generator change, run just lint, focused pytest, just test and just
    audit-writers. For resulting records, run just validate <resulting-path>, just
    validate-all <resulting-path> and just audit-graphs <resulting-path>; run full
    just validate-all before merge and just validate-history for the full history
    tree. Add a fresh immutable review of the actual corrected outcome.
limitations:
- Source-native definitions and relations are the biological grounding reviewed here.
  No specific strain growth experiment, universal environmental cutoff or protein
  mechanism is independently validated.
- Preserve growth without oxygen without adding strict oxygen intolerance or a particular
  respiratory or fermentative mechanism. A protein oxygen-sensitivity class would
  require its own identity and evidence.
- Current main and the captured commit-pinned OBO agree byte-for-byte and retain a
  2026-06-12 header despite a later file modification. This does not establish the
  original seed snapshot or independently reproduce its historical run.
- Upstream definition-source annotations were read within the exact METPO stanza as
  metadata. The complete secondary-ontology and literature chains behind those annotations
  were not independently resolved; no separate equivalence or mechanistic claim is
  made from them.
- This review covers the complete named target with ancestors as context. It does
  not certify or reject the whole source cohort. iModulonDB is not applicable without
  a specified gene, organism/dataset or expression component.
- External response bodies are retained in session scratch; the review retains source
  URLs, actual access UTC, SHA256 and exact reading scope. No protein example, native
  review status or curation-history event is promoted.
tags:
- unreviewed-path-order
- batch-038
- metpo
```
