# Cycle 3 Stage 1 (`add_records`) — Bounded Frontier Search & Class-Level Trait Addition Report

- **Run**: `mech-goal-sequence-20261019`
- **Cycle / Stage**: Cycle 3, Stage 1 (`add_records`, `goal-6114`)
- **Date**: 2026-10-26
- **Skill**: `.claude/skills/add-record/SKILL.md` (`add-record`)
- **Seeder**: `scripts/seed_foundational_traits.py` (`101` foundational trait classes across `18` categories; `17` added in Cycle 3 Stage 1)

---

## 1. Bounded Frontier Definition & Search Protocol

Following `.claude/skills/add-record/SKILL.md`, `.claude/skills/manage-identifiers/SKILL.md`, and `.claude/skills/id-label-correspondence/SKILL.md`, candidate evaluation was performed across three bounded frontier axes in two sequential passes:

1. **Schema Category & Hierarchy Coverage (`ProteinTraitCategoryEnum` & foundational `proteintraitsmech:*` subtrees)**:
   - All `68` enum values in `src/proteintraitsmech/schema/proteintraitsmech.yaml` (`63` populated on disk across `data/traits/**/*.yaml`, `5` catch-all/upper-level tokens `MIXED_OTHER`, `OTHER`, `SEQ_OTHER`, `STRUCT_OTHER`, `UPPER`) were inventoried against `data/traits/**/*.yaml` (`429,377` records at Cycle 3 Stage 1 start) to identify structural categories with `0–1` `proteintraitsmech:*` foundational records and sparse (`4–5`-record) foundational categories lacking canonical sequence/structural subclasses.
2. **Cross-Mech `TRAIT_NOT_IN_PTM` Inventory (`data/cross_mech/protein_inventory.jsonl`)**:
   - All 352 `TRAIT_NOT_IN_PTM` pairs (`133` distinct external CURIEs) from sibling Mech repositories were re-audited against the corpus and seeder exclusion rules (`scripts/seed_interpro.py`, `scripts/seed_reactome.py`, `scripts/seed_go.py`).
3. **Catalogued Upstream Data Sources (`download.yaml`)**:
   - All 51 source entries in `download.yaml` (`27` seeded, `24` candidate/reference/mapping) were audited against `data/raw/` availability and class-level vs. per-protein boundary rules.

---

## 2. Pass 1 Search Results & Admissible Class-Level Candidates

### 2.1 Sparse Foundational Categories Identified in Pass 1

At the start of Cycle 3 Stage 1 (`429,377` total records), Pass 1 identified **2 structural categories with `0–1` `proteintraitsmech:*` foundational records** (`STRUCT_SURFACE` with `0` `proteintraitsmech:*` records alongside `16` PATO quality terms; `STRUCT_DYNAMICS` with `1` `proteintraitsmech:ELBOW` record alongside `17` PATO quality terms), **3 sparse `4–5`-record categories missing canonical sequence/structural subclasses** (`SEQ_LOW_COMPLEXITY`, `STRUCT_ALLOSTERIC_SITE`, `STRUCT_DISULFIDE`), and **2 `5`-record sequence processing categories missing canonical degradation/autocatalytic subclasses** (`SEQ_INITIATOR_METHIONINE`, `SEQ_MATURE_CHAIN`):

