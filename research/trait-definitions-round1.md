---
topic: trait-definitions
round: 1
date: 2026-07-07
batch: NCBIfam / FUNC_PROTEIN_FAMILY + SEQ_DOMAIN / FUNCTION + SEQUENCE
prior_round: (none — first round; builds on research/definition-state-review.md)
---

# Trait definitions — Round 1: NCBIfam

First application of the [[edison-trait-definitions]] skill. NCBIfam is the largest
definition gap: 38k records whose definition was a template stub carrying no
function, despite the source shipping EC/GO/product for each model.

## Gap (from the audit)

| source | axis | category | n | avgW | stub% | lay% |
|---|---|---|--:|--:|--:|--:|
| ncbifam | FUNCTION | FUNC_PROTEIN_FAMILY | 20,313 | 16 | 100% | 0% |
| ncbifam | SEQUENCE | SEQ_DOMAIN | 17,927 | 16 | 100% | 0% |
| ncbifam | SEQUENCE | SEQ_REPEAT / SEQ_HOM_SUPERFAMILY | 154 | — | 100% | 0% |

## Current vs exemplar

- **current** (all 38k, one shape): `"<product> — an NCBIfam protein family
  (NF…, equivalog); members share this conserved family signature."` — the product
  name is the only real content; EC/GO carried on the record are never surfaced.
- **exemplar** (sibling SEQUENCE/domain sources): InterPro —
  `"This entry represents a domain found in sulphatases."`; Pfam/CDD abstracts —
  a sentence of real function. Short, function-forward, states what it *is*.

## Content source

NCBIfam's own `data/raw/ncbifam/hmm_PGAP.tsv`: `product_name`, `family_type`,
`ec_numbers`, `go_terms`, `gene_symbol`, `taxonomic_range_name`. EC/GO resolved to
**names** via `data/raw/ec/enzyme.dat` (8,456 names) and `data/raw/go-basic.obo`
(48,329 names). All SOURCED — no LLM.

## The consistent pattern (one per axis; every record byte-consistent)

The axis carries the framing (this respects the family_type→axis split — see the
codex axis-split review): FUNCTION = a whole-protein family; SEQUENCE = a region.

- **FUNCTION** — `"<product> (<gene>) — a functionally conserved protein family
  grouped by the NCBIfam full-length profile-HMM <acc> (<family_type>);
  catalyses <EC names>; associated with <GO names>. Members occur in <taxon>."`
- **SEQUENCE** — `"<product> — a protein domain|region modelled by the NCBIfam
  sequence-profile HMM <acc> (<family_type>); associated with <function>."`

Worked examples across the range:
1. `NF052528` (FUNCTION, equivalog): "lipoprotein heptaprenylglyceryl
   N-acetyltransferase LhaT — a functionally conserved protein family grouped by
   the NCBIfam full-length profile-HMM NF052528 (equivalog)."
2. `NF000032` (FUNCTION, exception, w/ EC): "D-alanine--D-serine ligase VanL — …
   (exception); catalyses D-alanine--D-serine ligase."
3. `NF036354` (SEQUENCE, domain): "L1 transposable element trimerization domain —
   a protein domain modelled by the NCBIfam sequence-profile HMM NF036354 (domain)."
4. `NF021843` (SEQUENCE, pfamautoeq): "DUF2034 domain-containing protein — a
   protein domain modelled by the NCBIfam sequence-profile HMM NF021843 (pfamautoeq)."

## Coverage

Records: ~38,240 · recomposed: ~38k (all with an hmm_PGAP row; `method: SOURCED`,
`definition_source: "NCBIfam PGAP (composed from product and EC/GO annotations)"`) · generated: 0 ·
residual: a handful without a matching accession row. `scripts/enrich_ncbifam_
definitions.py`, idempotent.

**Follow-up:** `seed_ncbifam.py` should adopt the same composition so a re-seed
matches (currently the enrichment recomposes post-seed in place). Next rounds:
ARO / FUNC_RESISTANCE (7.4k) and CDD / FUNC_ORTHOLOG_GROUP (4.8k) — the remaining
stub+no-layer batches.
