---
name: data-sources
description: Use this skill to create, review, maintain, and update the data-source registry at data/sources.yaml — the single authoritative list of every external resource ProteinTraitsMech seeds from, is considering, or has rejected (name, description, download link, licence, status, target trait_categories, hierarchy). Trigger when adding/evaluating a data source, recording a seeder's provenance, auditing licences, promoting a candidate to seeded, or keeping the registry in sync with the seeders, README, and the edison-deep-research rounds.
---

# Data Sources Registry

`data/sources.yaml` is the one place that answers "where did our data come from,
can we redistribute it, and what's next." Keep it accurate — the whole corpus is
CC0, so a mislabelled licence is a real problem.

## The file

A top-level `sources:` list. Each entry:

| field | req | notes |
|-------|-----|-------|
| `key` | ✓ | short unique slug (matches CURIE prefix lowercased where sensible) |
| `name` | ✓ | display name |
| `prefix` | | CURIE prefix used in identifiers (e.g. `PROSITE`, `MOD`) |
| `status` | ✓ | `seeded` \| `candidate` \| `deferred` \| `rejected` |
| `description` | ✓ | one line: what traits it supplies |
| `homepage` | ✓ | canonical site |
| `download` | ✓ | exact bulk-download URL/endpoint (+ the specific files in a comment) |
| `license` | ✓ | precise enough to judge CC0-redistribution; flag NC/ND/login |
| `license_url` | | link to the licence terms |
| `hierarchy` | | `true` / `false` / short description of the levels |
| `trait_categories` | | list of target `trait_category` values |
| `added_round` | | which edison-deep-research round surfaced it |
| `priority` | | for candidates: seed order |
| `seeder` | | `scripts/seed_*.py` (required when `status: seeded`) |
| `notes` | | caveats, scoping decisions, redundancy warnings |

## Operations

**Create** (add a source) — usually from an `edison-deep-research` round. Fill
every required field; put the exact download files in a comment on `download`;
set `status: candidate` (or `rejected` with a `notes` reason). Verify the
licence from the source's own terms page, not a search snippet.

**Review** (audit) — run `just sources-check`. It enforces required fields,
the `status` enum, unique keys, that every `seeded` source has an existing
seeder script, flags orphan seeders (a `seed_*.py` with no registry entry), and
warns on NC/ND/login licences. Also periodically re-verify download URLs still
resolve and licences haven't changed.

**Maintain** (keep in sync) — the registry must agree with three things:
1. the **seeders** — every `scripts/seed_*.py` has an entry; `seeder:` points to
   the real file (checked by `just sources-check`);
2. the **README seeds table** — same sources, same counts direction;
3. the **research rounds** — anything adopted/deferred/rejected there is
   reflected here with the matching `added_round`.

**Update** (status transitions) — when a candidate gets seeded: flip
`status: candidate → seeded`, add `seeder:`, drop `priority`, and add the entry
to the README seeds table. When re-evaluating: move to `deferred`/`rejected`
with a dated `notes` rationale. Never delete a `rejected` entry — the reason it
was rejected is the value.

## Rules

- **Licence honesty first.** If a source is NonCommercial / NoDerivatives /
  login-walled, it stays flagged even if already seeded (see `prosite`:
  CC BY-NC-ND). Surface it; don't silently redistribute.
- **One row per source of truth.** Member/aggregated DBs (e.g. NCBIfam, CDD are
  InterPro members) get their own row but note the relationship.
- **Download link must be the bulk endpoint**, not the homepage — with the
  specific file names in a comment (the seeder needs them).
- After any edit, run `just sources-check` and fix errors before committing.

## Related

- Populated by [`edison-deep-research`](../edison-deep-research/skill.md) rounds
  (`research/protein-trait-sources-round*.md`).
- Consumed by the seeders (`scripts/seed_*.py`) and the README seeds table.
