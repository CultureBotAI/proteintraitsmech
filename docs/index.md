---
layout: default
title: ProteinTraitsMech
---

# ProteinTraitsMech

<div style="display:flex;flex-wrap:wrap;gap:.75rem;margin:1rem 0 1.5rem">
  <a href="browse.html" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #155799;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#155799">200,658</div>
    <div style="font-size:.85rem;color:#57606a">Total records</div>
  </a>
  <a href="browse.html#axis=STRUCTURE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #16a34a;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#16a34a">145,508</div>
    <div style="font-size:.85rem;color:#57606a">STRUCTURE</div>
  </a>
  <a href="browse.html#axis=SEQUENCE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #2563eb;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#2563eb">10,968</div>
    <div style="font-size:.85rem;color:#57606a">SEQUENCE</div>
  </a>
  <a href="browse.html#axis=SEQUENCE_STRUCTURE" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #a855f7;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#a855f7">314</div>
    <div style="font-size:.85rem;color:#57606a">SEQUENCE_STRUCTURE</div>
  </a>
  <a href="browse.html#axis=FUNCTION" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #d97706;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#d97706">43,737</div>
    <div style="font-size:.85rem;color:#57606a">FUNCTION</div>
  </a>
  <a href="browse.html#axis=EVOLUTION" style="flex:1 1 130px;padding:.9rem 1rem;border:1px solid #d0d7de;border-left:4px solid #0d9488;border-radius:8px;background:#fff;color:inherit;text-decoration:none">
    <div style="font-size:1.7rem;font-weight:700;line-height:1.1;color:#0d9488">9</div>
    <div style="font-size:.85rem;color:#57606a">EVOLUTION</div>
  </a>
</div>

