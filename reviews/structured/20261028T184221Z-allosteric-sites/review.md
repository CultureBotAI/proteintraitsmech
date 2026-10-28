# Initial structural trait audit: allosteric-sites

- Review: 20261028T184221Z-allosteric-sites
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-28T18:37:02Z
- Finished UTC: 2026-10-28T18:42:21Z
- Reviewer: Codex cavity_binding_evidence (independent)
- Completion: partial
- Verdict: needs_curation
- Scientific review: true

## Summary

Every selected record was inspected and native deterministic checks pass. Bounded source-backed identity, scope and evidence corrections are needed; complete legacy reference and ontology recertification remains unavailable.

## Scope And Provenance

Bounded existing structural seed cohort; no new records or qualified protein promotion.

Selection: Explicit target membership resolved from current structure folders and generic site seeds; ignored-inclusive alias/parent search retained distinct concepts.
Coverage: full; 6 reviewed / 6 in the declared population.
Source: working_tree at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE | data/traits/structure/allosteric_site/allosteric-activator-site.yaml | generated | allosteric activator site |
| proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE | data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml | generated | allosteric inhibitor site |
| proteintraitsmech:ALLOSTERIC_REGULATORY_SITE | data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml | generated | allosteric regulatory site |
| proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE | data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml | generated | covalent allosteric regulatory site |
| proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET | data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml | generated | cryptic allosteric pocket |
| proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml | generated | subunit-interface allosteric site |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| strict native check | passed | True | proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE, proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE, proteintraitsmech:ALLOSTERIC_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | All 16 selected records pass strict schema validation. |
| graph native check | passed | True | proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE, proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE, proteintraitsmech:ALLOSTERIC_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify scientific entailment. |
| grounding native check | passed | True | proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE, proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE, proteintraitsmech:ALLOSTERIC_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | 16 records pass legacy-compatible grounding checks. This does not qualify any protein example. |
| Complete reference and ontology re-verification | unavailable | True | proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE, proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE, proteintraitsmech:ALLOSTERIC_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | Some publisher and PubMed/PMC pages were inaccessible; not every legacy citation, ontology CURIE, quote, or method was independently recertified. |

## Scientific And Domain Assessments

### allosteric activator site identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### allosteric inhibitor site identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### allosteric regulatory site identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_REGULATORY_SITE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### covalent allosteric regulatory site identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### cryptic allosteric pocket identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### subunit-interface allosteric site identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

## Findings

### fpocket-reference: All six allosteric methods cite an unrelated PMID

major / open / confirmed; issue key: structural-traits-fpocket-reference.

Replace PMID26950260 with PMID19486540 for fpocket; separate AlloSitePro rather than assigning its identity to the fpocket tool. Remove the broken filename-based mv and use the documented fpocket invocation. Candidate pockets do not establish allostery, crypticity, covalent reactivity or effect direction.

### allostery-scope: Generic allosteric class definitions require unjustified mechanisms

major / open / confirmed; issue key: structural-traits-allostery-scope.

General allosteric regulatory sites need not be pockets; activators/inhibitors need not follow a mandatory R/T scheme or a fixed enzyme inhibition mode. Subunit-interface sites need not require concerted rotation or catalytic cooperativity. Define demonstrated coupling and direction of effect; preserve specific mechanisms only at their documented scope.

### cryptic-equivalence: Cryptic binding pocket is broader than cryptic allosteric pocket

major / open / confirmed; issue key: structural-traits-cryptic-equivalence.

The exact synonym cryptic binding pocket drops the requirement for allosteric coupling. Mark as a broad synonym or remove. A single static pocket prediction does not establish crypticity; compare declared structural states and independently demonstrate allostery.

### interface-prediction-causality: Candidate interface pockets are used as causal evidence

major / open / confirmed; issue key: structural-traits-interface-prediction-causality.

The record quotes candidate regulatory regions as evidence for occupancy changing packing and regulating catalysis. These quoted claims do not entail the asserted causal edges. GO0042803 is labelled protein homodimerization activity while the class covers oligomeric interfaces generally. Defer those broad edges pending a demonstrated specific mechanism.

## Recommended Actions And Acceptance Checks

### action-fpocket-reference

Replace PMID26950260 with PMID19486540 for fpocket; separate AlloSitePro rather than assigning its identity to the fpocket tool. Remove the broken filename-based mv and use the documented fpocket invocation. Candidate pockets do not establish allostery, crypticity, covalent reactivity or effect direction.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-allostery-scope

