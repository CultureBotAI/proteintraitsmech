# Codex review prompt — representation, content & HTML-rendering consistency across trait axes and categories

## Your task

ProteinTraitsMech is a LinkML-governed knowledge base of ~279k class-level
`ProteinTraitRecord` YAMLs, organised on **five trait axes** (SEQUENCE,
STRUCTURE, SEQUENCE_STRUCTURE, FUNCTION, EVOLUTION) and ~48 fine-grained
`trait_category` buckets, projected into a client-side browser
(`docs/browse.html` + `browse.js` + `browse.css`, driven by
`scripts/build_docs_index.py`).

Assess **consistency across every (axis, category) cell** along three dimensions:

1. **Representation** — is the right comparable representation present, and
   populated the same way, wherever a category calls for it?
2. **Content** — are label / definition / groundings / citations / provenance
   structured and of comparable quality across cells, with direct-vs-mapping
   provenance applied consistently?
3. **HTML rendering** — does the browser render every field type the same way
   across cells, with no leaked markup, no per-axis gaps, and correct escaping?

This is a **consistency audit**, not a per-record bug hunt: the deliverable is
the set of *systematic* inconsistencies (a representation a category should carry
but doesn't; a field the detail view shows for one axis but drops for another;
markup that renders as raw text) and where each is fixed (seeder / schema /
`build_docs_index.py` / `browse.*`).

## Repository facts you must build on (verify them yourself in the tree)

- **Schema** `src/proteintraitsmech/schema/proteintraitsmech.yaml` — the axis↔category
  prefix rules and the representation slots: `sequence_pattern`,
  `secondary_structure_representations`, `structural_geometry_representations`,
  `chemical_participants`, `evolutionary_scope`, plus `xrefs` (direct) vs
  `mapped_xrefs` (mapping-derived), `trait_relations` (typed edges), `evidence`
  (`EvidenceItem`: `reference` DOI:/PMID:/CURIE + snippet), `canonical_examples`.
- **Index build** `scripts/build_docs_index.py` — the per-record projection
  (`records.<AXIS>[.NN].json` main shards + `detail/NNN.json` sidecars +
  `facets.json`), including the recently-added `chem` (direct) / `chemx`
  (mapping-derived) chemical-name fields, and the sidecars `chebi.json`,
  `corpus_map.json`, `methods.json`, `neighbors/`.
- **Browser** `docs/browse.js` (list cards, detail view, facet links, search,
  curieLink resolvers, chemistry/methods/examples/equivalence rows),
  `docs/browse.html`, `docs/browse.css`.
- Recent enrichment you should treat as the current baseline (confirm coverage):
  Pfam/CDD/NCBIfam/PROSITE definitions were rewritten from real source prose;
  CATH/SCOPe/ECOD carry `structural_geometry_representations` + license (SCOPe
  has none — no rep sid); EVOLUTION carries `evolutionary_scope`; ~79k records
  carry `evidence` DOIs; FUNCTION enzymatic/pathway carry chemistry.

## Dimension 1 — Representation consistency

For each (axis, category) cell, determine the representation it *should* carry and
whether it does, uniformly:

- SEQUENCE signatures/motifs → `sequence_pattern`; localized sites → residue info.
- STRUCTURE folds/domains/superfamilies/topologies → `structural_geometry_representations`
  (note SCOPe legitimately has none); `STRUCT_SECONDARY` → `secondary_structure_representations`.
- SEQUENCE_STRUCTURE repeats/coiled-coils → repeat-unit / register / topology reps.
- FUNCTION enzymatic → EC/Rhea anchor + `chemical_participants`; pathway → GO-BP / EC set.
- EVOLUTION → `evolutionary_scope` (taxon_scope, min/max_prevalence, method, metric).

Flag: categories where the representation is **present on some records and absent on
others of the same kind** (seeder gap); representations present on the **wrong**
category; a representation that exists in the schema but is **never populated** for a
category that needs it; and whether the **direct vs mapping** split (`xrefs`/
`chemical_participants` vs `mapped_xrefs`/`chemx`) is applied the same way across cells.

## Dimension 2 — Content consistency

Sample records per cell and compare structure + quality:

- **Definition**: real self-contained prose vs residual boilerplate/label-restatement/
  import artifacts (`( )`, `<i>`, "missing ref", "N/A"); consistent across a cell.
- **Label**: human-readable, not a raw accession or a description paragraph; consistent.
- **Groundings**: `xrefs` (source-direct) vs `mapped_xrefs` (mapping product, with
  `predicate` + `mapping_source`) used correctly and consistently; `parent_traits` /
  `trait_relations` typed and same-axis.
- **Citations**: `evidence` coverage — which cells have it, which don't, and is the
  DOI/PMID shape uniform.
- **Provenance**: `definition_source` + `license` present and consistent per source.

Flag systematic gaps (a source whose whole cell is boilerplate; a cell missing
citations that a sibling cell has; inconsistent grounding provenance).

## Dimension 3 — HTML rendering consistency

Read `build_docs_index.py` (projection) and `browse.js`/`browse.html`/`browse.css`
together, and reason about how each **field type** renders in BOTH the result card
and the detail view, for every axis/category:

- **Leaked markup**: any field whose value can contain HTML/markup (definitions with
  `<i>`/`<sub>`, ChEBI names, stripped-citation stubs) reaching the DOM as raw text or
  unescaped HTML. Confirm `escapeHTML`/`escapeAttr` are applied to every dynamic value.
- **Per-axis gaps**: detail-view rows (`sequence_pattern`, secondary-structure,
  geometry, chemistry direct **and** `chemx` via-mappings, examples, equivalence,
  mapped associations, evidence, methods, parents/relations) shown for one axis but
  silently dropped for another that has the data.
- **Field-type coverage**: is every projected field actually rendered somewhere? Are
  the new `chem`/`chemx`, `evidence`, `trait_relations`, `structural_geometry_representations`
  surfaced? Is `evidence` (DOIs) displayed at all?
- **Links**: `curieLink` resolver coverage per prefix (dead/duplicate links), facet-pill
  links, UniProt members link, source-file link — consistent behaviour across cells.
- **Search parity**: does search reach the fields that matter per axis (label/def/id +
  `chem`/`chemx`); any axis whose records are effectively unsearchable by their
  distinguishing content.
- **Card vs detail parity**: the four badges, pills, and truncation behave the same
  across axes; long values (paragraph labels, big chemistry lists) don't break layout.

## Deliverables (write as `research/representation-content-rendering-review-1.md`)

- A **confirmation scan**: record + cell counts; which representation slots / evidence /
  chemistry each cell carries (a coverage matrix: axis × category × {rep, def-quality,
  citations, chem}).
- Findings grouped by the three dimensions, each ranked by blast radius, each stating:
  the inconsistency, the affected cells, and the **fix location** (seeder file / schema /
  `build_docs_index.py` / `browse.js`|`browse.css`) — seeder-level where systematic.
- A short **rendering-gap table**: field type → shown-where → gap.
- Severity: blocker (unescaped/broken render, wrong-axis representation) · major (missing
  representation for a whole cell, leaked markup, unsearchable content, absent evidence
  display) · minor (style, thin grounding).
- Read-only: do **not** edit code, records, or the schema — review and report only.
