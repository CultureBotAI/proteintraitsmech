# Review of requires Ce

- Review: 20261021T100030Z-ce-chebi33369
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:51:49Z
- Finished UTC: 2026-10-21T10:00:30Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

One confirmed major grounding finding: CHEBI:33369 is a chemical entity, not equivalent to the proposed Ce requirement class. Neutral-atom versus elemental/ionic requirement scope remains explicitly unresolved and must be adjudicated before a typed role repair.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 013. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0) covers 118 record paths, leaving 429241 before this batch. 13 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml | generated | requires Ce |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_33369 | CHEBI:33369 resolves and is nonobsolete in OLS. Its source definition, structure, aliases, outgoing structural parents and cited role/comparison identities were inspected; the captured local parent was read. The alignment script and local crosswalk were also inspected; original upstream tables remain unverified. Successful reference resolution does not certify chemical-to-trait equivalence or a protein requirement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The primary maintained emitter is seed_cofactor_alignment.py with imported ChEBI helper utilities. The alignment script and crosswalk were captured and fully read. Local provenance is clear, while the original upstream MicroGrowAgents table/release remains independently unverified.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The local class denotes a proposed reusable requirement for Ce; CHEBI:33369 identifies its chemical target. The chemical identifier and label resolve coherently, while chemical identity and a requirement class have different denotations.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

Official licensing supports the chemical-source CC BY 4.0 statement. The requirement wrapper is generated locally, not a ChEBI assertion about a protein class. The captured crosswalk supports local MicroGrowAgents alignment provenance, not independent upstream-release verification.

### Biological requirement and chemical-state evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

CHEBI:33369 resolves to cerium atom, formula Ce, charge 0 and structure [Ce]. Ce and cerium are source names, so the local short label is not an unrelated-name error. The backend chemical definition is empty and OLS description is empty. Its outgoing relations classify a lanthanoid atom and an f-block element atom; no has-role relation occurs in this captured response. CHEBI:48782 separately denotes Ce3+, not an exact synonym, conjugate or automatic replacement for this atom.

### Chemical-role and protein-trait hierarchy

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The local root cofactor-requirement parent comes from the alignment emitter rather than a ChEBI has-role path for this neutral atom. The parent resolves, but whether the intended requirement is elemental nutrition or a specific ionic activity cofactor remains unresolved. No additional protein parent is inferred from chemical structural taxonomy, and this review does not certify the parent record.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

CHEBI:33369 in xrefs identifies a chemical entity while the local trait identifies a functional requirement. The schema restricts xrefs to true own-source equivalence and provides typed chemical_participants for chemical associations. Correct chemical resolution does not make these classes equivalent.

### Biological requirement and chemical-state evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

The complete primary abstract reports lanthanide-dependent growth of Methylacidiphilum fumariolicum SolV, naming cerium among several lanthanides, and a lanthanide cofactor in its homodimeric methanol dehydrogenase. It does not specify the oxidation state in the abstract, demonstrate neutral-atom incorporation, or establish an exclusive requirement for cerium over other listed lanthanides. No protein example is qualified or promoted.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_33369.

A specific physiological requirement for neutral Ce atoms is not established. The aligned short name may be intended as elemental shorthand, while its chemical anchor is charge-specific; the available primary abstract supports a lanthanide context without specifying neutral atoms or cerium-exclusive dependence. This unresolved scope is an acceptance dependency of the grounding repair, not a confirmed wrong-ID finding or justification for an automatic Ce3+ substitution.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-33369.chemical-entity-equivalence.

The local requires-Ce class denotes a protein requirement, while CHEBI:33369 denotes a neutral cerium atom. The xrefs slot asserts true own-source equivalence, so the generated link equates different kinds of entity. This is a grounding defect even when the chemical name resolves correctly; it does not by itself prove the proposed requirement impossible.

## Recommended Actions And Acceptance Checks

### A1