General allosteric regulatory sites need not be pockets; activators/inhibitors need not follow a mandatory R/T scheme or a fixed enzyme inhibition mode. Subunit-interface sites need not require concerted rotation or catalytic cooperativity. Define demonstrated coupling and direction of effect; preserve specific mechanisms only at their documented scope.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-cryptic-equivalence

The exact synonym cryptic binding pocket drops the requirement for allosteric coupling. Mark as a broad synonym or remove. A single static pocket prediction does not establish crypticity; compare declared structural states and independently demonstrate allostery.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-interface-prediction-causality

The record quotes candidate regulatory regions as evidence for occupancy changing packing and regulating catalysis. These quoted claims do not entail the asserted causal edges. GO0042803 is labelled protein homodimerization activity while the class covers oligomeric interfaces generally. Defer those broad edges pending a demonstrated specific mechanism.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

## Category Boundaries

- retain: proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE, proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE, proteintraitsmech:ALLOSTERIC_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE. These concepts differ by solvent connectivity, location, chemistry or demonstrated allosteric/functional coupling. Shared geometry and similar labels do not establish identity. No merges proposed.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| asd | https://pubmed.ncbi.nlm.nih.gov/31665428/; Title, DOI and abstract | supports | ASD article DOI10.1093/nar/gkz958 describes allosteric regulation at a distinct site and a database spanning enzymes and ion channels. It does not establish mandatory R/T transitions or noncompetitive inhibition for every site. |
| fpocket | https://link.springer.com/article/10.1186/1471-2105-10-168; Methods: alpha spheres, pocket filtering, scoring; rights | supports | PMID19486540, DOI10.1186/1471-2105-10-168 describes candidate pocket detection and scoring, not determination of allostery. Article license CC-BY-2.0. |
| fpocket-cli | https://raw.githubusercontent.com/Discngine/fpocket/master/doc/GETTINGSTARTED.md; Condensed output and output directory naming | supports | The -d flag is valid. Output names strip the input extension before appending _out; appending _out to a PDB filename gives the wrong path. |
| graph | research/structural-traits-20261028/cavities/graph-validation.txt; Actual native command output | supports | 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify scientific entailment. |
| grounding | research/structural-traits-20261028/cavities/grounding-validation.txt; Actual native command output | supports | 16 records pass legacy-compatible grounding checks. This does not qualify any protein example. |
| local | research/structural-traits-20261028/cavities/inspected-inputs.json; SHA256-frozen input records and owning seeders | supports | All 16 target YAML records and maintained seeder inputs were read; native inspect captured their bytes before formal judgement. |
| ostrem | https://shokatlab.ucsf.edu/pdfs/24256730.pdf; Nature article pages 1-3; DOI | supports | PMID24256730, DOI10.1038/nature12796 experimentally characterizes covalent inhibition of mutant KRAS(G12C) at a switch-II pocket, including mutant-cysteine dependence. It does not support universal Lys/Tyr reactivity. |
| popovych | https://experts.umn.edu/en/publications/dynamically-driven-protein-allostery/; Institutional author abstract and DOI | supports | DOI10.1038/nsmb1132 reports CAP allosteric communication through dynamics without a required structural change in the second subunit. Full text unavailable here; abstract only. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord.xrefs and parent_traits slots | supports | The xrefs field denotes equivalent identifiers; superclass relationships must preserve class extension. |
| search | research/structural-traits-20261028/cavities/identity-search.txt; Ignored-inclusive exact ID and label search over data/traits | supports | Aliases and parent relationships were searched with rg --no-ignore --hidden; the three cohorts retain distinct geometric and functional identities. |
| strict | research/structural-traits-20261028/cavities/strict-validation.txt; Actual native command output | supports | All 16 selected records pass strict schema validation. |
| wrong-pmid | https://pubmed.ncbi.nlm.nih.gov/26950260/; Title and DOI | refutes | PMID26950260 is an iron-porphyrin metal-organic-framework paper, DOI10.1021/acs.jpclett.6b00302, not fpocket or AlloSitePro. |

## Limits And Additional Notes

