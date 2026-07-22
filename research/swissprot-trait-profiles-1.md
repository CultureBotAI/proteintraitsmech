---
topic: swissprot-trait-profiles
phase: 1
date: 2026-07-21
issue: "#7 — Swiss-Prot population + multi-trait families"
inspiration: doi:10.1186/s13321-025-01092-3 (trait↔function), doi:10.1186/s12859-022-05093-z (trait clustering)
---

# Swiss-Prot trait profiles — Phase 1

Issue #7 wants a per-protein view of the corpus — for each Swiss-Prot protein,
which trait classes it carries + its GO/EC — to drive **trait↔function
correlation**, **decision-tree function prediction**, and **multi-trait-family
clustering**. This phase builds the pipeline and the pilot dataset, and shows the
correlation + clustering signal is real.

## What was built
- **`ProteinProfile` schema class** (+ `ProfileTrait`): a per-protein record —
  accession, taxon, length, `go_terms`, `ec_numbers`, and `traits[]` (the corpus
  trait classes carried, each with its axis/category and the `via` cross-reference
  that matched). Complements the trait-class corpus (one YAML per trait), doesn't
  replace it. Validated with `linkml-validate --target-class ProteinProfile`.
- **`scripts/build_swissprot_profiles.py`** (`just build-profiles`): indexes the
  corpus into **193,846 groundable trait classes** (Pfam/InterPro/CATH/PROSITE/
  SMART/CDD/NCBIfam/GO/EC), streams a Swiss-Prot slice from the UniProtKB REST API,
  and resolves each entry's signatures/classifications to corpus traits. Emits
  `data/profiles/<acc>.yaml` + a consolidated `profiles.jsonl` (the protein×trait
  matrix).

## Pilot dataset (1,000 reviewed human proteins)
| metric | value |
|---|--:|
| proteins profiled | 1,000 |
| carrying ≥1 corpus trait | **1,000 (100%)** |
| mean traits / protein | **30.0** |
| trait matches by axis | FUNCTION 19,854 · SEQUENCE 8,570 · STRUCTURE 1,537 |
| distinct traits · GO terms | 11,573 · 6,058 |

Every protein resolved to corpus traits — the trait vocabulary covers Swiss-Prot
richly, and each protein carries traits across all three axes (the multi-axis link
the alignment overlays capture, now per-protein).

## Signal 1 — sequence/structure trait → function (GO) correlation
Signature traits predict molecular function with confidence 1.00 (`P(GO | trait)`,
trait on ≥8 proteins):
| signature trait | → GO function | conf (n) |
|---|---|---|
| `Pfam:PF00069` / `PROSITE:PS50011` / `CATH:1.10.510.10` (protein kinase) | `GO:0005524` ATP binding | 1.00 (23–40) |
| `InterPro:IPR001356` (homeobox) | `GO:0000981` DNA-binding TF activity + `GO:0000785` chromatin | 1.00 (24) |

The kinase domain (sequence signature) → ATP binding, and homeobox → transcription
factor, fall straight out — a working baseline for "predict function from traits."

## Signal 2 — multi-trait families (domain-architecture clusters)
Clustering proteins by their **identical signature-trait architecture** (≥2 shared
Pfam/InterPro/CATH/… traits) gives 45 families in the pilot, e.g.:
- **6 proteins** — GPCR: `Pfam:PF00001` (7TM) + `CATH:1.20.1070.10` + `PROSITE:PS00237`.
- **5 proteins** — homeobox: `InterPro:IPR001356` + `CDD:cd00086` + `CATH:1.10.10.60`.
- **4 proteins** — EF-hand: `InterPro:IPR002048` + `CDD:cd00051` + `CATH:1.10.238.10`.

These are real, interpretable protein families derived purely from shared trait sets
— the "multi-trait family" baseline the issue targets.

## Next (phase 2+)
- **Scale**: `just build-profiles --query "reviewed:true" --limit N` over all
  Swiss-Prot (~570k); the trait index is cached, so scaling is a streamed crawl.
  Decide whether the full profile set is committed or a gitignored data artifact.
- **Decision tree / function prediction**: train on `profiles.jsonl` (traits →
  GO-MF) — the confidence-1.0 associations above are the leaves.
- **Formal clustering**: replace exact-architecture matching with trait-set
  similarity (Jaccard / the doi:10.1186/s12859-022-05093-z method) for fuzzy
  families; add UMAP/PaCMAP of the protein×trait matrix to the browser.
- **Feature correlation**: sequence-feature → structural-trait co-occurrence (does a
  given motif always co-occur with a given fold), across axes.

## Gate
`linkml-validate --target-class ProteinProfile` on the emitted profiles → No issues
found. Recipe: `just build-profiles`; cache gitignored (`data/raw/profiles_cache/`).
