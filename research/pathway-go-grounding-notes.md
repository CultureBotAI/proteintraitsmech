# Pathway → GO-BP grounding notes

Enriched FUNC_PATHWAY records with GO biological-process (GO-BP) `mapped_xrefs`, so a
downstream overlay can anchor SEED ↔ Reactome pathway equivalence on shared GO-BP CURIEs.
Date: 2026-07-04.

## Method

- **Reactome (authoritative):** for each record, GET
  `https://reactome.org/ContentService/data/query/<R-HSA-id>` and read
  `goBiologicalProcess.accession` → `GO:<accession>`. Raw responses cached under
  `data/raw/reactome/go/` (gitignored). ~0.12 s/call, all 2883 fetched (0 HTTP failures).
  Appended `{object: GO:<acc>, predicate: biolink:related_to, mapping_source: reactome_go_bp}`.
- **SEED (fuzzy side, kept precise):** parsed `data/raw/go-basic.obo` restricted to
  `namespace: biological_process`, non-obsolete → {normalized name → GO id} (24 123 names)
  and {normalized EXACT synonym → GO id} (41 723). Normalization: lowercase, punctuation→space,
  collapse spaces, trim. Matched subsystem `label` ONLY by exact normalized equality to a
  GO-BP term name or EXACT synonym — no substring/fuzzy. Appended
  `{object: GO:<id>, predicate: biolink:related_to, mapping_source: seed_name_go_bp}`.
  Only the 920 leaf `seed-subsystem-*.yaml` records were considered; the `spine/`
  class/subclass/superclass records were left untouched.

## Results

- **Reactome with GO-BP:** 1347 / 2883 records enriched = **46.7 %**.
  (The remaining ~53 % are granular sub-pathways with no `goBiologicalProcess` — expected.)
  807 distinct GO-BP CURIEs across the Reactome side.
- **SEED subsystems matched:** 45 / 920 = **4.9 %** (exact-match only, precision over recall).
  45 distinct GO-BP CURIEs.
- **Bridge potential** — GO-BP CURIEs carried by ≥1 Reactome AND ≥1 SEED record: **10**.
  `GO:0000050, GO:0005977, GO:0006098, GO:0006099, GO:0006548, GO:0006595, GO:0006656,`
  `GO:0006744, GO:0009062, GO:0015701`.

## Validation

`uv run linkml-validate` (closed-mode, target ProteinTraitRecord) over 20 enriched samples
(14 Reactome + 6 SEED) → 20/20 PASS. New GO entries append after any existing `mapped_xrefs`
(e.g. `seed_role_ec` EC entries) and before the trailing `license:` line.

## Notes / caveats

- `.gitignore` extended with `data/raw/go-basic.obo` and `data/raw/reactome/go/`
  (`data/raw/reactome/` was already ignored).
- SEED matches include GO synonym hits where SEED "…synthesis" maps to GO "…biosynthesis"
  via an EXACT synonym (e.g. Biotin biosynthesis → GO:0009102). These are genuine exact
  synonym matches, not fuzzy.
- Idempotent: re-running skips records already carrying the respective `mapping_source`.
