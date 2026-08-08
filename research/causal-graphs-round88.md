---
topic: causal-graphs
round: 88
date: 2026-08-07
target: aro/FUNC_RESISTANCE — vanU, vanJ, vanK, 3 records
prior_round: causal-graphs-round87.md
---

# Causal graphs — Round 88: three van proteins, three different mechanisms

Round 87 found that 8 of 35 van records describe proteins rather than clusters. These are
three of them, and **no two share a mechanism**:

| record | CARD's mechanism |
|---|---|
| **vanU** | *"a transcriptional **activator** of vancomycin resistance genes"* |
| **vanJ** | *"…by **recycling undecaprenol pyrophosphate** during cell wall biosynthesis"* |
| **vanK** | *"Fem family … **add the cross-bridge amino acids** to the stem pentapeptide"* |

Regulation, lipid-carrier recycling, and peptidoglycan cross-bridging — inside one gene
set, under one mechanism id (`ARO:3000213`), which I verified **before** writing this time
rather than guessing as in round 87.

## vanJ is round 58's mechanism in an unrelated family

*"Recycling undecaprenol pyrophosphate"* is exactly what **bacA and bcrC** do (round 58,
bacitracin). The two families share no ancestor and different drugs, and CARD describes the
same step for both.

**Both configs also omit the same edge**, for the same reason: neither CARD definition says
the drug *binds* the carrier — however standard that is in the textbooks. A test asserts
neither config has a `drug0` edge, tying the two omissions together so a later reader sees
they are one decision rather than two oversights.

## Three direction judgements, three different answers, all from the source

| round | CARD's wording | predicate |
|---|---|---|
| 78 | *"directly or indirectly change rates"* | `RO:0002211` neutral |
| 79 | *"result in increased expression"* | `RO:0002213` positive |
| 85 | *"negatively regulates"* | `RO:0002212` negative |
| **88** | *"a transcriptional **activator**"* | `RO:0002213` positive |

Four regulator configs, four predicates chosen by what the sentence says. Any pass that
"harmonised" them would be discarding evidence, not removing inconsistency.

## What vanK does not say

CARD gives the reaction (cross-bridge addition) and the phenotype (*"inducible, high-level
vancomycin resistance"*) and **nothing between them**. Round 81's ppsA-E position: the
graph carries the reaction and stops.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **670 passed** (+2) · `--verify-all`: 88 families, **0 problems**
* corpus: **372,261 edges · 0 errors · 372,261/372,261 snippet-cited**
* drafts remaining: **323 → 320**

## Open questions

* **3 van protein records remain**: the vanJ homologue (*"confer resistance to
  teicoplanin"*, no mechanism) and two family terms.
* **27 van records are cluster-level** and stay behind the modelling question.
