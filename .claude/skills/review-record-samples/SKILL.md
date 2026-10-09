---
name: review-record-samples
description: >-
  Use this skill to spot-check the CONTENT and STRUCTURE quality of
  ProteinTraitRecords by sampling 5 random records from every trait_category
  and reviewing each record individually AND each five-record set as a whole.
  It is the content-quality gate that complements `just validate-all` (schema
  only) and the `review-source-categories` skill (per-source category
  footprint): those never open a record to ask "is this a well-formed,
  correctly-categorised, class-level trait with a real definition and the right
  groundings?" — this does. Trigger when asked to review record quality,
  spot-check/audit trait records, sample records per category, "review 5 random
  per category", check definitions/structure/content of records, or as a
  periodic content-quality sweep after seeding.
---

# Review Record Samples

## What this is

`validate-all` proves a record matches the **schema**. `review-source-categories`
profiles which **categories** a source emits and flags gross mis-modelling. Neither
reads a record's prose to judge whether it is actually a *good trait record*. This
skill closes that gap: for **each `trait_category`**, sample **5 random records**,
then review

1. **each record** — structure + content, against the rubric below; and
2. **each set of five, as a whole** — are they consistent, coherent, and at the
   right granularity, and is any defect *systemic* (a seeder bug, not a one-off)?

Findings are candidates for a human decision, and — per this repo's rule — a defect
seen across the five is fixed **at the seeder**, not by hand-editing YAMLs.

## Sample (reproducible)

Fixed seed → the same sample every run, so findings are reproducible and re-checkable.
Set `PER` — records per **(trait_axis, trait_category) cell**:

- **`PER = 1`** — one random record per live axis-category cell: a
  taxonomy-wide **snapshot**. Part A per record + Part B applied *across* cells
  (coherence of the whole taxonomy, category granularity, systemic patterns).
  The quick default sweep.
- **`PER = 5`** — up to five per live cell: enables the within-category
  **set** review (Part B per five). Use for a deep pass on flagged categories.

```bash
python3 - <<'PY'
import os, re, random, collections
PER = 1                                       # 1 = one-per-cell snapshot; 5 = deep set review
random.seed(20260704)                         # change only to draw a fresh sample
CAT = re.compile(r'^trait_category:\s*(\S+)', re.M)
AX  = re.compile(r'^trait_axis:\s*(\S+)', re.M)
by_cell = collections.defaultdict(list)
for root, _, files in os.walk('data/traits'):
    for fn in files:
        if fn.endswith('.yaml'):
            p = os.path.join(root, fn); t = open(p, encoding='utf-8').read()
            mc, ma = CAT.search(t), AX.search(t)
            if mc and ma: by_cell[(ma.group(1), mc.group(1))].append(p)
for (ax, cat) in sorted(by_cell):
    picks = random.sample(sorted(by_cell[(ax, cat)]), min(PER, len(by_cell[(ax, cat)])))
    print(f"\n### {ax} / {cat}  ({len(by_cell[(ax, cat)])} records)")
    for p in picks: print("  " + p)
PY
```

Scope when needed: filter `by_cell` keys to one axis. For `PER = 5` fan out **one
subagent per axis** (or per category) so every set gets focused reading; for
`PER = 1` a single reviewer can cover the taxonomy-wide snapshot. Always `Read` each
sampled file in full before judging it.

---

## Part A — per-record review (structure + content)

For each sampled record, check:

| # | Check | Red flag |
|---|-------|----------|
| A1 | **Required fields present** | missing `identifier` / `label` / `definition` / `trait_axis` / `trait_category` / `term_kind` / `mapping_status` |
| A2 | **Identifier** is a source-anchored CURIE with the right prefix (`InterPro:`, `EC:`, `PROSITE:`…); curator-minted uses `proteintraitsmech:` | invented prefix; a per-protein id (`…_UNIPROTKB_<acc>_…`) used as a class |
| A3 | **Label** is human-readable and specific | empty, a raw id, `"null"`, or the accession repeated |
| A4 | **Definition** actually defines the trait — specific, self-contained prose | empty `definition: >-`; the label restated; boilerplate template only; import artifacts (stripped citations `( )`, HTML, truncation) |
| A5 | **Axis ⇄ category** agree (prefix rule) AND the category is the *right* fine-grained bucket for the content | e.g. a conserved *site* in `SEQ_DOMAIN`, a functional family in `STRUCT_DOMAIN`, a per-protein feature anywhere |
| A6 | **Class, not instance** — a reusable trait class, examples nested in `canonical_examples` | the record *is* one protein's annotation |
| A7 | **Groundings** sensible: `xrefs` / `mapped_xrefs` correct and typed (predicate + mapping_source), `parent_traits` point to a real broader class in the same axis | dangling parent; cross-axis parent; a family signature used as `parent_traits` on a non-family record; a mapped_xref with no predicate |
| A8 | **Representation slot present where the category needs it** | `SEQ_*` signature/motif w/o `sequence_pattern`; `STRUCT_FOLD/…` w/o `structural_geometry_representations`; `STRUCT_SECONDARY` w/o `secondary_structure_representations`; `EVO_*` w/o `evolutionary_scope`; `FUNC_ENZYMATIC_ACTIVITY` w/o EC/Rhea anchor |
| A9 | **Provenance** — `definition_source` + `license` present and accurate; `mapping_status` fits the content (SEEDED vs REVIEWED w/ evidence) | wrong/missing license; REVIEWED with no `evidence` |

