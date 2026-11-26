# Review of facultative oxygen preference

- Review: 20261021T174013Z-facultative-oxygen-preference-metpo1000612
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T17:32:49Z
- Finished UTC: 2026-10-21T17:40:13Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The current METPO source and the local facultative oxygen preference record agree in identity, copied definition and hierarchy. One confirmed major concerns its organism-growth denotation being imported as a protein trait. The defining observation is microbial growth both with and without molecular oxygen. It does not specify a preference for either condition, a quantitative growth advantage, or a particular respiratory or fermentative pathway.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 039. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb; ee9a05771251fd84096ca40cfee30ea23e064f91, the union covers 378 record paths, leaving 428981 before this batch. 39 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| METPO:1000612 | data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml | generated | facultative oxygen preference |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | METPO:1000612 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | METPO:1000612 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | METPO:1000612 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | METPO:1000612 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | METPO:1000612 | The complete METPO:1000612 target and recursive ancestors were read with the captured project contract, schema, maintained OBO route, syntax/emission helpers, registry and grouping owner. Exact name, definition, synonym scopes and parent resolve in the official OBO pinned to 8fddadb3fbd79058e22fbd519e36ab43b3496923; namespace and licence were inspected. Selected annotation terms were independently resolved at the explicitly stated scope, including empty or contrasting definitions where present. Current resolution is not proof of protein-domain eligibility, original seed bytes or complete citation-chain support. |

## Scientific And Domain Assessments

### Maintained OBO route and grouping boundary

ownership: supported. Targets: METPO:1000612.

The reviewed leaf is emitted through the oxygen preference route in seed_obo.py. The phenotype grouping uses a separate maintained helper. Any future eligibility correction needs a route decision and an audited disposition of the existing record and references.

### Exact source phenotype identity

identity: supported. Targets: METPO:1000612.

METPO:1000612 resolves to facultative oxygen preference in the current official ontology. Full local name, definition, parent and synonym scopes agree. Correct microbial source identity is distinguishable from eligibility for the protein-trait domain.

### Source-defined growth semantics

evidence: supported. Targets: METPO:1000612.

The defining observation is microbial growth both with and without molecular oxygen. It does not specify a preference for either condition, a quantitative growth advantage, or a particular respiratory or fermentative pathway. This assessment establishes authentic source denotation, not independent experimental validation of all physiological criteria.

### Independent definition-source scope

evidence: unknown. Targets: METPO:1000612.

OMP:0000087 supports the organism-level facultative context and calls facultative aerobe an exact synonym of its facultative anaerobe class. That source describes metabolic use of oxygen when available. METPO:1000612 is phrased more generally as growth under either condition; its exact meaning must not be silently strengthened to a quantitative respiratory preference.

### Local hierarchy and lexical fidelity

consistency: supported. Targets: METPO:1000612.

The parent concerns organism oxygen requirements or tolerance for growth. The sole retained alias Ox_facultative_aerobe_anaerobe is RELATED, as in METPO. The recursive local ancestors resolve and the phenotype grouping ends at the maintained scope boundary. No separate broken-parent finding is established.

### Organism growth versus protein capability

representation: concern. Targets: METPO:1000612.

Growth under both oxygen conditions is a property of the microorganism. It does not define oxygen-independent catalysis, protein oxygen sensing or a particular protein induction response. The source-to-category route preserves organism denotation rather than defining a distinct protein response.

### Retained source identifier without identity transfer

grounding: supported. Targets: METPO:1000612.

The METPO identifier denotes the reviewed organism phenotype correctly. No equivalence xref is present. A future protein-level class must not silently take METPO:1000612 with changed meaning; any relationship between that class and the organism phenotype needs its own scoped justification.

### Current source agreement and historical release limit

provenance: unknown. Targets: METPO:1000612.

The present OBO, pinned commit, header date, source registry, licence and target fields agree at the stated scope. The original seed snapshot and input sidecar were not recovered, so the header date is not proof of original-release bytes.

### Protein-class eligibility precedes optional enrichment

completeness: concern. Targets: METPO:1000612.

The organism phenotype has a reusable class identity. Its eligibility as a protein trait remains the material gap. No mandatory protein exemplar, sequence, structure or causal graph is inferred from optional fields, and adding an example would not itself change the class denotation.

### No asserted mechanism graph

graph: not_applicable. Targets: METPO:1000612.

The full target has no causal graph. Native graph checks do not supply a molecular mechanism.

### Preserve organism-level qualifiers

scope: concern. Targets: METPO:1000612.

