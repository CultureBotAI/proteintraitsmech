---
topic: causal-graphs
round: 20
date: 2026-08-05
target: aro/FUNC_RESISTANCE — vanX (ARO:3000011), 9 records; and a map of the van remainder
prior_round: causal-graphs-round19.md
---

# Causal graphs — Round 20: vanX, a third kind of mechanism, and what the van clusters actually contain

## The van clusters are not one family, and the ligases are already done

103 drafts mention a `van` gene or a glycopeptide. The first useful measurement was that
**the resistance ligases carry no drafts at all**: `ARO:3002978` (D-Ala-D-Lac ligase —
vanA/vanB/vanD/vanM) has **0**, because round 14 promoted them. What is left of the van
clusters is the **accessory and regulatory machinery**, and it is organised by *gene role*,
not by drug:

| family | ARO | drafts |
|---|---|--:|
| vanR (response regulator) | ARO:3000574 | 14 |
| vanS (sensor kinase) | ARO:3000071 | 14 |
| **vanX (D,D-dipeptidase)** | **ARO:3000011** | **9 — this round** |
| vanH (D-lactate dehydrogenase) | ARO:3000006 | 8 |
| vanY (D,D-carboxypeptidase) | ARO:3000077 | 7 |
| vanT (serine racemase) | ARO:3000372 | 7 |
| D-Ala-D-Ser ligases (vanC/E/G/L/N) | ARO:3002979 | 6 |
| vanXY (bifunctional) | ARO:3000496 | 6 |
| vanW · vanZ · vanU/V/J/K · cluster-level records | — | ~30 |

Each has a **different molecular function in one shared pathway**, so each needs its own
edges and its own evidence — one config cannot cover them the way ARO:3003292 covered 25
gyrA records. That is the opposite of round 18's finding, and it is why this round is 9
records rather than 100.

## Why vanX first

It is the crispest causal statement in the whole set, and one 1994 paper carries all of
it — **Reynolds, Depardieu, Dutka-Malen, Arthur & Courvalin, PMID:7854121**:

> *"These results establish that VanX is required for production of a D,D-dipeptidase that
> hydrolyses D-Ala-D-Ala, thereby preventing pentapeptide synthesis and subsequent binding
> of glycopeptides to D-Ala-D-Ala-containing peptidoglycan precursors at the cell surface."*

## A third kind of mechanism

| round | kind | how resistance happens |
|---|---|---|
| 12–16 | inactivation | the enzyme destroys the drug (β-lactamases) |
| 18–19 | target alteration | the target is changed so the drug binds it less well (gyrA/parC/gyrB/parE) |
| **20** | **precursor depletion** | **the drug's binding target is never made** |

VanX does not touch the drug and does not alter a target. It removes the substrate
(D-Ala-D-Ala) from which the drug's binding site would be built.

## Graph design

8 nodes (7 grounded), 9 edges, all snippet-cited. Routed through the KB trait record
`Pfam:PF01427` (*D-ala-D-ala dipeptidase*):

```
domain (Pfam:PF01427) --enables [RO:0002327]-->            dipeptidase (GO:0016805)
dipeptidase --has input [RO:0002233]-->                    D-alanyl-D-alanine (CHEBI:16576)
dipeptidase --negatively regulates [RO:0002212]-->         pentapeptide       ← the causal core
drug0 (glycopeptide) --molecularly interacts with [RO:0002436]--> pentapeptide
```

All four ontology terms were checked non-obsolete against OLS before use (#157).

**The specificity edge carries a negative result on purpose.** `dipeptidase has input
D-Ala-D-Ala` cites *"Pentadepsipeptide, pentapeptide and D-Ala-D-Lac were not substrates
for the enzyme."* — the sentence that makes the claim specific rather than vague, and the
reason the enzyme does not destroy the resistant precursor it is helping to build.

**The `determinant → resistance` edge uses #190's two-item form**, which landed for exactly
this shape:

1. the **genetic requirement** — *"Insertional inactivation of vanX led to increased
   synthesis of pentapeptide with a resulting change in the ratio of pentadepsipeptide:
   pentapeptide to less than 1:1."*
2. the **mechanism** that follows from it — the summary sentence above.

Loss of function is what makes this causal rather than correlative, and before #190 only
one of the two would have fitted on the edge.

## Provenance

* records touched: **9** · SEEDED → REVIEWED · edges written: **81**
* corpus after: **39,647 records · 40,115 graphs · 347,774 nodes · 369,336 edges ·
  0 errors · 369,336/369,336 edges snippet-cited**
* warnings 5,951 → **5,960**: +9, exactly one deliberate ungrounded node per record
  (`pentapeptide` — ChEBI has the D-Ala-D-Ala dipeptide but not the UDP-MurNAc pentapeptide)
* `just validate` on all 9 individually: **0 failures**
* drafts remaining: **1,166 → 1,157**

## Open questions

* **vanH is the natural next batch** (8 records): it supplies the D-lactate that the
  already-promoted vanA/vanB ligases esterify, so it completes the pathway from the other
  end. PMID:1931965 (Bugg et al. 1991) characterises VanH as *"a D-specific alpha-keto acid
  dehydrogenase"* and is already located.
* **vanR/vanS (28 records) are the biggest single block and are regulatory, not catalytic.**
  Their causal graph is induction of the cluster, not modification of a precursor — a
  fourth shape, and the one where two literatures (sensing and transcriptional activation)
  will most want #190's multi-evidence edges.
* **`pentapeptide` has no ChEBI term.** If the UDP-MurNAc pentapeptide matters across
  rounds — it will, for vanY, vanXY and the ligases — that is a term request, not a mapping
  exercise. Same conclusion as the QRDR nodes in rounds 18–19.
* **The cluster-level records (13 under ARO:3000234) describe operons, not proteins.**
  Whether a gene *cluster* should carry a protein-trait causal graph at all is a modelling
  question worth settling before curating them.
