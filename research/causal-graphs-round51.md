---
topic: causal-graphs
round: 51
date: 2026-08-07
target: aro/FUNC_RESISTANCE — fabG1 (ARO:3004887), 7 records
prior_round: causal-graphs-round50.md
---

# Causal graphs — Round 51: fabG1, and the blocker that was a claim nobody made

Round 50 unblocked #217 by fixing the *query shape* — the paper existed, my search
didn't match how it was titled. I closed #217 recommending the same technique for
**#219 (fabG1)**, blocked across three attempts on the same kind of claim.

**The technique did not work here, and that is the finding.** #219 was not a search
failure. It was a curation error one level up.

## What #219 was blocked on

That a *fabG1/mabA promoter substitution raises inhA expression* — the C-15T story,
real and well documented. Three rounds of searching failed to pin a verbatim snippet
stating the expression step. This round searched a fourth way (by title shape:
`TITLE:"inhA promoter"`), which surfaced only clinical-epidemiology papers:

> *"Resistance to isoniazid is typically caused by mutations in either katG or the
> inhA promoter. inhA mutations confer low-level resistance to isoniazid and
> cross-resistance to ethionamide…"* — PMID:26332235

That is the **phenotype association**, not the expression mechanism. Still blocked.

## The actual resolution: read what the source claims, not what you know

Re-reading CARD's own definitions for these 7 records:

> *"Mutations that occur in the fabg1 gene resulting in the inability for the
> antibiotic to inhibit mycolic acid biosynthesis."* — ARO:3004887
>
> *"fabG1 is involved in the fatty acid synthesis pathway, acting in the first
> reduction step for mycolic acid. It is associated with isoniazid resistance."*
> — ARO:3004895

**CARD never asserts the promoter mechanism.** It describes fabG1 as a FAS-II enzyme
whose mutation stops the drug inhibiting the pathway — **target alteration**, the
round 18–19 shape, and curatable from the source's own words all along.

I spent three attempts sourcing a claim the records do not make, because I knew the
promoter story and assumed the records were about it. The block was never in the
literature; it was that I never checked whether my mechanism was the source's.

## What is deliberately *not* asserted

The promoter/overexpression arm is **absent on purpose**, and the config and the
edge `notes` say so in as many words rather than leaving its absence to look like an
oversight. If someone later evidences the C-15T expression step, it is an added arm,
not a correction.

The pathway edge borrows **PMID:8284673** (Banerjee et al. 1994) from round 28 for
context only — it studied **InhA**, the *next* step, and the `notes` state that
rather than letting the citation imply it covered FabG1:

> *"The InhA protein shows significant sequence conservation with the Escherichia
> coli enzyme EnvM, and cell-free assays indicate that it may be involved in mycolic
> acid biosynthesis."*

## Graph

```
determinant --enables-->                fas_step (first reduction step, ungrounded)
fas_step --part of [BFO:0000050]-->     mycolic (GO:0071768)
drug0 --causally upstream of-->         inhibition        ← the drug's normal action
determinant --negatively regulates-->   inhibition        ← the causal core, CARD's words
```

**6 of 7 records carry the `drug0` edge; the 7th does not** — `antibiotic-resistant-fabg1`
is drug-agnostic and has no drug node, so #201's endpoint guard dropped that edge
rather than writing a dangling reference. That is the guard doing its job on a
record I would not have singled out by hand.

## What the review caught

The `drug0 --> inhibition` edge originally cited ARO:3004887 — a sentence about the
**mutation** — to support the claim that the drug **normally** inhibits the pathway. The
claim follows from the snippet, but the snippet does not state it, and the `notes` said
"Implied by what the mutation prevents". Filed as **#250** and fixed here: it now cites
**PMID:1656850** (*Isoniazid inhibition of mycolic acid synthesis by cell extracts*),
which states it directly.

Then the corpus-wide version of the question, measured instead of assumed: 2,878 `notes`
match hedge phrases, but **2,871 are M-CSA notes describing M-CSA's own role-typing**, not
our citation strength. The only two genuine matches are this fix's own note and one
statement about efflux biology. **The pattern was unique to this edge** — one found defect
did not imply a class of them, and checking cost less than the sweep would have.

## Provenance

* records touched: **7** · SEEDED → REVIEWED · evidence items: **67**
* `just test`: **594 passed** (+2)
* corpus after: **39,647 records · 40,115 graphs · 349,166 nodes · 371,133 edges ·
  0 errors · 371,133/371,133 edges snippet-cited**
* `just validate` on all 7 individually: **0 failures**
* `--verify`: 3 KB CURIEs checked, 0 precondition skips, 0 uncovered mechanisms, 0 problems
* drafts remaining: **679 → 672**

## Open questions

* **The generalisable lesson is not round 50's.** Round 50: *"no paper exists" often
  means "my query shape is wrong."* Round 51: **before searching at all, check whether
  the mechanism you are trying to evidence is the one the source asserts.** The second
  is cheaper and would have saved three rounds. Both belong in the skill.
* **This is worth a sweep, not a note.** Any other blocked family may be blocked the
  same way — me sourcing a better-known mechanism than the one CARD states. The
  remaining blocked items (#229's 10 ini-operon records, the 23 two-component pair
  records) should each be re-read against their own definitions *first*.
* **`fas_step` is ungrounded** — the FabG1/MabA ketoacyl-reductase step has no term in
  use here. Unlike the QRDR and pentapeptide gaps (rounds 18–21), this is one node per
  record, not enough to price a term request.
