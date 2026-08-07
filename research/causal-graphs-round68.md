---
topic: causal-graphs
round: 68
date: 2026-08-07
target: aro/FUNC_RESISTANCE — antibiotic inactivation enzymes (ARO:3000557), 34 records
prior_round: causal-graphs-round67.md
---

# Causal graphs — Round 68: three chemistries, and a hedge that turned out to be a house style

ARO:3000557 has **56 drafts** across several chemistries. Its three largest are group
transfers onto the drug: **nucleotidylation (12)**, **phosphorylation (14)**,
**acylation (8)** — 34 records, one factory.

## The finding: the hedge is systematic

Round 63 left the rifampin phosphotransferase donor out because CARD said *"usually by
ATP, sometimes GTP"*. I treated that as one term's quirk. It is not:

| chemistry | CARD's donor phrasing |
|---|---|
| nucleotidylation | *"Modification by NMP, **usually** AMP."* |
| phosphorylation | *"…**usually** by ATP, **sometimes** GTP."* |
| acylation | *"…**often** via acetylation by acetylCoA."* |

**All three hedge.** So none gets a donor node, and the factory encodes that as a property
of the family's text rather than three separate judgement calls.

**The contrast is what makes it a rule rather than a habit.** Round 64's vat
acetyltransferases *do* carry an `acetyl_coa` node — because ARO:3000453 names it outright,
with no hedge, and even gives the position acylated. Two acylation configs in this corpus
now differ on exactly this point, for a stated reason. A test pins both sides.

## Scope

ARO:3000557 covers more than these three (hydrolysis, hydroxylation, amidohydrolysis,
cell-wall restructuring). Each config's `notes` say only its own chemistry's members are
curated, and its precondition selects structurally on the mechanism id. The remaining
**22 drafts** in this family are the smaller chemistries.

## Provenance

* records touched: **34** · SEEDED → REVIEWED
* `just test`: **637 passed** (+2) · `just validate` on all 34: **0 failures**
* `--verify`: **0 problems** on all three configs
* corpus: **371,847 edges · 0 errors · 371,847/371,847 snippet-cited**
* drafts remaining: **492 → 458**

## Open questions

* **22 drafts remain under ARO:3000557** — hydrolysis (5), fusidic-acid lactonisation (2),
  hydroxylation (1), bacitracin amidohydrolysis (1), and others. Small, individually
  cheap, but each needs its own snippet.
* **The ~49 efflux records under ARO:3000159** still need measuring before curating —
  round 67's caution that SMR's proton-antiport edge must not be copied to RND/MFS/ABC
  pumps stands.
