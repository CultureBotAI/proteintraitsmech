---
topic: causal-graphs
round: 71
date: 2026-08-07
target: aro/FUNC_RESISTANCE — resistance by absence (ARO:3003764), 9 records
prior_round: causal-graphs-round70.md
---

# Causal graphs — Round 71: a 13th mechanism kind, and a claim of mine that was wrong again

## I said everything left needed a decision. It did not.

Round 70 ended with *"the remaining families each turn on a categorisation or modelling
question rather than on effort"*. That was asserted from an impression of the queue, and
measuring all 440 remaining drafts by **mechanism id** rather than by family found:

| mechanism | drafts |
|---|--:|
| resistance by absence (ARO:3003764) | **9 — this round** |
| resistance by host-dependent nutrient acquisition | 3 |
| antibiotic inactivation by sequestration | 1 |

None entangled with #229 or the van question. **Third time this session I have called
something exhausted or blocked and been wrong on measuring it** (after round 64's "non-van
work nearly exhausted" and #223/#231 earlier). The recurring error is the same: reasoning
from a remembered shape of the queue instead of counting.

## A 13th mechanism kind

Round 56's pncA was resistance by losing an *activity*. This is broader: **resistance
because the gene is not there at all.**

> *"Mechanism of antibiotic resistance conferred by deletion of gene (usually a porin)."*

## Keyed on the root term, deliberately

ARO:3003764 is a **mechanism** id, and its 9 records sit under unrelated families — a
stress-activated kinase (Hog1), a UDP-glucuronic acid decarboxylase (UXS1), a PhoPQ
regulator (mgrB), porins — with **no common ancestor but the root**. The promoter walks
`is_a` ancestry, so a mechanism id cannot be a family key. The config keys `ARO:3000000`
and lets the precondition select exactly.

That makes the candidate set the whole corpus, which is safe for `--apply` (drafts only,
precondition-filtered) and is precisely the case **#280's blast-radius guard** was built
for on the `--repromote` path — verified this round: re-promoting touches 9, not 5,036.

## Two things not asserted

1. **That the deleted gene is a porin.** CARD says *"usually"* — round 63's donor hedge in
   another costume — and these records include a kinase, a decarboxylase and a regulator.
2. **The downstream consequence.** It differs per record: Hog1's deletion raises exposed
   chitin, UXS1's accumulates UDP-glucuronic acid, mgrB's derepresses PhoPQ. No sentence
   covers all of them, so `absence → resistance` is the only downstream edge. Each record's
   own consequence is a good per-record addition and none is a family claim.

## Provenance

* records touched: **9** · SEEDED → REVIEWED
* `just test`: **642 passed** (+1) · `just validate` on all 9: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **440 → 431**

## Open questions

* **Two more mechanism-keyed pockets remain** — host-dependent nutrient acquisition (3) and
  inactivation by sequestration (1). Both need the same root-keyed treatment.
* **The 304 drafts carrying only `ARO:3000212`** are the real remainder, and they are
  spread across families rather than concentrated. That is round 18's per-record assessment
  arriving at last.
