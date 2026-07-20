---
topic: causal-graphs
round: 1
date: 2026-07-20
target: mcsa/STRUCT_ACTIVE_SITE — MCSA:2 (beta-lactamase class A, UniProtKB:P62593)
prior_round: none (first round — establishes the pattern)
method: M-CSA entry 2 mechanism page (verbatim), UniProtKB + SIFTS numbering, ChEBI id checks
---

# Causal graphs — Round 1: class A β-lactamase (MCSA:2)

First round of the [[edison-causal-graphs]] skill. The corpus was **greenfield**
(0 records with `causal_graphs`); this round writes the first mechanism graph and,
alongside it, the missing structural gate (`scripts/audit_causal_graphs.py` →
`just audit-graphs`). Target chosen from the gap audit: M-CSA is the one source
that already encodes stepwise mechanisms *with* per-step references, so a graph is
transcription-with-grounding, not invention.

## Gap (from the audit)
| source | category | n | w/graph | w/ev |
|--------|----------|--:|--------:|-----:|
| aro | FUNC_RESISTANCE | 7,452 | 0 | 3,242 |
| proteintraitsmech (BioLiP) | STRUCT_BINDING_SITE | 6,020 | 0 | 0 |
| **mcsa** | **STRUCT_ACTIVE_SITE** | **1,003** | **0** | **1,000** |
| interpro | SEQ_ACTIVE_SITE | 133 | 0 | 133 |

M-CSA `STRUCT_ACTIVE_SITE` is the flagship: mechanism-rich, ~100% already carry
`evidence` PMIDs, and its entries publish the causal steps. Picked **MCSA:2**
(class A β-lactamase) — the same protein the seq/struct/function alignment analysis
used as its worked exemplar (`research/sequence-structure-function-alignment-analysis-1.md`),
so numbering is already reconciled.

## Mechanism (researched — M-CSA entry 2, proposal 1)

Two covalent steps on the Ser70 nucleophile (source quotes verbatim; each is the
`snippet` on the corresponding edge). **Numbering:** M-CSA/literature use Ambler
(Ser70, Lys73, Ser130, Glu166); the record's UniProt frame calls these residues
68/71/128/164 — reconciled via SIFTS (author = UniProt + 2 on PDB 1BTL).

**Acylation**
1. Glu166 — "acts as a general base towards a structurally conserved water
   molecule, leading to the deprotonation of Ser70 (proton relay)".
2. "Glu166 deprotonates a conserved water molecule which in turn deprotonates the
   nucleophilic Ser70, initiating the nucleophilic addition onto the carbonyl
   carbon of the beta-lactam" → first tetrahedral intermediate.
3. Lys73 — "forms an ion pair with Ser 70, which is involved in the proton transfer
   event".
4. Ser130 — "mediates protonation of the substrate nitrogen" (protonates the
   leaving-group N as the ring opens).
5. "The tetrahedral intermediate collapses, cleaving the C-N bond in the
   beta-lactam" → covalent **acyl-enzyme intermediate**.

**Deacylation**
6. "Glu166 deprotonates water, which initiates a nucleophilic addition at the
   carbonyl carbon, forming a new tetrahedral intermediate".
7. "Water attacks the acyl-enzyme intermediate" → second tetrahedral intermediate.
8. "final collapse releases product and regenerates Ser70" → hydrolysed β-lactam
   (substituted β-amino acid), EC:3.5.2.6 / RHEA:20401.

## Graph design (`graph_id: catalysis`, 11 nodes / 11 edges)

- **Nodes (grounded 8/11):** ser70·lys73·ser130·glu166 (RESIDUE →
  `UniProtKB:P62593`, Ambler # in label); substrate (CHEMICAL → `CHEBI:35627`);
  water_acyl + water_deacyl (CHEMICAL → `CHEBI:15377`); product (CHEMICAL →
  `CHEBI:33705` = "substituted β-amino acids", verified on ChEBI); tetra1 /
  acyl_enzyme / tetra2 (STATE, intrinsically label-only — transient chemical
  states have no ontology CURIE).
- **Edges (11/11 snippet-cited):** the acylation chain glu166→water_acyl→ser70,
  lys73→ser70, ser70→substrate→tetra1, ser130→substrate, tetra1→acyl_enzyme; then
  the deacylation chain glu166→water_deacyl→acyl_enzyme→tetra2→product.
  `predicate_id` = `RO:0002436` (molecularly interacts with) for physical/chemical
  residue↔ligand steps, `RO:0002411` (causally upstream of) for state→state
  transitions; the specific chemistry (nucleophilic attack, deprotonates,
  protonates, collapses to) is the human-readable `predicate`.
- **Reference:** every edge cites the M-CSA entry-2 URL with the verbatim step
  quote as `snippet`; `notes` names the step and a primary PMID (17408273).

## Provenance
records touched: **1** (`MCSA:2`) · edges written: **11** · all edges cited: **yes**
(11/11 verbatim snippet) · nodes grounded: **8/11** · status: **SEEDED → REVIEWED**
(+ `curation_history` event, `llm_assisted: true`).

Gates: `just validate` → **No issues found** (closed-mode schema); `just audit-graphs`
→ **0 errors**, 3 warnings (the 3 STATE intermediates are label-only, expected).
New tooling: `scripts/audit_causal_graphs.py` (structural gate — dangling
subject/object, node_id uniqueness, node_type enum, evidence-presence, CURIE
patterns; `--strict` also fails ungrounded nodes / snippet-less edges).

## Open questions / next targets
- **STATE grounding.** Tetrahedral / acyl-enzyme intermediates have no clean CURIE;
  left label-only (audit WARN, not ERROR). Could mint local grounding or use a
  reaction-intermediate ontology later.
- **Predicate precision.** RO lacks fine catalytic-chemistry predicates
  (deprotonate/protonate/nucleophilic-attack); the label carries the specificity,
  RO carries the coarse causal class. A curated RO/MOP mapping is a future refinement.
- **Next rounds:** (2) a second M-CSA archetype of a different chemistry (a
  metalloenzyme, e.g. an M-CSA class B β-lactamase MCSA:15/16 — Zn-mediated, tests
  the LIGAND/metal path); (3) begin ARO `FUNC_RESISTANCE` (determinant → mechanism
  → resistant-phenotype edges), the largest mechanism-rich gap.
