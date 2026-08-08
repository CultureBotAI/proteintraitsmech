---
topic: causal-graphs
round: 99
date: 2026-08-08
target: aro/FUNC_RESISTANCE — generic target protection (ARO:3000185), 3 records
prior_round: causal-graphs-round98.md
---

# Causal graphs — Round 99: the records three mode-specific configs could not reach

Rounds 31, 44 and 45 curated **TetM** (ribosome displacement), **FusB** (EF-G rescue) and
**HelR** (RNAP displacement) — three distinct protection **modes**, each with its own
paper. `audit-drafts` showed three records under the same family still refused by all
three, and reading them says why: **they describe protection without naming a mode.**

> *"These proteins confer antibiotic resistance by bind the antibiotic target to prevent
> antibiotic binding."* — ARO:3000185, quoted verbatim including CARD's own *"by bind"*

That is the general mechanism, complete. Stretching a mode config to cover them would
import a mechanism from an unrelated paper — the failure this session has guarded against
since round 51.

## One edge separates protection from sequestration

```
protection    determinant --molecularly interacts with--> the TARGET
sequestration determinant --molecularly interacts with--> the DRUG   (round 72)
```

Both prevent the drug reaching its target; they differ in **what the determinant binds**.
A test asserts protection binds the target *and* that round 72's sequestration config still
binds the drug — so a later pass cannot harmonise them into one shape.

## Evidential status kept

ARO:3000507 says its proteins *"have been **experimentally shown** to protect
RNA-polymerase"*. That attribution is quoted rather than flattened into a bare claim, as
with round 97's ArmR (*"have previously been shown"*).

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **692 passed** (+2) · `audit-drafts`: 0 accepted
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **285 → 282**

## Open questions

* **`audit-drafts` also surfaced Bah amidohydrolase and the fosfomycin inactivation
  family**, both with stated mechanisms and no config. Neither read this round.
