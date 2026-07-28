---
date: 2026-07-28
issue: "#7 follow-up — what the protein map should be built from"
---

# The protein map was 44% GO, and it was measurably worse for it

The protein map positions each Swiss-Prot protein by the corpus traits it
carries. It was built from *every* corpus trait the protein has — signatures
(Pfam / InterPro / CDD / PROSITE / CATH / NCBIfam …) **and** GO/EC annotations.
By vocabulary that made it **44% GO/EC**: 15,613 of 35,507 features.

That is the confound phases 6, 9 and 14 each ran into from a different angle: GO
density tracks curation effort, not biology. Mouse averages **16.1** GO terms to
human's **12.6** — the effect that forced within-proteome normalisation on the
exemplar ranking, because absolute GO counts were handing every pick to whichever
community annotates hardest.

`cluster_trait_families.py` excluded GO/EC from the start for exactly this
reason. The map did not. That inconsistency was never deliberate — the two were
written five phases apart.

## Measured both ways

Neighbour purity at k=25, in the 50-d SVD space, against the purity expected from
label proportions:

| feature space | features | proteins | organism | CATH class |
|---|--:|--:|--:|--:|
| signatures + GO/EC | 35,507 | 78,296 | 2.27× | 2.34× |
| **signatures only** | 19,894 | 75,714 | **1.86×** | **3.12×** |

Removing GO/EC cuts organism purity by **18%** and raises structural-class purity
by **33%**. Both move in the direction the confound predicts: GO was carrying
organism-specific annotation practice into the geometry and diluting the
structural signal the map exists to show.

Cost: 2,582 proteins (3.3%) drop out because their only corpus traits were GO/EC.
That is the right outcome rather than a loss — a protein with no signature trait
has no architecture to place on an architecture map.

## This partly reinstates a claim phase 9 withdrew

Phase 8 reported that structural class organises the protein map more strongly
than organism does. Phase 9 withdrew it: on ten organisms the gap had closed to
2.34× versus 2.27×, essentially equal, and the withdrawal was correct **for the
feature space then in use**.

On signature-only features the gap is **3.12× versus 1.86×** — structure clearly
dominates again. So the honest position is narrower than either previous one:

* Phase 8's claim was directionally right but rested on a 4-organism sample, two
  of them mammals.
* Phase 9's withdrawal was right about that sample, and was measured on a feature
  space that was itself 44% annotation practice.
* With the confound removed and ten organisms in place, structure organises the
  map about **1.7×** more strongly than organism.

Three measurements, each correct about its own inputs. The claim only stabilised
once the inputs stopped carrying a confound nobody had checked for.
