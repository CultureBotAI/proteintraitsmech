# Loop A — #94, #125, #117: code and docs, zero records

**Use:** none — spent; it closed #94, #125 and #117. Kept as a
worked example of an audit that correctly closed without a code change.

Feed this to `/goal`, or paste it to any agent. A worked instance of
`prompts/backlog-loop-goal.md`, which remains the workflow; this supplies the scope,
the measured facts and the traps.

_Facts measured on `main` at `d11217c5df5`, 2026-08-04._

---

Work **#94, #125 and #117 as ONE pull request, three commits.**

## Why these three, and why one PR

They have **zero file overlap** — with each other and with Loop B — so nothing forces
them together. They are grouped because they share a **gate story**: none of them
touches a single record, so the whole PR is verified by `just test`, `just lint`, and
byte-identical builder output. Nothing needs `validate-all` over the corpus.

**If `git status` ever shows `data/traits` modified, stop.** That is the signal that
something has gone wrong, not a step in this work.

| issue | files | records |
|---|---|---|
| #94 | `build_biolip_causal_graphs.py`, `build_metalpdb_causal_graphs.py` | 0 |
| #125 | `yaml_emit.py` + 3 callers | 0 |
| #117 | `prompts/*.md`, `CLAUDE.md` | 0 |

Do #94 first: it is evidence-gathering and may close without a code change, which sets
the size of the rest.

## #94 — audit the round-15 builders. It is very likely a close, not a fix.

The issue asks whether `build_biolip_causal_graphs.py` and
`build_metalpdb_causal_graphs.py` carry two defect classes fixed elsewhere in `5e9e920`.
**Both appear already absent** — verify, then close with the evidence rather than
inventing work:

* **class 2, over-broad skip predicate** — both now call `has_graph(text,
  "ligand_binding")` and `has_graph(text, "metal_coordination")`, i.e. anchored on their
  own graph id. Fixed.
* **class 1, `re.sub` with a string replacement template** — the only `re.sub`
  replacements in either file are the constant `"mapping_status: REVIEWED"`. A constant
  with no backslash cannot be misread as a `\g` template. The hazard was splicing
  *payload* through a replacement, and both now use `record_io.append_to_section`.

So the deliverable is a comment on #94 showing both checks, and a close. **If you find
either class actually present, that is a real finding — fix it and say so.** Do not
manufacture a change to justify the visit.

## #125 — one `folded`, four signatures

There are **four** distinct `folded` functions, and a fifth under another name:

```
yaml_emit.folded(text) -> list[str]                    the shared one
seed_secondary_structure.folded(text) -> str           ">-\n  " + text
enrich_scop_structural_defs.folded(text, indent) -> str
review_llm_abstracts.folded(key, text) -> str
seed_biolip.yaml_folded(indent, text) -> list[str]     same idea, different name
```

**The trap, and the reason this is not a rename:** `seed_secondary_structure.folded`
does **not** collapse whitespace — it is literally `">-\n  " + text`, where the shared
one does `" ".join(text.split())`. Pointing it at the shared implementation therefore
**changes what it emits** for any input containing a newline or a run of spaces. Check
whether its inputs ever do before assuming the change is inert, and if they do, that is
a behaviour change that needs its own justification and a record diff.

`enrich_scop_structural_defs` takes an `indent`, and `review_llm_abstracts` takes a
`key` and emits a whole block. Unifying those means changing their callers, which is
fine, but it is the work — the duplication itself is not the hazard here, because none
of them can silently disagree about bytes: they are never called interchangeably.

A defensible outcome is a shared implementation with optional `key` and `indent`, three
callers updated, and `seed_secondary_structure` either converted **with** its whitespace
behaviour preserved or left alone with a comment saying why.

## #117 — say how each prompt is meant to be used

`CLAUDE.md` lists every file in `prompts/`, and `tests/test_docs_consistency.py` now
enforces that in both directions — an unlisted prompt fails, and so does a dangling
reference. You do not need to check it by hand; that list went stale twice in one day
while the mitigation was "remember to check".

What #117 asks for is a one-line note **in each file** saying how it is used, so a reader
can tell which kind of document they are holding without consulting `CLAUDE.md`.

**Option 1 in the issue is dead** — it proposed a skill wrapper, which #126 deleted on
purpose. I have already commented saying so. Do not re-add one.

## Gates

```bash
just test          # 209 with data/raw linked, 197 without; both fine
just lint          # must stay at zero, CI runs it
just audit-graphs
```

Plus, for #125: run every builder and seeder whose `folded` you touched, and diff the
dry-run output **byte for byte** against `main`. `seed_3did`, `seed_cdd`, `seed_cazy`,
`seed_cog`, `seed_complexportal` and `seed_biolip` all call one of these.

## Traps

- **Do not manufacture a fix for #94.** "Audited, both classes absent, here is the
  evidence" is the expected outcome and a complete one.
- **`seed_secondary_structure.folded` is not equivalent to the shared one.** See above.
- **Mutation-verify anything you add**, asserting the mutation target exists first.
- **No record may change.** All three issues are code and docs.

Pause and ask before merging.
