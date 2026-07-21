---
topic: causal-graphs
round: 2
date: 2026-07-21
target: mcsa/STRUCT_ACTIVE_SITE — MCSA:15 (metallo-β-lactamase class B1, UniProtKB:P25910)
prior_round: causal-graphs-round1.md
method: M-CSA entry 15 mechanism page (verbatim), UniProtKB P25910 metal-site features, ChEBI id checks
---

# Causal graphs — Round 2: class B1 metallo-β-lactamase (MCSA:15)

Second round of [[edison-causal-graphs]]. Round 1 (MCSA:2) captured the class A
**serine** mechanism (covalent acyl-enzyme). This round deliberately picks the
**metal path** — a di-zinc class B1 metallo-β-lactamase — to exercise the
LIGAND/metal node types and confirm the pattern generalises beyond serine
hydrolases. Same enzyme reaction (EC 3.5.2.6, β-lactam hydrolysis), completely
different chemistry.

## Gap (from the audit)
| source | category | n | w/graph | w/ev |
|--------|----------|--:|--------:|-----:|
| aro | FUNC_RESISTANCE | 7,452 | 0 | 3,242 |
| **mcsa** | **STRUCT_ACTIVE_SITE** | 1,003 | **1 → 2** | 1,000 |

Target **MCSA:15** — *Bacillus cereus* BcII (UniProtKB:P25910, PDB 1znb), the
canonical binuclear-zinc B1 metallo-β-lactamase. Chosen because its M-CSA
residue numbering (His99, His101, Asp103, His162, Cys181, His223, Asn193, Lys184)
**already matches the record's own STRUCT_METAL_SITE / STRUCT_BINDING_SITE
features** — no numbering reconciliation needed.

## Mechanism (researched — M-CSA entry 15)

No covalent intermediate. Two Zn²⁺ ions and a bridging hydroxide do the work
(verbatim quotes are the edge `snippet`s):

- **Metal sites** — "Asp103, Cys181, His99, His101, His223, His162 (metal ligands);
  Asn193, Lys184 (stabilizers)". Zn1 = His99/His101 (+ bridging Asp103/Cys181);
  Zn2 = His162/His223 (+ bridging Asp103/Cys181).
- **Substrate polarisation** — "The beta-lactam carbonyl interacts with zinc1
  polarising the bond and enhancing its susceptibility to nucleophilic attack".
- **Nucleophilic attack** — "Zinc activated water initiates a nucleophilic attack
  on the carbonyl of the beta-lactam ring, breaking the C-N bond in a substitution
  reaction". Asn193 "stabilises the anionic tetrahedral intermediate".
- **Product release (rate-determining)** — "The negatively charged nitrogen group
  then deprotonates an incoming, zinc-activated water molecule" → substituted
  β-amino acid.

## Graph design (`graph_id: catalysis`, 14 nodes / 13 edges)

- **Nodes (grounded 13/14):** zn1, zn2 (LIGAND → `CHEBI:29105` = zinc(2+),
  verified on ChEBI); his99/his101/asp103/his162/cys181/his223/asn193/lys184
  (RESIDUE → `UniProtKB:P25910`, positions match the record's metal features);
  water (CHEMICAL → `CHEBI:15377`); substrate (`CHEBI:35627`); product
  (`CHEBI:33705`); tetra (STATE, label-only — a transient intermediate).
- **Edges (13/13 snippet-cited):** 6 metal-coordination edges (His/Asp/Cys → Zn1/Zn2),
  then the mechanism chain zn1→substrate (polarise), zn2→water (activate),
  water→substrate (attack), substrate→tetra (C-N cleavage), asn193→tetra (stabilise),
  lys184→substrate (electrostatic), tetra→product (protonation/release).
  `predicate_id` = `RO:0002436` (molecularly interacts with) for coordination /
  chemical steps, `RO:0002411` (causally upstream of) for state transitions.
- **New node type exercised:** `LIGAND` (the two zinc ions) — round 1 used only
  RESIDUE/CHEMICAL/STATE. The metal path works cleanly.

## Provenance
records touched: **1** (`MCSA:15`) · edges written: **13** · all edges cited: **yes**
(13/13 verbatim snippet) · nodes grounded: **13/14** · status: **SEEDED → REVIEWED**
(+ `curation_history` event, `llm_assisted: true`).

Gates: `just validate` → **No issues found**; `just audit-graphs` → **0 errors**,
1 warning (the STATE intermediate is label-only, expected).

## Serine vs metal — the two mechanisms now side by side
| | MCSA:2 (class A) | MCSA:15 (class B1) |
|---|---|---|
| nucleophile | Ser70 (covalent) | bridging Zn-activated hydroxide |
| intermediate | acyl-enzyme (covalent) | anionic tetrahedral (non-covalent) |
| key residues | Ser70/Lys73/Ser130/Glu166 | 2×Zn²⁺ + 6 ligands + Asn193/Lys184 |
| new node types | — | LIGAND (Zn²⁺) |

## Open questions / next targets
- **Bridging-ligand representation.** Asp103/Cys181 coordinate both zincs; modelled
  as one edge each (to Zn1 / Zn2 resp.) with the bridging role in the description,
  rather than four edges. Faithful and less cluttered.
- **Coordination snippet.** The six coordination edges share the M-CSA residue-role
  roster as their `snippet` (the page states roles as a set, not per-residue prose);
  the per-Zn assignment lives in `notes`. Corroborated by the record's UniProt
  METAL_SITE features and PMID:8994966 (the 1znb structure).
- **Next:** round 3 → begin ARO `FUNC_RESISTANCE` (7,452 records, 3,242 with
  evidence) — a different edge shape (determinant → mechanism → resistant
  phenotype), the largest mechanism-rich gap.
