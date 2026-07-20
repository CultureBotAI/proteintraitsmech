# Codex analysis prompt — aligning the SEQUENCE, STRUCTURE, and FUNCTION coordinate systems (grounded in real UniProt/PDB proteins)

## Your task

ProteinTraitsMech splits trait records across five axes; three carry the bulk of
the biology — **SEQUENCE**, **STRUCTURE**, **FUNCTION** — and each localizes its
traits in a *different coordinate system*. A prior analysis
(`research/sequence-structure-alignment-analysis-1.md`, implemented as
`scripts/build_sequence_structure_alignment.py`) worked out the SEQUENCE↔STRUCTURE
alignment on a shared **UniProt residue frame** (SIFTS for PDB numbering, InterPro
for match spans). It does **not** treat FUNCTION as a third coordinate system.

**Extend that analysis to all three axes:** characterize the SEQUENCE, STRUCTURE
and FUNCTION coordinate systems, and find the concrete **paths to align across
them** — where they share a residue frame, where they only share whole-protein
identity, and where the bridge is chemistry or partonomy. **Ground everything in
real proteins** found via the **UniProtKB REST API** + **PDB (RCSB/PDBe)** +
**SIFTS** — specific proteins that simultaneously carry sequence, structure, and
function annotations, traced annotation-by-annotation.

This is **read-only** w.r.t. the repository (no edits to code/records/schema). You
**may** query the UniProt / PDBe / RCSB / SIFTS / InterPro REST APIs to discover
and verify exemplar proteins. Produce exactly one markdown report (see
Deliverable). Verify every "repository fact" against the tree.

## Repository facts to build on (verify them)

- **Axes + representation rule** (`CLAUDE.md`, `src/proteintraitsmech/schema/proteintraitsmech.yaml`):
  axis follows the *representation*, not the biology. The FUNCTION axis holds
  (verify counts): `FUNC_PROTEIN_FAMILY` (~32k), `FUNC_ORTHOLOG_GROUP` (~32k),
  `FUNC_PATHWAY` (~28k), `FUNC_ENZYMATIC_ACTIVITY` (~26k), `FUNC_INTERACTION_PARTNER`
  (~20k), `FUNC_MOLECULAR_FUNCTION` (~10k), `FUNC_RESISTANCE`, `FUNC_LOCALIZATION`,
  `FUNC_TRANSPORT`, `FUNC_COFACTOR_REQUIREMENT`, `FUNC_BINDING_CAPACITY`.
- **Residue-localized function already exists on the STRUCTURE/SEQUENCE axes**:
  `STRUCT_ACTIVE_SITE` (M-CSA), `STRUCT_BINDING_SITE` (BioLiP, with promoted
  per-residue features), `STRUCT_METAL_SITE` (MetalPDB), `SEQ_ACTIVE_SITE`,
  `SEQ_BINDING_SITE`, `SEQ_CLEAVAGE_SITE` (MEROPS P4–P4′ consensus), PTM sites —
  these are *function* biology carried on the axis of their *representation*.
- **Groundings** (the FUNCTION "ontology-anchor" coordinates): `EC:`, `RHEA:`,
  `CHEBI:` (`chemical_participants`), `GO:`, `OrthoDB:`/`OMA:`/`COG:`, `Pfam:`,
  `InterPro:`, `MEROPS:`, `TCDB:`, `Reactome:`.
- **The existing residue-frame machinery**: `build_sequence_structure_alignment.py`
  (`--providers stored,interpro,sifts`), `canonical_examples[].features[]`
  (start/end, trait_axis, trait_category), `sequence_pattern`, the SIFTS + InterPro
  providers, and `data/equivalence/*.tsv` overlays (`biolink:close_match` /
  `overlaps`, loaded bidirectionally by `build_docs_index`). Cross-axis pairs are
  **related, never merged** (merge-within-axis).

## Part 1 — characterize the three coordinate systems

For each axis, state *what a "coordinate" is* — what pins a trait to a place. Fill
a table (axis · category · coordinate type · frame · localizable to a residue?):

- **SEQUENCE** — 1-indexed **UniProt residue position** (feature spans, motif/regex
  hits) and **signature identity** (Pfam/PROSITE/InterPro model).
- **STRUCTURE** — **residue position via SIFTS** (PDB author numbering → UniProt),
  **3-D geometry** (`structural_geometry_representations`, PDB/AlphaFold), and
  **fold classification** (CATH/SCOP/ECOD/TED).
- **FUNCTION** — **heterogeneous**, and this is the crux:
  1. *residue-localized function* (active/binding/metal/cleavage sites, PTMs) →
     lives on the **same residue frame** as sequence/structure;
  2. *whole-protein function* (EC activity, GO term, ortholog group, protein
     family, pathway, transport, localization) → **no residue coordinate**;
     localized only by an **ontology/identity anchor** + whole-protein membership;
  3. *chemistry* (Rhea reaction, ChEBI participants) → a **chemical-entity**
     coordinate (the substrate/cofactor), not a residue.
  Make explicit which FUNCTION categories are residue-localizable and which are
  whole-protein-only.

