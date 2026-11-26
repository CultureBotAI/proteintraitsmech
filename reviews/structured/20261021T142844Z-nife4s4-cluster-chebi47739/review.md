# Review of requires NiFe4S4 cluster

- Review: 20261021T142844Z-nife4s4-cluster-chebi47739
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-21T14:15:12Z
- Finished UTC: 2026-10-21T14:28:44Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The NiFe4S4 composition and positive CODH catalytic context are supported. One confirmed major concerns chemical-to-protein-class equivalence; metal oxidation, bound protons and universal protein qualification are not inferred from source depictions.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 3 in batch 029. Fresh main inventory has 429359 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 248 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099, the union covers 278 record paths, leaving 429081 before this batch. 29 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 6cbcac34bb17f44ea7516dd3308d890367014e2b.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml | generated | requires NiFe4S4 cluster |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not qualify a protein requirement or prove semantic equivalence. |
| Causal graph integrity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | No graphs in target; no molecular-mechanism coverage is inferred. |
| Curation history validity | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | proteintraitsmech:COFACTOR_REQ_CHEBI_47739 | Official ChEBI and OLS resolve the exact chemical identifier and definition, with material structures, outgoing relations and compound_origins inspected. The direct cofactor role and local parent provenance are verified. Primary evidence is retained at its stated activity, chemical-state and experimental scope. Source authenticity and licensing do not establish chemical/protein-class equivalence. |

## Scientific And Domain Assessments

### Maintained cofactor requirement emitter

ownership: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

scripts/seed_chebi_cofactor.py owns generated target changes. Its source transformation is inspected; no emitted record has been edited.

### Protein trait class completeness

completeness: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The local identifier and requires-label denote a proposed reusable requirement class rather than a protein instance. Optional examples, sequence/structure representations and mechanisms are not automatically required; none are newly qualified.

### Causal mechanism evidence

graph: not_applicable. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

No causal graph or molecular mechanism is asserted by this YAML; graph validation does not constitute mechanism evidence.

### Requirement scope and scientific status

scope: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The target remains SEEDED, and no protein example, native review status or curation-history event is promoted by this observation.

### Exact nickel–iron–sulfur composition

identity: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The source label, ratio definition and heavy-atom graph agree on Ni:Fe:S = 1:4:4. The comparison cluster differs by one sulfur and is not equivalent. The source formula and formal graph charge are retained as depiction metadata, without inferring metal valences or a unique protein-bound proton topology.

### Positive CODH context and historical interpretation

evidence: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

Primary studies establish C-cluster structures and enzyme activity, while their interpretations of the fifth bridging sulfide differ. The later four-sulfur catalytic model and reversible D. vulgaris cluster rearrangement are considered alongside the earlier report of competent five-sulfur preparations. These are specific enzymes and experimental conditions, not interchangeable universal states.

### Exact active cluster state and protein qualification

representation: unknown. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

Positive C-cluster biology supports candidate requirements, but exact state and activity must be adjudicated for a chosen protein. Source-graph hydrogen count, individual metal oxidation states and a physiological requirement for the five-sulfur state are not independently resolved. No protein instance is promoted and no four-/five-sulfur merger is proposed.

### Source role and local parent provenance

consistency: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The direct cofactor role explains the local cofactor-requirement parent. The actual source transformation and parent resolve; this is provenance support, not proof of class equivalence or every candidate protein requirement.

### Maintained ChEBI emitter and attribution

provenance: supported. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The actual ChEBI emitter selects role-associated chemicals, synthesizes a requirement opening and appends chemical prose. Current official sources and CC BY 4.0 attribution are verified. The original seed release is unspecified, and the captured OLS metadata is not assumed to identify the backend or original seed release.

### Chemical entity versus protein-requirement equivalence

grounding: concern. Targets: proteintraitsmech:COFACTOR_REQ_CHEBI_47739.

The ChEBI identifier denotes a chemical entity or chemical family, whereas the local record denotes a protein requirement. The schema reserves xrefs for true source-direct equivalents. Positive activity context and source-role ancestry do not equate those different entities.

## Findings

### F1: Chemical entity is asserted equivalent to a protein requirement

major / open / confirmed; issue key: chebi.cofactor-requirement.CHEBI-47739.chemical-entity-equivalence.

The target places CHEBI:47739 in true-equivalence xrefs although that entry describes a chemical entity or chemical family and the local identifier describes a protein functional requirement. This violates the current equivalence semantics independently of whether a suitably scoped biological requirement can be supported.

## Recommended Actions And Acceptance Checks

### A1

