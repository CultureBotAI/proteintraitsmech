# Cycle 2 Stage 3 (`protein_examples`) Coverage, Promotion, and Blocker Report — 2026-10-25

- **Run / Cycle / Stage**: `mech-goal-sequence-20261019`, Cycle 2, Stage 3 (`protein_examples`, `goal-9220`)
- **Base commit on `main`**: `2ed9b577701df23d0b2b2337fdd16194415d8e5f`
- **Governing skills**:
  - `.claude/skills/proteintraitsmech-evolve-workflow/SKILL.md`
  - `.claude/skills/ground-protein-example/SKILL.md`
  - `.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md`

---

## 1. Corpus-Wide Mechanism-Graph (`causal_graphs`) Protein Example Audit

Across all **429,377** trait records in `data/traits/**/*.yaml`, **39,641** records contain native `causal_graphs` (including the 28 new Cycle 2 Stage 1 sequence feature leaf records in `data/traits/sequence/modification/` and `data/traits/sequence/targeting_signal/` and their Cycle 2 Stage 2 mechanism graphs).

| Source / Cohort | Directory / Scope | Records with `causal_graphs` | Records with `canonical_examples` (`>= 1`) | Records with `0` `canonical_examples` | Qualification & Blocker Status |
|---|---|---:|---:|---:|---|
| **M-CSA** | `data/traits/structure/active_site/mcsa` | 1,003 | 1,003 (100.0%) | 0 | 265 grounded with `QUALIFIED` examples (`MCSA_RESIDUE_EXACT`, `LOCALIZED`); 738 carry legacy seeded examples (`732` blocked on `missing_protein_sequence` in `data/raw/align_cache/residue_frame.json`, `6` lacking source residue coordinates; tracked in `proteintraitsmech-infra-0002`). |
| **BioLiP** | `data/traits/structure/binding_site/biolip` | 5,572 | 5,572 (100.0%) | 0 | 100% carry source-derived PDB/UniProt canonical examples; general ligand-class records lack a UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **MetalPDB** | `data/traits/structure/metal_site/metalpdb` | 228 | 228 (100.0%) | 0 | 100% carry source-derived canonical examples; mononuclear/polynuclear site classes lack a UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **UNIPROT_FT_SEQ_*** | `data/traits/sequence/{modification,targeting_signal}/uniprot-seq_*.yaml` | 5 | 5 (100.0%) | 0 | All 5 intermediate classes (`UNIPROT_FT_SEQ_INIT_METHIONINE`, `UNIPROT_FT_SEQ_MATURE_CHAIN`, `UNIPROT_FT_SEQ_PROPEPTIDE`, `UNIPROT_FT_SEQ_SIGNAL_PEPTIDE`, `UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`) carry 15 curated canonical examples each. |
| **EC** | `data/traits/function/enzymatic_activity/ec` | 6,888 | 5,784 (84.0%) | 1,104 | 5,784 carry Swiss-Prot `DR` canonical examples from `data/raw/expasy/enzyme.dat`; 1,104 have no Swiss-Prot `DR` cross-references in `enzyme.dat`, and `EC` lacks a source-shipped residue-interval table for `QUALIFIED` promotion (`proteintraitsmech-infra-0002`). |
| **RHEA** | `data/traits/function/enzymatic_activity/rhea` | 18,558 | 93 (0.5%) | 18,465 | `WHOLE_PROTEIN` functional grounding via `UNIPROT_REST` requires cryptographically bound v2 `.uniprot_fetch_receipt.json` (with `ProteinReference.fragment` status) and `uniprot_memberships.jsonl` (`proteintraitsmech-infra-0001`, `proteintraitsmech-infra-0002`). |
| **ARO** | `data/traits/function/resistance/aro` | 7,342 | 0 (0.0%) | 7,342 | `data/raw/card/aro.json` stores antimicrobial-resistance reference sequences via NCBI protein/nucleotide accessions and CARD model IDs without a reviewed 1:1 Swiss-Prot accession + coordinate table (`proteintraitsmech-infra-0002`). |
| **GO (`GO:7770085`)** | `data/traits/function/localization/go/protocatechuate-3-4-dioxygenase-complex-go7770085.yaml` | 1 | 0 (0.0%) | 1 | `WHOLE_PROTEIN` functional grounding requires a receipt-locked v2 `UNIPROT_REST` membership batch (`proteintraitsmech-infra-0002`). |
| **`proteintraitsmech:*` classes** | `data/traits/{structure,sequence}/**/*.yaml` | 44 | 0 (0.0%) | 44 | General mechanism/site classes (`8` structural root/cavity classes, `8` Cycle 1 Stage 1 structural leaf classes, and `28` Cycle 2 Stage 1 sequence feature leaf classes) defined without a source-shipped UniProt residue-interval table in `data/raw/` (`proteintraitsmech-infra-0002`). |
| **Total** | **`data/traits/**/*.yaml` with `causal_graphs`** | **39,641** | **12,685** | **26,956** | — |