## Part B — the five as a set

For each category's five, step back and judge the group:

| # | Check | Red flag |
|---|-------|----------|
| B1 | **Consistency** — same shape, fields, conventions across the five | one record diverges → seeder inconsistency or a mis-routed record |
| B2 | **Coherence** — all five are the *same kind* of thing, genuinely belonging to this category | a grab-bag mixing kinds (the "STRUCTURE mixes classification + features + qualities" smell) |
| B3 | **Granularity** — the category sits at the right level | a 1-record category (over-split, cf. the EVO collapse); or a category so broad it should sub-branch |
| B4 | **Definition diversity** — definitions are real and distinct | five near-identical boilerplate defs → the seeder isn't capturing source content |
| B5 | **Grounding/representation coverage** is uniform across the five | patchy — some grounded, some bare → seeder gap |
| B6 | **Systemic vs one-off** — is a per-record flaw shared by all five? | yes → it's a **seeder bug**; fix the seeder, not the records |

---

## Findings & output

Persist every new review using [the shared contract](../../../docs/record-reviews.md)
and [native profile](../../../docs/record-review-profile.md). Before judging,
capture exact selected paths/IDs and input hashes with
`uv run python scripts/record_review.py inspect --targets <targets.yaml>`.
Include the schema, source tables and seeders inspected with `--input`.

Use `kind: batch` and `scope.coverage: sampled` unless the entire declared
population was actually read. Persist the eligible population denominator,
PER, the actual random seed, axis/category strata, per-cell population and
sample counts, exact reviewed IDs, exclusions and limits. Use evidence-linked
assessment dimensions for axis/category/source, and metrics with units and
denominators for cell counts. Reading one record per cell is not full-corpus
coverage. Retain partial coverage when selected files could not be assessed.

For each selected record retain A1-A9 assessments, then B1-B6 set assessments
where applicable. Preserve the rule IDs on findings; identify the maintained
seeder/transform owning systemic defects and propose its acceptance checks.
Summarize clean/flagged categories, systemic blast radius, individual defects,
and unresolved granularity/coherence decisions within the declared sample.

Severity: **blocker** (schema/identity broken, instance-as-class, wrong axis) ·
**major** (wrong category, empty/boilerplate definition, missing required
representation, systemic seeder defect) · **minor** (style, thin grounding,
provenance nit). Validate and save the completed content with
`uv run python scripts/record_review.py validate <review.yaml>` and
`uv run python scripts/record_review.py save --content <review.yaml>`.
The saver creates `reviews/structured/<timestamp>-<slug>/review.yaml` and its
derived `review.md`. Link both in the final response. Session-only output is
not a completed review; unavailable required checks require an explicit
partial/blocked observation, not an unsupported passing verdict.

## Best practices

1. **Read the whole file** before judging — a thin projection hides the definition
   and groundings.
2. **Fix at the seeder, re-seed** — like `merge-traits` / `review-source-categories`,
   a flag repeated across the five is a seeder bug, not 5 record edits.
3. **Same seed to re-check** — after a fix, re-run with the same `random.seed` and
   confirm the flagged records now pass.
4. **This is the content gate; run the schema + footprint gates too** —
   `just validate-all` (schema) and `review-source-categories` (footprint) catch
   what this doesn't, and vice-versa.
5. **A merge/relation candidate is out of scope here** — hand equivalence/containment
   to the [[merge-within-axis]] / [[merge-traits]] skills; this skill judges whether
   each record is *individually* sound.
