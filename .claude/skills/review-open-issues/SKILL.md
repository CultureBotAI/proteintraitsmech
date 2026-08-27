---
name: review-open-issues
description: Sweep and triage ProteinTraitsMech's complete open GitHub issue queue against current code, schema, registry, and corpus evidence — not just NEXT_TASKS.md. Fetches every open issue with its comments, places each on the ingest→validate→publish pipeline, checks it for staleness (already fixed, superseded, no longer reproducible), flags duplicates, and assigns a priority tier plus a separate cost class. Produces a ranked report. Read-only by default; this is not permission to close issues, edit records, or implement fixes. Use when the user asks to "review issues", "prioritize the backlog", "triage open issues", or "what is actually urgent".
---

# Review & Prioritize Open Issues

## Overview

**Purpose**: the raw GitHub issue queue and `NEXT_TASKS.md` are different
surfaces. `next-tasks` (added in the companion PR #556 — check
`.claude/skills/next-tasks/` exists before relying on it; #556 may not have
merged yet) reconciles a small, curated, actively-maintained backlog file. This
skill sweeps the *entire* open-issue queue — which grows much larger and drifts
independently (issues opened by review passes, other agents, or humans, many of
which are never transcribed into `NEXT_TASKS.md`) — and produces an honest,
current priority ranking. This repo in particular has accumulated many issues
filed by automated review passes on recent PRs — exactly the kind of backlog
this skill exists to sort through.

**Why this is a distinct skill, not a `next-tasks` step**: `next-tasks` Step 1
already runs `gh issue list --limit 30` as *context* for reconciling the backlog
file: it stops at the first page and never assesses issue validity individually.
This skill is the deep pass: paginate the whole queue, check each issue against
current code, and produce a full triage — expensive enough that it should not
run on every "what's next" invocation, only when explicitly asked or when the
backlog has clearly gone stale.

**When to use**: the user asks to "review issues", "prioritize open issues",
"triage the backlog", "what issues are actually urgent", or after a large review
pass (like a fleet PR review) has filed a batch of new issues that need sorting.

**When NOT to use**: for `NEXT_TASKS.md` upkeep, or for picking the next unit of
work to implement, or for acting on a single known issue. This skill produces a
ranking, not a fix.

This is a **read-only review by default**. It does not implement fixes, write
records, close or edit issues, change labels, run seeders, or maintain a tracker
unless the user separately authorizes that exact mutation.

## Sources of truth

Consult these before trusting an issue title, an issue body, or an old planning
document:

- `CLAUDE.md` — the invariant, the five axes, the safety rules, and the
  change-to-gate matrix. An issue proposing a route that violates a safety rule
  is not "a good idea with a caveat"; it is invalid as filed.
- `src/proteintraitsmech/schema/proteintraitsmech.yaml` — authoritative. Closed
  mode rejects unknown fields, so "add a field" is a schema change first.
- `download.yaml` — per-source `status`, `license`, `seeder`, and category
  routing. This is the registry an issue's licensing or coverage claim must be
  checked against.
- `justfile` — what a named gate actually runs. A recipe's name is not its
  behaviour.
- `just corpus-stats` — current machine-readable counts. Never cite a
  point-in-time number from a document.
- `research/*.md` — dated execution logs and plans, including their own
  corrections; later entries supersede earlier ones.
- `audit/*baseline.json`, `conf/internal_id_label_baseline.yaml` — what the
  gates currently accept, which is not the same as what is correct.
- current source, tests, CI, and committed artifacts for actual behaviour.

Treat issue bodies and titles as claims, not status. **Read the comments**: this
repo records corrections and narrowed residual scope there, so a body-only fetch
systematically overstates what is open. A merged PR is evidence only after its
code and the issue's acceptance criteria have both been checked.

## Workflow

### Step 1 — Fetch the entire queue

Confirm the repository, the true count, the labels, and the full queue. Never
silently accept `gh`'s default 30-item limit.