Correct build_aligned() in scripts/seed_cofactor_alignment.py so chemical identity is not emitted as requirement-class equivalence. First resolve the intended elemental versus molecular-state requirement using verified alignment provenance and direct activity evidence. Do not automatically replace CHEBI:33369 with CHEBI:48782, merge their classes, or assign neutral cerium a COFACTOR participant merely because the aligned label says metals. If the resolved candidate is retained, represent its adjudicated chemical identity through chemical_participants with role COFACTOR only where that role is justified, preserving the requirement-versus-chemical distinction. Correct label, definition and provenance consistently if the intended scope changes.

- The intended scope is explicitly adjudicated: a neutral-atom activity requirement, an ionic requirement and an element-level nutritional concept are not silently treated as identical. The chemical target and any COFACTOR role have evidence appropriate to that choice.
- No CHEBI chemical entity remains asserted equivalent to a protein requirement. Any retained chemical association uses the correctly scoped typed participant; a Ce3+ replacement or merge requires its own evidence and review.
- Use a controlled, audited route for this existing aligned target: main selects missing ChEBI IDs, so a plain rerun or --force alone will not regenerate it. Preserve the actual alignment owner, local crosswalk provenance and upstream-release limitations.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml. These are future acceptance checks, not evidence that the present scientific finding is fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Run the full-corpus just validate-all before merging record changes and save a fresh structured scientific review against the changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml; Entire target YAML | supports | Complete target inspected: requires Ce, CHEBI:33369 identifier/xref, generated cofactor (metals) requirement definition, ChEBI with MicroGrowAgents curation attribution, two RELATED_SYNONYM entries cerium and metals, FUNCTION/FUNC_COFACTOR_REQUIREMENT and CLASS/SEEDED status, cofactor-requirement parent and CC BY 4.0 licence. No qualified protein or typed chemical participant is asserted. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| chebi-helper | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | The alignment emitter imports ChEBI loading, identifier, licence and formatting utilities from this helper. Its ordinary has-role selection is not asserted to have emitted the aligned Ce target. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The official Introduction defines the database scope as chemical entities, including atoms, ions and molecular classes; Licensing states that website data are CC BY 4.0. This supports the chemical-source licence, not a source assertion of the generated protein-requirement class. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the OLS comparison release, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_33369; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:33369 to nonobsolete cerium atom. Its actual label, description and synonyms were inspected. The term denotes a chemical entity, not a protein requirement class. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33369/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response supplies chemical name, definition, charge, structure, aliases and outgoing relations. The inspected outgoing relations contain only structural atom parents. The local cofactor candidate comes from the MicroGrowAgents alignment, not an inspected ChEBI cofactor-role assertion for the neutral atom. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing relations | supports | The source cofactor role concerns an organic molecule or ion required by an enzyme and is-a biochemical role CHEBI:52206. A role assertion does not by itself qualify a particular protein requirement. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33319/; name, definition, chemical_data, default_structure and outgoing relations | supports | Official structural parent CHEBI:33319 resolves; its actual name, definition, chemical data and outgoing relations were inspected. This is chemical taxonomy, not an asserted parent of the protein-requirement trait. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33562/; name, definition, chemical_data, default_structure and outgoing relations | supports | Official structural parent CHEBI:33562 resolves; its actual name, definition, chemical data and outgoing relations were inspected. This is chemical taxonomy, not an asserted parent of the protein-requirement trait. |
| state-comparison | https://www.ebi.ac.uk/chebi/backend/api/public/compound/48782/; name, definition, chemical_data, default_structure and outgoing relations | supports | The external chemical comparison separately resolves cerium(3+) with charge +3, [Ce+3] structure and direct cofactor role. It is not evidence of equivalent protein traits or authority to replace, merge or regenerate a different local record. |
| primary-context | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24034209%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID24034209; complete indexed primary abstract | supports | The complete primary abstract reports lanthanide-dependent growth of Methylacidiphilum fumariolicum SolV, naming cerium among several lanthanides, and a lanthanide cofactor in its homodimeric methanol dehydrogenase. It does not specify the oxidation state in the abstract, demonstrate neutral-atom incorporation, or establish an exclusive requirement for cerium over other listed lanthanides. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned and main | supports | load_mg_cofactors loads curated names/categories by ChEBI ID; build_aligned emits the requirement label/definition, root cofactor parent, RELATED_SYNONYMs and chemical xref, using imported ChEBI utilities. main selects only IDs absent from existing records; --force alone does not select this already existing target for regeneration. |
| crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and CHEBI:33369 row136 | supports | Captured row136 maps CHEBI:33369 to the local requirement identifier, name Ce, MicroGrowAgents cofactor_id cerium and category metals. This corroborates local alignment provenance; it does not independently establish the original upstream table or release. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml; Executed 2026-10-21T09:54:12Z through 2026-10-21T09:54:13Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml; Executed 2026-10-21T09:52:28Z through 2026-10-21T09:53:58Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml; Executed 2026-10-21T09:54:13Z through 2026-10-21T09:54:13Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:53:58Z through 2026-10-21T09:54:00Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The Ce candidate is alignment-derived; the current neutral-atom response does not assert cofactor role. That bounded absence is not proof that no qualifying context can exist. The original MicroGrowAgents table/release and intended elemental-versus-molecular scope remain independently unverified.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMID24034209 was inspected at complete indexed-abstract level, not full-paper level; its observations are used only within the stated experimental scope.
- No physiological-pH predominance, universal isoform/ion interchangeability or exact protein-bound state is inferred from a chemical name or source role. External chemical comparisons do not authorize a local sibling-record change.
- The lanthanide primary abstract does not independently establish Ce3+ oxidation state or neutral-atom use. Chemical charge identity is supplied by structured ChEBI, and no exclusive cerium dependence is claimed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T100030Z-ce-chebi33369
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires Ce
started_at: '2026-10-21T09:51:49Z'
finished_at: '2026-10-21T10:00:30Z'
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
summary: 'One confirmed major grounding finding: CHEBI:33369 is a chemical entity,
  not equivalent to the proposed Ce requirement class. Neutral-atom versus elemental/ionic
  requirement scope remains explicitly unresolved and must be adjudicated before a
  typed role repair.'
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
  - path: data/mappings/cofactor_crosswalk.tsv
    sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
    role: context
  - path: data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
    sha256: dcf68662e796a261f6806cc237096bc97159adf5f6ba1d03df1060cf0bf84ede
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
  - path: scripts/seed_cofactor_alignment.py
    sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 3 in batch 013. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0) covers 118 record paths,
    leaving 429241 before this batch. 13 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
