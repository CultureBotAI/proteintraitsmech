# NEXT_TASKS_LOOP

Which open issues are safe to hand to an unattended `/goal` loop, which need a human
first, and why. Companion to `NEXT_TASKS.md` (the durable backlog) and
`prompts/backlog-loop-goal.md` (the workflow itself).

_Reconciled 2026-08-04 against `main` at `9e132d5081e`. **All eight issues the previous
version listed as loop-ready are now closed**, so the ranking is rebuilt from scratch.
Every number was re-measured rather than carried over; three were wrong and are corrected
below._

---

## What makes a task loop-suitable

`/goal` can run a whole issue to a merged PR without help when four things hold:

1. **The finish line is a measurement, not a judgement.**
2. **No curation policy is needed.** What counts as good enough is the owner's call.
3. **Blast radius is knowable up front**, especially if records change.
4. **A gate can prove it** — `just test`, `just lint`, `just validate-all`,
   `just audit-graphs`, or a canary re-seed diffed byte-for-byte against `main`.

Everything in the first table meets all four. The rest say which one they fail.

---

## Loop-ready, in the order I would run them

| # | issue | why it fits | ends when | measured cost |
|---|---|---|---|---|
| 1 | **#135** BV-BRC stray backslash | now **determinate** — see below | both `\` become `/` | **1 record** |
| 2 | **#137** a spent prompt can cite a PR that never ran it | pure docs plus one test; three options, one recommended | the marker cannot be silently wrong | 5 prompt files, 1 test |
| 3 | **#132** builders have no runtime harness | bounded once scoped to one builder | one builder's loop driven over a temp dir — good, malformed, good | 1 builder |

### #135 stopped needing a judgement

It was filed as *"the upstream text probably means `/`"*, which is a guess. Re-reading the
raw source settles it: **the same field carries two stray backslashes**, and the second
disambiguates the first.

```
...including amino acid\nucleotide sequence, and immunological...
...kinetic and tertiary\quaternary structural...
```

`tertiary\quaternary` can only be `tertiary/quaternary`. So both are `/` typed as `\`, the
fix is determinate, and it is **two characters in one record** — the whole BV-BRC dump
contains no other stray backslash-letter.

### #132 names the wrong builder

The issue suggests `build_mcsa_causal_graphs` as "the smallest". Measured:

```
build_metalpdb_causal_graphs.py   301   <- smallest
build_biolip_causal_graphs.py     334
build_ec_causal_graphs.py         385
build_mcsa_causal_graphs.py       416
build_rhea_causal_graphs.py       498
```

`build_metalpdb` is the cheaper pattern, and `build_mcsa` additionally loads an M-CSA
cache that `build_metalpdb` does not.

---

## Not work — these need a decision

Three issues are substantially resolved and wait on a close/keep call rather than effort.

| issue | measured now | recommendation |
|---|---|---|
| **#96** "no test suite" | **5 test files, 221 tests**, `just test`, `just lint`, and CI running both on every PR | **close** — the remainder is #99 and #132, both filed |
| **#110** slugify, 28 implementations | **1 with logic, 31 delegating wrappers**, AST-enforced by `test_every_slugify_delegates_to_the_shared_one` | **close** — #124 resolved it; the wrappers exist so that no record is renamed |
| **#102** PSI-MOD Unimod xrefs | 825 dropped lines are real, but **0 terms** have `Unimod` as their only xref, against the 9 claimed | **re-scope or close** — the stated justification does not hold; already commented on the issue |

---

## Needs a human before it can be looped

| issue | fails | the decision only you can make |
|---|---|---|
| **#92**, **#115** PANTHER stubs | 2 | **6,709** records carry a composed stub; **1,657** have a reviewed abstract parked in `definitions[]`. Those 1,657 were reviewed and *declined* — improving them needs a curator, or a decision to write definitions from GO/protein-class content instead. Promoting them anyway would undo #112. |
| **#114** first-pass rubric was lenient | 2 | whether to re-review other sources under the stricter rubric, and at what cost |
| **#120** stale xrefs persist by design | 3 | needs per-entry provenance on `xrefs`, which is a schema change |
| **#122** `BIOLIP_DNA` conflates two molecules | 2 | almost certainly two records, but splitting a class record is a curation act |
| **#99** builders have no test coverage | 1 | open-ended; needs a target to be loopable. **#132 is the scoped version** — run that instead |
| **#5** web design review | 4 | visual judgement; no gate can prove it |

---

## Corrections found while reconciling

- **#132 names the wrong builder** as smallest — it is `build_metalpdb` (301 lines), not
  `build_mcsa` (416).
- **#135 is determinate, not a judgement** — the second stray backslash
  (`tertiary\quaternary`) settles what the first means.
- **#115's 1,142 is stale**; it is now **1,657**, because #112 demoted a further 515 after
  the issue was written. Of 6,709 stub records, those 1,657 are the ones that already have
  a reviewed abstract on file.
- **#102's severity claim remains disproven** — 0 terms, not 9. Recorded on the issue, in
  case it is ever picked up from the title alone.

---

## Running the loop

The workflow is `prompts/backlog-loop-goal.md`. It is a **prompt, not a command** — feed it
to the agent, or paste it; it is self-contained for exactly that reason.

```
/goal                          # then feed prompts/backlog-loop-goal.md
/goal #135                     # same, with a named issue as the hint
```

`prompts/` also holds three **spent** scoped prompts (`has-graph-hardening`,
`loop-text-decoding`, `loop-code-and-docs`). They are kept as worked examples and each
says so in its `**Use:**` line — do not run them.

Three things worth knowing before leaving a loop unattended:

- **It pauses for merge approval every time.** An unattended run stops with a reviewed,
  green PR open rather than merging it.
- **It will extend scope if review shows the work was incomplete rather than imperfect.**
  On #112 it re-reviewed 1,213 extra records after sampling showed the filter that selected
  391 was not a discriminator.
- **It corrects issue text it finds wrong, and files what it does not fix.** Of the eight
  issues closed since the last reconcile, four carried a wrong or stale number and two had
  a wrong root cause. Expect the backlog to change shape as well as shrink.
