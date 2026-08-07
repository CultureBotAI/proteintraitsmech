---
topic: causal-graphs
round: 35
date: 2026-08-07
target: aro/FUNC_RESISTANCE — MFS (13) and SMR (4) efflux subunits, 17 records
prior_round: causal-graphs-round34.md
---

# Causal graphs — Round 35: four machines under one family term

`ARO:3000748` now carries **four configs**, one per pump class, selected by the same
two-hop precondition. RND (round 33) and ABC (round 34) are done; this adds the two
remaining secondary transporters.

## Each class earns its own evidence by being a different machine

| class | how the substrate is taken | what drives it |
|---|---|---|
| RND (77) | captured from the **periplasm**, passed through a central cavity | proton gradient |
| ABC (14) | **no central cavity** — conformational change is conveyed across the membrane | ATP |
| **MFS (13)** | recognised **directly from the lipid bilayer** by inner-leaflet loops | secondary transport |
| **SMR (4)** | an **antiparallel homodimer** whose two states are the same structure in opposite orientations | secondary transport |

**MFS — Yin et al., Science 2006 (PMID:16675700):**

> *"Two long loops extend into the inner leaflet side of the cell membrane. This region can
> serve to recognize and bind substrate directly from the lipid bilayer."*

**SMR — Morrison et al., Nature 2011 (PMID:22178925):**

> *"…asymmetric antiparallel EmrE exchanges between inward- and outward-facing states that
> are identical except that they have opposite orientation in the membrane."*

The minimal transporter: alternating access achieved by *exchange* rather than by a large
conformational cycle. Four pumps, four genuinely different sentences — which is the case
for four configs rather than one "efflux" config with a shared snippet.

## Verified by construction, not assumed

```
17 written · 91 already curated by the RND/ABC configs · 31 refused
by config: {'MFS': 13, 'SMR': 4}
```

The per-config split was checked by reading back the written records' node sets, not
inferred from the run's counters.

## Two tests broke, and the reason is worth keeping

Both indexed `family_configs(...)` **positionally**, and the new configs went to the front.
One then matched the RND config by looking for `"RND"` in its `note` — which picked **MFS**,
whose note *mentions* RND to say it is distinct from it. Both now select on a structural
marker (`binding_pocket`, `atp_cycle`). Matching prose to identify a thing is the same
mistake as #199, in a test rather than in the promoter.

## Provenance

* records touched: **17** (13 MFS + 4 SMR) · SEEDED → REVIEWED · 31 refused
* corpus after: **39,647 records · 40,115 graphs · 348,683 nodes · 370,460 edges ·
  0 errors · 370,460/370,460 edges snippet-cited**
* warnings 6,437 → **6,471**: +34, two ungrounded nodes per record
* `just validate` on all 17 individually: **0 failures** · `verify-all`: 48 families, 0 problems
* drafts remaining: **899 → 882**

## Open questions

* **The 31 still-refused efflux drafts have no `part_of` complex at all**, so no class
  precondition can see them. They need individual checking — some are likely complexes
  rather than subunits, which is a categorisation question for `review-source-categories`
  rather than a curation one.
* **Grounding `export` to a GO transmembrane-transport term** would now clear one ungrounded
  node from **108 records across four configs** in a single edit. This is the cheapest
  warning reduction available anywhere in the corpus.
