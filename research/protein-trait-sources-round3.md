---
topic: protein-trait-sources
round: 3
date: 2026-07-07
question: >-
  Sources to populate empty first-order molecular-interaction categories
  (cofactor requirement, binding capacity, interaction partner) + confirm the
  metal/binding-site sources vetted in round 2.
prior_round: protein-trait-sources-round2.md
method: WebSearch/WebFetch verification, July 2026
---

# Protein Trait Sources — Round 3

Builds on [Round 2](protein-trait-sources-round2.md). Focus: the empty
first-order **molecular-interaction** categories the user prioritised —
`FUNC_COFACTOR_REQUIREMENT`, `FUNC_BINDING_CAPACITY`,
`FUNC_INTERACTION_PARTNER` — plus re-confirming the metal/binding-site sources
vetted-but-not-yet-seeded in Round 2.

Already ADOPTED/VETTED and NOT re-litigated here: PROSITE, TED/CATH, UniProtKB,
InterPro, SCOP/SCOPe, ECOD, RepeatsDB, MEROPS, MobiDB, dbPTM, SFLD, CAZy
(dbCAN-seq), NCBIfam, CDD, PSI-MOD, M-CSA, DisProt, PSI-MI, PATO, METPO, GO,
TCDB, ARO. **ELM stays ⛔ (non-commercial).**

## Ranked findings

Legend — Fit: target `trait_category`. Hier: parent/child classification.
✅ recommend · ⚠️ adopt with caveat · ⛔ skip.

| # | Source | Fit (category) | Hier | Download / format | Licence | Rec |
|---|--------|----------------|------|-------------------|---------|-----|
| 1 | **ChEBI `cofactor` subtree (CHEBI:23357)** + **UniProtKB `CC COFACTOR`** evidence | **FUNC_COFACTOR_REQUIREMENT** | ✅ role tree: cofactor → coenzyme / prosthetic group / siderophore + ~200 specific cofactors | ChEBI OBO/OWL (`chebi.obo`); UniProt cofactor via REST/SPARQL/flat file | CC-BY 4.0 (ChEBI) / CC-BY 4.0 (UniProt) | ✅ ChEBI supplies the reusable cofactor CLASSES; UniProt supplies evidence |
| 2 | **Rhea cofactor participants** | FUNC_COFACTOR_REQUIREMENT (enzyme-anchored) | via ChEBI | rhea-db.org/download (rhea2chebi, reaction TSV/RDF) | CC-BY 4.0 | ⚠️ same ChEBI classes as #1; use only to tie a cofactor to a Rhea reaction |
| 3 | **GO molecular-function `binding` (GO:0005488) subtree** | **FUNC_BINDING_CAPACITY** | ✅ deep is_a DAG (DNA/heme/calcium/ATP/metal ion binding…) | go.obo / go-basic (already fetched) | CC-BY 4.0 | ✅ ALREADY our source under FUNC_MOLECULAR_FUNCTION — do NOT create a parallel source |
| 4 | **Complex Portal 2025** (EBI) | **FUNC_INTERACTION_PARTNER** (complex membership) | flat participant list + stoichiometry; GO CC "protein-containing complex" parents | FTP + REST; ComplexTAB / PSI-MI XML 3.0 / MI-JSON, grouped by species | **CC0** | ✅ best fit — curated complex = reusable CLASS |
| 5 | **CORUM 5.x** (Helmholtz) | FUNC_INTERACTION_PARTNER (mammalian complexes) | complex → subunits | downloads page, TSV/JSON | **CC-BY 4.0** | ⚠️ mammalian-only, overlaps Complex Portal; secondary |
| 6 | **3did** (IRB Barcelona) | FUNC_INTERACTION_PARTNER (domain–domain interaction TYPES) | Pfam-pair interaction classes | full DB flat-file download, 6-month releases | ⚠️ mixed CC-BY / CC-BY-NC across versions | ⚠️ class-level but licence ambiguous — confirm current release licence before ingest |
| 7 | **BioLiP2** (Zhang group) | STRUCT_BINDING_SITE | — (ligand-typed) | weekly `BioLiP_*.txt` + `_nr.txt`, `receptor_*_nr.tar.bz2`, `ligand_*_nr.tar.bz2` | free (academic, no explicit CC) | ✅ **vetted, ready to seed** (Round 2) |
| 8 | **MetalPDB** (CERM/UniFI) | STRUCT_METAL_SITE | grouped by metal (Minimal Functional Site templates) | `flat_db_file.xml.gz`, `coordination_sphere.tar.gz`, `/downloadMetalSites` | ⚠️ no explicit licence published | ⚠️ **vetted, ready to seed** but confirm reuse terms with CERM |
| — | IntAct / MINT / BioGRID / STRING | FUNC_INTERACTION_PARTNER (raw PPIs) | — | various | mixed (BioGRID ⚠️, STRING CC-BY) | ⛔ **per-pair INSTANCES, not reusable classes** — reject as trait source |

