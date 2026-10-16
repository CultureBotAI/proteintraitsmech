# Mixed CK2 evidence follow-up identifies a HeLa co-immunoprecipitation study

- Review: 20261014T201943Z-cpx-2437-primary-evidence-followup
- Repository: culturebotai/proteintraitsmech
- Started UTC: 2026-10-14T20:18:25Z
- Finished UTC: 2026-10-14T20:19:43Z
- Reviewer: Codex (self_review)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

A newly identified 1995 primary-study abstract reports reciprocal catalytic-subunit co-precipitation with beta in human HeLa cells and proposes a mixed alpha/alpha-prime/beta2 isoform. This is stronger evidence than the previously inspected binary-contact abstracts. The full article was not accessible in this bounded follow-up. Preserve the candidate hold pending full-text control assessment and independent native adjudication, not a claim that mixed-assembly evidence does not exist. No record or canonical example changed.

## Scope And Provenance

Bounded primary-abstract follow-up for P68400/CPX-2437; not full-text scientific qualification, residue reasoning or a final grounding decision.

Selection: Exact candidate affected by predecessor F3 and issue 1116, with targeted searches for human mixed catalytic-subunit assembly evidence.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base 9e0c5536b0d0ef0a3f51b8767bfc19dc56466dc2.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c | reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl # candidate_id=ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c | snapshot_row | UniProtKB:P68400 / ComplexPortal:CPX-2437 |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Unchanged target closed-schema validation | passed | True | ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c | One unchanged record passes; schema validity does not establish stoichiometry or scientific qualification. |
| Exact source receipts and historical native digest | passed | True | ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c | Downloaded abstracts and cached Portal JSON match receipt hashes; exact MED IDs are 7706297 and 9525959. Portal membership is P19784/P67870/P68400 with ECO:0005546. Native candidate digest replays and record preimage hash still matches. |
| Full primary article and figure/control assessment | unavailable | False | ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c | Publisher web access returned forbidden/internal errors and the institutional repository exposed an abstract, not article figures. This bounded abstract review is complete, but full-text control inspection remains a follow-up before final adjudication. |

## Scientific And Domain Assessments

### Positive mixed-assembly evidence with uninspected full-text controls

evidence: concern. Targets: ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c.

The HeLa study supplies directly relevant positive evidence and should lead the next adjudication. Do not continue treating the question as only separate binary contacts, but do not equate an abstract-level co-immunoprecipitation report with a solved mixed structure or final native approval.

## Findings

### F3: Relevant human mixed-assembly primary evidence found; adjudication remains pending

major / open / provisional; issue key: cpx-2437-mixed-assembly.

The 1995 HeLa abstract narrows the prior evidence gap by reporting both catalytic paralogs co-precipitating with one another and beta. Full-text experimental controls and independent native adjudication remain outstanding. Preserve the historical hold while prioritizing this positive evidence, rather than interpreting the hold as refutation of mixed assembly.

Disposition: Positive primary evidence is now identified, but this abstract-level self-review does not finalize the exact candidate. Neither absence nor disproof of mixed assembly is asserted.

## Recommended Actions And Acceptance Checks

### full-text-adjudication

Obtain the HeLa primary article through an accessible lawful route, assess exact immunoprecipitation/immunodepletion controls and assembly scope, then independently adjudicate a freshly resolved native candidate.

- Inspect the 1995 figures, antibody specificity and depletion controls, and distinguish mixed holoenzyme from higher-order co-precipitating material.
- Record exact human protein identities and evidence scope; do not map PDB 1JWH to alpha-prime or infer residue coordinates.
- Distinguish three protein types from four chains when assessing the seeded generic subunit-count wording; do not certify current wording as stoichiometry.
- Preserve historical decisions; finalize or promote only after native evidence gates, independent review and applicable user authorization.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| hela-1995 | DOI:10.1074/jbc.270.13.7501; PMID:7706297; PubMed abstract and Europe PMC snapshot resultList.result[id=7706297].abstractText | partial | Human HeLa experiments use catalytic-subunit-specific antibodies, metabolic labeling and immunodepletion. Authors propose three isoforms including alpha/alpha-prime/beta2. This directly relevant biochemical support strengthens the mixed-assembly case; antibody controls, gels and oligomer discrimination were not independently inspected in full text. |
| platelet-1998 | DOI:10.1074/jbc.273.14.8459; PMID:9525959; PubMed abstract and Europe PMC snapshot resultList.result[id=9525959].abstractText | context_only | Platelet immunoblotting detects both catalytic paralogs but the abstract explicitly retains separate alpha-only and alpha-prime-only tetramer populations as an alternative. Do not elevate this to unambiguous mixed co-residence. Full text and figures were not inspected. |
| structure-1jwh | https://www.rcsb.org/structure/1JWH; Biological Assembly 1 and macromolecular entities; primary DOI:10.1093/emboj/20.19.5320 | context_only | Deposited assembly has two P68400 alpha chains and two P67870 beta chains; the catalytic construct is 337 residues. It does not contain P19784 alpha-prime and cannot be reused as a structure of the mixed variant. |
| portal | https://www.ebi.ac.uk/intact/complex-ws/complex/CPX-2437; Cached evidenceType and participants; source receipt acquired 2026-10-13 | context_only | Exact mixed membership is inferred by paralogy, ECO:0005546. Three participant identities do not encode a tetramer's stoichiometry; participant stochiometry values are null. This cached source was not freshly reacquired or edited. |
| predecessor | reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml; F3 / cpx-2437-mixed-assembly | context_only | Previous inspected sources did not include the new HeLa primary study. Preserve the original candidate while updating the evidence assessment, not a blanket claim that mixed complexes lack primary evidence. |

