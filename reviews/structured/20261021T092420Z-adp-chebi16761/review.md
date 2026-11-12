# Review of requires ADP

- Review: 20261021T092420Z-adp-chebi16761
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T09:16:42Z
- Finished UTC: 2026-10-21T09:24:20Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

ADP chemical identity and charge-specific scope are supported; candidate provenance is the inspected local MicroGrowAgents alignment, with upstream release unverified. One confirmed major grounding finding concerns the chemical identifier encoded as equivalent to a protein requirement class.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 011. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f) covers 98 record paths, leaving 429261 before this batch. 11 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml | generated | requires ADP |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | Full curation-history gate; this review adds no history event. |
| Source identity and asserted references | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_16761 | CHEBI:16761, its asserted structural parents and conjugates resolve; the OLS target is nonobsolete. The local requirement parent was captured and read. The chemical reference belongs in typed participant grounding rather than true-equivalence xrefs. The local alignment mapping was inspected; upstream MicroGrowAgents data were not independently verified. |

## Scientific And Domain Assessments

### Ownership

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

scripts/seed_cofactor_alignment.py is the maintained primary emitter; seed_chebi_cofactor.py supplies imported chemical-name and formatting utilities. The inspect was recaptured with the alignment script and local crosswalk before judgment. No sibling checkout or upstream input table was read.

### Completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Graph

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Scope

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The local requires-label and identifier denote a reusable candidate protein requirement for ADP. CHEBI:16761 denotes the chemically specified entity, not that protein class.

### Provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The ChEBI chemical text and the MicroGrowAgents candidate-cofactor attribution are separable. The primary alignment emitter synthesizes the requirement sentence and emits the source category as a RELATED_SYNONYM; the local crosswalk corroborates the mapping. Official ChEBI licensing supports its chemical content, while the exact upstream MicroGrowAgents release and its source table were not independently verified.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The appended chemical description agrees with the source: an adenine-containing purine ribonucleoside 5'-diphosphate. CHEBI:16761 encodes neutral C10H15N5O10P2, with the adenosine ribose stereochemistry and three diphosphate OH groups; the IUPAC name specifies trihydrogen diphosphate. CHEBI:87518 and CHEBI:456216 separately identify ADP(2−) and ADP(3−). The latter source definition describes a major species at pH 7.3, which does not establish the species bound in a particular enzyme. The target's lowercase adp and broader nucleotides terms are explicitly RELATED_SYNONYM entries from the alignment source, not exact chemical-equivalence assertions.

### Consistency

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The captured parent is the broader cofactor-requirement class, consistent with the local alignment intent. Current ChEBI outgoing roles do not independently supply a cofactor edge for ADP. This does not show the candidate class is impossible, but bounds its provenance to the inspected local alignment and leaves protein membership unqualified. This review does not certify the parent record itself.

### Evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The inspected primary abstract reports increased sensitivity of GDH-S445L to the allosteric activator ADP, with experiments in transduced cells and islets. It supports ADP-associated regulatory context, not a demonstrated requirement for neutral CHEBI:16761 or verification of the MicroGrowAgents source table. No qualified protein example is added, and an alternate regulatory, biosynthetic, transport or substrate role is not taken to disprove a cofactor role in another context.

### Grounding

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

CHEBI:16761 in true-equivalence xrefs identifies a chemical entity, while the local trait identifies a functional requirement. chemical_participants with role COFACTOR provides the appropriate typed chemical association.

### Representation

representation: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_16761.

The candidate FUNCTION requirement class is recoverable, but chemical reference and source-role context must remain distinct from class equivalence and from evidence that a protein requires the exact chemical species.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-16761.chemical-entity-equivalence.

The local class denotes a functional requirement for ADP, whereas CHEBI:16761 denotes the chemical entity. The schema reserves xrefs for true own-source equivalence, so the emitted association equates different kinds of entity. Correct chemical identity and candidate cofactor provenance do not remove this semantic mismatch.

## Recommended Actions And Acceptance Checks

### A1

Update build_aligned() in scripts/seed_cofactor_alignment.py to preserve CHEBI:16761 as chemical_participants with role COFACTOR and remove it from trait-equivalence xrefs. Retain the local requirement identifier, exact chemical charge/stereochemical scope and attributed candidate provenance. Do not substitute a conjugate, move the chemical into parent_traits, or recast this own-source association as an external mapped_xrefs product.

