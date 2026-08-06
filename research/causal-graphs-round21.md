---
topic: causal-graphs
round: 21
date: 2026-08-05
target: aro/FUNC_RESISTANCE — vanH (ARO:3000006), 8 records
prior_round: causal-graphs-round20.md
---

# Causal graphs — Round 21: vanH, and when the KB trait is a family rather than a domain

Round 20 did vanX, which **removes** the drug's binding target. vanH is the other end of
the same pathway: it **supplies the replacement**. Together with the vanA/vanB ligases
(promoted in round 14) they are one mechanism split across three genes, and the corpus now
has all three.

## One paper, six edges

**Bugg, Wright, Dutka-Malen, Arthur, Courvalin & Walsh, Biochemistry 1991 —
PMID:1931965** purified the enzyme and measured the affinity loss the whole mechanism
exists to produce. Every mechanism edge in this round is a sentence from it:

| step | verbatim |
|---|---|
| what VanH is | *"We report purification of VanH to homogeneity, characterization as a D-specific alpha-keto acid dehydrogenase, and comparison with D-lactate dehydrogenases from Leuconostoc mesenteroides and Lactobacillus leichmanii."* |
| what consumes its product | *"VanA was found to catalyze ester bond formation between D-alanine and the D-hydroxy acid products of VanH, the best substrate being D-2-hydroxybutyrate (Km = 0.60 mM)."* |
| the product reaches the wall | *"The VanA product D-alanyl-D-2-hydroxybutyrate could then be incorporated into the UDPMurNAc-pentapeptide peptidoglycan precursor by D-Ala-D-Ala adding enzyme from Escherichia coli or by crude extract from E. faecium BM4147."* |
| **the causal core, quantified** | *"The vancomycin binding constant … (Kd greater than 73 mM) was greater than 1000-fold higher than the binding constant for N-acetyl-D-alanyl-D-alanine (Kd = 54 microM), partly due to the disruption of a hydrogen bond in the vancomycin-target complex, thus providing a molecular rationale for high-level vancomycin resistance."* |

That last sentence carries **both** arms — the drug's normal affinity and its loss — which
is why it appears on two edges with different `notes` rather than being paraphrased once.

## The modelling decision worth recording: family, not domain

Every family since round 18 used `protein_traits`, whose fixed edge is

```
domain --part of [BFO:0000050]--> determinant
```

**vanH has no `protein_traits` block.** Its honest KB trait is `NCBIfam:NF000492`
(*D-lactate dehydrogenase VanH*), and a determinant is a **member of** a protein family,
not composed of one. The membership edge is written explicitly with `RO:0002350`.

The obvious alternative was `Pfam:PF00389`, the D-isomer-specific 2-hydroxyacid
dehydrogenase catalytic domain — which exists in the KB and is almost certainly present in
VanH. **It is not used**, because its InterPro abstract never mentions VanH, so citing it
for a membership claim would be precisely the defect filed as #196 one round earlier.
Choosing the weaker-looking node with real evidence over the better-looking node with
borrowed evidence is the point.

**The membership edge's two items are joined explicitly rather than implied**: the paper
says what VanH does; NCBIfam names the family that does it. The `notes` say so. The
NCBIfam snippet is that database's own **product name**, not the KB record's definition —
this repo composes those, and quoting one would be citing ourselves (the round-15 rule).

## Graph

9 nodes (7 grounded), 10 edges, all cited:

```
determinant --member of [RO:0002350]-->              family (NCBIfam:NF000492)
family --enables [RO:0002327]-->                     dh_activity (GO:0008720)
dh_activity --has output [RO:0002234]-->             D-hydroxy acid (CHEBI:16004)
D-hydroxy acid --causally upstream of [RO:0002411]-->depsipeptide
depsipeptide --negatively regulates [RO:0002212]-->  vancomycin-target complex   ← causal core
drug0 (glycopeptide) --molecularly interacts with [RO:0002436]--> vancomycin-target complex
```

**One grounding caveat is stated on the node itself:** `d_hydroxy_acid` is grounded to
`CHEBI:16004` ((R)-lactate), the physiological product, while the quoted measurements used
D-2-hydroxybutyrate, the best in vitro substrate. The node says which is which rather than
letting the CURIE imply the assay used lactate.

## Provenance

* records touched: **8** · SEEDED → REVIEWED · edges written: **80**
* corpus after: **39,647 records · 40,115 graphs · 347,814 nodes · 369,384 edges ·
  0 errors · 369,384/369,384 edges snippet-cited**
* warnings 5,960 → **5,976**: +16 = 8 × 2 deliberate ungrounded STATE nodes
  (`depsipeptide`, `van_complex`)
* `just validate` on all 8 individually: **0 failures**
* drafts remaining: **1,157 → 1,149**

## Open questions

* **vanR/vanS (28 records) is the biggest remaining block and a fourth mechanism shape** —
  regulatory induction of the cluster rather than modification of a precursor. It is also
  the case where #190's multi-evidence edges will matter most: sensing (VanS
  autophosphorylation) and transcriptional activation (VanR) are separate literatures.
* **vanY (7) and vanXY (6) are both D,D-carboxypeptidases** and probably share one
  mechanism config — the first chance in the van set to cover two families with one
  config, which is what round 18 could do and rounds 19–21 could not.
* **Two more ungrounded STATE nodes per record**, for the same reason as round 20's
  `pentapeptide`: ChEBI has the dipeptides but not the UDP-MurNAc precursors, and a
  drug–target complex is not a compound. Across rounds 20–21 that is 25 such nodes; if the
  van set is finished it will be ~100, which makes a term request worth pricing.
