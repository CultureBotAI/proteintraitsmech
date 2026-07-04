# Axis operators — reference

Derived from `research/cross-source-comparison-review-1.md` (§1 per-category
comparison matrix, §4 how comparison plugs into the equivalence pipeline). This
is the detailed backing for the per-axis summary in `skill.md`.

## The overlay builders

Every builder writes a TSV of `subject  predicate  object  relation_source`
edges under `data/equivalence/`. The analyzer / a curator loads them
bidirectionally.

| Builder | Output | Axis / scope | Predicate(s) | Notes |
|---------|--------|--------------|--------------|-------|
| `build_equivalence.py` | `cross_source.tsv` | SEQUENCE/STRUCTURE signatures | `close_match` | Phase 1 — InterPro member-DB integration (Pfam/PROSITE/SMART/… ⇒ same InterPro entry). |
| `build_member_overlap.py` | `member_overlap.tsv` | SEQUENCE localized | `close_match`, `narrow_match` | Phase 2 — UniProt member-set overlap; Jaccard → close, containment → narrow. |
| `verify_region_overlap.py` | (confirms) | SEQUENCE/STRUCTURE localized | — | Tier 2 — confirms a localized candidate by same-region coordinate overlap. **Required** before promoting a member-overlap hit. |
| `build_secondary_structure_equivalence.py` | `secondary_structure.tsv` | `STRUCT_SECONDARY` | `close_match`, `narrow_match` | Topology-string / SS-string operators. |
| `build_structural_equivalence.py` | `structural.tsv` (+ `structural_reps.tsv` manifest) | STRUCTURE folds | `close_match` (`foldseek-tm<score>-{fold,superfamily}`) | Phase 3 — Foldseek TM-score over TED/CATH/ECOD representative domains. Needs `foldseek` on PATH. |
| `build_function_anchor_equivalence.py` | `function.tsv` | FUNCTION | `close_match` | Same-category, cross-source shared ontology anchor (EC leaf / RHEA / ARO / TCDB / MI). |
| `embed_records.py` / `embed_neighbors.py` | embeddings + neighbors | all | — | Tier 5 — semantic neighbors for *candidate generation only*, never identity. |
| `analyze_trait_equivalence.py` | `trait_merge_plan.yaml` | all (axis-agnostic) | R1/R2 + C1/C2/C3 | Universal identity (see [[merge-traits]]). |

## Per-category operator matrix

### SEQUENCE
| Category | "Same trait" is… | Operator | Predicate |
|----------|------------------|----------|-----------|
| `SEQ_DOMAIN` / `SEQ_FAMILY` / `SEQ_HOMOLOGOUS_SUPERFAMILY` | same signature family across DBs | Phase 1 InterPro member-DB integration; else member overlap | `close_match` |
| `SEQ_MOTIF` / `SEQ_CONSERVATION` | same motif/region | Phase 2 member + Tier 2 region overlap | `close_match` / `narrow_match` |
| `SEQ_REPEAT` | same repeat family | Phase 2 member overlap (sequence periodicity) | `close_match` |
| `SEQ_PTM_SITE` / `SEQ_MODIFIED_RESIDUE` / `SEQ_GLYCOSYLATION_SITE` / `SEQ_CROSSLINK_SITE` | same modification at the same residues | Phase 2 + **Tier 2 mandatory** | `close_match` |

### STRUCTURE
| Category | "Same trait" is… | Operator | Predicate |
|----------|------------------|----------|-----------|
| `STRUCT_FOLD` / `STRUCT_TOPOLOGY` | same fold/topology | Foldseek TM-score ≥ 0.5 | `close_match` (`-fold`) |
| `STRUCT_HOMOLOGOUS_SUPERFAMILY` / `STRUCT_DOMAIN` | same superfamily/domain | Foldseek TM-score ≥ 0.7 | `close_match` (`-superfamily`) |
| `STRUCT_SECONDARY` | same SS element/arrangement/topology | topology-string / SS-string | `close_match` / `narrow_match` |
| `STRUCT_ACTIVE_SITE` / `STRUCT_BINDING_SITE` / `STRUCT_METAL_SITE` | same catalytic/ligand residues | same-region overlap (Phase 2 + Tier 2); mechanism/ontology anchor for M-CSA | `close_match`; `has_part` for residues |

