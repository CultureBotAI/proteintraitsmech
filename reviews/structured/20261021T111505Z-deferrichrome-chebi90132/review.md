# Review of requires deferrichrome

- Review: 20261021T111505Z-deferrichrome-chebi90132
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T11:07:28Z
- Finished UTC: 2026-10-21T11:15:05Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The iron-free six-residue deferrichrome identity is supported. One confirmed major finding concerns chemical-to-trait equivalence and one minor finding clarifies ambiguous residue grouping. Protein-specific non-substrate dependence remains unqualified.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 1 in batch 018. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9) covers 168 record paths, leaving 429191 before this batch. 18 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml | generated | requires deferrichrome |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_90132 | CHEBI:90132 resolves and is nonobsolete; exact formula, neutral iron-free structure, sequence, aliases, siderophore role and two structural parents were inspected. The local siderophore/cofactor ancestors and source roles were read. The public 1963 hexapeptide abstract and complete 2006 biosynthesis abstract were inspected within their stated limits. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Chemical identity and protein requirement scope

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The complete local YAML denotes a proposed reusable protein requirement for deferrichrome. CHEBI:90132 identifies its chemical referent or chemical class, not an equivalent protein-requirement class.

### ChEBI attribution and release provenance

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

scripts/seed_chebi_cofactor.py owns the generated target: it selects source roles, synthesizes the requirement wrapper, appends chemical text and emits a chemical xref. CC BY 4.0 is supported by the official source. Current comparison snapshots do not identify the original seed release.

### Chemical-role and protein-trait hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The inspected source role relation explains selection of the captured local broader requirement parent. Chemical-role taxonomy is not automatically a protein-requirement hierarchy or true equivalence; this one-record review does not certify the parent.

### Chemical association versus trait equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

CHEBI:90132 in xrefs denotes a chemical entity/class, whereas the target denotes a protein functional requirement. The schema requires true own-source equivalence rather than a chemical association.

### Deferrichrome residue composition and iron-free state

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

CHEBI:90132 is the neutral iron-free cyclic peptide C27H45N9O12. Its IUPAC sequence and structure contain three glycyl and three N5-acetyl-N5-hydroxy-L-ornithyl residues, with three hydroxamic acid groups. The source synonym explicitly distinguishes ferrichrome without bound iron. No ferric complex or twelve-residue species is identified by the structure.

### Clarity of the cyclic hexapeptide description

nomenclature: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The copied phrase about two units of three glycyl and three ornithyl residues is unnecessarily ambiguous about the grouping. The structure and primary hexapeptide description support six total residues; a twelve-residue interpretation is not established and is not used to declare wrong identity.

### FUNCTION cofactor requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_90132.

The siderophore role and ferrichrome biosynthesis support chemical/biological context. Neither establishes an exact free-ligand non-substrate requirement for a particular protein, nor rules out all such uses. Ferric-complex transport, NRPS production and ligand-dependent activity must remain distinct.

## Findings

### F1: Chemical entity is encoded as equivalent to a protein requirement class

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-90132.chemical-entity-equivalence.

The local requires-deferrichrome class denotes a protein functional requirement, whereas CHEBI:90132 denotes a specific neutral iron-free cyclic hexapeptide. xrefs equates these different entity types.

### F2: Clarify the six-residue composition

minor / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-90132.hexapeptide-wording.

The definition reproduces source wording about two units of three glycyl and three modified ornithyl residues. It can obscure whether those are two groups of three or a repeated six-residue block. The actual source sequence/structure and primary ferrichrome hexapeptide description support three residues of each kind, six total. This is a wording defect, not evidence of a different twelve-residue chemical.

## Recommended Actions And Acceptance Checks

### A1

Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:90132 from trait-equivalence xrefs and preserve the exact source identity through schema-compatible grounding. Preserve chemical-source provenance separately from the locally synthesized requirement. Before assigning a COFACTOR chemical_participant, adjudicate whether the intended activity-relative role satisfies the non-substrate requirement category; otherwise retain that uncertainty and use only a supported representation. Do not blindly move this own-source association to mapped_xrefs, infer a required protein from chemical role alone, or promote SEEDED status.

