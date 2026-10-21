---
topic: causal-graphs
round: 124
date: 2026-10-21
target: foundational-protein-traits — 25 mechanism-bearing records across 7 trait categories
prior_round: causal-graphs-round123.md
---

# Causal graphs — Round 124: Evidence-backed mechanisms for the 25 mechanism-bearing foundational protein-trait classes

## Scope and Eligibility Review

Stage 2 of the `mech-goal-sequence-20261019` cycle audited all `429,359` records in `data/traits/`:

- **Pre-Stage-1 corpus (`429,293` records)**:
  - `39,591` records already carry curated, validated `causal_graphs` (`0` errors in `audit_causal_graphs.py`).
  - `389,702` records do not carry `causal_graphs` due to source-limited or structural-classification boundaries (for example pure fold/superfamily/topology records in `CATH`/`SCOPe`/`ECOD`/`TED` with no source-asserted molecular mechanism, signature-only `Pfam`/`InterPro`/`SUPERFAMILY`/`NCBIfam`/`HAMAP`/`CDD`/`PRINTS` family descriptors without catalytic or binding mechanism assertions, pangenome/conservation `EVOLUTION` partitions, or `GO`/`RHEA` leaf terms without stoichiometry/mechanism annotations).
- **Stage 1 foundational additions (`66` records from `scripts/seed_foundational_traits.py`)**:
  - Reviewed all `66` records across 12 categories against `.claude/skills/edison-causal-graphs/SKILL.md`, `.claude/skills/molecular-causal-graphs/SKILL.md`, and `.claude/skills/curate-yaml-record/SKILL.md`.
  - **25 records are mechanism-bearing classes** with direct primary-literature support for their molecular causal graphs (`SEQ_NONSTANDARD_RESIDUE` [4], `STRUCT_ALLOSTERIC_SITE` [5], `SEQ_SIGNAL_PEPTIDE` [5], `SEQ_TRANSIT_PEPTIDE` [3], `SEQ_PROPEPTIDE` [3], `STRUCT_DISULFIDE` [4], `FUNC_LOCALIZATION` [1]).
  - **41 records are structural/compositional/geometric descriptors** where asserting a single directed molecular causal graph would fabricate an unsupported mechanism (`STRUCT_QUATERNARY` [11], `SEQ_COMPOSITION` [10], `STRUCT_SYMMETRY` [9], `MIXED_COILED_COIL` [7], `SEQ_LOW_COMPLEXITY` [4]).

## Curated Causal Graphs (25 Records, 25 Graphs, 111 Nodes, 86 Edges)

All 25 mechanism-bearing foundational records were updated via the registered writer `scripts/seed_foundational_traits.py` (preserving native `mapping_status: SEEDED` per `.claude/skills/curate-yaml-record/SKILL.md` with `curation_history` entry `curator: claude`, `action: EDIT`, `llm_assisted: true`), with `111/111` grounded nodes, `86/86` RO-typed (`predicate_id`) and snippet-cited edges, `0` errors / `0` warnings in `audit_causal_graphs.py --strict`, and `score_causal_graphs.py` score `95/95` (maximum possible for `mapping_status: SEEDED`, where `SEEDED_REVIEW_PENALTY = 5` is reserved for human `REVIEWED` promotion):

1. **`SEQ_NONSTANDARD_RESIDUE` (4 records)**:
   - `proteintraitsmech:NONSTD_SELENOCYSTEINE`: `SECIS_element` (`SO:1001274`) + `stop_codon_redefined_as_selenocysteine` (`SO:0000885`) + `L-selenocysteine` (`CHEBI:16633`) → `selenocysteine incorporation` (`GO:0001514`) → `L-selenocysteine residue` (`MOD:00040`) (PMID:28192430, PMID:26819414).
   - `proteintraitsmech:NONSTD_PYRROLYSINE`: `L-pyrrolysine` (`CHEBI:21860`) + `pyrrolysyl-tRNA synthetase activity` (`GO:0043767`) + `stop_codon_redefined_as_pyrrolysine` (`SO:0000884`) → `pyrrolysine incorporation` (`GO:0030631`) → `L-pyrrolysine residue` (`MOD:01155`) (PMID:42848426, PMID:16150879).
   - `proteintraitsmech:NONSTD_N_FORMYLMETHIONINE`: `methionyl-tRNA formyltransferase activity` (`GO:0004479`) → `N-formyl-L-methionine` (`CHEBI:16552`) / `N-formyl-L-methionine residue` (`MOD:00055`) → `translational initiation` (`GO:0006413`), followed by `formylmethionine deformylase activity` (`GO:0008463`) (PMID:42079159, PMID:42278349).
   - `proteintraitsmech:NONSTD_D_AMINO_ACID_RESIDUE`: `L-alpha-amino acid residue` (`MOD:00868`) + `peptidyl-amino-acid racemase activity` (`GO:0016855`) → `peptidyl-amino acid modification` (`GO:0018193`) → `D-alpha-amino acid residue` (`MOD:00869`) (PMID:29779654, PMID:23064837).
