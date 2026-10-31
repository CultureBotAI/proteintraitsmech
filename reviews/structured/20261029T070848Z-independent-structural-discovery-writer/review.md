# Independent review of the bounded structural-discovery writer and regression tests

- Review: 20261029T070848Z-independent-structural-discovery-writer
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-29T07:08:07Z
- Finished UTC: 2026-10-29T07:08:48Z
- Reviewer: Codex agent /root/preflight_boundary_review (independent)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: false

## Summary

Both current maintained code targets are positively assessed. Independent probes reproduce safe refusals for the escaped-YAML identity collision, dry-run report clobber and CRLF replay/hash defects reported under issue1204. Manifest source hashes now bind captured bytes. Thirteen focused tests passed independently. There are no new confirmed findings within this writer-safety scope. The scientific manifest, candidate novelty, biological evidence, detector execution and corpus application are excluded.

## Scope And Provenance

Complete read and bounded independent writer-safety review of the current new structural-discovery seeder and its regression test file, including manifest input invariants, exact-path safety, decoded ID/xref collisions, native strict validation, dry-run/apply/replay behavior, report destination controls and source/output hash provenance.

Selection: Explicit parent-assigned two-file maintained code scope; all2 targets reviewed. No sampling of scientific records.
Coverage: full; 2 reviewed / 2 in the declared population.
Source: working_tree at Git base 7276814bdf3bed73569a202c5e2c4b404e43d8f1.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| structural-discovery-seeder | scripts/seed_structural_discovery.py | maintained | Bounded structural-discovery new-record seeder |
| structural-discovery-seeder-tests | tests/test_seed_structural_discovery.py | maintained | Structural-discovery writer regression tests |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Native exact-input inspection | passed | True | structural-discovery-seeder, structural-discovery-seeder-tests | Native inspect bound both targets and20 context files to current working-tree bytes at7276814bdf3bed73569a202c5e2c4b404e43d8f1. Mutable scientific manifest is excluded. |
| Independent fixed writer safety probes | passed | True | structural-discovery-seeder, structural-discovery-seeder-tests | Escaped identifier and xref, CRLF edit, protected/existing/symlink-escape report paths and invalid apply report all refuse safely. Fresh owned report, captured manifest digest, default dry-run and validated replay positive controls pass. |
| Complete focused maintained seeder tests | passed | True | structural-discovery-seeder, structural-discovery-seeder-tests | 13 passed in0.64s. Tests cover dry-run, idempotence, preservation, literal/escaped ID and xref collisions, late schema failure, traversal/status/canary guards, byte-exact replay and report-path rules. |
| Historical source reconstruction verified against original digests | passed | True | structural-discovery-seeder, structural-discovery-seeder-tests | Reconstructed initial seeder and tests match the exact independently recorded pre-fix SHA256 values96cc0749... andb516c6...; prior negative helper/results/reports remain unchanged. |

## Scientific And Domain Assessments

### Native validated new-record writer and bounded ownership

ownership: supported. Targets: structural-discovery-seeder.

Candidate creation uses write_record(validate=True) after full selected-batch preflight. Exact structural paths, class/axis/PROPOSED status and source/license/recipe presence guards are retained. Changed destinations refuse replacement; no global exclusivity is claimed.

### Issue1204 decoded ID/xref collision guard

identity: supported. Targets: structural-discovery-seeder, structural-discovery-seeder-tests.

Every discovered YAML/YML corpus file is parsed, including ignored and hidden paths. Independent strictly valid escaped identifier/xref fixtures now refuse before creating a destination; the raw SDW-001 behavior is absent from current target bytes.

### Issue1204 report path cannot bypass dry-run or native writer

consistency: supported. Targets: structural-discovery-seeder, structural-discovery-seeder-tests.

main validates the report destination before invoking seed. Protected paths, existing evidence and a symlinked escape refuse; exclusive creation prevents silent report replacement. Independent actual-entry tests confirm invalid apply reports do not seed first.

### Issue1204 replay bytes and manifest digest binding

