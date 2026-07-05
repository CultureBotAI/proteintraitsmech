# Source documentation & metadata for FUNCTION-axis sources

Research round: identify downloadable **documentation** (per-entry prose),
**entry-metadata**, and **per-entry literature citations** for every SEEDED
FUNCTION-axis source, so we can enrich record definitions / labels / `synonyms`
/ `xrefs` and populate `evidence` (`EvidenceItem` with PMID/DOI + snippet), the
way `prosite.doc` enriched PROSITE and the CDD/NCBIfam metadata files enriched
those sources.

Verified 2026-07-05 against `download.yaml`, `justfile`, the `scripts/seed_*.py`
seeders, and the live source download pages/FTP listings. **Research only — no
files fetched, no records edited.**

## TL;DR — where the wins are

| Source | Good defs already? | Per-entry PMIDs/DOIs available? | Biggest gap |
|---|---|---|---|
| EC (ExPASy ENZYME) | leaf reactions only | **No** (ENZYME carries no refs) | `CC` comment prose (30,901 lines) unused |
| Rhea | **Yes** (equations) | **Yes** — RDF `rh:citation` only (not in TSV) | citations require `rhea.rdf.gz`/SPARQL |
| GO | **Yes** (go-basic def) | **Yes** — 16,287 defs carry PMID in def-xref | GO not seeded as records; defs on hand |
| ChEBI | Yes (obo def) | **Yes** — `reference.tsv.gz` | chemistry only (not FUNCTION records) |
| TCDB | **boilerplate** (name only) | website only, no bulk file | no downloadable family abstracts |
| CARD/ARO | **Yes** (aro.obo def) | **Yes** — inline in `def` dbxref brackets | seeder may not be lifting def-PMIDs → evidence |
| COG | thin (name+pathway) | **Yes** — `cog-20.def.tab` col 6 (653 COGs) | PMID + PDB columns already fetched, ignored |
| Reactome | **boilerplate** (name only) | **Yes** — ContentService only (API, no bulk) | summation + literatureRef are API-only |
| MEROPS | boilerplate (family name) | **Yes** — inside `meropsweb*.tar.gz` SQL dump | summary/holotype prose + refs need SQL parse |
| SEED/BV-BRC | **Yes** (curated description) | No per-subsystem PMID | already good; source paper cite only |

---

## EC — ExPASy ENZYME

Seeder `seed_ec.py` fetches `enzyme.dat` + `enzclass.txt` (`just fetch-ec`) and
uses `DE`(label) `AN`(synonyms) `CA`(reaction→definition) `DR`(examples). It
**does not read the `CC` comment lines** — and there are **30,901** of them in
enzyme.dat (free-text notes: cofactors, mechanism caveats, relationship to other
ECs, "formerly EC x"). ENZYME has **no literature references at all** (no `RX`/
`RN` records — confirmed: only `ID AN CA CC DE DR` tags present).

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| enzyme.dat | https://ftp.expasy.org/databases/enzyme/enzyme.dat | flat | ID/DE/AN/CA/CC/DR per EC leaf | CC-BY 4.0 | **fetched**; `CC` field unused |
| enzclass.txt | https://ftp.expasy.org/databases/enzyme/enzclass.txt | flat | class/subclass node names | CC-BY 4.0 | fetched + used |
| enzyme.rdf | https://ftp.expasy.org/databases/enzyme/enzyme.rdf | RDF | same content, RDF | CC-BY 4.0 | no (redundant) |

**No new download needed** — the enrichment is a seeder change: parse `CC` and
append it to `definition` (or a `comment` slot). No PMIDs exist to harvest.

**Recommended next enrichment:** in `seed_ec.py`, capture `CC` lines and fold
into the definition for the ~8k leaves that carry comments; no download.yaml
change.

---

## Rhea

