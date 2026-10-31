# Cycle 4 Stage 5 Remediation Validation Report (`resolve_review_findings`)

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle / Stage / Revision**: Cycle 4, Stage 5 (`resolve_review_findings`), Revision 1
- **Source Revision (`main`)**: `e5691e0b0c721edf6e67fbac4f28d04be0496ba7`
- **Scope Frozen At**: `2026-10-31T08:05:00Z`
- **Predecessor Stage 4 Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000004/stage-04/revision-0001/evidence.yaml` (`sha256: 6393ef3110ace7731a115db2c402d9f9cc4788a439a48e62bbfc627c5e34e79b`)
- **Post-Remediation Structured Review Bundle**: `reviews/structured/20261031T081500Z-cdd-cycle4-stage5-remediation-review/review.yaml` (`verdict: pass`, `native_verdict: COHORT_PASS_ALL_12_FINDINGS_RESOLVED`)

---

## 1. Finding Grouping and GitHub Issue Deduplication

All 12 findings in the Cycle 4 Stage 4 review bundle (`20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review`) were grouped by root cause and repair ownership and deduplicated against open and closed GitHub issues in `CultureBotAI/proteintraitsmech`:

| Group | Finding IDs | Target Records | Root Cause & Repair Owner | GitHub Issue | Stage 5 Status |
| --- | --- | --- | --- | --- | --- |
| `G4` | `F19`, `F20`, `F21`, `F22`, `F23`, `F24` | `CDD:cd17152`, `CDD:cd17153`, `CDD:cd15884`, `CDD:cd15895`, `CDD:cd18599`, `CDD:cd18601` | Tandem-repeat / paralog-subfamily CDD `SEQ_DOMAIN` records repaired in Cycle 3 Stage 5 via `scripts/cdd_errata.py` + `scripts/repair_cdd_errata.py` | [#1210](https://github.com/CultureBotAI/proteintraitsmech/issues/1210) (reused, closed by PR #1211) | `resolved` (verified on disk) |
| `G5` | `F25`, `F26`, `F27`, `F28`, `F29`, `F30` | `CDD:cd17071`, `CDD:cd16113`, `CDD:cd15855`, `CDD:cd15889`, `CDD:cd15856`, `CDD:cd15887` | Parent/paralog sibling CDD `SEQ_DOMAIN` records with upstream NCBI CDD template spelling, off-target ubiquitin protein-modifier digressions, and Qb/Qc SNARE transmembrane-domain contradictions (`scripts/cdd_errata.py` + `scripts/repair_cdd_errata.py` + `scripts/seed_cdd.py`) | [#1217](https://github.com/CultureBotAI/proteintraitsmech/issues/1217) (created under umbrella [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605)) | `resolved` (repaired in place in Stage 5) |

---

## 2. Native Writer Implementation (`#1217`)

1. **`scripts/cdd_errata.py` (`sha256: 5528121218bde822769aebbc1a886200dcb6841087d4f445e757624f18cbdb6d`)**:
   - Added `CYCLE4_CURATION_TIMESTAMP = "2026-10-31T08:10:00Z"` and 6 new `CddErratum` entries (`cd15855`, `cd15856`, `cd15887`, `cd15889`, `cd16113`, `cd17071`), expanding `ERRATA` from 24 to 30 accession-keyed entries (`F1`–`F30`).
2. **`scripts/repair_cdd_errata.py` (`sha256: 9af19aa9a592e7c34272db5bbe58b5aa5d7e8bbca8b299fd10945d1caeb07c0c`)**:
   - Updated module docstring and ran `.venv/bin/python scripts/repair_cdd_errata.py --apply`, updating all 6 Group `G5` records in place via `record_io.write_record(..., RegisteredEditor("scripts/repair_cdd_errata.py"))` while leaving all 24 previously repaired CDD records unchanged.
   - Re-ran `.venv/bin/python scripts/repair_cdd_errata.py` (dry-run) to verify idempotence (`already corrected; no history appended` across all 30 entries).