The captured external METPO stanzas METPO:1000612, METPO:1000608 and METPO:1000605 have overlapping growth definitions but distinct identifiers and annotations. Neither that overlap nor the OMP synonym proves a deterministic merge or a strict physiological distinction among those METPO classes. No protein instance is qualified and the SEEDED status is unchanged.

## Findings

### F1: Organism growth phenotype is represented as a protein trait

major / open / confirmed; issue key: metpo.environmental-response.METPO-1000612.organism-growth-as-protein-trait.

The definition of METPO:1000612 concerns organism growth. Growth under both oxygen conditions is a property of the microorganism. It does not define oxygen-independent catalysis, protein oxygen sensing or a particular protein induction response. The maintained route assigns this unchanged denotation to a ProteinTraitRecord in FUNC_ENVIRONMENTAL_RESPONSE without a separate protein-level defining predicate. The identifier is correctly resolved; the mismatch is the eligibility decision, not a wrong source accession.

## Recommended Actions And Acceptance Checks

### A1

Adjudicate METPO:1000612 in the maintained oxygen preference branch of scripts/seed_obo.py and document the disposition of this existing record and its references. Preserve its source growth qualifiers. If excluded, use an audited retirement or migration plan. If evidence supports a separate protein response, define that class with its own identity and support and an appropriate explicit relationship to the organism phenotype. Do not reinterpret this METPO identifier as a protein property.

