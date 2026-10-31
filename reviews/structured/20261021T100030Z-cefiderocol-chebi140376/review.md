# Review of requires cefiderocol

- Review: 20261021T100030Z-cefiderocol-chebi140376
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:51:50Z
- Finished UTC: 2026-10-21T10:00:30Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

One confirmed major grounding finding: CHEBI:140376 is a chemical entity, not equivalent to the proposed cefiderocol requirement class. Cefiderocol’s source siderophore role and antibiotic/transport biology do not yet qualify a protein activity requirement; that scope must be adjudicated before a typed role repair.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 4 in batch 013. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0) covers 118 record paths, leaving 429241 before this batch. 13 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml | generated | requires cefiderocol |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_140376 | CHEBI:140376 resolves and is nonobsolete in OLS. Its source definition, structure, aliases, outgoing structural parents and cited role/comparison identities were inspected; the captured local parent was read. Successful reference resolution does not certify chemical-to-trait equivalence or a protein requirement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

The local class denotes a proposed reusable requirement for cefiderocol; CHEBI:140376 identifies its chemical target. The chemical identifier and label resolve coherently, while chemical identity and a requirement class have different denotations.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

Official licensing supports the chemical-source CC BY 4.0 statement. The requirement wrapper is generated locally, not a ChEBI assertion about a protein class. The inspected source role path explains candidate selection without establishing a qualified protein requirement.

### Biological requirement and chemical-state evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

CHEBI:140376 identifies C30H34ClN7O10S2 cefiderocol with net charge 0. The encoded zwitterion contains a permanent pyrrolidinium cation and a carboxylate, as well as a separate carboxylic acid group. Its IUPAC name specifies (6R,7R) configuration and (2Z) oxime geometry. The lengthy appended definition agrees with those substituents; S-649266 and GSK-2696266 are source synonyms. The response identifies the antibiotic molecule, not an iron-chelated complex, formulation, salt or every protonation state.

### Chemical-role and protein-trait hierarchy

consistency: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

The direct siderophore role and source siderophore-to-cofactor hierarchy explain the candidate parent. The drug role and iron-transport experiments do not refute that ontology assertion, but also do not establish a required activity cofactor. The source role definition’s microbial-production wording is not evidence that this antibiotic was produced by a microorganism. No additional protein parent is inferred from chemical structural taxonomy, and this review does not certify the parent record.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

CHEBI:140376 in xrefs identifies a chemical entity while the local trait identifies a functional requirement. The schema restricts xrefs to true own-source equivalence and provides typed chemical_participants for chemical associations. Correct chemical resolution does not make these classes equivalent.

### Biological requirement and chemical-state evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

The complete primary abstract describes cefiderocol as a catechol-containing siderophore cephalosporin, reports affinity mainly for PBP3, and shows increased MICs in specified iron-transporter-deficient bacteria. These experiments support antibiotic and transport context. They do not establish cefiderocol as a required activity cofactor, and they do not prove that an additional qualifying role is impossible. No protein example is qualified or promoted.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_140376.

A cefiderocol requirement for protein activity remains independently unresolved. The inspected evidence establishes antibiotic/transport roles and a source siderophore-to-cofactor candidate path. It neither demonstrates the required-cofactor predicate nor excludes all possible qualifying contexts. Before a typed COFACTOR assertion is accepted, a curator must adjudicate whether the candidate class is retained with appropriate evidence or represented differently.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-140376.chemical-entity-equivalence.

The local requires-cefiderocol class denotes a protein requirement, while CHEBI:140376 denotes the stereochemically specified cefiderocol zwitterion. The xrefs slot asserts true own-source equivalence, so the generated link equates different kinds of entity. This is a grounding defect even when the chemical name resolves correctly; it does not by itself prove the proposed requirement impossible.

## Recommended Actions And Acceptance Checks

### A1

