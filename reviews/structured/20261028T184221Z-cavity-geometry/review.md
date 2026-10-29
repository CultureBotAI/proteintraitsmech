# Initial structural trait audit: cavity-geometry

- Review: 20261028T184221Z-cavity-geometry
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
Coverage: full; 7 reviewed / 7 in the declared population.
Source: working_tree at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL | data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml | generated | buried active-site substrate/product access tunnel |
| proteintraitsmech:CAVITY | data/traits/structure/cavity/cavity.yaml | generated | cavity |
| proteintraitsmech:CLEFT | data/traits/structure/cavity/cleft.yaml | generated | cleft |
| proteintraitsmech:GROOVE | data/traits/structure/cavity/groove.yaml | generated | groove |
| proteintraitsmech:POCKET | data/traits/structure/cavity/pocket.yaml | generated | pocket |
| proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE | data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml | generated | transmembrane ion-channel selectivity-filter pore |
| proteintraitsmech:TUNNEL | data/traits/structure/cavity/tunnel.yaml | generated | tunnel |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| strict native check | passed | True | proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL, proteintraitsmech:CAVITY, proteintraitsmech:CLEFT, proteintraitsmech:GROOVE, proteintraitsmech:POCKET, proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE, proteintraitsmech:TUNNEL | All 16 selected records pass strict schema validation. |
| graph native check | passed | True | proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL, proteintraitsmech:CAVITY, proteintraitsmech:CLEFT, proteintraitsmech:GROOVE, proteintraitsmech:POCKET, proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE, proteintraitsmech:TUNNEL | 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify scientific entailment. |
| grounding native check | passed | True | proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL, proteintraitsmech:CAVITY, proteintraitsmech:CLEFT, proteintraitsmech:GROOVE, proteintraitsmech:POCKET, proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE, proteintraitsmech:TUNNEL | 16 records pass legacy-compatible grounding checks. This does not qualify any protein example. |
| Complete reference and ontology re-verification | unavailable | True | proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL, proteintraitsmech:CAVITY, proteintraitsmech:CLEFT, proteintraitsmech:GROOVE, proteintraitsmech:POCKET, proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE, proteintraitsmech:TUNNEL | Some publisher and PubMed/PMC pages were inaccessible; not every legacy citation, ontology CURIE, quote, or method was independently recertified. |

## Scientific And Domain Assessments

### buried active-site substrate/product access tunnel identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### cavity identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:CAVITY.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### cleft identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:CLEFT.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### groove identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:GROOVE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### pocket identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:POCKET.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### transmembrane ion-channel selectivity-filter pore identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

### tunnel identity, scope, detection and evidence

evidence: concern. Targets: proteintraitsmech:TUNNEL.

Read all fields. Retain this distinct class, but correct the source-backed findings attached to this target. Deterministic validity does not establish mechanistic entailment or qualified examples.

## Findings

### enum-xrefs: Vocabulary identifier is not equivalent to each member

major / open / confirmed; issue key: structural-traits-enum-xrefs.

Remove valuesets:LocalStructuralFeature from trait-equivalence xrefs while retaining enum/member provenance. Record upstream Apache-2.0 attribution without assuming a blanket evidence license.

### geometry-coverage: Generic geometry seeds lack evidence and detection limits

major / open / confirmed; issue key: structural-traits-geometry-coverage.

The five generic geometry records contain no detection_methods or evidence. Add class-specific operational limits: probe radius and coordinate state, biological assembly, solvent connectivity, and need for independent functional evidence. Avoid inventing universal groove/cleft numerical boundaries.

### enclosed-parent: Connected tunnel and pore are not enclosed-void subclasses

major / open / confirmed; issue key: structural-traits-enclosed-parent.

Both functional pathways inherit CAVITY although its maintained definition requires an enclosed solvent-inaccessible void. Keep the explicit enum meaning and remove that superclass, retaining TUNNEL under the current broad passage definition. Do not merge geometry with demonstrated function.

### pathway-method: One CAVER recipe is labelled as two distinct methods

major / open / confirmed; issue key: structural-traits-pathway-method.

