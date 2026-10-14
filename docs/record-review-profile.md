# ProteinTraitsMech Record Review Profile

The [shared contract](record-reviews.md) governs new review observations.
`conf/record_review.yaml` lists the active routes and their existing rubrics.
CLAW owns the byte-identical schema, helper, common guide and contract test;
this profile and native skill sections remain ProteinTraitsMech-owned.
Historical reports and scientific records are not migrated by this adoption.

## Routes and scope

- `review-yaml-record` and audit-only `curate-yaml-record`: `kind: record`,
  applying the local field checklist to one complete ProteinTraitRecord.
- `review-yaml-category`: `kind: category`, explicit membership and evidenced
  lump/split/retain/defer decisions for a coherent source or category cohort.
- `review-record-samples`: `kind: batch`, normally `coverage: sampled`.
  Persist exact paths/IDs, total eligible population, seed, PER, axis/category
  strata and per-stratum counts, exclusions and limitations. Assess A1-A9 for
  every read record and B1-B6 for the applicable sets. A sample cannot certify
  all records in a category, even when every axis/category cell is represented.
- `review-source-categories`: use `just review-categories` for diagnostic input,
  then read records and save bounded `category` reviews with boundary decisions.
  A scan-only observation is `kind: repository`, `scientific_review: false`,
  with explicit targets and coverage; scan counts are not manual review counts.
- `codex-schema-hierarchy-review`: `kind: repository` with the exact sampled
  records and schema inputs. Retain the native concept, hierarchy, Biolink/RO,
  proposed taxonomy and oddity questions as assessments and proposed actions.
- `ground-protein-example`: resolved TSV/JSONL files remain staging inputs.
  A reviewed record or batch is persisted through the shared saver, with exact
  record and candidate IDs, release, source-asserted coordinates, taxon, native
  resolution digests and inspected evidence. Capture a native semantic digest
  on the corresponding target with its actual algorithm and definition; do not
  confuse a candidate digest with the SHA-256 of a whole record file.

Provider research, embedding audits, source discovery, issue triage and merge
planning remain inputs or other workflows. Provider success and generated
candidate metadata alone are not completed scientific record reviews.

## Commands and ownership

Run in the repository environment (`just install` installs project/dev dependencies):

```bash
uv run python scripts/record_review.py inspect --targets /tmp/targets.yaml --input download.yaml
uv run python scripts/record_review.py validate /tmp/completed-review.yaml
uv run python scripts/record_review.py save --content /tmp/completed-review.yaml
just check-record-reviews
just test-record-reviews
just validate <record-path>
just validate-all <record-path>
just audit-graphs <record-path>
just review-categories --source <source-label>
```

Use session-unique temporary paths. Add every schema, source table, seeder,
overlay or release sidecar used in the judgement with `inspect --input`.
`just review-categories` calls `scripts/review_source_categories.py`; its
display limit and skipped inputs must be reported, and its flags require
adjudication. The sampling snippet selects records; it does not review them.
The protein-example selector, resolver and finalizer keep their existing
manifest, receipt, TSV and digest contracts. None of those outputs substitutes
for `scripts/record_review.py save` after source inspection and assessment.

For seeded/generated records, identify the actual `scripts/seed_*.py`, source
routing table or maintained overlay owning the correction. `download.yaml`
owns declared source categories; `scripts/build_docs_index.py` owns
`infer_source` classification. Cite both where a routing discrepancy spans
them. A systemic sampling defect belongs to that seeder/transform, not a set
of hand-edited emitted records. Record exact owner paths and acceptance checks
in findings/actions, with an explicit uncertainty note if ownership is unresolved.

## Retained scientific gates

Class-level identity, representation-specific axes/categories, source releases,
licensing, hierarchy and edge-level evidence remain mandatory. The guarded
record writer and `just audit-writers` remain unchanged. `mapping_status:
REVIEWED` still requires human sign-off; a valid review bundle cannot promote
a record, qualify a protein or append curation/history events. UniProt promotion
still requires its release-pinned registry/evidence, resolution digest,
source-stratified review and qualified-occurrence checks plus authorization.

PR and merge-group `checks.yml` runs the common contract test alongside native
gates. `reviews/structured/<timestamp>-<slug>/review.yaml` is authoritative.
The workflow supplies `RECORD_REVIEW_BASE` from the trusted PR base SHA,
merge-group base SHA or push-before SHA and checks out full history, so a
committed rewrite/deletion of an earlier bundle fails the append-only check.
Local checks default to HEAD; an explicit manual workflow fallback may do so.
The sibling Markdown is generated by the saver. Both are Git-visible; existing
ignored report/staging directories retain their policies.
