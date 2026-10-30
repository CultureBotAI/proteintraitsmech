# Stage 4 Scientific Record & Cohort Review Report — Cycle 3 Revision 1

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `3`
- **Stage**: `4` (`record_review`)
- **Revision**: `1`
- **Repository**: `CultureBotAI/proteintraitsmech` (`proteintraitsmech`)
- **Reviewed Source Revision**: `adef1252dc47d9fc25268e3f36ad2ade8adba1a2`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000002/stage-05/revision-0001/evidence.yaml` (`37cf6670f427c35fabdccb772c188323d7d5128d595e571f39561fab61fc709c`)
- **Outcome**: `completed` (8 Cycle 1/2 carry-forward findings `F1`–`F2` and `F13`–`F18` verified `resolved`; 6 new open findings `F19`–`F24` preserved for Cycle 3 Stage 5 grouped remediation)

## Native Structured Review Bundles

| Review ID | Kind | Skill | Verdict | Artifact Path | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `20261030T092000Z-cdd-cd17152-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.yaml` | `e82d4b4dfd671d88e936fa3603792eb6d96de1a58a6fb5998e0f0c3e09e13d4f` |
| `20261030T092000Z-cdd-cd17152-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261030T092000Z-cdd-cd17152-record-review/review.md` | `5437944779a67a0e3fe88942daffc093413924e1dc7b4706e0510bad18cad6ac` |
| `20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.yaml` | `589053861c1a9faaf4dff3d29b7d28ef6fb9f281e902e2a1c99a19bfd41fa12f` |
| `20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261030T092100Z-cdd-cycle3-sibling-domain-cohort-review/review.md` | `6202eb7d72995245ab26b0d27ac82f45aa24e64a88e4508b7db954d0e79ccee7` |

## Frozen Inventory & Coverage

Full coverage (`14 / 14` target records, `100%`) of the frozen Cycle 3 Stage 4 `CDD` `SEQ_DOMAIN` cohort comprising:
1. The 2 Cycle 1 carry-forward records (`CDD:cd00104` / `F1` and `CDD:cd00959` / `F2`) repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`) and re-verified on disk.
2. The 6 Cycle 2 carry-forward records (`CDD:cd20535` / `F13`, `CDD:cd15885` / `F14`, `CDD:cd17151` / `F15`, `CDD:cd17154` / `F16`, `CDD:cd17149` / `F17`, and `CDD:cd18593` / `F18`) repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) and re-verified on disk.
3. The 6 remaining unpromoted tandem-repeat and paralog-subfamily `CDD` siblings (`CDD:cd17152`, `CDD:cd17153`, `CDD:cd15884`, `CDD:cd15895`, `CDD:cd18599`, and `CDD:cd18601`) plus 5 boundary-contrast context records (`cd17150`, `cd15894`, `cd15886`, `cd18592`, `cd18597`).

| Target ID | Label | Path | SHA-256 | Finding / Status |
| --- | --- | --- | --- | --- |
| `CDD:cd00104` | `KAZAL_FS` | `data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml` | `62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26` | F1 (`resolved`) |
| `CDD:cd00959` | `DeoC` | `data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml` | `3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f` | F2 (`resolved`) |
| `CDD:cd15884` | `SNARE_SNAP23C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap23-c-terminal-snare-motifs-of-snap23-a-m-cd15884.yaml` | `25c96270182b7deb52e5f9572354a19ecf9a4475a56315cb32367a69c45c0d04` | F21 (`open`) |
| `CDD:cd15885` | `SNARE_SNAP25C` | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml` | `78aed7842aa5e709350266838df7ec4f82495dd329040a99a8e9f79ae5433b1b` | F14 (`resolved`) |
| `CDD:cd15895` | `SNARE_SNAP23N` | `data/traits/sequence/domain/cdd/n-terminal-snare-motif-of-snap23-n-terminal-snare-motifs-of-snap23-a-m-cd15895.yaml` | `615522b360750919bbe4a9ad8005ccc1aa29ea684fab698cc0cf869838151e9d` | F22 (`open`) |
| `CDD:cd17149` | `DCX1_DCDC2` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml` | `47be01b784a9b7ce63f5b0a8bdcde6bc4aa040cc5bbadd27d3e480980d474bd5` | F17 (`resolved`) |
| `CDD:cd17151` | `DCX1_DCDC2C` | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml` | `6ec151fa12937392cbaf557d7f62d497d3c8d05471ec24b16d9efc2210769a8d` | F15 (`resolved`) |
| `CDD:cd17152` | `DCX2_DCDC2` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17152.yaml` | `e417b4fe9e69deec13282e792245d3746f15f29e609572f083a8cbc4fd68b11b` | F19 (`open`) |
| `CDD:cd17153` | `DCX2_DCDC2B` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17153.yaml` | `dc4f778b022ed8629d36eeeebe9a67b89437602f80da52cc2785c885b23f66dc` | F20 (`open`) |
| `CDD:cd17154` | `DCX2_DCDC2C` | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml` | `6ec1fd4e6c77d35fcd3c65b0387f517870965eeb622e47e122665a32b27c1f1d` | F16 (`resolved`) |
| `CDD:cd18593` | `ABC_6TM_MRP4_D1_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml` | `5c4fe1cf626fe5a1819aa98dfd15eff180d6f722dc872acbbe6e0410ae2ddcfb` | F18 (`resolved`) |
| `CDD:cd18599` | `ABC_6TM_MRP5_8_9_D2` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18599.yaml` | `55248bf08f405c7fb665974fecef9c1fcdd05a5b67774e4753a6dbf3cb53faea` | F23 (`open`) |
| `CDD:cd18601` | `ABC_6TM_MRP4_D2_like` | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-2-tmd2-of-multidrug-resistance-associ-cd18601.yaml` | `04c649ce8b0463952a711aa86cc477e9f4a130717a1e930e3e280ef478f4a080` | F24 (`open`) |
| `CDD:cd20535` | `CYCLIN_CCNM_CCNQ_rpt2` | `data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml` | `5d4cdbce834a6183b6fa860b8ee439da3c8ea5eb44634f692c08d320180b0249` | F13 (`resolved`) |