- The regenerated target preserves the intended CHEBI:90132 chemical scope without asserting equality to a protein requirement.
- Preserve the iron-free ligand, specified L-ornithyl stereochemistry and six-residue identity. Do not substitute ferrichrome iron complexes or treat biosynthetic production/transport as proof of a non-substrate protein requirement.
- Any typed participant has the supported activity-relative role and exact chemical scope; no unreviewed protein example, universal requirement or automatic status promotion is introduced.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml. These are future curation acceptance checks, not claims that the target has already changed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

### A2

In the maintained source-text transform or a registered, provenance-bearing override consumed by scripts/seed_chebi_cofactor.py, state explicitly that the iron-free cyclic hexapeptide contains three glycyl and three N5-acetyl-N5-hydroxy-L-ornithyl residues. Preserve the source quote as source context if retained; distinguish the clarified curator wording from upstream text.

- The regenerated definition gives six total residues and preserves the three specified modified L-ornithyl residues, iron-free identity and source provenance.
- No doubled peptide, new chemical ID or altered cofactor claim is introduced.
- After repair run just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml. These are future curation acceptance checks, not claims that the target has already changed.
- For maintained Python/writer changes add focused pytest coverage, then run just lint, just test and just audit-writers. Regenerate the scoped existing target through an audited route. Run full-corpus just validate-all before merging record changes and save a fresh structured scientific review against changed bytes.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing | supports | The official ChEBI Introduction defines its chemical entities and chemical classes. Licensing makes website data available under CC BY 4.0. This supports source licensing, not the locally synthesized protein-requirement claim. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Its original access timestamp is preserved. It is comparison-ontology metadata, not a release assignment for live backend responses or the original seed. |
| chemical | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_90132; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:90132 to nonobsolete deferrichrome. The actual definition, identifiers, aliases and chemical annotations were inspected; the source term denotes chemistry rather than a protein requirement. |
| chemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/90132/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The complete target chemical response was inspected: exact name, definition, formula/charge or R-group class representation, stereochemical encoding, aliases and incoming/outgoing relations. The source chemical role supplies candidate context and does not qualify a protein. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | ChEBI cofactor is a biochemical role for an organic molecule or ion required by an enzyme. The role is not a protein-requirement class. |
| local-cofactor-ancestor | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire captured ancestor YAML | supports | The fully captured broader cofactor-requirement ancestor was read. Its local requirement definition, ChEBI role xref and SEEDED status are context; this review does not certify that ancestor. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The source role describes microbial iron(III) chelation for transport and sequestration. Its outgoing is-a relations include cofactor, iron(3+) chelator and iron ionophore. This authentic source hierarchy is distinct from proof of non-substrate dependence in a protein. |
| cyclic-peptide | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24613/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines a cyclic peptide whose ring consists solely of amino-acid residues joined by peptide linkages. |
| macrocycle | https://www.ebi.ac.uk/chebi/backend/api/public/compound/51026/; Actual name, definition, names, chemical_data, default_structure and ontology_relations as applicable | supports | The structural parent defines a cyclic system with at least nine ring atoms; it is chemical taxonomy, not protein evidence. |
| hexapeptide-primary | https://www.nature.com/articles/200167a0?error=cookies_not_supported&amp;code=bc08522d-8d5e-4299-9e8e-873cd3f60e05; DOI10.1038/200167a0; complete public abstract, not subscription full text | supports | The complete publicly accessible primary abstract describes ferrichrome as a cyclic hexapeptide with three glycine and three hydroxylated ornithine residues, and proposes the corresponding grouped sequence. This concerns the peptide portion of the ferric trihydroxamate; source 90132 establishes the iron-free ligand identity. |
| biosynthesis-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A16502473%20AND%20SRC%3AMED&amp;format=json&amp;resultType=core; PMID16502473; DOI10.1002/cbic.200500301; complete indexed abstract | supports | The complete primary abstract reports an S. pombe NRPS producing cyclohexapeptide ferrichrome. Its substrate-binding specificities were assigned by molecular modelling. Production and biosynthetic-substrate context do not qualify a protein requiring free deferrichrome as a non-substrate cofactor. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; Executed 2026-10-21T11:10:50Z through 2026-10-21T11:10:50Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml data/traits/function/cofactor_requirement/chebi/dehydro-d-arabinono-1-4-lactone-chebi17803.yaml data/traits/function/cofactor_requirement/chebi/desferrialbomycins-chebi83198.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-3-chebi83127.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-3-chebi133862.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-b-chebi133861.yaml data/traits/function/cofactor_requirement/chebi/desferricoprogen-chebi83125.yaml data/traits/function/cofactor_requirement/chebi/desferriexochelin-772ms-chebi61152.yaml data/traits/function/cofactor_requirement/chebi/desferrimycobactin-t-chebi61168.yaml data/traits/function/cofactor_requirement/chebi/desferrioxamine-b-3-chebi84700.yaml; Executed 2026-10-21T11:08:13Z through 2026-10-21T11:10:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml; Executed 2026-10-21T11:10:50Z through 2026-10-21T11:10:51Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T11:10:31Z through 2026-10-21T11:10:33Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The Nature article was inspected at complete public-abstract level only; the 2006 paper at complete indexed-abstract level. Neither is used to infer universal biosynthetic substrate specificity or exact-ligand protein dependence. No twelve-residue identity error is asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T111505Z-deferrichrome-chebi90132
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires deferrichrome
started_at: '2026-10-21T11:07:28Z'
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
summary: The iron-free six-residue deferrichrome identity is supported. One confirmed
  major finding concerns chemical-to-trait equivalence and one minor finding clarifies
  ambiguous residue grouping. Protein-specific non-substrate dependence remains unqualified.
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
  - path: data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
    sha256: 8fa12f266e2453d3cfaba9f3506452ff4800e91bc0734eca604ae50a498dc968
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
  selection: Path-order position 1 in batch 018. Fresh main inventory has 429359 records;
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
targets:
- kind: generated
  label: requires deferrichrome
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_90132
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: CHEBI:90132 resolves and is nonobsolete; exact formula, neutral iron-free
    structure, sequence, aliases, siderophore role and two structural parents were
    inspected. The local siderophore/cofactor ancestors and source roles were read.
    The public 1963 hexapeptide abstract and complete 2006 biosynthesis abstract were
    inspected within their stated limits.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  evidence_ids:
  - chemical
  - chemical-role
  - cofactor-role
  - licence
  - release
  - siderophore-role
  - cyclic-peptide
  - macrocycle
  - hexapeptide-primary
  - biosynthesis-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T11:07:28Z'
  snapshot_sha256: 8fa12f266e2453d3cfaba9f3506452ff4800e91bc0734eca604ae50a498dc968
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
  accessed_at: '2026-10-21T11:07:28Z'
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
  accessed_at: '2026-10-21T11:07:28Z'
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
  accessed_at: '2026-10-21T11:07:28Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T11:07:28Z'
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
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FCHEBI_90132
  accessed_at: '2026-10-21T11:07:59.477783Z'
  snapshot_sha256: 5394a8fe447a10d95851f91ab2bac648237b9750c34839eb783159c170c5665f
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:90132 to nonobsolete deferrichrome. The actual definition,
    identifiers, aliases and chemical annotations were inspected; the source term
    denotes chemistry rather than a protein requirement.
