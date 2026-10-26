# Stage 6 Infrastructure Validation Report (`mech-goal-sequence-20261019`, Cycle 2)

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `2`
- **Stage**: `6` (`infrastructure`)
- **Revision**: `1`
- **Scope Frozen At**: `2026-10-26T01:23:18Z`
- **Frozen Snapshot**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-06/revision-0001/infra_snapshot.md` (`4e1e6ddf50234826e715a2f01f6437c7b36014c26da290cfec8ea6ceef38217c`)
- **Implementation Plan**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-06/revision-0001/implementation_plan.md`

## 1. Frozen Snapshot & Ledger Verification

- Verified `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-06/revision-0001/infra_snapshot.md` matches `status.json["infra_scope"]["content"]` byte-for-byte (`25,435` bytes, SHA-256 `4e1e6ddf50234826e715a2f01f6437c7b36014c26da290cfec8ea6ceef38217c`).
- Verified `INFRA_TASKS.md` machine-readable `InfrastructureNotebook` block preserves all 5 tasks (`proteintraitsmech-infra-0001` through `proteintraitsmech-infra-0005`), including the previously resolved `proteintraitsmech-infra-0003` (`https://github.com/CultureBotAI/proteintraitsmech/issues/605`), and assigns real GitHub issue URLs and explicit dispositions to all 4 pending tasks from the frozen snapshot (`proteintraitsmech-infra-0001` -> `https://github.com/CultureBotAI/proteintraitsmech/issues/1114`, `proteintraitsmech-infra-0002` -> `https://github.com/CultureBotAI/proteintraitsmech/issues/652`, `proteintraitsmech-infra-0004` -> `https://github.com/CultureBotAI/proteintraitsmech/issues/1190`, `proteintraitsmech-infra-0005` -> `https://github.com/CultureBotAI/proteintraitsmech/issues/1191`).

## 2. Implementation Outcomes (`proteintraitsmech-infra-0004` & `proteintraitsmech-infra-0005` Part 1)

1. **`proteintraitsmech-infra-0004` — `causal_graphs` deduplication and in-place refresh by `graph_id` (`#1190`, `status: resolved`)**:
   - Added `_graph_id(item: Any) -> str | None` (`lines 568-576`) and `_merge_causal_graphs(old_val: list, new_val: list) -> list` (`lines 579-627`) in `scripts/record_io.py` and dispatched `if key == "causal_graphs":` in `_union_list_keys` (`lines 646-651`).
   - Verified that `merge_on_reseed(existing: str, fresh: str) -> str` (`line 420`) replaces any existing on-disk `CausalGraph` in `old_val` whose `graph_id` appears in `new_val` in place with the updated `new_val` `CausalGraph`, preserves any curator/builder `CausalGraph` in `old_val` with a distinct `graph_id` in original order, and appends any newly introduced `graph_id` from `new_val` (falling back to `_key(item)` tuple deduplication for items without a non-empty `graph_id`) without emitting duplicate `graph_id` entries.
   - Added unit test `test_causal_graphs_merge_by_graph_id_updates_in_place_and_preserves_distinct_graphs` in `tests/test_record_io.py`.

