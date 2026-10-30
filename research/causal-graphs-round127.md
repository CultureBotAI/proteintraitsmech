---
topic: causal-graphs
round: 127
date: 2026-10-30
target: foundational-protein-traits (59 unlocked mechanism-bearing records across 11 trait categories; 41 on-disk records updated, 18 verified unchanged)
prior_round: causal-graphs-round126.md
---

# Causal graphs — Round 127: Live-PubMed verbatim abstract snippet curation and edge-snippet deduplication across all 59 unlocked foundational mechanism-bearing records

## Scope and Eligibility Review

Cycle 4, Stage 2 (`causal_graphs`) of run `mech-goal-sequence-20261019` reviewed all `429,406` records in `data/traits/` (`39,659` with `causal_graphs`) against `.claude/skills/edison-causal-graphs/SKILL.md`, `.claude/skills/molecular-causal-graphs/SKILL.md`, and `.claude/skills/curate-yaml-record/SKILL.md`:

- **Foundational protein-trait cohort (`113` records in `scripts/seed_foundational_traits.py` across `17` categories)**:
  - **`46` representation-bounded / non-mechanism-bearing records**: `SEQ_COMPOSITION` (`8`), `STRUCT_QUATERNARY` (`8`), `STRUCT_SYMMETRY` (`7`), `MIXED_COILED_COIL` (`8`), `EVO_CONSERVATION` (`6`), generic `SEQ_LOW_COMPLEXITY` (`5`: `LOWCOMP_REGION`, `LOWCOMP_HOMOREPEAT_TRACT`, `LOWCOMP_CRYPTIC_REPEAT_REGION`, `LOWCOMP_PRION_LIKE_Q_N_RICH_DOMAIN`, `LOWCOMP_RGG_RG_GAR_MOTIF_REGION`), and geometric `STRUCT_CAVITY` (`4`: `POCKET`, `CAVITY`, `CLEFT`, `GROOVE`).
  - **`67` mechanism-bearing cohort records (`MECHANISM_BEARING_CATEGORIES` + `MECHANISM_BEARING_LOWCOMP_IDS`)**:
    - **`8` structural records locked by `scripts/structural_trait_curations.py` (PR `#1202`)**: `6` in `CURATED_NO_GRAPH_IDS` (`ALLOSTERIC_SITE`, `ALLOSTERIC_ORTHOSTERIC_COUPLED`, `ALLOSTERIC_CRYPTIC_POCKET`, `ALLOSTERIC_SUBUNIT_INTERFACE`, `TUNNEL`, `CAVITY_SUBSTRATE_ACCESS_TUNNEL`) and `2` in `SCOPED_GRAPH_REFERENCES` (`ALLOSTERIC_COVALENT_REGULATORY_SITE`, `CAVITY_SELECTIVITY_FILTER_PORE`), left untouched per `tests/test_foundational_traits.py`.
    - **`59` unlocked mechanism-bearing foundational records (`58` `proteintraitsmech:*` + `1` `GO:7770085`, `59` graphs, `246` nodes, `187` edges)**: Audited live against NCBI E-utilities (`efetch`) across all cited PubMed abstracts (`65` unique PMIDs across the `61` graph-bearing foundational records) for (a) exact verbatim substring match against the live PubMed abstract and (b) distinct edge-specific sentences across all edges within each graph.

## Live-PubMed Verbatim Snippet Audit and Curation (41 Records Updated on Disk, 18 Verified Unchanged)

All **41 modified on-disk mechanism-bearing records** (`41` graphs, `174` nodes, `133` edges across `10` trait categories) were updated via `scripts/record_io.py` and synchronized in `scripts/seed_foundational_traits.py` (alongside syncing `proteintraitsmech:INIT_METHIONINE_NON_AUG_DECODED` in `scripts/seed_foundational_traits.py` to match its already-verbatim on-disk YAML) so that every edge across all `59` unlocked mechanism-bearing foundational records (`246/246` grounded nodes, `187/187` RO-typed edges) carries an exact verbatim sentence from its cited PubMed abstract and every edge within a graph carries a distinct snippet:

1. **`FUNC_LOCALIZATION` (`1` updated)**:
   - `GO:7770085` (`data/traits/function/localization/go/protocatechuate-3-4-dioxygenase-complex-go7770085.yaml`): Replaced the duplicated `PMID:11029436` snippet across edges 2, 4, and 5 with distinct verbatim sentences from `PMID:16101286` (edges 1 and 3) and `PMID:11029436` (edges 2, 4, and 5) across its 6-node / 5-edge graph (`pcagh_intradiol_ortho_cleavage`).
