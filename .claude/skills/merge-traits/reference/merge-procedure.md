# Merge procedure (`--apply`)

`scripts/analyze_trait_equivalence.py --apply` executes the **MERGE tier only**.
Review candidates (C1–C3) are never modified. This file documents exactly what
happens to each record so the result is predictable and auditable.

## 1. Target selection (deterministic)

Within a merge group, the surviving record ("target") is chosen by this ordered
key — every tiebreak is deterministic, so the same input always yields the same
target:

1. **Highest `mapping_status`** — REVIEWED (3) > PROPOSED (2) > SEEDED (1) >
   DEPRECATED (0). The most-curated record wins.
2. **Source-anchored over curator-minted** — an id that is *not*
   `proteintraitsmech:*` is preferred (keep the authoritative CURIE).
3. **Richest** — most `xrefs` + `parent_traits` (least information lost).
4. **Lexicographically smallest** identifier, then path — a pure stable tiebreak.

## 2. Folding losers into the target

For each non-target member:

| Field | Action |
|-------|--------|
| `xrefs` | union into the target (order-preserving, de-duplicated) |
| `parent_traits` | union into the target |
| `synonyms` | the loser's `label` is added as a `RELATED_SYNONYM`; the loser's own `synonyms` are merged, skipping any whose text equals the target label |
| `curation_history` | a CurationEvent is appended to the target (see below) |

Scalar fields on the target (`label`, `definition`, `trait_axis`,
`trait_category`, `sequence_pattern`, `license`) are **left untouched** — the
target was chosen precisely because it is the authoritative record.

## 3. Disposing of the loser

- **R1 (EXACT_ID — loser shares the target's identifier):** the loser file is
  **deleted**. Two files with the same identifier cannot both exist; all unique
  field content was folded into the target in step 2.
- **R2 (loser has a different identifier):** the loser file is **retained but
  deprecated** — `mapping_status: DEPRECATED`, an `xref` to the target
  identifier is added, and a deprecation CurationEvent is appended. This matches
  the schema's DEPRECATED semantics ("retained for traceability but flagged as
  superseded") so downstream references to the old id still resolve.

## 4. CurationEvent shape

Appended to `curation_history` (append-only). Matches the schema `CurationEvent`
class:

```yaml
curation_history:
  - timestamp: '2026-07-02T14:59:05+00:00'   # UTC, ISO-8601, required
    curator: merge-traits skill
    action: merged PROSITE:PS00654           # or "deprecated: merged into <id>"
    llm_assisted: true
```

## 5. Post-merge validation checklist

```bash
just build-docs                 # rebuild shards + facets
just validate-all               # closed-mode LinkML gate over the whole corpus
just analyze-merges             # should now report the merged groups as gone
```

Then confirm:

- The record total dropped by **exactly** the number of R1 losers deleted (R2
  losers are deprecated, not removed, so they still count).
- Each merge target validates and carries the new synonyms + CurationEvent.
- No new duplicate identifiers were introduced (re-running the analyzer shows
  the previously-flagged groups are gone and no new ones appeared).

## Reverting a mistaken apply

Because merges only touch tracked files under `data/traits/`, a bad run is fully
reversible before commit:

```bash
git checkout -- data/traits        # restore deleted losers + revert target edits
```
