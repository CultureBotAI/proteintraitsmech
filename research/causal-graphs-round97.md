---
topic: causal-graphs
round: 97
date: 2026-08-08
target: aro/FUNC_RESISTANCE — ArmR (1) + PDR1 (1), 2 records
prior_round: causal-graphs-round96.md
---

# Causal graphs — Round 97: ArmR, finally

`audit-drafts` (#316) surfaced 12 refused drafts under ARO:3000451 on its first run.
Reading them: ten are two-component **pair** records (baeSR, basRS, evgSA, kdpDE, liaFSR)
— #215's open question. **Two are not pairs, and both were curatable.**

## ArmR has been cited all session and never curated

It has been the standing example of why regulator lists cannot be built by keyword: it is
neither a repressor nor an activator but an **antirepressor**, and it defeated three
patterns in the efflux rounds. Its own definition turns out to state the complete chain
*including the structural basis*, which almost no other regulator record here does:

> *"ArmR, a 53-amino-acid **antirepressor**, **allosterically** inhibits MexR dimer-DNA
> binding by **occupying a hydrophobic binding cavity within the center of the MexR
> dimer**. ArmR up-regulation and MexR-ArmR complex formation **have previously been shown
> to** upregulate MexAB-OprM."*

**Both negatives are kept as separate edges** — ArmR ⊣ MexR-DNA binding, and ArmR ⊢
pump expression. Collapsing them into "activates the pump" would be true and would hide
that this is antirepression, which is the entire reason the record is interesting. A test
pins that both survive.

The second sentence's hedge is also kept: *"have PREVIOUSLY BEEN SHOWN to"* — CARD
attributes that claim rather than asserting it.

## PDR1 is not a pair

> *"PDR1 is a **transcription factor** that regulates the expression of several genes
> encoding ABC transporters, **contributing to** multidrug resistance."*

Round 78's shape. Neutral `RO:0002211` because CARD says *"regulates"* without a direction
— the same call as round 78 and the opposite of round 79, both of which were licensed by
what their sources said. A test asserts a two-component pair record is still refused.

## The audit earned its round

**#316 was built one round ago and immediately surfaced work I had walked past.** ArmR sat
as a draft through every efflux round while being quoted in their reports.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just test`: **688 passed** (+2) · `--verify-all`: **0 problems** · `audit-drafts`: 0 accepted
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **288 → 286**

## Open questions

* **10 two-component pair records remain** under ARO:3000451 — #215's question, now with a
  count.
