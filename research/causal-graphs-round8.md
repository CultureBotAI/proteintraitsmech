---
topic: causal-graphs
round: 8
date: 2026-07-21
target: extend protein-trait wiring — 4 β-lactamase families (TEM/SHV/CTX-M/OXA, 2,118 records) + backfill the 5 hand-curated graphs
prior_round: causal-graphs-round7.md
method: research subagent verified 21 KB trait CURIEs + 1 mechanism PMID per target; per-family protein_traits config; hand-backfill the exemplars
---

# Causal graphs — Round 8: protein-trait wiring at family scale + backfills

Round 7 established the principle (causal graphs must run through the KB's specific
protein-trait records) on MCSA:2 + the KPC family. This round extends it to the next
four β-lactamase families and backfills the remaining hand-curated graphs, so every
curated resistance graph now reaches into the SEQUENCE / STRUCTURE trait records.

A research subagent verified **21 KB trait CURIEs** (exact-identifier grep) and one
verbatim mechanism PMID per target.

## (A) Four β-lactamase families promoted with protein traits

Added to `promote_family_drafts.py` `FAMILY_SNIPPETS`; the class-A families reuse the
verified class-A traits, OXA uses the distinct class-D active-site trait.

| family (ARO) | records | active-site trait | fold trait | mechanism ref |
|---|--:|---|---|---|
| TEM (3000014) | 251 | `PROSITE:PS00146` (class A) | `CATH:3.40.710.10` | PMID:32576842 |
| SHV (3000015) | 242 | `PROSITE:PS00146` | `CATH:3.40.710.10` | PMID:10539992 |
| CTX-M (3000016) | 274 | `PROSITE:PS00146` | `CATH:3.40.710.10` | PMID:15105882 |
| **OXA (3000017)** | **1,351** | **`PROSITE:PRU10103` (class D)** | `CATH:3.40.710.10` | PMID:16121396 |

Each graph now wires: `active_site part_of determinant`, `determinant member_of
fold`, `active_site enables` the serine-hydrolysis mechanism. All validate clean;
OXA correctly carries the class-D (carbamylated-lysine) active-site trait, not the
class-A one. **2,118 records** (+ 232 KPC from round 7 = **2,350** class-A/D
β-lactamase determinants now wired through the KB's own signature + fold records).

## (B) Backfilled the 5 hand-curated graphs

Each now carries its specific KB trait records + partonomy/host edges (all edges
snippet-cited, 0 errors):

| record | added protein traits | nodes/edges |
|---|---|---|
| MCSA:15 (class B MBL) | `Pfam:PF00753` domain, `PROSITE:PS00743` signature, `CATH:3.60.15.30` fold, `GO:0008800` activity | 18 / 18 |
| GOB-10 (B3 MBL) | `Pfam:PF00753`, `CATH:3.60.15.30` | 8 / 9 |
| MdfA (MFS efflux) | `Pfam:PF07690` MFS domain, `CATH:1.20.1250.20` MFS fold | 7 / 8 |
| ErmB (methyltransferase) | `Pfam:PF00398` RrnaAD domain, `PROSITE:PRU01026` signature | 9 / 10 |
| tet(M) (EF-G GTPase) | `Pfam:PF00009` GTPase domain, `Pfam:PF03144` EF-G domain II | 8 / 9 |

The pattern in each: a key residue / the determinant `part_of` the domain, the
domain `member_of` the fold, the domain `enables` the mechanism/activity.

## Result — the causal layer is now wired into the KB's content
Every one of the 7 hand-curated graphs (MCSA:2/15, GOB-10, MdfA, ErmB, tet(M)) and
2,350 promoted β-lactamase determinants route their mechanism through **real KB
trait records** — the FUNCTION-axis resistance graphs reach into SEQUENCE
(PROSITE/Pfam signatures) and STRUCTURE (CATH folds) traits, the cross-axis link the
alignment overlays capture. Gates: `just validate` clean; `just audit-graphs` → 0
errors.

## Open questions / next
- **Non-β-lactamase families:** qnr (target protection), MCR (colistin), MFS/RND
  efflux families — each needs a `FAMILY_SNIPPETS` entry with its own protein-trait
  records (the research pattern here — verify Pfam/CATH via grep, one mechanism PMID
  — generalises).
- **MdfA/MFS `SEQ_FAMILY` domain:** `Pfam:PF07690` is stored under `family/` (a
  `SEQ_FAMILY` record), not `domain/`; the node still grounds to a real record.
- **B3-specific domain:** `CDD:cd07708` exists for the subclass-B3 MBL fold if a
  GOB-specific (rather than pan-MBL) domain node is preferred.
