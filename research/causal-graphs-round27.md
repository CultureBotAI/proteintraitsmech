---
topic: causal-graphs
round: 27
date: 2026-08-06
target: aro/FUNC_RESISTANCE — katG (ARO:3004266), 5 records
prior_round: causal-graphs-round26.md
---

# Causal graphs — Round 27: katG, and resistance by *losing* a function

A fifth kind of mechanism, and the first that is **not something the determinant does**:

| rounds | kind |
|---|---|
| 12–16 | inactivation — the enzyme destroys the drug |
| 18–19, 26 | target alteration — the target binds the drug less well |
| 20–21, 23 | precursor depletion / substitution |
| 22, 24 | regulation — it switches on the genes that do |
| **27** | **prodrug activation loss — the determinant *fails* to turn the drug on** |

Isoniazid is inert as administered. KatG's peroxidase activity converts it to the species
that inhibits InhA. A katG that has lost that activity leaves the drug inert — so the
graph's causal core is a **negative** regulation *by* the determinant of a step it would
otherwise perform. The node labels say "defective" rather than leaving a reader to infer
it.

## Both directions, from one 1992 paper

**Zhang, Heym, Allen, Young & Cole, Nature 1992 — PMID:1501713**

> *"A single M. tuberculosis gene, katG, encoding both catalase and peroxidase, restored
> sensitivity to INH in a resistant mutant of Mycobacterium smegmatis, and conferred INH
> susceptibility in some strains of Escherichia coli."*

> *"Deletion of katG from the chromosome was associated with INH resistance in two patient
> isolates of M. tuberculosis."*

**Gain restores sensitivity; loss confers resistance** — and the gain was shown in two host
species. Having both directions from the same experiment set is what makes this causal
rather than correlative, and both are on the `determinant → resistance` edge (#190's
two-item form).

## The downstream, from 1998

**Rozwarski et al., Science 1998 — PMID:9417034** identifies what the activated drug does:

> *"…covalent attachment of the activated form of the drug to the nicotinamide ring of
> nicotinamide adenine dinucleotide bound within the active site of InhA."*

The 1992 paper knows katG makes the drug work and not what the product is; the 1998 paper
knows the inhibitory species and calls it only "the activated form of the drug". The
`peroxidase → activated_inh` edge carries **both** and says in its `notes` that katG being
the activator is an inference from the two together — the same discipline as the QRDR and
RRDR edges.

## An honest caveat on the causal-core edge

Its evidence is a **deletion**, which is the extreme case of loss. Clinical katG resistance
substitutions (S315T above all) *reduce* rather than abolish activity. The edge's `notes`
say so, because a reader who took "deletion confers resistance" as the mechanism of every
katG resistance allele would be wrong about the commonest one.

## Provenance

* records touched: **5** · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,173 nodes · 369,839 edges ·
  0 errors · 369,839/369,839 edges snippet-cited**
* warnings 6,054 → **6,064**: +10, the two ungrounded intermediate nodes per record
* `just validate` on all 5 individually: **0 failures**
* drafts remaining: **1,085 → 1,080**

## Open questions

* **ethA (9 records) is the same mechanism kind and was deliberately not bundled.** Its
  primary characterisation was not findable in the searches this round ran — what surfaced
  was recent work on *boosters* (MymA, VirS, alpibectir) rather than EthA's own
  monooxygenase characterisation. It needs its own round with the right paper, not this
  round's evidence stretched to cover it.
* **fabG1/inhA (12 records) are a different mechanism again** — promoter substitutions that
  *overexpress* the target and titrate the drug, rather than failing to activate it. They
  must not reuse this config.
* **The remaining ~40 isoniazid-related genes are mostly 1–2 record chains** (ndh, nudC,
  mshA/B/C, nat, furA, sigI, iniA, mymA, Rv0565c, inbR, kasA, mmaA3, Rv1258c). Several have
  thin or contested evidence for their role in resistance; the honest outcome for some will
  be that they stay drafts.