- The regenerated target preserves CHEBI:16761 as the exact typed chemical participant with role COFACTOR and retains the local candidate requirement-class identity.
- No chemical entity is asserted equivalent to the protein requirement class; conjugate, stereochemical and source-role distinctions remain traceable.
- The maintained emitter is tested and the target regenerated and validated before a fresh review; protein qualification and obligatory physiological requirement remain separate evidence questions.
- Use a controlled, audited regeneration path for this existing aligned record: current main selects only missing ChEBI IDs, so merely rerunning the script, even with --force, does not select the already present ADP target.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml; Entire target YAML | supports | Complete YAML inspected, including local requirement identity, the ChEBI/MicroGrowAgents definition attribution, nucleotide-category wording, two MicroGrowAgents RELATED_SYNONYM entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, parent, chemical xref and ChEBI licence. No examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| chebi-helper | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | The ChEBI name/definition loaders and shared identifier, formatting and licence utilities are imported by seed_cofactor_alignment.py. The ordinary has-role selection route in this helper is not asserted to be the emitter of this ADP target. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| owner | scripts/seed_cofactor_alignment.py; load_mg_cofactors, build_aligned, main; imports from seed_chebi_cofactor.py | supports | build_aligned emits the target requirement sentence, MicroGrowAgents attribution, category parenthetical, root cofactor parent, RELATED_SYNONYM entries and CHEBI xref. main selects curated input IDs missing from the base ChEBI-role seed and uses imported ChEBI utilities. This is the maintained primary emitter for this ADP record. |
| crosswalk | data/mappings/cofactor_crosswalk.tsv; Header and CHEBI:16761 row 40 | supports | The captured local crosswalk row maps CHEBI:16761 to the local ADP requirement identifier, ADP name, MicroGrowAgents cofactor_id adp and category nucleotides. It corroborates the local alignment mapping; it is not an independently inspected upstream MicroGrowAgents release. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The inspected Introduction describes chemical entities and the Licensing section explicitly makes website data available under CC BY 4.0. This supports ChEBI chemical scope and the recorded ChEBI licence. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Official OLS metadata reports ChEBI version 256, loaded 2026-10-16. This identifies the OLS comparison release, not the separately timestamped live backend or the source release used for the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_16761; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:16761 to the nonobsolete ADP chemical entity. Its label, available description and aliases were inspected; it is not a protein requirement class. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/16761/; name, definition, chemical_data, default_structure, names, ontology_relations.outgoing_relations | supports | The complete official response supplies chemical identity, formula, charge, structure, names and outgoing relations. The current outgoing has-role entries are human metabolite and fundamental metabolite; there is no direct cofactor edge in this captured response. This bounded source observation does not refute the separately attributed MicroGrowAgents candidate class. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; definition and ontology_relations.outgoing_relations | supports | Cofactor is defined as an organic molecule or ion required by an enzyme for activity and is-a CHEBI:52206 biochemical role. Chemical has-role and protein requirement-class membership are different assertions. |
| chemical-parent-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37038/; name, definition, chemical_data and ontology_relations.outgoing_relations | supports | CHEBI:37038, an asserted immediate structural parent, resolves and its definition and outgoing relations were inspected. It classifies the chemical rather than the protein requirement trait. |
| chemical-parent-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/37096/; name, definition, chemical_data and ontology_relations.outgoing_relations | supports | CHEBI:37096, an asserted immediate structural parent, resolves and its definition and outgoing relations were inspected. It classifies the chemical rather than the protein requirement trait. |
| conjugate-1 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/87518/; name, definition, chemical_data, default_structure and ontology_relations.outgoing_relations | supports | The separately identified conjugate CHEBI:87518 resolves; its formula, charge, definition and reciprocal conjugate relation were inspected. This preserves charge-specific chemical identity, not automatic trait equivalence. |
| conjugate-2 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/456216/; name, definition, chemical_data, default_structure and ontology_relations.outgoing_relations | supports | The separately identified conjugate CHEBI:456216 resolves; its formula, charge, definition and reciprocal conjugate relation were inspected. This preserves charge-specific chemical identity, not automatic trait equivalence. |
| primary-context | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A28911206+AND+SRC%3AMED&amp;format=json&amp;resultType=core&amp;pageSize=1; PMID:28911206; complete indexed primary abstract in Europe PMC core response | supports | The inspected primary abstract reports increased sensitivity of GDH-S445L to the allosteric activator ADP, with experiments in transduced cells and islets. It supports ADP-associated regulatory context, not a demonstrated requirement for neutral CHEBI:16761 or verification of the MicroGrowAgents source table. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml; Executed 2026-10-21T09:17:15Z through 2026-10-21T09:17:16Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-2-chebi456215.yaml data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-chebi16027.yaml data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml data/traits/function/cofactor_requirement/chebi/aerobactin-chebi18157.yaml data/traits/function/cofactor_requirement/chebi/ammonium-chebi28938.yaml data/traits/function/cofactor_requirement/chebi/anhydromevalonyl-coa-chebi133870.yaml data/traits/function/cofactor_requirement/chebi/atp-3-chebi57299.yaml data/traits/function/cofactor_requirement/chebi/atp-4-chebi30616.yaml data/traits/function/cofactor_requirement/chebi/atp-chebi15422.yaml data/traits/function/cofactor_requirement/chebi/bacillithiol-chebi61338.yaml; Executed 2026-10-21T09:17:12Z through 2026-10-21T09:18:59Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml; Executed 2026-10-21T09:17:16Z through 2026-10-21T09:17:16Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T09:18:59Z through 2026-10-21T09:19:00Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- The candidate cofactor classification is locally attributed to the MicroGrowAgents alignment, not to a current ChEBI cofactor-role edge. The upstream MicroGrowAgents TSV and exact release were not independently inspected. The local crosswalk and emitter corroborate local provenance only; neither qualifies a particular protein or an obligatory physiological requirement.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The complete indexed abstract for PMID:28911206 was inspected; the full paper was not inspected for this review. It supplies only the bounded context stated above, not an independently qualified protein exemplar.
- No pKa, exact enzyme-bound protonation state, universal interchangeability of conjugates, or obligatory physiological requirement is inferred from an informal chemical name, source role or activity study.
- The current source role observation is limited to the captured ChEBI response; no absence claim about all releases or all possible ADP cofactor uses is made. The broader nucleotides term is RELATED_SYNONYM, not an exact-equivalence claim.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T092420Z-adp-chebi16761
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires ADP
started_at: '2026-10-21T09:16:42Z'
finished_at: '2026-10-21T09:24:20Z'
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
summary: ADP chemical identity and charge-specific scope are supported; candidate
  provenance is the inspected local MicroGrowAgents alignment, with upstream release
  unverified. One confirmed major grounding finding concerns the chemical identifier
  encoded as equivalent to a protein requirement class.
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
  - path: data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
    sha256: 428b58e5e3363f3d712d03dd3186f8054032e326c65260807b82358690a44012
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
  selection: Path-order position 3 in batch 011. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f) covers 98 record paths,
    leaving 429261 before this batch. 11 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
