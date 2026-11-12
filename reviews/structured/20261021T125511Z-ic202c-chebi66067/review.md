# Review of requires IC202C

- Review: 20261021T125511Z-ic202c-chebi66067
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T12:45:42Z
- Finished UTC: 2026-10-21T12:55:11Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

IC202C identity, unspecified aldoxime geometry and bounded isolation/MLCR evidence are supported. One confirmed major finding concerns chemical-to-protein-requirement equivalence. Siderophore activity is not automatically a qualified non-substrate protein requirement.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 5 in batch 024. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242) covers 228 record paths, leaving 429131 before this batch. 24 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml | generated | requires IC202C |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_66067 | Official backend and nonobsolete OLS resolve IC202C; source structural/role parents and licence were inspected. The actual primary IC202 papers support the bounded structure/isolation/MLCR claims. Unspecified oxime geometry is retained in accordance with the primary mixture report. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### IC202C aldoxime identity and unspecified geometry

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The target name, aldoxime definition and exact free-ligand source identity agree. The primary study reports an approximately 1:1 syn/anti mixture, so the source does not warrant silently choosing one E/Z structure. Net-zero source drawing, lack of iron and unspecified geometry remain distinct from a ferric complex or an in vivo protonation assignment.

### IC202C isolation, structure and iron-sensitive MLCR inhibition

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The complete primary paper supports the producing strain, aldoxime structural work, mixture and cell-culture inhibition. FeCl3 abrogation supports the authors’ iron-chelation interpretation under the tested conditions. It does not identify a protein whose catalytic activity requires IC202C as a non-substrate.

### Siderophore role versus non-substrate protein requirement

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The source siderophore role and cell-culture evidence are authentic. Iron transport/sequestration, chelation, biosynthesis and inhibitory phenotypes are not automatically demonstrations of an enzyme requiring the free chemical as a non-substrate. This record does not qualify a particular protein, bound chemical state or obligatory activity dependence, and the review makes no universal claim of cofactor absence.

### Siderophore parent and source role hierarchy

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The local siderophore-requirement parent resolves, and the source explicitly places siderophore under cofactor. That authentic source relation explains selection; it neither changes a chemical role into a protein class nor independently proves all native non-substrate requirement semantics. Structural chemical parents are not automatically additional protein parents.

### Chemical entity versus protein requirement

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

CHEBI:66067 denotes the IC202C aldoxime chemical entity, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Accurate source identity and an authentic source role do not make the chemical entity identical to the protein requirement class.

### Source attribution, licence and maintained emitter

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_66067.

The captured ChEBI seeder explains the synthesized requirement prefix, appended chemical text, role-derived parent and emitted chemical xref. The official licence is CC BY 4.0. The source chemical statement is attributable to ChEBI; the protein-requirement transformation is local and is not independently supplied by that attribution. Live backend and OLS version 256 are retained as comparison snapshots, with the original seed release unknown.

## Findings

### F1: Chemical source entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-66067.chemical-entity-equivalence.

CHEBI:66067 denotes the IC202C aldoxime chemical entity, whereas the local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot asserts true own-source equivalence. Accurate source identity and an authentic source role do not make the chemical entity identical to the protein requirement class.

## Recommended Actions And Acceptance Checks

### A1

Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait equality while preserving the exact supported chemical scope and source provenance. Preserve the IC202C aldoxime identity and unspecified syn/anti geometry; do not silently choose an isomer or substitute a ferric complex. Adjudicate the intended activity-relative role, distinguishing iron-chelation/culture effects from a non-substrate enzyme requirement. If the activity-relative role and chemical state are supported, an optional chemical_participants association with role COFACTOR may be used; otherwise preserve provenance and explicit uncertainty without inventing a participant. Do not move the same equality to mapped_xrefs, merge distinct chemical states, require optional examples or promote native status.

