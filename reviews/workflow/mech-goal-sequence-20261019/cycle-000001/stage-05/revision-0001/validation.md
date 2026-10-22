# Stage 5 Grouped Review-Finding Remediation Validation Report

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `1`
- **Stage**: `5` (`resolve_review_findings`)
- **Revision**: `1`
- **Base Commit (`origin/main`)**: `f80e2bf88b10d010a0f24427c3101ab501a59639`
- **Scope Frozen At**: `2026-10-22T07:50:00Z`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-04/revision-0001/evidence.yaml` (`509577e3349b9946fdde2b3a8148064a1398c7a3a755ace8d1b3356a43d31c7e`)
- **Fresh Structured Review Bundle**: `reviews/structured/20261022T081000Z-cdd-stage5-remediation-review/review.yaml`

## 1. Issue Grouping & Deduplication Summary

| Group | Issue | Status | Findings | Target Records | Ownership |
| --- | --- | --- | --- | --- | --- |
| `G1` | [#1171](https://github.com/CultureBotAI/proteintraitsmech/issues/1171) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605), [#952](https://github.com/CultureBotAI/proteintraitsmech/issues/952)) | `resolved` | `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `F9`, `F10`, `F11`, `F12` | `CDD:cd09530`, `CDD:cd13344`, `CDD:cd14999`, `CDD:cd15894`, `CDD:cd16523`, `CDD:cd16652`, `CDD:cd17150`, `CDD:cd18592`, `CDD:cd20534`, `CDD:cd21551` | `scripts/cdd_errata.py`, `scripts/repair_cdd_errata.py`, `scripts/seed_cdd.py`, `scripts/record_io.py` |
| `G2` | [#1172](https://github.com/CultureBotAI/proteintraitsmech/issues/1172) (cross-refs [#605](https://github.com/CultureBotAI/proteintraitsmech/issues/605)) | `deferred` | `F1`, `F2` | `CDD:cd00104`, `CDD:cd00959` | `scripts/cdd_errata.py`, `scripts/ground_protein_examples.py`, `data/grounding/qualified_record_bindings.jsonl.d` |

## 2. Repaired `G1` Records (`F3`–`F12`) Pre/Post SHA-256 Digests

| Finding | Record | Path | Pre-Repair SHA-256 | Post-Repair SHA-256 |
| --- | --- | --- | --- | --- |
| `F3` | `CDD:cd09530` | `data/traits/sequence/domain/cdd/sam-domain-of-samd14-subfamily-sam-sterile-alpha-motif-domain-of-samd1-cd09530.yaml` | `36e62ccee26da135fc9a3d26f625be68fcdbf7966d35fabb13971dd13c443957` | `c0bc37a8dec2c3365b52fae2d2aaac5b6bf49821c45a21afb80a40d7f7e948c8` |
| `F4` | `CDD:cd13344` | `data/traits/sequence/domain/cdd/myotubularian-mtm-related-7-protein-mtmr7-pleckstrin-homology-glucosyl-cd13344.yaml` | `25f25b4811e49099c08936c3489d0d1d02339cc8449e5621d2452941c9d6d2d2` | `d5acfeeea0fb6b135735571d61b25f65c9f9ec5b029839f9839cb005d3d71f52` |
| `F5` | `CDD:cd14999` | `data/traits/sequence/domain/cdd/urotensin-ii-receptor-member-of-the-class-a-family-of-seven-transmembr-cd14999.yaml` | `29cb639a3bbf2158faa5680b179a1d1e4c6c392928321359db55344eb23e5df5` | `eaa17d02b2a4cdc66548354887bab13526a28bafdf6a35d4af961bc19a7ec301` |
| `F6` | `CDD:cd15894` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-n-terminal-snare-motifs-of-snap25-a-m-cd15894.yaml` | `1c763a03debd0194ab731f4cd1facdc5a506578a252388a409fe3ceb9f30425d` | `352654c88fa7f674393a96150b36bd52960b7faec9e02a5673e1fe77203d350c` |
| `F7` | `CDD:cd16523` | `data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-myosin-regulatory-light-chain-interac-cd16523.yaml` | `3620b0d7f29bbc2778450e3a9730a1433348af1f13ba8786e3a09106ca0583e4` | `7e7f19caac76932e622daea9432efbefbf66e6f3a3490ee4ca963d62470fe25e` |
| `F8` | `CDD:cd16652` | `data/traits/sequence/domain/cdd/degenerated-ring-dring-finger-found-in-saccharomyces-cerevisiae-requir-cd16652.yaml` | `e15b95997315b996a6488ab375071f3e7db65f626e84d91703a9d6168e6b0029` | `70f2d8b8ccb1cfbee6576e523d68a6a905b5f624e9d66a615b79039a4b324b4e` |
| `F9` | `CDD:cd17150` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17150.yaml` | `587b8c22dc5e29192acb9f1b74ffeeb815729223f478bc32020aacb8e6fe6e0b` | `f864771ab3ec1726a47c308044288f531a2d291e8638b28fd9569e2126c2573b` |
| `F10` | `CDD:cd18592` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18592.yaml` | `819db68ddb4bd173baa067ff5908f9a7e90de8781735097ff24bed8e2c7f4c1f` | `cf1662ace92fe0b6c34751d82b951a2c3e266e619ba2e2af0de7aabec9b72eb5` |
| `F11` | `CDD:cd20534` | `data/traits/sequence/domain/cdd/first-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protein-cd20534.yaml` | `e960b87e4e30cb1624627e3a4b8e01ac2a181c0ffe6bdedba3082edd7fa06f11` | `aeac387dc9662528c19c1f06f4e60d8fa270916e971433c52b4ec5811613a7b4` |
| `F12` | `CDD:cd21551` | `data/traits/sequence/domain/cdd/vefs-vrn2-emf2-fis2-su-z-12-box-found-in-suppressor-of-zeste-12-protei-cd21551.yaml` | `ff603a20dd777948e50bd44c88575bdd8b4cf442e46f70d3df62bfba5a85e7d4` | `daa0e803cd3ed99813feb1e78005903a9cd6dba3e5cad5d877b92b140c63f7f2` |

## 3. Validation Checks Executed

| Check | Command | Exit Code | Result |
| --- | --- | --- | --- |
| Strict LinkML + OAK validation | `.venv/bin/python scripts/validate_strict.py --out /tmp/instance_validation_failures.tsv <12 CDD records>` | `0` | `12 files scanned, 0 errors` |
| Release-pinned UniProt grounding | `.venv/bin/python scripts/validate_uniprot_grounding.py --out /tmp/uniprot_grounding_validation.tsv <12 CDD records>` | `0` | `12 files scanned, 21,331 qualified record bindings, 0 semantic findings` |
| Causal-graph audit | `.venv/bin/python scripts/audit_causal_graphs.py <12 CDD records>` | `0` | `0 records, 0 errors, 0 warnings` |
| Registered write-route audit | `.venv/bin/python scripts/audit_writers.py` | `0` | `618 scripts examined, 8 registered editors, 0 findings` |
| Append-only curation history validation | `.venv/bin/python -c "import glob, sys, linkml.validator as v; sys.exit(sum(1 for f in sorted(glob.glob('history/*.yaml')) for _ in v.validate_file(f, 'src/proteintraitsmech/schema/history.yaml', 'CurationHistoryRecord').results))"` | `0` | `13 history/*.yaml files and all 10 G1 in-record curation_history lists validated, 0 errors` |
| CDD errata + editor guard unit tests | `.venv/bin/python -m pytest -o cache_dir=/tmp/pytest_cache tests/test_cdd_errata.py tests/test_inplace_editor_guards.py -q` | `0` | `123 passed` |
| Post-remediation structured review bundle validation | `record_review.validate_review()` + `parse_review_bundle()` + `source_provenance()` on `reviews/structured/20261022T081000Z-cdd-stage5-remediation-review` | `0` | `working_tree_attestation` verified against `f80e2bf88b10d010a0f24427c3101ab501a59639` across 27 inputs |