- Document the curator-adjudicated protein-domain eligibility and existing-record disposition for METPO:1000612, retaining its source organism-phenotype denotation.
- Exercise the maintained OBO route on a pinned input in dry-run mode and inspect the term outcome. If excluded, separately audit old-file retirement or migration and references; exclusion from future emission is not removal of existing output.
- Any distinct protein response class requires its own identity, protein-level definition and scoped support. Do not reassign the METPO phenotype identifier or infer equivalence merely from association. Optional examples follow the existing reviewed qualification workflow.
- For a future generator change run just lint, focused pytest, just test and just audit-writers. For resulting paths after an authorized disposition run just validate &lt;resulting-path&gt;, just validate-all &lt;resulting-path&gt; and just audit-graphs &lt;resulting-path&gt;; run full just validate-all before merge and just validate-history for the full history tree. Record a fresh immutable review of the actual corrected outcome.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml; Entire target YAML | supports | Entire YAML read: METPO:1000612 (facultative oxygen preference), exact growth definition, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, CLASS/SEEDED, METPO (2026-06-12), CC-BY-4.0 and parent METPO:1000601. The sole retained alias Ox_facultative_aerobe_anaerobe is RELATED, as in METPO. It asserts no protein example, molecular representation, xref, chemical participant or causal graph. |
| project-contract | CLAUDE.md; Protein-trait invariant, axis rules and generated-data maintenance rules | supports | The project represents protein trait classes and assigns axes by defining representation. A structurally valid generated record is not thereby a biologically qualified protein class. Generated corrections require the maintained ownership route. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord identifier/definition/parent_traits; FUNC_ENVIRONMENTAL_RESPONSE; optional representations | supports | The environmental-response category describes response or requirement to environmental conditions, with response-process or induction grounding, within a ProteinTraitRecord. Identifiers require one-to-one class identity; parent_traits states broader classes. Optional examples, structures and mechanisms are not required merely to make a record complete. |
| owner | scripts/seed_obo.py; SOURCES METPO routes; build_routing; build_yaml; read_release_stamp; seed_source | supports | The METPO METPO:1000601 route selects descendant classes by is_a and assigns FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. build_yaml copies source identity, definition, parents and non-label synonyms. It does not independently qualify protein-level meaning. The release stamp follows the source header. Existing output is skipped unless force is used; dry-run is default. Excluding a term from a future route does not itself retire existing output. |
| obo-syntax | scripts/obo_syntax.py; unescape, strip_comment and strip_suffixes | supports | Escaping, comments and suffix helpers perform lexical parsing. They do not transform an organism growth phenotype into a protein property. |
| yaml-emitter | scripts/yaml_emit.py; yaml_escape and slugify | supports | The YAML scalar and slug helpers preserve source text and build paths; they are not additional biological evidence. |
| registry | download.yaml; METPO block | supports | The METPO source block declares official OBO acquisition, CC-BY 4.0, its functional routes and seed_obo.py. It supports maintained provenance rather than individual term eligibility. |
| grouping-owner | scripts/seed_grouping_parents.py; TARGETS METPO:1000059; parse_obo; child_stamp; main | supports | METPO:1000059 is emitted as a phenotype grouping ancestor with a controlled parent boundary. This helper owns the grouping record, not the reviewed leaf. The stopped ancestor is not a broken source link. |
| browser-source | scripts/build_docs_index.py; infer_source METPO branch | supports | METPO identifier prefixes are recognized as METPO by the browser source inference. This agrees with the target provenance. |
| local-ancestor-1 | data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml; Entire ancestor YAML | supports | Entire ancestor METPO:1000601 (oxygen preference) read, including definition, hierarchy and source status. The parent concerns organism oxygen requirements or tolerance for growth. Its role here is hierarchy context, not an independent approval of a protein class. |
| local-ancestor-2 | data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml; Entire ancestor YAML | supports | Entire ancestor METPO:1000059 (phenotype) read, including definition, hierarchy and source status. The phenotype grouping concerns variation among instances of a species and stops at its configured local boundary. Its role here is hierarchy context, not an independent approval of a protein class. |
| facultative-context | https://www.ebi.ac.uk/ols4/api/ontologies/omp/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOMP_0000087; Exact returned term: label, description, obo_synonym, definition citations and status | context_only | The exact nonobsolete OMP:0000087 object denotes facultative anaerobe and records facultative aerobe as an EXACT synonym. Its organism phenotype does not require oxygen for growth but uses it in metabolism when present. This provides source context, not protein-level evidence or an automatic equivalence between distinct METPO identifiers. |
| metpo-ontology | https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo; Header and complete stanzas METPO:1000612, METPO:1000601, METPO:1000059, METPO:1000608, METPO:1000605; commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 | supports | The complete METPO:1000612 stanza agrees with the target label, definition, parent and retained synonym scopes. The sole retained alias Ox_facultative_aerobe_anaerobe is RELATED, as in METPO. The defining observation is microbial growth both with and without molecular oxygen. It does not specify a preference for either condition, a quantitative growth advantage, or a particular respiratory or fermentative pathway. The parent concerns organism oxygen requirements or tolerance for growth. Header and phenotype ancestry establish microbial phenotype scope. Source annotations are citations, not automatically equivalence relations. The pinned OBO is byte-identical to current captured main. |
| metpo-project | https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md; Full README, especially purpose, identifier resolution, versions and licence | supports | The official project describes microbial ecophysiological traits and phenotypes. It specifies the w3id.org/metpo namespace for seven-digit terms and declares CC-BY 4.0. Ontology-body resolution was inspected; universal term-page redirect behavior was not tested. |
| metpo-license | https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE; Licence title and public-licence identification | supports | The official licence text identifies Creative Commons Attribution 4.0 International, consistent with the ontology header, README and local record. This does not independently audit every upstream source licence. |
| metpo-commit | https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&amp;per_page=1; Returned commit identity/date and request path; raw equality checked separately | context_only | The path-scoped result identifies commit 8fddadb3fbd79058e22fbd519e36ab43b3496923 dated 2026-09-03. Its captured raw OBO equals current main despite retaining a 2026-06-12 header. These current observations do not establish the original seeding input bytes. |
| validation-1 | just validate data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml; Executed 2026-10-21T17:33:18Z through 2026-10-21T17:33:19Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml data/traits/function/environmental_response/metpo/facultative-psychrophilic-metpo1000720.yaml data/traits/function/environmental_response/metpo/facultatively-acidophilic-metpo1003007.yaml data/traits/function/environmental_response/metpo/facultatively-aerobic-metpo1000608.yaml data/traits/function/environmental_response/metpo/facultatively-alkaliphilic-metpo1003005.yaml data/traits/function/environmental_response/metpo/facultatively-anaerobic-metpo1000605.yaml data/traits/function/environmental_response/metpo/haloalkaliphilic-metpo1000621.yaml data/traits/function/environmental_response/metpo/halophilic-metpo1000620.yaml data/traits/function/environmental_response/metpo/halophily-preference-metpo1000629.yaml data/traits/function/environmental_response/metpo/halotolerant-metpo1000622.yaml; Executed 2026-10-21T17:34:00Z through 2026-10-21T17:35:12Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml; Executed 2026-10-21T17:33:19Z through 2026-10-21T17:33:19Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T17:35:12Z through 2026-10-21T17:35:13Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The captured external METPO stanzas METPO:1000612, METPO:1000608 and METPO:1000605 have overlapping growth definitions but distinct identifiers and annotations. Neither that overlap nor the OMP synonym proves a deterministic merge or a strict physiological distinction among those METPO classes.
- Source ontology definitions and selected cited ontology objects were inspected, not strain-specific growth experiments or protein activity data. Definition-source annotations are not assumed equivalence assertions; the entire upstream citation network was not validated.
- The complete source stanzas and current header agree with the target; main and commit-pinned bytes match. The original seeding input and historical run remain unestablished.
- This review covers the named record with captured local ancestors and external ontology context. It neither certifies nor rejects the full route. iModulonDB does not apply without a specified gene, organism/dataset or expression component.
- Actual source bodies, access UTC, URLs and SHA256 are retained in scratch. No protein example, native review status or curation-history event is promoted by these scientific observations.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T174013Z-facultative-oxygen-preference-metpo1000612
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of facultative oxygen preference
started_at: '2026-10-21T17:32:49Z'
finished_at: '2026-10-21T17:40:13Z'
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
summary: The current METPO source and the local facultative oxygen preference record
  agree in identity, copied definition and hierarchy. One confirmed major concerns
  its organism-growth denotation being imported as a protein trait. The defining observation
  is microbial growth both with and without molecular oxygen. It does not specify
  a preference for either condition, a quantitative growth advantage, or a particular
  respiratory or fermentative pathway.
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
  - path: data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
    sha256: cf539ded86c334d7ac3b43a8351331b789a0fb9e21b84413a15051ce930483ad
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
  selection: Path-order position 1 in batch 039. Fresh main inventory has 429359 records.
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
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb;
    ee9a05771251fd84096ca40cfee30ea23e064f91, the union covers 378 record paths, leaving
    428981 before this batch. 39 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - METPO:1000612
