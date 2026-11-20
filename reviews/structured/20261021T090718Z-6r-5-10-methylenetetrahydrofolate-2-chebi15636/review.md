# Review of requires (6R)-5,10-methylenetetrahydrofolate(2−)

- Review: 20261021T090718Z-6r-5-10-methylenetetrahydrofolate-2-chebi15636
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:01:26Z
- Finished UTC: 2026-10-21T09:07:18Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

(6R)-5,10-methylenetetrahydrofolate(2−) chemical identity, charge, stereochemical scope and source cofactor role are supported. The chemical ID is incorrectly encoded as equivalent to a protein requirement class; one confirmed major grounding finding requires maintained-writer curation.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 010. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618) covers 88 record paths, leaving 429271 before this batch. 10 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml | generated | requires (6R)-5,10-methylenetetrahydrofolate(2−) |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | Full curation-history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_15636 | CHEBI:15636, its source cofactor role, structural parent and conjugate resolve; current OLS reports a nonobsolete target. The local requirement parent was captured and read. The valid chemical reference belongs in typed participant grounding, not true-equivalence xrefs. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The local identifier and requires-label denote a reusable candidate protein requirement for (6R)-5,10-methylenetetrahydrofolate(2−). CHEBI:15636 identifies the named chemical with the specified charge and stereochemistry; it is not itself the protein requirement identifier.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The target CC-BY 4.0 statement agrees with the official source licence. ChEBI supports the chemical description and role, while the functional-requirement sentence is synthesized by the maintained seeder. That sentence is not treated as a verbatim ChEBI chemical definition or as a ChEBI-asserted protein class.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The source structure specifies C20H21N7O6 with charge −2, (6R) stereochemistry and L-glutamate. The two glutamate carboxyl groups are deprotonated. CHEBI:1989 is its separately identified neutral conjugate acid. The official backend definition is null and OLS description is empty, so the generated requirement sentence is not a source chemical definition. The term is the specified methylene-bridged stereoisomer, not methenyl-, methyl- or every polyglutamate folate.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The source directly asserts cofactor role, and the retained local parent denotes the broader cofactor-requirement class. This supports the candidate hierarchy construction without treating chemical has-role as protein is-a or importing the structural chemical parent into the trait hierarchy. The parent record itself is not certified by this review.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

CHEBI:15636 in true-equivalence xrefs denotes the chemical entity, whereas the local trait denotes a functional requirement. The schema provides chemical_participants with the COFACTOR role for the chemical association.

### Representation

representation: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

The FUNCTION requirement label can express a candidate class, but a source chemical role alone does not qualify a protein, determine a bound protonation state or establish physiological obligation. The chemical link must be a typed participant rather than class equivalence.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_15636.

Authoritative folate nomenclature supports retaining the precise C6 descriptor, one-carbon substitution and glutamate scope. The primary SHMT text supplies bounded one-carbon chemistry context; its folinic-acid structure does not prove the target’s bound charge state. Coenzyme/substrate terminology depends on the reaction and does not establish that no protein could require this chemical in a non-substrate cofactor role.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-15636.chemical-entity-equivalence.

The local class denotes the functional requirement for (6R)-5,10-methylenetetrahydrofolate(2−), while CHEBI:15636 denotes the chemical entity. The schema reserves xrefs for true source-direct equivalents, so the emitted association asserts equivalence between different kinds of entity. A correct cofactor-role annotation and exact chemical identity do not remove that semantic mismatch.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to preserve CHEBI:15636 as chemical_participants with role COFACTOR and remove it from trait-equivalence xrefs. Preserve the local requirement identifier, exact charge/stereochemical identity and source-role provenance. Do not substitute a conjugate, move the chemical to parent_traits, or treat this own-source association as an external mapped_xrefs product.

