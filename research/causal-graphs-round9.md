---
topic: causal-graphs
round: 9
date: 2026-07-21
target: protein-trait wiring for non-β-lactamase families — qnr, MCR, MFS, RND (371 records)
prior_round: causal-graphs-round8.md
method: research subagent verified trait CURIEs + mechanism PMIDs; generalized promoter (primary_key / part_pred / enable_pred, optional fold)
---

# Causal graphs — Round 9: non-β-lactamase families wired through protein traits

Rounds 7–8 wired the β-lactamase families (KPC/TEM/SHV/CTX-M/OXA) through their
active-site + fold trait records. This round extends the protein-trait wiring to
**four non-β-lactamase families spanning three more mechanisms** — target protection,
target alteration, and efflux — each grounded in its own KB domain/fold trait records.

## Generalized promoter (backward-compatible)
`promote_family_drafts.py` gained optional `protein_traits` keys so a family can use
a **domain** primary node with mechanism-appropriate predicates instead of the
β-lactamase active-site/catalysis defaults:
- `primary_key` (default `active_site`) · `part_pred` · `enable_pred` · `part_note` /
  `fold_note` / `enable_note`; **`fold` is now optional** (qnr has no matching CATH
  fold record).
- Defaults reproduce the β-lactamase output **byte-for-byte** — verified by
  re-promoting KPC with **0 file changes**, so the 2,350 β-lactamase graphs are
  untouched.

## Four families promoted (371 records)
| family (ARO) | records | mechanism | domain trait | fold trait |
|---|--:|---|---|---|
| qnr (3000419) | 111 | target **protection** | `Pfam:PF00805` (pentapeptide repeat) | — (no KB fold) |
| MCR (3004268) | 106 | target **alteration** (lipid A) | `InterPro:IPR058130` (pEtN transferase) | `CATH:3.40.720.10` |
| MFS (0010002) | 110 | **efflux** | `Pfam:PF07690` (MFS) | `CATH:1.20.1250.20` |
| RND (0010004) | 44 | **efflux** | `Pfam:PF00873` (AcrB/AcrD/AcrF) | `CATH:3.30.70.1430` |

Each graph wires `domain part_of determinant`, `determinant member_of fold` (where a
fold record exists), `domain enables` the family mechanism. All validate clean;
`just audit-graphs --strict` per record is snippet-complete. Mechanism references:
qnr PMID:21227918, MCR PMID:27958270, MFS PMID:38974671, RND PMID:19166984. The
hand-curated MdfA graph (in the MFS family) was correctly **skipped** by the
promoter's curation-signature guard.

## Coverage now
Curated (REVIEWED, protein-trait-wired) resistance graphs by mechanism:
- **inactivation** — KPC/TEM/SHV/CTX-M/OXA (2,350) + GOB-10, MCSA:2/15
- **efflux** — MFS (110) + RND (44) + MdfA
- **target protection** — qnr (111) + tet(M)
- **target alteration** — MCR (106) + ErmB

≈ **2,721 family records + the 7 hand-curated graphs** now route their mechanism
through real KB SEQUENCE (Pfam/PROSITE/InterPro) and STRUCTURE (CATH) trait records.
Gates: `just validate` clean; `just audit-graphs` → 0 errors.

## Open questions / next
- **qnr fold gap:** the KB lacks the Qnr/MfpA right-handed quadrilateral β-helix
  (Rfr) CATH fold — a seeding gap; a fold node can be added when the record exists.
- **MCR fold:** `CATH:3.40.720.10` (alkaline-phosphatase/sulfatase superfamily) is a
  strong candidate; confirm against the MCR-1 catalytic-domain crystal structure.
- **Remaining draft families:** ADC/PDC/ACT β-lactamases (class C), aminoglycoside
  modifying enzymes, vanH/vanA (glycopeptide target alteration), sul/dfr (target
  replacement) — each one `FAMILY_SNIPPETS` entry with verified trait records.
