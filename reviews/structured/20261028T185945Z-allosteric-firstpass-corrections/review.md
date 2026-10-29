# Historical first-pass allosteric observations: covalent grounding and pocket scope

- Review: 20261028T185945Z-allosteric-firstpass-corrections
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-28T18:54:43Z
- Finished UTC: 2026-10-28T18:59:45Z
- Reviewer: codex-gpt-6-astra / preflight_boundary_review (self_review)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Two confirmed errors in preserved first-pass output: a pocket is narrower than an interface site, and GO small-molecule binding inherits noncovalent binding and cannot denote covalent capture. This observation assesses exact archived first-pass bytes, not the already corrected current records.

## Scope And Provenance

Historical first-pass source snapshots of two explicit allosteric targets, confined to synonym scope and the covalent mechanism node.

Selection: Two accepted findings discovered during the 16-target post-curation audit; full YAML snapshots preserve original target IDs. Snapshot SHA-256 values exactly match the earlier native inspection of corpus paths.
Coverage: full; 2 reviewed / 2 in the declared population.
Source: working_tree at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE | research/structural-traits-20261028/followup-preimages/covalent-allosteric-regulatory-site.yaml | source | covalent allosteric regulatory site |
| proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | research/structural-traits-20261028/followup-preimages/subunit-interface-allosteric-site.yaml | source | subunit-interface allosteric site |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Frozen first-pass hash agreement | passed | True | proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE | Both snapshot SHA-256 values match the original corpus-path hashes in cavity-post-inspection.json, captured before the followup correction. The native inspect command then captured the snapshot paths themselves. |

## Scientific And Domain Assessments

### Covalent capture was incorrectly grounded as noncovalent GO binding

grounding: concern. Targets: proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE.

Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported three edges and their primary evidence.

### A pocket synonym was exact for a broader interface-site class

identity: concern. Targets: proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE.

Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM; the site definition does not require pocket geometry.

## Findings

### covalent-noncovalent-grounding: Covalent capture was incorrectly grounded as noncovalent GO binding

major / open / confirmed; issue key: structural-traits-covalent-noncovalent-grounding.

Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported three edges and their primary evidence.

### interface-pocket-synonym: A pocket synonym was exact for a broader interface-site class

major / open / confirmed; issue key: structural-traits-interface-pocket-synonym.

Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM; the site definition does not require pocket geometry.

## Recommended Actions And Acceptance Checks

### fix-covalent-noncovalent-grounding

Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported three edges and their primary evidence.

- Update the maintained overlay and regenerate through the exact-hash guarded writer.
- Append a new honest PROPOSED curation event without rewriting prior history.
- Reinspect corrected current output and save a linked native followup with source and semantic checks.

### fix-interface-pocket-synonym

Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM; the site definition does not require pocket geometry.

- Update the maintained overlay and regenerate through the exact-hash guarded writer.
- Append a new honest PROPOSED curation event without rewriting prior history.
- Reinspect corrected current output and save a linked native followup with source and semantic checks.

## Category Boundaries

- retain: proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE, proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE. Covalent reaction chemistry and interface location are distinct class criteria. Neither error establishes synonymous identity between the two targets.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| snapshots | research/structural-traits-20261028/motifs/cavity-firstpass-followup-inspection.json; Both full-file snapshots and original native inspection SHA-256 values | supports | Read both preimages and verified exact byte identity against the earlier target hashes. The first graph proposal in graph-review.json is retained as historical context and is corrected here. |
| go-small | https://amigo.geneontology.org/amigo/term/GO:0036094; Definition and is_a GO:0005488 parent | supports | Small-molecule binding is a molecular function whose is_a parent is binding (GO:0005488). |
| go-binding | https://amigo.geneontology.org/amigo/term/GO:0005488; Term definition | supports | The parent binding function explicitly requires a selective noncovalent interaction. It therefore does not describe covalent attachment. |
| kras | https://shokatlab.ucsf.edu/pdfs/24256730.pdf; Page 1 abstract and introduction; PMID:24256730, DOI:10.1038/nature12796 | supports | Inspected primary text describes irreversible inhibitor binding dependent on mutant Cys12, altered nucleotide preference and impaired Raf binding in KRAS(G12C). A local study-scoped covalent-capture process preserves this specific mechanism without imposing an incompatible GO molecular function. |
| boundary | research/structural-traits-20261028/followup-preimages/subunit-interface-allosteric-site.yaml; definition, synonyms and detection-method discussion | supports | The first-pass definition is a broad site at a subunit interface; it does not require a concavity. Its pocket synonym nevertheless asserted EXACT_SYNONYM, contradicting the broader class boundary. |

## Limits And Additional Notes