targets:
- kind: generated
  label: requires ADP
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cofactor_alignment.py
    role: Maintained MicroGrowAgents cofactor alignment emitter build_aligned and
      missing-ID selection
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_chebi_cofactor.py
    role: Imported ChEBI chemical-name/definition loader and shared formatting/identifier
      dependency
  path: data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_16761
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-2-chebi456215.yaml
    data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-chebi16027.yaml
    data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml data/traits/function/cofactor_requirement/chebi/aerobactin-chebi18157.yaml
    data/traits/function/cofactor_requirement/chebi/ammonium-chebi28938.yaml data/traits/function/cofactor_requirement/chebi/anhydromevalonyl-coa-chebi133870.yaml
    data/traits/function/cofactor_requirement/chebi/atp-3-chebi57299.yaml data/traits/function/cofactor_requirement/chebi/atp-4-chebi30616.yaml
    data/traits/function/cofactor_requirement/chebi/atp-chebi15422.yaml data/traits/function/cofactor_requirement/chebi/bacillithiol-chebi61338.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source identity and asserted references
  status: passed
  required: true
  summary: CHEBI:16761, its asserted structural parents and conjugates resolve; the
    OLS target is nonobsolete. The local requirement parent was captured and read.
    The chemical reference belongs in typed participant grounding rather than true-equivalence
    xrefs. The local alignment mapping was inspected; upstream MicroGrowAgents data
    were not independently verified.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - primary-context
  - chemical-parent-1
  - chemical-parent-2
  - conjugate-1
  - conjugate-2
  - crosswalk
  - owner
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T09:16:42Z'
  snapshot_sha256: 428b58e5e3363f3d712d03dd3186f8054032e326c65260807b82358690a44012
  support: supports
  summary: Complete YAML inspected, including local requirement identity, the ChEBI/MicroGrowAgents
    definition attribution, nucleotide-category wording, two MicroGrowAgents RELATED_SYNONYM
    entries, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, parent, chemical
    xref and ChEBI licence. No examples, causal graphs, qualified protein assertions
    or chemical_participants occur in this target YAML.
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum;
    FUNC_COFACTOR_REQUIREMENT
  accessed_at: '2026-10-21T09:16:42Z'
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
  accessed_at: '2026-10-21T09:16:42Z'
  snapshot_sha256: c94f89132779ded0393c70a67ea35da9bc1d1d5a5adbc5212aeac144a124c802
  support: supports
  summary: The ChEBI name/definition loaders and shared identifier, formatting and
    licence utilities are imported by seed_cofactor_alignment.py. The ordinary has-role
    selection route in this helper is not asserted to be the emitter of this ADP target.
