---
topic: causal-graphs
round: 116
date: 2026-08-10
target: aro/FUNC_RESISTANCE — ddlA (2) + FKS2 (1), 3 records
prior_round: causal-graphs-round115.md
---

# Causal graphs — Round 116: the only record that says *why* a drug competes

## ddlA gives the structural basis folP only named

Round 82's **folP** was the first competitive-inhibition record: CARD called dapsone *"a
competitive inhibitor"* and said it competed *"with para-aminobenzoate for the active
site"*. That named the relationship.

**ddlA says why it holds:**

> *"ddlA catalyzes the ATP-driven ligation of two D-alanine molecules… **Cycloserine has a
> similar structure to d-alanine** and inhibits the growth of the cell wall."*

A **substrate analog**, with the resemblance stated. That is the only structural basis for
competition anywhere in this corpus, and it earns an edge of its own —
`drug0 --shares ancestor with--> D-alanine` on `RO:0002158`, the predicate **verified in
round 89** after `RO:0002159` turned out to mean *serially* homologous, a developmental
term.

**What ddlA does not say is also recorded**: CARD never states what mutations in ddlA do.
It describes the enzyme and the mimicry and stops, so the resistance edge the family term
implies is not written.

## FKS2 is rpoB's position in a fungus

> *"Glucan synthase FKS2 is involved in the production of the fungal cell wall… Mutations
> in FKS2 **have been shown to** confer resistance to echinocandin antibiotic micafungin."*

Echinocandins inhibit glucan synthase. **This is the record that mechanism belongs to, and
CARD does not state it** — exactly rpoB's position for rifampicin (round 106). A test now
covers both records with one assertion.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **719 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **213 → 210**

## Open questions

* **~102 unconfigured drafts remain.** Read this round and not yet curated: MSH2 (a
  mismatch-repair gene conferring multi-class resistance), Fgd1 (delamanid), ald
  (cycloserine), pepQ, BLMT.
