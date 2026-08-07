---
topic: causal-graphs
round: 59
date: 2026-08-07
target: aro/FUNC_RESISTANCE — class D beta-lactamases (ARO:3000075), 19 records
prior_round: causal-graphs-round58.md
---

# Causal graphs — Round 59: class D, and the fourth over-narrow pattern

Rounds 12–16 curated class A β-lactamases (KPC, TEM) through `PROSITE:PS00146`, the
**class-A-specific** active-site signature. That motif **must not** be reused here — it is
class A's, and citing it for class D would be precisely the borrowed-evidence defect
filed as #196.

`PROSITE:PS00337` is the right record, and unusually its own definition **names class D**:

> *"Class-B enzymes are zinc containing proteins whilst class **-A, C and D** enzymes are
> serine hydrolases."*
>
> *"Beta-lactamases (EC 3.5.2.6) are enzymes which catalyze the hydrolysis of an amide
> bond in the beta-lactam ring…"*

So the membership claim rests on the source saying so, not on my inference — the thing
#196 is about. A test pins that PS00146 is not used.

## The claim deliberately left out

Class D's distinguishing chemistry is a **carbamylated lysine acting as the general
base** — the reason OXA enzymes are interesting at all. **No source read this round states
it**, so it is absent, the `note` says so, and a test pins the absence.

That is round 58's lesson recurring one round later: the claim I know best is the one most
likely to arrive uncited.

## The bug, for the fourth time this session

My precondition required "class D" and "beta-lactamase" **adjacent**. RAD-1's definition
reads *"a class D **RAD** beta-lactamase"*, so it was excluded — with a reason that was
false about the record.

| # | round | pattern | what it wrongly did |
|---|---|---|---|
| 1 | 52 | keyword over full YAML | 17 records skipped as "describes a repressor" |
| 2 | 53 | `\bpbp\s?\d` | skipped "PBP transpeptidases" |
| 3 | 58 | `hydrolyz\b` | audit reported 0 flagged while broken |
| 4 | **59** | `class d beta-lactamase` adjacency | skipped "class D RAD beta-lactamase" |

**Every one was caught by reading the records the guard refused, never by a gate.** #256
catches variant 1 only. This is now the most reliable defect in my own work, and the
`--verify` suite does not detect it.

## What stays a draft, honestly

Five records — BSU-1, CDD-1, CDD-2, RSD2-1, RSD2-2 — whose **own definitions do not say
class D** ("BSU-1 is a BSU beta-lactamase"). CARD's hierarchy places them there; their
definitions do not support it. Left as drafts rather than promoted on hierarchy alone.

## Provenance

* records touched: **19** · SEEDED → REVIEWED · 5 left as drafts
* `just test`: **618 passed** (+3) · `just validate` on all 19: **0 failures**
* `just audit-roles`: 1 candidate (vanS, known benign)
* corpus: **371,421 edges · 0 errors · 371,421/371,421 snippet-cited**
* drafts remaining: **613 → 594**

## Open questions

* **A pattern-breadth check is now clearly worth building.** Four instances, one detector
  (#256) covering one of them. The shape is: a precondition refuses a record whose own
  definition contains a *near-miss* of the required pattern. That is mechanically testable
  — fuzzy-match the requirement against refused definitions and flag high-similarity
  misses. Filed as **#264**.
* **The 5 thin-definition class D records** are the same question as #196 at record level.
