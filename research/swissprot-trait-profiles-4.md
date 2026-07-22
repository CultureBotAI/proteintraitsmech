---
topic: swissprot-trait-profiles
phase: 4
date: 2026-07-22
issue: "#7 — materialise cross-axis rules into the corpus"
prior: swissprot-trait-profiles-3.md
---

# Swiss-Prot trait profiles — Phase 4: materialise the cross-axis rules

Phase 3 mined the empirical cross-axis rules (a sequence signature that essentially
always encodes a specific fold; traits that imply function). Phase 4 **writes them
back into the corpus** as a data-backed equivalence overlay, so the browser and any
consumer see the sequence↔structure↔function coupling as typed edges on the trait
records — not just a report.

## What was materialised
`just trait-correlations --min-support 30 --min-conf 0.95 --min-lift 5
--emit-overlay data/equivalence/trait_cooccurrence.tsv` →

| overlay | edges | meaning |
|---|--:|---|
| **`data/equivalence/trait_cooccurrence.tsv`** | **516** | cross-axis empirical co-occurrence, `biolink:related_to` |
| — `seq-encodes-fold` | 284 | SEQUENCE signature → STRUCTURE fold (226 at conf ≥0.99) |
| — `trait-implies-function` | 232 | SEQUENCE/STRUCTURE trait → FUNCTION (GO/EC) |

Each edge's `relation_source` carries the evidence:
`seq-encodes-fold|conf=1.00|lift=625x|n=32|Swiss-Prot(human)`. Both endpoints are
real `ProteinTraitRecord` identifiers (they came from the corpus trait index), so
the overlay is auto-loaded bidirectionally by `build_docs_index.py` (the `*.tsv`
glob), exactly like the other equivalence overlays.

## Why an overlay, not `trait_relations`
Cross-axis edges are **relate-only, never a merge** (per the merge-within-axis
skill), and the equivalence overlay is the established home for derived cross-axis
relations (cf. `seq_struct_comembership.tsv`). This one is stronger than
co-membership: it is grounded in **actual protein co-occurrence** across 20,000
Swiss-Prot proteins with a confidence/lift threshold, not just a shared CATH id.

## The three cross-axis overlays now
| overlay | basis | edges |
|---|---|--:|
| `seq_struct_func_sites.tsv` (Path 1) | shared UniProt **residues** | 778 |
| `seq_struct_comembership.tsv` (Path 2) | shared **CATH grounding** on exemplars | 13,400 |
| **`trait_cooccurrence.tsv` (Path 4, new)** | **empirical protein co-occurrence** (conf/lift) | 516 |

Path 1 is residue-precise but sparse; Path 2 is broad but grounding-only; Path 4 is
the empirical middle — "these two trait classes actually travel together on real
proteins, X% of the time."

## Next (phase 5)
- **Auto-suggest `canonical_examples`**: a protein carrying signature X (from the
  profile matrix) is a candidate example for fold Y's record where the
  `seq-encodes-fold` rule holds — write the strongest as `canonical_examples`,
  connecting real proteins to the trait records (and giving the base residue-frame
  overlay shared exemplars).
- **Multi-organism** confirmation (mouse/yeast/E. coli) that the rules aren't
  human-specific; held-out-organism decision-tree test.
- Protein×trait **browser map** (UMAP/PaCMAP of `profiles.jsonl`).

## Gate
Stdlib-only; overlay is 4-column `biolink:` TSV, endpoints spot-checked as existing
trait records. Recipe: `just trait-correlations … --emit-overlay <path>`.
