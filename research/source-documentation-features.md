# Source documentation & entry-metadata enrichment audit

Per-source review of the SEEDED feature / PTM / motif / ontology sources: what
**documentation (per-entry prose)** and **entry metadata (incl. per-entry
PMIDs/DOIs)** each source exposes that could enrich our definitions / labels /
citations — and whether that requires a **new download** or just **better
parsing / sanitization of a file we already fetch**.

Scope follows the request: PSI-MOD, PSI-MI, DisProt, IDEAL, ELM, RepeatsDB,
M-CSA, METPO, PATO, RiPP/BAGEL, and the curated stability / evolution
taxonomies. Method: read `download.yaml`, `justfile` fetch recipes, and each
`scripts/seed_*.py`; inspected the actual bytes already in `data/raw/` where
present; verified external facts (IDPO ontology, ELM host) on the web.

Reference precedent for this work: `scripts/enrich_prosite_definitions.py`
(backfilled real prose from `prosite.doc`) and
`scripts/backfill_source_definitions.py` (CDD/NCBIfam labels+defs from cddid /
hmm_PGAP) — both **in-place enrichers**, not re-seeds, so existing record
enrichment is preserved. The same pattern applies to most fixes below.

---

## TL;DR classification

| Source | Doc/prose status | Per-entry PMIDs/DOIs? | Verdict |
|---|---|---|---|
| **PSI-MOD** | def in obo; ~good for most, placeholder stubs for Unimod/DeltaMass imports | YES — `PubMed:`/`DOI:` in def bracket (extracted) | **SANITIZE** (drop `DeltaMass:0`, clean stub defs); optional Unimod/RESID new download for the stub minority |
| **PSI-MI** | def in obo, rich | YES — `PMID:` in def bracket (extracted) | **already-good** |
| **DisProt** | IDPO class defs are **synthesized**, not authoritative | YES — per-region `reference_id`+`reference_source` in JSON we fetch (**not extracted**) | **NEW download** (IDPO obo) + **PARSE** existing JSON for PMIDs |
| **IDEAL** | ProS def curator-authored (ok); parent class def should be IDPO's | YES — `pubmed_id`/`publication` in XML we fetch (**not extracted**) | **PARSE** existing XML for PMIDs; shares IDPO download |
| **ELM** | `Description` column = class abstract, already used | NO clean bulk PMID-per-class file | **already-good** for defs; per-class PMIDs need per-class fetch (low priority, NC licence) |
| **RepeatsDB** | `description` in JSON, but only 28/123 nodes have one; rest synthesized | NO (literature is per-PDB, not per class node) | **SANITIZE** (fix `representative` whitespace; optional `wikipedia` xref); no new download |
| **M-CSA** | `description` = mechanism summary, already used, **but HTML tags** | YES — mechanism `pubmed_id` (extracted to evidence) | **SANITIZE** (strip HTML `<i>/<p>/<sub>`); no new download |
| **METPO** | def in obo, used | YES — def-source PMID (extracted) | **already-good** |
| **PATO** | def in obo, used | YES — def-source PMID (extracted) | **already-good** |
| **RiPP/BAGEL** | curator one-liners (ok) | NO (not cited) | **already-good**; optional add nomenclature-review DOIs |
| **Curated stability/evolution** | curator-authored, grounded to PATO / NCBITaxon | NO (not cited) | **already-good**; optional methodology DOIs |

**NEW download genuinely needed:** only **IDPO** (idpo.obo) — for authoritative
DisProt + IDEAL disorder-class definitions and hierarchy. Optional/second-tier:
**Unimod** (unimod.xml/obo) to rescue the PSI-MOD import-stub definition minority.
Everything else is parse-or-sanitize of a file we already have, or already good.

**Sources that expose per-entry PMIDs/DOIs:** PSI-MOD, PSI-MI, DisProt, IDEAL,
M-CSA, METPO, PATO (7 of 11). Of those, **DisProt and IDEAL PMIDs are present in
the file we already fetch but the seeder discards them** — pure parsing win.

