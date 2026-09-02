---
name: fetch-source
description: Add or harden a fetch-* recipe that downloads an upstream bulk release into data/raw/ with centralized retries, validation, atomic replacement, and release metadata. Use for new release downloads or when an existing recipe is flaky or can leave partial files behind.
---

# Fetch a source release

Route fixed bulk-file downloads through `scripts/fetch_source.py`. Do not add a bare
`curl -o` to a `fetch-*` recipe: the shared helper owns HTTP failures, redirects,
retries, connect/total timeouts, temporary files, validation, atomic replacement,
cleanup, and metadata.

## Recipe contract

```bash
python3 scripts/fetch_source.py \
  "https://example.org/releases/source.tsv.gz" \
  data/raw/source/source.tsv.gz \
  --max-time 600 \
  --min-bytes 1000 \
  --prefix-hex 1f8b
```

The URL and destination are separate argv values. Quote URLs containing `?`, `&`, or
other shell metacharacters. Keep the established recipe name and final destination path.
The helper downloads to a sibling `.part` file and calls `os.replace` only after every
validation succeeds, so an existing good release survives transfer and validation
failures.

Every success writes `<destination>.fetch.json` containing the requested and resolved
URLs, UTC fetch time, byte size, SHA-256, and any ETag, Last-Modified, and Content-Type
headers exposed by the server. These sidecars live under gitignored `data/raw/`; do not
commit them.

## Choose validation deliberately

- Always set a credible `--min-bytes`; avoid a token value for a known large release.
- Use `--prefix-hex 1f8b` for gzip and an appropriate magic prefix for other archives.
- Use `--contains <text>` for a stable header or format marker.
- Use `--sha256 <hex>` when the publisher supplies an expected digest. Do not calculate
  an “expected” digest from the same untrusted download.
- Repeat `--header 'Name: value'` only when the source requires a fixed request header.

Defaults are four retries with curl's transient-error exponential backoff, a 15-second
connect timeout, and a 300-second wall-clock deadline for the complete curl process,
including retries and delays. A transfer that dies mid-body is retried too, which curl
itself will not do -- an early close is exit 18 and a reset is 56, neither of which is in
its transient set (#545) -- and those attempts are charged to the same deadline, so the
number above remains the ceiling rather than becoming a per-attempt budget. Override
`--max-time` for large releases; do not copy retry flags into the justfile.

A 200 response carrying an HTML error page is refused rather than installed as the
release. Pass `--allow-html` for a source that genuinely serves HTML; no current call site
does. Use `--dry-run` to print the transport, destination, metadata,
and validation contract without touching the network or filesystem.

Existing destination permission bits are preserved during replacement. New public raw
releases and metadata sidecars use mode `0644`; the temporary files remain private until
validation succeeds.

## Scope boundary

The helper handles one fixed URL and one destination. Paginated APIs, authentication,
dynamic file enumeration, and source-specific post-processing remain in a dedicated
script, where they need their own checkpoint and partial-failure semantics. Record that
route in `docs/fetch-migration.md`; do not force it through shell interpolation.

When migrating an existing recipe, run `pytest tests/test_fetch_source.py`, `just --dry-run
fetch-<source>`, and the source registry gate. Update the migration checklist so every
`fetch-*` recipe remains accounted for.