- Regenerated xrefs no longer equates the source chemical with the protein requirement. Exact chemical provenance and the intended requirement scope remain explicit.
- Any optional participant is a separately justified chemical entity with an activity-relative role; absence of optional participants or examples is not itself a defect.
- After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml; just validate-all data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml; and just audit-graphs data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml.
- For maintained writer changes add focused regression coverage and run just audit-writers, just lint and just test. Regenerate this existing target through an audited scoped route. Run full just validate-all before merging record changes, recapture changed inputs and save a fresh structured review without overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections | supports | The inspected official Introduction and Licensing sections describe ChEBI chemical entities and roles and establish CC BY 4.0 licensing. This supports chemical-source provenance, not equivalence with a protein requirement. |
| release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16. Its original access time is retained. The live backend snapshot and OLS release are distinct; neither identifies the original seed release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/66067/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | CHEBI:66067 is IC202C, C23H44N6O7, net 0, with a primary amine, two N-hydroxyamide groups and a terminal aldoxime. The SMILES/InChI and name do not specify syn/anti or E/Z geometry. No iron atom is included. Source roles are siderophore, immunosuppressive, antimicrobial and metabolite, with hydroxamic-acid, primary-amino and aliphatic-aldoxime ancestry. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:66067; Inspected source response captured at the recorded UTC time | supports | OLS resolves CHEBI:66067 as nonobsolete. The actual name, definition, synonyms and formula/charge/SMILES/InChI annotations were inspected against the backend, including any explicitly described disagreement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | CHEBI:23357 is the biochemical role cofactor, defined for an organic molecule or ion required by an enzyme for activity. It is under biochemical role CHEBI:52206, not a protein class. Source role membership supplies candidate context rather than a qualified exact-state protein requirement. |
| siderophore-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Siderophore CHEBI:26672 is defined for microbial low-molecular-mass iron(III) chelators used in transport and sequestration. Its direct source parents include cofactor, iron(III) chelator and iron ionophore. This is an authentic source role hierarchy, not proof that a protein requires a free siderophore as a non-substrate enzyme cofactor. |
| hydroxamate-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Hydroxamic acid CHEBI:24650 describes N-hydroxyamide chemistry and derivatives; its conjugate-base class is hydroxamic acid anion. Fixed chemical data are null, so the exact target structure supplies the number and state of its N-hydroxyamide groups. |
| amino-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/50994/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Primary amino compound CHEBI:50994 is defined by replacing one ammonia hydrogen with an organyl group. This supports the free primary amino group in the source drawing, not a measured physiological protonation population. |
| terminal-parent | https://www.ebi.ac.uk/chebi/backend/api/public/compound/82744/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Aliphatic aldoxime CHEBI:82744 is an aldoxime derived from an aliphatic aldehyde. Its generic formula does not impose an E/Z isomer on IC202C. |
| immune-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/35705/; Inspected exact identity, definition or null, names, chemical data, structure and complete outgoing relations; target incoming context inspected separately | supports | Immunosuppressive agent CHEBI:35705 is a biological activity role, not a claim that its chemical bearer is an obligatory protein cofactor. |
| ic202bc-full | https://www.jstage.jst.go.jp/article/antibiotics1968/52/9/52_9_775/_pdf; Primary PDF main text pp.775–780, particularly IC202C structure pp.778–779, Table 2 and biological activities/Table 3 pp.779–780 | supports | Iijima et al., DOI:10.7164/antibiotics.52.775, pp.775–780. The actual primary PDF reports IC202B/C isolation from Streptoalloteichus sp.1454-19 and NMR/FAB-MS structure work. IC202C is an approximately 1:1 syn/anti aldoxime mixture; attempted separation failed. In MLCR, B and C had IC50 1.6 µg/ml. At 25 µg/ml compound, only FeCl3 among the tested 100 µM metal salts abrogated suppression; the authors infer an iron-chelation contribution. These cell-culture effects are not an exact protein non-substrate requirement assay. |
| ic202bc-abstract | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10726924%20AND%20SRC%3AMED&amp;resultType=core&amp;format=json; Verified PMID/DOI and complete indexed abstract; full article not inspected unless a separate full-text evidence entry is cited | supports | PMID:10726924; DOI:10.7164/antibiotics.52.775. The complete indexed abstract confirms IC202B/C isolation from Streptoalloteichus sp.1454-19, NMR/FAB-MS structure elucidation and MLCR IC50 1.6 µg/ml. Detailed syn/anti and metal-suppression claims are grounded in the separately captured full PDF, not inferred from this abstract. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml; Executed 2026-10-21T12:46:11Z through 2026-10-21T12:46:13Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml; Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml; Executed 2026-10-21T12:46:13Z through 2026-10-21T12:46:13Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The source drawing is a free ligand, not an iron complex or a measured physiological protonation distribution. The primary cell-culture experiments do not by themselves establish transport kinetics, a target protein, a universal antimicrobial spectrum or a non-substrate cofactor requirement.
- The IC202C biosynthesis and ribonucleotide-reductase citation records PMID:11217808 and PMID:11592505 supplied no indexed abstracts in the inspected responses. Their titles are not used to infer a mechanism, protein requirement or direct enzyme inhibition result. No E/Z-specific activity is assigned to either member of the reported mixture.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T125511Z-ic202c-chebi66067
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires IC202C
started_at: '2026-10-21T12:45:42Z'
finished_at: '2026-10-21T12:55:11Z'
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
summary: IC202C identity, unspecified aldoxime geometry and bounded isolation/MLCR
  evidence are supported. One confirmed major finding concerns chemical-to-protein-requirement
  equivalence. Siderophore activity is not automatically a qualified non-substrate
  protein requirement.
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
  - path: data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
    sha256: 846175c470cd997fa62b503af9dae6dab71875e835a6c5349875ca313c58ab6f
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
  selection: Path-order position 5 in batch 024. Fresh main inventory has 429359 records;
    union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242)
    covers 228 record paths, leaving 429131 before this batch. 24 inventories were
    combined. Published branch coverage is not described as merged main. Snapshot-row
    context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
