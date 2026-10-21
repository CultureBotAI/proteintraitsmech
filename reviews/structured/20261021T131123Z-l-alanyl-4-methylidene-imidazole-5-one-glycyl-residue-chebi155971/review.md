# Review of requires L-alanyl-4-methylidene-imidazole-5-one-glycyl residue

- Review: 20261021T131123Z-l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T13:02:31Z
- Finished UTC: 2026-10-21T13:11:23Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The exact attachment-bearing MIO residue and positive intrinsic histidase-cofactor context are supported. One confirmed major concerns chemical-to-protein-class equivalence; representation must preserve covalent residue origin rather than force an exogenous small molecule.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 2 in batch 025. Fresh main inventory has 429359 records; union with validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616) covers 238 record paths, leaving 429121 before this batch. 25 inventories were combined. Published branch coverage is not described as merged main. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml | generated | requires L-alanyl-4-methylidene-imidazole-5-one-glycyl residue |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_155971 | Official ChEBI/OLS resolve CHEBI:155971 and its direct prosthetic-group role and attachment-bearing residue structure. Local owner, source licence, chemical ancestry and bounded primary observations are inspected. Source identity and role are distinguished from protein-class equivalence and unqualified physiological requirements. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Attachment-bearing L-Ala-MIO-Gly residue identity

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The exact source name, formula, stereochemical graph and two attachment wildcards agree with a residue-derived moiety. The absence of source prose does not warrant inventing a free molecular structure. This is distinct from a class of proteins possessing or requiring the modification.

### Positive intrinsic MIO-cofactor evidence

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The histidase primary structure and mutation abstract directly support formation of the catalytically relevant MIO modification from an internal Ala-Ser-Gly segment. The proposed substrate geometry and detailed mechanism remain interpretations, and the paper is not promoted to a release-pinned protein example.

### Intrinsic prosthetic residue and requirement representation

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The direct prosthetic-group role and positive MIO biology are retained. The local category mentions non-substrate small molecules including prosthetic groups, while this exact entity is an internally formed covalent residue fragment. A curator must preserve that attachment scope when deciding an appropriate typed relation or participant; neither an exogenous cofactor requirement nor a mandatory category move follows automatically.

### Role-derived hierarchy and chemical ancestry

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

Direct prosthetic-group role explains the local prosthetic-requirement parent and its cofactor ancestor; the intrinsic residue attachment remains explicit. Structural chemical parents and biochemical roles are distinct from protein-trait classes. Parent resolution does not certify the parent's own equivalence semantics or universal protein requirements.

### Maintained ChEBI emitter and source attribution

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

scripts/seed_chebi_cofactor.py synthesizes the requirement label and opening definition from the chemical name and role, then appends available chemical prose. Official chemical sources, licence and the local registry resolve this provenance. Current resolution does not identify the original source release or independently qualify a required protein cofactor.

### Chemical entity versus protein-requirement class

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_155971.

The ChEBI entry denotes an attachment-bearing chemical residue, whereas the local requires-label denotes a protein functional class. Source role, chemical identity and positive biochemical context cannot make those denotations equivalent under xrefs.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-155971.chemical-entity-equivalence.

The target xrefs asserts CHEBI:155971 as a true equivalent of a protein-requirement class, but the official entry denotes a covalently attached residue-derived chemical entity. This violates the schema's own-source equivalence semantics independently of whether a particular activity requires it. Positive biological evidence and source role are retained; neither supplies class equality.

## Recommended Actions And Acceptance Checks

### A1

correct build in scripts/seed_chebi_cofactor.py so chemical provenance is preserved without chemical-to-protein-class equality. Adjudicate a representation of the intrinsic covalent residue and its activity-relative role. A typed relation or chemical participant is conditional on that decision; do not invent a detached small molecule, an uptake requirement or an automatic category move. If the schema cannot express the supported relation, retain provenance and explicit uncertainty rather than forcing a participant. Do not move the same false equivalence into mapped_xrefs or automatically promote a protein example.