2. **`STRUCT_ALLOSTERIC_SITE` (5 records)**:
   - `proteintraitsmech:ALLOSTERIC_REGULATORY_SITE`, `ALLOSTERIC_ACTIVATOR_SITE`, `ALLOSTERIC_INHIBITOR_SITE`, `ALLOSTERIC_CRYPTIC_POCKET`, `ALLOSTERIC_SUBUNIT_INTERFACE_SITE` (PMID:26952375, PMID:42396523, PMID:37882678).
3. **`SEQ_SIGNAL_PEPTIDE` (5 records)**:
   - `proteintraitsmech:SIGNAL_PEPTIDE_SEC_SPI`, `SIGNAL_PEPTIDE_SEC_SPII`, `SIGNAL_PEPTIDE_TAT_SPI`, `SIGNAL_PEPTIDE_TAT_SPII`, `SIGNAL_PEPTIDE_SEC_SPIII` (PMID:38336966, PMID:37905051, PMID:38319956, PMID:28792336).
4. **`SEQ_TRANSIT_PEPTIDE` (3 records)**:
   - `proteintraitsmech:TRANSIT_PEPTIDE_MITOCHONDRIAL`, `TRANSIT_PEPTIDE_CHLOROPLAST_STROMA`, `TRANSIT_PEPTIDE_THYLAKOID_LUMEN` (PMID:36690624, PMID:36732524, PMID:40919263).
5. **`SEQ_PROPEPTIDE` (3 records)**:
   - `proteintraitsmech:PROPEPTIDE_ZYMOGEN_ACTIVATION`, `PROPEPTIDE_INTRAMOLECULAR_CHAPERONE`, `PROPEPTIDE_PROHORMONE_DIBASIC` (PMID:38050917, PMID:40499874, PMID:42955853).
6. **`STRUCT_DISULFIDE` (4 records)**:
   - `proteintraitsmech:DISULFIDE_INTRACHAIN`, `DISULFIDE_INTERCHAIN`, `DISULFIDE_CYSTINE_KNOT`, `DISULFIDE_ALLOSTERIC_REDOX_SWITCH` (PMID:42829235, PMID:19005088, PMID:40763564, PMID:42681370).
7. **`FUNC_LOCALIZATION` (1 record)**:
   - `GO:7770085` (`protocatechuate 3,4-dioxygenase complex`): `protocatechuate 3,4-dioxygenase complex` (`GO:7770085`) + `iron(3+)` (`CHEBI:29034`) → `protocatechuate 3,4-dioxygenase activity` (`GO:0018578`) + `3,4-dihydroxybenzoate` (`CHEBI:36241`) → `3-carboxy-cis,cis-muconate(3-)` (`CHEBI:57496`) in `protocatechuate catabolic process, ortho-cleavage` (`GO:0019618`) (PMID:16101286, PMID:11029436).

## Hierarchy and Cross-Reference Audit Fixes

During the curation audit (`.claude/skills/curate-yaml-record/SKILL.md`), 19 `parent_traits` references and 1 `xrefs` reference across 19 of the 66 foundational trait records were found to point to unseeded placeholder CURIEs rather than canonical on-disk corpus records:
- Re-anchored `SEQ_NONSTANDARD_RESIDUE` (4 records): removed unseeded `proteintraitsmech:UNIPROT_FT_NON_STD` and replaced `proteintraitsmech:UNIPROT_FT_INIT_MET` with `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE`.
- Re-anchored `COMPBIAS_AROMATIC_POLAR_STICKER_SPACER` (`SEQ_COMPOSITION`) and `LOWCOMP_PRION_LIKE_DOMAIN` (`SEQ_LOW_COMPLEXITY`): replaced `IDPO:00076` with `IDPO:0000002` (`disorder function`).
- Re-anchored `STRUCT_ALLOSTERIC_SITE` (2 records): replaced `proteintraitsmech:BINDING_SITE` with `proteintraitsmech:POCKET` on `ALLOSTERIC_REGULATORY_SITE`, and `proteintraitsmech:PROTEIN_INTERFACE` with `proteintraitsmech:INTERFACE` on `ALLOSTERIC_SUBUNIT_INTERFACE_SITE`.
- Re-anchored `SEQ_SIGNAL_PEPTIDE` (5 records), `SEQ_TRANSIT_PEPTIDE` (3 records), and `SEQ_PROPEPTIDE` (3 records) from `UNIPROT_FT_SIGNAL` / `UNIPROT_FT_TRANSIT` / `UNIPROT_FT_PROPEP` to `proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE`, `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE`, and `proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE`.
- Updated `GO:7770085` `xrefs` from `RHEA:15457` to the on-disk record `RHEA:10084`.

## Provenance

- Records updated with `causal_graphs`: **25** (native `mapping_status: SEEDED` preserved; `curation_history` recorded with `curator: claude`, `action: EDIT`, `llm_assisted: true`)
- Additional non-mechanism foundational records with `parent_traits` hierarchy fixes: **2** (`SEQ_COMPOSITION`, `SEQ_LOW_COMPLEXITY`)
- `audit_causal_graphs.py --strict`: `25 records, 25 graphs, 111 nodes, 86 edges | grounded nodes 111/111, snippet-cited edges 86/86 | 0 errors, 0 warnings`
- `score_causal_graphs.py`: **25/25 records score 95/100 (`structural_errors=0`, `quality_warnings=0`, `reasons=mapping_status=SEEDED`)**
- Corpus after: **39,616 records with `causal_graphs`**