- evidence_id: chemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/90132/
  accessed_at: '2026-10-21T11:07:59.661470Z'
  snapshot_sha256: 43a98c9dc374a79365dd55e6e19bf19f36ac8a29162ee1f2065607e30289d215
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
  accessed_at: '2026-10-21T11:07:28Z'
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
- evidence_id: cyclic-peptide
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24613/
  accessed_at: '2026-10-21T11:09:32.239358Z'
  snapshot_sha256: 2e18308d9a954aa3c16c9de0b05752e7748c57855ab6b7e9ec4f62032c853564
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines a cyclic peptide whose ring consists solely
    of amino-acid residues joined by peptide linkages.
- evidence_id: macrocycle
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/51026/
  accessed_at: '2026-10-21T11:09:32.393064Z'
  snapshot_sha256: 1cadb78bef0b4baceb8f03f1ee7f7065056985f8abb1a3e35ddf4f343043d4c4
  support: supports
  locator: Actual name, definition, names, chemical_data, default_structure and ontology_relations
    as applicable
  summary: The structural parent defines a cyclic system with at least nine ring atoms;
    it is chemical taxonomy, not protein evidence.
- evidence_id: hexapeptide-primary
  kind: primary_source
  reference: https://www.nature.com/articles/200167a0?error=cookies_not_supported&code=bc08522d-8d5e-4299-9e8e-873cd3f60e05
  accessed_at: '2026-10-21T11:09:35.261120Z'
  snapshot_sha256: 990ca02869aa7d94f58e556854f425a3388a018d7a6af892ec9c7b4668268f74
  support: supports
  locator: DOI10.1038/200167a0; complete public abstract, not subscription full text
  summary: The complete publicly accessible primary abstract describes ferrichrome
    as a cyclic hexapeptide with three glycine and three hydroxylated ornithine residues,
    and proposes the corresponding grouped sequence. This concerns the peptide portion
    of the ferric trihydroxamate; source 90132 establishes the iron-free ligand identity.