- The regenerated class no longer asserts chemical-to-protein-class equivalence. Chemical provenance remains traceable, and any typed relation or participant has a curator-adjudicated exact identity and activity-relative role; otherwise explicit uncertainty is retained.
- Use audited regeneration for this existing target and focused transformation coverage. No native status or per-protein requirement is automatically promoted.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml. Run full just validate-all before merging record changes; recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; reused body verified against its original digest and access UTC | supports | Official ChEBI Introduction and Licensing sections identify a chemical-entity/role resource licensed CC BY 4.0. Chemical-source attribution does not assert equivalence to a synthesized protein requirement. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16, with its actual original access UTC retained. This does not identify the live backend release or exact release originally used by the seeder. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/155971/; Complete chemical identity, names, definition or null, formula/charge, structure, origins/citations and outgoing relations | supports | CHEBI:155971 resolves to L-alanyl-4-methylidene-imidazole-5-one-glycyl residue, with null prose definition, formula C8H9N3O2 and charge 0. Its structure *N[C@H](C)C1=NC(=C)C(=O)N1CC(*)=O contains two explicit attachment wildcards and the L-alanyl stereocentre; it is a residue fragment, not a complete detached molecule. The L-Ala-MIO-Gly residue alias agrees. Direct prosthetic-group role and imidazole ancestry are asserted; the absent InChI does not erase the explicit attachment-bearing graph. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:155971; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete CHEBI:155971 identifier and chemical name, with inspected formula/charge, structural annotations and synonyms. Its description is absent, matching the backend null definition. Resolution verifies source attribution, not every scientific assertion or protein-class equivalence. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified reused original UTC | supports | Cofactor CHEBI:23357 is an organic molecule or ion required for enzyme activity, attached loosely or tightly, and is a biochemical role. A chemical has-role assertion supplies candidate context without equating a chemical entity to a protein class. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified reused original UTC | supports | Biochemical role CHEBI:52206 is a role played by an entity or part within a biochemical context; cofactor is its child. It is not a chemical identity or independently qualified protein requirement. |
| prosthetic-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/; Definition and complete outgoing relations; verified reused original UTC | supports | Prosthetic group CHEBI:26348 is a tightly bound specific nonpolypeptide unit involved in protein activity and is a cofactor subtype. The MIO entry directly carries this role; interpretation must preserve its residue-derived covalent attachment instead of inventing a detached supplied molecule. |
| context-24780 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/24780/; Exact identifier, definition or null, chemical data/default structure and complete outgoing relations | supports | Imidazoles CHEBI:24780 is defined by the imidazole skeleton, including derivatives, under diazole. This supports broad structural ancestry of the MIO residue, not equivalence to a protein-requirement class. |
| mio-primary | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10220322%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified bibliographic identifiers and complete indexed abstract; full experimental paper not inspected through this response | supports | PMID:10220322; DOI:10.1021/bi982929q. The 2.1 Å Pseudomonas putida histidase structure identifies a highly electrophilic MIO modification formed autocatalytically by cyclization and dehydration of Ala-Ser-Gly residues 142–144. Mutation analysis supports the active centre; substrate placement and the detailed reaction mechanism are models. This provides positive residue-derived catalytic-cofactor context rather than evidence for uptake of a free small molecule. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml; Executed 2026-10-21T13:03:12Z through 2026-10-21T13:03:13Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml; Executed 2026-10-21T13:03:10Z through 2026-10-21T13:04:47Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml; Executed 2026-10-21T13:03:13Z through 2026-10-21T13:03:13Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T13:04:47Z through 2026-10-21T13:04:48Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The histidase study was inspected through its complete indexed abstract; the attempted PMC535883 full-text delivery failed and is excluded. The unsuccessful exploratory MIO query contained no records and supplies no evidence. The source null definition is retained, and no free MIO formula, transport requirement or universal Ala-Ser-Gly coordinate is asserted.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T131123Z-l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires L-alanyl-4-methylidene-imidazole-5-one-glycyl residue
started_at: '2026-10-21T13:02:31Z'
finished_at: '2026-10-21T13:11:23Z'
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
summary: The exact attachment-bearing MIO residue and positive intrinsic histidase-cofactor
  context are supported. One confirmed major concerns chemical-to-protein-class equivalence;
  representation must preserve covalent residue origin rather than force an exogenous
  small molecule.
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
  - path: data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    sha256: 69b2453bfe7faf96f8d17dc5a61d2a52f46532ee6a0608e75c039f408652809a
    role: target
  - path: data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml
    sha256: b46e2badf95bf0718eb473668f579602de9e98d477f437c2114eb6a5e3d36393
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
  selection: Path-order position 2 in batch 025. Fresh main inventory has 429359 records;
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
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242;
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616) covers 238 record paths,
    leaving 429121 before this batch. 25 inventories were combined. Published branch
    coverage is not described as merged main. Snapshot-row context paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
