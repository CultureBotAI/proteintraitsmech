---
name: merge-within-axis
description: Use this skill to detect and consolidate equivalent ProteinTraitRecords WITHIN a single trait axis, using the equivalence operator that is correct for that axis — because "same trait" means something different on each axis. SEQUENCE merges on sequence-signature identity + member/region overlap; STRUCTURE on fold TM-score + secondary-structure topology; SEQUENCE_STRUCTURE on repeat/coiled-coil units; FUNCTION on ontology anchors (EC/Rhea) + pathway overlap; EVOLUTION on taxon scope. It routes a merge job to the right overlay builder, sets the right confidence tier (merge vs review vs relation-only), and hands the MERGE tier to the merge-traits procedure. Trigger when asked to "merge within an axis", "merge STRUCTURE / SEQUENCE / FUNCTION traits", "find equivalents in <axis>", "which equivalence operator for this axis", "consolidate fold / pathway / domain records", or to dedup one axis at a time.
---

# Merge Within Axis Skill

## Overview

The generic [[merge-traits]] skill auto-merges only the two **axis-agnostic**
identity signals — `R1 EXACT_ID` (identical `identifier`) and `R2 EXACT_PATTERN`
(byte-identical `sequence_pattern`) — and lists everything else as review
candidates from three weak generic heuristics (shared xref, shared anchor, same
label). That is deliberately conservative and **under-covers**, because the real
notion of "same trait" is different on every axis:

- two **fold** records are the same when their representative domains superpose
  (TM-score), even with no sequence similarity;
- two **enzymatic-activity** records are the same when they denote the same
  reaction (EC leaf / Rhea), regardless of family;
- two **localized sequence features** are the same only when they cover the same
  *region* of the same proteins — high member overlap alone is a trap.

This skill answers: **for records on ONE axis, which operator decides equivalence,
which overlay produces the candidate edges, and which edges are safe to merge vs
only relate?** It is the axis-aware layer on top of merge-traits — merge-traits
still owns the universal R1/R2 auto-merge and the merge *procedure*; this skill
supplies the per-axis candidate generation and the promotion rule.

**The comparison is always same-axis AND same-category.** Never merge across
axes or categories (that is a modelling bug — fix the seeder). Cross-*source* is
what you want (two databases describing one trait); cross-category is not.

---

## Confidence tiers (predicate → what you may do)

Overlays emit Biolink-typed edges. The predicate fixes what the edge licenses:

| Predicate | Meaning | Action |
|-----------|---------|--------|
| `R1`/`R2` (merge-traits) | definitional identity | **MERGE** (auto) |
| `biolink:same_as` | same source identity (e.g. same Rhea reaction id) | **MERGE** |
| `biolink:close_match` | strong cross-source equivalence per the axis operator | **REVIEW → merge** once the axis threshold + a second signal agree |
| `biolink:narrow_match` | one subsumes the other (subclass-like) | **NEVER merge** — keep as hierarchy |
| `biolink:member_of` / `part_of` | membership / partonomy | **NEVER merge** — keep as `trait_relations` |
| `biolink:overlaps` / `related_to` | shares parts (e.g. pathways sharing enzymes) | **NEVER merge** — relate only |

Rule of thumb: **only `same_as` and R1/R2 auto-merge. `close_match` is a review
candidate that the axis operator must confirm.** Everything narrower is a
relation, not an identity.

---

## Per-axis operators

Each axis has a primary operator, a builder that emits `data/equivalence/*.tsv`,
and a signature trap to avoid. Full per-category detail is in
[`reference/axis-operators.md`](reference/axis-operators.md).

### SEQUENCE
Signature families (`SEQ_DOMAIN`, `SEQ_FAMILY`, `SEQ_HOMOLOGOUS_SUPERFAMILY`,
`SEQ_MOTIF`, `SEQ_CONSERVATION`) and localized features (`SEQ_REPEAT`,
`SEQ_PTM_SITE`, `SEQ_MODIFIED_RESIDUE`, `SEQ_GLYCOSYLATION_SITE`,
`SEQ_CROSSLINK_SITE`).

- **Operator:** signature identity via the InterPro member-DB integration
  (Phase 1), then **member-set + same-region overlap** for localized features
  (Phase 2 + Tier 2).
- **Builders:** `build_equivalence.py → cross_source.tsv`;
  `build_member_overlap.py → member_overlap.tsv`;
  `verify_region_overlap.py` (Tier 2 confirmation).
- **Trap — the localized-feature trap:** high member Jaccard alone is **not**
  equivalence. Two PTM/site/motif records over the same proteins can flag
  different residues. Require confirmed same-region overlap before promoting.

### STRUCTURE
Fold / topology / superfamily (`STRUCT_FOLD`, `STRUCT_TOPOLOGY`,
`STRUCT_HOMOLOGOUS_SUPERFAMILY`, `STRUCT_DOMAIN`; CATH/SCOPe/ECOD/TED),
secondary structure (`STRUCT_SECONDARY`), and local features
(`STRUCT_ACTIVE_SITE`, `STRUCT_BINDING_SITE`, `STRUCT_METAL_SITE`).

- **Operator:** structural superposition — Foldseek **TM-score** ≥ 0.5 (fold) /
  ≥ 0.7 (superfamily) → `close_match`; secondary structure by **topology-string**
  comparison; local features by same-region overlap (Phase 2 + Tier 2).
- **Builders:** `build_structural_equivalence.py → structural.tsv` (needs
  `foldseek` + the `structural_reps.tsv` manifest of TED/CATH/ECOD reps);
  `build_secondary_structure_equivalence.py → secondary_structure.tsv`.
