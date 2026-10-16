# TRX2-LMA1 primary-evidence follow-up beyond the 1996 abstract

- Review: 20261014T200325Z-cpx-1279-primary-evidence-followup
- Repository: culturebotai/proteintraitsmech
- Started UTC: 2026-10-14T20:00:55Z
- Finished UTC: 2026-10-14T20:03:25Z
- Reviewer: Codex (self_review)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The previously unread 1996 full paper includes single-deletion comparisons, providing stronger functional support for TRX2 than its abstract alone. Direct TRX2-Pbi2 assembly remains unresolved in the inspected evidence; retain the provisional hold pending independent adjudication of the explicitly curator-inferred membership. No record, decision or protein example changed.

## Scope And Provenance

Primary-evidence follow-up for the exact P22803/CPX-1279 candidate; not a whole-record curation or final grounding decision.

Selection: Exact target of previous F2 and issue 1115, focusing on the previously unread 1996 paper.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 9e0c5536b0d0ef0a3f51b8767bfc19dc56466dc2.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216 | reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl # candidate_id=ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216 | snapshot_row | UniProtKB:P22803 / ComplexPortal:CPX-1279 |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Unchanged target schema validation | passed | True | ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216 | One unchanged record passes closed-mode validation; not a scientific qualification. |
| Primary PDF and Portal receipt integrity | passed | True | ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216 | Both downloaded PDF and cached Portal JSON match their SHA-256 receipt pins. Exact Portal protein participants are P22803 and P0CT04. |
| Visual primary-page inspection | passed | True | ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216 | Read extracted article text, including the complete focal Results pages 790-791; visually inspected printed pages 789-791 and 793, including Figure 1, sequence-identification text, Figure 5 and Table II. No plot values were digitized. |

## Scientific And Domain Assessments

### TRX2-specific functional context versus direct physical membership

evidence: concern. Targets: ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216.

New single-deletion evidence strengthens the curator-inferred model. Functional substitution and direct assembly are different claims; obtain independent adjudication rather than continuing to describe this as merely a double-deletion abstract or silently upgrading it to physical evidence.

## Findings

### F2: Single-deletion support found; exact TRX2-Pbi2 assembly remains inferred

major / open / provisional; issue key: cpx-1279-trx2-evidence.

The missing full text has now been inspected. Its functional evidence supports reassessment, but purified identity and rescue evidence remain TRX1-specific. Retain the candidate hold for independent adjudication of curator-inferred membership, not because TRX2 has been disproven.

Disposition: Evidence gap is narrowed, not closed by this self-review. Curator inference is not forbidden, but its scope must be independently adjudicated before finalization.

## Recommended Actions And Acceptance Checks

### independent-adjudication

Independently adjudicate the exact curator-inferred P22803/CPX-1279 membership using the new full-text findings and native grounding policy; retain functional versus direct-assembly distinctions.

- Decide explicitly whether curator-inferred complex membership is adequately supported; do not relabel the evidence as physical interaction.
- Preserve the TRX1 identity of purified peptides and rescue constructs, and the positive TRX2 single-deletion context.
- Re-resolve, finalize and promote only through the native gates and separate authorization; no fabricated residue coordinates.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| paper-1996 | DOI:10.1083/jcb.132.5.787; PMID:8603912; Figure 1B-C (p.789), Results and peptide identity (p.790), Figure 5 and functional interpretation (p.791), Table II (p.793) | partial | LMA1-fraction fusion activity persists after either single deletion, whereas the double deletion loses that peak. Table II reports vacuole-less buds in 3/123 wild-type, 4/74 trx1-deletion, 3/91 trx2-deletion and 84/178 double-deletion cells. Purified peptides identify TRX1; p10 was unnamed. Supports functional redundancy, not direct identification of purified TRX2-Pbi2. Public PDF mirror was used after publisher abstract-only access and PMC access failure; DOI/title/authors/pages verified on the PDF. |
| paper-1997 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2134815/; Results, Figure 3B and thioredoxin redox activity discussion (PMID:9015301) | partial | Identifies p10 as Pbi2 and uses wild-type or cysteine-mutant TRX1 in rescue experiments. It does not turn the 1996 single-deletion phenotype into direct TRX2-Pbi2 purification evidence. |
| portal | https://www.ebi.ac.uk/intact/complex-ws/complex/CPX-1279; evidenceType, protein participants and publication crossReference | supports | Exact P22803-P0CT04 membership is curator-inferred (ECO:0005547). The listed PMID:12914955 is a review, not independent direct assembly evidence. Cached source/receipt inspected; no new Portal acquisition. |
| review-publication-type | https://pubmed.ncbi.nlm.nih.gov/12914955/; Publication types and DOI:10.1016/S0167-4889(03)00086-7 | context_only | PubMed classifies this cited paper as a Review. Its full text was not inspected here. |
| predecessor | reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml; F2 / cpx-1279-trx2-evidence | context_only | The prior abstract-only limitation is now addressed, but no independent final membership disposition has been installed. |

