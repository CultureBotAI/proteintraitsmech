---
topic: causal-graphs
round: 105
date: 2026-08-08
target: aro/FUNC_RESISTANCE — pgsA (4) + the rRNA parent term (4), 8 records
prior_round: causal-graphs-round104.md
---

# Causal graphs — Round 105: the second and third inconsistencies, same method

Round 104 found that I had left the fungal P450 family for a reason that did not
distinguish it from EF-Tu, which I had curated. Re-reading further found two more of the
same kind.

## pgsA — left in round 96, on round 95's own grounds

Round 96 recorded pgsA as *"a role and no mechanism"*. **That is exactly what round 95 had
curated aftA on, one round earlier.** And pgsA's definition is *richer* than aftA's — it
names the protein class **and** the exact transferase reaction:

> *"pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein
> involved in phospholipid biosynthesis. It is a **CDP-diacylglycerol-glycerol-3-phosphate
> 3-phosphatidyltransferase**."*

A test now asserts both configs assert the role and no drug link.

## The rRNA parent term — curated its children, never it

Rounds 54 and 55 curated 16S and 23S with their own mechanism sentences. **ARO:3000328 is
the term above both**, and it makes the general claim:

> *"Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic resistance to
> drugs that **target the bacterial ribosome**."*

Its graph is deliberately **weaker** than its children's. Rounds 54–55's distinctive edge —
`binding_site --part of--> determinant`, the drug's site being *inside* the target — comes
from the 16S and 23S definitions naming helix 34 and the peptidyl transferase centre. This
term names neither, so it gets no binding-site node. A test asserts the parent lacks it and
both children keep it.

This is round 101's shape again: **curating a family's members does not curate its term.**

## Three inconsistencies, one method

| round | left because | actually |
|---|---|---|
| 104 | *"thinner than EF-Tu"* | same shape as EF-Tu |
| 105 | *"a role and no mechanism"* | round 95 curated that shape |
| 105 | (never considered) | parent of two curated families |

All three found by **re-reading what I wrote**, not by new measurement. The reports are the
tool; I had been writing them and not reading them back.

## Provenance

* records touched: **8** · SEEDED → REVIEWED
* `just test`: **700 passed** (+2) · corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **265 → 257**

## Open questions

* **mshC, nudC and whiB7 (12) remain left, and the distinction does hold**: EF-Tu and P450
  name a *function* in the definition; these name only a gene. That difference is real,
  unlike the two above.