- All selected YAML records were read, but this is not complete re-verification of every legacy reference or ontology term. Inaccessible pages and search-only leads were not promoted to positive evidence.
- No executable structural detection run, new canonical protein qualification, paid research or scientific record changes were performed.
- Graph checks establish syntax and grounded identifiers, not whether citations entail the asserted causal edges.
- No absence claim outside the bounded ignored-inclusive data/traits search is made.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T184221Z-allosteric-sites
kind: category
repository: CultureBotAI/proteintraitsmech
title: 'Initial structural trait audit: allosteric-sites'
started_at: '2026-10-28T18:37:02Z'
finished_at: '2026-10-28T18:42:21Z'
reviewer:
  identity: Codex cavity_binding_evidence
  kind: agent
  independence: independent
  independence_basis: Read-only researcher separate from implementing root agent;
    did not author or edit selected records.
skill: .claude/skills/review-yaml-category/SKILL.md
completion: partial
verdict: needs_curation
scientific_review: true
summary: Every selected record was inspected and native deterministic checks pass.
  Bounded source-backed identity, scope and evidence corrections are needed; complete
  legacy reference and ontology recertification remains unavailable.
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: working_tree
  inputs:
  - path: .claude/skills/curate-yaml-record/references/review-checklist.md
    sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
    role: context
  - path: data/methods/methods.yaml
    sha256: 1a0940b44fdf879489b664614debac0347b7780f1d9cc2d0c3c863a6fea78b54
    role: context
  - path: data/traits/structure/active_site/catalytic-residue.yaml
    sha256: 37f66c3c1f17fefd0c966f4a3aac28b4a306682b7d3eb57591abd7758457d6df
    role: target
  - path: data/traits/structure/allosteric_site/allosteric-activator-site.yaml
    sha256: 5dc8cb6496fa24f611600a2e1cd32a36734c64fd68a0fd34b6de7104b82dce32
    role: target
  - path: data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml
    sha256: 879439c2aeedeaab4f5cb3fea2b1e7d5ad86c85e6fdebc2ebd51c342a70b722d
    role: target
  - path: data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml
    sha256: 4c74cf01a67a9f68c464e346c7ef43789d7ee439dc7210806164e84382a726e5
    role: target
  - path: data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml
    sha256: e299f11d2828dd1ea036581c1003dc64996e12fcd462325de989e6af678eab2d
    role: target
  - path: data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml
    sha256: ee3d412a7a82e2698ed04f797c77cff9470f75f66303bd12cb941e2f427c9a42
    role: target
  - path: data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml
    sha256: b9babc4e2985a071cbc5adb77bfbba9d53ce96157755edc2ac370285b1de006f
    role: target
  - path: data/traits/structure/binding_site/protein-binding-site.yaml
    sha256: 7dbd5cee351c560cb2348e0fc3ebdefb2b529a0353e1d62c1b381ff26c340760
    role: target
  - path: data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml
    sha256: 3022f7988f1c1bfcf898f5548b42ce0f9ef5c281b4cc9ecc7395110ba8c607d7
    role: target
  - path: data/traits/structure/cavity/cavity.yaml
    sha256: 96c1db4ce0f1c6485ec1224a449cd927b5dab182497f6531edf45fede1b8c3fe
    role: target
  - path: data/traits/structure/cavity/cleft.yaml
    sha256: 5178e23cbd152e127b94688c1405d9605f14546430e4ff96be5f67f2ab29447e
    role: target
  - path: data/traits/structure/cavity/groove.yaml
    sha256: 5ef7a5450ef756275a5394f00aebdf7007e7e7e32c1c13b0788e52a0a1c0ff07
    role: target
  - path: data/traits/structure/cavity/pocket.yaml
    sha256: 2d9de3cbb4af4c29c95c50f6263e061629029d8036f3c8b19dff0f9ed0399ae7
    role: target
  - path: data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml
    sha256: e1364af257da12766490e63302d075d55635bddfc04b58fce100f4f4ddf18d78
    role: target
  - path: data/traits/structure/cavity/tunnel.yaml
    sha256: 580096dc9504f7c2501cba91384a15b67e04b74664e00c5fc69211823a8253e3
    role: target
  - path: data/traits/structure/metal_site/metal-binding-site.yaml
    sha256: 93891458436edd95525d70836640cabf2b9e144542a164ca8f12ea14bee76efd
    role: target
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: scripts/seed_foundational_traits.py
    sha256: 75b1188f650d1007d6bdcc2744df5ff65e364aca4360f5b1c7bfe23479b9b50d
    role: context
  - path: scripts/seed_localstructuralfeature.py
    sha256: dea0ca33c86dc9cdc8597de859fe1db5ae92d3fb265e3f10b1074e5c2652415b
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Bounded existing structural seed cohort; no new records or qualified
    protein promotion.
  selection: Explicit target membership resolved from current structure folders and
    generic site seeds; ignored-inclusive alias/parent search retained distinct concepts.
  coverage: full
  population_size: 6
  reviewed_target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
