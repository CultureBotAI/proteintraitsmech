# Cycle 4 Stage 3 (`protein_examples`) Coverage, Promotion, and Blocker Report — 2026-10-30

- **Run / Cycle / Stage**: `mech-goal-sequence-20261019`, Cycle 4, Stage 3 (`protein_examples`, `d9d0ee7e587ecad667cf9bdb`)
- **Base commit on `main`**: `64daeedca4e133f20ec6f2cc6fa9819b18f8daa3`
- **Governing skills**:
  - `.claude/skills/proteintraitsmech-evolve-workflow/SKILL.md`
  - `.claude/skills/ground-protein-example/SKILL.md`
  - `.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md`

---

## 1. Corpus-Wide and Mechanism-Graph (`causal_graphs`) Protein Example Audit

Across all **429,406** trait records in `data/traits/**/*.yaml` (`+12` foundational `proteintraitsmech:*` trait classes added in Cycle 4 Stage 1 PR `#1213`), **142,403** records carry `canonical_examples` (**420,159** total `canonical_examples` entries on disk: **23,046** `QUALIFIED` examples on disk across **22,504** unique records and **23,062** durable `QualifiedRecordBinding` rows, plus **397,113** `UNQUALIFIED` legacy examples across **119,899** `UNQUALIFIED`-only records).

### 1.1 Corpus-Wide `QUALIFIED` Records and Bindings by `identifier` Prefix

| `identifier` Prefix | Records with `QUALIFIED` Examples on Disk | Durable `QualifiedRecordBinding` Rows | Cycle 4 Stage 3 Delta |
|---|---:|---:|---|
| `PANTHER` | 7,800 | 7,800 | — |
| **`CDD`** | **3,260** | **3,496** | **+369 records (`2,891 → 3,260`), +427 bindings (`3,069 → 3,496`)** |
| `NCBIfam` | 3,157 | 3,157 | — |
| `InterPro` | 2,961 | 3,021 | — |
| `PROSITE` | 2,397 | 2,401 | — |
| `HAMAP` | 1,574 | 1,574 | — |
| `Pfam` | 1,150 | 1,150 | — |
| `RHEA` | 93 | 101 | — |
| `GO` | 53 | 181 | — |
| `ComplexPortal` | 43 | 148 | — |
| `proteintraitsmech` | 16 | 33 | — |
| **Total** | **22,504** | **23,062** | **+369 records, +427 bindings** |

*(Note: 16 multi-interval/binding records share a `CanonicalProteinExample` across multiple `QualifiedRecordBinding` receipts, accounting for `23,046` on-disk `QUALIFIED` example objects across `23,062` durable binding rows.)*

### 1.2 Mechanism-Graph (`causal_graphs`) Protein Example Coverage (`39,659` Records)

Across all **429,406** trait records, **39,659** records contain native `causal_graphs` (`39,649` in Cycle 3 `+ 10` new `proteintraitsmech:*` mechanism-graph records added in Cycle 4 Stage 1 PR `#1213`).

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
| **`proteintraitsmech:*` classes** | `data/traits/{sequence,structure}/**/*.yaml` | 62 | 0 (0.0%) | 0 | 62 | General mechanism/site classes (`38` sequence feature leaf classes + `24` structural mechanism classes; `61` seeded by `scripts/seed_foundational_traits.py` + `1` by `scripts/seed_localstructuralfeature.py`) defined without a source-shipped UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **Total** | **`data/traits/**/*.yaml` with `causal_graphs`** | **39,659** | **12,685** | **93** | **26,974** | — |

### 1.3 Exact Inventory of the 62 `proteintraitsmech:*` Mechanism-Graph Classes Without `canonical_examples`

Following Cycle 4 Stage 1 (`+12` new `proteintraitsmech:*` trait classes in PR `#1213`, of which `10` carry `causal_graphs` and `2` — `proteintraitsmech:TRANSMEMBRANE_REENTRANT_PORE_LOOP` under `data/traits/sequence_structure/transmembrane/reentrant-pore-loop-membrane-region.yaml` and `proteintraitsmech:EVOL_DE_NOVO_ORPHAN_LINEAGE_RESTRICTED` under `data/traits/evolution/clade_specific/de-novo-orphan-lineage-restricted-trait.yaml` — are non-mechanism classes without `causal_graphs`), there are **62** on-disk `proteintraitsmech:*` records with `causal_graphs` (`61` seeded by `scripts/seed_foundational_traits.py` + `1` — `proteintraitsmech:DISULFIDE_BOND` — seeded by `scripts/seed_localstructuralfeature.py`):

