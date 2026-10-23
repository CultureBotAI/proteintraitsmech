---
topic: causal-graphs
round: 125
date: 2026-10-22
target: foundational-protein-traits & root local-structural / peptide-feature classes — 22 mechanism-bearing records updated across 10 trait categories (25 reviewed)
prior_round: causal-graphs-round124.md
---

# Causal graphs — Round 125: Evidence-backed 4-node / 3-edge molecular mechanisms for Cycle 2 Stage 1 foundational records and 10 root structural/peptide feature classes

## Scope and Eligibility Review

Cycle 2, Stage 2 (`causal_graphs`, `goal-167a`) of run `mech-goal-sequence-20261019` reviewed all `429,377` records in `data/traits/` against `.claude/skills/edison-causal-graphs/SKILL.md`, `.claude/skills/molecular-causal-graphs/SKILL.md`, and `.claude/skills/curate-yaml-record/SKILL.md`:

- **Pre-Cycle-2 corpus (`429,359` records)**:
  - `39,616` records already carried validated `causal_graphs` (`0` errors in `audit_causal_graphs.py`).
  - However, **10 root class-level records** serving as `parent_traits` anchors for local structural sites and UniProt peptide processing classes had `causal_graphs` missing (`0` graphs):
    - `scripts/seed_localstructuralfeature.py` (**5 mechanism-bearing root classes**): `proteintraitsmech:CATALYTIC_RESIDUE` (`STRUCT_ACTIVE_SITE`), `proteintraitsmech:PROTEIN_BINDING_SITE` (`STRUCT_BINDING_SITE`), `proteintraitsmech:METAL_BINDING_SITE` (`STRUCT_METAL_SITE`), `proteintraitsmech:DISULFIDE_BOND` (`STRUCT_DISULFIDE`), and `proteintraitsmech:INTERFACE` (`STRUCT_INTERFACE`). Geometric void/concavity/secondary-motif descriptors (`POCKET`, `CAVITY`, `CLEFT`, `TUNNEL`, `GROOVE`, `ELBOW`, and secondary-structure sub-motifs) are pure structural geometry descriptors whose specialized mechanism-bearing subclasses (`ALLOSTERIC_REGULATORY_SITE`, `CAVITY_SELECTIVITY_FILTER_PORE`, `CAVITY_SUBSTRATE_ACCESS_TUNNEL`) carry the mechanism graphs.
    - `scripts/seed_uniprot_peptide_classes.py` (**5 mechanism-bearing root classes** out of 5): `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE` (`SEQ_INITIATOR_METHIONINE`), `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN` (`SEQ_MATURE_CHAIN`), `proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE` (`SEQ_PROPEPTIDE`), `proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE` (`SEQ_SIGNAL_PEPTIDE`), and `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE` (`SEQ_TRANSIT_PEPTIDE`).
- **Cycle 2 Stage 1 foundational additions (`18` records in `scripts/seed_foundational_traits.py`)**:
  - **15 mechanism-bearing records** across `SEQ_INITIATOR_METHIONINE` (`4`), `SEQ_MATURE_CHAIN` (`4`), `SEQ_TRANSIT_PEPTIDE` (`3`), `SEQ_PROPEPTIDE` (`2`), and `STRUCT_CAVITY` (`2`): **12** of these records had initial 3-node / 2-edge causal graphs or substrate-to-activity predicate assignments that were upgraded to 4-node / 3-edge directed mechanisms with `RO:0000056` (`participates in`) on substrate edges, while **3** records (`proteintraitsmech:INIT_METHIONINE_ACETYLATED`, `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED`, `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION`) already had complete 4-node / 3-edge causal graphs from Stage 1 and were retained unchanged.
  - **3 `EVO_CONSERVATION` records** (`proteintraitsmech:CONSERVATION_ORTHOLOGOUS_CORE_GENE_FAMILY`, `proteintraitsmech:CONSERVATION_LINEAGE_SPECIFIC_ACCESSORY_FAMILY`, `proteintraitsmech:CONSERVATION_SINGLE_COPY_UNIVERSAL_MARKER`) are comparative-genomic / phylogenetic gene-family conservation partitions (`SO:0000857` / `SO:0005855`) rather than residue- or molecule-level biochemical mechanisms; consistent with the 8,666 `ProPan` pangenome records in `EVO_CONSERVATION`, they are representation-bounded and do not carry molecular `causal_graphs`.

## Curated Causal Graphs (22 Records Updated, 3 Stage 1 Records Retained Unchanged; 25 Graphs, 100 Nodes, 75 Edges Verified)

