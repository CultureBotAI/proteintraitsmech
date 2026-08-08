---
topic: causal-graphs
round: 96
date: 2026-08-08
target: aro/FUNC_RESISTANCE — three gyrB records stranded since round 61
prior_round: causal-graphs-round95.md
---

# Causal graphs — Round 96: three records a precondition of mine held for 34 rounds

Round 61 curated the topoisomerase subunits and left nine excluded. Three of those nine
were **gyrB records that should have been promoted**:

> definition: *"Point mutation in Escherichia coli resulting in aminocoumarin resistance."*
> label: *"**Escherichia coli gyrB** conferring resistance to aminocoumarin"*

The definition is thin and never names a gyrase. **The label does**, and the ARO term name
is authoritative. Round 61's precondition read the definition only, so the records sat as
drafts for 34 rounds while `--verify` reported them as expected skips.

## Why reading the label is safe here and not everywhere

The obvious objection is #254: **pilQ's label** said *"pilQ gene conferring resistance to
beta-lactam"* while its definition revealed an outer-membrane secretin — there the
definition was the **corrective** and the label was misleading.

The difference is what the label names. Here it names **the gene the family is about**
(gyrB, under the gyrB family term), and the parent term supplies the mechanism the members
omit. There it named a *drug class*, not a mechanism, and the family placement was the
thing in doubt.

**A test pins both directions**: the thin gyrB record now passes, and pilQ is still refused.

## The pattern, stated

This is the **eighth** too-narrow precondition of mine this session. The others were found
by counting refusals; this one by asking why a record with a configured ancestor was still
a draft — a question the earlier "which drafts would a config accept?" query (#310) also
answers, and which found the tet(34) defect the same way.

Both defects were invisible to every gate because **a precondition skip is expected
behaviour**. The only thing that surfaces them is asking what got refused and why.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **683 passed** (+1) · `--verify-all`: 95 families, **0 problems**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **291 → 288**

## Open questions

* **pgsA (3) read and left**: *"an integral membrane protein involved in phospholipid
  biosynthesis"* — a role and no mechanism, like round 95's aftA but without even an
  essentiality claim.
* **234 drafts have no config**; **53 remain decision-bound** (#309, #229).