- The regenerated target preserves its requirement-class identity and CHEBI:15636 as the exact chemical participant with role COFACTOR.
- No chemical entity is asserted equivalent to the protein requirement class; charge, stereochemistry and conjugate distinctions remain traceable.
- Protein qualification and obligatory physiological requirement remain separate evidence questions; test the maintained writer and regenerate/validate through the audited route before a fresh review.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The actual Introduction and Licensing sections describe ChEBI as a database of chemical entities and explicitly make its website data available under CC BY 4.0. This supports source scope and the target licence. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The captured official OLS ontology metadata reports ChEBI version 256, loaded 2026-10-16. This is the OLS comparison release, not a release assignment for separately timestamped live ChEBI backend responses or for the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_15636; Inspected source response captured at the recorded UTC time | supports | Official OLS resolves CHEBI:15636 to the nonobsolete (6R)-5,10-methylenetetrahydrofolate(2−) chemical entity. Its label, synonyms and source description were inspected; it does not define a protein requirement class. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15636/; name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations | supports | The full official ChEBI response resolves CHEBI:15636 and supplies its formula, charge, structure, stereochemistry, definition field (null for this entry) and outgoing chemical relations, including a direct cofactor role. These are chemical assertions, not a protein-class equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and ontology_relations.outgoing_relations | supports | The cofactor role is defined as an organic molecule or ion required by an enzyme and is-a CHEBI:52206 biochemical role. A chemical has-role edge is distinct from a subclass relation between protein requirement traits. |
| chemical-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/12071/; name, definition, chemical_data and outgoing relations | supports | The immediate source structural parent was inspected. It categorizes the chemical, not the generated protein requirement class; it is not automatically an additional parent_traits value. |
| conjugate | https://www.ebi.ac.uk/chebi/backend/api/public/compound/1989/; name, chemical_data, default_structure and ontology_relations.outgoing_relations | supports | The official response for CHEBI:1989 confirms the separately identified conjugate chemical, including its charge, structure and reciprocal conjugate relation. This context supports preserving exact IDs, not automatic merging. |
| nomenclature | https://iupac.qmul.ac.uk/misc/folic.html; IUPAC-IUB Recommendations1986, sections2.3–2.8; official web reproduction | supports | The actual IUPAC-IUB nomenclature recommendations distinguish acid/folate names, methylene and methenyl bridges, glutamate-chain scope and stereochemical descriptors. Sections2.6 and2.8 identify (6S)-tetrahydrofolate and (6R)-5,10-methylenetetrahydrofolate as natural stereoisomer examples; R/S labels can change under priority rules without inversion of the underlying C6 configuration. |
| primary-context | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11323337/fullTextXML; PMID39148791; DOI10.1039/d4sc03187c; Abstract, Introduction, Results2.1–2.2 and discussion of ligand identity | supports | The inspected primary SHMT full text describes transfer of a carbon unit from serine to THF to form methylene-THF and calls THF both a coenzyme and a physiological substrate. The neutron structural experiment uses folinic acid, a different THF analogue; its measured proton positions are not transferred to the exact target chemical. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml; Executed 2026-10-21T09:02:03Z through 2026-10-21T09:02:06Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml; Executed 2026-10-21T09:02:02Z through 2026-10-21T09:04:01Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml; Executed 2026-10-21T09:02:06Z through 2026-10-21T09:02:06Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:04:01Z through 2026-10-21T09:04:02Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- No exact protein requirement is qualified from a metabolite role, a reaction-participant role or a paper on another folate. The SHMT neutron structure uses folinic acid, not this target; proton positions, pKa values and substrate/cofactor membership are not transferred.
- The source and target do not assert a physiological-pH dominant species. Exact acid/anion and (6R)/(6S) identities are preserved; no universal interchangeability with conjugates, alternative one-carbon substitutions or polyglutamates is inferred.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T090718Z-6r-5-10-methylenetetrahydrofolate-2-chebi15636
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires (6R)-5,10-methylenetetrahydrofolate(2−)
started_at: '2026-10-21T09:01:26Z'
finished_at: '2026-10-21T09:07:18Z'
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
summary: (6R)-5,10-methylenetetrahydrofolate(2−) chemical identity, charge, stereochemical
  scope and source cofactor role are supported. The chemical ID is incorrectly encoded
  as equivalent to a protein requirement class; one confirmed major grounding finding
  requires maintained-writer curation.
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
  - path: data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
    sha256: d3b98f7514cf27dfebba6704c658ba4272e0a495d139b98dae35db9ac45f86d3
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
  selection: Path-order position 3 in batch 010. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618)
    covers 88 record paths, leaving 429271 before this batch. 10 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