The CAVER tool and Java recipe do not execute MOLE. Rename as CAVER and state starting-point/configuration, atom radii, probe size, conformer and ensemble requirements. A computed path is insufficient evidence for transport or ion selectivity.

### channel-overgeneralization: KcsA architecture was generalized to unrelated ion channels

major / open / confirmed; issue key: structural-traits-channel-overgeneralization.

Remove the universal approximately 12-A length, carbonyl geometry and near-diffusion rate from the broad class definition. Preserve KcsA-specific mechanism evidence with its explicit protein scope. Broad GO/CHEBI/SO domain IDs in these two pathway records are functional/contextual nodes rather than equivalent structural class identifiers.

## Recommended Actions And Acceptance Checks

### action-enum-xrefs

Remove valuesets:LocalStructuralFeature from trait-equivalence xrefs while retaining enum/member provenance. Record upstream Apache-2.0 attribution without assuming a blanket evidence license.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-geometry-coverage

The five generic geometry records contain no detection_methods or evidence. Add class-specific operational limits: probe radius and coordinate state, biological assembly, solvent connectivity, and need for independent functional evidence. Avoid inventing universal groove/cleft numerical boundaries.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-enclosed-parent

Both functional pathways inherit CAVITY although its maintained definition requires an enclosed solvent-inaccessible void. Keep the explicit enum meaning and remove that superclass, retaining TUNNEL under the current broad passage definition. Do not merge geometry with demonstrated function.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-pathway-method

The CAVER tool and Java recipe do not execute MOLE. Rename as CAVER and state starting-point/configuration, atom radii, probe size, conformer and ensemble requirements. A computed path is insufficient evidence for transport or ion selectivity.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

### action-channel-overgeneralization

Remove the universal approximately 12-A length, carbonyl geometry and near-diffusion rate from the broad class definition. Preserve KcsA-specific mechanism evidence with its explicit protein scope. Broad GO/CHEBI/SO domain IDs in these two pathway records are functional/contextual nodes rather than equivalent structural class identifiers.

- Change maintained seeder input or reviewed overlay as well as generated output.
- Revalidate schema and native graph/grounding checks after scoped curation.
- Re-review the exact affected claims against inspected sources; keep PROPOSED until native qualification gates are met.

## Category Boundaries

- retain: proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL, proteintraitsmech:CAVITY, proteintraitsmech:CLEFT, proteintraitsmech:GROOVE, proteintraitsmech:POCKET, proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE, proteintraitsmech:TUNNEL. These concepts differ by solvent connectivity, location, chemistry or demonstrated allosteric/functional coupling. Shared geometry and similar labels do not establish identity. No merges proposed.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| caver | https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002708; Introduction and CAVER algorithm | supports | PMID23093919 describes geometric pathway detection, starting-point selection and conformational ensembles. Tunnel/channel terminology differs across literature; computed pathways do not alone prove biological transport. |
| fpocket | https://link.springer.com/article/10.1186/1471-2105-10-168; Methods: alpha spheres, pocket filtering, scoring; rights | supports | PMID19486540, DOI10.1186/1471-2105-10-168 describes candidate pocket detection and scoring, not determination of allostery. Article license CC-BY-2.0. |
| graph | research/structural-traits-20261028/cavities/graph-validation.txt; Actual native command output | supports | 11 graphs, 45 nodes and 34 edges pass structural audit; this does not verify scientific entailment. |
| grounding | research/structural-traits-20261028/cavities/grounding-validation.txt; Actual native command output | supports | 16 records pass legacy-compatible grounding checks. This does not qualify any protein example. |
| kcsa | https://www.rcsb.org/structure/1BL8; Primary citation abstract and assembly | supports | PMID9525859, DOI10.1126/science.280.5360.69 reports KcsA carbonyl-lined selectivity-filter architecture. Its filter length and K/Na discrimination are protein-specific observations, not generic Na/Ca-channel definitions. |
| local | research/structural-traits-20261028/cavities/inspected-inputs.json; SHA256-frozen input records and owning seeders | supports | All 16 target YAML records and maintained seeder inputs were read; native inspect captured their bytes before formal judgement. |
| mole | https://pmc.ncbi.nlm.nih.gov/articles/PMC3765717/; Background; Methods; license | supports | PMID23953065, DOI10.1186/1758-2946-5-39, distinguishes connected channels and surface-to-surface pores; uses a broader cavity convention than the local enum. CC-BY-2.0. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord.xrefs and parent_traits slots | supports | The xrefs field denotes equivalent identifiers; superclass relationships must preserve class extension. |
| search | research/structural-traits-20261028/cavities/identity-search.txt; Ignored-inclusive exact ID and label search over data/traits | supports | Aliases and parent relationships were searched with rg --no-ignore --hidden; the three cohorts retain distinct geometric and functional identities. |
| strict | research/structural-traits-20261028/cavities/strict-validation.txt; Actual native command output | supports | All 16 selected records pass strict schema validation. |
| valuesets | https://linkml.io/valuesets/elements/LocalStructuralFeature/; Permissible Values and YAML | supports | The draft enum distinguishes enclosed CAVITY from accessible POCKET, surface GROOVE/CLEFT and connecting TUNNEL. Its enum identifier denotes the vocabulary, not each member. |
| valuesets-license | https://raw.githubusercontent.com/linkml/valuesets/main/LICENSE; LICENSE header | supports | The upstream valuesets repository declares Apache-2.0; a default CC-BY label would not be justified. |