Correct build in scripts/seed_chebi_cofactor.py so a chemical association is not emitted as true equality to a protein-requirement class. Preserve exact chemical identity, stoichiometry, redox/protonation or polymer scope, source provenance and positive biological context. Adjudicate the intended activity and the role required if an optional ChemicalParticipant is added. If no supported role or representation is available, retain provenance and explicit uncertainty rather than inventing one. Do not move false equality into mapped_xrefs, automatically replace the chemical or qualify a protein instance.

- The regenerated target no longer asserts chemical-to-protein-class equality. Any optional typed association has curator-adjudicated exact chemical scope and activity-relative role; otherwise source provenance and uncertainty remain explicit.
- Use a controlled audited ChEBI regeneration route: --force permits existing-record overwrite and --apply writes the selected cohort, so avoid an unreviewed broad rewrite.
- For maintained writer changes run just audit-writers, just lint and just test with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml, just validate-all data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml and just audit-graphs data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml. Run full just validate-all before merging record changes. Recapture changed inputs and save a fresh validated review rather than overwriting this observation.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| record | data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml; Entire target YAML | supports | Complete YAML inspected, including local protein-requirement identifier and label, synthesized definition, ChEBI attribution, FUNCTION/FUNC_COFACTOR_REQUIREMENT, CLASS/SEEDED status, local parent, chemical xref and stated CC-BY 4.0 licence. No optional examples, causal graphs, qualified protein assertions or chemical_participants occur in this target YAML. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord xrefs, parent_traits, chemical_participants; ChemicalParticipant/ChemicalRoleEnum; FUNC_COFACTOR_REQUIREMENT | supports | FUNC_COFACTOR_REQUIREMENT describes a non-substrate small molecule required for activity. xrefs asserts true own-source equivalence; chemical_participants represents chemical entities with typed roles. parent_traits asserts a broader class. Optional examples and causal graphs are not mandatory class representations. |
| owner | scripts/seed_chebi_cofactor.py; load_relations, load_names, build, main | supports | load_relations selects cofactor-role descendants and molecules with has_role; build synthesizes a protein-requirement label/definition, appends chemical source text, attributes the composite to ChEBI and emits CHEBI as xrefs. main selects one role-parent. The source chemical class and the synthesized requirement trait have different denotations. |
| registry | download.yaml; ChEBI source entry | supports | ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role and chemistry as a typed per-trait attribute. This identifies maintained source provenance; it does not establish a particular protein requirement. |
| local-parent-1 | data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml; Entire local parent YAML | supports | Entire local parent YAML inspected: local requirement identifier, definition, category, hierarchy, source chemical-role xref and SEEDED status. Parent resolution does not establish that its own xrefs have equivalent-class semantics. |
| licence | https://www.ebi.ac.uk/chebi/about/; Introduction and Licensing sections; verified reused body retains original access UTC | supports | The official ChEBI Introduction and Licensing sections describe chemical entities and roles and state CC BY 4.0 availability. This supports chemical-source attribution, not chemical/protein-class equivalence. |
| current-release | https://www.ebi.ac.uk/ols4/api/ontologies/chebi; Inspected source response captured at the recorded UTC time | supports | The verified reused OLS metadata reports ChEBI version 256, loaded on 2026-10-16. This is the captured ontology metadata, not a claim that the backend and original seed use that same release. |
| chemical | https://www.ebi.ac.uk/chebi/backend/api/public/compound/47739/; Complete material identity fields, names, definition, chemical data/default structure, outgoing relations, citations and compound_origins | supports | CHEBI:47739 resolves to NiFe4S4 cluster, defined by bridging sulfur and Ni:Fe:S = 1:4:4. The backend gives H3Fe4NiS4, charge 0, a cluster graph with depicted sulfhydryl hydrogens, and an InChI listing four Fe, one Ni and four S. It has a direct cofactor role and nickel-iron-sulfur-cluster parent CHEBI:60400. The generic source depiction does not determine individual metal oxidation states, experimentally bound protons, a catalytic redox state or complete protein ligation. No compound_origins entries are returned. |
| chemical-ontology | https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:47739; Inspected source response captured at the recorded UTC time | supports | OLS resolves the same nonobsolete identifier and agrees on the source label, definition, names and structural annotations. This supports source identity and attribution, not an equivalence to the synthesized protein requirement. |
| cofactor-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/; Definition and complete outgoing relations; verified reused body retains original access UTC | supports | Cofactor CHEBI:23357 is an organic molecule or ion required by an enzyme for activity, with coenzyme and prosthetic-group attachment modes. Its outgoing parent is biochemical role CHEBI:52206. A source role supplies positive candidate context without qualifying a particular protein requirement. |
| biochemical-role | https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/; Definition and complete outgoing relations; verified reused body retains original access UTC | supports | Biochemical role CHEBI:52206 concerns an entity or part acting within a biochemical context. It is a role class, not a molecular species or a protein requirement. |
| context-60400 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/60400/; Definition, chemical data/default structure and complete outgoing relations | supports | Nickel-iron-sulfur cluster CHEBI:60400 is a generic cluster containing nickel, iron and bridging sulfur atoms, with nickel-coordination-entity and iron-sulfur-cluster parents. It has no single fixed formula or graph and does not collapse the distinct four- and five-sulfur compositions. |
| cluster-comparison | https://www.ebi.ac.uk/chebi/backend/api/public/compound/177874/; External chemical comparison only: definition, stoichiometry, graph and outgoing relations | supports | CHEBI:177874 resolves to NiFe4S5 cluster, defined by bridging sulfur and Ni:Fe:S = 1:4:5. The backend gives H4Fe4NiS5, charge 0, a graph containing a fifth sulfur and depicted sulfhydryl hydrogens, and an InChI listing four Fe, one Ni and five S. It has a direct cofactor role and nickel-iron-sulfur-cluster parent CHEBI:60400. The source cites the historical CODH structure literature. Formula and SMILES bookkeeping do not establish metal oxidation states, bound protonation or catalytic competence. No compound_origins entries are returned. |
| ccd-component | https://data.rcsb.org/rest/v1/core/chemcomp/XCC; Complete RCSB-hosted wwPDB CCD response: name, formula, ambiguity flag and structure descriptors | supports | The RCSB-hosted wwPDB Chemical Component Dictionary response for the source-linked PDBeChem identifier XCC reports Fe4NiS4 and flags the component as ambiguous. Its heavy-atom composition matches the source ratio, while hydrogen-free component formula and ChEBI depicted hydrogens are not taken as experimental bound protonation or metal oxidation-state assignments. |
| cluster-historical | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11509720%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full experimental article not inspected through this response | supports | PMID:11509720; DOI:10.1126/science.1061500. The 2001 Carboxydothermus hydrogenoformans CODH structure describes a reduced NiFe4S5 C-cluster at 1.6 Å and proposes it as the CO-oxidation site. This establishes a reported five-sulfur structure, not a universal active-state assignment. |
| cluster-competence | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15113209%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full experimental article not inspected through this response | supports | PMID:15113209; DOI:10.1021/ja037776v. The 2004 C. hydrogenoformans CODH-II study reports fully competent five-sulfur preparations after dithionite/N2 treatment and after short CO treatment in the presence of DTT; prolonged CO exposure produced inactivation with a four-sulfur structure. This contrary experimental claim is retained with its preparation-specific scope. |
| cluster-ligands | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19583207%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full experimental article not inspected through this response | supports | PMID:19583207; DOI:10.1021/bi900574h. Native and cyanide-bound Moorella thermoacetica CODH/ACS structures lack the fifth bridging sulfide, with water/hydroxide at the unique Fe and cyanide at Ni. The authors argue against a catalytic role for that sulfide; a precatalytic role is not established by this abstract. |
| cluster-ligand-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2721637/fullTextXML; PMC2721637: complete main text, Methods—Protein Purification and Crystallization, Results—The Native C-Cluster, Discussion, Conclusion and Figures 1–5 | supports | The study used active M. thermoacetica CODH/ACS purified and crystallized without externally supplied CO, and found no fifth bridging sulfide. Its conclusion describes the catalytic core as NiFe4S4 and leaves any physiological precatalytic role for the fifth sulfide unresolved. This later interpretation is recorded alongside the contrary 2004 preparation-specific report, not converted into universal absence of any five-sulfur biological state. |
| cluster-redox | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.7554/eLife.39451&amp;format=json&amp;resultType=core; Verified PMID/DOI and complete indexed abstract; full experimental article not inspected through this response | supports | PMID:30277213; DOI:10.7554/eLife.39451. Desulfovibrio vulgaris CODH structures and spectroscopy reveal reversible redox-dependent C-cluster rearrangements. Mutagenesis suggests a role for the alternative ligation in Ni incorporation; that mechanistic interpretation is not a direct universal assembly proof. |
| cluster-redox-fulltext | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6168284/fullTextXML; PMC6168284: complete main text, Introduction, Results and discussion, Materials and methods—Protein preparation, metal analysis, and activity assays; Figures 1–5 and their supplements | supports | The D. vulgaris study identifies the canonical NiFe4S4 C-cluster and a reversible oxidized rearrangement. CO-oxidation assays, metal analysis, crystallography and EPR provide positive enzyme context; the C301S variant is inactive and lacks Ni. The paper treats the historical five-sulfide state as no longer considered catalytically relevant. Neither this interpretation nor the generic chemical graph fixes all metal oxidation states or bound protons. |
| validation-1 | just validate data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml; Executed 2026-10-21T14:16:12Z through 2026-10-21T14:16:13Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml; Executed 2026-10-21T14:16:10Z through 2026-10-21T14:17:43Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 12700<br>source evidence objects: 21048<br>qualified record bindings: 21048<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml; Executed 2026-10-21T14:16:13Z through 2026-10-21T14:16:13Z; exit 0 | supports | causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges &#124; grounded nodes 0/0, snippet-cited edges 0/0 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-21T14:17:43Z through 2026-10-21T14:17:44Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The reviewed record does not identify the exact ChEBI source release used for the seed. Current official responses are comparison snapshots, not proof of the original release.
- A ChEBI chemical-role assertion supplies candidate class context, not evidence that a particular protein requires that chemical, that every related protein does, or that the chemical is an obligatory physiological cofactor. No such per-protein qualification is claimed.
- External sources were inspected and SHA256-captured in session scratch. This bundle retains URLs, access times, digests and bounded observations rather than full response bodies.
- This one-record review does not certify its source cohort or parents. iModulonDB is not applicable to this generic chemical requirement class without a gene, organism or expression dataset.
- The 2001 and 2004 historical papers were inspected through complete indexed abstracts. The 2009 and 2018 main texts, methods and figure captions were inspected. Their later catalytic interpretations are not recast as proof that every five-sulfur preparation is inactive or that no precatalytic physiological role can exist. Source hydrogen counts and nominal charge do not establish experimental metal oxidation or bound protonation. The absence of compound_origins entries is not a biological absence claim.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261021T142844Z-nife4s4-cluster-chebi47739
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of requires NiFe4S4 cluster
started_at: '2026-10-21T14:15:12Z'
finished_at: '2026-10-21T14:28:44Z'
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
summary: The NiFe4S4 composition and positive CODH catalytic context are supported.
  One confirmed major concerns chemical-to-protein-class equivalence; metal oxidation,
  bound protons and universal protein qualification are not inferred from source depictions.
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
  - path: data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    sha256: 1db6aef2d260d07b8de7b84c8efb17e389cb9a37555ae25bbb15970828ba017e
    role: target
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
  selection: Path-order position 3 in batch 029. Fresh main inventory has 429359 records.
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
    f67243be00c3d9c891c24c22a32c932ea7bee099, the union covers 278 record paths, leaving
    429081 before this batch. 29 inventories were combined. Unpublished local coverage
    is explicitly not published or merged main coverage. Snapshot-row context paths
    are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
