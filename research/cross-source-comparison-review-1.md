---
topic: cross-source comparison representations by trait category
date: 2026-07-04
question: >-
  For each ProteinTraitsMech trait_category, what representation is comparable
  across sources, and what operator decides same / equivalent / related traits?
status: grounded design review
---

# Cross-source comparison review 1

## Verified repository facts

This review is grounded in the current repository state, especially:

- `src/proteintraitsmech/schema/proteintraitsmech.yaml` defines
  `ProteinTraitRecord`, the `TraitAxisEnum` axes `SEQUENCE`, `STRUCTURE`,
  `SEQUENCE_STRUCTURE`, `FUNCTION`, and `EVOLUTION`, and the full
  `ProteinTraitCategoryEnum`.
- The schema has sequence-level representation slots `sequence_pattern` and
  `residue_sequence`, plus `canonical_examples.features.start`,
  `canonical_examples.features.end`, and
  `canonical_examples.features.feature_type` on `SequenceFeatureAnnotation`.
  I found no schema slot named for a DSSP/STRIDE secondary-structure string,
  no secondary-structure topology slot, no representative-structure slot, no
  Foldseek 3Di slot, and no contact-map slot.
- `data/traits/structure/secondary/` contains exactly 8 YAML records:
  `ASX_MOTIF`, `BETA_BULGE`, `BETA_HAIRPIN`, `COILED_COIL`, `HELIX_CAP`,
  `KINK`, `NEST`, and `POLYPEPTIDE_STRUCTURAL_MOTIF`.
- `data/equivalence/` currently contains `cross_source.tsv` and
  `member_overlap.tsv`. `cross_source.tsv` has 24,299
  `biolink:close_match` edges; `member_overlap.tsv` has 2
  `biolink:narrow_match` edges.
- `scripts/build_docs_index.py` loads all `data/equivalence/*.tsv` files with
  the shared columns `subject`, `predicate`, `object`, `relation_source`, and
  loads them bidirectionally into the browser `eq` field.
- Existing comparison work is in `research/entry-merge-methods-round1.md` and
  the scripts `build_equivalence.py`, `build_member_overlap.py`,
  `verify_region_overlap.py`, `build_structural_equivalence.py`,
  `embed_records.py`, and `embed_neighbors.py`.

Thresholds already implemented or specified in the repo:

- Phase 1 InterPro member-DB integration: source-integrated signatures emit
  `biolink:close_match` into `data/equivalence/cross_source.tsv`.
- Phase 2 member overlap: Jaccard `J >= 0.90` is a merge candidate,
  `0.50 <= J < 0.90` is `biolink:close_match`, and containment
  `C >= 0.90` is `biolink:narrow_match` / containment.
- Tier-2 region verification: reciprocal residue overlap `>= 0.80` on a
  protein and agreeing fraction `>= 0.50` across sampled shared proteins
  confirms localized same-region equivalence.
- Phase 3 structure comparison: Foldseek TM-score `>= 0.50` means same fold;
  TM-score `>= 0.70` means same superfamily-level structural equivalence.
- Tier 5 semantic candidates: `embed_neighbors.py` uses embedding cosine
  `>= 0.92` for cross-source, same-axis, same-category review candidates only.

## 1. Per-category comparison matrix

Rows below cover every `ProteinTraitCategoryEnum` value in the schema. Source
counts come from the current docs shards where records exist; empty enum
categories are marked as gaps rather than inferred from source plans.