Correct build() in scripts/seed_chebi_cofactor.py to separate chemical identity from the proposed protein-requirement class and remove the false xrefs equivalence. Preserve the exact cefiderocol identity and source siderophore/antibiotic provenance while adjudicating the candidate’s required-cofactor scope. If the requirement class is retained with appropriate evidence, represent CHEBI:140376 through chemical_participants with role COFACTOR; do not assign that role solely from antibiotic binding/transport or imply the iron complex is the same exact chemical. If another representation is selected, document the evidence and maintain the chemical-versus-trait distinction rather than silently reclassifying the candidate.

- CHEBI:140376 is no longer asserted equivalent to a protein requirement class. The exact zwitterionic chemical identity and stereochemistry remain traceable; no unreviewed iron complex or protonation-state replacement is introduced.
- The curator explicitly adjudicates required-cofactor scope before accepting a COFACTOR participant. A retained candidate distinguishes source role context from evidence of protein activity dependence; antibacterial or transport activity is not presented as proof of either dependence or its impossibility.
- The maintained emitter is corrected and the chosen representation is regenerated and independently reviewed; no optional protein example is promoted without its own qualification.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml. These are future acceptance checks, not evidence that the present scientific finding is fixed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Run the full-corpus just validate-all before merging record changes and save a fresh structured scientific review against the changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The official Introduction defines the database scope as chemical entities, including atoms, ions and molecular classes; Licensing states that website data are CC BY 4.0. This supports the chemical-source licence, not a source assertion of the generated protein-requirement class. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | OLS metadata reports ChEBI version 256 loaded 2026-10-16. This is the OLS comparison release, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_140376; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:140376 to nonobsolete cefiderocol. Its actual label, description and synonyms were inspected. The term denotes a chemical entity, not a protein requirement class. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/140376/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The complete official response supplies chemical name, definition, charge, structure, aliases and outgoing relations. The chemical directly has siderophore and antibacterial-drug roles. Siderophore is-a cofactor in the source role ontology; this inherited chemical classification is not itself a demonstrated protein requirement for cefiderocol. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and outgoing relations | supports | The source cofactor role concerns an organic molecule or ion required by an enzyme and is-a biochemical role CHEBI:52206. A role assertion does not by itself qualify a particular protein requirement. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23066/; name, definition, chemical_data, default_structure and outgoing relations | supports | Official structural parent CHEBI:23066 resolves; its actual name, definition, chemical data and outgoing relations were inspected. This is chemical taxonomy, not an asserted parent of the protein-requirement trait. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/33575/; name, definition, chemical_data, default_structure and outgoing relations | supports | Official structural parent CHEBI:33575 resolves; its actual name, definition, chemical data and outgoing relations were inspected. This is chemical taxonomy, not an asserted parent of the protein-requirement trait. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; definition and outgoing relations | supports | The siderophore definition describes low-mass iron(III)-chelating compounds produced by microorganisms for iron transport and sequestration. Its outgoing source hierarchy includes iron(3+) chelator, iron ionophore and cofactor. This supplies the imported role path, not a protein activity requirement. |
| drug-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/36047/; name, definition and outgoing relations | supports | The asserted antibacterial-drug role means a drug used to treat or prevent bacterial infection. It supplies the antibiotic role context and does not logically exclude other roles. |
| primary-context | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:29061741%20AND%20SRC:MED&amp;format=json&amp;resultType=core; PMID29061741; complete indexed primary abstract | supports | The complete primary abstract describes cefiderocol as a catechol-containing siderophore cephalosporin, reports affinity mainly for PBP3, and shows increased MICs in specified iron-transporter-deficient bacteria. These experiments support antibiotic and transport context. They do not establish cefiderocol as a required activity cofactor, and they do not prove that an additional qualifying role is impossible. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml; Executed 2026-10-21T09:54:13Z through 2026-10-21T09:54:14Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/carboxymycobactin-chebi62579.yaml data/traits/function/cofactor_requirement/chebi/carotene-chebi17579.yaml data/traits/function/cofactor_requirement/chebi/ce-chebi33369.yaml data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml data/traits/function/cofactor_requirement/chebi/cerium-3-chebi48782.yaml data/traits/function/cofactor_requirement/chebi/cgmp-chebi16356.yaml data/traits/function/cofactor_requirement/chebi/chloride-chebi17996.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-1-chebi58416.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-a-chebi18230.yaml data/traits/function/cofactor_requirement/chebi/chlorophyll-b-1-chebi61721.yaml; Executed 2026-10-21T09:52:28Z through 2026-10-21T09:53:58Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml; Executed 2026-10-21T09:54:14Z through 2026-10-21T09:54:14Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:53:58Z through 2026-10-21T09:54:00Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- PMID29061741 was inspected at complete indexed-abstract level, not full-paper level; its observations are used only within the stated experimental scope.
- No physiological-pH predominance, universal isoform/ion interchangeability or exact protein-bound state is inferred from a chemical name or source role. External chemical comparisons do not authorize a local sibling-record change.
- The source’s fourth-generation antibiotic wording is retained as its description; no clinical efficacy, treatment guidance, microbial biosynthetic origin or classification beyond that source wording is independently asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T100030Z-cefiderocol-chebi140376
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires cefiderocol
started_at: '2026-10-21T09:51:50Z'
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
summary: 'One confirmed major grounding finding: CHEBI:140376 is a chemical entity,
  not equivalent to the proposed cefiderocol requirement class. Cefiderocol’s source
  siderophore role and antibiotic/transport biology do not yet qualify a protein activity
  requirement; that scope must be adjudicated before a typed role repair.'
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
  - path: data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
    sha256: ab326a2f38ff6cbaa4bb3961d41fb7846d60ab6114c4f81fef8177c254fd5316
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
    sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
    role: context
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
  selection: Path-order position 4 in batch 013. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
