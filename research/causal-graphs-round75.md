---
topic: causal-graphs
round: 75
date: 2026-08-07
target: aro/FUNC_RESISTANCE — Ara4N addition (ARO:3003580), 4 records
prior_round: causal-graphs-round74.md
---

# Causal graphs — Round 75: the route I twice said was already done

## The error

Rounds 73 and 74 both described ARO:3003580's pre-existing config as **"the L-Ara4N
config"**, and positioned their own work as adding routes *alongside* it. That was wrong
in two merged reports and in the config comments.

The pre-existing config is **mprF / lysyl-phosphatidylglycerol**. **Ara4N had no config at
all** — which is exactly why arnA, ArnT, PmrE and PmrF were still drafts after two rounds
that claimed to be filling in around them.

I only found it by doing what round 74's own report recommended: checking whether the
existing precondition was too narrow *before* assuming a fourth config was needed. The
refusal reasons said `"this determinant is not mprF"` — visible in one command, and
contradicting what I had written twice.

**This is the fourth distinct kind of mistake this session that a stated reason would have
caught if I had read it**: false skip reasons (#252), too-narrow patterns (#264), a
sibling-accepted near-miss dismissed (round 69→73), and now a config I named without
checking.

## What landed

4 records — arnA, ArnT, PmrE (ugd), PmrF — and the mislabelled comments corrected in the
same commit.

The determinant edge is `participates in`, following round 74's reasoning: CARD says PmrF
is *"required for the **synthesis and transfer**"*, and these records are different steps
(PmrE/ugd synthesise, ArnT transfers). No one of them performs the route.

ARO:3003580 now carries **four** surface-charge routes: mprF lysyl-PG, phosphoethanolamine,
glycylation, Ara4N.

## Provenance

* records touched: **4** · SEEDED → REVIEWED
* `just test`: **649 passed** · `just validate` on all 4: **0 failures**
* corpus: **0 errors · all edges snippet-cited**
* drafts remaining: **415 → 411**

## Open questions

* **6 charge-alteration drafts remain**: the family term, the almEFG operon (both correctly
  refused), a two-component regulator (cprRS), and three other lipid A modifications
  (acyltransferase, phosphatase, pgpB) that each need their own reading.
* **#287** — six config-count assertions still latent.