- evidence_id: biosynthesis-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A16502473%20AND%20SRC%3AMED&format=json&resultType=core
  accessed_at: '2026-10-21T11:09:57.519903Z'
  snapshot_sha256: 11aa8ac42aa92a2910804ee2a6b264c0a192d52c71880dc994a9b437b451ca89
  support: supports
  locator: PMID16502473; DOI10.1002/cbic.200500301; complete indexed abstract
  summary: The complete primary abstract reports an S. pombe NRPS producing cyclohexapeptide
    ferrichrome. Its substrate-binding specificities were assigned by molecular modelling.
    Production and biosynthetic-substrate context do not qualify a protein requiring
    free deferrichrome as a non-substrate cofactor.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  locator: Executed 2026-10-21T11:10:50Z through 2026-10-21T11:10:50Z; exit 0
  accessed_at: '2026-10-21T11:10:50Z'
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
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml
  locator: Executed 2026-10-21T11:10:50Z through 2026-10-21T11:10:51Z; exit 0
  accessed_at: '2026-10-21T11:10:51Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The complete local YAML denotes a proposed reusable protein requirement
    for deferrichrome. CHEBI:90132 identifies its chemical referent or chemical class,
    not an equivalent protein-requirement class.
  evidence_ids:
  - record
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-7
  topic: Chemical-role and protein-trait hierarchy
- area: grounding
  outcome: concern
  summary: CHEBI:90132 in xrefs denotes a chemical entity/class, whereas the target
    denotes a protein functional requirement. The schema requires true own-source
    equivalence rather than a chemical association.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-role
  - owner
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-8
  topic: Chemical association versus trait equivalence
