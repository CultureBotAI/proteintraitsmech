---
date: 2026-07-27
skill: scalability-check
verdict: "Git = ACT for the 570k proposal; Pages/browser = WATCH, no change warranted"
---

# Docs & repo scalability audit

Two questions: can the repo take a `ProteinProfile` YAML per Swiss-Prot protein
(issue #7's literal ask), and is the browser payload a live problem?

## 1. One YAML per Swiss-Prot protein — no

| axis | now | +570k YAMLs | verdict |
|---|--:|--:|---|
| tracked files | 410,494 | **980,494** | **ACT** — 2× the 500k threshold |
| working tree | 1.8 GB (`data/traits`) | ~4.0 GB | watch → act |
| `.git` | 849 MB | grows every reseed | watch |

A real `ProteinProfile` averages **3,810 B**, so 570k of them is ~2.2 GB and
takes the repo to ~980k tracked files — double the point where git operations and
the GitHub UI degrade. Even the 80,066 already in the matrix would add 0.31 GB
and 80k files for data one recipe regenerates.

The `scalability-check` skill's tier D covers exactly this: for very
high-volume machine-seeded sources, store them as a smaller number of
multi-record files or keep them out of `data/traits/` rather than minting
hundreds of thousands of tiny ones. **Keep the jsonl-only decision.** If more
coverage must be committed, bucket it (~256 multi-record files, as the detail
sidecars already do) for full coverage at 256 files instead of 570,000.

## 2. The browser payload — I called this ACT, and it is not

I reported "121 MB browser payload, past the 66 MB threshold, a real currently-live
issue". That was **uncompressed bytes on disk**, which is not what the browser
fetches. Measured properly:

| | |
|---|--:|
| record shards on disk | 121 MB |
| **transfer, as Pages serves it (gzip)** | **14.1 MB** (8.6×) |
| `JSON.parse`, all shards (V8) | **449 ms** |
| heap retained, all shards (V8) | 242 MB |

And 242 MB is the **worst case, not the normal path**, because the browser
already loads shards lazily by axis:

| axis | records | heap |
|---|--:|--:|
| landing (nothing selected) | 0 | **0 MB** |
| FUNCTION | 163,223 | 109 MB |
| STRUCTURE | 118,280 | 70 MB |
| SEQUENCE | 127,082 | 63 MB |
| SEQUENCE_STRUCTURE | 384 | ~0 MB |
| EVOLUTION | 9 | ~0 MB |

The only path that loads everything is a **bare text query with no narrowing
filter** — and that is a deliberate, documented choice (`neededAxes()`: "a bare
text query with no narrowing filter = the whole corpus"), because there is no
server to search against.

### No change warranted, and the obvious levers are duds

- **Truncating definitions**: they are already capped at ~140 chars (median 127).
  Cutting to 120 saves 10% of def bytes; to 80, 32% — at real cost to search
  recall and the result snippet.
- **Dropping fields**: there are none to drop. Every field in a shard is used by
  the list view — `df` is the detail-bucket pointer that makes lazy detail work,
  `def`/`chem`/`chemx` are searched, `sta`/`src` drive the facets, and
  `id`/`label`/`axis`/`cat` are the row itself. The index is already lean at
  **297 B/record**.

Strategies A (build docs in CI, not committed), B (lean index + lazy detail) and
C (shard sizing) from the skill are **already implemented**. The audit's outcome
is that the previous work holds up, not that it needs redoing.

## What would actually be next, if anything

Only the unfiltered-search path is heavy (242 MB). Making it cheaper means a
separate compact search index (id + label only ≈ 22 MB) with definitions fetched
on demand — worth doing if search on mobile is reported as a problem, and not
before. Filed as a note here rather than as a task, because nothing measured says
it is needed.