1. **Sequence Feature Leaf Classes (38 records: 32 from Cycles 2–3 + 6 from Cycle 4 Stage 1)**:
   - `data/traits/sequence/initiator_methionine/` (6): `proteintraitsmech:INIT_METHIONINE_ACETYLATED`, `proteintraitsmech:INIT_METHIONINE_EXCISED`, `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME`, `proteintraitsmech:INIT_METHIONINE_N_DEGRON`, `proteintraitsmech:INIT_METHIONINE_NON_AUG_DECODED` (Cycle 4), `proteintraitsmech:INIT_METHIONINE_RETAINED`
   - `data/traits/sequence/low_complexity/` (2): `proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION`, `proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK`
   - `data/traits/sequence/mature_chain/` (6): `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED`, `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE`, `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED`, `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED`, `proteintraitsmech:MATURE_CHAIN_SECRETED`, `proteintraitsmech:MATURE_CHAIN_SORTASE_CELL_WALL_ANCHORED` (Cycle 4)
   - `data/traits/sequence/nonstandard_residue/` (6): `proteintraitsmech:NONSTD_ALPHA_KETO_BETA_AMINO_ACID_RESIDUE` (Cycle 4), `proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE`, `proteintraitsmech:NONSTD_DEHYDROAMINO_ACID_RESIDUE` (Cycle 4), `proteintraitsmech:NONSTD_N_FORMYLMETHIONINE`, `proteintraitsmech:NONSTD_PYRROLYSINE`, `proteintraitsmech:NONSTD_SELENOCYSTEINE`
   - `data/traits/sequence/propeptide/` (6): `proteintraitsmech:PROPEPTIDE_CYSTEINE_SWITCH_METALLOPROTEASE` (Cycle 4), `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL`, `proteintraitsmech:PROPEPTIDE_INTRAMOLECULAR_CHAPERONE`, `proteintraitsmech:PROPEPTIDE_PROHORMONE_DIBASIC`, `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION`, `proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION`
   - `data/traits/sequence/signal_peptide/` (6): `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPIII`, `proteintraitsmech:SIGNAL_PEPTIDE_SRP_COTRANSLATIONAL` (Cycle 4), `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPII`
   - `data/traits/sequence/transit_peptide/` (6): `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST`, `proteintraitsmech:TRANSIT_PEPTIDE_CHLOROPLAST_STROMA`, `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME`, `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS`, `proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL`, `proteintraitsmech:TRANSIT_PEPTIDE_THYLAKOID_LUMEN`
2. **Structural Mechanism Classes (24 records: 20 from Cycles 1–3 + 4 from Cycle 4 Stage 1)**:
   - `data/traits/structure/allosteric_site/` (1): `proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE`
   - `data/traits/structure/cavity/` (2): `proteintraitsmech:CAVITY_BURIED_HYDRATION_MICROCAVITY` (Cycle 4), `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE`
   - `data/traits/structure/disulfide/` (7): `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH`, `proteintraitsmech:DISULFIDE_BOND`, `proteintraitsmech:DISULFIDE_CATALYTIC_CXXC`, `proteintraitsmech:DISULFIDE_CYSTINE_KNOT`, `proteintraitsmech:DISULFIDE_INTERCHAIN`, `proteintraitsmech:DISULFIDE_INTRACHAIN`, `proteintraitsmech:DISULFIDE_VICINAL_CYSTINE_RING` (Cycle 4)
   - `data/traits/structure/dynamics/` (6): `proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY`, `proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP`, `proteintraitsmech:DYNAMICS_DOMAIN_HINGE`, `proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP`, `proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH`, `proteintraitsmech:DYNAMICS_ORDER_TO_DISORDER_REGULATORY_SWITCH` (Cycle 4)
   - `data/traits/structure/interface/` (1): `proteintraitsmech:INTERFACE`
   - `data/traits/structure/surface/` (7): `proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH`, `proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH`, `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH`, `proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD`, `proteintraitsmech:SURFACE_HOT_SPOT_BINDING_EPITOPE_PATCH` (Cycle 4), `proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH`, `proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT`