## Part 2 — find the alignment paths (the core deliverable)

Enumerate and evaluate the paths that connect the three systems:

1. **Residue-frame path** (direct extension of the existing overlay): residue-
   localized FUNCTION (active/binding/metal/cleavage/PTM sites) ↔ SEQUENCE features
   ↔ STRUCTURE sites, all projected onto the shared UniProt residue frame. This is
   the same mechanism as `build_sequence_structure_alignment.py` — the extension is
   adding FUNCTION-site providers. State which FUNCTION categories qualify.
2. **Whole-protein co-membership path**: whole-protein FUNCTION (EC / GO / family /
   ortholog / pathway) ↔ SEQUENCE signatures (Pfam/InterPro) ↔ STRUCTURE folds
   (CATH/ECOD), aligned NOT by residues but by **co-occurrence on the same UniProt
   protein** (a Swiss-Prot entry's Pfam domain, EC number, GO terms, and CATH fold
   are all annotations of one protein) and by **shared cross-references**. Define
   the anchor and the edge semantics (relate-only).
3. **Cross-scale partonomy**: a residue-level function (an active site) is *part of*
   a whole-protein function (the enzymatic activity), which the domain (sequence)
   and fold (structure) *host*. Model this as a multi-scale relation
   (residue → domain/region → whole-protein → fold), not a single overlap.
4. **Chemistry bridge**: FUNCTION chemistry (Rhea/ChEBI substrate/cofactor) ↔
   the **binding-site residues** that contact that ligand (BioLiP/MetalPDB/UniProt
   BINDING) — links the chemical-entity coordinate to the residue frame.

For each path give: the shared anchor, whether it's residue-level or entity-level,
the predicate (`biolink:overlaps`/`part_of`/`related_to`/`close_match`), the data
already present vs. what must be fetched, and the coverage/limits.

## Part 3 — ground it in real proteins (leverage UniProtKB API + PDB)

Do NOT reason abstractly — find concrete exemplars via live APIs:

- **UniProtKB REST API** (`https://rest.uniprot.org/uniprotkb/search?...`): query for
  **reviewed (Swiss-Prot)** proteins that co-carry all three annotation types — a
  Pfam/PROSITE **sequence** signature, a **PDB** structure cross-reference, and
  **function** annotations (an EC number, catalytic activity, GO terms, an active
  site, a cofactor). E.g. filter on `reviewed:true AND database:pdb AND ec:* AND
  ft_act_site:* AND database:pfam`. Pull the JSON: features (DOMAIN, ACT_SITE,
  BINDING with residue positions), xrefs (Pfam, InterPro, PDB, CATH/Gene3D), EC,
  GO, cofactor, catalytic activity (Rhea).
- **PDBe / RCSB + SIFTS** (`https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/<pdb>`):
  for each exemplar's PDB, confirm the PDB↔UniProt residue mapping so structural
  residues land on the same frame.
- Pick **3–5 well-characterized exemplars** spanning enzyme families (e.g. a
  protein kinase such as `P17612`, a serine protease, a metalloenzyme, a
  redox/cofactor enzyme). For each, **trace the alignment on the UniProt residue
  frame**: the Pfam domain span (SEQUENCE), the PROSITE catalytic motif hit
  (SEQUENCE), the CATH fold via SIFTS + the PDB (STRUCTURE), the M-CSA/UniProt
  active-site residues and the EC activity + Rhea reaction + GO term (FUNCTION) —
  showing which annotations coincide at the same residues and which only co-occur
  on the whole protein. Use real accessions, real residue numbers, real PDB ids.

## Deliverable

Write **`research/sequence-structure-function-alignment-analysis-1.md`**:

1. **Coordinate-system taxonomy** — the per-axis/category table (coordinate type ·
   frame · residue-localizable?), making the SEQUENCE/STRUCTURE/FUNCTION systems
   explicit and where they are commensurable.
2. **Alignment-path map** — paths 1–4 with anchors, predicates, residue-vs-entity
   level, data-present vs fetch, and limits.
3. **UniProt/PDB-grounded exemplars** — the 3–5 real proteins, each traced on the
   shared residue frame (cite the exact UniProt accession, PDB id, Pfam/CATH/EC/GO
   ids, and residue numbers you verified via the APIs).
4. **Recommended builder extension** — how `build_sequence_structure_alignment.py`
   grows into a three-way overlay: a FUNCTION-site residue provider (path 1) + a
   whole-protein co-membership overlay (path 2) → `data/equivalence/`, relate-only.
   Note the smallest useful first step.
5. **Open questions / risks** — isoforms, PDB numbering, whole-protein vs residue
   granularity, generic-anchor traps (broad GO/EC), and where curator judgement is
   unavoidable.

Keep the taxonomy table + the exemplar traces as the primary deliverables. Cite
every API query and identifier you verified. Final message: the file path, the
single most promising alignment path, and the top exemplar.
