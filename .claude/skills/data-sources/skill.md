---
name: data-sources
description: Use this skill to create, review, maintain, and update download.yaml — the single authoritative download manifest + source catalogue for ProteinTraitsMech (kghub-downloader format, as in KG-Microbe). Each block records the download URL plus name, description, licence, status, target trait_categories, hierarchy, and seeder. Trigger when adding/evaluating a data source, recording a seeder's provenance, auditing licences, promoting a candidate to seeded, adding mapping files (e.g. interpro2go), or keeping the manifest in sync with the seeders, README, and the edison-deep-research rounds.

---

# Data Sources — download.yaml

`download.yaml` (repo root) is both the **download manifest** (kghub-downloader
format, `run.py download`-compatible, as in KG-Microbe) and the **source
catalogue**. It answers "where did our data come from, can we redistribute it,
and what's next." The whole corpus is CC0, so a mislabelled licence is a real
problem. (It replaced the older `data/sources.yaml` registry.)

## Format

A flat YAML list of blocks. `url` is the only field kghub-downloader requires;
everything else is metadata our tooling uses. One block per downloadable FILE
(a source with several files — e.g. InterPro's xml + tree + entry.list +
interpro2go — gets several blocks sharing `source:`).

| field | notes |
|-------|-------|
| `url` | **required** — the exact bulk-download URL/endpoint |
| `local_name` | optional download filename (avoid collisions; may include a subdir) |
| `name` | display name (on the source's primary block) |
| `source` | short key grouping a source's blocks (e.g. `interpro`) |
| `license` / `license_url` | precise enough to judge CC0 compat; append ` — FLAGGED` for NC/ND/login |
| `status` | `seeded` \| `candidate` \| `deferred` \| `rejected` (on the primary block) |
| `hierarchy` | `true` / `false` / short description |
| `trait_categories` | list of target `trait_category` values |
| `seeder` | `scripts/seed_*.py` — required for a seeded source |
| `tag` | e.g. `api`, `internal` — selective-download hint |
| `note` | caveats, scoping decisions, redundancy warnings |

Sections are comment-delimited by status (SEEDED / CANDIDATE / DEFERRED /
REJECTED).

## Operations

**Create** (add a source) — usually from an `edison-deep-research` round. Add a
block with the exact download `url`; fill `name`/`source`/`license`/`status` and,
for multi-file sources, one block per file sharing `source`. Verify the licence
from the source's own terms page, not a search snippet.

**Review** (audit) — `just sources-check` (scripts/check_sources.py): every
block has a `url`, `status` values are valid, every seeded source names an
existing `seeder`, orphan seeders are flagged, and NC/ND/login licences warn.
Periodically re-verify URLs still resolve and licences haven't changed.

**Maintain** (sync) — the manifest must agree with:
1. the **seeders** — every `scripts/seed_*.py` is referenced by a `seeder:`;
2. the **README seeds table** — same sources;
3. the **research rounds** — adopted/deferred/rejected there reflected here.

**Update** (transitions) — when a candidate is seeded: flip its `status` to
`seeded`, add `seeder:`, and add its file blocks + a README row. When
re-evaluating: move to `deferred`/`rejected` with a dated `note`. Never delete a
`rejected` entry — the reason is the value.

## Rules

- **Licence honesty first.** NonCommercial / NoDerivatives / login-walled stays
  ` — FLAGGED` even if already seeded (e.g. PROSITE is CC BY-NC-ND). Surface it.
- **`url` = the bulk endpoint**, not the homepage. API-only sources get `tag: api`.
- **Member/aggregated DBs** (NCBIfam, CDD are InterPro members) get their own
  blocks but note the relationship.
- After any edit, `just sources-check` and fix errors before committing.

## Related

- Populated by [`edison-deep-research`](../edison-deep-research/skill.md) rounds
  (`research/protein-trait-sources-round*.md`).
- Consumed by the seeders (`scripts/seed_*.py`) and the README seeds table.
