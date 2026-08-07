---
topic: causal-graphs
round: 31
date: 2026-08-06
target: aro/FUNC_RESISTANCE — ribosomal protection of tetracycline (ARO:3000185, tetracycline records), 21 records
prior_round: causal-graphs-round30.md
---

# Causal graphs — Round 31: target protection, and the drafts drop below 1,000

A **seventh** kind of mechanism, and the first where the determinant touches neither the
drug nor the target's structure: it **removes the drug from the target**.

| kind | rounds |
|---|---|
| inactivation · target alteration · precursor depletion · precursor substitution | 12–16, 18–21, 23, 26 |
| regulation · prodrug-activation loss · target overexpression | 22, 24, 27, 28, 30 |
| **target protection** | **31** |

## One family term, three mechanisms — so a precondition

`ARO:3000185` (*antibiotic target protection protein*) covers three unrelated stories:

| drug | protector | partner it binds |
|---|---|---|
| **tetracycline (21)** | TetM / TetO / OtrA | the ribosome |
| rifamycin (6) | RbpA, HelR | RNA polymerase |
| fusidane (5) | FusB / FusC / FusD | EF-G |

One config cannot describe all three — the round-19 and round-22 lesson — so
`_requires_tetracycline` takes the records whose drug is `ARO:3000050` and the other two
wait for their own evidence. It refused **172** candidates, most of them already-curated
qnr records from round 14, which share the `ARO:0001003` mechanism id but not this
mechanism.

## Dönhöfer et al., PNAS 2012 — PMID:23027944

> *"Ribosome protection proteins (RPPs) confer tetracycline resistance by binding to the
> ribosome and chasing the drug from its binding site."*

> *"Moreover, we observe direct interaction between domain IV of TetM and the tetracycline
> binding site and identify residues critical for conferring tetracycline resistance."*

**The superseded model is recorded alongside the new one**, because the paper's own framing
is a correction:

> *"The current model for the mechanism of action of RPPs proposes that drug release is
> **indirect** and achieved via conformational changes within the drug-binding site induced
> upon binding of the RPP to the ribosome."*

The cryo-EM structure supports **direct** dislodgement instead. A graph that cited only the
newer reading would hide that this was a live question and that the evidence is a 7.2 Å
structure rather than a settled fact.

## The guard caught my own mechanism id

The first draft of this config guessed `ARO:0000002` for the mechanism. `--verify` reported
**193 uncovered-mechanism records** — every candidate — because the real id is
`ARO:0001003`. That is the check from #203 doing exactly its job on new work, before a
single record was written.

## Provenance

* records touched: **21** · SEEDED → REVIEWED · 172 refused by precondition
* corpus after: **39,647 records · 40,115 graphs · 348,356 nodes · 370,197 edges ·
  0 errors · 370,197/370,197 edges snippet-cited**
* warnings 6,123 → **6,144**: +21, one ungrounded binding-site node per record
* `just validate` on all 21 individually: **0 failures**
* drafts remaining: **1,021 → 1,000**

## Open questions

* **The other two protection mechanisms** — rifamycin (RbpA, HelR) and fusidane (FusB/C/D)
  — are each a small round with their own paper. The precondition already keeps them out.
* **`rpsJ` is in this set and may not belong.** It is a ribosomal protein S10 whose
  substitutions confer tigecycline resistance, which is arguably target *alteration* rather
  than protection. It took this config because CARD places it under target protection; worth
  a `review-source-categories` look rather than assuming CARD's placement is right.
