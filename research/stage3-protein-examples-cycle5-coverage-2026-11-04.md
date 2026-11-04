# Cycle 5 Stage 3 (`protein_examples`) Coverage, Promotion, and Blocker Report — 2026-11-04

- **Run / Cycle / Stage**: `mech-goal-sequence-20261019`, Cycle 5, Stage 3 (`protein_examples`, `bc35a11ab014bc2b7b41966f`)
- **Base commit on `main`**: `490bbfd5284a45cb0aeca181b706045a149a08e0`
- **Governing skills**:
  - `.claude/skills/proteintraitsmech-evolve-workflow/SKILL.md`
  - `.claude/skills/ground-protein-example/SKILL.md`
  - `.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md`

---

## 1. Corpus-Wide and Mechanism-Graph (`causal_graphs`) Protein Example Audit

Across all **429,421** trait records in `data/traits/**/*.yaml` (`429,406` in Cycle 4 Stage 3 `+ 12` foundational `proteintraitsmech:*` trait classes added in Cycle 5 Stage 1 PR `#1221` [`c0d87f89e18`] `+ 3` structural-discovery `proteintraitsmech:*` trait classes added in PR `#1205` [`04b0ba0c0f9`: `proteintraitsmech:MEMBRANE_FACING_CHANNEL_FENESTRATION`, `proteintraitsmech:TUNNEL_BOTTLENECK`, `proteintraitsmech:BETA_ARCH`]), **142,403** records carry `canonical_examples` (**420,162** total `canonical_examples` entries on disk: **24,010** `QUALIFIED` examples on disk across **23,431** unique records and **24,026** durable `QualifiedRecordBinding` rows, plus **396,152** `UNQUALIFIED` legacy examples across **118,972** `UNQUALIFIED`-only records).

### 1.1 Corpus-Wide `QUALIFIED` Records and Bindings by `identifier` Prefix

| `identifier` Prefix | Records with `QUALIFIED` Examples on Disk | Durable `QualifiedRecordBinding` Rows | Cycle 5 Stage 3 Delta |
|---|---:|---:|---|
| `PANTHER` | 7,800 | 7,800 | — |
| **`CDD`** | **4,187** | **4,460** | **+927 records (`3,260 → 4,187`), +964 bindings (`3,496 → 4,460`)** |
| `NCBIfam` | 3,157 | 3,157 | — |
| `InterPro` | 2,961 | 3,021 | — |
| `PROSITE` | 2,397 | 2,401 | — |
| `HAMAP` | 1,574 | 1,574 | — |
| `Pfam` | 1,150 | 1,150 | — |
| `RHEA` | 93 | 101 | — |
| `GO` | 53 | 181 | — |
| `ComplexPortal` | 43 | 148 | — |
| `proteintraitsmech` | 16 | 33 | — |
| **Total** | **23,431** | **24,026** | **+927 records, +964 bindings** |

*(Note: 16 multi-interval/binding records share a `CanonicalProteinExample` across multiple `QualifiedRecordBinding` receipts, accounting for `24,010` on-disk `QUALIFIED` example objects across `24,026` durable binding rows.)*

### 1.2 Mechanism-Graph (`causal_graphs`) Protein Example Coverage (`39,669` Records)

Across all **429,421** trait records, **39,669** records contain native `causal_graphs` (`39,659` in Cycle 4 `+ 10` new `proteintraitsmech:*` mechanism-graph records added in Cycle 5 Stage 1 PR `#1221` [`c0d87f89e18`] and refined in Cycle 5 Stage 2 PR `#1223` [`490bbfd5284`]).

