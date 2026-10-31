# Stage 6 Infrastructure Implementation Plan (`mech-goal-sequence-20261019`, Cycle 4)

## 1. Frozen Intake Scope

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `4`
- **Stage**: `6` (`infrastructure`, `goal_id: infrastructure`)
- **Revision**: `1`
- **Source revision**: `1a7be00055d4a49a92d229904de1cb4472cf3ff8`
- **Ledger path**: `INFRA_TASKS.md`
- **Frozen timestamp (`frozen_at`)**: `2026-10-31T11:00:26Z`
- **Frozen snapshot SHA-256 (`snapshot_sha256`)**: `3c34042371b8df08bd0e46eb154c12a35fe1e9e8bbc3d0e6a947d68ebc9c39a1`
- **Frozen snapshot artifact**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000004/stage-06/revision-0001/infra_snapshot.md`

### Frozen Task Inventory (Pending Tasks at Freeze)

Note: `proteintraitsmech-infra-0003` ([CultureBotAI/proteintraitsmech#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605) / [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172)) and `proteintraitsmech-infra-0004` ([CultureBotAI/proteintraitsmech#1190](https://github.com/CultureBotAI/proteintraitsmech/issues/1190)) were already `resolved` in Cycle 1 Stages 5–6 and Cycle 2 Stage 6 respectively, and are preserved in `INFRA_TASKS.md` as historical resolved work. The 3 pending tasks (`status != resolved`) in the frozen snapshot are:

| Task ID | Issue | Status at Freeze | Priority | Target Disposition in Cycle 4 Stage 6 |
| --- | --- | --- | --- | --- |
| `proteintraitsmech-infra-0001` | [CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114) | `deferred` | P1 | `deferred` (carried forward; blocked on live UniProt REST v2 fetch generation and independent 36-candidate ComplexPortal review sign-off) |
| `proteintraitsmech-infra-0002` | [CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652) | `deferred` | P2 | `deferred` (carried forward; blocked on receipted `UNIPROT_REST` membership acquisition batches, `residue_frame.json` expansion, and upstream SIFTS/CARD coordinate tables) |
| `proteintraitsmech-infra-0005` | [CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) | `deferred` | P3 | `deferred` (Part 1 extended in Cycle 4 Stage 6 so `promote` auto-binds stem-prefixed `<batch>.uniprot_fetch_plan.json` and `<batch>.uniprot_fetch_receipt.json` siblings beside `--resolved` via `_default_optional_promote_sibling` and protects `args.fetch_request_plan`, `args.fetch_receipt`, and `args.panther_classifications` in `_validate_durable_paths`; `prosite-065` promoted in Cycle 3 Stage 3 and `cnp-020` promoted in Cycle 4 Stage 3; Part 2 — re-resolving and promoting/archiving the remaining 12 pre-`interpro_location_id` localized batches `cnp-017..019` and `cdd-042..050` — carried forward in open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)) |

---

## 2. Dependency-Aware Implementation Plan

### Selected for Tooling Upgrade (`deferred` for Stage 3 Batch Re-Resolution): `proteintraitsmech-infra-0005` ([#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191))

1. **Auto-bind optional stem-prefixed `<batch>.uniprot_fetch_plan.json` and `<batch>.uniprot_fetch_receipt.json` siblings in `scripts/ground_uniprot_examples.py` `main()` and protect all optional inputs in `_validate_durable_paths`**:
   - **Problem**:
     1. In Cycle 2 Stage 6 (`#1191`), `_default_promote_sibling` was added in `scripts/ground_uniprot_examples.py` so `promote` resolves stem-prefixed `<batch>.protein_registry.jsonl`, `<batch>.occurrence_evidence.jsonl`, `<batch>.uniprot_memberships.jsonl`, and `<batch>.sifts_mappings.jsonl` beside `--resolved <dir>/<batch>.resolved.jsonl`. However, `--fetch-request-plan` and `--fetch-receipt` still defaulted to `None` even when `<batch>.uniprot_fetch_plan.json` and `<batch>.uniprot_fetch_receipt.json` were present right beside `<batch>.resolved.jsonl` in `reports/uniprot-grounding/review-batches/`. Consequently, any `promote` invocation on a stem-prefixed batch required passing `--fetch-request-plan` and `--fetch-receipt` explicitly on the CLI to verify receipt provenance in `_verify_uniprot_fact_receipt` (`lines 3835-3840`) or `_verify_resolved_fetch_receipt_provenance`.
     2. In `_validate_durable_paths` (`lines 4058-4093`), `protected_input_keys` protected `args.residue_frame`, `args.interpro_frame`, `args.interpro_grouped_frame`, `args.profiles`, `args.sifts_registry`, `args.interpro_xml`, `args.pfam_clans`, `args.pfam_types`, and `args.go_obo` against durable output collision, but omitted `args.fetch_request_plan`, `args.fetch_receipt`, and `args.panther_classifications`.
   - **Implementation (`scripts/ground_uniprot_examples.py`, `lines 4078-4093` and `5355-5398`)**:
     - Add `_default_optional_promote_sibling(resolved: Path, filename: str) -> Path | None` (`lines 5355-5367`), which checks whether `resolved` ends with `.resolved.jsonl` (with a non-empty stem) and returns `parent / f"{stem}.{filename}"` if `prefixed.is_file()` is true, or `None` otherwise (never falling back to an unprefixed file that might belong to a different batch).
     - Wire `main()` (`lines 5391-5398`) so `if args.command == "promote" and args.fetch_request_plan is None:` sets `args.fetch_request_plan = _default_optional_promote_sibling(args.resolved, "uniprot_fetch_plan.json")` and `if args.command == "promote" and args.fetch_receipt is None:` sets `args.fetch_receipt = _default_optional_promote_sibling(args.resolved, "uniprot_fetch_receipt.json")`.
     - Add `args.fetch_request_plan`, `args.fetch_receipt`, and `args.panther_classifications` to the optional input tuple in `_validate_durable_paths` (`lines 4078-4093`) so durable registry outputs can never alias the batch's fetch plan, fetch receipt, or PANTHER classifications input.
   - **Acceptance Criteria & Tests (`tests/test_record_io.py`, `lines 1640-1661`; `tests/test_ground_uniprot_examples.py`, `lines 5958-6008`)**:
     - Extend `test_default_promote_sibling_prefers_stem_prefixed_batch_registries` in `tests/test_record_io.py` (`lines 1640-1661`) to verify `_default_optional_promote_sibling` returns `None` when `<batch>.uniprot_fetch_plan.json` / `<batch>.uniprot_fetch_receipt.json` are absent or when `--resolved` is unprefixed `resolved.jsonl`, and returns the resolved path when the stem-prefixed files exist.
     - Add `test_promote_main_defaults_stem_prefixed_fetch_plan_and_receipt_and_protects_optional_inputs` in `tests/test_ground_uniprot_examples.py` (`lines 5958-6008`) verifying that `ground.main(["promote", "--resolved", "<batch>.resolved.jsonl", ...])` populates `args.fetch_request_plan` and `args.fetch_receipt` from `<batch>.uniprot_fetch_plan.json` and `<batch>.uniprot_fetch_receipt.json` and that `_validate_durable_paths` raises `GroundingError("durable registry output must differ from staging/review input")` if a durable output collides with `fetch_request_plan`, `fetch_receipt`, or `panther_classifications`.
