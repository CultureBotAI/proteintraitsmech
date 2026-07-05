# Source documentation & entry-metadata files — structure/family sources

Goal: for each SEEDED structure/family-classification source, find the downloadable
**documentation** (per-entry prose descriptions — the analog of PROSITE's
`prosite.doc`/PDOC) and **entry-metadata** files (names, hierarchy, cross-refs,
literature) that could enrich record **definitions / labels / citations**.

We recently enriched PROSITE from `prosite.doc` (PDOC) and CDD/NCBIfam from
`cddid`/`hmm_PGAP` metadata. This report finds the *missing* equivalent per source.

Sources in scope: **CATH, SCOPe, ECOD, TED, Pfam, InterPro, CDD, NCBIfam, SMART, HAMAP**.

Method: read `download.yaml` + each `scripts/seed_*.py` to see what is already
fetched, then verified download listings on the live FTP/HTTP hosts (July 2026).
This is research + drafts only — no code, records, or `download.yaml` were edited.

Legend for "already-have?": **YES** = fetched by a `just fetch-*` recipe today;
**NO** = not fetched; **PARTIAL** = file is fetched but the enriching columns/blocks
inside it are not parsed by the seeder.

---

## Executive summary of what is already fetched (per source)

| Source | Seeder | Currently fetched | Prose used for definition today |
|---|---|---|---|
| CATH | `seed_cath.py` | `cath-names.txt` only | node name string |
| SCOPe | `seed_scope.py` | `dir.des`, `dir.hie` | node label + sccs (templated) |
| ECOD | `seed_ecod.py` | `ecod.latest.domains.txt` | group name (templated) |
| TED | `seed_ted.py` | 2 `*.domain_summary.tsv.gz` | structural metrics (templated) |
| Pfam | `seed_pfam.py` | `Pfam-A.clans.tsv.gz`, `Pfam-A.hmm.dat.gz` | short `description` field |
| InterPro | `seed_interpro.py` | `interpro.xml.gz`, `ParentChildTreeFile.txt`, `entry.list`, `interpro2go` | InterPro abstract (rich) |
| CDD | `seed_cdd.py` | `cddid_all.tbl.gz`, `family_superfamily_links` | one-line `desc` field |
| NCBIfam | `seed_ncbifam.py` | `hmm_PGAP.tsv` | `product_name`-templated |
| SMART | (via InterPro) | none of its own | — |
| HAMAP | (via InterPro / PROSITE profiles) | none of its own | — |

---

## CATH

CATH exposes node **names** but essentially no per-node prose paragraphs; its richest
per-entry text is the per-**domain** description file (CDDF), which is instance-level
(one entry per PDB domain), not class-level. C/A/T/H node "definitions" are just names.

Live listing: `http://download.cathdb.info/cath/releases/latest-release/cath-classification-data/`

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| cath-names.txt | http://download.cathdb.info/cath/releases/latest-release/cath-classification-data/cath-names.txt | TSV (`code \t rep-domain \t :name`) | node **name** for each C/A/T/H node | CATH data policy (CC-BY 4.0 as stamped in manifest) | **YES** |
| cath-domain-description-file.txt (CDDF) | http://download.cathdb.info/cath/releases/latest-release/cath-classification-data/cath-domain-description-file.txt | fixed-field records (DOMAIN/NAME/SOURCE/CATHCODE/CLASS/ARCH/TOPOL/HOMOL/DSEQ/SEGMENT…) | per-**domain** name + source protein + the CLASS/ARCH/TOPOL/HOMOL **level names** + secondary-structure string + segments | CC-BY 4.0 | **NO** |
| cath-superfamily-list.txt | http://download.cathdb.info/cath/releases/latest-release/cath-classification-data/cath-superfamily-list.txt | TSV | superfamily → representative + FunFam counts | CC-BY 4.0 | **NO** |
| README (file-format docs) | http://download.cathdb.info/cath/releases/latest-release/README-cath-classification-data-file-formats.txt | text | column/field documentation for the above | CC-BY 4.0 | **NO** |

- **Documentation / prose:** No true per-node prose doc. The CDDF `NAME`/`SOURCE`
  fields are per-domain protein names, not class definitions.
