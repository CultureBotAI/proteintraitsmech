# Stage 6 Infrastructure Implementation Plan (`mech-goal-sequence-20261019`, Cycle 3)

## 1. Frozen Intake Scope

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `3`
- **Stage**: `6` (`infrastructure`, `goal_id: infrastructure`)
- **Revision**: `1`
- **Ledger path**: `INFRA_TASKS.md`
- **Frozen timestamp (`frozen_at`)**: `2026-10-30T16:17:46Z`
- **Frozen snapshot SHA-256 (`snapshot_sha256`)**: `c70fb6b70f4531f1cb047aaad22ac72b68e48844dbedc18da2d731a9fb522921`
- **Frozen snapshot artifact**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-06/revision-0001/infra_snapshot.md`

### Frozen Task Inventory (Pending Tasks at Freeze)

Note: `proteintraitsmech-infra-0003` ([CultureBotAI/proteintraitsmech#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605) / [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172)) and `proteintraitsmech-infra-0004` ([CultureBotAI/proteintraitsmech#1190](https://github.com/CultureBotAI/proteintraitsmech/issues/1190)) were already `resolved` in Cycle 1 Stages 5–6 and Cycle 2 Stage 6 respectively, and are preserved in `INFRA_TASKS.md` as historical resolved work. The 3 pending tasks (`status != resolved`) in the frozen snapshot are:

| Task ID | Issue | Status at Freeze | Priority | Target Disposition in Cycle 3 Stage 6 |
| --- | --- | --- | --- | --- |
| `proteintraitsmech-infra-0001` | [CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114) | `deferred` | P1 | `deferred` (carried forward; blocked on live UniProt REST v2 fetch generation and independent 36-candidate ComplexPortal review sign-off) |
| `proteintraitsmech-infra-0002` | [CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652) | `deferred` | P2 | `deferred` (carried forward; blocked on receipted `UNIPROT_REST` membership acquisition batches, `residue_frame.json` expansion, and upstream SIFTS/CARD coordinate tables) |
| `proteintraitsmech-infra-0005` | [CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) | `deferred` | P3 | `deferred` (Part 1 — stem-prefixed `<batch>.<registry>.jsonl` sibling resolution in `scripts/ground_uniprot_examples.py` — landed in Cycle 2 Stage 6; `prosite-065` re-resolved and promoted in Cycle 3 Stage 3; two-pass `promote` preflight error aggregation across `record_install_errors` and `stale_selected_preimages` implemented and unit-tested in Cycle 3 Stage 6; Part 2 — re-resolving and promoting/archiving the remaining 13 pre-`interpro_location_id` localized batches `cnp-017..020` and `cdd-042..050` — carried forward in open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)) |

---

## 2. Dependency-Aware Implementation Plan

### Selected for Tooling Upgrade (`deferred` for Stage 3 Batch Re-Resolution): `proteintraitsmech-infra-0005` ([#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191))

1. **Aggregate all record-install conflicts with candidate/trait/protein context alongside stale preimages in `scripts/ground_uniprot_examples.py` `promote()` before running YAML splices**:
   - **Problem**: In `scripts/ground_uniprot_examples.py` (`promote`), the record-install loop over `sorted(grouped)` previously called `updated, row_changed = _install_example(record, row)` without catching per-row `GroundingError` and ran `_replace_examples_block(original_text, record)` inside the same loop. Consequently:
     1. When auditing or promoting one of the 13 remaining partially superseded localized batches (`human-ecoli-yeast-repair-cnp-017..020` and `repair-existing-local-review-042..050-2026-03-cdd`), `_install_example` aborted immediately on the very first conflicting row with a bare `ERROR: conflict:different_qualified_trait_occurrence` message that omitted `candidate_id`, `trait_id`, and `protein_id`, hiding all subsequent occurrence conflicts and `stale:record_changed_since_resolve` errors in the batch.
     2. Even when a batch contained install conflicts, `promote` executed `_replace_examples_block` YAML serialization splices on every preceding record before failing.
   - **Implementation (`scripts/ground_uniprot_examples.py`, `lines 4838-4884`)**:
     - Split the `grouped` record loop in `promote(args)` into a two-pass preflight:
       1. **Pass 1 (`lines 4845-4878`)**: Iterate over `sorted(grouped)` and each approved `row` in `sorted(grouped[path], key=lambda item: item["candidate_id"])`. Catch `GroundingError` from `_install_example(record, row)` and append `f"{row['candidate_id']} ({row.get('trait_id')} / {row.get('protein_id')}): {exc}"` to `record_install_errors`, while continuing to record `stale_selected_preimages` (`f"{row['candidate_id']}: stale:record_changed_since_resolve"`) and queueing changed records in `pending_splices`. If `record_install_errors` is non-empty after checking all records in the batch, raise `GroundingError("\n".join([*record_install_errors, *stale_selected_preimages]))` immediately without running `_replace_examples_block`.
       2. **Pass 2 (`lines 4879-4884`)**: When `record_install_errors` is empty, execute `_replace_examples_block(original_text, record)` and compute `prospective_sha256` across `pending_splices` before running `_promotion_qualified_record_preflight`.
   - **Acceptance Criteria & Tests (`tests/test_ground_uniprot_examples.py`, `lines 5845-5956`)**:
     - Add `test_promote_aggregates_candidate_context_for_record_conflicts_and_stale_preimages` verifying that when a promotion batch contains multiple `conflict:different_qualified_trait_occurrence` rows on `Pfam:PF00001` and a `stale:record_changed_since_resolve` row on `Pfam:PF00002`, `promote` exits with code `2`, reports every conflicting row with `f"{candidate_id} ({trait_id} / {protein_id}): conflict:different_qualified_trait_occurrence"` plus `f"{stale_candidate_id}: stale:record_changed_since_resolve"` in a single preflight pass, and leaves all on-disk records and durable grounding registries byte-for-byte unchanged.
2. **Diagnostic Census of the 13 Remaining Pre-`interpro_location_id` Localized Review Batches (`cnp-017..020`, `cdd-042..050`)**:
   - Using the upgraded single-pass preflight across all 13 remaining localized batches (`23,478` resolved rows, `12,248` `APPROVED` rows after `repair-existing-local-review-065-2026-03-prosite` was re-resolved and promoted in Cycle 3 Stage 3 across 321 `PROSITE` records), exact per-batch conflict and stale-preimage counts were verified:
     - `human-ecoli-yeast-repair-cnp-017`: `1,000` `APPROVED` rows -> `4` `conflict:different_qualified_trait_occurrence`, `12` `stale:record_changed_since_resolve`
     - `human-ecoli-yeast-repair-cnp-018`: `1,000` `APPROVED` rows -> `3` `conflict:different_qualified_trait_occurrence`, `8` `stale:record_changed_since_resolve`
     - `human-ecoli-yeast-repair-cnp-019`: `1,000` `APPROVED` rows -> `2` `conflict:different_qualified_trait_occurrence`, `6` `stale:record_changed_since_resolve`
     - `human-ecoli-yeast-repair-cnp-020`: `542` `APPROVED` rows -> `0` `conflict:different_qualified_trait_occurrence`, `50` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-042-2026-03-cdd`: `999` `APPROVED` rows -> `127` `conflict:different_qualified_trait_occurrence`, `72` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-043-2026-03-cdd`: `997` `APPROVED` rows -> `38` `conflict:different_qualified_trait_occurrence`, `3` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-044-2026-03-cdd`: `998` `APPROVED` rows -> `53` `conflict:different_qualified_trait_occurrence`, `1` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-045-2026-03-cdd`: `999` `APPROVED` rows -> `33` `conflict:different_qualified_trait_occurrence`, `3` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-046-2026-03-cdd`: `1,000` `APPROVED` rows -> `27` `conflict:different_qualified_trait_occurrence`, `5` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-047-2026-03-cdd`: `1,000` `APPROVED` rows -> `50` `conflict:different_qualified_trait_occurrence`, `7` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-048-2026-03-cdd`: `999` `APPROVED` rows -> `29` `conflict:different_qualified_trait_occurrence`, `6` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-049-2026-03-cdd`: `999` `APPROVED` rows -> `42` `conflict:different_qualified_trait_occurrence`, `5` `stale:record_changed_since_resolve`
     - `repair-existing-local-review-050-2026-03-cdd`: `715` `APPROVED` rows -> `83` `conflict:different_qualified_trait_occurrence`, `3` `stale:record_changed_since_resolve`
     - **Total across 13 batches**: `491` `conflict:different_qualified_trait_occurrence` rows and `181` `stale:record_changed_since_resolve` rows.
   - Re-resolving and promoting or archiving those 13 historical batches against current on-disk record preimages and `interpro_location_id` digests is Stage 3 corpus-promotion work tracked under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) and remains `status: deferred`.

---

## 3. Explicitly Carried-Forward (`deferred`) Tasks

- **`proteintraitsmech-infra-0001`** ([CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114)):
  - **Why deferred**: Promoting the 36 staged `WHOLE_PROTEIN` subunit candidates in `cross-mech-complex-20261013` (and the remaining v1 `WHOLE_PROTEIN` batches cataloged in Cycle 2 Stage 3) requires a live network UniProt REST v2 fetch generation (`scripts/fetch_uniprot_registry.py --apply`) to populate `ProteinReference.fragment` (`#1081` / PR `#1084`) and an independent scientific review sign-off on the 36-candidate ComplexPortal partition (including holds `#1115` and `#1116`).
