---
topic: causal-graphs
round: 89
date: 2026-08-07
target: aro/FUNC_RESISTANCE — vanJ homologues (ARO:3004255), 1 record
prior_round: causal-graphs-round88.md
---

# Causal graphs — Round 89: one record, three of my own errors

The last van protein record with anything curatable. Its definition is a bare resistance
claim — *"vanJ and vanJ homologue proteins confer resistance to teicoplanin"* — but it
**names vanJ**, whose mechanism round 88 curated. So the graph points at that record rather
than copying its chemistry (round 22's rule), and inherits whatever ARO:3002914 says today.

The edge is **homology, not mechanism**: CARD groups these by shared resistance phenotype
and never says every homologue performs vanJ's reaction.

## Three errors, and what caught each

**1. The predicate was semantically wrong.** I used `RO:0002159`, which the OLS *term*
endpoint failed to return — and I nearly recorded that as "unverifiable" and moved on.
Checking the *search* endpoint instead named it: **"serially homologous to"**, a
developmental term for repeated structures within one organism (vertebrae). Not sequence
homology. Replaced with `RO:0002158` "shares ancestor with", verified the same way.

The near-miss is the part worth keeping: an empty API response is not evidence of absence,
and I was one step from treating it as such.

**2. The config pointed vanJ at itself.** ARO:3002914 is a *descendant* of this family
term, and its own definition contains "vanJ" — so the marker matched and vanJ's record
gained a *"shares ancestor with vanJ"* edge. **A homology edge to oneself is not a weaker
claim, it is a meaningless one.** Caught by reading the written records, not by any gate;
now excluded by identifier and pinned by a test.

**3. A lambda, then an ambiguous variable name.** Both caught by ruff.

## The pattern across rounds 84–89

Six rounds, 21 records, and **nine self-inflicted defects** — three destructive edits, a
wrong mechanism id, a wrong predicate, a self-referential edge, and three lint errors.
Every one was caught, most by tooling built earlier in the same session. The corpus is
clean; my care is not what is keeping it clean.

## Provenance

* records touched: **1** · SEEDED → REVIEWED
* `just test`: **672 passed** (+2) · `--verify-all`: 89 families, **0 problems**
* corpus: **372,262 edges · 0 errors · 372,262/372,262 snippet-cited**
* drafts remaining: **320 → 319**

## Open questions

* **The van protein records are done.** Two family terms remain (*"Van genes encode for
  various proteins…"*) with no specific claim, and 27 cluster-level records behind the
  modelling question.
