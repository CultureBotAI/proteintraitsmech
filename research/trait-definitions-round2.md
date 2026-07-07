---
topic: trait-definitions
round: 2
date: 2026-07-07
batch: CDD / FUNC_ORTHOLOG_GROUP / FUNCTION
prior_round: trait-definitions-round1.md
---

# Trait definitions — Round 2: CDD ortholog groups (+ gap closed)

Builds on [Round 1](trait-definitions-round1.md) (NCBIfam). This round finishes the
last genuine template/name-only batch and records that the gap is now closed.

## Gap (from the audit)

| source | axis | category | n | avgW | template% | lay% |
|---|---|---|--:|--:|--:|--:|
| cdd | FUNCTION | FUNC_ORTHOLOG_GROUP | 4,825 | 9 | 100% | 0% |

## Current vs exemplar

- **current** (all 4,825, one shape): a NAME, not a definition —
  `"KOG0227, Splicing factor 3a, subunit 2 [RNA processing and modification]"`
  (KOG accession · group name · bracketed COG-style functional category).
- **exemplar**: GO/EC function definitions, and the NCBIfam recompose from Round 1.

## Content source

The name and functional category are already *in* the current string — parse
`"<ACC>, <name> [<category>]"`. No new fetch, no LLM (`method: SOURCED`).

## The consistent pattern

`"<name> (<KOG id>) — a eukaryotic orthologous group of proteins (KOG) in NCBI
CDD; functional category: <category>."`

Worked example:
- `KOG0227` → "Splicing factor 3a, subunit 2 (KOG0227) — a eukaryotic orthologous
  group of proteins (KOG) in NCBI CDD; functional category: RNA processing and
  modification."

## Coverage

Records: 4,825 · recomposed: 4,825 · generated: 0 · residual: 0.
`scripts/enrich_cdd_ortholog_definitions.py`, idempotent.

## Gap status — CLOSED

A final scan for template/name-only definition batches (source × category, n ≥ 100,
template ≥ 30%, layered < 20%) returns **NONE**. The remaining audit "stub" flags
are false positives on real definitions:

- **ARO / FUNC_RESISTANCE** (7,452) — real, ARO-ontology-curated definitions, just
  terse ("OXA-867 is a OXA beta-lactamase."). Author-sourced; recomposing would be
  *worse*. Left as-is.
- **InterPro / Pfam SEQ_DOMAIN** (~37k) — full source abstracts (avgW 78–89); the
  flag only catches the "This entry represents a domain…" opener. Left as-is.
- **SCOP / ECOD / CATH structural stubs** — carry a STRUCTURAL layer already
  (Rounds of the definition-state review). Covered.

## Definitions done across both rounds
NCBIfam 38,394 + CDD KOG 4,825 = **43,219** template/name-only definitions
recomposed from source metadata into consistent, hierarchy-aware, sourced prose.

**Follow-up:** `seed_ncbifam.py` and `seed_cdd.py` should adopt these compositions
so re-seeds match; and a re-embed will let the maps/related-traits reflect the 43k
improved definitions.
