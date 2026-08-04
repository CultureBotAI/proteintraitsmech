# NEXT_TASKS_LOOP

Which open issues are safe to hand to an unattended `/goal` loop, which need a human
first, and why. Companion to `NEXT_TASKS.md` (the durable backlog) and
`prompts/backlog-loop-goal.md` (the workflow itself).

_Reconciled 2026-08-04 against `main` at `957a19691d3`. Every number re-measured rather
than carried over._

**Two reconciles in one day, because the loop empties the list faster than the list is
written.** The first version's eight loop-ready issues all closed; its replacement ranked
three more, and those are now done too. That churn is the point — but it means the ranking
below is a snapshot, and should be re-derived rather than trusted if much has merged since.

---

## What makes a task loop-suitable

`/goal` can run a whole issue to a merged PR without help when four things hold:

1. **The finish line is a measurement, not a judgement.**
2. **No curation policy is needed.** What counts as good enough is the owner's call.
3. **Blast radius is knowable up front**, especially if records change.
4. **A gate can prove it** — `just test`, `just lint`, `just validate-all`,
   `just audit-graphs`, or a canary re-seed diffed byte-for-byte against `main`.

---

## Done since the last reconcile

Listed so a loop does not start them again, and because what each one *corrected* is
more reusable than what it fixed.

| issue | what landed, and what it corrected |
|---|---|
| **#135** | the stray backslash is `/`, fixed in the seeder. Filed as a guess; turned **determinate** once a second occurrence (`tertiary\quaternary`) was found in the same field |
| **#137** | spent markers cite the issues they closed, not a PR number — which cannot be verified at the moment it is written |
| **#132** | a runtime harness for `build_metalpdb`, which catches `break`-instead-of-`continue`. The issue named the wrong builder as smallest: 301 lines, not `build_mcsa`'s 416 |

---

## Loop-ready, in the order I would run them

| # | issue | why it fits now | ends when | measured cost |
|---|---|---|---|---|
| 1 | **#141** the other four builders have no runtime harness | **#132 supplied the pattern** — see below | all five builders assert the skip path at runtime | 4 builders |
| 2 | **#139** two U+FFFD in a BV-BRC definition | starts with a re-fetch, which is a measurement | it is known whether the loss is upstream or ours | 1 record |

**#141 is the scoped remainder of #99.** Work #141; #99 is the umbrella and should be
closed or re-scoped once it lands, not run alongside.

### #99 stopped being open-ended, and #141 is what is left of it

#99 was listed as "needs a human — open-ended, needs a target". **#132 supplied the target
and proved the pattern works**, and #141 records precisely what remains. All four remaining causal-graph builders have the shape the
harness needs, checked:

```
                                     traits ROOT constant   raw inputs as constants
build_biolip_causal_graphs.py                1                       3
build_ec_causal_graphs.py                    1                       0
build_mcsa_causal_graphs.py                  1                       1
build_rhea_causal_graphs.py                  1                       2
```

so `ROOT` is monkeypatchable and the heavy inputs are stubbable in each, exactly as in
`tests/test_builder_runtime.py`. No production change was needed for `build_metalpdb` and
none should be needed here. `build_ec` is the easiest of the four — no raw input at all.

### #139 begins with a measurement, not a judgement

The issue offers three options, and option 3 is runnable today: `just fetch-seed-subsystems`
exists. Re-fetch, then check whether the fresh dump still contains U+FFFD. That answers
*"is this one bad record or a live decode problem"* before anyone has to decide what the
lost characters were.

Only if the fresh dump is clean does it become a judgement — and then it is a re-seed, not
a guess. Note the damage is **lossy**, unlike #123's reversible byte round trip, so
`repair_mojibake` correctly declines it.

---

## Not work — these need a decision

Three issues are substantially resolved and wait on a close/keep call rather than effort.

| issue | measured now | recommendation |
|---|---|---|
| **#96** "no test suite" | **6 test files, 232 tests**, `just test`, `just lint`, and CI running both on every PR | **close** — the remainder is #141, which is loop-ready |
| **#110** slugify, 28 implementations | **1 with logic, 31 delegating wrappers**, AST-enforced | **close** — #124 resolved it; the wrappers exist so no record is renamed |
| **#102** PSI-MOD Unimod xrefs | 825 dropped lines are real, but **0 terms** have `Unimod` as their only xref, against the 9 claimed | **re-scope or close** — the stated justification does not hold |

---

## Needs a human before it can be looped

| issue | fails | the decision only you can make |
|---|---|---|
| **#92**, **#115** PANTHER stubs | 2 | **6,709** records carry a composed stub; **1,657** have a reviewed abstract parked in `definitions[]`. Those were reviewed and *declined* — improving them needs a curator, or a decision to write definitions from GO/protein-class content. Promoting them anyway would undo #112. |
| **#114** first-pass rubric was lenient | 2 | whether to re-review other sources under the stricter rubric, and at what cost |
| **#120** stale xrefs persist by design | 3 | needs per-entry provenance on `xrefs`, a schema change |
| **#122** `BIOLIP_DNA` conflates two molecules | 2 | almost certainly two records, but splitting a class record is a curation act |
| **#5** web design review | 4 | visual judgement; no gate can prove it |

---

## What the last two reconciles corrected

Kept because the pattern matters more than the individual fixes: **issue text goes stale or
was wrong in roughly half the cases checked.**

- **#132 named the wrong builder** as smallest — `build_metalpdb` (301 lines), not
  `build_mcsa` (416). Following the issue would have picked the more expensive pattern.
- **#135 was filed as a guess** (*"probably means `/`"*) and turned out determinate once the
  second stray backslash was found in the same field.
- **#115's 1,142 is stale** — now **1,657**, after #112 demoted a further 515.
- **#102's severity claim is disproven** — 0 terms, not 9.
- **#99 was mis-filed as needing a human.** It needed a *target*; #132 supplied one and
  #141 now carries the remainder.

---

## Running the loop

The workflow is `prompts/backlog-loop-goal.md`. It is a **prompt, not a command** — feed it
to the agent, or paste it; it is self-contained for exactly that reason.

```
/goal                          # then feed prompts/backlog-loop-goal.md
/goal #141                     # same, with a named issue as the hint
```

`prompts/` also holds three **spent** scoped prompts. Each says so in its `**Use:**` line —
do not run them.

Three things worth knowing before leaving a loop unattended:

- **It pauses for merge approval every time.**
- **It will extend scope if review shows the work was incomplete rather than imperfect.**
- **It corrects issue text it finds wrong, and files what it does not fix.** Expect the
  backlog to change shape as well as shrink: this file has been rewritten twice in a day
  for exactly that reason.