## Limits And Additional Notes

- Bounded follow-up of two primary studies and the exact cached Portal entry, not an exhaustive literature search or negative proof that TRX2 cannot bind Pbi2.
- Supplementary data and the full 2003 review were not inspected; no new independent reviewer was used.
- The 1996 source is labeled CC BY-NC-SA 4.0 by PMC; its raw PDF remains ignored and is not redistributed in the repository. This review records facts and interpretations, not a replacement article.
- No target-record edit, history event, finalized review decision, canonical example or evidence-policy change was made for TRX2.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261014T200325Z-cpx-1279-primary-evidence-followup
kind: record
repository: culturebotai/proteintraitsmech
title: TRX2-LMA1 primary-evidence follow-up beyond the 1996 abstract
started_at: '2026-10-14T20:00:55Z'
finished_at: '2026-10-14T20:03:25Z'
reviewer:
  identity: Codex
  kind: agent
  independence: self_review
  independence_basis: Same agent performing the cross-Mech follow-up; not independent
    or human sign-off.
skill: proteintraitsmech-cross-mech-proteins; curate-yaml-record; pdf
completion: completed
verdict: needs_curation
native_verdict: STRONGER_FUNCTIONAL_SUPPORT_EXACT_ASSEMBLY_STILL_INFERRED
scientific_review: true
summary: The previously unread 1996 full paper includes single-deletion comparisons,
  providing stronger functional support for TRX2 than its abstract alone. Direct TRX2-Pbi2
  assembly remains unresolved in the inspected evidence; retain the provisional hold
  pending independent adjudication of the explicitly curator-inferred membership.
  No record, decision or protein example changed.
source:
  git_revision: 9e0c5536b0d0ef0a3f51b8767bfc19dc56466dc2
  state: working_tree
  inputs:
  - path: data/raw/cross-mech-followups-20261014/pmid8603912.pdf
    sha256: 80d349ae1fbc86d72c1ee516add1b039e4f84237234232f9e28c9d3ca380d16d
    role: context
  - path: data/raw/cross-mech-followups-20261014/pmid8603912.pdf.fetch.json
    sha256: 55155d9007d0ab52f5915e08e6d22fd403f1e480b65d98af2fb99bfd0ef36513
    role: context
  - path: data/traits/function/interaction_partner/complexportal/lma1-complex-trx2-variant-cpx-1279.yaml
    sha256: f05a59fc3621122f87be95d7d26ea2cec8e5b9e3c996f8aa6291d7ce17f3027e
    role: context
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl
    sha256: 97a4612c183c3d92b2b54f371e43abfe23e24731e3722bbea4053d193f5af4eb
    role: target
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.sources/CPX-1279.json
    sha256: 9d745948442ba181895bc72819f6173bb75025aa982bd2f4d2020c1110be056a
    role: context
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.sources/CPX-1279.json.fetch.json
    sha256: 6bd67995a7b6a8f72e72763b331c11242ba40623ed148cef471e167673f34cd4
    role: context
  - path: reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml
    sha256: d9e511daf5cf59b5081be6679c64af7399304286f63280c4e48b90327045dbdc
    role: context
