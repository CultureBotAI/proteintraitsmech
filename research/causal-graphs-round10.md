---
topic: causal-graphs
round: 10
date: 2026-07-21
target: protein-trait wiring — class C β-lactamases + aminoglycoside-modifying enzymes + van/sul/dfr (1,647 records)
prior_round: causal-graphs-round9.md
method: research subagent verified trait CURIEs + mechanism PMIDs; _classc / _domfam config helpers
---

# Causal graphs — Round 10: class C, aminoglycoside enzymes, and target remodelling

Extends the protein-trait wiring to the last major β-lactamase class and to five
non-β-lactamase mechanisms, adding config helpers so a family is one line of setup.

## (A) Class C β-lactamases (AmpC) — 1,346 records
Same serine-β-lactamase fold as class A/D, a distinct class-C active-site signature.
A shared `_classc()` config wires each through `PROSITE:PRU10102` (class-C active
site) + `CATH:3.40.710.10` (fold); `active_site enables` the serine mechanism
(ARO:3000187). Evidence PMID:19136439 (AmpC review).
- ADC (`ARO:3005459`, the broad ADC family) 330, PDC 640, ACT 174, CMY 202.

## (B) Aminoglycoside-modifying enzymes (inactivation) — 227 records
A `_domfam()` helper (domain-primary, mechanism-appropriate predicates) wires each
through its catalytic domain + fold:
| family (ARO) | records | mechanism | domain | fold | PMID |
|---|--:|---|---|---|---|
| AAC (3000121) | 115 | acetylation | `InterPro:IPR000182` (GNAT) | `CATH:3.40.630` | 26818562 |
| APH (3000114) | 56 | phosphorylation | `Pfam:PF01636` | `CATH:3.90.1200` (PK-like) | 9200607 |
| ANT (3000218) | 56 | nucleotidylation | `Pfam:PF01909` | `CATH:3.30.460` | 25564464 |

## (C) Target remodelling — 74 records
| family (ARO) | records | mechanism | domain | fold | PMID |
|---|--:|---|---|---|---|
| van (3002978) | 9 | target **alteration** (D-Ala-D-Lac) | `Pfam:PF07478` | `CATH:3.30.470` (ATP-grasp) | 10908650 |
| sul (3004238) | 5 | target **replacement** (DHPS) | `Pfam:PF00809` | `CATH:3.20.20` (TIM barrel) | 37419898 |
| dfr (3001218) | 60 | target **replacement** (DHFR) | `Pfam:PF00186` | `CATH:3.40.430` | 35562546 |

Each graph: `domain part_of determinant`, `determinant member_of fold`, `domain
enables` the family mechanism. All validate clean; per-record `audit-graphs --strict`
snippet-complete.

## Every major resistance-mechanism class is now covered
| mechanism | families (protein-trait-wired) |
|---|---|
| enzymatic inactivation — β-lactam | class A (KPC/TEM/SHV/CTX-M), class C (ADC/PDC/ACT/CMY), class D (OXA), MBL (GOB/MCSA:15) |
| enzymatic inactivation — aminoglycoside | AAC, APH, ANT |
| efflux | MFS, RND, MdfA |
| target protection | qnr, tet(M) |
| target alteration | MCR, van, ErmB |
| target replacement | sul, dfr |

≈ **5,700 curated resistance determinants + the 7 hand-curated graphs** route their
mechanism through real KB SEQUENCE (Pfam/PROSITE/InterPro) and STRUCTURE (CATH) trait
records. Gates: `just validate` clean; `just audit-graphs` → 0 errors.

## Open questions / next
- **Remaining drafts:** the OXA-51/50/213-like subfamilies are covered under OXA;
  the long tail is efflux-subunit / regulatory / miscellaneous families and
  single-gene records — diminishing returns per family. `audit-graphs --strict`
  counts what remains snippet-pending.
- **Data-gap flags carried forward:** qnr Qnr/MfpA β-helix CATH fold absent; confirm
  MCR and APH folds against crystal structures before treating REVIEWED as gold.