2. **Diagnostic Census of the 12 Remaining Pre-`interpro_location_id` Localized Review Batches (`cnp-017..019`, `cdd-042..050`)**:
   - Following Cycle 4 Stage 3 (`d9d0ee7e587ecad667cf9bdb`), where `human-ecoli-yeast-repair-cnp-020` (`970` resolved rows across `542` `CDD` groups) was re-resolved with `interpro_location_id`, finalized (`542` `APPROVED`), and promoted across `427` written `CDD` records (`+369` newly `QUALIFIED` records, `+427` durable bindings), single-pass `promote` preflight across the 12 remaining localized batches (`22,508` resolved rows, `11,706` `APPROVED` rows) verified exact conflict and stale-preimage counts against current `main` (`1a7be00055d4a49a92d229904de1cb4472cf3ff8`):
     - `human-ecoli-yeast-repair-cnp-017`: `1,000` `APPROVED` rows -> `4` occurrence/record conflicts, `15` stale preimages
     - `human-ecoli-yeast-repair-cnp-018`: `1,000` `APPROVED` rows -> `3` occurrence/record conflicts, `8` stale preimages
     - `human-ecoli-yeast-repair-cnp-019`: `1,000` `APPROVED` rows -> `2` occurrence/record conflicts, `6` stale preimages
     - `repair-existing-local-review-042-2026-03-cdd`: `999` `APPROVED` rows -> `127` occurrence/record conflicts, `72` stale preimages
     - `repair-existing-local-review-043-2026-03-cdd`: `997` `APPROVED` rows -> `38` occurrence/record conflicts, `3` stale preimages
     - `repair-existing-local-review-044-2026-03-cdd`: `998` `APPROVED` rows -> `53` occurrence/record conflicts, `1` stale preimage
     - `repair-existing-local-review-045-2026-03-cdd`: `999` `APPROVED` rows -> `33` occurrence/record conflicts, `3` stale preimages
     - `repair-existing-local-review-046-2026-03-cdd`: `1,000` `APPROVED` rows -> `27` occurrence/record conflicts, `5` stale preimages
     - `repair-existing-local-review-047-2026-03-cdd`: `1,000` `APPROVED` rows -> `50` occurrence/record conflicts, `10` stale preimages
     - `repair-existing-local-review-048-2026-03-cdd`: `999` `APPROVED` rows -> `29` occurrence/record conflicts, `6` stale preimages
     - `repair-existing-local-review-049-2026-03-cdd`: `999` `APPROVED` rows -> `42` occurrence/record conflicts, `5` stale preimages
     - `repair-existing-local-review-050-2026-03-cdd`: `715` `APPROVED` rows -> `193` occurrence/record conflicts, `86` stale preimages
     - **Total across 12 batches**: `601` occurrence/record conflicts (`9` in `cnp-017..019`, `592` in `cdd-042..050`) and `220` stale preimages (`29` in `cnp-017..019`, `191` in `cdd-042..050`).
   - Re-resolving and promoting or archiving those 12 remaining historical batches against current on-disk record preimages and `interpro_location_id` digests is Stage 3 corpus-promotion work tracked under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) and remains `status: deferred`.