All **22 updated mechanism-bearing records** (12 upgraded Cycle 2 Stage 1 records + 10 root structural/peptide class records) were updated in both their registered seeders (`scripts/seed_foundational_traits.py`, `scripts/seed_localstructuralfeature.py`, `scripts/seed_uniprot_peptide_classes.py`) and on-disk YAML records with 4-node / 3-edge directed molecular causal graphs (`100/100` grounded nodes, `75/75` RO-typed and verbatim-snippet-cited edges across the 25 reviewed records, enriched mechanism definitions, and `curation_history` entry `2026-10-22T18:55:00Z` on the 22 edited records):

### Part A — 12 Cycle 2 Stage 1 Mechanism-Bearing Records Updated (plus 3 Retained Unchanged)

1. **`SEQ_INITIATOR_METHIONINE` (3 updated, 1 retained unchanged)**:
   - `proteintraitsmech:INIT_METHIONINE_EXCISED` (`data/traits/sequence/initiator_methionine/excised-initiator-methionine-site.yaml`): `translational initiation` (`GO:0006413`) → `L-methionine` (`CHEBI:16811`) → `participates in` (`RO:0000056`) `initiator methionyl aminopeptidase activity` (`GO:0004239`) → `protein processing` (`GO:0016485`) (PMID:2682640).
   - `proteintraitsmech:INIT_METHIONINE_RETAINED` (`data/traits/sequence/initiator_methionine/retained-initiator-methionine-site.yaml`): `translational initiation` (`GO:0006413`) → `L-methionine` (`CHEBI:16811`) → `negatively regulates` (`RO:0002212`) `initiator methionyl aminopeptidase activity` (`GO:0004239`) → `enables` (`RO:0002327`) `protein processing` (`GO:0016485`) (PMID:2682640).
   - `proteintraitsmech:INIT_METHIONINE_FORMYLATED_NME` (`data/traits/sequence/initiator_methionine/formylated-initiator-methionine-processing-site.yaml`): `N-formyl-L-methionine` (`MOD:00030`) → `participates in` (`RO:0000056`) `formylmethionine deformylase activity` (`GO:0008463`) → `initiator methionyl aminopeptidase activity` (`GO:0004239`) → `protein processing` (`GO:0016485`) (PMID:18718933).
   - `proteintraitsmech:INIT_METHIONINE_ACETYLATED` (`data/traits/sequence/initiator_methionine/n-acetylated-initiator-methionine-site.yaml`): *Retained unchanged from Stage 1* (`GO:0006413` → `CHEBI:16811` → `GO:0004596` → `MOD:00058`; PMID:27498224).
2. **`SEQ_MATURE_CHAIN` (3 updated, 1 retained unchanged)**:
   - `proteintraitsmech:MATURE_CHAIN_SECRETED` (`data/traits/sequence/mature_chain/signal-peptidase-processed-mature-chain.yaml`): `signal_peptide` (`SO:0000418`) → `protein processing` (`GO:0016485`) → `mature_protein_region` (`SO:0000419`) → `protein secretion` (`GO:0009306`) (PMID:34980915).
   - `proteintraitsmech:MATURE_CHAIN_PROPROTEIN_CLEAVED` (`data/traits/sequence/mature_chain/proprotein-convertase-processed-mature-chain.yaml`): *Retained unchanged from Stage 1* (`SO:0001062` → `GO:0004175` → `GO:0016485` → `SO:0000419`; PMID:18184105).
   - `proteintraitsmech:MATURE_CHAIN_INTEIN_SPLICED` (`data/traits/sequence/mature_chain/intein-spliced-mature-extein-chain.yaml`): `catalytic activity` (`GO:0003824`) → `protein splicing` (`GO:0016539`) → `mature_protein_region` (`SO:0000419`) → `protein maturation` (`GO:0051604`) (PMID:24695729).
   - `proteintraitsmech:MATURE_CHAIN_BIOACTIVE_PEPTIDE` (`data/traits/sequence/mature_chain/proteolytically-excised-bioactive-peptide-chain.yaml`): `endopeptidase activity` (`GO:0004175`) → `antimicrobial peptide biosynthetic process` (`GO:0002777`) → `mature_protein_region` (`SO:0000419`) → `antimicrobial humoral immune response mediated by antimicrobial peptide` (`GO:0061844`) (PMID:11134217).