## Diagnostic Checks Executed

- **Strict LinkML + OAK validation** (`scripts/validate_strict.py`): `0` errors across all 14 target records.
- **Release-pinned UniProt grounding replay** (`scripts/validate_uniprot_grounding.py`): `0` semantic findings across all 14 target records (`13,208` registry proteins; `22,314` source evidence objects; `22,314` qualified record bindings; `431` UniProt membership objects).
- **Causal-graph audit** (`scripts/audit_causal_graphs.py`): `0` graphs, `0` errors, `0` warnings.
- **Registered write-route audit** (`scripts/audit_writers.py`): `618` scripts examined (`51` seeders, `8` registered editors, `2` validated promoters, `52` declared bypasses), `0` findings.
- **Curation history validation** (`src/proteintraitsmech/schema/history.yaml` `HistoryRecord`): `15` files validated, `0` errors.

## Boundary Decisions

All 14 target `CDD` domain records represent distinct conserved protein sequence domains (`trait_axis: SEQUENCE`, `trait_category: SEQ_DOMAIN`; `parent_traits`: `CDD:cl00097`, `CDD:cl21457`, `CDD:cl40454`, `CDD:cl22856`, `CDD:cl28922`, and `CDD:cl38913`) and are retained (`action: retain`) as separate class-level trait records:
- `CDD:cd00104` (`KAZAL_FS`, `parent_traits: [CDD:cl00097]`, `28` canonical examples: `26` qualified and `2` historical across `39` durable `qualified_record_bindings.jsonl.d` receipts), `CDD:cd00959` (`DeoC`, `parent_traits: [CDD:cl21457]`, `5` canonical examples: `2` qualified and `3` historical across `2` durable `qualified_record_bindings.jsonl.d` receipts), and `CDD:cd20535` (`CYCLIN_CCNM_CCNQ_rpt2`, `parent_traits: [CDD:cl40454]`, C-terminal second cyclin box of `CCNQ`/`FAM58A`) are retained as distinct sequence-domain families with verified Cycle 1 Stage 6 and Cycle 2 Stage 5 errata repairs.
- Within the `DCDC2`/`DCDC2B`/`DCDC2C` tandem doublecortin-repeat cohort under `parent_traits: [CDD:cl28922]`, `CDD:cd17149` (`DCX1_DCDC2`, N-terminal repeat 1 of human `DCDC2` `Q9UHG0`), `CDD:cd17152` (`DCX2_DCDC2`, C-terminal repeat 2 of human `DCDC2` `Q9UHG0`), `CDD:cd17153` (`DCX2_DCDC2B`, C-terminal repeat 2 of human `DCDC2B` `A2VCK2`), `CDD:cd17151` (`DCX1_DCDC2C`, N-terminal repeat 1 of human `DCDC2C` `A8MYV0`), and `CDD:cd17154` (`DCX2_DCDC2C`, C-terminal repeat 2 of human `DCDC2C` `A8MYV0`) are retained separate from each other and from N-terminal `DCDC2B` sibling `CDD:cd17150` (`DCX1_DCDC2B`, qualified on human `A2VCK2` at residues `24-110`).
- Within the `SNAP25`/`SNAP23`/`SNAP29` Qb/Qc t-SNARE cohort under `parent_traits: [CDD:cl22856]`, `CDD:cd15885` (`SNARE_SNAP25C`, C-terminal Qc SNARE motif of `SNAP25`), `CDD:cd15895` (`SNARE_SNAP23N`, N-terminal Qb SNARE motif of `SNAP23` on human `O00161` and mouse `O09044`), and `CDD:cd15884` (`SNARE_SNAP23C`, C-terminal Qc SNARE motif of `SNAP23` on human `O00161` and mouse `O09044`) are retained separate from each other and from promoted boundary-contrast siblings `CDD:cd15894` (`SNARE_SNAP25N`, qualified on human `P60880` at residues `10-82`) and `CDD:cd15886` (`SNARE_SNAP29N`, qualified on human `O95721` at residues `50-112`).
- Within the `ABCC`/`MRP` transmembrane-domain cohort under `parent_traits: [CDD:cl38913]`, `CDD:cd18593` (`ABC_6TM_MRP4_D1_like`, TMD1 of `MRP4`/`ABCC4`), `CDD:cd18601` (`ABC_6TM_MRP4_D2_like`, TMD2 of `MRP4`/`ABCC4` on human `O15439` and mouse `E9Q236`), and `CDD:cd18599` (`ABC_6TM_MRP5_8_9_D2`, TMD2 of `MRP5`/`ABCC5` `O15440`, `MRP8`/`ABCC11` `Q96J66`, and `MRP9`/`ABCC12` `Q96J65`) are retained separate from each other and from repaired boundary-contrast siblings `CDD:cd18592` (`ABC_6TM_MRP5_8_9_D1`, qualified on human `O15440` at residues `162-454`) and `CDD:cd18597` (`ABC_6TM_MRP1_2_3_6_D2`, qualified on rat `O88269` at residues `967-1241`).