## Detail & rationale

### FUNC_COFACTOR_REQUIREMENT — ChEBI cofactor subtree is the class source (UniProt = evidence)

The reusable CLASS is "requires cofactor *X*", where *X* must be a grounded,
enumerable cofactor class — not a per-protein annotation. ChEBI's **`cofactor`
role (CHEBI:23357)** is exactly that: defined as "an organic molecule or ion
(usually a metal ion) required by an enzyme for its activity," with a small
top hierarchy (coenzyme / prosthetic group / siderophore) and ~200 specific
cofactor terms underneath (FAD, heme, PLP, biotin, NAD, metal ions, etc.). That
subtree gives us a clean set of reusable `FUNC_COFACTOR_REQUIREMENT` classes,
each groundable to a `CHEBI:` id and parent-linkable.

**UniProtKB `CC COFACTOR`** is the *evidence/population* layer, not the class
layer: its Cofactor subsection describes cofactors with ChEBI ids (the same
"biologically relevant ligands in UniProtKB using ChEBI" scheme we already lean
on), so it supplies per-protein instances that we aggregate as canonical
examples/evidence behind each ChEBI-anchored class. **Rhea** adds nothing new at
the class level — its participants are also ChEBI — but `rhea2chebi` can tie a
required cofactor to a specific reaction when we want mechanistic grounding.

Verdict: seed `FUNC_COFACTOR_REQUIREMENT` from the **ChEBI cofactor subtree**
(reusable classes), evidence with UniProt `CC COFACTOR`. No new external source
needed beyond ChEBI (already CC-BY, already a dependency).

### FUNC_BINDING_CAPACITY — already subsumed by GO binding; do NOT duplicate

"Capacity to bind a class of ligand" (DNA-binding, heme-binding,
calcium-binding, metal-binding, ATP-binding…) is precisely the GO
molecular-function **`binding` (GO:0005488)** subtree — a deep is_a DAG with
`ATP binding` (GO:0005524), `calcium ion binding` (GO:0005509), `heme binding`,
`DNA binding`, `metal ion binding`, etc. We already seed GO MF terms under
`FUNC_MOLECULAR_FUNCTION`. Creating a parallel `FUNC_BINDING_CAPACITY` source
would duplicate that hierarchy.

Recommendation: **do not add a source.** Either (a) treat the `binding` subtree
of GO as the population for `FUNC_BINDING_CAPACITY` by routing GO binding terms
into that category instead of the generic MF one, or (b) fold binding-capacity
into `FUNC_MOLECULAR_FUNCTION` and leave `FUNC_BINDING_CAPACITY` as an
organisational alias. No distinct authoritative "ligand-binding-family"
resource exists that beats GO's curated binding DAG. This is a schema/routing
decision, not a sourcing gap.

### FUNC_INTERACTION_PARTNER — class-vs-instance verdict

This is the hard one, and the answer is a modelling verdict, not just a source
pick:

- **Raw pairwise PPIs (IntAct, MINT, BioGRID, STRING) = INSTANCES, reject.**
  "Protein A interacts with protein B" is a per-pair fact about two specific
  UniProt accessions — not a reusable trait CLASS. Ingesting them would flood
  the KB with millions of instance edges and violate the class-level bar.
  STRING is CC-BY (fine licence) and BioGRID is ⚠️, but licence is moot: the
  granularity is wrong. ⛔.

