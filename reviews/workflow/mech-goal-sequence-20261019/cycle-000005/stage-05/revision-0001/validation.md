# Cycle 5 Stage 5 Remediation Validation Report (`resolve_review_findings`)

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle / Stage / Revision**: Cycle 5, Stage 5 (`resolve_review_findings`), Revision 1
- **Source Revision (`main`)**: `568e78869fb08b86849d13f6a23b3a32ec27cd08`
- **Scope Frozen At**: `2026-11-04T10:35:00Z`
- **Predecessor Stage 4 Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000005/stage-04/revision-0001/evidence.yaml` (`sha256: 4cd876b721db95144afe6a86ac6565842fb32498b5c40715b7a985b4f7a4961d`)
- **Post-Remediation Structured Review Bundle**: `reviews/structured/20261104T105000Z-cdd-cycle5-stage5-remediation-review/review.yaml` (`verdict: pass`, `native_verdict: COHORT_PASS_ALL_12_FINDINGS_RESOLVED`)

---

## 1. Finding Grouping and GitHub Issue Deduplication

All 12 findings in the Cycle 5 Stage 4 review bundle (`20261104T072100Z-cdd-cycle5-sibling-domain-cohort-review`) were grouped by root cause and repair ownership and deduplicated against open and closed GitHub issues in `CultureBotAI/proteintraitsmech`:

| Group | Finding IDs | Target Records | Root Cause & Repair Owner | GitHub Issue | Stage 5 Status |
| --- | --- | --- | --- | --- | --- |
| `G5` | `F25`, `F26`, `F27`, `F28`, `F29`, `F30` | `CDD:cd17071`, `CDD:cd16113`, `CDD:cd15855`, `CDD:cd15889`, `CDD:cd15856`, `CDD:cd15887` | Parent/paralog sibling CDD `SEQ_DOMAIN` records repaired in Cycle 4 Stage 5 via `scripts/cdd_errata.py` + `scripts/repair_cdd_errata.py` | [#1217](https://github.com/CultureBotAI/proteintraitsmech/issues/1217) (reused, closed by PR #1218) | `resolved` (verified on disk) |
| `G6` | `F31`, `F32`, `F33`, `F34`, `F35`, `F36` | `CDD:cd15854`, `CDD:cd15888`, `CDD:cd15857`, `CDD:cd15886`, `CDD:cd18598`, `CDD:cd18605` | Paralog/ortholog Qbc-SNARE (SNAP47/Sec9p) and tandem-domain ABCC10/MRP7 (TMD1/TMD2) sibling CDD `SEQ_DOMAIN` records with upstream NCBI CDD Qb/Qc SNARE transmembrane-domain contradictions and MRP7=ABCC7/CFTR nomenclature plus MRP1-MRP9 MDR overclaims (`scripts/cdd_errata.py` + `scripts/repair_cdd_errata.py` + `scripts/seed_cdd.py`) | [#1230](https://github.com/CultureBotAI/proteintraitsmech/issues/1230) (created under umbrella [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605)) | `resolved` (repaired in place in Stage 5) |

---

## 2. Native Writer Implementation (`#1230`, `#1233`)

1. **`scripts/cdd_errata.py` (`sha256: b3ba3ff2f928ffe32d5e3d5ce133639099d2b4303fb664c7cc87a9b297bbbc02`)**:
   - Added `CYCLE5_CURATION_TIMESTAMP = "2026-11-04T10:45:00Z"` and 6 new `CddErratum` entries (`cd15854`, `cd15857`, `cd15886`, `cd15888`, `cd18598`, `cd18605`), expanding `ERRATA` from 30 to 36 accession-keyed entries (`F1`–`F36`).
2. **`scripts/repair_cdd_errata.py` (`sha256: 737689e6c7c1f79ecc92807bf9707bd34143ce4f3fcf87a731fdd8dd9dd0cc13`)**:
   - Updated module docstring and ran `.venv/bin/python -u scripts/repair_cdd_errata.py --apply`, updating all 6 Group `G6` records in place via `record_io.write_record(..., RegisteredEditor("scripts/repair_cdd_errata.py"))` while leaving all 30 previously repaired CDD records unchanged.
   - Re-ran `.venv/bin/python -u scripts/repair_cdd_errata.py` (dry-run) to verify idempotence (`already corrected; no history appended` across all 36 entries).
3. **`tests/test_cdd_errata.py` (`sha256: 4d376a94ec18cdf814eba50a248bea4c46cb7447b227b15c048ba0fbc6eb9296`)**:
   - Expanded `test_errata_table_covers_all_thirty_six_stage4_targets` and parametrized errata tests to cover all 36 CDD accessions (`F1`–`F36`), verifying exact post-repair definitions, removal of bad substrings, grounded `evidence` accessions, `mapping_status: PROPOSED`, and `curation_history` actions `source_erratum_<accession>`.

