---
topic: causal-graphs
round: 101
date: 2026-08-08
target: aro/FUNC_RESISTANCE — rifampin + streptogramin inactivation terms, 2 records
prior_round: causal-graphs-round100.md
---

# Causal graphs — Round 101: the builder I wrote one round ago, applied to the two it missed

Round 100 built a builder for family terms of the form *"enzymes inactivate DRUG by
chemical modification"* and registered **three** families. `audit-drafts` immediately
listed two more with the same wording:

> *"Enzymes that inactivate **rifampin** antibiotics by chemical modification."*
> *"Resistance to **streptogramin** antibiotics may be conferred through enzymatic
> inactivation."*

Both had their **members** curated in rounds 62–64 — the rifampin chemistries and the
vat/vgb split. **Curating a family's members does not curate its term**, and nothing had
been asking.

A test now pins all five, so the next such term gets added to the list rather than
rediscovered.

## The shape of the last six rounds

| round | records | how they surfaced |
|---|--:|---|
| 96 | 3 | audit-drafts: refused by a too-narrow precondition |
| 97 | 2 | audit-drafts: ArmR, cited all session, never curated |
| 98 | 1 | audit-drafts: refused four times, never re-homed |
| 99 | 3 | audit-drafts: no mode config fit |
| 100 | 3 | audit-drafts: named at the end of round 99 |
| **101** | **2** | **audit-drafts: my own builder, under-registered** |

**Fourteen records in six rounds, none of them blocked, hard, or unmeasured** — all of them
things I had walked past. The audit is doing the finding; the rounds are doing the reading.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just test`: **694 passed** (+1) · `audit-drafts`: 0 accepted
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **279 → 277**

## Open questions

* **`audit-drafts`'s remaining buckets are now dominated by the decision-bound sets**:
  ARO:3000748 (22, #229), ARO:3000451 (10, #215), ARO:3000012 (10, mostly van).
