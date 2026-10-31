# Cycle 3 Stage 6 Infrastructure Validation Report

## 1. Frozen Intake Scope Verification (`INFRA_TASKS.md`)

- **Frozen Timestamp (`scope_frozen_at`)**: `2026-10-30T16:17:46Z`
- **Source Revision**: `028d303341152f1528dbf5f8db4dc7224c6dea69`
- **Snapshot Path**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-06/revision-0001/infra_snapshot.md`
- **Snapshot SHA-256**: `c70fb6b70f4531f1cb047aaad22ac72b68e48844dbedc18da2d731a9fb522921` (matches `/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/culturebotai-claw/workspace/session-orchestration/20261019/proteintraitsmech/cycles/cycle-000003/infra-scope.json`)

## 2. Implemented Changes (`proteintraitsmech-infra-0005` / `#1191`)

1. **`scripts/ground_uniprot_examples.py` (`promote` preflight error aggregation)**:
   - Upgraded the `promote` record-install loop (`sorted(grouped)`) to a two-pass preflight (`record_install_errors` + `stale_selected_preimages` + `pending_splices`) that collects all `_install_example(record, row)` `GroundingError` failures with `f"{row['candidate_id']} ({row.get('trait_id')} / {row.get('protein_id')}): {exc}"` alongside `stale:record_changed_since_resolve` across the entire batch before running `_replace_examples_block` YAML splices.
2. **`tests/test_ground_uniprot_examples.py`**:
   - Added `test_promote_aggregates_candidate_context_for_record_conflicts_and_stale_preimages` verifying that `promote` aggregates both `conflict:different_qualified_trait_occurrence` (with `candidate_id`, `trait_id`, and `protein_id` context) and `stale:record_changed_since_resolve` in a single failure report without mutating target records.
3. **`INFRA_TASKS.md`**:
   - Updated `proteintraitsmech-infra-0005` (`#1191`) machine-readable disposition and Markdown section with the Cycle 3 Stage 6 `promote` preflight upgrade and the exact diagnostic census across the 13 remaining localized batches (`12,248` `APPROVED` rows across `23,478` resolved rows: `491` `conflict:different_qualified_trait_occurrence` rows and `181` `stale:record_changed_since_resolve` rows).
4. **`reviews/workflow/latest.yaml`**:
   - Synchronized the Cycle 3 Stage 5 closure entry (`pr_number: 1211`, `merge_commit_sha: 028d303341152f1528dbf5f8db4dc7224c6dea69`, `receipt_sha256: 84f2cf4b561fdf2b5bb1c9f30f5915e82beb6f606c8fab11674a0a010ab4971e`, including `historical_issue_resolutions` for `#1172` and `#1188`) from `verified-evidence-index.json`.

## 3. Validation Gates Executed

| Gate | Command | Result |
| --- | --- | --- |
| Grounding unit tests | `.venv/bin/python -m pytest -q tests/test_ground_uniprot_examples.py` | PASS (`339 passed`, including `test_promote_aggregates_candidate_context_for_record_conflicts_and_stale_preimages`) |
| Record I/O unit tests | `.venv/bin/python -m pytest -q tests/test_record_io.py` | PASS (`132 passed, 2 skipped`) |
| Ruff lint | `.venv/bin/python -m ruff check --no-cache scripts/ground_uniprot_examples.py tests/test_ground_uniprot_examples.py` | PASS (`All checks passed!`) |
| Writer audit | `.venv/bin/python scripts/audit_writers.py` | PASS (`scripts examined: 620`, `OK: every writer of a trait record is a seeder, a registered editor, a registered validated promoter, or a declared bypass.`) |
| Grounding registry layout | `.venv/bin/python scripts/grounding_registry_layout.py check` | PASS (`occurrence_evidence.jsonl.d`: `22635` rows, `256` shards; `qualified_record_bindings.jsonl.d`: `22635` rows, `256` shards; `grounding registries: OK`) |
| Cross-Mech protein snapshot | `.venv/bin/python scripts/cross_mech_proteins.py check` | PASS (`OK: snapshot integrity verified`) |
| Record review ledger | `.venv/bin/python scripts/record_review.py check` | PASS (`valid_reviews: 28`, `coverage: declared_scopes_only`) |
| Vendored sync | `bash scripts/check_vendored_sync.sh` | PASS (`OK: 23 governed artifacts match the pinned claw revision`) |
| History validation | `.venv/bin/linkml-validate --schema src/proteintraitsmech/schema/history.yaml --target-class HistoryRecord history/**/*.yaml` | PASS (`20` history files, `No issues found`) |
| Workflow evidence & `INFRA_TASKS.md` schema | `kg_microbe_workflows.validate_goal_evidence` & `validate_infra_notebook` | PASS |

## 4. Carried-Forward Tasks

- **`proteintraitsmech-infra-0001` (`#1114`)**: Carried forward (`deferred`). Requires full offline UniProt Swiss-Prot 2026_01 release index (`data/raw/uniprot_sprot.dat.gz`) to run `audit-uniprot-grounding` without `--skip-audit`.
- **`proteintraitsmech-infra-0002` (`#652`)**: Carried forward (`deferred`). Requires explicit curator authorization per batch and offline release cache (`data/raw/uniprot_sprot.dat.gz`) to promote `APPROVED` rows from the 13 localized batches.
- **`proteintraitsmech-infra-0005` (`#1191`)**: Carried forward (`deferred`). `promote` preflight error aggregation landed and all 13 remaining localized batches are inventoried (`491` occurrence conflicts, `181` stale preimages); batch promotion remains gated on `#652` curator authorization and `#1114` release cache.
