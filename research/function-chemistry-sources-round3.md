---
topic: FUNCTION-axis + chemistry source expansion
round: 3
date: 2026-07-02
question: >-
  For the FUNCTION axis, what enzyme/reaction/pathway/ortholog/transport/AMR
  sources should we add (EC, Rhea, Reactome, KEGG, MetaCyc, UniPathway, COG,
  eggNOG/NOGs, CAZy, TCDB, CARD)? Which are already in? Is eggNOG too large?
  And how should chemistry (ChEBI / InChI / formula / CAS) be modelled?
prior_round: protein-trait-sources-round2.md
method: WebSearch verification of size / licence / download, July 2026.
---

# FUNCTION-axis + chemistry sources — Round 3

Status of every source named, plus the eggNOG size analysis and the chemistry
plan. New schema categories added this round: `FUNC_TRANSPORT`,
`FUNC_RESISTANCE`, `FUNC_PATHWAY`.

## "Have we incorporated…?" — current state

| Source | In corpus? | How |
|--------|-----------|-----|
| **EC** | **Partially** | 577 EC enzyme activities (trait-onto-map, EC-anchored) → FUNC_ENZYMATIC_ACTIVITY |
| **GO** | **As groundings** | GO xrefs via interpro2go / pfam2go / ec2go (thousands of records); not seeded as standalone MF terms |
| **KEGG KO / pathway / module** | **Only as xrefs** | KEGG:K##### xrefs on the trait-onto-map enzyme records; no bulk KEGG seed |
| Rhea, Reactome, MetaCyc, UniPathway, COG, eggNOG, CAZy, TCDB, CARD | **No** | — |

## Ranked findings

Fit = target `trait_category`. ✅ ingest · ⚠️ caveat · ⛔ blocked.

| # | Source | Fit | Size | Download | Licence | Rec |
|---|--------|-----|------|----------|---------|-----|
| 1 | **Rhea** | FUNC_ENZYMATIC_ACTIVITY (+ **ChEBI bridge**) | ~15k reactions | FTP (rxn, tsv, rhea2ec) | **CC-BY 4.0** | ✅ reactions ground EC records AND link to ChEBI participants |
| 2 | **Reactome** | FUNC_PATHWAY | ~2.7k human + multi-species pathways | download-data (tsv, BioPAX, SBML) | **CC0** | ✅ cleanest pathway source |
| 3 | **COG (2020, NCBI)** | FUNC_PATHWAY / functional class | 26 categories + ~4,877 COGs | NCBI FTP (cog-20.def.tab, fun-20.tab) | **US-gov public domain** | ✅ small, clean, PD |
| 4 | **EC (full, IUBMB)** | FUNC_ENZYMATIC_ACTIVITY | ~8k EC numbers | ENZYME (enzyme.dat) / Rhea | free | ✅ complete the EC hierarchy (we have 577 of ~8k) |
| 5 | **TCDB** | **FUNC_TRANSPORT** | 5-level class; ~20k proteins, ~1.6k families | tcdb.org / GitHub | CC-BY-SA 3.0 / ODbL (**ShareAlike**) | ⚠️ ShareAlike copyleft — seed the family classification, flag licence |
| 6 | **CARD / ARO** | **FUNC_RESISTANCE** | ARO ~6k terms | card.mcmaster.ca/latest/ontology | ARO **CC-BY 4.0** (full CARD data restricted) | ✅ ingest the ARO **ontology** (open); skip the licensed CARD data |
| 7 | **CAZy / dbCAN** | FUNC_ENZYMATIC_ACTIVITY | GH/GT/PL/CE/AA/CBM families | dbCAN-seq (CAZy has no bulk) | dbCAN CC-BY (NC) | ⚠️ via dbCAN; NC flag |
| — | **KEGG** (KO/pathway/module) | FUNC_PATHWAY | large | FTP **subscription-only** | proprietary; bulk = paid even academic | ⛔ cannot bulk-ingest; keep KEGG ids as xrefs only |
| — | **MetaCyc** | FUNC_PATHWAY | large | BioCyc **subscription** | restricted | ⛔ not freely downloadable |
| — | **UniPathway** | FUNC_PATHWAY | — | — | — | ⛔ **discontinued** — reactions folded into Rhea, ontology into GO. Use Rhea/Reactome instead |
| — | **eggNOG / NOGs** | FUNC | **4.4M OGs / 379 tax levels** | eggNOG FTP | CC-BY | ⛔ see analysis below |

