# ProteinTraitsMech

Knowledge base of protein **sequence** and **structure** traits, curated one YAML per trait with evidence-backed causal graphs.

Sibling to [dismech](https://github.com/monarch-initiative/dismech) (disease mechanisms), [TraitMech](../TraitMech) (microbial ecophysiological traits), CultureMech (growth media), and MediaIngredientMech (chemical ingredients). Same curation model: one YAML per record, LinkML-validated, provenance + audit trail, optional evidence-bearing causal mechanism graphs.

## Scope

ProteinTraitsMech covers traits along five axes:

- **SEQUENCE** — motifs, signal peptides, propeptides, cleavage sites, low-complexity / disordered regions, tandem repeats, compositional biases, conserved regions, epitopes, PTM sites.
- **STRUCTURE** — folds, structural domains, secondary-structure arrangements, topology classes, quaternary state, subunit interfaces, active / binding / allosteric / metal sites, disulfide bonds, cavities, symmetry, dynamics, structural stability, surface properties.
- **SEQUENCE_STRUCTURE** (mixed) — traits meaningful in both axes: transmembrane spans, coiled coils, structural tandem repeats.
- **FUNCTION** — entry-level (non-localised) traits: enzymatic activity, binding capacity, cofactor requirement, subcellular localisation, environmental response, interaction partner. Grounded by EC / Rhea / ChEBI / GO / UniProt SubCell. Complements the localised sequence/structure records rather than replacing them.
- **EVOLUTION** — comparative-genomics traits: conservation and distribution across taxa (conserved / clade-specific / variable) and pangenome partition (core / soft-core / shell / cloud / persistent / singleton).

Records anchor to authoritative resources: Pfam, InterPro, PROSITE, SMART, MEROPS, CATH, SCOP, PDB, GO, PR, UniProtKB.

## Quick start

```bash
just install                  # uv sync --extra dev
just gen-schema               # generate dataclasses from LinkML
just validate-all             # validate every ProteinTraitRecord YAML
```

## Schema

`src/proteintraitsmech/schema/proteintraitsmech.yaml` defines:

- **ProteinTraitRecord** — root class, one per YAML file. Carries `identifier` (preferably an existing InterPro / Pfam / PROSITE / CATH / SCOP / MEROPS / PR CURIE), `label`, `definition`, `parent_traits`, `xrefs`, `synonyms`, `trait_axis` (SEQUENCE / STRUCTURE / SEQUENCE_STRUCTURE / FUNCTION / EVOLUTION), `trait_category`, `term_kind`, optional `canonical_examples`, optional `evidence`, optional `curation_history`, and optional inline `causal_graphs`.
- **CausalGraph / CausalNode / CausalEdge** — evidence-backed causal mechanism graphs. Nodes represent proteins, domains, motifs, residues, PTMs, ligands, pathways, molecular functions, biological processes, phenotypes, or diseases. Every `CausalEdge` must carry at least one `EvidenceItem`.
- **CanonicalExample** — reference exemplar proteins (UniProtKB accession + taxon) that archetypally exhibit the trait.
- **TraitSynonym / EvidenceItem / CurationEvent** — ancillary classes.
- **TraitAxisEnum** — `SEQUENCE` / `STRUCTURE` / `SEQUENCE_STRUCTURE` / `FUNCTION` / `EVOLUTION`.
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
│       ├── mixed/<category>/<slug>.yaml
│       └── function/<category>/<slug>.yaml
├── src/proteintraitsmech/
│   └── schema/proteintraitsmech.yaml            # LinkML schema
├── scripts/                                     # seed / validate / audit tooling
├── tests/
└── docs/
```

Axis / category pairing is enforced by LinkML `rules` on
`ProteinTraitRecord`: any `SEQ_*` category requires `trait_axis: SEQUENCE`,
`STRUCT_*` requires `STRUCTURE`, `MIXED_*` requires `SEQUENCE_STRUCTURE`,
and `FUNC_*` requires `FUNCTION`. `UPPER` / `OTHER` are administrative
and may appear on any axis. `just validate-all` will reject a
mismatched pair.

**FUNCTION vs localised STRUCTURE.** These axes are complementary, not
exclusive. A UniProt entry with an ATP-binding site emits both a
`STRUCT_BINDING_SITE` record (localised — *where* ATP binds, residues
45–52) and a `FUNC_BINDING_CAPACITY` record (entry-level — *that* the
protein binds ATP). Likewise a catalytic residue emits both
`STRUCT_ACTIVE_SITE` and `FUNC_ENZYMATIC_ACTIVITY`. Curators should not
merge these; they answer different questions.

## Workflow

1. **Seed** — import candidate traits from an authoritative resource (Pfam / InterPro / PROSITE / CATH / SCOP / MEROPS). Seeded records land with `mapping_status: SEEDED` and axis + category inferred from the source.
2. **Curate** — edit `data/traits/<axis>/<category>/<slug>.yaml` directly; set `mapping_status: REVIEWED`, append a `CurationEvent`, attach `EvidenceItem` blocks with PMID / DOI + verbatim snippet.
3. **Add causal graphs** — attach `causal_graphs` when the trait has source-backed mechanism structure (e.g. "this active-site residue coordinates the substrate carbonyl"). Every `CausalEdge` must carry edge-level `evidence`; prefer grounded CURIEs for nodes and predicates (RO for predicates; PR / GO / CHEBI / MOD / HP / MONDO for nodes).
4. **Validate** — `just validate-all` invokes `linkml-validate` in batches over every record, reporting per-file failures with the reference-CLI diagnostics. Scope to a subset with a path or glob (`just validate-all data/traits/sequence/motif`).

## Enrichment fields

Two slots are populated automatically by the seeders when the source
supports them, and can also be added by curators:

- **`residue_sequence`** — the concrete amino-acid substring covered by
  a localised trait (SEQUENCE / STRUCTURE / SEQUENCE_STRUCTURE axes).
  Emitted by `seed_uniprot.py` for every FT record with a parsable
  coordinate range, sliced from the entry's `SQ` block (DISULFID is
  skipped — its coordinates encode a bond, not a substring).
  Complements `sequence_pattern`, which stays reserved for symbolic
  motif/regex syntax.
- **`parent_traits`** — links to broader/parent traits. Populated
  automatically:
    - **Not** from `seed_uniprot.py`: a UniProt entry's DR family/domain
      signatures (PROSITE/Pfam/InterPro/SMART/CATH/HAMAP) are the *protein's*
      memberships, so they are emitted as `xrefs`, not `parent_traits` — a
      family signature is not a broader class of a specific feature-trait
      (caught by the `review-source-categories` skill's `FAMILY_AS_PARENT`).
    - `seed_prosite.py` promotes each signature's PDOC documentation
      entry (from the `DO` line) to `parent_traits: [PROSITE:PDOCxxxxx]`
      — multiple ACs can share a PDOC (e.g. `PS00796` and `PS01180` →
      `PDOC00633` "14-3-3 proteins"), giving family-level grouping in
      the docs browser.
- **Ontology xrefs** — every record's `trait_category` is grounded to
  an authoritative ontology term (SO for sequence / structure features,
  MOD for specific PTMs, GO for functional classes) as an `xref` entry
  by [`scripts/ground_categories.py`](scripts/ground_categories.py)
  (`just ground-categories`). Mappings are curated in the script and
  verified against both the
  [OAK](https://incatools.github.io/ontology-access-kit/) local
  `sqlite:obo:<onto>` adapter (default, one download per ontology) and
  the [EBI OLS4 REST API](https://www.ebi.ac.uk/ols4/) — pass
  `--source ols` to switch backends. `--audit` prints the resolved
  table without touching files.

    ```bash
    just ground-categories --audit                   # audit only
    just ground-categories --apply                   # write xrefs
    just ground-categories --source ols --audit      # cross-check via OLS
    ```

    Current mapping table covers 33 of ~40 categories (STRUCT_CAVITY /
    STRUCT_SYMMETRY / STRUCT_DYNAMICS / STRUCT_STABILITY /
    STRUCT_SURFACE / STRUCT_ALLOSTERIC_SITE / SEQ_DISORDER /
    SEQ_EPITOPE / SEQ_NONSTANDARD_RESIDUE / FUNC_COFACTOR_REQUIREMENT
    are intentionally unmapped — extend `CATEGORY_MAPPINGS` when a
    non-obsolete term is identified).

- **`canonical_examples`** — reference proteins that exhibit the trait.
  Two sources coexist on a record:
    - `source: CURATOR` — hand-picked archetypes. Seeders emit one when
      the trait itself is anchored to a specific UniProt entry (TED
      folds, UniProt-seeded FT records).
    - `source: UNIPROTKB_API` — retrieved by
      [`scripts/fetch_uniprot_examples.py`](scripts/fetch_uniprot_examples.py)
      (`just fetch-examples`) by querying UniProtKB REST for entries
      cross-referenced to the trait's anchoring signature
      (`xref:prosite-PS00796`, `xref:pfam-PF00244`, etc.). Each hit
      carries `sequence_length`, `reviewed`, `annotation_score`,
      `family_classifications` (Pfam / InterPro / HAMAP / SMART / CATH
      xrefs on that specific entry) and a `fetched_at` date stamp so
      downstream consumers can rank / filter without re-querying UniProt.

    ```bash
    # populate 3 reviewed examples on one PROSITE PATTERN record
    just fetch-examples data/traits/sequence/pattern/1433-1.yaml --limit 3 --apply
    # or run over an entire subdirectory
    just fetch-examples data/traits/sequence/pattern --limit 5 --apply
    ```

    Idempotent: existing accessions are not re-added. `--force` drops
    prior `UNIPROTKB_API` picks and re-queries. Rate-limited
    (~4 req/s + exponential backoff on 429/503).

    Each example additionally carries its full amino-acid `sequence`
    and a `features` list (SequenceFeatureAnnotation records: `start`,
    `end`, `feature_type`, `trait_axis`, `trait_category`, `note`) —
    populated in a separate `--refresh-sequences` pass that batch-
    fetches flat files via `/uniprotkb/accessions?format=txt` and
    routes each FT line through `seed_uniprot.py`'s `FT_TYPE_MAP`.

    ```bash
    # fill in sequence + features on already-fetched API examples
    just fetch-examples data/traits/sequence/pattern --refresh-sequences --apply
    ```

    The docs browser renders each example's sequence in a 60-aa-per-row
    monospace viewer with per-residue coloured strips beneath each
    letter — one strip per feature covering that position, split by
    equal fractions when multiple features overlap. Colour is by
    trait axis (SEQUENCE = blue, STRUCTURE = green, SEQUENCE_STRUCTURE
    = purple). Hover a strip for the raw UniProt FT type + range + note.

## Seeds

| Source | Records | Bucket |
| --- | ---: | --- |
| [LinkML `LocalStructuralFeature`](https://linkml.io/valuesets/elements/LocalStructuralFeature/) | 19 | `data/traits/structure/{secondary,active_site,binding_site,cavity,disulfide,metal_site,dynamics,interface}/` |
| [PROSITE patterns](https://prosite.expasy.org/) (`prosite.dat`, PATTERN) | 1311 | `data/traits/sequence/pattern/` (1279 generic) + `data/traits/sequence/{modified_residue,glycosylation,crosslink}/` (32 PTM subtypes) |
| [PROSITE profiles](https://prosite.expasy.org/) (`prosite.dat`, MATRIX) | 1434 | `data/traits/sequence/profile/` |
| [PROSITE ProRules](https://prosite.expasy.org/) (`prorule.dat`) | 1449 | `data/traits/structure/domain/` (1445) + `data/traits/sequence/{modified_residue,glycosylation,prorule}/` (2 phospho + 1 N-glyco + 1 attachment motif) |
| [TED novel folds](https://ted.cathdb.info/) (Zenodo v5, [DOI:10.5281/zenodo.13908086](https://doi.org/10.5281/zenodo.13908086), CC-BY 4.0) | 7427 | `data/traits/structure/fold/novel/` |
| [TED highly-symmetric folds](https://ted.cathdb.info/) (same Zenodo record) | 6433 | `data/traits/structure/fold/high_symmetry/` |
| [UniProtKB](https://www.uniprot.org/) FT/CC/GO demultiplexer (`seed_uniprot.py`) | 0 (demo retired) | per-protein records are instance-level, not trait classes — retired; real entries attach as `canonical_examples` on class traits via `fetch_uniprot_examples.py` |
| [PSI-MOD](https://github.com/HUPO-PSI/psi-mod-CV) (HUPO-PSI protein modification CV, CC-BY-4.0) | 1971 | `data/traits/sequence/{modified_residue,glycosylation,lipidation,crosslink,ptm_ontology}/` |
| [ECOD](http://prodata.swmed.edu/ecod/) (Evolutionary Classification Of protein Domains, v295) | 45113 | `data/traits/structure/{architecture,homologous_superfamily,topology,fold/ecod}/` (21 + 6,178 + 3,955 + 34,959) |
| [CATH-Gene3D](https://www.cathdb.info/) hierarchy (`seed_cath.py`, CC-BY 4.0) | 8151 | `data/traits/structure/{class,architecture,topology,homologous_superfamily}/cath/` (unnamed nodes kept, labelled by CATH id + rep-domain xref) |
| [SCOPe 2.08](https://scop.berkeley.edu/) (`seed_scope.py`) | 22810 | `data/traits/structure/{class,fold,homologous_superfamily,domain}/scope/` (px/sp instances excluded — occurrences, not trait classes) |
| [Reactome](https://reactome.org/) pathways (`seed_reactome.py`, CC0) | 2883 | `data/traits/function/pathway/reactome/` (Homo sapiens reference set → FUNC_PATHWAY) |
| [CARD/ARO](https://card.mcmaster.ca/) resistance ontology (`seed_obo.py aro`, CC-BY 4.0) | 7451 | `data/traits/function/resistance/aro/` (determinants + mechanisms → FUNC_RESISTANCE) |
| [InterPro](https://www.ebi.ac.uk/interpro/) entries (integrative; public domain; GO-grounded via interpro2go) | 26264 | `data/traits/{structure/domain,structure/homologous_superfamily,sequence/repeat,sequence/conservation,structure/active_site,structure/binding_site,sequence/ptm_ontology}/interpro/` (Domain→STRUCT_DOMAIN, superfamily, Repeat→SEQ_REPEAT, Conserved-/Active-/Binding-site, PTM; `Family` excluded) |
| [Pfam-A](https://www.ebi.ac.uk/interpro/) families (`seed_pfam.py`, public domain) | 30134 | `data/traits/{structure/domain,sequence/repeat,mixed/coiled_coil,sequence/disorder,sequence/motif}/pfam/` (routed by family type; GO- + InterPro-grounded; Pfam-B discontinued) |
| [M-CSA](https://www.ebi.ac.uk/thornton-srv/m-csa/) (Mechanism & Catalytic Site Atlas, CC-BY-4.0) | 1003 | `data/traits/structure/active_site/mcsa/` |
| [DisProt](https://disprot.org/) (curated intrinsically disordered proteins, CC-BY-4.0) | 3199 | `data/traits/sequence/disorder/` (each entry carries full sequence + FT-shaped disorder regions with IDPO term IDs) |
| [PSI-MI](https://github.com/HUPO-PSI/psi-mi-CV) (HUPO-PSI molecular-interaction CV, CC-BY-4.0) | 146 | `data/traits/function/interaction_partner/psi_mi/` (only the `interaction type` branch, MI:0190) |
| [METPO](https://github.com/berkeleybop/metpo) (Microbial Ecophysiological Trait & Phenotype Ontology, CC-BY-4.0) | 118 | `data/traits/function/{environmental_response,enzymatic_activity}/metpo/` (growth-preference / tolerance + metabolism / enzyme-test branches) |
| [PATO](https://github.com/pato-ontology/pato) (Phenotype And Trait Ontology, CC-BY-4.0) | 28 | `data/traits/structure/{stability,dynamics,surface}/pato/` (curated physicochemical quality whitelist) |
| Curated stability taxonomy (`seed_stability.py`, CC0-1.0) | 33 | `data/traits/structure/stability/conditions/` (11 stressors × {base, increased, decreased}, parented to PATO stability) |
| Curated evolutionary / pangenome taxonomy (`seed_evolution.py`, CC0-1.0) | 9 | `data/traits/evolution/{conservation,pangenome}/` (EVOLUTION axis: conserved / clade-specific / variable + pangenome core/soft-core/shell/cloud/persistent/singleton) |
| [TCDB](https://www.tcdb.org/) transport classification (`seed_tcdb.py`, CC-BY-SA 3.0) | 2285 | `data/traits/function/transport/tcdb/` (Class/Subclass/Family → FUNC_TRANSPORT; 946 families ChEBI-grounded) |
| [COG 2020](https://www.ncbi.nlm.nih.gov/research/cog/) orthologous groups (`seed_cog.py`, US Gov public domain) | 4903 | `data/traits/function/ortholog_group/cog/` (4,877 COGs + 26 functional categories → FUNC_ORTHOLOG_GROUP) |
| [Rhea](https://www.rhea-db.org/) reactions (`seed_rhea.py`, CC-BY 4.0) | 18558 | `data/traits/function/enzymatic_activity/rhea/` (master reactions → FUNC_ENZYMATIC_ACTIVITY; ChEBI participants; EC via rhea2ec) |
| [ExPASy ENZYME](https://enzyme.expasy.org/) complete EC hierarchy (`seed_ec.py`, CC-BY 4.0) | 7375 | `data/traits/function/enzymatic_activity/ec/` (6,965 leaves + 410 nodes; GO/RHEA mapped, KEGG direct, DR examples — supersedes trait-onto-map EC) |
| [RepeatsDB](https://repeatsdb.org/) structural tandem repeats (`seed_repeatsdb.py`, CC-BY 4.0) | 122 | `data/traits/sequence_structure/structural_repeat/repeatsdb/` (Class/Topology/Fold/Clan → MIXED_STRUCTURAL_REPEAT) |

The last three are ingested by the generic **`seed_obo.py`** importer, which reads any OBO ontology and imports only the **branch-scoped** subset declared in its `SOURCES` config (a term is kept iff it is an `is_a` descendant of a configured root, and it inherits that root's axis/category). This is deliberately narrower than a whole-ontology dump — PSI-MI is mostly experimental methods, PATO qualities are generic modifiers, and METPO is organismal, so only the terms with genuine protein-trait analogues are seeded.

Refetch and re-seed:

```bash
just fetch-prosite            # writes data/raw/prosite.dat + prorule.dat (gitignored)
just fetch-ted                # writes data/raw/ted_*.tsv.gz (gitignored)
just fetch-psimod             # PSI-MOD.obo from HUPO-PSI GitHub (CC-BY-4.0)
just fetch-obo                # PSI-MI / PATO / METPO .obo files (all CC-BY-4.0)
just fetch-ecod               # ECOD domain list (~689 MB, weekly PDB-synced)
just seed-lsf --apply         # 19 LinkML LocalStructuralFeature records
just seed-prosite --apply     # 4194 PROSITE records; idempotent, skips existing
just seed-ted --apply         # 13860 TED fold records; idempotent
just seed-psimod --apply      # 1971 PSI-MOD PTM records; tags each CC-BY-4.0
just seed-ecod --apply        # 45113 ECOD hierarchy nodes (A/X/H/T/F)
just seed-mcsa --apply        # 1003 M-CSA catalytic mechanisms
just seed-disprot --apply     # 3199 DisProt IDP profiles with regions
just seed-obo all --apply     # 292 OBO records (PSI-MI 146 + METPO 118 + PATO 28)

# UniProtKB FT-line seed — pass accessions or a local flat file
just seed-uniprot --accession B0R5N7 --accession P25888 --apply

# SCOPe seeder is written but Berkeley's server is behind an anti-bot
# challenge — download dir.des.scope.*.txt and dir.hie.scope.*.txt
# manually from https://scop.berkeley.edu/downloads/ into
# data/raw/scope/, then run:
just seed-scope --apply
```

UniProtKB supported FT types → axis / category:

| UniProt FT type | Axis | Category | Notes |
|---|---|---|---|
| `TRANSMEM`, `INTRAMEM` | — | — | **skipped** — per-protein membrane spans are redundant with the general transmembrane trait |
| `SIGNAL` | SEQUENCE | `SEQ_SIGNAL_PEPTIDE` | |
| `TRANSIT` | SEQUENCE | `SEQ_TRANSIT_PEPTIDE` | mitochondrial / chloroplast / peroxisome targeting |
| `PROPEP` | SEQUENCE | `SEQ_PROPEPTIDE` | zymogen activation segment |
| `INIT_MET` | SEQUENCE | `SEQ_INITIATOR_METHIONINE` | N-terminal Met removed post-translationally |
| `CHAIN`, `PEPTIDE` | SEQUENCE | `SEQ_MATURE_CHAIN` | mature polypeptide product |
| `NON_STD` | SEQUENCE | `SEQ_NONSTANDARD_RESIDUE` | selenocysteine, pyrrolysine, curator-annotated |
| `REGION` /note="Disordered" | SEQUENCE | `SEQ_DISORDER` | other `REGION` free-text is skipped |
| `COMPBIAS` | SEQUENCE | `SEQ_COMPOSITION` | `/note` carries residue class (Gly-rich, basic, acidic, …) |
| `MOTIF` | SEQUENCE | `SEQ_MOTIF` | curator-defined; overlaps with PROSITE where cross-referenced |
| `MOD_RES` | SEQUENCE | `SEQ_MODIFIED_RESIDUE` | phosphorylation, methylation, acetylation, hydroxylation, sulfation, … |
| `CARBOHYD` | SEQUENCE | `SEQ_GLYCOSYLATION_SITE` | N-/O-linked, C-mannosylation, GPI anchor attachment |
| `LIPID` | SEQUENCE | `SEQ_LIPIDATION_SITE` | myristoylation, palmitoylation, prenylation, GPI-lipid |
| `CROSSLNK` | SEQUENCE | `SEQ_CROSSLINK_SITE` | isopeptide, ubiquitin/SUMO branch, sortase — bond not span, so no `residue_sequence` |
| `DOMAIN` | STRUCTURE | `STRUCT_DOMAIN` | |
| `ACT_SITE` | STRUCTURE | `STRUCT_ACTIVE_SITE` | |
| `SITE` | STRUCTURE | `STRUCT_BINDING_SITE` | |
| `BINDING` (non-metal ligand) | STRUCTURE | `STRUCT_BINDING_SITE` | ligand ChEBI added to `xrefs` |
| `BINDING` (metal ligand) / `METAL` | STRUCTURE | `STRUCT_METAL_SITE` | metal keyword detection on `/ligand` + `/ligand_note` |
| `DISULFID` | STRUCTURE | `STRUCT_DISULFIDE` | bond, not span — no `residue_sequence` |
| `HELIX`, `STRAND`, `TURN` | STRUCTURE | `STRUCT_SECONDARY` | requires an experimental structure in the entry |

Skipped (out-of-scope for this schema): `TOPO_DOM`, `VARIANT`, `VAR_SEQ`, `MUTAGEN`, `CONFLICT`, `UNSURE`, `NON_CONS`, `NON_TER`.

UniProtKB **entry-level** blocks (FUNCTION axis) → category:

| UniProt block or ref | Category | Grounding |
|---|---|---|
| `CC CATALYTIC ACTIVITY` (per `Reaction=`) | `FUNC_ENZYMATIC_ACTIVITY` | EC, Rhea, participating ChEBIs |
| `DR GO; F:…activity` | `FUNC_ENZYMATIC_ACTIVITY` | GO MF |
| `DR GO; F:…binding` | `FUNC_BINDING_CAPACITY` | GO MF |
| `CC COFACTOR` (per `Name=`) | `FUNC_COFACTOR_REQUIREMENT` | ChEBI |
| `CC SUBCELLULAR LOCATION` (per compartment) | `FUNC_LOCALIZATION` | UniProt SubCell |
| `DR GO; C:…` | `FUNC_LOCALIZATION` | GO CC |
| `CC INDUCTION` (keyword-matched) | `FUNC_ENVIRONMENTAL_RESPONSE` | keyword vocabulary (cold, heat, oxidative stress, hypoxia, anaerobic/aerobic, osmotic, UV, …) |
| `DR GO; P:response to …` | `FUNC_ENVIRONMENTAL_RESPONSE` | GO BP |
| `CC SUBUNIT` (per "Interacts with X") | `FUNC_INTERACTION_PARTNER` | partner name; PMIDs in evidence |

### Worked example — how one UniProtKB entry demultiplexes across the axes

Illustrated with P25888 (ATP-dependent RNA helicase RhlE, *E. coli* K12). This
shows the FT/CC → axis / category mapping the seeder encodes; the per-protein
records themselves are **not** seeded standalone (they are instance-level, not
trait classes — see the note in `docs/example.md`). A real protein is instead
attached as a `canonical_example` on the relevant class-level trait:

| Axis | Records | Categories |
|---|---:|---|
| SEQUENCE | 6 | 1 SEQ_DISORDER, 3 SEQ_COMPOSITION (Gly / basic+acidic / basic), 2 SEQ_MOTIF (Q motif + DEAD box) |
| STRUCTURE | 3 | 2 STRUCT_DOMAIN (Helicase ATP-binding + Helicase C-terminal), 1 STRUCT_BINDING_SITE (ATP → CHEBI:30616) |
| FUNCTION | 11 | 3 FUNC_ENZYMATIC_ACTIVITY (Rhea:13065 ATP hydrolysis, GO:0016887, GO:0003724), 2 FUNC_BINDING_CAPACITY (ATP + RNA), 2 FUNC_LOCALIZATION (Cytoplasm + GO:0005829), 2 FUNC_ENVIRONMENTAL_RESPONSE (cold shock + heat via GO:0009408), 2 FUNC_INTERACTION_PARTNER (PcnB + RNase E) |

Each record carries `identifier` → `proteintraitsmech:UNIPROTKB_<ACC>_<TYPE>_<KEY>`, `canonical_examples` linking to the source entry + NCBITaxon, `xrefs` (GO / EC / Rhea / ChEBI / partner labels), and `evidence` with the source PMIDs where the flat file cites them.

All seeded records land with `mapping_status: SEEDED`; curator review flips them to `REVIEWED` and adds evidence / causal graphs.

## License

CC0-1.0 — Public Domain Dedication.