Because `scripts/ground_uniprot_examples.py` requires source-shipped residue-interval tables in `data/raw/` (`residue_frame.json`, `interpro_frame.json`, `interpro_grouped_locations.json`, or `mcsa_entries.json`) keyed by external source ID, `ground_uniprot_examples.py` does not emit candidate rows for `proteintraitsmech:*` IDs (`proteintraitsmech-infra-0002`).

---

## 2. Re-Resolution, Finalization, and Promotion of `human-ecoli-yeast-repair-cnp-020`

Under `proteintraitsmech-infra-0005` (`#1191`), `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020` (`970` candidate rows across `542` `CDD` trait-record groups) had previously failed preflight with `50` `stale:record_changed_since_resolve` rows (`target-cnp020-000..002of008` had promoted `115` of its `542` `CDD` records after `cnp-020` was originally resolved, and `362` grouped/multi-interval `InterPro` occurrences lacked `interpro_location_id`).

In Cycle 4 Stage 3, we executed the full re-resolve → finalize → promote pipeline for `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020`:

1. **Re-resolution (`scripts/ground_uniprot_examples.py resolve`)**:
   - **Command**:
     ```bash
     .venv/bin/python scripts/ground_uniprot_examples.py resolve \
       --candidates reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.candidates.jsonl \
       --out reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.resolved.jsonl \
       --protein-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.protein_registry.jsonl \
       --evidence-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.occurrence_evidence.jsonl \
       --membership-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.uniprot_memberships.jsonl \
       --sifts-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.sifts_mappings.jsonl \
       --residue-frame data/raw/align_cache/residue_frame.json \
       --interpro-frame data/raw/align_cache/interpro_frame.json \
       --interpro-grouped-frame data/raw/align_cache/interpro_grouped_locations.json \
       --fetch-receipt reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.uniprot_fetch_receipt.json \
       --validate-evidence
     ```
   - Re-resolved all `970` candidates (`970` `QUALIFIED`, `0` `REJECTED`) across `542` `CDD` trait-record groups against current on-disk record preimages, `data/raw/align_cache/interpro_frame.json`, `data/raw/align_cache/interpro_grouped_locations.json` (`362` grouped/multi-interval rows with `interpro_location_id`, `608` single-interval rows), and `human-ecoli-yeast-repair-cnp-020.uniprot_fetch_receipt.json` (`886` proteins in batch `protein_registry.jsonl`, `970` evidence entries in batch `occurrence_evidence.jsonl`, `0` `validate_grounding_evidence` findings, `0` `record_content_findings`, `0` `review_flags`).
2. **Review Partition Finalization (`scripts/finalize_uniprot_review_batch.py`)**:
   - Re-bound `resolution_digest` in `human-ecoli-yeast-repair-cnp-020.review-decisions.partition-001.jsonl` to the re-resolved rows and ran:
     ```bash
     .venv/bin/python scripts/finalize_uniprot_review_batch.py \
       --batch reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020 \
       --decisions reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.review-decisions.partition-001.jsonl \
       --apply
     ```
   - Finalized `970` decisions across `542` `CDD` groups (`542` `APPROVED`, `0` all rejected).
