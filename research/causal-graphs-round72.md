---
topic: causal-graphs
round: 72
date: 2026-08-07
target: aro/FUNC_RESISTANCE — host-nutrient bypass (3) + sequestration (1), 4 records
prior_round: causal-graphs-round71.md
---

# Causal graphs — Round 72: two more mechanism kinds, and the guard earning its keep again

The last two mechanism-keyed pockets round 71's measurement found. Both use its root-keyed
treatment: the mechanism id is not an `is_a` ancestor of its own records, so `ARO:3000000`
is a scan root and the precondition does the selecting.

## 14th kind — bypass by host-nutrient uptake (3 records)

> *"Resistance via uptake of host nutrients to bypass antibiotic mechanism."*

**Nothing resists and nothing is modified.** The cell imports the product of the pathway
the drug blocks, and the target stops mattering. Distinct from round 58's bacA/bcrC, where
the cell makes *more* of what the drug sequesters — here it doesn't make it at all.

The worked case (ThfT expanding ECF transporters to include folate) is scoped in its
notes: the mechanism term names no nutrient, and the other two records are the generic
family and the transporter component.

## 15th kind — sequestration (1 record)

> *"Inactivation of an antibiotic by formation of a complex, preventing interaction of the
> antibiotic with its target."*

**The drug is bound, not chemically changed** — the one distinction that separates this
from every inactivation chemistry in rounds 62–70. A test asserts the predicates contain
"binds the drug" and none of hydrolysis/acetylation/phosphorylation/reduction.

The `complex --has part--> drug0` edge follows **round 21's correction**: a
drug-interacts-with-complex edge would be circular, since the drug is a *constituent* of
the complex, not something interacting with it.

## UncoveredMechanism caught the one thing I got wrong

The sequestration config initially covered only `ARO:3001206`. BRP(MBL) also carries the
generic `ARO:0001004`, so the guard **refused to promote it** — correctly. It reported
"selected but still draft", which is exactly the state that means *the config chose this
record and then could not honestly write it*.

The fix was not a workaround: CARD's sequestration definition **opens with** *"Inactivation
of an antibiotic"*, so the same sentence genuinely supports both ids. A test asserts the
two snippets are identical **and** that the shared one starts with that phrase — so a
future reader can see it is one claim covering two ids, not a snippet borrowed to satisfy
a guard.

That is the sixth time this session `UncoveredMechanism` has stopped a record from being
written on evidence that did not cover it.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **644 passed** (+2) · `just validate` on all 4: **0 failures**
* corpus: **371,934 edges · 0 errors · 371,934/371,934 snippet-cited**
* drafts remaining: **431 → 427**

## Open questions

* **The mechanism-keyed pockets are now exhausted** — verified by the same measurement that
  found them, not asserted. What remains is concentrated in `ARO:3000212` (304 drafts),
  efflux (50), cell-wall restructuring (41) and charge alteration (22).
* **304 `ARO:3000212` drafts** are spread across families rather than concentrated, which
  is round 18's per-record assessment arriving.
