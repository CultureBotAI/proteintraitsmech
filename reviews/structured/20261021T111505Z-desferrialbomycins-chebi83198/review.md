# Review of requires desferrialbomycins

- Review: 20261021T111505Z-desferrialbomycins-chebi83198
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:07:32Z
- Finished UTC: 2026-10-21T11:15:05Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The iron-free desferrialbomycin chemical-class identity and bounded antibacterial background are supported. One confirmed major finding concerns chemical-class-to-protein-requirement equivalence. Individual congener/inhibitor activity is not generalized to the entire apo class.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 018. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9) covers 168 record paths, leaving 429191 before this batch. 18 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml | generated | requires desferrialbomycins |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_83198 | CHEBI:83198 resolves and is nonobsolete. Its class definition, R-group representation, related alias, siderophore role and five structural parents were inspected. Local siderophore/cofactor ancestors and the two complete primary abstracts were read. The latter support bounded δ2/inhibitor context rather than every class member or exact protein requirement. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The complete local YAML denotes a proposed reusable protein requirement for desferrialbomycins. CHEBI:83198 identifies its chemical referent or chemical class, not an equivalent protein-requirement class.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

scripts/seed_chebi_cofactor.py owns the generated target: it selects source roles, synthesizes the requirement wrapper, appends chemical text and emits a chemical xref. CC BY 4.0 is supported by the official source. Current comparison snapshots do not identify the original seed release.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The inspected source role relation explains selection of the captured local broader requirement parent. Chemical-role taxonomy is not automatically a protein-requirement hierarchy or true equivalence; this one-record review does not certify the parent.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

CHEBI:83198 in xrefs denotes a chemical entity/class, whereas the target denotes a protein functional requirement. The schema requires true own-source equivalence rather than a chemical association.

### Desferrialbomycin chemical-class structure and variable substituents

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

CHEBI:83198 is an iron-free chemical class of pentapeptides with three modified L-ornithyl residues, L-seryl and the source-described unusual D-amino-acid/thiofuranose-pyrimidine component. The R-group drawing and generalized C36H58N10O17SR formula represent variable pyrimidine substitution; they do not define a single fixed-formula molecule or all physiological protonation states. The source charge 0 belongs to that drawing.

### Intact albomycin complexes versus released inhibitor

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The local background explicitly attributes antibacterial activity to iron(III) complexes, albomycins. The primaryδ2 / SB-217452 studies distinguish intact metal complexes, released nucleoside inhibitor and measured SerRS inhibition. They provide a concrete bounded member context, not evidence that all apo-class members directly inhibit every SerRS or that intact complexes have the same cell-free action as the released moiety.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_83198.

The siderophore role is authentic source context. Iron transport, antibiotic delivery and inhibition by a released moiety are distinct from the non-substrate protein requirement asserted by the local wrapper. Neither alternate roles nor these assays prove universal absence of cofactor use; no protein is qualified here.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-83198.chemical-entity-equivalence.

The local record denotes a protein requirement for desferrialbomycins, while CHEBI:83198 denotes an iron-free R-group chemical class of pentapeptides. xrefs conflates the functional requirement with the chemical-class referent.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:83198 from trait-equivalence xrefs and preserve the exact source identity through schema-compatible grounding. Preserve chemical-source provenance separately from the locally synthesized requirement. Before assigning a COFACTOR chemical_participant, adjudicate whether the intended activity-relative role satisfies the non-substrate requirement category; otherwise retain that uncertainty and use only a supported representation. Do not blindly move this own-source association to mapped_xrefs, infer a required protein from chemical role alone, or promote SEEDED status.