3. **Promotion (`scripts/ground_uniprot_examples.py promote --apply`)**:
   - **Command**:
     ```bash
     .venv/bin/python scripts/ground_uniprot_examples.py promote \
       --resolved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.resolved.jsonl \
       --approved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.approved.tsv \
       --fetch-request-plan reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.uniprot_fetch_plan.json \
       --fetch-receipt reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-cnp-020.uniprot_fetch_receipt.json \
       --apply
     ```
   - **Scope & Verification**:
     - `review coverage: CDD=542/25`
     - `542` approved `LOCALIZED` (`INTERPRO_MATCH`) rows across `542` unique `CDD` trait records (`115` already idempotently present on disk from `target-cnp020-000..002of008`, **`427` written `CDD` trait records** under `data/traits/sequence/domain/cdd/*.yaml`).
     - **`369` records transitioned from `0` `QUALIFIED` examples (`UNQUALIFIED` legacy examples only) to `1` `QUALIFIED` example** (`368` upgraded an existing legacy `SWISSPROT_PROFILE` example in-place to `QUALIFIED` with exact `InterPro 110.0` / `UniProt 2026_03` coordinates; `1` — `CDD:cd23767` `iq-isoleucine-glutamine-motif-containing-d-iqcd-iqcd-also-called-dynei-cd23767.yaml` — appended a first `QUALIFIED` example alongside `8` legacy examples).
     - **`53` records transitioned from `1` `QUALIFIED` example to `2` `QUALIFIED` examples** (all `53` upgraded an existing legacy `SWISSPROT_PROFILE` example on a different priority-taxon protein in-place to `QUALIFIED`).
     - **`5` records transitioned from `2` `QUALIFIED` examples to `3` `QUALIFIED` examples** (`CDD:cd22884` `atp-binding-cassette-abc-transporter-transmembrane-domain-tmd-1-of-mul-cd22884.yaml`, `CDD:cd22908` `atp-binding-cassette-domain-of-lipid-transporter-3-and-related-protein-cd22908.yaml`, `CDD:cd22914` `atp-binding-cassette-domain-1-of-cystic-fibrosis-transmembrane-conduct-cd22914.yaml`, `CDD:cd22931` `atp-binding-cassette-domain-of-mitochondrial-heavy-metal-transporter-a-cd22931.yaml`, and `CDD:cd23813` `first-beta-prism-domain-found-in-vibrio-cholerae-cytolysin-vcc-and-sim-cd23813.yaml`).
   - **Durable Registry Totals (Before → After)**:
     - `data/grounding/protein_registry.jsonl`: **13,293 → 13,532** proteins (**+239** new `ProteinReference` entries; `sha256=37b6d69d455279a0bebb7d68c1a581505e040d4083de3d46d80352f36ba254fc`)
     - `data/grounding/occurrence_evidence.jsonl.d/`: **22,635 → 23,062** evidence rows (**+427** new `GroundingEvidence` entries; `256` shards, `max_shard_bytes=70751`, `logical_sha256=5b1b033bf620c8f00a0f8f416114fc6a36dc3aacd98688557767fede9aa1f0b1`)
     - `data/grounding/qualified_record_bindings.jsonl.d/`: **22,635 → 23,062** transactional bindings (**+427** new record bindings; `256` shards, `max_shard_bytes=170234`, `logical_sha256=bcba094ed0d45166ff9c1ee12445440c9f9c20ce058e0878cf1862e1846a86ec`)

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

| Metric | Before Cycle 4 Stage 3 | After Cycle 4 Stage 3 | Delta |
|---|---:|---:|---:|
| Sibling Mechs scanned | 13 | 13 | 0 |
| Distinct proteins in inventory | 2,602 | 2,602 | 0 |
| **`HAS_QUALIFIED_PTM_EXAMPLE`** | **952** | **953** | **+1** (`UniProtKB:P50456` via `CDD:cd24074`) |
| **`LEGACY_EXAMPLES_ONLY`** | **654** | **653** | **-1** |
| `DISCOVERY_ONLY` | 996 | 996 | 0 |
| **`proteins_with_localized_qualified_traits`** | **339** | **346** | **+7** (`UniProtKB:P0A9B6`, `UniProtKB:P0AF20`, `UniProtKB:P11978`, `UniProtKB:P45425`, `UniProtKB:P50456`, `UniProtKB:P77570`, `UniProtKB:P77580`; plus 4 proteins that already had localized qualified traits gained additional localized `CDD` traits: `UniProtKB:P0A9Q9`, `UniProtKB:P11446`, `UniProtKB:Q01217`, `UniProtKB:Q03579`) |
| `sibling_pair_statuses.QUALIFIED_ON_TRAIT` | 393 | 393 | 0 |
| `sibling_pair_statuses.LEGACY_ON_TRAIT` | 6 | 6 | 0 |
| `sibling_pair_statuses.ABSENT_FROM_TRAIT` | 272 | 272 | 0 |
| `sibling_pair_statuses.NOT_A_PTM_NAMESPACE` | 919 | 919 | 0 |
| `sibling_pair_statuses.TRAIT_NOT_IN_PTM` | 167 | 167 | 0 |
| Active sequences (`2026_03` + 5 `2026_02`) | 2,484 | 2,484 | 0 |
| Sequences with usable generic annotations | 2,419 | 2,419 | 0 |
| `protein_inventory.jsonl` `sha256` | `3a22e36eb5c96150f39e856d23aa0da6d0b9b051b2358c0ef73a136bd8ca4081` | `363a50ea3ee7c5c0cfecd561059d2676cd24725d598201e3fcd800989e9c455c` | updated |
| `protein_sequences.jsonl` `sha256` | `9e8c3255175dd9c5856c50ec028bf16b7ecad3bc46ab7789d478005471fb08fd` | `8f8d258ced134231ee894cd240f684fa3c485477610542e8c122249174787396` | updated |