targets:
- kind: generated
  label: facultative oxygen preference
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  path: data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  record_class: ProteinTraitRecord
  target_id: METPO:1000612
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - METPO:1000612
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
    data/traits/function/environmental_response/metpo/facultative-psychrophilic-metpo1000720.yaml
    data/traits/function/environmental_response/metpo/facultatively-acidophilic-metpo1003007.yaml
    data/traits/function/environmental_response/metpo/facultatively-aerobic-metpo1000608.yaml
    data/traits/function/environmental_response/metpo/facultatively-alkaliphilic-metpo1003005.yaml
    data/traits/function/environmental_response/metpo/facultatively-anaerobic-metpo1000605.yaml
    data/traits/function/environmental_response/metpo/haloalkaliphilic-metpo1000621.yaml
    data/traits/function/environmental_response/metpo/halophilic-metpo1000620.yaml
    data/traits/function/environmental_response/metpo/halophily-preference-metpo1000629.yaml
    data/traits/function/environmental_response/metpo/halotolerant-metpo1000622.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - METPO:1000612
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - METPO:1000612
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
  - METPO:1000612
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: The complete METPO:1000612 target and recursive ancestors were read with
    the captured project contract, schema, maintained OBO route, syntax/emission helpers,
    registry and grouping owner. Exact name, definition, synonym scopes and parent
    resolve in the official OBO pinned to 8fddadb3fbd79058e22fbd519e36ab43b3496923;
    namespace and licence were inspected. Selected annotation terms were independently
    resolved at the explicitly stated scope, including empty or contrasting definitions
    where present. Current resolution is not proof of protein-domain eligibility,
    original seed bytes or complete citation-chain support.
  target_ids:
  - METPO:1000612
  evidence_ids:
  - record
  - project-contract
  - schema
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
  - facultative-context
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: cf539ded86c334d7ac3b43a8351331b789a0fb9e21b84413a15051ce930483ad
  support: supports
  summary: 'Entire YAML read: METPO:1000612 (facultative oxygen preference), exact
    growth definition, FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE, CLASS/SEEDED, METPO (2026-06-12),
    CC-BY-4.0 and parent METPO:1000601. The sole retained alias Ox_facultative_aerobe_anaerobe
    is RELATED, as in METPO. It asserts no protein example, molecular representation,
    xref, chemical participant or causal graph.'