## Carry-Forward Dispositions (`F1`–`F2`, `F13`–`F18`) & Preserved Open Findings (`F19`–`F24`)

| Finding ID | Carried From | Issue Key | Target | Severity | Status | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `F1` | `F1` | `cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion` | `CDD:cd00104` | `minor` | `resolved` | Repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` with updated sharded `qualified_record_bindings` receipts |
| `F2` | `F2` | `cdd-cd00959-dera-duplicated-opening-sentence` | `CDD:cd00959` | `minor` | `resolved` | Repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` with updated sharded `qualified_record_bindings` receipts |
| `F13` | `F13` | `cdd-cd20535-ccnq-rpt2-cnnm-acdp-magnesium-transporter-conflation` | `CDD:cd20535` | `major` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd20535`) |
| `F14` | `F14` | `cdd-cd15885-snap25c-transmembrane-domain-overclaim` | `CDD:cd15885` | `major` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd15885`) |
| `F15` | `F15` | `cdd-cd17151-dcdc2c-typo-and-dcdc2-paralog-disease-switch` | `CDD:cd17151` | `major` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd17151`) |
| `F16` | `F16` | `cdd-cd17154-dcdc2c-rpt2-dcdc2-paralog-disease-switch` | `CDD:cd17154` | `major` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd17154`) |
| `F17` | `F17` | `cdd-cd17149-dcdc2-typo-and-ubiquitin-modifier-digression` | `CDD:cd17149` | `minor` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd17149`) |
| `F18` | `F18` | `cdd-cd18593-mrp4-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18593` | `major` | `resolved` | Repaired in Cycle 2 Stage 5 (`#1188`, PR `#1201`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` (`source_erratum_cd18593`) |
| `F19` | — | `cdd-cd17152-dcdc2-rpt2-ubiquitin-modifier-digression` | `CDD:cd17152` | `minor` | `open` | CDD:cd17152 (`DCX2_DCDC2`) interpolates an off-target ubiquitin protein-modifier definition sentence into a microtubule-binding DCX repeat profile |
| `F20` | — | `cdd-cd17153-dcdc2b-rpt2-dcdc2-paralog-disease-switch` | `CDD:cd17153` | `major` | `open` | CDD:cd17153 (`DCX2_DCDC2B`) switches mid-definition from `DCDC2B` to paralog `DCDC2` reading-disability and ADHD genetics |
| `F21` | — | `cdd-cd15884-snap23c-transmembrane-domain-overclaim` | `CDD:cd15884` | `major` | `open` | CDD:cd15884 (`SNARE_SNAP23C`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines |
| `F22` | — | `cdd-cd15895-snap23n-transmembrane-domain-overclaim` | `CDD:cd15895` | `major` | `open` | CDD:cd15895 (`SNARE_SNAP23N`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP23 is membrane-anchored via palmitoylated cysteines |
| `F23` | — | `cdd-cd18599-mrp5-8-9-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18599` | `major` | `open` | CDD:cd18599 (`ABC_6TM_MRP5_8_9_D2`) misassigns `MRP7` to `ABCC7` (`CFTR`) instead of `ABCC10` and overclaims anticancer multidrug-resistance efflux across all `MRP1-MRP9` members |
| `F24` | — | `cdd-cd18601-mrp4-d2-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18601` | `major` | `open` | CDD:cd18601 (`ABC_6TM_MRP4_D2_like`) misassigns `MRP7` to `ABCC7` (`CFTR`) instead of `ABCC10` and overclaims anticancer multidrug-resistance efflux across all `MRP1-MRP9` members |

## Limitations & Stage 5 Hand-Off

- No scientific trait records (`data/traits/**/*.yaml`) were edited in Stage 4.
- All 6 new open findings (`F19`–`F24`) share a single upstream seeder/transform root cause in `scripts/seed_cdd.py` and are carried forward as `open` (`carry_forward_ids: [F19, F20, F21, F22, F23, F24]`) for Cycle 3 Stage 5 (`resolve_review_findings`) remediation via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py`.
