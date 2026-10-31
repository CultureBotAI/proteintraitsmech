---
name: add-record
description: "Review candidate gaps and add new class-level ProteinTraitRecord YAML files under data/traits/ with grounded identifiers, provenance, runnable detection method coverage, and strict LinkML validation."
category: curation
requires_database: false
requires_internet: false
version: 1.0.0
tags: [curation, add-record, yaml, traits, linkml, provenance, seeding]
---

# Add a Protein Trait Record (`add-record`)

Create new class-level `ProteinTraitRecord` YAML files in `data/traits/` for missing protein traits discovered from schema category audits, curated structural/sequence/biophysical taxonomies, literature curation, or cross-Mech trait gap reports.

Use [`curate-yaml-record`](../curate-yaml-record/SKILL.md) when a record already exists on disk and needs enrichment, [`ingest-source`](../ingest-source/SKILL.md) when onboarding a new bulk upstream release via `download.yaml`, and [`ground-protein-example`](../ground-protein-example/SKILL.md) when attaching `UniProtKB` protein carriers to an existing trait record.

---

## Non-Negotiable Invariants

1. **Class-level traits only (`term_kind: CLASS`)**: Every record in `data/traits/` defines a reusable protein trait class, never an individual protein accession (`UniProtKB:...` carriers belong in `canonical_examples` via the release-pinned grounding workflow, never as a `ProteinTraitRecord` `identifier`).
2. **Audited writer route**: Never hand-write unvalidated files into `data/traits/`. Emit new records through an idempotent seeder script (`scripts/seed_*.py`, dry-run by default, `--apply` to write) that calls `record_io.write_record(path, text, validate=True)`. Run `just audit-writers` whenever adding or modifying a writer script.
3. **Runnable detection recipe coverage**: Every added record must resolve to a runnable detection recipe either via its own `detection_methods` slot or through `by_source` / `by_category` in `data/methods/methods.yaml` (`python3 scripts/build_methods.py` and `pytest tests/test_methods_recipes.py`).
4. **License & provenance**: Every record must carry an explicit `definition_source` and a redistribution-compatible `license` (`CC-BY-4.0` or `CC0-1.0`). Do not ingest sources with restrictive or unresolved licensing.

---

## Workflow

### Step 1: Verify Absence & Scope

Before creating any record, verify that the trait does not already exist under a primary `identifier`, `xrefs` entry, or `synonyms` entry:

```bash
# Fast lookup against the indexed label and shard catalogs
.venv/bin/python -c '
import json
labels = json.load(open("docs/data/labels.json"))
for k, v in labels.items():
    if "candidate term" in v.lower() or k == "CANDIDATE:ID":
        print(k, "->", v)
'
```

- If an equivalent record already exists in the same axis, enrich it with [`curate-yaml-record`](../curate-yaml-record/SKILL.md) (adding `synonyms`, `xrefs`, `definitions`, or `evidence`) instead of creating a duplicate.
- To find unpopulated or sparse categories across the schema, compare `ProteinTraitCategoryEnum` in `src/proteintraitsmech/schema/proteintraitsmech.yaml` against `just corpus-stats` or `docs/data/facets.json`.

### Step 2: Assign Axis, Category, Identifier, and Path

Select `trait_axis` and `trait_category` from `src/proteintraitsmech/schema/proteintraitsmech.yaml` according to the representation that defines the trait:

| Directory | `trait_axis` | `trait_category` prefix | Defining representation |
| --- | --- | --- | --- |
| `data/traits/sequence/<category>/` | `SEQUENCE` | `SEQ_*` | Primary amino-acid sequence, motif regex, composition, cleavage/peptide feature, or PTM site |
| `data/traits/structure/<category>/` | `STRUCTURE` | `STRUCT_*` | 3D coordinates, secondary/supersecondary element, fold, symmetry, quaternary assembly, active/binding/allosteric/metal site, cavity, surface, stability, or dynamics |
| `data/traits/sequence_structure/<category>/` | `SEQUENCE_STRUCTURE` | `MIXED_*` | Coupled sequence-structure signatures (intrinsic disorder, transmembrane segment, coiled coil, aggregation/LLPS propensity, antimicrobial peptide, structural PTM) |
| `data/traits/function/<category>/` | `FUNCTION` | `FUNC_*` | Enzymatic reaction, molecular function, biological process, localization, interaction partner, cofactor requirement, transport, resistance, or virulence |
| `data/traits/evolution/<category>/` | `EVOLUTION` | `EVOL_*` | Homologous family/superfamily, orthologous group, clan, taxonomic phyletic profile, or horizontal transfer signature |

