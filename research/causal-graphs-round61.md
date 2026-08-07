---
topic: causal-graphs
round: 61
date: 2026-08-07
target: aro/FUNC_RESISTANCE — antibiotic resistant DNA topoisomerase subunits (ARO:3000370), 17 records
prior_round: causal-graphs-round60.md
---

# Causal graphs — Round 61: the same genes, a different drug, a different mechanism

Rounds 18–19 curated gyrA/parC/gyrB/parE for **fluoroquinolones**, where the drug traps
the cleavage complex. These 17 records are mostly **aminocoumarin** resistance on
overlapping genes — and CARD states a *different* mechanism for them:

> *"Many drugs target topoisomerases to inhibit DNA synthesis. Resistant DNA topoisomerase
> subunits **prevent antibiotic binding** and thus confer resistance."* — ARO:3000370

Not trapping, not stabilising: the drug simply cannot bind. Aminocoumarins act at the
ATPase site rather than the cleavage complex, so this is the right claim for these records
and the wrong one for rounds 18–19's.

**A test pins that the two do not merge.** If someone unified the configs, these records
would silently acquire a cleavage-complex claim no source here makes — the same
silent-inversion risk round 56's pncA direction test guards against.

## Scope stated, as in rounds 54–55

The worked case quotes gyrB and aminocoumarins specifically:

> *"Point mutations in DNA gyrase subunit B (gyrB) can result in resistance to
> aminocoumarins. These mutations usually involve arginine residues in organisms."*

The family also covers **parE** and **parY**, which that sentence does not name. The
`notes` say so and a test pins it.

## The guards were quiet, and that was the signal

`--verify`: 9 precondition skips, **0 problems, 0 near-misses**. After four too-narrow
patterns earlier this session, the #264 detector's silence is what made those 9 exclusions
trustworthy without re-reading each one. Second round running where a guard's silence
carried the information — the first was round 60.

## Provenance

* records touched: **17** · SEEDED → REVIEWED · 9 left as drafts
* `just test`: **624 passed** (+2) · `just validate` on all 17: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **576 → 559**

## Open questions

* **#267's sweep is still the right next step and still unbuilt.** I attempted it this
  session and backed it out: a per-family selector reported 1,561 "problems", nearly all
  of them records curated under their own more specific family. The sweep needs a
  cross-family "does ANY config accept this record?" question, which is a different query
  than the one `verify()` can answer today.
* **The remaining efflux/regulator drafts are the bulk of what is left**, and rounds 59–61
  suggest the tooling now holds up at that scale.