targets:
- kind: generated
  label: requires Ce
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  path: data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_33369
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml
    data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
    data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:33369 resolves and is nonobsolete in OLS. Its source definition,
    structure, aliases, outgoing structural parents and cited role/comparison identities
    were inspected; the captured local parent was read. The alignment script and local
    crosswalk were also inspected; original upstream tables remain unverified. Successful
    reference resolution does not certify chemical-to-trait equivalence or a protein
    requirement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - primary-context
  - chemical-parent-1
  - chemical-parent-2
  - state-comparison
  - owner
  - crosswalk
  - chebi-helper
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: dcf68662e796a261f6806cc237096bc97159adf5f6ba1d03df1060cf0bf84ede
  support: supports
  summary: 'Complete target inspected: requires Ce, CHEBI:33369 identifier/xref, generated
    cofactor (metals) requirement definition, ChEBI with MicroGrowAgents curation
    attribution, two RELATED_SYNONYM entries cerium and metals, FUNCTION/FUNC_COFACTOR_REQUIREMENT
    and CLASS/SEEDED status, cofactor-requirement parent and CC BY 4.0 licence. No
    qualified protein or typed chemical participant is asserted.'
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  support: supports
  summary: FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required
    for activity. xrefs asserts true own-source equivalence; chemical_participants
    represents chemical entities with typed roles. parent_traits asserts a broader
    class. Optional examples and causal graphs are not mandatory class representations.