| Source / Cohort | Directory / Scope | Records with `causal_graphs` | Records with `canonical_examples` (`>= 1`) | Records with `QUALIFIED` `canonical_examples` on Disk | Records with `0` `canonical_examples` | Qualification & Blocker Status |
|---|---|---:|---:|---:|---:|---|
| **M-CSA** | `data/traits/structure/active_site/mcsa` | 1,003 | 1,003 (100.0%) | 0 | 0 | All 1,003 carry seeded legacy examples on disk; `265` are resolved `QUALIFIED` (`MCSA_RESIDUE_EXACT`, `LOCALIZED`) in `reports/uniprot-grounding/resolved.jsonl` awaiting review-batch selection/promotion, `732` are blocked on `missing_protein_sequence` in `data/raw/align_cache/residue_frame.json`, and `6` lack source residue coordinates (`proteintraitsmech-infra-0002`). |
| **BioLiP** | `data/traits/structure/binding_site/biolip` | 5,572 | 5,572 (100.0%) | 0 | 0 | 100% carry source-derived PDB/UniProt canonical examples; general ligand-class records lack a UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **MetalPDB** | `data/traits/structure/metal_site/metalpdb` | 228 | 228 (100.0%) | 0 | 0 | 100% carry source-derived canonical examples; mononuclear/polynuclear site classes lack a UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **UNIPROT_FT_SEQ_*** | `data/traits/sequence/{initiator_methionine,mature_chain,propeptide,signal_peptide,transit_peptide}/uniprot-seq_*.yaml` | 5 | 5 (100.0%) | 0 | 0 | All 5 intermediate classes (`UNIPROT_FT_SEQ_INIT_METHIONINE`, `UNIPROT_FT_SEQ_MATURE_CHAIN`, `UNIPROT_FT_SEQ_PROPEPTIDE`, `UNIPROT_FT_SEQ_SIGNAL_PEPTIDE`, `UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`) carry 15 curated canonical examples each. |
| **EC** | `data/traits/function/enzymatic_activity/ec` | 6,888 | 5,784 (84.0%) | 0 | 1,104 | 5,784 carry Swiss-Prot `DR` canonical examples from `data/raw/expasy/enzyme.dat`; 1,104 have no Swiss-Prot `DR` cross-references in `enzyme.dat`, and `EC` lacks a source-shipped residue-interval table for `QUALIFIED` promotion (`proteintraitsmech-infra-0002`). |
| **RHEA** | `data/traits/function/enzymatic_activity/rhea` | 18,558 | 93 (0.5%) | 93 | 18,465 | `93` carry `101` promoted `QUALIFIED` bindings on disk; remaining `18,465` require `WHOLE_PROTEIN` functional grounding via `UNIPROT_REST` with cryptographically bound v2 `.uniprot_fetch_receipt.json` (with `ProteinReference.fragment` status) and `uniprot_memberships.jsonl` (`proteintraitsmech-infra-0001`, `proteintraitsmech-infra-0002`). |
| **ARO** | `data/traits/function/resistance/aro` | 7,342 | 0 (0.0%) | 0 | 7,342 | `data/raw/card/aro.json` stores antimicrobial-resistance reference sequences via NCBI protein/nucleotide accessions and CARD model IDs without a reviewed 1:1 Swiss-Prot accession + coordinate table (`proteintraitsmech-infra-0002`). |
| **GO (`GO:7770085`)** | `data/traits/function/localization/go/protocatechuate-3-4-dioxygenase-complex-go7770085.yaml` | 1 | 0 (0.0%) | 0 | 1 | `WHOLE_PROTEIN` functional grounding requires a receipt-locked v2 `UNIPROT_REST` membership batch (`proteintraitsmech-infra-0002`). |
| **`proteintraitsmech:*` classes** | `data/traits/{sequence,structure}/**/*.yaml` | 72 | 0 (0.0%) | 0 | 72 | General mechanism/site classes (`44` sequence feature leaf classes + `28` structural mechanism classes; `70` seeded by `scripts/seed_foundational_traits.py` + `2` by `scripts/seed_localstructuralfeature.py`) defined without a source-shipped UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **Total** | **`data/traits/**/*.yaml` with `causal_graphs`** | **39,669** | **12,685** | **93** | **26,984** | — |

### 1.3 Exact Inventory of the 72 `proteintraitsmech:*` Mechanism-Graph Classes Without `canonical_examples`

