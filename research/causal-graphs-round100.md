---
topic: causal-graphs
round: 100
date: 2026-08-08
target: aro/FUNC_RESISTANCE — bacitracin, fosfomycin, macrolide inactivation terms, 3 records
prior_round: causal-graphs-round99.md
---

# Causal graphs — Round 100: three family terms the audit named

`audit-drafts` listed Bah amidohydrolase and the fosfomycin family at the end of round 99;
reading them turned up a third with the same shape. Each is **one record — the family term
itself** — and each says the same kind of thing:

> *"Bah amidohydrolases are membrane proteins that **inactivate bacitracin**."*
> *"Enzymes that **inactivate fosfomycin by chemical modification**."*
> *"Enzymes shown to **inactivate macrolide antibiotics by chemical modification**…"*

A drug and a reaction *type*, with no reaction named. **Round 85's rule applies unchanged**:
no reaction node, because naming one would import a chemistry the term does not claim — and
the specific chemistries are curated separately (rounds 62–64, 68, 70) or not at all.

One builder serves all three, and a test asserts none of them mentions *acetyl*, *phospho*,
*nucleotidyl*, *hydroxyl* or *esterase*. That list is not hypothetical: macrolide esterases
and phosphotransferases are exactly what a reader would reach for here.

## What a hundred rounds settled

The rule that survived from round 51 onward, in one line: **assert what the source says,
quote its hedges, and when a mechanism you know is absent, leave the edge out and say why.**
Most of the 694 tests pin one instance of it.

The rule that arrived late and mattered most: **ask what your own guards refused.** Rounds
96–100 curated fourteen records that were never blocked, never hard, and never asked about
— three gyrB records, ArmR, PDR1, tet(34), three protection records, and these three. All
of them surfaced from `audit-drafts` (#316), built at round 96.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **694 passed** (+2) · `--verify-all`: **0 problems** · `audit-drafts`: 0 accepted
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **282 → 279**

## Open questions

* **53 remain decision-bound** (#309, #229) and **10 are #215's two-component pairs**.
* The rest are per-record, and `audit-drafts` is the tool that finds which of them are
  reachable.
