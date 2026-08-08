---
topic: causal-graphs
round: 92
date: 2026-08-07
target: aro/FUNC_RESISTANCE — ileS (ARO:3000446), 5 records
prior_round: causal-graphs-round91.md
---

# Causal graphs — Round 92: the first round of the 263

Round 91's full count of the 317 remaining drafts corrected a claim I had been repeating:
**263 of them have no config yet.** That is uncounted work, not blocked work — I had been
folding it into "the per-record remainder" and treating the whole balance as decision-bound.

This is the first round drawn from it. The largest un-configured families in that set are
**4–5 records each**, which is round 18's per-record assessment arriving in full: there is
no big family left, only many small ones.

## ileS, and two hedges in one sentence

> *"Mupirocin inhibits protein synthesis **by interfering with** isoleucyl-tRNA synthetase
> (ileS). Mutations in ileS **can** confer **low-level** mupirocin resistance."*

The first sentence gives the drug's action *and* its route — CARD makes the synthetase the
path to the process, which is why the graph runs
`drug0 → aminoacylation → protein_synthesis` rather than drug straight to translation.

The second hedges **twice**: *"can"* (conditional) and *"low-level"* (magnitude). Both are
kept in the snippet and named in the note. **NOT asserted**: how the mutations reduce the
drug's effect, which CARD does not say.

That is now the standing pattern across ~40 configs — the source's certainty and magnitude
are part of the claim, not decoration to be trimmed on the way into a graph.

## Provenance

* records touched: **5** · SEEDED → REVIEWED
* `just test`: **678 passed** (+1) · `just validate` on all 5: **0 failures**
* corpus: **372,283 edges · 0 errors · 372,283/372,283 snippet-cited**
* drafts remaining: **317 → 312**

## Open questions

* **258 drafts still have no config.** The families are 4–5 records each: cytochrome P450
  (5), Rv1258c (5), mshC (4), secretion-system subunits (4), nudC (4), target-replacement
  proteins (4), whiB7 (4), and a long tail below that.
* **53 are genuinely decision-bound** — #309 (28) and #229 (25).