targets:
- kind: generated
  label: requires (6R)-5,10-methylenetetrahydrofolate(2−)
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_15636
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml
    data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml
    data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml
    data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml
    data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: CHEBI:15636, its source cofactor role, structural parent and conjugate
    resolve; current OLS reports a nonobsolete target. The local requirement parent
    was captured and read. The valid chemical reference belongs in typed participant
    grounding, not true-equivalence xrefs.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - chemical-parent
  - conjugate
  - licence
  - release
  - primary-context
  - nomenclature
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:01:26Z'
  snapshot_sha256: d3b98f7514cf27dfebba6704c658ba4272e0a495d139b98dae35db9ac45f86d3
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
  accessed_at: '2026-10-21T09:01:26Z'
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
  accessed_at: '2026-10-21T09:01:26Z'
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
  accessed_at: '2026-10-21T09:01:26Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:01:26Z'
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
  summary: The actual Introduction and Licensing sections describe ChEBI as a database
    of chemical entities and explicitly make its website data available under CC BY
    4.0. This supports source scope and the target licence.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The captured official OLS ontology metadata reports ChEBI version 256,
    loaded 2026-10-16. This is the OLS comparison release, not a release assignment
    for separately timestamped live ChEBI backend responses or for the original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_15636
  accessed_at: '2026-10-21T09:02:33.875241Z'
  snapshot_sha256: 1b9e08d1602b562b09a79fefb522f5e329421ef6307d453e996d7dd5a9dd0c2d
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS resolves CHEBI:15636 to the nonobsolete (6R)-5,10-methylenetetrahydrofolate(2−)
    chemical entity. Its label, synonyms and source description were inspected; it
    does not define a protein requirement class.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15636/
  accessed_at: '2026-10-21T09:02:17.163065Z'
  snapshot_sha256: f06bd1624e9d8e89d7cbfe812389e0706c3906ff6b22ebd579d96cda78f5cdb8
  support: supports
  locator: name, definition, chemical_data, default_structure, names and ontology_relations.outgoing_relations
  summary: The full official ChEBI response resolves CHEBI:15636 and supplies its
    formula, charge, structure, stereochemistry, definition field (null for this entry)
    and outgoing chemical relations, including a direct cofactor role. These are chemical
    assertions, not a protein-class equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and ontology_relations.outgoing_relations
  summary: The cofactor role is defined as an organic molecule or ion required by
    an enzyme and is-a CHEBI:52206 biochemical role. A chemical has-role edge is distinct
    from a subclass relation between protein requirement traits.
- evidence_id: chemical-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/12071/
  accessed_at: '2026-10-21T09:03:20.613934Z'
  snapshot_sha256: ba8a47761841b78cca6d80ebcf0e31f4d4d20198d7b57a8fa6df307710324348
  support: supports
  locator: name, definition, chemical_data and outgoing relations
  summary: The immediate source structural parent was inspected. It categorizes the
    chemical, not the generated protein requirement class; it is not automatically
    an additional parent_traits value.
- evidence_id: conjugate
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/1989/
  accessed_at: '2026-10-21T09:02:17.850281Z'
  snapshot_sha256: 97a7aeede838448ce37a5c1a24b3af144b6ad626e5fb8ebb82fb5961eb1cdb04
  support: supports
  locator: name, chemical_data, default_structure and ontology_relations.outgoing_relations
  summary: The official response for CHEBI:1989 confirms the separately identified
    conjugate chemical, including its charge, structure and reciprocal conjugate relation.
    This context supports preserving exact IDs, not automatic merging.
