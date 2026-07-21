---
topic: causal-graphs
round: 3
date: 2026-07-21
target: aro/FUNC_RESISTANCE — ARO:3004802 (GOB-10 subclass B3 metallo-β-lactamase)
prior_round: causal-graphs-round2.md
method: ARO record + PMID:21299838 (GOB-1 characterisation, verbatim abstract), ChEBI/GO id checks
---

# Causal graphs — Round 3: antibiotic-resistance determinant (GOB-10, ARO:3004802)

Third round of [[edison-causal-graphs]], and the first outside M-CSA. Rounds 1–2
were **reaction-mechanism** graphs on catalytic-site records (serine MCSA:2,
metal MCSA:15). This round moves to the **FUNCTION/`FUNC_RESISTANCE`** axis and a
different **edge shape**: `determinant → mechanism → phenotype`. The ARO records
model resistance causation, not atomic chemistry.

## Gap (from the audit)
| source | category | n | w/graph | w/ev |
|--------|----------|--:|--------:|-----:|
| **aro** | **FUNC_RESISTANCE** | 7,452 | 0 → **1** | 3,242 |
| mcsa | STRUCT_ACTIVE_SITE | 1,003 | 2 | 1,000 |

ARO `FUNC_RESISTANCE` (7,452) is the largest mechanism-rich gap. But the seeded
determinant records are **thin** (label, definition, one AMR-family parent, one
PMID) — they don't carry the mechanism/drug-class as slots, so a graph requires
**researching** the resistance mechanism, not transcribing it (unlike M-CSA).

Target **GOB-10** (ARO:3004802) — a subclass B3 metallo-β-lactamase. Chosen
deliberately: its mechanism is the **same Zn-dependent β-lactam hydrolysis modelled
atomically in round 2 (MCSA:15)**, so this graph *connects the mechanism to its
clinical consequence* — the round-1/2 chemistry is *why* this determinant confers
resistance.

## Research (ARO + PMID:21299838, verbatim)

The determinant record itself: "GOB-10 is a class B beta-lactamase gene found in
Chryseobacterium meningosepticum." The biochemistry is from the characterised GOB
archetype **GOB-1** (PMID:21299838; GOB-10 is a GOB-family variant that inherits
the subclass-B3 MBL mechanism — a family-level inference, flagged):
- **B3 di-zinc MBL** — title: "Broad antibiotic resistance profile of the subclass
  B3 metallo-β-lactamase GOB-1, a di-zinc enzyme".
- **Zn-dependent** — "the Q116 residue plays a role in the binding of the zinc ion
  in the QHH site".
- **Broad hydrolysis** — "The MBL was purified to homogeneity and shown to exhibit
  a broad substrate profile, hydrolyzing all the tested β-lactam compounds
  efficiently" (penicillins, cephalosporins, carbapenems).

## Graph design (`graph_id: resistance`, 6 nodes / 6 edges)

The determinant→mechanism→phenotype chain:

- **Nodes (grounded 5/6):** gob10 (PROTEIN → `ARO:3004802`); gob_family (PROTEIN →
  `ARO:3004212`); zn (LIGAND → `CHEBI:29105`); hydrolysis (MOLECULAR_FUNCTION →
  `GO:0008800`, xrefs `EC:3.5.2.6` + `ARO:0001004`); betalactams (CHEMICAL →
  `CHEBI:27933` = β-lactam antibiotic, verified); resistance (PHENOTYPE,
  label-only — no clean CURIE).
- **Edges (6/6 snippet-cited):**
  1. gob10 —`member of` (RO:0002350)→ gob_family
  2. gob10 —`enables` (RO:0002327)→ hydrolysis
  3. zn —`is cofactor for` (RO:0002436)→ hydrolysis
  4. hydrolysis —`has input` (RO:0002233)→ betalactams
  5. hydrolysis —`causally upstream of` (RO:0002411)→ resistance
  6. gob10 —`causally upstream of` (RO:0002411)→ resistance
- **New node types exercised:** PROTEIN (determinant + family), MOLECULAR_FUNCTION,
  PHENOTYPE — and the **RO relations shift** from the chemistry verbs (round 1–2)
  to causation/membership (`member of`, `enables`, `has input`, `causally upstream
  of`), which is exactly the ARO edge shape.

## Provenance
records touched: **1** (`ARO:3004802`) · edges written: **6** · all edges cited:
**yes** (6/6 verbatim snippet) · nodes grounded: **5/6** · status: **SEEDED →
REVIEWED** (+ `curation_history`, `llm_assisted: true`).

Gates: `just validate` → **No issues found**; `just audit-graphs` → **0 errors**
(1 warning — the PHENOTYPE node is label-only).

## The three edge shapes now demonstrated
| round | record | axis | shape |
|---|---|---|---|
| 1 | MCSA:2 | STRUCTURE | serine reaction mechanism (covalent) |
| 2 | MCSA:15 | STRUCTURE | metal reaction mechanism (di-zinc, LIGAND) |
| **3** | **GOB-10** | **FUNCTION** | **determinant → mechanism → phenotype** |

And they *interlock*: MCSA:15 is the atomic mechanism of the very hydrolysis that
GOB-10's `hydrolysis` node names — the causal-graph layer now spans from atomic
chemistry to clinical phenotype for one enzyme family.

## Open questions / next targets
- **Family-level inference.** GOB-10's mechanism evidence is from GOB-1 (the
  characterised archetype). Flagged in the graph description + edge notes; standard
  for AMR-variant curation, but a curator should confirm before REVIEWED is treated
  as gold.
- **Determinant thinness.** ARO seeds don't carry drug-class / mechanism slots — a
  seeder enrichment pulling CARD's `confers_resistance_to_drug_class` and
  `resistance_mechanism` relations would let future graphs be transcribed rather
  than researched (like M-CSA). Worth a round-4 enrichment pass.
- **PHENOTYPE grounding.** The resistance phenotype is label-only; an ARO/ARO-drug
  or MONDO/HP grounding could be added.
- **Next:** round 4 → either the ARO seeder enrichment above, or an efflux-pump /
  target-alteration determinant (a genuinely different mechanism than inactivation).
