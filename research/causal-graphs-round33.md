---
topic: causal-graphs
round: 33
date: 2026-08-06
target: aro/FUNC_RESISTANCE — RND efflux subunits (ARO:3000748, RND complexes only), 77 records
prior_round: causal-graphs-round32.md
---

# Causal graphs — Round 33: efflux, and #223 was wrong about the hierarchy

A **ninth** mechanism kind, the largest family this thread has curated, and a correction to
an issue I had filed an hour earlier.

## #223 said this could not be a family round

It reported that all 137 efflux-subunit drafts sit flat under `ARO:3000748` with only three
shared ancestors, so one config would span RND, MFS, ABC, SMR and MATE at once — and
recommended per-record curation unless the seeder could recover CARD's gene families.

**That was true of the subunits and false of their complexes.** Each subunit carries
`relationship: part_of` a pump complex, and the *complex* is classified:

```
ARO:3000384 AcrAB-TolC   is_a  →  resistance-nodulation-cell division (RND) antibiotic efflux pump
ARO:3000770 AdeABC       is_a  →  RND …
ARO:3004076 MuxABC-OpmB  is_a  →  RND …
```

So the pump class is **two hops away and fully derivable from the release**. `_requires_rnd_pump`
does that lookup — subunit → `part_of` complex → is it `is_a` `ARO:0010004`? — which is why
this is a precondition rather than the hand-maintained name list #223 warned against. It
admitted 77 records and **refused 62**.

The lesson is narrow and reusable: *"the hierarchy does not group these"* was measured on
`is_a` only. ARO puts real structure in `relationship:` too, and one more query would have
found it before the issue was filed.

## Murakami et al., Nature 2006 — PMID:16915237

> *"AcrB is a principal multidrug efflux transporter in Escherichia coli that cooperates
> with an outer-membrane channel, TolC, and a membrane-fusion protein, AcrA."*

> *"Bound substrate was found in the periplasmic domain of one of the three protomers. The
> voluminous binding pocket is aromatic and allows multi-site binding."*

> *"The structures indicate that drugs are exported by a three-step functionally rotating
> mechanism in which substrates undergo ordered binding change."*

Multi-site binding in an aromatic pocket is what lets one pump handle chemically unrelated
drugs — the fact that makes efflux a *multidrug* mechanism rather than a drug-specific one,
so it is its own edge.

**A subunit is not the pump.** RND resistance is a property of a three-part machine, so the
graph says the determinant is `part of` a complex rather than making the subunit the whole
pump. Which complex is on each record's own ARO relations.

## The mechanism guard caught one more

`ARO:3005040` (YajC) carries `ARO:3000384` — a *complex* id — where a mechanism id belongs.
The guard refused it rather than substituting, so 76 of 77 were written and that one stays a
draft. Worth a look: a complex used as a mechanism is probably an ARO modelling quirk rather
than something this corpus should reproduce.

## Provenance

* records touched: **77** · SEEDED → REVIEWED · 62 refused by precondition, 1 by the guard
* corpus after: **39,647 records · 40,115 graphs · 348,607 nodes · 370,380 edges ·
  0 errors · 370,380/370,380 edges snippet-cited**
* warnings 6,164 → **6,395**: +231, three ungrounded nodes per record (the complex, the
  binding pocket and the export process — none has an ontology term)
* `just validate` on all 77 individually: **0 failures**
* drafts remaining: **990 → 913**

## Open questions

* **The 62 refused records are MFS, ABC, SMR and MATE pumps**, each a smaller round with its
  own energetics. The same two-hop precondition works for them — only the class id and the
  paper change.
* **Three ungrounded nodes per record is the worst ratio so far** (+231 warnings for 77
  records). GO has transmembrane-transport terms that would ground `export`; that would cut
  it by a third and is worth doing before the remaining pump classes repeat it.
