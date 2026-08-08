---
topic: causal-graphs
round: 95
date: 2026-08-07
target: aro/FUNC_RESISTANCE — mshA (5) + aftA (5), 10 records
prior_round: causal-graphs-round94.md
---

# Causal graphs — Round 95: one word apart

## mshA and mshC differ by a single verb

Round 94 read **mshC** and left it: *"Mutations that occur on the mshC gene resulting in the
inability for antibiotic to **function**."* That says nothing mechanistic.

**mshA** reads: *"…resulting in the inability for antibiotic to **activate**."*

One word different, and it names a mechanism — the drug is a prodrug and this determinant's
loss stops its activation. Rounds 56 (pncA) and 57 (ndh) curated the same kind from far
richer sentences; here it arrives in four words.

A test pins the separation, including that **mshC still has no config** — so a later pass
that notices two near-identical families cannot merge them without tripping it.

## aftA has a role and no mechanism at all

> *"Arabinofuranosyltransferase is **involved in** the biosynthesis of the arabinogalactan
> region of the mAGP complex, an **essential** component of the mycobacterial cell wall."*

CARD names the enzyme's job and calls its product essential. It **never mentions a drug,
mutations, or resistance** — thinner than round 81's ppsA-E, which at least paired a role
with a hedged resistance claim.

So the graph carries the role and stops, and a test bans *resist*, *drug*, *inhibit* and
*mutation* from its asserted predicates. `participates in` matches CARD's *"is involved
in"* rather than upgrading it.

## Provenance

* records touched: **10** (5 + 5) · SEEDED → REVIEWED
* `just test`: **682 passed** (+2) · `just validate` on all 10: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **301 → 291**

## Open questions

* **237 drafts still have no config**; **53 remain decision-bound** (#309, #229).
* **The remaining families are ≤5 records and increasingly thin** — several now say only
  that mutations confer resistance, with no role, drug, or mechanism.