targets:
- kind: generated
  label: requires NiFe4S4 cluster
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  path: data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  record_class: ProteinTraitRecord
  target_id: proteintraitsmech:COFACTOR_REQ_CHEBI_47739
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml
    data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml
    data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
    data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml
    data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not qualify a protein requirement or prove semantic equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  exit_code: 0
  status: passed
  required: true
  summary: No graphs in target; no molecular-mechanism coverage is inferred.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Official ChEBI and OLS resolve the exact chemical identifier and definition,
    with material structures, outgoing relations and compound_origins inspected. The
    direct cofactor role and local parent provenance are verified. Primary evidence
    is retained at its stated activity, chemical-state and experimental scope. Source
    authenticity and licensing do not establish chemical/protein-class equivalence.
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  evidence_ids:
  - chemical
  - chemical-ontology
  - cofactor-role
  - biochemical-role
  - licence
  - current-release
  - context-60400
  - cluster-comparison
  - ccd-component
  - cluster-historical
  - cluster-competence
  - cluster-ligands
  - cluster-ligand-fulltext
  - cluster-redox
  - cluster-redox-fulltext
evidence:
- evidence_id: record
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  locator: Entire target YAML
  accessed_at: '2026-10-21T14:15:12Z'
  snapshot_sha256: 1db6aef2d260d07b8de7b84c8efb17e389cb9a37555ae25bbb15970828ba017e
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
  accessed_at: '2026-10-21T14:15:12Z'
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
  accessed_at: '2026-10-21T14:15:12Z'
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
  accessed_at: '2026-10-21T14:15:12Z'
  snapshot_sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
  support: supports
  summary: ChEBI is declared CC-BY 4.0 with seed_chebi_cofactor.py, enrichment status/role
    and chemistry as a typed per-trait attribute. This identifies maintained source
    provenance; it does not establish a particular protein requirement.
