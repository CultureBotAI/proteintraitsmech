---
topic: causal-graphs
round: 77
date: 2026-08-07
target: aro/FUNC_RESISTANCE — Lpx lipid A biosynthesis (ARO:3000012), 4 records
prior_round: causal-graphs-round76.md
---

# Causal graphs — Round 77: the same molecule, the opposite intervention

Rounds 73–76 curated **five** routes that neutralise lipid A's charge by attaching
something to it. These four records — LpxA, LpxC, LpxD and the Acinetobacter Lpx mutant —
disrupt lipid A's **biosynthesis**.

**Same molecule, opposite direction of intervention**, and a reason not to reach for the
charge snippets: those five modify an intact lipid A; these change whether it is made
properly at all. A test pins that the config's nodes mention biosynthesis and not negative
charge.

## CARD hedges twice in one sentence

> *"The LpxA gene is **widely known to be involved in** the biosynthesis of lipid A … and
> mutations to this gene **may cause** resistance to antimicrobial peptides that target the
> outer membrane."*

Neither the enzyme's role nor the resistance is stated firmly. So:

* the determinant edge is `participates in` (RO:0000056), matching CARD's *"involved in"*
  rather than upgrading it to `enables`;
* the middle edge's `notes` say outright that the mechanism is **implied by the pairing**
  of a biosynthetic role with membrane-targeting peptides, and is **not** something CARD
  spells out;
* the `altered_membrane` node is deliberately vague, because CARD says the drug *"targets
  the outer membrane"* and never says what the mutation does to it.

The family term is the one place a firm claim appears (*"causing antibiotic resistance"*),
and it is quoted alongside rather than instead of the hedged record-level sentence.

## The guard stopped the write again — seventh time

These records carry `ARO:3000212` (mutation) as well as `ARO:3000213`, and my config
covered only the second. `UncoveredMechanism` refused all four, silently reporting
"0 records written" until I checked why.

Same resolution as round 72's BRP(MBL): the one sentence genuinely serves both ids — it
names the biosynthetic role *and* says *"mutations to this gene may cause resistance"* — so
covering both is one claim spanning two ids, not a snippet borrowed to satisfy a guard.

**Seventh time this session** `UncoveredMechanism` has stopped a record being written on
evidence that did not cover it. It is the single most productive guard in this codebase.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **652 passed** (+2) · `just validate` on all 4: **0 failures**
* corpus: **372,014 edges · 0 errors · 372,014/372,014 snippet-cited**
* drafts remaining: **409 → 405**

## Open questions

* **The non-van cell-wall-restructuring drafts are now down to 3**: the family term,
  tet(34) (correctly refused, #267) and an undecaprenyl-pyrophosphate record.
* **The remaining 41-record cell-wall block is almost entirely van/glycopeptide cluster**,
  so it is behind the operon modelling question rather than behind effort.