- **Entry metadata:** cath-names (names) already have; CDDF adds HOMOL-level **names
  for superfamilies that are blank ("-") in cath-names.txt**, plus a per-node
  secondary-structure summary that could populate the STRUCT secondary-structure slots.
- **Literature:** CATH publishes **no per-node PMID/DOI file**. (Superfamily-level
  functional literature lives only in FunFam/CATH-API annotations, not a bulk file.)
- **Licence:** CATH data are distributed under the CATH data policy; the manifest
  already stamps CATH records CC-BY 4.0.

**Recommended next enrichment:** parse CDDF to backfill **names for the many unnamed
(`-`) homologous-superfamily nodes** and to attach a secondary-structure-content
summary. Low prose value (no paragraphs, no citations) — treat as a label-completion,
not a definition-enrichment, source.

Draft `download.yaml` block:

```yaml
-
  url: http://download.cathdb.info/cath/releases/latest-release/cath-classification-data/cath-domain-description-file.txt
  local_name: cath/cath-domain-description-file.txt
  name: CATH domain description file (CDDF) — per-domain names + SS + level names
  source: cath_gene3d
  license: CC-BY 4.0
  status: candidate
  note: >-
    Backfills names for unnamed ("-") CATH homologous-superfamily nodes and a
    per-node secondary-structure summary. Instance-level (one record per PDB
    domain); parse for HOMOL-level names + SS content only. No PMIDs.
```

---

## SCOPe

SCOPe is the strongest CATH-family win: it ships a genuine **per-node curator-comment
file** (`dir.com`) — the direct analog of `prosite.doc` — that we do **not** fetch. It
also has the classification file `dir.cla`.

Live listing: `https://scop.berkeley.edu/downloads/parse/` (v2.08-stable, 2021-11-03)

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| dir.com.scope.2.08-stable.txt | https://scop.berkeley.edu/downloads/parse/dir.com.scope.2.08-stable.txt | text (`sunid \t free-text comment`) | **per-node curator comments** — the prose descriptions (function, fold notes, references in prose) | CC-BY (SCOPe terms) | **NO** |
| dir.des.scope.2.08-stable.txt | https://scop.berkeley.edu/downloads/parse/dir.des.scope.2.08-stable.txt | TSV (sunid, type, sccs, sid, description) | node type + sccs + label | CC-BY | **YES** |
| dir.hie.scope.2.08-stable.txt | https://scop.berkeley.edu/downloads/parse/dir.hie.scope.2.08-stable.txt | TSV (sunid, parent, children) | hierarchy | CC-BY | **YES** |
| dir.cla.scope.2.08-stable.txt | https://scop.berkeley.edu/downloads/parse/dir.cla.scope.2.08-stable.txt | TSV | full classification string + PDB/region per domain | CC-BY | **NO** |

- **Documentation / prose:** **YES — `dir.com`.** Curator comments per sunid; the
  closest thing in the classification world to PROSITE's PDOC. Often contains free-text
  references ("see PubMed …", author names) and fold rationale.
- **Entry metadata:** `dir.des` (have) + `dir.cla` (per-domain classification, not
  needed for class-level records).
- **Literature:** No structured PMID column, but `dir.com` embeds citations in prose;
  they would need light regex extraction to become `EvidenceItem`s.
- **Licence:** SCOPe CC-BY (already stamped tighter-than-CC0 in `seed_scope.py`).

**Recommended next enrichment:** fetch `dir.com` and attach the comment text to the
matching SCOPe node record as an enriched `definition` (or `comment`) — this is the
single highest-value classification-source prose file in scope after PDOC.

Draft `download.yaml` block:

```yaml
-
  url: https://scop.berkeley.edu/downloads/parse/dir.com.scope.2.08-stable.txt
  local_name: scope/dir.com.scope.2.08-stable.txt
  name: SCOPe curator comments (dir.com) — per-node prose descriptions
  source: scop2
  license: CC-BY 4.0
  status: candidate
  note: >-
    The PDOC analog for SCOPe: free-text curator comments keyed by sunid. Enriches
    SCOPe node definitions; embedded references can be regex-lifted to EvidenceItems.
    Berkeley host blocks bots — download manually or mirror, like dir.des/dir.hie.
```