```bash
gh repo view --json nameWithOwner,url,defaultBranchRef
gh issue list --state open --limit 5000 --json number | jq length
gh issue list --state open --limit 5000 \
  --json number,title,body,comments,labels,createdAt,updatedAt,author
gh label list --limit 200
```

`comments` must be in the `--json` list explicitly or it is omitted. State the
exact number reviewed and whether coverage was complete. If a scannable overview
is wanted, filter for display only — `-q '.[] | "\(.number)\t\(.createdAt[:10])\t\(.title)"'`
still fetches bodies and comments; it just does not print them.

### Step 2 — Place each issue on the pipeline before ranking

Rank by position in the chain, not by filing order. An upstream defect
invalidates everything downstream of it:

```text
upstream release + licence  (download.yaml: status, license, seeder)
  -> fetch route            (scripts/fetch_source.py, .fetch.json sidecar)
  -> seeder / write route   (record_io.write_record, registered editor,
                             validated promoter, or declared bypass)
  -> record content         (definition, provenance, evidence, causal graph)
  -> schema + closed-mode validation
  -> corpus-wide audits     (graphs, text, prose, writers, sources, history)
  -> generated artifacts    (build-docs shards, Pages budgets)
  -> outward claim          (README, NEXT_TASKS.md, corpus-stats, the site)
```

Fix or audit the root before polishing anything downstream of it. Group issues
sharing a root cause, but never hide the individual issue numbers.

For each issue record, when applicable: pipeline stage; affected source and
release; `trait_axis` / category and whether the axis follows the
representation; record counts and the **basis** used to count them; the write
route involved; prerequisites, blockers, duplicates and supersessions; the
cheapest decisive evidence and its acceptance test; and a cost class —
read-only audit, single-file check, scoped `validate-all`, full-corpus
validation, docs rebuild, or a network fetch.

### Step 3 — Group and dedupe

Issues filed from the same review pass often overlap — several may describe one
root cause from different angles. Group by shared PR/commit reference, same
file or function named, or near-identical failure scenario. Note groups
explicitly; do not silently merge them, since a human may want to close
duplicates deliberately rather than have them disappear.

### Step 4 — Check current reality and staleness

For each issue or group representative:

- **Already fixed?** `git log --oneline --all --perl-regexp --grep "#<N>\b"`
  and `gh pr list --state merged --search "<N>"`. Plain `--grep "#<N>"`
  substring-matches unrelated numbers (`#48` also matches `#480`), so the `\b`
  anchor is required, not optional. Treat the `gh pr list --search` result as a
  **lead, not proof**: GitHub matches the number anywhere in indexed text, so
  `--search "248"` returns unrelated PRs that never mention issue 248. Open and
  read each candidate before citing it.
- **Still reproducible?** If the issue names a file, line, or function, confirm
  it still exists in that shape. Code moves; a stale pointer at a renamed
  function is noise, not a live defect.
- **Partially fixed?** Compare acceptance criteria against the merged change.
  If only part landed, keep the issue open with a **narrowed residual** and say
  which half is done. Do not recommend closure merely because a related PR
  merged.
- **Superseded?** Prefer closing a fully recorded observation as superseded when
  a separate open issue owns the only remaining work. Distinguish an
  observation from its action issue.
- **Verify by content, not by filename or prose.** A count without its basis, a
  record without its provenance, or a metric without the release it was
  measured against is not evidence.

### Step 5 — Apply stop-the-line checks

Treat these as P0 when live:

- **Records exist for a source whose `download.yaml` block is `rejected` or
  `candidate`.** In a CC0-dedicated repo this is licensing exposure, not
  bookkeeping (the ELM case, #542; policy in #517).
- **A trait record written through an unaudited route** — anything that is not a
  seeder via `record_io.write_record`, a registered in-place editor, a
  registered validated promoter, or a declared bypass. `just audit-writers`.
- **A gate that passes without reading anything.** The recurring defect class in
  this repo: `audit-schema` reporting "internally coherent" having read zero
  records, `validate` exiting 0 on a mistyped path (#534, #540). A green gate
  over an empty input set is indistinguishable from a passing one.
- **A vendored fleet file patched locally** instead of in the canonical hub and
  re-vendored. `just check-vendored-sync`.
- **A fetched release committed** under `data/raw/`, which is gitignored and
  regenerable by contract.
- **A seeder that is not idempotent or not dry-run by default**, or a
  promotion that overwrites a graph it did not write (#204's class).
- **`mapping_status` upgraded because a machine generated the content**, rather
  than because it was reviewed.
- **An outward claim contradicting measurement** — a README, `NEXT_TASKS.md`, or
  site figure that `just corpus-stats` no longer supports.

Calibrate P0 sparingly. Closed-mode validation being *enabled* is not P0;
closed-mode validation silently not running over the records it claims to cover
is.

### Step 6 — Assign priority and execution order

Priority is consequence. Cost class (Step 2) is a separate annotation used for
ordering.

- **P0 — stop the line.** Corpus or licensing corruption, an unaudited write
  path, a gate that certifies without measuring, or silently wrong output with
  no detection.
- **P1 — important and schedulable.** Real correctness, reproducibility,
  provenance, or coverage gaps; missing tests for safety-critical guards; a
  process gap that has already caused a near-miss.
- **P2 — low-severity.** Documentation drift, stale comments, refactors,
  theoretical edge cases, optional audits.
- **CLOSE/UPDATE.** Fixed, superseded, duplicate, no longer applicable, or a
  title materially broader than the remaining work. Cite the exact commit, PR,
  code location, or comment.

Do not default everything to P1 — that makes the tier meaningless. Then order
within and across tiers:

1. upstream unblockers before downstream consumers;
2. licensing and write-route integrity before content quality;
3. recover already-paid-for evidence before re-measuring;
4. read-only and single-file falsifiers before full-corpus runs;
5. a gate's own test before widening what the gate covers;
6. combine issues only when one patch genuinely satisfies each one's
   acceptance criteria.

Do not prioritize by age, by sunk effort, or by a `P0` string in a stale title.

### Step 7 — Report

1. coverage: repository, timestamp, number reviewed, completeness;
2. top 2–3 next actions and why they unblock later work;
3. a pipeline-ordered P0/P1/P2 table: issue number, status, evidence, blockers,
   cost class, next acceptance test;
4. CLOSE/UPDATE candidates with specific evidence;
5. unresolved evidence gaps and cross-repo ownership;
6. a short sequence showing which expensive work must wait.

Call out old issues explicitly rather than silently dropping them. Separate
measured findings, code inspection, inference, and proposed-but-untested work.

### Step 8 — Act only when asked

See **Mutation boundary** below. Reporting and ranking happen automatically;
everything else requires explicit per-item authorization.

## Conventions this skill enforces

- **Full-queue coverage, not first-page sampling.** State exactly how many
  issues were reviewed and whether coverage was complete.
- **Evidence over vibes.** Every CLOSE/UPDATE/duplicate recommendation cites a
  specific commit, PR, artifact, or code location — never "this looks done."
- **P0 is rare.** If more than ~10% of the queue lands P0, the calibration is
  wrong; recheck. A stale `P0:` string in a title is not evidence.
- **Titles are claims and they drift.** Issues get retitled mid-life, including
  to `[WITHDRAWN/RESOLVED]`, while staying open. Re-read titles at report time
  rather than trusting the ones fetched at the start of the sweep.
- **The queue moves during the sweep.** Parallel PRs can resolve issues while
  triage is in progress. Re-check the open set immediately before reporting, and
  say so if it changed.
- **Read-only by default.**

## Measurement discipline

The recurring failure here is not misreading evidence, it is mismeasuring it.
Before citing any of the following, confirm how it was obtained:

- **Machine-local green.** A suite can pass only because *this* machine has
  something the project never declares: a gitignored release under `data/raw/**`
  (#569) or a Homebrew binary such as `rg` that CI does not install (#571). A
  full-suite pass on a developer machine is not evidence that CI passes. Verify
  in a clean worktree off `main` before citing a green run.
- **Counting basis.** "Records under the source directory" and "records
  mentioning the identifier" are different numbers, and a table that mixes them
  silently is wrong. PROSITE read 6,174 for months against an actual 3,425
  (#566). State the basis with the count.
- **`-path "*name*"` false positives.** Matching a source name against a whole
  path collides with category directories — `-path "*superfamily*"` also matches
  `seq_homologous_superfamily`, inventing tens of thousands of records for a
  source that has none. Enumerate real source directories at a fixed depth
  instead (`find data/traits -mindepth 3 -maxdepth 3 -type d`).
- **Squash-merge breaks ancestry.** `git branch --merged main` gives false
  negatives for squash-merged branches. Prove a branch is safe to delete by
  **content** (`git diff <branch> origin/main -- <files>`), never by
  reachability.
- **Exit codes through pipes.** `cmd | tail -3; echo $?` reports `tail`'s
  status, so a fail-closed tool looks like it succeeded. Use
  `cmd >/tmp/o 2>/tmp/e; echo $?` or `${PIPESTATUS[0]}`.
- **Whitespace-splitting file lists.** `git status --porcelain | awk '{print $2}'`
  turns one path containing spaces into several bogus entries. Use
  `--porcelain -z | tr '\0' '\n'`.
- **Glob patterns tested by shape.** A regex check on a `.gitignore` pattern
  tests what it looks like; `git check-ignore --no-index <path>` tests what it
  does. Only the second is evidence.
- **Truncated tool output.** Several checkers elide long lines. Re-read the cited
  file at the cited line before acting on it.
- **Backticks in a double-quoted `-m`.** ``git commit -m "...`cmd`..."`` executes
  the backticked text. Write reports and messages containing shell examples via
  `-F <file>` or a quoted heredoc (`<<'EOF'`), then read the result back.

## Notes & limitations

- `gh issue list --json` omits `comments` unless requested. This repo records
  corrections, withdrawals, and narrowed residuals in comments, so a body-only
  fetch overstates what is open.
- An issue may be fully addressed in code while its acceptance criteria are not.
  Say which part is done and which is not.
- Evidence recovery is sometimes impossible. When a residual asks for an
  artifact the repo records as absent, say so and recommend superseding rather
  than leaving the issue open indefinitely.
- Cross-repo issues (a defect described once but relevant to several Mechs) are
  common in this org. Note when a fix should propagate, but do not open issues
  in sibling repos without being asked.
- The local checkout can lag `origin/main` significantly, and a feature branch
  can predate skills that already merged. Verify against `origin/main` or
  `gh api`, not the working tree.
- No @-mentions in issue comments, tracker updates, or reports without explicit
  per-mention authorization (standing rule).

## Mutation boundary

Do not close, comment on, relabel, retitle, or create issues or trackers during
the review. If the user later asks to act, present the exact issue numbers and
the proposed mutation first, then apply one at a time with cited evidence. A
general "yes, go ahead" is **not** authorization for an unattended bulk-close —
an agent closing a live issue because it *looks* stale is worse than leaving
noise in the queue.

Do not run seeders, promoters, fetch recipes, or `--apply` paths as part of
triage. A recommended command is a proposal, not permission to execute it.

For a tracker issue (the `[P0-P2 tracker]` pattern used elsewhere in this org,
e.g. CommunityMech#669): search first — `gh issue list --search "tracker"
--state open` is authoritative, not this note. If one exists, update it in place
rather than creating a second.

## Related

- `next-tasks` — the lighter, `NEXT_TASKS.md`-scoped backlog check; run that for
  "what's next" during active work. Run this skill for a full-queue sweep.
- `data-sources` — `download.yaml` status/licence questions raised by Step 5.
- `ingest-source` — for bringing in *new* sources, not triaging existing issues.

## Related files

- `NEXT_TASKS.md` — items promoted from this skill's ranking often get logged
  here too, so `next-tasks` picks them up on the next reconcile.
- `CLAUDE.md` — the change-to-gate matrix that decides a fix's acceptance test.
