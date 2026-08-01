---
name: merge-traits
description: Use this skill to detect and consolidate equivalent ProteinTraitRecords — when two or more records denote the same trait and should become one. It makes UNEQUIVOCAL, DETERMINISTIC "Trait X = Trait Y (mergeable)" statements from hard identity rules, and separately lists related-but-not-equal review candidates that need a curator. Covers the rules, the analysis script, target selection, the merge procedure, and post-merge validation. Trigger when asked to deduplicate traits, find duplicate/equivalent records, assert trait equivalence, or merge records.
---

# Merge Traits Skill

## Overview

ProteinTraitsMech is a large seeded catalog (~70k `ProteinTraitRecord` YAMLs)
drawn from many sources (PROSITE, TED, ECOD, UniProtKB, PSI-MOD, M-CSA,
DisProt, PSI-MI, PATO, METPO). Seeders are path-idempotent, so exact
duplicates are rare — but they do occur when one source term is routed to two
directories, and different sources describe overlapping concepts.

This skill answers one question deterministically: **which records are the same
trait and can be merged into one?** It draws a hard line between two tiers:

- **MERGE (unequivocal).** Emitted as `Trait X = Trait Y`. Safe to auto-merge.
- **REVIEW (candidate).** Related, but NOT asserted equal. A curator decides.

> **Axis-specific candidates:** the universal R1/R2 identity rules here
> under-cover, because "same trait" differs per axis (fold TM-score vs EC/Rhea
> anchor vs same-region overlap). To generate axis-appropriate candidate edges —
> STRUCTURE folds, FUNCTION anchors, SEQUENCE member/region — use the companion
> **`merge-within-axis`** skill, then bring its MERGE-tier edges back to the
> procedure below.

**Key principle — in this corpus, `xrefs` are associative, not identity
assertions.** A PROSITE ProRule cross-references the PATTERN it is built on; an
N-glycosylation pattern cross-references the `MOD:` term it flags; ~2,700 motif
records all ground to the generic `SO:0001067` ("polypeptide_region"). So
"shares an xref" or "same label" does **not** mean "same trait". Only exact
identity signals qualify for MERGE. This is the analog of MediaIngredientMech's
"same CHEBI → MUST merge; name similarity → flag for review" — recalibrated to
what is actually unequivocal here.

---

## The rules

The **NEVER** guards — different `trait_axis`, different `trait_category`, or two
different values in the same identity namespace — apply to **R2 and the review
rules**. **R1 is exempt**: an identical `identifier` is *definitional* identity
(a source CURIE names exactly one entity), which outranks categorization. A same-
identifier hit that spans two categories is not two traits — it is one entity
mis-routed into two directories, and the merge consolidates it into the more
specific category (e.g. the PROSITE ProRule `PRU00498` existed as both a generic
`SEQ_MOTIF` in `prorule/` and a `SEQ_GLYCOSYLATION_SITE`; the glycosylation
record is kept, the generic copy folded in). A ProRule/pattern is a sequence
*signature*, not itself a specific trait, so the specific categorization is the
one worth keeping.

### MERGE — deterministic, emitted as "X = Y"

| Rule | Condition | Why it is unequivocal |
|------|-----------|-----------------------|
| **R1 EXACT_ID** | Two records carry the identical `identifier`. | Same source term seeded to two paths / imported twice — literally one entity. Exempt from the category guard (see above). |
| **R2 EXACT_PATTERN** | Byte-identical non-empty `sequence_pattern` AND identical `(axis, category)`. | The same sequence signature expressed twice. |

### REVIEW — related, NOT auto-merged

| Rule | Condition | Why it is only a candidate |
|------|-----------|----------------------------|
| **C1 XREF_IDENTITY** | One record's source-anchored `identifier` ∈ the other's `xrefs`, same `(axis, category)`. | Usually a pattern/rule pair — related, often two legitimately distinct records. |
| **C2 SHARED_ANCHOR** | Both cite the same *specific* identity xref (EC/RHEA/MOD/Pfam/InterPro/CATH/SCOP/ECOD/PROSITE/HAMAP) shared by ≤ `--anchor-cap` records, same `(axis, category)`. | Typically a PROSITE pattern+profile for one family — the same signature via two detection methods, but the repo keeps both on purpose. |
| **C3 SAME_LABEL_XSRC** | Identical normalized label across **different** sources, same `(axis, category)`. | A cross-source name collision worth a look. (Intra-source label reuse is excluded — thousands of distinct TED/ECOD folds share generic names.) |

