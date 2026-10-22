# Cycle 2 Stage 1 (`add_records`) — Bounded Frontier Search & Class-Level Trait Addition Report

- **Run**: `mech-goal-sequence-20261019`
- **Cycle / Stage**: Cycle 2, Stage 1 (`add_records`)
- **Date**: 2026-10-22
- **Skill**: `.claude/skills/add-record/SKILL.md` (`add-record`)
- **Seeder**: `scripts/seed_foundational_traits.py` (84 foundational trait classes across 16 categories; 18 added in Cycle 2 Stage 1)

---

## 1. Bounded Frontier Definition & Search Protocol

Following `.claude/skills/add-record/SKILL.md`, candidate evaluation was performed across three bounded frontier axes:

1. **Schema Category Coverage (`ProteinTraitCategoryEnum`)**:
   - All 57 enum values in `src/proteintraitsmech/schema/proteintraitsmech.yaml` were inventoried against `data/traits/**/*.yaml` to detect any empty (`0` records), single-record (`1` record), or sparse (`<= 5` records) class-level categories lacking fundamental subclass coverage.
2. **Cross-Mech `TRAIT_NOT_IN_PTM` Inventory (`data/cross_mech/protein_inventory.jsonl`)**:
   - All 352 `TRAIT_NOT_IN_PTM` pairs (133 distinct external CURIEs) from sibling Mech repositories were audited against the corpus and seeder exclusion rules (`scripts/seed_interpro.py`, `scripts/seed_reactome.py`, `scripts/seed_go.py`).
3. **Catalogued Upstream Data Sources (`download.yaml`)**:
   - All 51 source entries in `download.yaml` (`27` seeded, `24` candidate/reference/mapping) were checked against `data/raw/` availability and class-level vs. per-protein boundary rules.

---

## 2. Pass 1 Search Results & Admissible Class-Level Candidates

### 2.1 `ProteinTraitCategoryEnum` Audit (Pass 1)

At the start of Cycle 2 Stage 1 (`429,359` total records), 53 of 57 `ProteinTraitCategoryEnum` categories had on-disk records, while 4 (`SEQ_CLEAVAGE_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_LIPIDATION`, `SEQ_GLYCOSYLATION`) are explicitly documented in `src/proteintraitsmech/schema/proteintraitsmech.yaml` as per-protein `canonical_examples` feature categories (not standalone class-level directories).

Among the 53 populated class-level categories, Pass 1 identified **2 remaining single-record categories** (seeded only with a generic UniProt feature umbrella placeholder) and **4 sparse class-level categories (`<= 5` records)** missing canonical biological subclasses:

| Category | Pass 1 Count | Gap Identified in Pass 1 | Admissible New Class-Level Records Added | Pass 2 Count |
| --- | ---: | --- | ---: | ---: |
| `SEQ_INITIATOR_METHIONINE` | 1 | Only umbrella `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE` existed; lacked excised vs. retained, formylated bacterial/organellar NME, and N-terminally acetylated subclasses. | +4 | 5 |
| `SEQ_MATURE_CHAIN` | 1 | Only umbrella `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN` existed; lacked secretory signal-cleaved, propeptide-excised, intein-spliced extein, and double-glycine bacteriocin leader-cleaved mature chain classes. | +4 | 5 |
| `SEQ_TRANSIT_PEPTIDE` | 4 | Covered mitochondrial matrix, chloroplast stroma, and thylakoid lumen, but lacked mitochondrial intermembrane space (MIA/stop-transfer), apicoplast bipartite, and hydrogenosomal/mitosomal transit peptide classes. | +3 | 7 |
| `SEQ_PROPEPTIDE` | 4 | Covered zymogen inhibitory, intramolecular chaperone, and prohormone dibasic propeptides, but lacked vitamin K-dependent gamma-carboxylation recognition propeptides and C-terminal GPI-attachment propeptides. | +2 | 6 |
| `STRUCT_CAVITY` | 5 | Covered generic cavity/pocket/tunnel/channel/buried void, but lacked ion-channel selectivity filter pores and buried-active-site substrate access tunnels. | +2 | 7 |
| `EVO_CONSERVATION` | 3 | Covered generic conserved/variable/clade-specific protein classes, but lacked universal single-copy orthologs, purifying-selection constrained proteins ($\omega \ll 1$), and positively selected diversifying proteins ($\omega > 1$). | +3 | 6 |