2. **`SEQ_INITIATOR_METHIONINE` (`5` updated on disk, `1` verified unchanged on disk and synced in seeder)**:
   - Updated on disk (`5`): `proteintraitsmech:INIT_METHIONINE_EXCISED` (`PMID:27789217`), `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME` (`PMID:42416341`, `PMID:41023640`), `proteintraitsmech:INIT_METHIONINE_N_DEGRON` (`PMID:20110468`), `proteintraitsmech:INIT_METHIONINE_ACETYLATED` (`PMID:42352354`, `PMID:42897562`), and `proteintraitsmech:INIT_METHIONINE_RETAINED` (`PMID:27789217`).
   - Verified unchanged on disk (`1`): `proteintraitsmech:INIT_METHIONINE_NON_AUG_DECODED` (`PMID:18406322`; `scripts/seed_foundational_traits.py` synced to match on-disk verbatim snippet).
3. **`SEQ_MATURE_CHAIN` (`4` updated on disk, `2` verified unchanged)**:
   - Updated on disk (`4`): `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED` (`PMID:40915292`, `PMID:42352431`), `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED` (`PMID:42763638`, `PMID:42846646`), `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE` (`PMID:42724832`, `PMID:42600585`), and `proteintraitsmech:MATURE_CHAIN_SECRETED` (`PMID:42855143`, `PMID:42634148`).
   - Verified unchanged (`2`): `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED` (`PMID:7477383`) and `proteintraitsmech:MATURE_CHAIN_SORTASE_CELL_WALL_ANCHORED` (`PMID:10426969`).
4. **`SEQ_NONSTANDARD_RESIDUE` (`5` updated on disk, `1` verified unchanged)**:
   - Updated on disk (`5`): `proteintraitsmech:NONSTD_DEHYDROAMINO_ACID_RESIDUE` (`PMID:15595664`), `proteintraitsmech:NONSTD_N_FORMYLMETHIONINE` (`PMID:42416341`), `proteintraitsmech:NONSTD_PYRROLYSINE` (`PMID:12029131`), `proteintraitsmech:NONSTD_SELENOCYSTEINE` (`PMID:42886874`), and `proteintraitsmech:NONSTD_ALPHA_KETO_BETA_AMINO_ACID_RESIDUE` (`PMID:29643235`).
   - Verified unchanged (`1`): `proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE` (`PMID:16301328`).
5. **`SEQ_PROPEPTIDE` (`4` updated on disk, `2` verified unchanged)**:
   - Updated on disk (`4`): `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL` (`PMID:42694391`, `PMID:41956947`), `proteintraitsmech:PROPEPTIDE_INTRAMOLECULAR_CHAPERONE` (`PMID:42735804`), `proteintraitsmech:PROPEPTIDE_PROHORMONE_DIBASIC` (`PMID:42763638`, `PMID:42846646`), and `proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION` (`PMID:42797165`, `PMID:42735804`).
   - Verified unchanged (`2`): `proteintraitsmech:PROPEPTIDE_CYSTEINE_SWITCH_METALLOPROTEASE` (`PMID:2204088`) and `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION` (`PMID:42817284`, `PMID:41831090`).
6. **`SEQ_SIGNAL_PEPTIDE` (`6` updated on disk)**:
   - Updated on disk (`6`): `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI` (`PMID:42855143`, `PMID:42634148`), `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII` (`PMID:42855143`, `PMID:42634148`), `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPIII` (`PMID:42855143`, `PMID:42634148`), `proteintraitsmech:SIGNAL_PEPTIDE_SRP_COTRANSLATIONAL` (`PMID:14709160`), `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPI` (`PMID:42855143`, `PMID:42634148`), and `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPII` (`PMID:42855143`, `PMID:42634148`).
7. **`SEQ_TRANSIT_PEPTIDE` (`5` updated on disk, `1` verified unchanged)**:
   - Updated on disk (`5`): `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST` (`PMID:42830843`, `PMID:41529880`), `proteintraitsmech:TRANSIT_PEPTIDE_CHLOROPLAST_STROMA` (`PMID:41809595`, `PMID:41850868`), `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME` (`PMID:38244242`), `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS` (`PMID:42538748`), and `proteintraitsmech:TRANSIT_PEPTIDE_THYLAKOID_LUMEN` (`PMID:41850868`).
   - Verified unchanged (`1`): `proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL` (`PMID:42812058`).
8. **`SEQ_LOW_COMPLEXITY` (`2` verified unchanged)**:
   - Verified unchanged (`2`): `proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK` (`PMID:23901099`) and `proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION` (`PMID:17082456`).
