# Stage 4 Scientific Record & Cohort Review Report — Cycle 2 Revision 1

- **Run ID**: `mech-goal-sequence-20261019`
- **Cycle**: `2`
- **Stage**: `4` (`record_review`)
- **Revision**: `1`
- **Repository**: `CultureBotAI/proteintraitsmech` (`proteintraitsmech`)
- **Reviewed Source Revision**: `66e8f479733907dc0792e481f41bb2f0fbb9dc27`
- **Previous Evidence**: `reviews/workflow/mech-goal-sequence-20261019/cycle-000001/stage-05/revision-0001/evidence.yaml` (`10d01ef913b4531b80bd3b42ae8eea21f3c61872bc753196411b9e0c16b25a93`)
- **Outcome**: `completed` (2 Cycle 1 carry-forward findings `F1`–`F2` verified `resolved`; 6 new open findings `F13`–`F18` preserved for Cycle 2 Stage 5 grouped remediation)

## Native Structured Review Bundles

| Review ID | Kind | Skill | Verdict | Artifact Path | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `20261025T202200Z-cdd-cd20535-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261025T202200Z-cdd-cd20535-record-review/review.yaml` | `b22ad04e983db076bfe5702c85ef2c22339ab5b6ca1d25b269974773e23f7fea` |
| `20261025T202200Z-cdd-cd20535-record-review` | `record` | `review-yaml-record` | `needs_curation` | `reviews/structured/20261025T202200Z-cdd-cd20535-record-review/review.md` | `258250123dedb058164d816d1efa50b328de499a25c95c4b90fd9c4ac1bcb24e` |
| `20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review/review.yaml` | `2af8bcbcaf00ad835d60e5f6bb8785e15e21067c0f4f86bdab1a480b09b69f13` |
| `20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review` | `category` | `review-yaml-category` | `needs_curation` | `reviews/structured/20261025T202300Z-cdd-cycle2-sibling-domain-cohort-review/review.md` | `f24147baabf5d0b1a4e9c8984da41dc1fda8927f98c7e7bfd04ece23aabb96ca` |

## Frozen Inventory & Coverage

Full coverage (`8 / 8` target records, `100%`) of the frozen Cycle 2 Stage 4 `CDD` `SEQ_DOMAIN` cohort comprising:
1. The 2 Cycle 1 Stage 5 deferred carry-forward records (`CDD:cd00104` / `F1` and `CDD:cd00959` / `F2`) that were repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`), re-audited on disk for carry-forward lineage closure.
2. The 6 unpromoted tandem-repeat and paralog-subfamily `CDD` siblings of the Cycle 1 `CDD` cohort (`CDD:cd20535`, `CDD:cd15885`, `CDD:cd17151`, `CDD:cd17154`, `CDD:cd17149`, and `CDD:cd18593`) plus 6 boundary-contrast context records (`cd20534`, `cd04590`, `cd15894`, `cd17150`, `cd17152`, `cd18592`).

| Target ID | Label | Path | SHA-256 | Finding / Status |
| --- | --- | --- | --- | --- |
| `CDD:cd00104` | Kazal-type serine protease inhibitors and follistatin-like domains | `data/traits/sequence/domain/cdd/kazal-type-serine-protease-inhibitors-and-follistatin-like-domains-kaz-cd00104.yaml` | `62603604963ddda74e8d1b60d200f4e840556af07e4f5d0a4df182c57c441f26` | `F1` (`resolved`) |
| `CDD:cd00959` | 2-deoxyribose-5-phosphate aldolase (DERA) of the DeoC family | `data/traits/sequence/domain/cdd/2-deoxyribose-5-phosphate-aldolase-dera-of-the-deoc-family-2-deoxyribo-cd00959.yaml` | `3cdf985be034ecc04e92d01fb9c9adae688453821d1efdfad8f9909907169b8f` | `F2` (`resolved`) |
| `CDD:cd20535` | Second cyclin box found in cyclin-M (CCNM) family | `data/traits/sequence/domain/cdd/second-cyclin-box-found-in-cyclin-m-ccnm-family-the-ccnm-family-protei-cd20535.yaml` | `8424b28b9d91f750c4edcdb8cafa59d9d340f4cacb46938cc3355f2d65457074` | `F13` (`open`) |
| `CDD:cd15885` | C-terminal SNARE motif of SNAP25 | `data/traits/sequence/domain/cdd/c-terminal-snare-motif-of-snap25-c-terminal-snare-motifs-of-snap25-a-m-cd15885.yaml` | `91529c2545061d6f49418adfef6db7d2ab2e530d5c7eee801862fb0a3255edea` | `F14` (`open`) |
| `CDD:cd17151` | Dublecortin-like domain 1 found in doublecortin domain-containing protein 2C (DCDC2C) and similar proteins | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17151.yaml` | `6b23146bd71c843c2675704f6fbbea6b32f4fe113894c8bbeebf85ab6cb8438d` | `F15` (`open`) |
| `CDD:cd17154` | Doublecortin-like domain 2 found in doublecortin domain-containing protein 2C (DCDC2C) and similar proteins | `data/traits/sequence/domain/cdd/doublecortin-like-domain-2-found-in-doublecortin-domain-containing-pro-cd17154.yaml` | `92a423f28b256ec77c726a51a6bce8725e24218cf6f1d94c80fc8a1cfd115941` | `F16` (`open`) |
| `CDD:cd17149` | Dublecortin-like domain 1 found in doublecortin domain-containing protein 2 (DCDC2) and similar proteins | `data/traits/sequence/domain/cdd/dublecortin-like-domain-1-found-in-doublecortin-domain-containing-prot-cd17149.yaml` | `74a1c7b8bb284513e28bce564a5705142f643fa1bfe1c199bf6c338631bb2e76` | `F17` (`open`) |
| `CDD:cd18593` | Six-transmembrane helical domain 1 (TMD1) of multidrug resistance-associated protein MRP4 and similar proteins | `data/traits/sequence/domain/cdd/six-transmembrane-helical-domain-1-tmd1-of-multidrug-resistance-associ-cd18593.yaml` | `7f72a55f63a4f82d87f7f4456ea7b3085585eb2f7461b79fd3752ca19d368b9a` | `F18` (`open`) |