### 1.1 Exact Inventory of the 44 `proteintraitsmech:*` Mechanism-Graph Classes Without `canonical_examples`

1. **Foundational Structural & Cavity Classes (8 records)**:
   - `proteintraitsmech:CATALYTIC_RESIDUE` (`data/traits/structure/active_site/catalytic-residue.yaml`)
   - `proteintraitsmech:ALLOSTERIC_REGULATORY_SITE` (`data/traits/structure/allosteric_site/allosteric-regulatory-site.yaml`)
   - `proteintraitsmech:PROTEIN_BINDING_SITE` (`data/traits/structure/binding_site/protein-binding-site.yaml`)
   - `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE` (`data/traits/structure/cavity_channel_pore/selectivity-filter-pore-subsite.yaml`)
   - `proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL` (`data/traits/structure/cavity_channel_pore/substrate-access-tunnel.yaml`)
   - `proteintraitsmech:DISULFIDE_BOND` (`data/traits/structure/disulfide_bond/disulfide-bond.yaml`)
   - `proteintraitsmech:INTERFACE` (`data/traits/structure/interaction_interface/protein-interaction-interface.yaml`)
   - `proteintraitsmech:METAL_BINDING_SITE` (`data/traits/structure/metal_site/metal-binding-site.yaml`)
2. **Cycle 1 Stage 1 Local Structural Leaf Classes (8 records)**:
   - `proteintraitsmech:ALLOSTERIC_ACTIVATOR_SITE`, `proteintraitsmech:ALLOSTERIC_CRYPTIC_POCKET`, `proteintraitsmech:ALLOSTERIC_INHIBITOR_SITE`, `proteintraitsmech:ALLOSTERIC_SUBUNIT_INTERFACE_SITE` (`data/traits/structure/allosteric_site/`)
   - `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH`, `proteintraitsmech:DISULFIDE_CYSTINE_KNOT`, `proteintraitsmech:DISULFIDE_INTERCHAIN`, `proteintraitsmech:DISULFIDE_INTRACHAIN` (`data/traits/structure/disulfide_bond/`)
3. **Cycle 2 Stage 1 Sequence Feature Leaf Classes (28 records)**:
   - Initiator methionine (4): `proteintraitsmech:INIT_METHIONINE_COTRANSLATIONAL_MAP_CLEAVAGE`, `INIT_METHIONINE_FORMYLMETHIONINE_PDF_MAP_CLEAVAGE`, `INIT_METHIONINE_N_ACETYLATION_COUPLED_CLEAVAGE`, `INIT_METHIONINE_N_DEGRON_EXPOSURE` (`data/traits/sequence/modification/`)
   - Mature chain (4): `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_EXCISION`, `MATURE_CHAIN_ENDOPLASMIC_RETICULUM_PROHORMONE`, `MATURE_CHAIN_SECRETED_ECTODOMAIN_SHED`, `MATURE_CHAIN_VIRAL_POLYPROTEIN_CLEAVAGE_PRODUCT` (`data/traits/sequence/modification/`)
   - Non-standard residue (4): `proteintraitsmech:NONSTD_HYPUSINE`, `NONSTD_PYRROLYSINE`, `NONSTD_SELENOCYSTEINE`, `NONSTD_THIOGLYCINE` (`data/traits/sequence/modification/`)
   - Propeptide (5): `proteintraitsmech:PROPEPTIDE_AUTOINHIBITORY_METALLOPROTEASE_CYSTEINE_SWITCH`, `PROPEPTIDE_CARBOXYPEPTIDASE_ACTIVATION_SEGMENT`, `PROPEPTIDE_INTRAMOLECULAR_CHAPERONE`, `PROPEPTIDE_PROHORMONE_CONVERTASE_CLEAVED`, `PROPEPTIDE_ZYMOGEN_ACTIVATION_PEPTIDE` (`data/traits/sequence/modification/`)
   - Signal peptide (5): `proteintraitsmech:SIGNAL_PEPTIDE_ARCHAEAL_FLAGELLIN_TYPE_IV_PILIN`, `SIGNAL_PEPTIDE_BACTERIAL_LIPOPROTEIN_SPII`, `SIGNAL_PEPTIDE_EUKARYOTIC_SEC61`, `SIGNAL_PEPTIDE_GRAM_NEGATIVE_SEC_SPI`, `SIGNAL_PEPTIDE_TWIN_ARGININE_TRANSLOCATION_TAT` (`data/traits/sequence/targeting_signal/`)
   - Transit peptide (6): `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST_BIPARTITE`, `TRANSIT_PEPTIDE_CHLOROPLAST_STROMA_CPTP`, `TRANSIT_PEPTIDE_CHLOROPLAST_THYLAKOID_LUMEN_BIPARTITE`, `TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME`, `TRANSIT_PEPTIDE_MITOCHONDRIAL_INTERMEMBRANE_SPACE_BIPARTITE`, `TRANSIT_PEPTIDE_MITOCHONDRIAL_MATRIX_MTS` (`data/traits/sequence/targeting_signal/`)