## Limits And Additional Notes

- All selected YAML records were read, but this is not complete re-verification of every legacy reference or ontology term. Inaccessible pages and search-only leads were not promoted to positive evidence.
- No executable structural detection run, new canonical protein qualification, paid research or scientific record changes were performed.
- Graph checks establish syntax and grounded identifiers, not whether citations entail the asserted causal edges.
- No absence claim outside the bounded ignored-inclusive data/traits search is made.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T184221Z-cavity-geometry
kind: category
repository: CultureBotAI/proteintraitsmech
title: 'Initial structural trait audit: cavity-geometry'
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
  population_size: 7
  reviewed_target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
targets:
- target_id: proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  path: data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml
  label: buried active-site substrate/product access tunnel
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:CAVITY
  path: data/traits/structure/cavity/cavity.yaml
  label: cavity
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:CLEFT
  path: data/traits/structure/cavity/cleft.yaml
  label: cleft
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:GROOVE
  path: data/traits/structure/cavity/groove.yaml
  label: groove
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:POCKET
  path: data/traits/structure/cavity/pocket.yaml
  label: pocket
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  path: data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml
  label: transmembrane ion-channel selectivity-filter pore
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:TUNNEL
  path: data/traits/structure/cavity/tunnel.yaml
  label: tunnel
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
checks:
- check_id: strict
  name: strict native check
  status: passed
  required: true
  summary: All 16 selected records pass strict schema validation.
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
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
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
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
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
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
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
  evidence_ids:
  - local
evidence:
- evidence_id: caver
  kind: primary_source
  reference: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002708
  locator: Introduction and CAVER algorithm
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID23093919 describes geometric pathway detection, starting-point selection
    and conformational ensembles. Tunnel/channel terminology differs across literature;
    computed pathways do not alone prove biological transport.
- evidence_id: fpocket
  kind: primary_source
  reference: https://link.springer.com/article/10.1186/1471-2105-10-168
  locator: 'Methods: alpha spheres, pocket filtering, scoring; rights'
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID19486540, DOI10.1186/1471-2105-10-168 describes candidate pocket detection
    and scoring, not determination of allostery. Article license CC-BY-2.0.
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
- evidence_id: kcsa
  kind: database
  reference: https://www.rcsb.org/structure/1BL8
  locator: Primary citation abstract and assembly
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID9525859, DOI10.1126/science.280.5360.69 reports KcsA carbonyl-lined
    selectivity-filter architecture. Its filter length and K/Na discrimination are
    protein-specific observations, not generic Na/Ca-channel definitions.
- evidence_id: local
  kind: record_content
  reference: research/structural-traits-20261028/cavities/inspected-inputs.json
  locator: SHA256-frozen input records and owning seeders
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: All 16 target YAML records and maintained seeder inputs were read; native
    inspect captured their bytes before formal judgement.