- evidence_id: local-parent-1
  kind: record_content
  reference: data/traits/function/cofactor_requirement/chebi/cofactor-chebi23357.yaml
  locator: Entire local parent YAML
  accessed_at: '2026-10-21T14:15:12Z'
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
  locator: Introduction and Licensing sections; verified reused body retains original
    access UTC
  summary: The official ChEBI Introduction and Licensing sections describe chemical
    entities and roles and state CC BY 4.0 availability. This supports chemical-source
    attribution, not chemical/protein-class equivalence.
- evidence_id: current-release
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi
  accessed_at: '2026-10-21T08:47:19.026327Z'
  snapshot_sha256: ec4c86fcec2d75393b2fd28d66fafbed591ab17b0a1cd58fbbf1bceb8bcefa22
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: The verified reused OLS metadata reports ChEBI version 256, loaded on 2026-10-16.
    This is the captured ontology metadata, not a claim that the backend and original
    seed use that same release.
- evidence_id: chemical
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/47739/
  accessed_at: '2026-10-21T14:16:04.814434Z'
  snapshot_sha256: c84d48d8e57000abfe208db2a4bbdf9ea1c3a5ed45477e8ec71d35eb001ec9f3
  support: supports
  locator: Complete material identity fields, names, definition, chemical data/default
    structure, outgoing relations, citations and compound_origins
  summary: CHEBI:47739 resolves to NiFe4S4 cluster, defined by bridging sulfur and
    Ni:Fe:S = 1:4:4. The backend gives H3Fe4NiS4, charge 0, a cluster graph with depicted
    sulfhydryl hydrogens, and an InChI listing four Fe, one Ni and four S. It has
    a direct cofactor role and nickel-iron-sulfur-cluster parent CHEBI:60400. The
    generic source depiction does not determine individual metal oxidation states,
    experimentally bound protons, a catalytic redox state or complete protein ligation.
    No compound_origins entries are returned.
