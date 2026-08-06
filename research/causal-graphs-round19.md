---
topic: causal-graphs
round: 19
date: 2026-08-05
target: aro/FUNC_RESISTANCE — parC, gyrB and parE fluoroquinolone families, 28 records
prior_round: causal-graphs-round18.md
---

# Causal graphs — Round 19: the rest of the fluoroquinolone target set, and why it is three families rather than one

Round 18 closed gyrA and I queued the remainder as *"gyrB/parC/parE — 40 records, same
mechanism and same two papers, reusing round 18's config."* **That framing was wrong in
two ways, and checking it was the first thing this round did.**

## What the enumeration actually showed

| I said | measured |
|---|---|
| "40 records" | **40 drafts mention these genes, but only 29 are fluoroquinolone**; the rest are **aminocoumarin** resistance (a different drug, a different mechanism) or parents above the drug split |
| "same mechanism" | **two mechanisms.** ParC is topoisomerase IV's homologue of *GyrA*; GyrB and ParE are the *B* subunits — different domains, and the resistance residues are not the same chemistry |
| "same two papers" | **four papers.** The B subunits have their own QRDR literature, and the A-subunit affinity experiment does not apply to them |

The distinguishing fact is one sentence in the round-18 paper, which I had already
fetched but had not read for this purpose (PMID:24576155):

> *"The subunits in gyrase are GyrA and GyrB. The homologous subunits in topoisomerase IV
> are ParC and ParE in Gram-negative species and GrlA and GrlB in Gram-positive species.
> GyrA (and the equivalent topoisomerase IV subunit) contains the active site tyrosine
> residue. GyrB (and the equivalent topoisomerase IV subunit) contains the ATPase domain
> as well as the TOPRIM domain, which binds the divalent metal ions involved in DNA
> cleavage and ligation."*

So the split is **A subunits (GyrA, ParC) vs B subunits (GyrB, ParE)**, and it decides
both the domain node and which experiment may be cited.

## Families promoted

| family | ARO | records | domain node | QRDR evidence |
|---|---|--:|---|---|
| parC (fluoroquinolone) | ARO:3000619 | **12** | `Pfam:PF00521` (A) | PMID:15388468 (Ser80-Arg &c.), PMID:24576155 (Ser84/Glu88 in *A. baumannii* topo IV) |
| gyrB (fluoroquinolone) | ARO:3000864 | **11** | `Pfam:PF00204` (B) | PMID:1656869 (Asp426Asn, Lys447Glu), PMID:22290942 (QRDR extended to 500–540) |
| parE (fluoroquinolone) | ARO:3003313 | **5** | `Pfam:PF00204` (B) | PMID:15388468 (Glu453-Gly … Ser518-Cys) |

gyrA's 25 records were re-promoted unchanged in substance — they pick up the shared
helpers and one snippet correction (below).

## Why the B subunits could not reuse gyrA's evidence

The gyrA/parC causal edge cites *"mutation of either residue significantly decreases the
affinity of gyrase or topoisomerase IV for quinolones"* — the **water–metal ion bridge**
serine/acidic pair, which lies in the **A** subunit. Citing it on a gyrB record would be
citing the wrong experiment about the wrong protein.

The B subunits get their own:

* **PMID:1656869** (Yoshida 1991) is the exact B-subunit counterpart of the gyrA QRDR
  paper — *"all nine type 1 mutants had a point mutation from aspartic acid to asparagine
  at amino acid 426 and that all four type 2 mutants had a point mutation from lysine to
  glutamic acid at amino acid 447"*.
* **PMID:22290942** (Pantel 2012) is stronger evidence than association: they
  reconstituted gyrase with mutant GyrB and measured inhibition — *"All these
  substitutions are clearly implicated in FQ resistance, underlining the presence of a hot
  spot region housing most of the GyrB substitutions implicated in FQ resistance (residues
  NTE, 538 to 540)."*
* **parE is the weakest tier and is recorded as such** in the edge's own `notes`: PMID:15388468
  reports substitutions found in clinical isolates, not a reconstituted-enzyme measurement.

`tests/test_promoter_extra_edges.py::test_the_a_and_b_subunits_do_not_share_a_domain_node`
pins the split so a later edit cannot quietly collapse it.

## What the canary found this time

Promoting **one record per family before the rest** caught a real error in all three:

> `ERROR … graph resistance: duplicate node_id 'domain'`

The shared node helper emitted a `domain` node while `protein_traits["primary_key"]` was
also `"domain"` — round 18 had no clash only because its key was `gyra_domain`.
**`just validate` accepted it** (the schema has no uniqueness constraint on `node_id`);
only `just audit-graphs` calls it an error. Three records had it; 28 would have.

A second thing the canary surfaced was not a code defect but a scoping one:
`ARO:3003702`, *"Pseudomonas aeruginosa gyrA **and** parC conferring resistance to
fluoroquinolones"*, sits under the parC family and was swept in. Both are A subunits so
the domain node would have been right, but the QRDR node would have been labelled
ParC-only for a record about two QRDRs. The promoter gained a per-family `exclude` list
and the record stays a draft, awaiting a config with one QRDR node per subunit. **Round 18's
PR said this record was excluded; without the new mechanism, that claim would have
silently stopped being true.**

## One correction to round 18

Its cleavage-complex snippet was written `5'-DNA termini` where the source has `5′-DNA
termini` (U+2032 prime). Small, but "verbatim" is the rule that makes these snippets worth
having, so the shared constant now carries the prime and all 25 gyrA records were
re-promoted. Round 18 is #187; this correction rides in #189 because it stacks on it.

## Provenance

* records touched: **53** = 28 newly promoted + 25 gyrA re-promoted
* status SEEDED → REVIEWED on the 28 · edges written: **308** on the new records
* corpus after: **39,647 records · 40,115 graphs · 347,738 nodes · 369,291 edges ·
  0 errors · 369,291/369,291 edges snippet-cited**
* warnings 5,895 → **5,951**: +56, exactly the 28 × 2 deliberate ungrounded nodes
* `just validate` on all 53 individually: **0 failures** · `just test` 492 → **501**
* drafts remaining: **1,194 → 1,166**

## Open questions

* **The aminocoumarin families are untouched and are next in this gene set** —
  ARO:3000479 (gyrB) and ARO:3000457 (parE), ~5 drafts. Novobiocin binds the GyrB **ATPase**
  site, so it is neither this round's mechanism nor gyrA's: a third shape, needing the
  ATPase domain node (`Pfam:PF02518` exists in the KB) and its own literature.
* **`ARO:3003702` (gyrA + parC) needs a two-QRDR config** — the first record here whose
  determinant names two subunits.
* **Still no fold node**, unchanged from round 18: no quotable source for which CATH
  superfamily either QRDR-bearing region adopts.
* **The QRDR nodes remain ungrounded** — 53 of them now. If this is worth closing, it is a
  new term request, not a mapping exercise.
