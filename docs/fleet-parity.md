# Shared Mech foundation — parity matrix

Where ProteinTraitsMech stands against the sibling Mech knowledge bases on the shared
curation foundation (#484).

**Everything below was checked against the sibling repositories, not against the issue
text.** The fleet review the issue cites
(`CultureBotAI/culturebotai-claw docs/reviews/five_mech_shared_functionality_review.md`)
is not present in that repository — the `docs/` tree there holds `AUTONOMOUS_LOOPS.md`
and `proposals/`, and an org-wide code search for the filename returns nothing. So the
siblings' own implementations are the specification used here, primarily
[TraitMech](https://github.com/CultureBotAI/TraitMech) as the closest sibling and
[CultureMech](https://github.com/CultureBotAI/CultureMech) as the vendoring hub.

## Status

| # | Capability | Before | Now | Notes |
|---|---|---|---|---|
| 1 | `mech_shared.yaml` with `Discussion` + `Dataset` | ✗ | **✓** | Vendored byte-identical from the hub; `discussions` / `datasets` on `ProteinTraitRecord` |
| 2 | Append-only history schema + presence gate | ✗ | **✓** | `history.yaml` vendored **and governed**, `history/` tree, CI job. Presence advisory — see below |
| 3 | `new-history` / `validate-history` recipes | ✗ | **✓** | Claw-preferred, local fallback scaffolder |
| 4 | Validated-write helper + writer-safety audit | ✗ | ✗ | Deferred — **#492** |
| 5 | ID-to-label correspondence validation | ✗ | **partial** | Validator + its 69 tests vendored, governed and passing; adapter deferred — **#493** |
| 6 | Evidence snippet / reference validation | **✓** | **✓** | Pre-existing: `just audit-snippets` |
| 7 | Knowledge-gap scan + shared QC dashboard | ✗ | ✗ | **Not a gap.** No sibling has this in CI or as a dependency — see below |
| 8 | Vendored shared-file drift enforcement | ✗ | **✓** | `just check-vendored-sync` over **7** files + blocking CI job |

Capabilities this repo already had, which the issue does not mention:
`just validate-strict` (closed-schema, in-process — #485), `just audit-graphs`,
`just audit-snippets`, `just audit-reproducible`, `just audit-prose`, `just audit-text`.

`just audit-schema` is listed in the justfile and in CLAUDE.md but its script does not
exist, so the recipe dies with `can't open file`. Pre-existing, not touched here, and
filed as #496 — but named rather than counted, since listing a broken recipe among
this repo's capabilities is the kind of paper parity this document is supposed to expose.

## Two places this deliberately diverges from the issue

**History presence is advisory, not blocking.** #484's acceptance criteria say
"data-changing PRs require valid append-only history". The shared `history.yaml` states
the opposite as a design decision, with its reason:

> ENFORCEMENT IS DELIBERATELY SPLIT. Presence of a record is *advisory* — CI warns, it
> does not block, because a hard gate on provenance blocks legitimate work at
> inconvenient moments and trains people to route around it. But if a record IS written
> it must be schema-valid, and that check is hard.

Implementing the stronger reading here would make this repo's history layer mean
something different from its siblings', which is the opposite of what a parity issue is
for. Validity is enforced hard; presence is not. Tightening it is a fleet decision.

**The pin was bumped during review, and that mattered.** The first version pinned
`6be694f3` and concluded `history.yaml` was not in the hub's governed set. It was not — *at
that commit*. The hub added it on 2026-08-01, 92 commits later, at exactly the path a
`MAPPED` entry uses and byte-identical to the copy here. So the conclusion "not governable"
was an artefact of a stale pin, and `CLAUDE.md` had already been written claiming CI
enforcement that did not exist. The pin now tracks hub HEAD, `history.yaml` is governed,
and re-vendoring brought three upstream files forward (hydration-state handling in the
id-label validator — CultureMech curation logic, irrelevant here but part of the canon,
and its 15 new tests come with it).

**`chem_formula.py` is vendored despite being chemistry.** It is in the hub's governed
file list because `validate_id_label_correspondence.py` imports it. Dropping it would
mean maintaining a local fork of the validator — precisely the drift the contract
forbids. It is carried, unused, on purpose.

## Deferred, with reasons

**4 — validated-write helper + writer audit.** Real work, and this repo needs it in a
specific shape: 49 seeders write records, and `record_io.write_record` is already the
choke point they route through. A writer audit here means proving each of those 49 goes
through it rather than calling `path.write_text` — which is a different audit from the
siblings', because the failure mode is different. Filed as #492.

**5 — the id-label adapter.** The validator is vendored, passing its 69 tests, and
governed by the drift check. Making it *do* anything requires an adapter describing where
this repo's records keep `(id, label)` pairs — `mapped_xrefs`, `parent_traits`,
`trait_relations`, and causal-graph node groundings each have a different shape, and
`grounded nodes 342,631/350,267` says the surface is large. Wiring it without measuring
that first would produce a gate whose failures nobody can act on. Filed as #493.

**7 — knowledge-gap scan + QC dashboard. NOT a dependency decision, and this document
said it was.** The first version of this row read "blocked on a claw dependency decision".
Checked against the siblings, there is no such decision to make:

* **No sibling declares `culturebotai-claw` as a dependency.** All three `pyproject.toml`
  mentions are a *comment* — `matplotlib>=3.7,  # kg_microbe_qc dashboard chart (shared
  generator in claw)` — explaining why matplotlib is needed, not depending on claw.
* **No sibling runs these in CI.** TraitMech's `qc.yaml` mentions claw zero times, and
  neither `gen-qc-dashboard` nor `knowledge-gap-scan` is in the 16-recipe `qc` aggregate
  that CI actually invokes.

They are developer conveniences, run by a human who happens to have a checkout. Adopting
them as a dependency would make this repo the only one in the fleet that has one — and
`culturebotai-claw` is not a published package but a working repo (~60 status markdown
files at its root), so depending on it means pinning a moving checkout. That is the failure
the vendoring contract exists to prevent, and the one that already bit this work once when
a 92-commit-stale pin made `history.yaml` look ungovernable.

The convention is already in place: `just new-history` prefers claw when `CLAW_SRC`
resolves and falls back otherwise. If the dashboard is ever wanted, add the recipes with
the same `_require-claw` guard the siblings use — loud when absent, never in CI. That is a
ten-line change on the day someone wants it.

Note also that the *schema* side of knowledge-gap capture already landed: `Discussion` with
`kind: KNOWLEDGE_GAP` is on `ProteinTraitRecord`. Only the scanner and dashboard that
*read* it are absent. #494 closed as won't-fix-by-convention.

## Verifying

```bash
just check-vendored-sync     # byte-identity against the hub at scripts/.vendored_canon_ref
just validate-history        # every history record against the vendored schema
just validate-strict         # closed-schema over the corpus
uv run pytest tests/test_id_label_empty_adapter.py \
              tests/test_id_label_unknown_prefix.py \
              tests/test_id_label_plausibility.py
```