- These are preserved historical first-pass source snapshots, not a current-corpus verdict. Current records have already received separate followup edits; the next linked review assesses those bytes.
- This bounded observation does not recertify all legacy sources or execute detection software; it does not qualify any protein occurrence or confer human-reviewed status.
- Self-review is declared because the earlier graph recommendation was mine; the same observation corrects that prior recommendation explicitly.
- The original graph-review.json is retained unchanged. GO:0036094 in its KRAS proposal was an error; use a local BIOLOGICAL_PROCESS capture node for the covalent reaction.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T185945Z-allosteric-firstpass-corrections
kind: category
repository: CultureBotAI/proteintraitsmech
title: 'Historical first-pass allosteric observations: covalent grounding and pocket
  scope'
started_at: '2026-10-28T18:54:43Z'
finished_at: '2026-10-28T18:59:45Z'
reviewer:
  identity: codex-gpt-6-astra / preflight_boundary_review
  kind: agent
  model: gpt-6-astra
  independence: self_review
  independence_basis: Separate from the implementing root and original allosteric
    definition author, but I proposed the earlier KRAS graph and am explicitly correcting
    its GO binding error. I also authored seeder integration tests; no scientific
    record or ledger edits were made by this reviewer.
skill: .claude/skills/review-yaml-category/SKILL.md
completion: completed
verdict: needs_curation
scientific_review: true
summary: 'Two confirmed errors in preserved first-pass output: a pocket is narrower
  than an interface site, and GO small-molecule binding inherits noncovalent binding
  and cannot denote covalent capture. This observation assesses exact archived first-pass
  bytes, not the already corrected current records.'
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: working_tree
  inputs:
  - path: research/structural-traits-20261028/followup-preimages/covalent-allosteric-regulatory-site.yaml
    sha256: 93432c439995b29fb17feac28bdda1d77b344c6a39e90495c5fb44884b505754
    role: target
  - path: research/structural-traits-20261028/followup-preimages/subunit-interface-allosteric-site.yaml
    sha256: 558767b7edb38615804af7288437ac6ebfbcf50bf840f52d639106a9f1b5ee18
    role: target
  - path: research/structural-traits-20261028/motifs/cavity-post-inspection.json
    sha256: 1642ebc440aef602ccaebfa47a6b8e61b86e9432456c1e9c4060b39f89460baa
    role: context
  - path: research/structural-traits-20261028/motifs/graph-review.json
    sha256: 6ea5b70493799916d3d8de363b31fb801f56ed0c2a04bb1b3c8387dba1071df2
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Historical first-pass source snapshots of two explicit allosteric targets,
    confined to synonym scope and the covalent mechanism node.
  selection: Two accepted findings discovered during the 16-target post-curation audit;
    full YAML snapshots preserve original target IDs. Snapshot SHA-256 values exactly
    match the earlier native inspection of corpus paths.
  coverage: full
  population_size: 2
  reviewed_target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
targets:
- target_id: proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  path: research/structural-traits-20261028/followup-preimages/covalent-allosteric-regulatory-site.yaml
  label: covalent allosteric regulatory site
  kind: source
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  record_class: ProteinTraitRecord
- target_id: proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  path: research/structural-traits-20261028/followup-preimages/subunit-interface-allosteric-site.yaml
  label: subunit-interface allosteric site
  kind: source
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  record_class: ProteinTraitRecord
checks:
- check_id: historical-sha
  name: Frozen first-pass hash agreement
  status: passed
  required: true
  summary: Both snapshot SHA-256 values match the original corpus-path hashes in cavity-post-inspection.json,
    captured before the followup correction. The native inspect command then captured
    the snapshot paths themselves.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  command: .venv/bin/python scripts/record_review.py inspect --targets research/structural-traits-20261028/motifs/cavity-firstpass-followup-targets.json
    --input research/structural-traits-20261028/motifs/cavity-post-inspection.json
    --input research/structural-traits-20261028/motifs/graph-review.json --input src/proteintraitsmech/schema/proteintraitsmech.yaml
  exit_code: 0
  evidence_ids:
  - snapshots
evidence:
- evidence_id: snapshots
  kind: record_content
  reference: research/structural-traits-20261028/motifs/cavity-firstpass-followup-inspection.json
  locator: Both full-file snapshots and original native inspection SHA-256 values
  accessed_at: '2026-10-28T18:59:45Z'
  support: supports
  summary: Read both preimages and verified exact byte identity against the earlier
    target hashes. The first graph proposal in graph-review.json is retained as historical
    context and is corrected here.
- evidence_id: go-small
  kind: authority
  reference: https://amigo.geneontology.org/amigo/term/GO:0036094
  locator: Definition and is_a GO:0005488 parent
  accessed_at: '2026-10-28T18:58:22Z'
  support: supports
  summary: Small-molecule binding is a molecular function whose is_a parent is binding
    (GO:0005488).
- evidence_id: go-binding
  kind: authority
  reference: https://amigo.geneontology.org/amigo/term/GO:0005488
  locator: Term definition
  accessed_at: '2026-10-28T18:58:22Z'
  support: supports
  summary: The parent binding function explicitly requires a selective noncovalent
    interaction. It therefore does not describe covalent attachment.
