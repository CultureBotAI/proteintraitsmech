---
topic: causal-graphs
round: 112
date: 2026-08-08
target: aro/FUNC_RESISTANCE — Rv0565c, clpC1, Mas, nudC (isoniazid), 9 records
prior_round: causal-graphs-round111.md
---

# Causal graphs — Round 112: the end of the function-naming tail, and the one record left behind

Four families, one builder, nine records. All four name a protein and claim resistance with
nothing between — round 66's shape, applied through round 111's builder rather than by
hand.

## What each source qualified

* **Rv0565c** — *"**newly uncovered in recent literature**"*, and it names **no drug at
  all**, only *"antibiotic"*. CARD dating its own evidence.
* **clpC1** — a **subunit** with a stated role in a named complex. Unlike round 86's efflux
  subunits, no resistance mechanism is given, so there is no complex-to-process edge to
  write either.
* **Mas** — substrate, co-substrate and product all named. **More chemistry than most
  records here, and no drug.**
* **nudC (isoniazid)** — the twin of round 110's ethionamide record, and it says *"to
  **function**"* as well.

## Both nudC records refuse the same edge for the same word

Ethionamide and isoniazid are **both prodrugs**. Round 57 curated the activation story for
**ndh**, a neighbouring enzyme. Neither nudC definition says *"activate"* — they say
*"function"* — so neither gets the edge, and a test now covers both together rather than
each alone.

That word has now decided four graphs: mshA (**activate**, curated as prodrug loss), mshC
(**function**, left), and the two nudC records (**function**, curated for role only).

## kasA is the one left behind

It is the last function-naming draft, and it stays a draft. **It is #220's original
record** — asserting isoniazid resistance that PMID:12406221 specifically contradicts — and
round 102's eccC5 established that this corpus has **no structural way to carry a contested
claim**. A test asserts it has no config, so the omission is deliberate and visible rather
than an oversight.

## Provenance

* records touched: **9** · SEEDED → REVIEWED · kasA held for #220
* `just test`: **712 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **236 → 227**

## Open questions

* **The function-naming tail is exhausted** apart from kasA. What remains is the
  decision-bound sets (#309, #229, #215) and records whose definitions name neither a
  function nor a mechanism.
