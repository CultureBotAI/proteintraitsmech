---
topic: causal-graphs
round: 4
date: 2026-07-21
target: aro/FUNC_RESISTANCE — ARO enrichment (7,403 records) + ARO:3001328 (E. coli MdfA, efflux)
prior_round: causal-graphs-round3.md
method: ARO OBO is_a-ancestry enrichment; MdfA graph from ARO + PMID:12578981 (verbatim); ChEBI/GO id checks
---

# Causal graphs — Round 4: ARO enrichment at scale + an efflux determinant (MdfA)

Two deliverables. (A) A **seeder-style enrichment** that pulls CARD's drug-class +
mechanism relations onto **7,403 ARO determinant records**, so future resistance
graphs are *transcribable* (like M-CSA) instead of researched one gene at a time —
closing the round-3 gap. (B) A round-4 graph on a **different mechanism** — active
**efflux** (MdfA), contrasting the enzymatic-inactivation graphs of rounds 1–3.

## (A) ARO enrichment — `scripts/enrich_aro_resistance.py`

Round 3 found the determinant records too thin to transcribe (label, definition,
one AMR-family `is_a` parent). CARD puts the useful facts on the **AMR gene family
and its `is_a` ancestors**, not the leaf gene. This enrichment walks each record's
`is_a` ancestry in `aro.obo` and appends the inherited relations as
`trait_relations`:

- **mechanism** — `participates_in` → mechanism class, as `RO:0000056` (participates
  in). E.g. GOB-10 → antibiotic inactivation (ARO:0001004) + hydrolysis of β-lactam
  by MBL (ARO:3000203); MdfA → antibiotic efflux (ARO:0010000).
- **drug class** — `confers_resistance_to_drug_class` → drug class, as
  `biolink:related_to` (ARO has no cleaner predicate; the specific ARO relation is
  named in `relation_source`). E.g. GOB-10 → carbapenem/cephalosporin/penicillin.

Provenance: `relation_source` names the nearest asserting ancestor
(`"ARO participates_in (mechanism) via ARO:3000004 class B (metallo-) beta-lactamase"`).

| | count |
|---|--:|
| ARO records scanned | 7,452 |
| **enriched (drug-class + mechanism → trait_relations)** | **7,403** |
| skipped — not a determinant (mechanism/drug-class classes) | 32 |
| determinant with no inheritable relations | 17 |
| already had trait_relations | 0 |

Idempotent (re-run skips all 7,403; existing curation, incl. round-3 `causal_graphs`,
untouched). Spot-validated (`just validate`) — schema-clean. Recipe:
`just enrich-aro-resistance --apply`. This turns the 7,452-record gap from
"research each" into "transcribe from the record."

## (B) Round-4 graph — E. coli MdfA (ARO:3001328), an EFFLUX determinant

Chosen for a **different mechanism**: MdfA is a major-facilitator-superfamily (MFS)
H+-coupled multidrug efflux pump. It confers resistance **without modifying the
drug** — it uses the proton-motive force to actively expel intact antibiotic,
lowering the intracellular concentration. Opposite of the β-lactamase determinants
(which chemically destroy the drug).

### Research (ARO + PMID:12578981, verbatim)
- efflux mechanism — "each recognizes and expels a broad spectrum of chemically
  unrelated drugs from the cell".
- substrate — "The Escherichia coli Mdr transporter MdfA is able to transport
  differentially charged substrates" (chloramphenicol, thiamphenicol, lipophilic
  cations).
- phenotype — "The resistance of cells to many drugs simultaneously (multidrug
  resistance) often involves the expression of membrane transporters (Mdrs)…".
- (The proton-motive-force coupling is folded into the `efflux` node description —
  no clean verbatim PMF sentence was available, so it is not a separately-cited edge.)

### Graph design (`graph_id: resistance`, 5 nodes / 5 edges)
- **Nodes (grounded 4/5):** mdfa (PROTEIN → `ARO:3001328`); mfs_family (PROTEIN →
  `ARO:0010002`); efflux (MOLECULAR_FUNCTION → `ARO:0010000`, xref `GO:0015238`);
  chloramphenicol (CHEMICAL → `CHEBI:17698`, verified); resistance (PHENOTYPE,
  label-only).
- **Edges (5/5 snippet-cited):** mdfa —`member of`→ mfs_family; mdfa —`enables`→
  efflux; efflux —`has input`(exports)→ chloramphenicol; efflux —`causally upstream
  of`→ resistance; mdfa —`causally upstream of`→ resistance.

## Provenance
records touched: **7,404** (7,403 enriched + MdfA graph) · MdfA edges: **5** · all
cited: **yes** (5/5 verbatim) · MdfA status: **SEEDED → REVIEWED**.

Gates: `just validate` → No issues found; `just audit-graphs` → **0 errors**
corpus-wide (now **4 graphs, 35/35 edges snippet-cited**).

## Two resistance mechanisms now contrasted
| | GOB-10 (round 3) | MdfA (round 4) |
|---|---|---|
| mechanism | antibiotic **inactivation** (ARO:0001004) | antibiotic **efflux** (ARO:0010000) |
| drug fate | β-lactam ring hydrolysed (destroyed) | intact drug expelled from cell |
| machinery | Zn-dependent β-lactamase | MFS H+-coupled antiporter |
| interlocks with | MCSA:15 (atomic Zn mechanism) | — |

## Open questions / next targets
- **Predicate for drug class.** `biolink:related_to` is a lossy stand-in for
  `confers_resistance_to_drug_class`; a curated biolink/RO resistance predicate
  would sharpen it. The specific relation is preserved in `relation_source`.
- **Family-level curation at scale.** With the enrichment in place, a batch pass
  could auto-draft `causal_graphs` for whole AMR families from the now-present
  `trait_relations` (drafts, not REVIEWED, pending per-edge verbatim citation).
- **Next mechanisms:** target alteration (e.g. a *van* operon or *erm* rRNA
  methyltransferase) and target protection (e.g. a *tet(M)* ribosomal protection
  protein) — two more distinct edge shapes to complete the resistance-mechanism set.