targets:
- kind: generated
  label: requires cefiderocol
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_140376
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:140376 resolves and is nonobsolete in OLS. Its source definition,
    structure, aliases, outgoing structural parents and cited role/comparison identities
    were inspected; the captured local parent was read. Successful reference resolution
    does not certify chemical-to-trait equivalence or a protein requirement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - primary-context
  - chemical-parent-1
  - chemical-parent-2
  - siderophore-role
  - drug-role
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:51:50Z'
  snapshot_sha256: ab326a2f38ff6cbaa4bb3961d41fb7846d60ab6114c4f81fef8177c254fd5316
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
  accessed_at: '2026-10-21T09:51:50Z'
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
  accessed_at: '2026-10-21T09:51:50Z'
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
  accessed_at: '2026-10-21T09:51:50Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:51:50Z'
  snapshot_sha256: 175820a0774cc2ae713276150391b45b77c215ad3c0f31dcf2bea11969dcd51a
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
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_140376
  accessed_at: '2026-10-21T09:54:41.065575Z'
  snapshot_sha256: fd76dba3da821bdf57507ece2a9c85c3212927986e7b879c3dad9abe718fe2a9
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:140376 to nonobsolete cefiderocol. Its actual label,
    description and synonyms were inspected. The term denotes a chemical entity, not
    a protein requirement class.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/140376/
  accessed_at: '2026-10-21T09:54:29.365556Z'
  snapshot_sha256: 9a4a38a6766aadc391509a5a19033afc7330c96e7f051dc496ab988bcd1168ab
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The complete official response supplies chemical name, definition, charge,
    structure, aliases and outgoing relations. The chemical directly has siderophore
    and antibacterial-drug roles. Siderophore is-a cofactor in the source role ontology;
    this inherited chemical classification is not itself a demonstrated protein requirement
    for cefiderocol.
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
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23066/
  accessed_at: '2026-10-21T09:55:02.716091Z'
  snapshot_sha256: 02dc884ec0222bf1da71043038c76aca1b8a0cffe5bd023b0416a385d88ffc13
  support: supports
  locator: name, definition, chemical_data, default_structure and outgoing relations
  summary: Official structural parent CHEBI:23066 resolves; its actual name, definition,
    chemical data and outgoing relations were inspected. This is chemical taxonomy,
    not an asserted parent of the protein-requirement trait.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/33575/
  accessed_at: '2026-10-21T09:55:02.803773Z'
  snapshot_sha256: 9b58b6cb26cf8e9081f714b8be69a4d3c28833fc84bb4d84478d72d73e9a7097
  support: supports
  locator: name, definition, chemical_data, default_structure and outgoing relations
  summary: Official structural parent CHEBI:33575 resolves; its actual name, definition,
    chemical data and outgoing relations were inspected. This is chemical taxonomy,
    not an asserted parent of the protein-requirement trait.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T09:02:57.586907Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: definition and outgoing relations
  summary: The siderophore definition describes low-mass iron(III)-chelating compounds
    produced by microorganisms for iron transport and sequestration. Its outgoing
    source hierarchy includes iron(3+) chelator, iron ionophore and cofactor. This
    supplies the imported role path, not a protein activity requirement.
