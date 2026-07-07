# Axis split review 1

## Verdict per split

- **NCBIfam SEQUENCE<->FUNCTION: ⚠️ partially appropriate.** The core line in `scripts/seed_ncbifam.py:60-75` is principled for `equivalog`/`subfamily` versus `*_domain`/`domain`/`repeat`/`superfamily`, but the table silently defaults `PfamEq` and `PfamAutoEq` to `SEQ_DOMAIN` and therefore mishandles explicit source family types.
- **CDD SEQUENCE<->FUNCTION: ⚠️ partially appropriate.** `KOG* -> FUNC_ORTHOLOG_GROUP` in `scripts/seed_cdd.py:134-139` is correct, but the same function-family carve-out is not applied to non-KOG full-length CDD protein-cluster prefixes (`PRK`, `PLN`, `PHA`, `PTZ`, `MTH`, `CHL`), which are currently routed as `SEQ_DOMAIN`.
- **InterPro sites: ⛔ wrong under a strict axis-follows-representation reading.** `scripts/seed_interpro.py:62-71` routes `Active_site` and `Binding_site` signatures to `STRUCTURE`; InterPro defines these as short conserved sequence sites, not structure-derived classifications.

## The line, judged

The right criterion is: **sequence-region or sequence-signature classification -> SEQUENCE; source-asserted whole-protein/function-conserved family or ortholog group -> FUNCTION; structure-derived classification with structural representatives/geometry -> STRUCTURE.** The carve-out is principled because the FUNCTION side is not just "a sequence HMM with a function xref"; it is a source-level claim that membership transfers a conserved product/function identity.

NCBIfam mostly draws that line correctly. The code says `repeat -> SEQ_REPEAT`, `*_domain/domain/signature -> SEQ_DOMAIN`, `superfamily -> SEQ_HOMOLOGOUS_SUPERFAMILY`, and `_FUNC_FAMILY_TYPES = {"equivalog", "subfamily", "exception", "hypoth_equivalog", "paralog"}` -> `FUNC_PROTEIN_FAMILY` (`scripts/seed_ncbifam.py:51-75`). The raw source confirms all of those family types occur, plus unhandled `PfamEq` and `PfamAutoEq` (`data/raw/ncbifam/hmm_PGAP.tsv`, family_type counts: `PfamEq` 1,860; `PfamAutoEq` 1,203). NCBI's PGAP evidence docs define `PfamEq` and `PfamAutoEq` as equivalog-like HMM family types, so the current silent default is not a safe "unknown -> sequence domain" case.

CDD draws the KOG line correctly but inconsistently with NCBIfam for full-length functional families. The seeder declares KOG as euKaryotic Orthologous Groups (`scripts/seed_cdd.py:10-16`) and routes accessions starting with `KOG` to `FUNC_ORTHOLOG_GROUP` (`scripts/seed_cdd.py:134-136`). That matches raw records such as `CDD:KOG0001`, "Ubiquitin and ubiquitin-like proteins [Posttranslational modification...]" at `data/raw/cdd/cddid_all.tbl.gz` decompressed line 67161 and emitted `data/traits/function/ortholog_group/cdd/kog0001-ubiquitin-and-ubiquitin-like-proteins-posttranslational-modifi-kog0001.yaml:1-8`. But the same route function puts `PRK`, `PLN`, `PHA`, `PTZ`, `MTH`, `CHL`, and `sd` into `SEQ_DOMAIN` (`scripts/seed_cdd.py:131-138`). That is defensible for `cd`/`sd` domain models, but not for every full-length protein-cluster prefix if the NCBIfam function-family carve-out is meant to be source-consistent.

InterPro site routing departs from the representation convention. The raw XML marks `InterPro:IPR017441` as `type="Binding_site"` (`data/raw/interpro/interpro.xml.gz` decompressed line 2303320), and the emitted record is `STRUCT_BINDING_SITE` (`data/traits/structure/binding_site/interpro/protein-kinase-atp-binding-site-ipr017441.yaml:1-8`). InterPro documentation defines sites as short conserved residue sequences; this is not a structure-derived classification in the CATH/SCOPe/ECOD/TED sense.