Following Cycle 5 Stage 1 (`+12` new `proteintraitsmech:*` trait classes in PR `#1221`, of which `10` carry `causal_graphs` and `2` — `proteintraitsmech:COILED_COIL_PARALLEL_DIMERIC_LEUCINE_ZIPPER` under `data/traits/sequence_structure/coiled_coil/parallel-dimeric-leucine-zipper-coiled-coil.yaml` and `proteintraitsmech:EVOL_GENE_DUPLICATION_SUBFUNCTIONALIZED_PARALOG` under `data/traits/evolution/ortholog_group/gene-duplication-subfunctionalized-paralog-trait.yaml` — are non-mechanism classes without `causal_graphs`, alongside `3` non-mechanism structural discovery classes added in PR `#1205`), there are **72** on-disk `proteintraitsmech:*` records with `causal_graphs` (`70` seeded by `scripts/seed_foundational_traits.py` + `2` — `proteintraitsmech:DISULFIDE_BOND` and `proteintraitsmech:INTERFACE` — seeded by `scripts/seed_localstructuralfeature.py`):

1. **Sequence Feature Leaf Classes (44 records: 38 from Cycles 2–4 + 6 from Cycle 5 Stage 1)**:
   - `data/traits/sequence/initiator_methionine/` (7): `proteintraitsmech:INIT_METHIONINE_ACETYLATED`, `proteintraitsmech:INIT_METHIONINE_EXCISED`, `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME`, `proteintraitsmech:INIT_METHIONINE_M1_LINEAR_UBIQUITINATED` (Cycle 5), `proteintraitsmech:INIT_METHIONINE_N_DEGRON`, `proteintraitsmech:INIT_METHIONINE_NON_AUG_DECODED`, `proteintraitsmech:INIT_METHIONINE_RETAINED`
   - `data/traits/sequence/low_complexity/` (3): `proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION`, `proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK`, `proteintraitsmech:LOWCOMP_RGG_RG_RNA_BINDING_BOX_REGION` (Cycle 5)
   - `data/traits/sequence/mature_chain/` (7): `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED`, `proteintraitsmech:MATURE_CHAIN_BACKBONE_CYCLIZED` (Cycle 5), `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE`, `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED`, `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED`, `proteintraitsmech:MATURE_CHAIN_SECRETED`, `proteintraitsmech:MATURE_CHAIN_SORTASE_CELL_WALL_ANCHORED`
   - `data/traits/sequence/nonstandard_residue/` (6): `proteintraitsmech:NONSTD_ALPHA_KETO_BETA_AMINO_ACID_RESIDUE`, `proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE`, `proteintraitsmech:NONSTD_DEHYDROAMINO_ACID_RESIDUE`, `proteintraitsmech:NONSTD_N_FORMYLMETHIONINE`, `proteintraitsmech:NONSTD_PYRROLYSINE`, `proteintraitsmech:NONSTD_SELENOCYSTEINE`
   - `data/traits/sequence/propeptide/` (7): `proteintraitsmech:PROPEPTIDE_ANTIMICROBIAL_PEPTIDE_ANIONIC_SHIELD` (Cycle 5), `proteintraitsmech:PROPEPTIDE_CYSTEINE_SWITCH_METALLOPROTEASE`, `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL`, `proteintraitsmech:PROPEPTIDE_INTRAMOLECULAR_CHAPERONE`, `proteintraitsmech:PROPEPTIDE_PROHORMONE_DIBASIC`, `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION`, `proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION`
   - `data/traits/sequence/signal_peptide/` (7): `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII_LOL_AVOIDANCE` (Cycle 5), `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPIII`, `proteintraitsmech:SIGNAL_PEPTIDE_SRP_COTRANSLATIONAL`, `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPII`
   - `data/traits/sequence/transit_peptide/` (7): `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST`, `proteintraitsmech:TRANSIT_PEPTIDE_CHLOROPLAST_STROMA`, `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME`, `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS`, `proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL`, `proteintraitsmech:TRANSIT_PEPTIDE_SECONDARY_PLASTID_ASAFAP` (Cycle 5), `proteintraitsmech:TRANSIT_PEPTIDE_THYLAKOID_LUMEN`