## Limits And Additional Notes

- Bounded study discovery and primary-abstract assessment, not an exhaustive literature search or completed full-text assembly adjudication.
- Publisher full-text attempts failed; no new PDFs, figures, supplements or antibody-control data were inspected for CK2.
- The generated definition's generic three-subunit wording and label spelling were not corrected; record schema validity is not a stoichiometric endorsement.
- No record edit, curation event, candidate decision, canonical example, sequence annotation or causal graph was added for CK2.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261014T201943Z-cpx-2437-primary-evidence-followup
kind: record
repository: culturebotai/proteintraitsmech
title: Mixed CK2 evidence follow-up identifies a HeLa co-immunoprecipitation study
started_at: '2026-10-14T20:18:25Z'
finished_at: '2026-10-14T20:19:43Z'
reviewer:
  identity: Codex
  kind: agent
  independence: self_review
  independence_basis: Same agent continuing the cross-Mech evidence investigation;
    not independent adjudication or human sign-off.
skill: proteintraitsmech-cross-mech-proteins; curate-yaml-record
completion: completed
verdict: needs_curation
native_verdict: MIXED_ASSEMBLY_PRIMARY_SUPPORT_FOUND_FULL_TEXT_AND_ADJUDICATION_PENDING
scientific_review: true
summary: A newly identified 1995 primary-study abstract reports reciprocal catalytic-subunit
  co-precipitation with beta in human HeLa cells and proposes a mixed alpha/alpha-prime/beta2
  isoform. This is stronger evidence than the previously inspected binary-contact
  abstracts. The full article was not accessible in this bounded follow-up. Preserve
  the candidate hold pending full-text control assessment and independent native adjudication,
  not a claim that mixed-assembly evidence does not exist. No record or canonical
  example changed.
source:
  git_revision: 9e0c5536b0d0ef0a3f51b8767bfc19dc56466dc2
  state: working_tree
  inputs:
  - path: data/raw/cross-mech-followups-20261014/ck2-paper-abstracts.json
    sha256: 4e2c076dd7f73098af8d3fda85bdc140020c7a0f20fbc3072284b38f005fc627
    role: context
  - path: data/raw/cross-mech-followups-20261014/ck2-paper-abstracts.json.fetch.json
    sha256: 98906b3d4c0d2754e51e0bf341e63f4341c51b7827ea5782ba41dfb81ce5ab40
    role: context
  - path: data/traits/function/interaction_partner/complexportal/casein-kinase-ii-complex-csnk2a1-cnsk2a2-variant-cpx-2437.yaml
    sha256: fb503e0eac536f0a8c5ded20110e657a24d34275763883d16e7091ea5b7e786a
    role: context
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl
    sha256: 97a4612c183c3d92b2b54f371e43abfe23e24731e3722bbea4053d193f5af4eb
    role: target
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.sources/CPX-2437.json
    sha256: 5a54dc3ef10ed920d0327c5b2009fc7e98c6b1e6eaafda06b646432ae8fd5e10
    role: context
  - path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.sources/CPX-2437.json.fetch.json
    sha256: 9f402c08f6801ffdc456779fbaea334247c479856c5d3aa46ccab8c900484a77
    role: context
  - path: reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml
    sha256: d9e511daf5cf59b5081be6679c64af7399304286f63280c4e48b90327045dbdc
    role: context
scope:
  description: Bounded primary-abstract follow-up for P68400/CPX-2437; not full-text
    scientific qualification, residue reasoning or a final grounding decision.
  selection: Exact candidate affected by predecessor F3 and issue 1116, with targeted
    searches for human mixed catalytic-subunit assembly evidence.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