## eggNOG / NOG size analysis (requested)

eggNOG 5.0 holds **~4.4 million orthologous groups across 379 taxonomic
levels** (eggNOG 6.0 spans 12,535 organisms) — orders of magnitude larger than
the entire current corpus (~127k). Ingesting NOGs wholesale is infeasible and,
worse, low-value: most OGs are uncharacterised and per-lineage. Options, least
to most inclusive:

- **Skip (recommended).** Orthology-group membership is an *evolutionary*
  property of specific genes, not a class-level protein trait; the functional
  content we want (COG categories, KEGG KOs) is already reachable via COG and
  via xrefs.
- **Root-level only.** The top taxonomic level still has ~200k+ OGs — still too
  many, still mostly "uncharacterized protein".
- **COG instead.** COG 2020 (~4,877 groups, 26 functional categories, public
  domain) is the small, curated, functionally-annotated subset of the same idea
  — take COG, not eggNOG.

**Verdict: do not bulk-ingest eggNOG. Ingest COG.**

## Chemistry (ChEBI / InChI / formula / CAS) — not yet first-class

Today chemistry exists only as `CHEBI:` **xref values** and a `CHEMICAL`
CausalNode type — there is no chemical axis and no InChI/formula/SMILES/CAS
slots. **ChEBI** (CC-BY 4.0, freely downloadable as OBO/SDF) is the source of
record: every ChEBI entity carries InChI, **InChIKey**, molecular **formula**,
SMILES, mass/charge, and CAS as a registry xref.

Design forks (to resolve in the dedicated chemistry deep-research round the user
approved):
1. **Chemistry as record slots** — add `inchikey` / `formula` / `smiles` /
   `chebi` fields to records that denote/consume a chemical (cofactors,
   ligands, substrates), enriched from ChEBI. No new axis.
2. **A CHEMISTRY axis** — first-class ChEBI-anchored chemical-entity trait
   records (cofactor requirement, substrate, product) with the structural
   identifiers as slots. Bigger, but makes chemistry queryable.
3. **Rhea as the bridge** — Rhea reactions connect our EC enzyme records to
   their ChEBI participants; seeding Rhea (item 1 above) is the natural first
   step and pulls chemistry in relationally before any schema change.

Recommended sequence: seed **Rhea** (gets ChEBI participants in via reactions) →
run the chemistry deep-research to choose slots-vs-axis → enrich from ChEBI.

## Recommended next seeds (priority)

1. **Reactome** → FUNC_PATHWAY (CC0, cleanest).
2. **COG** → functional classification (PD, small) — *instead of* eggNOG.
3. **Rhea** → FUNC_ENZYMATIC_ACTIVITY grounding + ChEBI bridge (CC-BY).
4. **ARO** → FUNC_RESISTANCE (CC-BY; skip licensed CARD data).
5. **TCDB** → FUNC_TRANSPORT (flag ShareAlike).
6. Complete **EC** from ENZYME (we have 577 / ~8k).
7. **ChEBI enrichment** — after the chemistry deep-research decides the model.
8. **Do NOT** ingest eggNOG, KEGG bulk, MetaCyc, or UniPathway (blocked/dead).

## Sources

- eggNOG 5.0/6.0 — <https://pmc.ncbi.nlm.nih.gov/articles/PMC6324079/> · <https://pmc.ncbi.nlm.nih.gov/articles/PMC9825578/>
- COG (NCBI) — <https://www.ncbi.nlm.nih.gov/research/cog>
- KEGG FTP licence — <https://www.kegg.jp/kegg/download/> · <https://www.pathway.jp/en/academic.html>
- Reactome (CC0) — <https://reactome.org/license/> · <https://reactome.org/download-data>
- Rhea — <https://www.rhea-db.org/help/download> · <https://academic.oup.com/nar/article/50/D1/D693/6424769>
- UniPathway (inactive) — <https://github.com/geneontology/unipathway>
- TCDB — <https://www.tcdb.org/> · <https://bioregistry.io/tcdb>
- CARD / ARO — <https://card.mcmaster.ca/download> · <https://github.com/arpcard/aro>
- ChEBI — <https://www.ebi.ac.uk/chebi/> (CC-BY 4.0; InChI/InChIKey/formula/SMILES/CAS)