- evidence_id: chebi-helper
  kind: record_content
  reference: scripts/seed_chebi_cofactor.py
  locator: load_relations, load_names, build, main
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The alignment emitter imports ChEBI loading, identifier, licence and formatting
    utilities from this helper. Its ordinary has-role selection is not asserted to
    have emitted the aligned Ce target.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
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
  summary: The official Introduction defines the database scope as chemical entities,
    including atoms, ions and molecular classes; Licensing states that website data
    are CC BY 4.0. This supports the chemical-source licence, not a source assertion
    of the generated protein-requirement class.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the OLS
    comparison release, not a release assignment for live backend responses or the
    original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_33369
  accessed_at: '2026-10-21T09:54:40.992584Z'
  snapshot_sha256: 6d4515019829ebddd3021109fae00fb0c346a4f7abbfbdf66c431f70343c5c14
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:33369 to nonobsolete cerium atom. Its actual label,
    description and synonyms were inspected. The term denotes a chemical entity, not
    a protein requirement class.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33369/
  accessed_at: '2026-10-21T09:54:29.387490Z'
  snapshot_sha256: a1ea9c8f36a09d9ea8574ec0ac7038e59d144f2dcf48afac6b98d19f87d0f5f1
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The complete official response supplies chemical name, definition, charge,
    structure, aliases and outgoing relations. The inspected outgoing relations contain
    only structural atom parents. The local cofactor candidate comes from the MicroGrowAgents
    alignment, not an inspected ChEBI cofactor-role assertion for the neutral atom.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and outgoing relations
  summary: The source cofactor role concerns an organic molecule or ion required by
    an enzyme and is-a biochemical role CHEBI:52206. A role assertion does not by
    itself qualify a particular protein requirement.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33319/
  accessed_at: '2026-10-21T09:55:02.540245Z'
  snapshot_sha256: dcdb76e4b6843482b687febb7c9b9d39d86bbe25ac53a40a744c9f433467332d
  support: supports
  locator: name, definition, chemical_data, default_structure and outgoing relations
  summary: Official structural parent CHEBI:33319 resolves; its actual name, definition,
    chemical data and outgoing relations were inspected. This is chemical taxonomy,
    not an asserted parent of the protein-requirement trait.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33562/
  accessed_at: '2026-10-21T09:55:02.625748Z'
  snapshot_sha256: 5e91d035a028a4b18c486bfdebfa98fea090498a216b40b8a33ab956967d7679
  support: supports
  locator: name, definition, chemical_data, default_structure and outgoing relations
  summary: Official structural parent CHEBI:33562 resolves; its actual name, definition,
    chemical data and outgoing relations were inspected. This is chemical taxonomy,
    not an asserted parent of the protein-requirement trait.
- evidence_id: state-comparison
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/48782/
  accessed_at: '2026-10-21T09:54:29.445569Z'
  snapshot_sha256: 7e27bc6c017bddfb73e179a1ac4ca526cc1a9c703025a810118f4b0412f66d48
  support: supports
  locator: name, definition, chemical_data, default_structure and outgoing relations
  summary: The external chemical comparison separately resolves cerium(3+) with charge
    +3, [Ce+3] structure and direct cofactor role. It is not evidence of equivalent
    protein traits or authority to replace, merge or regenerate a different local
    record.
- evidence_id: primary-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:24034209%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:55:03.416346Z'
  snapshot_sha256: 00f05f8aecd13de645be4fda406a7d76c68d217fcc548412687be03fbba1c1ee
  support: supports
  locator: PMID24034209; complete indexed primary abstract
  summary: The complete primary abstract reports lanthanide-dependent growth of Methylacidiphilum
    fumariolicum SolV, naming cerium among several lanthanides, and a lanthanide cofactor
    in its homodimeric methanol dehydrogenase. It does not specify the oxidation state
    in the abstract, demonstrate neutral-atom incorporation, or establish an exclusive
    requirement for cerium over other listed lanthanides.
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned and main
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: load_mg_cofactors loads curated names/categories by ChEBI ID; build_aligned
    emits the requirement label/definition, root cofactor parent, RELATED_SYNONYMs
    and chemical xref, using imported ChEBI utilities. main selects only IDs absent
    from existing records; --force alone does not select this already existing target
    for regeneration.
