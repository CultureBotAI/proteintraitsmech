# has_graph hardening — #105, #106, #104 as one pull request

> ## ✅ DONE — do not run this
>
> Executed and merged as **#131** (`923506fc2642`) on 2026-08-04. **#104, #105 and #106
> are closed.** Running it again would re-do finished work.
>
> Kept as a **worked example** of scoping a multi-issue run: what a dependency check
> looks like when issues cannot be separate PRs, and what it means to carry measured
> facts into a prompt instead of trusting the issue text. For a live run, use
> `prompts/backlog-loop-goal.md`, which picks its own target.
>
> **What actually happened**, including where this prompt was wrong:
>
> - **#106's premise did not hold.** This prompt repeated the issue's claim that the
>   builder parses a record once per M-CSA id. It does not — there is one call per
>   iteration. The real redundancy was 42 repeat visits across 472 iterations, ~27 ms,
>   not the "N parses per record" both the issue and this file asserted.
> - **The `yaml.YAMLError` instruction was superseded.** Catching it in six builders
>   would leak the parser choice out of `record_io`; #131 introduced `RecordError`
>   instead, with `DuplicateKeyError` as a subclass.
> - **The trap list earned itself.** "Stop if `data/traits` shows any modification"
>   and "assert the mutation target exists" both held; nothing was written, and every
>   mutation was verified to fire.

A worked instance of `prompts/backlog-loop-goal.md`, not a replacement for it: that
file is the workflow, this supplied the scope, the measured facts and the traps for
one specific run.

_Facts measured on `main` at `e39111ffe7a`, 2026-08-04. Superseded by #131._

---

Work **#105, #106 and #104 as ONE pull request, three commits, in that order.**
Follow `prompts/backlog-loop-goal.md` for the workflow.

## Why one PR, not three

They overlap by construction, so three branches would conflict:

- **#105** changes `record_io._graph_ids`
- **#106** rewrites `build_rhea_mcsa_residue_graphs.py:333`
- **#104** wraps all six `has_graph` call sites — including the one #106 just rewrote

Do them in the order given: `record_io` first, then the caller that consumes it, then
the wrapping. Each commit stands alone and says what it fixes.

## Verified facts — do not re-derive them badly

| issue | measured |
|---|---|
| **#105** | **0 of 424,467** records have a duplicated top-level key. A regression guard, **not** a live defect — do not claim it fixes live data. |
| **#106** | 1,003 M-CSA active-site records. The builder calls `has_graph` once per M-CSA id, so a record with N ids is parsed N times: ~10 ms for 8 lookups against ~0.65 ms for one parse. Real cost today is seconds — fix it because the fix is smaller than the issue, not because it is slow. |
| **#104** | **Cannot fire today**: all 424,467 records parse. Six call sites, each `if has_graph(text, ...): stat[...]; continue`. |

The six call sites:

```
build_biolip_causal_graphs.py:269      build_mcsa_causal_graphs.py:370
build_metalpdb_causal_graphs.py:235    build_rhea_mcsa_residue_graphs.py:333
build_ec_causal_graphs.py:312          build_rhea_causal_graphs.py:423
```

## What each one means

**#105** — `_graph_ids` stops at the next top-level key, so it reads the **first**
`causal_graphs:` block; PyYAML keeps the **last**. On a record carrying the key twice
they disagree, and `has_graph` answers from the block a loader discards. Make it raise
on a duplicated key rather than answer wrongly. Note the old textual scanner behaved
identically — this is latent and pre-existing, not a regression from the parse rewrite.

**#106** — `record_io._graph_ids` already returns the whole set. Call it once per record
and test membership, instead of calling `has_graph` per id.

**#104** — `has_graph` raises on a malformed section deliberately: returning `False`
would make a builder append a duplicate, which is silent corruption. But no caller
catches it, so one bad record aborts a run partway through, **after** it has already
written to earlier records. Catch it in each builder's loop, warn with the path, and
skip the record — strictly better than either crashing or answering `False`.

## Gates — all must pass before the PR

```bash
just test          # 201 with data/raw linked, 189 without; both fine
just lint          # must stay at zero, CI runs it
just audit-graphs
```

For **#106**, prove the builder is unchanged in behaviour: run it before and after and
diff the output **byte for byte**. Do not accept "it still runs".

## Traps

- **Do not "fix" #105 by reading the last block.** Duplicate top-level keys are
  corruption; the point is to surface them, not to silently pick a winner.
- **#104's `except` must not swallow real bugs** — catch `yaml.YAMLError`, not
  `Exception`.
- **Mutation-verify every test added**, and assert the mutation target exists before
  applying it: a mutation that silently no-ops reports a false pass. That has happened
  twice in this repo.
- **Nothing here should change a single record.** All three are latent. If
  `git status` shows `data/traits` modified, something is wrong — stop and find out
  what before going further.

_(Original closing instruction: pause and ask before merging. #131 did.)_
