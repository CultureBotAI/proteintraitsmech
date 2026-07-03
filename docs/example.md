---
layout: default
title: Worked example — P25888
---

# Worked example — how one UniProtKB entry demultiplexes across the four axes

Using P25888 (ATP-dependent RNA helicase RhlE, *Escherichia coli* K12) to
illustrate how a single UniProtKB entry's `FT`/`CC` annotations map onto the
trait **axes** and **categories**.

> **Note.** This is an *illustration of the demultiplexing model*, not a set of
> live records. Per-protein records like these are instance-level annotations,
> not reusable trait *classes*, so they are **not** seeded standalone; instead a
> real protein is attached as a `canonical_example` on the relevant class-level
> trait (via `fetch_uniprot_examples.py`). The mapping below — FT type → axis /
> category — is what the seeders and the README table encode.

[← back to index](./) · [source entry](https://www.uniprot.org/uniprotkb/P25888/entry)

## SEQUENCE (6 records)

| # | Trait | Category | UniProt evidence |
|---|---|---|---|
| 1 | Disordered C-terminal region, residues 373-454 | `SEQ_DISORDER` | `FT REGION /note="Disordered"` (MobiDB-lite) |
| 2 | Gly-rich composition bias 393-406 | `SEQ_COMPOSITION` | `FT COMPBIAS /note="Gly residues"` |
| 3 | Basic + acidic residues 424-434 | `SEQ_COMPOSITION` | `FT COMPBIAS /note="Basic and acidic residues"` |
| 4 | Basic residues 443-454 | `SEQ_COMPOSITION` | `FT COMPBIAS /note="Basic residues"` |
| 5 | Q motif 1-29 | `SEQ_MOTIF` | `FT MOTIF /note="Q motif"` (cross-refs PROSITE `PS51195`) |
| 6 | DEAD box 156-159 | `SEQ_MOTIF` | `FT MOTIF /note="DEAD box"` (cross-refs PROSITE `PS00039`) |

## STRUCTURE (3 records)

| # | Trait | Category | UniProt evidence |
|---|---|---|---|
| 7 | Helicase ATP-binding domain 32-208 | `STRUCT_DOMAIN` | `FT DOMAIN /note="Helicase ATP-binding"` |
| 8 | Helicase C-terminal domain 219-381 | `STRUCT_DOMAIN` | `FT DOMAIN /note="Helicase C-terminal"` |
| 9 | ATP binding site 45-52 | `STRUCT_BINDING_SITE` | `FT BINDING /ligand="ATP" /ligand_id="ChEBI:CHEBI:30616"` |

## FUNCTION (11 records)

### FUNC_ENZYMATIC_ACTIVITY (3)

| # | Trait | Source |
|---|---|---|
| 10 | ATP + H₂O → ADP + phosphate + H⁺ (EC 3.6.4.13, Rhea:13065) | `CC CATALYTIC ACTIVITY` |
| 11 | ATP hydrolysis activity (GO:0016887) | `DR GO F:` |
| 12 | RNA helicase activity (GO:0003724) | `DR GO F:` |

### FUNC_BINDING_CAPACITY (2)

| # | Trait | Source |
|---|---|---|
| 13 | ATP binding (GO:0005524) | `DR GO F:` (complements the localised binding site #9) |
| 14 | RNA binding (GO:0003723) | `DR GO F:` |

### FUNC_LOCALIZATION (2)

| # | Trait | Source |
|---|---|---|
| 15 | Cytoplasm (with ribosome-associated note) | `CC SUBCELLULAR LOCATION` |
| 16 | Cytosol (GO:0005829) | `DR GO C:` |

### FUNC_ENVIRONMENTAL_RESPONSE (2)

| # | Trait | Source |
|---|---|---|
| 17 | Response to cold shock (PubMed:14527658) | `CC INDUCTION` — keyword scan matches "cold shock" |
| 18 | Response to heat (GO:0009408) | `DR GO P: response to heat` |

### FUNC_INTERACTION_PARTNER (2)

| # | Trait | Source |
|---|---|---|
| 19 | Interacts with PcnB (PubMed:10361280) | `CC SUBUNIT` |
| 20 | Interacts in vitro with RNase E (PubMed:15554979) | `CC SUBUNIT` |

## What's captured, what's still open

**Captured automatically:** identifiers, human-readable labels, cross-references to source ontologies, canonical exemplar (the source UniProt entry + NCBITaxon), evidence PMIDs where the flat file cites them.

**Open for curator work:**

- Deduplication where CC-derived and GO-derived records describe the same concept (e.g. records #15 + #16 both describe cytoplasmic localisation).
- `mapping_status: SEEDED` → `REVIEWED` after curator sign-off.
- `causal_graphs` — none of these 20 records carry a mechanism graph yet. A natural first graph on record #9 (ATP binding site) would model **ATP → (binds) → helicase ATP-binding domain → (hydrolyses) → ADP + Pi → (couples to) → RNA unwinding → (leads to) → ribosome assembly**, with each edge citing PubMed:15196029 / PubMed:18083833.

[← back to index](./)
