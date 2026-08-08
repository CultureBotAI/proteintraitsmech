---
topic: causal-graphs
round: 111
date: 2026-08-08
target: aro/FUNC_RESISTANCE — gdpD, gshF, drmA (daptomycin), 3 records
prior_north: causal-graphs-round110.md
prior_round: causal-graphs-round110.md
---

# Causal graphs — Round 111: three records, one builder, because I have applied this shape inconsistently before

Three *Enterococcus faecalis* daptomycin records, each naming an enzyme and a resistance
claim with nothing between — round 66's EF-Tu shape.

**They share a builder rather than three hand-written configs**, and the reason is specific:
rounds 104 and 105 found **two cases where I had applied this exact shape inconsistently by
hand** — the fungal P450 family left for a reason that did not distinguish it from EF-Tu,
and pgsA left on grounds round 95 had already curated aftA on. A builder removes the
judgement that I got wrong twice.

## drmA keeps two words about the evidence

> *"drmA is an **uncharacterized** 6-pass membrane protein, with mutations to the protein
> causing **modest** resistance to daptomycin."*

*"Uncharacterized"* is a statement about **what is known**, not about the protein.
*"Modest"* is an **effect size**. Both are the kind of word that disappears when a snippet
is tidied, and both are kept — a test asserts they survive in the snippet and the note.

This is the fourth distinct thing this corpus's sources qualify: a **value** (round 63), a
**claim's attribution** (round 97), a **magnitude** (round 92), and now the **state of
knowledge**.

## gshF names two activities and links neither

> *"gshF is a **bifunctional** glutamate-cysteine ligase / glutathione synthetase…"*

Both are in the node label; neither is connected to daptomycin, because CARD connects
neither.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **710 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **239 → 236**

## Open questions

* **9 unconfigured drafts naming a function remain** — ampR, Rv0565c, BLMT, clpC1, Mas,
  nudC (second record), and **kasA** (#220).