- evidence_id: project-contract
  kind: record_content
  reference: CLAUDE.md
  locator: Protein-trait invariant, axis rules and generated-data maintenance rules
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
  support: supports
  summary: The project represents protein trait classes and assigns axes by defining
    representation. A structurally valid generated record is not thereby a biologically
    qualified protein class. Generated corrections require the maintained ownership
    route.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord identifier/definition/parent_traits; FUNC_ENVIRONMENTAL_RESPONSE;
    optional representations
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: The environmental-response category describes response or requirement to
    environmental conditions, with response-process or induction grounding, within
    a ProteinTraitRecord. Identifiers require one-to-one class identity; parent_traits
    states broader classes. Optional examples, structures and mechanisms are not required
    merely to make a record complete.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_obo.py
  locator: SOURCES METPO routes; build_routing; build_yaml; read_release_stamp; seed_source
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 8b33fbdac45c28420b3e6ca31d0d9feb16c90701eb77c392b571f1b3261c7a9f
  support: supports
  summary: The METPO METPO:1000601 route selects descendant classes by is_a and assigns
    FUNCTION/FUNC_ENVIRONMENTAL_RESPONSE. build_yaml copies source identity, definition,
    parents and non-label synonyms. It does not independently qualify protein-level
    meaning. The release stamp follows the source header. Existing output is skipped
    unless force is used; dry-run is default. Excluding a term from a future route
    does not itself retire existing output.
- evidence_id: obo-syntax
  kind: record_content
  reference: scripts/obo_syntax.py
  locator: unescape, strip_comment and strip_suffixes
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 86cd5936ecb214f41073fc5ac56425efe647b56bf9a663dad62f6edfad3fbc0e
  support: supports
  summary: Escaping, comments and suffix helpers perform lexical parsing. They do
    not transform an organism growth phenotype into a protein property.
- evidence_id: yaml-emitter
  kind: record_content
  reference: scripts/yaml_emit.py
  locator: yaml_escape and slugify
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
  support: supports
  summary: The YAML scalar and slug helpers preserve source text and build paths;
    they are not additional biological evidence.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: METPO block
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: The METPO source block declares official OBO acquisition, CC-BY 4.0, its
    functional routes and seed_obo.py. It supports maintained provenance rather than
    individual term eligibility.
- evidence_id: grouping-owner
  kind: record_content
  reference: scripts/seed_grouping_parents.py
  locator: TARGETS METPO:1000059; parse_obo; child_stamp; main
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 504e4630cce0d19e86fe47a55b02008a77ebc8cfb6f4cdfddf487f1401a724f7
  support: supports
  summary: METPO:1000059 is emitted as a phenotype grouping ancestor with a controlled
    parent boundary. This helper owns the grouping record, not the reviewed leaf.
    The stopped ancestor is not a broken source link.
- evidence_id: browser-source
  kind: record_content
  reference: scripts/build_docs_index.py
  locator: infer_source METPO branch
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 926f593f6d3c81b16ff72148f1777d0b6d81cabe5fe806f4667c5745f28bb818
  support: supports
  summary: METPO identifier prefixes are recognized as METPO by the browser source
    inference. This agrees with the target provenance.
- evidence_id: local-ancestor-1
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/oxygen-preference-metpo1000601.yaml
  locator: Entire ancestor YAML
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 1ca0c206d8dcb38047a5f09b4843571524d85af2915375b26f8fa4c69a9e07c5
  support: supports
  summary: Entire ancestor METPO:1000601 (oxygen preference) read, including definition,
    hierarchy and source status. The parent concerns organism oxygen requirements
    or tolerance for growth. Its role here is hierarchy context, not an independent
    approval of a protein class.
- evidence_id: local-ancestor-2
  kind: record_content
  reference: data/traits/function/environmental_response/metpo/phenotype-metpo1000059.yaml
  locator: Entire ancestor YAML
  accessed_at: '2026-10-21T17:32:49Z'
  snapshot_sha256: 903daba1e34fdc7cace6ae639bd6bab85f0fb9acb6dfd33979ed8e1970992ddc
  support: supports
  summary: Entire ancestor METPO:1000059 (phenotype) read, including definition, hierarchy
    and source status. The phenotype grouping concerns variation among instances of
    a species and stops at its configured local boundary. Its role here is hierarchy
    context, not an independent approval of a protein class.
- evidence_id: facultative-context
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/omp/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FOMP_0000087
  accessed_at: '2026-10-21T17:33:42.029603Z'
  snapshot_sha256: 1f943631e765914ab7e4f77d95b99c8466bafe6691a7fa1dd8ee776cac211500
  support: context_only
  locator: 'Exact returned term: label, description, obo_synonym, definition citations
    and status'
  summary: The exact nonobsolete OMP:0000087 object denotes facultative anaerobe and
    records facultative aerobe as an EXACT synonym. Its organism phenotype does not
    require oxygen for growth but uses it in metabolism when present. This provides
    source context, not protein-level evidence or an automatic equivalence between
    distinct METPO identifiers.