provenance: supported. Targets: structural-discovery-seeder, structural-discovery-seeder-tests.

Exact byte comparison refuses CRLF-only existing edits without replacement. Successful replay reports actual output hashes. One captured manifest byte snapshot supplies parsing and the reported digest; injected later fixture edit does not falsify input provenance.

### Focused safety tests and independent adversarial controls

completeness: supported. Targets: structural-discovery-seeder-tests.

Both maintained test scenarios and independent probes exercise distinguishing inputs, not only implementation-shaped success assertions.13 focused cases passed; independent main-order, digest and strictly valid escaped-ID controls complement their coverage.

### Historical negative evidence and native-review lineage

provenance: supported. Targets: structural-discovery-seeder, structural-discovery-seeder-tests.

Raw negative/fixed observations and probe helpers are retained, with exact initial source/test reconstructions. The native review records current passing code assessments and links prior raw evidence; it does not invent native predecessor finding identities or silently rewrite earlier results.

## Findings

No findings recorded within this review's declared scope.

## Recommended Actions And Acceptance Checks

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| current-seeder | scripts/seed_structural_discovery.py; scripts/seed_structural_discovery.py | supports | Full current maintained writer read; native validated output route, parsed corpus identity scan, byte preimage check, captured manifest hash and prevalidated exclusive report path assessed. |
| current-tests | tests/test_seed_structural_discovery.py; tests/test_seed_structural_discovery.py | supports | Full maintained test file read;13 independently executed cases and their distinguishing failure inputs assessed. |
| native-writer | scripts/record_io.py; scripts/record_io.py | supports | Native write_record(validate=True) delegates to staged closed-schema validation and atomic one-record replacement; default merge behavior is not treated as collision permission. |
| native-validation | scripts/validate_strict.py; scripts/validate_strict.py | supports | Closed-mode LinkML validation used by the writer and probes; no scientific truth or cross-record novelty guarantee inferred. |
| native-contract | docs/record-reviews.md; docs/record-reviews.md | supports | Native inspect, provenance, evidence and immutable-review requirements read. Raw historical observations are not fabricated as native predecessor reviews. |
| add-record-contract | .claude/skills/add-record/SKILL.md; .claude/skills/add-record/SKILL.md | supports | New records require validated native seeding, class/axis/status/source constraints and separate actual detection/evidence gates. |
| fixed-probes | research/structural-discovery-20261028/preflight/seeder-fixed-probes.json; research/structural-discovery-20261028/preflight/seeder-fixed-probes.json | supports | Independent fixture results: all prior failures now refuse, actual main report order is exercised, manifest digest binds consumed bytes, positive dry-run/apply/replay hashes match. |
| fixed-helper | research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py; research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py | supports | Retained independent probe implementation, purpose/inputs/outputs/date/issue and temporary-only execution contract inspected. |
| fixed-review | research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json; research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json | supports | Prior raw independent follow-up records exact current implementation/test hashes,13-test independent execution and resolved raw SDW failure observations; reused only after byte equality. |
| initial-review | research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json; research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json | context_only | Raw initial independent review identifies SDW-001/002/003 and exact original code/test hashes. It was not a native saved review; no previous_occurrences identity is claimed. |
| initial-probes | research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json; research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json | context_only | Original independent negative observations: duplicate decoded identity created; dry-run report overwrote a synthetic trait; CRLF unchanged report hash disagreed with bytes. |
| initial-helper | research/structural-discovery-20261028/preflight/probe_discovery_seeder.py; research/structural-discovery-20261028/preflight/probe_discovery_seeder.py | context_only | Historical helper intentionally demonstrates old accepting behavior and will refuse/raise against fixed maintained code. Preserve its historical output instead of relabelling it as a passing rerun. |
| initial-seeder | research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py; research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py | context_only | Initial seeder reconstructed from captured tool-read text and verified byte-identical to96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a. |
| initial-tests | research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py; research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py | context_only | Initial tests reconstructed from captured tool-read text and verified byte-identical tob516c6afbc86b5c704a3b311d257bc0c1e8636f4740f10237de9f8952e8b33eb. |
| reconstruction | research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json; research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json | supports | Reconstruction provenance records expected/observed equal digests, manual method and historical execution/lineage limits. |
| issue1204-context | research/structural-discovery-20261028/seeder-findings-issue-body.md; research/structural-discovery-20261028/seeder-findings-issue-body.md | context_only | Retained issue body describes the same3 independently reproduced writer failures and acceptance checks; parent supplied GitHub issue1204 link. No reviewer remote action. |

