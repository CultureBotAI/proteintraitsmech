# Stage 6 Infrastructure Validation Report (`mech-goal-sequence-20261019`, Cycle 1)

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `1`
- **Stage**: `6` (`infrastructure`)
- **Revision**: `1`
- **Scope Frozen At**: `2026-10-22T11:14:52Z`
- **Frozen Snapshot**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/infra_snapshot.md` (`8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38`)
- **Implementation Plan**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/implementation_plan.md`

## 1. Frozen Snapshot & Ledger Verification

- Verified `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-06/revision-0001/infra_snapshot.md` matches `status.json["infra_scope"]["content"]` byte-for-byte (`14,947` bytes, SHA-256 `8393fd14c2c14e94415284edce027f2365cdc11d34db1a8fa65c4843240bfc38`).
- Verified `INFRA_TASKS.md` machine-readable `InfrastructureNotebook` block covers all 3 frozen tasks (`proteintraitsmech-infra-0001`, `proteintraitsmech-infra-0002`, `proteintraitsmech-infra-0003`) with unchanged issue URLs (`https://github.com/CultureBotAI/proteintraitsmech/issues/1114`, `https://github.com/CultureBotAI/proteintraitsmech/issues/652`, `https://github.com/CultureBotAI/proteintraitsmech/issues/605`) and explicit dispositions.

## 2. Implementation & Promotion Outcomes (`proteintraitsmech-infra-0003`)

1. **CDD Errata & Qualified Receipt Re-binding (`#1172`, `#605`)**:
   - Extended `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` with `CDD:cd00104` (`F1`, `KAZAL_FS` — corrected `'chyomotrypsin'` typo and clarified that avian ovomucoids are Kazal-type serine protease inhibitor proteins rather than target serine proteases, `PMID:6192856` / `UniProtKB:P00995`) and `CDD:cd00959` (`F2`, `DeoC` — removed duplicated opening sentence `'2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family.'`, `PMID:11305920` / `UniProtKB:P0A6L0`) plus transactional re-binding of their 41 durable `qualified_record_bindings.jsonl.d/` receipts (`39` on `CDD:cd00104` and `2` on `CDD:cd00959`; the 10 Stage-5-repaired CDD records received their 12 new receipts during the subsequent `ground_uniprot_examples.py promote --apply` step).
   - Command: `.venv/bin/python scripts/repair_cdd_errata.py --apply` -> `2` target records written (`CDD:cd00104: wrote source-definition erratum (F1)`, `CDD:cd00959: wrote source-definition erratum (F2)`), `10` already corrected (`already corrected; no history appended`), and `qualified_record_bindings: re-bound 41 durable receipt(s) (#1172)` (exit `0`).
2. **Legacy Schema-v1 Signature-Only `return_fields` Verification (`#605`)**:
   - Updated `scripts/fetch_uniprot_registry.py` (`LEGACY_SIGNATURE_RETURN_FIELDS`, `LEGACY_V1_RETURN_FIELD_SETS`, `_plan_return_fields`) so pre-`#971` schema-v1 signature-only fetch plans (`20` fields, before `xref_complexportal`, `go_id`, and `cc_catalytic_activity` brought v1 `RETURN_FIELDS` to `23` fields) remain verifiable read-only while schema-v2 fetch plans continue to require `REGISTRY_RETURN_FIELDS` (`24` fields, including `fragment`).