### SEQUENCE axis

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `SEQ_MOTIF` | Symbolic linear sequence pattern (`sequence_pattern`) or member signature; examples can carry residue coordinates. | Exact normalized pattern/profile identity for strict merge; otherwise UniProt member-set `J >= 0.90` plus Tier-2 reciprocal region overlap `>= 0.80` on `>= 0.50` sampled shared proteins. `0.50 <= J < 0.90` is related. | 3,121 records: PROSITE 2,714; ELM 274; Pfam 133. | `biolink:close_match`; `biolink:narrow_match` for containment; `biolink:same_as` only for strict same identifier/pattern. | Phase 1 for InterPro-integrated PROSITE/Pfam/CDD/NCBIfam where present; Phase 2 + Tier 2 for member/region; Tier 5 review. |
| `SEQ_SIGNAL_PEPTIDE` | N-to-C residue interval and cleavage boundary; optional `feature_type` from UniProt FT `SIGNAL`. | Same protein/same interval with reciprocal residue overlap `>= 0.80`; cross-source predictor classes should compare cleavage position within 1-3 residues. | 1 record: UniProtKB demo/class record. | `biolink:close_match`; `biolink:overlaps` for partial interval agreement. | GAP for cross-source overlay; schema can hold coordinates only inside examples, not a class-level boundary model. |
| `SEQ_TRANSIT_PEPTIDE` | N-terminal targeting peptide interval and cleavage boundary. | Same target class plus reciprocal interval overlap `>= 0.80`; cleavage position within 1-3 residues. | 1 record: UniProtKB demo/class record. | `biolink:close_match`; `biolink:overlaps` for partial. | GAP. |
| `SEQ_PROPEPTIDE` | Propeptide interval and mature-chain cleavage boundary. | Same cleavage product class plus reciprocal interval overlap `>= 0.80`; exact cleavage boundary for strict match. | 1 record: UniProtKB demo/class record. | `biolink:close_match`; `biolink:overlaps`. | GAP. |
| `SEQ_INITIATOR_METHIONINE` | Position 1 methionine processing feature. | Same feature type and position `start=end=1`; source evidence can vary. | 1 record: UniProtKB demo/class record. | `biolink:same_as` if same feature class; otherwise `biolink:close_match`. | GAP but low risk because category is atomic. |
| `SEQ_MATURE_CHAIN` | Mature chain / peptide product interval after processing. | Same product identity plus reciprocal interval overlap `>= 0.80`; exact start/end for strict match. | 1 record: UniProtKB demo/class record. | `biolink:close_match`; `biolink:overlaps`. | GAP. |
| `SEQ_NONSTANDARD_RESIDUE` | Single residue position and residue/modification identity. | Same nonstandard residue type and same coordinate; if coordinates differ but residue type same, related only. | 0 records. | `biolink:close_match` or `biolink:same_as` for same grounded residue class. | GAP: enum exists, no records. |
| `SEQ_CLEAVAGE_SITE` | Short linear pattern and cut-site coordinate. | Same cleavage grammar and cut offset; for instances, start/end cut coordinate within 1 residue. | 11 records: ELM. | `biolink:close_match`; `biolink:overlaps` for nearby cuts. | Phase 2 + Tier 2 possible if member sets exist; currently no asserted overlay. |
| `SEQ_TARGETING_SIGNAL` | Short linear targeting motif pattern, often regex-like ELM `TRG`. | Exact/compatible regex or member-region overlap; `J >= 0.90` plus Tier-2 region check for assertable edge. | 28 records: ELM. | `biolink:close_match`; `biolink:narrow_match` for more specific motif class. | GAP for current overlays; Tier 5 review possible. |
| `SEQ_LEADER_PEPTIDE` | N-terminal RiPP/bacteriocin leader interval and cleavage grammar. | Same precursor class plus interval overlap `>= 0.80`; strict match requires same cleavage site. | 20 curated records. | `biolink:close_match`; `biolink:overlaps`. | GAP. |
| `SEQ_LOW_COMPLEXITY` | Compositionally biased interval; residue alphabet and complexity score. | Same bias class plus interval overlap `>= 0.80`; future SEG/fLPS score thresholds should be stored externally. | 0 records. | `biolink:close_match`; `biolink:overlaps`. | GAP: enum exists, no records and no score slot. |
| `SEQ_DISORDER` | Disorder class / IDPO anchor and disordered interval examples. | Same IDPO term is class-level identity; instance intervals compare by reciprocal overlap `>= 0.80`. | 202 records: Pfam 166; DisProt 35; IDEAL 1. | `biolink:close_match`; `biolink:same_as` only for same IDPO class. | Round-1 notes say DisProt/IDEAL are pivoted by IDPO; Pfam disorder signatures can use Phase 2 + Tier 2. |
| `SEQ_REPEAT` | Linear repeat unit signature, HMM/profile, or repeated residue intervals. | Same signature via Phase 1; otherwise `J >= 0.90` plus Tier-2 repeated-region overlap `>= 0.80`. Containment for family/subfamily. | 2,073 records: Pfam 1,560; InterPro 390; NCBIfam 123. | `biolink:close_match`; `biolink:narrow_match`; `biolink:overlaps`. | Phase 1 and Phase 2 + Tier 2. Distinct from `MIXED_STRUCTURAL_REPEAT`. |
| `SEQ_COMPOSITION` | Whole-sequence or region composition vector / bias class. | Same grounded composition class; numeric profiles would need cosine or thresholded feature equality. | 0 records. | `biolink:close_match`. | GAP: enum exists, no records and no composition-vector slot. |
| `SEQ_CONSERVATION` | Conserved sequence region/profile and member/region coordinates. | `J >= 0.90` plus Tier-2 reciprocal region overlap `>= 0.80`; containment `C >= 0.90` for narrower conserved segment. | 775 records: InterPro. | `biolink:close_match`; `biolink:narrow_match`. | Phase 2 + Tier 2 possible; single current source limits cross-source edges. |
| `SEQ_EPITOPE` | Linear epitope peptide interval and immune-context grounding. | Same peptide sequence and same antigen interval; partial interval overlap is related, not equivalent. | 0 records. | `biolink:close_match`; `biolink:overlaps`. | GAP: enum exists, no records. |
| `SEQ_PTM_SITE` | Generic PTM site class, motif, or modified residue coordinate. | Same specific modification anchor if known; otherwise same motif/coordinate with reciprocal overlap for localized examples. | 1,251 records: PSI-MOD 1,194; ELM 40; InterPro 17. | `biolink:close_match`; `biolink:narrow_match` for specific PTM under generic PTM site. | Phase 1 for InterPro-integrated motifs; Phase 2 + Tier 2 for localized signatures; ontology-anchor comparison for PSI-MOD. |
| `SEQ_MODIFIED_RESIDUE` | Modification ontology anchor and residue coordinate in examples. | Same PSI-MOD/MOD/RESID/Unimod-style anchor; for instances same coordinate and residue. | 618 records: PSI-MOD 587; PROSITE 31. | `biolink:same_as` for same modification CURIE; otherwise `biolink:close_match`. | Ontology-anchor comparison; Phase 1/2 for PROSITE signatures where applicable. |
| `SEQ_GLYCOSYLATION_SITE` | Glycosylation subtype anchor or glycosylation motif/coordinate. | Same glyco subtype anchor; for motifs, exact/compatible pattern and Tier-2 region overlap. | 85 records: PSI-MOD 83; PROSITE 2. | `biolink:close_match`; `biolink:narrow_match`. | Ontology anchor plus Phase 1/2 for PROSITE signatures. |
| `SEQ_LIPIDATION_SITE` | Lipidation subtype anchor and modified residue coordinate. | Same lipidation anchor; instance same residue coordinate. | 40 records: PSI-MOD. | `biolink:same_as` for identical anchor; `biolink:close_match` otherwise. | Ontology-anchor comparison; no overlay currently. |
| `SEQ_CROSSLINK_SITE` | Non-disulfide crosslink subtype anchor and residue-pair coordinates. | Same crosslink chemistry and same residue pair for strict instance equivalence. | 69 records: PSI-MOD 67; PROSITE 2. | `biolink:close_match`; `biolink:has_part` for residue participants if materialized. | Ontology anchor plus Phase 1/2 for PROSITE signatures. |
| `SEQ_OTHER` | Undefined sequence representation. | No safe operator until records are reclassified. | 0 records. | None. | GAP. |