## Limits And Additional Notes

- This is completed bounded code review, scientific_review:false. No scientific manifest, candidate class identity, evidence/license claims, actual detection recipe behavior, parent relationships or protein qualification was accepted.
- The mutable data/curation/structural_trait_discovery.yaml is excluded from source. Earlier raw reports contain a historical manifest hash as context only; native save must not treat it as a current judged input.
- All independent apply-mode probes ran only in disposable synthetic fixture trees. No real corpus apply or full real-corpus scan was performed by this reviewer.
- Focused checks and independent probes were executed before this native-format observation and reused only after inspect confirmed identical code/test/context bytes. Broader lint/audit-writer/full-suite/remote publication gates remain parent responsibilities.
- The supported contract is one writer in an isolated worktree. No global ID reservation, cross-machine exclusion, concurrent-writer transaction or full batch atomicity is inferred.
- Initial SDW observations were raw JSON reports rather than saved native RecordReview bundles. findings:[] means no current scoped findings; it is not a fabricated native closure of those raw observations or an automatic GitHub issue closure.
- Historical source copies were reconstructed after fixes from captured initial text and verified against previously recorded exact hashes; their original relative-root assumptions make direct in-place execution inappropriate.
- This input has not been saved as an immutable native bundle by the reviewer. Parent will run the saver after ensuring Git visibility and unchanged source bytes. No Git, network, goal, cycle or session action was performed.
- Standalone review: no run_id, cycle or stage binding is invented.
- Parent reported filing https://github.com/CultureBotAI/proteintraitsmech/issues/1204; this reviewer did not fetch, edit or close that issue.
- The three original code defects and additional manifest hash observation are addressed in current assessments, with historical evidence preserved separately.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261029T070848Z-independent-structural-discovery-writer
kind: repository
repository: CultureBotAI/proteintraitsmech
title: Independent review of the bounded structural-discovery writer and regression
  tests
started_at: '2026-10-29T07:08:07Z'
finished_at: '2026-10-29T07:08:48Z'
reviewer:
  identity: Codex agent /root/preflight_boundary_review
  kind: agent
  independence: independent
  independence_basis: This reviewer did not author or modify the maintained seeder
    or tests. The parent owns implementation. This reviewer independently read both
    files and authored temporary-fixture adversarial probes; the new observation reuses
    those executed checks only after native inspection confirms identical target bytes.
skill: User-directed independent writer review using docs/record-reviews.md; no scientific
  curation skill invoked
completion: completed
verdict: pass_with_limitations
scientific_review: false
summary: Both current maintained code targets are positively assessed. Independent
  probes reproduce safe refusals for the escaped-YAML identity collision, dry-run
  report clobber and CRLF replay/hash defects reported under issue1204. Manifest source
  hashes now bind captured bytes. Thirteen focused tests passed independently. There
  are no new confirmed findings within this writer-safety scope. The scientific manifest,
  candidate novelty, biological evidence, detector execution and corpus application
  are excluded.