targets:
- kind: generated
  label: requires L-alanyl-4-methylidene-imidazole-5-one-glycyl residue
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_155971
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml
    data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml
    data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml
    data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
    data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI/OLS resolve CHEBI:155971 and its direct prosthetic-group
    role and attachment-bearing residue structure. Local owner, source licence, chemical
    ancestry and bounded primary observations are inspected. Source identity and role
    are distinguished from protein-class equivalence and unqualified physiological
    requirements.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - prosthetic-role
  - context-24780
  - mio-primary
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T13:02:31Z'
  snapshot_sha256: 69b2453bfe7faf96f8d17dc5a61d2a52f46532ee6a0608e75c039f408652809a
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
  accessed_at: '2026-10-21T13:02:31Z'
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
  accessed_at: '2026-10-21T13:02:31Z'
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
  accessed_at: '2026-10-21T13:02:31Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/prosthetic-group-chebi26348.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T13:02:31Z'
  snapshot_sha256: b46e2badf95bf0718eb473668f579602de9e98d477f437c2114eb6a5e3d36393
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
  locator: Introduction and Licensing sections; reused body verified against its original
    digest and access UTC
  summary: Official ChEBI Introduction and Licensing sections identify a chemical-entity/role
    resource licensed CC BY 4.0. Chemical-source attribution does not assert equivalence
    to a synthesized protein requirement.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: Verified reused OLS metadata reports ontology version 256 loaded 2026-10-16,
    with its actual original access UTC retained. This does not identify the live
    backend release or exact release originally used by the seeder.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/155971/
  accessed_at: '2026-10-21T13:03:25.311766Z'
  snapshot_sha256: a6194984d3b3099f58be68fde907b8916f439621ad56d1f24e19b55129c5672c
  support: supports
  locator: Complete chemical identity, names, definition or null, formula/charge,
    structure, origins/citations and outgoing relations
  summary: CHEBI:155971 resolves to L-alanyl-4-methylidene-imidazole-5-one-glycyl
    residue, with null prose definition, formula C8H9N3O2 and charge 0. Its structure
    *N[C@H](C)C1=NC(=C)C(=O)N1CC(*)=O contains two explicit attachment wildcards and
    the L-alanyl stereocentre; it is a residue fragment, not a complete detached molecule.
    The L-Ala-MIO-Gly residue alias agrees. Direct prosthetic-group role and imidazole
    ancestry are asserted; the absent InChI does not erase the explicit attachment-bearing
    graph.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:155971
  accessed_at: '2026-10-21T13:03:25.311892Z'
  snapshot_sha256: 4dac20a2c0deb2c580e4e6f94897fe155e406e00584146a7131e79e6805b2627
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete CHEBI:155971 identifier and chemical
    name, with inspected formula/charge, structural annotations and synonyms. Its
    description is absent, matching the backend null definition. Resolution verifies
    source attribution, not every scientific assertion or protein-class equivalence.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Cofactor CHEBI:23357 is an organic molecule or ion required for enzyme
    activity, attached loosely or tightly, and is a biochemical role. A chemical has-role
    assertion supplies candidate context without equating a chemical entity to a protein
    class.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Biochemical role CHEBI:52206 is a role played by an entity or part within
    a biochemical context; cofactor is its child. It is not a chemical identity or
    independently qualified protein requirement.