- evidence_id: registry
  kind: record_content
  reference: download.yaml
  locator: ChEBI source entry
  accessed_at: '2026-10-21T09:16:42Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T09:16:42Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: 'Entire local parent YAML inspected: local requirement identifier, definition,
    category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution
    does not establish that its own xrefs have equivalent-class semantics.'
- evidence_id: owner
  kind: record_content
  reference: scripts/seed_cofactor_alignment.py
  locator: load_mg_cofactors, build_aligned, main; imports from seed_chebi_cofactor.py
  accessed_at: '2026-10-21T09:17:59.340731Z'
  snapshot_sha256: b93c398484e659617770bc99f2116757bf0d9b25f731fd31c6e7c1e9c65536cf
  support: supports
  summary: build_aligned emits the target requirement sentence, MicroGrowAgents attribution,
    category parenthetical, root cofactor parent, RELATED_SYNONYM entries and CHEBI
    xref. main selects curated input IDs missing from the base ChEBI-role seed and
    uses imported ChEBI utilities. This is the maintained primary emitter for this
    ADP record.
- evidence_id: crosswalk
  kind: record_content
  reference: data/mappings/cofactor_crosswalk.tsv
  locator: Header and CHEBI:16761 row 40
  accessed_at: '2026-10-21T09:17:59.340731Z'
  snapshot_sha256: a1ebb2af5d9e39ae072efb1a0d6a4774272d6e0e881b3c792faae53b4fc748ba
  support: supports
  summary: The captured local crosswalk row maps CHEBI:16761 to the local ADP requirement
    identifier, ADP name, MicroGrowAgents cofactor_id adp and category nucleotides.
    It corroborates the local alignment mapping; it is not an independently inspected
    upstream MicroGrowAgents release.