- evidence_id: chemical-ontology
  kind: database
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/chebi/terms?obo_id=CHEBI:47739
  accessed_at: '2026-10-21T14:16:04.829442Z'
  snapshot_sha256: 218225e257a0ddb401558605525b71df38cc0a1191c6515eaa5736b4d8ebeb98
  support: supports
  locator: Inspected source response captured at the recorded UTC time
  summary: OLS resolves the same nonobsolete identifier and agrees on the source label,
    definition, names and structural annotations. This supports source identity and
    attribution, not an equivalence to the synthesized protein requirement.
- evidence_id: cofactor-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/23357/
  accessed_at: '2026-10-21T10:41:31.355972Z'
  snapshot_sha256: 4c04bfdbe6bd7fe5edd952eef8fbf70b950df6ab9693d629e1c6a1a7c00917a7
  support: supports
  locator: Definition and complete outgoing relations; verified reused body retains
    original access UTC
  summary: Cofactor CHEBI:23357 is an organic molecule or ion required by an enzyme
    for activity, with coenzyme and prosthetic-group attachment modes. Its outgoing
    parent is biochemical role CHEBI:52206. A source role supplies positive candidate
    context without qualifying a particular protein requirement.
- evidence_id: biochemical-role
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/52206/
  accessed_at: '2026-10-21T12:32:53.586758Z'
  snapshot_sha256: a2618530e2ab2677b173b52b5754a4bba1796bb11e8f41a7a5b62e8874dc5227
  support: supports
  locator: Definition and complete outgoing relations; verified reused body retains
    original access UTC
  summary: Biochemical role CHEBI:52206 concerns an entity or part acting within a
    biochemical context. It is a role class, not a molecular species or a protein
    requirement.
- evidence_id: context-60400
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/60400/
  accessed_at: '2026-10-21T14:17:26.079946Z'
  snapshot_sha256: f907f72256aff87a4aed3a63309e1fe5aa8f9d7a0c3ed519dbbda819378b65d9
  support: supports
  locator: Definition, chemical data/default structure and complete outgoing relations
  summary: Nickel-iron-sulfur cluster CHEBI:60400 is a generic cluster containing
    nickel, iron and bridging sulfur atoms, with nickel-coordination-entity and iron-sulfur-cluster
    parents. It has no single fixed formula or graph and does not collapse the distinct
    four- and five-sulfur compositions.
- evidence_id: cluster-comparison
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/177874/
  accessed_at: '2026-10-21T14:16:04.977431Z'
  snapshot_sha256: b4bf7df2faaf6064e068d46f64d3df7b900814d24c954199804a245a975900aa
  support: supports
  locator: 'External chemical comparison only: definition, stoichiometry, graph and
    outgoing relations'
  summary: CHEBI:177874 resolves to NiFe4S5 cluster, defined by bridging sulfur and
    Ni:Fe:S = 1:4:5. The backend gives H4Fe4NiS5, charge 0, a graph containing a fifth
    sulfur and depicted sulfhydryl hydrogens, and an InChI listing four Fe, one Ni
    and five S. It has a direct cofactor role and nickel-iron-sulfur-cluster parent
    CHEBI:60400. The source cites the historical CODH structure literature. Formula
    and SMILES bookkeeping do not establish metal oxidation states, bound protonation
    or catalytic competence. No compound_origins entries are returned.
