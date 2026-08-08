---
topic: causal-graphs
round: 110
date: 2026-08-08
target: aro/FUNC_RESISTANCE — Upc2, FUR1 (Saccharomyces), nudC, 4 records
prior_round: causal-graphs-round109.md
---

# Causal graphs — Round 110: a label that misled me, and a word that decided a graph

## Upc2 — the label said "mutations", the record carries overexpression

Its ARO term name is *"Candida spp. Upc2 **with mutations** conferring resistance to azole
antibiotics"*, so I keyed the config on `ARO:3000212`. **The record carries `ARO:3007609`
— target overexpression** — the mechanism id for what the mutations *do*, not for the fact
that they are mutations.

The promoter wrote **zero records** until I looked. **Second time this session I guessed a
mechanism id rather than reading it** (round 87 was the first), and both times the symptom
was identical: a silent zero. A test now pins the id.

The definition itself is complete, with CARD's own *"by"*:

> *"Mutations in Upc2 have been shown to confer resistance to azole antibiotics including
> fluconazole **by upregulating ERG11 expression**."*

Round 84's murA overexpressed the target itself; **this is a regulator whose mutation
raises the target's expression**. NOT asserted: that ERG11 encodes the azole target — CARD
names the gene and not its role.

## nudC — one word decided the graph

> *"…resulting in the inability for ethionamide **to function**."*

Round 95 drew a line between **mshA** (*"to **activate**"*, curated as prodrug-activation
loss) and **mshC** (*"to **function**"*, left). nudC says *"function"*.

**Ethionamide is a prodrug**, and round 57 curated exactly that story for **ndh**, a
neighbouring enzyme. The pull to write the activation edge here is strong and the word does
not license it — so a test enforces the line rather than leaving it to judgement each time.

## FUR1 in Saccharomyces — word for word the Candida record

Round 108's sentence with the genus changed. Curated identically, including the same
omission: 5-FC's activation by pyrimidine salvage is standard and CARD tells it for neither
species.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **708 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **243 → 239**

## Open questions

* **12 unconfigured drafts naming a function remain** — ampR, Rv0565c, BLMT, drmA, gdpD,
  gshF, clpC1, Mas, nudC (second record), and **kasA** (#220).