source:
  git_revision: 7276814bdf3bed73569a202c5e2c4b404e43d8f1
  state: working_tree
  inputs:
  - path: .claude/skills/add-record/SKILL.md
    sha256: c4cf4fe01c66c294ab66a5b99f574a670fdec2dcfe221d390a72ba95e23fd821
    role: context
  - path: AGENTS.md
    sha256: 8bfd4da2ecf01cbe56cdbfe1e7860a9f343eefdb984ef6775c7031a7c02a3349
    role: context
  - path: conf/record_review.yaml
    sha256: a776553cee8cbe239d4d00ea27d728c271ee7462a42532ccf7e5bd2a9e285a2b
    role: context
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json
    sha256: 542debde353e54eed418d6755362b7f64eac3ae981000151a98530ec1c1259de
    role: context
  - path: research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py
    sha256: 96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a
    role: context
  - path: research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py
    sha256: b516c6afbc86b5c704a3b311d257bc0c1e8636f4740f10237de9f8952e8b33eb
    role: context
  - path: research/structural-discovery-20261028/preflight/probe_discovery_seeder.py
    sha256: b0a5435bc0e1809e29aa6816698fdca37fce53d25eecd99c2b557a218f1fceab
    role: context
  - path: research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py
    sha256: b48a3e3f6d3916b0e0c427212996e783a973f6dbf3cf505d682baf7ef71c8571
    role: context
  - path: research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json
    sha256: fcf1701cc0372eb15190cd1f9868efb2d405b2272b95ca4e199b843b6e8a25a6
    role: context
  - path: research/structural-discovery-20261028/preflight/seeder-fixed-probes.json
    sha256: cf1b5aafac4e3a515d556d9f3463762ab05b5343005a8e1b8e4554c0220d6c1c
    role: context
  - path: research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json
    sha256: 9371e10a73c8d4b2e2604bc23757df1d8ab2d8ca8661aa384df1bd50145a3527
    role: context
  - path: research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json
    sha256: ab88795edfd1090cf780158ed09ef6de141032a21106a32494d5ab058ea4ca53
    role: context
  - path: research/structural-discovery-20261028/seeder-findings-issue-body.md
    sha256: f97c2d565998c07bc16dedbcf239138bbc7f3fa75e160b5d4649de678af9b286
    role: context
  - path: schema/record_review.yaml
    sha256: 229baf9b69118a1fe318e4c31085c0820e4e3d1365e7b04d6ace451b7c35f9bb
    role: context
  - path: scripts/record_io.py
    sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
    role: context
  - path: scripts/record_review.py
    sha256: 95a4ec41e38ec47ba3578e76838c46a0adbf47e49ad3636524735d08cfcb1c4d
    role: context
  - path: scripts/seed_structural_discovery.py
    sha256: 7143fb829f46ea77a48a9976d27d3e31f78ac1c5e3e845968fa52ef84b75dbd3
    role: target
  - path: scripts/validate_strict.py
    sha256: a36652f276ee85a3b9328172ff3f8a3661713860b66c8b3ca8ca715665683b26
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
  - path: tests/test_seed_structural_discovery.py
    sha256: 863f49dbf21ecba26e1059289b19d7631ba13a23cf433db4797a892f62e0fec8
    role: target
scope:
  description: Complete read and bounded independent writer-safety review of the current
    new structural-discovery seeder and its regression test file, including manifest
    input invariants, exact-path safety, decoded ID/xref collisions, native strict
    validation, dry-run/apply/replay behavior, report destination controls and source/output
    hash provenance.
  selection: Explicit parent-assigned two-file maintained code scope; all2 targets
    reviewed. No sampling of scientific records.
  coverage: full
  population_size: 2
  reviewed_target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  exclusions:
  - target: data/curation/structural_trait_discovery.yaml and emitted scientific records
    reason: Mutable scientific manifest deliberately excluded from source and judgement;
      code guards were tested using synthetic temporary fixtures. Historical raw reports
      may mention an earlier manifest digest only as context, not current scientific
      acceptance.
  - target: Other writers, full real-corpus preflight, repository-wide tests/CI and
      publication gates
    reason: Parent owns broader acceptance. This bounded code review does not recertify
      unrelated maintained code or remote checks.
  - target: Global identifier reservation, concurrent multi-writer transactions, workflows
      and sessions
    reason: Explicit single-writer isolated-worktree and standalone-task contract;
      these broader guarantees/actions were neither requested nor claimed.