targets:
- target_id: ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
  path: reports/uniprot-grounding/review-batches/cross-mech-complex-20261013.resolved.jsonl
  selector: candidate_id=ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
  label: UniProtKB:P68400 / ComplexPortal:CPX-2437
  kind: snapshot_row
  semantic_digest:
    algorithm: ground_uniprot_examples._resolution_digest
    sha256: 175f39b630db888be2303a2b4034b76c9d7a4218920675ccf8dd2198033641fb
    description: SHA-256 of sorted compact canonical JSON for the resolved row excluding
      resolution_digest and record_preimage; record_sha256 remains included.
  owner_paths:
  - repository: culturebotai/proteintraitsmech
    path: scripts/ground_uniprot_examples.py
    role: Native resolver and reviewed promoter; no promotion performed
  ownership_note: The generated target is data/traits/function/interaction_partner/complexportal/casein-kinase-ii-complex-csnk2a1-cnsk2a2-variant-cpx-2437.yaml,
    owned by scripts/seed_complexportal.py. Read-only evidence follow-up.
checks:
- check_id: schema
  name: Unchanged target closed-schema validation
  command: just validate data/traits/function/interaction_partner/complexportal/casein-kinase-ii-complex-csnk2a1-cnsk2a2-variant-cpx-2437.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One unchanged record passes; schema validity does not establish stoichiometry
    or scientific qualification.
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
- check_id: integrity
  name: Exact source receipts and historical native digest
  status: passed
  required: true
  summary: Downloaded abstracts and cached Portal JSON match receipt hashes; exact
    MED IDs are 7706297 and 9525959. Portal membership is P19784/P67870/P68400 with
    ECO:0005546. Native candidate digest replays and record preimage hash still matches.
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
- check_id: full-text
  name: Full primary article and figure/control assessment
  status: unavailable
  required: false
  summary: Publisher web access returned forbidden/internal errors and the institutional
    repository exposed an abstract, not article figures. This bounded abstract review
    is complete, but full-text control inspection remains a follow-up before final
    adjudication.
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
evidence:
- evidence_id: hela-1995
  kind: primary_source
  reference: DOI:10.1074/jbc.270.13.7501
  locator: PMID:7706297; PubMed abstract and Europe PMC snapshot resultList.result[id=7706297].abstractText
  accessed_at: '2026-10-14T20:18:25Z'
  snapshot_sha256: 4e2c076dd7f73098af8d3fda85bdc140020c7a0f20fbc3072284b38f005fc627
  support: partial
  quote: Both alpha and alpha' coprecipitate with beta and with each other.
  summary: Human HeLa experiments use catalytic-subunit-specific antibodies, metabolic
    labeling and immunodepletion. Authors propose three isoforms including alpha/alpha-prime/beta2.
    This directly relevant biochemical support strengthens the mixed-assembly case;
    antibody controls, gels and oligomer discrimination were not independently inspected
    in full text.
  search_scope: Targeted web searches for CK2 mixed alpha/alpha-prime co-immunoprecipitation
    and assembly; read the primary abstract at PubMed and CSHL, not only search snippets.
    No exhaustive absence claim. Publisher full-text access failed.
- evidence_id: platelet-1998
  kind: primary_source
  reference: DOI:10.1074/jbc.273.14.8459
  locator: PMID:9525959; PubMed abstract and Europe PMC snapshot resultList.result[id=9525959].abstractText
  accessed_at: '2026-10-14T20:18:25Z'
  snapshot_sha256: 4e2c076dd7f73098af8d3fda85bdc140020c7a0f20fbc3072284b38f005fc627
  support: context_only
  summary: Platelet immunoblotting detects both catalytic paralogs but the abstract
    explicitly retains separate alpha-only and alpha-prime-only tetramer populations
    as an alternative. Do not elevate this to unambiguous mixed co-residence. Full
    text and figures were not inspected.
- evidence_id: structure-1jwh
  kind: database
  reference: https://www.rcsb.org/structure/1JWH
  locator: Biological Assembly 1 and macromolecular entities; primary DOI:10.1093/emboj/20.19.5320
  accessed_at: '2026-10-14T20:18:25Z'
  support: context_only
  summary: Deposited assembly has two P68400 alpha chains and two P67870 beta chains;
    the catalytic construct is 337 residues. It does not contain P19784 alpha-prime
    and cannot be reused as a structure of the mixed variant.
- evidence_id: portal
  kind: database
  reference: https://www.ebi.ac.uk/intact/complex-ws/complex/CPX-2437
  locator: Cached evidenceType and participants; source receipt acquired 2026-10-13
  accessed_at: '2026-10-14T20:18:25Z'
  snapshot_sha256: 5a54dc3ef10ed920d0327c5b2009fc7e98c6b1e6eaafda06b646432ae8fd5e10
  support: context_only
  summary: Exact mixed membership is inferred by paralogy, ECO:0005546. Three participant
    identities do not encode a tetramer's stoichiometry; participant stochiometry
    values are null. This cached source was not freshly reacquired or edited.