**Identifier selection**:
- Prefer an authoritative external CURIE (`GO:`, `SO:`, `MOD:`, `CHEBI:`, `InterPro:`, `Pfam:`, `PROSITE:`, `CATH:`, `EC:`, `RHEA:`, `PATO:`, `ARO:`, `TCDB:`, `ELM:`, `MCSA:`, `ChEMBL:`) when the upstream ontology term has a 1:1 correspondence with the protein trait class.
- Use `proteintraitsmech:<UPPER_SNAKE_ID>` when curating a canonical protein-trait taxonomy node (such as structural symmetry classes, quaternary oligomeric states, compositional bias classes, or biophysical stability tiers) that has no single 1:1 external CURIE; cross-reference related ontology terms (`SO:`, `MOD:`, `CHEBI:`, `GO:`, `PATO:`, `InterPro:`) in `xrefs`.

### Step 3: Populate Schema-Valid Record Fields

Author records through `record_io.write_record(path, text, validate=True)` with the following structure:

```yaml
identifier: proteintraitsmech:NONSTD_SELENOCYSTEINE
label: selenocysteine residue
definition: >-
  Presence of a genetically encoded L-selenocysteine (Sec, U) residue incorporated
  co-translationally at an in-frame UGA codon via a SECIS element and SelB/eEFSec
  elongation factor, typically serving as a nucleophilic redox-active catalytic
  center in selenoenzymes.
definition_source: "UniProtKB feature type NON_STD; Sequence Ontology SO:0001413 (DOI:10.1152/physrev.00030.2013)"
trait_axis: SEQUENCE
trait_category: SEQ_NONSTANDARD_RESIDUE
term_kind: CLASS
mapping_status: SEEDED
synonyms:
  - synonym_text: Sec residue
    synonym_type: EXACT_SYNONYM
    source: IUPAC-IUBMB
  - synonym_text: 21st amino acid residue
    synonym_type: RELATED_SYNONYM
    source: PMID:24070661
xrefs:
  - SO:0001413
  - CHEBI:29999
  - MOD:00044
evidence:
  - reference: PMID:24070661
    snippet: "Selenocysteine (Sec), the 21st amino acid, is inserted into nascent polypeptides at UGA codons with the aid of the SECIS element."
    notes: Establishes the co-translational mechanism and sequence determinants of genetically encoded selenocysteine residues in selenoproteins.
license: CC-BY-4.0
```

**Field checklist**:
- `identifier`, `label`, `definition`, `definition_source`, `trait_axis`, `trait_category`, `term_kind: CLASS`, `mapping_status`, and `license` are present on every record.
- `parent_traits` references existing `identifier` values in `data/traits/` (do not introduce dangling parent edges).
- `synonyms` uses `SynonymEntry` objects (`synonym_text`, `synonym_type` in `EXACT_SYNONYM | BROAD_SYNONYM | NARROW_SYNONYM | RELATED_SYNONYM`, optional `source`).
- `xrefs` uses valid `PREFIX:ACCESSION` CURIE strings (`^[^\s:]+:[^\s:]+$`).
- `evidence` uses `EvidenceItem` objects (`reference` as `PMID:` or `DOI:`, optional `snippet` and `notes`).
- Leave `mapping_status: SEEDED` (or `PROPOSED`); `REVIEWED` is reserved for human sign-off.

### Step 4: Verify Detection Recipes, Baselines, and Governance Gates

After writing new records via `record_io.write_record`:

1. **Closed-mode LinkML validation**:
   ```bash
   .venv/bin/python scripts/validate_strict.py <new-files-or-dirs>
   ```
2. **Detection recipe coverage**:
   Ensure the inferred source (`infer_source` in `scripts/build_docs_index.py`) and `trait_category` resolve to a runnable detection recipe in `data/methods/methods.yaml`:
   ```bash
   .venv/bin/python scripts/build_methods.py
   .venv/bin/python -m pytest tests/test_methods_recipes.py
   ```
3. **Internal ID-label baseline**:
   Update the `records` count in `conf/internal_id_label_baseline.yaml` to match the new corpus total and verify:
   ```bash
   .venv/bin/python scripts/validate_internal_id_labels.py
   ```
4. **Writer audit, history record, and tests**:
   ```bash
   .venv/bin/python scripts/audit_writers.py
   .venv/bin/python scripts/new_history_record.py \
     --kind other \
     --slug "<batch-slug>" \
     --path "scripts/seed_<name>.py" \
     --event CREATE \
     --outcome changed \
     --summary "Seed <N> <category> protein trait records" \
     --details "<provenance, validation, and scope summary>"
   just validate-history
   .venv/bin/python -m pytest
   ```