### STRUCTURE axis

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `STRUCT_CLASS` | Structural class label / hierarchy node plus optional representative-domain distribution. | Same source rank and same normalized class; cross-tree close match only when representatives agree structurally. | 17 records: SCOPe 12; CATH 5. | `biolink:close_match`; `biolink:narrow_match` if one class is finer. | Phase 3 conceptually; no `structural.tsv` currently. |
| `STRUCT_ARCHITECTURE` | CATH/ECOD architecture label: gross secondary-structure arrangement ignoring connectivity. | Same architecture label when source-native; cross-source requires representative structure set agreement or Foldseek class-level clustering. TM-score is less decisive at this high rank; use `>= 0.50` only as candidate support. | 64 records: CATH 43; ECOD 21. | `biolink:close_match`; `biolink:narrow_match` for source hierarchy containment. | Phase 3 pipeline-ready; GAP in data because no geometry slot and no `structural.tsv`. |
| `STRUCT_TOPOLOGY` | Topology/connectivity class and representative domain geometry. | Foldseek TM-score `>= 0.50` across representatives for same fold/topology candidate; stronger support if many members agree. | 5,427 records: ECOD 3,955; CATH 1,472. | `biolink:close_match`; `biolink:narrow_match` for containment. | Phase 3 pipeline-ready via `build_structural_equivalence.py`, but schema lacks geometry pointer. |
| `STRUCT_HOMOLOGOUS_SUPERFAMILY` | Evolutionary structural superfamily: representative structures plus member sets. | Foldseek TM-score `>= 0.70` for superfamily-level structural match, plus member overlap where queryable. | 20,845 records: CATH 6,631; ECOD 6,178; InterPro 3,510; SCOPe 2,368; CDD 1,267; Pfam 891. | `biolink:close_match`; `biolink:narrow_match` / `biolink:member_of` for subfamily containment. | Phase 1 for InterPro-integrated signatures; Phase 2; Phase 3 for structural sources. |
| `STRUCT_FOLD` | Representative domain geometry: PDB/AlphaFold/TED domain range, optional 3Di/contact-map descriptor. | Foldseek TM-score `>= 0.50` for same fold, `>= 0.70` for superfamily-like stronger relation. | 55,735 records: ECOD 34,959; TED 13,860; SCOPe 6,916. | `biolink:close_match`; rarely `biolink:same_as` only for same structure/range and same source semantics. | Phase 3. `data/analysis/structural_reps.tsv` has 13,860 TED reps, but no `data/equivalence/structural.tsv` is present. |
| `STRUCT_DOMAIN` | Domain signature/member regions and, when structural, representative domain geometry. | Phase 1 mapping; Phase 2 `J >= 0.90` plus Tier-2 reciprocal region overlap `>= 0.80` on `>= 0.50` sampled shared proteins; structural representatives use Foldseek `>= 0.50`. | 135,044 records: NCBIfam 38,271; CDD 32,126; Pfam 27,961; InterPro 21,357; SCOPe 13,514; PROSITE 1,445; MEROPS 370. | `biolink:close_match`; `biolink:narrow_match`; `biolink:overlaps` for same protein but different region. | Phase 1, Phase 2 + Tier 2, Phase 3 where reps exist. |
| `STRUCT_SECONDARY` | Secondary-structure string/topology: DSSP/STRIDE 8- or 3-state string, SS-element order, or Foldseek 3Di-derived local alphabet. | Exact normalized SS grammar for named motifs; for assigned intervals, same DSSP/STRIDE state over reciprocal interval overlap `>= 0.80`; topology edit distance `<= 0.10` for close candidates. | 8 records: LinkML LocalStructuralFeature-derived generic motifs only. | `biolink:close_match`; `biolink:narrow_match`; `biolink:overlaps` for shared elements. | GAP: no representation slot and no source-derived SS-element taxonomy. |
| `STRUCT_QUATERNARY` | Oligomeric state / assembly stoichiometry and symmetry. | Same stoichiometry and assembly type; symmetry match for strict equivalence. | 0 records. | `biolink:close_match`; `biolink:has_part` for subunits if modeled. | GAP: enum exists, no records. |
| `STRUCT_INTERFACE` | Pairwise interface geometry: partner IDs/chains, residue contacts, buried area/contact map. | Same partner classes and contact-map overlap/Jaccard threshold; no current slot. | 1 record: LinkML LSF. | `biolink:close_match`; `biolink:has_part`; `biolink:interacts_with` if entity edges are materialized. | GAP. |
| `STRUCT_ACTIVE_SITE` | Catalytic-site residue set, geometry, M-CSA mechanism or InterPro active-site signature. | Same catalytic residue set and reaction/mechanism anchor; for signatures, Phase 2 + Tier 2 same-region overlap. | 1,137 records: M-CSA 1,003; InterPro 133; LinkML LSF 1. | `biolink:close_match`; `biolink:narrow_match`; `biolink:has_part` for residues. | Phase 1/2 + Tier 2 for InterPro signatures; ontology/mechanism anchor for M-CSA; geometry slot is missing. |
| `STRUCT_BINDING_SITE` | Binding-site residue set, ligand/cofactor/nucleic-acid anchor, and local geometry. | Same ligand class plus same residue-region overlap `>= 0.80`; stricter if same residue set/contact geometry. | 83 records: InterPro 82; LinkML LSF 1. | `biolink:close_match`; `biolink:has_part`; `biolink:overlaps`. | Phase 1/2 + Tier 2 for signatures; geometry/contact representation is missing. |
| `STRUCT_ALLOSTERIC_SITE` | Regulatory ligand/site residue set and conformational coupling target. | Same allosteric ligand/site class plus region overlap `>= 0.80`; relation to regulated active site needed for strict match. | 0 records. | `biolink:close_match`; `biolink:regulates` if materialized. | GAP. |
| `STRUCT_DISULFIDE` | Cys-Cys residue pair and bond pattern. | Same two cysteine positions or same disulfide topology; pattern containment for partial families. | 1 record: LinkML LSF. | `biolink:close_match`; `biolink:has_part`. | GAP for cross-source comparison; coordinate-pair slot absent. |
| `STRUCT_METAL_SITE` | Metal identity plus coordinating residue geometry. | Same metal ChEBI and same coordination residue set/geometry. | 1 record: LinkML LSF. | `biolink:close_match`; `biolink:has_part`; `biolink:has_participant`. | GAP; no geometry/coordination slot. |
| `STRUCT_CAVITY` | Pocket/channel geometry and residue lining/contact map. | Pocket-volume/shape/contact overlap; candidate thresholds need a source-specific pocket representation. | 5 records: LinkML LSF. | `biolink:close_match`; `biolink:overlaps`. | GAP; no pocket geometry slot. |
| `STRUCT_SYMMETRY` | Symmetry group/order and assembly/internal-repeat mapping. | Same point/space symmetry class and same order; geometry alignment for internal repeats. | 0 records. | `biolink:close_match`; `biolink:has_part`. | GAP: enum exists, no records. |
| `STRUCT_DYNAMICS` | PATO quality anchor or motion/flexibility class; optional conformational-state pair. | Same PATO anchor; numeric dynamic profile would need RMSF/ensemble representation, not present. | 13 records: PATO 12; LinkML LSF 1. | `biolink:same_as` for identical PATO; `biolink:close_match` for source analogues. | Ontology-anchor comparison; no numeric dynamics operator. |
| `STRUCT_STABILITY` | PATO/curated stability quality and condition/direction. | Same stability quality plus same condition and direction; condition containment gives narrow/broad match. | 36 records: curated 33; PATO 3. | `biolink:close_match`; `biolink:narrow_match`. | Ontology/curated-anchor comparison. |
| `STRUCT_SURFACE` | PATO surface/physicochemical quality; future surface maps. | Same PATO anchor; map overlap would require surface representation. | 13 records: PATO. | `biolink:same_as` for identical PATO; `biolink:close_match`. | Ontology-anchor comparison; no surface-map operator. |
| `STRUCT_OTHER` | Undefined structural representation. | No safe operator until reclassified. | 0 records. | None. | GAP. |