2. **`proteintraitsmech-infra-0005` — Stem-prefixed `<batch>.<registry>.jsonl` sibling resolution in `scripts/ground_uniprot_examples.py` (`#1191`, `status: deferred` for Part 2)**:
   - Added `_default_promote_sibling(resolved: Path, filename: str) -> Path` (`lines 5325-5337`) in `scripts/ground_uniprot_examples.py` and wired `main()` (`args.command == "promote"`, `lines 5345-5360`; pre-PR `lines 5330-5338` in the frozen task summary) so `args.protein_registry`, `args.evidence_registry`, `args.membership_registry`, and `args.sifts_registry` automatically prefer existing `<batch>.protein_registry.jsonl`, `<batch>.occurrence_evidence.jsonl`, `<batch>.uniprot_memberships.jsonl`, and `<batch>.sifts_mappings.jsonl` siblings beside `--resolved <dir>/<batch>.resolved.jsonl` before falling back to unprefixed directory defaults.
   - Added unit test `test_default_promote_sibling_prefers_stem_prefixed_batch_registries` in `tests/test_record_io.py`.
   - Verified why Part (2) (re-resolving and promoting/archiving the 14 historical localized batches `cnp-017..020`, `cdd-042..050`, and `prosite-065`; `24,444` resolved rows, `12,608` `APPROVED` rows) must remain `deferred` under open issue `#1191`: those 14 batches were resolved before `interpro_location_id` (`interpro_grouped_location`) was added to `occurrence_evidence.jsonl`, so records inside those batches that were subsequently promoted by newer batches now carry `source_evidence_id` digests computed with `interpro_location_id` (e.g., `PROSITE:PS51525` `UniProtKB:P35817` on disk has `ug-evidence:23db6c6b98407b3a9b355f6b9741bc1268c32f8ccdece5542764e0b1ef1bc69e` with `interpro_location_id`, whereas `repair-existing-local-review-065-2026-03-prosite.resolved.jsonl` has `ug-evidence:1f6015d2d2c0b7488a5d8e5f7c2fc77b88cbdc9348aaec881db6082ca8c8738b` without `interpro_location_id`), causing whole-batch `promote` preflight to fail closed with `conflict:different_qualified_trait_occurrence`.

## 3. Validation Gate Results

| Validation Gate | Command | Result |
|---|---|---|
| Record I/O & Sibling Resolution Unit Tests | `.venv/bin/python -m pytest -q tests/test_record_io.py` | `PASS` (`132 passed, 2 skipped`) |
| UniProt Grounding Unit Tests | `.venv/bin/python -m pytest -q tests/test_ground_uniprot_examples.py` | `PASS` (`338 passed`) |
| Ruff Static Analysis | `.venv/bin/python -m ruff check --no-cache scripts/record_io.py scripts/ground_uniprot_examples.py tests/test_record_io.py` | `PASS` (`All checks passed!`) |
| Writer Audit Gate | `.venv/bin/python scripts/audit_writers.py` | `PASS` (`scripts examined: 618`, `OK: every writer of a trait record is a seeder, a registered editor, a registered validated promoter, or a declared bypass.`) |
| Grounding Registry Layout | `.venv/bin/python scripts/grounding_registry_layout.py check` | `PASS` (`occurrence_evidence.jsonl.d: rows=22314 shards=256 logical_sha256=4f533e4f9be3c38baeef2b83d95e914b3cdd711fbe1dc0d02972befff5b1ca9f`; `qualified_record_bindings.jsonl.d: rows=22314 shards=256 logical_sha256=fd85c9ec2510d10dd2f9201cbd70cdbf5840b1104edad027622b7d2967e19d57`; `grounding registries: OK`) |
| Cross-Mech Snapshot Integrity | `.venv/bin/python scripts/cross_mech_proteins.py check` | `PASS` (`OK: snapshot integrity verified`) |
| Record Review Contract Gate | `.venv/bin/python scripts/record_review.py check` | `PASS` (`valid_reviews: 14`, `coverage: declared_scopes_only`) |

## 4. Carried-Forward / Deferred Tasks for Next Cycle

- `proteintraitsmech-infra-0001` (`https://github.com/CultureBotAI/proteintraitsmech/issues/1114`): `deferred` — blocked on live UniProt REST v2 fetch-generation refresh (`fragment: true|false` required by `#1081` / PR `#1084`) and independent scientific sign-off on the 36-candidate ComplexPortal partition (`#1114`, `#1115`, `#1116`).
- `proteintraitsmech-infra-0002` (`https://github.com/CultureBotAI/proteintraitsmech/issues/652`): `deferred` — source-limited and network-fetch-gated across RHEA, GO, M-CSA (`residue_frame.json`), ARO, EC, `proteintraitsmech:*`, SFLD, PRINTS, and ECOD/SIFTS.
- `proteintraitsmech-infra-0005` (`https://github.com/CultureBotAI/proteintraitsmech/issues/1191`): `deferred` — Part (1) (`_default_promote_sibling` in `scripts/ground_uniprot_examples.py`) landed in Cycle 2 Stage 6; Part (2) (re-resolving and promoting or archiving the 14 pre-`interpro_location_id` localized batches `cnp-017..020`, `cdd-042..050`, and `prosite-065` across `12,608` `APPROVED` rows) carried forward under open issue `#1191`.
