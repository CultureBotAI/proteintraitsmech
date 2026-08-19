# Curation history

Append-only provenance for curation sessions. **One record per change** — per target
for hand curation, per *migration* for a bulk edit. Written once and **never edited**;
corrections go in a new record that references the old one in its `details`.

```
history/<kind-dir>/<slug>/<TIMESTAMP>-<actor>-<shortid>.yaml
```

## Why this exists

Git records that a commit happened. It does not record *which model, using which tool,
changed what, why, and under which issue* — that a definition was checked against a
cached abstract, that an edge came from a particular deep-research provider, or that a
review deliberately changed nothing.

This repo has a concrete reason to want that beyond the fleet's. Several recent changes
here were bulk and mechanical — 27,784 definitions held back from a `--force` re-seed
(#455), 4,664 notes respelled (#466), 173 ancestry notes across 155 records rewritten (#364). Each
was one decision applied by one script to thousands of files, and the commit message is
currently the only place that decision is written down. A history record puts it where a
reader of the *data* can find it.

## Why the layout looks like that

Directory-per-slug plus an unguessable `shortid`: two agents curating the same record
concurrently cannot write the same file, so this layer has **zero merge-conflict
surface**. Compare a single shared CHANGELOG, which conflicts on every parallel PR.

## Enforcement is deliberately split

**Presence is advisory. Validity is not.**

`just validate-history` and CI hard-fail a record that is present and malformed. Neither
blocks a PR that writes no record at all. That is the shared schema's own decision, not
a local softening — a hard gate on provenance blocks legitimate work at inconvenient
moments and trains people to route around it, and a provenance layer people route around
is worse than none.

Note that issue #484's acceptance criteria ask for the stronger reading ("data-changing
PRs require valid append-only history"). This repo implements the fleet's semantics
instead, so that its history layer means the same thing as its siblings'. Tightening it
is a fleet decision, not one to make unilaterally here.

## Writing one

Do not hand-write records or filenames.

```bash
just new-history --kind record --slug aak-1-aro3006863 \
  --event EDIT --outcome changed --summary "..."
just validate-history                       # whole tree
just validate-history history/records/aak-1-aro3006863   # one target
```

`just new-history` prefers claw's canonical scaffolder when `CLAW_SRC` points at a
checkout, and falls back to `scripts/new_history_record.py`. Both write against the same
vendored `src/proteintraitsmech/schema/history.yaml`, which is what the validator and CI
check — the schema is the contract, not either producer.