- evidence_id: metpo-ontology
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/8fddadb3fbd79058e22fbd519e36ab43b3496923/metpo.obo
  accessed_at: '2026-10-21T17:32:40.269737Z'
  snapshot_sha256: 951019bb3917cd48105e4b3e1cc745af697e0d60a50d5292925310d615108b32
  support: supports
  locator: Header and complete stanzas METPO:1000612, METPO:1000601, METPO:1000059,
    METPO:1000608, METPO:1000605; commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
  summary: The complete METPO:1000612 stanza agrees with the target label, definition,
    parent and retained synonym scopes. The sole retained alias Ox_facultative_aerobe_anaerobe
    is RELATED, as in METPO. The defining observation is microbial growth both with
    and without molecular oxygen. It does not specify a preference for either condition,
    a quantitative growth advantage, or a particular respiratory or fermentative pathway.
    The parent concerns organism oxygen requirements or tolerance for growth. Header
    and phenotype ancestry establish microbial phenotype scope. Source annotations
    are citations, not automatically equivalence relations. The pinned OBO is byte-identical
    to current captured main.
- evidence_id: metpo-project
  kind: database
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/README.md
  accessed_at: '2026-10-21T17:32:40.048415Z'
  snapshot_sha256: 3fbbd78aef5c77e8dfa9c09447fed03c26211a52d79382b0ac763482500667f1
  support: supports
  locator: Full README, especially purpose, identifier resolution, versions and licence
  summary: The official project describes microbial ecophysiological traits and phenotypes.
    It specifies the w3id.org/metpo namespace for seven-digit terms and declares CC-BY
    4.0. Ontology-body resolution was inspected; universal term-page redirect behavior
    was not tested.
- evidence_id: metpo-license
  kind: authority
  reference: https://raw.githubusercontent.com/berkeleybop/metpo/main/LICENSE
  accessed_at: '2026-10-21T17:32:40.048590Z'
  snapshot_sha256: 9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411
  support: supports
  locator: Licence title and public-licence identification
  summary: The official licence text identifies Creative Commons Attribution 4.0 International,
    consistent with the ontology header, README and local record. This does not independently
    audit every upstream source licence.
- evidence_id: metpo-commit
  kind: database
  reference: https://api.github.com/repos/berkeleybop/metpo/commits?path=metpo.obo&per_page=1
  accessed_at: '2026-10-21T17:32:40.100881Z'
  snapshot_sha256: cb72f320df01d1039edd9d170b784ad1f2bd699bedaba0b3176a1d4ed22ccee1
  support: context_only
  locator: Returned commit identity/date and request path; raw equality checked separately
  summary: The path-scoped result identifies commit 8fddadb3fbd79058e22fbd519e36ab43b3496923
    dated 2026-09-03. Its captured raw OBO equals current main despite retaining a
    2026-06-12 header. These current observations do not establish the original seeding
    input bytes.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  locator: Executed 2026-10-21T17:33:18Z through 2026-10-21T17:33:19Z; exit 0
  accessed_at: '2026-10-21T17:33:19Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
    data/traits/function/environmental_response/metpo/facultative-psychrophilic-metpo1000720.yaml
    data/traits/function/environmental_response/metpo/facultatively-acidophilic-metpo1003007.yaml
    data/traits/function/environmental_response/metpo/facultatively-aerobic-metpo1000608.yaml
    data/traits/function/environmental_response/metpo/facultatively-alkaliphilic-metpo1003005.yaml
    data/traits/function/environmental_response/metpo/facultatively-anaerobic-metpo1000605.yaml
    data/traits/function/environmental_response/metpo/haloalkaliphilic-metpo1000621.yaml
    data/traits/function/environmental_response/metpo/halophilic-metpo1000620.yaml
    data/traits/function/environmental_response/metpo/halophily-preference-metpo1000629.yaml
    data/traits/function/environmental_response/metpo/halotolerant-metpo1000622.yaml
  locator: Executed 2026-10-21T17:34:00Z through 2026-10-21T17:35:12Z; exit 0
  accessed_at: '2026-10-21T17:35:12Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/environmental_response/metpo/facultative-oxygen-preference-metpo1000612.yaml
  locator: Executed 2026-10-21T17:33:19Z through 2026-10-21T17:33:19Z; exit 0
  accessed_at: '2026-10-21T17:33:19Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T17:35:12Z through 2026-10-21T17:35:13Z; exit 0
  accessed_at: '2026-10-21T17:35:13Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  topic: Maintained OBO route and grouping boundary
  summary: The reviewed leaf is emitted through the oxygen preference route in seed_obo.py.
    The phenotype grouping uses a separate maintained helper. Any future eligibility
    correction needs a route decision and an audited disposition of the existing record
    and references.
  evidence_ids:
  - owner
  - registry
  - grouping-owner
  - browser-source
  target_ids:
  - METPO:1000612
  assessment_id: assessment-1
