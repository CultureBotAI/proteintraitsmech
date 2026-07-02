---
layout: default
title: ProteinTraitsMech
---

# ProteinTraitsMech

Knowledge base of **protein sequence, structure, and function traits** — one YAML per trait, LinkML-validated, evidence-backed. Part of the [CultureBotAI](https://culturebotai.github.io/) family; sibling to [dismech](https://github.com/monarch-initiative/dismech) (disease mechanisms) and TraitMech (microbial ecophysiological traits).

<a href="browse.html" style="display:block;padding:1rem 1.25rem;margin:1rem 0 1.5rem;border:1px solid #159957;border-radius:8px;background:linear-gradient(120deg,#159957,#155799);color:#fff;text-decoration:none;box-shadow:0 2px 8px rgba(15,23,42,.10)">
  <strong style="font-size:1.05rem">🔎 Browse the corpus</strong><br>
  <span style="opacity:.9">Faceted search over 69,401 ProteinTraitRecords — filter by axis / category / source, then open any record for a rendered detail view.</span>
</a>

- **CultureBotAI** — [culturebotai.github.io](https://culturebotai.github.io/)
- **Repository** — [github.com/CultureBotAI/proteintraitsmech](https://github.com/CultureBotAI/proteintraitsmech)
- **Schema** — [`src/proteintraitsmech/schema/proteintraitsmech.yaml`](https://github.com/CultureBotAI/proteintraitsmech/blob/main/src/proteintraitsmech/schema/proteintraitsmech.yaml) · overview on [Schema page](schema.html)
- **Worked example** — [P25888 corpus (20 records across all four axes)](example.html)

## Corpus at a glance

| Source | Records | Directory |
|---|---:|---|
| LinkML `LocalStructuralFeature` valueset | 19 | `data/traits/structure/{secondary,active_site,binding_site,cavity,disulfide,metal_site,dynamics,interface}/` |
| PROSITE PATTERN (generic) | 1,279 | `data/traits/sequence/pattern/` |
| PROSITE PATTERN routed to PTM subtypes | 32 | `data/traits/sequence/{modified_residue,glycosylation,crosslink}/` |
| PROSITE MATRIX (profile) | 1,434 | `data/traits/sequence/profile/` |
| PROSITE ProRule (`DC=Domain`) | 1,445 | `data/traits/structure/domain/` |
| PROSITE ProRule (`DC=Site`, keyword-routed) | 4 | `data/traits/sequence/{modified_residue,glycosylation,prorule}/` |
| TED novel folds (Zenodo v5) | 7,427 | `data/traits/structure/fold/novel/` |
| TED highly-symmetric folds | 6,433 | `data/traits/structure/fold/high_symmetry/` |
| UniProtKB FT + CC + GO (demo: B0R5N7, P25888) | 38 | `data/traits/{sequence,structure,mixed,function}/…` |
| PSI-MOD (CC-BY-4.0) | 1,971 | `data/traits/sequence/{modified_residue,glycosylation,lipidation,crosslink,ptm_ontology}/` |
| ECOD v295 (A/X/H/T/F hierarchy) | 45,113 | `data/traits/structure/{architecture,homologous_superfamily,topology,fold/ecod}/` |
| M-CSA (CC-BY-4.0) | 1,003 | `data/traits/structure/active_site/mcsa/` |
| DisProt (CC-BY-4.0) | 3,199 | `data/traits/sequence/disorder/` |
| **Total** | **69,401** | |

## Trait axes

- **SEQUENCE** — motifs, signal peptides, propeptides, cleavage sites, low-complexity / disordered regions, tandem repeats, compositional biases, conserved regions, epitopes, PTM sites.
- **STRUCTURE** — folds, structural domains, secondary-structure arrangements, topology classes, quaternary state, subunit interfaces, active / binding / allosteric / metal sites, disulfide bonds, cavities, symmetry, dynamics, structural stability.
- **SEQUENCE_STRUCTURE** — transmembrane spans, coiled coils, structural tandem repeats.
- **FUNCTION** — enzymatic activity, binding capacity, cofactor requirement, subcellular localisation, environmental response, interaction partner. Grounded by EC / Rhea / ChEBI / GO / UniProt SubCell.

## Quick start

```bash
just install                  # uv sync --extra dev
just gen-schema               # LinkML → Python dataclasses
just validate-all             # closed-mode LinkML validation over every YAML
```

Seed pipelines:

```bash
just fetch-prosite  &&  just seed-prosite  --apply
just fetch-ted      &&  just seed-ted      --apply
just seed-lsf --apply
just seed-uniprot --accession P25888 --apply
```

All seeded records land with `mapping_status: SEEDED`; curator review flips them to `REVIEWED` and adds `evidence` blocks + `causal_graphs`.

## Curation model

Every record is a stand-alone YAML with:

- `identifier` (CURIE — anchored to the source resource when possible, `proteintraitsmech:` for curator-minted)
- `label` and `definition` (with `definition_source` provenance)
- `trait_axis` + `trait_category` (see [schema](schema.html))
- `parent_traits`, `xrefs`, `synonyms`
- optional `sequence_pattern` (raw PROSITE / regex syntax)
- optional `canonical_examples` (UniProtKB exemplars + NCBITaxon)
- optional evidence-backed `causal_graphs` (nodes + edges, each edge with ≥1 citation)
- append-only `curation_history`

## License

CC0-1.0 for the schema and curated records. Upstream sources retain their own licences — see [`data/raw/README.md`](https://github.com/CultureBotAI/proteintraitsmech/blob/main/data/raw/README.md).
