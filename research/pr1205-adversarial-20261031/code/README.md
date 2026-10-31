# Independent PR1205 code review, 2026-10-31

Owner: Codex agent `/root/preflight_boundary_review`. This is an ordinary PR
follow-up, not a new goal or workflow cycle. The parent owns maintained changes,
Git/index operations, issues, publication, native queue integration and branch
retirement. The reviewer owns only this new evidence directory.

Scope: the exact initial PR head `bc0c6d97aaab0ba20fcf8be28bc1527430679ccb`,
its seeder/tests, CI recovery, packaging helpers and integration with observed
main `c0d87f89e18a1c4a09904a835cf782d84d9d53d1`. Initial native inspection is
retained in `initial-code-inspection.json`; it is an observation, not a saved
scientific review. Initial and final code assessments remain separate. No
immutable prior native review or original publication manifest was rewritten.

The initial findings were filed by the parent as
[#1225](https://github.com/CultureBotAI/proteintraitsmech/issues/1225) (three
manifest guards) and
[#1226](https://github.com/CultureBotAI/proteintraitsmech/issues/1226) (two report
preflight boundaries). The explicit second historical CI base extends
[#1206](https://github.com/CultureBotAI/proteintraitsmech/issues/1206).
The older #1204 guard evidence remains historical context. Scientific source
rights/publication findings belong to the separate review and parent #1227 work.

## Helpers, inputs and outputs

Every helper below was authored on 2026-10-31 for this task. All are retained;
none is kept only in a temporary directory. The final inventory includes ignored
files independently of Git's ignore rules. Helpers write new observations, not
replacement historical reports.

| Helper | Purpose and inputs | Outputs / limitations |
| --- | --- | --- |
| `capture_review_inputs.py` | Exact commit/path allowlist read through GitHub `gh api`, for PR1205 and the observed main commit. | Byte-pinned copies below `inputs/` plus a timestamped inventory on success. The first attempt failed on API/DNS availability before a complete inventory; its source remains unchanged. It makes no remote mutations. |
| `capture_local_inputs.py` | Same allowlist, reading root-materialized objects with `git show`. | Retained all 19 PR inputs and a partial main subset, then stopped at an unmaterialized main workflow blob. Although the helper invokes no explicit fetch, Git attempted a lazy promisor fetch and failed on DNS. Do not call this a complete main snapshot or a network-free replay. Do not rerun until the required objects have been materialized by the parent. |
| `probe_seeder_boundaries.py` | Captured original seeder plus hash-pinned native writer, validator and schema; malformed synthetic records and report paths. | `seeder-boundary-probes-20261031T204540498534Z.json` documents five accepting guard defects, a positive control and a correctly rejected wrong-axis control. It applies only inside disposable fixture trees; the submitted three records are not claimed to contain these faults. |
| `probe_fixed_seeder.py` | Current maintained seeder; original fixture helper; unchanged native validation; read-only comparison with the three current records. | New source copy in `fixed-source-snapshots/<sha>.py` and new timestamped results. The first fix iteration still created a record before a read-only report-parent failure. Its source/result are retained. The final iteration refuses before mutation and keeps all three real emitted byte strings identical. |
| `probe_dual_review_base_restore.py` | Current workflow shell plus the unchanged historical `research/structural-discovery-20261028/ci-followup/probe_review_base_restore.py` fixture utilities. | Four cases: both commits missing, both present with unavailable origin, first present/second missing, unavailable second. It asserts the two production SHAs and substitutes only those literals. Local disposable Git origins and clients are the only Git state it changes. HEAD, refs, index, FETCH_HEAD, configuration and working files remain identical across each tested step. |

`inputs/<commit>/<original-path>` are exact source copies, not new maintained
entrypoints. In particular, their original `__file__` assumptions do not make
copied scripts independently runnable in place. Only the captured original
seeder is executed through a namespace bound to a disposable fixture root.
`fixed-source-snapshots/` preserves every tested maintained seeder iteration by
its SHA-256. These are historical source evidence, not extra supported writers.
The snapshot inventory records path, source commit when applicable, bytes and
hashes. It does not imply every referenced historical corpus or remote state is
available in a clean clone.

## Evidence and replay limits

`initial-code-findings.json` records the five stable finding IDs, exact native
rules, minimal fixes and proposed regression coverage. `final-code-assessment.json`
records observed dispositions against exact fixed input hashes and links the
prior report explicitly. These are bounded code audits, not fabricated native
RecordReview lineage or scientific acceptance. The parent runs native checks and
owns any native saving required by its review workflow.

The original 13 tests passed before the new findings. The independently rerun
final suite contains 29 passing tests. The eight final synthetic cases establish
only the specific guards tested. Later I/O failure or concurrent mutation can
still fail a command; no global transaction or reservation is claimed. Temporary
paths and fixture Git commit IDs in probe results are historical diagnostics,
not durable external dependencies. No real corpus write, maintained-code edit,
actual repository Git mutation, scientific detector, goal or session action was
performed by this reviewer.

The two-pin CI probes use local filesystem origins. They do not establish live
GitHub availability after squash or deletion. Actual required CI and the native
SQUASH queue remain parent-owned gates. Historical review bases must remain
available without weakening canonical verification. The fixed code report also
keeps integrated docs rebuilding and full validation separate from the code
probe result.