- area: identity
  outcome: supported
  topic: Exact source phenotype identity
  summary: METPO:1000612 resolves to facultative oxygen preference in the current
    official ontology. Full local name, definition, parent and synonym scopes agree.
    Correct microbial source identity is distinguishable from eligibility for the
    protein-trait domain.
  evidence_ids:
  - record
  - metpo-ontology
  - metpo-project
  target_ids:
  - METPO:1000612
  assessment_id: assessment-2
- area: evidence
  outcome: supported
  topic: Source-defined growth semantics
  summary: The defining observation is microbial growth both with and without molecular
    oxygen. It does not specify a preference for either condition, a quantitative
    growth advantage, or a particular respiratory or fermentative pathway. This assessment
    establishes authentic source denotation, not independent experimental validation
    of all physiological criteria.
  evidence_ids:
  - record
  - metpo-ontology
  target_ids:
  - METPO:1000612
  assessment_id: assessment-3
- area: evidence
  outcome: unknown
  topic: Independent definition-source scope
  summary: OMP:0000087 supports the organism-level facultative context and calls facultative
    aerobe an exact synonym of its facultative anaerobe class. That source describes
    metabolic use of oxygen when available. METPO:1000612 is phrased more generally
    as growth under either condition; its exact meaning must not be silently strengthened
    to a quantitative respiratory preference.
  evidence_ids:
  - record
  - metpo-ontology
  - facultative-context
  target_ids:
  - METPO:1000612
  assessment_id: assessment-4
- area: consistency
  outcome: supported
  topic: Local hierarchy and lexical fidelity
  summary: The parent concerns organism oxygen requirements or tolerance for growth.
    The sole retained alias Ox_facultative_aerobe_anaerobe is RELATED, as in METPO.
    The recursive local ancestors resolve and the phenotype grouping ends at the maintained
    scope boundary. No separate broken-parent finding is established.
  evidence_ids:
  - record
  - metpo-ontology
  - owner
  - grouping-owner
  - local-ancestor-1
  - local-ancestor-2
  target_ids:
  - METPO:1000612
  assessment_id: assessment-5
- area: representation
  outcome: concern
  topic: Organism growth versus protein capability
  summary: Growth under both oxygen conditions is a property of the microorganism.
    It does not define oxygen-independent catalysis, protein oxygen sensing or a particular
    protein induction response. The source-to-category route preserves organism denotation
    rather than defining a distinct protein response.
  evidence_ids:
  - record
  - schema
  - project-contract
  - owner
  - metpo-ontology
  target_ids:
  - METPO:1000612
  assessment_id: assessment-6
- area: grounding
  outcome: supported
  topic: Retained source identifier without identity transfer
  summary: The METPO identifier denotes the reviewed organism phenotype correctly.
    No equivalence xref is present. A future protein-level class must not silently
    take METPO:1000612 with changed meaning; any relationship between that class and
    the organism phenotype needs its own scoped justification.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  target_ids:
  - METPO:1000612
  assessment_id: assessment-7
- area: provenance
  outcome: unknown
  topic: Current source agreement and historical release limit
  summary: The present OBO, pinned commit, header date, source registry, licence and
    target fields agree at the stated scope. The original seed snapshot and input
    sidecar were not recovered, so the header date is not proof of original-release
    bytes.
  evidence_ids:
  - record
  - owner
  - registry
  - metpo-ontology
  - metpo-project
  - metpo-license
  - metpo-commit
  target_ids:
  - METPO:1000612
  assessment_id: assessment-8
- area: completeness
  outcome: concern
  topic: Protein-class eligibility precedes optional enrichment
  summary: The organism phenotype has a reusable class identity. Its eligibility as
    a protein trait remains the material gap. No mandatory protein exemplar, sequence,
    structure or causal graph is inferred from optional fields, and adding an example
    would not itself change the class denotation.
  evidence_ids:
  - record
  - schema
  - project-contract
  - metpo-ontology
  target_ids:
  - METPO:1000612
  assessment_id: assessment-9