3. **`SEQ_TRANSIT_PEPTIDE` (3 updated)**:
   - `proteintraitsmech:TRANSIT_PEPTIDE_MITO_IMS` (`data/traits/sequence/transit_peptide/mitochondrial-intermembrane-space-bipartite-transit-peptide.yaml`): `mitochondrial_targeting_signal` (`SO:0001808`) → `participates in` (`RO:0000056`) `endopeptidase activity` (`GO:0004175`) → `protein import into mitochondrial intermembrane space` (`GO:0045041`) → `mitochondrial intermembrane space` (`GO:0005758`) (PMID:8266095).
   - `proteintraitsmech:TRANSIT_PEPTIDE_APICOPLAST` (`data/traits/sequence/transit_peptide/apicoplast-bipartite-transit-peptide.yaml`): `transit_peptide` (`SO:0000725`) → `protein localization to organelle` (`GO:0033365`) → `protein processing` (`GO:0016485`) → `apicoplast` (`GO:0020011`) (PMID:10775264).
   - `proteintraitsmech:TRANSIT_PEPTIDE_HYDROGENOSOME_MITOSOME` (`data/traits/sequence/transit_peptide/hydrogenosomal-mitosomal-transit-presequence.yaml`): `transit_peptide` (`SO:0000725`) → `protein localization to organelle` (`GO:0033365`) → `mitosome` (`GO:0032047`) + `hydrogenosome` (`GO:0042566`) (PMID:16040811).
4. **`SEQ_PROPEPTIDE` (1 updated, 1 retained unchanged)**:
   - `proteintraitsmech:PROPEPTIDE_VKD_GLA_RECOGNITION` (`data/traits/sequence/propeptide/vitamin-k-dependent-gamma-carboxylation-recognition-propeptide.yaml`): *Retained unchanged from Stage 1* (`SO:0001062` → `GO:0004856` → `GO:0017187` → `MOD:00041`; PMID:3802193).
   - `proteintraitsmech:PROPEPTIDE_GPI_C_TERMINAL` (`data/traits/sequence/propeptide/gpi-anchor-c-terminal-propeptide.yaml`): `propeptide` (`SO:0001062`) → `participates in` (`RO:0000056`) `GPI-anchor transamidase activity` (`GO:0003923`) → `attachment of GPI anchor to protein` (`GO:0016255`) → `protein maturation` (`GO:0051604`) (PMID:35165458).
5. **`STRUCT_CAVITY` (2 updated)**:
   - `proteintraitsmech:CAVITY_SELECTIVITY_FILTER_PORE` (`data/traits/structure/cavity/transmembrane-ion-channel-selectivity-filter-pore.yaml`): `polypeptide_domain` (`SO:0000417`) → `metal ion binding` (`GO:0046872`) → `monoatomic ion channel activity` (`GO:0005216`) → `monoatomic ion transmembrane transport` (`GO:0034220`) (PMID:9525859).
   - `proteintraitsmech:CAVITY_SUBSTRATE_ACCESS_TUNNEL` (`data/traits/structure/cavity/buried-active-site-substrate-access-tunnel.yaml`): `chemical entity` (`CHEBI:24431`) → `small molecule binding` (`GO:0036094`) → `catalytic activity` (`GO:0003824`) → `metabolic process` (`GO:0008152`) (PMID:23093919).

### Part B — 10 Root Local-Structural and Peptide-Feature Class Records (Newly Populated with 4 Nodes / 3 Edges)

6. **Root local-structural feature classes (`scripts/seed_localstructuralfeature.py`, 5 records)**:
   - `proteintraitsmech:CATALYTIC_RESIDUE` (`data/traits/structure/active_site/catalytic-residue.yaml`): `amino-acid residue` (`CHEBI:83228`) → `small molecule binding` (`GO:0036094`) → `catalytic activity` (`GO:0003824`) → `metabolic process` (`GO:0008152`) (PMID:12421562, PMID:29106569).
   - `proteintraitsmech:PROTEIN_BINDING_SITE` (`data/traits/structure/binding_site/protein-binding-site.yaml`): `amino-acid residue` (`CHEBI:83228`) → `protein binding` (`GO:0005515`) → `protein complex oligomerization` (`GO:0051259`) → `protein-containing complex` (`GO:0032991`) (PMID:24081580).
   - `proteintraitsmech:METAL_BINDING_SITE` (`data/traits/structure/metal_site/metal-binding-site.yaml`): `amino-acid residue` (`CHEBI:83228`) → `metal ion binding` (`GO:0046872`) → `regulation of protein stability` (`GO:0031647`) + `catalytic activity` (`GO:0003824`) (PMID:23155064).
   - `proteintraitsmech:DISULFIDE_BOND` (`data/traits/structure/disulfide/disulfide-bond.yaml`): `L-cysteine residue` (`CHEBI:29950`) → `participates in` (`RO:0000056`) `protein disulfide isomerase activity` (`GO:0003756`) → `L-cystine (cross-link)` (`MOD:00034`) → `protein folding` (`GO:0006457`) (PMID:19005088, PMID:16959969).
   - `proteintraitsmech:INTERFACE` (`data/traits/structure/interface/interface.yaml`): `amino-acid residue` (`CHEBI:83228`) → `protein binding` (`GO:0005515`) → `protein dimerization activity` (`GO:0046983`) → `protein complex oligomerization` (`GO:0051259`) (PMID:24081580).
