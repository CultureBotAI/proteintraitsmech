---
topic: causal-graphs
round: 55
date: 2026-08-07
target: aro/FUNC_RESISTANCE — 23S rRNA mutations (ARO:3000336), 16 records
prior_round: causal-graphs-round54.md
---

# Causal graphs — Round 55: the 23S remainder, and the rRNA set closed

Round 50 curated the **macrolide** subset of 23S and needed a literature search to do it —
the round where "no paper exists" turned out to mean "my query shape is wrong". This is
everything else: lincosamides, oxazolidinones, phenicols, pleuromutilins, streptogramins,
aminoglycosides, capreomycin.

**It needed no search.** CARD's parent term states the entire chain:

> *"Point mutations in bacterial 23S rRNA from the large ribosomal subunit that confer
> resistance to antibiotics. Antibiotics such as linezolid block peptide synthesis through
> peptidyl transferase activity. **Mutations in the 23S rRNA subunit reduce antibiotic
> binding affinity at specific sites, conferring resistance.**"* — ARO:3000336

Drug action, mutation effect, direction, and the causal link, in three sentences. Round
51's lesson for the third round running: **read the source before searching.** Rounds 51,
54 and 55 all needed little or no literature for exactly this reason; rounds 50 and the
three failed #219 attempts needed a lot, because I was chasing mechanisms the sources
never claimed.

## Same shape as round 54, deliberately

```
binding_site --part of--> determinant     ← the drug's site is INSIDE the target
determinant --part of--> subunit (GO:0015934)
determinant --has quality--> low_affinity ← the causal core, CARD's words
low_affinity --negatively regulates--> binding_site
drug0 --negatively regulates--> pt_activity (GO:0000048)
```

A test now pins that **both** rRNA configs keep the `binding_site --part of--> determinant`
edge and `NUCLEIC_ACID` typing, so the two cannot drift apart silently.

## Scope stated, again

The peptidyl-transferase sentence names **linezolid**. The family spans seven drug classes
that act at the same centre but are not named by it, and the edge `notes` say so — pinned
by a test, as in round 54. The affinity edge carries a **second** citation (ARO:3004187,
lincosamides) precisely to show the family claim is not linezolid-only.

## Provenance

* records touched: **16** · SEEDED → REVIEWED · round 50's 27 macrolide records untouched
* `just test`: **606 passed** (+2) · `just validate` on all 16: **0 failures**
* `--verify`: 4 KB CURIEs, 0 precondition skips, 0 uncovered mechanisms, **0 problems**
* corpus: **371,331 edges · 0 errors · 371,331/371,331 snippet-cited**
* drafts remaining: **638 → 622**

## Open questions

* **The rRNA set is now done** — 16S (round 54, 14) + 23S macrolide (round 50, 27) +
  23S remainder (this round, 16) = **57 records**. #215's question about rRNA's place in a
  protein-traits KB is untouched and still open; nothing here depends on its answer.
* **Per-drug binding sites** remain the refinement for both configs (domain V, the PTC,
  helix 34/44), curatable from the records' own definitions without new literature.
* **What is left is the 565 label-only efflux/regulator block**, which is the first batch
  too large to review by reading every skip line — the check that caught three defects this
  session.