targets:
- kind: generated
  label: requires IC202C
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_66067
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official backend and nonobsolete OLS resolve IC202C; source structural/role
    parents and licence were inspected. The actual primary IC202 papers support the
    bounded structure/isolation/MLCR claims. Unspecified oxime geometry is retained
    in accordance with the primary mixture report.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - licence
  - release
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T12:45:42Z'
  snapshot_sha256: 846175c470cd997fa62b503af9dae6dab71875e835a6c5349875ca313c58ab6f
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
  accessed_at: '2026-10-21T12:45:42Z'
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
  accessed_at: '2026-10-21T12:45:42Z'
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
  accessed_at: '2026-10-21T12:45:42Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/siderophore-chebi26672.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T12:45:42Z'
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
  summary: The inspected official Introduction and Licensing sections describe ChEBI
    chemical entities and roles and establish CC BY 4.0 licensing. This supports chemical-source
    provenance, not equivalence with a protein requirement.
- evidence_id: release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Digest-verified reused OLS metadata reports ChEBI version 256, loaded 2026-10-16.
    Its original access time is retained. The live backend snapshot and OLS release
    are distinct; neither identifies the original seed release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/66067/
  accessed_at: '2026-10-21T12:46:36.684781Z'
  snapshot_sha256: ca04e27ee02fcfe5abdb4ca9772bac64c4d12ee5c7dc3247dd9de99087dc939c
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: CHEBI:66067 is IC202C, C23H44N6O7, net 0, with a primary amine, two N-hydroxyamide
    groups and a terminal aldoxime. The SMILES/InChI and name do not specify syn/anti
    or E/Z geometry. No iron atom is included. Source roles are siderophore, immunosuppressive,
    antimicrobial and metabolite, with hydroxamic-acid, primary-amino and aliphatic-aldoxime
    ancestry.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:66067
  accessed_at: '2026-10-21T12:46:36.552198Z'
  snapshot_sha256: 366d6ad4dbf8ba0bd5689ac59c03e12155ccbc5988fe5ff61008fd72938170dd
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves CHEBI:66067 as nonobsolete. The actual name, definition, synonyms
    and formula/charge/SMILES/InChI annotations were inspected against the backend,
    including any explicitly described disagreement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: CHEBI:23357 is the biochemical role cofactor, defined for an organic molecule
    or ion required by an enzyme for activity. It is under biochemical role CHEBI:52206,
    not a protein class. Source role membership supplies candidate context rather
    than a qualified exact-state protein requirement.
