---
date: 2026-07-26
issue: "#7 — broaden the tree, and test what the corpus map shows"
prior: swissprot-trait-profiles-8.md
---

# Swiss-Prot trait profiles — Phase 9: ten organisms, and a phase-8 claim withdrawn

Two items: the matrix's standing limitation (four organisms, two of them mammals)
and the untested assumption behind the corpus map. Both turned out to change a
previously reported conclusion.

## 1. The matrix now spans the tree

`just build-profiles --organisms --limit 25000 --jsonl-only --apply` →
**80,066 proteins across 10 proteomes**, vertebrate share **76% → 47%**.

| organism | proteins | clade |
|---|--:|---|
| *Homo sapiens* | 20,431 | mammal |
| *Mus musculus* | 17,267 | mammal |
| *Arabidopsis thaliana* | 16,419 | plant |
| *Saccharomyces cerevisiae* | 6,733 | fungus |
| *Caenorhabditis elegans* | 4,488 | nematode |
| *Escherichia coli* K-12 | 4,531 | Gram-negative bacterium |
| *Bacillus subtilis* 168 | 4,191 | Gram-positive bacterium |
| *Drosophila melanogaster* | 3,899 | insect |
| *Methanocaldococcus jannaschii* | 1,786 | **archaeon** |
| *Plasmodium falciparum* 3D7 | 321 | apicomplexan parasite |

Corpus trait classes observed: 70,446 → **83,583**.

### The held-out test finally has something to hold out

Phase 6 could only ask whether human-mined rules survive in a second mammal, a
fungus and one bacterium — and measured mouse as indistinguishable from a random
split. Across the full tree the two rule families separate much more sharply
(`research/rule-generalization-2.md`):

| held-out organism | seq-encodes-fold | trait-implies-function |
|---|--:|--:|
| *Mus musculus* | 99% | 88% |
| *Arabidopsis thaliana* | 98% | 86% |
| *Drosophila melanogaster* | 96% | 88% |
| *Saccharomyces cerevisiae* | 96% | 86% |
| *Caenorhabditis elegans* | 96% | 81% |
| *Escherichia coli* | 96% | 81% |
| *Bacillus subtilis* | 91% | 70% |
| *Methanocaldococcus jannaschii* | **100%** | **59%** |
| *Plasmodium falciparum* | **100%** | 100% |
| **aggregate** | **97.2%** (1,004/1,033) | **84.8%** (758/894) |

**Sequence→fold rules mined in human hold in an archaeon.** 11 of 11 testable, and
8 of 8 in an apicomplexan parasite — small numbers, but there is no degradation
with phylogenetic distance at all. Function rules degrade exactly as distance
grows, bottoming out at **59% in the archaeon**. Phase 6 saw a hint of this across
three close relatives; across three domains of life it is unambiguous.

The overlay was re-mined on the wider matrix: **1,479 → 2,590 edges**
(seq-encodes-fold 771 → 1,279, with 1,045 at conf ≥0.99).

## 2. Withdrawing a phase-8 conclusion

Phase 8 reported that on the protein map "structural class organises the space
about 1.6× more strongly than organism does" — 2.29× versus 1.42× — and concluded
the trait profiles carry structure that survives the species boundary. Re-measured
on ten organisms:

| labels | 4 organisms (phase 8) | 10 organisms |
|---|--:|--:|
| CATH structural class | 2.29× | **2.34×** |
| organism | 1.42× | **2.27×** |

**Organism catches up almost exactly.** Structural class barely moves; organism
nearly doubles. The claim that structure dominates does not survive a
representative sample of the tree.

The obvious objection is that the organism label went from 4 classes to 10, which
changes the chance baseline. So the controlled version — take the *same four
organisms* back out of the ten-organism matrix and re-measure:

| | organism | CATH class |
|---|--:|--:|
| same 4 organisms, re-extracted | 1.42× | 2.29× |
| all 10 organisms | 2.27× | 2.34× |

The four-organism numbers reproduce phase 8 **exactly**. The measurement was
right; the *generalisation* was wrong. Two mammals plus a fungus plus one
bacterium made organism look like a weak organiser because human and mouse
proteins are nearly interchangeable at this resolution. Add an archaeon, a plant
and a parasite and proteome membership becomes as predictive as fold class.

