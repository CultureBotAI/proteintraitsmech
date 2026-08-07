---
topic: causal-graphs
round: 67
date: 2026-08-07
target: aro/FUNC_RESISTANCE — SMR efflux pumps (ARO:0010003), 12 records
prior_round: causal-graphs-round66.md
---

# Causal graphs — Round 67: the first efflux family that says what pays for it

Most efflux records in this corpus say only *"pumps the drug out"* — which restates the
phenotype rather than explaining it. **SMR is the first family whose own text gives the
energetics:**

> *"EmrE is a small multidrug transporter that functions as a homodimer and that couples
> the efflux of small polyaromatic cations from the cell **with the import of protons down
> an electrochemical gradient**."* — ARO:3000264

That is a proton antiport, and it is what makes efflux a *mechanism*: the drug does not
leave because the pump wants it to, it leaves because protons are coming in. The
`proton_gradient --causally upstream of--> antiport` edge exists to carry exactly that, and
a test pins it — an efflux graph without its driving force is a phenotype with arrows.

## Scope, as usual

The antiport sentence is **EmrE's**. The other eleven members (abeS and the rest) are named
as SMR-family transporters without their own coupling data, so the edge cites EmrE and its
`notes` say so. A test pins the scope note.

This is the seventh consecutive round where the honest handling of a snippet's *reach* —
not the finding of the snippet — was the substantive work.

## Provenance

* records touched: **12** · SEEDED → REVIEWED · 0 skipped
* `just test`: **635 passed** (+2) · `just validate` on all 12: **0 failures**
* `--verify`: 4 KB CURIEs checked, **0 problems, 0 near-misses**
* `GO:0015297` (antiporter activity) checked non-obsolete against OLS (#157)
* corpus: **371,746 edges · 0 errors · 371,746/371,746 snippet-cited**
* drafts remaining: **504 → 492**

## Open questions

* **The other ~49 efflux records under ARO:3000159** are the larger block and mostly lack
  this energetics detail. Whether to reuse SMR's antiport edge for them is a real question
  and the answer is probably no — RND and MFS pumps couple differently, and asserting a
  proton antiport for an ABC transporter would be flatly wrong.
* **The 67-record `antibiotic inactivation enzyme` group** remains the largest non-van
  block.
* **#270 (tet(M))** remains the only stranded curated record.