---

## 3. Explicitly Carried-Forward (`deferred`) Tasks

- **`proteintraitsmech-infra-0001`** ([CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114)):
  - **Why deferred**: Promoting the 36 staged `WHOLE_PROTEIN` subunit candidates in `cross-mech-complex-20261013` (and the remaining v1 `WHOLE_PROTEIN` batches cataloged in Cycle 2 Stage 3) requires a live network UniProt REST v2 fetch generation (`scripts/fetch_uniprot_registry.py --apply`) to populate `ProteinReference.fragment` (`#1081` / PR `#1084`) and an independent scientific review sign-off on the 36-candidate ComplexPortal partition (including holds `#1115` and `#1116`).
- **`proteintraitsmech-infra-0002`** ([CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)):
  - **Why deferred**: Grounding the remaining ungrounded mechanism-graph records (`RHEA`, `GO`, `M-CSA`, `ARO`, `EC`, `proteintraitsmech:*`) and fail-closed structure/signature sources (`SFLD`, `PRINTS`, `ECOD`/SIFTS) requires live network `UNIPROT_REST` membership fetch generations, external sequence cache expansion (`data/raw/align_cache/residue_frame.json`), and upstream coordinate/mapping tables not shipped in `data/raw/`.
- **`proteintraitsmech-infra-0005`** ([CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)):
  - **Why deferred**: Part (1) (`_default_promote_sibling` and `_default_optional_promote_sibling` in `scripts/ground_uniprot_examples.py`, plus optional input collision protection in `_validate_durable_paths` and two-pass `promote` preflight error aggregation) is complete and unit-tested, `repair-existing-local-review-065-2026-03-prosite` was re-resolved and promoted across 321 `PROSITE` records in Cycle 3 Stage 3, and `human-ecoli-yeast-repair-cnp-020` was re-resolved and promoted across 427 `CDD` records in Cycle 4 Stage 3; Part (2) (re-resolving and promoting or archiving the remaining 12 pre-`interpro_location_id` localized batches `cnp-017..019` and `cdd-042..050` across `11,706` `APPROVED` rows with `601` occurrence/record conflicts and `220` stale preimages) is carried forward under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) for future Stage 3 (`protein_examples`) cycles.