## Mis-routed record classes

### Blocker: none found

I did not find an entire primary split that is wholly reversed. NCBIfam `equivalog_domain` did **not** land in FUNCTION: examples include `NCBIfam:TIGR00069` (`family_type=equivalog_domain`) emitted as `SEQUENCE/SEQ_DOMAIN` at `data/traits/sequence/domain/ncbifam/hisd-tigr00069.yaml:1-8`, and raw `NCBIfam:TIGR00401` at `data/raw/ncbifam/hmm_PGAP.tsv:14257` is also emitted under `data/traits/sequence/domain/ncbifam/msra-tigr00401.yaml:1-5`.

### Major: NCBIfam `PfamEq` silently defaults to `SEQ_DOMAIN`

- Code evidence: `route()` lowercases `family_type`, explicitly handles repeats/domains/superfamilies/function types, then defaults all other values to `SEQUENCE/SEQ_DOMAIN` (`scripts/seed_ncbifam.py:64-75`). `PfamEq` lowercases to `pfameq` and is not in any explicit branch.
- Source evidence: `data/raw/ncbifam/hmm_PGAP.tsv:28` has `NF013092.9`, `family_type=PfamEq`, product `inner capsid protein VP7`, GO `GO:0005198,GO:0019028`; `data/raw/ncbifam/hmm_PGAP.tsv:2016` has `NF019723.6`, `family_type=PfamEq`, product `ATP synthase epsilon subunit`, GO `GO:0015986,GO:0033178,GO:0042626`.
- Emitted evidence: `data/traits/sequence/domain/ncbifam/orbi-vp7-nf013092.yaml:1-8` and `data/traits/sequence/domain/ncbifam/ribosomal-s9-nf012598.yaml:1-8` are `SEQUENCE/SEQ_DOMAIN` despite `PfamEq` being an explicit equivalog-like source family type.
- Why: if `equivalog` and `subfamily` are carved out because the source asserts a function-conserved family, `PfamEq` belongs on the FUNCTION side more than on `SEQ_DOMAIN`. At minimum it must be explicit, not defaulted.

### Major: NCBIfam `PfamAutoEq` silently defaults to `SEQ_DOMAIN`

- Code evidence: same default in `scripts/seed_ncbifam.py:64-75`.
- Source evidence: `data/raw/ncbifam/hmm_PGAP.tsv:383` has `NF024283.8`, `family_type=PfamAutoEq`, product `UPF0606 protein KIAA1549`; `data/raw/ncbifam/hmm_PGAP.tsv:1742` has `NF023054.7`, `family_type=PfamAutoEq`, product `NAD(P)H dehydrogenase subunit NdhS`, GO `GO:0009767`.
- Emitted evidence: `data/traits/sequence/domain/ncbifam/kiaa1549-nf024283.yaml:1-8` and `data/traits/sequence/domain/ncbifam/duf751-nf017258.yaml:1-8` are `SEQUENCE/SEQ_DOMAIN`.
- Why: `PfamAutoEq` is weaker than `PfamEq`, so I would not automatically promote it to FUNCTION. But it is still an explicit family_type and many records are whole-protein family labels; routing them as `SEQ_DOMAIN` by falling through an "unknown" default is wrong. Use `SEQ_FAMILY` unless the project chooses to treat NCBI's AutoEq as function-conserved enough for `FUNC_PROTEIN_FAMILY`.

### Major: CDD full-length protein-cluster prefixes routed as `SEQ_DOMAIN`

