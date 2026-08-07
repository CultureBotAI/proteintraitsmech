---
topic: causal-graphs
round: 53
date: 2026-08-07
target: aro/FUNC_RESISTANCE — mutant PBPs (ARO:3003040), 16 records
prior_round: causal-graphs-round52.md
---

# Causal graphs — Round 53: the other half of the PBP family, and a skip log worth reading twice

Round 52 curated **target replacement** on ARO:3003040 — an acquired foreign PBP. This is
the same family's other mechanism: **target alteration**, the native PBP mutated until the
drug binds it poorly. ARO:3003040 now takes the **list form**, and each config's
precondition selects on the mechanism id the record itself carries.

Round 51's lesson applied first again — CARD states it verbatim:

> *"Mutations in PBP transpeptidases that change the affinity for penicillin thereby
> conferring resistance to penicillin antibiotics."* — ARO:3003938

and the **direction**, which the parent term leaves as a bare "change":

> *"Point mutation in Neisseria gonorrhoea PBP1 (ponA) **decreases** affinity between
> beta-lactam antibiotic molecule and PBP1."* — ARO:3004833

Literature was needed only for the step CARD asserts but does not show — that mutations
actually yield the low-affinity protein: **PMID:1938899** (Laible & Hakenbeck 1991). Its
`notes` state it studied *S. pneumoniae* PBP2x, so the other species rest on CARD's
family-level claim rather than on that paper.

## 16 records, 8 organisms

*E. coli*, *H. influenzae*, *H. pylori* (pbp1/2/3), *K. pneumoniae*, *N. gonorrhoeae*,
*N. meningitidis*, *S. pneumoniae* (PBP1a/2b/2x), *S. pyogenes*.

## Two records deliberately left as drafts

| record | why |
|---|---|
| ARO:3005046 MecI | a **repressor** of mec transcription (#251) — round 22's shape |
| ARO:3004835 pilQ | an outer-membrane **secretin** of the Type IV pilus, filed under the PBP family; its route is permeability, not target affinity (**#254**) |

Both carry an explicit skip reason rather than vanishing.

## The bug, again — and the reason it was caught

Round 52's finding was that a guard can state a **false reason** and still pass. This round
produced another instance, in the guard I had just written:

```
precondition skip: ARO:3003938 — own definition does not name a penicillin-binding protein
```

ARO:3003938 is *"Mutations in **PBP transpeptidases** that change the affinity for
penicillin"* — a PBP record, and the very term this config cites as its `reference`. My
pattern was `\bpbp\s?\d`, requiring a number; "PBP transpeptidases" has none. Widened to
`\bpbp\b` and pinned by a test.

**It was caught only by reading the skip log line by line**, which is now the second round
running where that habit was the thing that worked. That is the argument for **#253**: skip
reasons are prose that nothing verifies, and reading them is currently the only check.

## Provenance

* records touched: **16** · SEEDED → REVIEWED · **21 of 23** PBP records now curated
* `just test`: **599 passed** (+3) · `just validate` on all 16: **0 failures**
* corpus: **371,198 edges · 0 errors · 371,198/371,198 snippet-cited**
* drafts remaining: **667 → 652**

## Open questions

* **The per-config skip counters double-count.** A record curated by config A is reported
  as "excluded" by config B in the same run, which made the numbers read alarmingly
  (`12 already curated / 10 excluded` for 23 records) until measured on disk. Cosmetic, but
  it cost a diagnostic detour.
* **#254 (pilQ)** may not be alone — worth asking how many ARO records sit under a family
  whose mechanism their own definition contradicts. That is #229's question again.