- area: graph
  outcome: not_applicable
  topic: No asserted mechanism graph
  summary: The full target has no causal graph. Native graph checks do not supply
    a molecular mechanism.
  evidence_ids:
  - record
  target_ids:
  - METPO:1000612
  assessment_id: assessment-10
- area: scope
  outcome: concern
  topic: Preserve organism-level qualifiers
  summary: The captured external METPO stanzas METPO:1000612, METPO:1000608 and METPO:1000605
    have overlapping growth definitions but distinct identifiers and annotations.
    Neither that overlap nor the OMP synonym proves a deterministic merge or a strict
    physiological distinction among those METPO classes. No protein instance is qualified
    and the SEEDED status is unchanged.
  evidence_ids:
  - record
  - schema
  - metpo-ontology
  - facultative-context
  target_ids:
  - METPO:1000612
  assessment_id: assessment-11
findings:
- issue_key: metpo.environmental-response.METPO-1000612.organism-growth-as-protein-trait
  category: scope
  severity: major
  certainty: confirmed
  title: Organism growth phenotype is represented as a protein trait
  description: The definition of METPO:1000612 concerns organism growth. Growth under
    both oxygen conditions is a property of the microorganism. It does not define
    oxygen-independent catalysis, protein oxygen sensing or a particular protein induction
    response. The maintained route assigns this unchanged denotation to a ProteinTraitRecord
    in FUNC_ENVIRONMENTAL_RESPONSE without a separate protein-level defining predicate.
    The identifier is correctly resolved; the mismatch is the eligibility decision,
    not a wrong source accession.
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
  rule_id: 'ProteinTraitRecord checklist: class identity, defining representation
    and evidence scope'
  normalization_reason: 'Major: the record models an organism phenotype as a protein
    trait. The retained and correctly resolved source identity limits this to domain
    eligibility rather than an identity blocker.'
  finding_id: F1
  status: open
  target_ids:
  - METPO:1000612
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  native_severity: major
actions:
- action_id: A1
  description: Adjudicate METPO:1000612 in the maintained oxygen preference branch
    of scripts/seed_obo.py and document the disposition of this existing record and
    its references. Preserve its source growth qualifiers. If excluded, use an audited
    retirement or migration plan. If evidence supports a separate protein response,
    define that class with its own identity and support and an appropriate explicit
    relationship to the organism phenotype. Do not reinterpret this METPO identifier
    as a protein property.
  finding_ids:
  - F1
  target_ids:
  - METPO:1000612
  owner_paths:
  - path: scripts/seed_obo.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained METPO route selection, OBO parsing, provenance and class-record
      emission
  acceptance_checks:
  - Document the curator-adjudicated protein-domain eligibility and existing-record
    disposition for METPO:1000612, retaining its source organism-phenotype denotation.
  - Exercise the maintained OBO route on a pinned input in dry-run mode and inspect
    the term outcome. If excluded, separately audit old-file retirement or migration
    and references; exclusion from future emission is not removal of existing output.
  - Any distinct protein response class requires its own identity, protein-level definition
    and scoped support. Do not reassign the METPO phenotype identifier or infer equivalence
    merely from association. Optional examples follow the existing reviewed qualification
    workflow.
  - For a future generator change run just lint, focused pytest, just test and just
    audit-writers. For resulting paths after an authorized disposition run just validate
    <resulting-path>, just validate-all <resulting-path> and just audit-graphs <resulting-path>;
    run full just validate-all before merge and just validate-history for the full
    history tree. Record a fresh immutable review of the actual corrected outcome.
limitations:
- The captured external METPO stanzas METPO:1000612, METPO:1000608 and METPO:1000605
  have overlapping growth definitions but distinct identifiers and annotations. Neither
  that overlap nor the OMP synonym proves a deterministic merge or a strict physiological
  distinction among those METPO classes.
- Source ontology definitions and selected cited ontology objects were inspected,
  not strain-specific growth experiments or protein activity data. Definition-source
  annotations are not assumed equivalence assertions; the entire upstream citation
  network was not validated.
- The complete source stanzas and current header agree with the target; main and commit-pinned
  bytes match. The original seeding input and historical run remain unestablished.
- This review covers the named record with captured local ancestors and external ontology
  context. It neither certifies nor rejects the full route. iModulonDB does not apply
  without a specified gene, organism/dataset or expression component.
- Actual source bodies, access UTC, URLs and SHA256 are retained in scratch. No protein
  example, native review status or curation-history event is promoted by these scientific
  observations.
tags:
- unreviewed-path-order
- batch-039
- metpo
```
