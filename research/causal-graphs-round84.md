---
topic: causal-graphs
round: 84
date: 2026-08-07
target: aro/FUNC_RESISTANCE — murA transferase (ARO:3002811), 6 records
prior_round: causal-graphs-round83.md
---

# Causal graphs — Round 84: resistance by amount, not by affinity

Rounds 53, 61, 80 and 82 all curated the same underlying story: a mutation changes the
target so the drug binds it less. **murA is not that story**, and CARD says so plainly:

> *"murA … catalyses the initial step in peptidoglycan biosynthesis and **is inhibited by
> fosfomycin**. **Overexpression** of murA through mutations confers fosfomycin
> resistance."*

The enzyme is **unchanged**. There is simply more of it than the drug can inhibit. So there
is no affinity node, and a test enforces that — because four consecutive prior rounds
established a shape that would have been easy to import here without noticing it does not
fit.

That is the value of writing the tests as *"this config must NOT contain X"* rather than
only *"must contain Y"*: the failure mode after many similar rounds is not omission, it is
**pattern-matching the previous round**.

## One inference marked as mine

The final edge — *elevated murA levels → wall synthesis continues under drug* — carries a
note saying that "enough escapes inhibition" is **the reading CARD implies, not a sentence
it writes**. CARD gives overexpression and resistance; the mechanism connecting them is
obvious and still unstated, so the edge exists but says whose inference it is.

## The other five families measured this round

| family | drafts | state |
|---|--:|---|
| antifungal-resistant cytochrome P450 | 5 | *"mutations **or other modifications**"* — no mechanism, hedged twice; left |
| Rv1258c, mshC, Rv0678, aminoglycoside modifying enzyme | 4–5 each | not read this round |

## Provenance

* records touched: **6** · SEEDED → REVIEWED
* `just test`: **663 passed** (+1) · `just validate` on all 6: **0 failures**
* corpus: **372,225 edges · 0 errors · 372,225/372,225 snippet-cited**
* drafts remaining: **344 → 338**

## Open questions

* **Four small families remain unread**: Rv1258c (5), aminoglycoside modifying enzyme (5),
  mshC (4), Rv0678 (4).
* **The cytochrome P450 family is thinner than round 66's EF-Tu** — EF-Tu at least had a
  functional name and a causal "confer"; this has *"mutations or other modifications to
  confer resistance"* and nothing else.
