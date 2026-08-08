---
topic: causal-graphs
round: 90
date: 2026-08-07
target: aro/FUNC_RESISTANCE — ddl D-Ala-D-Ala ligases (ARO:3003970), 1 record
prior_round: causal-graphs-round89.md
---

# Causal graphs — Round 90: the enzyme that makes the cell vulnerable

I had counted this record among the 27 "cluster-level" van drafts behind the modelling
question. **It is not a cluster.** My split matched it because the word appears at the *end*
of its definition — *"depending on the presence of vancomycin resistance clusters"*. It is
a ligase family.

**Sixth time this session a pattern of mine was too coarse and the record only surfaced on
reading.** The hook's challenge — that those records were *grouped* with a decision rather
than gated by it — was correct for at least this one.

## The inversion

Every van record curated in rounds 20–23 and 87–89 describes something that **produces
resistance**. ddl is the opposite:

> *"Non-van ligases that synthesize D-Ala-D-Ala, **the default cell wall precursor that
> makes a cell vulnerable** to glycopeptide antibiotics."*

It builds the thing the drug binds. Losing it is what matters — round 71's
resistance-by-absence shape, arriving from the van set by a completely different route.

A test pins the framing, because **inverting this into a resistance story would be the
easiest possible error after twenty van records that all run the other way.**

## A phenotype that is not resistance

> *"…**can** render bacteria glycopeptide **DEPENDENT** **depending on** the presence of
> vancomycin resistance clusters."*

Doubly hedged, and *dependence* is a different phenotype from resistance. The note keeps
both the hedge and the distinction rather than flattening it into "confers resistance".

## Provenance

* records touched: **1** · SEEDED → REVIEWED
* `just test`: **675 passed** (+2) · `--verify-all`: 90 families, **0 problems**
* corpus: **372,265 edges · 0 errors · 372,265/372,265 snippet-cited**
* drafts remaining: **319 → 318**

## Open questions

* **26 records remain cluster-level** — re-checked, and this was the only misfiled one.
* **My own test asserted on a node LABEL** where the framing lives in the node **id**. The
  label is the chemical name and should not editorialise; the slip is recorded in the test.