- The regenerated target preserves the intended CHEBI:83198 chemical scope without asserting equality to a protein requirement.
- Preserve the variable chemical-class scope and distinguish apo ligands, ferric albomycins and released SB-217452. Do not infer a universal formula, protonation state, antibacterial mechanism or COFACTOR role from one congener or inhibitor experiment.
- Any typed participant has the supported activity-relative role and exact chemical scope; no unreviewed protein example, universal requirement or automatic status promotion is introduced.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml. These are future curation acceptance checks, not claims that the target has already changed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction defines its chemical entities and chemical classes. Licensing makes website data available under CC BY 4.0. This supports source licensing, not the locally synthesized protein-requirement claim. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Its original access timestamp is preserved. It is comparison-ontology metadata, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_83198; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:83198 to nonobsolete desferrialbomycins. The actual definition, identifiers, aliases and chemical annotations were inspected; the source term denotes chemistry rather than a protein requirement. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/83198/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The complete target chemical response was inspected: exact name, definition, formula/charge or R-group class representation, stereochemical encoding, aliases and incoming/outgoing relations. The source chemical role supplies candidate context and does not qualify a protein. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | ChEBI cofactor is a biochemical role for an organic molecule or ion required by an enzyme. The role is not a protein-requirement class. |
| local-cofactor-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | The fully captured broader cofactor-requirement ancestor was read. Its local requirement definition, ChEBI role xref and SEEDED status are context; this review does not certify that ancestor. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The source role describes microbial iron(III) chelation for transport and sequestration. Its outgoing is-a relations include cofactor, iron(3+) chelator and iron ionophore. This authentic source hierarchy is distinct from proof of non-substrate dependence in a protein. |
| pentapeptide | https://www.ebi.ac.uk/chebi/backend/api/public/compound/48545/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines five amino-acid residues connected by peptide linkages. This chemical classification does not establish a protein requirement. |
| hydroxamic-acid | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines hydroxamic acids and their derivatives; specific examples can be named N-hydroxy amides. This chemical classification does not establish a protein requirement. |
| thio-ring | https://www.ebi.ac.uk/chebi/backend/api/public/compound/48224/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The tetrahydrothiophenes structural parent has a null prose definition and outgoing organic heteromonocyclic compound and organosulfur heterocyclic compound parents. This chemical classification does not establish a protein requirement. |
| monocarboxylic-acid | https://www.ebi.ac.uk/chebi/backend/api/public/compound/25384/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines an oxoacid containing a single carboxy group. This chemical classification does not establish a protein requirement. |
| pyrimidone | https://www.ebi.ac.uk/chebi/backend/api/public/compound/38337/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines a pyrimidine carrying one or more oxo substituents. This chemical classification does not establish a protein requirement. |
| inhibitor-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11217799%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID11217799; DOI10.7164/antibiotics.53.1346; complete indexed abstract | supports | The complete primary abstract identifies SB-217452 as the serine-linked nucleoside portion of albomycin δ2, with potent SerRS inhibition but weak antibacterial activity compared with δ2. Ferric and aluminium δ2 complexes were isolated and had no SerRS inhibition in that study. This distinguishes released inhibitor, intact complexes and whole-cell activity. |
| serrs-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19721072%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID19721072; DOI10.1128/AAC.00782-09; complete indexed abstract | supports | The complete primary abstract genetically/biochemically characterizes two SerRS proteins in Streptomyces ATCC700974 and their different resistance to SB-217452. It supports the bounded inhibitor mechanism, not identical effects of every apo desferrialbomycin or an obligatory cofactor requirement. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml; Executed 2026-10-21T11:10:52Z through 2026-10-21T11:10:53Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml; Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml; Executed 2026-10-21T11:10:53Z through 2026-10-21T11:10:53Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The primary papers were inspected at complete indexed-abstract level only. Detailed whole-class stereochemical synthesis, every congener and all binding/protonation states were not independently experimentally verified; the structural stereochemistry is identified as source-encoded. No universal inhibitor/cofactor exclusion is claimed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T111505Z-desferrialbomycins-chebi83198
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires desferrialbomycins
started_at: '2026-10-21T11:07:32Z'
finished_at: '2026-10-21T11:15:05Z'
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
summary: The iron-free desferrialbomycin chemical-class identity and bounded antibacterial
  background are supported. One confirmed major finding concerns chemical-class-to-protein-requirement
  equivalence. Individual congener/inhibitor activity is not generalized to the entire
  apo class.
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
  - path: data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
    sha256: ea1b5f9c33729fb8ffd6e67676497c20ba66a9b135ce5eb2593280715601ae11
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
  selection: Path-order position 3 in batch 018. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9)
    covers 168 record paths, leaving 429191 before this batch. 18 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