- evidence_id: mole
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC3765717/
  locator: Background; Methods; license
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: PMID23953065, DOI10.1186/1758-2946-5-39, distinguishes connected channels
    and surface-to-surface pores; uses a broader cavity convention than the local
    enum. CC-BY-2.0.
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
- evidence_id: valuesets
  kind: authority
  reference: https://linkml.io/valuesets/elements/LocalStructuralFeature/
  locator: Permissible Values and YAML
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: The draft enum distinguishes enclosed CAVITY from accessible POCKET, surface
    GROOVE/CLEFT and connecting TUNNEL. Its enum identifier denotes the vocabulary,
    not each member.
- evidence_id: valuesets-license
  kind: authority
  reference: https://raw.githubusercontent.com/linkml/valuesets/main/LICENSE
  locator: LICENSE header
  accessed_at: '2026-10-28T18:42:21Z'
  support: supports
  summary: The upstream valuesets repository declares Apache-2.0; a default CC-BY
    label would not be justified.
assessments:
- assessment_id: assessment-0
  area: evidence
  topic: buried active-site substrate/product access tunnel identity, scope, detection
    and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  evidence_ids:
  - caver
  - kcsa
  - local
  - mole
  - schema
  - valuesets
- assessment_id: assessment-1
  area: evidence
  topic: cavity identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:CAVITY
  evidence_ids:
  - caver
  - fpocket
  - local
  - mole
  - schema
  - valuesets
  - valuesets-license
- assessment_id: assessment-2
  area: evidence
  topic: cleft identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:CLEFT
  evidence_ids:
  - caver
  - fpocket
  - local
  - mole
  - schema
  - valuesets
  - valuesets-license
- assessment_id: assessment-3
  area: evidence
  topic: groove identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:GROOVE
  evidence_ids:
  - caver
  - fpocket
  - local
  - mole
  - schema
  - valuesets
  - valuesets-license
- assessment_id: assessment-4
  area: evidence
  topic: pocket identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:POCKET
  evidence_ids:
  - caver
  - fpocket
  - local
  - mole
  - schema
  - valuesets
  - valuesets-license
- assessment_id: assessment-5
  area: evidence
  topic: transmembrane ion-channel selectivity-filter pore identity, scope, detection
    and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  evidence_ids:
  - caver
  - kcsa
  - local
  - mole
  - schema
  - valuesets
- assessment_id: assessment-6
  area: evidence
  topic: tunnel identity, scope, detection and evidence
  outcome: concern
  summary: Read all fields. Retain this distinct class, but correct the source-backed
    findings attached to this target. Deterministic validity does not establish mechanistic
    entailment or qualified examples.
  target_ids:
  - proteintraitsmech:TUNNEL
  evidence_ids:
  - caver
  - fpocket
  - local
  - mole
  - schema
  - valuesets
  - valuesets-license
