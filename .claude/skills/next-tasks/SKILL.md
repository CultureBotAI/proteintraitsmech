---
name: next-tasks
description: Assess and maintain the ProteinTraitsMech backlog. Reconciles NEXT_TASKS.md against what actually shipped (merged PRs, git log, open issues/PRs), separates genuinely-pending actionable work from done/stale/upstream-blocked items, surfaces a short prioritized menu with a recommendation, and — when asked — picks one up. Also the maintenance path for NEXT_TASKS.md itself — marking done items, adding new deferrals, bumping the reconcile date, and keeping cross-Mech items in sync. Use whenever the user asks "next tasks", "what's next", "is the backlog current", or after finishing a work thread.
category: workflow
requires_database: false
requires_internet: false
version: 1.0.0
---

# Next Tasks (backlog assessment + maintenance)

## Overview

**Purpose**: answer "what should I work on next?" *accurately*, and keep
`NEXT_TASKS.md` honest. The backlog drifts — items marked "pending" get shipped
in PRs, whole new threads never get logged, and some items are upstream-blocked
and will never be actionable here. This skill reconciles the written backlog
against reality, then produces a short, prioritized, *actionable* menu.

**Always reconcile before recommending** — never read `NEXT_TASKS.md` and relay
it verbatim. This repo's own backlog has needed exactly this correction before:
a prior reconcile note's every headline figure (draft counts, bucket sizes) was
stale by the time it was next read, because the corpus had moved under it. See
the "ARO draft backlog" block at the top of `NEXT_TASKS.md` for what "measured,
not assumed" looks like in practice here.

**When to use**: the user says "next tasks" / "what's next" / "anything left?",
asks whether the backlog is current, or you've just closed a work thread.

**When NOT to use**: to bring in a brand-new external data source — that's
`ingest-source` (which composes `data-sources`, `merge-traits`, and
`edison-deep-research`). This skill works the *existing* backlog.

## Workflow

### Step 1 — Reconcile

```bash
sed -n '1,400p' NEXT_TASKS.md
git log --oneline -20
gh pr list --state merged --limit 20 --json number,title,mergedAt \
  -q '.[] | "\(.number)\t\(.mergedAt[:10])\t\(.title)"'
gh pr list  --state open  --limit 20 2>/dev/null | head
gh issue list --state open --limit 30 2>/dev/null | head -30
```

For each pending item: *is its deliverable already in a merged PR or in the
code?* If yes → DONE. Spot-check any slot/recipe/file the item names before
trusting it (`grep -rl <slot> src/proteintraitsmech/schema/`) — backlog notes
cite things that were later renamed.

ProteinTraitsMech-specific traps when judging "done":

- **Measure, don't trust a stale count.** The corpus is ~430K trait records
  (`data/traits/`), and prior backlog notes have cited draft/bucket counts that
  were wrong by 2–20x by the time they were re-read. Recompute the actual
  number (e.g. via the audit recipe the item names) before reporting progress
  or declaring a bucket exhausted — do not relay a written figure as current.
- **Warn-mode / advisory gates hide residue.** Some `audit-*`/`validate-*`
  recipes report counts without failing the build. A green CI run is not
  evidence of zero findings — read the count the recipe prints, not just its
  exit code.
- **Research output is not curated content.** Files under `research/` (Edison
  or Codex deep-research reports) are *inputs*. An item is only DONE when
  DOI/PMID-backed claims have actually been applied to the `ProteinTraitRecord`
  YAML, not when a report merely exists.
- **`research/traits/**` is tracked, not gitignored.** Unlike some sibling
  Mechs where `research/` is scratch, here it holds real curation deliverables
  under git. A `rm -rf reports research` cleanup habit safe in another repo
  can silently delete committed work here. Always run `git status --short`
  before staging/committing and before any destructive cleanup command.

### Step 2 — Present the menu

