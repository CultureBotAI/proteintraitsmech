# Stage 6 Infrastructure Implementation Plan (`mech-goal-sequence-20261019`, Cycle 2)

## 1. Frozen Intake Scope

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `2`
- **Stage**: `6` (`infrastructure`, `goal_id: infrastructure`)
- **Revision**: `1`
- **Ledger path**: `INFRA_TASKS.md`
- **Frozen timestamp (`frozen_at`)**: `2026-10-26T01:23:18Z`
- **Frozen snapshot SHA-256 (`snapshot_sha256`)**: `4e1e6ddf50234826e715a2f01f6437c7b36014c26da290cfec8ea6ceef38217c`
- **Frozen snapshot artifact**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-06/revision-0001/infra_snapshot.md`

### Frozen Task Inventory (Pending Tasks at Freeze)

Note: `proteintraitsmech-infra-0003` ([CultureBotAI/proteintraitsmech#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605) / [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172)) was already `resolved` in Cycle 1 Stages 5–6 and is preserved in `INFRA_TASKS.md` as historical resolved work. The 4 pending tasks (`status != resolved`) in the frozen snapshot are:

| Task ID | Issue | Status at Freeze | Priority | Target Disposition in Cycle 2 Stage 6 |
| --- | --- | --- | --- | --- |
| `proteintraitsmech-infra-0001` | [CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114) | `deferred` | P1 | `deferred` (carried forward; blocked on live UniProt REST v2 fetch generation and independent 36-candidate ComplexPortal review sign-off) |
| `proteintraitsmech-infra-0002` | [CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652) | `deferred` | P2 | `deferred` (carried forward; blocked on receipted `UNIPROT_REST` membership acquisition batches, `residue_frame.json` expansion, and upstream SIFTS/CARD coordinate tables) |
| `proteintraitsmech-infra-0004` | [CultureBotAI/proteintraitsmech#1190](https://github.com/CultureBotAI/proteintraitsmech/issues/1190) | `note` | P3 | `resolved` (implemented and verified in Cycle 2 Stage 6) |
| `proteintraitsmech-infra-0005` | [CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) | `note` | P3 | `deferred` (Part 1 — stem-prefixed `<batch>.<registry>.jsonl` sibling resolution in `scripts/ground_uniprot_examples.py` — implemented and unit-tested in Cycle 2 Stage 6; Part 2 — re-resolving and promoting/archiving the 14 pre-`interpro_location_id` localized batches — carried forward in open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)) |

---

## 2. Dependency-Aware Implementation Plan

### Selected for Full Implementation (`resolved`): `proteintraitsmech-infra-0004` ([#1190](https://github.com/CultureBotAI/proteintraitsmech/issues/1190))

1. **Key `causal_graphs` list-union deduplication in `scripts/record_io.py` (`merge_on_reseed`) by `graph_id`**:
   - **Problem**: `scripts/record_io.py` defines `_MERGE_LIST_UNION_KEYS = ("xrefs", "go_terms", "evidence", "detection_methods", "canonical_examples", "causal_graphs", "parent_traits", "aliases")` and previously deduplicated `causal_graphs` items in `_union_list_keys` by full canonical JSON serialization (`json.dumps(item, sort_keys=True)`). When a registered seeder (`scripts/seed_foundational_traits.py`, `scripts/seed_localstructuralfeature.py`, `scripts/seed_uniprot_peptide_classes.py`, or `scripts/seed_causal_graphs.py`) upgraded nodes, edges, or snippet evidence inside an existing `CausalGraph` while retaining the same `graph_id`, running `merge_on_reseed(fresh, on_disk)` treated the old and new `CausalGraph` dicts as distinct items and appended a second graph with a duplicate `graph_id` (failing `scripts/audit_causal_graphs.py`).
   - **Implementation (`scripts/record_io.py`)**:
     - Add `_graph_id(item: Any) -> str | None` to extract non-empty string `graph_id` values from `CausalGraph` dicts.
     - Add `_merge_causal_graphs(fresh_graphs: list[Any], disk_graphs: list[Any]) -> list[Any]` and dispatch `if key == "causal_graphs":` in `_union_list_keys` so:
       1. Existing on-disk `CausalGraph` entries whose `graph_id` is also present in `fresh_graphs` are replaced in place by the updated `fresh` `CausalGraph` entry.
       2. Existing on-disk `CausalGraph` entries with a distinct `graph_id` (such as curator-added or builder-added graphs not emitted by the seeder) are preserved in order.
       3. Newly introduced `graph_id` entries from `fresh_graphs` are appended in order, with fallback JSON-key deduplication for any unkeyed items.
   - **Acceptance Criteria & Tests (`tests/test_record_io.py`)**:
     - Add `test_causal_graphs_merge_by_graph_id_updates_in_place_and_preserves_distinct_graphs` verifying that `merge_on_reseed` updates matching `graph_id` entries in place, preserves distinct curator-added `graph_id` entries without duplication, and appends newly seeded `graph_id` entries.

### Selected for Partial Implementation (`deferred` for Part 2): `proteintraitsmech-infra-0005` ([#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191))

1. **Part (1) — Implement stem-prefixed `<batch>.<registry>.jsonl` sibling resolution in `scripts/ground_uniprot_examples.py` `main()`**:
   - **Problem**: `scripts/ground_uniprot_examples.py promote -h` documents `--protein-registry`, `--evidence-registry`, `--membership-registry`, and `--sifts-registry` as `(default: beside --resolved)`, but `main()` previously populated those defaults using only unprefixed directory-level filenames (`args.resolved.resolve().parent / "protein_registry.jsonl"`, etc.). When `--resolved` points to a stem-prefixed review-batch file such as `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.resolved.jsonl`, the sibling artifacts on disk are `<batch>.protein_registry.jsonl` and `<batch>.occurrence_evidence.jsonl`, whereas unprefixed `review-batches/protein_registry.jsonl` does not exist, causing `_verify_provider_evidence` to reject every row with `stale:provider_missing:protein_registry` unless all registry flags are passed explicitly.
   - **Implementation (`scripts/ground_uniprot_examples.py`)**:
     - Add `_default_promote_sibling(resolved: Path, filename: str) -> Path` that derives the batch prefix when `resolved.name` ends with `.resolved.jsonl`, checks whether `<batch>.<filename>` exists as a file beside `resolved`, and returns `<batch>.<filename>` if present (falling back to unprefixed `<parent>/<filename>` otherwise).
     - Wire `main()` (`args.cmd == "promote"`) to use `_default_promote_sibling` for `args.protein_registry`, `args.evidence_registry`, `args.membership_registry`, and `args.sifts_registry`.
   - **Acceptance Criteria & Tests (`tests/test_record_io.py`)**:
     - Add `test_default_promote_sibling_prefers_stem_prefixed_batch_registries` verifying that stem-prefixed sibling registries are selected when present beside `<batch>.resolved.jsonl` and that unprefixed directory defaults remain the fallback when stem-prefixed siblings are absent or when `--resolved` is already named `resolved.jsonl`.
2. **Part (2) — Why re-resolution of the 14 historical localized batches (`cnp-017..020`, `cdd-042..050`, `prosite-065`) is deferred to future Stage 3 (`protein_examples`) cycles**:
   - Inspection of the 14 historical localized review batches (`human-ecoli-yeast-repair-cnp-017..020`, `repair-existing-local-review-042..050-2026-03-cdd`, and `repair-existing-local-review-065-2026-03-prosite`; `24,444` resolved rows, `12,608` `APPROVED` rows) showed that they were resolved prior to the addition of `interpro_location_id` (`interpro_grouped_location`) to `occurrence_evidence.jsonl`.
   - Consequently, records inside those batches that were subsequently promoted by newer batches now carry `source_evidence_id` digests computed *with* `interpro_location_id` (for example, `PROSITE:PS51525` `UniProtKB:P35817` on disk has `ug-evidence:23db6c6b98407b3a9b355f6b9741bc1268c32f8ccdece5542764e0b1ef1bc69e` with `interpro_location_id`, whereas `repair-existing-local-review-065-2026-03-prosite.resolved.jsonl` has `ug-evidence:1f6015d2d2c0b7488a5d8e5f7c2fc77b88cbdc9348aaec881db6082ca8c8738b` without `interpro_location_id`), causing whole-batch `promote` preflight to fail closed with `conflict:different_qualified_trait_occurrence` (17 rows in `prosite-065`, plus stale record preimages across `cnp-017..020` and `cdd-042..050`).
   - Re-resolving and promoting or archiving those 14 batches (`12,608` approved rows) against current record preimages and `interpro_location_id` is tracked under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) and carried forward as `status: deferred`.

---

## 3. Explicitly Carried-Forward (`deferred`) Tasks

- **`proteintraitsmech-infra-0001`** ([CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114)):
  - **Why deferred**: Promoting the 36 staged `WHOLE_PROTEIN` subunit candidates in `cross-mech-complex-20261013` (and the remaining v1 `WHOLE_PROTEIN` batches cataloged in Cycle 2 Stage 3) requires a live network UniProt REST v2 fetch generation (`scripts/fetch_uniprot_registry.py --apply`) to populate `ProteinReference.fragment` (`#1081` / PR `#1084`) and an independent scientific review sign-off on the 36-candidate ComplexPortal partition (including holds `#1115` and `#1116`).
- **`proteintraitsmech-infra-0002`** ([CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)):
  - **Why deferred**: Grounding the remaining ungrounded mechanism-graph records (`RHEA`, `GO`, `M-CSA`, `ARO`, `EC`, `proteintraitsmech:*`) and fail-closed structure/signature sources (`SFLD`, `PRINTS`, `ECOD`/SIFTS) requires live network `UNIPROT_REST` membership fetch generations, external sequence cache expansion (`data/raw/align_cache/residue_frame.json`), and upstream coordinate/mapping tables not shipped in `data/raw/`.
- **`proteintraitsmech-infra-0005`** ([CultureBotAI/proteintraitsmech#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191)):
  - **Why deferred**: Part (1) (`_default_promote_sibling` in `scripts/ground_uniprot_examples.py`) is implemented and unit-tested in this Stage 6 PR; Part (2) (re-resolving and promoting or archiving the 14 pre-`interpro_location_id` localized batches `cnp-017..020`, `cdd-042..050`, and `prosite-065` across `12,608` `APPROVED` rows) is carried forward under open issue [#1191](https://github.com/CultureBotAI/proteintraitsmech/issues/1191) for future Stage 3 (`protein_examples`) cycles.
