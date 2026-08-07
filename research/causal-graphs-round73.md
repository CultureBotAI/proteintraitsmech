---
topic: causal-graphs
round: 73
date: 2026-08-07
target: aro/FUNC_RESISTANCE — phosphoethanolamine transferases (ARO:3003580), 7 records
prior_round: causal-graphs-round72.md
---

# Causal graphs — Round 73: the other way to neutralise lipid A, found by a guard

ARO:3003580 already had a config: **L-Ara4N addition**. These 7 records neutralise lipid A
with **phosphoethanolamine** instead — same charge outcome, different moiety.

**#264's near-miss detector found them.** In round 69 it reported:

```
near-miss skip  ARO:3004269 (pmr phosphoethanolamine transferase):
  refused for lacking "L-Ara4N addition", but every token of it appears in the definition
```

I read that as a false positive at the time and moved on. It was not — the pmr definition
really does contain "L-Ara4N" and "addition", because **pmr transfers both moieties**. The
detector was pointing at a genuine gap: a whole second chemistry with no config.

That is the first time a guard I built found *work*, rather than a defect.

## The causal chain, and one hedge kept separate

The mechanism term states it causally:

> *"The loss or reduction of the net negative charge … is a mechanism of resistance for
> cationic antimicrobials that **depend on the negative charge for binding**."* — ARO:3003588

and pmr's definition names the consequence: *"impedes the binding of colistin to the cell
membrane"*.

But the chemistry term hedges: *"often **associated with** polymyxin resistance"*
(ARO:3004112). So it is cited **for the reaction** and the causal snippets carry the
resistance claim. A test pins that separation — mixing them would let the graph inherit a
strength its snippet does not have.

## A reporting artefact worth naming

`--verify` still shows a near-miss for ARO:3004269 against the **L-Ara4N** config, even
though the pEtN config now owns that record. Near-misses are reported per-config, so on a
multi-config family one config's refusal is visible even when another accepts. Same shape
as round 53's double-counted skip counters. Not a data defect, but it means near-miss
output on list-form families needs reading with that in mind.

## Provenance

* records touched: **7** · SEEDED → REVIEWED
* `just test`: **646 passed** (+2) · `just validate` on all 7: **0 failures**
* `--verify`: **0 problems**
* corpus: **371,961 edges · 0 errors · 371,961/371,961 snippet-cited**
* drafts remaining: **427 → 420**

## Open questions

* **14 charge-alteration drafts remain** under other sub-families (ARO:3007429 polymyxin-
  associated, and others) — each needs its own reading.
* **Near-miss reporting on list-form families** should probably suppress a config's
  near-miss when another config in the same family accepts the record. Small, and it would
  have saved me dismissing this one in round 69.