targets:
- target_id: proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  path: data/traits/structure/allosteric_site/allosteric-activator-site.yaml
  label: allosteric activator site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  path: data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml
  label: allosteric inhibitor site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  path: data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml
  label: allosteric regulatory site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  path: data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml
  label: covalent allosteric regulatory site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  path: data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml
  label: cryptic allosteric pocket
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  path: data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml
  label: subunit-interface allosteric site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
checks:
- check_id: strict
  name: strict native check
  status: passed
  required: true
  summary: All 16 selected records pass strict schema validation.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  command: .venv/bin/python scripts/validate_strict.py --workers 1 --out research/structural-traits-20261028/cavities/strict-errors.tsv
    data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml data/traits/structure/cavity/cavity.yaml
    data/traits/structure/cavity/cleft.yaml data/traits/structure/cavity/groove.yaml
    data/traits/structure/cavity/pocket.yaml data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml
    data/traits/structure/cavity/tunnel.yaml data/traits/structure/allosteric_site/allosteric-activator-site.yaml
    data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml
    data/traits/structure/binding_site/protein-binding-site.yaml data/traits/structure/active_site/catalytic-residue.yaml
    data/traits/structure/metal_site/metal-binding-site.yaml
  exit_code: 0
  evidence_ids:
  - strict
  scope_note: Executed once over all 16 selected targets; this review covers the declared
    subset.
- check_id: graph
  name: graph native check
  status: passed
  required: true
  summary: 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify
    scientific entailment.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml
    data/traits/structure/cavity/cavity.yaml data/traits/structure/cavity/cleft.yaml
    data/traits/structure/cavity/groove.yaml data/traits/structure/cavity/pocket.yaml
    data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml
    data/traits/structure/cavity/tunnel.yaml data/traits/structure/allosteric_site/allosteric-activator-site.yaml
    data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml
    data/traits/structure/binding_site/protein-binding-site.yaml data/traits/structure/active_site/catalytic-residue.yaml
    data/traits/structure/metal_site/metal-binding-site.yaml
  exit_code: 0
  evidence_ids:
  - graph
  scope_note: Executed once over all 16 selected targets; this review covers the declared
    subset.
- check_id: grounding
  name: grounding native check
  status: passed
  required: true
  summary: 16 records pass legacy-compatible grounding checks. This does not qualify
    any protein example.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out research/structural-traits-20261028/cavities/grounding-errors.tsv
    data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml data/traits/structure/cavity/cavity.yaml
    data/traits/structure/cavity/cleft.yaml data/traits/structure/cavity/groove.yaml
    data/traits/structure/cavity/pocket.yaml data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml
    data/traits/structure/cavity/tunnel.yaml data/traits/structure/allosteric_site/allosteric-activator-site.yaml
    data/traits/structure/allosteric_site/allosteric-inhibitor-site.yaml data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/covalent-allosteric-regulatory-site.yaml
    data/traits/structure/allosteric_site/cryptic-allosteric-pocket.yaml data/traits/structure/allosteric_site/subunit-interface-allosteric-site.yaml
    data/traits/structure/binding_site/protein-binding-site.yaml data/traits/structure/active_site/catalytic-residue.yaml
    data/traits/structure/metal_site/metal-binding-site.yaml
  exit_code: 0
  evidence_ids:
  - grounding
  scope_note: Executed once over all 16 selected targets; this review covers the declared
    subset.
- check_id: source-reverification
  name: Complete reference and ontology re-verification
  status: unavailable
  required: true
  summary: Some publisher and PubMed/PMC pages were inaccessible; not every legacy
    citation, ontology CURIE, quote, or method was independently recertified.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  evidence_ids:
  - local
evidence:
- evidence_id: asd
  kind: database
  reference: https://pubmed.ncbi.nlm.nih.gov/31665428/
  locator: Title, DOI and abstract
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: ASD article DOI10.1093/nar/gkz958 describes allosteric regulation at a
    distinct site and a database spanning enzymes and ion channels. It does not establish
    mandatory R/T transitions or noncompetitive inhibition for every site.