- Code evidence: `DOMAIN_PREFIXES = ("cd", "PRK", "PLN", "PHA", "PTZ", "MTH", "CHL", "sd")` and all route to `SEQ_DOMAIN` (`scripts/seed_cdd.py:131-138`).
- Source/emitted evidence: `CDD:PRK09505` is `alpha-amylase` in `data/raw/cdd/cddid_all.tbl.gz` decompressed line 13001 and emitted as `SEQUENCE/SEQ_DOMAIN` at `data/traits/sequence/domain/cdd/alpha-amylase-reviewed-prk09505.yaml:1-8`; `CDD:CHL00040` is `ribulose-1,5-bisphosphate carboxylase/oxygenase large subunit` in `data/raw/cdd/cddid_all.tbl.gz` decompressed line 36 and emitted as `SEQUENCE/SEQ_DOMAIN` at `data/traits/sequence/domain/cdd/ribulose-1-5-bisphosphate-carboxylase-oxygenase-large-subunit-chl00040.yaml:1-8`.
- Blast radius from raw CDD: `PRK` 7,039; `PLN` 1,247; `PHA` 1,011; `PTZ` 469; `MTH` 196; `CHL` 178.
- Why: this is cross-source inconsistency. NCBIfam full-length function-family HMMs are routed to FUNCTION, while CDD full-length protein-cluster PSSMs with product/function labels are routed to SEQUENCE solely because they are CDD/PSSM accessions. If the carve-out is "function-conserved whole-protein family", these should not be `SEQ_DOMAIN`.

### Major, secondary: InterPro `Active_site` and `Binding_site` routed to STRUCTURE

- Code evidence: `TYPE_MAP` maps `Active_site` to `("STRUCTURE", "STRUCT_ACTIVE_SITE", ...)` and `Binding_site` to `("STRUCTURE", "STRUCT_BINDING_SITE", ...)` (`scripts/seed_interpro.py:62-71`).
- Raw/emitted evidence: `InterPro:IPR017441` is raw XML `type="Binding_site"` (`data/raw/interpro/interpro.xml.gz` decompressed line 2303320) and emitted as `STRUCT_BINDING_SITE` at `data/traits/structure/binding_site/interpro/protein-kinase-atp-binding-site-ipr017441.yaml:1-8`; `InterPro:IPR023650` is raw XML `type="Active_site"` (`data/raw/interpro/interpro.xml.gz` decompressed line 2938144) and emitted as `STRUCT_ACTIVE_SITE` at `data/traits/structure/active_site/interpro/beta-lactamase-class-a-active-site-ipr023650.yaml:1-8`.
- Why: InterPro sites are conserved residue signatures. They may describe catalytic or binding biology, but their representation is still sequence-local unless the record carries structural geometry/contact evidence.

### Not findings

- `equivalog_domain`, `hypoth_equivalog_domain`, `subfamily_domain`, and `paralog_domain` are correctly kept on `SEQ_DOMAIN` by `ft.endswith("_domain")` (`scripts/seed_ncbifam.py:68-69`). Examples with strong EC/GO, such as `NCBIfam:TIGR00069` histidinol dehydrogenase (`data/traits/sequence/domain/ncbifam/hisd-tigr00069.yaml:1-19`), should stay SEQUENCE because the source family_type is domain-scoped.
- NCBIfam `exception`, `hypoth_equivalog`, and `paralog` are defensible on `FUNC_PROTEIN_FAMILY`. NCBI describes exception HMMs as recognizing a specific chemical function plus an additional distinguishing feature, hypothetical equivalogs as expected to have the same specific function, and paralog HMMs as a special case of subfamily. Local examples include `NCBIfam:NF000008` `exception` at `data/traits/function/protein_family/ncbifam/trim-dfra1-rpt-nf000008.yaml:1-8`, `NCBIfam:TIGR00495` `hypoth_equivalog` at `data/traits/function/protein_family/ncbifam/crvdna-42k-tigr00495.yaml:1-8`, and `NCBIfam:TIGR01477` `paralog` at `data/traits/function/protein_family/ncbifam/rifin-tigr01477.yaml:1-8`.
- CDD KOGs are not single-domain misroutes in the sampled records. `CDD:KOG0001` and `CDD:KOG0003` are emitted as `FUNCTION/FUNC_ORTHOLOG_GROUP` (`data/traits/function/ortholog_group/cdd/kog0001-ubiquitin-and-ubiquitin-like-proteins-posttranslational-modifi-kog0001.yaml:1-8`; `data/traits/function/ortholog_group/cdd/kog0003-ubiquitin-60s-ribosomal-protein-l40-fusion-translation-ribosom-kog0003.yaml:1-8`), and their raw descriptions include KOG functional classes (`data/raw/cdd/cddid_all.tbl.gz` decompressed lines 67161 and 67163).