7. **Root UniProt peptide-feature classes (`scripts/seed_uniprot_peptide_classes.py`, 5 records)**:
   - `proteintraitsmech:UNIPROT_FT_SEQ_INITIATOR_METHIONINE` (`data/traits/sequence/initiator_methionine/uniprot-seq_initiator_methionine.yaml`): `translational initiation` (`GO:0006413`) → `L-methionine` (`CHEBI:16811`) → `participates in` (`RO:0000056`) `initiator methionyl aminopeptidase activity` (`GO:0004239`) → `protein processing` (`GO:0016485`) (PMID:2682640).
   - `proteintraitsmech:UNIPROT_FT_SEQ_MATURE_CHAIN` (`data/traits/sequence/mature_chain/uniprot-seq_mature_chain.yaml`): `endopeptidase activity` (`GO:0004175`) → `protein processing` (`GO:0016485`) → `mature_protein_region` (`SO:0000419`) → `protein maturation` (`GO:0051604`) (PMID:18184105).
   - `proteintraitsmech:UNIPROT_FT_SEQ_PROPEPTIDE` (`data/traits/sequence/propeptide/uniprot-seq_propeptide.yaml`): `propeptide` (`SO:0001062`) → `protein folding` (`GO:0006457`) → `endopeptidase activity` (`GO:0004175`) → `zymogen activation` (`GO:0031638`) (PMID:38421254, PMID:31557781).
   - `proteintraitsmech:UNIPROT_FT_SEQ_SIGNAL_PEPTIDE` (`data/traits/sequence/signal_peptide/uniprot-seq_signal_peptide.yaml`): `signal_peptide` (`SO:0000418`) → `protein transport by the Sec complex` (`GO:0043952`) → `endopeptidase activity` (`GO:0004175`) → `protein secretion` (`GO:0009306`) (PMID:34980915).
   - `proteintraitsmech:UNIPROT_FT_SEQ_TRANSIT_PEPTIDE` (`data/traits/sequence/transit_peptide/uniprot-seq_transit_peptide.yaml`): `transit_peptide` (`SO:0000725`) → `protein import into chloroplast stroma` (`GO:0045037`) → `endopeptidase activity` (`GO:0004175`) → `chloroplast stroma` (`GO:0009570`) (PMID:37324391).

## Writer & Representation Blockers Recorded

- **Seeder re-seed idempotency (`scripts/record_io.py`)**: `merge_on_reseed` unions `causal_graphs` by serialized dict equality (`_union_list_keys`) rather than `graph_id` identity, so upgrading nodes or edges on an existing `graph_id` via `merge_on_reseed` appends a second graph with the same `graph_id`. All three seeders (`scripts/seed_foundational_traits.py`, `scripts/seed_localstructuralfeature.py`, `scripts/seed_uniprot_peptide_classes.py`) emit their full `causal_graphs` and `evidence` blocks directly and were verified to preserve idempotency when re-run against the updated on-disk YAML records; the `graph_id`-keyed merge enhancement is recorded in `INFRA_TASKS.md` (`proteintraitsmech-infra-0004`).
- **Source-limited and representation-bounded records**: Pure fold/superfamily/topology descriptors (`CATH`, `SCOPe`, `ECOD`, `TED`), signature-only domain families (`Pfam`, `InterPro`, `SUPERFAMILY`, `NCBIfam`, `HAMAP`, `CDD`, `PRINTS`), comparative-genomic conservation classes (`ProPan`, `EVO_CONSERVATION`), geometric void/concavity root terms (`POCKET`, `CAVITY`), and compositional/quaternary/symmetry/coiled-coil descriptors lack source-asserted molecular reaction or binding steps and rightly remain without `causal_graphs`.

## Provenance

- Records updated with 4-node / 3-edge `causal_graphs`: **22** (12 upgraded Cycle 2 Stage 1 records + 10 newly populated root structural/peptide class records; 3 already-4-node Stage 1 records verified and retained unchanged; native `mapping_status: SEEDED` preserved; `curation_history` recorded with `curator: claude`, `action: EDIT`, `llm_assisted: true`)
- `validate_strict.py`: `25 files scanned, 0 files with ERROR, 0 total ERROR rows`
- `audit_causal_graphs.py --strict`: `25 records, 25 graphs, 100 nodes, 75 edges | grounded nodes 100/100, snippet-cited edges 75/75 | 0 errors, 0 warnings`
- `score_causal_graphs.py`: **25/25 records score 95/100 (`structural_errors=0`, `quality_warnings=0`, `reasons=mapping_status=SEEDED`)**
- Corpus after: **39,641 records with `causal_graphs`** (up from `39,631`)
