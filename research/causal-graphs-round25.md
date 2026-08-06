---
topic: causal-graphs
round: 25
date: 2026-08-06
target: aro/FUNC_RESISTANCE — vanY (ARO:3000077), 6 records
prior_round: causal-graphs-round24.md
---

# Causal graphs — Round 25: vanY, and why two D,D-peptidases are not redundant

The last enzyme family of the van set. VanX (round 20) hydrolyses the free D-Ala-D-Ala
dipeptide; VanY strips the terminal D-Ala from the **assembled** precursor. The obvious
question — why does a cluster need both? — is one the source paper answers directly.

## One paper, and it is unusually quantitative

**Arthur, Depardieu, Cabanié, Reynolds & Courvalin, Mol Microbiol 1998 — PMID:10094630**

| claim | verbatim |
|---|---|
| what it is | *"The enzyme was a Zn2+-dependent D,D-carboxypeptidase that cleaved the C-terminal residue of peptidoglycan precursors ending in R-D-Ala-D-Ala or R-D-Ala-D-Lac but not the dipeptide D-Ala-D-Ala."* |
| **why it helps**, quantified | *"The specificity constants kcat/Km were 17- to 67-fold higher for substrates ending in the R-D-Ala-D-Ala target of glycopeptides."* |
| what it is required for | *"…was required for high-level glycopeptide resistance in a medium supplemented with D-Ala."* |
| **why both enzymes exist** | *"Thus, VanX and VanY had non-overlapping functions involving the hydrolysis of D-Ala-D-Ala and the removal of D-Ala from membrane-bound lipid intermediates respectively."* |

The `not the dipeptide D-Ala-D-Ala` clause in the first quote is the same shape as vanX's
and vanXY's negative results, and it is what makes the non-redundancy claim mechanical
rather than rhetorical: the two enzymes cannot substitute because their substrates differ.

## The requirement is conditional, and the record says so

VanY is required for **high-level** resistance **in D-Ala-supplemented medium** — not
simply "confers resistance". The `det_res` note states both qualifiers rather than
flattening them, because a reader of `evidence[]` would otherwise take a conditional
result for an unconditional one.

## The guard refused a record before anything was written

`_requires_lac_cluster` — the mirror of round 23's — held back
`ARO:3002959` (*vanY gene in vanG cluster*):

```
would skip  ARO:3002959: cluster vanG has no vanH, so it is the D-Ala-D-Ser route;
            this config's evidence measured R-D-Ala-D-Ala and R-D-Ala-D-Lac substrates only
```

The paper measured R-D-Ala-D-Ala and R-D-Ala-D-Lac. It says nothing about R-D-Ala-D-Ser,
so a vanG-cluster record would have been given a graph whose evidence does not cover its
substrate. Round 22 learned this by shipping 12 such records; rounds 23–25 caught it before
the first `--apply`.

## Provenance

* records touched: **6** · SEEDED → REVIEWED · 1 held back by precondition
* corpus after: **39,647 records · 40,115 graphs · 348,088 nodes · 369,738 edges ·
  0 errors · 369,738/369,738 edges snippet-cited**
* warnings 6,020 → **6,032**: +12, the two ungrounded precursor nodes per record
* `just validate` on all 6 individually: **0 failures**
* drafts remaining: **1,102 → 1,096**

## Open questions

* **`ARO:3002959` (vanY in vanG) needs its own evidence**, not this config's. If VanY-type
  carboxypeptidase activity on an R-D-Ala-D-Ser precursor has been measured, that is a
  one-paper round; if it has not, the honest outcome is that the record stays a draft.
* **The van set's remaining ~30 records are accessory or cluster-level** — vanW, vanZ,
  vanU/V/J/K, and 13 operon-level terms. The latter raise a modelling question that should
  be settled before curating them: a gene *cluster* is not a protein, and a
  `ProteinTraitRecord` causal graph asserting a protein trait about an operon may be the
  wrong shape entirely.