targets:
- target_id: structural-discovery-seeder
  path: scripts/seed_structural_discovery.py
  label: Bounded structural-discovery new-record seeder
  kind: maintained
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_structural_discovery.py
    role: Maintained writer and manifest/collision/report safety guards
- target_id: structural-discovery-seeder-tests
  path: tests/test_seed_structural_discovery.py
  label: Structural-discovery writer regression tests
  kind: maintained
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: tests/test_seed_structural_discovery.py
    role: Maintained focused safety regression coverage
checks:
- check_id: native-inspection
  name: Native exact-input inspection
  status: passed
  required: true
  summary: Native inspect bound both targets and20 context files to current working-tree
    bytes at7276814bdf3bed73569a202c5e2c4b404e43d8f1. Mutable scientific manifest
    is excluded.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/record_review.py inspect
    --targets research/structural-discovery-20261028/preflight/native-code-targets.json
    --input scripts/record_io.py --input scripts/validate_strict.py --input src/proteintraitsmech/schema/proteintraitsmech.yaml
    --input AGENTS.md --input .claude/skills/add-record/SKILL.md --input docs/record-reviews.md
    --input docs/record-review-profile.md --input conf/record_review.yaml --input
    schema/record_review.yaml --input scripts/record_review.py --input research/structural-discovery-20261028/seeder-findings-issue-body.md
    --input research/structural-discovery-20261028/preflight/probe_discovery_seeder.py
    --input research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json
    --input research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json
    --input research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py
    --input research/structural-discovery-20261028/preflight/seeder-fixed-probes.json
    --input research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json
    --input research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py
    --input research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py
    --input research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json
  exit_code: 0
  evidence_ids:
  - current-seeder
  - current-tests
  - native-contract
  scope_note: Inspection does not save an immutable review or certify science.
- check_id: independent-probes
  name: Independent fixed writer safety probes
  status: passed
  required: true
  summary: Escaped identifier and xref, CRLF edit, protected/existing/symlink-escape
    report paths and invalid apply report all refuse safely. Fresh owned report, captured
    manifest digest, default dry-run and validated replay positive controls pass.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py
  exit_code: 0
  evidence_ids:
  - fixed-probes
  - fixed-helper
  scope_note: Previously executed independently at the identical current seeder/test
    hashes; no real corpus apply. Exact unchanged source compiled with disposable
    fixture roots and actual native validator/writer.
- check_id: focused-tests
  name: Complete focused maintained seeder tests
  status: passed
  required: true
  summary: 13 passed in0.64s. Tests cover dry-run, idempotence, preservation, literal/escaped
    ID and xref collisions, late schema failure, traversal/status/canary guards, byte-exact
    replay and report-path rules.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  command: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q tests/test_seed_structural_discovery.py
    --rootdir=. -p no:cacheprovider
  exit_code: 0
  evidence_ids:
  - current-tests
  - fixed-review
  scope_note: Independent execution reused after exact-hash native inspection; broader
    suite not rerun.
- check_id: historical-byte-reconstruction
  name: Historical source reconstruction verified against original digests
  status: passed
  required: true
  summary: Reconstructed initial seeder and tests match the exact independently recorded
    pre-fix SHA256 values96cc0749... andb516c6...; prior negative helper/results/reports
    remain unchanged.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  command: shasum -a 256 research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py
    research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py
  exit_code: 0
  evidence_ids:
  - initial-seeder
  - initial-tests
  - reconstruction
  scope_note: Equality to expected hashes was assessed from the tool output. No historical
    file was executed in the real corpus.
evidence:
- evidence_id: current-seeder
  kind: record_content
  reference: scripts/seed_structural_discovery.py
  locator: scripts/seed_structural_discovery.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Full current maintained writer read; native validated output route, parsed
    corpus identity scan, byte preimage check, captured manifest hash and prevalidated
    exclusive report path assessed.
  snapshot_sha256: 7143fb829f46ea77a48a9976d27d3e31f78ac1c5e3e845968fa52ef84b75dbd3