- evidence_id: ccd-component
  kind: database
  reference: https://data.rcsb.org/rest/v1/core/chemcomp/XCC
  accessed_at: '2026-10-21T14:17:28.980634Z'
  snapshot_sha256: fe476cdb70ca7865a8ccb04ad3b94e6c0b78e8315e8865baff54e8b645a33333
  support: supports
  locator: 'Complete RCSB-hosted wwPDB CCD response: name, formula, ambiguity flag
    and structure descriptors'
  summary: The RCSB-hosted wwPDB Chemical Component Dictionary response for the source-linked
    PDBeChem identifier XCC reports Fe4NiS4 and flags the component as ambiguous.
    Its heavy-atom composition matches the source ratio, while hydrogen-free component
    formula and ChEBI depicted hydrogens are not taken as experimental bound protonation
    or metal oxidation-state assignments.
- evidence_id: cluster-historical
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11509720%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:17:26.918424Z'
  snapshot_sha256: a934f84784e0be31c008eac6ca0da92dd23965caab8bf6fd5baf10bad9f2b2c0
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental article
    not inspected through this response
  summary: PMID:11509720; DOI:10.1126/science.1061500. The 2001 Carboxydothermus hydrogenoformans
    CODH structure describes a reduced NiFe4S5 C-cluster at 1.6 Å and proposes it
    as the CO-oxidation site. This establishes a reported five-sulfur structure, not
    a universal active-state assignment.
- evidence_id: cluster-competence
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15113209%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:17:27.138016Z'
  snapshot_sha256: 7b5b6643ec51d445a059e23a08773d9b78005e80325a338de42e16fe5e5b5e6c
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental article
    not inspected through this response
  summary: PMID:15113209; DOI:10.1021/ja037776v. The 2004 C. hydrogenoformans CODH-II
    study reports fully competent five-sulfur preparations after dithionite/N2 treatment
    and after short CO treatment in the presence of DTT; prolonged CO exposure produced
    inactivation with a four-sulfur structure. This contrary experimental claim is
    retained with its preparation-specific scope.
- evidence_id: cluster-ligands
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:19583207%20AND%20SRC:MED&format=json&resultType=core
  accessed_at: '2026-10-21T14:17:27.459071Z'
  snapshot_sha256: f83840e9c1df626c1276a2906619830fc43367a61e1281fb7a37e5e17c25d302
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental article
    not inspected through this response
  summary: PMID:19583207; DOI:10.1021/bi900574h. Native and cyanide-bound Moorella
    thermoacetica CODH/ACS structures lack the fifth bridging sulfide, with water/hydroxide
    at the unique Fe and cyanide at Ni. The authors argue against a catalytic role
    for that sulfide; a precatalytic role is not established by this abstract.
- evidence_id: cluster-ligand-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2721637/fullTextXML
  accessed_at: '2026-10-21T14:20:19.313135Z'
  snapshot_sha256: 82c2e88ca01cf7f3ca50f4b97a908998d57a244cf446b8bc1d39e6ee30278f2a
  support: supports
  locator: 'PMC2721637: complete main text, Methods—Protein Purification and Crystallization,
    Results—The Native C-Cluster, Discussion, Conclusion and Figures 1–5'
  summary: The study used active M. thermoacetica CODH/ACS purified and crystallized
    without externally supplied CO, and found no fifth bridging sulfide. Its conclusion
    describes the catalytic core as NiFe4S4 and leaves any physiological precatalytic
    role for the fifth sulfide unresolved. This later interpretation is recorded alongside
    the contrary 2004 preparation-specific report, not converted into universal absence
    of any five-sulfur biological state.
- evidence_id: cluster-redox
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI%3A10.7554/eLife.39451&format=json&resultType=core
  accessed_at: '2026-10-21T14:17:28.839487Z'
  snapshot_sha256: 5a07ea22954fe753f82a622e84b29fa718942e60fb979086473be85c4a25c8fc
  support: supports
  locator: Verified PMID/DOI and complete indexed abstract; full experimental article
    not inspected through this response
  summary: PMID:30277213; DOI:10.7554/eLife.39451. Desulfovibrio vulgaris CODH structures
    and spectroscopy reveal reversible redox-dependent C-cluster rearrangements. Mutagenesis
    suggests a role for the alternative ligation in Ni incorporation; that mechanistic
    interpretation is not a direct universal assembly proof.