- evidence_id: predecessor
  kind: prior_review
  reference: reviews/structured/20261013T043714Z-cross-mech-complex-scientific/review.yaml
  locator: F3 / cpx-2437-mixed-assembly
  accessed_at: '2026-10-14T20:18:25Z'
  support: context_only
  summary: Previous inspected sources did not include the new HeLa primary study.
    Preserve the original candidate while updating the evidence assessment, not a
    blanket claim that mixed complexes lack primary evidence.
assessments:
- assessment_id: mixed-support
  area: evidence
  topic: Positive mixed-assembly evidence with uninspected full-text controls
  outcome: concern
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
  evidence_ids:
  - hela-1995
  - platelet-1998
  - structure-1jwh
  - portal
  - predecessor
  summary: The HeLa study supplies directly relevant positive evidence and should
    lead the next adjudication. Do not continue treating the question as only separate
    binary contacts, but do not equate an abstract-level co-immunoprecipitation report
    with a solved mixed structure or final native approval.
findings:
- finding_id: F3
  issue_key: cpx-2437-mixed-assembly
  category: evidence
  severity: major
  status: open
  certainty: provisional
  title: Relevant human mixed-assembly primary evidence found; adjudication remains
    pending
  description: The 1995 HeLa abstract narrows the prior evidence gap by reporting
    both catalytic paralogs co-precipitating with one another and beta. Full-text
    experimental controls and independent native adjudication remain outstanding.
    Preserve the historical hold while prioritizing this positive evidence, rather
    than interpreting the hold as refutation of mixed assembly.
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
  field_paths:
  - data/traits/function/interaction_partner/complexportal/casein-kinase-ii-complex-csnk2a1-cnsk2a2-variant-cpx-2437.yaml#/trait_relations
  evidence_ids:
  - hela-1995
  - platelet-1998
  - structure-1jwh
  - portal
  - predecessor
  owner_paths:
  - repository: culturebotai/proteintraitsmech
    path: scripts/ground_uniprot_examples.py
    role: Native evidence review and guarded promotion
  disposition_reason: Positive primary evidence is now identified, but this abstract-level
    self-review does not finalize the exact candidate. Neither absence nor disproof
    of mixed assembly is asserted.
  previous_occurrences:
  - repository: culturebotai/proteintraitsmech
    review_id: 20261013T043714Z-cross-mech-complex-scientific
    finding_id: F3
  external_issues:
  - https://github.com/CultureBotAI/proteintraitsmech/issues/1116
actions:
- action_id: full-text-adjudication
  description: Obtain the HeLa primary article through an accessible lawful route,
    assess exact immunoprecipitation/immunodepletion controls and assembly scope,
    then independently adjudicate a freshly resolved native candidate.
  finding_ids:
  - F3
  target_ids:
  - ug-4cc786210dea3eb99f412463dc66cbdea4e0a4ee5cd04602853d609a109edb5c
  ownership_note: Scientific reviewer through native grounding; any definition correction
    belongs to the maintained Complex Portal seeder or registered curation route,
    not generated browser files.
  acceptance_checks:
  - Inspect the 1995 figures, antibody specificity and depletion controls, and distinguish
    mixed holoenzyme from higher-order co-precipitating material.
  - Record exact human protein identities and evidence scope; do not map PDB 1JWH
    to alpha-prime or infer residue coordinates.
  - Distinguish three protein types from four chains when assessing the seeded generic
    subunit-count wording; do not certify current wording as stoichiometry.
  - Preserve historical decisions; finalize or promote only after native evidence
    gates, independent review and applicable user authorization.
limitations:
- Bounded study discovery and primary-abstract assessment, not an exhaustive literature
  search or completed full-text assembly adjudication.
- Publisher full-text attempts failed; no new PDFs, figures, supplements or antibody-control
  data were inspected for CK2.
- The generated definition's generic three-subunit wording and label spelling were
  not corrected; record schema validity is not a stoichiometric endorsement.
- No record edit, curation event, candidate decision, canonical example, sequence
  annotation or causal graph was added for CK2.
related_reviews:
- repository: culturebotai/proteintraitsmech
  review_id: 20261013T043714Z-cross-mech-complex-scientific
  relationship: Successor for F3 only; same affected candidate, positive new primary
    evidence and provisional hold retained.
links:
- https://pubmed.ncbi.nlm.nih.gov/7706297/
- https://doi.org/10.1074/jbc.270.13.7501
- https://pubmed.ncbi.nlm.nih.gov/9525959/
- https://www.rcsb.org/structure/1JWH
- https://github.com/CultureBotAI/proteintraitsmech/issues/1116
```