---

## ECOD

Honest finding: **ECOD has no separate prose or literature file.** All group names
(architecture, X, H, T, F) are already **columns inside** `ecod.latest.domains.txt`,
which we already fetch — the seeder reads them for labels.

Live listing: `http://prodata.swmed.edu/ecod/distributions/` (host refuses HTTPS/bot
fetches, consistent with the SCOPe/ECOD bot-blocking note in the manifest).

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| ecod.latest.domains.txt | http://prodata.swmed.edu/ecod/distributions/ecod.latest.domains.txt | TSV (uid, ecod_domain_id, f_id, pdb, chain, ranges, unp_acc, **arch_name, x_name, h_name, t_name, f_name**, asm_status, ligand) | per-domain assignment **+ all five level names inline** | free for academic use (ECOD) | **YES** |
| ecod.latest.fasta.txt / *.pdb.tsv / F40/F70/F99 sets | http://prodata.swmed.edu/ecod/distributions/ | FASTA / TSV | sequences + representative sets | ECOD academic | **NO** (not needed) |

- **Documentation / prose:** none exists. No `dir.com`/PDOC analog.
- **Entry metadata:** already inline (the `*_name` columns). Note many **F-group names
  are literally Pfam accessions/ids** (e.g. `F_...` named after a Pfam family).
- **Literature:** none per entry.
- **Licence:** free for academic use (already stamped).

**Recommended next enrichment:** no new download. The only lift is **cross-referencing
ECOD F-group names that equal Pfam ids to the corresponding Pfam/InterPro abstract** to
give ECOD F-groups a real definition (they currently have templated text). This reuses
files already fetched (Pfam/InterPro) rather than a new ECOD file.

*(No draft block — nothing new to download.)*

---

## TED

TED (The Encyclopedia of Domains) is a structural-domain catalogue keyed on AlphaFold
models. It has **no named families and no prose** — entries are structural domains with
CATH labels + geometric metrics. All metadata is columnar in the `*.domain_summary`
files; the two representative subsets we seed are the only class-scale slices.

Live record: `https://zenodo.org/records/13908086` (CC-BY 4.0)

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| novel_folds_set.domain_summary.tsv.gz | https://zenodo.org/records/13908086/files/novel_folds_set.domain_summary.tsv.gz | gz-TSV | 7,427 novel-fold representatives + metrics | CC-BY 4.0 | **YES** |
| high_symmetry_folds_set.domain_summary.tsv.gz | https://zenodo.org/records/13908086/files/high_symmetry_folds_set.domain_summary.tsv.gz | gz-TSV | 6,433 high-symmetry fold reps | CC-BY 4.0 | **YES** |
| ted_365m.domain_summary.cath.globularity.taxid.tsv.gz | https://zenodo.org/records/13908086/files/ted_365m.domain_summary.cath.globularity.taxid.tsv.gz | gz-TSV (19.9 GB) | full 365 M assignments + CATH labels + globularity + taxid | CC-BY 4.0 | **NO** (too large; instance-level) |
| ted-tools-main.zip | https://zenodo.org/records/13908086/files/ted-tools-main.zip | zip | code + column docs | CC-BY 4.0 | **NO** |

- **Documentation / prose:** none. Column semantics documented only in the paper /
  `ted-tools` repo, not per-entry text.
- **Entry metadata:** CATH label + structural metrics (already parsed for definitions).
- **Literature:** none per entry (cite the TED paper globally).
- **Licence:** CC-BY 4.0.

**Recommended next enrichment:** none from TED itself. TED entries that carry a **CATH
label** could inherit the CATH node name/definition (from cath-names / CDDF) — again a
cross-reference to an already-fetched source, not a new TED download.

*(No draft block — nothing new to download.)*

---

## Pfam

Pfam merged into InterPro, so the rich curated abstract text is served as the **InterPro
abstract** (already fetched inside `interpro.xml.gz`). But Pfam **still ships two files
we don't fetch that carry per-family prose *and literature references*** that InterPro
does not always surface: `Pfam-A.seed.gz` (Stockholm `#=GF CC` comment + `#=GF RN/RM`
PMIDs) and `pfamA.txt.gz` (the SQL dump text: comment, description, references, GA
thresholds). Today the seeder uses only the short `description` from
`Pfam-A.clans.tsv.gz`.

