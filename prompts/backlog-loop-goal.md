# Goal prompt — triage the open issues and deliver one end to end

Feed this to the **native** `/goal`, optionally with a hint (`/goal #104`,
`/goal tests`, `/goal cheapest thing that unblocks something else`). It is a prompt,
not a slash command, and is self-contained so it can equally be pasted to another
agent or an independent reviewer.

**Do not wrap it as a custom command.** `.claude/skills/goal/SKILL.md` used to exist
for that and was deleted: it registered a custom `/goal` that SHADOWED the native one
rather than feeding it, which is the opposite of the intent. If such a wrapper
reappears pointing here, delete it rather than repointing it.

Pick the highest-value open issue that is actually startable, and carry it all the
way: branch → work → gates → PR → adversarial review → issues from that review →
triage → merge → delete the branch. **Pause and ask** at the points marked below
rather than guessing.

The steps are ordered because each one has been skipped at least once, and the
skip is what caused the next defect.

---

## 0. Your role

You are delivering a change to a schema-governed knowledge base whose deliverable
is ~424k curated YAML records. A silent data defect is worse than a loud crash:
nobody reads 424k files, so anything that corrupts quietly stays corrupted. Prefer
loud failure, reversible edits, and a stated number over a plausible impression.

---

## 1. Survey and prioritise the open issues

```bash
gh issue list --state open --limit 50
gh pr list  --state open --limit 20            # what is already in flight
```

For each open issue establish four things, cheaply:

| | question |
|---|---|
| **Live or latent?** | can it actually fire on current data, or only in principle? Check — do not assume. |
| **Blast radius** | one record, one source, or the whole corpus? |
| **Blocked?** | does it need an unmerged PR, or a decision only the user can make? |
| **Cost** | an hour, or a paid sweep over thousands of records? |

Rank by *value ÷ cost*, with these tie-breaks, highest first:

1. **live data corruption** — anything writing wrong bytes into records
2. **a gate that does not gate** — a test, audit or validator that passes when it
   should fail (a false green is worse than no check, because it is trusted)
3. **blocks other issues** — unblocking work is worth more than doing it
4. **latent correctness** — real, cannot fire yet
5. **coverage / cleanup / performance**

Demote anything whose issue text you cannot verify. Issues written from a bad grep
carry wrong numbers; re-measure before planning around them.

### Dependencies — do this before choosing, not after

Build the dependency graph across **both** issues and open PRs:

- **File overlap.** List each open PR's files and intersect with what you plan to
  touch. If they overlap you will rebase or conflict — say so up front and prefer
  sequencing over parallel work.

  ```bash
  gh api repos/:owner/:repo/pulls/<n>/files --paginate --jq '.[].filename'
  ```

  Not `gh pr diff --name-only`: it fails with **HTTP 406** above 300 files, which
  is the normal size of a data PR here (#113 touched 519, #111 touched 1,608). It
  works on small PRs and dies on exactly the ones whose overlap you most need to
  know about.
- **Issue references.** An issue saying "properly fixing this means one shared
  implementation, see #93" is *downstream of* #93. Doing it first means doing it
  twice.
- **Consolidation before correction.** If N copies of a function are each wrong,
  the fix is one shared implementation, not N edits. Check whether a consolidation
  issue exists and is unmerged.
- **Tests before the risky change.** If the work rewrites something with no
  coverage, the coverage issue is a prerequisite, not a follow-up.
- **Unmerged prerequisite ⇒ do not start.** Branch from `main`, not from an
  unmerged branch, unless the user asks for a stack. If the prerequisite is small,
  offer to do it first as its own PR.

> **PAUSE — ask the user** when the top two candidates are close in value, when the
> best candidate is blocked by an unmerged PR, or when the issue needs a policy
> decision (what counts as good enough, whether machine-written text may be
> promoted, whether to gate at zero or ratchet). Present a ranked shortlist with
> one line of rationale each and a recommendation — not an essay, and not an open
> question with no default.

Proceed without asking when one candidate clearly dominates, or when the user named
the issue.

---

## 2. Branch before the first edit

Never commit to `main`. Docs-only and "obviously safe" changes are not exceptions —
that is exactly the category that lands on `main` by accident.

```bash
git worktree add -b <topic> ../<repo>-<topic> origin/main
```

Use a **worktree**: another session may hold `main` or another branch, and
`gh pr merge --delete-branch` fails if a sibling worktree has the base checked out.

---

## 3. Do the work

- **Canary before any fan-out.** One record, one file, one API call — through the
  *same launcher, shell and environment* as the batch. Verify the side effect on
  disk, not the exit code. A canary has repeatedly caught, in one unit, what would
  have been wrong in thousands: a shell-function wrapper a subprocess cannot see, a
  reviewer emitting two JSON arrays, an indent bug that corrupted a record.
- **Re-canary after a fix.** Never fix and fan out in the same step.
- **Idempotent, dry-run by default, `--apply` to write.** Then actually re-run it
  and diff: "idempotent" is a claim until the second run is byte-identical.
- **Reversible edits.** Never delete what you displace. Keep the prior value in the
  record so the change can be undone from the record itself.
- **Honest provenance.** Machine-generated or machine-reviewed content must say so
  in the record. Never let it become indistinguishable from curated content.
- **Verify every number before you write it.** Counts in commit messages, PR
  bodies, comments and issues are claims. Multiline `grep` patterns, filters that
  miss a clause, and `if hasattr(...) else True` guards have all produced confident
  wrong numbers. Compute it twice, by different means, if it will be quoted.

---

## 4. Gates — all of them, before the PR

```bash
just test                     # unit tests
just validate-all <scope>     # closed-mode LinkML; scope it, then run it whole
just audit-graphs             # structural integrity of causal graphs
just sources-check            # data-source registry
uv run ruff check scripts/ tests/   # compare to main's baseline, do not raise it
```

If you added tests, **mutation-verify** them: break the production code the test
covers and confirm the suite goes red. Assert the mutation target exists before
applying it — a mutation that silently no-ops reports a false pass. Restore
afterwards and confirm the tree is clean.

A test that passes against broken code is worse than no test.

---

## 5. Commit, push, open the PR

Small logical commits, not one blob. The message explains **why**, the constraint
that forced the design, and what you verified — not a restatement of the diff.

PR body: what changed, the measured result, what you deliberately did **not** fix
and why, and the gate output.

---

## 6. Review the PR adversarially — a separate, read-only pass

Not a restatement of what you just wrote. Reviews do not edit files, push, or
overwrite outputs.

- **Probe, do not read.** Write throwaway scripts that try to break the change:
  pathological inputs, the shapes nobody writes, the corpus's real extremes.
- **Check the claims in your own diff.** Every number in a comment or docstring.
- **Run the linter** — nothing else does.
- **Prefer an invariant to another guessed edge case.** If a function has been
  revised three times for three shapes nobody imagined, assert the property that
  must always hold and run it over all real data. That scales past your imagination;
  enumerating a fourth shape does not.
- **An independent model's report is a lead, not a finding.** Verify its strongest
  claims before repeating any of them. Reviews have been wholly fabricated when the
  input file was missing, and have been confidently wrong when a field was ignored.
  Never quote a rate you have not spot-checked.
- **Measure a heuristic before reporting it as coverage.** If you narrowed scope
  with a filter, sample what the filter *excluded*. A plausible filter that is never
  measured is indistinguishable from a correct one, right up until it is reported as
  done.

---

## 7. Every finding becomes an issue

File it even if the answer is "won't fix" — the issue is the record that the
finding existed. Include the reproduction, the blast radius, whether it can fire
today, and the suggested fix. Cross-reference the related issues.

---

## 8. Triage — and say which is which

Fix in *this* PR what belongs in it: defects the PR introduced, and anything
blocking it. File the rest. Then state plainly which you fixed, which you filed,
and **why** — "needs edits to six files this PR does not touch and cannot fire on
current data" is a reason; "out of scope" is not.

If review shows the work is incomplete rather than imperfect — the scope was chosen
by a heuristic that does not hold — **extend the work**. Reporting a partial pass
with an authoritative-sounding number is worse than not having run it.

---

## 9. Merge — the user's call

> **PAUSE — ask for merge approval** unless the user has already given it *for this
> PR in this conversation*. Approval of a previous PR is not approval of this one.

Report before asking: what merged-state looks like, the gate results, the issues
filed, and anything still unverified.

---

## 10. Merge and clean up

```bash
gh pr merge <n> --squash            # --delete-branch fails if a worktree holds main
git push origin --delete <topic>
git worktree remove ../<repo>-<topic>
git branch -D <topic>
git fetch --prune origin && git pull --ff-only origin main
```

Confirm the merge landed (`gh api .../pulls/<n> --jq .merged`) before deleting
anything. Then re-run `just test` on `main`.

---

## Pause points, in one list

Stop and ask when:

1. two candidate issues are close in value, or the best one is **blocked**;
2. the issue needs a **policy decision** (quality bar, provenance rules, whether to
   gate at zero or ratchet from a baseline);
3. the work would **cost real money at scale** and the canary changed your estimate;
4. review shows the scope was wrong and fixing it **multiplies the cost**;
5. **merge approval**;
6. anything **irreversible or outward-facing** that the user has not authorised —
   force-pushing a shared branch, closing someone else's issue, deleting data,
   @-mentioning anyone.

Ask with a concrete recommendation and a default. Do not ask what you can measure.
