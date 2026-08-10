---
topic: causal-graphs
round: 115
date: 2026-08-10
target: aro/FUNC_RESISTANCE — ampR (2) + fungal SREBP (1), 3 records
prior_round: causal-graphs-round114.md
---

# Causal graphs — Round 115: "differential" is a source declining to say, not omitting to say

## Two records, one mechanism id, opposite treatment

Both **Upc2** (round 110) and the **fungal SREBPs** (this round) carry `ARO:3007609`,
target overexpression. Their configs differ on the one thing that matters:

| record | CARD says | predicate |
|---|---|---|
| Upc2 | *"**by upregulating** ERG11 expression"* | `RO:0002213` positive |
| SREBP | *"through **differential** gene regulation"* | `RO:0002211` neutral |

*"Differential"* is the only word in this corpus where a source **states that the direction
is unspecified** rather than merely leaving it out. Every other neutral predicate here
(rounds 78, 110, 114) was chosen because CARD said *"regulates"* and stopped; this one was
chosen because CARD said, in effect, *"it varies."*

A test pins both, so the pair cannot be harmonised.

## ampR ends where the beta-lactamases begin

> *"Mutations in ampR of **certain organisms** **have been shown to** confer resistance to
> antibiotics **due to beta-lactamase overexpression**."*

Three qualifiers in one sentence — a **scope** (*certain organisms*), an **attribution**
(*have been shown*), and a **causal link** (*due to*) — and the outcome is a mechanism
**already curated**: the beta-lactamases of rounds 12–16 and 59.

So round 22's rule applies and the graph stops at the overexpression. A test asserts the
config contains no *hydrol*, *acyl*, *serine* or *amide bond* — the vocabulary of the
records it points toward.

Its `bla_expression` node is deliberately **ungrounded**: CARD names no specific
beta-lactamase, and picking one would choose arbitrarily among hundreds of curated records.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **717 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **216 → 213**

## Open questions

* **~105 unconfigured drafts remain.** Reading is still the only method that has worked;
  nine regexes each missed a form.
* **ahpC** was read again and remains blocked on **#260** — CARD asserts activation-loss and
  overexpression for the same gene.