Knowledge base of **protein sequence, structure, and function traits** — one YAML per trait, LinkML-validated, evidence-backed. Part of the [CultureBotAI](https://culturebotai.github.io/) family; sibling to [dismech](https://github.com/monarch-initiative/dismech) (disease mechanisms) and [TraitMech](https://culturebotai.github.io/TraitMech/) (microbial ecophysiological traits).

<a href="browse.html" style="display:block;padding:1rem 1.25rem;margin:1rem 0 1.5rem;border:1px solid #159957;border-radius:8px;background:linear-gradient(120deg,#159957,#155799);color:#fff;text-decoration:none;box-shadow:0 2px 8px rgba(15,23,42,.10)">
  <strong style="font-size:1.05rem">🔎 Browse the corpus</strong><br>
  <span style="opacity:.9">Faceted search over 200,658 ProteinTraitRecords — filter by axis / category / source, then open any record for a rendered detail view.</span>
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
| CATH-Gene3D hierarchy — Class/Architecture/Topology/Homologous-superfamily (CC-BY 4.0) | [8,151](browse.html#src=CATH) | `data/traits/structure/{class,architecture,topology,homologous_superfamily}/cath/` |
| SCOPe 2.08 — Class/Fold/Superfamily/Family/Domain (Berkeley; instances px/sp excluded) | [22,810](browse.html#src=SCOPe) | `data/traits/structure/{class,fold,homologous_superfamily,domain}/scope/` |
| Reactome pathways — Homo sapiens reference set (CC0) | [2,883](browse.html#src=Reactome) | `data/traits/function/pathway/reactome/` |
| CARD/ARO — antibiotic-resistance determinants + mechanisms (CC-BY 4.0) | [7,451](browse.html#src=CARD/ARO) | `data/traits/function/resistance/aro/` |
| InterPro entries — Domain / Homologous-superfamily / Repeat / Conserved-/Active-/Binding-site / PTM (public domain; GO via interpro2go → mapped_xrefs) | [26,264](browse.html#src=InterPro) | `data/traits/{structure,sequence}/…/interpro/` |
| Pfam-A families — Domain/Family→domain, Repeat, Coiled-coil, Disordered, Motif (public domain; GO+InterPro via pfam2go/pfam2interpro → mapped_xrefs) | [30,134](browse.html#src=Pfam) | `data/traits/{structure/domain,sequence/repeat,mixed/coiled_coil,sequence/disorder,sequence/motif}/pfam/` |
| M-CSA (CC-BY-4.0) | [1,003](browse.html#src=M-CSA) | `data/traits/structure/active_site/mcsa/` |
| DisProt (CC-BY-4.0) | [3,199](browse.html#src=DisProt) | `data/traits/sequence/disorder/` |
| PSI-MI interaction types (CC-BY-4.0) | [146](browse.html#src=PSI-MI) | `data/traits/function/interaction_partner/psi_mi/` |
| METPO ecophysiological traits (growth preferences, tolerances, metabolism; CC-BY-4.0) | [118](browse.html#src=METPO) | `data/traits/function/{environmental_response,enzymatic_activity}/metpo/` |
| PATO physicochemical qualities (CC-BY-4.0) | [28](browse.html#src=PATO) | `data/traits/structure/{stability,dynamics,surface}/pato/` |
| Curated stability taxonomy — per-condition (thermal, oxidative, saline, pH, osmotic, pressure, desiccation, chemical, proteolytic, mechanical) × increased/decreased (CC0-1.0) | [33](browse.html#src=curated) | `data/traits/structure/stability/conditions/` |
| Curated evolutionary / pangenome traits — conserved, clade-specific, variable; pangenome core/soft-core/shell/cloud/persistent/singleton (CC0-1.0) | [9](browse.html#src=curated) | `data/traits/evolution/{conservation,pangenome}/` |
| TCDB transport classification — Class/Subclass/Family (CC-BY-SA 3.0; 946 families ChEBI-grounded) | [2,285](browse.html#src=TCDB) | `data/traits/function/transport/tcdb/` |
| COG 2020 orthologous groups + 26 functional categories (US Gov public domain) | [4,903](browse.html#src=COG) | `data/traits/function/ortholog_group/cog/` |
| Rhea reactions — enzymatic reactions + ChEBI participants (CC-BY 4.0; EC via rhea2ec) | [18,558](browse.html#src=Rhea) | `data/traits/function/enzymatic_activity/rhea/` |
| ExPASy ENZYME — complete EC hierarchy (CC-BY 4.0; GO/RHEA mapped, KEGG direct, DR examples) | [7,375](browse.html#src=ExPASy%20ENZYME) | `data/traits/function/enzymatic_activity/ec/` |
| RepeatsDB — structural tandem-repeat Class/Topology/Fold/Clan (CC-BY 4.0) | [122](browse.html#src=RepeatsDB) | `data/traits/sequence_structure/structural_repeat/repeatsdb/` |
| **Total** | **[200,658](browse.html)** | |

*Bucket counts are seeding-time figures. Four duplicate PROSITE records (a ProRule / pattern copy that was routed to two directories) have since been consolidated via the [`merge-traits`](https://github.com/CultureBotAI/proteintraitsmech/tree/main/.claude/skills/merge-traits) skill, so per-bucket rows may slightly exceed the live total.*

## Trait categories

Every record carries a fine-grained `trait_category`. Counts link into the [browser](browse.html) pre-filtered to that subset.

| Category | Axis | Records |
|---|---|---:|
| `STRUCT_DOMAIN` | STRUCTURE | [64,279](browse.html#cat=STRUCT_DOMAIN) |
| `STRUCT_FOLD` | STRUCTURE | [55,735](browse.html#cat=STRUCT_FOLD) |
| `FUNC_ENZYMATIC_ACTIVITY` | FUNCTION | [26,009](browse.html#cat=FUNC_ENZYMATIC_ACTIVITY) |
| `STRUCT_HOMOLOGOUS_SUPERFAMILY` | STRUCTURE | [18,687](browse.html#cat=STRUCT_HOMOLOGOUS_SUPERFAMILY) |
| `FUNC_RESISTANCE` | FUNCTION | [7,451](browse.html#cat=FUNC_RESISTANCE) |
| `STRUCT_TOPOLOGY` | STRUCTURE | [5,427](browse.html#cat=STRUCT_TOPOLOGY) |
| `FUNC_ORTHOLOG_GROUP` | FUNCTION | [4,903](browse.html#cat=FUNC_ORTHOLOG_GROUP) |
| `SEQ_DISORDER` | SEQUENCE | [3,366](browse.html#cat=SEQ_DISORDER) |
| `FUNC_PATHWAY` | FUNCTION | [2,883](browse.html#cat=FUNC_PATHWAY) |
| `SEQ_MOTIF` | SEQUENCE | [2,849](browse.html#cat=SEQ_MOTIF) |
| `FUNC_TRANSPORT` | FUNCTION | [2,285](browse.html#cat=FUNC_TRANSPORT) |
| `SEQ_REPEAT` | SEQUENCE | [1,950](browse.html#cat=SEQ_REPEAT) |
| `SEQ_PTM_SITE` | SEQUENCE | [1,211](browse.html#cat=SEQ_PTM_SITE) |
| `STRUCT_ACTIVE_SITE` | STRUCTURE | [1,137](browse.html#cat=STRUCT_ACTIVE_SITE) |
| `SEQ_CONSERVATION` | SEQUENCE | [775](browse.html#cat=SEQ_CONSERVATION) |
| `SEQ_MODIFIED_RESIDUE` | SEQUENCE | [618](browse.html#cat=SEQ_MODIFIED_RESIDUE) |
| `MIXED_COILED_COIL` | SEQUENCE_STRUCTURE | [314](browse.html#cat=MIXED_COILED_COIL) |
| `FUNC_INTERACTION_PARTNER` | FUNCTION | [148](browse.html#cat=FUNC_INTERACTION_PARTNER) |
| `MIXED_STRUCTURAL_REPEAT` | SEQUENCE_STRUCTURE | [122](browse.html#cat=MIXED_STRUCTURAL_REPEAT) |
| `SEQ_GLYCOSYLATION_SITE` | SEQUENCE | [85](browse.html#cat=SEQ_GLYCOSYLATION_SITE) |
| `STRUCT_BINDING_SITE` | STRUCTURE | [84](browse.html#cat=STRUCT_BINDING_SITE) |
| `SEQ_CROSSLINK_SITE` | SEQUENCE | [69](browse.html#cat=SEQ_CROSSLINK_SITE) |
| `STRUCT_ARCHITECTURE` | STRUCTURE | [64](browse.html#cat=STRUCT_ARCHITECTURE) |
| `FUNC_ENVIRONMENTAL_RESPONSE` | FUNCTION | [50](browse.html#cat=FUNC_ENVIRONMENTAL_RESPONSE) |
| `SEQ_LIPIDATION_SITE` | SEQUENCE | [40](browse.html#cat=SEQ_LIPIDATION_SITE) |
| `STRUCT_STABILITY` | STRUCTURE | [36](browse.html#cat=STRUCT_STABILITY) |
| `STRUCT_CLASS` | STRUCTURE | [17](browse.html#cat=STRUCT_CLASS) |
| `STRUCT_DYNAMICS` | STRUCTURE | [13](browse.html#cat=STRUCT_DYNAMICS) |
| `STRUCT_SURFACE` | STRUCTURE | [13](browse.html#cat=STRUCT_SURFACE) |
| `STRUCT_SECONDARY` | STRUCTURE | [8](browse.html#cat=STRUCT_SECONDARY) |
| `STRUCT_CAVITY` | STRUCTURE | [5](browse.html#cat=STRUCT_CAVITY) |
| `FUNC_LOCALIZATION` | FUNCTION | [4](browse.html#cat=FUNC_LOCALIZATION) |
| `FUNC_BINDING_CAPACITY` | FUNCTION | [3](browse.html#cat=FUNC_BINDING_CAPACITY) |
| `SEQ_COMPOSITION` | SEQUENCE | [3](browse.html#cat=SEQ_COMPOSITION) |
| `SEQ_MATURE_CHAIN` | SEQUENCE | [2](browse.html#cat=SEQ_MATURE_CHAIN) |
| `EVO_CLADE_SPECIFIC` | EVOLUTION | [1](browse.html#cat=EVO_CLADE_SPECIFIC) |
| `EVO_CONSERVED` | EVOLUTION | [1](browse.html#cat=EVO_CONSERVED) |
| `EVO_PANGENOME_CLOUD` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_CLOUD) |
| `EVO_PANGENOME_CORE` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_CORE) |
| `EVO_PANGENOME_PERSISTENT` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_PERSISTENT) |
| `EVO_PANGENOME_SHELL` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_SHELL) |
| `EVO_PANGENOME_SINGLETON` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_SINGLETON) |
| `EVO_PANGENOME_SOFTCORE` | EVOLUTION | [1](browse.html#cat=EVO_PANGENOME_SOFTCORE) |
| `EVO_VARIABLE` | EVOLUTION | [1](browse.html#cat=EVO_VARIABLE) |
| `FUNC_COFACTOR_REQUIREMENT` | FUNCTION | [1](browse.html#cat=FUNC_COFACTOR_REQUIREMENT) |
| `STRUCT_DISULFIDE` | STRUCTURE | [1](browse.html#cat=STRUCT_DISULFIDE) |
| `STRUCT_INTERFACE` | STRUCTURE | [1](browse.html#cat=STRUCT_INTERFACE) |
| `STRUCT_METAL_SITE` | STRUCTURE | [1](browse.html#cat=STRUCT_METAL_SITE) |

## Trait axes

- **SEQUENCE** — motifs, signal peptides, propeptides, cleavage sites, low-complexity / disordered regions, tandem repeats, compositional biases, conserved regions, epitopes, PTM sites.
- **STRUCTURE** — folds, structural domains, secondary-structure arrangements, topology classes, quaternary state, subunit interfaces, active / binding / allosteric / metal sites, disulfide bonds, cavities, symmetry, dynamics, structural stability.
- **SEQUENCE_STRUCTURE** — traits with both a sequence signature and 3D periodicity: coiled coils, and structural tandem repeats with demonstrated periodicity (RepeatsDB Class/Topology/Fold/Clan → `MIXED_STRUCTURAL_REPEAT`). *(InterPro Repeat entries assert periodicity only in sequence, so they remain `SEQ_REPEAT`; per-protein transmembrane spans are not seeded.)*
- **FUNCTION** — enzymatic activity, binding capacity, cofactor requirement, subcellular localisation, environmental response, interaction partner. Grounded by EC / Rhea / ChEBI / GO / UniProt SubCell.
- **EVOLUTION** — comparative-genomics / phylogenomic traits: a protein's conservation and distribution across taxa (conserved, clade-specific, variable) and pangenome partition (core, soft-core, shell, cloud, persistent, singleton). Taxon scope, when relevant, via an NCBITaxon xref.

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
