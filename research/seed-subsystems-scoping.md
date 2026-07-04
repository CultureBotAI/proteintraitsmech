---
topic: SEED / PubSEED / BV-BRC subsystems as class-level FUNCTION traits
kind: source scoping report
date: 2026-07-04
question: >-
  Can the SEED subsystem framework (curated functional roles + subsystems,
  now served via BV-BRC/PATRIC) be seeded into ProteinTraitsMech as
  CLASS-level function traits, and is it worth doing?
verdict: DEFER — clean but heavily redundant; if seeded, narrow to the ~920 subsystem classes only
---

# SEED subsystems — source scoping

> Scope only. No seeder, no data written. Decision-oriented.

## TL;DR verdict

**DEFER (low priority).** The class-level unit is clean and the licence is a
**PASS** (US-Gov public domain via BV-BRC), but the content is **heavily
redundant** with what is already seeded: SEED **functional roles carry EC
numbers** (EC hierarchy already fully seeded via `seed_ec.py`), and SEED
**subsystems are metabolic pathways/modules** (Reactome `FUNC_PATHWAY` already
seeded; KEGG modules are the better-maintained pathway source). The one
distinctive contribution is **curated prokaryotic functional modules**
(Metabolism / Energy / Membrane-transport superclasses) that Reactome's
eukaryote-centric coverage misses. If seeded at all, seed **only the ~920
subsystem classes → `FUNC_PATHWAY`**, and **skip the role level** (redundant with
EC). Rank it **below a future KEGG-module seed**.

---

## 1. What SEED subsystems are