scope:
  description: Primary-evidence follow-up for the exact P22803/CPX-1279 candidate;
    not a whole-record curation or final grounding decision.
  selection: Exact target of previous F2 and issue 1115, focusing on the previously
    unread 1996 paper.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
targets:
- target_id: ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl
  selector: candidate_id=ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  label: UniProtKB:P22803 / ComplexPortal:CPX-1279
  kind: snapshot_row
  owner_paths:
  - repository: culturebotai/proteintraitsmech
    path: scripts/ground_uniprot_examples.py
    role: Native resolver and reviewed promoter; no promotion performed
  ownership_note: Generated trait is data/traits/function/interaction_partner/complexportal/lma1-complex-trx2-variant-cpx-1279.yaml;
    source owner scripts/seed_complexportal.py. Read-only evidence follow-up.
checks:
- check_id: schema
  name: Unchanged target schema validation
  command: just validate data/traits/function/interaction_partner/complexportal/lma1-complex-trx2-variant-cpx-1279.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One unchanged record passes closed-mode validation; not a scientific qualification.
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
- check_id: source-integrity
  name: Primary PDF and Portal receipt integrity
  status: passed
  required: true
  summary: Both downloaded PDF and cached Portal JSON match their SHA-256 receipt
    pins. Exact Portal protein participants are P22803 and P0CT04.
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
- check_id: figures
  name: Visual primary-page inspection
  status: passed
  required: true
  summary: Read extracted article text, including the complete focal Results pages
    790-791; visually inspected printed pages 789-791 and 793, including Figure 1,
    sequence-identification text, Figure 5 and Table II. No plot values were digitized.
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  evidence_ids:
  - paper-1996
evidence:
- evidence_id: paper-1996
  kind: primary_source
  reference: DOI:10.1083/jcb.132.5.787
  locator: PMID:8603912; Figure 1B-C (p.789), Results and peptide identity (p.790),
    Figure 5 and functional interpretation (p.791), Table II (p.793)
  accessed_at: '2026-10-14T20:00:55Z'
  snapshot_sha256: 80d349ae1fbc86d72c1ee516add1b039e4f84237234232f9e28c9d3ca380d16d
  support: partial
  summary: LMA1-fraction fusion activity persists after either single deletion, whereas
    the double deletion loses that peak. Table II reports vacuole-less buds in 3/123
    wild-type, 4/74 trx1-deletion, 3/91 trx2-deletion and 84/178 double-deletion cells.
    Purified peptides identify TRX1; p10 was unnamed. Supports functional redundancy,
    not direct identification of purified TRX2-Pbi2. Public PDF mirror was used after
    publisher abstract-only access and PMC access failure; DOI/title/authors/pages
    verified on the PDF.
- evidence_id: paper-1997
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC2134815/
  locator: Results, Figure 3B and thioredoxin redox activity discussion (PMID:9015301)
  accessed_at: '2026-10-14T19:58:00Z'
  support: partial
  summary: Identifies p10 as Pbi2 and uses wild-type or cysteine-mutant TRX1 in rescue
    experiments. It does not turn the 1996 single-deletion phenotype into direct TRX2-Pbi2
    purification evidence.
- evidence_id: portal
  kind: database
  reference: https://www.ebi.ac.uk/intact/complex-ws/complex/CPX-1279
  locator: evidenceType, protein participants and publication crossReference
  accessed_at: '2026-10-14T20:00:55Z'
  snapshot_sha256: 9d745948442ba181895bc72819f6173bb75025aa982bd2f4d2020c1110be056a
  support: supports
  summary: Exact P22803-P0CT04 membership is curator-inferred (ECO:0005547). The listed
    PMID:12914955 is a review, not independent direct assembly evidence. Cached source/receipt
    inspected; no new Portal acquisition.
- evidence_id: review-publication-type
  kind: database
  reference: https://pubmed.ncbi.nlm.nih.gov/12914955/
  locator: Publication types and DOI:10.1016/S0167-4889(03)00086-7
  accessed_at: '2026-10-14T19:59:02Z'
  support: context_only
  summary: PubMed classifies this cited paper as a Review. Its full text was not inspected
    here.