### 2.2 Summary of 18 New Class-Level `ProteinTraitRecord` Files Added

All 18 new records were added to `SPECS` in `scripts/seed_foundational_traits.py` and emitted via `record_io.write_record(..., validate=True)` with grounded ontology terms (`SO`, `GO`, `MOD`, `CHMO`, `CHEBI`, `NCIT`), primary literature provenance (`PMID` + `DOI` + verbatim snippet), runnable `detection_methods` CLI recipes, and verified `causal_graphs` (on all 15 mechanism-bearing records, audited with `scripts/audit_causal_graphs.py --strict`):

1. **`SEQ_INITIATOR_METHIONINE` (`data/traits/sequence/initiator_methionine/`)**:
   - `proteintraitsmech:INIT_METHIONINE_EXCISED` (`excised-initiator-methionine-site.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE`; MAP cotranslational excision at P1' small-side-chain residues (`PMID:2811860`, `PMID:16959962`).
   - `proteintraitsmech:INIT_METHIONINE_RETAINED` (`retained-initiator-methionine-site.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE`; steric retention of Met1 before bulky/charged P1' residues (`PMID:2811860`, `PMID:20022955`).
   - `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME` (`formylated-initiator-methionine-processing-site.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE`; sequential PDF deformylation + MAP cleavage in bacteria/organelles (`PMID:8066440`, `PMID:10984043`).
   - `proteintraitsmech:INIT_METHIONINE_ACETYLATED` (`n-acetylated-initiator-methionine-site.yaml`) — parent `proteintraitsmech:INIT_METHIONINE_RETAINED`; NatB/NatC/NatE/NatF N-alpha-acetylation of retained Met1 (`PMID:19420262`, `PMID:29754825`).
2. **`SEQ_MATURE_CHAIN` (`data/traits/sequence/mature_chain/`)**:
   - `proteintraitsmech:MATURE_CHAIN_SECRETED` (`signal-peptidase-processed-mature-chain.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN`; `SO:0000419` mature polypeptide after signal peptidase removal (`PMID:9008168`, `PMID:21953457`).
   - `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED` (`proprotein-convertase-processed-mature-chain.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN`; `SO:0000419` mature polypeptide chain generated by proprotein convertase cleavage (`PMID:9651384`, `PMID:23193131`).
   - `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED` (`intein-spliced-mature-extein-chain.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN`; `SO:0000419` mature extein ligated by autocatalytic protein splicing (`PMID:10894549`, `PMID:24755427`).
   - `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE` (`proteolytically-excised-bioactive-peptide-chain.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN`; `SO:0002387` mature bioactive antimicrobial/effector peptide after double-glycine leader cleavage (`PMID:8538411`, `PMID:23248205`).
3. **`SEQ_TRANSIT_PEPTIDE` (`data/traits/sequence/transit_peptide/`)**:
   - `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS` (`mitochondrial-intermembrane-space-bipartite-transit-peptide.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`; `SO:0000725` bipartite stop-transfer / Mia40-Erv1 CX3C-CX9C IMS sorting peptide (`PMID:16009131`, `PMID:19328061`).
   - `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST` (`apicoplast-bipartite-transit-peptide.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`; `SO:0000725` ER signal + plastid transit peptide targeting the 4-membrane apicoplast via SELMA (`PMID:10984049`, `PMID:12642605`).
   - `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME` (`hydrogenosomal-mitosomal-transit-presequence.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`; `SO:0000725` short N-terminal MRO targeting presequence (`PMID:8970150`, `PMID:15772074`).
4. **`SEQ_PROPEPTIDE` (`data/traits/sequence/propeptide/`)**:
   - `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION` (`vitamin-k-dependent-gamma-carboxylation-recognition-propeptide.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE`; `SO:0001062` GGCX docking propeptide driving Glu-to-Gla gamma-carboxylation prior to furin cleavage (`PMID:2553775`, `PMID:9845384`).
   - `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL` (`gpi-anchor-c-terminal-propeptide.yaml`) — parent `proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE`; `SO:0001062` C-terminal hydrophobic propeptide cleaved at the omega site by GPI transamidase (`PMID:10022882`, `PMID:18485873`).
5. **`STRUCT_CAVITY` (`data/traits/structure/cavity/`)**:
   - `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE` (`transmembrane-ion-channel-selectivity-filter-pore.yaml`) — parent `proteintraitsmech:POCKET` and `proteintraitsmech:CAVITY`; narrow carbonyl/side-chain dehydrating constriction governing ion selectivity (`PMID:9525859`, `PMID:11689935`).
   - `proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL` (`buried-active-site-substrate-access-tunnel.yaml`) — parent `proteintraitsmech:TUNNEL`; gated interior transport pathway connecting solvent to a buried catalytic pocket (`PMID:11517299`, `PMID:17881302`).
6. **`EVO_CONSERVATION` (`data/traits/evolution/conservation/`)**:
   - `proteintraitsmech:EVO_UNIVERSAL_SINGLE_COPY_ORTHOLOG` (`universal-single-copy-ortholog-protein.yaml`) — parent `proteintraitsmech:EVO_CONSERVED`; BUSCO/marker gene dosage-balance single-copy ortholog class (`PMID:18056067`, `PMID:25595208`).
   - `proteintraitsmech:EVO_PURIFYING_SELECTION_CONSTRAINED` (`purifying-selection-constrained-protein.yaml`) — parent `proteintraitsmech:EVO_CONSERVED`; $\omega = d_N/d_S \ll 1$ negative-selection constrained protein class (`PMID:11038535`, `PMID:26139633`).
   - `proteintraitsmech:EVO_POSITIVELY_SELECTED_DIVERSIFYING` (`positively-selected-diversifying-protein.yaml`) — parent `proteintraitsmech:EVO_VARIABLE`; $\omega = d_N/d_S > 1$ diversifying-selection protein class (`PMID:9611197`, `PMID:15703242`).

---

## 3. Pass 2 Repeated Frontier Search & Verification

After seeding the 18 new records (`429,377` total corpus records across `data/traits/**/*.yaml`), the bounded frontier search was repeated across all three axes:

1. **`ProteinTraitCategoryEnum` Distribution (Pass 2)**:
   - **53 of 57** categories are populated on disk.
   - **0 empty class-level categories** remain.
   - **0 single-record categories** remain (minimum category size across all 53 class-level categories is now `3` records, and every category seeded by `scripts/seed_foundational_traits.py` has `>= 4` records).
   - The remaining 4 enum values (`SEQ_CLEAVAGE_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_LIPIDATION`, `SEQ_GLYCOSYLATION`) are per-protein `canonical_examples` feature categories by schema design.
2. **Cross-Mech `TRAIT_NOT_IN_PTM` Audit (Pass 2)**:
   - Re-scanned all 352 `TRAIT_NOT_IN_PTM` pairs (133 distinct external IDs) in `data/cross_mech/protein_inventory.jsonl`:
     - `124` `InterPro:IPR...` entries (`294` pairs): 100% are `type="Family"` in `data/raw/interpro/entry.list`, intentionally excluded by `scripts/seed_interpro.py` (`KEEP_TYPES = {"Domain", "Repeat", "Active_site", "Binding_site", "Conserved_site", "PTM"}`) because whole-protein homology families are not composable protein traits.
     - `8` `Reactome:R-MTU-...` entries (`57` pairs): *Mycobacterium tuberculosis* species-specific pathway projections intentionally excluded by `scripts/seed_reactome.py` (`KEEP_SPECIES = {"Homo sapiens", "Escherichia coli", "Saccharomyces cerevisiae"}`).
     - `1` `GO:0004085` entry (`1` pair): obsolete GO term already merged as an `equivalent_trait` on `GO:0016937` (`data/traits/function/catalytic/go/butyryl-coa-dehydrogenase-activity-go0016937.yaml`).
   - **Result**: `0` unseeded admissible class-level traits remain in the cross-Mech inventory.
3. **Validation Summary**:
   - `scripts/validate_strict.py`: `36 files scanned, 0 errors` ( across all 18 new records + all 18 updated/existing records in the 6 modified directories).
   - `scripts/audit_causal_graphs.py --strict`: `21 records, 21 graphs, 75 nodes, 54 edges | grounded nodes 75/75 (100.0%), snippet-cited edges 54/54 (100.0%) | 0 errors, 0 warnings`.
   - `scripts/build_methods.py --check`: `OK` (`100%` runnable detection method coverage).
   - `scripts/validate_internal_id_labels.py`: `OK` (`429,377` records scanned, `0` new mismatches).
   - `pytest tests/test_foundational_traits.py tests/test_methods_recipes.py`: `10 passed`.

---

## 4. Preserved Unresolved Candidates & Search Limits

| Candidate / Frontier Slice | Reason Excluded or Deferred | Tracking |
| --- | --- | --- |
| `124` `InterPro` `Family` entries (`294` `TRAIT_NOT_IN_PTM` pairs in `data/cross_mech/protein_inventory.jsonl`) | Whole-protein homology families (`type="Family"` in `data/raw/interpro/entry.list`); excluded by `scripts/seed_interpro.py` class-level boundary rules. | Intentional architectural boundary (`CLAUDE.md`, `scripts/seed_interpro.py`) |
| `8` `Reactome:R-MTU-*` pathway entries (`57` `TRAIT_NOT_IN_PTM` pairs in `data/cross_mech/protein_inventory.jsonl`) | Species-specific *M. tuberculosis* Reactome projections outside `KEEP_SPECIES` in `scripts/seed_reactome.py`. | Intentional species scope (`scripts/seed_reactome.py`) |
| `SEQ_CLEAVAGE_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_LIPIDATION`, `SEQ_GLYCOSYLATION` | Per-protein residue-coordinate modification/cleavage feature categories carried inside `canonical_examples` rather than standalone class-level trait directories; class-level PTM signatures are already seeded under `SEQ_PTM_SITE` (`334` PROSITE/InterPro records). | Schema design (`src/proteintraitsmech/schema/proteintraitsmech.yaml`) |
| Unseeded candidate bulk sources in `download.yaml` (`dbPTM`, `SignalP/TargetP`, `Membranome`, `TMAlphaFold`, `3D-Surfer`, `Foldseek`, `EggNOG`, `OrthoDB`, `OMA`, `DGIdb`, `sabio_rk`, `P2Rank`) | External bulk sources without downloaded `data/raw/` releases or approved `ingest-source` seeders; out of scope for `add-record` (which forbids unapproved bulk source ingestion). | `download.yaml` (`status: candidate`) |
| Source-asserted `canonical_examples` for the 84 `proteintraitsmech:*` foundational trait classes | `proteintraitsmech` foundational trait classes define general sequence/structure/evolution classes without a source-shipped UniProt residue-interval table in `data/raw/`. | `INFRA_TASKS.md` (`proteintraitsmech-infra-0002`, [#652](https://github.com/CultureBotAI/proteintraitsmech/issues/652)) |
