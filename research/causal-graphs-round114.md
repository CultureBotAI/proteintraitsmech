---
topic: causal-graphs
round: 114
date: 2026-08-08
target: aro/FUNC_RESISTANCE — thyA, atpE, cya, 7 records
prior_round: causal-graphs-round113.md
---

# Causal graphs — Round 114: two records that give different halves of one mechanism

Round 113 found the tail was larger than I had said, and that **reading** beat every regex
I had tried. This round reads eight more and curates three families from them.

## folC and thyA split one mechanism between them

Both are **p-aminosalicylic acid** prodrug-activation loss.

* **folC** (round 113) names the **intermediate**: *"inhibits production of the dihydrofolate
  analog **hydroxyl-dihydrofolate**"*
* **thyA** (this round) names the **defect**: *"loss-of-function mutations … by **disrupting
  the substrate-binding affinity and catalytic activity**"*

Between them they give more of this mechanism than any other pair in the corpus, **and
neither gives the other's half.** A test asserts folC has the `analog` node and thyA does
not, and thyA has the `defect` node and folC does not — so a later pass cannot even out two
records that are genuinely uneven.

## atpE states the drug's action, which most target-alteration records do not

> *"Mutations in ATP synthase confer antibiotic resistance by **disrupting binding and
> blocking of ATP synthase reactions by Bedaquiline**."*

Both halves in one clause. Compare rounds 83 and 106, where rpoC and rpoB gave a structural
role and a bare resistance claim and the drug's action had to be left out.

## cya is uhpA's shape at one more remove

Round 109's uhpA lost an importer's **activator**. cya makes **cyclic AMP**, and cAMP
*"regulates the fosfomycin transporter glpT"* — the same reduced-import shape with a second
messenger in between.

**The direction is not asserted**: CARD says *"regulates"*, not "activates", so the edge is
the neutral `RO:0002211` — rounds 78 and 110's call. A test pins it.

## Provenance

* records touched: **7** · SEEDED → REVIEWED
* `just test`: **715 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **223 → 216**

## Open questions

* **~108 unconfigured drafts remain**, and reading is the only method that has worked.
  Several read this round and not yet curated: ampR, ahpC (#260), fungal SREBP, clpC1's
  second record, D-alanine synthase.