All 44 `proteintraitsmech:*` records represent class-level structural or sequence-feature mechanism definitions (seeded by `scripts/seed_foundational_traits.py`, `scripts/seed_localstructuralfeature.py`, and `scripts/seed_uniprot_peptide_classes.py`). Because `scripts/ground_uniprot_examples.py` requires source-shipped residue-interval tables in `data/raw/` (`residue_frame.json`, `interpro_frame.json`, `interpro_grouped_location.json`, or `mcsa_entries.json`) keyed by external source ID, `ground_uniprot_examples.py` does not emit candidate rows for `proteintraitsmech:*` IDs (`proteintraitsmech-infra-0002`).

---

## 2. Promotion of Reviewed Grounding Batch `human-ecoli-yeast-repair-mixed-039`

We audited all **235** `.approved.tsv` / `.review-decisions.jsonl` review batches under `reports/uniprot-grounding/review-batches/` against the **21,343** already-promoted `candidate_id`s in `data/grounding/qualified_record_bindings.jsonl.d/`:

- **Promoted in Cycle 2 Stage 3**:
  - **Batch**: `reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039`
  - **Command**:
    ```bash
    .venv/bin/python scripts/ground_uniprot_examples.py promote \
      --resolved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.resolved.jsonl \
      --approved reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.approved.tsv \
      --protein-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.protein_registry.jsonl \
      --evidence-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.occurrence_evidence.jsonl \
      --membership-registry reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.uniprot_memberships.jsonl \
      --fetch-request-plan reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.uniprot_fetch_plan.json \
      --fetch-receipt reports/uniprot-grounding/review-batches/human-ecoli-yeast-repair-mixed-039.uniprot_fetch_receipt.json \
      --apply
    ```
  - **Scope & Verification**:
    - `review coverage: InterPro=1000/25`
    - `972` approved `LOCALIZED` (`INTERPRO_MATCH`) candidate rows across `972` unique `InterPro` trait records (`964` `SEQ_DOMAIN`, `5` `SEQ_CONSERVATION`, `3` `SEQ_REPEAT`; `1` `SEQ_DOMAIN` already present on disk, **`971` newly written trait records**: `963` `SEQ_DOMAIN`, `5` `SEQ_CONSERVATION`, `3` `SEQ_REPEAT`).
    - All **971** written records previously had **`0` `QUALIFIED` canonical examples** on disk (carrying only legacy `SWISSPROT_PROFILE` examples); `951` upgraded the existing `SWISSPROT_PROFILE` example in-place to `QUALIFIED` with exact `InterPro 110.0` / `UniProt 2026_03` coordinates, and `20` appended a priority-taxon (`Homo sapiens` / `Saccharomyces cerevisiae`) `QUALIFIED` example alongside the existing legacy example.
    - Zero `record_content_findings` and zero `review_flags` across all 971 promoted rows; DUF and taxon-scoped records (`InterPro:IPR056044` `UniProtKB:P34263` *C. elegans* `B0303.14`, `InterPro:IPR055783..055785` `UniProtKB:O31978` *B. subtilis* `YomG`, `InterPro:IPR057262`/`IPR057377` `UniProtKB:Q57968` *M. jannaschii* `MJ0548`) match the exact protein and organism named in their definitions.
  - **Durable Registry Totals (Before → After)**:
    - `data/grounding/protein_registry.jsonl`: **12,925 → 13,208** proteins (**+283** new `ProteinReference` entries)
    - `data/grounding/occurrence_evidence.jsonl.d/`: **21,343 → 22,314** evidence rows (**+971** new `GroundingEvidence` entries)
    - `data/grounding/qualified_record_bindings.jsonl.d/`: **21,343 → 22,314** transactional bindings (**+971** new record bindings)