- evidence_id: fpocket
  kind: primary_source
  reference: https://link.springer.com/article/10.1186/1471-2105-10-168
  locator: 'Methods: alpha spheres, pocket filtering, scoring; rights'
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID19486540, DOI10.1186/1471-2105-10-168 describes candidate pocket detection
    and scoring, not determination of allostery. Article license CC-BY-2.0.
- evidence_id: fpocket-cli
  kind: authority
  reference: https://raw.githubusercontent.com/Discngine/fpocket/master/doc/GETTINGSTARTED.md
  locator: Condensed output and output directory naming
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: The -d flag is valid. Output names strip the input extension before appending
    _out; appending _out to a PDB filename gives the wrong path.
- evidence_id: graph
  kind: validation
  reference: research/structural-traits-20261028/cavities/graph-validation.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify
    scientific entailment.
- evidence_id: grounding
  kind: validation
  reference: research/structural-traits-20261028/cavities/grounding-validation.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: 16 records pass legacy-compatible grounding checks. This does not qualify
    any protein example.
- evidence_id: local
  kind: record_content
  reference: research/structural-traits-20261028/cavities/inspected-inputs.json
  locator: SHA256-frozen input records and owning seeders
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: All 16 target YAML records and maintained seeder inputs were read; native
    inspect captured their bytes before formal judgement.
- evidence_id: ostrem
  kind: primary_source
  reference: https://shokatlab.ucsf.edu/pdfs/24256730.pdf
  locator: Nature article pages 1-3; DOI
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID24256730, DOI10.1038/nature12796 experimentally characterizes covalent
    inhibition of mutant KRAS(G12C) at a switch-II pocket, including mutant-cysteine
    dependence. It does not support universal Lys/Tyr reactivity.
- evidence_id: popovych
  kind: primary_source
  reference: https://experts.umn.edu/en/publications/dynamically-driven-protein-allostery/
  locator: Institutional author abstract and DOI
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: DOI10.1038/nsmb1132 reports CAP allosteric communication through dynamics
    without a required structural change in the second subunit. Full text unavailable
    here; abstract only.
- evidence_id: schema
  kind: authority
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord.xrefs and parent_traits slots
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: The xrefs field denotes equivalent identifiers; superclass relationships
    must preserve class extension.
- evidence_id: search
  kind: search
  reference: research/structural-traits-20261028/cavities/identity-search.txt
  locator: Ignored-inclusive exact ID and label search over data/traits
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: Aliases and parent relationships were searched with rg --no-ignore --hidden;
    the three cohorts retain distinct geometric and functional identities.
  search_scope: All data/traits including hidden and ignored files; bounded ID, label,
    structural-neighbor and ontology-alias queries. No fleet-wide absence claim.
- evidence_id: strict
  kind: validation
  reference: research/structural-traits-20261028/cavities/strict-validation.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: All 16 selected records pass strict schema validation.
- evidence_id: wrong-pmid
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/26950260/
  locator: Title and DOI
  accessed_at: '2026-10-28T18:42:21Z'
  support: refutes
  summary: PMID26950260 is an iron-porphyrin metal-organic-framework paper, DOI10.1021/acs.jpclett.6b00302,
    not fpocket or AlloSitePro.
assessments:
- assessment_id: assessment-0
  area: evidence
  topic: allosteric activator site identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
- assessment_id: assessment-1
  area: evidence
  topic: allosteric inhibitor site identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
- assessment_id: assessment-2
  area: evidence
  topic: allosteric regulatory site identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
- assessment_id: assessment-3
  area: evidence
  topic: covalent allosteric regulatory site identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
- assessment_id: assessment-4
  area: evidence
  topic: cryptic allosteric pocket identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
- assessment_id: assessment-5
  area: evidence
  topic: subunit-interface allosteric site identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  evidence_ids:
  - asd
  - fpocket
  - fpocket-cli
  - local
  - ostrem
  - popovych
  - wrong-pmid