## Diagnostic Checks Executed

- **Strict LinkML + OAK validation** (`scripts/validate_strict.py`): `0` errors across all 8 target records.
- **Release-pinned UniProt grounding replay** (`scripts/validate_uniprot_grounding.py`): `0` semantic findings across all 8 target records (`13,208` registry proteins; `22,314` source evidence objects; `22,314` qualified record bindings; `431` UniProt membership objects).
- **Causal-graph audit** (`scripts/audit_causal_graphs.py`): `0` graphs, `0` errors, `0` warnings.
- **Registered write-route audit** (`scripts/audit_writers.py`): `618` scripts examined (`51` seeders, `8` registered editors, `2` validated promoters, `52` declared bypasses), `0` findings.
- **Curation history validation** (`src/proteintraitsmech/schema/history.yaml` `HistoryRecord`): `15` files validated, `0` errors.

## Boundary Decisions

All 8 target `CDD` domain records represent distinct conserved protein sequence domains (`trait_axis: SEQUENCE`, `trait_category: SEQ_DOMAIN`, `so_term: SO:0000417`) and are retained (`action: retain`) as separate class-level trait records:
- `CDD:cd00104` (`KAZAL_FS`) and `CDD:cd00959` (`DeoC`) are retained as distinct promoted domain families with verified Cycle 1 Stage 6 errata repairs and sharded `qualified_record_bindings` receipts.
- `CDD:cd20535` (`CYCLIN_CCNM_CCNQ_rpt2`, C-terminal second cyclin box of `CCNQ`/`FAM58A` under `InterPro:IPR006670`) is retained separate from N-terminal first cyclin box sibling `CDD:cd20534` (`CYCLIN_CCNM_CCNQ_rpt1` under `InterPro:IPR006671`) and separate from `CDD:cd04590` (`CBS_pair_ACDP` in `CNNM1-4` magnesium transporters).
- `CDD:cd15885` (`SNARE_SNAP25C`, C-terminal Qc SNARE motif of `SNAP25`, human `P60880` residues `140–202`) is retained separate from N-terminal Qb SNARE motif sibling `CDD:cd15894` (`SNARE_SNAP25N`, residues `19–81`).
- `CDD:cd17149` (`DCX1_DCDC2`, N-terminal repeat 1 of `DCDC2`), `CDD:cd17151` (`DCX1_DCDC2C`, N-terminal repeat 1 of `DCDC2C`), and `CDD:cd17154` (`DCX2_DCDC2C`, C-terminal repeat 2 of `DCDC2C`) are retained separate from each other and from `CDD:cd17150` (`DCX1_DCDC2B`) and `CDD:cd17152` (`DCX2_DCDC2`).
- `CDD:cd18593` (`ABC_6TM_MRP4_D1_like`, TMD1 of `MRP4`/`ABCC4`) is retained separate from sibling `CDD:cd18592` (`ABC_6TM_MRP5_8_9_D1`, TMD1 of `MRP5`/`ABCC5`, `MRP8`/`ABCC11`, and `MRP9`/`ABCC12`).

