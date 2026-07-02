---
layout: default
title: ProteinTraitsMech
---

# ProteinTraitsMech

<div style="display:flex;flex-wrap:wrap;gap:.75rem;margin:1rem 0 1.5rem">
  <a href="browse.html" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #155799;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#155799">95,977</div>
    <div style="font-size:.85rem;color:#57606a">Total records</div>
  </a>
  <a href="browse.html#axis=STRUCTURE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #16a34a;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#16a34a">86,586</div>
    <div style="font-size:.85rem;color:#57606a">STRUCTURE</div>
  </a>
  <a href="browse.html#axis=SEQUENCE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #2563eb;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#2563eb">7,931</div>
    <div style="font-size:.85rem;color:#57606a">SEQUENCE</div>
  </a>
  <a href="browse.html#axis=FUNCTION" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #d97706;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#d97706">282</div>
    <div style="font-size:.85rem;color:#57606a">FUNCTION</div>
  </a>
  <a href="browse.html#axis=SEQUENCE_STRUCTURE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #a855f7;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#a855f7">390</div>
    <div style="font-size:.85rem;color:#57606a">SEQUENCE_STRUCTURE</div>
  </a>
</div>

Knowledge base of **protein sequence, structure, and function traits** — one YAML per trait, LinkML-validated, evidence-backed. Part of the [CultureBotAI](https://culturebotai.github.io/) family; sibling to [dismech](https://github.com/monarch-initiative/dismech) (disease mechanisms) and TraitMech (microbial ecophysiological traits).

<a href="browse.html" style="display:block;padding:1rem 1.25rem;margin:1rem 0 1.5rem;border:1px solid #159957;border-radius:8px;background:linear-gradient(120deg,#159957,#155799);color:#fff;text-decoration:none;box-shadow:0 2px 8px rgba(15,23,42,.10)">
  <strong style="font-size:1.05rem">🔎 Browse the corpus</strong><br>
  <span style="opacity:.9">Faceted search over 95,977 ProteinTraitRecords — filter by axis / category / source, then open any record for a rendered detail view.</span>
</a>

- **CultureBotAI** — [culturebotai.github.io](https://culturebotai.github.io/)
- **Repository** — [github.com/CultureBotAI/proteintraitsmech](https://github.com/CultureBotAI/proteintraitsmech)
- **Schema** — [`src/proteintraitsmech/schema/proteintraitsmech.yaml`](https://github.com/CultureBotAI/proteintraitsmech/blob/main/src/proteintraitsmech/schema/proteintraitsmech.yaml) · overview on [Schema page](schema.html)
- **Worked example** — [P25888 corpus (20 records across all four axes)](example.html)

## Corpus at a glance

Record counts link into the [browser](browse.html) filtered by `source`. PROSITE and TED are broken into buckets by row, but each links to its full source set (the browser facets by source, not by bucket).

| Source | Records | Directory |
|---|---:|---|
| LinkML `LocalStructuralFeature` valueset | [19](browse.html#src=LinkML%20LSF) | `data/traits/structure/{secondary,active_site,binding_site,cavity,disulfide,metal_site,dynamics,interface}/` |
| PROSITE PATTERN (generic) | [1,279](browse.html#src=PROSITE) | `data/traits/sequence/pattern/` |
| PROSITE PATTERN routed to PTM subtypes | [32](browse.html#src=PROSITE) | `data/traits/sequence/{modified_residue,glycosylation,crosslink}/` |
| PROSITE MATRIX (profile) | [1,434](browse.html#src=PROSITE) | `data/traits/sequence/profile/` |
| PROSITE ProRule (`DC=Domain`) | [1,445](browse.html#src=PROSITE) | `data/traits/structure/domain/` |
| PROSITE ProRule (`DC=Site`, keyword-routed) | [4](browse.html#src=PROSITE) | `data/traits/sequence/{modified_residue,glycosylation,prorule}/` |
| TED novel folds (Zenodo v5) | [7,427](browse.html#src=TED) | `data/traits/structure/fold/novel/` |
| TED highly-symmetric folds | [6,433](browse.html#src=TED) | `data/traits/structure/fold/high_symmetry/` |
| UniProtKB FT + CC + GO (demo: B0R5N7, P25888) | [29](browse.html#src=UniProtKB) | `data/traits/{sequence,structure,function}/…` |
| PSI-MOD (CC-BY-4.0) | [1,971](browse.html#src=PSI-MOD) | `data/traits/sequence/{modified_residue,glycosylation,lipidation,crosslink,ptm_ontology}/` |
| ECOD v295 (A/X/H/T/F hierarchy) | [45,113](browse.html#src=ECOD) | `data/traits/structure/{architecture,homologous_superfamily,topology,fold/ecod}/` |
| InterPro entries — Domain / Homologous-superfamily / Repeat / Conserved-/Active-/Binding-site / PTM (public domain) | [26,264](browse.html#src=InterPro) | `data/traits/{structure,sequence,mixed}/…/interpro/` |
| M-CSA (CC-BY-4.0) | [1,003](browse.html#src=M-CSA) | `data/traits/structure/active_site/mcsa/` |
| DisProt (CC-BY-4.0) | [3,199](browse.html#src=DisProt) | `data/traits/sequence/disorder/` |
| PSI-MI interaction types (CC-BY-4.0) | [146](browse.html#src=PSI-MI) | `data/traits/function/interaction_partner/psi_mi/` |
| METPO ecophysiological traits (growth preferences, tolerances, metabolism; CC-BY-4.0) | [118](browse.html#src=METPO) | `data/traits/function/{environmental_response,enzymatic_activity}/metpo/` |
| PATO physicochemical qualities (CC-BY-4.0) | [28](browse.html#src=PATO) | `data/traits/structure/{stability,dynamics,surface}/pato/` |
| Curated stability taxonomy — per-condition (thermal, oxidative, saline, pH, osmotic, pressure, desiccation, chemical, proteolytic, mechanical) × increased/decreased (CC0-1.0) | [33](browse.html#src=curated) | `data/traits/structure/stability/conditions/` |
| **Total** | **[95,977](browse.html)** | |

*Bucket counts are seeding-time figures. Four duplicate PROSITE records (a ProRule / pattern copy that was routed to two directories) have since been consolidated via the [`merge-traits`](https://github.com/CultureBotAI/proteintraitsmech/tree/main/.claude/skills/merge-traits) skill, so per-bucket rows may slightly exceed the live total.*

## Trait categories

Every record carries a fine-grained `trait_category`. Counts link into the [browser](browse.html) pre-filtered to that subset.

| Category | Axis | Records |
|---|---|---:|
| `STRUCT_FOLD` | STRUCTURE | [48,819](browse.html#cat=STRUCT_FOLD) |
| `STRUCT_DOMAIN` | STRUCTURE | [22,804](browse.html#cat=STRUCT_DOMAIN) |
| `STRUCT_HOMOLOGOUS_SUPERFAMILY` | STRUCTURE | [9,688](browse.html#cat=STRUCT_HOMOLOGOUS_SUPERFAMILY) |
| `STRUCT_TOPOLOGY` | STRUCTURE | [3,955](browse.html#cat=STRUCT_TOPOLOGY) |
| `SEQ_DISORDER` | SEQUENCE | [3,200](browse.html#cat=SEQ_DISORDER) |
| `SEQ_MOTIF` | SEQUENCE | [2,716](browse.html#cat=SEQ_MOTIF) |
| `SEQ_PTM_SITE` | SEQUENCE | [1,211](browse.html#cat=SEQ_PTM_SITE) |
| `STRUCT_ACTIVE_SITE` | STRUCTURE | [1,137](browse.html#cat=STRUCT_ACTIVE_SITE) |
| `SEQ_CONSERVATION` | SEQUENCE | [775](browse.html#cat=SEQ_CONSERVATION) |
| `SEQ_MODIFIED_RESIDUE` | SEQUENCE | [618](browse.html#cat=SEQ_MODIFIED_RESIDUE) |
| `MIXED_STRUCTURAL_REPEAT` | SEQUENCE_STRUCTURE | [390](browse.html#cat=MIXED_STRUCTURAL_REPEAT) |
| `FUNC_INTERACTION_PARTNER` | FUNCTION | [148](browse.html#cat=FUNC_INTERACTION_PARTNER) |
| `SEQ_GLYCOSYLATION_SITE` | SEQUENCE | [85](browse.html#cat=SEQ_GLYCOSYLATION_SITE) |
| `STRUCT_BINDING_SITE` | STRUCTURE | [84](browse.html#cat=STRUCT_BINDING_SITE) |
| `FUNC_ENZYMATIC_ACTIVITY` | FUNCTION | [76](browse.html#cat=FUNC_ENZYMATIC_ACTIVITY) |
| `SEQ_CROSSLINK_SITE` | SEQUENCE | [69](browse.html#cat=SEQ_CROSSLINK_SITE) |
| `FUNC_ENVIRONMENTAL_RESPONSE` | FUNCTION | [50](browse.html#cat=FUNC_ENVIRONMENTAL_RESPONSE) |
| `SEQ_LIPIDATION_SITE` | SEQUENCE | [40](browse.html#cat=SEQ_LIPIDATION_SITE) |
| `STRUCT_STABILITY` | STRUCTURE | [36](browse.html#cat=STRUCT_STABILITY) |
| `STRUCT_ARCHITECTURE` | STRUCTURE | [21](browse.html#cat=STRUCT_ARCHITECTURE) |
| `STRUCT_DYNAMICS` | STRUCTURE | [13](browse.html#cat=STRUCT_DYNAMICS) |
| `STRUCT_SURFACE` | STRUCTURE | [13](browse.html#cat=STRUCT_SURFACE) |
| `STRUCT_SECONDARY` | STRUCTURE | [8](browse.html#cat=STRUCT_SECONDARY) |
| `STRUCT_CAVITY` | STRUCTURE | [5](browse.html#cat=STRUCT_CAVITY) |
| `FUNC_LOCALIZATION` | FUNCTION | [4](browse.html#cat=FUNC_LOCALIZATION) |
| `FUNC_BINDING_CAPACITY` | FUNCTION | [3](browse.html#cat=FUNC_BINDING_CAPACITY) |
| `SEQ_COMPOSITION` | SEQUENCE | [3](browse.html#cat=SEQ_COMPOSITION) |
| `SEQ_MATURE_CHAIN` | SEQUENCE | [2](browse.html#cat=SEQ_MATURE_CHAIN) |
| `FUNC_COFACTOR_REQUIREMENT` | FUNCTION | [1](browse.html#cat=FUNC_COFACTOR_REQUIREMENT) |
| `STRUCT_DISULFIDE` | STRUCTURE | [1](browse.html#cat=STRUCT_DISULFIDE) |
| `STRUCT_INTERFACE` | STRUCTURE | [1](browse.html#cat=STRUCT_INTERFACE) |
| `STRUCT_METAL_SITE` | STRUCTURE | [1](browse.html#cat=STRUCT_METAL_SITE) |

## Trait axes

- **SEQUENCE** — motifs, signal peptides, propeptides, cleavage sites, low-complexity / disordered regions, tandem repeats, compositional biases, conserved regions, epitopes, PTM sites.
- **STRUCTURE** — folds, structural domains, secondary-structure arrangements, topology classes, quaternary state, subunit interfaces, active / binding / allosteric / metal sites, disulfide bonds, cavities, symmetry, dynamics, structural stability.
- **SEQUENCE_STRUCTURE** — structural tandem repeats (InterPro Repeat families), coiled coils, transmembrane spans. *(Per-protein transmembrane spans are not seeded — too specific, covered by the general transmembrane trait; the populated records here are repeat-family classes with both a sequence signature and a 3D periodicity.)*
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
