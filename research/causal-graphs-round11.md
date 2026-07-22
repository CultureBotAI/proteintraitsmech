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

## Last clean clusters (`--drafts-only`, 166 drafts)
Five more genuine protein families with verified traits:
| family (ARO) | drafts | mechanism | domain / fold |
|---|--:|---|---|
| ABC-F ribosomal protection (3004469) | 46 | target protection | `Pfam:PF00005` / `CATH:1.20.1580` |
| chloramphenicol acetyltransferase CAT (3000122) | 34 | inactivation (acetylation) | `Pfam:PF00302` / `CATH:3.30.559` |
| fosfomycin thiol transferase FosA (3000133) | 31 | inactivation (epoxide opening) | `Pfam:PF00903` / `CATH:3.10.180` |
| 23S rRNA methyltransferase Cfr (3004274) | 28 | target alteration | `Pfam:PF04055` (radical-SAM) / `CATH:3.20.20` |
| ABC antibiotic efflux pump (0010001) | 27 | efflux | `Pfam:PF00005` / `CATH:1.20.1580` |

## Curation tracker (final)
| | records |
|---|--:|
| curated (REVIEWED, protein-trait-wired) | **6,180** |
| remaining drafts | 1,219 |

`just audit-graphs` → 7,401 graphs, **0 errors**; snippet-cited edges 42,192 → 59,870.

## What remains (1,219 drafts) — the un-batchable tail
Genuinely heterogeneous, no shared family reference fits: `ARO:0000031` "antibiotic
resistant gene variant or mutant" (~353 — point-mutant target genes gyrA/rpoB/16S/23S,
each a different protein), efflux-pump subunits and two-component regulators (diverse
functions), rRNA-mutation records (not proteins), and single-gene records. Forcing one
config on these would produce *inaccurate* graphs, violating the protein-trait principle
— so this is the honest stopping point for automated family promotion. Per-gene /
per-mutation curation (with `audit-graphs --strict` listing each snippet-pending edge) is
the remaining curator task.

## Fold re-grounding (the "data-gap" flags were false negatives)
The three flagged folds all **already exist** as KB records — re-grounded to the precise
ones (no seeding needed):
- ABC-F + ABC efflux (73 records): `CATH:1.20.1580` (class-1, mainly-α — wrong for an
  ATPase NBD) → **`CATH:3.40.50.300`** "P-loop containing nucleotide triphosphate
  hydrolases" (the correct NBD superfamily).
- qnr (111 records): added the fold node **`ECOD:T.207.9.1`** "Pentapeptide repeats" (the
  Qnr/MfpA right-handed β-helix / Rfr fold) — previously fold-less.
- Cfr: left at `CATH:3.20.20` (TIM Barrel — accurate; the radical-SAM identity is already
  carried by its `Pfam:PF04055` domain node; `CATH:3.20.20.70` is labelled "Aldolase
  class I", misleading for a radical-SAM enzyme).