| Category | Pass 1 Total (`proteintraitsmech:*`) | Gap Identified in Pass 1 | Admissible New Class-Level Records Added | Pass 2 Total (`proteintraitsmech:*`) |
| --- | ---: | --- | ---: | ---: |
| `STRUCT_SURFACE` | 16 (0) | Contained `16` generic `PATO` quality records (`pato/*.yaml`) and `0` `proteintraitsmech:*` foundational surface feature classes; lacked electrostatic patch, basic cationic patch, acidic anionic patch, hydrophobic patch, glycan steric shield, and membrane-interfacial aromatic belt classes. | +6 | 22 (6) |
| `STRUCT_DYNAMICS` | 18 (1) | Contained `17` `PATO` quality records (`pato/*.yaml`) and only `1` `proteintraitsmech:*` structural dynamics class (`proteintraitsmech:ELBOW`); lacked interdomain hinge, active-site catalytic gating lid, metamorphic fold-switching, 3D domain-swapping hinge, and allosteric dynamic coupling network classes. | +5 | 23 (6) |
| `SEQ_LOW_COMPLEXITY` | 4 (4) | Covered `LOWCOMP_REGION`, `LOWCOMP_HOMOREPEAT_TRACT`, `LOWCOMP_CRYPTIC_REPEAT_REGION`, and `LOWCOMP_PRION_LIKE_DOMAIN`, but lacked polyampholytic mixed-charge block LCRs (`E/D` + `K/R` blocks) and nucleoporin `FG`-repeat hydrogel LCRs. | +2 | 6 (6) |
| `STRUCT_ALLOSTERIC_SITE` | 5 (5) | Covered `ALLOSTERIC_REGULATORY_SITE`, `ALLOSTERIC_ACTIVATOR_SITE`, `ALLOSTERIC_INHIBITOR_SITE`, `ALLOSTERIC_CRYPTIC_POCKET`, and `ALLOSTERIC_SUBUNIT_INTERFACE_SITE`, but lacked covalent allosteric regulatory sites (nucleophilic allosteric cysteine/lysine pockets). | +1 | 6 (6) |
| `STRUCT_DISULFIDE` | 5 (5) | Covered `UNIPROT_FT_STRUCT_DISULFIDE`, `DISULFIDE_INTRACHAIN_STABILIZING`, `DISULFIDE_INTERCHAIN_COVALENT`, `DISULFIDE_ALLOSTERIC_REDOX_SWITCH`, and `DISULFIDE_CYSTINE_KNOT`, but lacked catalytic `CXXC` dithiol-disulfide active-site motifs (thioredoxin/PDI/DsbA superfamily). | +1 | 6 (6) |
| `SEQ_INITIATOR_METHIONINE` | 5 (5) | Covered `UNIPROT_FT_SEQ_INITIATOR_METHIONINE`, `INIT_METHIONINE_CLEAVED`, `INIT_METHIONINE_RETAINED`, `INIT_METHIONINE_FORMYLATED`, and `INIT_METHIONINE_N_ACETYLATED`, but lacked initiator-methionine `Ac/N-degron` and `Arg/N-degron` ubiquitin-proteasome recognition sites. | +1 | 6 (6) |
| `SEQ_MATURE_CHAIN` | 5 (5) | Covered `UNIPROT_FT_SEQ_MATURE_CHAIN`, `MATURE_CHAIN_ZYMOGEN_CLEAVED`, `MATURE_CHAIN_POLYPROTEIN_CLEAVED`, `MATURE_CHAIN_INTEIN_SPLICED`, and `MATURE_CHAIN_SHED_ECTODOMAIN`, but lacked autocatalytically cleaved mature chains (`Ntn`-hydrolase/pyruvoyl/autoproteolytic precursors). | +1 | 6 (6) |

### 2.2 Candidate Deduplication & Rejected Overlap Candidates (Pass 1)

Before admitting candidates, every proposed ontology anchor and mechanism was checked against the existing `429,377`-record corpus for exact or semantic equivalence:

- **Rejected as duplicate (`MOD:00125` hypusine)**: Already seeded under `SEQ_PTM_SITE` as `InterPro:IPR002093` (`data/traits/sequence/ptm_site/interpro/initiation-factor-eif-5a-hypusine-site-ipr002093.yaml`) and `PROSITE:PS00303`.
- **Rejected as duplicate (`MOD:01168` dehydroalanine / `MOD:01703` dehydrobutyrine)**: Already seeded under `SEQ_CROSSLINK` as `proteintraitsmech:CROSSLINK_LANTHIONINE_THIOETHER` (`data/traits/sequence/crosslink/lanthionine-methyllanthionine-thioether-crosslink-site.yaml`).
- **Rejected as duplicate (`IDPO:0000011` disorder-to-order / `IDPO:0000014` order-to-disorder)**: Already seeded under `SEQ_DISORDER` as `proteintraitsmech:DISORDER_TO_ORDER_TRANSITION` and `proteintraitsmech:ORDER_TO_DISORDER_TRANSITION` (`data/traits/sequence/disorder/`).

### 2.3 Summary of 17 New Class-Level `ProteinTraitRecord` Files Added

All 17 new records (plus two new runnable `MethodSpec` definitions: `M_FREESASA` `PMID:26973785` and `M_PRODY_ANM` `PMID:21471012`) were added to `scripts/seed_foundational_traits.py` and emitted via `record_io.write_record(..., validate=True)` with grounded ontology terms (`SO`, `GO`, `MOD`, `PATO`, `CHEBI`), primary literature provenance (`PMID` + verbatim abstract snippet), runnable `detection_methods` CLI recipes, and verified 4-node/3-edge `causal_graphs` on all 4 mechanism-bearing site/cleavage records:

1. **`SEQ_LOW_COMPLEXITY` (`data/traits/sequence/low_complexity/`)**:
   - `proteintraitsmech:LOWCOMP_POLYAMPHOLYTIC_CHARGE_BLOCK` (`polyampholytic-mixed-charge-block-low-complexity-region.yaml`) — parent `proteintraitsmech:LOWCOMP_REGION`; `SO:0001068` low-complexity region enriched in oppositely charged `E/D` and `K/R` blocks whose charge-patterning parameter $\kappa$ governs coil-to-globule collapse and nuclear speckle condensation (`PMID:23901099`, method `M_FLPS` `PMID:28851299`).
   - `proteintraitsmech:LOWCOMP_FG_NUCLEOPORIN_REPEAT_REGION` (`phenylalanine-glycine-fg-repeat-low-complexity-region.yaml`) — parent `proteintraitsmech:LOWCOMP_REGION`; `SO:0001068` `FG`/`FXFG`/`GLFG` cohesive low-complexity region forming the selective nuclear pore permeability barrier (`PMID:17082456`, method `M_FLPS` `PMID:28851299`).
2. **`SEQ_INITIATOR_METHIONINE` (`data/traits/sequence/initiator_methionine/`)**:
   - `proteintraitsmech:INIT_METHIONINE_N_DEGRON` (`initiator-methionine-ac-n-degron-and-arg-n-degron-site.yaml`) — parent `proteintraitsmech:INIT_METHIONINE_RETAINED`; `SO:0000419` / `MOD:00058` N-terminal degradation determinant recognized by Doa10/March6 (`Ac/N-degron`) or UBR-box E3 ubiquitin ligases (`Arg/N-degron`) (`PMID:20110468`, method `M_UNIPROT_ANNOT` `PMID:39552041`, 4-node/3-edge `causal_graphs`: `MOD:00058 -> GO:0004842 -> GO:0071596 -> GO:0043161`).