The SEED is a genome-annotation framework in which curation is done **at the
level of subsystems, by an expert, across many genomes at once — not gene by
gene** ([SEED/RAST, PMC3965101](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3965101/);
[SEED Viewer Manual/Subsystems](https://www.theseed.org/wiki/SEED_Viewer_Manual/Subsystems)).

| Concept | What it is | Level |
|---|---|---|
| **Functional role** | A named biological function a gene product performs; for enzymes the **EC number is embedded in the role name in parentheses**, e.g. `D-alanine--D-alanine ligase (EC 6.3.2.4)` | **CLASS** |
| **Subsystem** | A curator-defined **set of functional roles that act together** in a system — a metabolic pathway, a complex (e.g. the ribosome), or a protein class ([Glossary](https://www.theseed.org/wiki/Glossary)) | **CLASS** |
| **Superclass → Class → Subclass** | 3-level classification above the subsystem; **11 superclasses** (Metabolism, Energy, Protein Processing, …) ([subsystems_tab](https://www.bv-brc.org/docs/quick_references/organisms_taxon/subsystems_tab.html)) | **CLASS** (hierarchy) |
| **Spreadsheet cell / variant** | In a *populated* subsystem, **rows = genomes, columns = functional roles**, and each cell holds the **gene IDs from that genome that implement the role** ([SEED Viewer Manual/Subsystems](https://www.theseed.org/wiki/SEED_Viewer_Manual/Subsystems)) | **INSTANCE** (per-genome) |

So the SEED tree (~10,000 nodes = subsystems + roles combined;
[BMC Bioinformatics S21](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-12-S1-S21))
is a rooted classification: internal nodes = subsystems, leaves = functional
roles. **The class-level concepts are the superclass/class/subclass hierarchy,
the subsystems, and the functional roles.** The **instance level** is the
per-genome spreadsheet (which genes in genome X fill role Y) — that is the
`.subsystem.tab` per-genome annotation, and it is **out of scope**.

## 2. Download availability

Original **theseed.org / pubseed.theseed.org** is still online but effectively
**legacy/frozen**; the **live successor is BV-BRC** (Bacterial & Viral
Bioinformatics Resource Center, Argonne/U-Chicago, NIAID-funded), which merged
PATRIC + IRD/ViPR ([BV-BRC, PMC9825582](https://pmc.ncbi.nlm.nih.gov/articles/PMC9825582/)).

| Route | URL | Format | Level | Notes |
|---|---|---|---|---|
| **BV-BRC Data API `subsystem_ref`** ✅ **best** | `https://www.bv-brc.org/api/subsystem_ref/` | JSON / TSV via RQL or Solr | **CLASS** | The **reference subsystem→role definitions**, genome-independent. Verified live: **920 subsystem records**, each with `superclass, class, subclass, subsystem_id, subsystem_name, description, role_name[]` (array of functional roles, EC inline). ([API doc](https://www.bv-brc.org/api/doc/)) |
| BV-BRC per-genome subsystem | `ftps://ftp.bvbrc.org/genomes/<id>/<id>.subsystem.tab` | tab | **INSTANCE** | Per-genome gene→role assignments. **Skip** ([FTP ref](https://www.bv-brc.org/docs/quick_references/ftp.html)). |
| GitHub mirror (hierarchy outline) | [hallamlab/MetaPathwaysGUI `SEED_subsystems.txt`](https://github.com/hallamlab/MetaPathwaysGUI/blob/master/functional_categories/SEED_subsystems.txt) | indented outline | CLASS (partial) | superclass→…→subsystem→role tree; static snapshot, no IDs/descriptions. Useful cross-check only. |
| GitHub — SEEDtk / ModelSEED | [SEEDtk](https://github.com/SEEDtk), [ModelSEEDDatabase](https://github.com/ModelSEED/ModelSEEDDatabase) | perl/flat | mixed | SEEDtk = toolkit; ModelSEEDDatabase = biochemistry (compounds/reactions), **not** the subsystem→role catalogue. Not the right file. |

**Recommended input = the `subsystem_ref` API dump** (one JSON pull, ~920
records). Verified count via `Content-Range: items 0-1/920`.

## 3. Licence — GATE

**PASS.** BV-BRC is produced by a **US-Government-funded** project (NIAID
contract, Argonne/U-Chicago); its data are **US public domain**, mirroring the
COG situation already accepted in this repo. **Citation is requested** (not
required): cite *"Improvements to PATRIC / BV-BRC"*
([BV-BRC citation](https://www.bv-brc.org/citation);
[re3data record](https://www.re3data.org/repository/r3d100014100)). Stamp
records `license: US Government public domain (BV-BRC)` and keep the citation in
provenance — **do not relabel as CC0** in the field even though it is
CC0-compatible.

> Caveat to note in the seeder: the *curated description text* originates with
> the SEED/FIG curators; it is distributed by BV-BRC as public-domain data, so
> reuse is fine, but attribute the SEED/RAST papers in provenance.

## 4. Class vs instance — the pivot rule

**Confirmed: the seedable unit is the subsystem (and optionally the functional
role) as a CLASS — never one record per protein/gene.** The `subsystem_ref`
endpoint is already the class-level projection; the per-genome
`.subsystem.tab` files are the instance layer and are excluded. Genomes / genes
that implement a role become `canonical_examples` (schema slot exists,
`proteintraitsmech.yaml:265`) on the class record — the same pivot already used
for COG, DisProt and the UniProt peptide classes.

## 5. Target-schema mapping

Existing FUNCTION categories (`proteintraitsmech.yaml:1106-1171`):
`FUNC_ENZYMATIC_ACTIVITY`, `FUNC_PATHWAY`, `FUNC_ORTHOLOG_GROUP`,
`FUNC_PROTEIN_FAMILY`, etc.

| SEED concept | → Category | Grounding / identifier | Parenting |
|---|---|---|---|
| **Superclass / Class / Subclass** | parent nodes only | mint `proteintraitsmech:SEED_SUPERCLASS_<name>` etc. | classification spine |
| **Subsystem** | **`FUNC_PATHWAY`** | `id` = `subsystem_ref.subsystem_id` (e.g. `Mycosporine_synthesis_cluster`); consider `xref` to BV-BRC | `parent_traits` → its subclass/class/superclass node |
| **Functional role _with_ EC** | **`FUNC_ENZYMATIC_ACTIVITY`** *(only if seeded — see §6)* | parse `(EC x.x.x.x)` from `role_name`; ground via `mapped_xrefs` to `EC:x.x.x.x` (already-seeded EC record) | member of its subsystem |
| **Functional role _without_ EC** | `FUNC_PATHWAY` role, or drop | RoleID from `subsystem_id`+role | member of its subsystem |

Recommended concrete mapping: **subsystem → `FUNC_PATHWAY`** (parented by the
superclass/class/subclass spine); **role (EC-bearing) → `FUNC_ENZYMATIC_ACTIVITY`
grounded on the parsed EC** — but per §6 the role level is largely redundant and
should likely be dropped in a first pass.

## 6. Overlap / dedup — the redundancy flag

| Already seeded | Overlaps SEED… | Verdict |
|---|---|---|
| **ExPASy ENZYME full EC hierarchy** (`seed_ec.py`, `FUNC_ENZYMATIC_ACTIVITY`) | **SEED functional roles** (EC embedded in role names) | **High redundancy.** Every EC-bearing role duplicates an existing EC record. Do **not** re-seed as new enzymatic-activity traits — at most `mapped_xrefs` a subsystem to the EC. |
| **Reactome pathways** (`seed_reactome.py`, `FUNC_PATHWAY`) | **SEED subsystems** (= pathways/modules) | **Partial overlap**, but Reactome is eukaryote/human-centric; SEED adds **prokaryotic** modules → net-new coverage. |
| **COG 2020** (`seed_cog.py`, `FUNC_ORTHOLOG_GROUP`) + KOG, eggNOG-style | SEED FIGfams / role families | Orthology axis already covered; SEED roles ≈ FIGfams add little to `FUNC_ORTHOLOG_GROUP`. |
| **Rhea / EC→GO / InterPro / CDD / NCBIfam / TCDB** | role functions | Function space already dense. |

**Bottom line:** the roles are ~redundant with EC; the **subsystems** are the
only meaningfully new content, and even they compete with a (not-yet-done) KEGG
module seed that would be better-maintained and better-grounded (KO/KEGG-module
CURIEs). SEED's edge is **curated microbial functional modules** absent from
Reactome.

## 7. Verdict & ranked recommendation

**DEFER** — behind a KEGG pathway/module seed. Rank vs. current candidates:

1. KEGG modules/pathways (better prokaryotic `FUNC_PATHWAY` grounding) — *do first if pathway coverage is the goal.*
2. **SEED subsystems** — *secondary alternative; seed only if KEGG licence/effort blocks it.*
3. SEED functional roles — **skip** (redundant with already-seeded EC).

**If seeded (narrow plan):**
- **Input:** one pull of `https://www.bv-brc.org/api/subsystem_ref/` (JSON, ~920
  records; page with `limit()`/cursor). Cache under `data/raw/seed/`.
- **Parse:** for each record read `superclass/class/subclass/subsystem_id/
  subsystem_name/description/role_name[]`.
- **Emit (class-level only):**
  - superclass/class/subclass → mint parent nodes;
  - **one `FUNC_PATHWAY` record per subsystem** (~920), `parent_traits` = its
    subclass→class→superclass spine, `definition` = the curated `description`,
    `license: US Government public domain (BV-BRC)`, EC numbers parsed from
    `role_name` attached as `mapped_xrefs` (`EC:x.x.x.x`) rather than new records.
  - **Do NOT** emit per-role or per-gene records; **do NOT** touch
    `.subsystem.tab`.
- **Dedup:** run `merge-traits` against Reactome `FUNC_PATHWAY` and the EC
  corpus after seeding.
- Register in `download.yaml` as `status: deferred` (or `candidate`) with the
  `subsystem_ref` URL and the public-domain licence until a decision is made.

---

## Sources

- SEED/RAST: [The SEED and RAST (PMC3965101)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3965101/) · [Subsystems approach, NAR 2005](https://academic.oup.com/nar/article/33/17/5691/1067791) · [SEED Servers, PLOS One](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0048053)
- SEED docs: [SEED Viewer Manual/Subsystems](https://www.theseed.org/wiki/SEED_Viewer_Manual/Subsystems) · [Glossary](https://www.theseed.org/wiki/Glossary) · [theseed.org](https://theseed.org/wiki/Main_Page) · [Bioregistry: seed](https://bioregistry.io/registry/seed)
- BV-BRC: [BV-BRC paper (PMC9825582)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9825582/) · [Subsystems tab ref](https://www.bv-brc.org/docs/quick_references/organisms_taxon/subsystems_tab.html) · [Subsystems data & viewer](https://www.bv-brc.org/docs/quick_references/other/subsystems_data.html) · [FTP quick ref](https://www.bv-brc.org/docs/quick_references/ftp.html) · [API doc](https://www.bv-brc.org/api/doc/) · [Citation](https://www.bv-brc.org/citation) · [re3data](https://www.re3data.org/repository/r3d100014100)
- Verified live: `https://www.bv-brc.org/api/subsystem_ref/` → 920 subsystem records (superclass/class/subclass/subsystem_name/description/role_name[]).
- Mirrors: [hallamlab/MetaPathwaysGUI SEED_subsystems.txt](https://github.com/hallamlab/MetaPathwaysGUI/blob/master/functional_categories/SEED_subsystems.txt) · [SEEDtk](https://github.com/SEEDtk) · [ModelSEEDDatabase](https://github.com/ModelSEED/ModelSEEDDatabase)
- Tree size (~10k nodes): [BMC Bioinformatics 12(S1):S21](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-12-S1-S21)
