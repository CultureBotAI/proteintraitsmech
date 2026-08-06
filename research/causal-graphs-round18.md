---
topic: causal-graphs
round: 18
date: 2026-08-05
target: aro/FUNC_RESISTANCE — the gyrA fluoroquinolone family (ARO:3003292), 25 records
prior_round: causal-graphs-round17.md
---

# Causal graphs — Round 18: gyrA, and the first mechanism that is not drug inactivation

Rounds 12–17 covered catalysis (M-CSA), inactivation (β-lactamases), interaction
(BioLiP/MetalPDB) and transformation (Rhea/EC). What was left in the ARO tail is
**target alteration**, where the determinant is not an enzyme acting on the drug but the
drug's own target, altered so the drug binds it less well.

## Gap

`NEXT_TASKS.md` item 1: **1,219** records still carrying `graph_id: resistance-draft`
(re-counted today, unchanged). This round closes **25**, leaving **1,194**.

| gene group | drafts | this round |
|---|--:|--:|
| gyrA (fluoroquinolone, `is_a` ARO:3003292) | 25 | **all 25** |
| gyrA (other parents — triclosan ×3, gyrA+parC, topoisomerase-subunit parent) | 5 | no — see Open questions |
| gyrB · parC · parE (rest of the fluoroquinolone target set) | 40 | next |
| van* clusters | ~100 | later |
| rpoB/rpoC · katG/ahpC/fabG1/ethA · 16S/23S | ~80 | later |
| no gene symbol in the label (efflux, regulators) | 565 | needs per-record triage, not a family PR |

## What this corrects in the backlog

`NEXT_TASKS.md` says of these 1,219: *"No shared family config fits — needs per-gene
evidence."* **For gyrA that is wrong, and measurably so.** 25 of the 30 gyrA drafts are
`is_a` descendants of one family term (ARO:3003292, "fluoroquinolone resistant gyrA") and
share one mechanism, one drug class and one literature basis. The existing family promoter
covered them in a single run.

What *is* genuinely per-organism is the **residue numbering**, not the mechanism — Ser83/
Asp87 in E. coli GyrA are Ala90/Asp94 in *M. tuberculosis*. That is why this round asserts
no per-record residue node and states the frame on the QRDR node instead.

The claim should be re-scoped rather than deleted: it holds for the 565 label-only
efflux/regulator records, which is where it came from.

## Mechanism (researched)

Two sources, both free full text, and every snippet below was pasted from them rather
than paraphrased.

**Aldred KJ, Kerns RJ, Osheroff N. *Mechanism of quinolone action and resistance*.
Biochemistry 2014;53(10):1565–74. PMID:24576155** (PMC3985860)

1. The enzyme's own intermediate — *"To maintain genomic integrity during this process,
   the enzymes form covalent bonds between active site tyrosine residues and the newly
   generated 5′-DNA termini."*
2. Drug action — *"As a result of their intercalation, quinolones increase the steady-state
   concentration of cleavage complexes by acting as physical blocks to ligation."*
3. Why that kills — *"If the strand breaks overwhelm these processes, they can lead to cell
   death. This is the primary mechanism that quinolones use to kill bacterial cells"*
4. **The resistance step** — *"Furthermore, mutation of either residue significantly
   decreases the affinity of gyrase or topoisomerase IV for quinolones, and mutation of
   both residues abolishes the ability of clinically relevant quinolones to stabilize
   cleavage complexes."*
5. Which residues — *"the amino acids that most frequently are associated with quinolone
   resistance are Ser83 (based on E. coli GyrA numbering) and an acidic residue four amino
   acids downstream"*

**Yoshida H et al. *Quinolone resistance-determining region in the DNA gyrase gyrA gene of
Escherichia coli*. Antimicrob Agents Chemother 1990;34(6):1271–2. PMID:2168148** — the
paper that defined the QRDR, and **already an `xref` on these records**:

> *"quinolone resistance was caused by a point mutation within the region between amino
> acids 67 and 106, especially in the vicinity of amino acid 83, of the GyrA protein"*

So the resistance is not a change in what the enzyme does, but in how well the drug can
bind what the enzyme makes. The graph has to carry both arms — drug action and its loss.

## Graph design

**Nodes (9)** — 7 grounded, 2 deliberately not:

| node | type | grounding | note |
|---|---|---|---|
| `determinant` | PROTEIN | the record's own `ARO:` id | |
| `gyra_domain` | DOMAIN | **`Pfam:PF00521`** | KB record `data/traits/sequence/domain/pfam/dna-topoisoiv-pf00521.yaml` |
| `qrdr` | MOTIF | — | no ontology term denotes the QRDR; frame caveat carried in `description` |
| `gyrase_activity` | MOLECULAR_FUNCTION | `GO:0003918` | checked non-obsolete against OLS (#157) |
| `cleavage_complex` | STATE | — | same class as the 4,023 M-CSA reaction-intermediate STATE nodes |
| `cell_death` | PHENOTYPE | `GO:0008219` | |
| `mech0` | MOLECULAR_FUNCTION | `ARO:3000212` | from the record's own relations |
| `drug0` | CHEMICAL | `ARO:0000001` | from the record's own relations |
| `resistance` | PHENOTYPE | `GO:0046677` | |

**Edges (11 per record, 275 total), all snippet-cited.** The six that carry the actual
mechanism:

```
qrdr            --part of [BFO:0000050]-->        gyra_domain      PMID:2168148 + InterPro:IPR002205
gyra_domain     --enables [RO:0002327]-->         gyrase_activity  InterPro:IPR002205
gyrase_activity --causally upstream of [RO:0002411]--> cleavage_complex   PMID:24576155
drug0           --molecularly interacts with [RO:0002436]--> cleavage_complex  PMID:24576155
qrdr            --negatively regulates [RO:0002212]--> cleavage_complex  PMID:24576155   ← the causal core
cleavage_complex --causally upstream of [RO:0002411]--> cell_death   PMID:24576155
```

plus the five the family promoter already emitted (determinant→mech0, mech0→resistance,
determinant→resistance, resistance→drug0, gyra_domain part-of determinant).

**One edge is an inference across two sources and says so.** `qrdr part_of gyra_domain`
rests on Yoshida placing the QRDR at GyrA 67–106 *and* the InterPro abstract placing the
breakage-reunion region at the N-terminus of GyrA. Neither states the containment alone.
The edge's `notes` say that in as many words rather than presenting it as one assertion.

## What had to change in the code, and why the canary found it

The promoter's graph shape was written for **enzymatic inactivation** — an active site
that hydrolyses the drug — and every family in `FAMILY_SNIPPETS` until now fitted it.
Target alteration does not, so `promoted_graph` gained optional `extra_nodes` /
`extra_edges`, with a guard that **skips** an extra edge whose subject or object is not
among that record's nodes (mechanism and drug nodes come from each member's own ARO
relations, so a member need not carry the node an edge names).

**Applying it to one record before the other 24 found two defects in the shared builder
that had nothing to do with gyrA:**

1. the drug edge was emitted with **no `predicate_id` at all** — so promoting a draft
   *removed* the `ARO:2000001` the draft had;
2. the phenotype node was emitted **ungrounded** — so promoting a draft *removed* the
   draft's `GO:0046677`.

Both would have shipped as 25 new audit warnings blamed on the new graph. Neither is
visible to `just validate`; only `just audit-graphs` sees them, and only after writing.
Both are now fixed for every family, and pinned by `tests/test_promoter_extra_edges.py`.

## Provenance

* records touched: **25** · status SEEDED → **REVIEWED** · graphs replaced, not added
* edges written: **275**, all with a verbatim snippet · new grounded nodes: 75
* corpus after: **39,647 records · 40,115 graphs · 347,598 nodes · 369,095 edges ·
  0 errors · 369,095/369,095 edges snippet-cited**
* warnings 5,845 → **5,895**: +50, exactly the 25 × 2 deliberate ungrounded nodes
* `just validate` run on all 25 individually: **0 failures**
* drafts remaining: **1,219 → 1,194**

## Open questions

* **No fold node.** The skill's trait-routing pattern wants DOMAIN *and* FOLD. `Pfam:PF00521`,
  `CATH:1.10.268.10`, `CATH:3.90.199.10` and `CATH:2.120.10.90` all exist as KB records, but
  I found no source stating which CATH superfamily the QRDR-bearing region adopts that I
  could quote. Omitted rather than guessed; worth one lookup in the gyrB/parC round, which
  needs the same node.
* **The QRDR is ungrounded and there may be no fix.** It is a resistance-defined region, not
  a structural or sequence feature any ontology names. If it stays ungrounded, the
  gyrB/parC/parE round adds ~40 more such nodes.
* **5 gyrA drafts are deliberately not promoted**, because they are not this mechanism:
  `ARO:3004333`/`3004334`/`3004335` are **triclosan** resistance (drug class
  "disinfecting agents and antiseptics"), where the route from a gyrA substitution to
  triclosan resistance is not the QRDR story and CARD's own definition is thin;
  `ARO:3003702` is a combined **gyrA and parC** record; `ARO:3000273` is the
  topoisomerase-subunit parent above the fluoroquinolone/triclosan split.
* **`resistance --related to--> drug0` now carries `biolink:related_to`.** That is a weak
  predicate for a real relation; ARO's own `ARO:2000001` (confers_resistance_to_drug_class)
  is stronger but has the determinant, not the phenotype, as its subject. Worth revisiting
  as an edge-direction question rather than a vocabulary one.