- evidence_id: prosthetic-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/26348/
  accessed_at: '2026-10-21T10:10:09.154369Z'
  snapshot_sha256: 157d26df2acd97761722c8e4804050c3ea0ca1381a65c5d6523f8f11c154b5dd
  support: supports
  locator: Definition and complete outgoing relations; verified reused original UTC
  summary: Prosthetic group CHEBI:26348 is a tightly bound specific nonpolypeptide
    unit involved in protein activity and is a cofactor subtype. The MIO entry directly
    carries this role; interpretation must preserve its residue-derived covalent attachment
    instead of inventing a detached supplied molecule.
- evidence_id: context-24780
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/24780/
  accessed_at: '2026-10-21T13:04:06.936718Z'
  snapshot_sha256: 59e5b4adff66402fbcb5de26a9150b472658a4d67feb11e9547148ce93476f4a
  support: supports
  locator: Exact identifier, definition or null, chemical data/default structure and
    complete outgoing relations
  summary: Imidazoles CHEBI:24780 is defined by the imidazole skeleton, including
    derivatives, under diazole. This supports broad structural ancestry of the MIO
    residue, not equivalence to a protein-requirement class.
- evidence_id: mio-primary
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:10220322%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T13:04:33.973834Z'
  snapshot_sha256: e65e25fb9ed84b8a0fd71d7c58a9fb36b8cd53172731367ab87b13fe47021c90
  support: supports
  locator: Verified bibliographic identifiers and complete indexed abstract; full
    experimental paper not inspected through this response
  summary: PMID:10220322; DOI:10.1021/bi982929q. The 2.1 Å Pseudomonas putida histidase
    structure identifies a highly electrophilic MIO modification formed autocatalytically
    by cyclization and dehydration of Ala-Ser-Gly residues 142–144. Mutation analysis
    supports the active centre; substrate placement and the detailed reaction mechanism
    are models. This provides positive residue-derived catalytic-cofactor context
    rather than evidence for uptake of a free small molecule.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  locator: Executed 2026-10-21T13:03:12Z through 2026-10-21T13:03:13Z; exit 0
  accessed_at: '2026-10-21T13:03:13Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/iron-sulfur-vanadium-cofactor-chebi60357.yaml
    data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    data/traits/function/cofactor_requirement/chebi/l-ascorbate-chebi38290.yaml data/traits/function/cofactor_requirement/chebi/l-ascorbic-acid-chebi29073.yaml
    data/traits/function/cofactor_requirement/chebi/l-dehydroascorbic-acid-chebi27956.yaml
    data/traits/function/cofactor_requirement/chebi/la-chebi33336.yaml data/traits/function/cofactor_requirement/chebi/lanthanum-3-chebi49701.yaml
    data/traits/function/cofactor_requirement/chebi/lanthanum-cation-chebi231841.yaml
    data/traits/function/cofactor_requirement/chebi/lead-2-chebi49807.yaml data/traits/function/cofactor_requirement/chebi/lu-chebi33382.yaml
  locator: Executed 2026-10-21T13:03:10Z through 2026-10-21T13:04:47Z; exit 0
  accessed_at: '2026-10-21T13:04:47Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
  locator: Executed 2026-10-21T13:03:13Z through 2026-10-21T13:03:13Z; exit 0
  accessed_at: '2026-10-21T13:03:13Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T13:04:47Z through 2026-10-21T13:04:48Z; exit 0
  accessed_at: '2026-10-21T13:04:48Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The exact source name, formula, stereochemical graph and two attachment
    wildcards agree with a residue-derived moiety. The absence of source prose does
    not warrant inventing a free molecular structure. This is distinct from a class
    of proteins possessing or requiring the modification.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - context-24780
  topic: Attachment-bearing L-Ala-MIO-Gly residue identity
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: The histidase primary structure and mutation abstract directly support
    formation of the catalytically relevant MIO modification from an internal Ala-Ser-Gly
    segment. The proposed substrate geometry and detailed mechanism remain interpretations,
    and the paper is not promoted to a release-pinned protein example.
  evidence_ids:
  - mio-primary
  topic: Positive intrinsic MIO-cofactor evidence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: The direct prosthetic-group role and positive MIO biology are retained.
    The local category mentions non-substrate small molecules including prosthetic
    groups, while this exact entity is an internally formed covalent residue fragment.
    A curator must preserve that attachment scope when deciding an appropriate typed
    relation or participant; neither an exogenous cofactor requirement nor a mandatory
    category move follows automatically.
  evidence_ids:
  - record
  - schema
  - chemical
  - prosthetic-role
  - mio-primary
  topic: Intrinsic prosthetic residue and requirement representation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: Direct prosthetic-group role explains the local prosthetic-requirement
    parent and its cofactor ancestor; the intrinsic residue attachment remains explicit.
    Structural chemical parents and biochemical roles are distinct from protein-trait
    classes. Parent resolution does not certify the parent's own equivalence semantics
    or universal protein requirements.
  evidence_ids:
  - record
  - owner
  - chemical
  - local-parent-1
  - cofactor-role
  - prosthetic-role
  topic: Role-derived hierarchy and chemical ancestry
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: scripts/seed_chebi_cofactor.py synthesizes the requirement label and opening
    definition from the chemical name and role, then appends available chemical prose.
    Official chemical sources, licence and the local registry resolve this provenance.
    Current resolution does not identify the original source release or independently
    qualify a required protein cofactor.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: Maintained ChEBI emitter and source attribution
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The ChEBI entry denotes an attachment-bearing chemical residue, whereas
    the local requires-label denotes a protein functional class. Source role, chemical
    identity and positive biochemical context cannot make those denotations equivalent
    under xrefs.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical entity versus protein-requirement class
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-155971.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The target xrefs asserts CHEBI:155971 as a true equivalent of a protein-requirement
    class, but the official entry denotes a covalently attached residue-derived chemical
    entity. This violates the schema's own-source equivalence semantics independently
    of whether a particular activity requires it. Positive biological evidence and
    source role are retained; neither supplies class equality.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The chemical entity and protein-requirement class are different
    entity types, a major grounding defect. The result does not deny positive biochemical
    roles or require an unsupported representation.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: correct build in scripts/seed_chebi_cofactor.py so chemical provenance
    is preserved without chemical-to-protein-class equality. Adjudicate a representation
    of the intrinsic covalent residue and its activity-relative role. A typed relation
    or chemical participant is conditional on that decision; do not invent a detached
    small molecule, an uptake requirement or an automatic category move. If the schema
    cannot express the supported relation, retain provenance and explicit uncertainty
    rather than forcing a participant. Do not move the same false equivalence into
    mapped_xrefs or automatically promote a protein example.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_155971
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated class no longer asserts chemical-to-protein-class equivalence.
    Chemical provenance remains traceable, and any typed relation or participant has
    a curator-adjudicated exact identity and activity-relative role; otherwise explicit
    uncertainty is retained.
  - Use audited regeneration for this existing target and focused transformation coverage.
    No native status or per-protein requirement is automatically promoted.
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/l-alanyl-4-methylidene-imidazole-5-one-glycyl-residue-chebi155971.yaml.
    Run full just validate-all before merging record changes; recapture changed inputs
    and save a fresh validated review rather than overwriting this observation.
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
- The histidase study was inspected through its complete indexed abstract; the attempted
  PMC535883 full-text delivery failed and is excluded. The unsuccessful exploratory
  MIO query contained no records and supplies no evidence. The source null definition
  is retained, and no free MIO formula, transport requirement or universal Ala-Ser-Gly
  coordinate is asserted.
tags:
- unreviewed-path-order
- batch-025
- chebi-cofactor
```
