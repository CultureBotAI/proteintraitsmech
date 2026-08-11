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

## The mismatch that was not one

The first draft of this round asserted that `ARO:3000212` — *"mutation conferring antibiotic
resistance"* — disagreed with nat's definition, which names **overexpression**, and filed
**#393** for the class.

`ARO:3000212`'s **own** definition settles it the other way:

> *"Point mutations in the DNA may lead to an altered gene product… Examples included
> modified antibiotic targets with lower binding affinities and the deactivation of
> repressors that result in **increased expression** of genes that inactivate or pump out
> antibiotics."*

**The mechanism term explicitly covers the increased-expression route.** There is no
mismatch. #393 is closed as invalid.

This is round 51's lesson, inverted and repeated: *before building on a claim about a source,
read what the source says.* Round 51 spent three rounds sourcing a mechanism CARD never
asserted. Round 123 spent a config asserting a disagreement between a record and its
mechanism term **without reading the mechanism term** — which was one `grep` away.

The mech edge now cites `ARO:3000212`'s own definition, which is what that edge is *about*.
The first version cited nat's definition there — a sentence with no mutation claim at all
(#398).

## Two records, and only one of them joins the routes

| record | definition |
|---|---|
| **ARO:3004930** | *"Mutations that occur in nat **which through overexpression of the enzyme** can result in or contribute to antibiotic resistance to isoniazid."* |
| **ARO:3004910** | *"…catalyzes the transfer of the acetyl group… **Reports have shown** that overexpression of this enzyme **may be** responsible for increased resistance to isoniazid."* |

CARD **joins** mutation and overexpression on ARO:3004930 and never joins them on
ARO:3004910. So two configs: the joined record gets
`determinant --causally upstream of--> overexpression` from its own sentence, and the parent
gets **no incoming edge on that node at all**, because nothing supplies one.

The first version promoted **both** with the parent's sentence and then annotated ARO:3004930
with a "disagreement" its own definition refutes (#395). **That is #371 inverted** — every
prior instance was a record borrowing a relative's specificity; this one *discarded its own*.

## What is still not asserted

Isoniazid **is** a hydrazine, and CARD says NAT acts on *"arylamines and hydrazines"*. The
drug-inactivation mechanism is one step of chemical reasoning away — and CARD never takes it.
No edge makes isoniazid the substrate; **no config carries a drug edge at all.**

The first version did carry one, as `acetylation --RO:0002610--> drug0` whose **sole**
evidence was Pfam's *"NAT is also responsible for the inactivation of Isoniazid … in humans"*
— **inverting round 121's rule** that out-of-scope context may ride on an edge CARD supports
but may never be an edge's only evidence. And the test pinned that wrong shape (#396). The
weaker predicate hid the claim from the `has input`/`has output` ban without removing it from
the graph.

## Provenance

* records touched: **2** · SEEDED → REVIEWED
* `just lint`: passed · `just test`: **753 passed** (+4), run before the push
* corpus after: **350,267 nodes · 372,570 edges · 0 errors · 372,570/372,570 snippet-cited**
* `just validate` on both: 0 failures · `--verify`: 4 KB CURIEs, the split refusal firing by
  name, 0 problems · `just audit-fit`: 0
* drafts remaining: **190 → 188**

## Review

One round, **six findings, all filed (#395–#399 plus #393's correction), all addressed.**
The reviewer's verdict on the first version was **not mergeable**, and it was right:

* **#395** the record discarding its own definition for its parent's — #371 inverted;
* **#396** out-of-scope context as an edge's sole evidence, with a test pinning it;
* **#397** an `overexpression --positively regulates--> determinant` edge that was circular
  (overexpression *is* elevated abundance of the determinant, not a regulator of it),
  unsupported by any sentence, and left the node with no incoming edge;
* **#398** mech edges citing a sentence with no mutation claim;
* **#399** `GO:0008080` where `GO:0004060` (*arylamine N-acetyltransferase activity*) is the
  exact term, **already a KB record**, and whose definition literally states the
  `has input acetyl-CoA` claim the graph made separately.

## Review round 2: the fix for #398 introduced the defect #398 was about

Verdict on the round-1 output was **not mergeable**, on one finding.

**#400.** The #398 fix gave `mech` and `mech_res` the corrected *snippet* —
`ARO:3000212`'s own definition — and left the *attribution* alone. `promoted_graph_dict`
stamps `cfg["reference"]` on a bare-string snippet, so **4 evidence items shipped citing
ARO:3000212's definition under `reference: ARO:3004910` / `ARO:3004930`**, records whose own
definitions contain none of that text.

A corpus scan for that definition under a *self*-reference returns **exactly the 2 records
this round touched**; nothing else in 9,738 ARO resistance graphs does it. The base branch
was self-consistent. It is a regression, and it contradicts the fix's own stated rationale —
*"the mech edge is about ARO:3000212, so it carries ARO:3000212's own definition."* The
snippet moved; the attribution did not.

**That is the third round running in which a fix produced the defect it was fixing** —
#374→#382, #382→#387, #398→#400. Each time the fix was aimed at the finding's instance and
landed there; each time the *shape* re-emerged one field over.

**#401**: the two configs were not mutually exclusive. `ARO:3004930` passed **both**
preconditions and was selected only because the joined config came first in the list —
reordering would silently strip its `determinant → overexpression` edge with every gate
green. They now refuse each other's record **by name**.

**#402 is the one that matters beyond this round.** No test in the 755 pinned an evidence
`reference` — mutation-proven: flipping one leaves the suite green. **That is the blind spot
#348, #382 and #400 all slipped through, three attribution defects in three rounds.** There
is now a test that loads the emitted records and checks every ARO/Pfam/GO-cited snippet
against that record's own definition on disk. It is the config-scoped version of #365's
corpus-wide check.

## Two review rounds

| round | findings | filed | fixed |
|---|--:|--:|--:|
| 1 | 6 | 5 (#395–#399) + #393 closed invalid | 6 |
| 2 | 9 | 3 (#400–#402) | 3 |

Round 2 left six non-blocking findings filed or noted, including that
`test_nat_asserts_no_drug_edge_at_all` overclaims — both records **do** carry the promoter's
fixed `confers resistance to (drug class)` edge, and the test scans only `extra_edges`.

**Two rounds ran, against five in rounds 121–122**, which each found new defect classes as
late as round 4. This round should still be assumed under-reviewed.
