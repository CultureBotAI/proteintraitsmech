---
topic: causal-graphs
round: 38
date: 2026-08-07
target: aro/FUNC_RESISTANCE — efflux activators (ARO:3000451, 15 verified), 15 records
prior_round: causal-graphs-round37.md
---

# Causal graphs — Round 38: the same family, the opposite sign

Round 37 curated 27 efflux **repressors** — resistance by losing a function. These are the
15 **activators**: resistance by the regulator *doing* something.

```
repressor (r37)   determinant --negatively regulates--> repression   RO:0002212
activator (r38)   activation   --positively regulates--> pump        RO:0002213
```

Two configs under one family term, selected by verified lists rather than by ancestry —
because the direction is stated in prose and ARO does not encode it.

> *"AdeR is a positive regulator of AdeABC efflux system."* — `ARO:3000553`

## The list is deliberately conservative, and that cost a real record

The pattern excluded **marA**, which *is* a transcriptional activator — its definition does
not say so in a form the check recognises. Eight records were excluded in total.

That is the right way to be wrong here. **A false exclusion leaves a record as a draft; a
false inclusion asserts the wrong direction** on a graph whose entire content is that
direction. The excluded ids are in the config comment so they can be revisited by reading
rather than re-derived.

`_EFFLUX_ACTIVATORS` and `_EFFLUX_REPRESSORS` are asserted **disjoint** by a test, since the
one record that appeared in both keyword passes — ArmR, an antirepressor — is exactly the
kind that must land in neither.

## Provenance

* records touched: **15** · SEEDED → REVIEWED · 48 refused
* corpus after: **39,647 records · 40,115 graphs · 348,778 nodes · 370,580 edges ·
  0 errors · 370,580/370,580 edges snippet-cited**
* warnings 6,424 → **6,454**: +30, two ungrounded nodes per record
* `just validate` on all 15 individually: **0 failures**
* drafts remaining: **851 → 836**

## Open questions

* **46 records remain under this family term** — the 8 excluded here, plus ~37 that state
  neither direction. Several are two-component **sensors** (PhoQ, ParR, CpxA) whose
  mechanism is LPS modification rather than efflux, and belong with mprF (round 32) rather
  than here. Reading them is the same cheap measurement that produced rounds 37 and 38.
* **marA specifically is worth one look**: it is the archetype of the mar regulon and its
  exclusion is a limitation of the check, not a judgement about the biology.
