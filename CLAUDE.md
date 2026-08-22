# CLAUDE.md

Operational guidance for agents working in ProteinTraitsMech. Mutable corpus metrics do
not belong here; run `just corpus-stats` for current machine-readable counts.

## Purpose and invariant

ProteinTraitsMech is a LinkML-governed knowledge base of protein trait classes. The
deliverable is one `ProteinTraitRecord` YAML per file under `data/traits/`, with
provenance, optional evidence, and optional evidence-bearing causal graphs.

The schema at `src/proteintraitsmech/schema/proteintraitsmech.yaml` is authoritative.
Generated models, validators, writers, records, and documentation must follow it. The
axis follows the representation used to define a trait, not merely its biology.

The five paths and axes are:

| Path | `trait_axis` | Category prefix |
| --- | --- | --- |
| `data/traits/sequence/` | `SEQUENCE` | `SEQ_*` |
| `data/traits/structure/` | `STRUCTURE` | `STRUCT_*` |
| `data/traits/sequence_structure/` | `SEQUENCE_STRUCTURE` | `MIXED_*` |
| `data/traits/function/` | `FUNCTION` | `FUNC_*` |
| `data/traits/evolution/` | `EVOLUTION` | `EVOL_*` |

## Safety rules

- Files named by `scripts/check_vendored_sync.sh` are byte-identical fleet assets. Change
  them in the canonical hub, then bump and re-vendor; do not patch them locally.
- Record writes must use an audited route: a seeder through `record_io.write_record`, a
  registered in-place editor, or a declared bypass. Run `just audit-writers` after writer
  changes.
- `data/raw/` contains gitignored, regenerable upstream downloads. Never commit fetched
  releases. Register sources and fetch routes in `download.yaml` and `justfile`. Fixed
  bulk-file recipes must use `scripts/fetch_source.py`, which validates a temporary file,
  atomically replaces the destination, and records a `.fetch.json` release sidecar.
- Seeders are dry-run by default and must be idempotent. They may use project dependencies;
  invoke them through their `just` recipe unless the recipe explicitly uses `python3`.
- `seed_uniprot.py` is a retired per-protein demonstration, not the supported class-level
  ingest route. Add real proteins as `canonical_examples` with
  `fetch_uniprot_examples.py`.
- Do not assume the root CC0 dedication overrides upstream terms. Preserve per-record
  provenance/license metadata, treat restrictive or missing terms as a release blocker,
  and escalate unresolved source dispositions under issue #517.
- Closed-mode validation rejects unknown fields. Change the schema first, regenerate as
  needed, then update writers and records.

## Common commands

```bash
just install
just corpus-stats                         # current JSON metrics; no Pages build required
just validate-all [path-or-glob]          # closed-mode record validation
just audit-schema
just audit-graphs [path]
just audit-text
just audit-prose
just audit-writers
just sources-check
just test
just lint
just build-docs                           # regenerate sharded browser data
just check-vendored-sync
just validate-history
```

`mapping_status` progresses `SEEDED → PROPOSED → REVIEWED → DEPRECATED`. Every
`CausalEdge` requires edge-level evidence. Prefer grounded CURIEs and source-backed
claims; do not upgrade status merely because a machine generated content.

## Task-to-skill router

| Task | Skill |
| --- | --- |
| Source registry/catalog work | [data-sources](.claude/skills/data-sources/SKILL.md) |
| Fetch an upstream release | [fetch-source](.claude/skills/fetch-source/SKILL.md) |
| Ingest a new source | [ingest-source](.claude/skills/ingest-source/SKILL.md) |
| Review source/category routing | [review-source-categories](.claude/skills/review-source-categories/SKILL.md) |
| Sample record quality | [review-record-samples](.claude/skills/review-record-samples/SKILL.md) |
| Research source candidates | [edison-deep-research](.claude/skills/edison-deep-research/SKILL.md) |
| Curate definitions | [edison-trait-definitions](.claude/skills/edison-trait-definitions/SKILL.md) |
| Curate mechanism graphs | [edison-causal-graphs](.claude/skills/edison-causal-graphs/SKILL.md) |
| Merge duplicates | [merge-traits](.claude/skills/merge-traits/SKILL.md) |
| Select within-axis equivalence | [merge-within-axis](.claude/skills/merge-within-axis/SKILL.md) |
| Review schema/hierarchy | [codex-schema-hierarchy-review](.claude/skills/codex-schema-hierarchy-review/SKILL.md) |
| Audit embedding fields | [embedding-field-audit](.claude/skills/embedding-field-audit/SKILL.md) |
| Measure Git/Pages scale | [scalability-check](.claude/skills/scalability-check/SKILL.md) |
| Full open-issue queue triage | [review-open-issues](.claude/skills/review-open-issues/SKILL.md) |

## Change-to-gate matrix

| Change | Required gates |
| --- | --- |
| Python/code | `just lint`, focused pytest, `just test`; writers also `just audit-writers` |
| Schema | `just audit-schema`, `just gen-schema`, focused tests, `just validate-all` |
| Trait records | scoped `just validate-all`, relevant audits, then full validation before merge |
| Causal graphs | record validation plus `just audit-graphs` |
| Documentation/browser | docs consistency tests and `just build-docs`; inspect generated-size impact |
| History | `just validate-history` |
| Source registry/fetching | `just sources-check`, license/provenance review, fetcher tests |
| Vendored foundation | upstream change, re-vendor, then `just check-vendored-sync` |

The browser loads lean record shards lazily from the active axis, category, source, and
status filters, then fetches a bucketed detail sidecar only when a detail view opens.
Rebuild docs after material record changes; do not describe the site as loading the entire
corpus at startup. Run `just audit-pages --site <built-site>` before deployment.

See [README.md](README.md) for the data model and workflows,
[prompts/README.md](prompts/README.md) for hand-off/review prompts, and run
`just corpus-stats` for current corpus and generated-artifact measurements.
