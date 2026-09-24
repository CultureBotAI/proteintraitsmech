# Adversarial review of PR #756 — 2026-09-24

Reviewed the implementation at `e8714eb3ad6`, then reproduced and repaired the
findings below in the feature worktree. This was a self-review, not an independent
maintainer approval. The user separately authorized merging after review and fixes.

The review covered descriptor identity and result shape, evidence provenance,
nonstandard residues, cohort/map joins, cohort-file parsing, output-overwrite
guards, numerical replay, map filters/CSV export and stale-overlay rejection.

## Findings and fixes

- **P2 — [#757](https://github.com/CultureBotAI/proteintraitsmech/issues/757):
  descriptor contracts could be bypassed.** A catalog entry with descriptor ID
  `proteintraitsmech:B03` and inventory ID `B99` allowed a rehashed fraction of
  2.0 to validate. Incompatible family/result shapes could also reach a missing
  payload key. Catalog loading and direct observation validation now enforce the
  canonical ID, inventory ID, result kind and unit for each implemented pilot
  descriptor before invoking its scientific checks.
- **P2 — [#758](https://github.com/CultureBotAI/proteintraitsmech/issues/758):
  predictor provenance could be misrepresented.** A populated B22 observation
  passed after relabeling it `EXPERIMENT` or removing predictor mode. The adapter
  also claimed the local calculators' standard-residue-only policy on valid
  external scores for `AX`. Pilot descriptors now enforce their calculation or
  prediction evidence mode, populated B22 results require mode and full-reference
  context, and external predictor metadata does not inherit an invented alphabet
  or nonstandard-residue policy. Missing B22 placeholders remain valid.
- **P2 — [#759](https://github.com/CultureBotAI/proteintraitsmech/issues/759):
  a selected protein could disappear from the map.** A two-protein selection
  passed the bundle gate with only one protein plotted after refreshing the
  derived artifacts. The gate now requires each selected protein to occur exactly
  once in the map. Calculation and verification share cohort-file parsing,
  including indented comments. The general overlay builder still supports
  matching a subset from a broader observation store.

## Verification

- Fifteen new negative regression cases failed before their fixes; a positive
  two-protein cohort control already passed. All 382 targeted tests pass after
  the fixes, including 83 biophysical calculation/publication tests.
- Repository-wide Ruff and `git diff --check` pass.
- The complete pilot was regenerated with calculator version 1.0.1 and passed
  `just check-biophysical-pilot`. All 276 result payloads and statuses are exactly
  unchanged from the reviewed base. Method provenance and content identifiers
  changed, with matching manifest, TSV, analysis and map sidecar updates.
- An isolated headless Chrome check verified loading, 23-protein coverage,
  numerical filtering, CSV values/IDs, map switching, rejection of a stale
  sidecar and a 390-pixel layout. It observed no JavaScript runtime errors.

No further merge-blocking findings remain from this review. Required PR and merge
queue checks must pass on the reviewed changes before landing; their final results
are recorded on [PR #756](https://github.com/CultureBotAI/proteintraitsmech/pull/756).
Real predictor acquisition, cohort expansion and the remaining descriptor roadmap
remain [#753](https://github.com/CultureBotAI/proteintraitsmech/issues/753),
[#754](https://github.com/CultureBotAI/proteintraitsmech/issues/754) and
[#755](https://github.com/CultureBotAI/proteintraitsmech/issues/755).