---

## PSI-MOD

Fetched now (`seed_psi_mod.py`, `just fetch-psimod`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| PSI-MOD.obo | `https://raw.githubusercontent.com/HUPO-PSI/psi-mod-CV/master/PSI-MOD.obo` | OBO 1.2 | `name`, `def` (+source bracket), `synonym`, `is_a`, `xref` (Unimod/RESID/mass), `def`-source PubMed/DOI/ChEBI | CC-BY-4.0 | ✅ yes |

1. **Documentation/prose** — the per-term `def:` **is in the obo we already
   fetch**, and for the large majority it is a proper definition (e.g.
   MOD:00010 *"A protein modification that effectively converts a source amino
   acid residue to an L-alanine."*). The defect is a **minority of
   Unimod/DeltaMass-imported stubs** whose def is literally a placeholder in the
   source file — e.g. `MOD:00760` def = `"modification from Unimod N-linked
   glycosylation - missing ref"`. No richer prose for these exists *inside*
   PSI-MOD. **Fix is sanitization of the def text on import**, not a new file:
   strip the `- missing ref` tail and detect the `modification from
   (Unimod|DeltaMass|RESID)…` stub pattern → fall back to the term name (as the
   seeder already does when def is empty) rather than emitting the stub verbatim.
2. **Entry metadata** — `name`, `synonym` (scoped), `is_a` (MOD hierarchy),
   `xref` (Unimod/RESID) all present and extracted by `seed_psi_mod.py`.
3. **Literature citations** — PubMed/DOI live in the **def-source bracket**
   (`def: "…" [ChEBI:29948, DeltaMass:0, PubMed:6692818, RESID:AA0001]`);
   `normalise_source()` already canonicalises `PubMed:`→`PMID:` and `doi`→`DOI:`
   into `xrefs`. **Already exposed.**
4. **Junk-xref bug (`DeltaMass:0`)** — the same def-source bracket contains
   `DeltaMass:0`. `normalise_source()` filters only `psi-mod`/`pubmed`/`doi`;
   `DeltaMass` is passed through unchanged and passes the CURIE regex, so every
   term seeded from a DeltaMass-cited def carries a junk `DeltaMass:0` xref
   (flagged in record-sample-review-1, sequence appendix). **Fix:** add
   `DeltaMass` (and any `:0` local) to the drop-list in `normalise_source()`.
   (Note: `grep 'xref: DeltaMass:'` = 0 — the junk comes from the def bracket,
   not the `xref:` lines, so the existing `parse_xref` filter list never sees it.)
5. **Licence** — CC-BY-4.0.

**Recommended next action:** **SANITIZE existing** — (a) drop `DeltaMass:*` in
`normalise_source`; (b) replace import-stub defs (`… - missing ref`,
`modification from Unimod/DeltaMass …`) with the term name. *Optional second
tier:* a **new download of Unimod** (`unimod.obo` / `unimod.xml`) keyed by the
`Unimod:` xref already on each stub record would supply real descriptions for
that minority — but it is not required to remove the artifacts.

*(Optional Unimod block — only if you decide to enrich the stub minority; do NOT
add unless pursued:)*
```yaml
-
  url: https://raw.githubusercontent.com/HUPO-PSI/psi-mod-CV/master/unimod.obo  # verify path; Unimod also at www.unimod.org/xml/unimod.xml
  local_name: unimod.obo
  name: Unimod (PTM masses + descriptions) — PSI-MOD stub enrichment
  source: unimod
  license: see unimod.org terms
  status: candidate
  note: only to backfill descriptions for the PSI-MOD terms whose def is a "modification from Unimod …" stub, keyed by the Unimod: xref already on those records.
```

---

## PSI-MI

Fetched now (`seed_obo.py psimi`, `just fetch-obo`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| PSI-MI.obo | `https://raw.githubusercontent.com/HUPO-PSI/psi-mi-CV/master/psi-mi.obo` | OBO | `name`, rich `def`, `synonym`, `is_a`, def-source PMID/GO/RESID | CC-BY-4.0 | ✅ yes |

1. **Prose** — `def:` in the obo is a full authored sentence (e.g. MI:0220
   ubiquitination = *"Reversible reaction that create a covalent bond between a
   C-terminus G of ubiquitin and a K residue of the target."*). Already used.
2. **Metadata** — name, synonyms, is_a hierarchy: extracted.
3. **Literature** — PMID in def-source bracket (`[GO:0016567, PMID:11583613,
   RESID:AA0125]`) → extracted to xrefs by `normalise_source`. **Exposed.**
4. **Licence** — CC-BY-4.0.

**Recommended next action:** **already-good.** No new download; no sanitization
needed. (Only modelling caveat, out of scope here: MI:0220-type reaction terms
are being routed under FUNC_INTERACTION_PARTNER — a category question, not a
documentation gap.)

---

## DisProt

Fetched now (`seed_disprot.py`, cached `data/raw/disprot.entries.json`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| disprot.entries.json | `https://disprot.org/api/search?release=current&format=json&namespace=all&get_consensus=false` | JSON | 3,199 proteins; per-**region** `term_id/term_name/term_namespace` (IDPO), `reference_id`, `reference_source`, `cross_refs`, `ec_*` | CC-BY-4.0 | ✅ yes |
| **IDPO ontology** | `http://purl.obolibrary.org/obo/idpo.obo` (also `disprot.org/download`, GitHub `BioComputingUP/idpo`) | OBO/OWL | authoritative IDPO **term definitions** + is_a hierarchy for the 32 classes we seed | CC-BY-4.0 | ❌ **NO** |

1. **Documentation/prose** — **gap.** `seed_disprot.py` **synthesizes** each
   IDPO class definition from the term name (`f"{name} — an IDPO disorder class
   ({namespace}, {tid}); a protein region with this intrinsic-disorder property.
   {n} DisProt protein(s) annotated…"`). The JSON carries `term_name` but **not**
   the IDPO definition. The authoritative per-term definition lives in the **IDPO
   ontology**, which DisProt itself is built on and publishes as obo/owl
   (verified: `purl.obolibrary.org/obo/idpo.owl`, and each term has a definition
   page at `disprot.org/ontology`). → **NEW download** of `idpo.obo` gives real
   defs + a real is_a hierarchy (currently the seeder fabricates 3 namespace
   group-nodes to avoid dangling parents; IDPO supplies the true parents).
2. **Entry metadata** — regions carry `term_id/term_name/term_namespace`,
   `cross_refs` (PDB), `ec_*`; used partially.
3. **Literature citations** — **present but discarded.** Every region has
   `reference_id` + `reference_source` (e.g. `reference_id='8632448',
   reference_source='pmid'`) and a `cross_refs` PDB list. `seed_disprot.py`
   reads `start/end` only and never touches `reference_id`. → **PARSE** to attach
   `PMID:<reference_id>` as evidence on the annotating example / region, and
   `cross_refs` PDB as xrefs.
4. **Licence** — CC-BY-4.0 (both the JSON and IDPO).

**Recommended next action:** **NEW download** — add IDPO obo to the manifest and
use it for class definitions + hierarchy (this also fixes IDEAL's ProS parent
`IDPO:0000011` def). **PLUS parse-existing** — expose per-region
`reference_id`(pmid) + `cross_refs`(PDB) that the JSON already contains. IDPO is
shared with IDEAL, so one download serves both.

Draft `download.yaml` addition:
```yaml
# IDPO — Intrinsically Disordered Proteins Ontology (authoritative defs +
# hierarchy for the IDPO classes DisProt & IDEAL annotate against).
-
  url: http://purl.obolibrary.org/obo/idpo.obo
  local_name: idpo.obo
  name: IDPO (Intrinsically Disordered Proteins Ontology)
  source: idpo
  license: CC-BY 4.0
  status: candidate
  hierarchy: true
  trait_categories: [SEQ_DISORDER]
  seeder: seed_disprot.py / seed_ideal.py (definition + parent backfill)
  note: >-
    Supplies real term definitions and is_a parents for the ~32 IDPO disorder
    classes currently seeded with synthesized defs + 3 fabricated namespace
    group-nodes. Also anchors IDEAL ProS parent IDPO:0000011. Alt sources:
    disprot.org/download, github.com/BioComputingUP/idpo.
```

---

## IDEAL

Fetched now (`seed_ideal.py`, `just fetch-ideal`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| IDEAL.xml.gz | `https://www.ideal-db.org/IDEAL.xml.gz` | gzip XML | per-entry `name`, synonyms, `function` prose, `subcellular_location`, `sequence`, `motif`/`ProS` regions, **`pubmed_id`/`publication`/`reference`** | CC-BY 4.0 | ✅ yes |

1. **Documentation/prose** — the seeded ProS **class** definition is
   curator-authored and fine. Its **parent** (`IDPO:0000011` "disorder to order")
   has no local def → resolved by the **IDPO download** above (shared). The XML
   also carries rich per-entry `function` prose and subcellular location that are
   currently used only as example metadata, not surfaced.
2. **Entry metadata** — motifs (`motif_name`, `motif_region_start/end`),
   UniProt accessions, organism, sequence: extracted onto examples.
3. **Literature citations** — **present but discarded.** The XML contains
   `pubmed_id` / `publication` / `reference` tags (≈19k reference tags across the
   file; `has PubMed refs: True`). `seed_ideal.py` parses `<General>`,
   `<motif>` only and never reads references. → **PARSE** to attach the per-entry
   / per-ProS PMIDs as evidence on the ProS examples.
4. **Licence** — CC-BY 4.0.

**Recommended next action:** **PARSE existing XML** to expose the `pubmed_id`
references it already contains; **share the IDPO download** for the ProS parent
definition. No IDEAL-specific new download.

---

## ELM

Fetched now (`seed_elm.py`, `just fetch-elm`). *Note: `download.yaml` still marks
ELM `status: rejected` (NC licence) although a seeder exists and records are
seeded with the NC licence stamped per-record — the manifest is stale here.*

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| elm_classes.tsv | `http://elm.eu.org/elms/elms_index.tsv` | TSV | `Accession, ELMIdentifier, FunctionalSiteName, **Description**, Regex, Probability, #Instances, #Instances_in_PDB` (353 classes) | ELM Software License (**non-commercial**) | ✅ yes |
| elm_instances.tsv | `http://elm.eu.org/instances.tsv?q=*` | TSV | per-instance protein, coords, logic | NC | ✅ yes |

1. **Documentation/prose** — the **`Description` column IS the class abstract**
   and is already used verbatim in `definition` (`f"{site_name} — {desc}"`).
   **Already good**, no richer separate prose file needed for the class text.
2. **Entry metadata** — `FunctionalSiteName`, `Regex` (→ `sequence_pattern`),
   `Probability`, instance counts: present/used.
3. **Literature citations** — **not in the bulk class TSV** (no PMID column,
   confirmed from the local header). ELM shows per-class references on the web
   class pages (`elm.eu.org/elms/<ELMIdentifier>`) and there is an
   `elm_interaction_domains.tsv`, but there is **no clean bulk PMID-per-class
   download**. Per-class PMIDs would require a per-class page/JSON fetch. (Live
   verification blocked: `elm.eu.org` refused the connection — the host commonly
   blocks automated fetches, another reason to keep ELM low-touch.)
4. **Licence** — ELM Software License, **non-commercial** (FLAGGED; stamped
   per-record, incompatible with repo CC0 redistribution).

**Recommended next action:** **already-good** for definitions. **Do NOT** add a
new bulk download for citations — none exists; per-class PMID harvesting is a
per-request scrape that is low priority given the NC licence. Reconcile the
stale `status: rejected` vs the seeded reality in `download.yaml` separately.

---

## RepeatsDB

Fetched now (`seed_repeatsdb.py`, `just fetch-repeatsdb`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| classification.json | `https://repeatsdb.org/api/production/classification` | JSON | 123 class→topology→fold→clan nodes: `name`, `description`, `wikipedia`, `representative` (PDB+chain), `statistics` | CC-BY 4.0 | ✅ yes |

1. **Documentation/prose** — `description` **is in the JSON we fetch and is
   already used**, but **only 28 of 123 nodes have a non-empty description**
   (confirmed by count); the other 95 fall back to the seeder's synthesized
   template. There is **no richer separate class-prose file** — RepeatsDB's prose
   lives on the per-node web pages / Wikipedia, and the node JSON also carries an
   unused **`wikipedia`** URL field for some nodes (e.g. node 3 → solenoid, node
   4 → toroid). No new download would materially improve the 95 thin nodes.
2. **Entry metadata** — dotted-id hierarchy (parent chained by the seeder),
   `representative` PDB chain → xref. **Parsing bug:** `representative` values
   contain leading whitespace/newlines (e.g. `"        \n5eamA"` on node 4), and
   `seed_repeatsdb.py` takes `rep[:4]` → would emit spaces instead of the PDB id.
   **Fix:** `.strip()`/regex the representative before slicing.
3. **Literature citations** — **none at the classification-node level.**
   RepeatsDB literature is per-PDB-entry (structure annotations), not per class
   node. No per-class PMIDs to expose.
4. **Licence** — CC-BY 4.0.

**Recommended next action:** **SANITIZE existing** — fix the `representative`
whitespace before PDB extraction; optionally add the `wikipedia` field as a
see-also xref. **No new download** (class-node prose and per-class citations
don't exist in a fetchable form).

---

## M-CSA

Fetched now (`seed_mcsa.py`, cached `data/raw/mcsa.entries.jsonl`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| entries (JSON API) | `https://www.ebi.ac.uk/thornton-srv/m-csa/api/entries/` | JSON | per-entry `description` (mechanism summary, **contains HTML**), `all_ecs`, `reaction.compounds` (ChEBI), `residues` (PDB/CATH), `reference_uniprot_id`, `reaction.mechanisms[].references[].pubmed_id` | CC-BY-4.0 | ✅ yes |

1. **Documentation/prose** — the mechanism `description` **is in the API we
   fetch and is already used** as the definition, and its content is excellent
   (record-sample-review calls it "a model"). The defect is **HTML markup left
   in the text** — `<i>`, `<p>`, `<sub>` tags (flagged: MCSA:824 `<i>`,
   prostaglandin-E-synthase `<p>`). **Fix is sanitization on import** (strip
   HTML tags + unescape entities), not a new file — the API is the authoritative
   source and there is no cleaner prose elsewhere.
2. **Entry metadata** — EC, ChEBI compounds, PDB/CATH residues, UniProt ref:
   extracted to `xrefs` / `canonical_examples`.
3. **Literature citations** — **exposed.** `extract_pmids()` already pulls
   `reaction.mechanisms[].references[].pubmed_id` → `evidence: PMID:…`. Good.
4. **Licence** — CC-BY-4.0.

**Recommended next action:** **SANITIZE existing** — strip HTML tags/entities
from `description` before writing `definition` (and fix the "boltulinum"-type
typos only if trivial). No new download. *(Separate, larger, out-of-scope issue
from the review: M-CSA records are enzyme/mechanism-scoped and filed under
STRUCT_ACTIVE_SITE — a modelling/axis decision, not a documentation gap.)*

---

## METPO

Fetched now (`seed_obo.py metpo`, `just fetch-obo`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| METPO.obo | `https://raw.githubusercontent.com/berkeleybop/metpo/main/metpo.obo` | OBO | `name`, `def`, `synonym`, `is_a`, def-source refs | CC-BY-4.0 | ✅ yes |

1. **Prose** — `def:` in obo, used as definition. 2. **Metadata** — name/syn/is_a
extracted (branch-scoped routes). 3. **Literature** — PMID/DOI via def-source
`normalise_source` (when present). 4. **Licence** — CC-BY-4.0.

**Recommended next action:** **already-good.** No new download.

---

## PATO

Fetched now (`seed_obo.py pato`, `just fetch-obo`):

| file | url | format | contents | licence | already-have? |
|---|---|---|---|---|---|
| PATO.obo | `https://raw.githubusercontent.com/pato-ontology/pato/master/pato.obo` | OBO | `name`, rich `def`, `synonym`, `is_a`, def-source PMID | CC-BY-4.0 | ✅ yes |

1. **Prose** — full authored `def:` in obo, used (whitelisted quality roots).
2. **Metadata** — extracted. 3. **Literature** — def-source PMID → xrefs.
4. **Licence** — CC-BY-4.0.

**Recommended next action:** **already-good.** No new download. (One review
caveat, out of scope: some PATO records land in a category that looks like a
mismatch — modelling, not documentation.)

---

## RiPP / BAGEL

Curated in-code (`seed_ripp.py`) — no download; 20 hand-authored classes.

1. **Documentation/prose** — curator one-line descriptions per class
   (lanthipeptide, lasso, sactipeptide, …). Adequate and clean (no artifacts).
   No structured external file to enrich from: BAGEL4 / antiSMASH ship class
   *names* in code, not a citable CV with prose. The authoritative prose source
   is the RiPP consensus-nomenclature reviews.
2. **Entry metadata** — synonyms curated. No hierarchy.
3. **Literature citations** — **none currently.** Could add the nomenclature
   reviews as `definition_source`/evidence DOIs: Arnison et al. 2013
   (`DOI:10.1039/c2np20085f`) and Montalbán-López et al. 2021
   (`DOI:10.1039/d0np00027b`).
4. **Licence** — CC0-1.0 (curated).

**Recommended next action:** **already-good / curated.** No download. *Optional:*
attach the two consensus-nomenclature DOIs as citations.

---

## Curated stability / evolution taxonomies

Internal generators — `seed_stability.py`, `seed_evolution.py`; CC0-1.0; no
download.

1. **Documentation/prose** — definitions are curator-authored and clean (no
   import artifacts). **stability** records already parent to the verified PATO
   terms (`PATO:0015026` stability / `0015027` increased / `0015028` decreased);
   **evolution** records ground clade scope via `NCBITaxon:` xrefs. This is
   exactly the "model tier" the review praised.
2. **Entry metadata** — parents (PATO), synonyms, taxon xrefs present.
3. **Literature citations** — **none** (hand-authored taxonomy). Optional: cite
   the stability/pangenome methodology reviews if desired.
4. **Licence** — CC0-1.0.

**Recommended next action:** **already-good.** No download, no sanitization.
*Optional:* add methodology-review DOIs as `definition_source`.

---

## Consolidated action list

**New download (add to `download.yaml`):**
- **IDPO** (`idpo.obo`) — real definitions + hierarchy for DisProt & IDEAL
  disorder classes (block drafted above). *Optional:* **Unimod** for the PSI-MOD
  import-stub minority.

**Parse-existing (data already fetched, seeder discards it):**
- **DisProt** — per-region `reference_id`(pmid) + `cross_refs`(PDB).
- **IDEAL** — per-entry `pubmed_id`/`publication`.

**Sanitize-existing (clean text/xrefs on import; mirror in an in-place backfiller
à la `enrich_prosite_definitions.py`):**
- **PSI-MOD** — drop `DeltaMass:*` junk xref; replace "…- missing ref" /
  "modification from Unimod/DeltaMass" stub defs with the term name.
- **M-CSA** — strip HTML `<i>/<p>/<sub>` (+ entities) from `description`.
- **RepeatsDB** — `.strip()` the `representative` before `rep[:4]` PDB slice;
  optional `wikipedia` see-also xref.

**Already-good (no action):** PSI-MI, METPO, PATO, ELM (defs), RiPP, curated
stability/evolution.
