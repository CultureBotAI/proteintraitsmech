---
topic: causal-graphs
round: 63
date: 2026-08-07
target: aro/FUNC_RESISTANCE — rifampin hydroxylation, phosphorylation, glycosylation (ARO:3000576), 9 records
prior_round: causal-graphs-round62.md
---

# Causal graphs — Round 63: the other three chemistries, written as a factory

Round 62 curated the **arr** ADP-ribosyltransferases and left the family's other three
reactions. This finishes them: hydroxylation (4), phosphorylation (3), glycosylation (2).
**ARO:3000576's 17 member records are now all curated**; only the abstract family term
itself remains a draft, correctly, since it names no specific chemistry.

## Written as a factory, on purpose

All four are the same sentence — *an enzyme covalently modifies the drug, the drug stops
working* — differing only in the chemistry. So they share one builder:

```python
_rifampin_modification_config(mech_id, human, snippet, activity_label)
```

Two reasons, both learned the hard way this session:

* **Four hand-written preconditions is four chances to write a bad pattern.** That defect
  cost four fixes here (#252, #255, #264, #267). The factory's discriminator is purely
  structural — the mechanism id the record carries — so there is no pattern to get wrong.
* **Parallel configs drift.** Round 55 had to add a test pinning that the two rRNA configs
  kept the same partonomy edge. A factory makes drift impossible rather than detectable.

## One thing deliberately not asserted

CARD's phosphorylation definition reads *"Phosphorylation of antibiotic **usually by ATP,
sometimes GTP**."* The phosphoryl donor is therefore **not a node**. Naming ATP would
assert a specificity the source explicitly declines to give — and this is the first time
the source's own hedge, rather than its silence, was the thing to preserve.

A test pins that neither ATP nor GTP appears in the node labels.

## Provenance

* records touched: **9** · SEEDED → REVIEWED · family now 17/17 members curated
* `just test`: **628 passed** (+2) · `just validate` on all 9: **0 failures**
* `--verify`: 0 problems, 0 near-misses across all four configs
* `just audit-fit`: **1 stranded** (tet(M), #270) — unchanged
* corpus: **371,579 edges · 0 errors · 371,579/371,579 snippet-cited**
* drafts remaining: **551 → 542**

## Open questions

* **The efflux/regulator block is what is left**, and it is mostly per-record rather than
  per-family — round 18's original assessment, still true.
* **#270 (tet(M))** remains the only stranded curated record.
