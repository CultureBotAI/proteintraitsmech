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
- `fetch-elife-metallophores` (immutable Zenodo release, article and tables; publisher
  MD5 and pinned SHA-256 verified by the source parser before ingest)
- `fetch-cath`

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
- `fetch-scope-parse`
- `fetch-psimod`
- `fetch-obo`

Migrate these in follow-up batches after choosing credible source-specific minimum sizes,
magic bytes, stable content markers, or publisher checksums.

## Dynamic/API fetchers requiring source-specific design

- `fetch-slc10-models` — bounded three-file AlphaFold v6 snapshot, with every
  download routed through `fetch_source.py`. New ignored directories only;
  completion manifest written after all three predictions pass format checks.
  Separate from experimental PDB/SIFTS acquisition and never a trait writer.

- `fetch-slc10-pilot` — seven exact UniProt accessions (original response bytes,
  accession and single-release checks), plus three PDB mmCIF and three residue-level
  SIFTS files through `fetch_source.py`. Dry-run by default; only a new ignored
  research snapshot is written. No trait, canonical-example, or grounding promotion.
  Partial snapshots lack the completion manifest and must not be consumed.

- `fetch-complexportal` — discovers a changing server-side file list in shell.
- `fetch-opm` — fetches an index, then dynamically enumerates class identifiers.
- `fetch-repeatsdb-annotations` — paginated API script.
- `fetch-cazy-families` — multi-page scraper.
- `fetch-interpro-members` — paginated API script.
- `fetch-examples` — candidate-only UniProt API discovery; no record writes. Its
  pagination/retry rules remain source-specific, while promotion is handled by the
  release-pinned grounding workflow.
- `fetch-residue-frame` — residue-coordinate API enrichment.
- `fetch-interpro-frame` — InterPro API enrichment.
- `build-profiles` — bounded UniProtKB discovery matrix, not canonical-example evidence.
  The paginated client checks a single release and advertised totals, reports deliberate
  limits as incomplete, and publishes a new `--out-dir` bundle with a trait-index snapshot
  and acquisition receipt. Existing outputs and cached indexes are never replaced.
  Use `--expect-release` to pin a reviewed acquisition plan and `--require-complete` to
  reject query truncation; dry-run performs read-only discovery without writing files.
  Set `--max-pages` to bound page requests **per query**, even for short server pages;
  each page has at most four attempts. Exhaustion fails before the next request and
  publishes no partial bundle, including when an earlier query already completed.
  The entry and page limits are separate, and the receipt records both. Omitting
  `--max-pages` preserves the uncapped-page behavior; acquisition plans should set it.
  Publication uses a native atomic no-replace rename on macOS/Linux (Windows rename is
  already no-replace), failing closed if the platform or filesystem cannot provide it.
- `fetch-uniprot-registry` — exact-accession, same-response protein metadata/sequence and
  database-cross-reference snapshots for the grounding workflow; release-header,
  checksum, exact-membership, and content-address gates are implemented in its Python
  client. The membership snapshot is evidence; the discovery query itself is not.
- `fetch-uniprot-review-batch` — bounded wrapper around the same pinned registry client;
  it derives the exact accession set from one named review ledger and writes only that
  batch's ignored registry, membership, and blocked-accession staging outputs.
- `fetch-interpro-missing-abstracts` — API enrichment of existing records.
- `fetch-uniprot-lineage` — exact-accession batches for taxon and domain of life of the
  embedded example proteins; map labels only, no record or grounding writes. Dry-run plan
  by default, one-release rule on the `x-uniprot-release` header, per-batch checkpoint and
  a receipt are in its Python client.
- `fetch-biolip-sifts` — derives one PDBe residue-level SIFTS XML URL per PDB from the
  BioLiP missing-protein stage, then writes a complete, content-addressed manifest under
  the ignored BioLiP SIFTS raw snapshot root.
- `fetch-biolip-sifts-uniprot` — derives exact UniProt accessions from the BioLiP SIFTS
  mapping stage, replays that stage before every network request and write, then writes a
  complete registry, membership, blocked-accession ledger, and receipt under the ignored
  UniProt grounding staging root.

These should reuse the helper only for any fixed bulk sub-download. Their pagination,
checkpointing, authentication, and partial-result rules belong in their Python clients.

## Bounded chemistry acquisition

`fetch-amino-acid-properties` is a bounded 22-file chemistry acquisition using
the shared fetcher for every CCD/parameter file. It writes only a new ignored
snapshot, hashes all inputs, and publishes a completion manifest only after all
transfers succeed. Downloaded Biopython source files are parsed as literal data,
never imported or executed. It does not write trait or grounding records.

## Non-network route

- `fetch-traitontomap` — copies from a local sibling checkout; the HTTP helper does not
  apply.

`build-go2chebi` also contains a direct fixed-file `curl`, but is not named `fetch-*`.
Move that transport through the helper in the fixed-file follow-up batch.
