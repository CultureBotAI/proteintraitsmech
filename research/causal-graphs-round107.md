---
topic: causal-graphs
round: 107
date: 2026-08-08
target: aro/FUNC_RESISTANCE — fabI (2), nfsB (2), rpoA (3), 7 records
prior_round: causal-graphs-round106.md
---

# Causal graphs — Round 107: three definitions, three different amounts of evidence

## fabI gives what fabG1 never did

Round 51 spent three attempts failing to source a drug action for **fabG1**, and closed
#219 by finding CARD had never claimed one. **fabI is the same pathway**, and CARD gives it
outright:

> *"fabI is a enoyl-acyl carrier reductase … **The bacterial biocide Triclosan blocks the
> final reduction step in fatty acid elongation, inhibiting biosynthesis.** Point mutations
> in fabI **can** confer resistance to Triclosan and Isoniazid."*

Enzyme, drug action, mutation, resistance. Two drugs are named as resisted and **only
Triclosan's action is described** — so isoniazid gets no edge, which is exactly the gap
round 51 could not close for its neighbour.

## nfsB keeps a genetic precondition

> *"Mutations in nfsB lead to increased resistance to nitrofurazone and furazolidone **in
> an nfsA mutant background**."*

Prodrug-activation loss — the enzyme reduces the antibiotics themselves — **conditional on
another gene already being broken**. That clause is a node and an edge, not a footnote:
dropping it turns *"mutations confer resistance when another gene is broken"* into
*"mutations confer resistance"*. A test pins it.

This is the first **genetic precondition** in the corpus, distinct from the hedges collected
since round 63 (a value hedged, a claim attributed, a magnitude qualified).

## rpoA gets less than rpoB and rpoC, because it says less

Rounds 83 and 106 gave rpoC and rpoB an `active_center` node, because both definitions say
what their subunit forms. **rpoA's does not** — so it gets `participates in transcription`
and nothing structural. A test asserts the two have it and rpoA lacks it.

Three sibling records, three graph sizes, each matching its own sentence.

## Provenance

* records touched: **7** · SEEDED → REVIEWED
* `just test`: **703 passed** (+2) · corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **254 → 247**

## Open questions

* **19 unconfigured drafts naming a function remain**, including **kasA** — #220's original
  record, which should not be curated before that decision.
