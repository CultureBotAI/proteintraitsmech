---
topic: Representation, content & HTML-rendering consistency across trait axes/categories
reviewer: Codex (gpt-5-codex, via codex:codex-rescue) — prompt research/prompts/representation-content-rendering-review-prompt.md
date: 2026-07-05
mode: read-only (Codex sandbox blocked its own file write; report transcribed by Claude)
codex_session: 019f33da-8bd2-75f1-802d-0c39d63a2d12
---

# Representation / content / rendering review 1

Read-only audit of consistency across all 48 populated (trait_axis, trait_category)
cells + the docs browser + `build_docs_index.py` + the schema.

**Confirmation scan:** 278,819 records; 48 populated cells; axes — SEQUENCE 117,163,
STRUCTURE 91,264, FUNCTION 69,946, SEQUENCE_STRUCTURE 437, EVOLUTION 9.

## Findings (ranked by blast radius)

### 1. `evidence` (citations) is populated but never projected or rendered — MAJOR
78,639 records carry `evidence` (DOI/PMID), but `build_docs_index.py` does not
project it and the detail view has no row — the entire citation backfill is
invisible in the browser.
- data: e.g. `data/traits/function/enzymatic_activity/rhea/…-rhea32603.yaml:21`
- schema: `src/proteintraitsmech/schema/proteintraitsmech.yaml:346`
- gaps: projection `scripts/build_docs_index.py:366-410`; detail render `docs/browse.js:428` (no row)
- **Fix:** project a compact `evidence` field (reference + notes) and add an
  "Evidence / citations" detail row (linkify DOI:/PMID: via `curieLink`).

### 2. Chemical search is half-wired — MAJOR (regression from the chem work)
`computeFacetCounts` matches `chem`/`chemx` (`docs/browse.js:338-343`), but the
actual record filter `filterRecords` still matches only id/label/definition
(`docs/browse.js:427-432`) — so the search placeholder promises chemical search
(`docs/browse.html:27`) that the result list never delivers.
- **Fix:** add the same `chem`/`chemx` clause to `filterRecords` (the search
  edit landed in only one of the two match sites).

### 3. `evolutionary_scope` present but not projected/rendered — MAJOR
All 9 EVOLUTION records carry `evolutionary_scope`, but it is neither projected
nor shown (no comparable representation surfaced for the axis).
- data: `data/traits/evolution/conservation/conserved-protein.yaml:17`,
  `data/traits/evolution/pangenome/shell-protein.yaml:17`
- gaps: projection `scripts/build_docs_index.py:366-410`; detail `docs/browse.js:630-653`
- **Fix:** project + render the band (taxon_scope, min/max_prevalence, method).

### 4. Import markup / placeholders leak into definitions — MAJOR (content)
Systematic across whole cells:
- **247 files with `<i>` tags**, all `STRUCT_ACTIVE_SITE` (M-CSA) — e.g.
  `data/traits/structure/active_site/mcsa/dgtpase-mcsa966.yaml:4`.
- **7,098 files with `( )` placeholder stubs** (stripped citations), mostly
  sequence cells (InterPro) — e.g.
  `data/traits/sequence/conservation/interpro/…-ipr000842.yaml:4`.
- **Fix at the seeders:** strip HTML in `seed_mcsa.py`; drop empty `( )` in
  `seed_interpro.py`'s abstract cleaner (it already removes `[ ]` cite stubs — add
  the paren case). These render as raw noise in label/definition.

### 5. SEQUENCE_STRUCTURE lacks comparable repeat/register/topology reps — MAJOR
`MIXED_COILED_COIL` / `MIXED_STRUCTURAL_REPEAT` carry no heptad-register /
repeat-unit / topology representation, so the axis has no comparable
representation slot populated.
- data: `data/traits/mixed/coiled_coil/pfam/angiomotin-c-pf12240.yaml:6-22`,
  `data/traits/sequence_structure/structural_repeat/repeatsdb/alpha-beta-trefoil-4-3-2.yaml:6-12`
- **Fix:** populate a representation (RepeatsDB unit/topology; coiled-coil register)
  or record the gap explicitly.

## Rendering-gap table

| Field | Populated on | Projected? | Detail row? | Searchable? |
|-------|-------------|-----------|-------------|-------------|
| `evidence` (DOI/PMID) | 78,639 records | no | no | n/a |
| `evolutionary_scope` | 9 EVOLUTION | no | no | n/a |
| `chem` / `chemx` | 19,215 / 8,877 | yes | yes (chem) | **facet-count only, not the list filter** |
| `structural_geometry_representations` | CATH/ECOD/TED | yes (`geo`) | yes | — |
| `secondary_structure_representations` | STRUCT_SECONDARY | yes (`ss`) | yes | — |

## Priority
1. **Wire chemical search into `filterRecords`** (one-line, fixes a live regression).
2. **Project + render `evidence`** (surfaces the whole citation backfill).
3. **Project + render `evolutionary_scope`.**
4. **Seeder sanitize:** M-CSA `<i>` (247) + InterPro `( )` (7,098) in definitions.
5. Populate a MIXED representation or document the gap.
