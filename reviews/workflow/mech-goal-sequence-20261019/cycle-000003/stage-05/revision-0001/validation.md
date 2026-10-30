# Cycle 3 Stage 5 Grouped Review-Finding Remediation Validation Report

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `3`
- **Stage**: `5` (`resolve_review_findings`)
- **Revision**: `1`
- **Base Commit (`origin/main`)**: `334fabd4fe53db189c1e6d4a10cda521ddbe9091`
- **Scope Frozen At**: `2026-10-30T11:45:00Z`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-04/revision-0001/evidence.yaml` (`675d9c6efc52c8ad25d7e0a13f9306fe0d92d901a3f629ec9a5328230feec9e9`)
- **Fresh Structured Review Bundle**: `reviews/structured/20261030T115500Z-cdd-cycle3-stage5-remediation-review/review.yaml`

## 1. Issue Grouping & Deduplication Summary

| Group | Issue | Status | Findings | Target Records | Ownership |
| --- | --- | --- | --- | --- | --- |
| `G2` | [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605)) | `resolved` | `F1`, `F2` | `CDD:cd00104`, `CDD:cd00959` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/ground_protein_examples.py`, `data/grounding/qualified_record_bindings.jsonl.d` |
| `G3` | [#1188](https://github.com/CultureBotAI/proteintraitsmech/issues/1188) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605), [#1171](https://github.com/CultureBotAI/proteintraitsmech/issues/1171)) | `resolved` | `F13`, `F14`, `F15`, `F16`, `F17`, `F18` | `CDD:cd20535`, `CDD:cd15885`, `CDD:cd17151`, `CDD:cd17154`, `CDD:cd17149`, `CDD:cd18593` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/seed_cdd.py`, `scripts/record_io.py`, `tests/test_cdd_errata.py` |
| `G4` | [#1210](https://github.com/CultureBotAI/proteintraitsmech/issues/1210) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605), [#1171](https://github.com/CultureBotAI/proteintraitsmech/issues/1171), [#1188](https://github.com/CultureBotAI/proteintraitsmech/issues/1188)) | `resolved` | `F19`, `F20`, `F21`, `F22`, `F23`, `F24` | `CDD:cd17152`, `CDD:cd17153`, `CDD:cd15884`, `CDD:cd15895`, `CDD:cd18599`, `CDD:cd18601` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/seed_cdd.py`, `scripts/record_io.py`, `tests/test_cdd_errata.py` |

## 2. Repaired `G4` Records (`F19`–`F24`) Pre/Post SHA-256 Digests

| Finding | Record | Path | Pre-Repair SHA-256 | Post-Repair SHA-256 |
| --- | --- | --- | --- | --- |
| `F19` | `CDD:cd17152` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml` | `e417b4fe9e69deec13282e792245d3746f15f29e609572f083a8cbc4fd68b11b` | `082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c` |
| `F20` | `CDD:cd17153` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml` | `dc4f778b022ed8629d36eeeebe9a67b89437602f80da52cc2785c885b23f66dc` | `d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75` |
| `F21` | `CDD:cd15884` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml` | `25c96270182b7deb52e5f9572354a19ecf9a4475a56315cb32367a69c45c0d04` | `e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510` |
| `F22` | `CDD:cd15895` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml` | `615522b360750919bbe4a9ad8005ccc1aa29ea684fab698cc0cf869838151e9d` | `5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b` |
| `F23` | `CDD:cd18599` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml` | `55248bf08f405c7fb665974fecef9c1fcdd05a5b67774e4753a6dbf3cb53faea` | `ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585` |
| `F24` | `CDD:cd18601` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml` | `04c649ce8b0463952a711aa86cc477e9f4a130717a1e930e3e280ef478f4a080` | `d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099` |

## 3. Validation Checks Executed

| Check | Command | Exit Code | Result |
| --- | --- | --- | --- |
| Registered CDD errata writer dry-run | `.venv/bin/python scripts/repair_cdd_errata.py` | `0` | `6 G4 records need correction; 18 Cycle 1/2 records already corrected (no history appended)` |
| Registered CDD errata writer apply | `.venv/bin/python scripts/repair_cdd_errata.py --apply` | `0` | `6 G4 records updated in place via record_io.write_validated_record; 18 Cycle 1/2 records unchanged` |
| Registered CDD errata writer idempotence check | `.venv/bin/python scripts/repair_cdd_errata.py` | `0` | `All 24 errata records already corrected (no history appended)` |
| Strict LinkML + OAK validation | `.venv/bin/python scripts/validate_strict.py <14 CDD cohort records>` | `0` | `14 files scanned, 0 errors` |
| Release-pinned UniProt grounding | `.venv/bin/python scripts/validate_uniprot_grounding.py <14 CDD cohort records>` | `0` | `14 files scanned, 13,293 registry proteins, 22,635 qualified record bindings, 431 UniProt memberships, 0 semantic findings` |
| Causal-graph audit | `.venv/bin/python scripts/audit_causal_graphs.py <14 CDD cohort records>` | `0` | `0 records, 0 errors, 0 warnings` |
| Registered write-route audit | `.venv/bin/python scripts/audit_writers.py` | `0` | `620 scripts examined (51 seeders, 9 registered editors, 2 validated promoters, 52 declared bypasses), OK` |
| Append-only curation history validation | `.venv/bin/python -c "import glob, sys, linkml.validator as v; files = sorted(glob.glob('history/**/*.yaml', recursive=True)); sys.exit(sum(1 for f in files for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml', 'HistoryRecord').results))"` | `0` | `20 history/**/*.yaml files and all 14 cohort in-record curation_history lists validated, 0 errors` |
| CDD errata + editor guard unit tests | `.venv/bin/pytest -q tests/test_cdd_errata.py tests/test_inplace_editor_guards.py` | `0` | `190 passed` |
| Post-remediation structured review bundle validation | `.venv/bin/python scripts/record_review.py --schema schema/record_review.yaml check --require-reviews --base main` | `0` | `28 valid structured review bundles verified, including 20261030T115500Z-cdd-cycle3-stage5-remediation-review (verdict: pass)` |
