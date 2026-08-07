---
topic: causal-graphs
round: 34
date: 2026-08-07
target: aro/FUNC_RESISTANCE — ABC efflux subunits (ARO:3000748, ABC complexes), 14 records
prior_round: causal-graphs-round33.md
---

# Causal graphs — Round 34: the same family term, a different machine

Round 33 curated 77 RND efflux subunits and left 62 refused by its class precondition.
This takes the ABC ones — the **same ARO family term**, and a genuinely different pump.

## Why reusing round 33's evidence would have been wrong

RND runs on the **proton gradient** and passes substrate through a **central cavity**.
Crow, Greene, Kaplan & Koronakis, PNAS 2017 (**PMID:29109272**) on MacB:

> *"The MacB transmembrane domain **lacks a central cavity** through which substrates could
> be passed, but instead conveys conformational changes from one side of the membrane to
> the other, a process we term mechanotransmission."*

> *"Comparison of ATP-bound and nucleotide-free states reveals how reversible dimerization
> of the nucleotide binding domains drives opening and closing of the MacB periplasmic
> domains…"*

Both are tripartite — transporter, adaptor, exit duct — and there the similarity stops.
Attaching round 33's proton-antiport, central-cavity evidence to these 14 records would
assert the wrong energetics **and** the wrong route for the substrate.

## Two configs under one family term

This is the second use of #208's multiple-configs-per-family, and the first where both
configs are for the *same* determinant type distinguished only by their machine. The
selector is the class precondition from round 33:

```
verify ARO:3000748 (RND config): 139 candidates,  62 precondition skips
verify ARO:3000748 (ABC config): 139 candidates, 124 precondition skips
apply:  14 written · 77 skipped (already curated by the RND config) · 48 refused
```

`_requires_rnd_pump` was generalised to `_requires_pump_class(class_id, human)` when the
second class needed the identical two-hop walk — four copies of the same lookup is the
standing lesson of #93, and MFS and SMR still to come would have made it four.

## Provenance

* records touched: **14** · SEEDED → REVIEWED · 48 refused by precondition
* corpus after: **39,647 records · 40,115 graphs · 348,649 nodes · 370,422 edges ·
  0 errors · 370,422/370,422 edges snippet-cited**
* warnings 6,395 → **6,437**: +42, three ungrounded nodes per record
* `just validate` on all 14 individually: **0 failures**
* drafts remaining: **913 → 899**

## Open questions

* **MFS (13) and SMR (4) remain**, and are now trivial to scope: the same
  `_requires_pump_class` with `ARO:0010002` / `ARO:0010003`, plus a paper each. Both are
  secondary transporters like RND, so their evidence should describe proton antiport rather
  than being borrowed from either curated config.
* **~31 efflux drafts have no `part_of` complex at all** and so are invisible to every class
  precondition. They need checking individually — some may be complexes rather than
  subunits, which would be a categorisation question rather than a curation one.
* **The ungrounded-node ratio is unchanged from round 33** (three per record). Grounding
  `export` to a GO transmembrane-transport term would fix it across all four pump classes at
  once and is worth doing before MFS and SMR add more.
