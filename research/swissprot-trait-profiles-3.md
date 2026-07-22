---
topic: swissprot-trait-profiles
phase: 3
date: 2026-07-21
issue: "#7 — cross-axis feature correlation"
prior: swissprot-trait-profiles-2.md
---

# Swiss-Prot trait profiles — Phase 3: cross-axis feature correlation

Issue #7 asks, verbatim, to "get correlations for all features e.g if certain
sequence features always encode certain structural traits." Phase 3 answers it from
the 20,000-protein matrix — and the answer validates the KB's central premise
(sequence, structure and function traits are correlated across axes).

## Method — `scripts/analyze_trait_correlations.py` (`just trait-correlations`)
For every ordered trait pair (A → B) co-occurring on the profiled proteins, compute
support(A), **confidence** P(B|A), and **lift** P(B|A)/P(B), using the corpus trait
index for each trait's axis. Report the strongest **cross-axis** implications:
sequence signature → structure fold, and sequence/structure → function. 4.86M trait
pairs evaluated; thresholds support≥30, conf≥0.9, lift≥3.

## Result 1 — do sequence features encode structural traits? **Yes.**
**311 sequence-signature → structure-fold rules at ≥0.9 confidence; 226 at ≥0.99** —
a sequence signature that essentially *always* encodes one specific fold, at
500–625× lift.
| sequence signature | → structure fold | conf | lift |
|---|---|--:|--:|
| `Pfam:PF00176` (SNF2 helicase) | `CATH:3.40.50.10810` | 1.00 | 625× |
| `PROSITE:PS50838` | `CATH:1.10.10.1210` | 1.00 | 588× |
| `Pfam:PF01825` | `CATH:2.60.220.50` | 1.00 | 588× |
| `NCBIfam:TIGR01494` (P-type ATPase) | `CATH:3.40.1110.10` + `CATH:2.70.150.10` | 1.00 | 556× |
| `Pfam:PF00122` (E1-E2 ATPase) | `CATH:3.40.1110.10` | 1.00 | 556× |

The two-fold hits (a P-type ATPase signature → *both* its constituent CATH domains)
show the correlation captures multi-domain architecture, not just one-to-one folds.
This is the empirical backbone of the sequence↔structure alignment overlays: a
signature and a fold that co-occur on ~every protein carrying the signature.

## Result 2 — sequence / structure trait → function
**419 rules** at ≥0.9 confidence / ≥3 lift, e.g.:
| trait | → function | conf | lift |
|---|---|--:|--:|
| `Pfam:PF00105` / `PROSITE:PS00031` (steroid-receptor Zn) | `GO:0004879` nuclear receptor activity | 1.00 | 385× |
| `PROSITE:PS00973/972` | `GO:0004843` deubiquitinase | 1.00 | 189× |
| `PROSITE:PS50215` | `GO:0004222` metalloendopeptidase | 1.00 | 183× |
| `CATH:3.30.497.10` (structure) | `GO:0004867` serine-protease inhibitor | 1.00 | 196× |

Both sequence *and* structure traits appear as confident function predictors — the
same implications the phase-2 decision tree learned, now quantified as association
rules across the whole matrix.

## Reading the result
- The KB's premise holds empirically: **hundreds of signatures deterministically
  encode a fold**, and sequence/structure traits imply function at high lift. The
  three axes are not independent labels — they are tightly coupled per protein.
- These high-confidence rules are directly usable: (a) as `has_part` / co-occurrence
  edges between the SEQUENCE-signature and STRUCTURE-fold trait records; (b) to
  auto-suggest `canonical_examples` (a protein carrying signature X is an example of
  fold Y's record); (c) as priors for the phase-2 function predictor.

## Next (phase 4)
- **Materialise** the ≥0.99 sequence→fold rules as typed `trait_relations`
  (`biolink:related_to` / co-occurrence) between the signature and fold records —
  a data-backed cross-axis overlay complementing the CATH co-membership overlay.
- **Multi-organism** run (mouse/yeast/E. coli) to confirm the rules are not
  human-specific, and a held-out-organism test of the decision tree.
- Protein×trait **browser map** (UMAP/PaCMAP of `profiles.jsonl`).

## Gate
Stdlib-only; reads the (gitignored, regenerable) matrix + the cached trait index.
Recipe: `just trait-correlations`.
