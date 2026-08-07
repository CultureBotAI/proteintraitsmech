---
topic: causal-graphs
round: 32
date: 2026-08-06
target: aro/FUNC_RESISTANCE — mprF (ARO:3003580, mprF records), 10 records
prior_round: causal-graphs-round31.md
---

# Causal graphs — Round 32: mprF, and the drug that is repelled

An **eighth** kind of mechanism. The drug is not destroyed, altered, displaced, pumped out
or left unactivated — it is **repelled**, because the determinant changes the surface charge
of the envelope so a cationic peptide no longer reaches it.

## Peschel et al., J Exp Med 2001 — PMID:11342591

> *"We describe a novel staphylococcal gene, mprF, which determines resistance to several
> host defense peptides such as defensins and protegrins."*

> *"Analysis of membrane lipids demonstrated that the mprF mutant no longer modifies
> phosphatidylglycerol with l-lysine."*

> *"As this unusual modification leads to a reduced negative charge of the membrane surface,
> MprF-mediated peptide resistance…"*

Three steps, each measured: the gene confers the resistance, the mutant loses the lipid
modification, and the modification is what lowers the charge. The `determinant → lysyl-PG`
edge is shown **by absence** — the mutant no longer makes the modified lipid — and its
description says so.

The paper also gives the phenotype in the setting that matters: *"An mprF mutant strain was
killed considerably faster by human neutrophils and exhibited attenuated virulence in
mice."*

## One family term, four chemistries — so a precondition again

`ARO:3003580` (*gene altering cell wall charge*) also holds **ArnT** and **PmrF** (L-Ara4N
on lipid A), the **ICR** phosphoethanolamine transferases, and **PhoP** (a regulator). They
share the *principle* — add positive charge, repel cationic peptides — and not the
chemistry. `_requires_mprf` took the 10 mprF records; **129 candidates were refused**.

## The guard refused all ten records first, and was right to

My first config guessed four mechanism ids. Every one was wrong, and the run wrote
**nothing**:

```
mechanism skip: ARO:3003421 — no snippet for ARO:3003588
mechanism skip: ARO:3003324 — no snippet for ARO:0001001
… 10 records written: 0
```

The real ids are `ARO:3003588` (*charge alteration conferring antibiotic resistance*) and
`ARO:0001001` (*antibiotic target alteration*). Before #203 the promoter would have
substituted its first snippet for both and stamped all ten `REVIEWED`. This is the second
round running (31, 32) where that guard caught my own mechanism ids, which suggests
guessing them is the normal failure and not an unlucky one.

## Provenance

* records touched: **10** · SEEDED → REVIEWED · 129 refused by precondition
* corpus after: **39,647 records · 40,115 graphs · 348,376 nodes · 370,226 edges ·
  0 errors · 370,226/370,226 edges snippet-cited**
* warnings 6,144 → **6,164**: +20, the lysyl-PG and surface-charge nodes
* `just validate` on all 10 individually: **0 failures**
* drafts remaining: **1,000 → 990**

## Open questions

* **The other three chemistries under this term** are each a small round: ArnT/PmrF
  (L-Ara4N), the ICR phosphoethanolamine transferases, PhoP as a regulator (which would
  point at the enzymes it induces, as rounds 22 and 24 did).
* **`surface_charge` is a QUALITY node with no grounding** — the first QUALITY node in the
  corpus. Net envelope charge has no ontology term, which is the same gap as the QRDR, the
  RRDR and the decoding site.
