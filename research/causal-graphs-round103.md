---
topic: causal-graphs
round: 103
date: 2026-08-08
target: aro/FUNC_RESISTANCE — cls (ARO:3003272), 4 records; plus audit-drafts' third section
prior_round: causal-graphs-round102.md
---

# Causal graphs — Round 103: closing the audit's mirror blind spot

Round 102 found four records by a hand-written query, and named the reason `audit-drafts`
could not see them: **it only reports records under a *configured* family.** A family with
no config and no mechanism id is invisible to it — the mirror of the blind spot it was
built to fix.

That query is now the recipe's **third section**:

```
UNCONFIGURED families with drafts (116 terms) -- nothing has ever considered these:
     14  ARO:0000010    antibiotic resistance gene cluster, cassette, or operon
     13  ARO:3000234    glycopeptide resistance gene cluster
      5  ARO:3007522    antifungal-resistant cytochrome P450 enzyme
      ...
      3  ARO:3003272    daptomycin resistant cls
```

It surfaced **cls** on its first run — a family I had not seen in 103 rounds.

## cls: three sentences, and the third does not follow

> *"Cardiolipin synthetase catalyzes the formation of cardiolipin from two
> phosphatidylglycerol molecules. Cardiolipin is important in **membrane translocation and
> permeabilization**. Current known mutations on the enzyme confer resistance to
> **daptomycin**."*

The reaction, why the product matters, and the resistance — and **nothing connects the
third to the first two**. Daptomycin is a membrane-active lipopeptide, so the inference is
inviting; that is precisely why it is left out. Round 83 refused rpoC rifampicin's rpoB
mechanism for the same reason, and there the obvious guess was not merely uncited but
attached to the wrong subunit.

A test bans *daptomycin*, *resist* and *drug* from the config's asserted text.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **697 passed** (+2) · corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **275 → 271**

## Open questions

* **The audit's three sections now cover all three states**: a draft a config would accept,
  a draft a configured family refuses, and a family nothing has considered. The first is 0,
  the second 56, the third 116 terms.
* **27 of the unconfigured terms are the van clusters** (#309) — the largest single block
  and still decision-bound.
