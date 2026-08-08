---
topic: causal-graphs
round: 102
date: 2026-08-08
target: aro/FUNC_RESISTANCE — ESX-5 secretion subunits (ARO:3004916), 2 records
prior_round: causal-graphs-round101.md
---

# Causal graphs — Round 102: a record that argues with itself

The family term ARO:3004916 carries **no mechanism id at all**, which is why nothing could
be keyed on it and why it sat outside `audit-drafts`' reach — that audit only sees records
under a *configured* family. Its **members** carry ids and definitions:

> *"eccB5 is a transmembrane protein **within the ESX-5 secretion system complex** … and
> mutations **contribute to a decreased uptake of antibiotic** in the outer membrane."*

Round 86's subunit shape (part-of a named complex) plus reduced permeability, hedged as
CARD hedges it: *"contribute to"*, not *"confer"*.

## eccC5 contradicts itself in one sentence

> *"…mutations contribute to a decreased uptake of antibiotic in the outer membrane,
> **yet** the Relational Sequencing Tuberculosis Data platform finds **no evidence of an
> association** between eccC5 mutations and drug resistance."*

CARD states the mechanism and cites evidence against it **in the same breath**.

**The sentence is quoted whole, on the mechanism edge.** Truncating at the comma would
leave a clean claim the source itself disputes — and the comma is exactly where a tidier
snippet would end. A test asserts both halves are present.

This is #220's shape with the contradiction *inside* the source rather than between source
and paper. Commented there: two instances now, different origins, plus #306's 65 records —
all the same carrier problem, **a real judgement with a reason, stored where nothing can
query it**.

## A gap in audit-drafts worth naming

`audit-drafts` reports records under **configured** families. These four were under a
family with no config *and* no mechanism id, so nothing pointed at them; I found them by
measuring the 223-record tail directly. The audit's blind spot is the mirror of the one it
was built to fix.

## Provenance

* records touched: **2** · SEEDED → REVIEWED · 3 excluded (thin variants, no complex named)
* `just test`: **695 passed** (+1) · corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **277 → 275**

## Open questions

* **`audit-drafts` cannot see families with no config.** A companion query — largest
  *un*configured families — is what found this round's work and is not yet a recipe.
