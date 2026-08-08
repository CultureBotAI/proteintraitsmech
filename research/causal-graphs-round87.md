---
topic: causal-graphs
round: 87
date: 2026-08-07
target: aro/FUNC_RESISTANCE — Van ligase + VanZ (ARO:3002906, ARO:3000116), 2 records
prior_round: causal-graphs-round86.md
---

# Causal graphs — Round 87: the van block was not all operon-level either

I had written that the remaining van/glycopeptide records were behind the gene-cluster
modelling question. Measuring their definitions found **8 of 35 are not cluster-level at
all** — they describe individual proteins with their own mechanisms:

| record | its own definition |
|---|---|
| **Van ligase** | *"synthesize alternative substrates for peptidoglycan synthesis that **reduce vancomycin binding affinity**"* |
| **VanZ** | *"**prevents the incorporation of the terminal D-Ala** into peptidoglycan subunits"* |
| vanU | *"a transcriptional activator of vancomycin resistance genes"* |
| vanJ, vanJ homologue, vanK | membrane protein / Fem-family enzyme |

**Fifth time this session I asserted a block was exhausted and was wrong on measuring it.**
The pattern is consistent enough now to state as a property of how I work rather than as a
series of accidents: I generalise from the records I happened to read, and the
generalisation survives until something forces a count.

## Two curated, with their omissions marked

**Van ligase** is round 21's precursor-substitution shape reached from the record's own
sentence rather than from the pathway papers.

**VanZ** gets one edge. CARD says it *prevents* incorporation of the terminal D-Ala and
never says **how**, nor how a missing D-Ala reaches teicoplanin resistance. Both gaps are
stated in the note rather than bridged.

## Three of my own mistakes, all caught

1. **Guessed the mechanism id.** I wrote `ARO:0001002` (target replacement); both records
   carry `ARO:3000213`. Zero records written until I looked.
2. **A blanket replace clobbered an unrelated config.** Fixing (1) with a bare
   `"mech": {"ARO:0001002":` → `"ARO:3000213"` substitution also rewrote **round 52's PBP
   target-replacement config**. The suite caught it; a test now names that id.
   **Third destructive blanket edit this session**, after round 70's `--repromote` and
   round 86's assignment-instead-of-append.
3. **My own #256 guard caught my new skip reasons.** They claimed *"describes a gene
   cluster"* and *"describes an operon member"* when the checks behind them only match the
   words *cluster* / *operon*. Reasons now claim no more than they check.

That third one is the guard working exactly as designed, on code written minutes earlier by
the person who wrote the guard.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just test`: **668 passed** (+2) · `--verify-all`: 85 families, **0 problems**
* corpus: **372,256 edges · 0 errors · 372,256/372,256 snippet-cited**
* drafts remaining: **325 → 323**

## Open questions

* **6 van protein records remain readable**: vanU (regulation), vanJ ×2, vanK, and the two
  family terms. Each needs its own reading.
* **27 van records really are cluster-level** and really are behind the modelling question
  — that part of the earlier claim held.
