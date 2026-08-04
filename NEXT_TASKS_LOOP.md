# NEXT_TASKS_LOOP

Which open issues are safe to hand to an unattended `/goal` loop, which need a human
first, and why. Companion to `NEXT_TASKS.md` (the durable backlog) and
`prompts/backlog-loop-goal.md` (the workflow itself).

_Compiled 2026-08-04, against `main` at `52807b6ad35`. Every number below was
re-measured rather than copied from the issue text. **Four were wrong** and are corrected
here — including one whose entire stated justification does not hold._

---

## What makes a task loop-suitable

`/goal` can run a whole issue to a merged PR without help when four things hold:

1. **The finish line is a measurement, not a judgement.** "37 records carry a literal
   `\n`" ends at 0. "Definitions should be better" does not end.
2. **No curation policy is needed.** Anything that decides what counts as good enough,
   or whether machine-written text may stand as fact, is the repo owner's call.
3. **Blast radius is knowable up front.** A change that rewrites records or renames
   files needs the counterfactual measured before it runs, and a human told the number.
4. **A gate can prove it.** `just test`, `just lint`, `just validate-all`,
   `just audit-graphs`, or a canary re-seed whose diff is byte-comparable against `main`.

Everything in the first table meets all four. Everything in the second fails at least
one, and says which.

---

## Loop-ready, in the order I would run them

| # | issue | why it fits | ends when | measured cost |
|---|---|---|---|---|
| 1 | **#105** duplicate top-level key: `has_graph` reads the first block, PyYAML keeps the last | pure function, one file, no data touched | `_graph_ids` raises on a duplicated key instead of answering from the wrong block | **0 records affected today** — a pure regression guard |
| 2 | **#106** residue builder re-parses the section once per `graph_id` | mechanical; `_graph_ids` already returns the whole set | one parse per record, membership tested against the set | 1,003 records, seconds either way |
| 3 | **#104** `has_graph` raises on a malformed section and no builder catches it | six builders, one identical `try/except` each | a bad record is warned about and skipped, not a crash mid-run | cannot fire today — all 424,467 records parse |
| 4 | **#125** three `folded()` variants, each a different signature | three call sites, all covered by `just test` | one `folded` with an optional `key`, three callers updated | 3 call sites |
| 5 | **#117** `prompts/*.md` do not say how they are meant to be used | two-line docs change; #126 settled the approach — a note, **not** a command wrapper | each `prompts/*.md` opens with how it is used | 2 files |
| 6 | **#103** OBO escapes decoded for citations but not definitions | bounded set, `validate-all` proves it | **37** records (issue says 36) carry a literal `\n` → 0 | 37 records |
| 7 | **#123** two records carry mojibake, one re-seeds to different bytes each run | tiny, and the fix is in the fetch/decode step | both records stable across two consecutive re-seeds | 2 records |
| 8 | **#94** audit round-15 builders for the two defect classes fixed in `5e9e920` | investigative but bounded; the two classes are precisely defined | every round-15 builder checked, findings filed | 2 builders |

**Trap on #103, worth stating before the loop hits it:** the InterPro records contain
`\textsuperscript`, which is **LaTeX, not an OBO escape**. Decoding it corrupts them. Any
fix must scope to OBO-sourced records.

---

## Needs a human before it can be looped

| issue | what it fails | the decision only you can make |
|---|---|---|
| **#92**, **#115** PANTHER stubs — **1,657** records, not the 1,142 in #115 | criterion 2 | 903 FLAG + 239 REJECT + the **515 demoted by #112** were all *reviewed and declined*. #115 predates #112, so its number is stale. Improving them needs a curator, or a decision to write definitions from GO/protein-class content instead. Promoting them anyway would undo #112. |
| **#114** the first-pass rubric was systematically lenient | criterion 2 | whether to re-review other sources under the stricter rubric, and at what cost |
| **#120** a re-seed can no longer remove an xref the source dropped | criterion 3 | needs per-entry provenance on `xrefs`, which is a schema change |
| **#122** `BIOLIP_DNA` conflates two molecules | criterion 2 | almost certainly two records, but splitting a class record is a curation act |
| **#102** PSI-MOD Unimod xrefs | criterion 1 | **the issue's severity claim does not hold** — see corrections below. Whether 825 dropped `Unimod:` xrefs matter at all is a scope call |
| **#99** builders have no test coverage | criterion 1 | open-ended; needs a target ("cover the six graph builders") to be loopable |
| **#96** no test suite | — | substantially done: **201 tests** (189 without the gitignored raw releases linked), `just test`, `just lint`, and CI running both. Needs a close/keep decision, not work |
| **#110** `slugify` 28 implementations | — | resolved by #124: one implementation, 32 parameter-only wrappers, AST-enforced. Needs a close decision |
| **#5** web design review | criterion 4 | visual judgement; no gate can prove it |

---

## Corrections found while compiling this

Re-measured on `main`, not copied from the issue text:

- **#103 says 36 records; it is 37.**
- **#102 says "9 terms lose their only reference"; it is 0.** The 825 dropped `Unimod:`
  xref lines are real, but **no term has `Unimod` as its only xref**, so nothing loses
  its only reference. That was the entire stated justification, so the issue needs
  re-scoping before anyone works it.
- **#105 affects 0 records**, confirmed across all 424,467 — it is a regression guard,
  not a live defect.
- **#115 says 1,142 stub records; it is now 1,657** — the issue predates #112, which demoted a
  further 515. Of 6,709 PANTHER records still carrying a composed stub, 1,657 have a reviewed
  abstract parked in `definitions[]`.
- **#91** was already fixed and is now closed.

---

## Running the loop

```
/goal            # ranks the open issues itself and proposes one
/goal #105       # skip the ranking pause and take a named issue
```

Two things worth knowing before leaving it unattended:

- **`/goal` pauses for merge approval every time.** Prior approval of one PR is not
  approval of the next, so an unattended run stops with a reviewed, green PR open rather
  than merging it. That is deliberate.
- **It will extend scope if review shows the work was incomplete rather than imperfect.**
  On #112 it re-reviewed 1,213 extra records after sampling showed the filter that chose
  391 was not a discriminator. Budget for that on anything touching many records.