- evidence_id: current-tests
  kind: record_content
  reference: tests/test_seed_structural_discovery.py
  locator: tests/test_seed_structural_discovery.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Full maintained test file read;13 independently executed cases and their
    distinguishing failure inputs assessed.
  snapshot_sha256: 863f49dbf21ecba26e1059289b19d7631ba13a23cf433db4797a892f62e0fec8
- evidence_id: native-writer
  kind: record_content
  reference: scripts/record_io.py
  locator: scripts/record_io.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Native write_record(validate=True) delegates to staged closed-schema validation
    and atomic one-record replacement; default merge behavior is not treated as collision
    permission.
  snapshot_sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
- evidence_id: native-validation
  kind: record_content
  reference: scripts/validate_strict.py
  locator: scripts/validate_strict.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Closed-mode LinkML validation used by the writer and probes; no scientific
    truth or cross-record novelty guarantee inferred.
  snapshot_sha256: a36652f276ee85a3b9328172ff3f8a3661713860b66c8b3ca8ca715665683b26
- evidence_id: native-contract
  kind: authority
  reference: docs/record-reviews.md
  locator: docs/record-reviews.md
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Native inspect, provenance, evidence and immutable-review requirements
    read. Raw historical observations are not fabricated as native predecessor reviews.
  snapshot_sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
- evidence_id: add-record-contract
  kind: authority
  reference: .claude/skills/add-record/SKILL.md
  locator: .claude/skills/add-record/SKILL.md
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: New records require validated native seeding, class/axis/status/source
    constraints and separate actual detection/evidence gates.
  snapshot_sha256: c4cf4fe01c66c294ab66a5b99f574a670fdec2dcfe221d390a72ba95e23fd821
- evidence_id: fixed-probes
  kind: validation
  reference: research/structural-discovery-20261028/preflight/seeder-fixed-probes.json
  locator: research/structural-discovery-20261028/preflight/seeder-fixed-probes.json
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: 'Independent fixture results: all prior failures now refuse, actual main
    report order is exercised, manifest digest binds consumed bytes, positive dry-run/apply/replay
    hashes match.'
  snapshot_sha256: cf1b5aafac4e3a515d556d9f3463762ab05b5343005a8e1b8e4554c0220d6c1c
- evidence_id: fixed-helper
  kind: validation
  reference: research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py
  locator: research/structural-discovery-20261028/preflight/probe_discovery_seeder_fixed.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Retained independent probe implementation, purpose/inputs/outputs/date/issue
    and temporary-only execution contract inspected.
  snapshot_sha256: b48a3e3f6d3916b0e0c427212996e783a973f6dbf3cf505d682baf7ef71c8571
- evidence_id: fixed-review
  kind: prior_review
  reference: research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json
  locator: research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Prior raw independent follow-up records exact current implementation/test
    hashes,13-test independent execution and resolved raw SDW failure observations;
    reused only after byte equality.
  snapshot_sha256: fcf1701cc0372eb15190cd1f9868efb2d405b2272b95ca4e199b843b6e8a25a6
- evidence_id: initial-review
  kind: prior_review
  reference: research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json
  locator: research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: Raw initial independent review identifies SDW-001/002/003 and exact original
    code/test hashes. It was not a native saved review; no previous_occurrences identity
    is claimed.
  snapshot_sha256: 9371e10a73c8d4b2e2604bc23757df1d8ab2d8ca8661aa384df1bd50145a3527
- evidence_id: initial-probes
  kind: validation
  reference: research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json
  locator: research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: 'Original independent negative observations: duplicate decoded identity
    created; dry-run report overwrote a synthetic trait; CRLF unchanged report hash
    disagreed with bytes.'
  snapshot_sha256: ab88795edfd1090cf780158ed09ef6de141032a21106a32494d5ab058ea4ca53