Live listing: `https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/` (rel 2026-01)

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| Pfam-A.clans.tsv.gz | https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.clans.tsv.gz | gz-TSV | accession, clan, clan_name, id, **short description** | public domain (Pfam/InterPro) | **YES** |
| Pfam-A.hmm.dat.gz | https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.dat.gz | gz-Stockholm-ish | family type, GA, TC, NC, length | public domain | **YES** |
| **Pfam-A.seed.gz** | https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.seed.gz | gz-Stockholm (185 MB) | **`#=GF CC` free-text comment (the prose) + `#=GF RN/RM/RT/RA` literature refs (PMIDs)** per family | public domain | **NO** |
| **pfamA.txt.gz** | https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/pfamA.txt.gz | gz-TSV SQL dump (13 MB) | per-family: description, **comment**, GA/TC/NC, type, **wikipedia + references** columns | public domain | **NO** |
| Pfam-C.gz | https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-C.gz | gz | clan definitions + `CC` comment + member list | public domain | **NO** |

- **Documentation / prose:** `Pfam-A.seed.gz` `#=GF CC` is the classic Pfam comment
  paragraph; `pfamA.txt.gz` `comment` column is the same text in tabular form (much
  smaller download — **13 MB vs 185 MB**, and no Stockholm parsing).
- **Entry metadata:** `pfamA.txt.gz` also gives GA/TC/NC thresholds, type, wikipedia
  title — richer than the clans TSV.
- **Literature:** **YES — per-family PMIDs.** `Pfam-A.seed.gz` `#=GF RM` lines and the
  `pfamA` references carry PMIDs → directly usable as `EvidenceItem`s. This is the only
  in-scope family source (besides NCBIfam) with structured per-entry citations.
- **Licence:** Pfam data are public domain (CC0-equivalent) via EBI/InterPro.

**Recommended next enrichment:** fetch `pfamA.txt.gz`, use its `comment` column to
enrich Pfam definitions beyond the one-line description, and lift its/`Pfam-A.seed`
`#=GF RM` **PMIDs into EvidenceItems**. Prefer `pfamA.txt.gz` (tabular, 13 MB) over the
185 MB seed alignment unless the `#=GF RM` refs are needed at family granularity.

Draft `download.yaml` blocks:

```yaml
-
  url: https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/pfamA.txt.gz
  local_name: pfam/pfamA.txt.gz
  name: Pfam-A SQL dump (per-family comment + references + thresholds)
  source: pfam
  license: public domain (Pfam / InterPro)
  status: candidate
  note: >-
    Tabular per-family metadata (13 MB): description + long `comment` prose + GA/TC/NC
    + type + wikipedia + literature references. Enriches Pfam definitions and supplies
    per-family PMIDs for EvidenceItems. Smaller alternative to parsing Pfam-A.seed.gz.
-
  url: https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.seed.gz
  local_name: pfam/Pfam-A.seed.gz
  name: Pfam-A seed alignments (#=GF CC comment + #=GF RM literature refs)
  source: pfam
  license: public domain (Pfam / InterPro)
  status: candidate
  note: >-
    185 MB Stockholm. Use only if per-family #=GF RM PMIDs / #=GF CC prose are needed
    at seed-alignment granularity; otherwise pfamA.txt.gz carries the same comment text.
```

---

## InterPro

InterPro is the reference case: we already fetch `interpro.xml.gz` (rich abstracts +
types) and use it for definitions. The **gap is not a missing download — it is that the
`<publications>` block already inside `interpro.xml.gz` is not being extracted**. Each
InterPro entry's XML carries a `<pub_list>`/`<publications>` element with **PMID + DOI +
citation** — the schema's `EvidenceItem` slot could be populated with zero new fetches.