### SEQUENCE_STRUCTURE axis

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `MIXED_TRANSMEMBRANE` | Hydrophobic sequence interval plus membrane topology and helix/strand structural state. | Same topology class plus interval overlap `>= 0.80`; helix-vs-strand must agree. | 0 records. | `biolink:close_match`; `biolink:overlaps`. | GAP: enum exists, no records. |
| `MIXED_COILED_COIL` | Heptad-repeat sequence signature plus supercoiled helical bundle topology. | Phase 1/2 member and region overlap for Pfam signatures; future SS/topology grammar should match heptad register and coiled-coil oligomer/topology. | 314 records: Pfam. | `biolink:close_match`; `biolink:narrow_match`. | Phase 1 possible where Pfam maps to InterPro; Phase 2 + Tier 2 possible. See coiled-coil resolution below. |
| `MIXED_STRUCTURAL_REPEAT` | Repeat unit sequence/structure periodicity and repeat topology/class. | Same RepeatsDB Class/Topology/Fold/Clan level; structural reps use Foldseek `>= 0.50`; repeat-unit interval overlap for instances. | 122 records: RepeatsDB. | `biolink:close_match`; `biolink:narrow_match`; `biolink:member_of`. | Phase 3 conceptually; single current source limits cross-source edges. |
| `MIXED_OTHER` | Undefined sequence-structure representation. | No safe operator until reclassified. | 0 records. | None. | GAP. |

### FUNCTION axis

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `FUNC_ENZYMATIC_ACTIVITY` | Ontology/reaction anchors: EC leaf, Rhea reaction, GO molecular function, ChEBI participants. | Same Rhea is strict reaction match; same EC leaf plus matching Rhea/participant set is merge candidate; generic GO anchors alone are not identity. | 26,003 records: Rhea 18,558; ExPASy ENZYME 7,375; METPO 70. | `biolink:close_match`; `biolink:same_as` only for same reaction identifier; `biolink:has_participant` for ChEBI. | Tier 4 ontology-anchor comparison in prior work; no dedicated overlay script beyond mapped xrefs. |
| `FUNC_BINDING_CAPACITY` | Entry-level binding target class: GO MF binding term and/or ChEBI/entity anchor. | Same specific ligand/entity anchor; avoid generic GO:0005515-like anchors as identity. | 0 records in docs shards. | `biolink:close_match`; `biolink:has_participant`. | GAP: enum exists, no current records. |
| `FUNC_COFACTOR_REQUIREMENT` | Cofactor ChEBI/prosthetic-group anchor and role. | Same ChEBI cofactor and role; broader ChEBI class gives `narrow_match`. | 0 records. | `biolink:close_match`; `biolink:has_participant`; `biolink:narrow_match`. | GAP: enum exists, no current records. |
| `FUNC_LOCALIZATION` | Subcellular localization anchor: GO CC or UniProt SubCell. | Same specific cellular component; partonomy should be `narrow_match`/`part_of` semantics, not same-as. | 0 records. | `biolink:close_match`; `biolink:narrow_match`. | GAP: enum exists, no current records. |
| `FUNC_ENVIRONMENTAL_RESPONSE` | GO BP/METPO environmental-response anchor plus condition. | Same response/condition anchor; condition hierarchy gives narrower/broader relation. | 48 records: METPO. | `biolink:close_match`; `biolink:narrow_match`. | Ontology-anchor comparison; no overlay currently. |
| `FUNC_INTERACTION_PARTNER` | Interaction type / partner class anchor, currently PSI-MI interaction type branch. | Same specific PSI-MI interaction type; if future partner entities are added, require same partner class. | 146 records: PSI-MI. | `biolink:close_match`; `biolink:interacts_with` for entity edges. | Ontology-anchor comparison; no overlay currently. |
| `FUNC_TRANSPORT` | TCDB transport class/family plus transported substrate ChEBI where present. | Same TCDB family or same substrate+mechanism; TCDB hierarchy gives `narrow_match`/`member_of`. | 2,285 records: TCDB. | `biolink:close_match`; `biolink:narrow_match`; `biolink:has_participant`. | Tier 4 / source hierarchy; prior work notes future TCDB-Pfam/InterPro close matches. |
| `FUNC_RESISTANCE` | CARD/ARO resistance determinant/mechanism/drug class anchor. | Same ARO term; same drug ChEBI and mechanism for cross-source candidates. | 7,451 records: CARD/ARO. | `biolink:close_match`; `biolink:narrow_match`. | Ontology-anchor comparison; no cross-source overlay currently. |
| `FUNC_PATHWAY` | Pathway/module anchor: Reactome now, future KEGG/MetaCyc/GO BP. | Same pathway stable identifier; pathway hierarchy may be partonomy, so child-parent is not equivalence. | 2,883 records: Reactome. | `biolink:close_match`; `biolink:narrow_match` or `biolink:part_of` where hierarchy is partonomy. | Ontology/source-anchor comparison; no cross-source overlay currently. |
| `FUNC_ORTHOLOG_GROUP` | Orthologous group/family membership set and source category. | Member-set overlap `J >= 0.90` for close/merge candidate; containment `C >= 0.90` for `narrow_match`; COG category membership should be `member_of`. | 9,728 records: COG 4,903; CDD 4,825. | `biolink:close_match`; `biolink:narrow_match`; `biolink:member_of`. | Phase 2 member overlap; hierarchy relation audit from prior review. |

### EVOLUTION axis

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `EVO_CONSERVATION` | Conservation state class plus optional NCBITaxon scope. | Same state and same taxon scope; broader/narrower taxon scopes give `narrow_match`. | 3 curated records. | `biolink:close_match`; `biolink:narrow_match`. | GAP for cross-source overlay; curated taxonomy only. |
| `EVO_PANGENOME` | Pangenome partition class plus species/clade scope. | Same partition definition and same taxon scope; threshold definitions must be source-specific if PPanGGOLiN/Roary-like outputs are added. | 6 curated records. | `biolink:close_match`; `biolink:narrow_match`. | GAP for cross-source overlay; curated taxonomy only. |

### Administrative categories

| category | comparable representation | comparison operator + threshold | sources providing it now | Biolink edge on match | existing Phase/Tier or gap |
|---|---|---|---|---|---|
| `UPPER` | Administrative/documentation grouping. | Do not compare as biological trait equivalence. | 1,980 records: PROSITE documentation groups. | Prefer `biolink:member_of` from signatures to documentation/group nodes, not `same_as`. | Prior hierarchy review flags PROSITE PDOC as grouping, not subclass. |
| `OTHER` | Undefined category. | No safe operator. | 0 records. | None. | GAP. |

## 2. Minimal LinkML representation-slot additions

The current schema can hold sequence patterns and example residue coordinates,
but not the comparable representations needed for structural categories. The
minimal closed-mode-clean change is to add two optional, inlined,
multivalued representation classes to `ProteinTraitRecord`. This keeps records
valid when absent, avoids broad free-text overloading, and lets the existing
operators read representations directly.

