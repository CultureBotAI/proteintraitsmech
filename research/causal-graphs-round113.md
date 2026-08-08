---
topic: causal-graphs
round: 113
date: 2026-08-08
target: aro/FUNC_RESISTANCE — folC, alaS, cysB, 4 records
prior_round: causal-graphs-round112.md
---

# Causal graphs — Round 113: my "names a function" filter was the ninth too-narrow pattern

Round 112 closed saying the function-naming tail was exhausted. **It was not.** The filter
I used required an *"is a &lt;X&gt;ase"* form, and the remaining 127 drafts include:

* *"**An alanyl-tRNA synthetase** conferring resistance to novobiocin…"*
* *"**Positive regulator** of gene expression in the cysteine regulon…"*
* *"**Dihydrofolate synthase** (synthetase) enzymes resistant to aminosalicylates…"*

All three name a function; none matches the pattern. **Ninth too-narrow pattern of the
session**, and the first that under-reported *work* rather than mis-classifying a record.

## folC is the fullest prodrug-activation-loss statement in the corpus

> *"Dihydrofolate synthase is **required for bioactivation** of p-aminosalicylic acid, and
> mutation … **inhibits production of the dihydrofolate analog hydroxyl-dihydrofolate**,
> **thus preventing activation** and conferring resistance."*

Rounds 56 (pncA), 57 (ndh), 95 (mshA) and 108 (FUR1) all curated this mechanism from
sentences that stopped earlier. **This one runs end to end and names the intermediate** —
the only prodrug config in the corpus that does. A test asserts the `analog` node exists
here and does not in pncA's, so the distinction cannot be smoothed away.

## Two records where CARD states its own gap

Both alaS and cysB end *"Sequence data unavailable."* — CARD recording what it does not
have, alongside what it does. Kept in the snippets.

cysB is also a **regulator of a regulon unrelated to the drug**: *"Positive regulator of
gene expression in the cysteine regulon. cysB mutants confer resistance to novobiocin."*
CARD joins the two by juxtaposition only, so the graph does not join them at all.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **713 passed** (+1), **run before the push** · corpus: **0 errors**
* drafts remaining: **227 → 223**

## Open questions

* **The tail is larger than round 112 said.** Of ~125 remaining unconfigured drafts, an
  unknown number name a function in a form no pattern of mine has matched yet. Counting
  them needs a better filter than a regex — or reading them.
