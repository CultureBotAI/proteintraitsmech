# Prompts

These are hand-off documents, not slash commands. Feed a prompt to the named native
workflow or an independent reviewer. Do not wrap a prompt as a skill: a wrapper named
`goal` previously shadowed the native command it was meant to invoke.

## Live workflows

- `backlog-loop-goal.md` — give to the native goal workflow to select and deliver an
  agent-ready issue end to end.
- `claude_code_deep_research.md` — research and curate one protein-trait record with the
  configured deep-research provider.
- `schema-review.md` — an independent, read-only schema review prompt.

## Historical/scoped runs

- `has-graph-hardening.md` — completed hardening run; retained as a worked example.
- `loop-code-and-docs.md` — scoped code/documentation run retained for archaeology.
- `loop-text-decoding.md` — scoped text-decoding run retained for archaeology.

Each prompt's opening `Use:` line is authoritative for whether it is live, scoped, or
spent. Historical issue narratives belong in these files and Git history, not in
`CLAUDE.md` startup context.
