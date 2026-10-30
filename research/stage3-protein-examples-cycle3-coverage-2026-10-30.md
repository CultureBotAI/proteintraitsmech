# Cycle 3 Stage 3 (`protein_examples`) Coverage, Promotion, and Blocker Report — 2026-10-30

- **Run / Cycle / Stage**: `mech-goal-sequence-20261019`, Cycle 3, Stage 3 (`protein_examples`, `goal-13975`)
- **Base commit on `main`**: `7276814bdf3bed73569a202c5e2c4b404e43d8f1`
- **Governing skills**:
  - `.claude/skills/proteintraitsmech-evolve-workflow/SKILL.md`
  - `.claude/skills/ground-protein-example/SKILL.md`
  - `.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md`

---

## 1. Corpus-Wide and Mechanism-Graph (`causal_graphs`) Protein Example Audit

Across all **429,394** trait records in `data/traits/**/*.yaml` (`+17` records added in Cycle 3 Stage 1 PR `#1194`), **142,403** records carry `canonical_examples` (`420,158` total `canonical_examples` entries: **22,619** `QUALIFIED` examples on disk across **22,135** unique records and **22,635** durable `QualifiedRecordBinding` rows, plus **397,539** `UNQUALIFIED` legacy examples across **120,268** `UNQUALIFIED`-only records).

### 1.1 Corpus-Wide `QUALIFIED` Records and Bindings by `identifier` Prefix

| `identifier` Prefix | Records with `QUALIFIED` Examples on Disk | Durable `QualifiedRecordBinding` Rows | Cycle 3 Stage 3 Delta |
|---|---:|---:|---|
| `PANTHER` | 7,800 | 7,800 | — |
| `NCBIfam` | 3,157 | 3,157 | — |
| `InterPro` | 2,961 | 3,021 | — |
| `CDD` | 2,891 | 3,069 | — |
| **`PROSITE`** | **2,397** | **2,401** | **+317 records (`2,080 → 2,397`), +321 bindings (`2,080 → 2,401`)** |
| `HAMAP` | 1,574 | 1,574 | — |
| `Pfam` | 1,150 | 1,150 | — |
| `RHEA` | 93 | 101 | — |
| `GO` | 53 | 181 | — |
| `ComplexPortal` | 43 | 148 | — |
| `proteintraitsmech` | 16 | 33 | — |
| **Total** | **22,135** | **22,635** | **+317 records, +321 bindings** |

*(Note: 16 multi-interval/binding records share a `CanonicalProteinExample` across multiple `QualifiedRecordBinding` receipts, accounting for `22,619` on-disk `QUALIFIED` example objects across `22,635` durable binding rows.)*

### 1.2 Mechanism-Graph (`causal_graphs`) Protein Example Coverage (`39,649` Records)

Across all **429,394** trait records, **39,649** records contain native `causal_graphs` (`39,641` in Cycle 2 `+ 17` added in Cycle 3 Stage 1/2 `- 9` structural records whose non-conforming `causal_graphs` were removed in PR `#1202`).

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
| **`proteintraitsmech:*` classes** | `data/traits/{sequence,structure}/**/*.yaml` | 52 | 0 (0.0%) | 0 | 52 | General mechanism/site classes (`32` sequence feature leaf classes + `20` structural mechanism classes; `50` seeded by `scripts/seed_foundational_traits.py` + `2` by `scripts/seed_localstructuralfeature.py`) defined without a source-shipped UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **Total** | **`data/traits/**/*.yaml` with `causal_graphs`** | **39,649** | **12,685** | **93** | **26,964** | — |

### 1.3 Exact Inventory of the 52 `proteintraitsmech:*` Mechanism-Graph Classes Without `canonical_examples`

Following Cycle 3 Stage 1/2 (`+17` new `proteintraitsmech:*` mechanism-graph records in PRs `#1194` and `#1197`) and PR `#1202` (`-9` structural records whose non-conforming `causal_graphs` were removed: `ALLOSTERIC_REGULATORY_SITE`, `ALLOSTERIC_ACTIVATOR_SITE`, `ALLOSTERIC_INHIBITOR_SITE`, `ALLOSTERIC_CRYPTIC_POCKET`, `ALLOSTERIC_SUBUNIT_INTERFACE_SITE`, `CAVITY_SUBSTRATE_ACCESS_TUNNEL`, `CATALYTIC_RESIDUE`, `PROTEIN_BINDING_SITE`, `METAL_BINDING_SITE`), there are **52** on-disk `proteintraitsmech:*` records with `causal_graphs`:

1. **Sequence Feature Leaf Classes (32 records: 28 from Cycle 2 Stage 1 + 4 from Cycle 3 Stage 1)**:
   - `data/traits/sequence/initiator_methionine/` (5): `proteintraitsmech:INIT_METHIONINE_ACETYLATED`, `proteintraitsmech:INIT_METHIONINE_EXCISED`, `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME`, `proteintraitsmech:INIT_METHIONINE_N_DEGRON` (Cycle 3), `proteintraitsmech:INIT_METHIONINE_RETAINED`
   - `data/traits/sequence/low_complexity/` (2, Cycle 3): `proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION`, `proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK`
   - `data/traits/sequence/mature_chain/` (5): `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED` (Cycle 3), `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE`, `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED`, `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED`, `proteintraitsmech:MATURE_CHAIN_SECRETED`
   - `data/traits/sequence/nonstandard_residue/` (4): `proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE`, `proteintraitsmech:NONSTD_N_FORMYLMETHIONINE`, `proteintraitsmech:NONSTD_PYRROLYSINE`, `proteintraitsmech:NONSTD_SELENOCYSTEINE`
   - `data/traits/sequence/propeptide/` (5): `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL`, `proteintraitsmech:PROPEPTIDE_INTRAMOLECULAR_CHAPERONE`, `proteintraitsmech:PROPEPTIDE_PROHORMONE_DIBASIC`, `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION`, `proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION`
   - `data/traits/sequence/signal_peptide/` (5): `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPII`, `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPIII`, `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPI`, `proteintraitsmech:SIGNAL_PEPTIDE_TAT_SPII`
   - `data/traits/sequence/transit_peptide/` (6): `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST`, `proteintraitsmech:TRANSIT_PEPTIDE_CHLOROPLAST_STROMA`, `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME`, `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS`, `proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL`, `proteintraitsmech:TRANSIT_PEPTIDE_THYLAKOID_LUMEN`
2. **Structural Mechanism Classes (20 records: 7 retained from Cycles 1–2 + 13 from Cycle 3 Stage 1)**:
   - `data/traits/structure/allosteric_site/` (1, Cycle 3): `proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE`
   - `data/traits/structure/cavity/` (1): `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE`
   - `data/traits/structure/disulfide/` (6: 5 existing + 1 Cycle 3): `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH`, `proteintraitsmech:DISULFIDE_BOND`, `proteintraitsmech:DISULFIDE_CATALYTIC_CXXC` (Cycle 3), `proteintraitsmech:DISULFIDE_CYSTINE_KNOT`, `proteintraitsmech:DISULFIDE_INTERCHAIN`, `proteintraitsmech:DISULFIDE_INTRACHAIN`
   - `data/traits/structure/dynamics/` (5, Cycle 3): `proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY`, `proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP`, `proteintraitsmech:DYNAMICS_DOMAIN_HINGE`, `proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP`, `proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH`
   - `data/traits/structure/interface/` (1): `proteintraitsmech:INTERFACE`
   - `data/traits/structure/surface/` (6, Cycle 3): `proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH`, `proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH`, `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH`, `proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD`, `proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH`, `proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT`

Because `scripts/ground_uniprot_examples.py` requires source-shipped residue-interval tables in `data/raw/` (`residue_frame.json`, `interpro_frame.json`, `interpro_grouped_location.json`, or `mcsa_entries.json`) keyed by external source ID, `ground_uniprot_examples.py` does not emit candidate rows for `proteintraitsmech:*` IDs (`proteintraitsmech-infra-0002`).

---

## 2. Re-Resolution, Finalization, and Promotion of `repair-existing-local-review-065-2026-03-prosite`

In Cycle 2 Stage 6 (`proteintraitsmech-infra-0005`, `#1191`), `scripts/ground_uniprot_examples.py` `main()` was updated to prefer stem-prefixed `<batch>.protein_registry.jsonl` and `<batch>.occurrence_evidence.jsonl` siblings, and 14 historical pre-`interpro_location_id` localized batches (`cnp-017..020`, `cdd-042..050`, and `prosite-065`) were queued for re-resolution against current on-disk record preimages and `interpro_location_id` (`interpro_grouped_location`) digests.

In Cycle 3 Stage 3, we executed the full re-resolve → finalize → promote pipeline for `reports/uniprot-grounding/review-batches/repair-existing-local-review-065-2026-03-prosite`:

1. **Re-resolution (`scripts/ground_uniprot_examples.py resolve`)**:
   - Re-resolved all `966` candidates across `360` `PROSITE` trait-record groups against current on-disk record preimages, `data/raw/interpro/protein2ipr.dat.gz`, `data/raw/align_cache/interpro_grouped_location.json`, and `repair-existing-local-review-065-2026-03-prosite.uniprot_fetch_receipt.json` (`966` `QUALIFIED` resolved rows, `224` proteins in batch `protein_registry.jsonl`, `1,004` evidence entries in batch `occurrence_evidence.jsonl`).
2. **Review Partition Finalization (`scripts/finalize_uniprot_review_batch.py`)**:
   - Verified `0` `record_content_findings` and `0` `review_flags` across all `966` candidates (`360` groups).
   - Preserved the `343` reviewed `APPROVED` group selections whose candidate `source_evidence_id` matched current on-disk state (`22` already idempotently present on disk + `321` unpromoted `QUALIFIED` examples).
   - Reclassified the `17` groups whose target record and exact `protein_id` already had a `QUALIFIED` example on disk from an earlier pre-`interpro_location_id` promotion (`PS51525`, `PS51529`, `PS51530`, `PS51535`, `PS51536`, `PS51537`, `PS51539`, `PS51544`, `PS51547`, `PS51555`, `PS51565`, `PS51566`, `PS51568`, `PS51579`, `PS51583`, `PS51588`, `PS51590`) as `REJECTED` (`DEFER_ALREADY_SATISFIED` on the already-grounded protein; `DEFER_ALTERNATE_CANDIDATE` on alternates), eliminating the `conflict:different_qualified_trait_occurrence` preflight block.
