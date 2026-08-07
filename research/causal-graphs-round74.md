---
topic: causal-graphs
round: 74
date: 2026-08-07
target: aro/FUNC_RESISTANCE — alm glycylation (ARO:3003580), 5 records
prior_round: causal-graphs-round73.md
---

# Causal graphs — Round 74: a third way to neutralise lipid A, and a relay

ARO:3003580 now carries **three** charge-alteration routes: L-Ara4N addition,
phosphoethanolamine addition (round 73), and **glycylation** — *Vibrio cholerae*'s almEFG
system. All three attach a different group to lipid A and all three share ARO:3003588's
causal sentence: cationic antimicrobials *depend on* the negative charge, so neutralising
it is the resistance.

## The relay is why the predicate is not "enables"

> *"Its mechanism involves transfer of a glycyl molecule to the carrier protein **almF** by
> **almE**, followed by glycylation of lipid A by **almG**."* — ARO:3007434

Three named roles in order. **No single record performs the route**, so the determinant
edge is `participates in` (RO:0000056) rather than `enables` — almE charges the carrier,
almG does the transfer, almF is the carrier. Using `enables` would claim each protein
does the whole job.

## The operon record is deliberately left as a draft

**ARO:3007434 is the almEFG operon itself**, and it is also the best mechanism source for
the five protein records — they cite it. Curating it would pre-empt the open question of
whether a gene cluster should carry a protein-trait causal graph, which is the same
question blocking the van set. The precondition refuses it with that reason stated, and a
test pins the refusal.

Citing a record while declining to curate it is the honest position here: its *definition*
is evidence, its *modelling* is undecided.

## A config-count assertion broke for the fourth time

Round 73's test asserted `len(cfgs) == 2`; this round's third config broke it. After #235
and rounds 35, 48 and 68 — **and I nearly wrote a fifth** (`== 3`) in this round's own
test before catching it. Both now select on node labels.

**Six such assertions remain in the suite.** Filed as **#288** rather than swept at the end
of a long session.

## Provenance

* records touched: **5** · SEEDED → REVIEWED · the operon record left as a draft
* `just test`: **649 passed** (+2) · `just validate` on all 5: **0 failures**
* `--verify`: **0 problems, 0 near-misses**
* corpus: **371,981 edges · 0 errors · 371,981/371,981 snippet-cited**
* drafts remaining: **420 → 415**

## Open questions

* **#288** — six remaining config-count assertions, each a latent version of the same break.
* **10 charge-alteration drafts remain**, mostly the arn/Ara4N proteins that the existing
  L-Ara4N config refuses; worth checking whether its precondition is too narrow rather
  than assuming they need a fourth config.