- area: evidence
  outcome: supported
  summary: CHEBI:90132 is the neutral iron-free cyclic peptide C27H45N9O12. Its IUPAC
    sequence and structure contain three glycyl and three N5-acetyl-N5-hydroxy-L-ornithyl
    residues, with three hydroxamic acid groups. The source synonym explicitly distinguishes
    ferrichrome without bound iron. No ferric complex or twelve-residue species is
    identified by the structure.
  evidence_ids:
  - chemical
  - chemical-role
  - cyclic-peptide
  - macrocycle
  - hexapeptide-primary
  topic: Deferrichrome residue composition and iron-free state
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-9
- area: nomenclature
  outcome: concern
  summary: The copied phrase about two units of three glycyl and three ornithyl residues
    is unnecessarily ambiguous about the grouping. The structure and primary hexapeptide
    description support six total residues; a twelve-residue interpretation is not
    established and is not used to declare wrong identity.
  evidence_ids:
  - record
  - chemical-role
  - hexapeptide-primary
  topic: Clarity of the cyclic hexapeptide description
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-10
- area: representation
  outcome: unknown
  summary: The siderophore role and ferrichrome biosynthesis support chemical/biological
    context. Neither establishes an exact free-ligand non-substrate requirement for
    a particular protein, nor rules out all such uses. Ferric-complex transport, NRPS
    production and ligand-dependent activity must remain distinct.
  evidence_ids:
  - record
  - schema
  - chemical-role
  - siderophore-role
  - biosynthesis-primary
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  assessment_id: assessment-11
  topic: FUNCTION cofactor requirement representation
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-90132.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is encoded as equivalent to a protein requirement class
  description: The local requires-deferrichrome class denotes a protein functional
    requirement, whereas CHEBI:90132 denotes a specific neutral iron-free cyclic hexapeptide.
    xrefs equates these different entity types.
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
- issue_key: chebi.cofactor-requirement.CHEBI-90132.hexapeptide-wording
  category: nomenclature
  severity: minor
  title: Clarify the six-residue composition
  description: The definition reproduces source wording about two units of three glycyl
    and three modified ornithyl residues. It can obscure whether those are two groups
    of three or a repeated six-residue block. The actual source sequence/structure
    and primary ferrichrome hexapeptide description support three residues of each
    kind, six total. This is a wording defect, not evidence of a different twelve-residue
    chemical.
  evidence_ids:
  - record
  - chemical-role
  - hexapeptide-primary
  certainty: confirmed
  field_paths:
  - definition
  normalization_reason: The exact chemical identity remains recoverable from label,
    ID and structure; clarifying ambiguous grouping is a bounded non-blocking wording
    repair.
  finding_id: F2
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
actions:
- action_id: A1
  description: Update build() in scripts/seed_chebi_cofactor.py to remove CHEBI:90132
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target preserves the intended CHEBI:90132 chemical scope without
    asserting equality to a protein requirement.
  - Preserve the iron-free ligand, specified L-ornithyl stereochemistry and six-residue
    identity. Do not substitute ferrichrome iron complexes or treat biosynthetic production/transport
    as proof of a non-substrate protein requirement.
  - Any typed participant has the supported activity-relative role and exact chemical
    scope; no unreviewed protein example, universal requirement or automatic status
    promotion is introduced.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml.
    These are future curation acceptance checks, not claims that the target has already
    changed.
  - For maintained Python/writer changes add focused pytest coverage, then run just
    lint, just test and just audit-writers. Regenerate the scoped existing target
    through an audited route. Run full-corpus just validate-all before merging record
    changes and save a fresh structured scientific review against changed bytes.
- action_id: A2
  description: In the maintained source-text transform or a registered, provenance-bearing
    override consumed by scripts/seed_chebi_cofactor.py, state explicitly that the
    iron-free cyclic hexapeptide contains three glycyl and three N5-acetyl-N5-hydroxy-L-ornithyl
    residues. Preserve the source quote as source context if retained; distinguish
    the clarified curator wording from upstream text.
  finding_ids:
  - F2
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_90132
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated definition gives six total residues and preserves the three specified
    modified L-ornithyl residues, iron-free identity and source provenance.
  - No doubled peptide, new chemical ID or altered cofactor claim is introduced.
  - After repair run just validate data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/deferrichrome-chebi90132.yaml.
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
- The Nature article was inspected at complete public-abstract level only; the 2006
  paper at complete indexed-abstract level. Neither is used to infer universal biosynthetic
  substrate specificity or exact-ligand protein dependence. No twelve-residue identity
  error is asserted.
tags:
- unreviewed-path-order
- batch-018
- chebi-cofactor
```
