# ProteinTraitsMech

Knowledge base of protein **sequence** and **structure** traits, curated one YAML per trait with evidence-backed causal graphs.

Sibling to [dismech](https://github.com/monarch-initiative/dismech) (disease mechanisms), [TraitMech](../TraitMech) (microbial ecophysiological traits), CultureMech (growth media), and MediaIngredientMech (chemical ingredients). Same curation model: one YAML per record, LinkML-validated, provenance + audit trail, optional evidence-bearing causal mechanism graphs.

## Scope

ProteinTraitsMech covers traits along two axes:

- **SEQUENCE** — motifs, signal peptides, propeptides, cleavage sites, low-complexity / disordered regions, tandem repeats, compositional biases, conserved regions, epitopes, PTM sites.
- **STRUCTURE** — folds, structural domains, secondary-structure arrangements, topology classes, quaternary state, subunit interfaces, active / binding / allosteric / metal sites, disulfide bonds, cavities, symmetry, dynamics, structural stability, surface properties.
- **SEQUENCE_STRUCTURE** (mixed) — traits meaningful in both axes: transmembrane spans, coiled coils, structural tandem repeats.

Records anchor to authoritative resources: Pfam, InterPro, PROSITE, SMART, MEROPS, CATH, SCOP, PDB, GO, PR, UniProtKB.

## Quick start

```bash
just install                  # uv sync --extra dev
just gen-schema               # generate dataclasses from LinkML
just validate-all             # validate every ProteinTraitRecord YAML
```

## Schema

`src/proteintraitsmech/schema/proteintraitsmech.yaml` defines:

- **ProteinTraitRecord** — root class, one per YAML file. Carries `identifier` (preferably an existing InterPro / Pfam / PROSITE / CATH / SCOP / MEROPS / PR CURIE), `label`, `definition`, `parent_traits`, `xrefs`, `synonyms`, `trait_axis` (SEQUENCE / STRUCTURE / SEQUENCE_STRUCTURE), `trait_category`, `term_kind`, optional `canonical_examples`, optional `evidence`, optional `curation_history`, and optional inline `causal_graphs`.
- **CausalGraph / CausalNode / CausalEdge** — evidence-backed causal mechanism graphs. Nodes represent proteins, domains, motifs, residues, PTMs, ligands, pathways, molecular functions, biological processes, phenotypes, or diseases. Every `CausalEdge` must carry at least one `EvidenceItem`.
- **CanonicalExample** — reference exemplar proteins (UniProtKB accession + taxon) that archetypally exhibit the trait.
- **TraitSynonym / EvidenceItem / CurationEvent** — ancillary classes.
- **TraitAxisEnum** — `SEQUENCE` / `STRUCTURE` / `SEQUENCE_STRUCTURE`.
- **ProteinTraitCategoryEnum** — `SEQ_*`, `STRUCT_*`, `MIXED_*` fine-grained buckets (see schema for the full list).
- **TermKindEnum** — `CLASS` / `DATATYPE_PROPERTY` / `OBJECT_PROPERTY` / `ANNOTATION_PROPERTY`.
- **MappingStatusEnum** — `SEEDED` / `PROPOSED` / `REVIEWED` / `DEPRECATED`.
- **PriorityEnum**, **SynonymTypeEnum**, **CausalNodeTypeEnum**.

## Layout

```
ProteinTraitsMech/
├── data/
│   ├── raw/                                     # vendored source releases (Pfam, InterPro, CATH, SCOP, MEROPS, …)
│   └── traits/
│       ├── sequence/<category>/<slug>.yaml
│       ├── structure/<category>/<slug>.yaml
│       └── mixed/<category>/<slug>.yaml
├── src/proteintraitsmech/
│   └── schema/proteintraitsmech.yaml            # LinkML schema
├── scripts/                                     # seed / validate / audit tooling
├── tests/
└── docs/
```

## Workflow

1. **Seed** — import candidate traits from an authoritative resource (Pfam / InterPro / PROSITE / CATH / SCOP / MEROPS). Seeded records land with `mapping_status: SEEDED` and axis + category inferred from the source.
2. **Curate** — edit `data/traits/<axis>/<category>/<slug>.yaml` directly; set `mapping_status: REVIEWED`, append a `CurationEvent`, attach `EvidenceItem` blocks with PMID / DOI + verbatim snippet.
3. **Add causal graphs** — attach `causal_graphs` when the trait has source-backed mechanism structure (e.g. "this active-site residue coordinates the substrate carbonyl"). Every `CausalEdge` must carry edge-level `evidence`; prefer grounded CURIEs for nodes and predicates (RO for predicates; PR / GO / CHEBI / MOD / HP / MONDO for nodes).
4. **Validate** — `just validate-all` runs closed-mode LinkML validation over every record.

## Seeds

| Source | Records | Bucket |
| --- | ---: | --- |
| [LinkML `LocalStructuralFeature`](https://linkml.io/valuesets/elements/LocalStructuralFeature/) | 19 | `data/traits/structure/{secondary,active_site,binding_site,cavity,disulfide,metal_site,dynamics,interface}/` |
| [PROSITE patterns](https://prosite.expasy.org/) (`prosite.dat`, PATTERN) | 1311 | `data/traits/sequence/pattern/` and `data/traits/sequence/ptm_site/` (31 PTM-flagged) |
| [PROSITE profiles](https://prosite.expasy.org/) (`prosite.dat`, MATRIX) | 1434 | `data/traits/sequence/profile/` |
| [PROSITE ProRules](https://prosite.expasy.org/) (`prorule.dat`) | 1449 | `data/traits/structure/domain/` (1445) + `data/traits/sequence/prorule/` (4 Site rules) |
| [TED novel folds](https://ted.cathdb.info/) (Zenodo v5, [DOI:10.5281/zenodo.13908086](https://doi.org/10.5281/zenodo.13908086), CC-BY 4.0) | 7427 | `data/traits/structure/fold/novel/` |
| [TED highly-symmetric folds](https://ted.cathdb.info/) (same Zenodo record) | 6433 | `data/traits/structure/fold/high_symmetry/` |
| [UniProtKB](https://www.uniprot.org/) FT lines (per-accession, demo seed) | 18 (2 entries) | `data/traits/{sequence,structure,mixed}/…` per FT type |

Refetch and re-seed:

```bash
just fetch-prosite            # writes data/raw/prosite.dat + prorule.dat (gitignored)
just fetch-ted                # writes data/raw/ted_*.tsv.gz (gitignored)
just seed-lsf --apply         # 19 LinkML LocalStructuralFeature records
just seed-prosite --apply     # 4194 PROSITE records; idempotent, skips existing
just seed-ted --apply         # 13860 TED fold records; idempotent

# UniProtKB FT-line seed — pass accessions or a local flat file
just seed-uniprot --accession B0R5N7 --accession P25888 --apply
```

UniProtKB supported FT types → axis / category:

| UniProt FT type | Axis | Category | Notes |
|---|---|---|---|
| `TRANSMEM`, `INTRAMEM` | SEQUENCE_STRUCTURE | `MIXED_TRANSMEMBRANE` | one record per span |
| `SIGNAL` / `PROPEP` | SEQUENCE | `SEQ_SIGNAL_PEPTIDE` / `SEQ_PROPEPTIDE` | |
| `REGION` /note="Disordered" | SEQUENCE | `SEQ_DISORDER` | other `REGION` free-text is skipped |
| `COMPBIAS` | SEQUENCE | `SEQ_COMPOSITION` | `/note` carries residue class (Gly-rich, basic, acidic, …) |
| `MOTIF` | SEQUENCE | `SEQ_MOTIF` | curator-defined; overlaps with PROSITE where cross-referenced |
| `MOD_RES`, `LIPID`, `CARBOHYD`, `CROSSLNK` | SEQUENCE | `SEQ_PTM_SITE` | |
| `DOMAIN` | STRUCTURE | `STRUCT_DOMAIN` | |
| `ACT_SITE` | STRUCTURE | `STRUCT_ACTIVE_SITE` | |
| `SITE` | STRUCTURE | `STRUCT_BINDING_SITE` | |
| `BINDING` (non-metal ligand) | STRUCTURE | `STRUCT_BINDING_SITE` | ligand ChEBI added to `xrefs` |
| `BINDING` (metal ligand) / `METAL` | STRUCTURE | `STRUCT_METAL_SITE` | metal keyword detection on `/ligand` + `/ligand_note` |
| `DISULFID` | STRUCTURE | `STRUCT_DISULFIDE` | |
| `HELIX`, `STRAND`, `TURN` | STRUCTURE | `STRUCT_SECONDARY` | requires an experimental structure in the entry |

Skipped (out-of-scope for this schema): `CHAIN`, `INIT_MET`, `TRANSIT`, `VARIANT`, `VAR_SEQ`, `MUTAGEN`, `CONFLICT`, `UNSURE`, `NON_CONS`, `NON_TER`, `NON_STD`, `PEPTIDE`.

All seeded records land with `mapping_status: SEEDED`; curator review flips them to `REVIEWED` and adds evidence / causal graphs.

## License

CC0-1.0 — Public Domain Dedication.