Live listing: `https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/`

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| interpro.xml.gz | https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/interpro.xml.gz | gz-XML | abstracts + types + member_list + GO + **`<publications>` (PMID/DOI) per entry** | public domain | **PARTIAL** (fetched; publications not parsed) |
| entry.list | https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/entry.list | TSV | accession, type, name | public domain | **YES** |
| ParentChildTreeFile.txt | https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/ParentChildTreeFile.txt | text tree | parent/child hierarchy | public domain | **YES** |
| interpro2go | https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/interpro2go | text | InterPro → GO | public domain | **YES** |

- **Documentation / prose:** the InterPro abstract (already used) is the best prose in
  the whole set — no additional file needed.
- **Entry metadata:** complete already.
- **Literature:** **YES, and already downloaded** — inside `interpro.xml.gz`
  `<publications>`. Also underlies the enrichment path for Pfam/SMART/HAMAP entries that
  are InterPro-integrated (their citations surface through the InterPro abstract's refs).
- **Licence:** public domain (EBI).

**Recommended next enrichment:** extend `seed_interpro.py` to read the `<publications>`
element already present in `interpro.xml.gz` and emit per-entry PMIDs/DOIs as
`EvidenceItem`s. Highest ROI of all — a parser change, not a download.

*(No draft block — file already in the manifest; only the parser needs to read the
`<publications>` element.)*

---

## CDD

We fetch `cddid_all.tbl.gz` (one-line desc) and `family_superfamily_links`. CDD's
longer curator descriptions are **not** in a per-entry prose file: the detailed
paragraph shown on the web comes from `data.json` (456 MB, everything) and there is a
`README`. The genuinely useful *missing* files are **`cddannot_generic.dat.gz` /
`cddannot.dat.gz`** — per-domain **conserved-feature/site annotations** (feature name +
evidence + residues) — which map onto STRUCT_ACTIVE_SITE / STRUCT_BINDING_SITE features,
plus `cdd.versions`/`README` for provenance.

Live listing: `https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/`

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| cddid_all.tbl.gz | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/cddid_all.tbl.gz | gz-TSV | PSSMID, acc, short name, **1-line desc**, length | US Gov public domain | **YES** |
| family_superfamily_links | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/family_superfamily_links | TSV | family → superfamily hierarchy | public domain | **YES** |
| cddannot_generic.dat.gz | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/cddannot_generic.dat.gz | gz (441 KB) | per-domain **conserved-feature/site annotations** (feature label + residues) | public domain | **NO** |
| cddannot.dat.gz | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/cddannot.dat.gz | gz (794 KB) | full feature-annotation set (curated sites) | public domain | **NO** |
| data.json | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/data.json | JSON (456 MB) | comprehensive per-domain record incl. long descriptions | public domain | **NO** (large) |
| README | https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/README | text (53 KB) | file-format + column documentation | public domain | **NO** |

- **Documentation / prose:** the one-line `desc` (have) is CDD's only *compact* prose;
  full paragraphs exist only in the 456 MB `data.json`. No small per-entry prose file.
- **Entry metadata:** `cddannot*` add curated **feature/site** annotations — richer than
  definition text; these are structural-feature payloads, not paragraphs.
- **Literature:** **no bulk per-entry PMID file** for CDD's own `cd*` models. (Web pages
  cite references but there is no compact citations dump.)
- **Licence:** US Government public domain.

**Recommended next enrichment:** fetch `cddannot_generic.dat.gz` to attach curated
conserved-feature/site annotations to CDD domain records (feeds STRUCT_ACTIVE_SITE /
STRUCT_BINDING_SITE features), and grab the `README` for column provenance. No compact
prose/citation win beyond what `cddid` already gives.

Draft `download.yaml` block:

```yaml
-
  url: https://ftp.ncbi.nlm.nih.gov/pub/mmdb/cdd/cddannot_generic.dat.gz
  local_name: cdd/cddannot_generic.dat.gz
  name: CDD conserved-feature / site annotations (generic)
  source: cdd
  license: US Government public domain
  status: candidate
  note: >-
    Per-domain curated feature/site annotations (feature label + residues). Feeds
    STRUCT_ACTIVE_SITE / STRUCT_BINDING_SITE feature payloads on CDD records; not prose.
    Full set in cddannot.dat.gz; column docs in the CDD README.
```