- evidence_id: licence
  kind: authority
  reference: https://www.ebi.ac.uk/chebi/about/
  accessed_at: '2026-10-21T08:48:05.571149Z'
  snapshot_sha256: f541592fc56a6bda901699cf4a970e5129a18cdbd780e642ad5c36a5ad55251b
  support: supports
  locator: Introduction and Licensing sections
  summary: The inspected Introduction describes chemical entities and the Licensing
    section explicitly makes website data available under CC BY 4.0. This supports
    ChEBI chemical scope and the recorded ChEBI licence.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Official OLS metadata reports ChEBI version 256, loaded 2026-10-16. This
    identifies the OLS comparison release, not the separately timestamped live backend
    or the source release used for the original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_16761
  accessed_at: '2026-10-21T09:17:32.304181Z'
  snapshot_sha256: 5d5364a76b2fd5d7dcbe4a492ded528dcb3eb92165aff53dfb2108a59a4ae546
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:16761 to the nonobsolete ADP chemical entity. Its label,
    available description and aliases were inspected; it is not a protein requirement
    class.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/16761/
  accessed_at: '2026-10-21T09:17:31.641513Z'
  snapshot_sha256: 7c068acc0ce95538a614cf4c1e4182e67bf4ced89fae4a63a1238283a083e37f
  support: supports
  locator: name, definition, chemical_data, default_structure, names, ontology_relations.outgoing_relations
  summary: The complete official response supplies chemical identity, formula, charge,
    structure, names and outgoing relations. The current outgoing has-role entries
    are human metabolite and fundamental metabolite; there is no direct cofactor edge
    in this captured response. This bounded source observation does not refute the
    separately attributed MicroGrowAgents candidate class.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T08:48:04.105973Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: definition and ontology_relations.outgoing_relations
  summary: Cofactor is defined as an organic molecule or ion required by an enzyme
    for activity and is-a CHEBI:52206 biochemical role. Chemical has-role and protein
    requirement-class membership are different assertions.
- evidence_id: chemical-parent-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37038/
  accessed_at: '2026-10-21T09:18:27.476425Z'
  snapshot_sha256: 5a6218fb483366a4e6dd43d41b2b876cf098717c9312f6a5a8af8a79bfb6c5ad
  support: supports
  locator: name, definition, chemical_data and ontology_relations.outgoing_relations
  summary: CHEBI:37038, an asserted immediate structural parent, resolves and its
    definition and outgoing relations were inspected. It classifies the chemical rather
    than the protein requirement trait.
- evidence_id: chemical-parent-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/37096/
  accessed_at: '2026-10-21T09:18:27.514930Z'
  snapshot_sha256: f4c92b75db6df7c72c9deb3e51256041e4fc2aaf1a9ce89438b96ac7a933000e
  support: supports
  locator: name, definition, chemical_data and ontology_relations.outgoing_relations
  summary: CHEBI:37096, an asserted immediate structural parent, resolves and its
    definition and outgoing relations were inspected. It classifies the chemical rather
    than the protein requirement trait.
- evidence_id: conjugate-1
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/87518/
  accessed_at: '2026-10-21T09:18:28.303666Z'
  snapshot_sha256: 770e823e6f3f3e30c9391f2e898d946c5b41e9ac4f0afa42beae454daa01016c
  support: supports
  locator: name, definition, chemical_data, default_structure and ontology_relations.outgoing_relations
  summary: The separately identified conjugate CHEBI:87518 resolves; its formula,
    charge, definition and reciprocal conjugate relation were inspected. This preserves
    charge-specific chemical identity, not automatic trait equivalence.
- evidence_id: conjugate-2
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/456216/
  accessed_at: '2026-10-21T09:18:28.309445Z'
  snapshot_sha256: 10453aa1acac88e3209957c6c99f9d0b4ff096980471435ff6dd4b73c25fbde3
  support: supports
  locator: name, definition, chemical_data, default_structure and ontology_relations.outgoing_relations
  summary: The separately identified conjugate CHEBI:456216 resolves; its formula,
    charge, definition and reciprocal conjugate relation were inspected. This preserves
    charge-specific chemical identity, not automatic trait equivalence.