- **Complex Portal (CC0) = the reusable CLASS source. ✅** A curated stable
  macromolecular complex (e.g. `CPX-…`) is a *named, reusable entity* with a
  defined member list and stoichiometry. The trait "is a subunit of complex
  *X*" is class-level and reusable across every protein that participates, and
  each complex carries a stable identifier and GO "protein-containing complex"
  parentage. 2025 build: ~2,150 manually curated human complexes (plus ML-
  predicted hu.MAP3.0 complexes, which we'd exclude or tier lower), 28 species,
  CC0, FTP + REST in ComplexTAB / PSI-MI XML 3.0 / MI-JSON. This is the right
  way to populate `FUNC_INTERACTION_PARTNER`: model the **complex as the class**,
  membership as the trait.

- **CORUM 5.x = secondary, CC-BY. ⚠️/✅** Same complex-as-class model, 7,900+
  mammalian complexes, but mammalian-only and heavily overlapping Complex Portal;
  CC-BY 4.0 is compatible. Use to top up mammalian coverage after Complex Portal.

- **3did = domain–domain interaction TYPES, class-level but ⚠️ licence.** A
  Pfam-domain-pair that interacts (with 3D template) IS a reusable interaction
  class ("proteins bearing domain P1 can interact with proteins bearing domain
  P2"). Full DB is downloadable, 6-monthly. Caveat: different releases have
  shipped under CC-BY *and* CC-BY-NC — confirm the current release's licence
  before ingest. If CC-BY, it's a genuine class-level complement to Complex
  Portal for interaction *mechanism*. (DOMINE is defunct; InterPreTS is a
  prediction tool, not a source — both skipped.)

**Bottom line:** reusable interaction-partner traits come from *complexes*
(Complex Portal, CC0) and *domain-interaction types* (3did, licence-gated), NOT
from pairwise PPI databases. Seed Complex Portal; treat 3did as a
licence-conditional secondary; do not ingest IntAct/BioGRID/STRING/MINT as
trait classes.

### Sites (secondary) — confirm Round-2 vettings

- **STRUCT_BINDING_SITE ← BioLiP2:** confirmed. Weekly flat files
  (`BioLiP_<date>.txt`, `..._nr.txt`) plus non-redundant receptor/ligand
  tarballs at zhanggroup.org/BioLiP DOWNLOAD; current build 2025-07. Free for
  academic use (no explicit CC statement — attribution to the NAR 2024 paper).
  **Vetted, ready to seed.**
- **STRUCT_METAL_SITE ← MetalPDB:** bulk download confirmed —
  `flat_db_file.xml.gz` (whole DB as XML), `coordination_sphere.tar.gz`, and a
  per-site `/downloadMetalSites` endpoint; sites grouped by metal as Minimal
  Functional Site templates. Caveat: MetalPDB publishes **no explicit data
  licence** on its About/Help pages — treat as ⚠️ and confirm reuse/redistribution
  terms with CERM before committing to a CC0 KB. **Vetted, ready to seed pending
  licence confirmation.**
- **SEQ_ACTIVE_SITE / SEQ_BINDING_SITE:** the dedicated upgrade over the thin
  InterPro-derived records is **M-CSA** (Mechanism and Catalytic Site Atlas),
  which we already partly use for STRUCT_ACTIVE_SITE — it defines catalytic
  residues/roles per enzyme family (CC-BY). No better dedicated source surfaced
  for sequence-anchored active sites; broaden M-CSA usage rather than add a new
  source. UniProt `ACT_SITE`/`BINDING` feature types (already in `seed_uniprot`)
  remain the volume source for the per-protein instances.

## Recommended next seeds (priority order)

1. **Complex Portal 2025** (CC0) → `FUNC_INTERACTION_PARTNER` as complex-
   membership classes. Highest-value fill for the priority gap; clean CC0.
2. **ChEBI cofactor subtree (CHEBI:23357)** (CC-BY) → `FUNC_COFACTOR_REQUIREMENT`
   classes, evidenced by UniProtKB `CC COFACTOR`. Reuses an existing dependency.
3. **BioLiP2** (free/academic) → `STRUCT_BINDING_SITE`; **MetalPDB** (⚠️ licence)
   → `STRUCT_METAL_SITE` — the two Round-2 vettings, now with confirmed download
   URLs.
4. **FUNC_BINDING_CAPACITY**: no new seed — route GO `binding` (GO:0005488)
   subtree here or alias to `FUNC_MOLECULAR_FUNCTION` (schema decision).
5. **CORUM 5.x** (CC-BY) and, licence permitting, **3did** (⚠️) → secondary
   interaction-partner top-ups after Complex Portal.

## Sources

- UniProtKB cofactor/ligand annotation (ChEBI) — <https://academic.oup.com/bioinformatics/article/39/1/btac793/6885442> · <https://pmc.ncbi.nlm.nih.gov/articles/PMC9825770/>
- ChEBI cofactor role (CHEBI:23357) — <https://www.ebi.ac.uk/chebi/searchId.do?chebiId=23357>
- Rhea enzyme/cofactor annotation + downloads — <https://academic.oup.com/bioinformatics/article/36/6/1896/5613180> · <https://www.rhea-db.org/download>
- GO molecular-function binding — <https://amigo.geneontology.org/amigo/term/GO:0005524> · <https://wiki.geneontology.org/Binding_Guidelines>
- Complex Portal 2025 — <https://academic.oup.com/nar/article/53/D1/D644/7903366> · <https://www.ebi.ac.uk/complexportal>
- CORUM 2024/5.x — <https://academic.oup.com/nar/article/53/D1/D651/7889246> · <https://mips.helmholtz-muenchen.de/corum/download>
- 3did — <https://academic.oup.com/nar/article/42/D1/D374/1066653> · <https://3did.irbbarcelona.org/>
- BioLiP2 — <https://academic.oup.com/nar/article/52/D1/D404/7233921> · <https://zhanggroup.org/BioLiP/>
- MetalPDB — <https://academic.oup.com/nar/article/41/D1/D312/1055329> · <https://metalpdb.cerm.unifi.it/>
- M-CSA — <https://www.ebi.ac.uk/thornton-srv/m-csa/>
