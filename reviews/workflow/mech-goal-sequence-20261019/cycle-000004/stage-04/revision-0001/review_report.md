# Stage 4 Scientific Record & Cohort Review Report — Cycle 4 Revision 1

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `4`
- **Stage**: `4` (`record_review`)
- **Revision**: `1`
- **Repository**: `CultureBotAI/proteintraitsmech` (`proteintraitsmech`)
- **Reviewed Source Revision**: `5869b9c877b532972a405523c7c6e21945c177e4`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000003/stage-05/revision-0001/evidence.yaml` (`b2fff9f04946591e53a630873434c36df162f32a1e75d2eda4a425686b49e8dc`)
- **Outcome**: `completed` (6 Cycle 3 Stage 5 G4 findings `F19`–`F24` verified `resolved` on disk; 6 new open findings `F25`–`F30` across 6 parent/paralog sibling CDD records preserved for Cycle 4 Stage 5 grouped remediation)

## Native Structured Review Bundles

| Review ID | Kind | Skill | Verdict | Artifact Path | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `20261031T043800Z-cdd-cd17071-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261031T043800Z-cdd-cd17071-record-review/review.yaml` | `10afd869879cbb047607bc097928b707a0585991a6e0ef04f83dc84b54ed2e22` |
| `20261031T043800Z-cdd-cd17071-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261031T043800Z-cdd-cd17071-record-review/review.md` | `9156ce0b4e988c19053439d95d61c5fe08bc79cf487ecf13af812751f01f4910` |
| `20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review/review.yaml` | `1ff58108810922c05c3db0d4dd013c79ae909a516a5eacdac29eb3e10e9dc743` |
| `20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261031T043900Z-cdd-cycle4-sibling-domain-cohort-review/review.md` | `08bd96595a1e4f2d648b90eacbb6357dd383f6536c741007d8a1880ca7b9ca5d` |

## Frozen Inventory & Coverage

Full coverage (`12 / 12` target records, `100%`) of the frozen Cycle 4 Stage 4 `CDD` `SEQ_DOMAIN` cohort comprising:
1. The 6 Cycle 3 Stage 5 G4 records (`CDD:cd17152` / `F19`, `CDD:cd17153` / `F20`, `CDD:cd15884` / `F21`, `CDD:cd15895` / `F22`, `CDD:cd18599` / `F23`, and `CDD:cd18601` / `F24`) repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`), promoted across Cycle 3 Stage 6 (`#1212`) and Cycle 4 Stage 3 (`#1215`), and re-verified on disk at `5869b9c877b532972a405523c7c6e21945c177e4`.
2. The 6 newly audited parent/paralog sibling `CDD` records (`CDD:cd17071`, `CDD:cd16113`, `CDD:cd15855`, `CDD:cd15889`, `CDD:cd15856`, and `CDD:cd15887`) in the `DCX_DCDC2` (`CDD:cl28922`) and `Qb/Qc SNARE_SNAP` (`CDD:cl22856`) clades that still carry upstream NCBI CDD template prose defects, plus 8 boundary-contrast context records (`cd17149`, `cd17150`, `cd17151`, `cd17154`, `cd15885`, `cd15894`, `cd18592`, `cd18593`).

