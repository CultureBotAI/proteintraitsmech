---
topic: causal-graphs
round: 66
date: 2026-08-07
target: aro/FUNC_RESISTANCE — antibiotic resistant EF-Tu (ARO:3003356), 12 records
prior_round: causal-graphs-round65.md
---

# Causal graphs — Round 66: the first family curated *without* a mechanism

Every round since 51 has found CARD stating a mechanism, often verbatim. **This family
does not have one.** CARD says only:

> *"Sequence variants of elongation factor Tu that confer resistance to different classes
> of antibiotics."* — ARO:3003356

Stated **causally** — "confer", not the nim family's "associated with" (round 65) — but it
never says *how*. Nor can the generic mutation term rescue it:

> *"Point mutations in the DNA may lead to an altered gene product… Examples included
> modified antibiotic targets with lower binding affinities **and** the deactivation of
> repressors that result in increased expression of genes"* — ARO:3000212

Those are two **incompatible** routes offered as examples. Quoting it would not pin
EF-Tu's, only make the graph look better sourced than it is.

## What is asserted, and what is not

```
determinant --enables--> ef_activity (GO:0003746)
ef_activity --part of--> elongation (GO:0006414)
```

That is the one mechanistic fact CARD's own naming supplies: the determinant *is* an
elongation factor. Plus the base determinant→resistance edge, which CARD does state.

**Not asserted:** that elfamycins bind EF-Tu, that the variants reduce that binding, or
that the drug inhibits elongation. All true as far as I know, none of it cited by anything
read this round.

This is round 51's failure mode named in advance rather than after three wasted rounds: I
spent three attempts on fabG1 sourcing a mechanism I knew and the records never claimed. A
test pins the absence, so the well-known story cannot drift in later from memory.

## Why curate at all rather than leave drafts

The determinant→resistance claim **is** stated, causally, by CARD. Leaving 12 records as
drafts would lose that. The honest shape is a *short* graph that says what is known and
stops — not a blocked record, and not a padded one. #254 (pilQ) was left as a draft because
CARD asserted **no** claim at all; here there is a real claim, just not a mechanistic one.

## Provenance

* records touched: **12** · SEEDED → REVIEWED · 0 skipped
* `just test`: **633 passed** (+1) · `just validate` on all 12: **0 failures**
* `--verify`: 5 KB CURIEs checked, **0 problems, 0 near-misses**
* both GO terms checked non-obsolete against OLS before use (#157)
* corpus: **371,707 edges · 0 errors · 371,707/371,707 snippet-cited**
* drafts remaining: **516 → 504**

## Open questions

* **The elfamycin-binding arm is a real, citable addition** — it needs one paper showing
  elfamycins bind EF-Tu and that the resistant variants reduce it. That is a well-posed
  literature task, unlike #219's, because the claim is standard and the search shape is
  obvious.
* **SMR efflux pumps (11)** and the **67-record inactivation-enzyme group** remain the
  next non-van work.