### Secondary-structure representation

Recommended slot on `ProteinTraitRecord`:

```yaml
secondary_structure_representations:
  description: >-
    Comparable secondary-structure representation for STRUCT_SECONDARY and
    related local structural motifs: DSSP/STRIDE 3- or 8-state strings,
    normalized SS-element topology strings, or local structural alphabets.
  multivalued: true
  inlined_as_list: true
  range: SecondaryStructureRepresentation
```

Recommended class:

```yaml
SecondaryStructureRepresentation:
  attributes:
    method:
      description: Assignment method or source, e.g. DSSP, STRIDE, PDBsum/PROMOTIF.
      range: string
      required: true
    state_alphabet:
      description: DSSP_8, DSSP_3, STRIDE_8, STRIDE_3, TOPOLOGY, FOLDSEEK_3DI.
      range: string
      required: true
    ss_string:
      description: Per-residue secondary-structure string when available.
      range: string
    topology_string:
      description: Normalized element grammar, e.g. E-turn-E, H-loop-H, beta-alpha-beta.
      range: string
    residue_start:
      range: integer
      minimum_value: 1
    residue_end:
      range: integer
      minimum_value: 1
    structure_ref:
      description: PDB/AlphaFold/TED/CATH domain reference used for assignment.
      range: string
    evidence_source:
      description: CURIE, URL, or source file for the assignment.
      range: string
```

Population:

- For source-derived SS records, run DSSP (`mkdssp`) or STRIDE on a PDB or
  AlphaFold representative and store both the raw per-residue string and a
  normalized topology string.
- For current class-level records such as `BETA_HAIRPIN`, store a topology
  string even when no single structure is canonical: `E-turn-E` for beta
  hairpin, `E-bulge-E` for beta bulge, `helix-cap` for helix cap, etc.
- For super-secondary motifs, normalize synonyms to a small grammar:
  `H-loop-H`, `H-turn-H`, `E-turn-E`, `E-H-E`, `E-E-E-E`, `H-loop-H-Ca-binding`
  and similar.

Comparison:

- Strict class match: exact normalized `topology_string` plus compatible
  `state_alphabet`.
- Instance match: same DSSP/STRIDE state or compatible 3-state reduction over
  reciprocal residue overlap `>= 0.80`.
- Close candidate: normalized topology edit distance `<= 0.10`, or local
  SS-string alignment identity `>= 0.80` over `>= 0.80` of the shorter string.

### 3D-geometry representation

Recommended slot on `ProteinTraitRecord`:

```yaml
structural_geometry_representations:
  description: >-
    Comparable 3D geometry pointer for STRUCT_FOLD, STRUCT_TOPOLOGY,
    STRUCT_HOMOLOGOUS_SUPERFAMILY, STRUCT_DOMAIN, and local structural-site
    records.
  multivalued: true
  inlined_as_list: true
  range: StructuralGeometryRepresentation
```

Recommended class:

```yaml
StructuralGeometryRepresentation:
  attributes:
    representative_structure:
      description: PDB, AlphaFoldDB, TED, CATH, SCOPe, or ECOD representative.
      range: string
      required: true
    chain_id:
      range: string
    residue_start:
      range: integer
      minimum_value: 1
    residue_end:
      range: integer
      minimum_value: 1
    residue_range:
      description: String range for discontinuous domains, e.g. 2-80_100-139.
      range: string
    geometry_kind:
      description: DOMAIN_REPRESENTATIVE, SITE_RESIDUE_SET, CONTACT_MAP, SURFACE_PATCH, POCKET.
      range: string
      required: true
    foldseek_3di:
      description: Optional Foldseek 3Di descriptor or pointer to a sidecar.
      range: string
    contact_map_ref:
      description: Optional sidecar path/URI for a contact map or pocket graph.
      range: string
    evidence_source:
      range: string
```

Population:

- Convert the existing `data/analysis/structural_reps.tsv` TED manifest
  (`curie`, `af_acc`, `range`) into per-record `representative_structure` and
  range references, or keep it as a sidecar and link to it through this slot.
- Add CATH/SCOPe/ECOD representative domain rows to the same manifest and then
  populate this slot from the manifest.
- For sites/cavities/interfaces, populate residue sets or contact-map sidecar
  pointers rather than embedding large matrices in YAML.

Comparison:

- `STRUCT_FOLD` / `STRUCT_TOPOLOGY`: Foldseek TM-score `>= 0.50` emits
  `biolink:close_match`.
- `STRUCT_HOMOLOGOUS_SUPERFAMILY`: Foldseek TM-score `>= 0.70` emits
  superfamily-level `biolink:close_match`.
- Sites/cavities/interfaces: compare contact/residue-set overlap; until those
  slots exist, these categories are not genuinely comparable across sources.

## 3. Secondary-structure and super-secondary trait taxonomy

### Current 8 mapped to taxonomy

| existing record | current path | current grounding | recommended role |
|---|---|---|---|
| `POLYPEPTIDE_STRUCTURAL_MOTIF` | `data/traits/structure/secondary/polypeptide-structural-motif.yaml` | `SO:0001079`, `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep as parent for local SS/super-secondary motifs that do not form stable globular units. |
| `ASX_MOTIF` | `data/traits/structure/secondary/asx-motif.yaml` | `SO:0001106`, `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep under local structural motifs; represent with side-chain/backbone topology grammar. |
| `BETA_BULGE` | `data/traits/structure/secondary/beta-bulge.yaml` | `SO:0001107`, `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep under beta local motifs; represent as disrupted beta-pair topology. |
| `BETA_HAIRPIN` | `data/traits/structure/secondary/beta-hairpin.yaml` | `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep; add topology `E-turn-E`. |
| `COILED_COIL` | `data/traits/structure/secondary/coiled-coil.yaml` | `SO:0001080`, `valuesets:LocalStructuralFeature`, `SO:0001114` | Double-home issue: use `MIXED_COILED_COIL` as canonical home for coiled-coil trait records; retain this only as legacy/generic structural-motif bridge or deprecate in a future migration. |
| `HELIX_CAP` | `data/traits/structure/secondary/helix-cap.yaml` | `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep under helix local motifs; represent as N-cap/C-cap grammar. |
| `KINK` | `data/traits/structure/secondary/kink.yaml` | `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep under helix/local bend motifs; represent as interrupted helix geometry/topology. |
| `NEST` | `data/traits/structure/secondary/nest.yaml` | `SO:0001120`, `valuesets:LocalStructuralFeature`, `SO:0001114` | Keep under local structural motifs; represent as two-residue anion-binding concavity grammar. |

### Coiled-coil resolution

Pick one canonical home: `MIXED_COILED_COIL`.

