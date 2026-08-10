---
topic: causal-graphs
round: 118
date: 2026-08-10
target: aro/FUNC_RESISTANCE — ald (2) + BLMT (1), 3 records
prior_round: causal-graphs-round117.md
---

# Causal graphs — Round 118: two records one step from a mechanism the corpus already holds

## ald and ddlA sit either side of the same step

Round 116 curated **ddlA** with the corpus's only structural basis for competition:
*"Cycloserine has a **similar structure** to d-alanine."*

**ald** supplies L-alanine to the same wall, and says:

> *"Resistance due to mutations in ald can cause cycloserine **to not function**."*

*"Function"* again — the word that has now decided five graphs (mshA, mshC, both nudC
records, and this). The mimicry edge sits on a record **one step away in the same pathway**,
which makes borrowing it across especially tempting, and a test asserts ddlA has the
`RO:0002158` edge and ald does not.

## BLMT states its resistance three times and never explains it

> *"BLMT is a **bleomycin resistance protein**… This protein **confers a survival
> advantage**… BLMT **confers resistance to bleomycin**."*

Three sentences, three restatements, no mechanism. It carries the **inactivation** mechanism
id while describing no reaction — and **BLMT actually sequesters bleomycin**, which is round
72's shape and appears in no sentence here.

So the graph carries the one thing CARD adds beyond restating: *"encoded by the ble gene on
the transposon Tn5"*. A test bans *sequest*, *binds* and *complex* from the asserted text
**and requires the note to name the known-but-uncited mechanism** — the same both-halves
form as round 117's MSH2.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **723 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **206 → 203**

## Open questions

* **~95 unconfigured drafts remain.** Fgd1 (delamanid) was read again and left: its
  definition is a bare *"genetic variants … with mutations associated with resistance"*,
  with the F420 activation story — which the term's own name gestures at — unstated.
