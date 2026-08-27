# Shared Mech foundation — parity matrix

Where ProteinTraitsMech stands against the sibling Mech knowledge bases on the shared
curation foundation (#484).

The sibling repositories remain the source for domain-specific behavior. General
byte-identical artifacts are now governed by the public
[`CultureBotAI/culturebotai-claw`](https://github.com/CultureBotAI/culturebotai-claw)
manifest at the full immutable commit in `scripts/.vendored_canon_ref`; no Mech is a
vendoring hub.

## Status

| # | Capability | Before | Now | Notes |
|---|---|---|---|---|
| 1 | `mech_shared.yaml` with `Discussion` + `Dataset` | ✗ | **✓** | Vendored byte-identical from claw; `discussions` / `datasets` on `ProteinTraitRecord` |
| 2 | Append-only history schema + presence gate | ✗ | **✓** | `history.yaml` vendored **and governed**, `history/` tree, CI job. Presence advisory — see below |
| 3 | `new-history` / `validate-history` recipes | ✗ | **✓** | Claw-preferred, local fallback scaffolder |
| 4 | Validated-write helper + writer-safety audit | ✗ | **✓** | Atomic closed-schema helper; registered editors enforced; bulk seeders explicitly retain fast merge path — **#492** |
| 5 | ID-to-label correspondence validation | ✗ | **✓** | Fleet YAML adapter + offline count-and-identity gate for actionable internal groundings — **#493** |
| 6 | Evidence snippet / reference validation | **✓** | **✓** | Pre-existing: `just audit-snippets` |
| 7 | Knowledge-gap scan + shared QC dashboard | ✗ | ✗ | **Not a gap.** No sibling has this in CI or as a dependency — see below |
| 8 | Vendored shared-file drift enforcement | ✗ | **✓** | `just check-vendored-sync` over the claw manifest's applicable artifacts + blocking CI job |

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

**The pin and artifact membership are external to this repository.** The former checker
embedded `FILES` and `MAPPED` arrays and compared against a CultureMech commit. The
current checker requires one full claw commit, fetches the single manifest from exactly
that revision, verifies each canonical payload digest, expands this consumer's package
path, and compares the applicable local bytes and modes. The shell launcher therefore
contains no second artifact list that can silently diverge from governance.

**`chem_formula.py` is vendored despite being chemistry.** It is in claw's governed
manifest because `validate_id_label_correspondence.py` imports it. Dropping it would
mean maintaining a local fork of the validator — precisely the drift the contract
forbids. It is carried, unused, on purpose.

## Deferred, with reasons

**4 — validated-write helper + writer audit.** Implemented in the repo-specific
shape #492 required. `record_io.write_validated_record` writes beside the target,
runs the same closed-schema validator as `validate-strict`, and atomically replaces
only a valid candidate. The registered in-place definition editors use that path,
and `audit-writers` fails if one falls back to a direct write. Bulk seeders retain
`write_record`'s merge-first fast path: validating roughly 430,000 individual files
during generation would duplicate the corpus gate and make release builds unusable.
They remain classified and covered by corpus-wide `validate-strict` in CI.

**5 — the id-label adapter.** Implemented after measurement, rather than guessing.
`conf/id_label_targets.yaml` maps causal-node `grounding/label` and canonical-example
identifier/label pairs for the vendored fleet validator. The broad OAK-backed check is
report-first because its known external-ontology backlog is not yet gateable.

The actionable `proteintraitsmech:` subset is blocking in CI. It resolves entirely
against committed record labels and pins both the 5,543 mismatch count and a SHA-256 over
the exact mismatch identities. A fix paired with a new regression therefore fails even
when the count stays constant. The baseline was computed over 429,271 records and 5,799
internal grounded nodes; no `data/raw`, network, or ontology download is required.

**7 — knowledge-gap scan + QC dashboard. NOT a dependency decision, and this document
said it was.** The first version of this row read "blocked on a claw dependency decision".
Checked against the siblings, there is no such decision to make:

* **No sibling declares `culturebotai-claw` as a dependency.** All three `pyproject.toml`
  mentions are a *comment* — `matplotlib>=3.7,  # kg_microbe_qc dashboard chart (shared
  generator in claw)` — explaining why matplotlib is needed, not depending on claw.
* **No sibling runs these in CI.** TraitMech's `qc.yaml` mentions claw zero times, and
  neither `gen-qc-dashboard` nor `knowledge-gap-scan` is in the 16-recipe `qc` aggregate
  that CI actually invokes.

They are developer conveniences, run by a human who happens to have a checkout. The
governance integration does not create a runtime claw dependency: its standalone checker
is vendored and reads only the manifest and payloads at the immutable claw revision.
Making unrelated dashboard tools depend on a moving checkout would be a separate and
unnecessary coupling.

The convention is already in place: `just new-history` prefers claw when `CLAW_SRC`
resolves and falls back otherwise. If the dashboard is ever wanted, add the recipes with
the same `_require-claw` guard the siblings use — loud when absent, never in CI. That is a
ten-line change on the day someone wants it.

Note also that the *schema* side of knowledge-gap capture already landed: `Discussion` with
`kind: KNOWLEDGE_GAP` is on `ProteinTraitRecord`. Only the scanner and dashboard that
*read* it are absent. #494 closed as won't-fix-by-convention.

## Verifying

```bash
just check-vendored-sync     # bytes/modes against claw's pinned immutable manifest
just validate-history        # every history record against the vendored schema
just validate-strict         # closed-schema over the corpus
just validate-internal-id-labels  # offline internal grounding identity gate
just report-id-labels         # broad OAK-backed report (local adapters required)
just audit-writers           # every writer has a classified route
uv run pytest tests/test_id_label_empty_adapter.py \
              tests/test_id_label_unknown_prefix.py \
              tests/test_id_label_plausibility.py
```
