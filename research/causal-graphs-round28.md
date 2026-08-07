---
topic: causal-graphs
round: 28
date: 2026-08-06
target: aro/FUNC_RESISTANCE — inhA (ARO:3003417), 5 records
prior_round: causal-graphs-round27.md
---

# Causal graphs — Round 28: inhA, two resistance routes on one determinant

Round 27 curated katG, which makes isoniazid work. This is what the activated drug hits —
and the first family in this thread whose records carry **two different resistance routes**,
both demonstrated in the same 1994 paper.

## One paper, two experiments, two mechanisms

**Banerjee et al., Science 1994 — PMID:8284673**

| route | verbatim |
|---|---|
| **target alteration** | *"A missense mutation within the mycobacterial inhA gene was shown to confer resistance to both INH and ethionamide (ETH) in M. smegmatis and in M. bovis."* |
| **titration by overexpression** | *"The wild-type inhA gene also conferred INH and ETH resistance when transferred on a multicopy plasmid vector to M. smegmatis and M. bovis BCG."* |

The second is the more surprising result and the one worth having in a graph: **the
wild-type gene confers resistance when there is simply more of it.** No change to the
protein, no alteration of the binding site — just more target than the activated drug can
modify. That is why promoter substitutions upstream of *inhA* (in the *fabG1-inhA* operon)
are resistance alleles without touching a coding sequence, and the edge's `notes` say so.

Both routes are separate edges with their own evidence. A record showing only one would
misdescribe half the clinical alleles.

## It joins up with round 27

The `inh_nad → inha_activity` inhibition edge cites Rozwarski 1998, and its `notes` record
that the inhibitory species exists **only because katG activated the prodrug** — curated on
`ARO:3004266` one round earlier. Rounds 27 and 28 are the two halves of one drug's story:
the enzyme that switches isoniazid on, and the enzyme it switches on *against*.

## Provenance

* records touched: **5** · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,188 nodes · 369,864 edges ·
  0 errors · 369,864/369,864 edges snippet-cited**
* warnings 6,064 → **6,069**: +5, one ungrounded adduct node per record
* `just validate` on all 5 individually: **0 failures**
* drafts remaining: **1,080 → 1,075**

## Open questions

* **fabG1 (7) is the natural next record set and was deliberately not bundled.** Its claim —
  that promoter substitutions in the *fabG1-inhA* operon raise InhA levels — is the
  mechanism this round's overexpression edge *predicts*, but the paper demonstrating it in
  M. tuberculosis was not found by this round's searches (the PMID tried returned an
  unrelated polyphosphate-kinase paper). Stretching Banerjee's multicopy-plasmid result to
  cover chromosomal promoter alleles would be exactly the over-reach #201 exists to stop.
* **ethA (9)** remains in the same position, for the same reason (round 27).
* **A sixth mechanism kind is now in the corpus:** titration by target overexpression. It
  is likely to recur — several efflux and target-duplication records in the 565 label-only
  tail will be this shape rather than target alteration.