Seeder `seed_rhea.py` uses the REST TSV export (`rhea-id,equation,chebi-id,ec`).
Definitions (equations) are **real and good**. Rhea reactions are evidenced by
**~15,500 unique PubMed references** — but the PMID↔reaction links live **only in
the RDF** (`rh:citation` predicate) or via SPARQL; they are **not** in any TSV
(the FTP `tsv/` dir has rhea2ec/rhea2go/rhea2uniprot/rhea2xrefs/rhea-directions/
smiles but no citation column).

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| REST export TSV | https://www.rhea-db.org/rhea?query=&columns=rhea-id,equation,chebi-id,ec&format=tsv | tsv | id/equation/chebi/ec | CC-BY 4.0 | **fetched** (as rhea-reactions.tsv) |
| rhea2xrefs.tsv | https://ftp.expasy.org/databases/rhea/tsv/rhea2xrefs.tsv | tsv (1.1M) | Rhea→KEGG/MetaCyc/EcoCyc/Reactome/MACiE/GO xrefs | CC-BY 4.0 | no |
| rhea.rdf.gz | https://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz | RDF/XML gz | full model incl. `rh:citation` → PubMed | CC-BY 4.0 | **no — only source of per-reaction PMIDs** |
| SPARQL endpoint | https://sparql.rhea-db.org/sparql | SPARQL | query `?reaction rh:citation ?pmid` | CC-BY 4.0 | n/a |

Draft download.yaml block:
```yaml
-
  url: https://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
  local_name: rhea/rhea.rdf.gz
  name: Rhea RDF (per-reaction literature citations)
  source: rhea
  license: CC-BY 4.0
  status: candidate
  note: >-
    The ONLY bulk source of Rhea per-reaction PubMed citations (rh:citation).
    TSV exports carry none. Parse to attach EvidenceItem(PMID) to the 18k
    FUNC_ENZYMATIC_ACTIVITY rhea records. Alternatively query the SPARQL
    endpoint for a rhea-id→PMID TSV instead of downloading the whole RDF.
```

**Recommended next enrichment:** SPARQL-export a `rhea2pmid.tsv`
(`?r rh:citation ?p`) and attach top-N PMIDs per reaction as `evidence`. Highest-
value literature win of the whole set (18k reactions, curated PMIDs).

---

## GO (Gene Ontology)