- evidence_id: predecessor
  kind: prior_review
  reference: reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml
  locator: F2 / cpx-1279-trx2-evidence
  accessed_at: '2026-10-14T20:00:55Z'
  support: context_only
  summary: The prior abstract-only limitation is now addressed, but no independent
    final membership disposition has been installed.
assessments:
- assessment_id: functional-support
  area: evidence
  topic: TRX2-specific functional context versus direct physical membership
  outcome: concern
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  evidence_ids:
  - paper-1996
  - paper-1997
  - portal
  - predecessor
  summary: New single-deletion evidence strengthens the curator-inferred model. Functional
    substitution and direct assembly are different claims; obtain independent adjudication
    rather than continuing to describe this as merely a double-deletion abstract or
    silently upgrading it to physical evidence.
findings:
- finding_id: F2
  issue_key: cpx-1279-trx2-evidence
  category: evidence
  severity: major
  status: open
  certainty: provisional
  title: Single-deletion support found; exact TRX2-Pbi2 assembly remains inferred
  description: The missing full text has now been inspected. Its functional evidence
    supports reassessment, but purified identity and rescue evidence remain TRX1-specific.
    Retain the candidate hold for independent adjudication of curator-inferred membership,
    not because TRX2 has been disproven.
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  field_paths:
  - data/traits/function/interaction_partner/complexportal/lma1-complex-trx2-variant-cpx-1279.yaml#/trait_relations
  evidence_ids:
  - paper-1996
  - paper-1997
  - portal
  - predecessor
  owner_paths:
  - repository: culturebotai/proteintraitsmech
    path: scripts/ground_uniprot_examples.py
    role: Native evidence review and promotion route
  disposition_reason: Evidence gap is narrowed, not closed by this self-review. Curator
    inference is not forbidden, but its scope must be independently adjudicated before
    finalization.
  previous_occurrences:
  - repository: culturebotai/proteintraitsmech
    review_id: 20261013T043714Z-cross-mech-complex-scientific
    finding_id: F2
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1115
actions:
- action_id: independent-adjudication
  description: Independently adjudicate the exact curator-inferred P22803/CPX-1279
    membership using the new full-text findings and native grounding policy; retain
    functional versus direct-assembly distinctions.
  finding_ids:
  - F2
  target_ids:
  - ug-884e08c85c5490fb0a83a5e0a20ed58ef0b38c6c0d97ef9585f126efdc6b4216
  ownership_note: Scientific reviewer through the maintained grounding workflow; no
    hand-edited staging decisions.
  acceptance_checks:
  - Decide explicitly whether curator-inferred complex membership is adequately supported;
    do not relabel the evidence as physical interaction.
  - Preserve the TRX1 identity of purified peptides and rescue constructs, and the
    positive TRX2 single-deletion context.
  - Re-resolve, finalize and promote only through the native gates and separate authorization;
    no fabricated residue coordinates.
limitations:
- Bounded follow-up of two primary studies and the exact cached Portal entry, not
  an exhaustive literature search or negative proof that TRX2 cannot bind Pbi2.
- Supplementary data and the full 2003 review were not inspected; no new independent
  reviewer was used.
- The 1996 source is labeled CC BY-NC-SA 4.0 by PMC; its raw PDF remains ignored and
  is not redistributed in the repository. This review records facts and interpretations,
  not a replacement article.
- No target-record edit, history event, finalized review decision, canonical example
  or evidence-policy change was made for TRX2.
related_reviews:
- repository: culturebotai/proteintraitsmech
  review_id: 20261013T043714Z-cross-mech-complex-scientific
  relationship: Successor for F2 only, retaining the exact affected candidate and
    provisional uncertainty.
links:
- https://doi.org/10.1083/jcb.132.5.787
- https://pdfs.semanticscholar.org/9915/ad62ccc5e07142e507bc5d46cfee2eaa0408.pdf
- https://github.com/CultureBotAI/proteintraitsmech/issues/1115
```
