---
topic: protein sequence & structure trait sources
round: 2
date: 2026-07-02
question: >-
  Beyond the Round 1 sources, which additional established, downloadable
  resources supply protein sequence/structure traits — preferably as
  classifications/hierarchies, minimally with each trait defined in terms of
  sequence or structure elements?
prior_round: protein-trait-sources-round1.md
method: >-
  Web search + source-page/paper verification (WebSearch/WebFetch), July 2026.
  Each candidate checked for: established status, bulk download + format,
  licence, hierarchy, and whether traits are defined via sequence/structure.
---

# Protein trait sources — Round 2

Builds on [Round 1](protein-trait-sources-round1.md). Focus of this round: an
**integrative** family resource, the two remaining **structural
classifications** (CATH, SCOP2), and sources that fill Round 1's **open gaps**
(structural repeats, metal/ligand sites, enzyme superfamilies, linear motifs,
PTMs, disorder consensus).

## Ranked findings

Legend — Fit: which `trait_category` it feeds. Hier: has a parent/child
classification. ✅ recommend · ⚠️ adopt with caveat · ⛔ skip.

| # | Source | Fit (category) | Hier | Download / format | Licence | Rec |
|---|--------|----------------|------|-------------------|---------|-----|
| 1 | **InterPro** v101 | STRUCT_DOMAIN, SEQ_MOTIF, STRUCT_HOMOLOGOUS_SUPERFAMILY (integrative) | ✅ type-specific (ParentChildTreeFile) | FTP `interpro.xml`, `entry.list`, `match_complete.xml` | **public domain** | ✅ top pick |
| 2 | **CATH‑Gene3D** | STRUCT_{CLASS,ARCHITECTURE,TOPOLOGY,HOMOLOGOUS_SUPERFAMILY,DOMAIN} | ✅ C/A/T/H + FunFams | FTP (all releases), HMMs, domain lists | **CC‑BY 4.0** | ✅ validates/extends TED |
| 3 | **RepeatsDB** (2025) | **MIXED_STRUCTURAL_REPEAT** / STRUCT_FOLD | ✅ Class>Topology>Fold>Clan>Family | web services, dataset export (PDB+AlphaFoldDB) | CC‑BY (paper OA) | ✅ fills empty repeat gap |
| 4 | **MEROPS** v12.5 | FUNC_ENZYMATIC_ACTIVITY, STRUCT_ACTIVE_SITE (peptidases) | ✅ clan→family→species | EBI site/FTP, ~3 rel/yr | free (EBI) | ✅ clan=structure, family=sequence |
| 5 | **SCOP2 / SCOPe 2.08** | STRUCT_{CLASS,FOLD,HOMOLOGOUS_SUPERFAMILY,DOMAIN} | ✅ class/fold/superfamily/family | SCOPe flat files + MySQL on **Zenodo**; SCOP2 via RCSB | CC‑BY | ⚠️ Berkeley host blocks bots → use Zenodo mirror |
| 6 | **MobiDB** (2025) | SEQ_DISORDER (consensus) | — (ECO‑typed) | bulk TSV / FASTA / JSON | **CC‑BY** | ✅ complements DisProt (consensus + IDPO/GO) |
| 7 | **dbPTM** (2025) | SEQ_MODIFIED_RESIDUE, SEQ_{GLYCOSYLATION,CROSSLINK}_SITE | by PTM type | website bulk download | free (academic) | ⚠️ 2.24M experimental sites; huge — subset by type |
| 8 | **SFLD** | FUNC_ENZYMATIC_ACTIVITY (mechanism) | ✅ superfamily→subgroup→family | TSV, MSAs, SSNs (archive) | free (UCSF) | ⚠️ static since 2019 but downloadable |
| 9 | **BioLiP2** | STRUCT_BINDING_SITE | — | full + nr95 flat files | free | ✅ fills sparse binding‑site gap |
| 10 | **MetalPDB** | STRUCT_METAL_SITE | grouped by metal (MFS templates) | FTP by metal + flat file | free (CERM) | ✅ fills sparse metal‑site gap |
| 11 | **CAZy / dbCAN‑seq** | FUNC_ENZYMATIC_ACTIVITY (GH/GT/PL/CE/AA/CBM) | family classes | dbCAN‑seq bulk (CAZy itself no bulk) | dbCAN‑seq **CC‑BY** | ⚠️ seed via dbCAN‑seq, not CAZy directly |
| 12 | **ELM** (2024, 356 classes) | SEQ_MOTIF (SLiMs) | motif class tree | TSV / PSI‑MI XML / MiTAB | ⛔ **non‑commercial only** | ⛔ licence incompatible w/ CC0 redistribution |
| — | NCBIfam, CDD, IDEAL | (from Round 1) | mixed | FTP | PD / CC‑BY | ✅ still worth doing; NCBIfam+CDD are also InterPro members |

## Detail & rationale

