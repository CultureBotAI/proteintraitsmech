---
topic: causal-graphs
round: 54
date: 2026-08-07
target: aro/FUNC_RESISTANCE — 16S rRNA mutations (ARO:3003211), 14 records
prior_round: causal-graphs-round53.md
---

# Causal graphs — Round 54: 16S rRNA, the counterpart to round 50

Round 50 curated 23S rRNA macrolide resistance and had to find its paper by search. This
is the 16S side, and it needed **no search at all** — round 51's lesson applied first, and
CARD carries the whole chain verbatim.

The general rule, on the parent term:

> *"The antibiotic-binding sites are located within functionally important structures in
> the ribosomal RNA. Antibiotic resistance is often conferred by base substitutions or
> methylations at these sites in the rRNA."* — ARO:3003211

and the worked case, on ARO:3003499:

> *"Tetracycline binds tightly to the helix 34 domain in 16S rRNA, where it interferes
> sterically with the binding of aminoacyl-tRNA to the ribosome A site to block protein
> synthesis."*

Together those give the reason the mechanism works at all: **the drug's binding site is
*inside* the target, so a base substitution changes the site itself.** That is the
`binding_site --part of--> determinant` edge, and it is what distinguishes this from an
ordinary target-alteration graph.

## The determinant is RNA

`determinant_node_type: NUCLEIC_ACID`, as round 50 established. In a protein-traits KB the
temptation is to type everything PROTEIN; for rRNA that is false rather than merely
awkward. The open modelling question about rRNA's place here (#215) is unaffected — this
records what the determinant *is*, not whether it belongs.

## One snippet honestly scoped

The helix-34 quote is **tetracycline's**. This family also spans pactamycin, edeine,
viomycin and peptide/polyamine antibiotics, which bind their own sites (helix 44, the 3'
major and minor domains). The edge `notes` say the snippet does not cover them, and a test
pins that — a single-drug snippet used family-wide has to admit it.

## Provenance

* records touched: **14** · SEEDED → REVIEWED
* `just test`: **604 passed** (+2) · `just validate` on all 14: **0 failures**
* `--verify`: 4 KB CURIEs checked, 0 precondition skips, 0 uncovered mechanisms, **0 problems**
* corpus: **371,252 edges · 0 errors · 371,252/371,252 snippet-cited**
* drafts remaining: **652 → 638**

## Open questions

* **Per-drug binding sites are the obvious refinement.** helix 34 (tetracycline), helix 44
  (aminoglycosides/streptomycin), 3' minor domain (edeine) are each stated in the records'
  own definitions, so a per-drug `binding_site` label is curatable without new literature.
  Deliberately not done here: it would need one config per drug, and the family-level graph
  is honest as long as the snippet's scope is stated.
* **The 23S set still has ~15 drafts** beyond round 50's macrolide batch.