- evidence_id: drug-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/36047/
  accessed_at: '2026-10-21T09:56:12.641871Z'
  snapshot_sha256: cd02b5e95a759d9be8d1b3a51657d5d536a2f53d43647448b69caf4de6bd737f
  support: supports
  locator: name, definition and outgoing relations
  summary: The asserted antibacterial-drug role means a drug used to treat or prevent
    bacterial infection. It supplies the antibiotic role context and does not logically
    exclude other roles.
- evidence_id: primary-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:29061741%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T09:55:03.473730Z'
  snapshot_sha256: 9506c787ad384d1756b21257f0b7192abe0c0f66a8b8c797a80afdb9bd0eb8c6
  support: supports
  locator: PMID29061741; complete indexed primary abstract
  summary: The complete primary abstract describes cefiderocol as a catechol-containing
    siderophore cephalosporin, reports affinity mainly for PBP3, and shows increased
    MICs in specified iron-transporter-deficient bacteria. These experiments support
    antibiotic and transport context. They do not establish cefiderocol as a required
    activity cofactor, and they do not prove that an additional qualifying role is
    impossible.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  locator: Executed 2026-10-21T09:54:13Z through 2026-10-21T09:54:14Z; exit 0
  accessed_at: '2026-10-21T09:54:14Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml
  locator: Executed 2026-10-21T09:54:14Z through 2026-10-21T09:54:14Z; exit 0
  accessed_at: '2026-10-21T09:54:14Z'
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
  summary: scripts/seed_chebi_cofactor.py owns generated target changes. Its source
    transformation is inspected; no emitted record has been edited.
  evidence_ids:
  - owner
  - registry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The local class denotes a proposed reusable requirement for cefiderocol;
    CHEBI:140376 identifies its chemical target. The chemical identifier and label
    resolve coherently, while chemical identity and a requirement class have different
    denotations.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: Official licensing supports the chemical-source CC BY 4.0 statement. The
    requirement wrapper is generated locally, not a ChEBI assertion about a protein
    class. The inspected source role path explains candidate selection without establishing
    a qualified protein requirement.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: evidence
  outcome: supported
  summary: CHEBI:140376 identifies C30H34ClN7O10S2 cefiderocol with net charge 0.
    The encoded zwitterion contains a permanent pyrrolidinium cation and a carboxylate,
    as well as a separate carboxylic acid group. Its IUPAC name specifies (6R,7R)
    configuration and (2Z) oxime geometry. The lengthy appended definition agrees
    with those substituents; S-649266 and GSK-2696266 are source synonyms. The response
    identifies the antibiotic molecule, not an iron-chelated complex, formulation,
    salt or every protonation state.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - chemical-parent-1
  - chemical-parent-2
  - siderophore-role
  - drug-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-7
  topic: Biological requirement and chemical-state evidence