### 2.1 Disposition of Other Unpromoted Review Batches in `reports/uniprot-grounding/review-batches/`

1. **`human-ecoli-yeast-repair-mixed-041` (Not promoted — superseded by `cnp-020`)**:
   - Contains `151` approved `InterPro` candidates, of which `127` are already in `qualified_record_bindings.jsonl.d/` and `7` match the exact `protein_id` already `QUALIFIED` on disk. The remaining `17` rows in `041` (`IPR063456`, `IPR063504`, `IPR063556..063558`, `IPR063601`, `IPR063614`, `IPR063624`, `IPR063694`, `IPR063903`, `IPR063911`, `IPR063973`, `IPR064028`, `IPR064050`, `IPR064061`, `IPR064066`, `IPR064082`) were already repaired and promoted with `Homo sapiens` `QUALIFIED` examples by `human-ecoli-yeast-repair-cnp-020` (e.g., human `NIPBL` `UniProtKB:Q6KC79` on `IPR063456`, human `APOB` `UniProtKB:P04114` on `IPR063504`), whereas `041` staged the older mouse (`Mus musculus`) orthologs (`UniProtKB:Q6KCD5`, `UniProtKB:E9Q414`). Promoting `041` would only append redundant mouse examples onto records that already have `QUALIFIED` human examples.
2. **Legacy v1-Receipt `WHOLE_PROTEIN` Batches (`missing:uniprot_fragment_status_for_whole_protein`, tracked in `proteintraitsmech-infra-0001`)**:
   - `cross-mech-complex-20261013` (`33` approved `ComplexPortal` subunit rows across `22` mechanism-graph records), `ready-local-review-077-2026-03-panther` (`967` rows), `repair-existing-local-review-177-2026-03-topup` (`428` rows), `repair-existing-local-review-179-2026-03-topup` (`14` rows), `human-ecoli-yeast-repair-mixed-038` (`58` rows), `human-ecoli-yeast-repair-mixed-040` (`424` rows), `human-ecoli-yeast-repair-mixed-042` (`115` rows), `human-ecoli-yeast-repair-panther-021..037`, `human-ecoli-yeast-complete-panther-001..005`, `human-ecoli-yeast-complete-go-008..021`, `human-ecoli-yeast-complete-rhea-035..054`, and `human-ecoli-yeast-complete-complexportal-006` were resolved under v1 UniProt fetch receipts (`uniprot_fragment: null`) and fail closed at preflight until re-fetched under v2 receipts with `ProteinReference.fragment`.
3. **Partially Superseded `LOCALIZED` Batches (`conflict:different_qualified_trait_occurrence` / `stale:record_changed_since_resolve`, tracked in `proteintraitsmech-infra-0005`)**:
   - `human-ecoli-yeast-repair-cnp-017..020`, `repair-existing-local-review-042..050-2026-03-cdd`, and `repair-existing-local-review-065-2026-03-prosite` contain unpromoted `LOCALIZED` candidates alongside rows whose target records were subsequently modified by later promotions, requiring re-resolution against current on-disk record preimages.

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

| Metric | Before Cycle 2 Stage 3 | After Cycle 2 Stage 3 | Delta |
|---|---:|---:|---:|
| Sibling Mechs scanned | 13 | 13 | 0 |
| Distinct proteins in inventory | 2,602 | 2,602 | 0 |
| **`HAS_QUALIFIED_PTM_EXAMPLE`** | **943** | **949** | **+6** |
| **`LEGACY_EXAMPLES_ONLY`** | **663** | **657** | **-6** |
| `DISCOVERY_ONLY` | 996 | 996 | 0 |
| **`proteins_with_localized_qualified_traits`** | **316** | **329** | **+13** |
| Active sequences (`2026_03` + 5 `2026_02`) | 2,484 | 2,484 | 0 |
| Sequences with usable generic annotations | 2,419 | 2,419 | 0 |