- evidence_id: siderophore-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26672/
  accessed_at: '2026-10-21T12:46:36.724992Z'
  snapshot_sha256: 1ac432c5ea916b157a4b958e8c38d8b955ede686142c49ead9c1e2ed5713154b
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Siderophore CHEBI:26672 is defined for microbial low-molecular-mass iron(III)
    chelators used in transport and sequestration. Its direct source parents include
    cofactor, iron(III) chelator and iron ionophore. This is an authentic source role
    hierarchy, not proof that a protein requires a free siderophore as a non-substrate
    enzyme cofactor.
- evidence_id: hydroxamate-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24650/
  accessed_at: '2026-10-21T12:47:42.051321Z'
  snapshot_sha256: 489ee6f999b8a733ab1e6334c09f36828ec55ecae22082aca866ad781b0861bf
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Hydroxamic acid CHEBI:24650 describes N-hydroxyamide chemistry and derivatives;
    its conjugate-base class is hydroxamic acid anion. Fixed chemical data are null,
    so the exact target structure supplies the number and state of its N-hydroxyamide
    groups.
- evidence_id: amino-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/50994/
  accessed_at: '2026-10-21T12:47:42.607536Z'
  snapshot_sha256: cb33882973f24845f2fc7b638dee070ab8d0937558e93e1a60f80b284b9ada8d
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Primary amino compound CHEBI:50994 is defined by replacing one ammonia
    hydrogen with an organyl group. This supports the free primary amino group in
    the source drawing, not a measured physiological protonation population.
- evidence_id: terminal-parent
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/82744/
  accessed_at: '2026-10-21T12:47:42.748882Z'
  snapshot_sha256: 3709efa8da238bc520ddaa264ce40a19f56c68f6a3314661031ce54e38f42d84
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Aliphatic aldoxime CHEBI:82744 is an aldoxime derived from an aliphatic
    aldehyde. Its generic formula does not impose an E/Z isomer on IC202C.
- evidence_id: immune-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/35705/
  accessed_at: '2026-10-21T12:47:44.147534Z'
  snapshot_sha256: df871c5096cde1d3a119851a1ef0fad07662fea860a627e82f85e37cd4d56b88
  support: supports
  locator: Inspected exact identity, definition or null, names, chemical data, structure
    and complete outgoing relations; target incoming context inspected separately
  summary: Immunosuppressive agent CHEBI:35705 is a biological activity role, not
    a claim that its chemical bearer is an obligatory protein cofactor.
- evidence_id: ic202bc-full
  kind: primary_source
  reference: https://www.jstage.jst.go.jp/article/antibiotics1968/52/9/52_9_775/_pdf
  accessed_at: '2026-10-21T12:48:15.324338Z'
  snapshot_sha256: 062ea1c262c27dade17dc6caac5555be5535a73ddb2b4f71aee82f2e4b0747a6
  support: supports
  locator: Primary PDF main text pp.775–780, particularly IC202C structure pp.778–779,
    Table 2 and biological activities/Table 3 pp.779–780
  summary: Iijima et al., DOI:10.7164/antibiotics.52.775, pp.775–780. The actual primary
    PDF reports IC202B/C isolation from Streptoalloteichus sp.1454-19 and NMR/FAB-MS
    structure work. IC202C is an approximately 1:1 syn/anti aldoxime mixture; attempted
    separation failed. In MLCR, B and C had IC50 1.6 µg/ml. At 25 µg/ml compound,
    only FeCl3 among the tested 100 µM metal salts abrogated suppression; the authors
    infer an iron-chelation contribution. These cell-culture effects are not an exact
    protein non-substrate requirement assay.
