---
topic: causal-graphs
round: 94
date: 2026-08-07
target: aro/FUNC_RESISTANCE — generic target-replacement proteins (ARO:3000381), 5 records
prior_round: causal-graphs-round93.md
---

# Causal graphs — Round 94: the abstract statement of a mechanism curated 42 rounds ago

Round 52 curated **mecA/PBP2a** — a foreign PBP doing the wall synthesis while the native
ones stay inhibited — and called it target *replacement*. This family states the same
mechanism abstractly, and **supplies the piece round 52 had to leave implicit**:

> *"Alternate proteins that have the **same functions** as other antibiotic target
> proteins, but are **structurally different and thus resistant** to antibiotics. These can
> replace the activity of other antibiotic-sensitive proteins in the presence of
> antibiotics."*

Two halves in one sentence:

* **"same functions"** — why substituting works at all
* **"structurally different and THUS resistant"** — why the drug misses it

Round 52's mecA config asserted the first and inferred the second. Here CARD's own *"thus"*
is the causal link, so the edge carries it.

## What the abstraction costs, and what it does not

The `shared_function` node is **deliberately unnamed**: CARD's claim is that the function is
*the same*, not what it is, and the members do not name a specific target. Naming one would
be inventing the very thing the family term abstracts over.

That is the opposite decision from round 52, where mecA's own definition named the target
(peptidoglycan synthesis) and the config said so. **Same mechanism, two levels of
abstraction, two configs — because the sources differ, not the biology.**

## Provenance

* records touched: **5** · SEEDED → REVIEWED
* `just test`: **680 passed** (+1) · `just validate` on all 5: **0 failures**
* corpus: **372,308 edges · 0 errors · 372,308/372,308 snippet-cited**
* drafts remaining: **306 → 301**

## Open questions

* **Read and left this round**: nudC and mshC (*"resulting in the inability for antibiotic
  to function"* — no mechanism), and the secretion-system subunits, which carry **no
  mechanism id at all** and so cannot be keyed by one.
* **247 drafts still have no config**; **53 remain decision-bound** (#309, #229).