3. **`tests/test_cdd_errata.py` (`sha256: eecb43cd493750086aca8dbb47fb9dd8d9a5cd4574867663bd4392d018ed5807`)**:
   - Expanded expected accession set to all 30 CDD accessions (`F1`–`F30`) and added `test_cycle4_sibling_errata_fixes` verifying exact post-repair definitions, removal of bad substrings, grounded `evidence` accessions, `mapping_status: PROPOSED`, and `curation_history` actions `source_erratum_<accession>`.

---

## 3. Pre- and Post-Remediation Record Digests (Group `G5`)

| Finding | Identifier | Label | Path | Pre-Repair SHA-256 | Post-Repair SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `F25` | `CDD:cd17071` | `DCX1_DCDC2-like` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml` | `deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50` | `1aff2abcd815c6155a36d63abf731f22dc6644f6f673e5286f407d0476f35266` |
| `F26` | `CDD:cd16113` | `DCX2_DCDC2-like` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml` | `d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f` | `2ddc254725899c6217899f51342f7d9b86610b95d0c2a3df0dd2943d715f7a4b` |
| `F27` | `CDD:cd15855` | `SNARE_SNAP25_23C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml` | `306f687472e4fb91d6dcad19fa7ea13f99eb85fbafb7e86440302296b710b267` | `fd7dc3af4c9120523b0d00017a4c8b631bcd635468f031a23fc9ef480646ab06` |
| `F28` | `CDD:cd15889` | `SNARE_SNAP25_23N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml` | `a7de1d8068c056d075c9ddfc6e5f1a0cb9f9bb4102e6779f92fd06fd75acbd6e` | `e01a1f77672ae59b19218bc22b8d7970c2cc3bc2517b6bad56e5ed3c19453b4a` |
| `F29` | `CDD:cd15856` | `SNARE_SNAP29C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml` | `84d8d25d5f6ce8934609c55719a0d4a09b385e2ba1cbb5134c2649573d8327c0` | `c5c11e86520d19d5bd1fccc934f8d80f4fa927e64cbd53e8d0f8e3ffa8315c0a` |
| `F30` | `CDD:cd15887` | `SNARE_SNAP29N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml` | `edd0ed8a35d333d4f87c1ac2a4aee0d30f5af17a5a6c9a169007401798101519` | `5fb03c07b2e0d6dd1bea53f4c87b478dd9021fb9a970f64876c5d3a26e4519a4` |

---

## 4. Verification Gate Results

| Check | Command | Exit Code | Result |
| --- | --- | --- | --- |
| Strict LinkML + OAK validation (12 cohort records) | `.venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv <12 cohort paths>` | `0` | `Scanned 12 files, 0 error(s).` |
| UniProt grounding semantic replay (12 cohort records) | `.venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv <12 cohort paths>` | `0` | `12 files scanned, 13,532 registry proteins, 23,062 source evidence objects, 23,062 qualified record bindings, 431 UniProt memberships, 0 semantic findings.` |
| Causal graph audit (12 cohort records) | `.venv/bin/python scripts/audit_causal_graphs.py <12 cohort paths>` | `0` | `0 records, 0 errors, 0 warnings.` |
| Registered writer audit | `.venv/bin/python scripts/audit_writers.py` | `0` | `620 scripts examined (51 seeders, 9 registered editors, 2 transactional promoters, 52 declared bypasses), OK.` |
| Append-only history validation | `.venv/bin/python -c "import glob, sys, linkml.validator as v; files = sorted(glob.glob('history/**/*.yaml', recursive=True)); sys.exit(sum(1 for f in files for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml', 'HistoryRecord').results))"` | `0` | All 21 history YAML files pass `HistoryRecord` validation. |
| CDD errata unit + writer guard tests | `.venv/bin/pytest -q tests/test_cdd_errata.py tests/test_inplace_editor_guards.py` | `0` | `214 passed` |
| Ruff lint | `.venv/bin/ruff check --no-cache scripts/ tests/` | `0` | `All checks passed!` |
| Structured review bundle gate | `.venv/bin/python scripts/record_review.py --schema schema/record_review.yaml check --require-reviews --base main` | `0` | `OK: 1 review bundle(s) checked` |
