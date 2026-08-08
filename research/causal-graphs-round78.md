---
topic: causal-graphs
round: 78
date: 2026-08-07
target: aro/FUNC_RESISTANCE — two-component regulators of efflux (ARO:3000750), 9 records
prior_round: causal-graphs-round77.md
---

# Causal graphs — Round 78: the sixth chance to write a regulator as an effector

evgS, kdpD, ParR, ParS, phoQ, smeR, smeS, TxR and the family term. **These proteins
transport nothing.** Writing them as if they effluxed the drug would repeat the
ArmR / MecI (#251) / pilQ (#254) / arlS / tet(34) (#267) error a sixth time.

So the graph ends at the **efflux process**, the way round 22's vanR/vanS ended at
vanH/vanX and round 76's cprRS ended at the Arn records:

```
determinant --participates in--> signalling (GO:0000160)
signalling  --regulates-------> efflux_process (ARO:0010000)
efflux_process --causally upstream of--> resistance
```

A test asserts the node labels contain none of *antiport*, *transporter activity*,
*gradient* or *extrud* — the vocabulary of rounds 67 and 69, which is where pump chemistry
belongs.

## Two hedges kept

* **`participates in`, not `enables`** — each record is *one half* of a pair. CARD says
  *"either a histidine kinase or a response regulator, that is **part of** a two-component
  regulatory system"*.
* **`RO:0002211 regulates`, not the positive form** — CARD says *"**directly or
  indirectly** change rates"*, not "increase". For **kdpD**, whose own definition is about
  potassium homeostasis, the link to efflux really is indirect; a positive edge would
  overstate it family-wide.

## The audit flagged a record, and it was my own false positive

`just audit-roles` went from 1 candidate to 2 after this promotion. The new one —
**pvrR** — is not one of these 9 records at all. It was caught by round 71's
`has quality (deleted or inactivated)` predicate matching the audit's `inactivat\w*`.

A `has quality` edge is a **state descriptor**, never an effector act. Fixed by excluding
those predicates structurally, and pinned by a test.

**That is the third false-positive shape this audit has produced** — after `enables`
(round 62) and the `\b`-boundary bug (round 68) — and all three were over-broad matching
on a predicate string. The audit has now cost three fixes and found zero real defects. It
is still worth having for the 565-record block it was built for, but that ratio should be
stated rather than buried.

## Provenance

* records touched: **9** · SEEDED → REVIEWED
* `just test`: **655 passed** (+3) · `just validate` on all 9: **0 failures**
* `just audit-roles`: back to **1** (vanS, known benign)
* corpus: **372,041 edges · 0 errors · 372,041/372,041 snippet-cited**
* drafts remaining: **405 → 396**

## Open questions

* **27 drafts remain under ARO:3000159**, which is #229's territory — the Mex complexes,
  arlS, and the ini operon records.
* **12 efflux drafts under ARO:0000031** (gene variant or mutant) have not been measured.
