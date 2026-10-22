# Stage 6 Infrastructure Implementation Plan (`mech-goal-sequence-20261019`, Cycle 1)

## 1. Frozen Intake Scope

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `1`
- **Stage**: `6` (`infrastructure`, `goal_id: infrastructure`)
- **Revision**: `1`
- **Ledger path**: `INFRA_TASKS.md`
- **Frozen timestamp (`frozen_at`)**: `2026-10-22T11:14:52Z`
- **Frozen snapshot SHA-256 (`snapshot_sha256`)**: `8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38`
- **Frozen snapshot artifact**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/infra_snapshot.md`

### Frozen Task Inventory

| Task ID | Issue | Status at Freeze | Priority | Target Disposition in Stage 6 |
| --- | --- | --- | --- | --- |
| `proteintraitsmech-infra-0001` | [CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114) | `deferred` | P1 | `deferred` (carried forward; blocked on live UniProt REST v2 fetch generation and independent 36-candidate ComplexPortal review sign-off) |
| `proteintraitsmech-infra-0002` | [CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652) | `deferred` | P2 | `deferred` (carried forward; blocked on receipted `UNIPROT_REST` membership acquisition batches, `residue_frame.json` expansion, and upstream SIFTS/CARD coordinate tables) |
| `proteintraitsmech-infra-0003` | [CultureBotAI/proteintraitsmech#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605) / [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172) | `open` | P2 | `resolved` (implemented and verified in Stage 6) |

---

## 2. Dependency-Aware Implementation Plan

### Selected for Implementation: `proteintraitsmech-infra-0003` ([#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605), [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172))

1. **Extend CDD errata table and transactional qualified-record receipt re-binding (`scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`)**:
   - The 10 held `CDD` records (`CDD:cd13344`, `CDD:cd14999`, `CDD:cd15894`, `CDD:cd17150`, `CDD:cd09530`, `CDD:cd16523`, `CDD:cd16652`, `CDD:cd18592`, `CDD:cd20534`, `CDD:cd21551`) had their definitions repaired in Stage 5 ([#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172) / PR [#1173](https://github.com/CultureBotAI/proteintraitsmech/pull/1173)), while the 2 already-promoted `CDD` records (`CDD:cd00104`, `CDD:cd00959`) noted in `proteintraitsmech-infra-0003` remained pending transactional `qualified_record_bindings.jsonl.d/` receipt re-binding.
   - Add `CDD:cd00104` (Kazal domain `chyomotrypsin` typo and target-protease vs. avian ovomucoid inhibitor prose defect) and `CDD:cd00959` (duplicated opening sentence on `DeoC`, `2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family`) to `ERRATA` in `scripts/cdd_errata.py`.
   - Upgrade `scripts/repair_cdd_errata.py` so `--apply` transactionally updates `record_sha256` and `content_gate_projection` in `data/grounding/qualified_record_bindings.jsonl.d/` for any repaired record that already carries durable qualified examples, using `ground_uniprot_examples._install_promotion_transaction` and `grounding_registry_layout.registry_lock`.
   - Run `.venv/bin/python scripts/repair_cdd_errata.py --apply` to repair `CDD:cd00104` and `CDD:cd00959` and re-bind their 41 durable receipts in `data/grounding/qualified_record_bindings.jsonl.d/`.

2. **Preserve read-only verification for pre-#971 20-field signature-only `schema_version=1` UniProt fetch plans (`scripts/fetch_uniprot_registry.py`)**:
   - Pre-#971 `schema_version=1` fetch plans (239 batches under `reports/uniprot-grounding/review-batches/`, including `human-ecoli-yeast-complete-cdd-058of128` and `human-ecoli-yeast-complete-cdd-066of128`) used the 20-field `LEGACY_SIGNATURE_RETURN_FIELDS` tuple before `xref_complexportal`, `go_id`, and `cc_catalytic_activity` were appended to `FACT_FIELDS` in PR `#971`.
   - Update `scripts/fetch_uniprot_registry.py` (`LEGACY_SIGNATURE_RETURN_FIELDS`, `LEGACY_V1_RETURN_FIELD_SETS`, `_plan_return_fields`) so `verify_fetch_receipt` accepts both 20-field and 23-field `schema_version=1` fetch plans during read-only verification while keeping `schema_version=2` strict on `REGISTRY_RETURN_FIELDS` (`24` fields).
   - Add unit test coverage in `tests/test_fetch_uniprot_registry.py` (`test_legacy_v1_signature_only_return_fields_verifies_read_only`) and `tests/test_cdd_errata.py`.

3. **Re-resolve, finalize, and promote the 12 held `Homo sapiens` / `Saccharomyces cerevisiae` candidate examples across the 10 repaired `CDD` records**:
   - Re-run `.venv/bin/python scripts/ground_uniprot_examples.py resolve` on `human-ecoli-yeast-complete-cdd-058of128` and `human-ecoli-yeast-complete-cdd-066of128` so all candidate rows bind the repaired record preimages and fresh `resolution_digest` hashes.
   - Update the review decisions for the 12 previously held target-taxon candidates (`CDD:cd16652` `UniProtKB:Q12508`, `CDD:cd20534` `UniProtKB:Q8N1B3`, `CDD:cd16523` `UniProtKB:Q8WY64`, `CDD:cd09530` `UniProtKB:Q9P1V8`, `CDD:cd21551` `UniProtKB:Q15022`, `CDD:cd18592` `UniProtKB:O15440` / `UniProtKB:Q96J66` / `UniProtKB:Q96J65` in `058of128`; `CDD:cd13344` `UniProtKB:Q9Y216`, `CDD:cd14999` `UniProtKB:Q9UKP6`, `CDD:cd15894` `UniProtKB:P60880`, `CDD:cd17150` `UniProtKB:A2VCK2` in `066of128`) from `REJECTED` (`HOLD_FOR_PROSE_CURATION` / `HOLD_PROSE_REVIEW`) to `APPROVED` and finalize both batches with `scripts/finalize_uniprot_review_batch.py --apply`.
   - Promote both batches via `.venv/bin/python scripts/ground_uniprot_examples.py promote --apply`, installing the 12 newly qualified `canonical_examples` into the 10 repaired `CDD` YAML records and updating the sharded grounding registries under `data/grounding/`.
   - Refresh cross-Mech protein coverage artifacts via `.venv/bin/python scripts/cross_mech_proteins.py refresh`.

---

## 3. Explicitly Carried-Forward (`deferred`) Tasks

- **`proteintraitsmech-infra-0001`** ([CultureBotAI/proteintraitsmech#1114](https://github.com/CultureBotAI/proteintraitsmech/issues/1114)):
  - **Why deferred**: Promoting the 36 staged `WHOLE_PROTEIN` subunit candidates in `cross-mech-complex-20261013` requires a live network UniProt REST v2 fetch generation (`scripts/fetch_uniprot_registry.py --apply`) to populate `ProteinReference.fragment` (`#1081` / PR `#1084`) and an independent scientific review sign-off on the 36-candidate ComplexPortal partition (including holds `#1115` and `#1116`).
- **`proteintraitsmech-infra-0002`** ([CultureBotAI/proteintraitsmech#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)):
  - **Why deferred**: Grounding the remaining ungrounded mechanism-graph records (`RHEA`, `GO`, `M-CSA`, `ARO`) and fail-closed structure/signature sources (`SFLD`, `PRINTS`, `ECOD`/SIFTS) requires live network `UNIPROT_REST` membership fetch generations, external sequence cache expansion (`data/raw/align_cache/residue_frame.json`), and upstream coordinate/mapping tables not shipped in `data/raw/`.
