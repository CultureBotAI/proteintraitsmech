# Semantic text map inputs

`just text-map-inputs` validates a read-only preview of the full YAML corpus.
`just text-map-inputs --limit 10 --output /tmp/proteintraitsmech-canary.jsonl` exports an
explicit subset; `just text-map-inputs --output /tmp/proteintraitsmech-full.jsonl` exports
the full corpus. Repeated `--record data/traits/...yaml` selects named records.
The JSON summary states full/subset scope, record count, adapter version and
SHA-256 of the exact JSONL bytes. A failed export preserves any prior output.

Each line contains identifier, label, category, page, source_path, text,
text_sha256 and adapter_version. Paths and identifiers are checked, files are
indexed on disk and documents are emitted one at a time in stable path order.
The adapter does not load models, reuse vector caches, or change corpus records.

The text uses the existing domain-specific `embed_records.py` representation.
It preserves meaningful fields and the documented exclusion of curation process
metadata and raw chemical/protein sequences. Page links follow the current site
renderer and point at individual records. The installed shared fleet runtime consumes
this input to generate pinned BGE/PaCMAP artifacts; the adapter alone does not
publish a map or certify old cache provenance.

For ProteinTraitsMech, current YAML is projected to the same full-mode fields as
`build_docs_index.py` and the shared `embedding_documents.py` renderer: definition
whitespace/cap (500 characters), first six synonyms, layered definitions,
class-defining motif, direct chemical names, and shared identifier groundings.
`docs/data/chebi.json` supplies direct chemical names and must exist; the export
fails if it is missing. Full-mode text is read from current YAML, so it does not
inherit a stale generated record-shard inventory. The definition-only and protein
signature maps remain separate existing views. Links use the supported
`browse.html#record=<encoded identifier>` route.

The shared runtime is installed and site publication is enabled in
`conf/text_map.yaml` with a verified full-corpus bundle. `just build-docs` and
the Pages workflow first call `scripts/stage_text_map.py`: enabled maps are checked
against fresh full YAML inputs, the pinned BGE profile and actual PaCMAP before
any published-site files change. The canonical runtime stages `docs/text-map/`;
only successful staging enables the hidden Semantic text map links on the static
landing, browser and legacy map pages via `docs/data/text_map_status.json`.
Disabling the setting clears this status without deleting the existing specialty
maps. The standalone staging command requires only PyYAML beyond the Python standard
library; it performs no model inference and does not import NumPy or Torch.

When enabled, the pinned shared BGE map is the primary text-map navigation target.
Historical full-description/definition-only text coordinates are explicitly legacy
views: their missing model revision and complete input identity are not backfilled
or inferred from a current cache. Chemical and protein-feature maps remain
separate specialty views with their own representations.

The [locked runtime guide](../conf/embedding-runtime/README.md) documents the
installed Python 3.13 environment and the explicit export, inspect, embed,
project and check commands. Semantic curation requires a matching local
cache-backed map refresh before enabled site checks can pass: export the full
current corpus, update its verified vector cache, rebuild the bundle and run
its freshness check before rendering. Unchanged records reuse matching cache
entries. Model inference is not run automatically in CI, and historical caches
without matching provenance are not silently reused.
