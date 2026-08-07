---
topic: causal-graphs
round: 29
date: 2026-08-06
target: aro/FUNC_RESISTANCE — 16S rRNA / aminoglycoside (ARO:3003666), 45 records
prior_round: causal-graphs-round28.md
---

# Causal graphs — Round 29: the first determinant that is not a protein

45 records, the largest single family this thread has curated, and the first whose
determinant is **ribosomal RNA**.

## The code said it was a protein

`promoted_graph_dict` hardcoded `node_type: PROTEIN` for the determinant. Correct for every
family until now, and simply false for the **105 draft records whose determinant is rRNA**
— 44 here, 26 under the 23S/macrolide family, the rest across linezolid, pleuromutilin,
oxazolidinone and tetracycline. `CausalNodeTypeEnum` has `NUCLEIC_ACID`; nothing was using
it. Now an optional `determinant_node_type`, defaulting to `PROTEIN`.

**The larger question is filed as #215 rather than answered here.** This is a knowledge base
of *protein* traits, and the causal-graph method requires routing mechanisms through the
corpus's own protein-trait records — a domain, a fold, an active site. An rRNA determinant
has none and cannot: the corpus holds no rRNA trait records to point at. So these graphs are
fully evidenced and structurally unlike every other family here. Round 29 curates them as
they are and says so; the choice should be made deliberately before the other 60.

## Two papers, and the resistance one measured its own mechanism

**Recht, Douthwaite & Puglisi, EMBO J 1999 — PMID:10357824**

> *"Expression in E.coli of plasmid-encoded 16S rRNA containing an A1408 to G substitution
> confers resistance to a subclass of the aminoglycoside antibiotics that contain a 6'
> amino group on ring I."*

> *"Chemical footprinting experiments indicate that resistance arises from the lower
> affinity of the drug for the eukaryotic rRNA sequence."*

The substitution was **built**, not observed, and the affinity loss **measured**, not
inferred. Note also the scope the record keeps: a *subclass* of aminoglycosides, those with
a 6′ amino group on ring I — not the whole class.

**Carter et al., Nature 2000 — PMID:11014183** supplies the drug-action arm from the 30S
crystal structures with paromomycin, streptomycin and spectinomycin, *"which interfere with
decoding and translocation"*.

## The elegant part, and it is in the graph

The resistance substitution makes the bacterial site look **eukaryotic**:

> *"A major difference in the binding site for these antibiotics between prokaryotic and
> eukaryotic ribosomes is the identity of the nucleotide at position 1408 (Escherichia coli
> numbering), which is an adenosine in prokaryotic ribosomes and a guanosine in eukaryotic
> ribosomes."*

The same fact explains why aminoglycosides are selective for bacteria **and** how bacteria
escape them. A graph that recorded only "substitution lowers affinity" would lose it, so it
is a separate edge.

## Provenance

* records touched: **45** · SEEDED → REVIEWED · edges written: **405**
* corpus after: **39,647 records · 40,115 graphs · 348,278 nodes · 370,089 edges ·
  0 errors · 370,089/370,089 edges snippet-cited**
* warnings 6,069 → **6,114**: +45, one ungrounded decoding-site node per record
* `just validate` on all 45 individually: **0 failures**
* drafts remaining: **1,075 → 1,030**

## Open questions

* **#215 should be settled before the other 60 rRNA records** — 23S/macrolide (26) is the
  next largest and has equally good literature, but it inherits the same structural
  oddness.
* **The decoding-site node is ungrounded**, like the QRDR and the RRDR. That is now four
  distinct resistance-defined regions across rounds 18–29 with no ontology term between
  them; if a term request is ever made, it should cover the class rather than one region.
