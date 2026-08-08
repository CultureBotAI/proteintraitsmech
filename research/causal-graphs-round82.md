---
topic: causal-graphs
round: 82
date: 2026-08-07
target: aro/FUNC_RESISTANCE — folP dihydropteroate synthase (ARO:3000226), 8 records
prior_round: causal-graphs-round81.md
---

# Causal graphs — Round 82: the most completely stated mechanism in the corpus

Round 81's ppsA-E gave two claims and a gap. This family gives the **entire chain in one
sentence**:

> *"Point mutations in dihydropteroate synthase folP **prevent sulfonamide antibiotics from
> inhibiting its role in folate synthesis**, thus conferring sulfonamide resistance."*

Enzyme, pathway, drug action, mutation effect and resistance. A second record adds what no
other family in this corpus has supplied — **the kind of inhibition**:

> *"Dapsone inhibits bacterial synthesis of dihydrofolic acid by **competing with
> para-aminobenzoate for the active site** … Thus acts as a **competitive inhibitor** of
> folP. Point mutation within the folP gene results in **lowered affinity** of dapsone for
> folP."*

## Why competitive inhibition earns its own edge

Rounds 53, 61 and 80 all wrote "the mutation lowers the drug's affinity" without being able
to say why that does not also break the enzyme. Here CARD answers it: the drug is a
**substrate analogue** occupying para-aminobenzoate's own site. So *"lowered affinity for
the drug"* and *"still binds its real substrate"* are the same claim seen from two sides,
and the graph says so on the edge rather than leaving it implied.

A test asserts the predicate contains "competitive", that the snippet contains "competitive
inhibitor", and that the description distinguishes it from allosteric — because a generic
`inhibits` edge would lose exactly the distinction that makes the mechanism coherent.

## Provenance

* records touched: **8** · SEEDED → REVIEWED
* `just test`: **660 passed** (+1) · `just validate` on all 8: **0 failures**
* corpus: **372,161 edges · 0 errors · 372,161/372,161 snippet-cited**
* drafts remaining: **366 → 358**

## Open questions

* **Two curatable families remain in this block**: rpoC (6) and liaFSR (6).
* **Rounds 80–82 span the full quality range** of CARD definitions — embB complete,
  ppsA-E a gap, folP complete *with* inhibition kinetics — in three consecutive rounds and
  two organisms. Any future config-writing helper should assume nothing about a family's
  definition quality before reading it.