3. **Promotion (`scripts/ground_uniprot_examples.py promote --apply`)**:
   - **Command**:
     ```bash
     .venv/bin/python scripts/ground_uniprot_examples.py promote \
       --resolved reports/uniprot-grounding/review-batches/repair-existing-local-review-065-2026-03-prosite.resolved.jsonl \
       --approved reports/uniprot-grounding/review-batches/repair-existing-local-review-065-2026-03-prosite.approved.tsv \
       --fetch-request-plan reports/uniprot-grounding/review-batches/repair-existing-local-review-065-2026-03-prosite.uniprot_fetch_plan.json \
       --fetch-receipt reports/uniprot-grounding/review-batches/repair-existing-local-review-065-2026-03-prosite.uniprot_fetch_receipt.json \
       --apply
     ```
     *(Verified that `_default_promote_sibling` from `#1191` automatically resolved the stem-prefixed `.protein_registry.jsonl` and `.occurrence_evidence.jsonl` siblings without explicit flags.)*
   - **Scope & Verification**:
     - `review coverage: PROSITE=966/25`
     - `343` approved `LOCALIZED` (`INTERPRO_MATCH`) rows across `343` unique `PROSITE` trait records (`22` already present on disk, **`321` written `PROSITE` trait records**: `318` `SEQ_PROFILE` under `data/traits/sequence/profile/*.yaml` and `3` `SEQ_MOTIF` under `data/traits/sequence/pattern/{agouti-1,chitosanase-46-80,nos}.yaml`).
     - **`317` records transitioned from `0` `QUALIFIED` examples (`UNQUALIFIED` legacy examples only) to `1` `QUALIFIED` example** (`316` upgraded an existing legacy `SWISSPROT_PROFILE` example in-place to `QUALIFIED` with exact `InterPro 110.0` / `UniProt 2026_03` coordinates: `313` in `profile/` + `3` in `pattern/`; `1` in `profile/` appended a first `QUALIFIED` example).
     - **`4` records in `data/traits/sequence/profile/` that already carried `1` `QUALIFIED` example on a different protein received a second priority-taxon `QUALIFIED` example** (`PROSITE:PS51551` `ephrin-rbd-2.yaml`, `PROSITE:PS51562` `rna-cap0-mt.yaml`, `PROSITE:PS51564` `sam-icmt.yaml`, `PROSITE:PS51559` `sam-rmt2.yaml`).
   - **Durable Registry Totals (Before → After)**:
     - `data/grounding/protein_registry.jsonl`: **13,208 → 13,293** proteins (**+85** new `ProteinReference` entries; `sha256=740d3e4e75247422c23b156bcc1a0ab4a05ed1a62ab3b36587a60a7a236ac0bf`)
     - `data/grounding/occurrence_evidence.jsonl.d/`: **22,314 → 22,635** evidence rows (**+321** new `GroundingEvidence` entries; `logical_sha256=da7bcfa558c075a8271e46bee18669797c9542d11323be42b27f72d7e53056a1`)
     - `data/grounding/qualified_record_bindings.jsonl.d/`: **22,314 → 22,635** transactional bindings (**+321** new record bindings; `logical_sha256=fecaf4c1635ec037fcf8bffc0a7cbc7514168f423fe7d1c65500edbbd441c487`)

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

| Metric | Before Cycle 3 Stage 3 | After Cycle 3 Stage 3 | Delta |
|---|---:|---:|---:|
| Sibling Mechs scanned | 13 | 13 | 0 |
| Distinct proteins in inventory | 2,602 | 2,602 | 0 |
| **`HAS_QUALIFIED_PTM_EXAMPLE`** | **949** | **952** | **+3** (`UniProtKB:P50135`, `UniProtKB:P64554`, `UniProtKB:Q14353`) |
| **`LEGACY_EXAMPLES_ONLY`** | **657** | **654** | **-3** |
| `DISCOVERY_ONLY` | 996 | 996 | 0 |
| **`proteins_with_localized_qualified_traits`** | **329** | **339** | **+10** |
| `sibling_pair_statuses.QUALIFIED_ON_TRAIT` | 393 | 393 | 0 |
| `sibling_pair_statuses.LEGACY_ON_TRAIT` | 6 | 6 | 0 |
| `sibling_pair_statuses.ABSENT_FROM_TRAIT` | 272 | 272 | 0 |
| `sibling_pair_statuses.NOT_A_PTM_NAMESPACE` | 919 | 919 | 0 |
| `sibling_pair_statuses.TRAIT_NOT_IN_PTM` | 167 | 167 | 0 |
| Active sequences (`2026_03` + 5 `2026_02`) | 2,484 | 2,484 | 0 |
| Sequences with usable generic annotations | 2,419 | 2,419 | 0 |