- evidence_id: primary-context
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A28911206+AND+SRC%3AMED&format=json&resultType=core&pageSize=1
  accessed_at: '2026-10-21T09:18:51.427680Z'
  snapshot_sha256: 36991d2f804b120ad14de9e47ba5ac57d1b106b3331622d3a76ecb2b4a6586cc
  support: supports
  locator: PMID:28911206; complete indexed primary abstract in Europe PMC core response
  summary: The inspected primary abstract reports increased sensitivity of GDH-S445L
    to the allosteric activator ADP, with experiments in transduced cells and islets.
    It supports ADP-associated regulatory context, not a demonstrated requirement
    for neutral CHEBI:16761 or verification of the MicroGrowAgents source table.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  locator: Executed 2026-10-21T09:17:15Z through 2026-10-21T09:17:16Z; exit 0
  accessed_at: '2026-10-21T09:17:16Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-2-chebi456215.yaml
    data/traits/function/cofactor_requirement/chebi/adenosine-5-monophosphate-chebi16027.yaml
    data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml data/traits/function/cofactor_requirement/chebi/aerobactin-chebi18157.yaml
    data/traits/function/cofactor_requirement/chebi/ammonium-chebi28938.yaml data/traits/function/cofactor_requirement/chebi/anhydromevalonyl-coa-chebi133870.yaml
    data/traits/function/cofactor_requirement/chebi/atp-3-chebi57299.yaml data/traits/function/cofactor_requirement/chebi/atp-4-chebi30616.yaml
    data/traits/function/cofactor_requirement/chebi/atp-chebi15422.yaml data/traits/function/cofactor_requirement/chebi/bacillithiol-chebi61338.yaml
  locator: Executed 2026-10-21T09:17:12Z through 2026-10-21T09:18:59Z; exit 0
  accessed_at: '2026-10-21T09:18:59Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/adp-chebi16761.yaml
  locator: Executed 2026-10-21T09:17:16Z through 2026-10-21T09:17:16Z; exit 0
  accessed_at: '2026-10-21T09:17:16Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T09:18:59Z through 2026-10-21T09:19:00Z; exit 0
  accessed_at: '2026-10-21T09:19:00Z'
  support: supports
  summary: No issues found
assessments:
- area: ownership
  outcome: supported
  summary: scripts/seed_cofactor_alignment.py is the maintained primary emitter; seed_chebi_cofactor.py
    supplies imported chemical-name and formatting utilities. The inspect was recaptured
    with the alignment script and local crosswalk before judgment. No sibling checkout
    or upstream input table was read.
  evidence_ids:
  - owner
  - chebi-helper
  - crosswalk
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-2
  topic: Completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-3
  topic: Graph
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-4
  topic: Scope
- area: identity
  outcome: supported
  summary: The local requires-label and identifier denote a reusable candidate protein
    requirement for ADP. CHEBI:16761 denotes the chemically specified entity, not
    that protein class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-5
  topic: Identity
- area: provenance
  outcome: supported
  summary: The ChEBI chemical text and the MicroGrowAgents candidate-cofactor attribution
    are separable. The primary alignment emitter synthesizes the requirement sentence
    and emits the source category as a RELATED_SYNONYM; the local crosswalk corroborates
    the mapping. Official ChEBI licensing supports its chemical content, while the
    exact upstream MicroGrowAgents release and its source table were not independently
    verified.
  evidence_ids:
  - record
  - owner
  - licence
  - chemical-role
  - release
  - crosswalk
  - chebi-helper
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-6
  topic: Provenance
- area: evidence
  outcome: supported
  summary: 'The appended chemical description agrees with the source: an adenine-containing
    purine ribonucleoside 5''-diphosphate. CHEBI:16761 encodes neutral C10H15N5O10P2,
    with the adenosine ribose stereochemistry and three diphosphate OH groups; the
    IUPAC name specifies trihydrogen diphosphate. CHEBI:87518 and CHEBI:456216 separately
    identify ADP(2−) and ADP(3−). The latter source definition describes a major species
    at pH 7.3, which does not establish the species bound in a particular enzyme.
    The target''s lowercase adp and broader nucleotides terms are explicitly RELATED_SYNONYM
    entries from the alignment source, not exact chemical-equivalence assertions.'
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - chemical-parent-1
  - chemical-parent-2
  - conjugate-1
  - conjugate-2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-7
  topic: Evidence
- area: consistency
  outcome: supported
  summary: The captured parent is the broader cofactor-requirement class, consistent
    with the local alignment intent. Current ChEBI outgoing roles do not independently
    supply a cofactor edge for ADP. This does not show the candidate class is impossible,
    but bounds its provenance to the inspected local alignment and leaves protein
    membership unqualified. This review does not certify the parent record itself.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - cofactor-role
  - crosswalk
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-8
  topic: Consistency
