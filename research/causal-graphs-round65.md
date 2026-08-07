---
topic: causal-graphs
round: 65
date: 2026-08-07
target: aro/FUNC_RESISTANCE — nitroimidazole reductases (ARO:3007103), 13 records
prior_round: causal-graphs-round64.md
---

# Causal graphs — Round 65: inactivation by reduction, and a family that argues with itself

A fourth inactivation chemistry, distinct from the transfers (rounds 62–64) and the
hydrolyses: **nothing is added and no bond is cleaved.** The drug's nitro group is reduced
to an amine and the molecule stops being an antibiotic.

> *"Nitroimidazole reductases are a group of enzymes that deactivate nitroimidazole
> antibiotics by reducing their nitro functional group to an amino group."* — ARO:3007103

The `nitro --part of--> drug0` edge is round 64's device reused: the group reduced **is**
the drug's own structure, which is why changing it destroys the antibiotic.

## Two honesty problems in the family's own text

Both handled rather than smoothed, and both pinned by tests.

**1. CARD states the chemistry causally and the resistance only as an association.**

> *"These enzymes are **associated with** resistance to nitroimidazole derivatives…"*

Not "confer". The `determinant → resistance` edge carries **both** sentences with `notes`
saying which is which, rather than quoting only the strong one and letting the graph imply
a causal claim CARD declined to make.

**2. The family contains its own negative result.**

> *"**NimB expression alone is not sufficient for nitroimidazole resistance.**"* —
> ARO:3007671

The enzyme is necessary but not sufficient; constitutive transcription from a promoter
mutation is also required. That sentence **bounds** what the other two snippets claim, so
it is quoted on the edge — the same use of a negative result as rounds 20 and 23, but this
is the first time the negative came from *inside* the family being curated rather than
from a paper.

This is the third distinct kind of source-hedge handled in four rounds: round 63's
"usually ATP, sometimes GTP" (an unresolved alternative), round 64's unusual precision,
and now an explicit insufficiency claim. Reading each definition rather than assuming a
house style keeps paying.

## Provenance

* records touched: **13** · SEEDED → REVIEWED · 0 skipped
* `just test`: **632 passed** (+2) · `just validate` on all 13: **0 failures**
* `--verify`: **0 problems, 0 near-misses**
* `just audit-fit`: **1 stranded** (tet(M), #270) — unchanged
* corpus: **371,683 edges · 0 errors · 371,683/371,683 snippet-cited**
* drafts remaining: **529 → 516**

## Open questions

* **I was wrong last round that non-van work was nearly exhausted.** Measuring instead of
  asserting shows EF-Tu (11), SMR efflux pumps (11), and a 67-record
  `antibiotic inactivation enzyme` group still un-configured. The correction matters more
  than the miss: I had started reasoning from a remembered impression of the queue rather
  than from a count, which is the exact habit rounds 58–64 were built on avoiding.
* **#270 (tet(M))** remains the only stranded curated record.