- evidence_id: initial-helper
  kind: validation
  reference: research/structural-discovery-20261028/preflight/probe_discovery_seeder.py
  locator: research/structural-discovery-20261028/preflight/probe_discovery_seeder.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: Historical helper intentionally demonstrates old accepting behavior and
    will refuse/raise against fixed maintained code. Preserve its historical output
    instead of relabelling it as a passing rerun.
  snapshot_sha256: b0a5435bc0e1809e29aa6816698fdca37fce53d25eecd99c2b557a218f1fceab
- evidence_id: initial-seeder
  kind: record_content
  reference: research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py
  locator: research/structural-discovery-20261028/preflight/historical/seed_structural_discovery.initial.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: Initial seeder reconstructed from captured tool-read text and verified
    byte-identical to96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a.
  snapshot_sha256: 96cc0749a8791d599bafeefe3eea9bf2258f900e25d078416fe8553edf9c6e4a
- evidence_id: initial-tests
  kind: record_content
  reference: research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py
  locator: research/structural-discovery-20261028/preflight/historical/test_seed_structural_discovery.initial.py
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: Initial tests reconstructed from captured tool-read text and verified byte-identical
    tob516c6afbc86b5c704a3b311d257bc0c1e8636f4740f10237de9f8952e8b33eb.
  snapshot_sha256: b516c6afbc86b5c704a3b311d257bc0c1e8636f4740f10237de9f8952e8b33eb
- evidence_id: reconstruction
  kind: prior_review
  reference: research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json
  locator: research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json
  accessed_at: '2026-10-29T07:08:48Z'
  support: supports
  summary: Reconstruction provenance records expected/observed equal digests, manual
    method and historical execution/lineage limits.
  snapshot_sha256: 542debde353e54eed418d6755362b7f64eac3ae981000151a98530ec1c1259de
- evidence_id: issue1204-context
  kind: prior_review
  reference: research/structural-discovery-20261028/seeder-findings-issue-body.md
  locator: research/structural-discovery-20261028/seeder-findings-issue-body.md
  accessed_at: '2026-10-29T07:08:48Z'
  support: context_only
  summary: Retained issue body describes the same3 independently reproduced writer
    failures and acceptance checks; parent supplied GitHub issue1204 link. No reviewer
    remote action.
  snapshot_sha256: f97c2d565998c07bc16dedbcf239138bbc7f3fa75e160b5d4649de678af9b286
assessments:
- assessment_id: writer-contract
  area: ownership
  topic: Native validated new-record writer and bounded ownership
  outcome: supported
  summary: Candidate creation uses write_record(validate=True) after full selected-batch
    preflight. Exact structural paths, class/axis/PROPOSED status and source/license/recipe
    presence guards are retained. Changed destinations refuse replacement; no global
    exclusivity is claimed.
  target_ids:
  - structural-discovery-seeder
  evidence_ids:
  - current-seeder
  - native-writer
  - add-record-contract
  - fixed-probes
- assessment_id: decoded-collision
  area: identity
  topic: Issue1204 decoded ID/xref collision guard
  outcome: supported
  summary: Every discovered YAML/YML corpus file is parsed, including ignored and
    hidden paths. Independent strictly valid escaped identifier/xref fixtures now
    refuse before creating a destination; the raw SDW-001 behavior is absent from
    current target bytes.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  evidence_ids:
  - current-seeder
  - current-tests
  - fixed-probes
  - initial-probes
- assessment_id: report-preservation
  area: consistency
  topic: Issue1204 report path cannot bypass dry-run or native writer
  outcome: supported
  summary: main validates the report destination before invoking seed. Protected paths,
    existing evidence and a symlinked escape refuse; exclusive creation prevents silent
    report replacement. Independent actual-entry tests confirm invalid apply reports
    do not seed first.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  evidence_ids:
  - current-seeder
  - current-tests
  - fixed-probes
  - fixed-helper
- assessment_id: exact-byte-provenance
  area: provenance
  topic: Issue1204 replay bytes and manifest digest binding
  outcome: supported
  summary: Exact byte comparison refuses CRLF-only existing edits without replacement.
    Successful replay reports actual output hashes. One captured manifest byte snapshot
    supplies parsing and the reported digest; injected later fixture edit does not
    falsify input provenance.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  evidence_ids:
  - current-seeder
  - current-tests
  - fixed-probes
  - initial-probes