| Target ID | Label | Path | SHA-256 | Finding / Status |
| --- | --- | --- | --- | --- |
| `CDD:cd15855` | `SNARE_SNAP25C_23C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-and-snap23-c-terminal-snare-motifs-of-cd15855.yaml` | `306f687472e4fb91d6dcad19fa7ea13f99eb85fbafb7e86440302296b710b267` | `F27` (`open`) |
| `CDD:cd15856` | `SNARE_SNAP29C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap29-c-terminal-snare-motif-of-snap29-a-me-cd15856.yaml` | `84d8d25d5f6ce8934609c55719a0d4a09b385e2ba1cbb5134c2649573d8327c0` | `F29` (`open`) |
| `CDD:cd15884` | `SNARE_SNAP23C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml` | `e69d6f93c2ecb23a1f5ebf31407261c087a24b52333f171544127e919db95510` | `F21` (`resolved`) |
| `CDD:cd15887` | `SNARE_SNAP29N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap29-n-terminal-snare-motif-of-snap29-a-me-cd15887.yaml` | `edd0ed8a35d333d4f87c1ac2a4aee0d30f5af17a5a6c9a169007401798101519` | `F30` (`open`) |
| `CDD:cd15889` | `SNARE_SNAP25N_23N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap25-and-snap23-n-terminal-snare-motifs-of-cd15889.yaml` | `a7de1d8068c056d075c9ddfc6e5f1a0cb9f9bb4102e6779f92fd06fd75acbd6e` | `F28` (`open`) |
| `CDD:cd15895` | `SNARE_SNAP23N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml` | `5f6fbec3995ae2fb53b2b2bef97ec582cd8a651c9164a83a5bf59e0d2c99aa3b` | `F22` (`resolved`) |
| `CDD:cd16113` | `DCX2_DCDC2_like` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd16113.yaml` | `d3e0f20833782f29d82b77caac4651d4d4f7a6948a18850f974003cacc36022f` | `F26` (`open`) |
| `CDD:cd17071` | `DCX1_DCDC2_like` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17071.yaml` | `deaeaef82093e32e314b0cb69b61a4a3a34da7a0f93922309babf7ef18ffea50` | `F25` (`open`) |
| `CDD:cd17152` | `DCX2_DCDC2` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml` | `082daf8401d1f220c913762740af284d558cee384794debc8ad4ae783946083c` | `F19` (`resolved`) |
| `CDD:cd17153` | `DCX2_DCDC2B` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml` | `d7e0a360b5933d431cc9f738a686058b165b1c12aeafeae856359140c4a56f75` | `F20` (`resolved`) |
| `CDD:cd18599` | `ABC_6TM_MRP5_8_9_D2` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml` | `ce5da2ef4ffd83652c48b1ad5c2e744aafcf51ce4eb011e3b601f842cf0d3585` | `F23` (`resolved`) |
| `CDD:cd18601` | `ABC_6TM_MRP4_D2_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml` | `d7973623d9d52e02a34f979e416688e94444ddc1a30fb6fe88dc56afa62f7099` | `F24` (`resolved`) |

## Diagnostic Checks Executed

- **Strict LinkML + OAK validation** (`scripts/validate_strict.py`): `0` errors across all 12 target records.
- **Release-pinned UniProt grounding replay** (`scripts/validate_uniprot_grounding.py`): `0` semantic findings across all 12 target records (`13,532` registry proteins; `23,062` source evidence objects; `23,062` qualified record bindings; `431` UniProt membership objects).
- **Causal-graph audit** (`scripts/audit_causal_graphs.py`): `0` graphs, `0` errors, `0` warnings.
- **Registered write-route audit** (`scripts/audit_writers.py`): `620` scripts examined (`51` seeders, `9` registered editors, `2` transactional promoters, `52` declared bypasses), `0` findings.
- **Curation history validation** (`src/proteintraitsmech/schema/history.yaml` `HistoryRecord`): `21` files validated, `0` errors.

## Boundary Decisions

All 12 target `CDD` domain records represent distinct conserved protein sequence domains (`trait_axis: SEQUENCE`, `trait_category: SEQ_DOMAIN`; `parent_traits`: `CDD:cl28922`, `CDD:cl22856`, and `CDD:cl38913`) and are retained (`action: retain`) as separate class-level trait records:
- Within the `DCDC2`/`DCDC2B`/`DCDC2C` tandem doublecortin-repeat clade under `parent_traits: [CDD:cl28922]`, subfamily parent profiles `CDD:cd17071` (`DCX1_DCDC2_like`, N-terminal repeat 1 of `DCDC2` and similar proteins) and `CDD:cd16113` (`DCX2_DCDC2_like`, C-terminal repeat 2 of `DCDC2` and similar proteins) are retained alongside paralog-specific repeat-2 child profiles `CDD:cd17152` (`DCX2_DCDC2`, qualified on human `Q9UHG0` residues `142-227` and mouse `Q5DU00` residues `142-227`) and `CDD:cd17153` (`DCX2_DCDC2B`, qualified on human `A2VCK2` residues `146-226`) and boundary-contrast repeat-1/repeat-2 siblings (`cd17149`, `cd17150`, `cd17151`, `cd17154`).
- Within the `Qb/Qc SNARE` clade under `parent_traits: [CDD:cl22856]`, combined `SNAP25`/`SNAP23` N-terminal Qb (`CDD:cd15889`, `SNARE_SNAP25N_23N`) and C-terminal Qc (`CDD:cd15855`, `SNARE_SNAP25C_23C`) profiles, paralog-specific `SNAP23` N-terminal Qb (`CDD:cd15895`, `SNARE_SNAP23N`) and C-terminal Qc (`CDD:cd15884`, `SNARE_SNAP23C`) profiles, and paralog-specific `SNAP29` N-terminal Qb (`CDD:cd15887`, `SNARE_SNAP29N`) and C-terminal Qc (`CDD:cd15856`, `SNARE_SNAP29C`) profiles are retained as non-overlapping N-terminal Qb vs C-terminal Qc coiled-coil SNARE helices and distinct CDD hierarchy/paralog levels.
- Within the `ABCC`/`MRP` transmembrane-domain clade under `parent_traits: [CDD:cl38913]`, C-terminal TMD2 profiles `CDD:cd18599` (`ABC_6TM_MRP5_8_9_D2`, MRPs 5/8/9, `ABCC5`/`ABCC11`/`ABCC12`) and `CDD:cd18601` (`ABC_6TM_MRP4_D2_like`, `MRP4`/`ABCC4`) are retained as distinct ABCC subfamily six-helix bundle profiles non-overlapping with their N-terminal TMD1 counterparts (`CDD:cd18592` and `CDD:cd18593`).

## Verified Resolved Cycle 3 Stage 5 G4 Findings (`F19`–`F24`) & Preserved Open Findings (`F25`–`F30`)

| Finding ID | Issue Key | Target | Severity | Status | Summary |
| --- | --- | --- | --- | --- | --- |
| `F19` | `cdd-cd17152-dcdc2-rpt2-ubiquitin-modifier-digression` | `CDD:cd17152` | `minor` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd17152`) |
| `F20` | `cdd-cd17153-dcdc2b-rpt2-dcdc2-paralog-disease-switch` | `CDD:cd17153` | `major` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd17153`) |
| `F21` | `cdd-cd15884-snap23c-transmembrane-domain-overclaim` | `CDD:cd15884` | `major` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd15884`) |
| `F22` | `cdd-cd15895-snap23n-transmembrane-domain-overclaim` | `CDD:cd15895` | `major` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd15895`) |
| `F23` | `cdd-cd18599-mrp5-8-9-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18599` | `major` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd18599`) |
| `F24` | `cdd-cd18601-mrp4-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18601` | `major` | `resolved` | Repaired in Cycle 3 Stage 5 (`#1210`, PR `#1211`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd18601`) |
| `F25` | `cdd-cd17071-dcx1-dcdc2-like-typo-and-ubiquitin-modifier-digression` | `CDD:cd17071` | `minor` | `open` | `CDD:cd17071` (`DCX1_DCDC2_like`) misspells `Doublecortin-like` as `Dublecortin-like` in its opening definition sentence and interpolates an off-target ubiquitin protein-modifier digression (`PMID:16278295`) |
| `F26` | `cdd-cd16113-dcx2-dcdc2-like-ubiquitin-modifier-digression` | `CDD:cd16113` | `minor` | `open` | `CDD:cd16113` (`DCX2_DCDC2_like`) interpolates an off-target ubiquitin protein-modifier definition sentence into a microtubule-binding DCX beta-grasp repeat profile (`PMID:16278295`) |
| `F27` | `cdd-cd15855-snap25c-23c-transmembrane-domain-overclaim` | `CDD:cd15855` | `major` | `open` | `CDD:cd15855` (`SNARE_SNAP25C_23C`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines (`PMID:9759094`, `PMID:9159129`) |
| `F28` | `cdd-cd15889-snap25n-23n-transmembrane-domain-overclaim` | `CDD:cd15889` | `major` | `open` | `CDD:cd15889` (`SNARE_SNAP25N_23N`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 and SNAP23 are membrane-anchored via palmitoylated cysteines (`PMID:9759094`, `PMID:9159129`) |
| `F29` | `cdd-cd15856-snap29c-transmembrane-domain-overclaim` | `CDD:cd15856` | `major` | `open` | `CDD:cd15856` (`SNARE_SNAP29C`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines (`PMID:9736707`, `PMID:9759094`) |
| `F30` | `cdd-cd15887-snap29n-transmembrane-domain-overclaim` | `CDD:cd15887` | `major` | `open` | `CDD:cd15887` (`SNARE_SNAP29N`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP29 lacks both a transmembrane domain and palmitoylated membrane-anchoring cysteines (`PMID:9736707`, `PMID:9759094`) |

## Limitations & Stage 5 Hand-Off

- No scientific trait records (`data/traits/**/*.yaml`) were edited in Stage 4.
- All 6 new open findings (`F25`–`F30`) share a single upstream seeder/transform root cause in `scripts/seed_cdd.py` and are carried forward as `open` (`carry_forward_ids: [F25, F26, F27, F28, F29, F30]`) for Cycle 4 Stage 5 (`resolve_review_findings`) remediation via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py`.