2. **Structural Mechanism Classes (28 records: 24 from Cycles 1–4 + 4 from Cycle 5 Stage 1)**:
   - `data/traits/structure/allosteric_site/` (2): `proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE`, `proteintraitsmech:ALLOSTERIC_METAL_ION_REGULATORY_SITE` (Cycle 5)
   - `data/traits/structure/cavity/` (3): `proteintraitsmech:CAVITY_BURIED_HYDRATION_MICROCAVITY`, `proteintraitsmech:CAVITY_INTRAMOLECULAR_CHANNELING_TUNNEL` (Cycle 5), `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE`
   - `data/traits/structure/disulfide/` (8): `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH`, `proteintraitsmech:DISULFIDE_BOND`, `proteintraitsmech:DISULFIDE_CATALYTIC_CXXC`, `proteintraitsmech:DISULFIDE_CYSTINE_KNOT`, `proteintraitsmech:DISULFIDE_CYSTINE_STABILIZED_ALPHA_BETA` (Cycle 5), `proteintraitsmech:DISULFIDE_INTERCHAIN`, `proteintraitsmech:DISULFIDE_INTRACHAIN`, `proteintraitsmech:DISULFIDE_VICINAL_CYSTINE_RING`
   - `data/traits/structure/dynamics/` (7): `proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY`, `proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP`, `proteintraitsmech:DYNAMICS_COUPLED_FOLDING_AND_BINDING_TRANSITION` (Cycle 5), `proteintraitsmech:DYNAMICS_DOMAIN_HINGE`, `proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP`, `proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH`, `proteintraitsmech:DYNAMICS_ORDER_TO_DISORDER_REGULATORY_SWITCH`
   - `data/traits/structure/interface/` (1): `proteintraitsmech:INTERFACE`
   - `data/traits/structure/surface/` (7): `proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH`, `proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH`, `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH`, `proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD`, `proteintraitsmech:SURFACE_HOT_SPOT_BINDING_EPITOPE_PATCH`, `proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH`, `proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT`

Because `scripts/ground_uniprot_examples.py` requires source-shipped residue-interval tables in `data/raw/` (`residue_frame.json`, `interpro_frame.json`, `interpro_grouped_locations.json`, or `mcsa_entries.json`) keyed by external source ID, `ground_uniprot_examples.py` does not emit candidate rows for `proteintraitsmech:*` IDs (`proteintraitsmech-infra-0002`).

---

## 2. Re-Resolution, Finalization, and Promotion of `human-ecoli-yeast-repair-cnp-019`

Under `proteintraitsmech-infra-0005` (`#1191`), `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019` (`1,900` candidate rows across `1,000` `CDD` trait-record groups) had previously failed preflight with `2` occurrence conflicts (`conflict:different_qualified_trait_occurrence` on `CDD:cd20323` and `CDD:cd21958` due to pre-`interpro_location_id` evidence IDs) and `6` `stale:record_changed_since_resolve` rows (`CDD:cd21480`, `CDD:cd21551`, `CDD:cd21592`, `CDD:cd21822`, `CDD:cd22096`, `CDD:cd22253`).

In Cycle 5 Stage 3, we executed the full re-resolve → finalize → promote pipeline for `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019`:

1. **Re-resolution (`scripts/ground_uniprot_examples.py resolve`)**:
   - **Command**:
     ```bash
     .venv/bin/python scripts/ground_uniprot_examples.py resolve \
       --candidates reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.candidates.jsonl \
       --out reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.resolved.jsonl \
       --protein-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.protein_registry.jsonl \
       --evidence-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.occurrence_evidence.jsonl \
       --membership-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.uniprot_memberships.jsonl \
       --sifts-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.sifts_mappings.jsonl \
       --residue-frame data/raw/align_cache/residue_frame.json \
       --interpro-frame data/raw/align_cache/interpro_frame.json \
       --interpro-grouped-frame data/raw/align_cache/interpro_grouped_locations.json \
       --fetch-receipt reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.uniprot_fetch_receipt.json \
       --validate-evidence
     ```
   - Re-resolved all `1,900` candidates (`1,900` `QUALIFIED`, `0` `REJECTED`) across `1,000` `CDD` trait-record groups against current on-disk record preimages, `data/raw/align_cache/interpro_frame.json`, `data/raw/align_cache/interpro_grouped_locations.json` (`1,123` grouped/multi-interval rows with `interpro_location_id`, `777` single-interval rows), and `human-ecoli-yeast-repair-cnp-019.uniprot_fetch_receipt.json` (`1,485` proteins in batch `protein_registry.jsonl`, `1,900` evidence entries in batch `occurrence_evidence.jsonl`, `0` `validate_grounding_evidence` findings, `0` `record_content_findings`, `0` `review_flags`).
