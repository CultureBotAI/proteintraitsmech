---
topic: causal-graphs
round: 11
date: 2026-07-21
target: clear the long tail via broad class/family nodes (1,642 drafts) + --drafts-only guard
prior_round: causal-graphs-round10.md
---

# Causal graphs — Round 11: clearing the long tail

The 3,027 remaining drafts clustered under a few **broad class/family nodes** rather
than many tiny families. Promoting those broad nodes (with `--drafts-only`) cleared
the bulk in four moves.

## Broad-node promotions (`--drafts-only`, 1,642 drafts)
| broad node | drafts | traits used |
|---|--:|---|
| `ARO:3000078` class A β-lactamase | 715 | `PROSITE:PS00146` + `CATH:3.40.710.10` (GES/CARB/VEB/LEN/OXY/OKP/…) |
| `ARO:3000076` class C β-lactamase | 253 | `PROSITE:PRU10102` + `CATH:3.40.710.10` |
| `ARO:3000004` class B (metallo) β-lactamase | 627 | `Pfam:PF00753` + `CATH:3.60.15.30` (IMP/VIM/NDM/GOB/BlaB/subclass B1+B3) |
| `ARO:3000560` Erm 23S rRNA methyltransferase | 47 | `Pfam:PF00398` (target alteration) |

All the metallo-β-lactamase carbapenemases (IMP/VIM/NDM) are now wired through the MBL
domain + fold traits, matching the hand-curated MCSA:15 / GOB-10.

## The `--drafts-only` fix (important)
A broad node (class A) contains members already curated under a *more specific* family
(KPC/TEM/SHV/CTX-M). Promoting the broad node first **overwrote** those with the generic
config — clobbering their family-specific evidence. Fixed by:
- discarding the clobber (`git checkout`), and
- adding **`--drafts-only`** to `promote_family_drafts.py`: it promotes only
  `resistance-draft` graphs and never re-promotes already-curated members. Broad nodes
  must use it; specific-family re-promotion (config change) still works without it.
- Verified KPC-2 kept its specific evidence (11 `PMID:28388065` refs) while GES-1/IMP-1
  gained curated graphs.

## Curation tracker
| | records |
|---|--:|
| curated (REVIEWED, protein-trait-wired) | **6,014** |
| remaining drafts | 1,385 |

`just audit-graphs` → 7,401 graphs, **0 errors**; snippet-cited edges 42,192 → 58,463.

## What remains (1,385 drafts)
Genuinely heterogeneous, low per-family yield: `ARO:0000031` "antibiotic resistant gene
variant or mutant" (~337 — point-mutant genes: gyrA/rpoB/16S rRNA mutations, target
alteration by mutation), efflux-pump subunits / two-component regulators, glycopeptide-
associated genes, and single-gene records. These need per-mutation or per-gene curation
rather than one shared family reference — a curator task; `audit-graphs --strict` lists
each snippet-pending edge.
