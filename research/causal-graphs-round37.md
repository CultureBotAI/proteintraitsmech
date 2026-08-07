---
topic: causal-graphs
round: 37
date: 2026-08-07
target: aro/FUNC_RESISTANCE — efflux repressors (ARO:3000451, 27 verified), 27 records
prior_round: causal-graphs-round36.md
---

# Causal graphs — Round 37: efflux repressors, and a list that had to be read rather than matched

#231 scoped this family and said the blocker was that regulatory direction is stated in
prose rather than in the ontology. That is a **measurement**, not a decision — so this round
made it.

## The keyword match was wrong on four of thirty-one

Matching `repress` across the 88 drafts' definitions returned 31. Reading them returned
**27**:

| excluded | why |
|---|---|
| `ARO:3004056` **ArmR** | an **anti**repressor — *"allosterically inhibits MexR dimer-DNA binding"*. Opposite direction |
| `ARO:3000831` CpxR · `ARO:3004054` P. aeruginosa CpxR · `ARO:3004069` MvaT | mention repression without **being** the repressor |

ArmR is the one that matters: a keyword split would have asserted that an antirepressor
represses, in a graph whose whole content is the direction of that relation.

The 27 are a checked list rather than a derivation, because the direction is not in the
ontology structure to derive from. The check is recorded here and in the config comment so
it can be **re-run** rather than trusted.

## The shape is round 27's, applied to efflux

CARD states the causal direction outright in the archetype:

> *"AcrR is a repressor of the AcrAB-TolC multidrug efflux complex. AcrR mutations result in
> high level antibiotic resistance."* — `ARO:3000702`

So the core edge runs **backwards**, as katG's does: resistance is the *absence* of a
function. A mutated repressor stops holding the pump down, more pump is made, more drug is
exported. Nothing about the pump changes — and the pump's own mechanism is already curated
(rounds 33–36), so this graph carries only the consequence of making more of it.

## What the config deliberately does not assert

Which pump each repressor controls differs per record — AcrAB-TolC for AcrR, AdeIJK for
AdeN, CmeABC for CmeR — and is named in that record's own definition. The `pump` node is
therefore generic, with a description saying where the specific identity lives. Asserting
one pump across 27 records would be the round-22 error.

## Provenance

* records touched: **27** · SEEDED → REVIEWED · 61 refused by the precondition
* corpus after: **39,647 records · 40,115 graphs · 348,748 nodes · 370,550 edges ·
  0 errors · 370,550/370,550 edges snippet-cited**
* warnings 6,370 → **6,424**: +54, two ungrounded nodes per record
* `just validate` on all 27 individually: **0 failures**
* drafts remaining: **878 → 851**

## Open questions

* **The 20 activators are the same story with the sign flipped** and need their own config —
  over-activity drives the pump rather than loss of repression lifting it.
* **The 37 "other"** need the same reading treatment the 31 just got; some are two-component
  sensors (PhoQ, ParR) whose mechanism is LPS modification rather than efflux at all, and
  belong with mprF's neighbours rather than here.
* **The `pump` node is generic on purpose.** If per-record pump identity is wanted, it has to
  come from each record's definition text — a per-record parse, which is a different tool
  from a family config.
