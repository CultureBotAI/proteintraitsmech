---
topic: causal-graphs
round: 76
date: 2026-08-07
target: aro/FUNC_RESISTANCE — LPS aminoacylation + cprRS regulation (ARO:3003580), 2 records
prior_round: causal-graphs-round75.md
---

# Causal graphs — Round 76: a fifth route, and a regulator that points at round 75

Four charge-alteration drafts remained after round 75, and they turned out to be **four
different situations** — worth recording, because "4 records left in a family" reads as one
task and was not:

| record | CARD says | outcome |
|---|---|---|
| ARO:3004363 lipid A acyltransferase | *"confer resistance … through the **aminoacylation** of lipopolysaccharide, thereby decreasing the negative charge"* | **curated** — causal, complete |
| ARO:3005065 cprRS | *"it **induces the Arn operon** to confer resistance"* | **curated as regulation** |
| ARO:3004287 lipid A phosphatase | *"is **proposed to be** initiated through binding…"* | left — the mechanism is offered as a proposal |
| ARO:3003920 pgpB | *"A gene that produces the protein lipid A 4'-phosphatase."* | left — no mechanism at all |

## cprRS ends where round 75 begins

cprRS does not alter charge. It **induces the Arn operon**, whose Ara4N chemistry was
curated one round earlier. So its graph stops there:

```
sensing --causally upstream of--> determinant
determinant --positively regulates--> arn_operon  (grounded to ARO:3003578, PmrF)
```

That is **round 22's rule** — a regulator's graph should end at the records that do the
work — and the first time this session it has applied to a record whose downstream I had
curated in the immediately preceding round. Restating the Ara4N chemistry here would
duplicate it and then drift from it; pointing at `ARO:3003578` inherits whatever that
record says today.

A test pins both halves: the grounding is a **real KB record** (verified), and the
regulator's node labels contain neither "lipid A" nor "charge".

**The drug is also the signal.** *"In the presence of cationic peptides, it induces…"* — the
antibiotic induces the system that resists it, which is why the `sensing → determinant`
edge exists rather than starting the graph at the determinant.

## Provenance

* records touched: **2** · SEEDED → REVIEWED · 2 left with stated reasons
* `just test`: **650 passed** (+1) · `just validate` on both: **0 failures**
* corpus: **372,002 edges · 0 errors · 372,002/372,002 snippet-cited**
* drafts remaining: **411 → 409**

## Open questions

* **ARO:3004287's mechanism is "proposed"** — curatable if the proposal is recorded *as* a
  proposal, which is #220's question in miniature.
* **pgpB has no mechanism**, like round 66's EF-Tu. That round curated anyway because a
  resistance claim existed; here there is not even that.
* ARO:3003580 now carries **five** routes plus a regulator. Worth checking, when the six
  #287 assertions are swept, that none of its tests count configs.
