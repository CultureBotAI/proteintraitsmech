---
topic: causal-graphs
round: 56
date: 2026-08-07
target: aro/FUNC_RESISTANCE — pncA (ARO:3004267), 3 records
prior_round: causal-graphs-round55.md
---

# Causal graphs — Round 56: pncA, and the first mechanism that runs backwards

## A 12th mechanism kind, and the only one so far that is an absence

Every mechanism curated in this thread works by the determinant **doing** something —
destroying the drug, rebuilding a precursor, pumping it out, replacing a target, changing
a binding site. pncA is the first where resistance is the **loss** of an activity the
susceptible cell has.

Pyrazinamide is a **prodrug**. Without pyrazinamidase it is never converted to pyrazinoic
acid, so the drug is inert rather than defeated. Nothing resists it; nothing activates it.

CARD states the chain, round 51's lesson for the fourth round running:

> *"pncA is a pyrazinamidase/nicotinamidase. It catalyzes the activation of pyrazinamide
> to pyrazinoic acid. Mutations arise within the pncA gene that caused the loss of
> pyrazinamidase activity is the major mechanism of antibiotic resistance."* — ARO:3003418

> *"Point mutations in pncA prevent the enzyme from activating antibiotics."* — ARO:3004267

## The edge direction is the whole point

```
determinant --has quality--> loss
loss --negatively regulates--> pzase (GO:0008936)   ← the core, running BACKWARDS
pzase --has input--> drug0
pzase --has output--> poa (pyrazinoic acid)
```

The core edge points from the **loss** to the activity, not from the determinant to the
drug. A later reader "tidying" that into `determinant --> drug0` would silently invert the
biology, so **a test pins the direction** and says why.

## Two groundings handled differently, on purpose

* `pzase` **is** grounded — `GO:0008936` (nicotinamidase activity), the EC 3.5.1.19
  function CARD names, checked non-obsolete against OLS before use (#157).
* `poa` is **not**. Pyrazinoic acid is the active metabolite, not the drug class, and I did
  not verify a CHEBI id for it this round. A guessed CURIE would be exactly the unverified
  grounding rounds 51–55 were about. The node description says so, and a test pins it.

## Provenance

* records touched: **3** · SEEDED → REVIEWED
* `just test`: **608 passed** (+2) · `just validate` on all 3: **0 failures**
* `--verify`: 4 KB CURIEs, 0 precondition skips, 0 uncovered mechanisms, **0 problems**
* corpus: **371,342 edges · 0 errors · 371,342/371,342 snippet-cited**
* drafts remaining: **622 → 619**

## Open questions

* **katG and ethA are already curated** — the "~40 record prodrug-activation" item in
  NEXT_TASKS was stale. What actually remained was pncA (3), **ndh (4)** and **ahpC (3)**.
  Measuring beat trusting the queue, again.
* **ndh and ahpC are the same shape but not the same claim.** ahpC is a compensatory
  peroxidase whose relation to isoniazid resistance is indirect, and ndh alters the
  NADH/NAD+ ratio rather than losing an activating step. Neither is a pncA copy, and each
  should be read on its own definition first.
* **`poa` wants one verified CHEBI lookup**, which is a five-minute job and would remove
  the round's only deliberate grounding gap.