targets:
- kind: generated
  label: requires desferrialbomycins
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_83198
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
    data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
    data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml
    data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml
    data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:83198 resolves and is nonobsolete. Its class definition, R-group
    representation, related alias, siderophore role and five structural parents were
    inspected. Local siderophore/cofactor ancestors and the two complete primary abstracts
    were read. The latter support bounded δ2/inhibitor context rather than every class
    member or exact protein requirement.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - siderophore-role
  - pentapeptide
  - hydroxamic-acid
  - thio-ring
  - monocarboxylic-acid
  - pyrimidone
  - inhibitor-primary
  - serrs-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:07:32Z'
  snapshot_sha256: ea1b5f9c33729fb8ffd6e67676497c20ba66a9b135ce5eb2593280715601ae11
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
  accessed_at: '2026-10-21T11:07:32Z'
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
  accessed_at: '2026-10-21T11:07:32Z'
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
  accessed_at: '2026-10-21T11:07:32Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:07:32Z'
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
  locator: Introduction and Licensing
  summary: The official ChEBI Introduction defines its chemical entities and chemical
    classes. Licensing makes website data available under CC BY 4.0. This supports
    source licensing, not the locally synthesized protein-requirement claim.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Its original access timestamp is preserved. It is comparison-ontology metadata,
    not a release assignment for live backend responses or the original seed.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_83198
  accessed_at: '2026-10-21T11:08:00.131147Z'
  snapshot_sha256: 88ecaea0d0285964f2696cc919b3fffa6772af3646a44380d8f3a32d331fe314
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:83198 to nonobsolete desferrialbomycins. The actual
    definition, identifiers, aliases and chemical annotations were inspected; the
    source term denotes chemistry rather than a protein requirement.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/83198/
  accessed_at: '2026-10-21T11:07:59.508165Z'
  snapshot_sha256: 77963fd926d0e2fcc2bed2d38e64fbd1eafcb53db8caab998eec03eb3131393f
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: 'The complete target chemical response was inspected: exact name, definition,
    formula/charge or R-group class representation, stereochemical encoding, aliases
    and incoming/outgoing relations. The source chemical role supplies candidate context
    and does not qualify a protein.'
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: ChEBI cofactor is a biochemical role for an organic molecule or ion required
    by an enzyme. The role is not a protein-requirement class.
- evidence_id: local-cofactor-ancestor
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire captured ancestor YAML
  accessed_at: '2026-10-21T11:07:32Z'
  snapshot_sha256: d5a2579eae56a7b94424792e5694c0d1c58765e388630b1ab7807be0c8ded909
  support: supports
  summary: The fully captured broader cofactor-requirement ancestor was read. Its
    local requirement definition, ChEBI role xref and SEEDED status are context; this
    review does not certify that ancestor.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T09:02:57.586907Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The source role describes microbial iron(III) chelation for transport and
    sequestration. Its outgoing is-a relations include cofactor, iron(3+) chelator
    and iron ionophore. This authentic source hierarchy is distinct from proof of
    non-substrate dependence in a protein.
- evidence_id: pentapeptide
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/48545/
  accessed_at: '2026-10-21T11:09:32.901233Z'
  snapshot_sha256: 27521d0b81c9e601d1a85685b000e90ae44ed435b7d2d9e821a42efeaefc27d5
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines five amino-acid residues connected by peptide
    linkages. This chemical classification does not establish a protein requirement.
- evidence_id: hydroxamic-acid
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/
  accessed_at: '2026-10-21T11:09:33.549154Z'
  snapshot_sha256: 489ee6f999b8a733ab1e6334c09f36828ec55ecae22082aca866ad781b0861bf
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines hydroxamic acids and their derivatives; specific
    examples can be named N-hydroxy amides. This chemical classification does not
    establish a protein requirement.