findings:
- finding_id: enum-xrefs
  issue_key: structural-traits-enum-xrefs
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: Vocabulary identifier is not equivalent to each member
  description: Remove valuesets:LocalStructuralFeature from trait-equivalence xrefs
    while retaining enum/member provenance. Record upstream Apache-2.0 attribution
    without assuming a blanket evidence license.
  target_ids:
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:TUNNEL
  field_paths:
  - xrefs
  - provenance
  evidence_ids:
  - local
  - schema
  - valuesets
  - valuesets-license
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: geometry-coverage
  issue_key: structural-traits-geometry-coverage
  category: completeness
  severity: major
  status: open
  certainty: confirmed
  title: Generic geometry seeds lack evidence and detection limits
  description: 'The five generic geometry records contain no detection_methods or
    evidence. Add class-specific operational limits: probe radius and coordinate state,
    biological assembly, solvent connectivity, and need for independent functional
    evidence. Avoid inventing universal groove/cleft numerical boundaries.'
  target_ids:
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:TUNNEL
  field_paths:
  - definition
  - detection_methods
  - evidence
  - notes
  evidence_ids:
  - local
  - valuesets
  - caver
  - mole
  - fpocket
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: enclosed-parent
  issue_key: structural-traits-enclosed-parent
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: Connected tunnel and pore are not enclosed-void subclasses
  description: Both functional pathways inherit CAVITY although its maintained definition
    requires an enclosed solvent-inaccessible void. Keep the explicit enum meaning
    and remove that superclass, retaining TUNNEL under the current broad passage definition.
    Do not merge geometry with demonstrated function.
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  field_paths:
  - parent_traits
  evidence_ids:
  - local
  - valuesets
  - caver
  - mole
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
- finding_id: pathway-method
  issue_key: structural-traits-pathway-method
  category: evidence
  severity: major
  status: open
  certainty: confirmed
  title: One CAVER recipe is labelled as two distinct methods
  description: The CAVER tool and Java recipe do not execute MOLE. Rename as CAVER
    and state starting-point/configuration, atom radii, probe size, conformer and
    ensemble requirements. A computed path is insufficient evidence for transport
    or ion selectivity.
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  field_paths:
  - detection_methods
  evidence_ids:
  - local
  - caver
  - mole
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
- finding_id: channel-overgeneralization
  issue_key: structural-traits-channel-overgeneralization
  category: scope
  severity: major
  status: open
  certainty: confirmed
  title: KcsA architecture was generalized to unrelated ion channels
  description: Remove the universal approximately 12-A length, carbonyl geometry and
    near-diffusion rate from the broad class definition. Preserve KcsA-specific mechanism
    evidence with its explicit protein scope. Broad GO/CHEBI/SO domain IDs in these
    two pathway records are functional/contextual nodes rather than equivalent structural
    class identifiers.
  target_ids:
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  field_paths:
  - definition
  - xrefs
  - causal_graphs
  evidence_ids:
  - local
  - schema
  - kcsa
  - caver
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
actions:
- action_id: action-enum-xrefs
  description: Remove valuesets:LocalStructuralFeature from trait-equivalence xrefs
    while retaining enum/member provenance. Record upstream Apache-2.0 attribution
    without assuming a blanket evidence license.
  finding_ids:
  - enum-xrefs
  target_ids:
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:TUNNEL
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-geometry-coverage
  description: 'The five generic geometry records contain no detection_methods or
    evidence. Add class-specific operational limits: probe radius and coordinate state,
    biological assembly, solvent connectivity, and need for independent functional
    evidence. Avoid inventing universal groove/cleft numerical boundaries.'
  finding_ids:
  - geometry-coverage
  target_ids:
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:TUNNEL
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-enclosed-parent
  description: Both functional pathways inherit CAVITY although its maintained definition
    requires an enclosed solvent-inaccessible void. Keep the explicit enum meaning
    and remove that superclass, retaining TUNNEL under the current broad passage definition.
    Do not merge geometry with demonstrated function.
  finding_ids:
  - enclosed-parent
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-pathway-method
  description: The CAVER tool and Java recipe do not execute MOLE. Rename as CAVER
    and state starting-point/configuration, atom radii, probe size, conformer and
    ensemble requirements. A computed path is insufficient evidence for transport
    or ion selectivity.
  finding_ids:
  - pathway-method
  target_ids:
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  acceptance_checks:
  - Change maintained seeder input or reviewed overlay as well as generated output.
  - Revalidate schema and native graph/grounding checks after scoped curation.
  - Re-review the exact affected claims against inspected sources; keep PROPOSED until
    native qualification gates are met.
- action_id: action-channel-overgeneralization
  description: Remove the universal approximately 12-A length, carbonyl geometry and
    near-diffusion rate from the broad class definition. Preserve KcsA-specific mechanism
    evidence with its explicit protein scope. Broad GO/CHEBI/SO domain IDs in these
    two pathway records are functional/contextual nodes rather than equivalent structural
    class identifiers.
  finding_ids:
  - channel-overgeneralization
  target_ids:
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
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
  - proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL
  - proteintraitsmech:CAVITY
  - proteintraitsmech:CLEFT
  - proteintraitsmech:GROOVE
  - proteintraitsmech:POCKET
  - proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE
  - proteintraitsmech:TUNNEL
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