- assessment_id: meaningful-tests
  area: completeness
  topic: Focused safety tests and independent adversarial controls
  outcome: supported
  summary: Both maintained test scenarios and independent probes exercise distinguishing
    inputs, not only implementation-shaped success assertions.13 focused cases passed;
    independent main-order, digest and strictly valid escaped-ID controls complement
    their coverage.
  target_ids:
  - structural-discovery-seeder-tests
  evidence_ids:
  - current-tests
  - fixed-probes
  - fixed-review
  - initial-probes
  metrics:
  - name: Focused tests passed
    value: 13
    unit: test cases
    definition: Cases independently executed in the single maintained focused test
      file; not repository-wide coverage.
    denominator: 13
    minimum: 0
    maximum: 13
- assessment_id: historical-evidence
  area: provenance
  topic: Historical negative evidence and native-review lineage
  outcome: supported
  summary: Raw negative/fixed observations and probe helpers are retained, with exact
    initial source/test reconstructions. The native review records current passing
    code assessments and links prior raw evidence; it does not invent native predecessor
    finding identities or silently rewrite earlier results.
  target_ids:
  - structural-discovery-seeder
  - structural-discovery-seeder-tests
  evidence_ids:
  - initial-review
  - initial-probes
  - initial-helper
  - initial-seeder
  - initial-tests
  - reconstruction
  - native-contract
findings: []
actions: []
limitations:
- This is completed bounded code review, scientific_review:false. No scientific manifest,
  candidate class identity, evidence/license claims, actual detection recipe behavior,
  parent relationships or protein qualification was accepted.
- The mutable data/curation/structural_trait_discovery.yaml is excluded from source.
  Earlier raw reports contain a historical manifest hash as context only; native save
  must not treat it as a current judged input.
- All independent apply-mode probes ran only in disposable synthetic fixture trees.
  No real corpus apply or full real-corpus scan was performed by this reviewer.
- Focused checks and independent probes were executed before this native-format observation
  and reused only after inspect confirmed identical code/test/context bytes. Broader
  lint/audit-writer/full-suite/remote publication gates remain parent responsibilities.
- The supported contract is one writer in an isolated worktree. No global ID reservation,
  cross-machine exclusion, concurrent-writer transaction or full batch atomicity is
  inferred.
- Initial SDW observations were raw JSON reports rather than saved native RecordReview
  bundles. findings:[] means no current scoped findings; it is not a fabricated native
  closure of those raw observations or an automatic GitHub issue closure.
- Historical source copies were reconstructed after fixes from captured initial text
  and verified against previously recorded exact hashes; their original relative-root
  assumptions make direct in-place execution inappropriate.
- This input has not been saved as an immutable native bundle by the reviewer. Parent
  will run the saver after ensuring Git visibility and unchanged source bytes. No
  Git, network, goal, cycle or session action was performed.
notes:
- 'Standalone review: no run_id, cycle or stage binding is invented.'
- Parent reported filing https://github.com/CultureBotAI/proteintraitsmech/issues/1204;
  this reviewer did not fetch, edit or close that issue.
- The three original code defects and additional manifest hash observation are addressed
  in current assessments, with historical evidence preserved separately.
links:
- https://github.com/CultureBotAI/proteintraitsmech/issues/1204
- research/structural-discovery-20261028/preflight/seeder-preliminary-code-review.json
- research/structural-discovery-20261028/preflight/seeder-preliminary-probes.json
- research/structural-discovery-20261028/preflight/seeder-fixed-code-review.json
- research/structural-discovery-20261028/preflight/seeder-fixed-probes.json
- research/structural-discovery-20261028/preflight/historical/reconstruction-provenance.json
tags:
- structural-discovery
- independent-code-review
- writer-safety
- issue-1204
- standalone
```
