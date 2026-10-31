# PR1205 adversarial follow-up, 2026-10-31

This is ordinary follow-up authorized by the user's request for adversarial
review, issues, fixes, merge and branch deletion. It is not a new goal or cycle.
The reviewed original head is `bc0c6d97aaab0ba20fcf8be28bc1527430679ccb`.
Current main `c0d87f89e18a1c4a09904a835cf782d84d9d53d1` was integrated in
`9dae07a86b815f9f21cd0ce96b050c8e4192feaf`; the native baseline check confirms
429,421 records with unchanged 5,544 mismatch identities and 5,800 checked pairs.

The original worktree became unreadable to this session at the operating-system
boundary. Work continued in a full isolated checkout under `/private/tmp/`.
No original worktree, worker, pane, session, goal or evidence was removed or
restarted. Local machine paths in probe outputs are historical diagnostics,
not portable runtime dependencies.

## Findings and bounded repairs

- #1225: reject non-string/blank/comment-only recipe coverage, primary UniProtKB
  protein IDs and category/directory mismatches before writing a batch.
- #1226: reject redirected report ancestry and non-directory parents before
  invoking the writer; create allowed parent directories before seeding. Exclusive
  report output remains. This does not promise transactionality against later
  I/O failures or concurrent mutations.
- #1227: add unchanged SQL-supplement CC-BY-2.0 attribution and withdraw exactly
  two full manual files from the final release tree. See the adjacent
  [source notice](../structural-discovery-20261028/motifs/SOURCE-NOTICES.md).
  Historical bytes/hashes and all immutable reviews remain preserved.
- #1206 follow-up: recover two explicitly pinned historical review bases in CI,
  including the reviewed PR1205 head, without recreating retired refs or changing
  the native validator. Both commits are needed after squash merge.

The three scientific records and maintained manifest remain byte-identical to
the original reviewed head. All remain PROPOSED, with no new qualified/canonical
protein carriers, coordinates or causal graphs. CAVER/DSSP recipes were inspected
but not executed. Science review independence is disclosed per target: the
beta-arch reviewer previously authored candidate research; the cavity record
reviewer did not author those candidate records. A separate prior beta-arch
reviewer and the root agent also cross-checked its primary-text support.

## Retained review and helper provenance

- `code/`: immutable initial byte capture, native inspection, malformed-input
  probes, findings, and subsequent fixed-code/CI probes. Initial negative probes
  demonstrate old acceptance and are intentionally not passing assertions about
  the repaired code. See each helper's docstring and the directory README.
- `science/`: native inspection, complete historical review inputs, bounded
  source/collision checks and validations. The three `*-review-completed.yaml`
  files are saved through the native review helper under `reviews/structured/`.
  Earlier drafts and a failed intermediate schema validation remain disclosed.
- `provenance/`: initial 27-helper/137-file/10-additive-checksum audit, source-rights
  findings, official-package inspection and the complete unchanged GNU GPLv3.
  Its README documents helper purposes, inputs, outputs, dates and issue context.

Every task-created helper is retained here with its results. Historical snapshot
files, old publication manifests and old review bundles are not rewritten to
pretend they describe the follow-up. The original initial-manifest counts are
historical: two of its full-source artifacts are now intentionally withdrawn.
Temporary logs and disposable fixture repositories are not portable inputs.
Final CI/check/merge evidence belongs to the PR control plane and need not cause
a recursive evidence commit.

`materialize_review_inputs.py` is the coordinator's additional retained helper
(2026-10-31, #1206): it reads existing native `git_commit` review pins, explicitly
loads and hash-verifies missing historical Git blobs in this partial clone, and
writes a new timestamped receipt here. It verified 144 distinct input blobs for
12 historical reviews. This prepares the environment; the unchanged native
validator then passed all 38 bundles with `--base origin/main`. The initial
missing-blob failure is retained alongside the successful native result.

The native docs rebuild now reports 429,421 records, including 118,338 STRUCTURE
records, and verifies landing-page and SLC10 output consistency. See
`validation/` for exact local commands and receipts. Raw command logs preserve
their original trailing whitespace/blank lines; source whitespace checks exclude
only those `.log` receipts. The follow-up checksum receipt excludes itself and
records the actual staged publication bytes, not hypothetical later CI results.
