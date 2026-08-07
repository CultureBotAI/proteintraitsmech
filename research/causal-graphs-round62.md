---
topic: causal-graphs
round: 62
date: 2026-08-07
target: aro/FUNC_RESISTANCE — rifampin ADP-ribosyltransferases (arr, under ARO:3000576), 8 records
prior_round: causal-graphs-round61.md
---

# Causal graphs — Round 62: one drug, four chemistries, one config

ARO:3000576 ("rifampin inactivation enzyme") has 18 drafts and reads like a single family.
Measuring its members' mechanism ids first — the habit from rounds 51 and 58 — shows
**four different reactions**:

| chemistry | ARO | drafts |
|---|---|--:|
| **ADP-ribosylation** (arr) | ARO:3000266 | **8 — this round** |
| hydroxylation | ARO:3000450 | 4 |
| phosphorylation | ARO:3000105 | 3 |
| glycosylation | ARO:3000208 | 2 |

They inactivate the *same drug* by *different reactions*. One config across the family
would assert the wrong chemistry for ten of eighteen records — rounds 22 and 58's error.
So this round is **8 records**, and the other three subsets need their own snippets.

## The graph, from two CARD sentences

> *"The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+."*
> — ARO:3000266
>
> *"Enzymes that inactivate rifampin antibiotics by chemical modification."* — ARO:3000576

```
determinant --enables-->            adp_ribosylation
adp_ribosylation --has input-->     nad (CHEBI:15846)   ← the cosubstrate
adp_ribosylation --has input-->     drug0              ← the acceptor
adp_ribosylation --causally upstream of--> modified
```

**Both inputs are stated on purpose.** NAD+ is what makes this a *transferase* rather than
a hydrolase, and the drug being the acceptor is what makes it *inactivation* rather than
target alteration — the distinction rounds 18–19 and 51–61 kept having to restate.

`CHEBI:15846` was checked against OLS before use (#157): current, labelled NAD(+). It is
the round's only grounding, and the two ungrounded nodes say why they are ungrounded.

## Scope stated, as in rounds 54–55, 59–61

The family sentence covers hydroxylation, glycosylation and phosphorylation too. Its
`notes` say only the ADP-ribosylating members are curated by this config, and a test pins
that the other three mechanism ids are absent from `mech`.

## Provenance

* records touched: **8** · SEEDED → REVIEWED · 10 left as drafts, by chemistry
* `just test`: **626 passed** (+1) · `just validate` on all 8: **0 failures**
* `--verify`: 10 precondition skips, **0 problems, 0 near-misses**
* `just audit-fit`: **1 stranded** (tet(M), #270) — unchanged
* corpus: **371,552 edges · 0 errors · 371,552/371,552 snippet-cited**
* drafts remaining: **559 → 551**

## Open questions

* **Three subsets of ARO:3000576 remain** (hydroxylation 4, phosphorylation 3,
  glycosylation 2). Each is small, each has its own mechanism-term definition already, and
  they are the cheapest remaining work in the corpus.
* **#270 (tet(M))** is still the only stranded curated record, and still the fourth
  distinct precondition-defect shape.
