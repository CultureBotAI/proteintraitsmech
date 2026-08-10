---
topic: causal-graphs
round: 120
date: 2026-08-10
target: aro/FUNC_RESISTANCE — FrxA (ARO:3007059), 1 record
prior_round: causal-graphs-round119.md
---

# Causal graphs — Round 120: two nitroreductases, one prodrug edge

**FrxA** and **nfsB** (round 107) are both nitroreductases whose mutations confer resistance
to nitro-containing antibiotics. Their configs differ by one edge, and the difference is one
clause:

| record | CARD says | drug edge |
|---|---|---|
| nfsB | *"NfsB **reduces** a broad range of nitroaromatic compounds **including the antibiotics** nitrofurazone and nitrofurantoin"* | `has input (the drug)` |
| FrxA | *"FrxA encodes an NADH-flavin oxidoreductase … Mutations in this gene confer resistance to nitrofuran antibiotics and metronidazole"* | **none** |

nfsB's sentence makes the **drug the enzyme's substrate**, which is what licenses reading
the mutation as prodrug-activation loss. FrxA's says what the enzyme *is* and what mutations
*do*, and never connects them. A test asserts nfsB has the `drug0` edge and FrxA does not.

## The ESX-5 system term is held, and the reason is #229's

**ARO:3004915** describes the ESX-5 **secretion system**: *"The system is comprised of genes
that encode the structural components…"*

Round 102 curated its **subunits** — eccB5 and eccC5 — with `part of` edges into the
complex. The **system term itself** is the complex-versus-subunit question **#229** is
about, and curating it would answer that by fiat. A test asserts it has no config, so the
hold is visible rather than looking like an oversight.

This is the same treatment as round 86's Mex complexes and round 112's kasA: **when the
reason for not curating is a decision, the absence gets a test.**

## Provenance

* records touched: **1** · SEEDED → REVIEWED · ESX-5 system term held for #229
* `just test`: **727 passed** (+2), **run before the push** · corpus: **0 errors**
* drafts remaining: **199 → 198**

## Open questions

* **~90 unconfigured drafts remain.**
* **Three records are now held with tests naming their blocker**: kasA (#220), the ESX-5
  system term (#229), and mshC's bare record (no mechanism at all).
