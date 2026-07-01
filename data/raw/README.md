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