- **Trap:** sequence member-overlap is weak across CATH/SCOPe/ECOD/TED — homologs
  diverge past detectable identity while keeping the fold. Use TM-score, not
  member overlap, for fold-level classes. CATH/ECOD reps are whole-chain (no
  stored domain bounds) — coarser for multi-domain chains.

### SEQUENCE_STRUCTURE
`MIXED_STRUCTURAL_REPEAT`, `MIXED_COILED_COIL`, `MIXED_TRANSMEMBRANE`.

- **Operator:** repeat-unit / coiled-coil register + supercoil topology; member
  overlap once the MIXED categories are populated (RepeatsDB for repeats).
- **Builders:** reuse the Phase-2 member-overlap path; no dedicated builder yet.
- **Trap:** a sequence-only `SEQ_REPEAT` is **not** mergeable with a
  `MIXED_STRUCTURAL_REPEAT` (different axis) — don't cross the bridge.

### FUNCTION
`FUNC_ENZYMATIC_ACTIVITY`, `FUNC_PATHWAY`, `FUNC_TRANSPORT`, `FUNC_RESISTANCE`,
`FUNC_INTERACTION_PARTNER`, `FUNC_ORTHOLOG_GROUP`, `FUNC_PROTEIN_FAMILY`.

- **Operator:** shared **ontology anchor**, not embedding similarity. Same Rhea
  reaction id → `same_as`; same EC leaf (+ agreeing Rhea/participant set) →
  `close_match`; ARO/TCDB/PSI-MI specific type → `close_match`.
- **Builders:** `build_function_anchor_equivalence.py → function.tsv` (enzymatic:
  EC leaf / RHEA / ARO / TCDB / MI; GO and ChEBI excluded);
  `build_pathway_overlap_equivalence.py → pathway.tsv` (`FUNC_PATHWAY`: shared
  GO biological-process anchor ∥ constituent EC-set Jaccard).
- **Trap — the generic-anchor trap:** a broad GO term or a shared ChEBI
  participant is **not** identity (ChEBI is `has_participant`). And **pathways
  are not enzymes:** a `FUNC_PATHWAY` sharing one EC with a `FUNC_ENZYMATIC_ACTIVITY`
  is not equivalent, and two pathways sharing enzymes are `overlaps`, never
  `close_match`. SEED↔Reactome pathway equivalence is anchored on shared GO-BP
  (with a cap on generic BP terms), not on EC alone.

### EVOLUTION
`EVO_CONSERVATION`, `EVO_PANGENOME`.

- **Operator:** same taxon scope + same distribution threshold definition.
- **Status:** **not ready.** Current curated classes lack taxon-scope/threshold
  fields; do not assert cross-source equivalence until they carry them.

---

## Workflow

```bash
just build-docs                 # REQUIRED — overlays/analyzer read the shards
```

1. **Pick the axis** and confirm the category(ies) in scope.
2. **Run the axis operator(s)** to produce candidate edges:
   ```bash
   just build-equivalence               # SEQUENCE signatures → cross_source.tsv
   python3 scripts/build_member_overlap.py           # SEQUENCE localized
   python3 scripts/build_structural_equivalence.py   # STRUCTURE folds (foldseek)
   python3 scripts/build_secondary_structure_equivalence.py
   just build-function-equivalence      # FUNCTION anchors → function.tsv
   ```
3. **Classify each edge by predicate** (tier table above): `same_as`/R1/R2 →
   MERGE; `close_match` → REVIEW; narrower → relation-only.
4. **Confirm `close_match` with the axis operator + a second signal** before
   promoting (e.g. structural TM-score AND agreeing labels; EC-leaf AND agreeing
   Rhea; member overlap AND confirmed same region).
5. **Execute the MERGE tier through merge-traits** — it owns target selection,
   field folding, the `curation_history` audit event, and disposal (delete R1
   losers / DEPRECATE R2). Do **not** hand-merge review candidates:
   ```bash
   just analyze-merges              # R1/R2 plan (universal)
   just analyze-merges --apply
   ```
6. **Re-validate:** `just build-docs && just validate-all`; confirm the record
   total dropped by exactly the number of merged losers.

---

## Best practices

1. **One axis at a time.** Load only that axis's operator and overlay; do not mix
   a FUNCTION run with a STRUCTURE run — the operators and traps differ.
2. **Never merge on `close_match` alone.** It is a candidate; the axis operator
   plus a corroborating signal must agree. Only `same_as`/R1/R2 auto-merge.
3. **Relations are not merges.** `member_of`, `part_of`, `overlaps`,
   `narrow_match` stay as edges (`trait_relations`), never collapse the records.
4. **Respect the traps:** localized-feature (SEQUENCE), member-overlap-is-weak
   (STRUCTURE), generic-anchor / pathway≠enzyme (FUNCTION), not-ready (EVOLUTION).
5. **A recurring `close_match` cluster is a modelling signal, not a merge queue.**
   If two sources genuinely describe one trait, add the shared identity anchor
   (a cross-ref, a grounding) so a deterministic operator fires — don't merge by
   hand.

---

## Reference files

| File | Contents |
|------|----------|
| [`reference/axis-operators.md`](reference/axis-operators.md) | The full per-category operator matrix (from cross-source-comparison-review-1 §1/§4), every overlay builder and its output/predicate, the trap catalogue, and the open gaps (FUNCTION pathway overlap, EVOLUTION taxon scope). |

Related: the universal identity rules and the merge *procedure* live in the
[[merge-traits]] skill; this skill only adds the per-axis candidate operators.
