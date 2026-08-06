---
topic: causal-graphs
round: 22
date: 2026-08-06
target: aro/FUNC_RESISTANCE — vanR (ARO:3000574) and vanS (ARO:3000071), 16 records
prior_round: causal-graphs-round21.md
---

# Causal graphs — Round 22: vanR/vanS, and the first graphs that point at earlier rounds

## A fourth kind of mechanism, and the first that confers no resistance

| rounds | kind | how resistance happens |
|---|---|---|
| 12–16 | inactivation | the enzyme destroys the drug |
| 18–19 | target alteration | the target is changed so the drug binds it less well |
| 20 | precursor depletion | the drug's binding target is never made |
| 21 | precursor substitution | the binding target is rebuilt with 1000-fold lower affinity |
| **22** | **regulation** | **nothing here resists anything — it switches on the genes that do** |

VanR and VanS are the two halves of a two-component system. Writing their graph as if they
conferred resistance would be false. So their graph **ends at the records that do**:
`ARO:3000006` (vanH, round 21) and `ARO:3000011` (vanX, round 20), whose mechanisms are
already curated. **This is the first round whose graphs cite earlier rounds' output as
nodes** rather than restating what those records already say.

That is what the corpus is for. A regulator record that repeated vanX's dipeptidase
chemistry would duplicate it and drift from it; one that points at `ARO:3000011` inherits
whatever that record says today.

## One paper, again

**Arthur, Molinas & Courvalin, J Bacteriol 1992 — PMID:1556077** characterised the system
and mapped the promoter:

| claim | verbatim |
|---|---|
| the system regulates the enzymes | *"Synthesis of these enzymes was regulated at the transcriptional level by the VanS-VanR two-component regulatory system encoded by the proximal part of the cluster."* |
| what VanR is | *"VanR was a transcriptional activator related to response regulators of the OmpR subclass."* |
| what VanS is | *"VanS stimulated VanR-dependent transcription and was related to membrane-associated histidine protein kinases which control the level of phosphorylation of response regulators."* |
| **the promoter, mapped** | *"Analysis of transcriptional fusions with a reporter gene and RNA mapping indicated that the VanR-VanS two-component regulatory system activates a promoter used for cotranscription of the vanH, vanA, and vanX resistance genes."* |
| where resistance actually is | *"The distal part of the van cluster encodes VanH, VanA, and a third enzyme, VanX, all of which are necessary for resistance."* |

**One edge deliberately understates what it could have claimed.** `activity →
vanr_protein` says *positively regulates*, not *phosphorylates*: the paper states the
stimulation and the kinase relationship but reports no direct phosphotransfer assay. The
`notes` say so. A phosphotransfer edge would need the biochemistry paper, which this round
did not use.

## The correction this round needed: not every cluster has the operon

The first promotion covered **all 28** vanR/vanS drafts. That was wrong, and the review
caught it by asking whether the config's claim holds for every descendant rather than for
the family term.

The evidence is **VanA-type** (PMID:1556077 studied Tn1546/pIP816), and the downstream
nodes are vanH and vanX. But the van clusters do not all have those genes. Checked gene by
gene against the corpus's own `van* gene in van* cluster` records rather than inferred from
the cluster letter:

| cluster | vanH | vanX | genes present |
|---|---|---|---|
| vanA · vanB · vanD · vanF · vanM · vanO · vanP | ✅ | ✅ | vanH vanX … |
| vanC · vanE · vanG · vanL · vanN | ❌ | ❌ | **vanT, vanXY** — the D-Ala-D-Ser route |
| vanI | ❌ | ✅ | vanK vanW vanX |

So **12 records were promoted asserting an operon composition false for their cluster**,
and are now excluded and left as drafts. They need a config whose downstream is vanT and
vanXY — which is the round already queued for the D-Ala-D-Ser side.

This is the third time a family-level config has over-reached (round 19's A/B subunits;
round 19's combined gyrA+parC record; now this), and the first where the check that caught
it was *data* — the corpus's own per-cluster gene records — rather than reading.

## Fully grounded — the first time in this thread

**9–10 nodes per record, every one with a CURIE; corpus warnings unchanged at 5,976.**

Rounds 18–21 each added 1–2 label-only nodes per record — the QRDR, the pentapeptide, the
drug–target complex — because no ontology names them. A regulatory story has no such gap:
GO has the processes (`GO:0000155`, `GO:0000156`, `GO:0045893`), ARO has the genes, and
NCBIfam has the families (`NF033117` VanR, `NF033091` VanS). The 16 records added **136 nodes
and 184 edges and not one warning**.

The family nodes follow round 21's rule: a determinant is a **member of** a family
(`RO:0002350`), not composed of one, and the snippet is NCBIfam's own **product name**, not
the KB record's definition — this repo composes those (#196, and the round-15
don't-cite-yourself rule).

## Provenance

* records touched: **16** (8 vanR + 8 vanS, the vanH/vanX-bearing clusters only) ·
  SEEDED → REVIEWED · edges written: **184** · 12 deliberately left as drafts
* corpus after: **39,647 records · 40,115 graphs · 347,902 nodes · 369,504 edges ·
  0 errors · 369,504/369,504 edges snippet-cited**
* warnings **5,976 → 5,976** — unchanged
* `just validate` on all 16 individually: **0 failures**
* drafts remaining: **1,149 → 1,133**

## Open questions

* **The D-Ala-D-Ser side is now one coherent round**: the 12 excluded vanR/vanS records,
  the 6 D-Ala-D-Ser ligases, vanT (7) and vanXY (6) all belong to the same clusters and
  share a downstream. Doing them together is better than doing vanY/vanXY alone.
* **vanY (7) + vanXY (6)** are both D,D-carboxypeptidases and remain a candidate for one
  config covering two families.
* **The phosphotransfer edge is understated on purpose.** PMID:8981985 reports that VanS
  *negatively* controls VanR-mediated activation in the absence of drug — i.e. it is
  bifunctional, kinase and phosphatase. That is a real refinement and needs its own round;
  the current edge is not wrong, it is coarse.
* **Cross-round node citation should probably become a rule, not a one-off.** Any regulator,
  efflux repressor or two-component record whose downstream is already curated should point
  at it. Worth stating in the `edison-causal-graphs` skill before the ~565 label-only
  efflux/regulator drafts are approached, since most of them are this shape.