### SEQUENCE_STRUCTURE
| Category | "Same trait" is… | Operator | Predicate |
|----------|------------------|----------|-----------|
| `MIXED_STRUCTURAL_REPEAT` | same periodic repeat (seq + 3D) | RepeatsDB class/topology; member overlap | `close_match` |
| `MIXED_COILED_COIL` | same heptad register + supercoil | member overlap once seeded | `close_match` |
| `MIXED_TRANSMEMBRANE` | same TM span family | member overlap once seeded | `close_match` |

### FUNCTION
| Category | "Same trait" is… | Operator | Predicate |
|----------|------------------|----------|-----------|
| `FUNC_ENZYMATIC_ACTIVITY` | same reaction | same Rhea id → `same_as`; same EC leaf (+ Rhea/participants) → `close_match` | `same_as` / `close_match`; `has_participant` for ChEBI |
| `FUNC_INTERACTION_PARTNER` | same specific interaction type | same PSI-MI type | `close_match`; `interacts_with` for entities |
| `FUNC_TRANSPORT` | same TC family | same TCDB family id | `close_match` (single-source today) |
| `FUNC_RESISTANCE` | same determinant/mechanism | same ARO id | `close_match` (single-source today) |
| `FUNC_ORTHOLOG_GROUP` | same cluster | membership → `member_of` (not merge) | `member_of` |
| `FUNC_PATHWAY` | same pathway | **no anchor today** (see gaps) | — |

### EVOLUTION
| Category | "Same trait" is… | Operator | Status |
|----------|------------------|----------|--------|
| `EVO_CONSERVATION` / `EVO_PANGENOME` | same taxon scope + threshold | taxon-scope + distribution-threshold match | **not ready** — records lack the fields |

## Trap catalogue

1. **Localized-feature trap (SEQUENCE, STRUCTURE local sites):** high member
   Jaccard alone ≠ equivalence. Two records over the same proteins can annotate
   different residues. Confirm same-region overlap (`verify_region_overlap.py`).
2. **Member-overlap-is-weak trap (STRUCTURE folds):** homologs diverge past
   detectable sequence identity while keeping the fold — CATH/SCOPe/ECOD/TED
   agree structurally, not by member set. Use TM-score, not member overlap.
3. **Generic-anchor trap (FUNCTION):** broad GO terms and shared ChEBI
   participants are not identity (ChEBI is `has_participant`). Only specific,
   low-frequency anchors count. `build_function_anchor_equivalence.py` excludes
   GO/ChEBI for this reason.
4. **Pathway ≠ enzyme trap (FUNCTION):** a `FUNC_PATHWAY` sharing an EC with a
   `FUNC_ENZYMATIC_ACTIVITY` is not equivalent; two pathways sharing enzymes are
   `overlaps`, never `close_match`.
5. **Bridge trap (SEQUENCE_STRUCTURE):** never merge a sequence-only `SEQ_REPEAT`
   with a `MIXED_STRUCTURAL_REPEAT` — different axis by design.

## Open gaps

- **FUNCTION pathway equivalence (SEED ↔ Reactome):** no shared anchor exists —
  Reactome records carry only `Reactome:` xrefs, SEED subsystems only `EC:`
  mapped_xrefs; `IDENTITY_NAMESPACES` in `analyze_trait_equivalence.py` has no
  pathway namespace. A proper capability needs a **pathway-identity anchor**:
  enrich Reactome pathways with their constituent EC set and score SEED/Reactome
  pairs by shared-EC **Jaccard → `biolink:overlaps`** (a proposed
  `build_pathway_overlap_equivalence.py`), reserving `close_match` for very high
  overlap + agreeing labels. Grounding both to GO biological process is the
  alternative anchor. Until then, pathway↔pathway equivalence is out of scope —
  do not force it through the generic C3 same-label heuristic.
- **STRUCTURE fold overlay** requires `foldseek` + AlphaFold/PDB downloads; the
  `structural_reps.tsv` manifest (TED + CATH + ECOD) is the runnable input, the
  TM-score pass is the heavy gated step.
- **EVOLUTION:** blocked on taxon-scope / threshold fields on the records.