## Carry-Forward Dispositions (`F1`–`F2`) & Preserved Open Findings (`F13`–`F18`)

| Finding ID | Carried From | Issue Key | Target | Severity | Status | Summary |
| --- | --- | --- | --- | --- | --- | --- |
| `F1` | `F1` | `cdd-cd00104-kazal-definition-typo-and-inhibitor-target-confusion` | `CDD:cd00104` | `minor` | `resolved` | Repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` with updated sharded `qualified_record_bindings` receipts |
| `F2` | `F2` | `cdd-cd00959-dera-duplicated-opening-sentence` | `CDD:cd00959` | `minor` | `resolved` | Repaired in Cycle 1 Stage 6 (`#1172`, PR `#1175`) via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py` with updated sharded `qualified_record_bindings` receipts |
| `F13` | — | `cdd-cd20535-ccnq-rpt2-cnnm-acdp-magnesium-transporter-conflation` | `CDD:cd20535` | `major` | `open` | CDD:cd20535 (`CYCLIN_CCNM_CCNQ_rpt2`) conflates the second cyclin box of Cyclin-Q/Cyclin-M (`CCNQ`/`FAM58A`) with the `CNNM1-4` (`ACDP`) magnesium transporter family |
| `F14` | — | `cdd-cd15885-snap25c-transmembrane-domain-overclaim` | `CDD:cd15885` | `major` | `open` | CDD:cd15885 (`SNARE_SNAP25C`) asserts that Qb/Qc SNAREs have a transmembrane domain whereas SNAP25 is membrane-anchored via palmitoylated cysteines |
| `F15` | — | `cdd-cd17151-dcdc2c-typo-and-dcdc2-paralog-disease-switch` | `CDD:cd17151` | `major` | `open` | CDD:cd17151 (`DCX1_DCDC2C`) misspells Doublecortin-like as Dublecortin-like in definition and switches to paralog `DCDC2` disease genetics |
| `F16` | — | `cdd-cd17154-dcdc2c-rpt2-dcdc2-paralog-disease-switch` | `CDD:cd17154` | `major` | `open` | CDD:cd17154 (`DCX2_DCDC2C`) switches mid-definition from `DCDC2C` to paralog `DCDC2` reading-disability and ADHD genetics |
| `F17` | — | `cdd-cd17149-dcdc2-typo-and-ubiquitin-modifier-digression` | `CDD:cd17149` | `minor` | `open` | CDD:cd17149 (`DCX1_DCDC2`) misspells Doublecortin-like as Dublecortin-like in definition and interpolates an off-target ubiquitin protein-modifier sentence |
| `F18` | — | `cdd-cd18593-mrp4-abcc-mrp7-cftr-misassignment-and-mdr-overclaim` | `CDD:cd18593` | `major` | `open` | CDD:cd18593 (`ABC_6TM_MRP4_D1_like`) misassigns `MRP7` to `ABCC7` (`CFTR`) instead of `ABCC10` and overclaims anticancer multidrug-resistance efflux across all `MRP1-MRP9` members |

## Limitations & Stage 5 Hand-Off

- No scientific trait records (`data/traits/**/*.yaml`) were edited in Stage 4.
- All 6 new open findings (`F13`–`F18`) share a single upstream seeder/transform root cause in `scripts/seed_cdd.py` and are carried forward as `open` (`carry_forward_ids: [F13, F14, F15, F16, F17, F18]`) for Cycle 2 Stage 5 (`resolve_review_findings`) remediation via `scripts/cdd_errata.py` and `scripts/repair_cdd_errata.py`.