## Category calls

- **NCBIfam equivalog/subfamily/exception/hypoth_equivalog/paralog -> `FUNC_PROTEIN_FAMILY`: keep.** This category is more precise than `FUNC_ORTHOLOG_GROUP`; TIGRFAM/NCBIfam equivalogs are conserved-function family models, not necessarily ortholog clusters.
- **NCBIfam `PfamEq` -> `FUNC_PROTEIN_FAMILY`: change.** It is explicitly equivalog-like and whole-protein/function-label oriented, so `SEQ_DOMAIN` is the wrong category.
- **NCBIfam `PfamAutoEq` -> `SEQ_FAMILY` by default, or `FUNC_PROTEIN_FAMILY` only by policy decision.** It is not a domain, but its function-conservation guarantee is weaker than `PfamEq`.
- **CDD KOG -> `FUNC_ORTHOLOG_GROUP`: keep.** KOGs are euKaryotic Orthologous Groups, and the schema already defines `FUNC_ORTHOLOG_GROUP` for COG/eggNOG/KEGG-style conserved-function ortholog groups (`src/proteintraitsmech/schema/proteintraitsmech.yaml:1265-1271`).
- **Do not create an EVOLUTION category for KOGs.** Orthology is evolutionary evidence, but these records are membership in a named functional ortholog group. The current EVOLUTION categories are conservation state and pangenome partition (`src/proteintraitsmech/schema/proteintraitsmech.yaml:1281-1296`), not source-defined ortholog group identity.
- **CDD PRK/PLN/PHA/PTZ/MTH/CHL -> `FUNC_PROTEIN_FAMILY` if the NCBIfam carve-out is meant to be source-consistent.** Do not use `FUNC_ORTHOLOG_GROUP` unless a prefix is documented as an orthologous group source.
- **InterPro Active_site/Binding_site need sequence-side site categories.** With the current schema, `SEQ_CONSERVATION` is the least-wrong immediate target; a better schema would add `SEQ_ACTIVE_SITE` and `SEQ_BINDING_SITE` or allow sequence-signature site records to carry role-specific qualifiers.

## Recommended fixes

1. **`scripts/seed_ncbifam.py`: make `family_type` routing exhaustive and stop silent defaulting.**
   - Before: `_FUNC_FAMILY_TYPES = {"equivalog", "subfamily", "exception", "hypoth_equivalog", "paralog"}` (`scripts/seed_ncbifam.py:60`), then unknown/blank -> `SEQUENCE/SEQ_DOMAIN` (`scripts/seed_ncbifam.py:74-75`).
   - After:
     - `equivalog`, `subfamily`, `exception`, `hypoth_equivalog`, `paralog`, `pfameq` -> `FUNCTION`, `FUNC_PROTEIN_FAMILY`, `function/protein_family/ncbifam`.
     - `pfamautoeq` -> `SEQUENCE`, `SEQ_FAMILY`, `sequence/family/ncbifam` unless the project explicitly decides AutoEq is function-conserved enough for `FUNC_PROTEIN_FAMILY`.
     - `domain`, `signature`, `*_domain` -> `SEQUENCE`, `SEQ_DOMAIN`, `sequence/domain/ncbifam`.
     - `repeat` -> `SEQUENCE`, `SEQ_REPEAT`, `sequence/repeat/ncbifam`.
     - `superfamily` -> `SEQUENCE`, `SEQ_HOMOLOGOUS_SUPERFAMILY`, `sequence/homologous_superfamily/ncbifam`.
     - Unknown nonblank `family_type` -> fail or report as unhandled; do not silently emit `SEQ_DOMAIN`.
   - Migrate records: 1,860 `PfamEq` records from `data/traits/sequence/domain/ncbifam/` to `data/traits/function/protein_family/ncbifam/`; 1,203 `PfamAutoEq` records from `data/traits/sequence/domain/ncbifam/` to `data/traits/sequence/family/ncbifam/` or to FUNCTION if that policy is chosen.

