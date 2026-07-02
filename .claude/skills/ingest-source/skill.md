---
name: ingest-source
description: End-to-end workflow to add a NEW external data source to ProteinTraitsMech — download it, analyze it, write a seeder that emits ProteinTraitRecord YAMLs, validate with linkml-validate and fix errors until 100% pass, dedup/merge against the existing corpus, and wire up the docs. Trigger when asked to "ingest / seed / add <source>", "bring in <database>", or to turn a candidate in download.yaml into seeded records. Composes the data-sources, merge-traits, and edison-deep-research skills.
---

# Ingest a New Source

The repeatable pipeline for turning an external resource into validated,
deduplicated `ProteinTraitRecord` YAMLs. Each `scripts/seed_*.py` is one product
of this workflow; follow the same shape.

## 0. Decide scope (analyze first)

- **Register it** in `download.yaml` (see [`data-sources`](../data-sources/skill.md)):
  exact bulk `url`, licence (flag NC/ND/login), status `candidate`. If it came
  from research, it is already there (see the `edison-deep-research` rounds).
- **Download** the bulk file(s) to `data/raw/<source>/` (gitignored; add a
  `fetch-<source>` recipe + a `.gitignore` line).
- **Inspect**: format, entry types, size, and — critically — **what maps to a
  `trait_axis` + `trait_category`**. Only ingest rows that are protein
  sequence/structure/function/evolution traits with a real definition.
- **Check redundancy**: does an already-seeded source cover this? (e.g. Pfam ⊂
  InterPro; NCBIfam/CDD are InterPro members.) Prefer additive subsets; capture
  the relationship as an xref rather than duplicating.
- **Pick groundings**: reuse the `*2go` / mapping files (interpro2go, ec2go,
  pfam2go, …) to attach GO/EC/etc. xrefs. Register each mapping file in
  download.yaml.
- If the source needs a `trait_category` or `trait_axis` that doesn't exist,
  add it to the schema enum FIRST (see step 3's schema note) — the closed-mode
  validator reads `proteintraitsmech.yaml` directly.

## 1. Write the seeder (`scripts/seed_<source>.py`)

Mirror an existing seeder (`seed_interpro.py` for hierarchical DBs,
`seed_traitontomap.py` for tabular, `seed_obo.py` for OBO, `seed_stability.py`
for curated). Non-negotiables:

- **stdlib-only**, hand-formatted YAML (reuse `yaml_escape` / folded-scalar
  helpers); no PyYAML dependency for writing.
- **identifier**: source-anchored CURIE when possible (`Pfam:PF00069`,
  `EC:2.7.11.1`); else `proteintraitsmech:<SLUG>`.
- emit `label`, folded `definition`, `definition_source`, `trait_axis`,
  `trait_category`, `term_kind: CLASS`, `mapping_status: SEEDED`,
  `parent_traits` (source hierarchy), `xrefs` (from mappings), `license`.
- **idempotent** (skip existing by path), **dry-run by default**, `--apply` to
  write, `--force` to overwrite.
- one subdir per source: `data/traits/<axis-dir>/<category-dir>/<source>/`.

## 2. Validate until it passes — the loop that must not be skipped

```bash
just validate-all data/traits/<...>/<source>       # closed-mode linkml-validate
```

Rely on **linkml-validate** (closed mode: unknown slots/enum values are errors).
Iterate until **N/N pass**:

- **enum error** (bad `trait_category`/`trait_axis`) → the value must exist in
  `proteintraitsmech.yaml`; either fix the mapping or add the permissible value
  to the schema (then `just gen-schema`).
- **pattern error** (xref/identifier) → xrefs must match
  `^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$`; drop or fix malformed CURIEs.
- **YAML parse error** → fix escaping (colons, quotes, leading `-`/`?`) in the
  hand-formatted output, not the data.
- transient batch failures re-validate clean — isolate the batch
  (`just validate-all <onefile>`) before assuming a real error.

Do NOT proceed to commit while any record fails. Re-run `--apply --force` after
each seeder fix.

## 3. Dedup / merge against the corpus

A new source almost always overlaps existing ones. Run the
[`merge-traits`](../merge-traits/skill.md) analyzer after `just build-docs`:

```bash
just build-docs && just analyze-merges          # then --apply for the MERGE tier
```

- **R1 EXACT_ID** catches a source re-emitting an identifier already present →
  consolidate.
- Cross-source equivalence that is *unequivocal by a mapping* (e.g. Pfam↔InterPro
  via **pfam2interpro**, or two sources sharing an EC) is a **derivative merge
  rule**: rather than lowering merge-traits' bar, encode the mapping as an xref
  on ingest so the records are linked, and let a curator decide true merges. If
  the mapping makes them the *same* trait, add the mapping-target as the
  `identifier` (so R1 fires) instead of minting a parallel id.
- Review candidates (C1–C3) are never auto-merged.

## 4. Wire up + verify

- `build_docs_index.py` `infer_source`: add the identifier-prefix → source label.
- `download.yaml`: flip the source's `status` to `seeded`, add `seeder:` and any
  mapping-file blocks; `just sources-check` must pass.
- `justfile`: `fetch-<source>` + `seed-<source>` recipes.
- `just build-docs`; update `docs/index.md` (stat cards, source table row,
  category table — regenerate rows from `facets.json`, verify the category sum
  equals the total) and the README seeds table.
- **Final gate**: `just validate-all` over the whole corpus → N/N pass.

## 5. Commit

One commit per source, after the full gate passes. Message: source, licence,
count delta, category, groundings, and any redundancy/scoping decision. Do not
commit `data/raw/` (gitignored). Push only when asked.

## Checklist

- [ ] registered in download.yaml with verified licence
- [ ] fetched to data/raw/<source>/ (gitignored) + fetch recipe
- [ ] scope decided (axis/category, subset, redundancy, groundings)
- [ ] seeder written (stdlib, idempotent, dry-run default)
- [ ] `just validate-all <dir>` → N/N (schema enum added if needed)
- [ ] `just analyze-merges` reviewed; unequivocal dups consolidated
- [ ] infer_source + recipes + gitignore + download.yaml seeded
- [ ] build-docs; index.md + README updated + reconciled
- [ ] `just validate-all` whole corpus → N/N
- [ ] committed