- evidence_id: nomenclature
  kind: authority
  reference: https://iupac.qmul.ac.uk/misc/folic.html
  accessed_at: '2026-10-21T09:03:21.489703Z'
  snapshot_sha256: e6f08c4f2dc3dc3cc25691b0d2496973f81ddfadaa56e94523ca87631edb7164
  support: supports
  locator: IUPAC-IUB Recommendations1986, sections2.3–2.8; official web reproduction
  summary: The actual IUPAC-IUB nomenclature recommendations distinguish acid/folate
    names, methylene and methenyl bridges, glutamate-chain scope and stereochemical
    descriptors. Sections2.6 and2.8 identify (6S)-tetrahydrofolate and (6R)-5,10-methylenetetrahydrofolate
    as natural stereoisomer examples; R/S labels can change under priority rules without
    inversion of the underlying C6 configuration.
- evidence_id: primary-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11323337/fullTextXML
  accessed_at: '2026-10-21T09:03:46.932737Z'
  snapshot_sha256: 905cdbfd164cd5388529622255d3bc1cb8ee3d06a9680ac35210b6ebf3d2aa3a
  support: supports
  locator: PMID39148791; DOI10.1039/d4sc03187c; Abstract, Introduction, Results2.1–2.2
    and discussion of ligand identity
  summary: The inspected primary SHMT full text describes transfer of a carbon unit
    from serine to THF to form methylene-THF and calls THF both a coenzyme and a physiological
    substrate. The neutron structural experiment uses folinic acid, a different THF
    analogue; its measured proton positions are not transferred to the exact target
    chemical.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  locator: Executed 2026-10-21T09:02:03Z through 2026-10-21T09:02:06Z; exit 0
  accessed_at: '2026-10-21T09:02:06Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-3-chebi60470.yaml
    data/traits/function/cofactor_requirement/chebi/6-hydroxy-fad-chebi40260.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
    data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolic-acid-chebi1989.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolate-2-chebi57453.yaml
    data/traits/function/cofactor_requirement/chebi/6s-5-6-7-8-tetrahydrofolic-acid-chebi15635.yaml
    data/traits/function/cofactor_requirement/chebi/7-8-didemethyl-8-hydroxy-5-deazariboflavin-chebi43034.yaml
    data/traits/function/cofactor_requirement/chebi/acetyl-coa-chebi15351.yaml data/traits/function/cofactor_requirement/chebi/achromobactin-chebi61346.yaml
    data/traits/function/cofactor_requirement/chebi/achromobactin-free-acid-chebi65352.yaml
  locator: Executed 2026-10-21T09:02:02Z through 2026-10-21T09:04:01Z; exit 0
  accessed_at: '2026-10-21T09:04:01Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/6r-5-10-methylenetetrahydrofolate-2-chebi15636.yaml
  locator: Executed 2026-10-21T09:02:06Z through 2026-10-21T09:02:06Z; exit 0
  accessed_at: '2026-10-21T09:02:06Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:04:01Z through 2026-10-21T09:04:02Z; exit 0
  accessed_at: '2026-10-21T09:04:02Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-1
  topic: Ownership
- area: completeness
  outcome: supported
  summary: The local identifier and requires-label denote a proposed reusable requirement
    class rather than a protein instance. Optional examples, sequence/structure representations
    and mechanisms are not automatically required; none are newly qualified.
  evidence_ids:
  - record
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The local identifier and requires-label denote a reusable candidate protein
    requirement for (6R)-5,10-methylenetetrahydrofolate(2−). CHEBI:15636 identifies
    the named chemical with the specified charge and stereochemistry; it is not itself
    the protein requirement identifier.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: The target CC-BY 4.0 statement agrees with the official source licence.
    ChEBI supports the chemical description and role, while the functional-requirement
    sentence is synthesized by the maintained seeder. That sentence is not treated
    as a verbatim ChEBI chemical definition or as a ChEBI-asserted protein class.
  evidence_ids:
  - record
  - licence
  - chemical-role
  - owner
  - registry
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-6
  topic: Provenance
