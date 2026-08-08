---
topic: causal-graphs
round: 81
date: 2026-08-07
target: aro/FUNC_RESISTANCE — ppsA-E polyketide synthases (ARO:3005002), 9 records
prior_round: causal-graphs-round80.md
---

# Causal graphs — Round 81: a resistance claim with a gap in the middle

Round 80's embB gave enzyme, pathway, drug action and mutation in three sentences. This
family, one round later and in the same organism, gives **two claims and nothing between
them**:

> *"Genes ppsA-E constitute an operon encoding enzymes involved in the biosynthesis of
> **phthiocerol dimycocerosate** and other lipids in Mycobacterium tuberculosis. Mutations
> within this region **can result in** resistance to **pyrazinamide**."*

A lipid-biosynthesis role, and a hedged resistance claim about a completely different
drug — one that round 56 established is a **prodrug activated by pncA**. How a PDIM defect
confers pyrazinamide resistance is real in the literature and **absent from every source
read here**.

So the graph has **one edge**: the biosynthetic role. A test asserts there is exactly one,
that its notes record the omission, and that CARD's *"can result in"* hedge survives into
the snippet.

This is round 66's EF-Tu position and #219's lesson in the same record set: **the mechanism
I know is the one most likely to arrive uncited.** Two rounds in a row have now produced
opposite outcomes from the same source — embB fully mechanised, ppsA-E deliberately
sparse — which is the strongest argument yet against a house style.

## The operon appears again, and is again not modelled

The family term describes an **operon** (*"Genes ppsA-E constitute an operon"*) while the
records are individual proteins. It is cited as the source of the biosynthetic claim and
not modelled — the same position round 74 took with almEFG, and the same open question
behind the van set.

## Provenance

* records touched: **9** · SEEDED → REVIEWED
* `just test`: **659 passed** (+1) · `just validate` on all 9: **0 failures**
* corpus: **372,122 edges · 0 errors · 372,122/372,122 snippet-cited**
* drafts remaining: **375 → 366**

## Open questions

* **The PDIM→pyrazinamide link is a well-posed literature task** — unlike #219's, the
  claim is specific and the search shape is obvious. It would turn a one-edge graph into a
  real mechanism.
* **Three curatable families remain in this block**: folP (7), rpoC (6), liaFSR (6).