2. **`scripts/seed_cdd.py`: split CDD source prefixes by semantics instead of one `DOMAIN_PREFIXES` bucket.**
   - Before: `DOMAIN_PREFIXES = ("cd", "PRK", "PLN", "PHA", "PTZ", "MTH", "CHL", "sd")` -> `SEQ_DOMAIN` (`scripts/seed_cdd.py:131-138`).
   - After:
     - `KOG*` -> `FUNCTION`, `FUNC_ORTHOLOG_GROUP`, `function/ortholog_group/cdd` (unchanged).
     - `cd*`, `sd*` -> `SEQUENCE`, `SEQ_DOMAIN`, `sequence/domain/cdd`.
     - `PRK*`, `PLN*`, `PHA*`, `PTZ*`, `MTH*`, `CHL*` -> `FUNCTION`, `FUNC_PROTEIN_FAMILY`, `function/protein_family/cdd`, if the NCBIfam carve-out is intended to cover equivalent full-length functional protein-cluster PSSMs.
     - `cl*` parent nodes of seeded `cd/sd` records -> `SEQUENCE`, `SEQ_HOMOLOGOUS_SUPERFAMILY`, `sequence/homologous_superfamily/cdd` (unchanged).
     - `pfam*`, `COG*`, `TIGR*`, `NF*`, `smart*`, `LOAD_*` -> explicitly skipped with a counted reason (already-covered mirrors), not just `None`.
   - Migrate records: 10,140 CDD protein-cluster records by raw prefix count (`PRK` 7,039; `PLN` 1,247; `PHA` 1,011; `PTZ` 469; `MTH` 196; `CHL` 178) from `data/traits/sequence/domain/cdd/` to `data/traits/function/protein_family/cdd/`.

3. **`scripts/seed_interpro.py`: stop routing sequence-signature sites to STRUCTURE.**
   - Before: `Active_site` -> `STRUCTURE/STRUCT_ACTIVE_SITE`; `Binding_site` -> `STRUCTURE/STRUCT_BINDING_SITE` (`scripts/seed_interpro.py:68-69`).
   - Immediate after, using existing categories: `Active_site`, `Binding_site`, and `Conserved_site` -> `SEQUENCE/SEQ_CONSERVATION`, with the InterPro entry type preserved in a source/type field if available.
   - Better schema-aware after: add sequence-side categories for active/binding site signatures, then route `Active_site` -> `SEQUENCE/SEQ_ACTIVE_SITE` and `Binding_site` -> `SEQUENCE/SEQ_BINDING_SITE`; reserve `STRUCT_ACTIVE_SITE` and `STRUCT_BINDING_SITE` for M-CSA/structure-derived residue sets, ligand contacts, or geometry-bearing records.

## Source notes used for semantics

- NCBI PGAP evidence documentation: https://www.ncbi.nlm.nih.gov/genome/annotation_prok/evidence/ . Relevant local application: source family types `Exception HMM`, `Equivalog HMM`, `Hypothetical equivalog HMM`, `Equivalog domain HMM`, `PfamEq`, `PfamAutoEq`, `Paralog HMM`.
- NCBI CDD overview: https://www.ncbi.nlm.nih.gov/Structure/cdd/cdd.shtml . Relevant local application: CDD contains PSSM/MSA models for domains and full-length proteins, and imports source databases including PRK and COG/KOG-like collections.
- InterPro entry type documentation: https://interpro-documentation.readthedocs.io/en/latest/entries_info.html and https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/what-is-an-interpro-entry/interpro-entry-types/ . Relevant local application: InterPro sites are short conserved sequences/residue groups.