Reason: the schema itself defines `SEQUENCE_STRUCTURE` as the axis for traits
meaningful in both sequence and structure, and its examples include coiled
coils. Current data confirms this: `MIXED_COILED_COIL` has 314 Pfam records
under `data/traits/mixed/coiled_coil/pfam/`, while `STRUCT_SECONDARY` has one
generic `COILED_COIL` class-level motif. Coiled coils are not just generic
secondary-structure elements; comparable representation requires both heptad
repeat/register and supercoiled helical bundle topology.

Recommended future cleanup, without doing it in this review:

- Keep source-derived coiled-coil families in `MIXED_COILED_COIL`.
- Treat `proteintraitsmech:COILED_COIL` as a legacy/generic bridge to the
  mixed category, or deprecate/remap it to `MIXED_COILED_COIL`.
- Do not seed new source-derived coiled-coil traits under `STRUCT_SECONDARY`.

### Complete taxonomy to seed

The taxonomy below separates elementary secondary-structure states from local
motifs and super-secondary motifs. `STRUCT_SECONDARY` remains the category for
element/topology grammar; `STRUCT_TOPOLOGY`/`STRUCT_FOLD` remain the categories
for whole-domain topology/fold classes.

| proposed trait | parent | grounding / representation | candidate sources | seeding recipe | existing mapping |
|---|---|---|---|---|---|
| secondary-structure element | `POLYPEPTIDE_STRUCTURAL_MOTIF` | DSSP/STRIDE 3- or 8-state state class | DSSP, STRIDE, PDBsum, CATH SS | Add parent class; assign from DSSP/STRIDE states on representative structures. | Missing. |
| alpha helix | secondary-structure element | DSSP H / STRIDE helix; topology token `H` | DSSP, STRIDE, PDBsum, CATH SS | Seed one class; examples from PDB/AlphaFold assignments. | Missing. |
| 3_10 helix | secondary-structure element | DSSP G; topology token `G` or helix subtype | DSSP, STRIDE | Seed as helix subtype. | Missing. |
| pi helix | secondary-structure element | DSSP I; topology token `I` or helix subtype | DSSP, STRIDE | Seed as helix subtype. | Missing. |
| beta strand | secondary-structure element | DSSP E strand; topology token `E` | DSSP, STRIDE, PDBsum, CATH SS | Seed class; use strand interval assignments. | Missing. |
| beta bridge | secondary-structure element | DSSP B isolated bridge | DSSP, STRIDE | Seed class; useful bridge between strand and local motif. | Missing. |
| beta sheet | secondary-structure arrangement | ordered strand set with H-bond topology | DSSP, STRIDE, PDBsum, CATH SS | Seed as arrangement; compare strand-order and pairing graph. | Missing. |
| turn | local SS element | DSSP T; turn subtype if source provides | DSSP, STRIDE, PDBsum/PROMOTIF | Seed umbrella plus typed children. | Missing. |
| beta turn types I/I'/II/II'/VIa/VIb/VIII | turn | PROMOTIF/PDBsum turn classification | PDBsum/PROMOTIF, DSSP-derived geometry | Seed subtypes with topology and phi/psi class notes. | Missing. |
| gamma turn | turn | PROMOTIF/PDBsum turn classification | PDBsum/PROMOTIF | Seed subtype. | Missing. |
| alpha turn | turn | PROMOTIF/PDBsum turn classification | PDBsum/PROMOTIF | Seed subtype. | Missing. |
| pi turn | turn | PROMOTIF/PDBsum turn classification | PDBsum/PROMOTIF | Seed subtype. | Missing. |
| bend | local SS element | DSSP S / bend geometry | DSSP, STRIDE | Seed as local element; compare interval/state. | Missing; related to `KINK` but not identical. |
| loop / coil | local SS element | DSSP blank/C or 3-state coil | DSSP, STRIDE | Seed as residual state only; avoid overusing as trait equivalence. | Missing. |
| polyproline II helix | helix subtype | PPII helix geometry, not standard DSSP core state | PDBsum/PROMOTIF, DSSP-derived geometry | Seed if source exposes PPII; compare by geometry/topology. | Missing. |
| helix cap | helix local motif | N-cap/C-cap topology | PDBsum/PROMOTIF, DSSP/STRIDE | Add `secondary_structure_representations.topology_string`. | Existing `HELIX_CAP`. |
| helix kink | helix local motif | interrupted helix geometry | DSSP/STRIDE plus bend/kink detection | Normalize `KINK` as helix/local bend motif where applicable. | Existing `KINK`. |
| asx motif | local structural motif | Asn/Asp side-chain nucleated 5-residue motif | PDBsum/PROMOTIF/local structural feature vocabularies | Add motif grammar and representative examples. | Existing `ASX_MOTIF`. |
| nest | local structural motif | two-residue anion-binding concavity | PDBsum/PROMOTIF/local structural feature vocabularies | Add motif grammar and examples. | Existing `NEST`. |
| beta bulge | beta local motif | beta H-bond disruption | PDBsum/PROMOTIF, DSSP-derived sheet pairing | Add disrupted beta-pair topology. | Existing `BETA_BULGE`. |
| beta hairpin | super-secondary beta motif | `E-turn-E` | PDBsum/PROMOTIF, CATH SS, DSSP/STRIDE | Seed from paired adjacent antiparallel strands and turn loop. | Existing `BETA_HAIRPIN`. |
| beta meander | super-secondary beta motif | repeated adjacent antiparallel strand topology | PDBsum/PROMOTIF, CATH SS, super-secondary motif libraries | Seed as strand-pairing grammar. | Missing. |
| Greek key | super-secondary beta motif | four-strand beta topology / connectivity | CATH topology labels, PDBsum/PROMOTIF, super-secondary motif libraries | Seed under `STRUCT_SECONDARY` only for local motif; whole-domain Greek-key topology remains `STRUCT_TOPOLOGY`. | Missing; term appears in schema description for `STRUCT_TOPOLOGY`. |
| jelly roll | super-secondary beta motif / topology | beta-sandwich/barrel-like strand topology | CATH/SCOPe/ECOD, PDBsum/PROMOTIF | Seed local motif only if not a whole-domain fold; otherwise classify as `STRUCT_TOPOLOGY`/`STRUCT_FOLD`. | Missing; term appears in schema description for `STRUCT_TOPOLOGY`. |
| beta-alpha-beta motif | super-secondary mixed motif | `E-H-E` or `beta-alpha-beta` grammar | PDBsum/PROMOTIF, CATH SS, super-secondary motif libraries | Seed from adjacent strand-helix-strand topology. | Missing. |
| helix-turn-helix | super-secondary helix motif | `H-turn-H` grammar | PDBsum/PROMOTIF, CATH SS, InterPro/Pfam domain definitions as candidates | Seed as local motif; if sequence family/domain-specific, link rather than merge with domains. | Missing. |
| helix-loop-helix | super-secondary helix motif | `H-loop-H`; EF-hand is specific calcium-binding subtype | PDBsum/PROMOTIF, CATH SS, InterPro/Pfam candidates | Seed umbrella; compare exact topology plus optional ligand role. | Missing. |
| EF-hand | super-secondary motif plus metal-binding function | `H-loop-H` calcium-binding topology; Ca participant | PDBsum/PROMOTIF, CATH/Pfam/InterPro candidates | Seed as `STRUCT_SECONDARY` only for local motif; related metal-binding site is `STRUCT_METAL_SITE`. | Missing. |
| helix-hairpin-helix | super-secondary helix motif | `H-hairpin-H` / `H-loop-H` specialized grammar | PDBsum/PROMOTIF, CATH SS, InterPro/Pfam candidates | Seed as motif; do not collapse with DNA-repair domains that contain it. | Missing. |
| alpha-alpha corner / helical hairpin | super-secondary helix motif | two-helix packing grammar | PDBsum/PROMOTIF, CATH SS | Seed as local topology. | Missing. |
| coiled coil | mixed sequence-structure motif | heptad repeat plus supercoiled helical bundle | Pfam, InterPro, PDBsum, coiled-coil predictors | Canonical category is `MIXED_COILED_COIL`; do not seed new `STRUCT_SECONDARY` records. | Existing double home: `STRUCT_SECONDARY` generic plus 314 Pfam `MIXED_COILED_COIL`. |
| beta barrel as local/super-secondary topology | super-secondary beta topology, if sub-domain | closed beta-strand barrel grammar | CATH/SCOPe/ECOD, PDBsum/CATH SS | Use `STRUCT_SECONDARY` only for local repeated-barrel motif; whole-domain beta barrels are `STRUCT_TOPOLOGY`/`STRUCT_FOLD`. | Missing. |
| beta helix / beta solenoid | repeated super-secondary motif | periodic beta-strand solenoid grammar | RepeatsDB, CATH/SCOPe/ECOD, PDBsum | Usually `MIXED_STRUCTURAL_REPEAT` when periodic; link to `STRUCT_SECONDARY` motif grammar. | Missing in `STRUCT_SECONDARY`; RepeatsDB covers structural repeats. |
| alpha solenoid | repeated super-secondary motif | periodic helical repeat grammar | RepeatsDB, CATH/SCOPe/ECOD | Prefer `MIXED_STRUCTURAL_REPEAT` for source-derived periodic families. | Missing in `STRUCT_SECONDARY`; RepeatsDB covers structural repeats. |