- evidence_id: ic202bc-abstract
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A10726924%20AND%20SRC%3AMED&resultType=core&format=json
  accessed_at: '2026-10-21T12:47:44.276176Z'
  snapshot_sha256: 2c896f2bfe06b15911ff65103ade952ffb5da2b81def6c5eafa7e7cb940cfb3f
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full article not inspected
    unless a separate full-text evidence entry is cited
  summary: PMID:10726924; DOI:10.7164/antibiotics.52.775. The complete indexed abstract
    confirms IC202B/C isolation from Streptoalloteichus sp.1454-19, NMR/FAB-MS structure
    elucidation and MLCR IC50 1.6 µg/ml. Detailed syn/anti and metal-suppression claims
    are grounded in the separately captured full PDF, not inferred from this abstract.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  locator: Executed 2026-10-21T12:46:11Z through 2026-10-21T12:46:13Z; exit 0
  accessed_at: '2026-10-21T12:46:13Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/hydrogencarbonate-chebi17544.yaml
    data/traits/function/cofactor_requirement/chebi/hydrogenphosphate-chebi43474.yaml
    data/traits/function/cofactor_requirement/chebi/hydroquinone-chebi17594.yaml data/traits/function/cofactor_requirement/chebi/ic202a-chebi66065.yaml
    data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml data/traits/function/cofactor_requirement/chebi/iron-2-chebi29033.yaml
    data/traits/function/cofactor_requirement/chebi/iron-3-chebi29034.yaml data/traits/function/cofactor_requirement/chebi/iron-cation-chebi24875.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-iron-cofactor-chebi60504.yaml
    data/traits/function/cofactor_requirement/chebi/iron-sulfur-molybdenum-cofactor-chebi30409.yaml
  locator: Executed 2026-10-21T12:46:01Z through 2026-10-21T12:48:55Z; exit 0
  accessed_at: '2026-10-21T12:48:55Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml
  locator: Executed 2026-10-21T12:46:13Z through 2026-10-21T12:46:13Z; exit 0
  accessed_at: '2026-10-21T12:46:13Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T12:48:56Z through 2026-10-21T12:48:57Z; exit 0
  accessed_at: '2026-10-21T12:48:57Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The target name, aldoxime definition and exact free-ligand source identity
    agree. The primary study reports an approximately 1:1 syn/anti mixture, so the
    source does not warrant silently choosing one E/Z structure. Net-zero source drawing,
    lack of iron and unspecified geometry remain distinct from a ferric complex or
    an in vivo protonation assignment.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - terminal-parent
  - ic202bc-full
  topic: IC202C aldoxime identity and unspecified geometry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The complete primary paper supports the producing strain, aldoxime structural
    work, mixture and cell-culture inhibition. FeCl3 abrogation supports the authors’
    iron-chelation interpretation under the tested conditions. It does not identify
    a protein whose catalytic activity requires IC202C as a non-substrate.
  evidence_ids:
  - ic202bc-full
  - ic202bc-abstract
  - siderophore-role
  topic: IC202C isolation, structure and iron-sensitive MLCR inhibition
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The source siderophore role and cell-culture evidence are authentic. Iron
    transport/sequestration, chelation, biosynthesis and inhibitory phenotypes are
    not automatically demonstrations of an enzyme requiring the free chemical as a
    non-substrate. This record does not qualify a particular protein, bound chemical
    state or obligatory activity dependence, and the review makes no universal claim
    of cofactor absence.
  evidence_ids:
  - record
  - schema
  - chemical
  - siderophore-role
  - ic202bc-full
  topic: Siderophore role versus non-substrate protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The local siderophore-requirement parent resolves, and the source explicitly
    places siderophore under cofactor. That authentic source relation explains selection;
    it neither changes a chemical role into a protein class nor independently proves
    all native non-substrate requirement semantics. Structural chemical parents are
    not automatically additional protein parents.
  evidence_ids:
  - record
  - local-parent-1
  - chemical
  - siderophore-role
  - cofactor-role
  - owner
  topic: Siderophore parent and source role hierarchy
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-8
- area: grounding
  outcome: concern
  summary: CHEBI:66067 denotes the IC202C aldoxime chemical entity, whereas the local
    COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs slot
    asserts true own-source equivalence. Accurate source identity and an authentic
    source role do not make the chemical entity identical to the protein requirement
    class.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - ic202bc-full
  - siderophore-role
  topic: Chemical entity versus protein requirement
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-9
- area: provenance
  outcome: supported
  summary: The captured ChEBI seeder explains the synthesized requirement prefix,
    appended chemical text, role-derived parent and emitted chemical xref. The official
    licence is CC BY 4.0. The source chemical statement is attributable to ChEBI;
    the protein-requirement transformation is local and is not independently supplied
    by that attribution. Live backend and OLS version 256 are retained as comparison
    snapshots, with the original seed release unknown.
  evidence_ids:
  - record
  - owner
  - registry
  - licence
  - release
  - chemical
  topic: Source attribution, licence and maintained emitter
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-66067.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical source entity is asserted equivalent to a protein requirement
  description: CHEBI:66067 denotes the IC202C aldoxime chemical entity, whereas the
    local COFACTOR_REQ identifier denotes a protein functional requirement. The xrefs
    slot asserts true own-source equivalence. Accurate source identity and an authentic
    source role do not make the chemical entity identical to the protein requirement
    class.
  evidence_ids:
  - record
  - schema
  - chemical
  - chemical-ontology
  - owner
  - ic202bc-full
  - siderophore-role
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical entity and synthesized protein-requirement class
    have different denotations. This is a major grounding defect independent of biological
    relevance or the presence of optional representations.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Update build in scripts/seed_chebi_cofactor.py to remove chemical-to-protein-trait
    equality while preserving the exact supported chemical scope and source provenance.
    Preserve the IC202C aldoxime identity and unspecified syn/anti geometry; do not
    silently choose an isomer or substitute a ferric complex. Adjudicate the intended
    activity-relative role, distinguishing iron-chelation/culture effects from a non-substrate
    enzyme requirement. If the activity-relative role and chemical state are supported,
    an optional chemical_participants association with role COFACTOR may be used;
    otherwise preserve provenance and explicit uncertainty without inventing a participant.
    Do not move the same equality to mapped_xrefs, merge distinct chemical states,
    require optional examples or promote native status.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_66067
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - Regenerated xrefs no longer equates the source chemical with the protein requirement.
    Exact chemical provenance and the intended requirement scope remain explicit.
  - Any optional participant is a separately justified chemical entity with an activity-relative
    role; absence of optional participants or examples is not itself a defect.
  - After the scoped repair run just validate data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml;
    just validate-all data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml;
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/ic202c-chebi66067.yaml.
  - For maintained writer changes add focused regression coverage and run just audit-writers,
    just lint and just test. Regenerate this existing target through an audited scoped
    route. Run full just validate-all before merging record changes, recapture changed
    inputs and save a fresh structured review without overwriting this observation.
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
- The source drawing is a free ligand, not an iron complex or a measured physiological
  protonation distribution. The primary cell-culture experiments do not by themselves
  establish transport kinetics, a target protein, a universal antimicrobial spectrum
  or a non-substrate cofactor requirement.
- The IC202C biosynthesis and ribonucleotide-reductase citation records PMID:11217808
  and PMID:11592505 supplied no indexed abstracts in the inspected responses. Their
  titles are not used to infer a mechanism, protein requirement or direct enzyme inhibition
  result. No E/Z-specific activity is assigned to either member of the reported mixture.
tags:
- unreviewed-path-order
- batch-024
- chebi-cofactor
```