- **`proteintraitsmech-infra-0002`** ([CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)):
  - **Why deferred**: Grounding the remaining ungrounded mechanism-graph records (`RHEA`, `GO`, `M-CSA`, `ARO`, `EC`, `proteintraitsmech:*`) and fail-closed structure/signature sources (`SFLD`, `PRINTS`, `ECOD`/SIFTS) requires live network `UNIPROT_REST` membership fetch generations, external sequence cache expansion (`data/raw/align_cache/residue_frame.json`), and upstream coordinate/mapping tables not shipped in `data/raw/`.
- **`proteintraitsmech-infra-0005`** ([CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)):
  - **Why deferred**: Part (1) (`_default_promote_sibling` in `scripts/ground_uniprot_examples.py`) landed in Cycle 2 Stage 6, `repair-existing-local-review-065-2026-03-prosite` was re-resolved and promoted across 321 `PROSITE` records in Cycle 3 Stage 3, and two-pass `promote` preflight error aggregation (`record_install_errors` + `pending_splices`) is implemented and unit-tested in this Cycle 3 Stage 6 PR; Part (2) (re-resolving and promoting or archiving the remaining 13 pre-`interpro_location_id` localized batches `cnp-017..020` and `cdd-042..050` across `12,248` `APPROVED` rows with `491` occurrence conflicts and `181` stale preimages) is carried forward under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) for future Stage 3 (`protein_examples`) cycles.