Grounding recommendations:

- DSSP and STRIDE provide assignment states and strings; they should ground
  representation values, not necessarily ontology identity by themselves.
- `POLYPEPTIDE_STRUCTURAL_MOTIF` and the LocalStructuralFeature/SO xrefs already
  present in the 8 records provide the current local motif grounding.
- PATO is appropriate for qualities such as stability, dynamics, and surface
  categories, not for most secondary-structure element identity.
- SO xrefs are already present on several LocalStructuralFeature-derived
  records and can continue to ground local structural motif classes where SO
  terms exist.

## 4. How comparison plugs into the existing equivalence pipeline

The pipeline convention to preserve is:

```text
subject<TAB>predicate<TAB>object<TAB>relation_source
```

Every new comparison should emit a TSV under `data/equivalence/`; no bulk edge
materialization into individual trait YAMLs is needed. `scripts/build_docs_index.py`
will load the overlay bidirectionally into `eq`.

### Existing overlays

- Phase 1: `scripts/build_equivalence.py` reads InterPro member-list mappings
  and emits `data/equivalence/cross_source.tsv`. Current data: 24,299
  `biolink:close_match` edges.
- Phase 2: `scripts/build_member_overlap.py` computes UniProt member-set
  Jaccard/containment and writes review candidates; `--emit-edges` is guarded
  for non-localized categories.
- Tier 2: `scripts/verify_region_overlap.py` confirms localized candidates by
  reciprocal region overlap and writes `data/equivalence/member_overlap.tsv`.
  Current data: 2 `biolink:narrow_match` edges.
- Phase 3: `scripts/build_structural_equivalence.py` derives
  `data/analysis/structural_reps.tsv` and can emit
  `data/equivalence/structural.tsv` after Foldseek runs. Current repository has
  the 13,860-row TED manifest plus header, but no `structural.tsv`.
- Tier 5: `scripts/embed_records.py` and `scripts/embed_neighbors.py` generate
  semantic review candidates only; they should not emit equivalence edges
  automatically.

### New secondary-structure overlay

Add a new script, conceptually:

```text
just build-secondary-structure-equivalence *args:
    python3 scripts/build_secondary_structure_equivalence.py {{args}}
```

Inputs:

- `secondary_structure_representations` from records, once added; until then,
  a sidecar manifest can be used:
  `data/analysis/secondary_structure_reps.tsv` with columns such as
  `curie`, `method`, `state_alphabet`, `structure_ref`, `residue_range`,
  `ss_string`, `topology_string`.
- Optional DSSP/STRIDE outputs cached under `data/raw/secondary_structure/`.

Operators:

- Exact normalized topology string match (`E-turn-E`, `H-loop-H`,
  `E-H-E`, etc.) emits `biolink:close_match`.
- Topology containment emits `biolink:narrow_match`; for example, a specific
  beta-turn subtype is narrower than `turn`, and EF-hand is narrower than
  helix-loop-helix plus calcium-binding context.
- Same assigned state over reciprocal residue overlap `>= 0.80` emits
  `biolink:close_match` for source-derived element entries.
- Partial overlap without matching grammar emits `biolink:overlaps`, if the
  team wants non-equivalence relatedness in the browser; otherwise keep it in
  review candidates only.

Output:

```text
data/equivalence/secondary_structure.tsv
subject  predicate  object  relation_source
proteintraitsmech:BETA_HAIRPIN  biolink:close_match  <source-id>  ss-topology:E-turn-E
```

Guardrail:

- Do not compare `STRUCT_SECONDARY` entries by text labels alone. Require a
  DSSP/STRIDE state string, normalized topology string, or explicit curated
  motif grounding.

### Structural geometry overlay extension

Extend `scripts/build_structural_equivalence.py` rather than creating a
parallel structural script:

- Promote `data/analysis/structural_reps.tsv` from TED-only to a cross-source
  manifest containing TED, CATH, SCOPe, and ECOD representatives.