- evidence_id: crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and CHEBI:33369 row136
  accessed_at: '2026-10-21T09:51:49Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: Captured row136 maps CHEBI:33369 to the local requirement identifier, name
    Ce, MicroGrowAgents cofactor_id cerium and category metals. This corroborates
    local alignment provenance; it does not independently establish the original upstream
    table or release.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  locator: Executed 2026-10-21T09:54:12Z through 2026-10-21T09:54:13Z; exit 0
  accessed_at: '2026-10-21T09:54:13Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml
    data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
    data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml
    data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml
    data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml
  locator: Executed 2026-10-21T09:52:28Z through 2026-10-21T09:53:58Z; exit 0
  accessed_at: '2026-10-21T09:53:58Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml
  locator: Executed 2026-10-21T09:54:13Z through 2026-10-21T09:54:13Z; exit 0
  accessed_at: '2026-10-21T09:54:13Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:53:58Z through 2026-10-21T09:54:00Z; exit 0
  accessed_at: '2026-10-21T09:54:00Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: The primary maintained emitter is seed_cofactor_alignment.py with imported
    ChEBI helper utilities. The alignment script and crosswalk were captured and fully
    read. Local provenance is clear, while the original upstream MicroGrowAgents table/release
    remains independently unverified.
  evidence_ids:
  - owner
  - chebi-helper
  - crosswalk
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The local class denotes a proposed reusable requirement for Ce; CHEBI:33369
    identifies its chemical target. The chemical identifier and label resolve coherently,
    while chemical identity and a requirement class have different denotations.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: Official licensing supports the chemical-source CC BY 4.0 statement. The
    requirement wrapper is generated locally, not a ChEBI assertion about a protein
    class. The captured crosswalk supports local MicroGrowAgents alignment provenance,
    not independent upstream-release verification.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  - crosswalk
  - chebi-helper
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: evidence
  outcome: supported
  summary: CHEBI:33369 resolves to cerium atom, formula Ce, charge 0 and structure
    [Ce]. Ce and cerium are source names, so the local short label is not an unrelated-name
    error. The backend chemical definition is empty and OLS description is empty.
    Its outgoing relations classify a lanthanoid atom and an f-block element atom;
    no has-role relation occurs in this captured response. CHEBI:48782 separately
    denotes Ce3+, not an exact synonym, conjugate or automatic replacement for this
    atom.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - chemical-parent-1
  - chemical-parent-2
  - state-comparison
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-7
  topic: Biological requirement and chemical-state evidence
- area: consistency
  outcome: unknown
  summary: The local root cofactor-requirement parent comes from the alignment emitter
    rather than a ChEBI has-role path for this neutral atom. The parent resolves,
    but whether the intended requirement is elemental nutrition or a specific ionic
    activity cofactor remains unresolved. No additional protein parent is inferred
    from chemical structural taxonomy, and this review does not certify the parent
    record.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - cofactor-role
  - state-comparison
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-8
  topic: Chemical-role and protein-trait hierarchy
- area: grounding
  outcome: concern
  summary: CHEBI:33369 in xrefs identifies a chemical entity while the local trait
    identifies a functional requirement. The schema restricts xrefs to true own-source
    equivalence and provides typed chemical_participants for chemical associations.
    Correct chemical resolution does not make these classes equivalent.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-9
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: The complete primary abstract reports lanthanide-dependent growth of Methylacidiphilum
    fumariolicum SolV, naming cerium among several lanthanides, and a lanthanide cofactor
    in its homodimeric methanol dehydrogenase. It does not specify the oxidation state
    in the abstract, demonstrate neutral-atom incorporation, or establish an exclusive
    requirement for cerium over other listed lanthanides. No protein example is qualified
    or promoted.
  evidence_ids:
  - primary-context
  - chemical-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-10
  topic: Biological requirement and chemical-state evidence
