---
topic: causal-graphs
round: 85
date: 2026-08-07
target: aro/FUNC_RESISTANCE — aminoglycoside modifying enzymes (6) + Rv0678 (5), 11 records
prior_round: causal-graphs-round84.md
---

# Causal graphs — Round 85: matching the graph's generality to the source's

## Aminoglycoside modifying enzymes — general, on purpose

> *"…proteins involved in the enzymatic inactivation of aminoglycoside antibiotics through
> **chemical modification**."*

Round 68 curated *nucleotidylation*, *phosphorylation* and *acylation* as separate configs
under ARO:3000557. This family term names **no reaction at all**, and neither do its
members. So the graph has a deliberately unspecific `modification` node, and a test bans
*acetyl*, *phospho*, *nucleotidyl* and *adenylyl* from its labels.

Aminoglycoside-modifying enzymes are the textbook example of exactly those three
chemistries, which is what makes the ban necessary rather than pedantic — round 84's
finding that the failure mode is **pattern-matching a previous round**, one round later.

## Rv0678 — the step that matters is the one CARD omits

> *"Rv0678 encodes a transcription factor which **negatively regulates** the expression of
> the mmpS5/L5 efflux pump."*

That is a **repressor**. These records confer resistance because mutations *relieve* the
repression and efflux rises — and **CARD never says that**. It states the repression and
stops.

So the graph does too: one edge, `negatively regulates`, with notes recording that
derepression is not asserted.

**The mirror of round 79.** There, ARO:3000219 says mutations *"result in increased
expression"*, so the edge is positive and the mechanism is complete. Here the same
biology arrives one sentence short, and the difference between the two graphs is entirely
a difference between two CARD sentences — not between two mechanisms.

## Provenance

* records touched: **11** (6 + 5) · SEEDED → REVIEWED
* `just test`: **665 passed** (+2) · `just validate` on all 11: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **338 → 327**

## Open questions

* **Rv1258c (5) and mshC (4) were read and left.** Rv1258c: *"Mutations in the Rv1258c
  (Tap) efflux pump contributing to antibiotic resistance"* — names the pump, no mechanism.
  mshC: *"Mutations … resulting in the inability for antibiotic to function"* — no
  mechanism and no role.
* **The derepression step for Rv0678 is a well-posed literature task**, joining round 81's
  PDIM→pyrazinamide and round 83's rpoC.
