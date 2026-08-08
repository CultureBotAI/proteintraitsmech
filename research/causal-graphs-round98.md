---
topic: causal-graphs
round: 98
date: 2026-08-08
target: aro/FUNC_RESISTANCE — tet(34) (ARO:3002870), 1 record
prior_round: causal-graphs-round97.md
---

# Causal graphs — Round 98: "this config doesn't fit" was never followed by "so which one does?"

tet(34) has been excluded from **four** chemistry configs across rounds 60, 70 and 91. Every
refusal was correct: it carries `ARO:0001004`, `ARO:3000213` and `ARO:3000450` while
describing none of them, and #267 filed the misfiling.

**And CARD states a mechanism the whole time:**

> *"tet(34) causes the activation of Mg2+-dependent purine nucleotide synthesis, **which
> protects the protein synthesis pathway**."*

That is target protection. It sat uncurated for **37 rounds** because each round asked
*"does this config fit?"*, got a correct **no**, and stopped. Nobody asked *"then which one
does?"*

`just audit-drafts` (#316) is what surfaced it — the same query that found the three
stranded gyrB records one round earlier.

## One sentence, three mechanism ids

The record carries three chemistry ids and describes none of them, so **all three cite the
same sentence**. That is not a snippet borrowed to satisfy `UncoveredMechanism` (rounds 72,
77): it is the only mechanism CARD gives, and therefore the honest evidence for each of the
three ids the record wrongly carries. A test asserts all three map to one string, and the
note says why.

**Both directions are pinned**: the protection config accepts it, and the hydroxylation
config — fixed in #310 after re-accepting it once — still refuses it.

## A shell-quoting mistake, recorded

The first attempt to comment on #267 used backticks around the mechanism ids in a
`--body` argument; the shell substituted them and ate three ids. Reposted via heredoc with
a correction note. **This is the second time this session** that backticks in a `gh` body
caused command substitution.

## Provenance

* records touched: **1** · SEEDED → REVIEWED
* `just test`: **690 passed** (+2) · `audit-drafts`: 0 accepted
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **286 → 285**

## Open questions

* **#267's misfiling is unchanged** — tet(34) still carries three unsupported mechanism
  ids. Curating it does not fix CARD's classification.
