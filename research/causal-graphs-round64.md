---
topic: causal-graphs
round: 64
date: 2026-08-07
target: aro/FUNC_RESISTANCE — streptogramin inactivation (ARO:3000233), 13 records
prior_round: causal-graphs-round63.md
---

# Causal graphs — Round 64: two chemistries on two drug subtypes

**CARD's parent term says it outright**, which is the first time a family has announced its
own split rather than leaving me to measure it:

> *"There are two known mechanisms of streptogramin inactivation shown clinically to
> confer resistance: 1) vgB lyase enzymes linearize type B streptogramin antibiotics by
> breaking the ester linkage; 2) vat…"*

Different reaction **and** different substrate, so one config would have been wrong twice
over. Two configs: **vat acetyltransferases (9)**, **vgb lyases (4)**.

## The two graphs are deliberately not parallel

Rounds 62–63 could share a factory because all four rifampin chemistries were *transfer*
reactions — something is added to the drug. **vgb is not a transfer**: nothing is added,
a ring is opened.

| | vat | vgb |
|---|---|---|
| reaction | acetyl transfer | elimination / ring-opening |
| donor node | `acetyl_coa` (CHEBI:15351) | **none — nothing is donated** |
| drug edge | `has input` (the acceptor) | `lactone --part of--> drug0` |

That `part of` edge is the point: **the ring *is* the drug's structure**, which is why
breaking it destroys the antibiotic. A test pins that no donor node appears in the lyase
config, because copying the transfer shape across would have been the easy mistake.

## CARD is unusually precise here

Both definitions name more than the outcome — the **position** acylated ("the secondary
alcohol of streptogramin A compounds"), the **bond** broken ("at the ester linkage"), and
the **reaction type** ("through an elimination mechanism"). Contrast round 63, where the
phosphoryl donor had to be left out because CARD hedged it. Same source, very different
precision, family to family.

`CHEBI:15351` checked against OLS before use (#157): current, acetyl-CoA.

## Provenance

* records touched: **13** · SEEDED → REVIEWED · 1 left (the abstract family term)
* `just test`: **630 passed** (+2) · `just validate` on all 13: **0 failures**
* `--verify`: **0 problems, 0 near-misses** across both configs
* `just audit-fit`: **1 stranded** (tet(M), #270) — unchanged
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **542 → 529**

## Open questions

* **What remains is dominated by the van/operon families** — ARO:3002976 (19),
  ARO:0000010 (15), ARO:3000234 (13) — all of which touch the still-open modelling
  question of whether a gene cluster should carry a protein-trait causal graph.
* **#270 (tet(M))** remains the only stranded curated record.
