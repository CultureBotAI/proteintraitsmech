---
topic: causal-graphs
round: 123
date: 2026-08-10
target: aro/FUNC_RESISTANCE — nat (ARO:3004910), 2 records
prior_round: causal-graphs-round122.md
---

# Causal graphs — Round 123: the record whose relation and definition name different mechanisms

Chosen off the measured survey (#392), which found the standing hand-over note's backlog
figures stale in every particular and ~150 of 190 drafts to be effort rather than decision.
`nat` is from the prodrug/isoniazid block that survey recommended first.

## One sentence, three separate problems

> *"Arylamine N-acetyltransferase catalyzes the transfer of the acetyl group from acetyl
> coenzyme A to the free amino group of arylamines and hydrazines. **Reports have shown**
> that **overexpression** of this enzyme **may be** responsible for increased resistance to
> isoniazid."*

**1. The route CARD names is not the one its ARO relation asserts.** The record carries
`ARO:3000212` — *"mutation conferring antibiotic resistance"* — and its definition says
**overexpression**. The promoter takes the mechanism node from the relation and the snippets
from the definition, so without care this record gets a mutation-mechanism edge evidenced by
a sentence about expression level.

`overexpression` is therefore its own node, with its own edges, and the note says the
relation and the definition disagree. Filed as **#393**, because nothing detects the class
and it is the *first edge of every `ARO:3000212` graph*.

**2. Attributed, then hedged.** *"Reports have shown"* (round 97's shape) and *"may be
responsible"* (round 63's) stack on one claim. The `overexpression → resistance` edge is
`RO:0002610 correlated with`, and the whole sentence is quoted so both survive.

**3. The easy inference is the reader's, not the source's.** Isoniazid **is** a hydrazine,
and CARD says NAT acts on *"arylamines and hydrazines"*. Joining those two facts gives a
clean drug-inactivation mechanism — and **CARD never joins them.** It states the chemistry,
then states separately that overexpression may confer resistance.

So no edge makes isoniazid the enzyme's substrate. This is round 120's FrxA/nfsB distinction
on a harder case: there the missing clause was absent, here the missing clause is one step of
chemical reasoning away, which makes it easier to supply without noticing.

**What can be said, and its scope.** The KB record `Pfam:PF00797` *does* make the link:

> *"NAT is also responsible for the inactivation of Isoniazid (a drug used to treat
> tuberculosis) **in humans**."*

That is cited — as `RO:0002610`, on its own edge, with the organism scope stated in the notes,
because this record is *M. tuberculosis* nat. A causal predicate would assert the transfer
across organisms, and nothing supports that. Same treatment as round 121's Neisseria
modelling result.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just lint`: passed · `just test`: **751 passed** (+2), run before the push
* corpus after: **350,267 nodes · 372,573 edges · 0 errors · 372,573/372,573 snippet-cited**
* `just validate` on both: 0 failures · `--verify`: 3 KB CURIEs, 0 skips, 0 problems
* `just audit-fit`: 0 · drafts remaining: **190 → 188**

## Open questions

* **#393 wants a count before more `ARO:3000212` families are curated.** For every promoted
  record carrying that mechanism, does its own definition contain a mutation word, or does it
  say *overexpression* / *upregulation* / *increased expression*? Unknown today.
* **#345, #365 and #393 are one family of defect** — the graph's fixed structure asserting
  something the record's own text does not. That framing is more useful than three issues.
* **`ARO:3004893` (ahpC) is the other clean prodrug-activation record and is blocked on
  #260**, where CARD contradicts itself: one ahpC record says the enzyme *activates*
  antibiotics, the other calls it an alkyl hydroperoxide reductase protecting against
  oxidative stress.