- area: evidence
  outcome: supported
  summary: The source structure specifies C20H21N7O6 with charge −2, (6R) stereochemistry
    and L-glutamate. The two glutamate carboxyl groups are deprotonated. CHEBI:1989
    is its separately identified neutral conjugate acid. The official backend definition
    is null and OLS description is empty, so the generated requirement sentence is
    not a source chemical definition. The term is the specified methylene-bridged
    stereoisomer, not methenyl-, methyl- or every polyglutamate folate.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - chemical-parent
  - conjugate
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-7
  topic: Evidence
- area: consistency
  outcome: supported
  summary: The source directly asserts cofactor role, and the retained local parent
    denotes the broader cofactor-requirement class. This supports the candidate hierarchy
    construction without treating chemical has-role as protein is-a or importing the
    structural chemical parent into the trait hierarchy. The parent record itself
    is not certified by this review.
  evidence_ids:
  - record
  - chemical-role
  - cofactor-role
  - chemical-parent
  - local-parent-1
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-8
  topic: Consistency
- area: grounding
  outcome: concern
  summary: CHEBI:15636 in true-equivalence xrefs denotes the chemical entity, whereas
    the local trait denotes a functional requirement. The schema provides chemical_participants
    with the COFACTOR role for the chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-9
  topic: Grounding
- area: representation
  outcome: concern
  summary: The FUNCTION requirement label can express a candidate class, but a source
    chemical role alone does not qualify a protein, determine a bound protonation
    state or establish physiological obligation. The chemical link must be a typed
    participant rather than class equivalence.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-10
  topic: Representation
- area: evidence
  outcome: supported
  summary: Authoritative folate nomenclature supports retaining the precise C6 descriptor,
    one-carbon substitution and glutamate scope. The primary SHMT text supplies bounded
    one-carbon chemistry context; its folinic-acid structure does not prove the target’s
    bound charge state. Coenzyme/substrate terminology depends on the reaction and
    does not establish that no protein could require this chemical in a non-substrate
    cofactor role.
  evidence_ids:
  - chemical-role
  - conjugate
  - nomenclature
  - primary-context
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  assessment_id: assessment-11
  topic: Evidence
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-15636.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local class denotes the functional requirement for (6R)-5,10-methylenetetrahydrofolate(2−),
    while CHEBI:15636 denotes the chemical entity. The schema reserves xrefs for true
    source-direct equivalents, so the emitted association asserts equivalence between
    different kinds of entity. A correct cofactor-role annotation and exact chemical
    identity do not remove that semantic mismatch.
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
  normalization_reason: This is a material semantic grounding error in a maintained
    generator mapping; the local requirement identity remains recoverable.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to preserve CHEBI:15636
    as chemical_participants with role COFACTOR and remove it from trait-equivalence
    xrefs. Preserve the local requirement identifier, exact charge/stereochemical
    identity and source-role provenance. Do not substitute a conjugate, move the chemical
    to parent_traits, or treat this own-source association as an external mapped_xrefs
    product.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_15636
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves its requirement-class identity and CHEBI:15636
    as the exact chemical participant with role COFACTOR.
  - No chemical entity is asserted equivalent to the protein requirement class; charge,
    stereochemistry and conjugate distinctions remain traceable.
  - Protein qualification and obligatory physiological requirement remain separate
    evidence questions; test the maintained writer and regenerate/validate through
    the audited route before a fresh review.
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
- No exact protein requirement is qualified from a metabolite role, a reaction-participant
  role or a paper on another folate. The SHMT neutron structure uses folinic acid,
  not this target; proton positions, pKa values and substrate/cofactor membership
  are not transferred.
- The source and target do not assert a physiological-pH dominant species. Exact acid/anion
  and (6R)/(6S) identities are preserved; no universal interchangeability with conjugates,
  alternative one-carbon substitutions or polyglutamates is inferred.
tags:
- unreviewed-path-order
- batch-010
- chebi-cofactor
```
