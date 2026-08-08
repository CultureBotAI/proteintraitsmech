---
topic: causal-graphs
round: 86
date: 2026-08-07
target: aro/FUNC_RESISTANCE — named efflux subunits (ARO:3000748), 2 records
prior_round: causal-graphs-round85.md
---

# Causal graphs — Round 86: separating what #229 blocks from what it doesn't

I had written that ARO:3000748 was decision-blocked, with *"roughly 12–13 genuine single
subunits"* waiting behind #229. **The 12–13 was wrong.** Measuring the definition shapes
found **two**:

> *"MexA is the membrane fusion protein **of** the MexAB-OprM multidrug efflux complex."*
> *"MexB is the inner membrane multidrug exporter **of** the efflux complex MexAB-OprM."*

A subunit describes **its place in something larger**. A complex's definition says it
*"consists of"* or *"is composed of"* components — and widening the pattern to match a bare
"component" pulls in all seven Mex complexes, which is checked and recorded in the
precondition's docstring.

So the separable part of #229's family was 2 records, not 12. **That is the fourth estimate
this session I made from impression and had to correct on measuring** — after round 64's
"non-van work nearly exhausted", round 70's "everything left needs a decision", and round
75's mislabelled config.

## The edge that makes it a subunit

```
determinant --part of [BFO:0000050]--> complex --participates in--> efflux_process
```

Writing `determinant --> efflux` directly would make **each subunit a pump**. A test
asserts the first edge is the partonomy and that no direct determinant→efflux edge exists.

The `complex` node is deliberately **ungrounded**: the complex records exist, but they are
themselves #229's open categorisation question, so pointing at one would smuggle in the
answer.

## A destructive edit, caught by tests

My first version assigned `FAMILY_SNIPPETS["ARO:3000748"] = [new_config]`, which **silently
dropped the family's four existing pump-class configs**. Two tests failed immediately and
the fix was to append rather than assign — but it is the second time this session a bare
assignment to an existing key destroyed prior work, after round 70's `--repromote`.

One of the two failures was **#287's config-count assertion, fifth instance**. Both tests
now select pump-class configs structurally, by the `export` node they all carry.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just test`: **666 passed** (+1) · `just validate` on both: **0 failures**
* corpus: **372,253 edges · 0 errors · 372,253/372,253 snippet-cited**
* drafts remaining: **327 → 325**

## Open questions

* **23 records remain under ARO:3000748** and are genuinely #229's: 7 Mex complexes,
  arlS, the ini operon set, and others.
* **#287** is now at five demonstrated breaks and six remaining assertions.