- area: consistency
  outcome: unknown
  summary: The direct siderophore role and source siderophore-to-cofactor hierarchy
    explain the candidate parent. The drug role and iron-transport experiments do
    not refute that ontology assertion, but also do not establish a required activity
    cofactor. The source role definition’s microbial-production wording is not evidence
    that this antibiotic was produced by a microorganism. No additional protein parent
    is inferred from chemical structural taxonomy, and this review does not certify
    the parent record.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - cofactor-role
  - siderophore-role
  - drug-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-8
  topic: Chemical-role and protein-trait hierarchy
- area: grounding
  outcome: concern
  summary: CHEBI:140376 in xrefs identifies a chemical entity while the local trait
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-9
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: The complete primary abstract describes cefiderocol as a catechol-containing
    siderophore cephalosporin, reports affinity mainly for PBP3, and shows increased
    MICs in specified iron-transporter-deficient bacteria. These experiments support
    antibiotic and transport context. They do not establish cefiderocol as a required
    activity cofactor, and they do not prove that an additional qualifying role is
    impossible. No protein example is qualified or promoted.
  evidence_ids:
  - primary-context
  - chemical-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-10
  topic: Biological requirement and chemical-state evidence
- area: representation
  outcome: unknown
  summary: A cefiderocol requirement for protein activity remains independently unresolved.
    The inspected evidence establishes antibiotic/transport roles and a source siderophore-to-cofactor
    candidate path. It neither demonstrates the required-cofactor predicate nor excludes
    all possible qualifying contexts. Before a typed COFACTOR assertion is accepted,
    a curator must adjudicate whether the candidate class is retained with appropriate
    evidence or represented differently.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - owner
  - primary-context
  - siderophore-role
  - drug-role
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-140376.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-cefiderocol class denotes a protein requirement,
    while CHEBI:140376 denotes the stereochemically specified cefiderocol zwitterion.
    The xrefs slot asserts true own-source equivalence, so the generated link equates
    different kinds of entity. This is a grounding defect even when the chemical name
    resolves correctly; it does not by itself prove the proposed requirement impossible.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build() in scripts/seed_chebi_cofactor.py to separate chemical
    identity from the proposed protein-requirement class and remove the false xrefs
    equivalence. Preserve the exact cefiderocol identity and source siderophore/antibiotic
    provenance while adjudicating the candidate’s required-cofactor scope. If the
    requirement class is retained with appropriate evidence, represent CHEBI:140376
    through chemical_participants with role COFACTOR; do not assign that role solely
    from antibiotic binding/transport or imply the iron complex is the same exact
    chemical. If another representation is selected, document the evidence and maintain
    the chemical-versus-trait distinction rather than silently reclassifying the candidate.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_140376
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - CHEBI:140376 is no longer asserted equivalent to a protein requirement class.
    The exact zwitterionic chemical identity and stereochemistry remain traceable;
    no unreviewed iron complex or protonation-state replacement is introduced.
  - The curator explicitly adjudicates required-cofactor scope before accepting a
    COFACTOR participant. A retained candidate distinguishes source role context from
    evidence of protein activity dependence; antibacterial or transport activity is
    not presented as proof of either dependence or its impossibility.
  - The maintained emitter is corrected and the chosen representation is regenerated
    and independently reviewed; no optional protein example is promoted without its
    own qualification.
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/cefiderocol-chebi140376.yaml.
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
- PMID29061741 was inspected at complete indexed-abstract level, not full-paper level;
  its observations are used only within the stated experimental scope.
- No physiological-pH predominance, universal isoform/ion interchangeability or exact
  protein-bound state is inferred from a chemical name or source role. External chemical
  comparisons do not authorize a local sibling-record change.
- The source’s fourth-generation antibiotic wording is retained as its description;
  no clinical efficacy, treatment guidance, microbial biosynthetic origin or classification
  beyond that source wording is independently asserted.
tags:
- unreviewed-path-order
- batch-013
- chebi-cofactor
```