- area: representation
  outcome: unknown
  summary: A specific physiological requirement for neutral Ce atoms is not established.
    The aligned short name may be intended as elemental shorthand, while its chemical
    anchor is charge-specific; the available primary abstract supports a lanthanide
    context without specifying neutral atoms or cerium-exclusive dependence. This
    unresolved scope is an acceptance dependency of the grounding repair, not a confirmed
    wrong-ID finding or justification for an automatic Ce3+ substitution.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - owner
  - primary-context
  - state-comparison
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-33369.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-Ce class denotes a protein requirement, while CHEBI:33369
    denotes a neutral cerium atom. The xrefs slot asserts true own-source equivalence,
    so the generated link equates different kinds of entity. This is a grounding defect
    even when the chemical name resolves correctly; it does not by itself prove the
    proposed requirement impossible.
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
  normalization_reason: The emitter encodes equality between a chemical entity and
    a protein-requirement denotation. Repair requires typed chemical association with
    scope adjudication where needed, rather than an alias edit or automatic chemical
    substitution.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build_aligned() in scripts/seed_cofactor_alignment.py so chemical
    identity is not emitted as requirement-class equivalence. First resolve the intended
    elemental versus molecular-state requirement using verified alignment provenance
    and direct activity evidence. Do not automatically replace CHEBI:33369 with CHEBI:48782,
    merge their classes, or assign neutral cerium a COFACTOR participant merely because
    the aligned label says metals. If the resolved candidate is retained, represent
    its adjudicated chemical identity through chemical_participants with role COFACTOR
    only where that role is justified, preserving the requirement-versus-chemical
    distinction. Correct label, definition and provenance consistently if the intended
    scope changes.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_33369
  owner_paths:
  - path: scripts/seed_cofactor_alignment.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained alignment table reader and build_aligned requirement-class emitter
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Imported ChEBI chemical-name/definition and formatting dependency
  acceptance_checks:
  - 'The intended scope is explicitly adjudicated: a neutral-atom activity requirement,
    an ionic requirement and an element-level nutritional concept are not silently
    treated as identical. The chemical target and any COFACTOR role have evidence
    appropriate to that choice.'
  - No CHEBI chemical entity remains asserted equivalent to a protein requirement.
    Any retained chemical association uses the correctly scoped typed participant;
    a Ce3+ replacement or merge requires its own evidence and review.
  - 'Use a controlled, audited route for this existing aligned target: main selects
    missing ChEBI IDs, so a plain rerun or --force alone will not regenerate it. Preserve
    the actual alignment owner, local crosswalk provenance and upstream-release limitations.'
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml.
    These are future acceptance checks, not evidence that the present scientific finding
    is fixed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Run the full-corpus just validate-all
    before merging record changes and save a fresh structured scientific review against
    the changed bytes.
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The Ce candidate is alignment-derived; the current neutral-atom response does not
  assert cofactor role. That bounded absence is not proof that no qualifying context
  can exist. The original MicroGrowAgents table/release and intended elemental-versus-molecular
  scope remain independently unverified.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- PMID24034209 was inspected at complete indexed-abstract level, not full-paper level;
  its observations are used only within the stated experimental scope.
- No physiological-pH predominance, universal isoform/ion interchangeability or exact
  protein-bound state is inferred from a chemical name or source role. External chemical
  comparisons do not authorize a local sibling-record change.
- The lanthanide primary abstract does not independently establish Ce3+ oxidation
  state or neutral-atom use. Chemical charge identity is supplied by structured ChEBI,
  and no exclusive cerium dependence is claimed.
tags:
- unreviewed-path-order
- batch-013
- chebi-cofactor
```
