---
topic: causal-graphs
round: 43
date: 2026-08-07
target: aro/FUNC_RESISTANCE — permeability (ARO:3000270), 42 records
prior_round: causal-graphs-round42.md
---

# Causal graphs — Round 43: the mirror of efflux

A **tenth** mechanism kind. Rounds 33–35 curated pumps that push the drug out; these records
are why it never gets in.

## The determinant is the channel, not the resistance

Most of these are **porins** — carO, OprD, OmpF, LamB, Omp38. Their wild-type function is to
**admit** the drug, and the resistance is the loss or down-regulation of that function. Eight
of the 42 carry ARO's `resistance by absence` mechanism id (`ARO:3003764`) alongside `reduced
permeability`, which is the ontology saying the same thing.

So the graph has the inverted shape of katG (round 27) and the efflux repressors (round 37):
`determinant --enables--> influx`, and resistance is what happens when that edge's subject is
gone.

> *"…the major role of this membrane must usually be to serve as a permeability barrier to
> prevent the entry of noxious compounds and at the same time to allow the influx of nutrient
> molecules."* — Nikaido 2003, **PMID:14665678**

Exclusion is the outer membrane's **default**; channels are the exception. That is what makes
losing one a resistance mechanism rather than a defect.

## The guard named the mechanism id, again

I guessed `ARO:3000185` for "resistance by absence". `UncoveredMechanism` refused two records
and named the real id — `ARO:3003764`. **Fourth time this session** that guessing a mechanism
id was the failure and the guard was the fix (rounds 31, 32, 42, 43).

## Provenance

* records touched: **42** · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,908 nodes · 370,754 edges ·
  0 errors · 370,754/370,754 edges snippet-cited**
* warnings 6,500 → **6,584**: +84, two ungrounded nodes per record
* `just validate` on all 42 individually: **0 failures** · `just test` 581
* drafts remaining: **813 → 771**

## Open questions

* **marA (#238) is now half-unblocked.** Its second arm is exactly this mechanism, and this
  config's evidence covers it. What it still needs is a config carrying *both* arms rather
  than being forced into either family.
* **The `influx` and `barrier` nodes are ungrounded.** GO has transmembrane-transport terms
  that might ground `influx`, as `GO:1990961` grounded `export` in the efflux rounds — the
  same cheap fix, now worth ~42 more records.
