# Cycle 2 Stage 5 Grouped Review-Finding Remediation Validation Report

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `2`
- **Stage**: `5` (`resolve_review_findings`)
- **Revision**: `1`
- **Base Commit (`origin/main`)**: `915722d7841e357c9b305c5bdfd867edf815cf72`
- **Scope Frozen At**: `2026-10-25T23:15:00Z`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-04/revision-0001/evidence.yaml` (`60a2374cb7b0c3289dbcf5c785da8aaf475658639107d70766e5e19fd92b49d9`)
- **Fresh Structured Review Bundle**: `reviews/structured/20261025T233000Z-cdd-cycle2-stage5-remediation-review/review.yaml`

## 1. Issue Grouping & Deduplication Summary

| Group | Issue | Status | Findings | Target Records | Ownership |
| --- | --- | --- | --- | --- | --- |
| `G2` | [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605)) | `resolved` | `F1`, `F2` | `CDD:cd00104`, `CDD:cd00959` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/ground_protein_examples.py`, `data/grounding/qualified_record_bindings.jsonl.d` |
| `G3` | [#1188](https://github.com/CultureBotAI/proteintraitsmech/issues/1188) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605), [#1171](https://github.com/CultureBotAI/proteintraitsmech/issues/1171)) | `resolved` | `F13`, `F14`, `F15`, `F16`, `F17`, `F18` | `CDD:cd20535`, `CDD:cd15885`, `CDD:cd17151`, `CDD:cd17154`, `CDD:cd17149`, `CDD:cd18593` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/seed_cdd.py`, `scripts/record_io.py`, `tests/test_cdd_errata.py` |

## 2. Repaired `G3` Records (`F13`–`F18`) Pre/Post SHA-256 Digests

| Finding | Record | Path | Pre-Repair SHA-256 | Post-Repair SHA-256 |
| --- | --- | --- | --- | --- |
| `F13` | `CDD:cd20535` | `data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml` | `8424b28b9d91f750c4edcdb8cafa59d9d340f4cacb46938cc3355f2d65457074` | `5d4cdbce834a6183b6fa860b8ee439da3c8ea5eb44634f692c08d320180b0249` |
| `F14` | `CDD:cd15885` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml` | `91529c2545061d6f49418adfef6db7d2ab2e530d5c7eee801862fb0a3255edea` | `78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b` |
| `F15` | `CDD:cd17151` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml` | `6b23146bd71c843c2675704f6fbbea6b32f4fe113894c8bbeebf85ab6cb8438d` | `6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d` |
| `F16` | `CDD:cd17154` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml` | `92a423f28b256ec77c726a51a6bce8725e24218cf6f1d94c80fc8a1cfd115941` | `6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d` |
| `F17` | `CDD:cd17149` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml` | `74a1c7b8bb284513e28bce564a5705142f643fa1bfe1c199bf6c338631bb2e76` | `47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5` |
| `F18` | `CDD:cd18593` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml` | `7f72a55f63a4f82d87f7f4456ea7b3085585eb2f7461b79fd3752ca19d368b9a` | `5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb` |

## 3. Validation Checks Executed

| Check | Command | Exit Code | Result |
| --- | --- | --- | --- |
| Registered CDD errata writer dry-run | `.venv/bin/python scripts/repair_cdd_errata.py` | `0` | `6 G3 records need correction; 12 Cycle 1 records already corrected (no history appended)` |
| Registered CDD errata writer apply | `.venv/bin/python scripts/repair_cdd_errata.py --apply` | `0` | `6 G3 records updated in place via record_io.write_validated_record; 12 Cycle 1 records unchanged` |
| Strict LinkML + OAK validation | `.venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv <8 CDD cohort records>` | `0` | `8 files scanned, 0 errors` |
| Release-pinned UniProt grounding | `.venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv <8 CDD cohort records>` | `0` | `8 files scanned, 13,208 registry proteins, 22,314 qualified record bindings, 0 semantic findings` |
| Causal-graph audit | `.venv/bin/python scripts/audit_causal_graphs.py <8 CDD cohort records>` | `0` | `0 records, 0 errors, 0 warnings` |
| Registered write-route audit | `.venv/bin/python scripts/audit_writers.py` | `0` | `618 scripts examined (51 seeders, 8 registered editors, 2 validated promoters, 52 declared bypasses), OK` |
| Append-only curation history validation | `.venv/bin/python -c "import glob, sys, linkml.validator as v; files = sorted(glob.glob('history/**/*.yaml', recursive=True)); sys.exit(sum(1 for f in files for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml', 'HistoryRecord').results))"` | `0` | `15 history/**/*.yaml files and all 8 cohort in-record curation_history lists validated, 0 errors` |
| CDD errata + editor guard unit tests | `.venv/bin/python -m pytest tests/test_cdd_errata.py tests/test_inplace_editor_guards.py -q` | `0` | `160 passed in 3.92s` |
| Post-remediation structured review bundle validation | `.venv/bin/python scripts/record_review.py check --require-reviews --base origin/main` | `0` | `14 valid structured review bundles verified, including 20261025T233000Z-cdd-cycle2-stage5-remediation-review (verdict: pass)` |
