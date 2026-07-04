# Codex review prompt — per-category cross-source entry comparison & the representation problem

## Your task

Produce a design review answering ONE question for ProteinTraitsMech:

> **For each `trait_category`, what is the canonical COMPARABLE REPRESENTATION of
> an entry, and what OPERATOR decides whether two entries from different data
> sources are the same / equivalent / related trait?**

Different categories are comparable in fundamentally different spaces, and the
schema must be able to *hold* the representation before entries can be compared:

- **Sequence traits** are comparable as **N→C linear features**: a residue
  interval (start–end) and/or a symbolic pattern (PROSITE syntax / regex / HMM).
  Two sequence entries are the same when their patterns/positional profiles
  match or their annotated regions coincide.
- **Secondary structure (2D)** is comparable as a **secondary-structure string
  / element topology**: DSSP/STRIDE 8- or 3-state strings, SS-element order
  (e.g. a β-hairpin = β–turn–β; helix-turn-helix = H–loop–H), or a structural
  alphabet (Foldseek 3Di). Two SS entries are the same when their SS-element
  grammar / topology string matches.
- **Tertiary structure (3D)** is comparable as **geometry**: a representative
  domain structure compared by TM-score/Foldseek, or a contact map.
- **Function** is comparable by **ontology anchors** (EC / Rhea / GO / ChEBI /
  SubCell) — shared specific grounding = equivalence.

**We are currently combining secondary (2°) and tertiary (3°) structure under a
single STRUCTURE axis.** A required output of this review is to ensure the 2°
structure traits are *fully represented* — as categories, as records, and with a
representation that makes them comparable — not folded away under 3° traits.

## Repository facts you must build on (verify them yourself in the tree)

- Schema: `src/proteintraitsmech/schema/proteintraitsmech.yaml`. One
  `ProteinTraitRecord` per YAML under `data/traits/<axis>/<cat>/…`. Axes:
  SEQUENCE, STRUCTURE, SEQUENCE_STRUCTURE, FUNCTION, EVOLUTION.
- **Representation slots that exist today**: `sequence_pattern` (PROSITE/regex),
  `residue_sequence` (one realized instance), and per-example `start`/`end`/
  `feature_type` coordinates on `canonical_examples`. **There is NO slot for a
  secondary-structure string / DSSP codes, and NO slot for a 3D-geometry
  representation (representative structure ref, Foldseek 3Di descriptor, contact
  map).** This is the core gap for structural comparison.
- **STRUCT_SECONDARY is almost empty at the class level**: only **8 curated
  generic motifs** exist — `structure/secondary/`: asx motif, beta bulge, beta
  hairpin, coiled coil, helix cap, kink, nest, and a parent "polypeptide
  structural motif". No source-derived SS-element traits (α-helix, 3₁₀/π-helix,
  β-strand, β-sheet, β-bridge, turn types, PPII, bend) and no super-secondary
  taxonomy (β-α-β, Greek key, jelly roll, helix-hairpin-helix, β-meander,
  β-barrel-as-topology, EF-hand, etc.).
- **Inconsistency to resolve**: "coiled coil" exists BOTH as `STRUCT_SECONDARY`
  (`structure/secondary/coiled-coil.yaml`) AND as the `MIXED_COILED_COIL`
  category (SEQUENCE_STRUCTURE axis). Pick one home and justify it.
- Existing structural categories: STRUCT_CLASS, _ARCHITECTURE, _TOPOLOGY,
  _HOMOLOGOUS_SUPERFAMILY, _FOLD, _DOMAIN, _SECONDARY, _QUATERNARY, _INTERFACE,
  _ACTIVE_SITE, _BINDING_SITE, _ALLOSTERIC_SITE, _DISULFIDE, _METAL_SITE,
  _CAVITY, _SYMMETRY, _DYNAMICS, _STABILITY, _SURFACE, _OTHER.
- Sources already seeded (per README / index): PROSITE, Pfam, InterPro, CATH,
  SCOPe, ECOD, TED, NCBIfam, CDD, M-CSA, PSI-MOD, DisProt, IDEAL, ELM, MEROPS,
  RepeatsDB, TCDB, COG, Rhea, EC, CARD/ARO, Reactome, PSI-MI, PATO, METPO.

## Prior work you must EXTEND, not duplicate

The entry-merge pipeline already exists (`research/entry-merge-methods-round1.md`,
`data/equivalence/*.tsv` overlays loaded into the browser `eq` field):

- **Phase 1** — InterPro member-DB integration → `biolink:close_match`
  (`build_equivalence.py`, 24k edges).
- **Phase 2** — UniProt member-set Jaccard/containment overlap
  (`build_member_overlap.py`), with **Tier-2 region-overlap verification**
  (`verify_region_overlap.py`) that rejects co-occurring-but-distinct domains
  by comparing InterPro match coordinates.
- **Phase 3** — Foldseek TM-score structural equivalence for CATH/SCOPe/ECOD/TED
  (`build_structural_equivalence.py`; representative manifest derived).
- **Tier-5** — text-embedding cosine neighbors (`embed_records.py` +
  `embed_neighbors.py`) for semantic merge candidates (review-only).

Your review is the **representation layer that sits UNDER these operators**: it
says, per category, *what to compare and in what space*, and where the current
schema/data can't yet hold that representation.

## Edge typing

Prioritize the **Biolink Model** (same_as / close_match / narrow_match /
member_of / has_part / overlaps) exactly as the existing overlays do; use **RO**
only for relations Biolink lacks. Never assert equivalence from a mapping alone
without the category's comparison operator agreeing.

## Deliverables (write as `research/cross-source-comparison-review-1.md`)

1. **Per-category comparison matrix** — a table with one row per `trait_category`:
   `category | comparable representation | comparison operator + threshold |
   sources providing it | Biolink edge on match | which existing Phase/Tier
   implements it (or GAP)`. Group by axis. Be specific about thresholds.

2. **Representation-slot recommendations** — concrete LinkML additions so the
   schema can HOLD each representation, at minimum:
   - a secondary-structure representation (DSSP/STRIDE 3- or 8-state string, and/
     or an SS-element topology string), with how it's populated and compared;
   - a 3D-geometry representation pointer (representative structure ref +
     optional Foldseek 3Di descriptor / contact map) so STRUCT_FOLD/_TOPOLOGY/
     _DOMAIN entries carry something Phase-3 can compare directly;
   - keep additions closed-mode-validation clean and minimal.

3. **Secondary-structure trait taxonomy (completeness)** — the full set of 2°
   and super-secondary traits that SHOULD exist, mapped to the 8 that already do,
   with: parent hierarchy, grounding ontology terms (DSSP states, the
   "polypeptide structural motif" / SS-motif vocabularies, SO/PATO where
   relevant), and candidate DATA SOURCES + a seeding recipe for each (DSSP,
   STRIDE, PDBsum, CATH SS, super-secondary-structure databases). Resolve the
   coiled-coil double-home.

4. **How comparison plugs into the pipeline** — for the new/under-served
   categories (esp. 2° structure), which operator (SS-string alignment, 3Di /
   Foldseek, topology-string match) and what `just`-style script would emit the
   equivalence overlay, consistent with the existing `data/equivalence/*.tsv`
   convention.

5. **Oddities & risks** — mis-categorizations, representation mismatches,
   double-homed traits, and any category whose entries are currently not
   comparable at all.

Keep it concrete and repo-grounded (cite file paths, category names, real
counts). Prefer specific thresholds and named tools/ontologies over generalities.
Print the full review to stdout if you cannot write the file.
