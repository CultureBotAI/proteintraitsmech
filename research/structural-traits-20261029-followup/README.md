# PR1202 follow-up provenance

This native research directory retains the 2026-10-29 bounded review and repair of
[issue1203](https://github.com/CultureBotAI/proteintraitsmech/issues/1203) in
[PR1202](https://github.com/CultureBotAI/proteintraitsmech/pull/1202). Its scripts
are task evidence, not maintained record writers. No helper is needed at runtime.
The maintained implementation is `scripts/structural_trait_curations.py` and
`scripts/curate_structural_traits.py`. Merge and cleanup were not authorized.

The baseline is `93c1a021d76a94fd299e0a1e3cf8f1b9671a3703`; the guard fix is
`9bf975d3b135ed72168451f0a670a16a7bb468f0`. All five helpers below were used or
retained on 2026-10-29 for issue1203/PR1202. Original parent review reports retain
their authorship. `helper-retention.json` proves exact preservation of the three
named temporary helper bodies; the temporary originals were not removed.

| Helper | Purpose and inputs | Outputs and execution limits |
| --- | --- | --- |
| `reproduce-stale-ledger.py` | Historical independent HTH reproduction, copied with its repository-root locator made relative. Reads the actual ledger, secondary seeder and editor. | Writes a temporary ledger/trait and adjacent `reproduce-stale-ledger.json`. The archived JSON records **old93c acceptance**, not current behavior. Under the fixed code the loader raises `ValueError` before output; that rejection is expected success of the fix. Do not rerun over historical evidence. |
| `code-review-probes.py` | Historical initial reviewer probe, retained from the parent with its root locator made relative. Requires exact93c HEAD/source bytes, its Git base and follow-up preimages. This copy was retained but not executed by the implementation worker. | Would write `code-review-probes.json` beside itself. It asserts the old-head context and demonstrates the pre-fix seeder discrepancy. It intentionally does not run at the fixed head. The original parent's probe result is referenced by `independent-code-review.json`. |
| `replay-proof.py` | Exact body of `/tmp/ptm-1202-replay-proof.py`. Reads current implementation/ledger, exact93c record bytes and c414739/follow-up Git preimages. It checks24 record replays,25 source-owner outputs and127 unrelated emissions. | Writes `replay-verification.json`; no corpus writes. Executed from repository root before the guard-fix commit. It can assess the same fixed implementation in a separate evidence checkout, but do not overwrite the retained historical result. |
| `run-bounded-validation.py` | Exact body of `/tmp/ptm-1202-run-bounded-validation.py`. Calls native24-record validation, graph/history/vendored gates and planned editor/review checks from repository root. Depends on the repository virtualenv, `just`, the named UV cache and network permission for vendored artifacts. | Writes `/tmp/ptm-1202-followup-gate-N.log` and `native-validation.json`. The historical run stopped after sandbox DNS blocked vendored-sync. The recorded permitted network retry and subsequent editor/review checks succeeded separately. This body is historical, not a one-command replay of the final aggregate receipt. |
| `prepare-evidence.py` | Exact body of `/tmp/ptm-1202-prepare-evidence.py`. Aggregated prior science review, scoped validation, inspection JSON and temporary logs into the local review input. | Wrote independent-delta/review-dispositions/native-validation JSON and `/tmp/ptm-1202-native-review.json`, later saved by the native helper. **Historical/nonportable**: it reads transient inputs, appends to an evolving receipt, uses fixed historical timing, and must not be executed over committed evidence. It does not reproduce a fresh independent review. |

## Temporary input mapping

`prepare-evidence.py` read `/tmp/ptm-1202-review-inspection.json`, now preserved
byte-for-byte as `review-input-inspection.json`. Its target hashes are independently
checked by the native review saver. The saved native pair is
`reviews/structured/20261029T044503Z-structural-ledger-guard-followup/`.

Its `/tmp/ptm-1202-followup-{lint,writers,vendored-retry,editor,reviews}.log` inputs
are mapped to the corresponding `command`, `log`, `output` and `exit_code` entries
in `native-validation.json`. The initial gate logs are retained there as well,
including the network failure and successful retry. The receipt records their
historical commands; the helper's original pre-aggregation input state was not
preserved separately, so no fresh end-to-end replay claim is made. The full test
command, result and log hash are in `full-test-result.json`; its original log is
`/tmp/ptm-1202-followup-test.log`.

`final-code-rereview-9bf975d3.json` and `final-science-rereview-9bf975d3.json` are
unchanged parent reports for the guard-fix commit. Their external probe/log paths
refer to retained parent control-plane evidence, not files that this worker may
clean. The code report's helper-retention follow-up is addressed by this directory
and its manifest. A final provenance-only commit needs its own delta review and
remote checks; these 9bf reports do not claim those later gates passed.

The 24 scientific record files and all scientific ledger blocks remained unchanged.
Hash pins detect stale edits relative to maintained review metadata; replacing all
relevant pins is a new review input, not cryptographic proof of approval. These
artifacts neither confer human `REVIEWED` status nor qualify protein occurrences.