3. **Re-resolution, Finalization, and Promotion of Batches `058of128` and `066of128` (`#605`)**:
   - Re-ran `scripts/ground_uniprot_examples.py resolve` for `human-ecoli-yeast-complete-cdd-058of128` (`144` resolved rows, `0` blocked) and `human-ecoli-yeast-complete-cdd-066of128` (`151` resolved rows, `0` blocked).
   - Finalized all `144` (`058of128`) and `151` (`066of128`) review decisions as `APPROVE` via `scripts/finalize_uniprot_review_batch.py --apply` after all 10 held CDD records' upstream definition defects were repaired.
   - Executed `scripts/ground_uniprot_examples.py promote --apply`:
     - `058of128`: `records_written: 6`, `examples_promoted: 8`, `examples_existing: 136`, `durable_protein_registry_count: 12922`, `durable_evidence_registry_count: 21339`, `durable_qualified_record_binding_count: 21339`.
     - `066of128`: `records_written: 4`, `examples_promoted: 4`, `examples_existing: 147`, `durable_protein_registry_count: 12925`, `durable_evidence_registry_count: 21343`, `durable_qualified_record_binding_count: 21343`.
   - All 12 previously held `Homo sapiens` (`NCBITaxon:9606`) and `Saccharomyces cerevisiae S288C` (`NCBITaxon:559292`) examples are now promoted as `QUALIFIED` across `CDD:cd13344`, `CDD:cd14999`, `CDD:cd15894`, `CDD:cd17150`, `CDD:cd09530`, `CDD:cd16523`, `CDD:cd16652`, `CDD:cd18592`, `CDD:cd20534`, and `CDD:cd21551`.

## 3. Validation Gate Results

| Validation Gate | Command | Result |
|---|---|---|
| Grounding Registry Layout | `.venv/bin/python scripts/grounding_registry_layout.py check` | `PASS` (`occurrence_evidence.jsonl.d: rows=21343 shards=256 logical_sha256=45a7bb92cd710b6c74d4373efae227d532c566fd453a572dbced15f73620367b`; `qualified_record_bindings.jsonl.d: rows=21343 shards=256 logical_sha256=028510464fccfcca94c7b5caa7ceb963b3ec7e44d6029713b723f29fff94ea4b`; `grounding registries: OK`) |
| Strict Closed-Mode LinkML Validation | `.venv/bin/python scripts/validate_strict.py` (12 modified CDD YAML records) | `PASS` (`files scanned: 12`, `files with ERROR: 0`, `total ERROR rows: 0`) |
| UniProt Grounding & Durable Receipt Verification | `.venv/bin/python scripts/validate_uniprot_grounding.py` (12 modified CDD YAML records + full durable registries) | `PASS` (`files scanned: 12`, `registry proteins: 12925`, `source evidence objects: 21343`, `qualified record bindings: 21343`, `UniProt membership objects: 431`, `semantic findings: 0`) |
| Cross-Mech Snapshot Integrity | `.venv/bin/python scripts/cross_mech_proteins.py check` | `PASS` (`OK: snapshot integrity verified`) |
| Writer Audit Gate | `.venv/bin/python scripts/audit_writers.py` | `PASS` (`scripts examined: 618`, `OK: every writer of a trait record is a seeder, a registered editor, a registered validated promoter, or a declared bypass`) |
| Record Review Contract Gate | `.venv/bin/python scripts/record_review.py check` | `PASS` (`valid_reviews: 11`) |
| Unit Tests | `.venv/bin/python -m pytest tests/test_cdd_errata.py tests/test_fetch_uniprot_registry.py tests/test_ground_uniprot_examples.py -q` | `PASS` (`558 passed`) |
| Ruff Static Analysis | `.venv/bin/ruff check --no-cache scripts/cdd_errata.py scripts/repair_cdd_errata.py scripts/fetch_uniprot_registry.py tests/test_cdd_errata.py tests/test_fetch_uniprot_registry.py` | `PASS` (`All checks passed!`) |

## 4. Carried-Forward / Deferred Tasks for Next Cycle

- `proteintraitsmech-infra-0001` (`https://github.com/CultureBotAI/proteintraitsmech/issues/1114`): `deferred` — blocked on live UniProt REST v2 fetch-generation refresh (`fragment: true|false` required by `#1081` / PR `#1084`) and independent scientific sign-off on the 36-candidate ComplexPortal partition (`#1114`, `#1115`, `#1116`).
- `proteintraitsmech-infra-0002` (`https://github.com/CultureBotAI/proteintraitsmech/issues/652`): `deferred` — source-limited and network-fetch-gated across RHEA, GO, M-CSA (`residue_frame.json`), ARO, SFLD, PRINTS, and ECOD/SIFTS.
