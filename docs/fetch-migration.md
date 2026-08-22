# Fetch recipe migration

`scripts/fetch_source.py` is the transport contract for fixed bulk-release URLs. It
centralizes retries and timeouts, validates a sibling temporary file, atomically replaces
the final path, and records a `.fetch.json` release sidecar. Recipe names and existing
destination paths stay stable during migration.

This checklist accounts for every `fetch-*` recipe in the justfile. Update it whenever a
recipe is added, removed, or migrated.

## Migrated fixed-file recipes

- `fetch-prosite`
- `fetch-ted`
- `fetch-ecod`
- `fetch-metalpdb`
- `fetch-3did`
- `fetch-biolip`
- `fetch-chebi`
- `fetch-orthodb`
- `fetch-iedb`
- `fetch-interpro`
- `fetch-pfam`

These are the first measured batch: the common CLAUDE.md examples plus the largest or
most fragile multi-file releases. Each call supplies a source-specific timeout and at
least one content/size check.

## Fixed-file recipes awaiting migration

- `fetch-reactome`
- `fetch-tcdb`
- `fetch-cog`
- `fetch-seed-subsystems`
- `fetch-rhea`
- `fetch-ec`
- `fetch-uniprot-keywords`
- `fetch-repeatsdb`
- `fetch-ncbifam`
- `fetch-panther`
- `fetch-cdd`
- `fetch-ideal`
- `fetch-elm`
- `fetch-merops`
- `fetch-aro`
- `fetch-cath`
- `fetch-scope-parse`
- `fetch-psimod`
- `fetch-obo`

Migrate these in follow-up batches after choosing credible source-specific minimum sizes,
magic bytes, stable content markers, or publisher checksums.

## Dynamic/API fetchers requiring source-specific design

- `fetch-complexportal` — discovers a changing server-side file list in shell.
- `fetch-opm` — fetches an index, then dynamically enumerates class identifiers.
- `fetch-repeatsdb-annotations` — paginated API script.
- `fetch-cazy-families` — multi-page scraper.
- `fetch-interpro-members` — paginated API script.
- `fetch-examples` — UniProt API enrichment with record writes.
- `fetch-residue-frame` — residue-coordinate API enrichment.
- `fetch-interpro-frame` — InterPro API enrichment.
- `fetch-interpro-missing-abstracts` — API enrichment of existing records.

These should reuse the helper only for any fixed bulk sub-download. Their pagination,
checkpointing, authentication, and partial-result rules belong in their Python clients.

## Non-network route

- `fetch-traitontomap` — copies from a local sibling checkout; the HTTP helper does not
  apply.

`build-go2chebi` also contains a direct fixed-file `curl`, but is not named `fetch-*`.
Move that transport through the helper in the fixed-file follow-up batch.