**1. InterPro (top pick).** The integrative resource: 85,000 families/domains
combining PROSITE, Pfam, SMART, PRINTS, PANTHER, PIRSF, SFLD, CDD, HAMAP,
NCBIfam, CATH‑Gene3D and SUPERFAMILY, with **type‑specific hierarchies** (a
domain entry only nests under domains, families under families) shipped as
`ParentChildTreeFile.txt`, plus GO/PDBe/AlphaFold mappings. Public domain,
anonymous FTP. Seeding InterPro entries (not the 200M matches) would unify much
of what we seed piecemeal and give real `parent_traits`. Highest leverage.

**2. CATH‑Gene3D.** CC‑BY 4.0, the canonical C(lass)/A(rchitecture)/T(opology)/
H(omologous superfamily) hierarchy + FunFams, full FTP of domain lists,
boundaries and HMMs. TED is CATH‑derived, so CATH gives us the authoritative
upper hierarchy those TED folds hang from.

**3. RepeatsDB.** Directly fills the **empty** `MIXED_STRUCTURAL_REPEAT` bucket:
a 4–5 level structural classification (Class > Topology > Fold, then sequence‑
based Clan > Family in collaboration with Pfam) of structured tandem‑repeat
proteins over PDB **and** AlphaFoldDB (34k+ sequences in 2025), with dataset
download. Each unit has start/end + fold — a structure‑grounded definition.

**4. MEROPS.** Peptidase clans (grouped by **structure**) → families (grouped by
**sequence**) → species: exactly the "definition in sequence/structure terms"
bar, as a clean hierarchy. Complements M‑CSA for proteolytic enzymes.

**5. SCOP2 / SCOPe.** We already have a `seed_scope.py`, blocked because the
Berkeley host rejects bots. The verified fix: pull the parseable files + MySQL
dump from the **Zenodo** archive instead of scop.berkeley.edu. CC‑BY.

**6. MobiDB.** CC‑BY consensus disorder for all UniProt, now with ECO evidence
types and IDPO/GO function terms propagated from DisProt — a scalable
complement to DisProt's manually‑curated set. Bulk TSV/FASTA/JSON.

**9–10. BioLiP2 / MetalPDB.** Both fill Round 1 gaps that are near‑empty today
(`STRUCT_BINDING_SITE` ~2, `STRUCT_METAL_SITE` ~1). BioLiP2 = biologically
relevant ligand–protein interaction sites (freely downloadable, full + nr95);
MetalPDB = metal sites as "Minimal Functional Site" 3D templates grouped by
metal, with FTP + flat file. Both define sites structurally.

**12. ELM — skip on licence.** Excellent SLiM classification (356 classes) but
distributed under a **non‑commercial** licence, incompatible with a CC0
redistributable KB. Track for reference/linking only, do not ingest.

## Recommended next seeds (priority order)

1. **InterPro** entries + `ParentChildTreeFile` → unifying family/domain
   hierarchy (biggest structural win).
2. **RepeatsDB** → fill `MIXED_STRUCTURAL_REPEAT` (currently 0).
3. **CATH‑Gene3D** upper hierarchy → parent TED folds.
4. **MetalPDB** + **BioLiP2** → flesh out metal/binding sites.
5. **MEROPS** → peptidase clan/family hierarchy.
6. **MobiDB** (consensus) + **NCBIfam/CDD/IDEAL** (Round‑1 carryover).

All are branch/subset‑scopeable with the existing seeder pattern; InterPro,
CATH, RepeatsDB, MEROPS and SCOP2 also satisfy the **preferred** hierarchy
criterion.

## Sources

- InterPro 2025 — <https://academic.oup.com/nar/article/53/D1/D444/7905301> · downloads <https://www.ebi.ac.uk/interpro/>
- CATH‑Gene3D — <https://www.cathdb.info/download> · <https://reusabledata.org/cath.html>
- RepeatsDB 2025 — <https://pmc.ncbi.nlm.nih.gov/articles/PMC11701623/> · <https://repeatsdb.org/>
- MEROPS — <https://www.ebi.ac.uk/merops/> · <https://academic.oup.com/nar/article/46/D1/D624/4626772>
- SCOP2 / SCOPe — <https://scop.berkeley.edu/downloads/> · <https://www.rcsb.org/docs/search-and-browse/browse-options/scop2>
- MobiDB 2025 — <https://pmc.ncbi.nlm.nih.gov/articles/PMC11701742/>
- dbPTM 2025 — <https://academic.oup.com/nar/article/53/D1/D377/7889255> · <https://biomics.lab.nycu.edu.tw/dbPTM/>
- SFLD — <https://pmc.ncbi.nlm.nih.gov/articles/PMC3965090/> · <http://sfld.rbvi.ucsf.edu/>
- BioLiP2 — <https://academic.oup.com/nar/article/52/D1/D404/7233921> · <https://zhanggroup.org/BioLiP/>
- MetalPDB — <https://academic.oup.com/nar/article/41/D1/D312/1055329> · <https://metalpdb.cerm.unifi.it/>
- CAZy / dbCAN‑seq — <https://academic.oup.com/nar/article/46/D1/D516/4372485> · <https://en.wikipedia.org/wiki/CAZy>
- ELM 2024 — <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10767929/> · downloads <http://elm.eu.org/downloads.html>