- evidence_id: cluster-redox-fulltext
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6168284/fullTextXML
  accessed_at: '2026-10-21T14:20:19.313080Z'
  snapshot_sha256: 7c2592ab5db9bc1470277e3822c06b087d9a8097da1127a7139613b80b2d874e
  support: supports
  locator: 'PMC6168284: complete main text, Introduction, Results and discussion,
    Materials and methods—Protein preparation, metal analysis, and activity assays;
    Figures 1–5 and their supplements'
  summary: The D. vulgaris study identifies the canonical NiFe4S4 C-cluster and a
    reversible oxidized rearrangement. CO-oxidation assays, metal analysis, crystallography
    and EPR provide positive enzyme context; the C301S variant is inactive and lacks
    Ni. The paper treats the historical five-sulfide state as no longer considered
    catalytically relevant. Neither this interpretation nor the generic chemical graph
    fixes all metal oxidation states or bound protons.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  locator: Executed 2026-10-21T14:16:12Z through 2026-10-21T14:16:13Z; exit 0
  accessed_at: '2026-10-21T14:16:13Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/cofactor_requirement/chebi/nicotinamide-chebi17154.yaml
    data/traits/function/cofactor_requirement/chebi/nicotinic-acid-chebi15940.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    data/traits/function/cofactor_requirement/chebi/nife4s5-cluster-chebi177874.yaml
    data/traits/function/cofactor_requirement/chebi/oxidised-coenzyme-f420-glu-n-polyanion-chebi133980.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-2-chebi47942.yaml
    data/traits/function/cofactor_requirement/chebi/pantetheine-4-phosphate-chebi16858.yaml
    data/traits/function/cofactor_requirement/chebi/pantethine-chebi31959.yaml data/traits/function/cofactor_requirement/chebi/pantothenate-chebi16646.yaml
    data/traits/function/cofactor_requirement/chebi/pantothenic-acids-chebi25848.yaml
  locator: Executed 2026-10-21T14:16:10Z through 2026-10-21T14:17:43Z; exit 0
  accessed_at: '2026-10-21T14:17:43Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 12700\nsource evidence objects: 21048\n\
    qualified record bindings: 21048\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
  locator: Executed 2026-10-21T14:16:13Z through 2026-10-21T14:16:13Z; exit 0
  accessed_at: '2026-10-21T14:16:13Z'
  support: supports
  summary: 'causal-graph audit: 0 records, 0 graphs, 0 nodes, 0 edges | grounded nodes
    0/0, snippet-cited edges 0/0 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-21T14:17:43Z through 2026-10-21T14:17:44Z; exit 0
  accessed_at: '2026-10-21T14:17:44Z'
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
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
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-2
  topic: Protein trait class completeness
- area: graph
  outcome: not_applicable
  summary: No causal graph or molecular mechanism is asserted by this YAML; graph
    validation does not constitute mechanism evidence.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-3
  topic: Causal mechanism evidence
- area: scope
  outcome: supported
  summary: The target remains SEEDED, and no protein example, native review status
    or curation-history event is promoted by this observation.
  evidence_ids:
  - record
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-4
  topic: Requirement scope and scientific status