findings:
- finding_id: fpocket-reference
  issue_key: structural-traits-fpocket-reference
  category: evidence
  severity: major
  status: open
  certainty: confirmed
  title: All six allosteric methods cite an unrelated PMID
  description: Replace PMID26950260 with PMID19486540 for fpocket; separate AlloSitePro
    rather than assigning its identity to the fpocket tool. Remove the broken filename-based
    mv and use the documented fpocket invocation. Candidate pockets do not establish
    allostery, crypticity, covalent reactivity or effect direction.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  field_paths:
  - detection_methods
  evidence_ids:
  - local
  - wrong-pmid
  - fpocket
  - fpocket-cli
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
- finding_id: allostery-scope
  issue_key: structural-traits-allostery-scope
  category: scope
  severity: major
  status: open
  certainty: confirmed
  title: Generic allosteric class definitions require unjustified mechanisms
  description: General allosteric regulatory sites need not be pockets; activators/inhibitors
    need not follow a mandatory R/T scheme or a fixed enzyme inhibition mode. Subunit-interface
    sites need not require concerted rotation or catalytic cooperativity. Define demonstrated
    coupling and direction of effect; preserve specific mechanisms only at their documented
    scope.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  field_paths:
  - definition
  - parent_traits
  - causal_graphs
  evidence_ids:
  - local
  - asd
  - popovych
  - ostrem
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
- finding_id: cryptic-equivalence
  issue_key: structural-traits-cryptic-equivalence
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: Cryptic binding pocket is broader than cryptic allosteric pocket
  description: The exact synonym cryptic binding pocket drops the requirement for
    allosteric coupling. Mark as a broad synonym or remove. A single static pocket
    prediction does not establish crypticity; compare declared structural states and
    independently demonstrate allostery.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  field_paths:
  - synonyms
  - definition
  - detection_methods
  evidence_ids:
  - local
  - fpocket
  - ostrem
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
- finding_id: interface-prediction-causality
  issue_key: structural-traits-interface-prediction-causality
  category: graph
  severity: major
  status: open
  certainty: confirmed
  title: Candidate interface pockets are used as causal evidence
  description: The record quotes candidate regulatory regions as evidence for occupancy
    changing packing and regulating catalysis. These quoted claims do not entail the
    asserted causal edges. GO0042803 is labelled protein homodimerization activity
    while the class covers oligomeric interfaces generally. Defer those broad edges
    pending a demonstrated specific mechanism.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  field_paths:
  - causal_graphs[0].edges[1]
  - causal_graphs[0].edges[3]
  - causal_graphs[0].nodes
  evidence_ids:
  - local
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
actions:
- action_id: action-fpocket-reference
  description: Replace PMID26950260 with PMID19486540 for fpocket; separate AlloSitePro
    rather than assigning its identity to the fpocket tool. Remove the broken filename-based
    mv and use the documented fpocket invocation. Candidate pockets do not establish
    allostery, crypticity, covalent reactivity or effect direction.
  finding_ids:
  - fpocket-reference
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-allostery-scope
  description: General allosteric regulatory sites need not be pockets; activators/inhibitors
    need not follow a mandatory R/T scheme or a fixed enzyme inhibition mode. Subunit-interface
    sites need not require concerted rotation or catalytic cooperativity. Define demonstrated
    coupling and direction of effect; preserve specific mechanisms only at their documented
    scope.
  finding_ids:
  - allostery-scope
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-cryptic-equivalence
  description: The exact synonym cryptic binding pocket drops the requirement for
    allosteric coupling. Mark as a broad synonym or remove. A single static pocket
    prediction does not establish crypticity; compare declared structural states and
    independently demonstrate allostery.
  finding_ids:
  - cryptic-equivalence
  target_ids:
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-interface-prediction-causality
  description: The record quotes candidate regulatory regions as evidence for occupancy
    changing packing and regulating catalysis. These quoted claims do not entail the
    asserted causal edges. GO0042803 is labelled protein homodimerization activity
    while the class covers oligomeric interfaces generally. Defer those broad edges
    pending a demonstrated specific mechanism.
  finding_ids:
  - interface-prediction-causality
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
boundary_decisions:
- action: retain
  target_ids:
  - proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE
  - proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE
  - proteintraitsmech:ALLOSTERIC_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  rationale: These concepts differ by solvent connectivity, location, chemistry or
    demonstrated allosteric/functional coupling. Shared geometry and similar labels
    do not establish identity. No merges proposed.
  evidence_ids:
  - local
  - search
limitations:
- All selected YAML records were read, but this is not complete re-verification of
  every legacy reference or ontology term. Inaccessible pages and search-only leads
  were not promoted to positive evidence.
- No executable structural detection run, new canonical protein qualification, paid
  research or scientific record changes were performed.
- Graph checks establish syntax and grounded identifiers, not whether citations entail
  the asserted causal edges.
- No absence claim outside the bounded ignored-inclusive data/traits search is made.
tags:
- structural-traits
- initial-audit
```
