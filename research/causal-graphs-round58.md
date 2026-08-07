---
topic: causal-graphs
round: 58
date: 2026-08-07
target: aro/FUNC_RESISTANCE — bacA (ARO:3002986) + bcrC (ARO:3003250), 2 records
prior_round: causal-graphs-round57.md
---

# Causal graphs — Round 58: two families, one config, and a claim left out on purpose

## The measurement that shaped the round

ARO:3000012 ("molecular bypass") has **29 drafts** and looked like the next big family.
Reading them first — the discipline from round 51 — showed it is **not one mechanism**:

| under ARO:3000012 | what it actually does |
|---|---|
| bacA, bcrC | recycle undecaprenyl pyrophosphate |
| Lpx mutants | lipid A biosynthesis, outer-membrane peptide resistance |
| ddl | a **non-functional** D-Ala-D-Ala ligase |
| van genes | the whole glycopeptide cluster |

One config across that would be **round 22's error again** — asserting an operon
composition, or here a mechanism, false for most of its members. So this round is **2
records**, not 29.

## Two families sharing one config

CARD describes one step two ways:

> *"The bacA gene product (BacA) **recycles undecaprenyl pyrophosphate** during cell wall
> biosynthesis which confers resistance to bacitracin."*

> *"The bcrC gene product (BcrC) is an **undecaprenyl pyrophosphate phosphatase** …
> When overexpressed it can confer resistance to bacitracin."*

Same carrier, same step, resistance either by recycling or by more of it. **First time in
this thread two family ids share a config dict outright** — previously a family took a
list of configs; this is the inverse.

## The edge that is missing on purpose

**Bacitracin sequesters undecaprenyl pyrophosphate.** That is the textbook mode of action,
and it is why these records confer resistance at all. **Neither CARD definition states
it**, so there is no `drug0 → upp` edge.

That is round 51's lesson in its sharpest form yet: the claim I am most tempted to add is
the one I know best and the source never made. A test pins its absence, precisely because
it is the edge most likely to be added later from memory rather than from a source.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just test`: **615 passed** (+1) · `just validate` on both: **0 failures**
* `just audit-roles`: 1 candidate (vanS, known benign)
* corpus: **371,364 edges · 0 errors · 371,364/371,364 snippet-cited**
* drafts remaining: **615 → 613**

## Open questions

* **ARO:3000012's other 27 drafts need three or four separate configs**, one per real
  mechanism. The van subset overlaps the operon-modelling question that is still open.
* **`upp` has no verified CHEBI id.** Undecaprenyl pyrophosphate almost certainly has one;
  this round did not look it up rather than guess. Cheap to close.
* **Two records is a small round, and that is the finding** — the queue counted 29 where
  the mechanism counted 2.
