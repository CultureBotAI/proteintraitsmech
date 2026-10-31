# Motif discovery and independent cavity-review evidence

Date: 2026-10-29 UTC. Owner: `/root/grounding_route_audit` in the parent-owned
structural discovery goal on `discover/structural-traits-20261028-04f08f`.
Related coordination: ProteinTraitsMech issues #1200, #1201 and #1204. These
references identify task context; this directory does not close those issues.

This directory contains bounded motif discovery inputs and independent science
reviews of cavity records authored by other agents. It does not own trait records,
the maintained discovery manifest, schema, native emitter, Git or live sessions.
Native review inputs are prepared here; the coordinator saves immutable bundles
through `scripts/record_review.py save`. Historical inputs, failed attempts and
earlier reviews are retained without replacing their conclusions.

## Helper provenance

Every helper below was created/used on 2026-10-29 for the goal above. Relative
input/output names resolve within this directory unless a repository path or URL
is stated. Each helper's source contains its exact command arguments and paths.

| Helper | Purpose | Inputs | Outputs |
| --- | --- | --- | --- |
| `reproduce_collision_scan.py` | Reproduce initial bounded searches or run a refined alias scan that includes ignored files | `initial-collision-search.json`; repository corpus/staging/index/research roots; explicit regexes | New timestamped refined/replay JSON and gzip evidence; does not overwrite initial results |
| `fetch_primary_evidence.py` | Retain two small primary motif-source artifacts | BMC2009 supplement URL and Europe PMC9530121 full-text XML URL, both embedded in source | `motivated-proteins-2009-supplement5.zip`, `natcomm-2022-immunoglobulin.xml`, `primary-artifact-retrieval.json` |
| `inspect_identity_and_tool_docs.py` | Check exact SO identities/license and HBPLUS documentation | Official SO ontology/license URLs and HBPLUS documentation archive URL | Retained ontology/license/archive, `identity-tool-doc-retrieval.json`, selected `hbplus-official-doc-text.json` |
| `check_bottleneck_canary.py` | Freeze one exact prewrite row and use the native closed validator | Pinned initial one-row manifest; native schema/validator; cavity card; historical CAVER `/tmp` inputs listed below | `bottleneck-canary-reviewed-row-20261029T0704Z.yaml`, `bottleneck-canary-validation-20261029T0704Z.json` |
| `retain_canary_sources.py` | Retain already-inspected primary/authority bytes | PLOS2012, RCSB1CQW and bio.tools CAVER URLs; exact CAVER `/tmp` PDF/text | PLOS HTML, RCSB JSON, registry JSON, unchanged manual PDF/text, `canary-source-retention-20261029T0704Z.json` |
| `prepare_canary_native_review.py` | Prepare the independent actual-canary native review input | Native inspection; emitted record; pinned one-row manifest; frozen row; reviewed source bytes; current rubric | Native inspection with rubric, semantic comparison, unsaved review input and original validation attempt |
| `normalize_canary_review_input.py` | Remove duplicate evidence-ID references in the unsaved canary input only | `canary-native-review-input.yaml` before coordinator save | Corrected unsaved input and `canary-native-review-input-validation-normalized.json`; no immutable bundle changes |
| `retain_fenestration_sources.py` | Retain two bounded already-inspected primary/authority responses | PNAS2401591121 publisher URL and RCSB7WLI core-entry URL | `fenestration-source-retrieval.json` and RCSB JSON; publisher403 preserved as a failed retention attempt |
| `retain_fenestration_pdf.py` | Preserve the inspected published PNAS paper from another researcher's temporary download | Hash-pinned `/tmp/nalcn-fenestration.pdf`; original public mirror URL in source | Unchanged published PDF, `pdftotext -layout` extraction, `fenestration-pdf-provenance.json` |
| `prepare_fenestration_native_review.py` | Prepare independently assessed native record review without saving a bundle | Native inspection with exact emitted record/manifest/source/rubric hashes; completed native gates | `fenestration-native-review-input.yaml`, semantic-comparison JSON, validation JSON |
| `inventory_helper_provenance.py` | Capture exact helper bytes and link this purpose/input/output inventory | This README and every local `*.py` helper, including itself | New `helper-provenance-20261029.json`; no scientific judgment or corpus changes |

The canary preparation initially failed native review validation because one
assessment repeated an evidence ID. The original failed validation artifact is
retained. The normalization helper fixed only that unsaved input; the successful
validation artifact records its new hash. Do not rerun that helper against a
published review: use a new linked observation if a saved review needs correction.

## Historical and portable inputs

The following absolute temporary inputs were explicitly supplied by the cavity
researcher. They were read, never modified or deleted here:

| Temporary source | Retained destination | Source-byte SHA256 |
| --- | --- | --- |
| `/tmp/caver-discovery-userguide.pdf` | `caver-discovery-userguide.pdf` | `035f7cb504fde9d6a49250ca13e575780d934d3a45ebb48f9c942d5d54f83305` |
| `/tmp/caver-discovery-userguide.txt` | `caver-discovery-userguide.txt` | `8fb14bec46975c714c5ea04dfe20472b5815cd4dc779b763fb1b9aa5fd9d2a68` |
| `/tmp/nalcn-fenestration.pdf` | `fenestration-pnas-published.pdf` | `2e41cc55e593194f998f2656d2d0101ce9d5a9d5236e5673f02abc4638498b8b` |

Original URLs, acquisition dates, hashes and extraction commands are in the
corresponding provenance JSON/helpers. `/tmp` paths are historical acquisition
locations, not portable dependencies or promised future files. The retained
bytes or a source-identical reacquisition are necessary to replay those steps.
Remote URLs may change: new bytes require version verification and scientific
reassessment, not a silent hash refresh.

Initial broad searches generated large minified-context logs. They remain
preserved as ignored gzip files; `raw-search-compression-manifest.json` records
original/compressed hashes, sizes and the original lossless-verification result.
Compression was a historical inline operation; `reproduce_collision_scan.py`
retains the original search argument vectors and can produce new timestamped
results. Gzip-header bytes need not repeat, and today’s corpus is not the historical
search state. Compact refined search metadata are the reviewable summary. No
large collision log, SO release or HBPLUS archive is proposed for Git publication.

Some raw evidence remains ignored and may be absent from a clean clone. Native
working-tree reviews attest the exact inspected bytes and preserve their hashes;
they do not claim all local evidence was committed. Preserve the local artifacts.
Compact source URLs, hash manifests, candidate cards, review inputs and helper
code support provenance without treating mutable remote downloads as immutable.

The first canary manifest contained one row. Later discovery manifests contain
more rows. Its pinned historical helpers intentionally reject the newer manifest;
that is a drift guard, not permission to update earlier reviews. The independently
reviewed scientific contents and emitted bytes have their own recorded hashes.

## Scope limits

No external CAVER/MOLE/HBPLUS structure analysis ran here. Runnable templates and
manual discriminators are documented as such. PDB anchors are whole-structure
source references, not qualified canonical protein occurrences or invented
residue boundaries. Source licenses remain separate from project-authored
synthesis. Evidence alone does not promote `PROPOSED` to human `REVIEWED`.