- evidence_id: thio-ring
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/48224/
  accessed_at: '2026-10-21T11:09:33.626445Z'
  snapshot_sha256: 16015d352926a84bd6e6a4531a18797e23e74228127773478333b3a77e551fce
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The tetrahydrothiophenes structural parent has a null prose definition
    and outgoing organic heteromonocyclic compound and organosulfur heterocyclic compound
    parents. This chemical classification does not establish a protein requirement.
- evidence_id: monocarboxylic-acid
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/25384/
  accessed_at: '2026-10-21T11:09:35.060996Z'
  snapshot_sha256: 342f6e158d906689ac0ad191f2377556d04e221b83c9e43521fb4ceb1a4e2cc4
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines an oxoacid containing a single carboxy group.
    This chemical classification does not establish a protein requirement.
- evidence_id: pyrimidone
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/38337/
  accessed_at: '2026-10-21T11:09:33.993220Z'
  snapshot_sha256: 43a7f8e36b2ee81292e731873258428bead740697d9808a4a2d4eb9407a22eab
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines a pyrimidine carrying one or more oxo substituents.
    This chemical classification does not establish a protein requirement.
- evidence_id: inhibitor-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A11217799%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:57.519605Z'
  snapshot_sha256: 8ef34b3478f482e80f7ef00c134c97a8b2960dd5a305a49821d7c1de87729299
  support: supports
  locator: PMID11217799; DOI10.7164/antibiotics.53.1346; complete indexed abstract
  summary: The complete primary abstract identifies SB-217452 as the serine-linked
    nucleoside portion of albomycin δ2, with potent SerRS inhibition but weak antibacterial
    activity compared with δ2. Ferric and aluminium δ2 complexes were isolated and
    had no SerRS inhibition in that study. This distinguishes released inhibitor,
    intact complexes and whole-cell activity.
- evidence_id: serrs-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A19721072%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:58.092959Z'
  snapshot_sha256: c015e2f522c8b3d466d6fde28af34842229a4a5223ea3be98232c950aa74b1b4
  support: supports
  locator: PMID19721072; DOI10.1128/AAC.00782-09; complete indexed abstract
  summary: The complete primary abstract genetically/biochemically characterizes two
    SerRS proteins in Streptomyces ATCC700974 and their different resistance to SB-217452.
    It supports the bounded inhibitor mechanism, not identical effects of every apo
    desferrialbomycin or an obligatory cofactor requirement.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  locator: Executed 2026-10-21T11:10:52Z through 2026-10-21T11:10:53Z; exit 0
  accessed_at: '2026-10-21T11:10:53Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
    data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml
    data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml
    data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml
    data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml
    data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml
    data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml
  locator: Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0
  accessed_at: '2026-10-21T11:10:31Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml
  locator: Executed 2026-10-21T11:10:53Z through 2026-10-21T11:10:53Z; exit 0
  accessed_at: '2026-10-21T11:10:53Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0
  accessed_at: '2026-10-21T11:10:33Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The complete local YAML denotes a proposed reusable protein requirement
    for desferrialbomycins. CHEBI:83198 identifies its chemical referent or chemical
    class, not an equivalent protein-requirement class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-5
  topic: Chemical identity and protein requirement scope
- area: provenance
  outcome: supported
  summary: 'scripts/seed_chebi_cofactor.py owns the generated target: it selects source
    roles, synthesizes the requirement wrapper, appends chemical text and emits a
    chemical xref. CC BY 4.0 is supported by the official source. Current comparison
    snapshots do not identify the original seed release.'
  evidence_ids:
  - record
  - owner
  - registry
  - chemical-role
  - licence
  - release
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-6
  topic: ChEBI attribution and release provenance
- area: consistency
  outcome: supported
  summary: The inspected source role relation explains selection of the captured local
    broader requirement parent. Chemical-role taxonomy is not automatically a protein-requirement
    hierarchy or true equivalence; this one-record review does not certify the parent.
  evidence_ids:
  - record
  - owner
  - local-parent-1
  - chemical-role
  - siderophore-role
  - cofactor-role
  - local-cofactor-ancestor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-7
  topic: Chemical-role and protein-trait hierarchy