9. **`STRUCT_DISULFIDE` (`6` updated on disk)**:
   - Updated on disk (`6`): `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH` (`PMID:42681370`), `proteintraitsmech:DISULFIDE_CATALYTIC_CXXC` (`PMID:9403310`), `proteintraitsmech:DISULFIDE_CYSTINE_KNOT` (`PMID:42882221`), `proteintraitsmech:DISULFIDE_INTERCHAIN` (`PMID:19005088`), `proteintraitsmech:DISULFIDE_INTRACHAIN` (`PMID:42829235`), and `proteintraitsmech:DISULFIDE_VICINAL_CYSTINE_RING` (`PMID:9843400`).
10. **`STRUCT_CAVITY` (`1` unlocked verified unchanged)**:
    - Verified unchanged (`1`): `proteintraitsmech:CAVITY_BURIED_HYDRATION_MICROCAVITY` (`PMID:8589694`).
11. **`STRUCT_DYNAMICS` (`2` updated on disk, `4` verified unchanged)**:
    - Updated on disk (`2`): `proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP` (`PMID:30703322`) and `proteintraitsmech:DYNAMICS_ORDER_TO_DISORDER_REGULATORY_SWITCH` (`PMID:23245995`).
    - Verified unchanged (`4`): `proteintraitsmech:DYNAMICS_DOMAIN_HINGE` (`PMID:8204609`), `proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH` (`PMID:29784778`, `PMID:20591649`), `proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP` (`PMID:8580836`), and `proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY` (`PMID:19351898`).
12. **`STRUCT_SURFACE` (`3` updated on disk, `4` verified unchanged)**:
    - Updated on disk (`3`): `proteintraitsmech:SURFACE_HOT_SPOT_BINDING_EPITOPE_PATCH` (`PMID:9642043`), `proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH` (`PMID:14654279`), and `proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD` (`PMID:27114034`).
    - Verified unchanged (`4`): `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH` (`PMID:7761829`), `proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH` (`PMID:8612072`), `proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH` (`PMID:19571001`), and `proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT` (`PMID:9778346`).

## Writer & Representation Observations

- **`merge_on_reseed` idempotence on updated `causal_graphs`**: When `scripts/seed_foundational_traits.py` updates `causal_graphs` on an existing record, `_union_list_keys` in `scripts/record_io.py` replaces the `causal_graphs` block with `yaml.safe_dump({"causal_graphs": merged})`, whereas a subsequent `merge_on_reseed(existing, fresh)` call where `old_val == new_val` skips `replace_block` and retains `fresh`'s 2-space list indentation. Running a second `merge_on_reseed` pass normalizes the on-disk record to `fresh`'s exact formatting while preserving `curation_history`, ensuring `rio.merge_on_reseed(on_disk, fresh) == on_disk` idempotence across all `59` unlocked mechanism-bearing records (verified by `tests/test_foundational_traits.py`).
- **Source-limited and representation-bounded records**: The `46` non-mechanism-bearing foundational records (`SEQ_COMPOSITION`, `STRUCT_QUATERNARY`, `STRUCT_SYMMETRY`, `MIXED_COILED_COIL`, `EVO_CONSERVATION`, generic `SEQ_LOW_COMPLEXITY`, and geometric `STRUCT_CAVITY`) and the `6` structural records in `CURATED_NO_GRAPH_IDS` (`scripts/structural_trait_curations.py`, PR `#1202`) remain representation-bounded without `causal_graphs`.

## Provenance

- Records updated on disk with live-PubMed-verified distinct edge snippets: **41** (`40` `proteintraitsmech:*` + `1` `GO:7770085`; `18` unlocked mechanism-bearing records verified unchanged on disk; native `mapping_status: SEEDED` preserved; `curation_history` recorded on all `41` updated records via `scripts/record_io.py`)
- `validate_strict.py` (on all 59 unlocked mechanism-bearing foundational records): `59 files scanned, 0 files with ERROR, 0 total ERROR rows`
- `audit_causal_graphs.py --strict` (on all 61 graph-bearing foundational records): `61 records, 61 graphs, 253 nodes, 192 edges | grounded nodes 249/253 (246/246 on unlocked records), snippet-cited edges 192/192 (187/187 distinct verbatim on unlocked records) | 0 errors, 0 warnings`
- `score_causal_graphs.py` (on all 59 unlocked mechanism-bearing foundational records): **59/59 score 95/100 (`structural_errors=0`, `quality_warnings=0`, `reasons=mapping_status=SEEDED`)**
- Corpus after: **39,659 records with `causal_graphs`** (`429,406` total trait records)