---

## NCBIfam

Honest finding: NCBIfam's `hmm_PGAP.tsv` (already fetched) **already contains the
documentation and literature columns** — the seeder just doesn't use all of them.
Verified header of the fetched file includes:
`product_name`, `gene_symbol`, `ec_numbers`, `go_terms`, **`pmids`**, `family_type`,
`taxonomic_range_name`, and a free-text **`comment`** column.

Live listing: `https://ftp.ncbi.nlm.nih.gov/hmm/current/`

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| hmm_PGAP.tsv | https://ftp.ncbi.nlm.nih.gov/hmm/current/hmm_PGAP.tsv | TSV | accession, label, product_name, gene, **ec_numbers, go_terms, pmids, comment**, family_type, taxonomic_range | US Gov public domain | **PARTIAL** (fetched; `pmids` + `comment` not parsed) |
| hmm_PGAP.HMM.tgz | https://ftp.ncbi.nlm.nih.gov/hmm/current/hmm_PGAP.HMM.tgz | tgz | the HMMs (DESC/COM lines) | public domain | **NO** (not needed) |

- **Documentation / prose:** the `comment` column carries curator free text per family;
  `product_name` is the concise definition basis already used.
- **Entry metadata:** ec_numbers, go_terms already parsed to xrefs.
- **Literature:** **YES — the `pmids` column is a structured per-family PMID list**,
  already sitting in the fetched TSV, unused. Direct `EvidenceItem` fodder.
- **Licence:** US Government public domain.

**Recommended next enrichment:** no new download — extend `seed_ncbifam.py` to read the
**`pmids`** column (→ EvidenceItems) and the **`comment`** column (→ enrich definition).
Second-highest ROI after InterPro publications: pure parser change on an already-fetched
file.

*(No draft block — file already in the manifest; the `pmids`/`comment` columns just need
parsing.)*

---

## SMART

SMART is an InterPro member DB with **no open bulk download** — its HMMs, alignments and
thresholds are behind an academic/commercial **licence** (EMBLEM / biobyte). There is no
public `dir.com`/PDOC-style prose file and no bulk PMID file.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| SMART bulk data (HMMs/alignments/thresholds) | https://software.embl-em.de/software/18 (academic licence) | licence-gated | domain models + descriptions | proprietary licence (EMBLEM) — **FLAGGED** | **NO** (not open) |
| SMART entries via InterPro | (inside `interpro.xml.gz`, already fetched) | XML | SMART signatures integrated into InterPro abstracts + publications | public domain (InterPro) | **YES (indirect)** |

- **Documentation / prose:** only via the InterPro abstract of the InterPro entry that
  integrates each SMART signature.
- **Entry metadata / literature:** SMART's own citations surface through InterPro
  `<publications>` (see InterPro section) — no separate SMART file to fetch.
- **Licence:** SMART's bulk data are licence-restricted (incompatible with CC0
  redistribution) — do **not** ingest directly; rely on InterPro.

**Recommended next enrichment:** none direct. SMART enrichment rides entirely on the
InterPro-publications parser change already recommended. Do not add a SMART download
block (licence-incompatible).

*(No draft block — licence-gated; use InterPro.)*

---

## HAMAP

HAMAP (SIB) ships open files on the ExPASy FTP. Its per-family prose lives in the
**profile `DE` lines** and, more richly, in the **`hamap_rules.dat`** annotation-rule
file (UniRule-style: family description, taxonomic scope, annotations, and references).
This is the HAMAP analog of a prose/metadata doc and we fetch none of it today.

Live listing: `https://ftp.expasy.org/databases/hamap/`

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| hamap.prf.gz | https://ftp.expasy.org/databases/hamap/hamap.prf.gz | gz-PROSITE-profile (18 MB) | per-family PROSITE-format profiles incl. `DE` description + `AC`/`ID` | CC-BY-ND 4.0 (SIB) — **FLAGGED (NoDerivatives, like PROSITE)** | **NO** |
| hamap_rules.dat | https://ftp.expasy.org/databases/hamap/hamap_rules.dat | text (6.4 MB) | per-rule **family description + annotations + taxonomic scope + literature refs** | CC-BY-ND 4.0 (SIB) — **FLAGGED** | **NO** |
| rules_index.dat | https://ftp.expasy.org/databases/hamap/rules_index.dat | text (173 KB) | rule ↔ family index | CC-BY-ND 4.0 (SIB) | **NO** |
| README / SOP PDFs | https://ftp.expasy.org/databases/hamap/README | text/PDF | format + curation docs | CC-BY-ND (SIB) | **NO** |