3. **`SEQ_MATURE_CHAIN` (`data/traits/sequence/mature_chain/`)**:
   - `proteintraitsmech:MATURE_CHAIN_AUTOCATALYTIC_CLEAVED` (`autocatalytically-cleaved-mature-polypeptide-chain.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN`; `SO:0000419` mature polypeptide chain generated by intramolecular N-to-O/N-to-S acyl shift and backbone cleavage in `Ntn`-hydrolase/pyruvoyl precursors (`PMID:7477383`, method `M_UNIPROT_ANNOT` `PMID:39552041`, 4-node/3-edge `causal_graphs`: `GO:0006508 -> SO:0000419 -> GO:0051604 -> GO:0003824`).
4. **`STRUCT_ALLOSTERIC_SITE` (`data/traits/structure/allosteric_site/`)**:
   - `proteintraitsmech:ALLOSTERIC_COVALENT_REGULATORY_SITE` (`covalent-allosteric-regulatory-site.yaml`) — parent `proteintraitsmech:ALLOSTERIC_REGULATORY_SITE`; nucleophilic non-orthosteric cysteine/lysine pocket where covalent modifier adduct formation remodels the active site (`PMID:24256730`, method `M_FPOCKET` `PMID:26950260`, 4-node/3-edge `causal_graphs`: `CHEBI:24431 -> GO:0036094`, `CHEBI:29950 -> GO:0036094 -> GO:0030234`).
5. **`STRUCT_DISULFIDE` (`data/traits/structure/disulfide/`)**:
   - `proteintraitsmech:DISULFIDE_CATALYTIC_CXXC` (`catalytic-cxxc-dithiol-disulfide-active-site-motif.yaml`) — parent `proteintraitsmech:DISULFIDE_ALLOSTERIC_REDOX_SWITCH`; `MOD:00034` / `GO:0015035` redox-active `CXXC` motif cycling between dithiol and disulfide states to catalyze thiol-disulfide exchange (`PMID:9403310`, method `M_DSSP_SSBOND` `PMID:25352545`, 4-node/3-edge `causal_graphs`: `CHEBI:29950 -> GO:0015035 -> MOD:00034` and `GO:0015035 -> GO:0045454`).
6. **`STRUCT_SURFACE` (`data/traits/structure/surface/`)**:
   - `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH` (`surface-electrostatic-patch.yaml`) — parent `PATO:0002193` (`electric charge`); contiguous cluster of solvent-accessible charged residues generating a localized electrostatic potential lobe (`PMID:7761829`, method `M_APBS` `PMID:11517324`).
   - `proteintraitsmech:SURFACE_BASIC_CATIONIC_PATCH` (`positively-charged-cationic-surface-patch.yaml`) — parents `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH` and `PATO:0002195` (`positively charged`); `Lys`/`Arg`/`His`-enriched positive electrostatic patch recognizing polyanionic DNA/RNA or phosphoinositide membranes (`PMID:14654279`, method `M_APBS` `PMID:11517324`).
   - `proteintraitsmech:SURFACE_ACIDIC_ANIONIC_PATCH` (`negatively-charged-acidic-surface-patch.yaml`) — parents `proteintraitsmech:SURFACE_ELECTROSTATIC_PATCH` and `PATO:0002196` (`negatively charged`); `Asp`/`Glu`-enriched negative electrostatic patch mediating cationic partner docking and halophilic hydration (`PMID:8638017`, method `M_APBS` `PMID:11517324`).
   - `proteintraitsmech:SURFACE_HYDROPHOBIC_PATCH` (`solvent-exposed-hydrophobic-surface-patch.yaml`) — parent `PATO:0001884` (`hydrophobic`); non-polar solvent-exposed patch driving interface desolvation and aggregation propensity (`PMID:19571001`, method `M_FREESASA` `PMID:26973785`).
   - `proteintraitsmech:SURFACE_GLYCOSYLATION_SHIELD` (`surface-glycan-steric-shield.yaml`) — root class; dense array of surface-exposed N-/O-linked glycans (`MOD:00006`) sterically masking underlying polypeptide epitopes (`PMID:12646921`, method `M_FREESASA` `PMID:26973785`).
   - `proteintraitsmech:SURFACE_MEMBRANE_ANCHORING_AROMATIC_BELT` (`interfacial-aromatic-tryptophan-tyrosine-membrane-belt.yaml`) — root class; circumferential belt of surface-exposed `Trp`/`Tyr` side chains at the lipid headgroup-water interface (`PMID:9778346`, method `M_FREESASA` `PMID:26973785`).
7. **`STRUCT_DYNAMICS` (`data/traits/structure/dynamics/`)**:
   - `proteintraitsmech:DYNAMICS_DOMAIN_HINGE` (`interdomain-hinge-bending-region.yaml`) — parents `proteintraitsmech:ELBOW` and `PATO:0001543` (`flexibility`); flexible interdomain linker pivot mediating rigid-body domain closure (`PMID:8204609`, method `M_PRODY_ANM` `PMID:21471012`).
   - `proteintraitsmech:DYNAMICS_CATALYTIC_GATING_LOOP` (`active-site-catalytic-gating-lid-loop.yaml`) — parent `PATO:0001543` (`flexibility`); mobile active-site lid/omega loop cycling between open substrate-entry and closed solvent-excluded catalytic states (`PMID:30703322`, method `M_PRODY_ANM` `PMID:21471012`).
   - `proteintraitsmech:DYNAMICS_METAMORPHIC_FOLD_SWITCH` (`metamorphic-fold-switching-region.yaml`) — parent `PATO:0001543` (`flexibility`); polypeptide region reversibly remodeling secondary structure and tertiary packing between distinct folds (`PMID:18583598`, method `M_PRODY_ANM` `PMID:21471012`).
   - `proteintraitsmech:DYNAMICS_DOMAIN_SWAPPING_HINGE_LOOP` (`3d-domain-swapping-hinge-loop.yaml`) — parents `proteintraitsmech:ELBOW` and `PATO:0001543` (`flexibility`); hinge loop transitioning from an intramolecular turn to an extended intermolecular linker during 3D domain swapping (`PMID:8580836`, method `M_PRODY_ANM` `PMID:21471012`).
   - `proteintraitsmech:DYNAMICS_ALLOSTERIC_ENSEMBLE_TRANSMISSION_PATHWAY` (`allosteric-dynamic-coupling-residue-network.yaml`) — parent `PATO:0001543` (`flexibility`); dynamically coupled residue network transmitting allosteric signals via conformational population shift (`PMID:19351898`, method `M_PRODY_ANM` `PMID:21471012`).

---

## 3. Pass 2 Repeated Frontier Search & Exhaustion Verification

After seeding the 17 new records (`429,394` total corpus records across `data/traits/**/*.yaml`), the bounded frontier search was repeated across all three axes:

1. **`ProteinTraitCategoryEnum` & Foundational Hierarchy Audit (Pass 2)**:
   - **63 of 68** `ProteinTraitCategoryEnum` categories are populated on disk (`429,394` total records); the remaining 5 enum values (`MIXED_OTHER`, `OTHER`, `SEQ_OTHER`, `STRUCT_OTHER`, `UPPER`) are schema catch-all/upper-level tokens with no class-level records by design (`scripts/audit_schema.py` reports `OK: schema is internally coherent`).
   - All **18 categories** seeded by `scripts/seed_foundational_traits.py` (`101` foundational trait records total; `44` with `causal_graphs`) now have at least `4` `proteintraitsmech:*` records (`>= 5` `proteintraitsmech:*` records in 16 of 18 categories), and both `STRUCT_SURFACE` (`22` total / `6` `proteintraitsmech:*`) and `STRUCT_DYNAMICS` (`23` total / `6` `proteintraitsmech:*`) now have complete foundational class hierarchies anchored to `PATO` and `proteintraitsmech:ELBOW`.
2. **Cross-Mech `TRAIT_NOT_IN_PTM` Audit (Pass 2)**:
   - Re-verified all 352 `TRAIT_NOT_IN_PTM` pairs (`133` distinct external IDs) in `data/cross_mech/protein_inventory.jsonl`: `124` `InterPro` `Family` entries (`294` pairs), `8` *M. tuberculosis* `Reactome:R-MTU-*` pathway entries (`57` pairs), and `1` obsolete GO term (`GO:0004085`, already merged into `GO:0016937` `alt_id`). `0` unseeded admissible class-level traits remain.
3. **Validation Summary**:
   - `scripts/validate_strict.py`: `0 errors` across all 7 modified trait category directories (`75` files scanned = `6 + 6 + 6 + 6 + 6 + 22 + 23`).
   - `scripts/audit_causal_graphs.py --strict`: `0 errors, 0 warnings` across all modified mechanism-bearing directories (`24` records, `24` graphs, `98` grounded nodes `100.0%`, `74` snippet-cited edges `100.0%`).
   - `scripts/build_methods.py`: `OK — 109 methods (37 sources, 66 categories)`.
   - `scripts/validate_internal_id_labels.py`: `OK: internal id-label mismatch count and identity match the baseline` (`429,394` records examined).
   - `scripts/audit_writers.py`: `OK` (`0` rogue writers).
   - `pytest tests/test_foundational_traits.py tests/test_methods_recipes.py tests/test_record_io.py`: `145 passed, 2 skipped`.

---

## 4. Preserved Unresolved Candidates & Search Limits

| Candidate / Frontier Slice | Reason Excluded or Deferred | Tracking |
| --- | --- | --- |
| `MOD:00125` (hypusine), `MOD:01168` (dehydroalanine), `MOD:01703` (dehydrobutyrine), `IDPO:0000011` (disorder-to-order), `IDPO:0000014` (order-to-disorder) | Rejected in Pass 1 deduplication because equivalent class-level traits already exist (`InterPro:IPR002093`/`PROSITE:PS00303`, `proteintraitsmech:CROSSLINK_LANTHIONINE_THIOETHER`, `proteintraitsmech:DISORDER_TO_ORDER_TRANSITION`, `proteintraitsmech:ORDER_TO_DISORDER_TRANSITION`). | Deduplicated (`add-record` hard identity rules) |
| `124` `InterPro` `Family` entries (`294` `TRAIT_NOT_IN_PTM` pairs in `data/cross_mech/protein_inventory.jsonl`) | Whole-protein homology families (`type="Family"` in `data/raw/interpro/entry.list`); excluded by `scripts/seed_interpro.py` class-level boundary rules. | Intentional architectural boundary (`CLAUDE.md`, `scripts/seed_interpro.py`) |
| `8` `Reactome:R-MTU-*` pathway entries (`57` `TRAIT_NOT_IN_PTM` pairs in `data/cross_mech/protein_inventory.jsonl`) | Species-specific *M. tuberculosis* Reactome projections outside `KEEP_SPECIES` in `scripts/seed_reactome.py`. | Intentional species scope (`scripts/seed_reactome.py`) |
| `MIXED_OTHER`, `OTHER`, `SEQ_OTHER`, `STRUCT_OTHER`, `UPPER` | Catch-all/upper-level `ProteinTraitCategoryEnum` tokens not assigned to leaf class-level trait records (`scripts/audit_schema.py`). | Schema design (`src/proteintraitsmech/schema/proteintraitsmech.yaml`) |
| Unseeded candidate bulk sources in `download.yaml` (`dbPTM`, `SignalP/TargetP`, `Membranome`, `TMAlphaFold`, `3D-Surfer`, `Foldseek`, `EggNOG`, `OrthoDB`, `OMA`, `DGIdb`, `sabio_rk`, `P2Rank`) | External bulk sources without downloaded `data/raw/` releases or approved `ingest-source` seeders; out of scope for `add-record` (which forbids unapproved bulk source ingestion). | `download.yaml` (`status: candidate`) |
| Source-asserted `canonical_examples` for the `101` `proteintraitsmech:*` foundational trait classes (`48` `proteintraitsmech:*` single-file mechanism-graph classes total) | `proteintraitsmech` foundational trait classes define general sequence/structure/evolution classes without a source-shipped UniProt residue-interval table in `data/raw/`. | `INFRA_TASKS.md` (`proteintraitsmech-infra-0002`, [#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)) |