- area: grounding
  outcome: concern
  summary: CHEBI:83198 in xrefs denotes a chemical entity/class, whereas the target
    denotes a protein functional requirement. The schema requires true own-source
    equivalence rather than a chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-8
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: CHEBI:83198 is an iron-free chemical class of pentapeptides with three
    modified L-ornithyl residues, L-seryl and the source-described unusual D-amino-acid/thiofuranose-pyrimidine
    component. The R-group drawing and generalized C36H58N10O17SR formula represent
    variable pyrimidine substitution; they do not define a single fixed-formula molecule
    or all physiological protonation states. The source charge 0 belongs to that drawing.
  evidence_ids:
  - chemical
  - chemical-role
  - pentapeptide
  - hydroxamic-acid
  - thio-ring
  - monocarboxylic-acid
  - pyrimidone
  topic: Desferrialbomycin chemical-class structure and variable substituents
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-9
- area: evidence
  outcome: supported
  summary: The local background explicitly attributes antibacterial activity to iron(III)
    complexes, albomycins. The primaryδ2 / SB-217452 studies distinguish intact metal
    complexes, released nucleoside inhibitor and measured SerRS inhibition. They provide
    a concrete bounded member context, not evidence that all apo-class members directly
    inhibit every SerRS or that intact complexes have the same cell-free action as
    the released moiety.
  evidence_ids:
  - record
  - chemical-role
  - inhibitor-primary
  - serrs-primary
  topic: Intact albomycin complexes versus released inhibitor
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-10
- area: representation
  outcome: unknown
  summary: The siderophore role is authentic source context. Iron transport, antibiotic
    delivery and inhibition by a released moiety are distinct from the non-substrate
    protein requirement asserted by the local wrapper. Neither alternate roles nor
    these assays prove universal absence of cofactor use; no protein is qualified
    here.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - siderophore-role
  - inhibitor-primary
  - serrs-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-83198.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local record denotes a protein requirement for desferrialbomycins,
    while CHEBI:83198 denotes an iron-free R-group chemical class of pentapeptides.
    xrefs conflates the functional requirement with the chemical-class referent.
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
  normalization_reason: A chemical entity/class and a protein requirement for it have
    different denotations. The intended candidate requirement is recoverable through
    correctly typed grounding and activity-relative role adjudication.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:83198
    from trait-equivalence xrefs and preserve the exact source identity through schema-compatible
    grounding. Preserve chemical-source provenance separately from the locally synthesized
    requirement. Before assigning a COFACTOR chemical_participant, adjudicate whether
    the intended activity-relative role satisfies the non-substrate requirement category;
    otherwise retain that uncertainty and use only a supported representation. Do
    not blindly move this own-source association to mapped_xrefs, infer a required
    protein from chemical role alone, or promote SEEDED status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_83198
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves the intended CHEBI:83198 chemical scope without
    asserting equality to a protein requirement.
  - Preserve the variable chemical-class scope and distinguish apo ligands, ferric
    albomycins and released SB-217452. Do not infer a universal formula, protonation
    state, antibacterial mechanism or COFACTOR role from one congener or inhibitor
    experiment.
  - Any typed participant has the supported activity-relative role and exact chemical
    scope; no unreviewed protein example, universal requirement or automatic status
    promotion is introduced.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml.
    These are future curation acceptance checks, not claims that the target has already
    changed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing target
    through an audited route. Run full-corpus just validate-all before merging record
    changes and save a fresh structured scientific review against changed bytes.
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
- The primary papers were inspected at complete indexed-abstract level only. Detailed
  whole-class stereochemical synthesis, every congener and all binding/protonation
  states were not independently experimentally verified; the structural stereochemistry
  is identified as source-encoded. No universal inhibitor/cofactor exclusion is claimed.
tags:
- unreviewed-path-order
- batch-018
- chebi-cofactor
```