- evidence_id: kras
  kind: primary_source
  reference: https://shokatlab.ucsf.edu/pdfs/24256730.pdf
  locator: Page 1 abstract and introduction; PMID:24256730, DOI:10.1038/nature12796
  accessed_at: '2026-10-28T18:59:45Z'
  support: supports
  summary: Inspected primary text describes irreversible inhibitor binding dependent
    on mutant Cys12, altered nucleotide preference and impaired Raf binding in KRAS(G12C).
    A local study-scoped covalent-capture process preserves this specific mechanism
    without imposing an incompatible GO molecular function.
- evidence_id: boundary
  kind: record_content
  reference: research/structural-traits-20261028/followup-preimages/subunit-interface-allosteric-site.yaml
  locator: definition, synonyms and detection-method discussion
  accessed_at: '2026-10-28T18:59:45Z'
  support: supports
  summary: The first-pass definition is a broad site at a subunit interface; it does
    not require a concavity. Its pocket synonym nevertheless asserted EXACT_SYNONYM,
    contradicting the broader class boundary.
assessments:
- assessment_id: assessment-covalent-noncovalent-grounding
  area: grounding
  topic: Covalent capture was incorrectly grounded as noncovalent GO binding
  outcome: concern
  summary: Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded
    local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported
    three edges and their primary evidence.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  evidence_ids:
  - snapshots
  - go-small
  - go-binding
  - kras
- assessment_id: assessment-interface-pocket-synonym
  area: identity
  topic: A pocket synonym was exact for a broader interface-site class
  outcome: concern
  summary: Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM;
    the site definition does not require pocket geometry.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  evidence_ids:
  - snapshots
  - boundary
findings:
- finding_id: covalent-noncovalent-grounding
  issue_key: structural-traits-covalent-noncovalent-grounding
  category: grounding
  severity: major
  status: open
  certainty: confirmed
  title: Covalent capture was incorrectly grounded as noncovalent GO binding
  description: Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded
    local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported
    three edges and their primary evidence.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  field_paths:
  - causal_graphs
  evidence_ids:
  - snapshots
  - go-small
  - go-binding
  - kras
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  external_issues:
  - https://github.com/CultureBotAI/ProteinTraitsMech/issues/1201
- finding_id: interface-pocket-synonym
  issue_key: structural-traits-interface-pocket-synonym
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: A pocket synonym was exact for a broader interface-site class
  description: Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM;
    the site definition does not require pocket geometry.
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  field_paths:
  - synonyms
  evidence_ids:
  - snapshots
  - boundary
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  external_issues:
  - https://github.com/CultureBotAI/ProteinTraitsMech/issues/1201
actions:
- action_id: fix-covalent-noncovalent-grounding
  description: Replace GO:0036094 in the study-scoped KRAS mechanism with an ungrounded
    local BIOLOGICAL_PROCESS node describing covalent capture. Preserve the supported
    three edges and their primary evidence.
  finding_ids:
  - covalent-noncovalent-grounding
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  acceptance_checks:
  - Update the maintained overlay and regenerate through the exact-hash guarded writer.
  - Append a new honest PROPOSED curation event without rewriting prior history.
  - Reinspect corrected current output and save a linked native followup with source
    and semantic checks.
- action_id: fix-interface-pocket-synonym
  description: Change inter-subunit allosteric pocket from EXACT_SYNONYM to NARROW_SYNONYM;
    the site definition does not require pocket geometry.
  finding_ids:
  - interface-pocket-synonym
  target_ids:
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_foundational_traits.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained curation overlay; frozen preimage is historical input only
  acceptance_checks:
  - Update the maintained overlay and regenerate through the exact-hash guarded writer.
  - Append a new honest PROPOSED curation event without rewriting prior history.
  - Reinspect corrected current output and save a linked native followup with source
    and semantic checks.
boundary_decisions:
- action: retain
  target_ids:
  - proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE
  - proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE
  rationale: Covalent reaction chemistry and interface location are distinct class
    criteria. Neither error establishes synonymous identity between the two targets.
  evidence_ids:
  - snapshots
  - go-binding
  - kras
  - boundary
limitations:
- These are preserved historical first-pass source snapshots, not a current-corpus
  verdict. Current records have already received separate followup edits; the next
  linked review assesses those bytes.
- This bounded observation does not recertify all legacy sources or execute detection
  software; it does not qualify any protein occurrence or confer human-reviewed status.
- Self-review is declared because the earlier graph recommendation was mine; the same
  observation corrects that prior recommendation explicitly.
notes:
- The original graph-review.json is retained unchanged. GO:0036094 in its KRAS proposal
  was an error; use a local BIOLOGICAL_PROCESS capture node for the covalent reaction.
links:
- https://github.com/CultureBotAI/ProteinTraitsMech/issues/1201
tags:
- structural-traits
- historical-firstpass
- followup
```
