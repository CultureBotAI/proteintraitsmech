---
name: review-source-categories
description: Review, per data source, which trait categories and axes it contributes to ProteinTraitsMech, and flag records that are mis-modelled for a trait-*class* knowledge base — instance-level (per-protein) records, family signatures misused as parent_traits, axis/category mismatches, and drift from the categories a source declares in download.yaml. Trigger when asked to "review the trait categories of a source", after ingesting or re-seeding a source, when a record's parent_traits / axis / category look wrong, or as a periodic modelling-quality gate.
---

# Review Source Trait Categories

ProteinTraitsMech is a catalogue of trait **classes** (a family, a fold, an
enzyme activity, a binding capacity…), each optionally illustrated by
`canonical_examples`. A recurring failure mode is a seeder that emits records
which look like traits but aren't: per-protein annotations, or associations
(family memberships, mappings) dressed up as `parent_traits`. This skill audits
every source's category footprint and surfaces those cases.

## Run it

```bash
just review-categories                     # full corpus, per-source summary + flags
just review-categories --flags-only        # only sources with anomalies
just review-categories --source UniProtKB  # one source
just review-categories --show 10           # more example files per flag
```

Read-only; scans `data/traits/**` and groups by the same `infer_source` the
docs build uses. It scans the full corpus, so budget the run accordingly.
The output is a deterministic diagnostic scan, not completed scientific review;
read its skipped-input count and display limit before making coverage claims.

## Persist the reviewed result

Follow [docs/record-reviews.md](../../../docs/record-reviews.md) and
[the native profile](../../../docs/record-review-profile.md). Resolve a bounded
source/category cohort, read the selected records in full, and capture exact
targets before judging with `uv run python scripts/record_review.py inspect
--targets <targets.yaml> --input download.yaml --input scripts/review_source_categories.py
--input scripts/build_docs_index.py`. Add inspected seeders and source tables
as inputs. Record population, selection, actual reviewed IDs, sampling and
exclusions; `--show N` examples do not imply the rest were read.

Persist a `kind: category` review with explicit retain/lump/split/defer
decisions, axis/category/source dimensions, and evidence-linked adjudication of
INSTANCE_LEVEL, FAMILY_AS_PARENT, AXIS_CAT_MISMATCH and UNDECLARED_CAT. Preserve
those native rule IDs and explain severity normalization. Generated-record
fixes belong to their maintained seeder/routing table; declaration corrections
belong to `download.yaml`, and source-inference corrections to
`scripts/build_docs_index.py`. Include exact owner paths and acceptance checks.

If only the scan ran, use `scientific_review: false` and describe its limited
deterministic scope; do not claim literature or identity was reviewed. Validate
and save assessed content with `uv run python scripts/record_review.py validate
<review.yaml>` followed by `uv run python scripts/record_review.py save --content
<review.yaml>`. Link both saved files under `reviews/structured/<timestamp>-<slug>/`.
Flags and a zero scan exit code alone do not decide the scientific verdict.

## What each source report shows

- **axes / status** distribution (a healthy source is usually one axis and
  `SEEDED`/`REVIEWED`);
- **trait_category distribution** — the answer to "what categories does this
  source contribute"; a long tail of 1-record categories often means the
  category granularity is wrong (see the EVO collapse precedent: 9 one-record
  `EVO_*` categories → `EVO_CONSERVATION` + `EVO_PANGENOME`);
- **flags** — records that need a human decision.

## The flags and how to fix them

| Flag | Meaning | Fix |
|------|---------|-----|
| **INSTANCE_LEVEL** | Record is scoped to a single protein (`proteintraitsmech:UNIPROTKB_<acc>_…`, or a curator-minted id whose only UniProtKB xref *is* the subject). That is an annotation, not a reusable trait class. | Re-express as a `canonical_example` on the class-level trait (e.g. the GO/EC/Pfam term), and retire the per-protein record. Fix the seeder so it attaches examples to classes, not one record per protein. |
| **FAMILY_AS_PARENT** | `parent_traits` carries a family/domain **signature** (Pfam/InterPro/HAMAP/SMART/CATH/SCOP/…) on a record whose own category is *not* a structural family — i.e. an association misused as an `rdfs:subClassOf` parent. | Move the signatures off `parent_traits`. If they describe the protein, they belong on the example's `family_classifications`. A trait's real parent is a broader class in the same conceptual axis (GO:0005506 → GO:0005488, not Pfam:PF15461). |
| **AXIS_CAT_MISMATCH** | The category prefix (`SEQ_/STRUCT_/MIXED_/FUNC_/EVO_`) disagrees with `trait_axis`. | One of the two is wrong in the seeder's routing table; correct and re-seed. |
| **UNDECLARED_CAT** | The source emits a category absent from its `trait_categories:` in `download.yaml`. | Either the seeder drifted (fix it) or `download.yaml` is stale (update the declared set). Keep the two in sync. |

`STRUCT_DOMAIN`, `STRUCT_FOLD`, `SEQ_REPEAT`, `MIXED_*`, etc. are **family
categories** — a family signature *is* a legitimate parent there, so
FAMILY_AS_PARENT is deliberately not raised for them (see `FAMILY_CATEGORIES`
in the script).

## Interpreting: not every flag is a bug

The flags are *candidates for review*, not automatic errors. A UniProt demo
seed legitimately produces INSTANCE_LEVEL records; the question is whether they
belong in the corpus as-is. Decide per source, then either fix the seeder +
re-seed, or record why the pattern is acceptable.

## Best practices

1. **Run after every new/changed seeder**, before committing — it is the
   modelling-quality analogue of `just validate-all` (which only checks the
   schema, not whether a record is a sensible *trait*).
2. **Fix at the seeder, not the record.** Like the `merge-traits` skill: a
   growing flag count means a seeder bug; patch the seeder and re-seed rather
   than hand-editing YAMLs.
3. **Keep `download.yaml` `trait_categories` honest** — UNDECLARED_CAT is only
   useful if the declared set is maintained.
4. **Re-run after fixes** and confirm the flag count drops to the expected
   residue (0, or the set you consciously accepted).