- one line per PENDING & actionable item, ranked by value;
- call out what's newly DONE and what's UPSTREAM-BLOCKED (so gaps are explained);
- **recommend one** — usually the item that continues the active thread, is
  fully specified, or unblocks the most downstream work.

Use `AskUserQuestion` only when the directions genuinely diverge; otherwise
recommend and proceed on confirmation.

### Step 3 — Maintain NEXT_TASKS.md (every invocation, even if only bookkeeping)

- Mark shipped items **DONE (YYYY-MM-DD, PR #NNN)** in place, or move them out.
- Add unlogged threads as their own `##` section with cold-start context
  (what / why / next, PRs, key ids/paths).
- Convert relative dates to **absolute**; bump `Last reconciled:` to today.
- For **cross-Mech** items (kept in sync with CultureMech / MIM / CommunityMech
  / TraitMech), flag divergence — but do not edit sibling repos unless asked.

Commit the reconciliation. Doc-only changes may show "no checks reported" on
the path-filtered `validate-strict` workflow — that's `MERGEABLE`/`CLEAN`, not
a failure; `checks` (lint, `audit-schema`, `audit-writers`,
`validate-internal-id-labels`, `test`) still runs on every PR regardless.

### Step 4 — Pick it up (only if the user says to)

Hand off to the right skill, then drive it the usual way: branch → implement →
`just lint` / the targeted `audit-*`/`validate-*` recipe → PR → watch CI →
merge → sync main. Re-run Step 3 to record the new state.

## CI gates (what "green" actually means here)

From `.github/workflows/`:

- **`checks`** (unfiltered, every PR): `just lint`, `just audit-schema`,
  `just audit-writers`, `just validate-internal-id-labels`, `just test`. All
  read only committed schema/data — none need `data/raw`.
- **`validate-strict`**: closed-schema validation (`validate_strict.py`) +
  causal-graph structural audit (`audit_causal_graphs.py`). Path-filtered to
  schema/`data/traits/**`/validator changes; scoped to changed files on a PR,
  full-corpus on push to `main`.
- **`history-and-vendored`**: two sparse-checkout, curl+diff-only gates (no
  `uv`/Python) — `validate-history` and `vendored-sync` (the drift check
  against `CultureBotAI/CultureMech@<scripts/.vendored_canon_ref>`). Fast by
  design; the repo is ~431K files and ~768MB, essentially all `data/traits/`,
  and neither job reads a record.
- **`pages`**: publishes docs; not a correctness gate.

Recipes with no workflow behind them (`audit-*`/`validate-*` variants not
listed above) run locally only — a green PR is no evidence they pass. Run them
yourself if an item claims otherwise.

## Conventions this skill enforces

- **Reconcile-before-relay**: the file is a starting point, not ground truth.
- **Honest classification**: don't recommend upstream-blocked items; don't hide
  them either.
- **Every invocation updates the file** (at minimum the reconcile date).
- **Absolute dates**, PR numbers on done items, cold-start context on new items.

## Notes & limitations

- `scripts/check_vendored_sync.sh` diffs this repo's copy of the shared
  id-label validator files against `CultureBotAI/CultureMech@<the pinned ref
  in scripts/.vendored_canon_ref>`. To propagate a hub-side fix here: land it
  in CultureMech first, merge, then bump the ref in this repo.
- This repo joined the vendored-sync fleet later than the original three
  spokes (CultureMech#298) — some hub-side conventions assume a fleet of four
  and may need a fifth-repo update; check before trusting a cross-Mech count.
- Without `gh` or a network, reconcile from `git log` alone and say so.

## Related

- `ingest-source`, `data-sources`, `merge-traits`, `edison-deep-research` —
  bring in *new* sources/traits (outside this skill).
- `audit-schema-gaps` equivalents here are the `audit-*` justfile recipes
  (`audit-schema`, `audit-graphs`, `audit-writers`, `audit-roles`,
  `audit-reproducible`, ...) — the tools a chosen backlog item is usually
  handed off to.

## Related files

- `NEXT_TASKS.md` — the backlog this skill reads and maintains.