- **Documentation / prose:** `hamap_rules.dat` is the prose+annotation doc (the PDOC
  analog for HAMAP); `hamap.prf.gz` `DE` lines give the concise family definition.
- **Entry metadata:** family id/accession, taxonomic scope, annotation rules.
- **Literature:** HAMAP rules cite references; also surfaces via InterPro `<publications>`
  for HAMAP-integrated entries.
- **Licence:** **FLAGGED** — HAMAP/SIB data are CC-BY-ND (NoDerivatives), the same
  restriction that flagged PROSITE. Prose text can be *referenced/quoted with attribution*
  but redistributing derived text under CC0 is problematic — treat like PROSITE (extract
  definition, keep provenance, do not relicense).

**Recommended next enrichment:** if pursued under the same treatment as PROSITE (verbatim
snippet + attribution, no relicensing), fetch `hamap.prf.gz` for `DE` definitions and
`hamap_rules.dat` for family prose. Otherwise, take HAMAP enrichment for free via the
InterPro abstract/publications, which is public-domain and already downloaded.

Draft `download.yaml` blocks (licence-flagged — mirror the PROSITE treatment):

```yaml
-
  url: https://ftp.expasy.org/databases/hamap/hamap.prf.gz
  local_name: hamap/hamap.prf.gz
  name: HAMAP profiles (PROSITE format) — per-family DE definition
  source: hamap
  license: CC BY-ND 4.0 (SIB) — NoDerivatives — FLAGGED
  status: candidate
  note: >-
    DE lines give concise HAMAP family definitions. NoDerivatives licence (as PROSITE):
    quote with attribution, do not relicense derived text. Public-domain alternative:
    take HAMAP text via the InterPro abstract (interpro.xml.gz), already fetched.
-
  url: https://ftp.expasy.org/databases/hamap/hamap_rules.dat
  local_name: hamap/hamap_rules.dat
  name: HAMAP annotation rules — family prose + refs (PDOC analog)
  source: hamap
  license: CC BY-ND 4.0 (SIB) — NoDerivatives — FLAGGED
  status: candidate
  note: >-
    UniRule-style per-family description, taxonomic scope, annotations, literature refs.
    Same NoDerivatives caveat as hamap.prf.gz / PROSITE.
```

---

## Ranked recommendations (highest-value first)

1. **InterPro `<publications>`** — parser change only; per-entry PMID/DOI already sitting
   in the fetched `interpro.xml.gz`. Also the public-domain citation path for Pfam, SMART
   and HAMAP integrated entries. **Zero new download.**
2. **NCBIfam `pmids` + `comment`** — parser change only; per-family PMIDs + curator prose
   already in the fetched `hmm_PGAP.tsv`. **Zero new download.**
3. **SCOPe `dir.com`** — a real per-node curator-comment prose file (the PDOC analog for
   SCOPe); one new download (CC-BY). Highest-value *new* fetch.
4. **Pfam `pfamA.txt.gz`** (13 MB) — per-family long `comment` + references; public
   domain; enriches definitions and supplies PMIDs.
5. **CDD `cddannot_generic.dat.gz`** — curated conserved-feature/site annotations (feeds
   STRUCT_ACTIVE_SITE/BINDING_SITE features), not prose; public domain.
6. **CATH CDDF** — backfills unnamed superfamily node names + SS content; label
   completion, no citations.
7. **HAMAP `hamap.prf.gz` / `hamap_rules.dat`** — real prose but **CC-BY-ND FLAGGED**
   (PROSITE-style caveat); prefer the InterPro path.
8. **ECOD / TED / SMART** — no missing doc/metadata download. ECOD names are already
   inline; TED has no families/prose; SMART is licence-gated (use InterPro).
```