---

## 3. Pre- and Post-Remediation Record Digests (Group `G6`)

| Finding | Identifier | Label | Path | Pre-Repair SHA-256 | Post-Repair SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `F31` | `CDD:cd15854` | `SNARE_SNAP47C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap47-c-terminal-snare-motif-of-snap47-a-me-cd15854.yaml` | `fb37dabacc4f6c4f10e99ff638b2e76c36427c397ba7ee485d767b0ce06658a8` | `b2b582af0716d16c276e7fde6366d344d63578d8e246cbb78de47c596bea7740` |
| `F32` | `CDD:cd15888` | `SNARE_SNAP47N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap47-n-terminal-snare-motif-of-snap47-a-me-cd15888.yaml` | `5efe3d638e0e2553214d45509996fd6ced8e0cf4d336eb1fee3988ab415a54db` | `6d175da7d6247a9340f86327114222cf3d74fa80d424aabcf32554c714ce9be1` |
| `F33` | `CDD:cd15857` | `SNARE_SEC9C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-sec9-c-terminal-snare-motif-of-fungal-sec9-a-cd15857.yaml` | `69d841bb6da236a30c02b81fbf0708146b3990591a3a41741a3cab2a248ca9c2` | `51521fa63229b60f7e17e777f17b855e6f99f5e91d508fe42dada46de24fbe5b` |
| `F34` | `CDD:cd15886` | `SNARE_SEC9N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-sec9-n-terminal-snare-motif-of-fungal-sec9-a-cd15886.yaml` | `5fa48242c7a2fd0003ebdd908526675e43c8c3539430e142a77c257cd82e7bb1` | `fae776ea05c2febd604647864e11a21e90d2be1ceba4a39becf5ec56aeffb75b` |
| `F35` | `CDD:cd18598` | `ABC_6TM_MRP7_D1_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18598.yaml` | `1dfa8217dad328d5dce76325c19c8068f57f254be6c7d32f3e3d47c6e8c26857` | `9ec4e325fa97ccee8614f49fd8a8af8badb85f134f0f4f0dad78156963a75e7d` |
| `F36` | `CDD:cd18605` | `ABC_6TM_MRP7_D2_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18605.yaml` | `b3b65c3771652b48ea340b2dcb16a69228a1e5994d97b8c5044fb21412b34486` | `4851b3e2623cce8ef03b5c832ff6d047655897a5238c25fe7fefa2829906679e` |

---

## 4. Verification Gate Results

| Check | Command | Exit Code | Result |
| --- | --- | --- | --- |
| Strict LinkML + OAK validation (12 cohort records) | `.venv/bin/python -u scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv <12 cohort paths>` | `0` | `Scanned 12 files, 0 error(s).` |
| UniProt grounding semantic replay (12 cohort records) | `.venv/bin/python -u scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv <12 cohort paths>` | `0` | `12 files scanned; 24,026 corpus qualified_record_bindings verify across 14,024 registry proteins with 0 semantic findings.` |
| Causal graph audit (12 cohort records) | `.venv/bin/python -u scripts/audit_causal_graphs.py <12 cohort paths>` | `0` | `0 records, 0 errors, 0 warnings.` |
| Registered writer audit | `.venv/bin/python -u scripts/audit_writers.py` | `0` | `621 scripts examined (52 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses), OK with 0 unguarded writer findings.` |
| Append-only history validation | `.venv/bin/python -c "import glob, sys, linkml.validator as v; files = sorted(glob.glob('history/**/*.yaml', recursive=True)); sys.exit(sum(1 for f in files for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml', 'HistoryRecord').results))"` | `0` | All 26 append-only history YAML files validate cleanly against `HistoryRecord`. |
| CDD errata unit + writer guard tests | `.venv/bin/pytest -q tests/test_cdd_errata.py tests/test_inplace_editor_guards.py` | `0` | `238 passed` (`All 36 CDD errata entries report 'already corrected; no history appended' on dry-run replay, and all 238 unit and writer-guard tests pass.`) |
| Ruff lint | `.venv/bin/ruff check --no-cache scripts/ tests/` | `0` | `All checks passed!` |
| Structured review bundle gate | `.venv/bin/python scripts/record_review.py --schema schema/record_review.yaml check --require-reviews --base main` | `0` | `valid_reviews: 41, coverage: declared_scopes_only` |
