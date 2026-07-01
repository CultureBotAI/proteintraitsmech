# data/raw/

Vendored copies of upstream data releases used to seed `data/traits/`.
Files in this directory are **gitignored** — regenerable via the
matching `just fetch-*` recipe. This README stays checked in so the
provenance is visible without needing to run anything.

## Current sources

### PROSITE

- URL: <ftp://ftp.expasy.org/databases/prosite/>
- Files: `prosite.dat` (patterns + profiles, ~25 MB), `prorule.dat`
  (ProRules, ~1.6 MB), `ps_reldt.txt` (release date stamp)
- Fetch: `just fetch-prosite`
- Seed: `just seed-prosite` (dry-run) / `just seed-prosite --apply`
- License: CC BY-NC-ND 4.0 (see
  <https://prosite.expasy.org/prosite_license.html>). The seeded YAMLs
  under `data/traits/` inherit the ProteinTraitsMech repo license
  (CC0-1.0); the raw dumps themselves are not redistributed here.

### TED (The Encyclopedia of Domains)

- URL: <https://ted.cathdb.info/> — bulk data on Zenodo
  ([DOI:10.5281/zenodo.13908086](https://doi.org/10.5281/zenodo.13908086),
  v5 / 2024-10-31)
- Files: `ted_novel_folds.tsv.gz` (7,427 novel fold representatives,
  ~700 KB), `ted_high_symmetry_folds.tsv.gz` (6,433 highly-symmetric
  fold representatives, ~530 KB)
- Fetch: `just fetch-ted`
- Seed: `just seed-ted` (dry-run) / `just seed-ted --apply`
- License: CC-BY 4.0 upstream; the seeded YAMLs under `data/traits/`
  inherit the ProteinTraitsMech repo license (CC0-1.0).
- Scope: We seed only the two bounded fold catalogues (~14 K records
  combined). The ~365 M individual TED domain assignments are not
  suitable for one-YAML-per-record — reference them via the same
  Zenodo record if you need per-domain coverage.
