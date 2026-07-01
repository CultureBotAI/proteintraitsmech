---
layout: default
title: Schema — ProteinTraitsMech
---

# Schema

Authoritative source: [`src/proteintraitsmech/schema/proteintraitsmech.yaml`](https://github.com/CultureBotAI/proteintraitsmech/blob/main/src/proteintraitsmech/schema/proteintraitsmech.yaml). This page is a plain-English guide; the LinkML file is the machine-readable contract.

[← back to index](./)

## Root class — `ProteinTraitRecord`

One YAML file per record. Required slots: `identifier`, `label`, `trait_axis`. Recommended: `trait_category`, `definition`, `definition_source`, `mapping_status`.

| Slot | Range | Notes |
|---|---|---|
| `identifier` | CURIE | Prefer source-anchored (e.g. `PROSITE:PS00001`, `TED:AF-…-TED03`, `UniProtKB:P25888`); use `proteintraitsmech:` for curator-minted |
| `label` | string | Human-readable trait label |
| `definition` | string | Text definition (folded scalar) |
| `definition_source` | string | Release stamp or CURIE-style pointer to the source |
| `synonyms` | list of `TraitSynonym` | With `synonym_type: EXACT / NARROW / BROAD / RELATED` |
| `parent_traits` | list of CURIE | `rdfs:subClassOf` parents |
| `xrefs` | list of CURIE | Cross-references to other ontologies / databases |
| `sequence_pattern` | string | Raw PROSITE / ELM / regex syntax (SEQUENCE-axis records only) |
| `canonical_examples` | list of `CanonicalExample` | UniProtKB accession + taxon + note |
| `trait_axis` | `TraitAxisEnum` | See below |
| `trait_category` | `ProteinTraitCategoryEnum` | See below |
| `term_kind` | `TermKindEnum` | `CLASS` / `DATATYPE_PROPERTY` / `OBJECT_PROPERTY` / `ANNOTATION_PROPERTY` |
| `mapping_status` | `MappingStatusEnum` | `SEEDED` / `PROPOSED` / `REVIEWED` / `DEPRECATED` |
| `evidence` | list of `EvidenceItem` | Optional entry-level citation list |
| `causal_graphs` | list of `CausalGraph` | Evidence-backed mechanism graphs |
| `curation_history` | list of `CurationEvent` | Append-only audit trail |

## `TraitAxisEnum`

| Value | Meaning |
|---|---|
| `SEQUENCE` | Trait defined on the linear amino-acid sequence |
| `STRUCTURE` | Trait defined on the 3D structure (fold, contact, geometry) |
| `SEQUENCE_STRUCTURE` | Trait meaningful in both axes — transmembrane spans, coiled coils, structural tandem repeats |
| `FUNCTION` | Entry-level (non-localised) trait — enzymatic activity, binding capacity, cofactor requirement, localisation, environmental response, interaction partner |

## `ProteinTraitCategoryEnum`

### SEQUENCE

Basic segments: `SEQ_MOTIF`, `SEQ_SIGNAL_PEPTIDE`, `SEQ_TRANSIT_PEPTIDE`, `SEQ_PROPEPTIDE`, `SEQ_INITIATOR_METHIONINE`, `SEQ_MATURE_CHAIN`, `SEQ_NONSTANDARD_RESIDUE`, `SEQ_CLEAVAGE_SITE`, `SEQ_LOW_COMPLEXITY`, `SEQ_DISORDER`, `SEQ_REPEAT`, `SEQ_COMPOSITION`, `SEQ_CONSERVATION`, `SEQ_EPITOPE`.

PTM site subtypes (specific — prefer these over the generic bucket): `SEQ_MODIFIED_RESIDUE`, `SEQ_GLYCOSYLATION_SITE`, `SEQ_LIPIDATION_SITE`, `SEQ_CROSSLINK_SITE`.

Generic PTM bucket (use when the modification class is unknown or heterogeneous): `SEQ_PTM_SITE`.

Fallback: `SEQ_OTHER`.

### STRUCTURE

CATH/SCOP hierarchy (top-down): `STRUCT_CLASS`, `STRUCT_ARCHITECTURE`, `STRUCT_TOPOLOGY`, `STRUCT_HOMOLOGOUS_SUPERFAMILY`, `STRUCT_FOLD`, `STRUCT_DOMAIN`.

Local geometry: `STRUCT_SECONDARY`, `STRUCT_QUATERNARY`, `STRUCT_INTERFACE`, `STRUCT_ACTIVE_SITE`, `STRUCT_BINDING_SITE`, `STRUCT_ALLOSTERIC_SITE`, `STRUCT_DISULFIDE`, `STRUCT_METAL_SITE`, `STRUCT_CAVITY`, `STRUCT_SYMMETRY`, `STRUCT_DYNAMICS`, `STRUCT_STABILITY`, `STRUCT_SURFACE`, `STRUCT_OTHER`.

### SEQUENCE_STRUCTURE (mixed)

`MIXED_TRANSMEMBRANE`, `MIXED_COILED_COIL`, `MIXED_STRUCTURAL_REPEAT`, `MIXED_OTHER`.

### FUNCTION

| Category | Grounding |
|---|---|
| `FUNC_ENZYMATIC_ACTIVITY` | EC, Rhea, GO MF `*activity`, participating ChEBIs |
| `FUNC_BINDING_CAPACITY` | GO MF `* binding`, UniProt KW |
| `FUNC_COFACTOR_REQUIREMENT` | ChEBI + UniProt `CC COFACTOR` |
| `FUNC_LOCALIZATION` | UniProt SubCell, GO CC |
| `FUNC_ENVIRONMENTAL_RESPONSE` | GO BP `response_to_*`, UniProt `CC INDUCTION` keyword scan |
| `FUNC_INTERACTION_PARTNER` | UniProt `CC SUBUNIT`, IntAct / BioGRID / STRING |

### Administrative

`UPPER` (organisational parent), `OTHER`.

### Axis / category pairing

`ProteinTraitRecord` carries LinkML `rules` that enforce the category
prefix against the axis:

| Category prefix | Required axis |
|---|---|
| `SEQ_*` | `SEQUENCE` |
| `STRUCT_*` | `STRUCTURE` |
| `MIXED_*` | `SEQUENCE_STRUCTURE` |
| `FUNC_*` | `FUNCTION` |
| `UPPER` / `OTHER` | unconstrained |

`just validate-all` will reject a mismatched pair.

### FUNCTION vs localised STRUCTURE

FUNCTION and STRUCTURE records for the same protein are complementary,
not duplicative. A UniProt entry with an ATP-binding pocket at residues
45–52 emits *both* a `STRUCT_BINDING_SITE` record (localised: *where*
ATP binds) *and* a `FUNC_BINDING_CAPACITY` record (entry-level: *that*
the protein binds ATP). Likewise, a catalytic residue emits both
`STRUCT_ACTIVE_SITE` and `FUNC_ENZYMATIC_ACTIVITY`. The two answer
different questions and are meant to coexist.

## `CausalGraph` / `CausalNode` / `CausalEdge`

Optional inline mechanism graph attached to a record. Every `CausalEdge` requires ≥1 `EvidenceItem` — mechanism assertions are curator-generated and must cite their support.

`CausalNodeTypeEnum` covers `PROTEIN`, `DOMAIN`, `MOTIF`, `RESIDUE`, `PTM`, `LIGAND`, `NUCLEIC_ACID`, `CHEMICAL`, `PATHWAY`, `MOLECULAR_FUNCTION`, `BIOLOGICAL_PROCESS`, `CELLULAR_LOCALIZATION`, `PHENOTYPE`, `DISEASE`, `TRAIT`, `STATE`, `QUALITY`, `ENVIRONMENTAL_FACTOR`, `EXPERIMENTAL_FACTOR`, `OTHER`.

## Prefixes declared in the schema

Ontologies: `PR`, `GO`, `PATO`, `UBERON`, `CL`, `CHEBI`, `RHEA`, `SO`, `UO`, `IAO`, `RO`, `OBI`, `MOD`, `MONDO`, `HP`, `NCBITaxon`.
Databases: `UniProtKB`, `Pfam`, `InterPro`, `PROSITE`, `SMART`, `CATH`, `SCOP`, `MEROPS`, `HAMAP`, `EC`, `KEGG`, `Reactome`, `NCBIGene`, `HGNC`, `TED`, `AlphaFoldDB`, `valuesets`.
Provenance: `PMID`, `DOI`, `dcterms`, `skos`, `biolink`.

[← back to index](./)