- area: identity
  outcome: supported
  summary: The source label, ratio definition and heavy-atom graph agree on Ni:Fe:S
    = 1:4:4. The comparison cluster differs by one sulfur and is not equivalent. The
    source formula and formal graph charge are retained as depiction metadata, without
    inferring metal valences or a unique protein-bound proton topology.
  evidence_ids:
  - record
  - chemical
  - chemical-ontology
  - cluster-comparison
  - ccd-component
  - context-60400
  topic: Exact nickel–iron–sulfur composition
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-5
- area: evidence
  outcome: supported
  summary: Primary studies establish C-cluster structures and enzyme activity, while
    their interpretations of the fifth bridging sulfide differ. The later four-sulfur
    catalytic model and reversible D. vulgaris cluster rearrangement are considered
    alongside the earlier report of competent five-sulfur preparations. These are
    specific enzymes and experimental conditions, not interchangeable universal states.
  evidence_ids:
  - cluster-historical
  - cluster-competence
  - cluster-ligands
  - cluster-ligand-fulltext
  - cluster-redox-fulltext
  topic: Positive CODH context and historical interpretation
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-6
- area: representation
  outcome: unknown
  summary: Positive C-cluster biology supports candidate requirements, but exact state
    and activity must be adjudicated for a chosen protein. Source-graph hydrogen count,
    individual metal oxidation states and a physiological requirement for the five-sulfur
    state are not independently resolved. No protein instance is promoted and no four-/five-sulfur
    merger is proposed.
  evidence_ids:
  - record
  - schema
  - chemical
  - cluster-competence
  - cluster-ligand-fulltext
  - cluster-redox-fulltext
  topic: Exact active cluster state and protein qualification
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-7
- area: consistency
  outcome: supported
  summary: The direct cofactor role explains the local cofactor-requirement parent.
    The actual source transformation and parent resolve; this is provenance support,
    not proof of class equivalence or every candidate protein requirement.
  evidence_ids:
  - record
  - owner
  - chemical
  - cofactor-role
  - biochemical-role
  - local-parent-1
  topic: Source role and local parent provenance
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-8
- area: provenance
  outcome: supported
  summary: The actual ChEBI emitter selects role-associated chemicals, synthesizes
    a requirement opening and appends chemical prose. Current official sources and
    CC BY 4.0 attribution are verified. The original seed release is unspecified,
    and the captured OLS metadata is not assumed to identify the backend or original
    seed release.
  evidence_ids:
  - record
  - owner
  - registry
  - chemical
  - chemical-ontology
  - licence
  - current-release
  topic: Maintained ChEBI emitter and attribution
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-9
- area: grounding
  outcome: concern
  summary: The ChEBI identifier denotes a chemical entity or chemical family, whereas
    the local record denotes a protein requirement. The schema reserves xrefs for
    true source-direct equivalents. Positive activity context and source-role ancestry
    do not equate those different entities.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  topic: Chemical entity versus protein-requirement equivalence
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  assessment_id: assessment-10
findings:
- issue_key: chebi.cofactor-requirement.CHEBI-47739.chemical-entity-equivalence
  category: grounding
  severity: major
  title: Chemical entity is asserted equivalent to a protein requirement
  description: The target places CHEBI:47739 in true-equivalence xrefs although that
    entry describes a chemical entity or chemical family and the local identifier
    describes a protein functional requirement. This violates the current equivalence
    semantics independently of whether a suitably scoped biological requirement can
    be supported.
  evidence_ids:
  - record
  - schema
  - owner
  - chemical
  certainty: confirmed
  field_paths:
  - xrefs
  - chemical_participants
  normalization_reason: The record equates different entity types, a major grounding
    defect. This does not deny positive source-role or enzyme evidence and does not
    force a molecular participant with an unsupported role.
  finding_id: F1
  status: open
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
actions:
- action_id: A1
  description: Correct build in scripts/seed_chebi_cofactor.py so a chemical association
    is not emitted as true equality to a protein-requirement class. Preserve exact
    chemical identity, stoichiometry, redox/protonation or polymer scope, source provenance
    and positive biological context. Adjudicate the intended activity and the role
    required if an optional ChemicalParticipant is added. If no supported role or
    representation is available, retain provenance and explicit uncertainty rather
    than inventing one. Do not move false equality into mapped_xrefs, automatically
    replace the chemical or qualify a protein instance.
  finding_ids:
  - F1
  target_ids:
  - proteintraitsmech:COFACTOR_REQ_CHEBI_47739
  owner_paths:
  - path: scripts/seed_chebi_cofactor.py
    repository: CultureBotAI/proteintraitsmech
    role: Maintained ChEBI role parser, requirement-class synthesis, hierarchy selection
      and YAML emitter
  acceptance_checks:
  - The regenerated target no longer asserts chemical-to-protein-class equality. Any
    optional typed association has curator-adjudicated exact chemical scope and activity-relative
    role; otherwise source provenance and uncertainty remain explicit.
  - 'Use a controlled audited ChEBI regeneration route: --force permits existing-record
    overwrite and --apply writes the selected cohort, so avoid an unreviewed broad
    rewrite.'
  - For maintained writer changes run just audit-writers, just lint and just test
    with focused coverage. Run just validate data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml,
    just validate-all data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml
    and just audit-graphs data/traits/function/cofactor_requirement/chebi/nife4s4-cluster-chebi47739.yaml.
    Run full just validate-all before merging record changes. Recapture changed inputs
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
- The 2001 and 2004 historical papers were inspected through complete indexed abstracts.
  The 2009 and 2018 main texts, methods and figure captions were inspected. Their
  later catalytic interpretations are not recast as proof that every five-sulfur preparation
  is inactive or that no precatalytic physiological role can exist. Source hydrogen
  counts and nominal charge do not establish experimental metal oxidation or bound
  protonation. The absence of compound_origins entries is not a biological absence
  claim.
tags:
- unreviewed-path-order
- batch-029
- chebi-cofactor
```
