---
topic: causal-graphs
round: 79
date: 2026-08-07
target: aro/FUNC_RESISTANCE — mutant efflux regulatory proteins (ARO:3000219), 11 records
prior_round: causal-graphs-round78.md
---

# Causal graphs — Round 79: the direction one family states and its neighbour does not

## The block from the previous round dissolved

Round 79's first attempt curated **AxyZ** alone and hit `UncoveredMechanism`: AxyZ carries
`ARO:3000212` (mutation) while its own definition describes only regulation. I refused to
cover the mutation id with the regulation snippet, because *"is a transcriptional
regulator"* is not evidence for *"mutations confer resistance"* — unlike rounds 72 and 77,
where one sentence genuinely supported both ids.

**Measuring the family it belongs to resolved it.** AxyZ sits under **ARO:3000219**, whose
term reads:

> *"Efflux regulatory proteins **with mutations that result in increased expression** of
> efflux proteins."*

That *is* the mutation evidence. The refusal was right and the fix was to find the sentence
rather than reuse a wrong one — 11 records instead of 1.

## Two neighbouring families, two different predicates

| family | CARD says | predicate |
|---|---|---|
| ARO:3000750 (round 78) | *"directly or indirectly **change rates** of antibiotic efflux"* | `RO:0002211` **regulates** |
| ARO:3000219 (this round) | *"mutations that result in **increased expression**"* | `RO:0002213` **positively regulates** |

Both are efflux regulators; only one states a direction. **A test pins both**, because the
tempting cleanup — making two similar configs agree — would either invent a direction for
round 78's or discard the one CARD gives here.

That is the fourth pair this session held apart deliberately: SMR/MATE coupling ions
(rounds 67, 69), vat/rifampin donors (rounds 63–64, 68), fluoroquinolone/aminocoumarin
topoisomerase mechanisms (rounds 18–19, 61), and now these.

## Provenance

* records touched: **11** · SEEDED → REVIEWED
* `just test`: **657 passed** (+2) · `just validate` on all 11: **0 failures**
* `just audit-roles`: **1** (vanS, known benign) · `audit-graphs`: **0 errors**
* corpus: **372,074 edges · 372,074/372,074 snippet-cited**
* drafts remaining: **396 → 385**

## Open questions

* **Five curatable families remain in the ARO:3000212 block**: emb arabinosyltransferase
  (9), polyketide synthase (8), folP (7), rpoC (6), liaFSR (6). Each is a distinct target
  and needs its own reading.
* **#229** now has seven measured instances and should probably be rescoped to the general
  shape rather than the original eight Mex pairs.
