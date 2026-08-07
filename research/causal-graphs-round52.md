---
topic: causal-graphs
round: 52
date: 2026-08-07
target: aro/FUNC_RESISTANCE — beta-lactam resistant PBPs (ARO:3003040), 5 records
prior_round: causal-graphs-round51.md
---

# Causal graphs — Round 52: target replacement, and a predicate that lied about why it skipped

## An 11th mechanism kind

| rounds | kind |
|---|---|
| 12–16 | inactivation |
| 18–19, 51 | target **alteration** — the target is mutated |
| 20–21 | precursor depletion / substitution |
| **52** | **target replacement — nothing about the native target changes; a foreign enzyme does the job instead** |

CARD states it verbatim, so round 51's lesson was applied *first* this time — read the
source's claim before searching:

> *"A foreign PBP2a acquired by lateral gene transfer that is able to perform
> peptidoglycan synthesis in the presence of beta-lactams."* — ARO:3000617

Only the affinity claim needed literature: **PMID:3499861** (*"…penicillin-binding protein
2' (PBP 2'), which has been associated with methicillin resistance and which has very low
affinity for beta-lactam antibiotics"*, 137 clinical strains) and **PMID:6563036**
(Hartman & Tomasz 1984 — present in resistant strains and *not* in the isogenic
susceptible ones, which is what makes it causal rather than incidental).

## The bug worth the round: a skip reason that was false

ARO:3003040 mixes two mechanisms. My first precondition discriminated by **keyword**, over
the record's **whole YAML**. It reported:

```
precondition skip: ARO:3007423 — definition describes a repressor, not a replacement PBP
```

ARO:3007423 is *"Mutant PBP3 in E. coli conferring resistance to beta-lactams"* — not a
repressor. The word came from **inherited drug-class boilerplate** ("the deactivation of
repressors that result in increased expression of genes that inactivate…"). **17 records
were excluded with a fabricated reason.**

The outcome was accidentally right — those 17 *should* be skipped, being target alteration
rather than replacement — which is exactly what makes it dangerous. A guard that reaches
the right answer for a stated reason that is false is worse than one that fails, because
the log reads as verification. I only caught it because 17 repressors seemed implausible.

Both halves are now fixed and pinned by tests:
* `_own_definition()` reads only the record's own `definition:` block.
* the predicate discriminates **structurally**, on whether the record carries
  `ARO:0001002` (target replacement), not on keywords.

Same 5 records selected; 17 now skipped as *"carries no target-replacement mechanism …
needs the round 18-19 shape"*, and **1** — ARO:3005046, MecI — still caught by reading, as
the *repressor* of mec transcription carrying a replacement mechanism id. Filed as **#251**.
Same trap as ArmR in the efflux rounds.

## Provenance

* records touched: **5** (mecA, mecB, mecC, mecD, methicillin resistant PBP2) · SEEDED → REVIEWED
* `just test`: **596 passed** (+2) · `just validate` on all 5: **0 failures**
* corpus: **371,153 edges · 0 errors · 371,153/371,153 snippet-cited**
* drafts remaining: **672 → 667**

## Open questions

* **The 17 PBP-mutation records are a queued round**, not a blocked one: same shape as
  rounds 18–19, spanning PBP3 in *E. coli*, *H. influenzae* and *H. pylori*.
* **#251** — MecI is one instance; the mec/bla regulator records likely need the round-22
  regulation shape, pointing at the replacement records this round curated.
* **A guard can state a false reason and still pass.** Nothing checks that a skip reason
  is *true*. Worth a cheap probe: skip reasons naming a concept absent from the record's
  own definition.