- area: evidence
  outcome: supported
  summary: The inspected primary abstract reports increased sensitivity of GDH-S445L
    to the allosteric activator ADP, with experiments in transduced cells and islets.
    It supports ADP-associated regulatory context, not a demonstrated requirement
    for neutral CHEBI:16761 or verification of the MicroGrowAgents source table. No
    qualified protein example is added, and an alternate regulatory, biosynthetic,
    transport or substrate role is not taken to disprove a cofactor role in another
    context.
  evidence_ids:
  - primary-context
  - chemical-role
  - schema
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-9
  topic: Evidence
- area: grounding
  outcome: concern
  summary: CHEBI:16761 in true-equivalence xrefs identifies a chemical entity, while
    the local trait identifies a functional requirement. chemical_participants with
    role COFACTOR provides the appropriate typed chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-10
  topic: Grounding
- area: representation
  outcome: concern
  summary: The candidate FUNCTION requirement class is recoverable, but chemical reference
    and source-role context must remain distinct from class equivalence and from evidence
    that a protein requires the exact chemical species.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  assessment_id: assessment-11
  topic: Representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-16761.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local class denotes a functional requirement for ADP, whereas CHEBI:16761
    denotes the chemical entity. The schema reserves xrefs for true own-source equivalence,
    so the emitted association equates different kinds of entity. Correct chemical
    identity and candidate cofactor provenance do not remove this semantic mismatch.
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
  normalization_reason: This is a material semantic grounding error in the maintained
    generator mapping, while the local requirement identity remains recoverable.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cofactor_alignment.py
    role: Maintained MicroGrowAgents cofactor alignment emitter build_aligned and
      missing-ID selection
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_chebi_cofactor.py
    role: Imported ChEBI chemical-name/definition loader and shared formatting/identifier
      dependency
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build_aligned() in scripts/seed_cofactor_alignment.py to preserve
    CHEBI:16761 as chemical_participants with role COFACTOR and remove it from trait-equivalence
    xrefs. Retain the local requirement identifier, exact chemical charge/stereochemical
    scope and attributed candidate provenance. Do not substitute a conjugate, move
    the chemical into parent_traits, or recast this own-source association as an external
    mapped_xrefs product.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_16761
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_cofactor_alignment.py
    role: Maintained MicroGrowAgents cofactor alignment emitter build_aligned and
      missing-ID selection
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_chebi_cofactor.py
    role: Imported ChEBI chemical-name/definition loader and shared formatting/identifier
      dependency
  acceptance_checks:
  - The regenerated target preserves CHEBI:16761 as the exact typed chemical participant
    with role COFACTOR and retains the local candidate requirement-class identity.
  - No chemical entity is asserted equivalent to the protein requirement class; conjugate,
    stereochemical and source-role distinctions remain traceable.
  - The maintained emitter is tested and the target regenerated and validated before
    a fresh review; protein qualification and obligatory physiological requirement
    remain separate evidence questions.
  - 'Use a controlled, audited regeneration path for this existing aligned record:
    current main selects only missing ChEBI IDs, so merely rerunning the script, even
    with --force, does not select the already present ADP target.'
limitations:
- The reviewed record does not identify the exact ChEBI source release used for the
  seed. Current official responses are comparison snapshots, not proof of the original
  release.
- The candidate cofactor classification is locally attributed to the MicroGrowAgents
  alignment, not to a current ChEBI cofactor-role edge. The upstream MicroGrowAgents
  TSV and exact release were not independently inspected. The local crosswalk and
  emitter corroborate local provenance only; neither qualifies a particular protein
  or an obligatory physiological requirement.
- External sources were inspected and SHA256-captured in session scratch. This bundle
  retains URLs, access times, digests and bounded observations rather than full response
  bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB
  is not applicable to this generic chemical requirement class without a gene, organism
  or expression dataset.
- The complete indexed abstract for PMID:28911206 was inspected; the full paper was
  not inspected for this review. It supplies only the bounded context stated above,
  not an independently qualified protein exemplar.
- No pKa, exact enzyme-bound protonation state, universal interchangeability of conjugates,
  or obligatory physiological requirement is inferred from an informal chemical name,
  source role or activity study.
- The current source role observation is limited to the captured ChEBI response; no
  absence claim about all releases or all possible ADP cofactor uses is made. The
  broader nucleotides term is RELATED_SYNONYM, not an exact-equivalence claim.
tags:
- unreviewed-path-order
- batch-011
- chebi-cofactor
```
