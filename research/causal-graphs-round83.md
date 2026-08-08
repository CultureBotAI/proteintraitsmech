---
topic: causal-graphs
round: 83
date: 2026-08-07
target: aro/FUNC_RESISTANCE — rpoC (7) and liaFSR (7), 14 records
prior_round: causal-graphs-round82.md
---

# Causal graphs — Round 83: the last two families of the ARO:3000212 block

Two families, two shapes already established, and one trap avoided.

## rpoC — role and resistance, nothing between

> *"RNA polymerase is a multisubunit enzyme … The **beta prime subunit** forms the active
> center of the enzyme and template/transcript binding sites. **Mutations in rpoC gene
> confers antibiotic resistance.**"*

Round 81's ppsA-E shape: a structural role, a bare resistance claim, and no link. CARD never
says a drug binds there or what the mutations change.

**And the obvious guess would have been wrong.** Rifampicin binds **rpoB**, not rpoC — so
reaching for the familiar RNA-polymerase mechanism would have produced a confidently
incorrect graph, not merely an uncited one. A test bans *rifampicin*, *rifamycin*, *rpoB*,
*binds the drug* and *inhibit* from the config's asserted text.

That is the first time this session where the mechanism I would have reached for was not
just unsupported but **attached to a different subunit**.

## liaFSR — the drug is the inducer

> *"The liaFSR system regulates the cell envelope stress response. It is **transcriptionally
> activated by exposure to** … **antibiotics with lipid II inhibition properties**."*

Round 76's cprRS inversion: the antibiotic *activates* the system rather than being the
thing resisted at that step. So the graph runs `drug0 → stress → determinant → response`,
and stops — CARD never says how the response then confers resistance.

The final edge uses the neutral `RO:0002211`, as round 78's did and round 79's did not,
because CARD gives no direction here.

## Provenance

* records touched: **14** (7 + 7) · SEEDED → REVIEWED
* `just test`: **662 passed** (+2) · `just validate` on all 14: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **358 → 344**

## Open questions

* **The ARO:3000212 block's curatable families are now done.** What remains under that
  mechanism id is spread thinly — round 18's per-record assessment, arriving in full.
* **rpoC's real mechanism is a well-posed literature task**, like round 81's
  PDIM→pyrazinamide link: a specific claim with an obvious search shape.