2. **Review Partition Finalization (`scripts/finalize_uniprot_review_batch.py`)**:
   - Re-bound `resolution_digest` in `human-ecoli-yeast-repair-cnp-019.review-decisions.partition-001.jsonl` to the re-resolved rows (with `DEFER_ALREADY_SATISFIED` on the 2 groups where the exact priority-taxon protein and `InterPro 110.0` residue interval were already promoted as `QUALIFIED` on disk: `CDD:cd22096` / `UniProtKB:O94952` `30..78` and `CDD:cd21551` / `UniProtKB:Q15022` `563..684`) and ran:
     ```bash
     .venv/bin/python scripts/finalize_uniprot_review_batch.py \
       --batch reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019 \
       --decisions reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.review-decisions.partition-001.jsonl \
       --apply
     ```
   - Finalized `1,900` decisions across `1,000` `CDD` groups (`998` `APPROVED`, `2` all rejected [`DEFER_ALREADY_SATISFIED`]).
3. **Promotion (`scripts/ground_uniprot_examples.py promote --apply`)**:
   - **Command**:
     ```bash
     .venv/bin/python scripts/ground_uniprot_examples.py promote \
       --resolved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.resolved.jsonl \
       --approved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-019.approved.tsv \
       --apply
     ```
   - **Scope & Verification**:
     - `review coverage: CDD=1000/25`
     - `998` approved `LOCALIZED` (`INTERPRO_MATCH`) rows across `998` unique `CDD` trait records (`34` already idempotently present on disk, **`964` written `CDD` trait records** under `data/traits/sequence/domain/cdd/*.yaml`; plus `2` `DEFER_ALREADY_SATISFIED` groups already satisfied on disk).
     - **`927` records transitioned from `0` `QUALIFIED` examples (`UNQUALIFIED` legacy examples only) to `1` `QUALIFIED` example** (`924` upgraded an existing legacy `SWISSPROT_PROFILE` example in-place to `QUALIFIED` with exact `InterPro 110.0` / `UniProt 2026_03` coordinates; `3` — `CDD:cd20346` [`UniProtKB:P36113` on `brcat-domain-found-in-ankyrin-repeat-and-ibr-domain-containing-protein-cd20346.yaml`], `CDD:cd22054` [`UniProtKB:E9PAV3` on `nascent-polypeptide-associated-complex-nac-alpha-subunit-the-nascent-p-cd22054.yaml`], and `CDD:cd22249` [`UniProtKB:A6NJZ7` on `udm1-ubiquitin-dependent-dsb-recruitment-module-1-found-in-ring-finger-cd22249.yaml`] — appended a first `QUALIFIED` example alongside `8` legacy examples).
     - **`37` records transitioned from `1` `QUALIFIED` example to `2` `QUALIFIED` examples** (all `37` upgraded an existing legacy `SWISSPROT_PROFILE` example on a different priority-taxon protein in-place to `QUALIFIED`).
     - **`36` records remained at `1` `QUALIFIED` example** (`34` approved rows already idempotently present on disk + `2` `DEFER_ALREADY_SATISFIED` groups `CDD:cd22096` and `CDD:cd21551` already satisfied on disk).
   - **Durable Registry Totals (Before → After)**:
     - `data/grounding/protein_registry.jsonl`: **13,532 → 14,024** proteins (**+492** new `ProteinReference` entries; `sha256=beca7bd5768ef4727a42bb0e33eeb288dfc835feb00a44041bb2196a96f3d4db`)
     - `data/grounding/occurrence_evidence.jsonl.d/`: **23,062 → 24,026** evidence rows (**+964** new `GroundingEvidence` entries; `256` shards, `max_shard_bytes=74582`, `logical_sha256=ef06d8c6f9f385d0a132cec03a3cc3be65afca0c766283be498098ae6d432ea6`)
     - `data/grounding/qualified_record_bindings.jsonl.d/`: **23,062 → 24,026** transactional bindings (**+964** new record bindings; `256` shards, `max_shard_bytes=176276`, `logical_sha256=d7db0f9a1ea8ad0559c56b026cfb3e0aacb4adcedcf8ba05dcf793bdf7fcb5e3`)