- Optionally populate `structural_geometry_representations` from this manifest.
- Emit `data/equivalence/structural.tsv` with
  `relation_source=foldseek-tm<score>-fold` for TM-score `>= 0.50` and
  `relation_source=foldseek-tm<score>-superfamily` for TM-score `>= 0.70`.

### Member/region overlay categories

Keep using the existing Phase 2 + Tier 2 path for localized sequence and
signature categories:

- `SEQ_MOTIF`, `SEQ_REPEAT`, `SEQ_CONSERVATION`, `SEQ_PTM_SITE`,
  `SEQ_MODIFIED_RESIDUE`, `SEQ_GLYCOSYLATION_SITE`, `SEQ_CROSSLINK_SITE`.
- `STRUCT_DOMAIN`, `STRUCT_ACTIVE_SITE`, `STRUCT_BINDING_SITE`,
  `STRUCT_METAL_SITE` where signatures have member/coordinate output.
- `MIXED_COILED_COIL` and `MIXED_TRANSMEMBRANE` once seeded.

The existing localized-feature trap remains the key safety rule: high member
Jaccard alone is not equivalence unless same-region overlap is confirmed.

### Function/evolution overlays

For function categories, add small anchor overlay builders rather than using
embedding similarity:

- `build_function_anchor_equivalence.py`: EC/Rhea/GO/ChEBI/ARO/TCDB/COG anchors
  emit `close_match`, `narrow_match`, or `member_of` according to the category
  operator above.
- Avoid asserting equivalence from generic anchors such as broad GO binding
  terms. The operator must agree with the category representation.

For evolution categories, wait until records carry taxon scope and source
threshold definitions; current curated classes are not enough for cross-source
equivalence.

## 5. Oddities and risks

1. `STRUCT_SECONDARY` is underrepresented relative to the now-shared
   STRUCTURE axis. There are only 8 class-level records, all generic
   LocalStructuralFeature-derived motifs; there are no source-derived alpha
   helix, 3_10 helix, pi helix, beta strand, beta sheet, beta bridge, turn,
   bend, loop/coil, PPII, or systematic super-secondary motif records.

2. The largest structural comparison gap is representational, not algorithmic.
   The repo already has `build_structural_equivalence.py` and a TED manifest,
   but records cannot carry a representative structure, 3Di descriptor, or
   contact-map pointer in schema-valid YAML.

3. Secondary and tertiary structure share the `STRUCTURE` axis, but they are
   not comparable in the same space. `STRUCT_SECONDARY` needs DSSP/STRIDE
   strings and topology grammar; `STRUCT_FOLD`/`STRUCT_TOPOLOGY` need 3D
   geometry and Foldseek/TM-score. Reusing only Phase 3 Foldseek for all
   structure would fold away 2D traits.

4. Coiled coil is double-homed. Current data has the generic
   `STRUCT_SECONDARY` `COILED_COIL` record and 314 Pfam `MIXED_COILED_COIL`
   records. The canonical home for source-derived coiled-coil traits should be
   `MIXED_COILED_COIL`; keeping the generic structural motif without a bridge
   risks duplicate search/filter results and false cross-category merges.

5. Several enum categories are empty (`SEQ_NONSTANDARD_RESIDUE`,
   `SEQ_LOW_COMPLEXITY`, `SEQ_COMPOSITION`, `SEQ_EPITOPE`,
   `STRUCT_QUATERNARY`, `STRUCT_ALLOSTERIC_SITE`, `STRUCT_SYMMETRY`,
   `MIXED_TRANSMEMBRANE`, and several `FUNC_*` categories). They should stay in
   the matrix as explicit gaps, but no cross-source operator can be validated
   until records and representations exist.

6. Some populated categories still lack comparable class-level representation.
   Examples: `STRUCT_CAVITY` has 5 generic records but no pocket geometry;
   `STRUCT_INTERFACE` has 1 generic record but no contact map; `STRUCT_METAL_SITE`
   has 1 generic record but no coordination geometry.

7. `UPPER` contains 1,980 PROSITE documentation/group records. These are useful
   grouping nodes, but they should not be treated as biological equivalence
   targets. Prior work already flags PROSITE PDOC grouping as `member_of` or
   close documentation grouping rather than subclass/same-as.

8. Function categories compare by anchors, but anchor specificity matters.
   Rhea reactions and EC leaves are useful; broad GO terms are often too
   generic. The review in `research/entry-merge-methods-round1.md` explicitly
   warns not to use generic anchors as identity.

9. Phase 2 member-set overlap is powerful but unsafe for localized features
   without Tier 2. The existing nuclear-receptor example in prior work shows
   that co-occurring domains can have high Jaccard while occupying disjoint
   regions.

10. Tier 5 embeddings are useful for review but should remain non-assertive.
    `embed_neighbors.py` is correctly scoped to semantic neighbors and
    review-only merge candidates; it should not emit `data/equivalence/*.tsv`
    edges automatically.

## Recommendations summary

1. Add two minimal representation slots:
   `secondary_structure_representations` and
   `structural_geometry_representations`.
2. Seed a real `STRUCT_SECONDARY` taxonomy from DSSP/STRIDE/PDBsum/CATH SS:
   elementary states, turns/bends, local motifs, and super-secondary motifs.
3. Canonicalize source-derived coiled coils under `MIXED_COILED_COIL`; treat
   the existing `STRUCT_SECONDARY` coiled-coil record as a legacy/generic bridge
   until a migration can resolve it.
   **DONE (2026-07-04):** `proteintraitsmech:COILED_COIL` remapped to
   `MIXED_COILED_COIL` / `SEQUENCE_STRUCTURE` and moved to
   `data/traits/mixed/coiled_coil/coiled-coil.yaml` as the generic umbrella
   class (cross-axis `POLYPEPTIDE_STRUCTURAL_MOTIF` parent dropped; no records
   referenced it). No new coiled-coil records under `STRUCT_SECONDARY`.
4. Add `build_secondary_structure_equivalence.py` to emit
   `data/equivalence/secondary_structure.tsv` using topology-string and
   SS-string operators.
5. Extend `build_structural_equivalence.py` by populating CATH/SCOPe/ECOD
   representatives alongside TED and then emitting `structural.tsv`.
   **DONE (2026-07-04):** `--derive` now emits a cross-source
   `data/analysis/structural_reps.tsv` (37,078 reps: TED 13,860 AlphaFold +
   CATH 8,102 & ECOD 15,116 PDB-domain reps from their domain xrefs; SCOPe
   skipped — seeded nodes carry no px/domain sid). The Foldseek stage now
   fetches AlphaFold *or* RCSB PDB structures (chain-filtered) and emits
   `data/equivalence/structural.tsv` with
   `relation_source=foldseek-tm<score>-{fold,superfamily}`. `--derive-ted`
   retained for the legacy TED-only manifest.
