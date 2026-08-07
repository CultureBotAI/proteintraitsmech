---
topic: causal-graphs
round: 26
date: 2026-08-06
target: aro/FUNC_RESISTANCE — rifamycin-resistant rpoB (ARO:3000210), 11 records
prior_round: causal-graphs-round25.md
---

# Causal graphs — Round 26: rpoB, the same shape as gyrA on a different target

Round 18's gyrA established target alteration: a short conserved region of the drug's
target, substituted, and the drug binds less well. rpoB is that shape again — the
rifampicin resistance-determining region — and it is the first round to leave the van set.

## Two papers, eight years apart, and neither is sufficient alone

**Telenti et al., Lancet 1993 — PMID:8095569** defined the region, with a control:

> *"Mutations involving 8 conserved aminoacids were identified in 64 of 66
> rifampicin-resistant isolates of diverse geographical origin, but in none of 56 sensitive
> isolates. All mutations were clustered within a region of 23 aminoacids."*

*"but in none of 56 sensitive isolates"* is what makes this a case-control result rather
than an observation, and it is quoted rather than paraphrased for exactly that reason.

**Campbell et al., Cell 2001 — PMID:11290327** showed why those residues matter:

> *"The inhibitor binds in a pocket of the RNAP beta subunit deep within the DNA/RNA
> channel, but more than 12 A away from the active site."*

> *"…the inhibitor acts by directly blocking the path of the elongating RNA when the
> transcript becomes 2 to 3 nt in length."*

The 1993 paper knows *where* resistance substitutions fall and not why; the 2001 structure
knows where the drug sits and not which substitutions matter clinically. The `rrdr part_of
domain` edge carries **both**, with a note saying the containment is an inference from the
two together — the same discipline as round 18's QRDR edge.

**The mechanism is allosteric, and the graph says so.** The pocket is >12 Å from the
catalytic site, so rifampicin obstructs the nascent transcript's path rather than the
chemistry — which is why it blocks initiation once the transcript reaches 2–3 nt rather
than stopping elongation in progress. A graph that only said "drug inhibits enzyme" would
lose the part that explains the drug's clinical behaviour.

## Both mechanism ids needed snippets

These records carry **two** — `ARO:0001002` and `ARO:3000212`. The `UncoveredMechanism`
guard (#203) refuses to substitute one mechanism's evidence for another, so both had to be
written. Before that guard existed this round would silently have cited one for both.

## The #196 check caught this round's own config

The first draft cited the InterPro abstract sentence *"This domain forms one of the two
distinctive lobes of the Rpb2 structure"* as part-of evidence, and
`just verify-family-drafts` flagged it: the sentence never names the polymerase, so it does
not establish that an rpoB determinant has this domain. Replaced with a quote that does,
plus a note that Rpb2 is the structural name for the beta subunit. **A guard written for a
27-family backlog earned its keep on brand-new work within the hour.**

## Provenance

* records touched: **11** · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,143 nodes · 369,804 edges ·
  0 errors · 369,804/369,804 edges snippet-cited**
* warnings 6,032 → **6,054**: +22, the RRDR and binding-pocket nodes
* `just validate` on all 11 individually: **0 failures**
* drafts remaining: **1,096 → 1,085**

## Open questions

* **The other rpo* records are different drugs, not different organisms** — daptomycin-
  and vancomycin-resistant rpoB/rpoC sit under different ARO parents, and their mechanisms
  are not the RRDR story. `ARO:3003090`, `ARO:3003290`, `ARO:3004725` and their children
  need their own evidence, and for daptomycin/vancomycin via RNA polymerase that evidence
  may be thin enough that the honest outcome is leaving them as drafts.
* **`rpoA` and `rpoC` rifampicin records exist** (`ARO:3004998`, `ARO:3004995`) — compensatory
  or secondary substitutions rather than the primary target, which is a different claim
  and should not reuse this config.
* **Next by size:** the isoniazid/ethionamide set (katG, ahpC, fabG1, ethA, mshA/mshC —
  ~40 records), where the mechanism is prodrug activation rather than target alteration.
