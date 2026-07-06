# Tool value vs compute — which sources earn their keep

**Goal:** identify the core subset of tools (seeders) that yield the most
*valuable* traits for the least *computation*, so a lean pipeline can be run when
full coverage isn't needed.

Reproduce: `python3 scripts/tool_value_analysis.py` (read-only, ~40 s over the
whole corpus). Numbers below are from the **317,621-record** corpus (47 tools).

## How "value" and "cost" are defined

**Value** is a transparent per-record proxy (each component ∈ [0,1], weighted):

| Signal | Weight | What it rewards |
|---|---|---|
| groundings | 0.25 | `xrefs` + `mapped_xrefs` (a connected, cross-referenced trait) |
| evidence | 0.20 | a DOI/PMID `evidence:` block (citation-backed) |
| definition | 0.20 | real definition text length (content, not a stub) |
| layered defs | 0.15 | a `definitions:` list (STRUCTURAL/MECHANISTIC/GENERAL) |
| representation | 0.10 | a sequence_pattern / secondary_structure / geometry / chemistry slot |
| hierarchy | 0.10 | `parent_traits` (sits in a real taxonomy) |

**Cost** is proxied by **record count** — the dominant recurring compute is
per-record text embedding (+ neighbours + PaCMAP), which scales linearly with the
number of records. So a tool's *compute share* = its share of all records.

**Efficiency** = `value_share ÷ compute_share`. **>1 means the tool delivers more
value than its compute footprint; <1 means it's dead weight per compute.**

*Caveat:* this is a structural-richness proxy, not biological importance. The
weights are in `WEIGHTS` at the top of the script — retune and re-run to test
sensitivity.

## The tools, ranked by efficiency

| tool | records | compute% | value% | **eff** | strengths |
|---|--:|--:|--:|--:|---|
| **rhea** | 18,558 | 5.8% | 9.2% | **1.58** | representation 1.00, evidence 0.95 |
| **mcsa** | 1,003 | 0.3% | 0.5% | **1.46** | evidence 1.00, definition 0.92 |
| **ted** | 13,860 | 4.4% | 6.3% | **1.45** | evidence 1.00, geometry 1.00 |
| **interpro** | 26,264 | 8.3% | 11.3% | **1.37** | definition 0.85, evidence 0.81 |
| curated/seed | 920 | 0.3% | 0.4% | 1.30 | hierarchy + groundings |
| **prosite** | 6,174 | 1.9% | 2.4% | **1.24** | definition 0.90 |
| repeatsdb | 122 | 0.0% | 0.0% | 1.16 | geometry 0.98 |
| **cath** | 8,151 | 2.6% | 2.8% | **1.08** | geometry 1.00, hierarchy 1.00 |
| **go** | 38,245 | 12.0% | 12.5% | **1.04** | hierarchy 1.00, def 0.39, grounding 0.38 |
| ec | 7,375 | 2.3% | 2.3% | 1.01 | hierarchy, definition 0.47 |
| pfam | 31,025 | 9.8% | 9.7% | 0.99 | definition 0.73 |
| cazy | 557 | 0.2% | 0.2% | 0.98 | definition 0.56 |
| aro | 7,452 | 2.3% | 2.3% | 0.97 | evidence 0.44 |
| cog | 4,877 | 1.5% | 1.4% | 0.94 | hierarchy |
| **ecod** | 45,113 | **14.2%** | 13.1% | 0.92 | hierarchy 1.00 (thin otherwise) |
| reactome | 2,883 | 0.9% | 0.8% | 0.87 | hierarchy |
| tcdb | 2,285 | 0.7% | 0.6% | 0.87 | definition, representation |
| **ncbifam** | 38,394 | **12.1%** | 9.2% | **0.76** | evidence 0.50 but thin defs/groundings |
| **cdd** | 38,218 | **12.0%** | 9.1% | **0.75** | definition 0.63 but few groundings |
| **scope** | 22,810 | **7.2%** | 5.0% | **0.70** | hierarchy only — mostly stub definitions |
| merops | 370 | 0.1% | 0.0% | 0.22 | bare (no def/grounding/evidence) |

## The core subset — most value for least compute

Adding tools greedily by efficiency:

- **The top 8 tools** (rhea, mcsa, ted, interpro, curated/seed, prosite, repeatsdb, cath) → **33% of all value for 24% of compute.**
- **+ go, ec** → **48% of value for 38% of compute.**
- **+ pfam, cazy, aro, mi, mod, cog** → **62% of value for 53% of compute.**

**Recommended core (lean pipeline):**

> **rhea · mcsa · ted · interpro · prosite · cath · repeatsdb · ec · go · pfam**
> (+ the tiny curated grouping nodes)

These span every axis with the richest traits — enzyme mechanism (Rhea/M-CSA/EC),
structural folds *with geometry* (TED/CATH/RepeatsDB), sequence signatures *with
real abstracts + citations* (InterPro/PROSITE/Pfam), and the GO function backbone.
Roughly **half the value at ~40% of the compute**, and every high-efficiency tool
is included.

## The expensive tail — candidates to sample or defer

Three tools are **~31% of the entire compute budget for ~19% of the value**:

| tool | compute% | eff | why it's low-value-per-record |
|---|--:|--:|---|
| **ncbifam** | 12.1% | 0.76 | thin definitions, few groundings (0.14) |
| **cdd** | 12.0% | 0.75 | almost no groundings (0.09) |
| **scope** | 7.2% | 0.70 | stub definitions (0.17) — the fold *names* without the structural prose |

Plus **ecod** (14.2% of compute, eff 0.92): the single largest compute consumer,
carried almost entirely by `hierarchy` — its definitions and groundings are thin.

**If compute is the constraint:** drop or down-sample ncbifam + cdd + scope + the
bulk of ecod first — that reclaims **~45% of the embedding compute** while losing
only the least-connected, stub-definition records. Better still, these are the
prime targets for the **layered-definitions enrichment** (e.g. the SCOP `dir.com`
structural descriptions already lifted scope's fold nodes) and grounding backfills
— enriching them *raises their efficiency* rather than deleting coverage.

## Most valuable individual traits

The highest-scoring records concentrate where several signals stack:
- **FUNCTION / enzyme mechanism** — Rhea reactions (ChEBI participants + citations)
  and M-CSA active sites (mechanistic definition + PMID) score highest.
- **STRUCTURE / folds with geometry** — TED / CATH / RepeatsDB records carrying a
  `structural_geometry_representations` slot **and** (now) a STRUCTURAL definition.
- **SEQUENCE / signatures with prose** — InterPro & PROSITE entries that carry the
  full source abstract + a DOI plus GO/EC groundings.

The common thread — and the lever for raising corpus value cheaply — is
**evidence + a real definition + a representation slot + groundings on the same
record**, which is exactly what the citation-backfill, representation, and
layered-definition passes add.