Full rationale, the false-positive catalog that motivated each guard, and the
identity-namespace list are in
[`reference/rules-and-evidence.md`](reference/rules-and-evidence.md).

---

## Running the analysis

```bash
just build-docs                          # REQUIRED first — the analyzer reads
                                         # docs/data/records.<AXIS>.json shards
just analyze-merges                      # dry-run: prints tiers + writes plan
just analyze-merges --show-review        # also list every review candidate
just analyze-merges --anchor-cap 3       # tighten the C2 generic-grounding cut
just analyze-merges --apply              # execute the MERGE groups only
```

The dry run writes `data/analysis/trait_merge_plan.yaml` — one entry per merge
group (statement, rules, evidence, chosen target, members) and the full review
list. **Always read the plan before `--apply`.**

Catalog status (2026-07): the initial **4 MERGE groups** (all R1 — PROSITE
ProRules routed into both a PTM-subtype dir and `prorule/`, plus `PS00654` in
two dirs) have been **applied** (corpus 69,684 → 69,680), so a fresh run now
reports 0 MERGE groups. **675 review candidates** (6 C1 + 669 C2) remain, by
design untouched.

---

## Merge procedure (`--apply`)

`--apply` executes **MERGE groups only** — review candidates are never touched.
For each group it picks a deterministic target, folds the losers in, and leaves
an audit trail:

1. **Target selection** (deterministic, reproducible): highest `mapping_status`
   (REVIEWED > PROPOSED > SEEDED) → source-anchored id over `proteintraitsmech:`
   → richest (most xrefs + parents) → lexicographically smallest id, then path.
2. **Fold in** each loser: union `xrefs` and `parent_traits`; add the loser's
   `label` and `synonyms` to the target's `synonyms`.
3. **Audit**: append a `curation_history` CurationEvent to the target
   (`action: "merged <ids>"`, `llm_assisted: true`).
4. **Dispose of the loser**:
   - **R1 (same identifier):** delete the redundant file.
   - **R2 (different ids):** set the loser `mapping_status: DEPRECATED`, add an
     `xref` to the target, and append a deprecation CurationEvent — retained for
     traceability per the schema's DEPRECATED semantics.

The exact field-merge logic and conflict handling are in
[`reference/merge-procedure.md`](reference/merge-procedure.md).

---

## Best practices

1. **`just build-docs` first**, then analyze — the analyzer reads the shards, so
   a stale index yields stale statements.
2. **Dry-run, read the plan, then `--apply`.** Only the MERGE tier is executed.
3. **Never promote a review candidate to a merge by editing the plan.** If a C1–
   C3 pair really is one trait, encode that as a schema/seeder fix (or add the
   identity signal) so the deterministic rule fires — don't merge by hand.
4. **Re-validate after applying:** `just build-docs && just validate-all`, and
   confirm the record total dropped by exactly the number of R1 losers removed.
5. **Treat a growing MERGE set as a seeder bug.** Repeated R1 hits mean a seeder
   is emitting the same identifier to two paths — fix the seeder rather than
   merging after the fact.

---

## Reference files

| File | Contents |
|------|----------|
| [`reference/rules-and-evidence.md`](reference/rules-and-evidence.md) | Each rule in depth, the identity-namespace list, the NEVER guards, and the real false positives (associative xrefs, generic groundings, intra-source label reuse) that justify why only R1/R2 are unequivocal. |
| [`reference/merge-procedure.md`](reference/merge-procedure.md) | Target-selection precedence, field-by-field merge semantics, R1-vs-R2 disposal, the CurationEvent shape, and the post-merge validation checklist. |