GO is **not seeded as records** — no `identifier: GO:` records exist; GO is used
only as `mapped_xrefs`/grounding (via ec2go, interpro2go, pfam2go, etc.).
`data/raw/go-basic.obo` is **already fetched**. It has **48,329 `def:` lines,
16,287 of which carry a PMID** in the def dbxref bracket — so GO definitions and
their supporting PMIDs are already on disk if we ever want to (a) label GO-
grounded xrefs, or (b) lift the def PMID onto the grounded trait as evidence.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| go-basic.obo | https://purl.obolibrary.org/obo/go/go-basic.obo | OBO | term name/def(+PMID)/synonyms/is_a | CC-BY 4.0 | **fetched** |
| go.obo (full) | https://purl.obolibrary.org/obo/go.obo | OBO | + relationships (part_of, regulates) | CC-BY 4.0 | no (go-basic sufficient) |
| goa xrefs | (external2go/*2go, already used) | tsv | source→GO maps | CC-BY 4.0 | fetched (ec2go, pfam2go, interpro2go) |

**No new download needed.** Recommended enrichment: when a record has a GO
`mapped_xref`, pull the GO term's def+PMID from go-basic.obo to (a) enrich the
xref label and (b) seed a candidate `EvidenceItem`. Low effort, uses on-disk data.

---

## ChEBI

Not a FUNCTION-axis record source — ChEBI is the **chemistry sidecar**
(`build_chebi_sidecar.py`, `docs/data/chebi.json`) that resolves
`chemical_participants`. Currently uses `compounds.tsv.gz`, `chemical_data.tsv.gz`,
`structures.tsv.gz`. Two flat files add prose + literature per compound:

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| comments.tsv.gz | https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/comments.tsv.gz | tsv gz (169K) | free-text prose per compound | CC-BY 4.0 | no |
| reference.tsv.gz | https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/reference.tsv.gz | tsv gz (131M) | per-compound PubMed/PMC/DOI refs | CC-BY 4.0 | no |
| names.tsv.gz | https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/names.tsv.gz | tsv gz (8.3M) | synonyms per compound | CC-BY 4.0 | no |
| chebi.obo | https://purl.obolibrary.org/obo/chebi.obo | OBO | def(+PMID)/roles/is_a | CC-BY 4.0 | no |

Draft download.yaml block (optional, chemistry-tier):
```yaml
-
  url: https://ftp.ebi.ac.uk/pub/databases/chebi/flat_files/comments.tsv.gz
  local_name: chebi/comments.tsv.gz
  name: ChEBI compound comments (prose)
  source: chebi
  license: CC-BY 4.0
  status: candidate
  note: 169K prose notes per ChEBI id; could enrich chebi.json sidecar tooltips.
```

**Recommended next enrichment:** low priority for FUNCTION records; `names.tsv.gz`
would give participant synonyms in the sidecar. `reference.tsv.gz` is huge (131M)
and per-compound, not per-trait — skip unless chemistry evidence is wanted.

---

## TCDB (Transporter Classification Database)

Seeder `seed_tcdb.py` uses `families.py` (`<TC>\t<family name>`) +
`getSubstrates.py`. Definitions are **boilerplate** ("<name> — a Transporter
Classification family (TC …)"). TCDB **has** rich per-family abstracts and
"18,336 reference citations describing 1,536 families" — but **only on the web
family pages**; there is **no bulk downloadable abstracts/citations file**. The
download surface is a set of CGI mapping endpoints (all tab-delimited), none of
which carries prose or PMIDs.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| families.py | https://www.tcdb.org/cgi-bin/projectv/public/families.py | tsv | TC → family name | CC-BY-SA 3.0 | **fetched** (name only) |
| getSubstrates.py | https://www.tcdb.org/cgi-bin/substrates/getSubstrates.py | tsv | system → ChEBI substrates | CC-BY-SA 3.0 | fetched |
| go.py | https://www.tcdb.org/cgi-bin/projectv/public/go.py | tsv | system → GO | CC-BY-SA 3.0 | no (grounding) |
| pfam.py | https://www.tcdb.org/cgi-bin/projectv/public/pfam.py | tsv | system → Pfam | CC-BY-SA 3.0 | no (grounding) |
| pdb.py | https://www.tcdb.org/cgi-bin/projectv/public/pdb.py | tsv | system → PDB | CC-BY-SA 3.0 | no |
| acc2tcid.py | https://www.tcdb.org/cgi-bin/projectv/public/acc2tcid.py | tsv | UniProt/RefSeq → TC | CC-BY-SA 3.0 | no (examples) |
| family abstracts | https://www.tcdb.org/search/result.php?tc=<TC> (per-page) | HTML | prose + PMIDs | CC-BY-SA 3.0 | **no bulk file** |

Draft download.yaml block (metadata, grounding only — no prose):
```yaml
-
  url: https://www.tcdb.org/cgi-bin/projectv/public/go.py
  local_name: tcdb/tcdb2go.tsv
  name: TCDB → GO mapping
  source: tcdb
  license: CC-BY-SA 3.0
  status: candidate
  note: grounds FUNC_TRANSPORT families with GO; TCDB has NO bulk prose/citation file.
```

**Recommended next enrichment:** definitions stay boilerplate unless we scrape
per-family pages (allowed under CC-BY-SA with attribution but out of the bulk-
file model). Best cheap win: add `go.py`/`pfam.py` xref grounding. Flag: prose
enrichment for TCDB requires HTML scraping, not a download.

---

## CARD / ARO (Antibiotic Resistance Ontology)

Seeder `seed_obo.py aro` ingests `aro.obo`. Definitions are **real and good**,
and — importantly — **the `def` dbxref bracket already carries PMIDs** (e.g.
`def: "Macrolides are…" [PMID:27480866, PMID:15544496, PMID:11324679]`; 2,132
`xref:` lines in the file). So per-entry literature is **already on disk**.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| aro.obo | https://raw.githubusercontent.com/arpcard/aro/master/src/ontology/aro.obo | OBO | ARO term def(+PMID)/synonyms/xref/is_a | CC-BY 4.0 | **fetched** |
| aro.json | https://card.mcmaster.ca/latest/ontology | json (tar) | ARO + CARD model | CC-BY 4.0 | listed |

**No new download needed.** Action is in the seeder: confirm `seed_obo.py` lifts
the def-bracket PMIDs (and `xref:` PMIDs) into `evidence`/`EvidenceItem`. If it
currently drops them, that is the single cheapest evidence win in the set — the
PMIDs are already fetched.

**Recommended next enrichment:** parse `[PMID:…]` from each ARO `def:` and emit
`EvidenceItem`(reference=PMID, snippet=def text) on the FUNC_RESISTANCE records.

---

## COG (NCBI Clusters of Orthologous Genes 2020)

Seeder `seed_cog.py` reads `cog-20.def.tab` **columns 0–4 only** (COG, cats,
name, gene, pathway). The file has **7 columns** — and **column 6 is a PubMed ID**
(**653 COGs carry one**) and **column 7 is a PDB id**. Both are **already fetched
and silently dropped**:

```
COG=COG0011 | cats=H | name=Thiamin-binding stress-response protein YqgV… | gene=YqgV | pathway= | PMID=20471400 | PDB=1LXJ
COG=COG0012 | cats=J | name=Ribosome-binding ATPase YchF, GTP1/OBG family | gene=GTP1 | pathway= | PMID=21527254 | PDB=2DWQ
```

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| cog-20.def.tab | https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/cog-20.def.tab | tsv | COG/cats/name/gene/pathway/**PMID**/**PDB** | US Gov PD | **fetched**; cols 6–7 unused |
| fun-20.tab | https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/fun-20.tab | tsv | 26 category letters + desc | US Gov PD | fetched + used |
| cog-20.cog.csv | https://ftp.ncbi.nlm.nih.gov/pub/COG/COG2020/data/cog-20.cog.csv | csv | per-protein COG membership | US Gov PD | no (instances, skip) |

**No new download needed** — enrichment is a seeder change: read col 6 → `evidence`
(PMID) and col 7 → a PDB `xref`/structure representation. COG has no per-COG prose
beyond the name+pathway already used.

**Recommended next enrichment:** in `seed_cog.py` emit `EvidenceItem`(PMID) for
the 653 COGs with col-6 PMIDs, and a PDB xref for col-7. Zero new downloads.

---

## Reactome

Seeder `seed_reactome.py` uses `ReactomePathways.txt` (id/name/species) +
`ReactomePathwaysRelation.txt`. Definitions are **boilerplate** ("<name> — a
Reactome pathway…"). Reactome **does** have rich per-pathway **summation** prose
and **literatureReference** arrays with `pubMedIdentifier` — but these are **not
in the bulk download set** (which has no descriptions/PMIDs); they are available
**only via the ContentService REST API** (or the Neo4j graph-DB dump / BioPAX).

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| ReactomePathways.txt | https://reactome.org/download/current/ReactomePathways.txt | tsv | id/name/species (no prose) | CC0 | **fetched** |
| ReactomePathwaysRelation.txt | https://reactome.org/download/current/ReactomePathwaysRelation.txt | tsv | parent/child | CC0 | fetched |
| ContentService `query` | https://reactome.org/ContentService/data/query/{id} | json | `summation[].text`, `literatureReference[].pubMedIdentifier` | CC0 | **no — per-pathway API** |
| ContentService `pathway` | https://reactome.org/ContentService/data/pathway/{id}/containedEvents | json | contained events | CC0 | no |
| graphdb dump | https://reactome.org/download/current/reactome.graphdb.tgz | Neo4j | full model incl. summation+refs | CC0 | no (heavy) |
| BioPAX (Homo sapiens) | https://reactome.org/download/current/biopax.zip | BioPAX | pathways + xrefs | CC0 | no |

Draft download.yaml block:
```yaml
-
  url: https://reactome.org/ContentService/data/query/R-HSA-{id}
  name: Reactome ContentService (pathway summation + literature)
  source: reactome
  license: CC0
  status: candidate
  tag: api
  note: >-
    Per-pathway summation prose (summation[].text) → real definitions, and
    literatureReference[].pubMedIdentifier → EvidenceItem PMIDs. Not in the bulk
    download (ReactomePathways.txt has neither). Fetch per R-HSA id for the ~2.9k
    seeded pathways, or parse reactome.graphdb.tgz once. API deprecation note:
    use ContentService (/ContentService/), NOT the old RESTful API.
```

**Recommended next enrichment:** batch the ContentService `query` endpoint over
the seeded R-HSA ids to replace boilerplate definitions with `summation` text and
add `EvidenceItem` PMIDs. Second-highest literature win after Rhea. (Note:
reactome.org blocks generic bot fetches — use a real client / the reactome2py
library.)

---

## MEROPS

Seeder `seed_merops.py` parses `pepunit.lib` FASTA headers → family + type-
peptidase name. Definitions are **boilerplate** ("MEROPS peptidase family S01…").
MEROPS has per-family **summary** and **holotype** descriptions and **>20,000
literature references** — but these are **not** in `pepunit.lib`; they live inside
the **MySQL dump** (`meropsweb124.tar.gz`) and the reference dump
(`meropsrefs.txt`). No standalone prose/citation flat file exists.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| pepunit.lib | https://ftp.ebi.ac.uk/pub/databases/merops/current_release/pepunit.lib | FASTA | headers: family/type-peptidase/organism | EBI free (academic) | **fetched** |
| meropsweb124.tar.gz | https://ftp.ebi.ac.uk/pub/databases/merops/current_release/meropsweb124.tar.gz | MySQL dump (gz tar) | `domain`(family summary text), `holotype`, `substrate`, `refs`/`literature` tables | EBI free (academic) | **no — holds prose + PMIDs** |
| meropsrefs.txt | https://ftp.ebi.ac.uk/pub/databases/merops/current_release/meropsrefs.txt | SQL text | reference DB (>20k citations, PMIDs) | EBI free (academic) | no |
| dnld_list.txt | https://ftp.ebi.ac.uk/pub/databases/merops/current_release/dnld_list.txt | tsv | accession/family/species | EBI free (academic) | no |

Draft download.yaml block:
```yaml
-
  url: https://ftp.ebi.ac.uk/pub/databases/merops/current_release/meropsweb124.tar.gz
  local_name: merops/meropsweb124.tar.gz
  name: MEROPS MySQL dump (family summaries + literature)
  source: merops
  license: MEROPS (EBI; free for academic use) — FLAGGED (not CC0)
  status: candidate
  note: >-
    Bundles the `domain` (per-family summary prose), `holotype`, and reference
    tables — the only source of MEROPS family definitions + PMIDs. Parse the SQL
    (no need for a live MySQL) to enrich the ~370 SEQ_FAMILY records' definitions
    and attach EvidenceItem PMIDs. NB licence is NOT CC0 — stamp per-record.
```

**Recommended next enrichment:** parse `meropsweb*.tar.gz` for the family `domain`
summary text (→ real definitions) and its references (→ evidence PMIDs). Note the
version number in the filename (`124`) changes per release — resolve from the
`current_release/` directory listing.

---

## SEED / BV-BRC subsystems

Seeder `seed_seed_subsystems.py` already uses `subsystem_ref.json`, which
**includes a curated `description`** field → definitions are **real** where
present, boilerplate only where description is empty. Each record carries
superclass/class/subclass spine + EC xrefs parsed from role names. **No per-
subsystem PMID/DOI** is exposed by the `subsystem_ref` endpoint — only the
source-paper citations (Overbeek 2005, Aziz 2008, Olson 2023) apply corpus-wide.

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| subsystem_ref | https://www.bv-brc.org/api/subsystem_ref/?limit(25000)&http_accept=application/json | json | superclass/class/subclass/name/**description**/role_name[] | US Gov PD | **fetched + description used** |
| subsystem (roles) | https://www.bv-brc.org/api/subsystem/?… | json | per-genome role instances | US Gov PD | no (instances, excluded by design) |

**No new download needed.** BV-BRC exposes no per-subsystem literature. Optional:
attach the three source-paper PMIDs as corpus-level provenance (already noted in
the seeder header/comment). Definitions are as good as this source gets.

**Recommended next enrichment:** none required; source is already well-defined.
If desired, add the SEED/RAST + BV-BRC paper PMIDs as a shared `EvidenceItem`.

---

## Cross-source priority (recommended order of work)

1. **Rhea `rhea.rdf.gz` / SPARQL → PMIDs** — 18k enzymatic-reaction records,
   curated per-reaction citations. Biggest literature yield; new download.
2. **COG col-6 PMIDs + col-7 PDB** — 653 PMIDs, already on disk; seeder-only fix.
3. **ARO def-bracket PMIDs** — already on disk; seeder-only fix (confirm/lift).
4. **Reactome ContentService summation + literatureReference** — replaces
   boilerplate defs AND adds PMIDs for ~2.9k pathways; API batch.
5. **MEROPS `meropsweb*.tar.gz`** — real family defs + PMIDs; SQL-dump parse.
6. **EC `CC` comments** — richer defs for ~8k leaves; seeder-only, no PMIDs.
7. GO / ChEBI defs already on disk (grounding-side enrichment, low priority).
8. TCDB / SEED — no bulk prose/citation surface; leave as-is (TCDB prose would
   require per-page scraping under CC-BY-SA).