---

## 3. Cross-Mech Protein Inventory Refresh (`data/cross_mech/`)

Rebuilt `data/cross_mech/{coverage.json,coverage.md,protein_inventory.jsonl,protein_sequences.jsonl}` using the pinned snapshot inputs:

```bash
.venv/bin/python scripts/build_cross_mech_inventory.py \
  --residue-frame data/raw/align_cache/residue_frame.json \
  --uniprot-discovery reports/uniprot-grounding/cross-mech/refresh-20261013/discovery.entries.json \
  --candidate-queue reports/uniprot-grounding/cross-mech/refresh-20261013/candidates.jsonl \
  --review-batch reports/uniprot-grounding/review-batches/cross-mech-refresh-20261010 \
  --review-batch reports/uniprot-grounding/review-batches/cross-mech-complex-20261010 \
  --apply
```

| Metric | Before Cycle 5 Stage 3 | After Cycle 5 Stage 3 | Delta |
|---|---:|---:|---:|
| Sibling Mechs scanned | 13 | 13 | 0 |
| Distinct proteins in inventory | 2,602 | 2,602 | 0 |
| **`HAS_QUALIFIED_PTM_EXAMPLE`** | **953** | **958** | **+5** (`UniProtKB:P11511` via `CDD:cd20616`, `UniProtKB:P24385` via `CDD:cd20573`/`CDD:cd20576`, `UniProtKB:P24864` via `CDD:cd20579`/`CDD:cd20581`, `UniProtKB:P35222` via `CDD:cd21724`, `UniProtKB:Q05513` via `CDD:cd21095`) |
| **`LEGACY_EXAMPLES_ONLY`** | **653** | **648** | **-5** |
| `DISCOVERY_ONLY` | 996 | 996 | 0 |
| **`proteins_with_localized_qualified_traits`** | **346** | **353** | **+7** (`UniProtKB:P08394` via `CDD:cd22352`, `UniProtKB:P0C037` via `CDD:cd20296`, `UniProtKB:P11511` via `CDD:cd20616`, `UniProtKB:P24385` via `CDD:cd20573`/`CDD:cd20576`, `UniProtKB:P24864` via `CDD:cd20579`/`CDD:cd20581`, `UniProtKB:P35222` via `CDD:cd21724`, `UniProtKB:Q05513` via `CDD:cd21095`; plus 5 proteins that already had localized qualified traits gained additional localized `CDD` traits: `UniProtKB:O00625` [`+CDD:cd20288`], `UniProtKB:O96028` [`+CDD:cd21991`], `UniProtKB:P07333` [`+CDD:cd20936`], `UniProtKB:P07648` [`+CDD:cd22353`], `UniProtKB:P30745` [`+CDD:cd21117`]) |
| `sibling_pair_statuses.QUALIFIED_ON_TRAIT` | 393 | 393 | 0 |
| `sibling_pair_statuses.LEGACY_ON_TRAIT` | 6 | 6 | 0 |
| `sibling_pair_statuses.ABSENT_FROM_TRAIT` | 272 | 272 | 0 |
| `sibling_pair_statuses.NOT_A_PTM_NAMESPACE` | 919 | 919 | 0 |
| `sibling_pair_statuses.TRAIT_NOT_IN_PTM` | 167 | 167 | 0 |
| Active sequences (`2026_03` + 5 `2026_02`) | 2,484 | 2,484 | 0 |
| Sequences with usable generic annotations | 2,419 | 2,419 | 0 |
| `protein_inventory.jsonl` `sha256` | `363a50ea3ee7c5c0cfecd561059d2676cd24725d598201e3fcd800989e9c455c` | `caad0b5cf53a0ced6d7e8bf5ac901fd52452e5b0584efd3f625184063eef23f3` | updated |
| `protein_sequences.jsonl` `sha256` | `8f8d258ced134231ee894cd240f684fa3c485477610542e8c122249174787396` | `2be14ffe471e41090604ce2f056a16de319b474af5b5771286c5ee2a70035011` | updated |