Corrected statement: **on a representative sample of the tree, structural class
and organism organise the protein map about equally** (2.34× vs 2.27×).

## 3. What the corpus map actually shows

`docs/map.html` colours the trait-corpus map by axis, which presents axis as the
structure the embedding found. Never tested. `just measure-map`
(`research/map-structure-1.md`):

| space | label | purity | chance | lift |
|---|---|--:|--:|--:|
| embedding | trait axis | 0.943 | 0.342 | 2.76× |
| embedding | **source database** | 0.803 | 0.083 | **9.68×** |
| 2-d map | trait axis | 0.962 | 0.342 | 2.81× |
| 2-d map | source database | 0.761 | 0.083 | 9.17× |

Source looks far stronger — but that comparison is weak on its own, because
`source` has 28 classes to `axis`'s 5 and only **3 of 28 sources emit more than
one axis**, making source nearly a refinement of axis. The sharp test is
conditional: *within* one axis, where the map paints every point the same colour,
do neighbourhoods still sort by database?

| axis | records | source purity | chance | lift |
|---|--:|--:|--:|--:|
| STRUCTURE | 11,265 | **0.991** | 0.300 | 3.31× |
| FUNCTION | 16,330 | 0.894 | 0.156 | 5.75× |
| SEQUENCE | 12,393 | 0.596 | 0.221 | 2.69× |

Within STRUCTURE, **99% of a record's 25 nearest neighbours come from the same
database** — checked at 12k, 40k, 100k and the full 344,797 (0.991 → 0.997), so
this is not a sampling artefact. A reader seeing clean blobs on the corpus map is
substantially looking at databases.

### But the embedding is not blind across sources

That reads as damning and would be over-read without its counter-test. Taking
pairs already known to be cross-source equivalent and querying the **whole**
corpus:

| | full-record | definition-only |
|---|--:|--:|
| partner ranked #1 | **68.1%** | 70.5% |
| partner within top-25 | 94.7% | 93.4% |
| of those 25, share same-source | 49.7% | 42.2% |

So where a genuine cross-source equivalent exists, it is usually the single
nearest neighbour in the corpus. Same-source neighbourhoods are mostly an
artefact of most records having **no counterpart in another database** — their
neighbourhoods fill with same-source records by default. Both facts are true and
neither alone is the story; the script now reports them together for that reason.

One negative result worth recording: the definition-only embedding exists to
isolate "pure definition semantics" from identifiers, and it is **just as
source-stratified** (STRUCTURE 0.993 vs 0.991). The source signal is not
identifiers leaking into the embedded text — it is house style in the definition
prose itself.

## Corpus changes

| | phase 8 | phase 9 |
|---|--:|--:|
| matrix | 48,962 proteins / 4 organisms | **80,066 / 10** |
| trait classes observed | 70,446 | **83,583** |
| `trait_cooccurrence.tsv` | 1,479 edges | **2,590** |
| protein map points | 47,768 | **78,296** |

`canonical_examples` were re-ranked against the wider matrix (11,019 records
newly reachable — traits that exist only in the six added proteomes).

## Gate

* Rule-replication, map-measurement and protein-map scripts are read-only.
* The phase-8 withdrawal rests on a controlled re-measurement, not on the raw
  before/after: same four organisms, re-extracted, reproduce 1.42× / 2.29×.
* Corpus-map purity checked for sampling artefacts across four sample sizes up to
  the full 344,797 records.

## Caveats

* *Plasmodium* contributes 321 reviewed proteins, so its 100% replication rests on
  8–9 testable rules. It is a weak cell, not a strong one.
* Ten proteomes are still a convenience sample of model organisms; there is no
  thermophilic bacterium, no protist outside apicomplexa, no fungus besides
  budding yeast.
* Neighbour purity remains one summary statistic and says nothing about *which*
  neighbours; the retrieval counter-test is the check that stops it being
  over-read, and both should be quoted together.

## Next

- Feed shared `canonical_examples` proteins into the residue-frame base overlay
  (Path 1) — the last item carried from phase 4, untouched here.
- The corpus map's source stratification is worth acting on, not just measuring:
  a source-balanced or source-residualised embedding would make the map show trait
  semantics rather than provenance.
- Re-check the phase-6 conclusion that a random split leaks orthologs, now that the
  matrix is only 47% vertebrate.
