# Supplemental source-verified obsolete binding-site equivalence

- Review: 20261028T184648Z-protein-binding-obsolete-xref
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-28T18:46:48Z
- Finished UTC: 2026-10-28T18:46:48Z
- Reviewer: Codex cavity_binding_evidence (independent)
- Completion: partial
- Verdict: needs_curation
- Scientific review: true

## Summary

At the original audited commit, the protein binding site asserts an obsolete broader SO class as equivalent. Native SO source now verified; remove this xref. Other legacy claims are not recertified.

## Scope And Provenance

Supplemental review of one equivalent xref in the original frozen protein-binding-site record.

Selection: The SO0001091 uncertainty identified during the initial cohort review.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: git_commit at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:PROTEIN_BINDING_SITE | data/traits/structure/binding_site/protein-binding-site.yaml | generated | protein binding site |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Source ontology term inspection | passed | True | proteintraitsmech:PROTEIN_BINDING_SITE | Native SO source contains obsolete:true for SO0001091. |
| Full legacy record recertification | unavailable | True | proteintraitsmech:PROTEIN_BINDING_SITE | This supplemental review resolves the exact xref question only; inaccessible legacy sources remain unverified. |

## Scientific And Domain Assessments

### SO0001091 equivalence

identity: concern. Targets: proteintraitsmech:PROTEIN_BINDING_SITE.

Remove the obsolete broader identifier; do not infer a replacement exact xref from an ontology parent alone.

## Findings

### obsolete-binding-xref: Obsolete broader SO term used as exact binding-site equivalence

major / open / confirmed; issue key: structural-traits-obsolete-binding-xref.

The seed xrefs SO0001091, obsolete generic non_covalent_binding_site. Remove it; retain source-provenance-backed SO0000410 pending any narrower mapping adjudication.

## Recommended Actions And Acceptance Checks

### remove-xref

Remove SO0001091 from the maintained owner or reviewed overlay and regenerate this selected record without resetting later curation.

- The exact xref no longer appears on this target; other source-supported mappings remain.
- Strict schema and guarded writer checks pass.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| so | https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-edit.obo; data-version2026-08-07; term SO0001091, lines8794-8803 | refutes | SO0001091 is obsolete non_covalent_binding_site for broad chemical-group binding. It is not a current equivalent protein-partner binding class. |
| original | data/traits/structure/binding_site/protein-binding-site.yaml; c4147394c698324ae537c0c63c2c9f6647c4f4fc xrefs | supports | The frozen seed lists SO0001091 as an xref. |

## Limits And Additional Notes

- Historical source-state review deliberately assesses the original baseline commit, not ongoing root edits.
- This supplement resolves one xref; it does not certify all legacy citations, mechanisms or examples.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T184648Z-protein-binding-obsolete-xref
kind: record
repository: CultureBotAI/proteintraitsmech
title: Supplemental source-verified obsolete binding-site equivalence
started_at: '2026-10-28T18:46:48Z'
finished_at: '2026-10-28T18:46:48Z'
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
summary: At the original audited commit, the protein binding site asserts an obsolete
  broader SO class as equivalent. Native SO source now verified; remove this xref.
  Other legacy claims are not recertified.
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: git_commit
  inputs:
  - path: data/traits/structure/binding_site/protein-binding-site.yaml
    sha256: 7dbd5cee351c560cb2348e0fc3ebdefb2b529a0353e1d62c1b381ff26c340760
    role: target
  - path: scripts/seed_localstructuralfeature.py
    sha256: dea0ca33c86dc9cdc8597de859fe1db5ae92d3fb265e3f10b1074e5c2652415b
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Supplemental review of one equivalent xref in the original frozen protein-binding-site
    record.
  selection: The SO0001091 uncertainty identified during the initial cohort review.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
targets:
- target_id: proteintraitsmech:PROTEIN_BINDING_SITE
  path: data/traits/structure/binding_site/protein-binding-site.yaml
  label: protein binding site
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  record_class: ProteinTraitRecord
checks:
- check_id: native-source
  name: Source ontology term inspection
  status: passed
  required: true
  summary: Native SO source contains obsolete:true for SO0001091.
  target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
  evidence_ids:
  - so
- check_id: legacy-recertification
  name: Full legacy record recertification
  status: unavailable
  required: true
  summary: This supplemental review resolves the exact xref question only; inaccessible
    legacy sources remain unverified.
  target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
evidence:
- evidence_id: so
  kind: authority
  reference: https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-edit.obo
  locator: data-version2026-08-07; term SO0001091, lines8794-8803
  accessed_at: '2026-10-28T18:46:48Z'
  support: refutes
  summary: SO0001091 is obsolete non_covalent_binding_site for broad chemical-group
    binding. It is not a current equivalent protein-partner binding class.
- evidence_id: original
  kind: record_content
  reference: data/traits/structure/binding_site/protein-binding-site.yaml
  locator: c4147394c698324ae537c0c63c2c9f6647c4f4fc xrefs
  accessed_at: '2026-10-28T18:46:48Z'
  support: supports
  summary: The frozen seed lists SO0001091 as an xref.
assessments:
- assessment_id: xref
  area: identity
  topic: SO0001091 equivalence
  outcome: concern
  summary: Remove the obsolete broader identifier; do not infer a replacement exact
    xref from an ontology parent alone.
  target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
  evidence_ids:
  - so
  - original
findings:
- finding_id: obsolete-binding-xref
  issue_key: structural-traits-obsolete-binding-xref
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: Obsolete broader SO term used as exact binding-site equivalence
  description: The seed xrefs SO0001091, obsolete generic non_covalent_binding_site.
    Remove it; retain source-provenance-backed SO0000410 pending any narrower mapping
    adjudication.
  target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
  field_paths:
  - xrefs
  evidence_ids:
  - so
  - original
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
actions:
- action_id: remove-xref
  description: Remove SO0001091 from the maintained owner or reviewed overlay and
    regenerate this selected record without resetting later curation.
  finding_ids:
  - obsolete-binding-xref
  target_ids:
  - proteintraitsmech:PROTEIN_BINDING_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  acceptance_checks:
  - The exact xref no longer appears on this target; other source-supported mappings
    remain.
  - Strict schema and guarded writer checks pass.
boundary_decisions: []
limitations:
- Historical source-state review deliberately assesses the original baseline commit,
  not ongoing root edits.
- This supplement resolves one xref; it does not certify all legacy citations, mechanisms
  or examples.
tags:
- structural-traits
- initial-audit
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261028T184221Z-binding-catalytic-metal
  relationship: supplements previously unresolved ontology inspection
```
