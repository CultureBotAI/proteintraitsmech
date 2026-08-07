---
topic: causal-graphs
round: 60
date: 2026-08-07
target: aro/FUNC_RESISTANCE — tetracycline inactivation by hydroxylation (ARO:3000036), 18 records
prior_round: causal-graphs-round59.md
---

# Causal graphs — Round 60: tetracycline hydroxylases, and the fifth misfiled record

CARD's parent term states the mechanism **and** why it confers resistance, in two
sentences — so no search was needed, round 51's lesson for the fifth round running:

> *"Enzymes or other gene products which hydroxylate tetracycline and other tetracycline
> derivatives. Hydroxylation inactivates tetracycline-like antibiotics, thus conferring
> resistance to these compounds."*

The substrate is **the antibiotic itself**, which is what makes this inactivation rather
than target alteration — the distinction rounds 18–19 and 51–59 kept circling.

## tet(34) is not a hydroxylase

**ARO:3002870** carries the hydroxylation mechanism id, and its own definition says
something else entirely:

> *"tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, which
> **protects the protein synthesis pathway**."*

That is **target protection**, not inactivation. Excluded with an explicit reason, left as
a draft, filed as **#267**.

**Fifth record this session filed under a family whose mechanism its own definition
contradicts** — after MecI (#251), pilQ (#254), ahpC (#260), and the five thin-definition
class D records. That is no longer a run of bad luck; it is a property of CARD's hierarchy
worth stating as one finding rather than five issues.

## The guards agreed with the exclusion

`--verify` reported **1 precondition skip, 0 problems** — and crucially the #264 near-miss
detector stayed **silent**, confirming tet(34) is a genuine miss rather than a
pattern-too-narrow artefact. That is the first round where a new guard's silence carried
information, rather than its noise.

## Provenance

* records touched: **18** · SEEDED → REVIEWED · tet(34) left as a draft
* `just test`: **622 passed** (+1) · `just validate` on all 18: **0 failures**
* `--verify`: 1 precondition skip, 0 near-misses, **0 problems**
* corpus: **371,475 edges · 0 errors · 371,475/371,475 snippet-cited**
* drafts remaining: **594 → 576**

## Open questions

* **#267 and its four siblings should probably be one issue, not five.** The pattern —
  CARD placing a record under a mechanism its own definition contradicts — now has five
  instances found by five different preconditions. A single sweep asking "for every curated
  family, which members' definitions disagree with the family mechanism?" would find the
  rest in one pass, and `audit-roles` is most of the machinery.
* **`hydroxylation` is ungrounded.** A tetracycline monooxygenase GO/EC term very likely
  exists; not looked up rather than guessed.
