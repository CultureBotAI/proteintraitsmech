---
topic: causal-graphs
round: 30
date: 2026-08-06
target: aro/FUNC_RESISTANCE — ethA (ARO:3003456), 9 records
prior_round: causal-graphs-round29.md
---

# Causal graphs — Round 30: ethA, and finding the paper that round 27 could not

Round 27 curated katG and **deliberately left ethA out**, because its characterisation was
not found: the searches that round ran surfaced recent *booster* work (MymA, VirS,
alpibectir) rather than EthA's own. Fetching **PMID:10944230** directly by identifier
rather than by title is what found it. The lesson is small and reusable — a title search
for a 25-year-old mechanism paper competes with everything published since, and an
identifier does not.

## DeBarber et al., PNAS 2000 — and the mechanism is shown by its converse

> *"Synthesis of radiolabeled ETA and an examination of drug metabolites formed by whole
> cells of Mycobacterium tuberculosis (MTb) have allowed us to demonstrate that ETA is
> activated by S-oxidation before interacting with its cellular target."*

> *"We have demonstrated that overproduction of Rv3855 (EtaR), a putative regulatory protein
> from MTb, confers ETA resistance whereas overproduction of an adjacent, clustered
> monooxygenase (Rv3854c, EtaA) confers **ETA hypersensitivity**."*

No knockout is needed: **more EtaA makes cells more sensitive**, so less of it makes them
more resistant. The same paper shows overproducing the *regulator* confers resistance,
which is the identical fact from the other side. The `notes` say the direction the evidence
runs, because "overproduction confers hypersensitivity" is not the same sentence as "loss
confers resistance" and a reader should see which was measured.

## It closes a triangle with rounds 27 and 28

> *"ETA is metabolized by MTb to a 4-pyridylmethanol product remarkably similar in structure
> to that formed by the activation of isoniazid by the catalase-peroxidase KatG."*

The paper draws the katG parallel itself. So the corpus now holds all three corners of the
isoniazid/ethionamide story, each pointing at the others' records rather than restating
them:

| record | round | role |
|---|--:|---|
| `ARO:3004266` katG | 27 | activates isoniazid |
| `ARO:3003456` ethA | **30** | activates ethionamide |
| `ARO:3003417` inhA | 28 | the target both converge on — and its own record carries both resistance routes |

ethA's `activated_eta → inha_gene` edge points at the round-28 record, with a note that the
target identification comes from PMID:8284673 (which showed *inhA* mutations confer
resistance to **both** drugs) rather than from this round's paper.

## Provenance

* records touched: **9** · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,314 nodes · 370,134 edges ·
  0 errors · 370,134/370,134 edges snippet-cited**
* warnings 6,114 → **6,123**: +9, one ungrounded activated-drug node per record
* `just validate` on all 9 individually: **0 failures**
* drafts remaining: **1,030 → 1,021**

## Open questions

* **fabG1 (7) is still blocked**, and the same identifier-not-title trick did not rescue it:
  PMID:12406222 returns a *Lactococcus* nisA promoter paper, so the citation I had for
  "overexpression of inhA confers resistance" is wrong. The claim is real and is what round
  28's overexpression edge predicts; the paper needs finding by another route.
* **23S rRNA (26) is filed as #217** — the drug-action arm is quotable from Schlünzen 2001,
  but no source was found that *constructs* a 23S substitution and measures the affinity
  loss, which is the tier round 29's 16S family had.
* **The remaining isoniazid genes** (ndh, nudC, mshA/B/C, nat, furA, sigI, iniA, mymA,
  Rv0565c, inbR, kasA, mmaA3) are 1–2 record chains with thin or contested evidence. For
  several, the honest outcome is that they stay drafts.
