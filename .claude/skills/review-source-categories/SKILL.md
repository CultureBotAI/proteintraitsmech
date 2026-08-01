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
docs build uses. Takes ~1-2 min over the full corpus.

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
